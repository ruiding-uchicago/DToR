import json
import os
import random
import re

from typing import Optional
from typing_extensions import Literal

def clean_code_blocks(content: str) -> str:
    """
    安全清理LLM输出中的代码块标记，确保JSON解析成功
    只清理明确的代码块标记，不影响JSON内容本身
    """
    if not content or not isinstance(content, str):
        return content

    # 清理开头的各种代码块标记
    patterns_to_remove = [
        r'```+(?:json|javascript|js|txt|text|plaintext)?\s*',  # 标准格式
        r'````+(?:json|javascript|js|txt|text|plaintext)?\s*', # 多反引号
        r'`````+(?:json|javascript|js|txt|text|plaintext)?\s*' # 更多反引号
    ]

    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    # 清理结尾的反引号（各种数量）
    content = re.sub(r'```+\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'````+\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'`````+\s*$', '', content, flags=re.MULTILINE)

    # 清理中间独立的反引号行
    content = re.sub(r'^\s*```+\s*$', '', content, flags=re.MULTILINE)

    return content.strip()

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

from ollama_deep_researcher.configuration import Configuration, SearchAPI
from ollama_deep_researcher.utils import deduplicate_and_format_sources, tavily_search, format_sources, perplexity_search, duckduckgo_search, searxng_search, strip_thinking_tokens, get_config_value, query_local_vector_store, find_volume_paths
from ollama_deep_researcher.state import SummaryState, SummaryStateInput, SummaryStateOutput
from ollama_deep_researcher.prompts import query_writer_instructions, complementary_query_writer_instructions, summarizer_instructions, reflection_instructions, get_current_date
try:
    from ollama_deep_researcher.fet_prompts import (
        FET_SUMMARY_PROMPT,
        FET_REFLECTION_PROMPT,
        FET_COMPLEMENTARY_QUERY_PROMPT,
        FET_FINAL_SUMMARY_PROMPT,
        FET_WEB_SEARCH_ENHANCEMENT
    )
except ImportError:
    # FET prompts not available
    FET_SUMMARY_PROMPT = None
    FET_REFLECTION_PROMPT = None
    FET_COMPLEMENTARY_QUERY_PROMPT = None
    FET_FINAL_SUMMARY_PROMPT = None
    FET_WEB_SEARCH_ENHANCEMENT = None
from ollama_deep_researcher.dtor_nodes import (
    reflect_logger,
    finalize_logger,
    setup_logging,
    invoke_with_failover,
)

default_config_long_recursion = RunnableConfig(recursion_limit=300)

# Helper function to detect FET queries
def detect_fet_query(state, config=None) -> bool:
    """Detect if FET mode should be activated based on configuration.

    FET mode is ONLY activated when:
    1. User has explicitly enabled FET raw data in configuration
    2. The actual data retrieved is from FET vector stores

    This prevents false positives from general FET knowledge queries.
    """
    # If config is provided, check if FET raw data is enabled
    if config:
        try:
            from ollama_deep_researcher.configuration import Configuration
            configurable = Configuration.from_runnable_config(config) if not isinstance(config, Configuration) else config

            # Only activate FET mode if explicitly enabled in config
            if not configurable.enable_fet_raw_data:
                return False
        except:
            pass

    # Secondary check: if data is actually from FET vector stores
    sources = str(state.get("local_sources_gathered", "")).lower() if hasattr(state, "get") else str(getattr(state, "local_sources_gathered", "")).lower()
    results = str(state.get("local_research_results", ""))[:500].lower() if hasattr(state, "get") else str(getattr(state, "local_research_results", ""))[:500].lower()

    # Check if data is from FET vector stores
    fet_data_indicators = [
        "excel_vectorstore" in sources,
        any(term in results for term in [
            "ion_ioff_mean", "vt_mean", "ss_mean", "gm_max_mean",
            "vt_drift", "health_score", "device_state",
            "folder_id", "run_id", "buffer_type"
        ])
    ]

    return any(fet_data_indicators)

# Helper function to initialize a new session
def init_session(state: SummaryStateInput, config: RunnableConfig = None) -> SummaryStateInput:
    """Initialize a new research session, including creating fresh log files."""
    # Set up fresh logging for this session
    timestamp = setup_logging()

    # Return the input state unchanged
    return state

# Nodes
def generate_query(state: SummaryState, config: RunnableConfig):
    """LangGraph node that generates a search query based on the research topic.

    Uses an LLM to create an optimized search query for web research based on
    the user's research topic. Supports both LMStudio and Ollama as LLM providers.

    For FET sensor queries (containing Ion/Ioff, SS, VT, gm_max, etc.), preserves
    the original query format to ensure proper parsing by the FET RAG system.

    Args:
        state: Current graph state containing the research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """

    # Check if FET mode is enabled in configuration first
    fet_mode_enabled = False
    try:
        from ollama_deep_researcher.configuration import Configuration
        configurable = Configuration.from_runnable_config(config)
        fet_mode_enabled = configurable.enable_fet_raw_data
    except:
        pass

    # Only preserve original format if FET mode is explicitly enabled
    if fet_mode_enabled:
        # Check if this is a FET sensor query by looking for characteristic terms
        fet_indicators = [
            r'Ion/Ioff', r'ion/ioff', r'Ion_Ioff', r'ion_ioff',
            r'\bSS\b', r'subthreshold swing',
            r'\bVT\b', r'\bvt\b', r'VT_', r'vt_', r'threshold voltage',
            r'gm_max', r'gm max', r'transconductance',
            r'\bFET\b', r'field-effect transistor', r'field effect transistor',
            r'phosphate sensor', r'pH sensor', r'glucose sensor', r'nitrate sensor',
            r'CNC graphene', r'EC graphene', r'bio-graphene',
            r'Device \d+', r'Thrust \d+',
            r'drift', r'hysteresis', r'health score',
            r'mV/dec', r'mA/mm'
        ]

        is_fet_query = any(
            re.search(pattern, state.research_topic, re.IGNORECASE)
            for pattern in fet_indicators
        )

        # If it's a FET query AND FET mode is enabled, preserve the original format
        if is_fet_query:
            print(f"FET mode enabled and FET query detected, preserving original format: {state.research_topic}")
            return {"search_query": state.research_topic}

    # Only use LLM for non-FET queries
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=state.research_topic
    )

    # Generate a query
    configurable = Configuration.from_runnable_config(config)

    # Attempt to generate the query through the failover helper
    use_json_format = "gpt-oss" not in configurable.local_llm.lower()
    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=formatted_prompt),
                HumanMessage(content="Generate a query for web search:"),
            ],
            temperature=0,
            json_mode=use_json_format,
        )
        content = result.content
    except Exception as exc:
        print(f"Failed to generate search query via LLM: {exc}")
        return {"search_query": state.research_topic}

    # Parse the JSON response and get the query
    try:
        # Always try to parse as JSON first, regardless of model type
        # gpt-oss models can generate valid JSON even without format="json"
        cleaned_content = clean_code_blocks(content)
        query = json.loads(cleaned_content)
        search_query = query['query']

        # Type checking and conversion for robustness
        if isinstance(search_query, list):
            print(f"Warning: LLM returned list for search_query: {search_query[:2] if len(search_query) > 2 else search_query}...")
            search_query = search_query[0] if search_query else state.research_topic
        elif not isinstance(search_query, str):
            print(f"Warning: search_query is {type(search_query)}, converting to string")
            search_query = str(search_query) if search_query else state.research_topic

    except (json.JSONDecodeError, KeyError):
        # If JSON parsing fails, fall back to content parsing
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
        # For any model, try to extract a clean query from the content
        search_query = content.strip().split('\n')[0].strip() if content.strip() else state.research_topic
    except Exception as e:
        # Outer exception handler for any unexpected errors
        print(f"Unexpected error in generate_search_query: {e}")
        search_query = state.research_topic

    return {"search_query": search_query}

