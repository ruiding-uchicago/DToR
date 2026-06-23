import json
import uuid
import hashlib
import os
import logging
from datetime import datetime
from typing import List, Dict, Literal, Optional, Tuple
import re
import copy

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

from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import END

from ollama_deep_researcher.configuration import Configuration
from ollama_deep_researcher.dtor_state import DToRState, ResearchBranch
from ollama_deep_researcher.state import SummaryState
from ollama_deep_researcher.lmstudio import ChatLMStudio
from ollama_deep_researcher.openai_wrapper import ChatOpenAIWrapper
from ollama_deep_researcher.utils import strip_thinking_tokens, format_sources, deduplicate_and_format_sources
default_config_long_recursion = RunnableConfig(recursion_limit=300)

# Create loggers at module level but configure them dynamically
logger = logging.getLogger("dtor_nodes")
analysis_logger = logging.getLogger("dtor_nodes.analysis")
query_logger = logging.getLogger("dtor_nodes.query_gen")
routing_logger = logging.getLogger("dtor_nodes.routing")
finalize_logger = logging.getLogger("dtor_nodes.finalize")
reflect_logger = logging.getLogger("dtor_nodes.reflect")

# Don't propagate to avoid duplicate messages
analysis_logger.propagate = False
query_logger.propagate = False
routing_logger.propagate = False
finalize_logger.propagate = False
reflect_logger.propagate = False

