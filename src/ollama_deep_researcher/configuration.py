import os
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, Literal, List, Union

from langchain_core.runnables import RunnableConfig
default_config_long_recursion = RunnableConfig(recursion_limit=300)

###
class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"

class Configuration(BaseModel):
    """The configurable fields for the research assistant."""

    max_web_research_loops: int = Field(
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform"
    )
    local_llm: str = Field(
        default="gpt-oss:20b",
        title="LLM Model Name",
        description="Name of the LLM model to use"
    )
    llm_provider: Literal["ollama", "lmstudio", "openai"] = Field(
        default="ollama",
        title="LLM Provider",
        description="Provider for the LLM (Ollama, LMStudio, or OpenAI)"
    )
    search_api: Literal["perplexity", "tavily", "duckduckgo", "searxng"] = Field(
        default="duckduckgo",
        title="Search API",
        description="Web search API to use"
    )
    fetch_full_page: bool = Field(
        default=True,
        title="Fetch Full Page",
        description="Include the full page content in the search results"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/",
        title="Ollama Base URL",
        description="Base URL for Ollama API"
    )
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        title="LMStudio Base URL",
        description="Base URL for LMStudio OpenAI-compatible API"
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses"
    )
    use_local_rag: bool = Field(
        default=True,
        title="Use Local RAG",
        description="Whether to use local vector store for RAG before web search"
    )
    enable_web_search: bool = Field(
        default=True,
        title="Enable Web Search",
        description="Whether to perform web searches (similar to use_local_rag)"
    )
    vector_store_paths: Optional[List[str]] = Field(
        default=None,
        title="Vector Store Paths (Legacy)",
        description="[DEPRECATED - Use paper_vector_path instead] Legacy paths to local vector stores"
    )
    embedding_model: str = Field(
        default="BAAI/bge-m3",
        title="Embedding Model",
        description="Embedding model to use for vector store queries"
    )

    # Multi-modal RAG configuration
    enable_fet_raw_data: bool = Field(
        default=False,
        title="Enable FET Raw Data",
        description="Enable FET sensor experimental raw data retrieval (triggers FET-specific processing)"
    )
    fet_excel_path: Optional[str] = Field(
        default="/Users/ruiding/mac_python_folder/MADE_PUBLIC_REPO_snapshot2025/excel_raw_data_vectorization/excel_vectorstore",
        title="FET Excel Vector Store Path",
        description="Path to FET Excel data vector store (used when enable_fet_raw_data is True)"
    )
    local_unstructured_docs_path: Optional[str] = Field(
        default="/Users/ruiding/mac_python_folder/MADE_PUBLIC_REPO_snapshot2025/non_excel_vectorstore",
        title="Local Unstructured Documents Path",
        description="Path to local unstructured/non-Excel documents vector store"
    )
    fet_k_folders: int = Field(
        default=8,
        title="FET Folders to Retrieve",
        description="Number of folders to retrieve in FET hierarchical search"
    )
    fet_k_runs_per_folder: int = Field(
        default=4,
        title="FET Runs per Folder",
        description="Number of runs to retrieve per folder in FET search"
    )
    fet_k_non_excel: int = Field(
        default=3,
        title="FET Non-Excel Results",
        description="Number of non-Excel documents to retrieve in FET search"
    )

    enable_code_retrieval: bool = Field(
        default=False,
        title="Enable Code Retrieval",
        description="Enable code repository retrieval"
    )
    code_vector_path: Optional[str] = Field(
        default="/Users/ruiding/mac_python_folder/code_vectorstore",
        title="Code Vector Store Path",
        description="Path to code repository vector store (used when enable_code_retrieval is True)"
    )
    code_results_count: int = Field(
        default=10,
        title="Code Results Count",
        description="Number of code chunks to retrieve from code vector store"
    )

    enable_paper_retrieval: bool = Field(
        default=False,
        title="Enable Paper Retrieval",
        description="Enable academic paper retrieval"
    )
    paper_vector_path: Optional[str] = Field(
        default="/Users/ruiding/mac_python_folder/langchain_agent/vector_store_5_rand",
        title="Paper Vector Store Path",
        description="Path to academic papers vector store (used when enable_paper_retrieval is True)"
    )
    paper_results_count: int = Field(
        default=5,
        title="Paper Results Count",
        description="Number of chunks to retrieve from academic papers vector store"
    )
    searxng_url: str = Field(
        default="http://localhost:8888",
        title="SearXNG URL",
        description="Base URL for SearXNG instance (used when search_api is 'searxng')"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        title="OpenAI API Key",
        description="API key for OpenAI (required when llm_provider is 'openai')"
    )
    openai_model: str = Field(
        default="gpt-5-nano",
        title="OpenAI Model",
        description="OpenAI model to use (e.g., gpt-5-nano, gpt-5-mini, gpt-5, gpt-4o)"
    )
    openai_fallback_models: Optional[List[str]] = Field(
        default=["gpt-5-nano", "gpt-5-mini", "gpt-5"],
        title="OpenAI Fallback Models",
        description="Additional OpenAI models to try if the primary model fails"
    )
    
    
    # Deep Tree of Research configuration options
    research_mode: Literal["single", "dtor"] = Field(
        default="single",
        title="Research Mode",
        description="Research mode: 'single' for standard research, 'dtor' for Deep Tree of Research"
    )
    max_branches: int = Field(
        default=3,
        title="Max Branches",
        description="Maximum number of branches to explore in Deep Tree of Research mode"
    )
    max_branch_depth: int = Field(
        default=3,
        title="Max Branch Depth",
        description="Maximum depth of each branch in Deep Tree of Research mode"
    )
    nodes_per_branch: int = Field(
        default=100,
        title="Nodes Per Branch",
        description="Budget of research nodes per branch in Deep Tree of Research mode"
    )
    
    @model_validator(mode='before')
    @classmethod
    def parse_vector_store_paths(cls, data: Any) -> Any:
        """Parse vector_store_paths from string to list if needed."""
        if isinstance(data, dict):
            if 'vector_store_paths' in data and isinstance(data['vector_store_paths'], str):
                data['vector_store_paths'] = [
                    path.strip() for path in data['vector_store_paths'].split(',')
                ]
            if 'openai_fallback_models' in data and isinstance(data['openai_fallback_models'], str):
                data['openai_fallback_models'] = [
                    model.strip() for model in data['openai_fallback_models'].split(',') if model.strip()
                ]
        return data
    
    @model_validator(mode='after')
    def validate_local_rag_config(self) -> 'Configuration':
        """Validate that at least one RAG modality is configured when use_local_rag is True."""
        if self.use_local_rag:
            # Check if any modality is enabled
            modalities_enabled = [
                self.enable_fet_raw_data and self.fet_excel_path,
                self.enable_code_retrieval and self.code_vector_path,
                self.enable_paper_retrieval and self.paper_vector_path,
                self.vector_store_paths and len(self.vector_store_paths) > 0  # Legacy fallback
            ]
            
            if not any(modalities_enabled):
                raise ValueError(
                    "When use_local_rag is True, at least one RAG modality must be configured:\n"
                    "- Enable FET data: set enable_fet_raw_data=True and fet_excel_path\n"
                    "- Enable code retrieval: set enable_code_retrieval=True and code_vector_path\n"
                    "- Enable paper retrieval: set enable_paper_retrieval=True and paper_vector_path\n"
                    "- Or provide legacy vector_store_paths"
                )
        return self
    
    @model_validator(mode='after')
    def validate_openai_config(self) -> 'Configuration':
        """Validate that OpenAI API key is provided when llm_provider is 'openai'."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("openai_api_key must be provided when llm_provider is 'openai'")
        return self
    
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        
        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        
        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}
        
        return cls(**values)
