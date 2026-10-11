#!/usr/bin/env python3
"""
query.py — Query the TRIPPEDD show-doc index.

Hybrid scoring: BM25 (sparse lexical) + LSI cosine (semantic).
Offline, numpy only.

Usage:
    python3 query.py "what's Cipher's personality?"
    python3 query.py "art style of In the Bushes" -k 3
    python3 query.py --json "Ashes teeth law"
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from index import RAG_DIR, INDEX_PATH, CHUNKS_PATH, tokenize

W_BM25 = 0.55
W_LSI = 0.45
K1 = 1.2
B = 0.75

_cache = {}


def load():
    if "data" in _cache:
        return _cache["data"]
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        sys.exit("index not built yet — run `python3 index.py` first.")
    idx = np.load(INDEX_PATH, allow_pickle=False)
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        chunks = json.load(f)
    data = {
        "vocab": {t: i for i, t in enumerate(idx["vocab"])},
        "idf": idx["idf"].astype(np.float64),
        "doc_len": idx["doc_len"].astype(np.float64),
        "post_start": idx["post_start"],
        "post_ids": idx["post_ids"],
        "post_cnt": idx["post_cnt"].astype(np.float64),
        "post_tfidf": idx["post_tfidf"].astype(np.float64),
        "U_k": idx["U_k"].astype(np.float64),
        "S_k": idx["S_k"].astype(np.float64),
        "doc_emb": idx["doc_emb"].astype(np.float64),
        "chunks": chunks,
    }
    data["avgdl"] = float(np.mean(data["doc_len"])) if len(data["doc_len"]) else 1.0
    data["n"] = len(chunks)
    _cache["data"] = data
    return data


def score(data, q_counts):
    n = data["n"]
    bm25 = np.zeros(n)
    a = np.zeros(n)  # A @ q  (tf-idf doc weights projected onto query)
    dl, avgdl = data["doc_len"], data["avgdl"]
    for j, qtf in q_counts.items():
        s, e = data["post_start"][j], data["post_start"][j + 1]
        ids = data["post_ids"][s:e]
        if len(ids) == 0:
            continue
        cnt = data["post_cnt"][s:e]
        denom = cnt + K1 * (1 - B + B * dl[ids] / avgdl)
        bm25[ids] += data["idf"][j] * (cnt * (K1 + 1)) / denom * (1.0 + 0.25 * qtf)
        a[ids] += (1.0 + np.log1p(qtf)) * data["idf"][j] * data["post_tfidf"][s:e]
    # LSI: q_emb = S_k^-1 U_k^T a
    q_emb = (data["U_k"].T @ a) / np.maximum(data["S_k"], 1e-9)
    nrm = np.linalg.norm(q_emb)
    lsi = np.zeros(n) if nrm == 0 else data["doc_emb"] @ (q_emb / nrm)
    b_n = bm25 / (bm25.max() or 1.0)
    l_n = np.clip(lsi, 0, None)
    l_n = l_n / (l_n.max() or 1.0)
    return W_BM25 * b_n + W_LSI * l_n


def search(query, k=5):
    data = load()
    q_counts = Counter(data["vocab"][t] for t in tokenize(query)
                       if t in data["vocab"])
    if not q_counts:
        return []
    final = score(data, q_counts)
    order = np.argsort(-final)[:k]
    return [
        {"score": round(float(final[i]), 4),
         "source": data["chunks"][i]["source"],
         "section": data["chunks"][i]["section"],
         "text": data["chunks"][i]["text"]}
        for i in order if final[i] > 0
    ]


def snippet(text, limit=900):
    t = text.replace("\n\n", "\n").strip()
    return t if len(t) <= limit else t[: limit - 1].rstrip() + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    q = " ".join(args.query)
    hits = search(q, k=args.k)
    if args.json:
        print(json.dumps({"query": q, "results": hits}, ensure_ascii=False, indent=2))
        return
    if not hits:
        print("No results — try different wording or rebuild the index.")
        return
    print(f'query: "{q}"\n')
    for i, h in enumerate(hits, 1):
        print(f"[{i}] score={h['score']}  {Path(h['source']).name} :: {h['section']}")
        print(f"    {h['source']}")
        body = h["text"] if args.full else snippet(h["text"])
        for line in body.splitlines()[:14]:
            print(f"    | {line}")
        print()


if __name__ == "__main__":
    main()
