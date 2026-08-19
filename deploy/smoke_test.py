#!/usr/bin/env python3
"""Offline acceptance test — no API key, no network. Run after install:

    PYTHONPATH=src python deploy/smoke_test.py

Mocks the LLM and the search backend, then drives a real DToR graph to a final
report. Exits non-zero on failure.
"""
import json, os, sys, tempfile, pathlib, glob

for _base in [pathlib.Path(__file__).resolve().parent, *pathlib.Path(__file__).resolve().parents]:
    if (_base / "src" / "ollama_deep_researcher").is_dir():
        sys.path.insert(0, str(_base / "src")); break
else:
    sys.exit("cannot locate src/ollama_deep_researcher — run from the repo")
# capture the operator's real setting before we override env for the fast run
_user_npb = os.environ.get("NODES_PER_BRANCH")
if _user_npb is None:
    _envfile = pathlib.Path(__file__).resolve().parent / ".env"
    if _envfile.exists():
        for _line in _envfile.read_text().splitlines():
            if _line.strip().startswith("NODES_PER_BRANCH="):
                _user_npb = _line.split("=", 1)[1].split("#")[0].strip()

os.environ.update({
    "LLM_PROVIDER": "openai", "OPENAI_API_KEY": "sk-smoke",
    "OPENAI_MODEL": "gpt-5.6-luna",
    "USE_LOCAL_RAG": "false", "ENABLE_FET_RAW_DATA": "false",
    "ENABLE_CODE_RETRIEVAL": "false", "ENABLE_PAPER_RETRIEVAL": "false",
    "RESEARCH_MODE": "dtor", "SEARCH_API": "duckduckgo",
    "MAX_BRANCHES": "3", "MAX_BRANCH_DEPTH": "1",
    "MAX_WEB_RESEARCH_LOOPS": "1", "NODES_PER_BRANCH": "2",
    "FETCH_FULL_PAGE": "False",
})

import logging

def _quiet():
    """dtor_nodes calls setup_logging() at import time; re-silence after imports."""
    for _n in ("dtor_nodes", "dtor_nodes.analysis", "dtor_nodes.query_gen",
               "dtor_nodes.routing", "dtor_nodes.finalize", "dtor_nodes.reflect"):
        lg = logging.getLogger(_n)
        lg.handlers.clear(); lg.setLevel(logging.CRITICAL); lg.propagate = False

fails = []
def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)

print("\n1. heavy deps absent")
for mod in ("torch", "chromadb", "sentence_transformers", "transformers"):
    try:
        __import__(mod); check(f"{mod} not installed", False, "found — RAG profile leaked in")
    except ImportError:
        check(f"{mod} not installed", True)

print("\n2. config + graph")
from ollama_deep_researcher.configuration import Configuration
cfg = Configuration.from_runnable_config(None)
check("provider is openai", cfg.llm_provider == "openai", cfg.llm_provider)
check("local RAG off", cfg.use_local_rag is False)
from ollama_deep_researcher.dtor_nodes import get_llm
_quiet()
check("LLM constructs", type(get_llm(cfg)).__name__ == "ChatOpenAIWrapper")

print("\n3. portal-mode patch applied")
from ollama_deep_researcher.chainlit_app import parse_user_input
_, mode = parse_user_input("PFAS sensing with 2D materials")
check("RESEARCH_MODE honoured", mode == "dtor",
      "" if mode == "dtor" else f"got {mode!r} — apply deploy/0001-portal-mode-default.patch")

print("\n4. config guard")
if _user_npb is None:
    print("  [SKIP] NODES_PER_BRANCH not configured yet (default 100 is safe)")
else:
    _npb = int(_user_npb)
    check("NODES_PER_BRANCH >= 10", _npb >= 10,
          f"{_npb}" if _npb >= 10
          else f"{_npb} — router deadlocks when a branch budget hits 0")

print("\n5. end-to-end DToR (mocked LLM + search)")
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
n = {"llm": 0, "search": 0}

def _fake(self, messages, stop=None, run_manager=None, **kw):
    n["llm"] += 1
    t = " ".join(str(getattr(m, "content", "")) for m in messages).lower()
    if "master research synthesizer" in t:
        o = "# Final Report\n\nIntegrated prose. LOD 42 nM."
    elif "research synthesis expert" in t:
        o = "## Branch Synthesis\n\nConfidence: High"
    elif "diversification expert" in t or "diverse perspectives" in t:
        o = json.dumps({"perspectives": [
            {"title": f"Angle {i}", "description": "d", "query": f"q{i}"} for i in (1, 2, 3)]})
    elif "research analysis expert" in t:
        o = json.dumps({"decision": "finalize", "rationale": "ok", "knowledge_gaps": []})
    else:
        o = json.dumps({"query": "kw a b", "rationale": "r"})
    return ChatResult(generations=[ChatGeneration(message=AIMessage(content=o))])

import ollama_deep_researcher.openai_wrapper as ow
ow.ChatOpenAIWrapper._generate = _fake
import ollama_deep_researcher.graph as G
def _fake_search(q, max_results=3, fetch_full_page=False):
    n["search"] += 1
    return {"results": [{"title": "T", "url": "https://example.org/1",
                         "content": "mock", "raw_content": "mock"}]}
G.duckduckgo_search = _fake_search

os.chdir(tempfile.mkdtemp())
from ollama_deep_researcher.dtor_graph import create_main_graph
from ollama_deep_researcher.dtor_state import DToRStateInput
import contextlib, io
_sink = io.StringIO()
# init_session re-runs setup_logging() mid-graph, so silence both streams here
with contextlib.redirect_stdout(_sink), contextlib.redirect_stderr(_sink):
    _quiet()
    res = create_main_graph().invoke(
        DToRStateInput(research_topic="smoke topic", mode="dtor"),
        config={"configurable": {"thread_id": "smoke"}, "recursion_limit": 300})
summary = res.get("final_summary", "")
check("final report produced", bool(summary), f"{len(summary)} chars")
check("all 3 branches ran", n["llm"] > 15, f"{n['llm']} LLM calls")
check("search invoked", n["search"] > 0, f"{n['search']} searches")
check("branch files written", len(glob.glob("synthesis_branches_and_final/*/branch_*.md")) == 3)

print("\n" + ("FAILED: " + ", ".join(fails) if fails else "ALL CHECKS PASSED"))
sys.exit(1 if fails else 0)
