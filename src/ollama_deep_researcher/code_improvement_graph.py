import json
import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional

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

from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import Field

from ollama_deep_researcher.configuration import Configuration # Use existing config for LLM
from ollama_deep_researcher.state import CodeImprovementState, CodeImprovementInput, CodeImprovementOutput
from ollama_deep_researcher.utils import strip_thinking_tokens
from ollama_deep_researcher.prompts import (
    analyze_code_and_plan_research_instructions,
    generate_revision_plan_instructions,
    implement_code_revision_instructions,
)
from ollama_deep_researcher.graph import graph as single_research_graph # Import the existing research graph
from ollama_deep_researcher.dtor_nodes import setup_logging, invoke_with_failover  # Import helpers from DToR nodes

# --- Logger Setup ---
logger = logging.getLogger(__name__)
# Configure logging (can be done once globally, but doing it here ensures it's set)
# setup_logging() # Assuming setup_logging is called elsewhere or configure here if needed

# --- Helper Functions ---

def save_output_files(state: CodeImprovementState):
    """Saves the revision plan and revised code to files."""
    try:
        output_dir = "code_improvement_output"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean base filename from description or request
        base_name_src = state.problem_description or state.human_request or "code_revision"
        safe_base_name = re.sub(r'[\/*?"<>|]', "", base_name_src)
        safe_base_name = re.sub(r'\s+', '_', safe_base_name)[:50] # Limit length
        
        # Save Revision Plan
        if state.revision_plan:
            plan_filename = f"{safe_base_name}_{timestamp}_plan.md"
            plan_filepath = os.path.join(output_dir, plan_filename)
            with open(plan_filepath, "w", encoding="utf-8") as f:
                f.write("## Revision Plan\n\n")
                f.write(state.revision_plan)
            logger.info(f"Revision plan saved to: {plan_filepath}")

        # Save Revised Code
        if state.revised_code:
            code_filename = f"{safe_base_name}_{timestamp}_code.py"
            code_filepath = os.path.join(output_dir, code_filename)
            # Extract code from markdown block if necessary
            code_to_save = state.revised_code
            match = re.search(r"```python\n(.*)```", state.revised_code, re.DOTALL | re.IGNORECASE)
            if match:
                code_to_save = match.group(1).strip()
                
            with open(code_filepath, "w", encoding="utf-8") as f:
                f.write(code_to_save)
            logger.info(f"Revised code saved to: {code_filepath}")

    except Exception as e:
        logger.error(f"Error saving output files: {e}")
        # Optionally update state with error
        # return {"error_message": f"Failed to save output files: {e}"}
    return {} # No state update needed here, just performs side effect


# --- Graph Nodes ---

def initialize_workflow(state: CodeImprovementInput) -> Dict:
    """Initializes the state for the code improvement workflow."""
    logger.info("Initializing Code Improvement Workflow...")
    # setup_logging() # Initialize logging if not done globally - Logging now initialized in dtor_nodes.py
    return {
        "problem_description": state.problem_description,
        "current_code": state.current_code,
        "current_performance": state.current_performance,
        "human_request": state.human_request,
        "original_input": state # Keep original input for reference
    }

def analyze_and_plan_research(state: CodeImprovementState, config: RunnableConfig) -> Dict:
    """Node to analyze code context and plan research."""
    logger.info("Analyzing code and planning research...")
    configurable = Configuration.from_runnable_config(config)

    # System message contains the core instructions and format
    system_prompt = analyze_code_and_plan_research_instructions # Instructions without dynamic context
    
    # Human message provides the specific context for this run
    human_prompt = f"""Please analyze the following ML code context and generate a critique and research topic in the specified JSON format.

<INPUT_CONTEXT>
Problem Description: {state.problem_description}
---
Current Code:
```python
{state.current_code}
```
---
Current Performance: {state.current_performance}
---
Human Request: {state.human_request}
</INPUT_CONTEXT>

Provide your analysis and research plan in JSON format:"""

    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ],
            temperature=0,
            json_mode=True,
        )
        content = result.content
        logger.debug(f"Analysis LLM raw response: {content}")
        
        try:
            # Always try to parse as JSON first, regardless of model type
            # gpt-oss models can generate valid JSON even without format="json"
            cleaned_content = clean_code_blocks(content)
            data = json.loads(cleaned_content)
            critique = data.get("critique", "Critique generation failed.")
            research_topic = data.get("research_topic")
            
            # Verify we have valid data
            if not critique or not research_topic:
                raise ValueError("Missing required fields in JSON response")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise Exception(f"JSON parsing failed: {str(e)}")

    except Exception as e:
        logger.info(f"JSON mode failed for analyze_and_plan_research, trying with standard mode...")
        
        # Fallback to standard mode if JSON mode fails
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ],
            temperature=0,
            json_mode=False,
        )
        content = result.content
        
        if configurable.strip_thinking_tokens:
            content = strip_thinking_tokens(content)
        
        # Try to extract JSON from the text response
        try:
            import re
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                json_str = match.group(0)
                cleaned_json = clean_code_blocks(json_str)
                data = json.loads(cleaned_json)
                critique = data.get("critique", "")
                research_topic = data.get("research_topic", "")
                
                # Verify we have valid data
                if critique and research_topic:
                    logger.info("Successfully extracted JSON from text response")
                else:
                    raise ValueError("Invalid data in extracted JSON")
            else:
                raise ValueError("No JSON-like structure found in the response")
                
        except Exception as e:
            logger.warning(f"Failed to extract JSON from text response: {str(e)}")
            # Final fallback
            critique = content.strip()[:500] if content.strip() else "Code analysis completed."
            research_topic = f"how to improve ML code for task: {state.problem_description[:100]}"

    if not research_topic:
        logger.warning("LLM failed to generate a research topic. Using fallback.")
        research_topic = f"how to improve ML code for task: {state.problem_description[:100]}"
        
    logger.info(f"Critique: {critique}")
    logger.info(f"Generated Research Topic: {research_topic}")
    return {"critique": critique, "research_topic": research_topic}


