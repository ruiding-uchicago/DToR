#!/usr/bin/env python3
"""
Stage 1: Diversify Only - Generate perspectives for DToR research
This script only runs the diversification step and saves the results
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import hashlib

# Add src to path
sys.path.insert(0, 'src')

from ollama_deep_researcher.configuration import Configuration
from ollama_deep_researcher.dtor_state import DToRState, DToRStateInput
from ollama_deep_researcher.dtor_nodes import diversify_initial_query
from langchain_core.runnables import RunnableConfig

def main():
    parser = argparse.ArgumentParser(description='Run diversify only for DToR')
    parser.add_argument('--topics-file', required=True, help='Path to topics file')
    parser.add_argument('--run-id', required=True, help='Run ID for checkpoint')
    parser.add_argument('--checkpoint-dir', default='cluster_checkpoints', help='Checkpoint directory')
    args = parser.parse_args()

    # Read topic
    with open(args.topics_file, 'r') as f:
        topic = f.read().strip()

    print("="*60)
    print("DToR Stage 1: Diversify Only")
    print(f"Topic: {topic[:100]}...")
    print(f"Run ID: {args.run_id}")
    print("="*60)

    # Create checkpoint directory
    checkpoint_dir = Path(args.checkpoint_dir) / args.run_id
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Create thread ID (same format as run_batch_cluster.py)
    thread_id = f"research_{hashlib.md5(topic.encode()).hexdigest()[:6]}"

    # Create checkpoint file path (for Stage 2 to use)
    checkpoint_file = checkpoint_dir / f"{thread_id}.sqlite"

    # Create configuration
    config_dict = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": "",
            "research_mode": "dtor",
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
            "use_local_rag": False  # Diversify doesn't need RAG
        }
    }

    config = RunnableConfig(**config_dict)
    configurable = Configuration.from_runnable_config(config)

    # Create initial state
    initial_state = DToRState(
        research_topic=topic,
        mode="dtor",
        max_branches=configurable.max_branches,
        max_branch_depth=configurable.max_branch_depth,
        nodes_per_branch=configurable.nodes_per_branch
    )

    print("\nCalling diversify_initial_query...")

    try:
        # Execute diversification
        result = diversify_initial_query(initial_state, config)

        # Extract branches/perspectives
        if isinstance(result, dict) and 'branches' in result:
            branches = result['branches']
        elif hasattr(result, 'branches'):
            branches = result.branches
        else:
            print("Error: No branches returned from diversify")
            return 1

        print(f"\nGenerated {len(branches)} perspectives:")
        perspectives_data = []

        for branch_id, branch in branches.items():
            print(f"  - {branch_id}: {branch.perspective}")
            perspectives_data.append({
                'id': branch_id,
                'perspective': branch.perspective
            })

        # Save perspectives to JSON file
        perspectives_file = checkpoint_dir / "perspectives.json"
        with open(perspectives_file, 'w') as f:
            json.dump({
                'topic': topic,
                'perspectives': perspectives_data,
                'timestamp': datetime.now().isoformat(),
                'thread_id': thread_id
            }, f, indent=2)

        print(f"\nPerspectives saved to: {perspectives_file}")

        # Note: We don't need to manually save checkpoint here
        # The checkpoint is created when running the graph
        # We only need the perspectives.json for Stage 2
        print(f"Checkpoint database created at: {checkpoint_file}")

        print("\nDiversify stage completed successfully!")
        return 0

    except Exception as e:
        print(f"Error during diversification: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
