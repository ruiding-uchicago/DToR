# DToR — API-only deployment playbook

Run DToR as a module inside another team's portal: **OpenAI API backend
(`gpt-5.6-luna`), local RAG off, no Ollama, no GPU, no Docker.**
Ships the Chainlit UI and optional Phoenix tracing.

Two ways to consume it:
- **As a library** — `from ollama_deep_researcher import run_research`.
  See [MODULE.md](MODULE.md).
- **As a chat UI** — Chainlit, per the install below.

Everything below was executed and verified on 2026-08-18 (Python 3.12, macOS)
from a clean venv, **including a live run against the real `gpt-5.6-luna` API
and real Tavily search**. Numbers are measured, not estimated.

Live run: topic *"PFAS detection using 2D-material FET biosensors"*, 2 branches
× depth 1 → **582 s, 16 Tavily searches, 19,949-character final report**, 2
branch syntheses + 1 final report on disk. The model returned clean JSON at
every structured step; no fallback triggered.

---

## Install

```bash
git clone <this repo> dtor && cd dtor
python3 -m venv .venv && source .venv/bin/activate
pip install -r deploy/requirements.txt          # ~331 MB, ~2 min

git apply deploy/0001-portal-mode-default.patch # REQUIRED, see below

cp deploy/env.example deploy/.env               # fill OPENAI_API_KEY + TAVILY_API_KEY
PYTHONPATH=src python deploy/smoke_test.py      # must print ALL CHECKS PASSED
./deploy/run.sh
```

Chainlit → http://127.0.0.1:8000

`smoke_test.py` needs no API key and no network: it mocks the LLM and the
search backend and drives a real DToR graph to a final report. Hand it to the
receiving team as the acceptance gate.

---

## Why `pip install -e .` is not used

The repo's `pyproject.toml` puts `torch`, `chromadb`, `sentence-transformers`
and `peft` in the **core** dependencies — roughly 3 GB — even though none of
them execute once local RAG is off. `deploy/requirements.txt` is the pruned
set. Verified absent from the working install:

```
[PASS] torch not installed
[PASS] chromadb not installed
[PASS] sentence_transformers not installed
[PASS] transformers not installed
```

Measured venv sizes:

| Profile | Size | Notes |
|---|---|---|
| `pip install -e '.[ui]'` (upstream) | ~3 GB | torch + chromadb + transformers |
| **`deploy/requirements.txt`** | **331 MB** | what this playbook ships |
| same + 4 lazy-import edits | 254 MB | see "Going leaner" |
| Phoenix **server** (separate venv) | 792 MB | never install into the app venv |

`langchain-community` (92 MB) is still present only to satisfy three imports in
`utils.py` that never execute on this path. It does **not** pull torch.

---

## The required patch

`0001-portal-mode-default.patch` is not optional. Chainlit derives the research
mode from the message text, and that silently overrides `RESEARCH_MODE`.
Verified on unpatched source, with `RESEARCH_MODE=dtor` exported:

```
parse_user_input("PFAS sensing with 2D materials") -> mode='single'
```

Every portal request would run single-path and never branch. After the patch,
`RESEARCH_MODE` is the default and typing `dtor` / `single` still overrides
per request. `smoke_test.py` check 3 enforces this.

---

## Phoenix tracing (optional)

The app needs only the OTel client (`arize-phoenix-otel`, 1 MB, already in
`requirements.txt`). The **server** is 792 MB with pandas and SQLAlchemy — keep
it in its own venv:

```bash
python3 -m venv .venv-phoenix
./.venv-phoenix/bin/pip install arize-phoenix
./deploy/run.sh --with-phoenix          # starts the server, then Chainlit
```

Phoenix → http://127.0.0.1:6006 (takes ~35 s on first boot)

Verified: one DToR run produced a trace of 60+ spans in project `dtor`, with
per-node names (`init_session`, `local_rag_research`, `web_research`,
`summarize_local_rag_results`, `ChatOpenAIWrapper`, …).

**Never expose port 6006.** Phoenix has no authentication. Reach it via
`ssh -L 6006:127.0.0.1:6006 user@host`.

---

## Mounting into the portal

Chainlit needs a WebSocket upgrade:

```nginx
location /research/ {
    proxy_pass         http://127.0.0.1:8000/;
    proxy_http_version 1.1;
    proxy_set_header   Upgrade    $http_upgrade;
    proxy_set_header   Connection "upgrade";
    proxy_set_header   Host       $host;
    proxy_read_timeout 3600s;      # a DToR run takes 10-30 min
}
```