# Function to set up logging with fresh timestamps for each session
def setup_logging():
    """Sets up logging with fresh timestamps for each research session"""
    # Clean up any existing handlers to prevent duplicate logs
    for specific_logger in [logger, analysis_logger, query_logger, routing_logger, finalize_logger, reflect_logger]:
        while specific_logger.handlers:
            specific_logger.handlers.pop()
    
    # Set up logging to files
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set up log levels - use INFO for production
    logger.setLevel(logging.INFO)
    analysis_logger.setLevel(logging.INFO)
    query_logger.setLevel(logging.INFO)
    routing_logger.setLevel(logging.INFO)
    finalize_logger.setLevel(logging.INFO)
    reflect_logger.setLevel(logging.INFO)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')  # Simpler format for console
    
    # Main logger setup
    main_log_file = os.path.join(log_dir, f"dtor_nodes_{timestamp}.log")
    file_handler = logging.FileHandler(main_log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Specialized loggers setup
    analysis_log_file = os.path.join(log_dir, f"analysis_{timestamp}.log")
    analysis_handler = logging.FileHandler(analysis_log_file)
    analysis_handler.setFormatter(file_formatter)
    analysis_logger.addHandler(analysis_handler)
    
    query_log_file = os.path.join(log_dir, f"query_gen_{timestamp}.log")
    query_handler = logging.FileHandler(query_log_file)
    query_handler.setFormatter(file_formatter)
    query_logger.addHandler(query_handler)
    
    routing_log_file = os.path.join(log_dir, f"routing_{timestamp}.log")
    routing_handler = logging.FileHandler(routing_log_file)
    routing_handler.setFormatter(file_formatter)
    routing_logger.addHandler(routing_handler)
    
    finalize_log_file = os.path.join(log_dir, f"finalize_{timestamp}.log")
    finalize_handler = logging.FileHandler(finalize_log_file)
    finalize_handler.setFormatter(file_formatter)
    finalize_logger.addHandler(finalize_handler)
    
    reflect_log_file = os.path.join(log_dir, f"reflect_{timestamp}.log")
    reflect_handler = logging.FileHandler(reflect_log_file)
    reflect_handler.setFormatter(file_formatter)
    reflect_logger.addHandler(reflect_handler)
    
    # Add console handlers to show important messages
    for specific_logger in [analysis_logger, query_logger, routing_logger, finalize_logger, reflect_logger]:
        specific_console = logging.StreamHandler()
        specific_console.setLevel(logging.INFO)
        specific_console.setFormatter(console_formatter)
        specific_logger.addHandler(specific_console)
    
    logger.info("Logging initialized with timestamp: %s - Check logs directory for detailed logs", timestamp)
    return timestamp

# Initialize logging on module import (can be re-initialized later)
current_timestamp = setup_logging()

# Helper function to get LLM based on configuration
LOCAL_MODEL_TIMEOUT_SECONDS = float(os.environ.get("LOCAL_LLM_TIMEOUT_SECONDS", 300))


def get_llm(
    configurable,
    temperature: float = 0,
    json_mode: bool = False,
    provider_override: Optional[str] = None,
    model_override: Optional[str] = None,
    timeout_seconds: float = LOCAL_MODEL_TIMEOUT_SECONDS,
):
    """Helper to get the appropriate LLM based on provider configuration."""
    provider = provider_override or configurable.llm_provider

    if provider in {"ollama", "lmstudio"}:
        model_name = model_override or configurable.local_llm
        use_json_format = json_mode and "gpt-oss" not in model_name.lower()
        format_param = "json" if use_json_format else None

        if provider == "lmstudio":
            return ChatLMStudio(
                base_url=configurable.lmstudio_base_url,
                model=model_name,
                temperature=temperature,
                client_kwargs={"timeout": timeout_seconds},
                format=format_param
            )
        # Default to Ollama for local provider
        return ChatOllama(
            base_url=configurable.ollama_base_url,
            model=model_name,
            temperature=temperature,
            client_kwargs={"timeout": timeout_seconds},
            format=format_param
        )

    if provider == "openai":
        model_name = model_override or getattr(configurable, "openai_model", None) or configurable.local_llm
        format_param = "json" if json_mode else None
        if not configurable.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return ChatOpenAIWrapper(
            api_key=configurable.openai_api_key,
            model=model_name,
            temperature=temperature,
            format=format_param
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


def _normalize_messages(payload) -> List[BaseMessage]:
    """Normalize incoming payload into a list of LangChain messages."""
    if isinstance(payload, list):
        normalized = []
        for item in payload:
            if isinstance(item, BaseMessage):
                normalized.append(item)
            else:
                normalized.append(HumanMessage(content=str(item)))
        return normalized

    if isinstance(payload, BaseMessage):
        return [payload]

    # Treat everything else as a human message
    return [HumanMessage(content=str(payload))]


def _gather_openai_models(configurable: Configuration) -> List[str]:
    models: List[str] = []
    primary = getattr(configurable, "openai_model", None)
    if primary:
        models.append(primary)
    fallback_list = getattr(configurable, "openai_fallback_models", None) or []
    for model in fallback_list:
        if model and model not in models:
            models.append(model)
    return models


def invoke_with_failover(
    configurable: Configuration,
    payload,
    *,
    temperature: float = 0,
    json_mode: bool = False,
) -> BaseMessage:
    """Try the configured provider and fall back to OpenAI models if needed."""

    attempts: List[Tuple[str, Optional[str]]] = []
    primary_provider = configurable.llm_provider

    openai_models = _gather_openai_models(configurable) if configurable.openai_api_key else []

    if primary_provider == "openai":
        for model_name in openai_models:
            attempts.append(("openai", model_name))
    else:
        attempts.append((primary_provider, None))
        if openai_models:
            for model_name in openai_models:
                attempts.append(("openai", model_name))

    # Remove duplicates while preserving order
    seen = set()
    unique_attempts: List[Tuple[str, Optional[str]]] = []
    for attempt in attempts:
        if attempt not in seen:
            unique_attempts.append(attempt)
            seen.add(attempt)

    messages = _normalize_messages(payload)
    errors: List[Tuple[str, Optional[str], Exception]] = []

    for index, (provider, model_name) in enumerate(unique_attempts, start=1):
        provider_label = f"{provider}:{model_name or configurable.local_llm}"
        try:
            logger.info(
                "LLM attempt %s/%s using %s (json_mode=%s)",
                index,
                len(unique_attempts),
                provider_label,
                json_mode,
            )
            llm = get_llm(
                configurable,
                temperature=temperature,
                json_mode=json_mode,
                provider_override=provider,
                model_override=model_name,
                timeout_seconds=LOCAL_MODEL_TIMEOUT_SECONDS,
            )
            result = llm.invoke(messages)
            if index > 1:
                logger.info("LLM fallback succeeded with %s", provider_label)
            return result
        except Exception as exc:
            logger.warning("LLM attempt failed for %s: %s", provider_label, exc)
            errors.append((provider, model_name, exc))

    error_summary = "; ".join(
        f"{prov}:{model or configurable.local_llm} -> {repr(err)}" for prov, model, err in errors
    )
    raise RuntimeError(f"All LLM providers failed ({error_summary})")

# 1. Initial Query Diversification Node
def diversify_initial_query(state: DToRState, config: RunnableConfig):
    """
    Takes user's research question and generates 3-5 diverse perspectives/approaches.
    Each perspective becomes a root of a separate branch in the tree.
    """
    import json  # Move import to top of function to avoid UnboundLocalError

    configurable = Configuration.from_runnable_config(config)

    # Skip if not in DToR mode (using either state mode or config mode)
    if state.mode != "dtor" and getattr(configurable, 'research_mode', 'single') != "dtor":
        return {}

    # Check if we should load perspectives from a file (Stage 2 scenario)
    perspectives_file = os.environ.get('PERSPECTIVES_FILE')
    if perspectives_file and os.path.exists(perspectives_file):
        logger.info(f"Loading perspectives from {perspectives_file}")
        with open(perspectives_file, 'r') as f:
            perspectives_data = json.load(f)

        # Create branches from loaded perspectives
        branches = {}
        for perspective_info in perspectives_data.get('perspectives', []):
            branch_id = perspective_info['id']
            perspective = perspective_info['perspective']

            # Create initial research node for the perspective
            initial_node = SummaryState(
                research_topic=f"{state.research_topic}: (Make sure to focus on this perspective) {perspective} - Follow all existing research in this area, carefully identifying gaps in current knowledge and proposing novel connections between different research domains.",
                search_query="",
                research_loop_count=0,
                processing_status="pending"
            )

            branch = ResearchBranch(
                branch_id=branch_id,
                depth=0,
                perspective=perspective,
                research_nodes=[initial_node],
                remaining_budget=configurable.nodes_per_branch
            )

            branches[branch_id] = branch
            logger.info(f"Loaded branch {branch_id[:8]}... for perspective: {perspective}")

        # Set the active branch based on TARGET_BRANCH_ID if specified
        target_branch_id = os.environ.get('TARGET_BRANCH_ID')
        active_branch = target_branch_id if target_branch_id in branches else next(iter(branches.keys()))

        logger.info(f"Loaded {len(branches)} branches from perspectives file, active: {active_branch}")

        return {
            "branches": branches,
            "active_branch_id": active_branch,
            "max_branches": configurable.max_branches,
            "max_branch_depth": configurable.max_branch_depth,
            "nodes_per_branch": configurable.nodes_per_branch
        }

    # Check if this is a resume scenario (checkpoint recovery)
    # If research_topic already contains the perspective marker, we're resuming
    if ": (Make sure to focus on this perspective)" in state.research_topic:
        logger.info("Resume scenario detected - reconstructing branches with stable IDs")

        # Extract perspective information from the research topic
        import re
        perspective_match = re.search(r"perspective\) (.+?) - ", state.research_topic)
        perspective = perspective_match.group(1) if perspective_match else "Resumed Research"

        # Generate stable branch ID based on the research topic
        stable_seed = f"{state.research_topic}_resume"
        branch_id = hashlib.md5(stable_seed.encode()).hexdigest()[:16]

        # Create a single branch for the resumed research
        branch = ResearchBranch(
            branch_id=branch_id,
            depth=0,
            perspective=perspective,
            research_nodes=[SummaryState(
                research_topic=state.research_topic,
                search_query="",
                research_loop_count=0  # Will be restored by checkpoint
            )],
            remaining_budget=configurable.nodes_per_branch
        )

        logger.info(f"Reconstructed branch with stable ID: {branch_id[:8]}... for perspective: {perspective}")

        return {
            "branches": {branch_id: branch},
            "active_branch_id": branch_id,
            "max_branches": configurable.max_branches,
            "max_branch_depth": configurable.max_branch_depth,
            "nodes_per_branch": configurable.nodes_per_branch
        }

    # --- Initialize state from config ---
    # Ensure the state reflects the runtime configuration for key parameters
    state.max_branches = configurable.max_branches
    state.max_branch_depth = configurable.max_branch_depth
    state.nodes_per_branch = configurable.nodes_per_branch
    logger.info(f"Initialized DToR state with config: max_branches={state.max_branches}, max_depth={state.max_branch_depth}, nodes_per_branch={state.nodes_per_branch}")
    # --- End Initialization ---

    # Create the prompt for diversification
    # Use the now-updated state.max_branches value
    diversification_prompt = f"""
    You are a research topic diversification expert. Your task is to generate {state.max_branches} diverse perspectives
    or approaches to address the following research topic: "{state.research_topic}"
    
    Each perspective should:
    1. Represent a distinct angle or lens through which to explore the topic
    2. Be specific enough to guide research in a clear direction
    3. Collectively cover a broad range of viewpoints related to the topic
    
    <FORMAT>
    Format your response as a JSON object with an array of perspectives:
    {{
        "perspectives": [
            {{
                "title": "Brief title of this perspective",
                "description": "One paragraph explaining this research approach",
                "query": "An effective web search query to begin researching this perspective"
            }},
            ... (repeat for each perspective)
        ]
    }}
    </FORMAT>
    """
    
    # Generate diverse perspectives
    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=diversification_prompt),
                HumanMessage(
                    content=(
                        f"Generate {state.max_branches} diverse perspectives for researching: {state.research_topic}"
                    )
                ),
            ],
            temperature=0,
            json_mode=True,
        )
        
        content = result.content
        
        # Parse the JSON response
        try:
            cleaned_content = clean_code_blocks(content)
            response_data = json.loads(cleaned_content)
            perspectives = response_data.get("perspectives", [])
            
            # Verify we have valid perspectives
            if not perspectives or not all(isinstance(p, dict) and "title" in p for p in perspectives):
                raise ValueError("Invalid perspectives format")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise Exception(f"JSON parsing failed: {str(e)}")
            
    except Exception as e:
        logger.info(f"JSON mode failed for diversify_initial_query, trying with standard mode...")
        
        # Fallback to standard mode if JSON mode fails
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=diversification_prompt),
                HumanMessage(
                    content=(
                        f"Generate {state.max_branches} diverse perspectives for researching: {state.research_topic}"
                    )
                ),
            ],
            temperature=0,
            json_mode=False,
        )
        content = result.content
        
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
        
        # Try to extract JSON from the text response
        try:
            # Find JSON-like structure in the text
            import re
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                json_str = match.group(0)
                cleaned_json = clean_code_blocks(json_str)
                response_data = json.loads(cleaned_json)
                perspectives = response_data.get("perspectives", [])
                
                # Verify we have valid perspectives
                if perspectives and all(isinstance(p, dict) and "title" in p for p in perspectives):
                    logger.info("Successfully extracted JSON from text response")
                else:
                    raise ValueError("Invalid perspectives in extracted JSON")
            else:
                raise ValueError("No JSON-like structure found in the response")
                
        except Exception as e:
            logger.warning(f"Failed to extract JSON from text response: {str(e)}")
            # Create simple default perspectives as final fallback
            perspectives = [
                {
                    "title": "Technical Analysis",
                    "description": f"Technical and methodological approach to analyze {state.research_topic}",
                    "query": f"{state.research_topic} technical methodology"
                },
                {
                    "title": "Application Focus",
                    "description": f"Practical application and implementation approach for {state.research_topic}",
                    "query": f"{state.research_topic} applications implementation"
                },
                {
                    "title": "Comparative Study",
                    "description": f"Comparative analysis and evaluation approach for {state.research_topic}",
                    "query": f"{state.research_topic} comparison evaluation"
                }
            ][:state.max_branches]
    
    # Create branches for each perspective
    branches = {}
    # Use the now-updated state.max_branches and state.nodes_per_branch
    for idx, perspective in enumerate(perspectives[:state.max_branches]):
        # Generate stable, deterministic branch ID instead of random UUID
        # This ensures the same branch IDs are generated if we restart
        stable_seed = f"{state.research_topic}_{idx}_{perspective['title']}"
        branch_id = hashlib.md5(stable_seed.encode()).hexdigest()[:16]
        logger.info(f"Creating branch with stable ID: {branch_id[:8]}... for perspective: {perspective['title']}")
        
        # Create initial SummaryState for this branch
        initial_state = SummaryState(
            research_topic=f"{state.research_topic}: (Make sure to focus on this perspective) {perspective['title']} - {perspective['query']}",
            search_query=perspective['query'],
            research_loop_count=0
        )
        
        # Create the branch using the config value for nodes_per_branch
        branch = ResearchBranch(
            branch_id=branch_id,
            depth=0,
            perspective=perspective['title'],
            research_nodes=[initial_state],
            remaining_budget=state.nodes_per_branch # Use value from state (now updated from config)
        )
        
        branches[branch_id] = branch
    
    # Set the first branch as active if we have branches
    active_branch_id = next(iter(branches.keys())) if branches else None
    
    # Return the updated state values along with branches
    return {
        "branches": branches,
        "active_branch_id": active_branch_id,
        "max_branches": state.max_branches,
        "max_branch_depth": state.max_branch_depth,
        "nodes_per_branch": state.nodes_per_branch
    }