def run_deep_research(state: CodeImprovementState, config: RunnableConfig) -> Dict:
    """Node to invoke the existing deep research graph."""
    logger.info(f"Running deep research for topic: {state.research_topic}")
    
    if not state.research_topic:
        logger.error("Cannot run research, no research topic provided.")
        return {"research_report": "Error: Research topic was not generated.", "error_message": "Missing research topic."}

    # Prepare input for the sub-graph
    research_input = {"research_topic": state.research_topic}
    
    try:
        # Invoke the existing graph
        # We pass the parent graph's config, assuming the sub-graph uses compatible settings (like LLM provider)
        research_output = single_research_graph.invoke(research_input, config=config)
        
        # Extract the final summary from the sub-graph's output state
        report = research_output.get("running_summary", "Research report generation failed.")
        logger.info(f"Deep research completed. Report length: {len(report)} chars")
        return {"research_report": report}
        
    except Exception as e:
        logger.error(f"Error invoking deep research sub-graph: {e}", exc_info=True)
        return {"research_report": f"Error during research: {e}", "error_message": f"Sub-graph invocation failed: {e}"}


def generate_revision_plan(state: CodeImprovementState, config: RunnableConfig) -> Dict:
    """Node to generate the high-level code revision plan."""
    logger.info("Generating revision plan...")
    configurable = Configuration.from_runnable_config(config)
    # Use slightly higher temperature for potentially more creative planning

    # Provide only a snippet of code for context if it's very long
    code_snippet = state.current_code[:2000] + "..." if len(state.current_code) > 2000 else state.current_code

    # System message contains the core instructions and format
    system_prompt = "You are an expert ML engineer. Based on the user's context and research report, create a concise, actionable revision plan in markdown format (under 200 words)." # Simplified System Prompt

    # Human message provides the specific context for this run
    human_prompt = f"""Use the Research Report below ONLY as a knowledge reference to help you generate a code revision plan.

<RESEARCH_REPORT_REFERENCE>
{state.research_report}
</RESEARCH_REPORT_REFERENCE>

---

Now, analyze the following context and create a concise, actionable plan (under 200 words) to improve the `Current Code Snippet` based *only* on the reference report and the context provided.

<ORIGINAL_CONTEXT>
Problem Description: {state.problem_description}
Current Performance: {state.current_performance}
Human Request: {state.human_request}
---
Current Code Snippet:
```python
{code_snippet}
```
</ORIGINAL_CONTEXT>

Output the plan as a numbered list of specific code changes in order to increase the performance of the code (e.g., '1. Replace xx with yy', '2. Add zz'). Start the list directly, 4 points max. Do not include explanations or summaries.
"""

    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ],
            temperature=0.3,
            json_mode=False,
        )
        plan = result.content
        if configurable.strip_thinking_tokens:
           plan = strip_thinking_tokens(plan)
           
        logger.info(f"Revision plan generated: {plan[:500]}...")
        return {"revision_plan": plan}
        
    except Exception as e:
        logger.error(f"Error in generate_revision_plan: {e}")
        return {"revision_plan": f"Error generating revision plan: {e}", "error_message": str(e)}