Serving under a subpath also needs `--root-path /research` on the `chainlit run`
line in `run.sh`. Run under systemd/supervisor for restarts.

---

## Known limits (verified, tell the receiving team)

- **No checkpointing.** `chainlit_app.py` builds the graph with
  `checkpointer=None`. A browser refresh loses the run; reports still land in
  `output/` and `synthesis_branches_and_final/`.
- **Single-process concurrency.** One DToR run is ~200 sequential LLM calls over
  10-30 min in-process. N users = N concurrent runs in one worker. Put a queue
  in front before opening it to a real audience.
- **Chainlit ignores `.env`.** It never calls `load_dotenv()`; `run.sh` sources
  the file and exports explicitly. Don't invoke `chainlit run` by hand and
  expect `.env` to apply.
- **Phoenix shows no token counts or cost.** `openai_wrapper.py` returns no usage
  metadata. Node tree, prompts and latency are fine.
- **No web-search spans.** `utils.py` search functions use LangSmith
  `@traceable`, not OpenTelemetry.
- **Topic mangling.** `parse_user_input` strips the substrings `single` / `dtor` /
  `deep tree` out of the topic text itself. Cosmetic.

## Verify DToR actually branched

`gpt-5.6-luna` supports structured outputs, but `openai_wrapper.py` sends only
`model` and `input` — the parameter never reaches the API, so JSON parsing is
prompt-only. **In the live run this was fine**: the model returned strict JSON
and produced genuinely differentiated perspectives, e.g.

```
- Selective Biorecognition and Anti-Fouling Interfaces
- 2D-Material FET Device Physics and Signal Optimization
- Field Deployment, Environmental-Matrix Validation, and Multiplexed Monitoring
```

It is still prompt-only, so on a parse failure `diversify_initial_query` falls
back to three hardcoded perspectives. Spot-check after the first real run:

```bash
grep -i "Creating branch" logs/dtor_nodes_*.log
```

Literally `Technical Analysis` / `Application Focus` / `Comparative Study` means
it degraded — the tree collapsed into one question asked three times.

---

## Core fixes carried on this branch

Two real bugs were found while verifying against the live API and are fixed in
`src/` on the `dtor-module` branch. A 96-configuration stress grid over
branches x depth x budget x gap-count went from **66 failures to 0**.

**1. Router branch-switch deadlock.** `route_next_action` assigned
`state.active_branch_id` when it wanted to switch branches, but a LangGraph
conditional edge consumes only the *return value* — the mutation was discarded.
If branch A exhausted its budget while branch B still had pending nodes, the
router kept selecting B while `research_node` kept receiving A, which had
nothing to do: `GraphRecursionError` after 300 idle steps. The router now
returns `select_next_branch` (a real node, so the switch persists), and
`select_next_branch` only keeps the current branch while it still has
actionable work.

**2. Runs ending with no final report.** `route_next_action` treated a branch
with a summary as complete, while `synthesize_final_report` required
`is_complete` — so the graph reached the end and returned nothing.
`synthesize_branch` now marks the branch complete when it writes the summary.

Also: `branch_summaries` is surfaced through `DToRStateOutput`, so callers get
per-branch syntheses instead of only the merged report.

The `NODES_PER_BRANCH >= 10` check in `smoke_test.py` is kept as a quality
guard — a starved branch still contributes little — but it is no longer
load-bearing for correctness.

## Going leaner (optional, 331 → 254 MB)

Making four imports lazy drops `langchain-community`, `langchain`,
`langchain-openai` and `langchain-ollama`. Verified working (same end-to-end
result, Chainlit boots), but it is four edits against upstream:

| File | Change |
|---|---|
| `utils.py:14-17` | move `SearxSearchWrapper` / `HuggingFaceEmbeddings` / `Chroma` / `Document` into the functions that use them |
| `dtor_nodes.py:41` | move `ChatOllama` into `get_llm()` |
| `lmstudio.py:12` | `ChatOpenAI` base → `BaseChatModel` (LMStudio is unused here) |
| `chainlit_app.py:39` | `langchain.schema.runnable.config` → `langchain_core.runnables` |

77 MB for four points of divergence from upstream. Not worth it unless image
size is a hard constraint — the default profile keeps the repo untouched apart
from the one required patch.