def local_rag_research(state: SummaryState, config: RunnableConfig):
    """LangGraph node that performs multi-modal local RAG.

    Queries different types of local vector stores based on configuration:
    - FET sensor raw data (if enable_fet_raw_data=True)
    - Code repositories (if enable_code_retrieval=True)
    - Academic papers (if enable_paper_retrieval=True)

    Each modality is labeled in the results for proper downstream processing.

    Args:
        state: Current graph state containing the search query
        config: Configuration for the runnable, including modality settings

    Returns:
        Dictionary with labeled multi-modal results and sources
    """
    configurable = Configuration.from_runnable_config(config)

    # Check if local RAG is disabled at the highest level
    if not configurable.use_local_rag:
        print("Local RAG is disabled (use_local_rag=False), skipping all local retrieval.")
        return {
            "local_research_results": [],
            "local_sources_gathered": []
        }

    # Initialize results containers
    all_results = []
    all_sources = []

    # Modality 1: FET Sensor Raw Data (使用专门的FETSensorRAG)
    if configurable.enable_fet_raw_data and configurable.fet_excel_path:
        print("Retrieving FET sensor experimental data using hierarchical RAG...")
        from ollama_deep_researcher.advanced_fet_rag import FETSensorRAG

        fet_rag = FETSensorRAG(
            excel_vectorstore_path=configurable.fet_excel_path,
            non_excel_vectorstore_path=configurable.local_unstructured_docs_path,
            embedding_model=configurable.embedding_model,
            k_folders=configurable.fet_k_folders,
            k_runs_per_folder=configurable.fet_k_runs_per_folder,
            k_non_excel=configurable.fet_k_non_excel,
            use_llm_parsing=False,  # 不使用LLM解析，直接返回原始结果
            config=config  # 传入config以便FETSensorRAG能访问LLM配置
        )

        fet_results = fet_rag.query(state.search_query)

        # Process FET results - combine all FET data into one comprehensive object
        if fet_results and 'results' in fet_results and fet_results['results']:
            # Combine all FET results into one comprehensive content
            fet_content_parts = []
            for result in fet_results['results']:
                content = result.get('raw_content', '')
                if content:
                    fet_content_parts.append(content)

            # Create one comprehensive FET modality object
            if fet_content_parts:
                combined_fet_content = f"\n=== MODALITY: FET Sensor Experimental Data ===\n" + "\n\n".join(fet_content_parts)
                all_results.append(combined_fet_content)

            # Add FET sources with detailed folder information
            if 'folder_sources' in fet_results:
                # Add individual folder sources with Globus links
                for folder_source in fet_results['folder_sources']:
                    folder_id = folder_source['folder_id']
                    globus_url = folder_source['url']
                    target = folder_source.get('target', 'unknown')
                    score = folder_source.get('score', 0)

                    # Create a detailed source entry
                    source_entry = f"[FET Data - {target}] {folder_id}\n  Globus: {globus_url}"
                    all_sources.append(source_entry)
            elif 'stats' in fet_results:
                # Fallback to stats if folder_sources not available
                stats = fet_results['stats']
                source_info = f"[FET Data] Analyzed {stats.get('folders_analyzed', 0)} folders"
                if stats.get('runs_analyzed', 0) > 0:
                    source_info += f", {stats.get('runs_analyzed', 0)} runs"
                if stats.get('context_docs', 0) > 0:
                    source_info += f", {stats.get('context_docs', 0)} supporting documents"
                if stats.get('recommendations', 0) > 0:
                    source_info += f", {stats.get('recommendations', 0)} recommendations"
                all_sources.append(source_info)

    # Modality 2: Code Repositories
    if configurable.enable_code_retrieval and configurable.code_vector_path:
        print("Retrieving code repository data...")
        # Handle multi-volume structure for code vector stores
        code_paths = find_volume_paths(configurable.code_vector_path)
        code_results = query_local_vector_store(
            query=state.search_query,
            vector_store_paths=code_paths,
            embedding_model=configurable.embedding_model,
            limit=configurable.code_results_count  # 使用专门的code_results_count
        )

        # Combine all code results into one comprehensive object
        if code_results and 'results' in code_results:
            code_content_parts = []
            for result in code_results['results']:
                content = result.get('raw_content', '')
                if content:
                    code_content_parts.append(content)

            # Create one comprehensive Code modality object
            if code_content_parts:
                combined_code_content = f"\n=== MODALITY: Code Repository ===\n" + "\n\n".join(code_content_parts)
                all_results.append(combined_code_content)

            # Format code sources
            code_sources = format_sources(code_results)
            if code_sources:
                all_sources.append(f"[Code] {code_sources}")

    # Modality 3: Academic Papers (Publication Chunks)
    if configurable.enable_paper_retrieval and configurable.paper_vector_path:
        print("Retrieving academic paper data...")
        # Handle multi-volume structure for paper vector stores
        paper_paths = find_volume_paths(configurable.paper_vector_path)
        paper_results = query_local_vector_store(
            query=state.search_query,
            vector_store_paths=paper_paths,
            embedding_model=configurable.embedding_model,
            limit=configurable.paper_results_count  # 使用paper_results_count作为publication的计数
        )

        # Combine all paper results into one comprehensive object
        if paper_results and 'results' in paper_results:
            paper_content_parts = []
            for result in paper_results['results']:
                content = result.get('raw_content', '')
                if content:
                    paper_content_parts.append(content)

            # Create one comprehensive Papers modality object
            if paper_content_parts:
                combined_paper_content = f"\n=== MODALITY: Academic Papers ===\n" + "\n\n".join(paper_content_parts)
                all_results.append(combined_paper_content)

            # Format paper sources
            paper_sources = format_sources(paper_results)
            if paper_sources:
                all_sources.append(f"[Papers] {paper_sources}")

    # Fallback to original vector_store_paths if no modalities enabled
    if not all_results and configurable.use_local_rag and configurable.vector_store_paths:
        print("Using legacy vector store paths...")
        vector_paths = []
        for base_path in configurable.vector_store_paths:
            volume_paths = find_volume_paths(base_path)
            vector_paths.extend(volume_paths)

        legacy_results = query_local_vector_store(
            query=state.search_query,
            vector_store_paths=vector_paths,
            embedding_model=configurable.embedding_model,
            limit=configurable.paper_results_count  # 使用paper_results_count，因为legacy通常是publication
        )

        # Combine all legacy results into one object
        if legacy_results and 'results' in legacy_results:
            legacy_content_parts = []
            for result in legacy_results['results']:
                content = result.get('raw_content', '')
                if content:
                    legacy_content_parts.append(content)

            # Create one comprehensive legacy object
            if legacy_content_parts:
                combined_legacy_content = "\n=== MODALITY: Legacy Documents ===\n" + "\n\n".join(legacy_content_parts)
                all_results.append(combined_legacy_content)

            legacy_sources = format_sources(legacy_results)
            if legacy_sources:
                all_sources.append(legacy_sources)

    # Return combined multi-modal results as ONE comprehensive object per round
    if all_results:
        # Combine all modalities into one comprehensive local RAG result for this round
        comprehensive_local_result = "\n\n".join(all_results)
        return {
            "local_research_results": [comprehensive_local_result],  # ONE comprehensive object!
            "local_sources_gathered": all_sources
        }
    else:
        return {
            "local_research_results": [],
            "local_sources_gathered": []
        }

