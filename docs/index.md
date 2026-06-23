---
title: Local Deep Researcher Documentation
description: A LangGraph-based research assistant for iterative web research
---

# Local Deep Researcher Documentation

Local Deep Researcher is a LangGraph-based research assistant that performs iterative web research and optional local retrieval, running entirely on user-controlled infrastructure. It prioritizes local LLM hosts (Ollama or LMStudio), gracefully falls back to OpenAI when permitted, and can execute either a linear "single path" investigation or a multi-branch Deep Tree of Research (DToR) exploration.

## What is Local Deep Researcher?

Local Deep Researcher is a resilient research assistant that:

- **Runs locally** with Ollama or LMStudio (or falls back to OpenAI)
- **Performs iterative research** through web search and local RAG
- **Supports two modes**: single-path research for focused investigations, or Deep Tree of Research (DToR) for multi-branch exploration
- **Integrates with LangGraph Studio** for interactive debugging and state inspection
- **Provides production workflows** with SQLite checkpoints and cluster-ready orchestration

The agent fans out to web search (DuckDuckGo, SearXNG, Tavily, Perplexity), optionally pulls from local vector stores, and keeps iterating until the topic is covered.

## Installation

The package uses `pyproject.toml` for dependency management. Install with pip:

### Basic Installation

pip install -e .### With Optional Features

# UI Integration (Chainlit + Phoenix)
pip install -e '.[ui]'

# FET RAG Support
pip install -e '.[fet_rag]'

# Development Tools
pip install -e '.[dev]'

# All optional dependencies
pip install -e '.[dev,ui,fet_rag]'See the [Dependency List](dependency_list.md) for complete dependency information.

## Quick Start

1. **Install the package:**ash
   pip install -e '.[ui]'  # With UI support

2. **Start Ollama** (or configure LMStudio/OpenAI)

3. **Run research:**
   - **LangGraph Studio**: `langgraph dev`
   - **CLI**: `python src/ollama_deep_researcher/dtor_cli.py -m single -t "your topic"`
   - **Chainlit UI**: `chainlit run src/ollama_deep_researcher/chainlit_app.py`

## Key Features

- **LLM flexibility**: Ollama or LMStudio by default, with automatic fallback to OpenAI if permitted
- **Two research modes**: linear loop for quick digs, DToR (Deep Tree of Research) for broad, multi-branch studies
- **Search & RAG plug-ins**: swap web backends, query FET sensor data/code/papers stored in Chroma
- **LangGraph Studio integration**: inspect state, resume runs, and debug with structured logs
- **Headless & production workflows**: CLI with SQLite checkpoints plus cluster-ready orchestration scripts
- **Artifact trail**: per-iteration logs, branch syntheses, final reports, and optional FET fabrication parameters

## Getting Help

- Check the [README](https://github.com/ruiding-uchicago/DToR_deep_research/blob/main/README.md) for installation and basic usage
- Review the [Troubleshooting](https://github.com/ruiding-uchicago/DToR_deep_research/blob/main/README.md#troubleshooting-highlights) section
- Explore the [examples](https://github.com/ruiding-uchicago/DToR_deep_research/tree/feature/cli-package/examples) directory for usage examples

## Contributing

Contributions that improve stability, documentation, or add new modalities are welcome! See the main [README](../README.md) for more information.
