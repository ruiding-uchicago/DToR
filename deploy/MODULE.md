# Using DToR as a library

```python
from ollama_deep_researcher import run_research

result = run_research(
    "Solid-state electrolytes for lithium metal batteries",
    api_key="sk-...",              # or set OPENAI_API_KEY
    model="gpt-5.6-luna",
    branches=3, depth=2, loops=2,
    search_api="tavily",
)

print(result.report)               # str  — the final integrated report
print(result.branch_summaries)     # {perspective: synthesis}
print(result.elapsed_seconds)
```

`run_research` returns a `ResearchResult` and raises `ValueError` on bad
arguments or `DToRError` when the graph finishes without a report.

## Progress reporting

A run takes 10-30 minutes, so pass `on_progress` to show the user what is
happening instead of a spinner:

```python
def report(event):
    # push to a websocket, write to Redis, update a DB row, ...
    print(event)                     # "[ 142.7s] branch 1/3 - searching the web"
    print(event.stage,               # "web_research" (raw node name)
          event.branches_completed,  # 1
          event.branches_total,      # 3
          event.research_nodes_done, # 4
          event.elapsed_seconds)     # 142.7

run_research(topic, on_progress=report, ...)
```

The callback fires as each graph node finishes — roughly 45-90 times per dtor
run. Exceptions raised inside it are swallowed, so a broken progress sink can
never fail the research job. `event.stage` is the raw LangGraph node name and
is the stable field to switch on; `event.label` is prose for humans and may be
reworded.

## Arguments

| Argument | Default | Meaning |
|---|---|---|
| `topic` | — | the research question (required) |
| `mode` | `"dtor"` | `"dtor"` = branching tree, `"single"` = linear loop |
| `api_key` | `$OPENAI_API_KEY` | OpenAI key |
| `model` | `$OPENAI_MODEL` → `gpt-5.6-luna` | model id |
| `fallback_models` | — | models to try if the primary fails |
| `branches` | 3 | perspectives to explore (dtor) |
| `depth` | 2 | maximum branch depth (dtor) |
| `loops` | 2 | search/reflect iterations per research node |
| `nodes_per_branch` | 20 | node budget per branch (dtor); keep >= 10 |
| `search_api` | `duckduckgo` | `tavily` / `duckduckgo` / `perplexity` / `searxng` |
| `fetch_full_page` | `False` | fetch full pages instead of snippets — costs tokens |
| `use_local_rag` | `False` | enable local retrieval (needs the RAG extras) |
| `extra_env` | — | escape hatch for settings without a named argument |
| `recursion_limit` | 300 | LangGraph step ceiling |
| `thread_id` | derived from topic | checkpoint identity |
| `on_progress` | — | callback invoked with a `ProgressEvent` per completed node |

Any argument left as `None` falls back to its environment variable, then to
the default above.

## Adding RAG later

The API keeps local retrieval off by default. To turn it on once vector stores
exist, no code change is needed:

```python
run_research(
    topic,
    use_local_rag=True,
    extra_env={
        "ENABLE_PAPER_RETRIEVAL": "true",
        "PAPER_VECTOR_PATH": "/data/paper_vectorstore",
        "PAPER_RESULTS_COUNT": "5",
        "EMBEDDING_MODEL": "BAAI/bge-m3",
    },
)
```

That path additionally requires the heavy extras (`pip install -e '.[fet_rag]'`
— torch, chromadb, sentence-transformers), which `deploy/requirements.txt`
deliberately omits.

## Behaviour worth knowing

- **Blocking and sequential.** One dtor run is ~200 LLM calls over 10-30 minutes
  in the calling thread. Run it in a worker/queue, not in a request handler.
  `on_progress` is the hook for feeding a status endpoint while it runs.
- **Per-call settings, no global state.** Configuration is applied to
  `os.environ` for the duration of the call and restored afterwards, because
  `Configuration` reads the environment and lets it win over the config dict.
  Consequence: `run_research` is **not thread-safe** — concurrent calls in one
  process would fight over the environment. Use separate processes.
- **Side effects on disk.** Branch and final reports are written under
  `synthesis_branches_and_final/<topic>/`, logs under `logs/`, both relative to
  the current working directory.
- **`sources` is usually empty in dtor mode.** The graph deliberately discards
  per-node sources when branching, to stop them accumulating across branches.