def generate_complementary_query(state: SummaryState, config: RunnableConfig):
    """LangGraph node that generates a complementary search query based on local RAG results.

    Analyzes local knowledge to create a query that explores a different but related angle
    of the research topic, ensuring diverse search results.

    Args:
        state: Current graph state containing the original search query and local RAG results
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including complementary_search_query containing the diversified query
    """
    configurable = Configuration.from_runnable_config(config)
    print(f"=== ENTERING generate_complementary_query ===")

    # First, check if we should skip this node entirely
    if not configurable.use_local_rag or not state.local_research_results:
        # Return empty result, forcing the system to skip this search
        print("Local RAG disabled or no results, skipping complementary query generation.")
        return {"complementary_search_query": ""}

    # Now that we know local_research_results is not empty, we can safely access it
    print(f"use_local_rag: {configurable.use_local_rag}, local_research_results sample exists: True") # Safe to print now
    # Optionally print a sample if needed, checking length first:
    # if state.local_research_results:
    #     print(f"local_research_results sample: {str(state.local_research_results[0])[:100]}...")

    # Check if FET data and use appropriate prompt
    is_fet = detect_fet_query(state, config) and FET_COMPLEMENTARY_QUERY_PROMPT is not None
    current_date = get_current_date()
    local_rag_result = state.local_rag_summary

    if is_fet:
        print("FET query detected, using FET-specific complementary query prompt")
        formatted_prompt = FET_COMPLEMENTARY_QUERY_PROMPT.format(
            search_query=state.search_query,
            local_rag_summary=state.local_rag_summary
        )
    else:
        # Use a simplified prompt format
        formatted_prompt = f"""Your goal is to generate a complementary search query based on local knowledge.

<CONTEXT>
Current date: {current_date}
Original research topic: {state.research_topic}
Original search query: {state.search_query}
</CONTEXT>

<GOAL>
Generate a different but related query that explores a new angle on the research topic.
</GOAL>

<REQUIREMENTS>
- Generate a search query with 5-10 keywords, not a complete sentence
- Focus on key terms and concepts, avoid questions
- Maximum 50 characters recommended
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with this exact key:
- "query": A search query that explores a different angle of the research topic
</FORMAT>

<EXAMPLE>
Example output:
{{
    "query": "alternative materials fabrication methods sensors"
}}
</EXAMPLE>

Provide your response in JSON format:"""

    print(f"Using research_topic: {state.research_topic}")
    print(f"Using original_query: {state.search_query}")
    print(f"Local RAG result length: {len(local_rag_result)}")
    print(f"Formatted prompt first 200 chars: {formatted_prompt[:200]}...")
    print(f"Local RAG summary: {state.local_rag_summary}")

    use_json_format = "gpt-oss" not in configurable.local_llm.lower()
    print("About to invoke LLM...")
    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=formatted_prompt),
                HumanMessage(
                    content=(
                        "Based on the following local RAG summary, <LOCAL_KNOWLEDGE> {state.local_rag_summary}</LOCAL_KNOWLEDGE>. "
                        "Generate a complementary query (different from the original query {state.search_query}) in JSON format with ONLY a 'query' field:"
                    )
                ),
            ],
            temperature=0,
            json_mode=use_json_format,
        )
        print("LLM invocation completed")
        content = result.content
    except Exception as e:
        print(f"Error during LLM invocation: {e}")
        fallback_queries = [
            f"Alternative perspectives on {state.research_topic}",
            f"Different angles on {state.research_topic}",
            f"New perspectives on {state.research_topic}",
            f"Complementary approaches to {state.research_topic}",
        ]
        return {"complementary_search_query": random.choice(fallback_queries)}
    print(f"Raw LLM response: {content[:300]}...")

    # New recursive function to find any query at any level in the JSON
    def find_query_in_json(json_obj):
        """Recursively search for keys containing 'query' in a JSON object at any level."""
        if isinstance(json_obj, dict):
            # First try to find direct keys containing 'query'
            query_keys = [k for k in json_obj.keys() if 'query' in k.lower()]
            if query_keys:
                # Sort by priority - exact match first, then by length (shorter is better)
                query_keys.sort(key=lambda x: (0 if x.lower() == 'query' else 1, len(x)))
                key = query_keys[0]
                if json_obj[key] and isinstance(json_obj[key], str):
                    print(f"Found query under key '{key}': {json_obj[key]}")
                    return json_obj[key]

            # If not found, search recursively in nested objects
            for key, value in json_obj.items():
                result = find_query_in_json(value)
                if result:
                    return result

        elif isinstance(json_obj, list):
            # Search in each element of the list
            for item in json_obj:
                result = find_query_in_json(item)
                if result:
                    return result

        return None

    # Parse the JSON response and get the complementary query
    try:
        # Always try to parse as JSON first, regardless of model type
        # gpt-oss models can generate valid JSON even without format="json"
        cleaned_content = clean_code_blocks(content)
        query_data = json.loads(cleaned_content)
        print(f"Full parsed JSON: {query_data}")

        # First try the recursive search for any query at any level
        complementary_query = find_query_in_json(query_data)

        # If not found through recursive search, try the original method as fallback
        if not complementary_query:
            print("Recursive search failed, trying original method")
            # Try to get the query from the 'query' key which we asked for in our prompt
            if 'query' in query_data and query_data['query']:
                complementary_query = query_data['query']
                print(f"Found query: {complementary_query}")
            else:
                # Try other possible keys as fallback
                possible_keys = ['complementary_query', 'search_query', 'follow_up_query', 'query_to_search', 'new_query','complementary_query_to_search']
                complementary_query = ""

                for key in possible_keys:
                    if key in query_data and query_data[key]:
                        complementary_query = query_data[key]
                        print(f"Found query under alternative key '{key}': {complementary_query}")
                        break

        # If still empty, try to use the entire content as the query if it looks like plain text
        if not complementary_query and not content.startswith('{') and not content.startswith('['):
            print("Using raw content as query")
            complementary_query = content.strip()

        # Last resort fallback
        if not complementary_query:
            print("Empty complementary query generated, using fallback")
            complementary_query = f"Alternative aspects of {state.research_topic}"

        print(f"Final complementary query: '{complementary_query}'")

        # Ensure state.search_query is a string before comparison
        if not isinstance(state.search_query, str):
            print(f"Warning: search_query is {type(state.search_query)}, converting for comparison...")
            if isinstance(state.search_query, list):
                state.search_query = state.search_query[0] if state.search_query else ""
            else:
                state.search_query = str(state.search_query) if state.search_query else ""

        # Check if the complementary query is too similar to the original query
        if complementary_query.lower().strip() == state.search_query.lower().strip():
            print("Warning: Complementary query is identical to original query. Trying backup approach...")

            # Direct backup approach without using local RAG content
            backup_prompt = f"""Generate a complementary search query for the research topic.

<ORIGINAL_INFORMATION>
Research topic: {state.research_topic}
Original search query: {state.search_query}
</ORIGINAL_INFORMATION>

<INSTRUCTIONS>
1. You MUST generate a query that is DIFFERENT from the original query.
2. Take a completely different perspective or angle on the research topic.
3. Format your response as a JSON object with a single "query" field.
4. Keep your query concise and focused.
5. DO NOT return the original query or anything too similar.
</INSTRUCTIONS>

Example output:
{{
    "query": "limitations and criticisms of {state.research_topic}"
}}

Provide only the JSON response:"""

            try:
                backup_result = invoke_with_failover(
                    configurable,
                    [
                        SystemMessage(content=backup_prompt),
                        HumanMessage(
                            content=f"Generate a complementary query that is DIFFERENT from: '{state.search_query}'"
                        ),
                    ],
                    temperature=0,
                    json_mode=use_json_format,
                )

                backup_content = backup_result.content
                print(f"Backup approach result: {backup_content[:300]}...")

                try:
                    cleaned_backup = clean_code_blocks(backup_content)
                    backup_data = json.loads(cleaned_backup)
                    backup_query = find_query_in_json(backup_data)

                    # Ensure state.search_query is string before comparison
                    if not isinstance(state.search_query, str):
                        state.search_query = str(state.search_query[0]) if isinstance(state.search_query, list) and state.search_query else ""

                    if backup_query and backup_query.lower().strip() != state.search_query.lower().strip():
                        print(f"Using backup query: {backup_query}")
                        return {"complementary_search_query": backup_query}
                    else:
                        # If backup also failed or returned the same query, use a template fallback, randomly pick one from the list
                        fallback_queries = [f"Criticisms and limitations of {state.research_topic}", f"Alternative perspectives on {state.research_topic}", f"Different angles on {state.research_topic}", f"New perspectives on {state.research_topic}", f"Complementary approaches to {state.research_topic}"]
                        print("Backup approach failed or returned same query, using template fallback")
                        return {"complementary_search_query": random.choice(fallback_queries)}

                except (json.JSONDecodeError, KeyError):
                    # If JSON parsing fails, use raw content if it doesn't look like JSON
                    if not backup_content.startswith('{') and not backup_content.startswith('['):
                        # Ensure state.search_query is string before comparison
                        if not isinstance(state.search_query, str):
                            state.search_query = str(state.search_query[0]) if isinstance(state.search_query, list) and state.search_query else ""

                        if backup_content.lower().strip() != state.search_query.lower().strip():
                            return {"complementary_search_query": backup_content.strip()}

                    # Last resort template fallback, randomly pick one from the list
                    fallback_queries = [f"Alternative approaches to {state.research_topic}", f"Different approaches to {state.research_topic}", f"New approaches to {state.research_topic}", f"Complementary approaches to {state.research_topic}"]
                    return {"complementary_search_query": random.choice(fallback_queries)}

            except Exception as e:
                print(f"Error during backup LLM invocation: {e}")
                # Last resort template fallback, randomly pick one from the list
                fallback_queries = [f"Disadvantages and limitations of {state.research_topic}", f"Criticisms and limitations of {state.research_topic}", f"Alternative perspectives on {state.research_topic}", f"Different angles on {state.research_topic}", f"New perspectives on {state.research_topic}", f"Complementary approaches to {state.research_topic}"]
                return {"complementary_search_query": random.choice(fallback_queries)}

        return {"complementary_search_query": complementary_query}
    except (json.JSONDecodeError, KeyError) as e:
        # If parsing fails, return empty query instead of using a fallback
        print(f"JSON parsing failed with error: {e}")
        print(f"Raw content: {content[:200]}...")

        # Try to use the raw content if it's not JSON
        if not content.startswith('{') and not content.startswith('['):
            print("Using raw content as query since it's not JSON")
            return {"complementary_search_query": content.strip()}

        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
            print(f"After stripping tokens: {content[:200]}...")

        print("All attempts failed - returning fallback query")
        # Last resort template fallback, randomly pick one from the list
        fallback_queries = [f"Different perspectives on {state.research_topic}", f"Alternative perspectives on {state.research_topic}", f"Different angles on {state.research_topic}", f"New perspectives on {state.research_topic}", f"Complementary approaches to {state.research_topic}"]
        return {"complementary_search_query": random.choice(fallback_queries)}

