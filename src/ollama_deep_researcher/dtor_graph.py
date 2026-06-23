from typing import Optional

from typing_extensions import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

from ollama_deep_researcher.configuration import Configuration
from ollama_deep_researcher.dtor_state import DToRState, DToRStateInput, DToRStateOutput
from ollama_deep_researcher.dtor_nodes import (
    diversify_initial_query,
    analyze_research_report,
    generate_follow_up_queries,
    synthesize_branch,
    synthesize_final_report,
    route_next_action,
    select_next_branch,
    setup_logging
)
from ollama_deep_researcher.graph import graph as single_research_graph, default_config_long_recursion

def research_node(state: DToRState, config: RunnableConfig) -> DToRState:
    """
    Executes regular research on the current active node in the branch.
    This runs the original single path graph on the current research node.
    """
    # Skip if not in DToR mode
    if state.mode != "dtor":
        return state
    
    # Get the active branch and the research node to process
    if not state.active_branch_id or state.active_branch_id not in state.branches:
        return state
    
    branch = state.branches[state.active_branch_id]
    
    # Find the next pending research node to process
    research_node = None
    research_idx = -1
    
    for idx, node in enumerate(branch.research_nodes):
        if hasattr(node, 'processing_status') and node.processing_status == "pending":
            research_node = node
            research_idx = idx
            break
    
    # If no pending node was found, return
    if research_node is None or research_idx == -1:
        return state
    
    # Mark node as in progress
    research_node.processing_status = "in_progress"
    updated_branches = state.branches.copy()
    branch_update = updated_branches[state.active_branch_id]
    branch_update.research_nodes[research_idx] = research_node
    updated_branches[state.active_branch_id] = branch_update
    
    # Create intermediate state to reflect the update
    intermediate_state = DToRState(
        research_topic=state.research_topic,
        mode=state.mode,
        branches=updated_branches,
        active_branch_id=state.active_branch_id,
        max_branch_depth=state.max_branch_depth,
        max_branches=state.max_branches,
        nodes_per_branch=state.nodes_per_branch,
        final_summary=state.final_summary,
        is_complete=state.is_complete,
        all_sources=state.all_sources
    )
    
    # Run the original research graph on this node
    research_result = single_research_graph.invoke(
        {"research_topic": research_node.research_topic},
        config=config
    )
    
    # Update the research node with the results
    updated_node = research_node
    
    # Check if research_result is a dict-like object and extract running_summary
    if hasattr(research_result, "get"):
        updated_node.running_summary = research_result.get("running_summary")
    elif hasattr(research_result, "running_summary"):
        updated_node.running_summary = research_result.running_summary
    else:
        # Default to the research_result itself if it's a string or use a default message
        updated_node.running_summary = str(research_result) if not isinstance(research_result, dict) else "Research complete, but no summary available."
    
    # Get sources from the research result if available
    configurable = Configuration.from_runnable_config(config)
    if getattr(configurable, 'research_mode', 'single') != 'dtor':
        # Only assign sources if NOT in DToR mode
        if hasattr(research_result, 'sources_gathered'):
            updated_node.sources_gathered = research_result.sources_gathered
        elif hasattr(research_result, "get") and "sources_gathered" in research_result:
            updated_node.sources_gathered = research_result.get("sources_gathered")
    
        if hasattr(research_result, 'complementary_sources_gathered'):
            updated_node.complementary_sources_gathered = research_result.complementary_sources_gathered
        elif hasattr(research_result, "get") and "complementary_sources_gathered" in research_result:
            updated_node.complementary_sources_gathered = research_result.get("complementary_sources_gathered")
    
        if hasattr(research_result, 'local_sources_gathered'):
            updated_node.local_sources_gathered = research_result.local_sources_gathered
        elif hasattr(research_result, "get") and "local_sources_gathered" in research_result:
            updated_node.local_sources_gathered = research_result.get("local_sources_gathered")
    else:
        # In DToR mode, ensure these lists are empty on the node state to prevent accumulation
        updated_node.sources_gathered = []
        updated_node.complementary_sources_gathered = []
        updated_node.local_sources_gathered = []
    
    # Update processing status to completed
    updated_node.processing_status = "completed"
    
    # Update the branch with the processed research node
    updated_branches = state.branches.copy()
    branch_update = updated_branches[state.active_branch_id]
    branch_update.research_nodes[research_idx] = updated_node
    updated_branches[state.active_branch_id] = branch_update
    
    # Return updated state
    return DToRState(
        research_topic=state.research_topic,
        mode=state.mode,
        branches=updated_branches,
        active_branch_id=state.active_branch_id,
        max_branch_depth=state.max_branch_depth,
        max_branches=state.max_branches,
        nodes_per_branch=state.nodes_per_branch,
        final_summary=state.final_summary,
        is_complete=state.is_complete,
        all_sources=state.all_sources
    )

def init_session(state: DToRStateInput, config: RunnableConfig = None) -> DToRStateInput:
    """Initialize a new research session, including creating fresh log files."""
    # Set up fresh logging for this session
    timestamp = setup_logging()
    
    # Return the input state unchanged
    return state

