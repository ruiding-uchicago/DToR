#!/usr/bin/env python3
"""
Step 1/3 - clean each paper's full text.

Reuses EnhancedAcademicTextCleaner (vendored as academic_text_cleaner.py from the
DToR scraping pipeline) to turn
    corpus/<DOI>/paragraphs_whole.txt
into
    corpus/<DOI>/paragraphs_whole_sanitized.txt
which is the exact file the chunker (02_build_rag.py) consumes. This mirrors the
cleaning stage of the production 1M-paper RAG (XML/HTML stripping, unicode
normalisation, citation/URL/DOI standardisation, equation/table preservation,
reference removal).
"""
import sys
import tarfile
import time
from collections import Counter
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE = Path(__file__).resolve().parent
CORPUS = BASE / "corpus"
sys.path.insert(0, str(BASE))
from academic_text_cleaner import EnhancedAcademicTextCleaner

_cleaner = None


def _init():
    global _cleaner
    _cleaner = EnhancedAcademicTextCleaner()


def work(folder_str):
    folder = Path(folder_str)
    raw = folder / "paragraphs_whole.txt"
    out = folder / "paragraphs_whole_sanitized.txt"
    if not raw.exists():
        return "no_raw"
    try:
        content = open(raw, encoding="utf-8", errors="replace").read()
        cleaned = _cleaner.clean_text(content)
        if not cleaned.strip():
            return "empty_after_clean"
        with open(out, "w", encoding="utf-8") as f:
            f.write(cleaned)
        return "ok"
    except Exception as e:
        return f"err:{type(e).__name__}"


def main():
    if not CORPUS.exists() or not any(CORPUS.iterdir()):
        tgz = BASE / "corpus.tar.gz"
        if tgz.exists():
            print("extracting corpus.tar.gz ...")
            with tarfile.open(tgz) as t:
                t.extractall(BASE)
    folders = sorted(str(p) for p in CORPUS.iterdir() if p.is_dir())
    print(f"sanitizing {len(folders)} papers with EnhancedAcademicTextCleaner ...")
    t0 = time.time()
    counts = Counter()
    with ProcessPoolExecutor(max_workers=8, initializer=_init) as ex:
        for fu in as_completed([ex.submit(work, f) for f in folders]):
            counts[fu.result()] += 1
    print(dict(counts), f"in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
