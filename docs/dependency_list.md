# Dependency List

This document lists all dependencies for the Local Deep Researcher project, organized by dependency groups as defined in `pyproject.toml`.

## Python Version Requirement

- **Python**: >=3.9 (Python 3.11+ recommended)

## Core Dependencies

These are the required dependencies installed with `pip install -e .`:

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `langgraph` | ==0.3.21 | LangGraph framework for building stateful LLM applications |
| `langgraph-checkpoint-sqlite` | (latest) | SQLite checkpointing for LangGraph |
| `langchain-community` | ==0.3.20 | Community integrations for LangChain |
| `langchain-core` | ==0.3.76 | Core LangChain abstractions |
| `langchain-chroma` | ==0.2.6 | ChromaDB integration for LangChain |
| `langchain-huggingface` | ==0.3.1 | HuggingFace model integration |
| `langchain-ollama` | ==0.3.8 | Ollama LLM integration |
| `langchain-openai` | ==0.3.11 | OpenAI API integration |
| `tavily-python` | >=0.5.0 | Tavily search API client |
| `ddgs` | >=9.5.5 | DuckDuckGo search client |
| `openai` | >=1.12.0 | OpenAI Python SDK |
| `httpx` | >=0.28.1 | HTTP client library |
| `markdownify` | >=0.11.0 | HTML to Markdown converter |
| `python-dotenv` | ==1.0.1 | Environment variable management |
| `sentence-transformers` | ==4.0.0 | Sentence embeddings and transformers |
| `chromadb` | ==1.0.21 | Vector database for embeddings |
| `peft` | ==0.15.1 | Parameter-Efficient Fine-Tuning library |

## Optional Dependencies

### Development Tools (`dev`)

Install with: `pip install -e '.[dev]'`

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `mypy` | ==1.11.1 | Static type checker |
| `ruff` | ==0.6.1 | Fast Python linter and formatter |

### UI Integration (`ui`)

Install with: `pip install -e '.[ui]'`

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `chainlit` | >=2.0.0 | Chainlit UI framework for LLM applications |
| `arize-phoenix` | (latest) | Arize Phoenix observability platform |
| `openinference-instrumentation-langchain` | (latest) | OpenInference instrumentation for LangChain |

### Documentation Build (`docs`)

Install with: `pip install -e '.[docs]'`

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `jupyter-book` | ==1.0.2 | Sphinx-based Jupyter Book release compatible with `_config.yml` / `_toc.yml` |
| `sphinx` | >=7.0.0 | Core documentation engine |
| `myst-parser` | >=2.0.0 | MyST Markdown parser used by Sphinx |
| `sphinx-book-theme` | >=1.0.0 | Theme used for the documentation |
| `sphinx-design` | >=0.5.0 | Design components (cards, tabs) |

> `jupyter-book` is pinned to the last Sphinx-based release to avoid the new MyST Build pipeline (v2+) that requires a different project layout and triggers the `EISDIR` error when used with this book.

### FET RAG Support (`fet_rag`)

Install with: `pip install -e '.[fet_rag]'`

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `chromadb` | >=0.4.0 | Vector database (also in core deps) |
| `langchain-chroma` | >=0.1.0 | ChromaDB integration (also in core deps) |
| `langchain-huggingface` | >=0.0.1 | HuggingFace integration (also in core deps) |
| `sentence-transformers` | >=2.0.0 | Sentence embeddings (also in core deps) |
| `transformers` | >=4.30.0 | HuggingFace Transformers library |
| `langchain` | >=0.1.0 | Core LangChain library |
| `langchain-community` | >=0.0.1 | Community integrations (also in core deps) |
| `langchain-core` | >=0.1.0 | Core abstractions (also in core deps) |
| `numpy` | >=1.20.0 | Numerical computing library |
| `pandas` | >=1.3.0 | Data manipulation library |
| `tqdm` | >=4.60.0 | Progress bar library |

**Note**: Some packages in `fet_rag` are also in core dependencies. This is intentional for completeness and to allow standalone FET RAG installations.

## Build System Requirements

| Package | Version Constraint | Description |
|---------|-------------------|-------------|
| `setuptools` | >=73.0.0 | Package building and distribution |
| `wheel` | (latest) | Built package format |

## Installation Examples

### Basic Installation
```bash
pip install -e .
```

### With UI Support
```bash
pip install -e '.[ui]'
```

### With FET RAG Support
```bash
pip install -e '.[fet_rag]'
```

### With Development Tools
```bash
pip install -e '.[dev]'
```

### All Optional Dependencies
```bash
pip install -e '.[dev,ui,fet_rag]'
```

## Transitive Dependencies

The packages listed above have their own dependencies (transitive dependencies) that will be automatically installed. The full dependency tree can be viewed with:

```bash
pip show <package-name>
```

Or generate a full dependency list:
```bash
pip freeze > requirements_full.txt
```

## Version Pinning

- **Core dependencies**: Most are pinned to specific versions for reproducibility
- **Optional dependencies**: Some use `>=` constraints for flexibility
- **Transitive dependencies**: Managed automatically by pip

For production deployments, consider using `pip-tools` or `pip-compile` to generate fully pinned requirement files.
