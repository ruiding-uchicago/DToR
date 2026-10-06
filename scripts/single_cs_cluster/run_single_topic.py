#!/usr/bin/env python3
"""
Single Topic Research Runner - Simplified for parallel cluster execution
Runs ONE research topic in single mode (no DToR complexity)
"""

import sys
import argparse
import logging
import os
from pathlib import Path
from datetime import datetime

# Project imports
try:
    from src.ollama_deep_researcher.configuration import Configuration
    from src.ollama_deep_researcher.dtor_nodes import setup_logging
except ImportError as e:
    print(f"ImportError: {e}. Please ensure you run this script from the project root directory.")
    sys.exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_single_topic(topic: str,
                     output_dir: str = "Single_DR_final",
                     topic_name: str = None) -> bool:
    """
    Run research on a single topic (simplified - no checkpointing needed)

    Returns:
        True if successful, False otherwise
    """
    # Configuration - load from environment and FORCE single mode
    config_dict = {}
    for field_name in Configuration.model_fields.keys():
        env_value = os.environ.get(field_name.upper())
        if env_value is not None:
            if env_value.lower() == 'true':
                config_dict[field_name] = True
            elif env_value.lower() == 'false':
                config_dict[field_name] = False
            elif env_value.isdigit():
                config_dict[field_name] = int(env_value)
            else:
                config_dict[field_name] = env_value

    # FORCE single mode
    config_dict['research_mode'] = 'single'
    config_instance = Configuration(**config_dict)

    # Initialize logging
    timestamp = setup_logging()

    logger.info("="*60)
    logger.info("SINGLE TOPIC RESEARCH")
    logger.info(f"Topic: {topic[:80]}...")
    logger.info(f"Mode: single (FORCED)")
    logger.info(f"Max Web Research Loops: {config_instance.max_web_research_loops}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info("="*60)

    # Setup output directory
    output_path = Path(output_dir)
    # Use topic_name if provided (from filename), otherwise use truncated topic
    if topic_name:
        safe_dirname = topic_name
    else:
        safe_dirname = topic.replace(' ', '_').replace('/', '_')[:100]
    topic_dir = output_path / safe_dirname
    topic_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output dir: {topic_dir}")

    # Import single research graph directly
    from src.ollama_deep_researcher.graph import graph as single_research_graph

    # Prepare run configuration
    run_config = {
        "configurable": {
            **config_instance.model_dump(),
        },
        "recursion_limit": 500,
    }

    try:
        logger.info("Starting research...")

        # Simple invoke - no checkpointing needed
        inputs = {"research_topic": topic}
        result = single_research_graph.invoke(inputs, config=run_config)

        logger.info("Research completed!")

        # Extract final report
        final_report = None
        if result:
            # Try dict access
            if hasattr(result, 'get'):
                final_report = result.get('running_summary')
            # Try attribute access
            elif hasattr(result, 'running_summary'):
                final_report = result.running_summary

        if not final_report:
            final_report = str(result) if result else "No report generated"

        # Save report
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = topic_dir / f"report_{timestamp_str}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Research Report: {topic}\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Mode: single\n")
            f.write(f"Max Web Research Loops: {config_instance.max_web_research_loops}\n")
            if config_instance.enable_fet_raw_data:
                f.write(f"FET Sensor Mode: Enabled\n")
            f.write("\n---\n\n")
            f.write(final_report)

        logger.info("="*60)
        logger.info("✓ SUCCESS")
        logger.info(f"Report saved to: {report_path}")
        logger.info("="*60)

        return True

    except Exception as e:
        logger.error("="*60)
        logger.error("✗ FAILED")
        logger.error(f"Error: {e}", exc_info=True)
        logger.error("="*60)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run single-mode research on ONE topic"
    )

    parser.add_argument(
        "topic",
        help="Research topic string or path to topic file"
    )
    parser.add_argument(
        "--output-dir",
        default="Single_DR_final",
        help="Output directory (default: Single_DR_final)"
    )
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Check if topic is a file path
    topic_text = args.topic
    topic_name = None
    if Path(args.topic).exists() and Path(args.topic).is_file():
        logger.info(f"Reading topic from file: {args.topic}")
        with open(args.topic, 'r', encoding='utf-8') as f:
            topic_text = f.read().strip()
        # Use filename (without .txt) as directory name
        topic_name = Path(args.topic).stem

    # Run research
    success = run_single_topic(
        topic=topic_text,
        output_dir=args.output_dir,
        topic_name=topic_name
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
