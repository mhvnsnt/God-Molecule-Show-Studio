#!/usr/bin/env python3
"""
index.py — Build a hybrid BM25 + LSI search index over the TRIPPEDD show docs.

Zero-install: stdlib + numpy only. Fully offline. Re-run when docs change.

Design notes (kept lean for an 87%-full disk):
  * Chunk .md/.txt/.rst files by markdown headers into ~1200-char chunks.
  * BM25 postings stored SPARSE (per-term doc-id/count/tfidf lists) — the
    index file is a few MB, not a dense 100MB+ matrix.
  * LSI via Gram-matrix eigendecomposition (G = A A^T, n x n) instead of a
    full SVD, so we never materialize V x V or V x k dense factors.

Usage:
    python3 index.py              # build/rebuild the index
    python3 index.py --roots DIR [DIR...]
    python3 index.py --stats
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

RAG_DIR = Path(__file__).resolve().parent
INDEX_PATH = RAG_DIR / "index.npz"
CHUNKS_PATH = RAG_DIR / "chunks.json"

DEFAULT_ROOTS = [
    Path.home() / "workspace" / "trippedd-studio",
    Path.home() / "workspace" / "god-molecule-studio",
]

SKIP_DIRS = {
    ".git", ".github", "node_modules", ".venv", "__pycache__", ".next",
    "dist", "build", ".cache", "venv", ".mypy_cache", ".ruff_cache",
}
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".webm",
    ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".glb", ".gltf", ".fbx",
    ".obj", ".blend", ".ttf", ".otf", ".woff", ".woff2", ".zip", ".gz",
    ".tar", ".7z", ".pdf", ".exe", ".bin", ".pyc", ".lock", ".sqlite", ".db",
}
WANT_EXTS = {".md", ".markdown", ".txt", ".rst"}

CHUNK_TARGET = 1200
CHUNK_OVERLAP = 250
LSI_RANK = 256
MIN_DF = 3
MAX_DF_FRAC = 0.70

STOPWORDS = set(
    """
