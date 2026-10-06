#!/usr/bin/env python3
"""
Final synthesis for ToT research - combines all branch reports
"""

import os
import sys
import json
import argparse
import glob
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from ollama_deep_researcher.tot_nodes import synthesize_final_report
from ollama_deep_researcher.tot_state import ToTState, ResearchBranch
from ollama_deep_researcher.state import SummaryState
from ollama_deep_researcher.configuration import Configuration
from langchain_core.runnables import RunnableConfig

def read_branch_report(file_path):
    """Read and parse a branch synthesis report"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Extract branch ID from filename
    filename = os.path.basename(file_path)
    # Pattern: branch_<id>_<perspective>_<timestamp>.md
    branch_id = filename.split('_')[1]

    # Extract perspective from content (first line after # Branch Synthesis:)
    perspective = "Unknown"
    for line in content.split('\n'):
        if line.startswith('# Branch Synthesis:'):
            perspective = line.replace('# Branch Synthesis:', '').strip()
            break

    return {
        'branch_id': branch_id,
        'perspective': perspective,
        'summary': content
    }

def create_mock_state(branch_reports, topic, config_dict):
    """Create a ToTState object with branch summaries for final synthesis"""

    branches = {}
    for report in branch_reports:
        # Create a minimal research node for each branch
        research_node = SummaryState(
            research_topic=f"{topic}: (Focus: {report['perspective']})",
            running_summary=report['summary']
        )

        branch = ResearchBranch(
            branch_id=report['branch_id'],
            perspective=report['perspective'],
            branch_summary=report['summary'],
            is_complete=True,
            depth=1,
            research_nodes=[research_node]  # Include at least one research node
        )
        branches[report['branch_id']] = branch

    # Create state with all ToT parameters
    state = ToTState(
        research_topic=topic,
        mode="tot",
        branches=branches,
        is_complete=False,
        max_branches=config_dict['configurable'].get('max_branches', 3),
        max_branch_depth=config_dict['configurable'].get('max_branch_depth', 1),
        nodes_per_branch=config_dict['configurable'].get('nodes_per_branch', 1)
    )

    return state

def main():
    parser = argparse.ArgumentParser(description='Generate final ToT synthesis')
    parser.add_argument('--topic-file', required=True, help='Topic file')
    parser.add_argument('--run-id', required=True, help='Run ID')
    parser.add_argument('--synthesis-dir', required=True, help='Synthesis directory')
    args = parser.parse_args()

    # Read the topic
    with open(args.topic_file, 'r') as f:
        topic = f.read().strip()

    print(f"Generating final synthesis for: {topic[:100]}...")
    print(f"Synthesis directory: {args.synthesis_dir}/{args.run_id}")

    # Find all branch reports (check both possible locations)
    branch_files = glob.glob(f"{args.synthesis_dir}/{args.run_id}/branch_*.md")

    # Also check actual output directory (Stage 2 creates with full path but truncates to 50 chars)
    actual_output_dir = args.topic_file.replace('.txt', '').replace('/', '_')[:50]
    actual_dir_files = glob.glob(f"{args.synthesis_dir}/{actual_output_dir}/branch_*.md")

    # Also check with _txt suffix for edge cases
    actual_output_dir_txt = (args.topic_file.replace('.txt', '').replace('/', '_') + '_txt')[:50]
    actual_dir_txt_files = glob.glob(f"{args.synthesis_dir}/{actual_output_dir_txt}/branch_*.md")

    # Combine and deduplicate
    branch_files = list(set(branch_files + actual_dir_files + actual_dir_txt_files))
    print(f"Found {len(branch_files)} branch reports")

    if not branch_files:
        print("Error: No branch reports found")
        sys.exit(1)

    # Read all branch reports
    branch_reports = []
    for bf in sorted(branch_files):
        print(f"Reading: {os.path.basename(bf)}")
        report = read_branch_report(bf)
        branch_reports.append(report)

    # Create configuration
    config_dict = {
        "configurable": {
            "research_mode": "tot",
            "ollama_base_url": os.environ.get("OLLAMA_HOST", "http://localhost:21485"),
            "local_llm": os.environ.get("LOCAL_LLM"),  # Read from env
            "temperature": 0,
            "max_search_results": 20,
            "total_research_iterations": 40,
            "max_iterations_per_search_engine": 10,
            "nodes_per_branch": 100,
            "max_branches": 3,
            "max_branch_depth": 3,
            "strip_thinking_tokens": True,
            "use_local_rag": False  # Synthesis doesn't need RAG
        }
    }

    # Create mock state with branches
    state = create_mock_state(branch_reports, topic, config_dict)

    config = RunnableConfig(**config_dict)

    print("\nCalling synthesize_final...")

    try:
        # Call the synthesis function
        result = synthesize_final_report(state, config)

        # Extract the final synthesis
        if isinstance(result, dict) and 'final_summary' in result:
            final_synthesis = result['final_summary']
        elif hasattr(result, 'final_summary'):
            final_synthesis = result.final_summary
        else:
            # If result is a string representation of dict, try to parse it
            result_str = str(result)
            if result_str.startswith("{'final_summary':"):
                import ast
                try:
                    parsed = ast.literal_eval(result_str)
                    final_synthesis = parsed['final_summary']
                except:
                    final_synthesis = result_str
            else:
                final_synthesis = result_str

        # Write the final synthesis (use actual output directory to match Stage 2)
        actual_output_dir = args.topic_file.replace('.txt', '').replace('/', '_')[:50]
        output_dir = f"{args.synthesis_dir}/{actual_output_dir}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/final_synthesis.md"
        with open(output_file, 'w') as f:
            f.write(f"# Final ToT Synthesis Report\n\n")
            f.write(f"**Research Topic:** {topic}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Number of Branches:** {len(branch_reports)}\n\n")
            f.write("---\n\n")
            f.write(final_synthesis)

        print(f"\nFinal synthesis written to: {output_file}")
        print(f"Length: {len(final_synthesis)} characters")

    except Exception as e:
        print(f"Error generating synthesis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()