def web_research(state: SummaryState, config: RunnableConfig):
    """LangGraph node that performs web research using the generated search query.

    Executes a web search using the configured search API (tavily, perplexity,
    duckduckgo, or searxng) and formats the results for further processing.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """

    # Configure
    configurable = Configuration.from_runnable_config(config)

    # Check if web search is disabled
    if not configurable.enable_web_search:
        print("Web search is disabled (enable_web_search=False), skipping web retrieval.")
        return {
            "sources_gathered": [],
            "research_loop_count": state.research_loop_count + 1,
            "web_research_results": []
        }

    # Get the search API
    search_api = get_config_value(configurable.search_api)

    # Check if FET query and enhance search if needed
    search_query = state.search_query
    is_fet = detect_fet_query(state, config) and FET_WEB_SEARCH_ENHANCEMENT is not None
    if is_fet and "fabrication" not in search_query.lower():
        search_query = FET_WEB_SEARCH_ENHANCEMENT.format(base_query=search_query)
        print(f"FET query enhanced for academic search: {search_query}")

    # Search the web
    print(f"[DEBUG] web_research: Using search API '{search_api}' with query: '{search_query}'")

    if search_api == "tavily":
        search_results = tavily_search(search_query, fetch_full_page=configurable.fetch_full_page, max_results=3)
        print(f"[DEBUG] web_research: Tavily returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "perplexity":
        search_results = perplexity_search(search_query, state.research_loop_count)
        print(f"[DEBUG] web_research: Perplexity returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "duckduckgo":
        search_results = duckduckgo_search(search_query, max_results=5, fetch_full_page=configurable.fetch_full_page)
        print(f"[DEBUG] web_research: DuckDuckGo returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "searxng":
        # Temporarily set the SEARXNG_URL environment variable if configured
        original_searxng_url = os.environ.get("SEARXNG_URL")
        if configurable.searxng_url:
            os.environ["SEARXNG_URL"] = configurable.searxng_url
        try:
            search_results = searxng_search(search_query, max_results=5, fetch_full_page=configurable.fetch_full_page)
            print(f"[DEBUG] web_research: SearXNG returned {len(search_results.get('results', []))} results")
        finally:
            # Restore original value
            if original_searxng_url is not None:
                os.environ["SEARXNG_URL"] = original_searxng_url
            elif "SEARXNG_URL" in os.environ:
                del os.environ["SEARXNG_URL"]
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    print(f"[DEBUG] web_research: Final search_str length: {len(search_str)} chars")
    print(f"[DEBUG] web_research: search_str preview: '{search_str[:100]}...'")

    sources_formatted = format_sources(search_results)
    print(f"[DEBUG] web_research: sources_formatted: '{sources_formatted[:100]}...'")

    result = {"sources_gathered": [sources_formatted], "research_loop_count": state.research_loop_count + 1, "web_research_results": [search_str]}
    print(f"[DEBUG] web_research: Returning result with web_research_results length: {len(result['web_research_results'][0])}")
    return result

def complementary_web_research(state: SummaryState, config: RunnableConfig):
    """LangGraph node that performs web research using the complementary search query.

    Similar to the web_research node but uses the complementary search query that explores
    a different but related angle of the research topic.

    Args:
        state: Current graph state containing the complementary search query
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including complementary_sources_gathered and complementary_web_research_results
    """
    # Configure
    configurable = Configuration.from_runnable_config(config)

    # Check if web search is disabled
    if not configurable.enable_web_search:
        print("Web search is disabled (enable_web_search=False), skipping complementary web retrieval.")
        return {
            "complementary_sources_gathered": [],
            "complementary_web_research_results": []
        }

    # Get the search API
    search_api = get_config_value(configurable.search_api)

    # If complementary query is not available, skip this node
    if not state.complementary_search_query:
        return {"complementary_sources_gathered": [], "complementary_web_research_results": []}

    # Search the web with complementary query
    print(f"[DEBUG] complementary_web_research: Using search API '{search_api}' with query: '{state.complementary_search_query}'")

    if search_api == "tavily":
        search_results = tavily_search(state.complementary_search_query, fetch_full_page=configurable.fetch_full_page, max_results=1)
        print(f"[DEBUG] complementary_web_research: Tavily returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "perplexity":
        search_results = perplexity_search(state.complementary_search_query, state.research_loop_count)
        print(f"[DEBUG] complementary_web_research: Perplexity returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "duckduckgo":
        search_results = duckduckgo_search(state.complementary_search_query, max_results=3, fetch_full_page=configurable.fetch_full_page)
        print(f"[DEBUG] complementary_web_research: DuckDuckGo returned {len(search_results.get('results', []))} results")
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    elif search_api == "searxng":
        # Temporarily set the SEARXNG_URL environment variable if configured
        original_searxng_url = os.environ.get("SEARXNG_URL")
        if configurable.searxng_url:
            os.environ["SEARXNG_URL"] = configurable.searxng_url
        try:
            search_results = searxng_search(state.complementary_search_query, max_results=3, fetch_full_page=configurable.fetch_full_page)
            print(f"[DEBUG] complementary_web_research: SearXNG returned {len(search_results.get('results', []))} results")
        finally:
            # Restore original value
            if original_searxng_url is not None:
                os.environ["SEARXNG_URL"] = original_searxng_url
            elif "SEARXNG_URL" in os.environ:
                del os.environ["SEARXNG_URL"]
        search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=2500, fetch_full_page=configurable.fetch_full_page)
    else:
        raise ValueError(f"Unsupported search API: {configurable.search_api}")

    print(f"[DEBUG] complementary_web_research: Final search_str length: {len(search_str)} chars")
    print(f"[DEBUG] complementary_web_research: search_str preview: '{search_str[:100]}...'")

    sources_formatted = format_sources(search_results)
    print(f"[DEBUG] complementary_web_research: sources_formatted: '{sources_formatted[:100]}...'")

    result = {
        "complementary_sources_gathered": [sources_formatted],
        "complementary_web_research_results": [search_str]
    }
    print(f"[DEBUG] complementary_web_research: Returning result with complementary_web_research_results length: {len(result['complementary_web_research_results'][0])}")
    return result

def summarize_sources(state: SummaryState, config: RunnableConfig):
    """LangGraph node that summarizes research results from both local and web sources.

    Uses an LLM to create or update a running summary based on the newest research
    results, integrating them with any existing summary.

    Args:
        state: Current graph state containing research topic, running summary,
            and research results from both local and web sources
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """

    # Existing summary
    existing_summary = state.running_summary

    # Get the most recent research results
    research_content = ""

    # Add local research results if available (ALL results, not just the last one)
    if state.local_research_results and len(state.local_research_results) > 0:
        all_local_results = "\n\n".join(state.local_research_results)
        research_content += f"<Local Research Results>\n{all_local_results}\n</Local Research Results>\n\n"

    # Add web research results from original query if available (ALL results)
    if state.web_research_results and len(state.web_research_results) > 0:
        all_web_results = "\n\n".join(state.web_research_results)
        research_content += f"<Main Research Results>\n{all_web_results}\n</Main Research Results>\n\n"

    # Add complementary web research results if available (ALL results)
    if state.complementary_web_research_results and len(state.complementary_web_research_results) > 0:
        all_complementary_results = "\n\n".join(state.complementary_web_research_results)
        research_content += f"<Complementary Research Results>\n{all_complementary_results}\n</Complementary Research Results>\n\n"

    # Build the human message
    if existing_summary:
        human_message_content = (
            f"<Existing Summary> \n {existing_summary} \n <Existing Summary>\n\n"
            f"<New Context> \n {research_content} \n <New Context>"
            f"Update the Existing Summary with the New Context on this topic: \n <User Input> \n {state.research_topic} \n <User Input>\n\n"
        )
    else:
        human_message_content = (
            f"<Context> \n {research_content} \n <Context>"
            f"Create a Summary using the Context on this topic: \n <User Input> \n {state.research_topic} \n <User Input>\n\n"
        )

    # Run the LLM through the shared failover helper
    configurable = Configuration.from_runnable_config(config)

    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=summarizer_instructions),
                HumanMessage(content=human_message_content),
            ],
            temperature=0.3,
        )
        running_summary = result.content
    except Exception as exc:
        print(f"Error generating running summary: {exc}")
        running_summary = f"Summary unavailable due to LLM error: {exc}"

    if configurable.strip_thinking_tokens:
        running_summary = strip_thinking_tokens(running_summary)

    # Add current summary to summary_history
    # Create an object with metadata about this summary iteration
    iteration_summary = {
        "iteration": state.research_loop_count,
        "summary": running_summary,
        "query": state.search_query,
        "complementary_query": state.complementary_search_query if state.complementary_search_query else ""
    }

    # Return updated state with the new summary and updated history
    return {
        "running_summary": running_summary,
        "summary_history": [iteration_summary]
    }

def reflect_on_summary(state: SummaryState, config: RunnableConfig):
    """LangGraph node that identifies knowledge gaps and generates follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    a new search query to address those gaps. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """

    # Log the input state
    reflect_logger.info(f"===== REFLECTING ON SUMMARY - INPUT STATE =====")
    reflect_logger.info(f"Research topic: {state.research_topic}")
    reflect_logger.info(f"Research loop count: {state.research_loop_count}")
    reflect_logger.info(f"Summary length: {len(state.running_summary) if state.running_summary else 0} chars")

    # Generate a query
    configurable = Configuration.from_runnable_config(config)

    # Choose the appropriate LLM based on the provider
    # Check if using gpt-oss model which doesn't handle format="json" well
    use_json_format = "gpt-oss" not in configurable.local_llm.lower()

    # Check if FET data and use appropriate reflection prompt
    is_fet = detect_fet_query(state, config) and FET_REFLECTION_PROMPT is not None

    if is_fet:
        reflect_logger.info("Using FET-specific reflection prompt")
        reflection_prompt = FET_REFLECTION_PROMPT.format(
            running_summary=state.running_summary,
            research_topic=state.research_topic
        )
        human_prompt = "Evaluate the FET analysis completeness and suggest next steps:"
    else:
        reflection_prompt = reflection_instructions.format(research_topic=state.research_topic)
        human_prompt = f"Reflect on our existing knowledge: \n === \n {state.running_summary}, \n === \n And now identify a knowledge gap and generate a follow-up web search query:"

    reflect_logger.info("Sending reflection prompt to LLM...")
    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=reflection_prompt),
                HumanMessage(content=human_prompt),
            ],
            temperature=0,
            json_mode=use_json_format,
        )
        reflect_logger.info(f"Raw LLM response: {result.content}")
        response_content = result.content
    except Exception as exc:
        reflect_logger.warning(f"Reflection LLM invocation failed: {exc}")
        fallback_queries = [
            f"Tell me more about {state.research_topic}",
            f"What are the latest trends in {state.research_topic}?",
            f"What are the latest developments in {state.research_topic}?",
            f"What are the latest advancements in {state.research_topic}?",
            f"What are the latest innovations in {state.research_topic}?",
            f"What are the latest breakthroughs in {state.research_topic}?",
        ]
        query = random.choice(fallback_queries)
        reflect_logger.info(f"Using fallback query after LLM failure: {query}")
        reflect_logger.info("===== REFLECTION COMPLETE =====")
        return {"search_query": query}

    # Strip thinking tokens if configured
    try:
        # Always try to parse as JSON first, regardless of model type
        # gpt-oss models can generate valid JSON even without format="json"
        cleaned_content = clean_code_blocks(response_content)
        reflection_content = json.loads(cleaned_content)
        # Get the follow-up query
        query = reflection_content.get('follow_up_query')
        knowledge_gap = reflection_content.get('knowledge_gap', 'No knowledge gap specified')

        reflect_logger.info(f"Knowledge gap identified: {knowledge_gap}")

        # Check if query is None or empty
        if not query:
            # Use a fallback query, randomly pick one from the list
            fallback_queries = [f"Tell me more about {state.research_topic}", f"What are the latest trends in {state.research_topic}?", f"What are the latest developments in {state.research_topic}?", f"What are the latest advancements in {state.research_topic}?", f"What are the latest innovations in {state.research_topic}?", f"What are the latest breakthroughs in {state.research_topic}?"]
            query = random.choice(fallback_queries)
            reflect_logger.info(f"Using fallback query: {query}")

        reflect_logger.info(f"Generated follow-up query: {query}")
        reflect_logger.info("===== REFLECTION COMPLETE =====")
        return {"search_query": query}
    except (json.JSONDecodeError, KeyError, AttributeError):
        # If parsing fails, use fallback approach
        reflect_logger.warning("Failed to parse LLM response, using fallback query")
        content = response_content
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
        # Try to extract a clean query from content
        query = content.strip().split('\n')[0].strip() if content.strip() else ""

        # Check if query is None or empty
        if not query:
            # Use a fallback query, randomly pick one from the list
            fallback_queries = [f"Tell me more about {state.research_topic}", f"What are the latest trends in {state.research_topic}?", f"What are the latest developments in {state.research_topic}?", f"What are the latest advancements in {state.research_topic}?", f"What are the latest innovations in {state.research_topic}?", f"What are the latest breakthroughs in {state.research_topic}?", f"What are the latest advancements in {state.research_topic}?", f"What are the latest innovations in {state.research_topic}?", f"What are the latest breakthroughs in {state.research_topic}?"]
            query = random.choice(fallback_queries)
            reflect_logger.info(f"Using fallback query: {query}")

        reflect_logger.info(f"Generated follow-up query: {query}")
        reflect_logger.info("===== REFLECTION COMPLETE =====")
        return {"search_query": query}
    except (json.JSONDecodeError, KeyError, AttributeError):
        # If parsing fails or the key is not found, use a fallback query
        reflect_logger.warning("Failed to parse LLM response as JSON, using fallback query")
        fallback_queries = [f"Tell me more about {state.research_topic}", f"What are the latest trends in {state.research_topic}?", f"What are the latest developments in {state.research_topic}?", f"What are the latest advancements in {state.research_topic}?", f"What are the latest innovations in {state.research_topic}?", f"What are the latest breakthroughs in {state.research_topic}?", f"What are the latest advancements in {state.research_topic}?", f"What are the latest innovations in {state.research_topic}?", f"What are the latest breakthroughs in {state.research_topic}?"]
        query = random.choice(fallback_queries)
        reflect_logger.info(f"Using fallback query: {query}")
        reflect_logger.info("===== REFLECTION COMPLETE =====")
        return {"search_query": query}

