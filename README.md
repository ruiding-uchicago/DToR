# Local Deep Researcher ⚙️📚

Local, resilient research assistant built on LangGraph. Install [Ollama](https://ollama.com/download) (or bring your own OpenAI-compatible host such as LMStudio), then the agent fans out to web search (DuckDuckGo, SearXNG, Tavily, Perplexity), optionally pulls from local vector stores, and keeps iterating until the topic is covered. Choose between a focused single-path loop or a Deep Tree of Research (DToR) exploration that manages multiple perspectives in parallel, culminating in a consolidated deep research report.

## What you get ✨
- **LLM flexibility:** Ollama or LMStudio by default, with automatic fallback to OpenAI if permitted.
- **Two research modes:** linear loop for quick digs, DToR (Deep Tree of Research) for broad, multi-branch studies.
- **Search & RAG plug-ins:** swap web backends, query FET sensor data/code/papers stored in Chroma, or fall back to legacy stores.
- **LangGraph Studio integration:** inspect state, resume runs, and debug with structured logs.
- **Headless & production workflows:** CLI with SQLite checkpoints plus cluster-ready orchestration scripts.
- **Artifact trail:** per-iteration logs, branch syntheses, final reports, and optional FET fabrication parameters.

## Installation 📦

The package uses `pyproject.toml` for dependency management. Install with pip:

### Basic Installation

Install the core package with all required dependencies:

```bash
pip install -e .
```

### Optional Dependencies

Install additional features using optional dependency groups:

**UI Integration (Chainlit + Phoenix):**
```bash
pip install -e '.[ui]'
```
Includes: `chainlit`, `arize-phoenix`, `openinference-instrumentation-langchain`

**FET RAG Support:**
```bash
pip install -e '.[fet_rag]'
```
Includes: additional vector store dependencies, transformers, numpy, pandas, tqdm

**Development Tools:**
```bash
pip install -e '.[dev]'
```
Includes: `mypy`, `ruff` for type checking and linting

**Combine Multiple Groups:**
```bash
# UI + FET RAG
pip install -e '.[ui,fet_rag]'

# All optional dependencies
pip install -e '.[dev,ui,fet_rag]'
```

### Prerequisites

- **Python 3.9+** (Python 3.11+ recommended)
- **Ollama** or **LMStudio** (or OpenAI API key) for LLM inference
- For FET RAG: vector stores configured (see [`docs/MODALITY_RAG.md`](docs/MODALITY_RAG.md))

Documentation lives under [`docs/`](docs). Start with:
- [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md) – architecture map, modules, state objects, failover behavior.
- [`docs/RESEARCH_WORKFLOWS.md`](docs/RESEARCH_WORKFLOWS.md) – single-path loop, DToR routing, batching scripts.
- [`docs/MODALITY_RAG.md`](docs/MODALITY_RAG.md) – configuration and query tips for FET/code/paper retrieval.

## Workstation workflow (LangGraph Studio) 💻
1. **Configuration:** copy `.env.example` → `.env` only if you need repeatable server settings. On laptops you can leave it out and use the Studio UI—remember that environment variables always override UI values.
2. **Raise the file limit:** heavy RAG, especially FET stores, can exhaust descriptors. On macOS/Linux run `ulimit -n 1048575` before launching.
3. **Start Studio:**
   ```bash
   uvx --refresh --from "langgraph-cli[inmem]==0.1.89" --with-editable . --python 3.11 langgraph dev
   ```
4. **Sign in first:** click the LangSmith icon in the top-left as soon as the UI opens. Submitting a run while logged out triggers a redirect that looks like a stalled workflow.
5. **Pick your graph:** `ollama_deep_researcher` for the single loop, `deep_researcher_dtor` for Deep Tree of Research.
6. **Configure & run:** adjust settings in Studio (or let `.env` drive them), enter a topic, and launch.

> 🕹️ Running DToR unattended? Keep the terminal closed and start `python auto_continue.py`. It watches the logs and auto-clicks “Continue” whenever Studio pauses for confirmation.

## Batch & production options 🚀
- **Headless CLI:**
  ```bash
  python run_batch.py "llama quantization techniques" \
    -c research_mode dtor -c max_branches 3 -c max_branch_depth 2
  ```
  Outputs stream to stdout and are saved in `synthesis_branches_and_final/` plus `logs/`.
- **Cluster orchestration:**
  - **DToR mode (multi-branch research):**
    - `dtor_orchestration_cs_cluster/run_batch_cluster.py` runs DToR with SQLite checkpoints, wall-time awareness, and signal hooks for SLURM/PBS (CS cluster).
    - `dtor_orchestration_dsi_cluster/run_batch_cluster.py` runs DToR on the DSI cluster with appropriate partition and environment settings.
    - `dtor_orchestration_*/run_diversify_only.py` (Stage 1) precomputes perspectives so later jobs can focus on branch execution.
  - **Single mode (parallel simple research):**
    - `single_cs_cluster/submit_all_single_parallel.sh` submits multiple topics as independent single-mode jobs (CS cluster).
    - `single_cs_cluster/submit_single_topic.sh` runs one topic in single mode (no checkpointing, faster execution).
  Both respect the same `.env` used locally—prototype in Studio, ship to the cluster with the same settings.

## Configuration cheat sheet 🧭
Priority: **environment** → **Studio overrides** → **code defaults** (`Configuration` class).

Key toggles:
- `LLM_PROVIDER`, `LOCAL_LLM`, `OLLAMA_BASE_URL`, `LMSTUDIO_BASE_URL`
- `SEARCH_API` + API keys (`TAVILY_API_KEY`, `PERPLEXITY_API_KEY`, `SEARXNG_URL`)
- `RESEARCH_MODE`, `MAX_WEB_RESEARCH_LOOPS`, `MAX_BRANCHES`, `MAX_BRANCH_DEPTH`
- RAG flags: `USE_LOCAL_RAG`, `ENABLE_FET_RAW_DATA`, `ENABLE_CODE_RETRIEVAL`, `ENABLE_PAPER_RETRIEVAL`
- FET settings: vector store paths, top-k values, embedding model (`BAAI/bge-m3` by default)

## Reproducible local paper RAG 📚
Want to exercise the paper-retrieval modality (`paper_vector_path`) end-to-end without the full ≈1.3M-paper corpus? [`examples/local_rag_build/`](examples/local_rag_build/) ships **973 license-cleared open-access (CC-BY/CC0) papers** plus the exact build pipeline — clean (`EnhancedAcademicTextCleaner`) → `RecursiveCharacterTextSplitter(2500/500)` → `BAAI/bge-m3` → Chroma — that mirrors production. Run `01_sanitize.py` → `02_build_rag.py` → `03_verify.py`, then point `PAPER_VECTOR_PATH` at the resulting store. Provenance and per-paper licenses are in its [`manifest.csv`](examples/local_rag_build/manifest.csv) / [`LICENSE_AUDIT.csv`](examples/local_rag_build/LICENSE_AUDIT.csv); see the [example README](examples/local_rag_build/README.md).

## Outputs & logs 🗃️
- `logs/` – analysis, query generation, routing, reflection, finalisation logs per run.
- `synthesis_branches_and_final/<topic>/` – DToR branch syntheses and final merged reports.
- Studio UI – interactive state tree and checkpoints.

## Troubleshooting highlights 🛠️
- Studio won’t open? copy the printed URL (usually `http://127.0.0.1:2024`).
- Forced login mid-run? sign in via the LangSmith icon before submitting.
- Slow or timing out? disable `FETCH_FULL_PAGE`, drop `MAX_WEB_RESEARCH_LOOPS`, or switch to a faster model.
- JSON parsing hiccups? the agent already strips code fences, but switching models or tightening prompts can help.
- LMStudio/Ollama errors? verify the local server is running and the model is pulled.

## Repo layout 🗂️
```
src/ollama_deep_researcher/
  configuration.py      # Pydantic config schema & env merge logic
  graph.py              # Single-path research loop
  dtor_graph.py          # Deep Tree of Research wrapper graph
  dtor_nodes.py          # DToR node logic (diversify, analyse, route, synthesise)
  state.py / dtor_state.py  # Dataclasses for graph state
  utils.py              # Search adapters, RAG helpers, formatting utilities
  prompts.py            # Prompt templates (single + FET-specific)
  lmstudio.py, openai_wrapper.py  # Model wrappers
run_batch.py            # Headless CLI entrypoint
dtor_orchestration_cs_cluster/   # CS cluster DToR orchestration (yuxinchen-contrib partition)
dtor_orchestration_dsi_cluster/  # DSI cluster DToR orchestration (ai+s partition)
single_cs_cluster/      # CS cluster single-mode parallel jobs
auto_continue.py        # Studio auto-click helper for long DToR runs
examples/local_rag_build/  # Reproducible CC-BY local paper-RAG example (clean→chunk→bge-m3→Chroma)
docs/                   # Deep-dive documentation
```

## License
MIT — see [`LICENSE`](LICENSE).

## Thanks
- Built with LangGraph/LangChain and a collection of community search libraries.
- Contributions that improve stability, docs, or new modalities are welcome!

<sub><i>This work is partially inspired by <a href="https://github.com/langchain-ai/local-deep-researcher">langchain-ai/local-deep-researcher</a>.</i></sub>

# Docker Image

## CLI Docker

1. Build the image: `docker build -t dtor-cli:latest -f Dockerfile-cli .`

2. Run the research task:

```bash
docker run --rm \
    -v ./output:/app/output \
    -e USE_LOCAL_RAG=false \
    dtor-cli:latest \
    -m single \
    -t "<your research topic>" \
    -o /app/output
```

If Ollama runs on the host, `use host.docker.internal`:

```bash
docker run --rm \
    -v ./output:/app/output \
    --add-host=host.docker.internal:host-gateway \
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
    -e USE_LOCAL_RAG=false \
    dtor-cli:latest \
    -m single \
    -t "<your research topic>" \
    -o /app/output
```

## Docker Compose

1. Build the image: `docker-compose -f docker-compose-cli.yml build`

2. Run the research task:

```bash
docker-compose -f docker-compose-cli.yml run --rm dtor-cli \
  -m single \
  -t "<your research topic>" \
  -o /app/output
```

## UI Docker

1. Build and start services: `docker-compose -f docker-compose-ui.yml up --build`

Access the UIs:
Chainlit: http://localhost:8000
Phoenix: http://localhost:6006

2. Environment variables - Create a .env file in the project root:

```bash
# .env
PHOENIX_ENABLED=true
OLLAMA_BASE_URL=http://host.docker.internal:11434
USE_LOCAL_RAG=false
LLM_PROVIDER=ollama
LOCAL_LLM=gpt-oss:20b
```

3. (Optional) Run in detached mode: `docker-compose -f docker-compose-ui.yml up -d`

4 View logs:

```bash
# All services
docker-compose -f docker-compose-ui.yml logs -f

# Specific service
docker-compose -f docker-compose-ui.yml logs -f chainlit
docker-compose -f docker-compose-ui.yml logs -f phoenix
```

5. Stop services: `docker-compose -f docker-compose-ui.yml down`

# Documentation

A GitHub Pages site is located at `docs` and there is a GitHub action workflow which publishes site content whenever a change is made to the `docs` directory on the `main` branch.

Commands to build locally:

```bash
# Install the deps
pip install -e '.[docs]'

# Build to docs
cd docs
jupyter book build --html --strict

# Or if using the new format:
jupyter book start
```