# 2. Analysis Node
def analyze_research_report(state: DToRState, config: RunnableConfig):
    """
    Takes a completed research report as input, identifies knowledge gaps and potential new directions.
    Decides whether to expand (branch), terminate (prune), or finalize.
    """
    configurable = Configuration.from_runnable_config(config)
    
    # Log the input state
    analysis_logger.info(f"===== ANALYZING RESEARCH - INPUT STATE =====")
    analysis_logger.info(f"Research topic: {state.research_topic}")
    analysis_logger.info(f"Mode: {state.mode}")
    analysis_logger.info(f"Active branch ID: {state.active_branch_id}")
    analysis_logger.info(f"Number of branches: {len(state.branches)}")
    analysis_logger.info(f"Is complete: {state.is_complete}")
    
    # Skip if not in DToR mode or no active branch
    if state.mode != "dtor" or not state.active_branch_id:
        analysis_logger.info("Skipping analyze_research_report: Not in DToR mode or no active branch")
        return {}
    
    # Get the current active branch
    branch = state.branches[state.active_branch_id]
    
    # Log branch details
    analysis_logger.info(f"Active branch details:")
    analysis_logger.info(f"  Perspective: {branch.perspective}")
    analysis_logger.info(f"  Depth: {branch.depth}/{state.max_branch_depth}")
    analysis_logger.info(f"  Remaining budget: {branch.remaining_budget}")
    analysis_logger.info(f"  Is complete: {branch.is_complete}")
    analysis_logger.info(f"  Research nodes: {len(branch.research_nodes)}")
    
    # Skip if this branch has no research nodes
    if not branch.research_nodes:
        analysis_logger.info("Skipping analyze_research_report: Branch has no research nodes")
        return {}
    
    # Find the next completed but not analyzed node
    latest_research = None
    node_index = -1
    
    for idx, node in enumerate(branch.research_nodes):
        if hasattr(node, 'processing_status') and node.processing_status == "completed":
            latest_research = node
            node_index = idx
            break
    
    # If no completed node was found, skip analysis
    if latest_research is None:
        analysis_logger.info("Skipping analyze_research_report: No completed nodes ready for analysis")
        return {}
    
    # Log research node details
    analysis_logger.info(f"Latest research node details:")
    analysis_logger.info(f"  Node ID: {latest_research.node_id if hasattr(latest_research, 'node_id') else 'unknown'}")
    analysis_logger.info(f"  Research topic: {latest_research.research_topic}")
    analysis_logger.info(f"  Summary length: {len(latest_research.running_summary) if latest_research.running_summary else 0} chars")
    
    # Log a sample of the summary content
    if latest_research.running_summary:
        sample_length = min(50, len(latest_research.running_summary))
        summary_sample = latest_research.running_summary[:sample_length] + "..." if len(latest_research.running_summary) > sample_length else latest_research.running_summary
        analysis_logger.info(f"  Summary sample (first {sample_length} chars): {summary_sample}")
    else:
        analysis_logger.info("  No summary content available")
    
    # Debug information
    analysis_logger.info(f"===== ANALYZING RESEARCH =====")
    analysis_logger.info(f"Branch ID: {state.active_branch_id}")
    analysis_logger.info(f"Branch perspective: {branch.perspective}")
    analysis_logger.info(f"Branch depth: {branch.depth}/{state.max_branch_depth}")
    analysis_logger.info(f"Remaining budget: {branch.remaining_budget}")
    analysis_logger.info(f"Research topic: {latest_research.research_topic}")
    analysis_logger.info(f"Summary length: {len(latest_research.running_summary) if latest_research.running_summary else 0} chars")
    
    # For early nodes, encourage expansion rather than pruning
    force_expand = branch.depth < state.max_branch_depth - 1 and branch.remaining_budget > 0
    if force_expand:
        analysis_logger.info("NOTICE: Early in branch development, forcing EXPAND decision")
    
    # Prepare analysis prompt
    analysis_prompt = f"""
    You are a research analysis expert. Analyze the following research summary to identify knowledge gaps 
    and potential new directions for further research.
    
    <RESEARCH SUMMARY>
    {latest_research.running_summary if latest_research.running_summary else "No research summary available yet."}
    </RESEARCH SUMMARY>
    
    <CONTEXT>
    Branch perspective: {branch.perspective}
    Current branch depth: {branch.depth}
    Remaining research budget: {branch.remaining_budget}
    Maximum branch depth: {state.max_branch_depth}
    </CONTEXT>
    
    <TASK>
    Analyze the research summary to determine the next action:
    1. "expand" - Continue this branch with new queries (if budget and depth allow)
    2. "prune" - Terminate this branch (if it's exhausted or unproductive)
    3. "finalize" - Complete this branch with its current findings
    
    {"IMPORTANT: Since this branch is still early in its development, you should strongly prefer to EXPAND it with new queries unless there is a compelling reason not to." if force_expand else ""}
    
    Identify 2-3 specific knowledge gaps, areas that need further exploration or questions that remain unanswered.
    
    <FORMAT>
    Format your response as a JSON object with the following fields:
    {{
        "decision": "expand|prune|finalize",
        "rationale": "Brief explanation of your decision",
        "knowledge_gaps": [
            {{
                "topic": "Description of knowledge gap 1",
                "query": "Effective web search query to address this gap"
            }},
            ... (repeat for each gap)
        ]
    }}
    </FORMAT>
    """
    
    # Generate analysis
    analysis_logger.info("Sending analysis prompt to LLM...")
    analysis_logger.info("Attempting with JSON mode enabled")
    
    try:
        result = invoke_with_failover(
            configurable,
            analysis_prompt,
            temperature=0,
            json_mode=True,
        )
        content = result.content
        analysis_logger.info(f"LLM Response received (JSON mode), length: {len(content)} chars")
        analysis_logger.info(f"DEBUG: Complete JSON response: {content}")
        
        # Parse the JSON response
        try:
            cleaned_content = clean_code_blocks(content)
            response_data = json.loads(cleaned_content)
            
            # Verify required fields
            if not all(key in response_data for key in ["decision", "rationale"]):
                analysis_logger.warning("JSON parsed but missing required fields")
                raise ValueError("Missing required fields in JSON response")
                
            decision = response_data.get("decision", "").lower()
            rationale = response_data.get("rationale", "")
            knowledge_gaps = response_data.get("knowledge_gaps", [])
            
            # Validate decision
            if decision not in ["expand", "prune", "finalize"]:
                analysis_logger.warning(f"Invalid decision: {decision}")
                raise ValueError(f"Invalid decision: {decision}")
                
            analysis_logger.info("JSON parsing successful")
            
        except (json.JSONDecodeError, ValueError) as e:
            analysis_logger.warning(f"JSON parsing failed: {str(e)}")
            raise
            
    except Exception as e:
        analysis_logger.info(f"JSON mode failed, trying with standard mode...")
        
        # Fallback to standard mode if JSON mode fails
        result = invoke_with_failover(
            configurable,
            analysis_prompt,
            temperature=0,
            json_mode=False,
        )
        content = result.content
        analysis_logger.info(f"LLM Response received (standard mode), length: {len(content)} chars")
        analysis_logger.info(f"DEBUG: Complete standard response: {content}")
        
        # Try to extract JSON from the text response
        try:
            # Find JSON-like structure in the text
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                json_str = match.group(0)
                cleaned_json = clean_code_blocks(json_str)
                response_data = json.loads(cleaned_json)
                
                # Verify required fields
                if all(key in response_data for key in ["decision", "rationale"]):
                    decision = response_data.get("decision", "").lower()
                    rationale = response_data.get("rationale", "")
                    knowledge_gaps = response_data.get("knowledge_gaps", [])
                    
                    # Validate decision
                    if decision not in ["expand", "prune", "finalize"]:
                        analysis_logger.warning(f"Invalid decision: {decision}")
                        # Default to expand if in early stages, otherwise finalize
                        decision = "expand" if force_expand else "finalize"
                    
                    analysis_logger.info("Successfully extracted JSON from text response")
                else:
                    raise ValueError("Missing required fields in extracted JSON")
            else:
                raise ValueError("No JSON-like structure found in the response")
                
        except Exception as e:
            analysis_logger.warning(f"Failed to extract JSON from text response: {str(e)}")
            # Default to a safe fallback
            decision = "expand" if force_expand else "finalize"
            rationale = "Default decision due to parsing failure"
            knowledge_gaps = []
    
    # Log the results
    analysis_logger.info(f"Parsing LLM response as JSON...")
    analysis_logger.info(f"Decision: {decision}")
    analysis_logger.info(f"Rationale: {rationale}")
    analysis_logger.info(f"Knowledge gaps: {len(knowledge_gaps)}")
    
    # Log each knowledge gap
    for i, gap in enumerate(knowledge_gaps):
        if isinstance(gap, dict):
            topic = gap.get('topic', 'Unknown topic')
            query = gap.get('query', 'Unknown query')
            analysis_logger.info(f"  Gap {i+1}: {topic}")
            analysis_logger.info(f"    Query: {query}")
    
    # --- Enforce Max Depth Limit --- 
    if branch.depth >= state.max_branch_depth:
        if decision == "expand":
            analysis_logger.warning(f"Max depth ({state.max_branch_depth}) reached, but LLM decided to expand. Overriding to FINALIZE.")
            decision = "finalize"
            rationale += " (Forced finalize due to max depth)"
            # Ensure no knowledge gaps are passed on when forcing finalize
            knowledge_gaps = [] 
        else:
             analysis_logger.info(f"Max depth ({state.max_branch_depth}) reached. Decision is '{decision}'.")
    # --- End Max Depth Enforcement ---

    # Update the branch based on the decision
    updated_branches = state.branches.copy()
    branch_update = copy.deepcopy(updated_branches[state.active_branch_id])
    
    # Mark the node as analyzed
    branch_update.research_nodes[node_index].processing_status = "analyzed"
    
    if decision == "expand":
        # Branch will continue, don't mark as complete
        branch_update.is_complete = False
        if branch.remaining_budget > 0:
            analysis_logger.info(f"Decision: EXPAND branch (remaining budget: {branch.remaining_budget})")
        else:
            analysis_logger.info(f"Decision: EXPAND branch")
    else:
        # Branch is complete (pruned or finalized)
        branch_update.is_complete = True
        analysis_logger.info(f"Decision: {decision.upper()} branch (complete)")
    
    updated_branches[state.active_branch_id] = branch_update
    
    # Determine if knowledge gaps should be returned
    # Only return gaps if decision is expand AND we haven't hit the max depth
    should_return_gaps = decision == "expand" and branch.depth < state.max_branch_depth

    analysis_logger.info(f"Returning {len(knowledge_gaps) if should_return_gaps else 0} knowledge gaps for next step")
    
    # Return the updated state and knowledge gaps for query generation
    return_dict = {
        "branches": updated_branches,
        "knowledge_gaps": knowledge_gaps if should_return_gaps else []
    }
    
    # Log the knowledge gaps being returned for debugging
    if should_return_gaps:
        analysis_logger.info(f"DEBUG: Returning knowledge_gaps with {len(knowledge_gaps)} items")
        for i, gap in enumerate(knowledge_gaps):
            analysis_logger.info(f"DEBUG: knowledge_gap[{i}] - topic: '{gap.get('topic')}', query: '{gap.get('query')}'")
    else:
        analysis_logger.info(f"DEBUG: Not returning any knowledge_gaps (should_return_gaps={should_return_gaps})")
    
    analysis_logger.info("===== ANALYSIS COMPLETE =====")
    
    return return_dict

