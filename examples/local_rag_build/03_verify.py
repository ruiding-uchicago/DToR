#!/usr/bin/env python3
"""
Step 3/3 - verify the store and demo retrieval (loads it exactly as DToR does).
"""
import glob
import sqlite3
from pathlib import Path

import torch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).resolve().parent
STORE = str(BASE / "vectorstore")

# raw chromadb sanity
db = glob.glob(f"{STORE}/chroma.sqlite3")
if not db:
    raise SystemExit(f"no store at {STORE} - run 02_build_rag.py first")
c = sqlite3.connect(db[0])
cur = c.cursor()
cur.execute("SELECT name FROM collections")
print("collections:", [r[0] for r in cur.fetchall()])
cur.execute("SELECT count(*) FROM embeddings")
print("embeddings rows:", cur.fetchone()[0])
c.close()

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\nloading bge-m3 on {device} ...", flush=True)
emb = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": device},
    encode_kwargs={"normalize_embeddings": True},
)
vs = Chroma(persist_directory=STORE, embedding_function=emb)
print("langchain collection count:", vs._collection.count())

queries = [
    "SARS-CoV-2 vaccine neutralizing antibody response",
    "atmospheric aerosol remote sensing retrieval",
    "deep learning model for image segmentation",
]
for q in queries:
    print("\n" + "=" * 80)
    print("QUERY:", q)
    for d, score in vs.similarity_search_with_score(q, k=3):
        m = d.metadata
        print(f"  score={score:.4f}  doi={m.get('doi')}  chunk={m.get('chunk_id')}")
        print(f"    {d.page_content[:150].strip()!r}")
