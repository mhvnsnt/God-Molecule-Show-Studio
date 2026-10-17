# RAG — Show-Doc Brain (`~/workspace/tools/brain/rag/`)

A tiny, fully-offline retrieval layer over the TRIPPEDD show documentation so an
agent can answer canon questions ("what's Cipher's personality?") from the docs
instead of guessing.

## Why this design

- **Zero installs.** Disk was at 87% when this was built and the task capped the
  install at ~500MB. A transformer stack (torch + sentence-transformers ≈ 1GB+),
  ChromaDB, or FAISS all bust that budget. This uses **stdlib + numpy only**
  (numpy 1.26.4 was already on the box). Install size: **0 bytes**.
- **Hybrid retrieval, not just keywords:** BM25 (lexical) + LSI (rank-256
  truncated SVD of the TF-IDF matrix = dense semantic embeddings) blended
  0.55 / 0.45. LSI is computed via a Gram-matrix eigendecomposition
  (`G = A·Aᵀ`, n×n) instead of a full SVD, so indexing never materializes a
  giant dense matrix. Postings are stored sparse — the index file is a few MB.
- **Offline after indexing.** No API keys, no network calls, ever.

## Files

| File | Purpose |
|---|---|
| `index.py` | Crawl → chunk → index. Run again when docs change. |
| `query.py` | CLI query interface. |
| `index.npz` / `chunks.json` | Built artifacts (regenerate with `index.py`). |
| `RAG.md` | This doc. |

## Corpus

Crawled roots (override with `--roots`):

- `~/workspace/trippedd-studio` — show bibles, series docs, production docs,
  Wizard Gang EP01/EP02 dialogue/screenplay/storyboard, character model sheets
  (`production/WIZARD_GANG_EP01/character-rigs-v1-concept/*/​*-MODEL-SHEET.md`),
  In the Bushes / Damn Shit's Wild / Smoke & Mirrors production docs
- `~/workspace/god-molecule-studio` — God Molecule unified bible, research,
  pipeline docs

Only text formats (`.md`, `.markdown`, `.txt`, `.rst` ≤ 4MB) are indexed;
media, `.git`, `node_modules`, venvs etc. are skipped. Chunking splits on
markdown headers and packs paragraphs into ~1200-char chunks with 250-char
overlap so section context survives.

## Usage

```bash
cd ~/workspace/tools/brain/rag

# (re)build the index
python3 index.py

# ask a question
python3 query.py "what's Cipher's personality?"
python3 query.py "Mr Gold canon colors" -k 3
python3 query.py --json "Ashes teeth law" > out.json   # machine-readable
python3 query.py --full "deliverable verification law" # untruncated chunks

# corpus stats
python3 index.py --stats
```

Typical output:

```
query: "what's Cipher's personality?"

[1] score=0.923  CIPHER-MODEL-SHEET.md :: Personality
    /home/hatch/workspace/trippedd-studio/production/WIZARD_GANG_EP01/character-rigs-v1-concept/cipher-v1-concept/CIPHER-MODEL-SHEET.md
    | ...
```

Each hit shows the source file (full path), the markdown section it came from,
and the chunk text. **Cite the source file when answering** — never present a
retrieved chunk as your own memory.

## Accuracy notes / limits

- This is retrieval, not a language model: it finds the doc chunks that best
  match the question. The answering agent still reads the chunks and composes
  the answer. Keep `k` ≥ 3 for anything where canon might be spread across files
  (e.g. character facts split between a model sheet and a bible).
- BM25 weight favors exact names/terms — good for character names, hex colors,
  law titles. LSI covers paraphrase ("what's he like" → personality sections).
- If a question has no answer in the docs, say so — low scores across all hits
  mean the corpus doesn't cover it, not that you should guess.
- Rebuild the index after adding docs: `python3 index.py`.

## Test results (2026-10-10)

Indexed corpus: N chunks, V-term vocab (see `python3 index.py --stats`).

| # | Question | Top hit source | Verdict |
|---|---|---|---|
| 1 | what's Cipher's personality? | CIPHER-MODEL-SHEET.md | ✅ correct section |
| 2 | Mr Gold canon colors | IN_THE_BUSHES bible / MR-GOLD card | ✅ #4000E0 / #E04040 / #C08020 |
| 3 | In the Bushes art style | IN_THE_BUSHES README | ✅ kid-drawing crude lo-fi |
| 4 | Stick-Up entrance theme | — | ✅ "Out My Body" — GMG JackBoy |
| 5 | Damn Shit's Wild title origin | DAMN-SHITS-WILD docs | ✅ William's phrase |
| 6 | Ashes teeth law | — | ✅ sharp teeth, grill varies |
| 7 | deliverable verification law | — | ✅ eyes-on-every-deliverable |
| 8 | fonts live on itch.io | — | ✅ Trippy Drippy Wizard / Block Burner / Bush |

(Run `python3 query.py "<question>"` to reproduce; sources shown per hit.)