# Helper function to generate branch summary
def generate_branch_summary(branch: ResearchBranch, latest_summary: str, configurable: Configuration) -> str:
    """Generate a summary for a completed branch."""
    summary_prompt = f"""
    You are a research synthesis expert. Create a coherent summary of the findings from this research branch.
    
    <BRANCH INFO>
    Research perspective: {branch.perspective}
    </BRANCH INFO>
    
    <FINAL RESEARCH SUMMARY>
    {latest_summary}
    </FINAL RESEARCH SUMMARY>
    
    <TASK>
    Create a comprehensive summary of the key findings, insights, and conclusions from this research branch.
    Focus on what makes this perspective unique and valuable to the overall research topic.
    Your summary should be well-structured and highlight the most important discoveries.
    Always provide a complete summary, even if thinking through a complex process.
    </TASK>
    """
    
    # Generate branch summary
    result = invoke_with_failover(
        configurable,
        [
            SystemMessage(content=summary_prompt),
            HumanMessage(
                content=(
                    f"Synthesize the research findings for the '{branch.perspective}' perspective."
                )
            ),
        ],
        temperature=0,
    )
    
    summary = result.content
    if configurable.strip_thinking_tokens:
        summary = strip_thinking_tokens(summary)
    
    return summary

# 3. Query Generation Node
def generate_follow_up_queries(state: DToRState, config: RunnableConfig):
    """
    Takes knowledge gaps from analysis and generates new research nodes.
    Creates a new research node for each gap identified in the analysis.
    """
    configurable = Configuration.from_runnable_config(config)
    
    # Debug the state object
    query_logger.info(f"DEBUG: State object type: {type(state)}")
    query_logger.info(f"DEBUG: State attributes: {dir(state)}")
    query_logger.info(f"DEBUG: Knowledge gaps attribute exists: {hasattr(state, 'knowledge_gaps')}")
    
    if hasattr(state, 'knowledge_gaps'):
        query_logger.info(f"DEBUG: State.knowledge_gaps type: {type(state.knowledge_gaps)}")
    
    # Skip if not in DToR mode
    if state.mode != "dtor":
        query_logger.info("Skipping generate_follow_up_queries: Not in DToR mode")
        return {}
    
    # Skip if no knowledge gaps were identified
    knowledge_gaps = getattr(state, 'knowledge_gaps', [])
    if not knowledge_gaps:
        query_logger.info("Skipping generate_follow_up_queries: No knowledge gaps provided")
        return {}
    
    # Get the active branch
    if not state.active_branch_id or state.active_branch_id not in state.branches:
        query_logger.info("Skipping generate_follow_up_queries: No active branch")
        return {}
    
    branch = state.branches[state.active_branch_id]
    
    # Skip if branch is complete or out of budget
    if branch.is_complete or branch.remaining_budget <= 0:
        query_logger.info(f"Skipping generate_follow_up_queries: Branch has no budget left ({branch.remaining_budget}) or is complete ({branch.is_complete})")
        return {}
    
    # Log what we're working with
    query_logger.info(f"===== GENERATING FOLLOW-UP QUERIES =====")
    query_logger.info(f"Branch: {branch.perspective} (ID: {state.active_branch_id})")
    query_logger.info(f"KNOWLEDGE GAPS RECEIVED FROM ANALYSIS: {len(knowledge_gaps)}")
    
    # Log each knowledge gap
    for i, gap in enumerate(knowledge_gaps):
        query_logger.info(f"  {i+1}. Topic: {gap.get('topic', 'No topic')}")
        query_logger.info(f"     Query: {gap.get('query', 'No query')}")
    
    # Extract original research question
    # Start with the state's research topic
    original_research_question = state.research_topic
    
    # If there are research nodes, extract from first node
    if branch.research_nodes:
        # Get first research node which should contain the original question
        first_node = branch.research_nodes[0]
        if hasattr(first_node, 'research_topic'):
            # Extract the original part before any "Focus:" or similar markers
            topic = first_node.research_topic
            focus_markers = ["(Focus:", "- Focus:", "(Make sure to focus", ": (Make sure"]
            for marker in focus_markers:
                if marker in topic:
                    original_research_question = topic.split(marker)[0].strip()
                    break
    
    query_logger.info(f"Original research question: {original_research_question}")
    query_logger.info(f"Branch perspective: {branch.perspective}")
    
    # Create new research nodes based on the knowledge gaps
    new_research_nodes = []
    
    for gap in knowledge_gaps:
        # Make sure we have the required fields in the gap
        topic = gap.get('topic', 'Further research')
        query = gap.get('query', f"Advanced research on {branch.perspective}")
        
        # Create a refined research topic that doesn't accumulate previous additions
        # Instead, it combines the original question with the perspective and the new topic
        refined_research_topic = f"{original_research_question} (Focus: {branch.perspective} - {topic})"
        
        query_logger.info(f"Creating new research node:")
        query_logger.info(f"  Topic: {refined_research_topic}")
        query_logger.info(f"  Query: {query}")
        
        # Create a new research state for each knowledge gap
        new_state = SummaryState(
            research_topic=refined_research_topic,
            search_query=query,
            research_loop_count=0,
            # Set initial processing status to pending
            processing_status="pending"
        )
        new_research_nodes.append(new_state)
    
    query_logger.info(f"Created {len(new_research_nodes)} new research nodes for branch {branch.perspective}")
    
    # Update the branch with new research nodes and decrement budget
    updated_branches = state.branches.copy()
    branch_update = updated_branches[state.active_branch_id]
    
    # Only add as many nodes as we have budget for
    nodes_to_add = min(len(new_research_nodes), branch.remaining_budget)
    branch_update.research_nodes.extend(new_research_nodes[:nodes_to_add])
    branch_update.remaining_budget -= nodes_to_add
    branch_update.depth += 1
    
    query_logger.info(f"Added {nodes_to_add} nodes to branch, new depth: {branch_update.depth}, remaining budget: {branch_update.remaining_budget}")
    query_logger.info("===== QUERY GENERATION COMPLETE =====")
    
    updated_branches[state.active_branch_id] = branch_update
    
    return {
        "branches": updated_branches
    }