def process_mode_selection(state: DToRStateInput, config: RunnableConfig = None) -> Literal["single_path", "dtor_mode"]:
    """Routes to the appropriate research mode based on user selection."""
    import logging
    logging.info(f"DEBUG process_mode_selection: state type={type(state)}, state={state}")

    # Check both state and config for the mode
    configurable = Configuration.from_runnable_config(config)
    config_mode = getattr(configurable, 'research_mode', 'single')

    # Use either the explicit state mode or the config mode
    # state is a TypedDict (dict), so use .get() instead of attribute access
    effective_mode = state.get('mode') if state.get('mode') else config_mode

    logging.info(f"DEBUG effective_mode={effective_mode}, config_mode={config_mode}")

    # Route to the appropriate path
    return "dtor_mode" if effective_mode == "dtor" else "single_path"

def single_path_research(state: DToRStateInput, config: RunnableConfig = None) -> DToRStateOutput:
    """Wrapper for the original single-path research agent."""
    # Run the original research graph
    # state is a TypedDict (dict), so use .get() instead of attribute access
    result = single_research_graph.invoke(
        {"research_topic": state.get('research_topic', '')},
        config=config
    )
    
    # Convert to DToR output format
    return DToRStateOutput(
        final_summary=result.get('running_summary', ''),
        all_sources=[]  # Sources are included in the summary
    )

# Build the Deep Tree of Research graph
def build_dtor_graph(checkpointer: Optional[object] = None):
    # Create the builder
    builder = StateGraph(DToRState, input=DToRStateInput, output=DToRStateOutput, config_schema=Configuration)
    
    # Define the mapping for router outcomes
    ROUTE_MAPPING = {
        "diversify_query": "diversify_query", # Should not happen, defensive
        "analyze_research": "analyze_research",
        "generate_queries": "generate_queries",
        "research_node": "research_node",
        "synthesize_branch": "synthesize_branch",
        "synthesize_final": "synthesize_final",
        END: END
    }
    
    # Add nodes
    builder.add_node("diversify_query", diversify_initial_query)
    builder.add_node("analyze_research", analyze_research_report)
    builder.add_node("generate_queries", generate_follow_up_queries)
    builder.add_node("research_node", research_node)
    builder.add_node("select_next_branch", select_next_branch)
    builder.add_node("synthesize_branch", synthesize_branch)
    builder.add_node("synthesize_final", synthesize_final_report)
    
    # Add the initial edge from START to diversify_query
    builder.add_edge(START, "diversify_query")
    
    # Add edges for the DToR workflow
    builder.add_conditional_edges(
        "research_node",
        route_next_action,
        ROUTE_MAPPING # Use the defined mapping
    )
    
    builder.add_edge("diversify_query", "select_next_branch")
    
    # *** REMOVE static edge ***
    # builder.add_edge("select_next_branch", "research_node")
    # *** ADD conditional edge ***
    builder.add_conditional_edges(
        "select_next_branch",
        route_next_action,
        ROUTE_MAPPING # Use the defined mapping
    )
    
    # *** REMOVE static edge ***
    # builder.add_edge("analyze_research", "generate_queries")
    # *** ADD conditional edge ***
    builder.add_conditional_edges(
        "analyze_research",
        route_next_action,
        ROUTE_MAPPING # Use the defined mapping
    )
    
    builder.add_edge("generate_queries", "research_node") # After generating queries, we need to research them
    builder.add_edge("synthesize_branch", "select_next_branch") # After synthesizing, select the next branch
    
    builder.add_edge("synthesize_final", END)
    
    # Compile the main graph
    main_graph = builder.compile(checkpointer=checkpointer)
    
    # Add step timeout to prevent CancelledError
    main_graph.step_timeout = 86400  # 24 hours in seconds
    
    return main_graph

# Create the main entry graph that routes between single-path and DToR modes
def create_main_graph(checkpointer: Optional[object] = None):
    builder = StateGraph(DToRStateInput, output=DToRStateOutput, config_schema=Configuration)
    
    # Add init_session node to set up logging at the start of each run
    builder.add_node("init_session", init_session)
    
    # Add nodes for different research modes
    builder.add_node("single_path", single_path_research)
    builder.add_node("dtor_mode", build_dtor_graph(checkpointer=checkpointer))
    
    # Add the initial edge from START to init_session
    builder.add_edge(START, "init_session")
    
    # Add conditional routing based on mode selection
    builder.add_conditional_edges(
        "init_session",
        process_mode_selection
    )
    
    # Both modes lead to the end
    builder.add_edge("single_path", END)
    builder.add_edge("dtor_mode", END)
    
    # Compile the main graph
    main_graph = builder.compile(checkpointer=checkpointer)
    
    # Add step timeout to prevent CancelledError
    main_graph.step_timeout = 86400  # 24 hours in seconds
    
    return main_graph

# Export the main graph
graph = create_main_graph()
# Add step timeout to prevent CancelledError
graph.step_timeout = 86400  # 24 hours in seconds 