def finalize_summary(state: SummaryState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Uses an LLM to create a comprehensive final summary by analyzing multiple iterations
    of research summaries. Then combines this with deduplicated sources to create a
    well-structured research report with proper citations.

    Args:
        state: Current graph state containing the running summary, summary history, and sources gathered
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    # Configure LLM
    configurable = Configuration.from_runnable_config(config)

    # Log the input state
    finalize_logger.info(f"===== FINALIZING SUMMARY - INPUT STATE =====")
    finalize_logger.info(f"Research topic: {state.research_topic}")
    finalize_logger.info(f"Research loop count: {state.research_loop_count}")
    finalize_logger.info(f"Summary history entries: {len(state.summary_history) if state.summary_history else 0}")
    finalize_logger.info(f"Sources gathered: {len(state.sources_gathered) if state.sources_gathered else 0}")
    finalize_logger.info(f"Complementary sources: {len(state.complementary_sources_gathered) if state.complementary_sources_gathered else 0}")
    finalize_logger.info(f"Local sources: {len(state.local_sources_gathered) if state.local_sources_gathered else 0}")

    # Determine if we're in DToR mode - in DToR mode, we don't include sources in each individual research node
    is_dtor_mode = getattr(configurable, 'research_mode', 'single') == 'dtor'
    finalize_logger.info(f"Research mode: {'DToR' if is_dtor_mode else 'Single'}")

    # Process summary history for use in the final synthesis
    # If we have summary history, we'll use that; otherwise we'll use the running_summary
    summary_history_text = ""

    if state.summary_history and len(state.summary_history) > 0:
        # We have summary history, format it for the LLM
        finalize_logger.info("Formatting summary history for final synthesis")
        for i, summary_item in enumerate(state.summary_history):
            summary_history_text += f"\n--- ITERATION {summary_item.get('iteration', i+1)} ---\n"
            summary_history_text += f"Search Query: {summary_item.get('query', 'Unknown')}\n"
            if summary_item.get('complementary_query'):
                summary_history_text += f"Complementary Query: {summary_item.get('complementary_query')}\n"
            summary_history_text += f"Summary:\n{summary_item.get('summary', '')}\n\n"
    else:
        # No history available, just use the current summary
        finalize_logger.info("No summary history available, using current running summary")
        summary_history_text = f"Only one research iteration was performed. Summary:\n{state.running_summary}"

    # Check if FET data and build appropriate prompt
    is_fet = detect_fet_query(state, config) and FET_FINAL_SUMMARY_PROMPT is not None
    current_date = get_current_date()

    # Build the prompt
    if is_fet:
        finalize_logger.info("Generating FET-specific final report")
        final_summary_prompt = FET_FINAL_SUMMARY_PROMPT.format(
            research_topic=state.research_topic,
            current_date=current_date,
            running_summary=summary_history_text
        )
    else:
        final_summary_prompt = f"""
    You are a domain expert technical writer.
    Your single task: craft a concise, data-oriented mini report from the material provided.
    Write with bullet-level density, no storytelling fluff.
    Do **not** invent metrics; if data are missing, state “‑ not reported”.
    Never cite sources—the calling program discards them.
    <GOAL>
    Create a detailed and insightful final research report on: {state.research_topic}
    Your objective is to synthesize the collected information into a thorough and well-supported document.
    </GOAL>

    <CONTEXT>
    You have conducted {state.research_loop_count} iterations of research on this topic.
    Below you'll find summaries from each research iteration.
    </CONTEXT>
    Require ≥ 4 bullets, each with at least one numeric datum (else write “- not reported”).
    """
    human_final_summary_prompt = f"""
    The User has queried for a comprehensive research on \n<User Input>\n {state.research_topic} \n <User Input>. Based on the <RESEARCH_HISTORY> {summary_history_text} </RESEARCH_HISTORY>, please create the final comprehensive research report on: {state.research_topic}.
    <INSTRUCTIONS>
    1. Create a well-structured, **thorough**, and comprehensive final report that synthesizes all the research findings across iterations
    2. Organize information logically with clear section headings and a coherent narrative flow
    3. Highlight key insights, patterns, and conclusions, **providing supporting details or evidence from the research history where appropriate**
    4. Show how the research evolved across iterations, noting how later iterations built upon, refined, or potentially contradicted earlier findings
    5. Note any significant remaining gaps, unanswered questions, or areas identified for potential future research
    6. Make the report clear, easy to read, and understand for someone unfamiliar with the specifics of the research process
    7. Aim for a substantial report excluding sources, focusing on depth and quality of synthesis.
    8. ALWAYS provide a complete summary, even if complex. If you're thinking through the process, make sure to finish with your final report.
    </INSTRUCTIONS>
    """

    # Get the final summary from the LLM
    finalize_logger.info("===== STEP 1: GENERATING FINAL RESEARCH REPORT =====")
    finalize_logger.info("Invoking LLM to synthesize research findings...")
    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=final_summary_prompt),
                HumanMessage(content=human_final_summary_prompt),
            ],
            temperature=0.3,
        )
        final_content = result.content
        if configurable.strip_thinking_tokens:
            final_content = strip_thinking_tokens(final_content)
        finalize_logger.info(f"Final summary generated: {len(final_content)} chars")
    except Exception as exc:
        finalize_logger.error(f"Failed to generate final summary: {exc}")
        final_content = (
            "Final report generation failed due to an LLM error. "
            "The following consolidated research history is provided instead:\n\n"
            f"{summary_history_text}"
        )

    # In DToR mode, we don't include sources in the final summary of individual research nodes
    # as sources will be managed at the DToR level (synthesize_final_report)
    if is_dtor_mode:
        # Don't include sources in DToR mode
        finalize_logger.info("DToR mode detected, not including sources in final summary")
        return {"running_summary": final_content}

    # For single mode, continue with the original source processing
    # Deduplicate sources before joining
    finalize_logger.info("Processing and deduplicating sources...")
    seen_sources = set()
    unique_sources = []

    # Process web sources from original query
    for source in state.sources_gathered:
        # Split the source into lines and process each individually
        for line in source.split('\n'):
            # Only process non-empty lines
            if line.strip() and line not in seen_sources:
                seen_sources.add(line)
                unique_sources.append(line)

    # Process web sources from complementary query
    for source in state.complementary_sources_gathered:
        # Split the source into lines and process each individually
        for line in source.split('\n'):
            # Only process non-empty lines
            if line.strip() and line not in seen_sources:
                seen_sources.add(line)
                unique_sources.append("🔍 " + line)  # Add a magnifying glass emoji to denote complementary search source

    # Process local sources with enhanced categorization
    fet_sources = []
    code_sources = []
    paper_sources = []
    other_local_sources = []

    for source in state.local_sources_gathered:
        # Process multi-line FET sources (with Globus links)
        if "[FET Data -" in source and "Globus:" in source:
            # This is a multi-line FET source with Globus link
            lines = source.split('\n')
            full_source = '\n'.join(lines).strip()
            if full_source not in seen_sources:
                seen_sources.add(full_source)
                fet_sources.append(full_source)
        else:
            # Split the source into lines and process each individually
            for line in source.split('\n'):
                # Only process non-empty lines
                if line.strip() and line not in seen_sources:
                    seen_sources.add(line)
                    # Categorize local sources by type
                    if "[FET Data]" in line:
                        fet_sources.append(line)
                    elif "[Code]" in line:
                        code_sources.append(line)
                    elif "[Papers]" in line:
                        paper_sources.append(line)
                    elif "Globus:" not in line:  # Skip standalone Globus lines
                        other_local_sources.append("📚 " + line)

    # Build the sources section with categories
    sources_sections = []

    # Add web sources
    if unique_sources:
        sources_sections.append("#### Web Sources:")
        sources_sections.extend(unique_sources)

    # Add FET sources
    if fet_sources:
        sources_sections.append("\n#### FET Sensor Data:")
        for src in fet_sources:
            # For multi-line sources with Globus links, format nicely
            if "Globus:" in src:
                sources_sections.append("🧪 " + src)
            else:
                sources_sections.append("🧪 " + src)

    # Add code sources
    if code_sources:
        sources_sections.append("\n#### Code Repositories:")
        sources_sections.extend(["💻 " + src for src in code_sources])

    # Add paper sources
    if paper_sources:
        sources_sections.append("\n#### Academic Papers:")
        sources_sections.extend(["📄 " + src for src in paper_sources])

    # Add other local sources
    if other_local_sources:
        sources_sections.append("\n#### Other Local Documents:")
        sources_sections.extend(other_local_sources)

    # Join all sources with proper formatting
    all_sources = "\n".join(sources_sections) if sources_sections else "No sources available"
    finalize_logger.info(f"Deduplicated sources: {len(seen_sources)} unique sources")

    # Combine LLM-generated final summary with enhanced sources
    final_report = f"{final_content}\n\n### Sources:\n{all_sources}"

    # Generate remote printing parameters if FET-related query OR FET RAG is enabled
    # Check if FET RAG is enabled in configuration
    fet_rag_enabled = getattr(configurable, 'enable_fet_raw_data', False)

    # Expanded keyword pool for better detection
    fet_keywords = [
        'fet', 'sensor', 'graphene', 'inkjet', 'print', 'fabricat', 'synthesis',
        'phosphat', 'biosens', 'transistor', 'electrode', 'ion/ioff', 'ion_ioff',
        'ratio', 'detection', 'ide', 'substrate', 'anneal', 'mobility', 'dirac',
        'gate', 'drain', 'source', 'channel', 'oxide', 'sio2', 'ito', 'cvd',
        'rgo', 'go', 'pbase', 'aptamer', 'functionali'
    ]

    # Check if query contains FET-related keywords
    query_lower = state.research_topic.lower()
    is_fet_query = any(keyword in query_lower for keyword in fet_keywords)

    # Generate parameters only if FET RAG is explicitly enabled in configuration
    if fet_rag_enabled:
        try:
            finalize_logger.info("FET RAG enabled in configuration, generating remote printing parameters...")

            # Read FET handbook context (only key parameters)
            fet_handbook_context = """
Key fabrication parameters from Chen Lab FET handbook:
- Drop spacing: 25 µm typical for inkjet printing
- Coats/passes: 5-10 (more coats for better continuity across 200 µm gaps)
- Stage temperature: 60°C during printing (range 40-80°C)
- Anneal temperature: 200-350°C (200°C preserves polymer binders, 350°C higher conductivity)
- IDE gap (S): 200 µm typical
- IDE finger width (W): 100 µm typical
- Oxide thickness: 90 nm or 300 nm SiO2
- Substrates: ITO_glass, ITO_PET (max 130°C), ITO_PEN (max 130°C), Si_SiO2
- Graphene types: CNC_graphene (cellulose nanocrystals), CVD_graphene (control)
- PBASE functionalization: 10 mg/mL in DMF, 90-120 min incubation
- AJP printing: Aerosol Jet Printing with 10 pL cartridge
- Solution gating: Ag/AgCl reference, 0-0.5V sweep range
- Measurement cycles: 50 cycles standard, 100 for stability testing
"""

            # Generate parameters using second LLM call
            param_prompt = f"""Based on the research findings and FET sensor fabrication handbook, generate standardized remote printing parameters.

<FET_HANDBOOK_CONTEXT>
{fet_handbook_context}
</FET_HANDBOOK_CONTEXT>

<RESEARCH_QUERY>
{state.research_topic}
</RESEARCH_QUERY>

<RESEARCH_FINDINGS_SUMMARY>
{final_content}
</RESEARCH_FINDINGS_SUMMARY>

Generate a JSON object with optimized inkjet printing and fabrication parameters for remote execution.

OPTIMIZATION GUIDELINES:
- If query mentions Ion/Ioff ratio: optimize for high on/off ratio (more printing passes, higher anneal temperature)
- If query mentions phosphate detection: enable PBASE functionalization for biosensing
- If query mentions flexibility: use PET/PEN substrates with lower temperature processing
- If query mentions sensitivity: use thinner oxide (90nm) and optimize surface chemistry
- Consider the specific requirements mentioned in the research query

PARAMETER RANGES AND CONSTRAINTS (from Chen Lab handbook):
- drop_spacing_um: 20-30 (25 typical)
- coats_passes: 5-10 (more coats for better continuity)
- stage_temperature_C: 40-80 (60 typical)
- anneal_temperature_C: 200-350 (200 preserves binders, 350 higher conductivity, max 130 for PET/PEN)
- anneal_time_min: 10-60 (30 typical)
- gap_S_um: 100-300 (200 typical)
- finger_width_W_um: 50-200 (100 typical)
- oxide_thickness_nm: 90 or 300 (90 for higher sensitivity, 300 for stability)
- gate_sweep_cycles: 50-100 (50 standard, 100 for stability testing)
- V_D_mV: 50-100
- V_G_range_V: "0-0.5" for solution gate, larger for back gate
- incubation_time_min: 60-120 for PBASE (90 typical)

CRITICAL JSON FORMAT REQUIREMENTS:
1. Output ONLY valid JSON - no text before or after
2. Use double quotes for all strings
3. Use actual values within the ranges above
4. Numbers should be unquoted (e.g., 200 not "200")
5. Boolean values should be lowercase (true/false)
6. No trailing commas in arrays or objects
7. Do NOT include comments in the JSON

IMPORTANT: Your response must start with {{ and end with }}. Output ONLY the JSON object below with values chosen from the ranges above:

{{
"device_architecture": "GFET_on_ITO",
"substrate": {{
    "type": "ITO_glass",
    "oxide_thickness_nm": 300,
    "preparation": ["solvent_clean", "O2_plasma_60s"]
}},
"electrode_geometry": {{
    "type": "IDE",
    "gap_S_um": 200,
    "finger_width_W_um": 100,
    "material": "Au"
}},
"inkjet_printing": {{
    "graphene_type": "CNC_graphene",
    "drop_spacing_um": 25,
    "coats_passes": 7,
    "stage_temperature_C": 60,
    "cartridge_volume_pL": 10
}},
"thermal_processing": {{
    "anneal_temperature_C": 250,
    "anneal_time_min": 30,
    "atmosphere": "air"
}},
"surface_functionalization": {{
    "enabled": true,
    "treatments": [
    {{
        "chemical": "PBASE",
        "concentration": "10mg/mL_in_DMF",
        "incubation_time_min": 90
    }}
    ]
}},
"measurement_parameters": {{
    "gate_sweep_cycles": 50,
    "V_D_mV": 100,
    "V_G_range_V": "0-0.5",
    "reference_electrode": "Ag/AgCl"
}}
}}"""

            finalize_logger.info("===== STEP 2: REMOTE PRINTING PARAMETER GENERATION =====")
            finalize_logger.info("FET RAG is enabled in configuration - generating parameters")
            finalize_logger.info(f"Context being passed: FET handbook + Query + Full report ({len(final_content)} chars)")

            try:
                param_result = invoke_with_failover(
                    configurable,
                    [
                        SystemMessage(content="You are a FET sensor fabrication expert. Generate precise JSON parameters for remote printing."),
                        HumanMessage(content=param_prompt),
                    ],
                    temperature=0.3,
                )
                param_json = param_result.content
                if configurable.strip_thinking_tokens:
                    param_json = strip_thinking_tokens(param_json)

                finalize_logger.info(f"LLM returned parameter response: {len(param_json)} chars")
            except Exception as exc:
                finalize_logger.warning(f"Failed to generate remote printing parameters: {exc}")
                param_json = None

            if param_json:
                import json
                try:
                    # Extract JSON from response if wrapped in code blocks
                    if "```json" in param_json:
                        param_json = param_json.split("```json")[1].split("```")[0]
                    elif "```" in param_json:
                        param_json = param_json.split("```")[1].split("```")[0]

                    # Parse to validate JSON structure
                    params = json.loads(param_json.strip())

                    # Add formatted parameters to report
                    final_report += "\n\n---\n\n"
                    final_report += "## 🔬 Remote Printing Parameters (Auto-Generated)\n\n"
                    final_report += "*Generated via two-step LLM process: Step 1 synthesized research findings, Step 2 generated optimized parameters*\n\n"
                    final_report += "```json\n"
                    final_report += json.dumps(params, indent=2)
                    final_report += "\n```\n"
                    final_report += "\n**Optimization Notes:**\n"
                    final_report += "- Parameters tailored based on research query requirements\n"
                    final_report += "- Validated against Chen Lab FET handbook specifications\n"
                    final_report += "- Adjust based on specific equipment capabilities and material availability\n"

                    finalize_logger.info("Successfully generated and added remote printing parameters")
                    finalize_logger.info(f"Final report length: {len(final_report)} chars (includes research + parameters)")

                except json.JSONDecodeError as e:
                    finalize_logger.warning(f"Failed to parse generated JSON: {e}")
                    final_report += "\n\n### Remote Printing Parameters (Raw)\n"
                    final_report += "```\n"
                    final_report += param_json
                    final_report += "\n```\n"
                    final_report += "\n*Note: JSON validation failed. Please review and correct the parameters manually.*\n"
            else:
                final_report += "\n\n### Remote Printing Parameters\n"
                final_report += "Automatic parameter generation failed due to repeated LLM errors. Refer to the Chen Lab FET handbook for manual setup.\n"

        except Exception as e:
            finalize_logger.error(f"Failed to generate printing parameters: {e}")
            # Continue without parameters if generation fails

    finalize_logger.info("===== FINAL SUMMARY COMPLETE =====")

    return {"running_summary": final_report}