# 4. Branch Synthesis Node
def synthesize_branch(state: DToRState, config: RunnableConfig):
    """
    Activates when a branch reaches max depth or exhausts its budget.
    Analyzes all research reports within that specific branch.
    Creates a coherent branch-level summary report.
    """
    configurable = Configuration.from_runnable_config(config)
    
    # Skip if not in DToR mode
    if state.mode != "dtor":
        return {}
    
    # Get the current active branch
    if not state.active_branch_id or state.active_branch_id not in state.branches:
        return {}
    
    branch = state.branches[state.active_branch_id]
    
    # Skip if branch already has a summary (but allow complete branches without summary)
    if branch.branch_summary:
        return {}
    
    # Get all research summaries from this branch
    summaries = [node.running_summary for node in branch.research_nodes if node.running_summary]
    
    if not summaries:
        # No summaries to synthesize
        return {}
    
    # Get all sources from this branch
    all_branch_sources = []
    for node in branch.research_nodes:
        if hasattr(node, 'sources_gathered'):
            all_branch_sources.extend(node.sources_gathered)
        if hasattr(node, 'complementary_sources_gathered'):
            all_branch_sources.extend(node.complementary_sources_gathered)
        if hasattr(node, 'local_sources_gathered'):
            all_branch_sources.extend(node.local_sources_gathered)
    research_summaries = "\n\n---\n\n".join(summaries)
    # Format the combined summary prompt
    synthesis_prompt = f"""
    You are a research synthesis expert.
    Your task is to create a coherent summary report integrating findings from the provided research summaries, focusing on the specified perspective.
    Highlight key findings, patterns, conclusions, discoveries, and insights **-include more than 2 numeric figures (e.g., limits-of-detection, accuracies, costs) if present in the summaries**.
    Structure your summary with clear sections and headings. Finish with a one-line "Confidence: High/Medium/Low" assessment.
    Always provide a complete summary, even if thinking through a complex process.
    """
    
    human_message_content = f"""
    Context: The following summaries explore the '{branch.perspective}' perspective, which is one angle for investigating the broader research topic: '{state.research_topic}'.
    
    Research Perspective: {branch.perspective}
    
    Research Summaries:
    {research_summaries}
    
    Task: Synthesize the research findings based on the perspective and summaries provided above. Frame the synthesis acknowledging its role within the larger research topic.
    **Deliverable layout** A. Consolidated Insights (~6 bullets) B. Divergent Claims (bullet pairs statement vs. counter-statement) C. Notable Gaps (~3 bullets) D. Confidence E. Notable Candidates - list the distinct materials, probes, or techniques that surface in this branch (separate with commas).
    """
    
    # Generate branch synthesis
    result = invoke_with_failover(
        configurable,
        [
            SystemMessage(content=synthesis_prompt),
            HumanMessage(content=human_message_content),
        ],
        temperature=0,
    )
    
    branch_summary = result.content
    if configurable.strip_thinking_tokens:
        branch_summary = strip_thinking_tokens(branch_summary)
    
    # Update the branch with its summary
    updated_branches = state.branches.copy()
    branch_update = updated_branches[state.active_branch_id]
    branch_update.branch_summary = branch_summary
    updated_branches[state.active_branch_id] = branch_update
    
    # Add formatted sources to the global sources list
    formatted_sources = deduplicate_and_format_sources(all_branch_sources, max_tokens_per_source=2500)
    
    # --- ADD SAVING LOGIC ---
    try:
        # Define base directory and create subfolder based on initial topic
        base_dir = "synthesis_branches_and_final"
        
        # Helper function to sanitize text for directory/file names
        def sanitize_for_path(text, num_words=5, max_len=50):
            words = text.split()[:num_words]
            sanitized = "_".join(words)
            sanitized = re.sub(r'[^\w\\-]+', '_', sanitized) # Keep alphanumeric, underscore, hyphen
            sanitized = re.sub(r'_+', '_', sanitized) # Replace multiple underscores
            sanitized = sanitized.strip('_')
            return sanitized[:max_len]

        # Get the initial topic from the state
        initial_topic = state.research_topic
        subfolder_name = sanitize_for_path(initial_topic)
        
        save_dir = os.path.join(base_dir, subfolder_name)
        os.makedirs(save_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize perspective for filename
        safe_perspective = re.sub(r'[^a-zA-Z0-9_-]', '_', branch.perspective)[:50]
        filename = os.path.join(save_dir, f"branch_{branch.branch_id[:8]}_{safe_perspective}_{timestamp}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Branch Synthesis: {branch.perspective}\\n")
            f.write(f"## Branch ID: {branch.branch_id}\\n")
            # Check if parent_branch_id exists before writing
            if hasattr(branch, 'parent_branch_id') and branch.parent_branch_id:
                 f.write(f"## Parent Branch ID: {branch.parent_branch_id}\\n")
            f.write(f"## Depth: {branch.depth}\\n\\n")
            f.write(branch_summary)
        logger.info(f"Branch summary saved to {filename}") # Use main logger
    except Exception as e:
        logger.error(f"Failed to save branch summary: {e}") # Use main logger
    # --- END SAVING LOGIC ---
    
    return {
        "branches": updated_branches,
        "all_sources": [formatted_sources]
    }

# 5. Final Synthesis Node
def synthesize_final_report(state: DToRState, config: RunnableConfig):
    """
    Takes all branch-level synthesis reports as input.
    Integrates insights across all branches.
    Resolves contradictions between branches.
    Produces comprehensive tree-level final report.
    """
    configurable = Configuration.from_runnable_config(config)
    
    # Log the input state
    finalize_logger.info(f"===== SYNTHESIZING FINAL REPORT - INPUT STATE =====")
    finalize_logger.info(f"Research topic: {state.research_topic}")
    finalize_logger.info(f"Mode: {state.mode}")
    finalize_logger.info(f"Number of branches: {len(state.branches)}")
    finalize_logger.info(f"Is complete: {state.is_complete}")
    
    # Skip if not in DToR mode
    if state.mode != "dtor":
        finalize_logger.info("Skipping synthesize_final_report: Not in DToR mode")
        return {}
    
    # Check if all branches are complete and have summaries
    all_complete = all(
        branch.is_complete and branch.branch_summary 
        for branch in state.branches.values()
    )
    
    if not all_complete:
        finalize_logger.info("Skipping synthesize_final_report: Not all branches are complete or have summaries")
        return {}
    
    # Collect all branch summaries
    branch_summaries = {
        branch.perspective: branch.branch_summary
        for branch in state.branches.values()
    }
    
    # Log branch summaries
    finalize_logger.info(f"Branch summaries:")
    for perspective, summary in branch_summaries.items():
        finalize_logger.info(f"  {perspective}: {len(summary)} chars")
    
    branch_summaries_text = "\n\n---\n\n".join([f"== {perspective} ==\n{summary}" for perspective, summary in branch_summaries.items()])
    
    # Format the final synthesis prompt
    synthesis_prompt = f"""
    You are a master research synthesizer, renowned for creating detailed and insightful reports. 
    Your primary goal is to produce a comprehensive, coherent, and well-structured final research report by integrating findings across multiple perspectives provided in the user message.
    """
    
    human_message_content = f"""
    Research Topic: {state.research_topic}
    
    Branch Summaries:
    {branch_summaries_text}
    
    Task: Create a detailed, final integrated research report based on the topic and branch summaries above. Adhere strictly to the following structure and requirements:
    
    1.  **Introduction:** Clearly introduce the research topic ({state.research_topic}). Briefly outline the different perspectives or branches explored (summaries provided above) and the overall scope of the report.
    2.  **Synthesized Findings:** Thoroughly synthesize the key findings, arguments, and evidence presented across all research branches. Identify common themes and points of convergence. Provide sufficient detail from the summaries to support your synthesis.
    3.  **Contradiction Analysis & Resolution:** Explicitly identify and discuss any significant contradictions or discrepancies found between the different perspectives. Attempt to resolve these contradictions or explain why they persist, drawing on the information provided.
    4.  **Unique Perspective Insights:** Dedicate a section to highlighting the unique insights, specific nuances, or distinct contributions offered by each individual research branch/perspective. Elaborate on what makes each perspective valuable.
    5.  **Comprehensive Conclusion:** Provide a robust conclusion that summarizes the main synthesized findings and addresses the original research topic ({state.research_topic}) in depth. Reflect on the overall understanding gained through the multi-perspective approach.
    6.  **Candidate Inventory:**  Present a de-duplicated list drawn from all branch rosters.  Format as a single paragraph of comma-separated names or a short table—your choice.  Include at least the top ten if more are available.

    Report Requirements:
    *   Structure your report logically with clear sections and informative headings.
    *   Maintain a formal and objective tone.
    *   Ensure the report flows smoothly and coherently.
    *   If available, include well-formatted tables e.g.:
    | Category | Representative Material/Methodology | Performance Highlights | Key Advantage | Main Limitation |
    *   Populate at least **five rows** in any table you include, and fill the Performance Highlights column with concrete numbers where available (write n/a if none reported).
    *   The final report should be substantial and reflect a deep integration of the provided summaries. Strive for completeness and thoroughness in your explanations and analysis. Aim for 1200-2000 words** at least.

    *   Always provide a complete report, even if reasoning through complex information.
    
    """
    
    # Generate final synthesis
    finalize_logger.info("Generating final synthesis...")
    result = invoke_with_failover(
        configurable,
        [
            SystemMessage(content=synthesis_prompt),
            HumanMessage(content=human_message_content),
        ],
        temperature=0,
    )
    
    final_summary = result.content
    if configurable.strip_thinking_tokens:
        final_summary = strip_thinking_tokens(final_summary)
    
    finalize_logger.info(f"Final summary generated: {len(final_summary)} chars")
    
    # --- ADD SAVING LOGIC ---
    try:
        # Define base directory and create subfolder based on initial topic
        base_dir = "synthesis_branches_and_final"
        
        # Helper function to sanitize text for directory/file names
        def sanitize_for_path(text, num_words=5, max_len=50):
            words = text.split()[:num_words]
            sanitized = "_".join(words)
            sanitized = re.sub(r'[^\w\\-]+', '_', sanitized) # Keep alphanumeric, underscore, hyphen
            sanitized = re.sub(r'_+', '_', sanitized) # Replace multiple underscores
            sanitized = sanitized.strip('_')
            return sanitized[:max_len]

        # Get the initial topic from the state
        initial_topic = state.research_topic
        subfolder_name = sanitize_for_path(initial_topic)
        
        save_dir = os.path.join(base_dir, subfolder_name)
        os.makedirs(save_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize topic for filename (replace spaces, limit length)
        safe_topic = sanitize_for_path(state.research_topic) # Reuse helper
        filename = os.path.join(save_dir, f"final_report_{safe_topic}_{timestamp}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Final Research Report: {state.research_topic}\\n\\n")
            f.write(final_summary)
        finalize_logger.info(f"Final report saved to {filename}")
    except Exception as e:
        finalize_logger.error(f"Failed to save final report: {e}")
    # --- END SAVING LOGIC ---
    
    finalize_logger.info("===== FINAL SYNTHESIS COMPLETE =====")
    
    return {
        "final_summary": final_summary,
        "is_complete": True
    }

# 6. Branch Monitor & Tree Controller
def route_next_action(state: DToRState, config: RunnableConfig) -> Literal["diversify_query", "analyze_research", "generate_queries", "synthesize_branch", "synthesize_final", END]:
    """
    Determines the next action in the Deep Tree of Research flow based on current state.
    Controls overall tree growth and branch progression.
    """
    # Debug the current state
    routing_logger.info(f"\n===== ROUTING NEXT ACTION =====")
    routing_logger.info(f"Mode: {state.mode}")
    routing_logger.info(f"Active branch: {state.active_branch_id}")
    routing_logger.info(f"Complete: {state.is_complete}")
    routing_logger.info(f"Number of branches: {len(state.branches)}")

    # Check for knowledge gaps in state
    has_knowledge_gaps = hasattr(state, 'knowledge_gaps') and state.knowledge_gaps
    if has_knowledge_gaps:
        routing_logger.info(f"Knowledge gaps detected: {len(state.knowledge_gaps)}")
        # Log first few knowledge gaps
        for i, gap in enumerate(state.knowledge_gaps[:2]):
            routing_logger.info(f"  Gap {i+1}: {gap.get('topic', 'No topic')}")
        routing_logger.info(f"DEBUG: In routing - knowledge_gaps type: {type(state.knowledge_gaps)}")
    else:
        routing_logger.info("No knowledge gaps in current state")
        routing_logger.info(f"DEBUG: In routing - has knowledge_gaps attr: {hasattr(state, 'knowledge_gaps')}")
        if hasattr(state, 'knowledge_gaps'):
            routing_logger.info(f"DEBUG: In routing - knowledge_gaps value: {state.knowledge_gaps}")
            routing_logger.info(f"DEBUG: In routing - knowledge_gaps type: {type(state.knowledge_gaps)}")
    
    # If not in DToR mode, end immediately (single mode is handled by the other graph)
    if state.mode != "dtor":
        routing_logger.info("Not in DToR mode, ending processing")
        return END

    # If research is complete, end
    if state.is_complete:
        routing_logger.info("Research is marked complete, ending processing")
        return END

    # If no branches yet, start with diversification
    if not state.branches:
        routing_logger.info("No branches exist, starting with diversification")
        return "diversify_query"

    # --- Revised Routing Logic --- 

    # First, check if the *currently active* branch has immediate work
    if state.active_branch_id and state.active_branch_id in state.branches:
        active_branch = state.branches[state.active_branch_id]
        if not active_branch.is_complete:
            # Check for knowledge gaps to generate queries
            if has_knowledge_gaps and active_branch.remaining_budget > 0:
                routing_logger.info(f"Active branch {active_branch.perspective} has knowledge gaps. Routing to generate queries.")
                return "generate_queries"
            # Check for pending nodes to research
            pending_nodes = [node for node in active_branch.research_nodes if hasattr(node, 'processing_status') and node.processing_status == "pending"]
            if pending_nodes:
                routing_logger.info(f"Active branch {active_branch.perspective} has pending nodes. Routing to research node.")
                return "research_node"
            # Check for completed nodes to analyze
            completed_nodes = [node for node in active_branch.research_nodes if hasattr(node, 'processing_status') and node.processing_status == "completed"]
            if completed_nodes and active_branch.remaining_budget > 0:
                routing_logger.info(f"Active branch {active_branch.perspective} has completed nodes needing analysis. Routing to analyze research.")
                return "analyze_research"
        # If active branch is complete but needs synthesis
        elif active_branch.is_complete and not active_branch.branch_summary:
             routing_logger.info(f"Active branch {active_branch.perspective} is complete but needs synthesis. Routing to synthesize branch.")
             return "synthesize_branch"

    # If active branch has no immediate work or is complete, find the next actionable branch
    routing_logger.info("Active branch has no immediate work or is complete. Searching other branches...")
    next_actionable_branch_id = None
    action_for_next_branch = None

    for branch_id, branch in state.branches.items():
        if not branch.is_complete:
            # Check for pending nodes first
            pending_nodes = [node for node in branch.research_nodes if hasattr(node, 'processing_status') and node.processing_status == "pending"]
            if pending_nodes:
                routing_logger.info(f"Found pending nodes in branch {branch.perspective}. Selecting this branch.")
                next_actionable_branch_id = branch_id
                action_for_next_branch = "research_node"
                break # Prioritize pending research

            # Check for completed nodes needing analysis
            completed_nodes = [node for node in branch.research_nodes if hasattr(node, 'processing_status') and node.processing_status == "completed"]
            if completed_nodes and branch.remaining_budget > 0:
                 routing_logger.info(f"Found completed nodes in branch {branch.perspective} needing analysis. Selecting this branch.")
                 next_actionable_branch_id = branch_id
                 action_for_next_branch = "analyze_research"
                 # Continue searching in case another branch has pending nodes (higher priority)

    # If we found an actionable branch, set it active and return the action
    if next_actionable_branch_id and action_for_next_branch:
        state.active_branch_id = next_actionable_branch_id
        routing_logger.info(f"Routing to '{action_for_next_branch}' for branch {state.branches[next_actionable_branch_id].perspective}")
        return action_for_next_branch

    # If no actionable work found in any incomplete branch, check for synthesis needs
    routing_logger.info("No actionable research/analysis found in any incomplete branch. Checking synthesis needs...")
    needs_branch_synthesis = []
    all_branches_effectively_complete = True
    for branch_id, branch in state.branches.items():
        if not branch.is_complete:
            # If it's marked incomplete but has no summary, it needs synthesis
            if not branch.branch_summary:
                 needs_branch_synthesis.append(branch_id)
                 all_branches_effectively_complete = False
            else:
                 # Has summary but marked incomplete? Log warning and consider it complete.
                 routing_logger.warning(f"Branch {branch.perspective} marked incomplete but has a summary. Treating as complete for routing.")
                 # Optionally mark it complete in state if desired: state.branches[branch_id].is_complete = True
        elif branch.is_complete and not branch.branch_summary:
             # Marked complete but missing summary - needs synthesis
             needs_branch_synthesis.append(branch_id)
             all_branches_effectively_complete = False

    # If any branch needs synthesis, do that first
    if needs_branch_synthesis:
        target_branch_id = needs_branch_synthesis[0]
        routing_logger.info(f"Found branches needing synthesis: {needs_branch_synthesis}. Routing to synthesize branch {state.branches[target_branch_id].perspective}.")
        state.active_branch_id = target_branch_id
        return "synthesize_branch"

    # If all branches are effectively complete and we haven't made the final summary
    if all_branches_effectively_complete and not state.final_summary:
        routing_logger.info("All branches appear complete. Moving to final synthesis.")
        return "synthesize_final"

    # Safety fallback: If we reach here, something is unexpected. End the process.
    routing_logger.error("Routing reached an unexpected state with no clear next action. Ending run.")
    return END
    # --- End Revised Routing Logic ---

# Function to select the next branch
def select_next_branch(state: DToRState, config: RunnableConfig):
    """Selects the next active branch to work on."""
    # Skip if not in DToR mode
    if state.mode != "dtor":
        return {}

    routing_logger.info(f"\n===== SELECTING NEXT BRANCH =====")
    routing_logger.info(f"Current active branch: {state.active_branch_id}")

    # DIVERSIFY_ONLY mode: Stop immediately after diversification
    if os.environ.get('DIVERSIFY_ONLY', 'false').lower() == 'true':
        routing_logger.info("DIVERSIFY_ONLY mode: Stopping after diversification")
        routing_logger.info(f"Created {len(state.branches)} branches/perspectives")
        for branch_id, branch in state.branches.items():
            routing_logger.info(f"  - {branch_id}: {branch.perspective}")
        return {"active_branch_id": None, "is_complete": True}

    # TARGET_BRANCH_ID mode: Select a specific branch
    target_branch_id = os.environ.get('TARGET_BRANCH_ID')
    if target_branch_id:
        routing_logger.info(f"TARGET_BRANCH_ID mode: Targeting branch {target_branch_id}")
        if target_branch_id in state.branches:
            branch = state.branches[target_branch_id]
            if not branch.is_complete:
                routing_logger.info(f"Selecting target branch: {target_branch_id} - {branch.perspective}")
                return {"active_branch_id": target_branch_id}
            else:
                routing_logger.info(f"Target branch {target_branch_id} is already complete")
                # Branch is complete, check if we should stop
                if os.environ.get('ONE_BRANCH_PER_JOB', 'false').lower() == 'true':
                    routing_logger.info("ONE_BRANCH_PER_JOB mode: Target branch completed, stopping")
                    return {"active_branch_id": None, "is_complete": True}
        else:
            routing_logger.warning(f"Target branch {target_branch_id} not found in branches: {list(state.branches.keys())}")

    # ONE_BRANCH_PER_JOB mode: Stop after completing one branch
    # Check explicit env var OR (SLURM environment AND not DIVERSIFY_ONLY)
    one_branch_mode = (
        os.environ.get('ONE_BRANCH_PER_JOB', 'false').lower() == 'true' or
        (os.environ.get('SLURM_JOB_ID') and
         os.environ.get('DIVERSIFY_ONLY', 'false').lower() != 'true')
    )

    if one_branch_mode:
        # Check if we have any completed branches
        completed_branches = [b for b in state.branches.values() if b.is_complete]
        if completed_branches:
            # We have at least one completed branch, stop here
            routing_logger.info(f"ONE_BRANCH_PER_JOB mode: {len(completed_branches)} branch(es) completed")
            routing_logger.info(f"Completed branches: {', '.join([b.perspective for b in completed_branches])}")
            routing_logger.info("Ending job after branch completion")
            # Return None to signal completion
            return {"active_branch_id": None, "is_complete": True}

    # If current branch is still active and not complete, keep it
    if (state.active_branch_id and
        state.active_branch_id in state.branches and
        not state.branches[state.active_branch_id].is_complete):
        routing_logger.info(f"Keeping current active branch: {state.branches[state.active_branch_id].perspective}")
        return {}

    # Find the first incomplete branch
    next_branch_id = None
    for branch_id, branch in state.branches.items():
        if not branch.is_complete:
            next_branch_id = branch_id
            routing_logger.info(f"Selected next branch: {branch_id} - {branch.perspective}")
            break

    if next_branch_id:
        routing_logger.info(f"Moving to next branch: {state.branches[next_branch_id].perspective}")
    else:
        routing_logger.info("No more incomplete branches found")

    return {"active_branch_id": next_branch_id} 
