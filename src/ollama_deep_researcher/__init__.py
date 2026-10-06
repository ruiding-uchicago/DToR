version = "0.0.1"

# Public programmatic entry point. Kept import-light on purpose: pulling in the
# graphs here would build them (and create logs/) at import time.
from ollama_deep_researcher.api import ResearchResult, DToRError, run_research

__all__ = ["run_research", "ResearchResult", "DToRError", "version"]