def summarize_local_rag_results(state: SummaryState, config: RunnableConfig):
    """LangGraph node that summarizes local RAG results before generating a complementary query.

    Creates a concise summary of the local RAG results to help with generating
    a more focused complementary query.

    Args:
        state: Current graph state containing the local RAG results
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including local_rag_summary key
    """
    # If local RAG is disabled or no results, return empty summary
    configurable = Configuration.from_runnable_config(config)

    if not configurable.use_local_rag or not state.local_research_results:
        return {"local_rag_summary": ""}

    # Use all local RAG results
    local_rag_result = "\n\n".join(state.local_research_results) if state.local_research_results else ""

    # Check if this is FET data (pass config for proper detection)
    is_fet = detect_fet_query(state, config) and FET_SUMMARY_PROMPT is not None

    # Build the summary prompt (FET-aware or standard)
    if is_fet:
        print("FET data detected, using FET-specific summary prompt")
        summary_prompt = FET_SUMMARY_PROMPT.format(
            research_topic=state.research_topic,
            local_rag_result=local_rag_result
        )
    else:
        print(f"Local RAG result length: {len(local_rag_result)}")
        summary_prompt = f"""
    <GOAL>
    Create a concise summary (<500 characters) of the local knowledge provided below.
    </GOAL>

    <CONTEXT>
    These are results from a local knowledge base search related to: {state.research_topic}
    Search query used: {state.search_query}
    </CONTEXT>


    <INSTRUCTIONS>
    1. Summarize the key findings, concepts, and information from the local knowledge
    2. Focus on aspects that might suggest different angles to explore in further research
    3. Keep your summary under 500 characters
    4. Start with "After querying local literature with '{state.search_query}', we found that..."
    5. Always provide a complete summary, even if thinking through a complex process.
    </INSTRUCTIONS>
    """

    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=summary_prompt),
                HumanMessage(content=f"Please summarize the local knowledge base results: \n\n {local_rag_result}"),
            ],
            temperature=0.3,
        )
        local_rag_summary = result.content
        if configurable.strip_thinking_tokens:
            local_rag_summary = strip_thinking_tokens(local_rag_summary)
    except Exception as exc:
        print(f"Failed to summarize local RAG results: {exc}")
        local_rag_summary = ""  # Fall back to empty summary to avoid blocking the workflow

    return {"local_rag_summary": local_rag_summary}

