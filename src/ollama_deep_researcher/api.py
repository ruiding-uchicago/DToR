"""Programmatic entry point for embedding DToR in another application.

    from ollama_deep_researcher.api import run_research

    result = run_research("PFAS detection with 2D-material FET biosensors",
                          api_key=..., branches=3, depth=2)
    print(result.report)

Everything the graph needs is passed as arguments; nothing is read from
module-level globals, so two callers in the same process can use different
settings. Values left as None fall back to the corresponding environment
variable, then to the library default.
"""

from __future__ import annotations

import hashlib
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["ResearchResult", "run_research", "DToRError"]


class DToRError(RuntimeError):
    """Raised when a research run cannot produce a report."""


@dataclass
class ResearchResult:
    """Outcome of one research run."""

    topic: str
    report: str
    mode: str
    branch_summaries: Dict[str, str] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def __bool__(self) -> bool:
        return bool(self.report)


# Node budget below this can strand a branch: if one branch's budget reaches
# exactly zero while another still has pending nodes, older revisions of the
# router deadlocked. The router is fixed, but a starved branch still produces a
# thinner report, so warn rather than fail.
_MIN_SANE_NODES_PER_BRANCH = 3


@contextmanager
def _scoped_env(values: Dict[str, str]):
    """Apply env vars for the duration of a call, then restore them.

    Configuration.from_runnable_config reads os.environ directly and lets it
    win over the config dict, so per-call settings have to go through the
    environment. This keeps that side effect from leaking.
    """
    previous: Dict[str, Optional[str]] = {}
    try:
        for key, value in values.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yield
    finally:
        for key, old in previous.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


def _pick(explicit: Any, env_name: str, default: Any) -> Any:
    if explicit is not None:
        return explicit
    raw = os.environ.get(env_name)
    return raw if raw is not None else default


def run_research(
    topic: str,
    *,
    mode: str = "dtor",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    fallback_models: Optional[List[str]] = None,
    branches: Optional[int] = None,
    depth: Optional[int] = None,
    loops: Optional[int] = None,
    nodes_per_branch: Optional[int] = None,
    search_api: Optional[str] = None,
    fetch_full_page: Optional[bool] = None,
    use_local_rag: bool = False,
    extra_env: Optional[Dict[str, str]] = None,
    recursion_limit: int = 300,
    thread_id: Optional[str] = None,
) -> ResearchResult:
    """Run one research job and return the finished report.

    Args:
        topic: The research question.
        mode: "dtor" for the multi-branch tree, "single" for the linear loop.
        api_key: OpenAI key. Falls back to OPENAI_API_KEY.
        model: Model id, e.g. "gpt-5.6-luna". Falls back to OPENAI_MODEL.
        fallback_models: Models to try if the primary one fails.
        branches: Perspectives to explore (dtor only).
        depth: Maximum branch depth (dtor only).
        loops: Search/reflect iterations per research node.
        nodes_per_branch: Node budget per branch (dtor only).
        search_api: "tavily", "duckduckgo", "perplexity" or "searxng".
        fetch_full_page: Download full pages instead of snippets. Costs tokens.
        use_local_rag: Enable local retrieval. Off by default; enabling it
            requires the RAG extras and at least one configured vector store.
        extra_env: Escape hatch for settings without a named argument, e.g.
            {"ENABLE_PAPER_RETRIEVAL": "true", "PAPER_VECTOR_PATH": "/data/vs"}.
        recursion_limit: LangGraph step ceiling for one run.
        thread_id: Checkpoint identity. Derived from the topic when omitted.

    Returns:
        ResearchResult with the report and, in dtor mode, per-branch summaries.

    Raises:
        ValueError: on an empty topic, an unknown mode, or a missing API key.
        DToRError: if the graph finishes without producing a report.
    """
    if not topic or not topic.strip():
        raise ValueError("topic must be a non-empty string")
    topic = topic.strip()

    if mode not in ("dtor", "single"):
        raise ValueError(f"mode must be 'dtor' or 'single', got {mode!r}")

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("no OpenAI API key: pass api_key= or set OPENAI_API_KEY")

    env: Dict[str, str] = {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": key,
        "OPENAI_MODEL": str(_pick(model, "OPENAI_MODEL", "gpt-5.6-luna")),
        "RESEARCH_MODE": mode,
        "USE_LOCAL_RAG": "true" if use_local_rag else "false",
        "SEARCH_API": str(_pick(search_api, "SEARCH_API", "duckduckgo")),
        "MAX_WEB_RESEARCH_LOOPS": str(_pick(loops, "MAX_WEB_RESEARCH_LOOPS", 2)),
        "STRIP_THINKING_TOKENS": "True",
    }
    if not use_local_rag:
        env.update({
            "ENABLE_FET_RAW_DATA": "false",
            "ENABLE_CODE_RETRIEVAL": "false",
            "ENABLE_PAPER_RETRIEVAL": "false",
        })
    if fallback_models is not None:
        env["OPENAI_FALLBACK_MODELS"] = ",".join(fallback_models)
    if fetch_full_page is not None:
        env["FETCH_FULL_PAGE"] = "True" if fetch_full_page else "False"

    if mode == "dtor":
        budget = int(_pick(nodes_per_branch, "NODES_PER_BRANCH", 20))
        if budget < _MIN_SANE_NODES_PER_BRANCH:
            import warnings
            warnings.warn(
                f"nodes_per_branch={budget} is very small; a branch can exhaust "
                f"its budget after one expansion and contribute little to the "
                f"final report. Use >= {_MIN_SANE_NODES_PER_BRANCH}, ideally >= 10.",
                stacklevel=2,
            )
        env.update({
            "MAX_BRANCHES": str(_pick(branches, "MAX_BRANCHES", 3)),
            "MAX_BRANCH_DEPTH": str(_pick(depth, "MAX_BRANCH_DEPTH", 2)),
            "NODES_PER_BRANCH": str(budget),
        })
    if extra_env:
        env.update({k: str(v) for k, v in extra_env.items()})

    tid = thread_id or f"dtor_{hashlib.md5(topic.encode('utf-8')).hexdigest()[:12]}"
    started = time.time()

    with _scoped_env(env):
        # Imported inside the call so the environment above is in place before
        # Configuration is built, and so importing this module stays cheap.
        from ollama_deep_researcher.dtor_graph import create_main_graph
        from ollama_deep_researcher.dtor_state import DToRStateInput

        graph = create_main_graph()
        raw = graph.invoke(
            DToRStateInput(research_topic=topic, mode=mode),
            config={"configurable": {"thread_id": tid},
                    "recursion_limit": recursion_limit},
        )

    report = (raw or {}).get("final_summary", "") or ""
    if not report:
        raise DToRError(
            f"research finished without a report (topic={topic!r}, mode={mode}). "
            "Check the logs/ directory for the failing node."
        )

    summaries: Dict[str, str] = dict(raw.get("branch_summaries") or {})

    sources = [s for s in (raw.get("all_sources") or []) if isinstance(s, str)]

    return ResearchResult(
        topic=topic,
        report=report,
        mode=mode,
        branch_summaries=summaries,
        sources=sources,
        elapsed_seconds=round(time.time() - started, 1),
    )