a about above after again against all am an and any are as at be because been
before being below between both but by can could did do does doing down during
each few for from further had has have having he her here hers herself him his
how i if in into is it its itself just me more most my myself no nor not now of
off on once only or other ought our ours ourselves out over own same she should
so some such than that the their theirs them themselves then there these they
this those through to too under until up very was we were what when where which
while who whom why with would you your yours yourself yourselves s t ll ve re
d ll m don should now
""".split()
)

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def tokenize(text):
    return [t for t in TOKEN_RE.findall(text.lower())
            if t not in STOPWORDS and len(t) > 1]


def iter_doc_files(roots):
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            print(f"  [skip] missing root: {root}", file=sys.stderr)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                p = Path(dirpath) / fn
                ext = p.suffix.lower()
                if ext in SKIP_EXTS:
                    continue
                if ext in WANT_EXTS:
                    try:
                        if p.stat().st_size > 4_000_000:
                            continue
                    except OSError:
                        continue
                    yield p


def read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        return ""


def looks_binary(text):
    return "\x00" in text[:4096]


def chunk_markdown(text, source, relpath):
    sections = []
    header = Path(relpath).stem.replace("-", " ").replace("_", " ")
    buf = []
    for line in text.splitlines():
        m = HEADER_RE.match(line.strip())
        if m and buf:
            sections.append((header, buf))
            header = m.group(2).strip()
            buf = []
        elif m:
            header = m.group(2).strip()
        else:
            buf.append(line)
    if buf:
        sections.append((header, buf))

    chunks = []
    for sec_header, lines in sections:
        paras, para = [], []
        for line in lines:
            if line.strip():
                para.append(line.strip())
            elif para:
                paras.append(" ".join(para))
                para = []
        if para:
            paras.append(" ".join(para))
        if not paras:
            continue

        cur, cur_len = [], 0
        for p in paras:
            if cur_len + len(p) > CHUNK_TARGET and cur:
                body = "\n\n".join(cur)
                chunks.append({"source": source, "section": sec_header, "text": body})
                tail = body[-CHUNK_OVERLAP:]
                cur = [tail] if tail.strip() else []
                cur_len = len(cur[0]) if cur else 0
            cur.append(p)
            cur_len += len(p) + 2
        if cur:
            chunks.append(
                {"source": source, "section": sec_header, "text": "\n\n".join(cur)})
    return chunks


def build_index(roots):
    t0 = time.time()
    files = list(iter_doc_files(roots))
    print(f"crawled {len(files)} files", flush=True)

    chunks = []
    for p in files:
        text = read_text(p)
        if not text.strip() or looks_binary(text):
            continue
        try:
            rel = p.relative_to(Path.home())
        except ValueError:
            rel = p
        chunks.extend(chunk_markdown(text, str(p), str(rel)))
    chunks = [c for c in chunks if len(c["text"].strip()) > 40]
    n = len(chunks)
    print(f"chunks: {n} ({time.time()-t0:.1f}s)", flush=True)
    if n == 0:
        raise SystemExit("no chunks — nothing to index")

    # --- vocabulary (document frequency pruning) ---
    doc_tokens = [tokenize(c["text"]) for c in chunks]
    df = {}
    for toks in doc_tokens:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    terms = sorted(t for t, c in df.items()
                   if MIN_DF <= c <= int(MAX_DF_FRAC * n))
    vocab = {t: i for i, t in enumerate(terms)}
    V = len(terms)
    print(f"vocab: {V} terms", flush=True)
    df_arr = np.array([df[t] for t in terms], dtype=np.float64)

    # --- sparse postings: per term -> (doc ids, raw counts, tf-idf) ---
    post_ids, post_cnt, post_tfidf = [], [], []
    post_start = np.zeros(V + 1, dtype=np.int64)
    idf = (np.log((n - df_arr + 0.5) / (df_arr + 0.5)) + 1.0).astype(np.float32)
    doc_len = np.zeros(n, dtype=np.float32)

    # build term->docs as dict of lists first (memory-friendly)
    postings = [[] for _ in range(V)]
    for i, toks in enumerate(doc_tokens):
        counts = {}
        for t in toks:
            j = vocab.get(t)
            if j is not None:
                counts[j] = counts.get(j, 0) + 1
        doc_len[i] = sum(counts.values())
        for j, c in counts.items():
            postings[j].append((i, c))
    for j in range(V):
        post_start[j + 1] = post_start[j] + len(postings[j])
        idf_j = idf[j]
        for i, c in postings[j]:
            post_ids.append(i)
            post_cnt.append(c)
            post_tfidf.append((1.0 + np.log1p(c)) * idf_j)
    post_ids = np.array(post_ids, dtype=np.int32)
    post_cnt = np.array(post_cnt, dtype=np.float32)
    post_tfidf = np.array(post_tfidf, dtype=np.float32)
    del postings
    print(f"postings: {len(post_ids)} ({time.time()-t0:.1f}s)", flush=True)

    # --- LSI via Gram eigendecomposition ---
    # A (n x V tf-idf) is too big dense for a full SVD, but G = A A^T is n x n.
    # Build A as float32 dense in blocks to bound memory, accumulate G.
    k = min(LSI_RANK, n - 1)
    G = np.zeros((n, n), dtype=np.float64)
    block = 4096
    for b0 in range(0, V, block):
        b1 = min(V, b0 + block)
        Ab = np.zeros((n, b1 - b0), dtype=np.float32)
        for j in range(b0, b1):
            s, e = post_start[j], post_start[j + 1]
            Ab[post_ids[s:e], j - b0] = post_tfidf[s:e]
        G += Ab @ Ab.T
        del Ab
    print(f"gram built ({time.time()-t0:.1f}s), eigendecomposing...", flush=True)
    vals, vecs = np.linalg.eigh(G)  # ascending
    order = np.argsort(-vals)
    vals, vecs = vals[order][:k], vecs[:, order][:, :k]
    S_k = np.sqrt(np.maximum(vals, 0)).astype(np.float32)
    U_k = vecs.astype(np.float32)
    doc_emb = U_k * S_k
    dn = np.linalg.norm(doc_emb, axis=1, keepdims=True)
    dn[dn == 0] = 1.0
    doc_emb /= dn

    np.savez_compressed(
        INDEX_PATH,
        vocab=np.array(terms),
        idf=idf,
        doc_len=doc_len,
        post_start=post_start,
        post_ids=post_ids,
        post_cnt=post_cnt,
        post_tfidf=post_tfidf,
        U_k=U_k,
        S_k=S_k,
        doc_emb=doc_emb,
    )
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    print(f"saved {INDEX_PATH} ({INDEX_PATH.stat().st_size/1e6:.1f} MB) + "
          f"chunks.json in {time.time()-t0:.1f}s total", flush=True)


def stats():
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        chunks = json.load(f)
    idx = np.load(INDEX_PATH)
    by_source = {}
    for c in chunks:
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
    print(f"chunks: {len(chunks)}  vocab: {len(idx['vocab'])}  "
          f"index: {INDEX_PATH.stat().st_size/1e6:.1f} MB")
    for s, c in sorted(by_source.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {c:4d}  {s}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", nargs="*", default=[str(r) for r in DEFAULT_ROOTS])
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    if args.stats:
        stats()
    else:
        build_index(args.roots)


if __name__ == "__main__":
    main()
