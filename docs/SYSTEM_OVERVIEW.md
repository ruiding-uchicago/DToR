# Local Deep Researcher – System Overview

## Project Purpose
Local Deep Researcher is a LangGraph-based agent that performs iterative web research and optional local retrieval while running entirely against user-controlled infrastructure. It prioritises local LLM hosts (Ollama or LMStudio), gracefully falls back to OpenAI when permitted, and can execute either a linear “single path” investigation or a multi-branch Deep Tree of Research (DToR) exploration.

## Architecture At A Glance
```
LangGraph Studio / CLI
        │
        ▼
  create_main_graph (dtor_graph.py)
        │─────────────┬─────────────────────────┐
        │             │                         │
        ▼             ▼                         ▼
 init_session   single_path_research     dtor_mode (DToR subgraph)
                      │                         │
                      ▼                         ▼
             Graph (graph.py)        Branch orchestration (dtor_nodes.py)
                      │                         │
                      ▼                         ▼
          Search + RAG utilities         Advanced RAG + utilities
         (utils.py, advanced_fet_rag.py, configuration.py, prompts.py, …)
```

### Entry Points
- **LangGraph Studio** (`langgraph.json`) registers:
  - `ollama_deep_researcher` – the single-path research loop (default).
  - `deep_researcher_dtor` – the Deep Tree of Research orchestrator.
  - `code_improvement_researcher` – ML code audit workflow that embeds the research graph.
- **Batch / CLI** scripts (`dtor_orchestration_cs_cluster/` for CS cluster, `dtor_orchestration_dsi_cluster/` for DSI cluster, and `run_batch.py`) wrap the same graphs with SQLite checkpoints so long-running jobs can be resumed or scheduled on SLURM-style clusters.

### Key Modules
- `configuration.py` – central Pydantic schema that merges environment variables, Studio overrides, and code defaults. Enforces modality validation (`enable_fet_raw_data`, `enable_code_retrieval`, `enable_paper_retrieval`) and guarantees OpenAI credentials when `llm_provider="openai"`.
- `graph.py` – single-path LangGraph with nodes for query generation, local retrieval, web search, summarisation, reflection, routing, and final synthesis. Exports `graph`.
- `dtor_graph.py` + `dtor_nodes.py` + `dtor_state.py` – Deep Tree of Research coordinator that builds branches, allocates budgets, and composes the single-path graph per branch.
- `advanced_fet_rag.py` – hierarchical multi-view retrieval for FET sensor data; also handles manufacturing heuristics and Globus source mapping.
- `utils.py` – pluggable search adapters (DuckDuckGo, SearXNG, Tavily, Perplexity), local Chroma helpers, deduplication, `<think>` token stripping, and path discovery.
- `lmstudio.py` / `openai_wrapper.py` – wrappers that normalise local LMStudio behaviour and OpenAI “golden pattern” responses.

### Configuration Precedence
1. **Environment variables** (`.env`, deployment settings)
2. **LangGraph Studio Config panel** (per-run overrides)
3. **Defaults in `Configuration`** (compiled schema)

Selected configuration keys:
- `LLM_PROVIDER`, `LOCAL_LLM`, `OLLAMA_BASE_URL`, `LMSTUDIO_BASE_URL`, `OPENAI_API_KEY`
- `SEARCH_API`, `FETCH_FULL_PAGE`, `USE_LOCAL_RAG`, modality toggles and limits
- `RESEARCH_MODE`, `MAX_BRANCHES`, `MAX_BRANCH_DEPTH`, `NODES_PER_BRANCH`

### State Objects
- `SummaryState` (`state.py`) tracks per-research-loop context: queries, collected artefacts, summary history, loop counter, node status, and unique IDs.
- `DToRState` (`dtor_state.py`) holds branch dictionaries, budgets, knowledge gaps, and final synthesis output. `ResearchBranch` embeds lists of `SummaryState`s.
- `CodeImprovementState` reuses the research graph to audit ML code, demonstrating how other workflows can compose the system.

### Failover Philosophy
`dtor_nodes.invoke_with_failover` standardises model calls: attempt the configured local provider first, then iterate through OpenAI primary and fallback models if available. This helper is reused throughout `graph.py`, DToR nodes, and the code improvement workflow, ensuring long jobs survive transient local host failures.

### Outputs
- **LangGraph Studio**: interactive traces, state visualisation.
- **Filesystem**:
  - `logs/` – timestamped log streams per run (analysis, query generation, routing, finalisation, reflection).
  - `synthesis_branches_and_final/<topic>/` – branch syntheses and final reports.
  - Optional FET fabrication parameter JSON emitted by `finalize_summary` when FET mode is active.
- **CLI**: prints final report to stdout while persisting artefacts above.

### Extensibility Notes
- Adding a new modality only requires extending `Configuration`, wiring retrieval in `local_rag_research`, and updating the summarisation prompts to recognise the modality label.
- Additional routing strategies can be prototyped by adjusting `route_next_action` and `select_next_branch` because branch state is serialised via `SummaryState.node_id` and the SQLite checkpointer.
- External automation (e.g., auto-continue via Selenium) operates against the logs and Studio UI without needing changes to the graph definitions.

Use this document as the high-level map. Implementation specifics for the research flows and modality retrieval live in `docs/RESEARCH_WORKFLOWS.md` and `docs/MODALITY_RAG.md`.
