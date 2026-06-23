# Research Workflows

This guide explains how Local Deep Researcher executes single-path and Deep Tree of Research investigations, how routing decisions are made, and how orchestration scripts manage checkpoints and logs.

## Single-Path Loop

The single-path graph (`graph.py`) is compiled as `ollama_deep_researcher`. It operates as a deterministic loop with structured state updates:

```
START
  ↓
init_session
  ↓
generate_query
  ↓
local_rag_research
  ↓
summarize_local_rag_results
  ↓
generate_complementary_query
  ↓
web_research
  ↓
complementary_web_research
  ↓
summarize_sources
  ↓
reflect_on_summary ─────→ route_research ─────→ (back to local_rag_research)
                                         ↘
                                   finalize_summary → END
```

### Node Responsibilities
- **init_session** – resets logging via `setup_logging` from `dtor_nodes`.
- **generate_query** – LLM-derived query with JSON-first parsing; preserves raw FET prompts when `enable_fet_raw_data` is true.
- **local_rag_research** – orchestrates modality-aware retrieval (FET sensors, code repositories, academic papers, legacy paths). Results are labelled and merged for later summarisation.
- **summarize_local_rag_results** – produces a concise (<500 chars) local knowledge digest, using FET-specific prompts when appropriate.
- **generate_complementary_query** – analyses the local digest to craft a divergent query; supplies back-off templates if JSON parsing fails.
- **web_research / complementary_web_research** – adapts to `SEARCH_API` (DuckDuckGo, SearXNG, Tavily, Perplexity), deduplicates sources, optionally fetches full page content, and records formatted citations.
- **summarize_sources** – integrates new results (local + main + complementary), updates `running_summary`, and appends an iteration record to `summary_history`.
- **reflect_on_summary** – identifies knowledge gaps with structured output, increments `research_loop_count`, and supplies the next `search_query`.
- **route_research** – loops until `max_web_research_loops` is exceeded, then forwards to `finalize_summary`.
- **finalize_summary** – synthesises iteration history, dedupes sources, and (when FET mode enabled) emits manufacturing parameter JSON alongside the report.

Each node uses `invoke_with_failover` so a stalled local model can fall back to OpenAI. The `SummaryState` dataclass aggregates queries, sources, summaries, and node status so downstream nodes can make decisions without hidden globals.

## Deep Tree of Research (DToR) Mode

Deep Tree of Research explores a topic through multiple perspectives simultaneously. It is best suited for broad or ambiguous questions where several independent lines of inquiry are valuable.

When `RESEARCH_MODE=dtor`, the main entry graph (`dtor_graph.py`) builds a DToR subgraph that composes the single-path loop as a reusable “research node.” The flow is:

1. **diversify_initial_query** – generates up to `max_branches` perspectives. Branch IDs are deterministic (`md5(topic + index + title)`) so checkpoint recovery reuses the same identifiers.
2. **select_next_branch** – picks the first actionable branch, honouring environment overrides (`TARGET_BRANCH_ID`, `ONE_BRANCH_PER_JOB`, `DIVERSIFY_ONLY`) which are useful on clusters.
3. **research_node** – pulls the next `SummaryState` marked as `pending`, switches it to `in_progress`, runs the single-path graph, and marks it `completed`. Sources are cleared to avoid duplication in DToR mode.
4. **analyze_research_report** – inspects the latest completed node, decides to `expand`, `prune`, or `finalize`, and surfaces knowledge gaps. Early in a branch it biases toward expansion to ensure depth.
5. **generate_follow_up_queries** – converts knowledge gaps into new `SummaryState` entries, consuming branch budget (`nodes_per_branch`) and increasing depth.
6. **synthesize_branch** – once a branch is complete (no budget or depth left) it aggregates all node summaries, writes a markdown report, and tags sources.
7. **synthesize_final_report** – when every branch has a summary, it fuses them into a final report with shared tables, contradiction analysis, and a candidate inventory.
8. **route_next_action / select_next_branch** – centralised router that evaluates branch readiness (pending nodes, completed-but-unanalysed nodes, synthesis required) and loops until `is_complete` is set.

