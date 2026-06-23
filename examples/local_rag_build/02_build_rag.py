#!/usr/bin/env python3
"""
Step 2/3 - chunk + embed + index.

Faithful reproduction of step_1_preprocess_1M_for_RAG_online.py:
  * RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=500,
        separators=["\n\n", "\n", ". ", " ", ""])
  * BAAI/bge-m3 embeddings
  * Chroma persistent store, default "langchain" collection, hnsw:space="cosine"
  * per-chunk metadata: paper_id, source, source_type, chunk_id, doi,
    chunk_index, total_chunks

The resulting ./vectorstore plugs straight into DToR via paper_vector_path.
DOIs are read from manifest.csv (authoritative - correctly handles multi-segment
DOIs such as Hindawi's 10.1155/YEAR/ID, which cannot be recovered from the
folder name alone).
"""
import csv
import time
from pathlib import Path

import torch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE = Path(__file__).resolve().parent
CORPUS = BASE / "corpus"
OUT = str(BASE / "vectorstore")
MANIFEST = BASE / "manifest.csv"
PATTERN = "paragraphs_whole_sanitized.txt"
EMBED_BATCH = 512


def load_doi_map():
    m = {}
    if MANIFEST.exists():
        for r in csv.DictReader(open(MANIFEST)):
            m[r["folder"]] = r["doi"]
    return m


def main():
    doi_map = load_doi_map()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=500,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"loading BAAI/bge-m3 on {device} ...", flush=True)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
    )
    vs = Chroma(
        persist_directory=OUT,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
    )

    docs = []
    n_papers = 0
    for folder in sorted(p for p in CORPUS.iterdir() if p.is_dir()):
        txt = folder / PATTERN
        if not txt.exists():
            continue
        content = open(txt, encoding="utf-8", errors="replace").read()
        if not content.strip():
            continue
        paper_id = folder.name
        doi = doi_map.get(paper_id, paper_id.replace("_", "/", 1))
        chunks = splitter.create_documents(
            texts=[content],
            metadatas=[{
                "paper_id": paper_id,
                "source": str(txt),
                "source_type": "research_paper",
            }],
        )
        for i, ch in enumerate(chunks):
            ch.metadata.update({
                "chunk_id": f"{paper_id}_{i}",
                "doi": doi,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })
        docs.extend(chunks)
        n_papers += 1

    print(f"papers={n_papers}  chunks={len(docs)}  "
          f"avg={len(docs)/max(n_papers,1):.1f} chunks/paper", flush=True)

    t0 = time.time()
    for i in range(0, len(docs), EMBED_BATCH):
        vs.add_documents(docs[i:i + EMBED_BATCH])
        print(f"  indexed {min(i+EMBED_BATCH, len(docs))}/{len(docs)}", flush=True)
    try:
        count = vs._collection.count()
    except Exception:
        count = "unknown"
    print(f"DONE indexed {len(docs)} chunks ({count} in collection) "
          f"in {time.time()-t0:.1f}s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
