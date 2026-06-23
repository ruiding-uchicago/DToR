# Local Paper RAG — reproducible example

A small, **fully open-access** reproduction of the 1M-paper local retrieval stack
that DToR consults via `paper_vector_path` (see [`docs/MODALITY_RAG.md`](../../docs/MODALITY_RAG.md)).
It runs the *exact* pipeline described in the paper end-to-end on **973 CC-BY/CC0
papers**, producing a Chroma store that plugs straight into the agent.

```
corpus/<DOI>/paragraphs_whole.txt
   │  01_sanitize.py   (EnhancedAcademicTextCleaner)            → paragraphs_whole_sanitized.txt
   │  02_build_rag.py  (RecursiveCharacterTextSplitter 2500/500 → BAAI/bge-m3 → Chroma, cosine)
   ▼
vectorstore/           ← point DToR's paper_vector_path here
```

## Why this exists

The production corpus (≈1.3M papers) cannot be redistributed. This folder is a
**license-cleared, self-contained slice** so anyone can reproduce the chunking +
vectorization end-to-end and verify retrieval, with no copyright concerns.

## Provenance & license (read first)

All 973 papers are open access under **CC-BY / CC-BY-SA / CC0 / public-domain**
and were license-audited against **Crossref + Unpaywall** before inclusion.
- `manifest.csv` — per-paper `doi`, `publisher`, license, OA status (973 rows).
- `LICENSE_AUDIT.csv` — the full 1000-row audit, including the 27 excluded papers.
- `ATTRIBUTION.md` — how the set was vetted and how to attribute.

Publisher mix: MDPI 200 · PLOS 130 · Frontiers 129 · BMC 118 · Hindawi 86 ·
Copernicus 80 · eLife 70 · PeerJ 60 · JMIR 60 · F1000Research 40.

## Contents

| Path | What |
|------|------|
| `corpus.tar.gz` | 973 open-access full texts; extracts → `corpus/<DOI>/paragraphs_whole.txt` (15 MB) |
| `manifest.csv` | per-paper DOI + publisher + license (authoritative DOIs) |
| `LICENSE_AUDIT.csv` | full Crossref/Unpaywall audit of the original 1000 |
| `academic_text_cleaner.py` | vendored cleaner; only `EnhancedAcademicTextCleaner` is used |
| `01_sanitize.py` | clean → `paragraphs_whole_sanitized.txt` |
| `02_build_rag.py` | chunk + bge-m3 embed + Chroma index → `vectorstore/` |
| `03_verify.py` | sanity-check the store + demo similarity queries |
| `requirements.txt` | build dependencies (DToR-pinned) |

`corpus/` (extracted from `corpus.tar.gz`), `vectorstore/`, and the `*_sanitized.txt`
files are **regenerated** locally and are git-ignored — only `corpus.tar.gz` is committed.

## Run it

```bash
pip install -r requirements.txt          # bge-m3 (~2.3 GB) downloads on first run
tar -xzf corpus.tar.gz                    # → corpus/  (01_sanitize.py also auto-extracts)
python 01_sanitize.py                     # ~seconds (CPU, 8 procs)
python 02_build_rag.py                    # GPU: a few min; CPU: ~20-30 min
python 03_verify.py                       # prints counts + 3 example queries
```

Result (reference run, BAAI/bge-m3 on GPU): 973 papers → 961 with non-empty
cleaned text → **25,906 chunks** (~27/paper), Chroma collection `langchain`,
`hnsw:space=cosine`, ~514 MB. (12 papers cleaned to empty text and were skipped.)

## Fidelity to the production pipeline

| Stage | This example | Production |
|-------|--------------|------------|
| clean | `EnhancedAcademicTextCleaner.clean_text()` | same class (`improved_academic_text_cleaner.py`) |
| chunk | `RecursiveCharacterTextSplitter(2500, 500, ["\n\n","\n",". "," ",""])` | identical (`step_1_preprocess_1M_for_RAG_online.py`) |
| embed | `BAAI/bge-m3` | identical |
| index | Chroma, `langchain` collection, cosine | identical (cosine matches the merged store) |
| metadata | `paper_id, doi, chunk_id, chunk_index, total_chunks, source_type` | identical |
| shard/merge | not needed at 973 papers | `merge_vector_stores.py` consolidates `vol_*` |

## Plug into DToR

The store has no `vol_*` subdir, so DToR queries it directly as a single Chroma DB.

```bash
# .env
USE_LOCAL_RAG=true
ENABLE_PAPER_RETRIEVAL=true
PAPER_VECTOR_PATH=/abs/path/to/examples/local_rag_build/vectorstore
EMBEDDING_MODEL=BAAI/bge-m3
PAPER_RESULTS_COUNT=5
```