The DToR state machine persists to SQLite when run via `SqliteSaver`, allowing long experiments to resume mid-branch. `research_node` and `generate_follow_up_queries` ensure budgets (`remaining_budget`) and depth (`max_branch_depth`) are respected even during restarts.

### Configuration Reference

| Setting | Description | Default |
|---------|-------------|---------|
| `RESEARCH_MODE` | `"single"` or `"dtor"` | `single` |
| `MAX_BRANCHES` | Number of perspectives generated at diversification | `3` |
| `MAX_BRANCH_DEPTH` | Maximum depth of each branch | `3` |
| `NODES_PER_BRANCH` | Research node budget per branch | `100` |

Set these in `.env`, pass `-c key value` overrides on the CLI, or adjust via LangGraph Studio.

### Visualising Branch Progress
- LangGraph Studio renders each branch as it executes, so you can observe diversification, branch routing, and synthesis steps.
- Logs under `logs/` mirror the same structure: `analysis_*.log`, `routing_*.log`, `finalize_*.log`, etc. Use them when running headless to see which branch is active and why routing decisions were made.

### When To Use DToR vs Single Path
- Choose **Deep Tree of Research** when the topic benefits from multiple perspectives (e.g., surveying competing materials, comparing research schools, or planning multi-step investigations). DToR automatically re-enters branches to close knowledge gaps and resolves contradictions in the final synthesis.
- Choose the **single-path loop** when the request is narrow, you need a quick high-level summary, or compute resources are limited. The single-path mode still iterates via reflection but avoids the overhead of branch management.

### Running DToR
- Studio: set `research_mode` to `"dtor"` and watch the tree evolve in the UI.
- CLI: `python run_batch.py "topic" -c research_mode dtor`.
- Cluster mode: `dtor_orchestration_cs_cluster/run_batch_cluster.py` (CS cluster) or `dtor_orchestration_dsi_cluster/run_batch_cluster.py` (DSI cluster) supports staged execution (`run_diversify_only.py` for Stage 1 and SLURM-friendly wall-time checkpoints).

### Logging and Checkpointing
- `setup_logging()` in `dtor_nodes` creates per-run log files (analysis, query generation, routing, finalisation, reflection) under `logs/`. The same helper is reused by single-path runs for consistency.
- `graph.step_timeout = 86400` on all compiled graphs to prevent LangGraph from cancelling multi-hour research automatically.
- `dtor_orchestration_cs_cluster/run_batch_cluster.py` (CS cluster) and `dtor_orchestration_dsi_cluster/run_batch_cluster.py` (DSI cluster) provide wall-time aware execution: they track topics, monitor signals (`SIGUSR1` checkpoint, `SIGUSR2` status), and gracefully terminate before SLURM/PBS limits via `grace_period_minutes`.
- `dtor_orchestration_*/run_diversify_only.py` supports staging: first diversify to produce perspectives, then later jobs run Stage 2/3 against stored branches.

## Additional Workflows

### Code Improvement Researcher
`code_improvement_graph.py` reuses the single-path graph to support an ML code-review workflow:
1. Analyse user-provided code and context.
2. Generate a research topic and call the deep research graph for background.
3. Produce a concise revision plan.
4. Regenerate code based on the plan.
5. Save plan and code artefacts to `code_improvement_output/`.

This demonstrates how other applications can embed `graph` or the DToR subgraph while leveraging the same configuration, failover, and logging infrastructure.

## Running the Workflows
- **Studio**: launch with `langgraph dev` and pick the appropriate graph. Configure provider, search, mode, and modality toggles through the UI.
- **Headless / CLI**:
  ```bash
  python run_batch.py "topic" -c research_mode dtor -c max_web_research_loops 4

  # CS cluster (yuxinchen-contrib partition)
  python dtor_orchestration_cs_cluster/run_batch_cluster.py --topics-file research_topics.txt --wall-time 3.5

  # DSI cluster (ai+s partition)
  python dtor_orchestration_dsi_cluster/run_batch_cluster.py --topics-file research_topics.txt --wall-time 3.5
  ```
  All commands honour `.env` defaults and accept `-c key value` overrides.

Refer to `docs/MODALITY_RAG.md` for a detailed breakdown of modality retrieval and to `docs/SYSTEM_OVERVIEW.md` for module-level architecture.