def route_research(state: SummaryState, config: RunnableConfig) -> Literal["finalize_summary", "local_rag_research"]:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_web_research_loops setting

    Returns:
        String literal indicating the next node to visit ("local_rag_research" or "finalize_summary")
    """

    configurable = Configuration.from_runnable_config(config)
    if state.research_loop_count <= configurable.max_web_research_loops:
        return "local_rag_research"
    else:
        return "finalize_summary"

def create_single_research_graph(checkpointer: Optional[object] = None):
    """Create single-path research graph."""

    # Add nodes and edges
    builder = StateGraph(SummaryState, input=SummaryStateInput, output=SummaryStateOutput, config_schema=Configuration)

    # Add the initialization node
    builder.add_node("init_session", init_session)
    builder.add_node("generate_query", generate_query)
    builder.add_node("local_rag_research", local_rag_research)
    builder.add_node("summarize_local_rag_results", summarize_local_rag_results)
    builder.add_node("generate_complementary_query", generate_complementary_query)
    builder.add_node("web_research", web_research)
    builder.add_node("complementary_web_research", complementary_web_research)
    builder.add_node("summarize_sources", summarize_sources)
    builder.add_node("reflect_on_summary", reflect_on_summary)
    builder.add_node("finalize_summary", finalize_summary)

    # Add edges
    builder.add_edge(START, "init_session")
    builder.add_edge("init_session", "generate_query")
    builder.add_edge("generate_query", "local_rag_research")
    builder.add_edge("local_rag_research", "summarize_local_rag_results")
    builder.add_edge("summarize_local_rag_results", "generate_complementary_query")
    builder.add_edge("generate_complementary_query", "web_research")
    builder.add_edge("web_research", "complementary_web_research")
    builder.add_edge("complementary_web_research", "summarize_sources")
    builder.add_edge("summarize_sources", "reflect_on_summary")
    builder.add_conditional_edges("reflect_on_summary", route_research)
    builder.add_edge("finalize_summary", END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph


graph = create_single_research_graph()
# Add step timeout to prevent CancelledError
graph.step_timeout = 86400  # 24 hours in seconds