def implement_code_revision(state: CodeImprovementState, config: RunnableConfig) -> Dict:
    """Node to implement the code changes based on the revision plan."""
    logger.info("Implementing code revisions...")
    configurable = Configuration.from_runnable_config(config)

    if not state.revision_plan:
        logger.error("Cannot implement revisions, no revision plan provided.")
        return {"revised_code": "Error: Revision plan was not generated.", "error_message": "Missing revision plan."}

    # System message contains the core instructions and format
    system_prompt = "You are an expert Python programmer functioning as a code execution engine. Revise the user's code based *only* on the revision plan provided. Output *only* the complete, revised Python code without any other text or explanations." # Simplified System Prompt

    # Human message provides the specific context for this run
    # Simplified Human Prompt: Only provide essential inputs
    human_prompt = f"""Revise the Original Code based *only* on the Revision Plan.
Output *only* the complete, revised Python code.
Your code should not be garanteed to be bug free, the modifications should not introduce new bugs.
***extremely important***: You ***MUST*** output the revised code in full and directly conductable, not any omitted parts is allowed.

--- Revision Plan ---
{state.revision_plan}

--- Original Code ---
```python
{state.current_code}
```

--- Revised Code Output ---
```python
"""

    # --- Debugging: Save LLM Input ---
    try:
        debug_dir = "code_revision_inputs"
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Add microseconds for uniqueness
        debug_filename = f"implement_code_revision_input_{timestamp}.txt"
        debug_filepath = os.path.join(debug_dir, debug_filename)
        
        with open(debug_filepath, "w", encoding="utf-8") as f:
            f.write("--- SYSTEM PROMPT ---\n")
            f.write(system_prompt)
            f.write("\n\n--- HUMAN PROMPT ---\n")
            f.write(human_prompt)
            
        logger.info(f"Saved LLM input for implement_code_revision to: {debug_filepath}")
        
    except Exception as e:
        logger.error(f"Error saving debug LLM input: {e}")
    # --- End Debugging ---

    try:
        result = invoke_with_failover(
            configurable,
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt),
            ],
            temperature=0.3,
            json_mode=False,
        )
        code = result.content
        # Code is often returned in markdown blocks, attempt to clean it
        match = re.search(r"```(?:python)?\n(.*)```", code, re.DOTALL | re.IGNORECASE)
        if match:
            revised_code = match.group(1).strip()
            logger.info("Extracted Python code from markdown block.")
        else:
            # If no markdown block, assume the whole output is code, maybe strip thinking tokens
            revised_code = code
            if configurable.strip_thinking_tokens:
                revised_code = strip_thinking_tokens(revised_code).strip()
            logger.warning("LLM did not return code in a markdown block. Using raw output (with potential thinking token stripping).")

        logger.info(f"Code revision implemented. New code length: {len(revised_code)} chars")
        
        # Perform the file saving as a side effect using RunnableLambda
        # save_output_files(state) # Call saving logic here directly? Or use lambda
        
        return {"revised_code": revised_code}

    except Exception as e:
        logger.error(f"Error in implement_code_revision: {e}")
        return {"revised_code": f"# Error implementing revision: {e}\n{state.current_code}", "error_message": str(e)}

# --- Build Graph ---

# Define the state machine
workflow = StateGraph(
    CodeImprovementState, 
    input=CodeImprovementInput, 
    output=CodeImprovementOutput,
    config_schema=Configuration # Add the configuration schema here
)

# Add nodes
workflow.add_node("initialize_workflow", initialize_workflow)
workflow.add_node("analyze_and_plan_research", analyze_and_plan_research)
workflow.add_node("run_deep_research", run_deep_research)
workflow.add_node("generate_revision_plan", generate_revision_plan)
workflow.add_node("implement_code_revision", implement_code_revision)
# Use RunnableLambda to wrap the side-effect function for saving files
workflow.add_node("save_outputs", RunnableLambda(save_output_files))

# Define edges
workflow.add_edge(START, "initialize_workflow")
workflow.add_edge("initialize_workflow", "analyze_and_plan_research")
workflow.add_edge("analyze_and_plan_research", "run_deep_research")
workflow.add_edge("run_deep_research", "generate_revision_plan")
workflow.add_edge("generate_revision_plan", "implement_code_revision")
workflow.add_edge("implement_code_revision", "save_outputs") # Save after implementation
workflow.add_edge("save_outputs", END)


# Compile the graph
# Add a configuration schema to the graph's input
# This allows the UI to show fields from Configuration alongside CodeImprovementInput
# Note: This schema combines fields. Ensure no naming conflicts or handle them appropriately.
# combined_schema = type(
#     'CombinedInputSchema',
#     (CodeImprovementInput, Configuration),
#     {'__annotations__': {
#         **CodeImprovementInput.__annotations__,
#         **{k: v for k, v in Configuration.__annotations__.items() if k not in CodeImprovementInput.__annotations__}
#     }}
# )

# Compile with the config schema associated directly with the StateGraph definition
code_improvement_graph = workflow.compile(checkpointer=None) # Add checkpointer later if needed

# Explicitly tell LangGraph about the configurable fields for the UI
# code_improvement_graph = code_improvement_graph_base.with_configurable_fields(Configuration) # This was incorrect

# Optional: Define input schema specifically for the compiled graph if needed separately
# code_improvement_graph = code_improvement_graph.with_types(input_type=combined_schema)

logger.info("Code Improvement Graph compiled.") 
