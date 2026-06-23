#!/usr/bin/env python3
"""
Cluster-Optimized Batch Research Runner with Wall-Time Resilience
Designed for supercomputer environments with hard time limits (e.g., 4 hours)
Features:
- Automatic checkpointing and resumption
- Wall-time aware execution with graceful shutdown
- Skip completed tasks automatically
- Preserve processing order across restarts
- Progress tracking and state management
- Signal handling for SLURM/PBS systems
"""

import sys
import argparse
import logging
import signal
import time
import json
import pickle
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# LangGraph imports - simplified to match run_batch.py
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import pickle

# Project imports
try:
    from src.ollama_deep_researcher.configuration import Configuration, default_config_long_recursion
    from src.ollama_deep_researcher.dtor_state import DToRStateInput, DToRStateOutput
    from src.ollama_deep_researcher.graph import SummaryStateOutput
    from src.ollama_deep_researcher.dtor_nodes import setup_logging
except ImportError as e:
    print(f"ImportError: {e}. Please ensure you run this script from the project root directory.")
    sys.exit(1)

# Load environment variables if .env exists
from dotenv import load_dotenv
load_dotenv(override=True)  # Force reload .env file

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cluster_research.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"

@dataclass
class TaskState:
    """State for a single research task"""
    topic: str
    status: TaskStatus
    thread_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    checkpoint_file: Optional[str] = None
    final_report_path: Optional[str] = None
    error_message: Optional[str] = None
    last_event_count: int = 0
    # DToR progress tracking
    dtor_branches_completed: int = 0  # Number of branches fully explored
    dtor_current_branch: Optional[str] = None  # Current branch ID
    dtor_current_depth: int = 0  # Current depth in branch
    dtor_nodes_explored: int = 0  # Total nodes explored across all branches
    last_node_type: Optional[str] = None  # research/reflect/analyze etc

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        data['status'] = TaskStatus(data['status'])
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)

class ClusterBatchRunner:
    """
    Cluster-optimized batch runner with wall-time resilience
    """

    def __init__(self,
                 wall_time_hours: float = 4.0,
                 checkpoint_dir: str = "cluster_checkpoints",
                 output_dir: str = "synthesis_branches_and_final",
                 state_file: str = "cluster_state.json",
                 grace_period_minutes: int = 10):
        """
        Initialize the cluster batch runner

        Args:
            wall_time_hours: Wall time limit in hours (default 4.0)
            checkpoint_dir: Directory for LangGraph checkpoints
            output_dir: Directory for final reports
            state_file: JSON file tracking overall batch state
            grace_period_minutes: Minutes before wall time to start graceful shutdown
        """
        self.wall_time_hours = wall_time_hours
        self.checkpoint_dir = Path(checkpoint_dir)
        self.output_dir = Path(output_dir)
        self.state_file = Path(state_file)
        self.grace_period_minutes = grace_period_minutes

        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Ensure state file parent exists (matters when scoped under checkpoint dir)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Runtime tracking
        self.start_time = datetime.now()
        self.wall_time_limit = self.start_time + timedelta(hours=wall_time_hours)
        self.grace_period_start = self.wall_time_limit - timedelta(minutes=grace_period_minutes)

        # Signal handling for graceful shutdown
        self.shutdown_requested = False
        self.register_signal_handlers()

        # Task management
        self.tasks: List[TaskState] = []
        self.current_task_index = -1

        # Configuration - load from environment variables
        # Read all env vars and convert to config dict
        config_dict = {}
        for field_name in Configuration.model_fields.keys():
            env_value = os.environ.get(field_name.upper())
            if env_value is not None:
                # Convert string values to appropriate types
                if env_value.lower() == 'true':
                    config_dict[field_name] = True
                elif env_value.lower() == 'false':
                    config_dict[field_name] = False
                elif env_value.isdigit():
                    config_dict[field_name] = int(env_value)
                else:
                    config_dict[field_name] = env_value

        self.config_instance = Configuration(**config_dict)

        # Initialize logging system from dtor_nodes
        self.timestamp = setup_logging()
        logger.info(f"Configuration loaded. Mode: {self.config_instance.research_mode}")
        logger.info(f"Session timestamp: {self.timestamp}")

        # Checkpoint management
        self.checkpointers: Dict[str, SqliteSaver] = {}

    def register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self.handle_shutdown_signal)
        signal.signal(signal.SIGINT, self.handle_shutdown_signal)
        signal.signal(signal.SIGUSR1, self.handle_checkpoint_signal)  # Manual checkpoint
        signal.signal(signal.SIGUSR2, self.handle_status_signal)  # Status report

    def handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.warning(f"Received signal {signum}. Initiating graceful shutdown...")
        self.shutdown_requested = True

    def handle_checkpoint_signal(self, signum, frame):
        """Handle checkpoint signal - force checkpoint current state"""
        logger.info("Manual checkpoint requested via SIGUSR1")
        self.save_state()

    def handle_status_signal(self, signum, frame):
        """Handle status signal - log current progress"""
        logger.info("Status report requested via SIGUSR2")
        self.print_status_report()

    def load_or_create_state(self, topics: List[str]) -> None:
        """Load existing state or create new one"""
        if self.state_file.exists():
            logger.info(f"Loading existing state from {self.state_file}")
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)

                # Reconstruct task states
                self.tasks = [TaskState.from_dict(t) for t in state_data['tasks']]
                self.current_task_index = state_data.get('current_task_index', -1)

                # Log loaded tasks for debugging
                for i, task in enumerate(self.tasks):
                    logger.info(f"  Task {i}: {task.status.value} - {task.thread_id}")

                # Verify topics match
                existing_topics = [t.topic for t in self.tasks]
                if existing_topics != topics:
                    logger.warning("Topic list changed! Updating task list...")
                    self.merge_task_lists(existing_topics, topics)

                logger.info(f"Loaded state: {len(self.tasks)} tasks, current index: {self.current_task_index}")

            except Exception as e:
                logger.error(f"Failed to load state: {e}. Starting fresh...")
                self.initialize_fresh_state(topics)
        else:
            self.initialize_fresh_state(topics)

    def initialize_fresh_state(self, topics: List[str]):
        """Initialize fresh state for new batch"""
        logger.info(f"Initializing fresh state for {len(topics)} topics")
        self.tasks = []
        for topic in topics:
            thread_id = self.generate_thread_id(topic)
            checkpoint_file = self.checkpoint_dir / f"{thread_id}.sqlite"
            self.tasks.append(TaskState(
                topic=topic,
                status=TaskStatus.PENDING,
                thread_id=thread_id,
                checkpoint_file=str(checkpoint_file)
            ))
        self.current_task_index = -1
        self.save_state()

    def merge_task_lists(self, existing_topics: List[str], new_topics: List[str]):
        """Merge existing task states with new topic list"""
        # Create mapping of existing tasks
        existing_map = {t.topic: t for t in self.tasks}

        # Build new task list preserving existing states
        new_tasks = []
        for topic in new_topics:
            if topic in existing_map:
                new_tasks.append(existing_map[topic])
            else:
                thread_id = self.generate_thread_id(topic)
                checkpoint_file = self.checkpoint_dir / f"{thread_id}.sqlite"
                new_tasks.append(TaskState(
                    topic=topic,
                    status=TaskStatus.PENDING,
                    thread_id=thread_id,
                    checkpoint_file=str(checkpoint_file)
                ))

        self.tasks = new_tasks
        logger.info(f"Merged task list: {len(self.tasks)} total tasks")

    def generate_thread_id(self, topic: str) -> str:
        """Generate consistent thread ID for a topic"""
        import hashlib
        # Sanitize topic for filesystem use
        sanitized = topic.strip().replace(' ', '_').replace('/', '_')[:50]
        # Use MD5 hash for consistent ID across process restarts
        stable_hash = hashlib.md5(topic.encode('utf-8')).hexdigest()[:6]
        return f"research_{sanitized}_{stable_hash}"

    def save_state(self):
        """Save current state to JSON file"""
        state_data = {
            'tasks': [t.to_dict() for t in self.tasks],
            'current_task_index': self.current_task_index,
            'last_save': datetime.now().isoformat(),
            'wall_time_hours': self.wall_time_hours,
            'checkpoint_dir': str(self.checkpoint_dir),
            'output_dir': str(self.output_dir)
        }

        # Atomic write with temp file
        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        temp_file.replace(self.state_file)
        logger.debug(f"State saved to {self.state_file}")

    def check_time_remaining(self) -> Tuple[bool, float]:
        """
        Check if we have time to continue
        Returns: (can_continue, hours_remaining)
        """
        now = datetime.now()

        # Check if we're in grace period
        if now >= self.grace_period_start:
            hours_remaining = (self.wall_time_limit - now).total_seconds() / 3600
            logger.warning(f"Entering grace period. {hours_remaining:.2f} hours remaining")
            return False, hours_remaining

        hours_remaining = (self.wall_time_limit - now).total_seconds() / 3600
        return True, hours_remaining

    def get_next_task(self) -> Optional[TaskState]:
        """Get next task to process"""
        for i, task in enumerate(self.tasks):
            if task.status == TaskStatus.PENDING:
                self.current_task_index = i
                return task
            elif task.status == TaskStatus.INTERRUPTED:
                # Prioritize interrupted tasks for resumption
                self.current_task_index = i
                return task
        return None

    def get_checkpointer(self, task: TaskState):
        """Get or create checkpointer connection string for a task"""
        checkpoint_path = Path(task.checkpoint_file)
        # Return the path string for use with from_conn_string
        return str(checkpoint_path)

    def run_single_task(self, task: TaskState) -> bool:
        """
        Run or resume a single research task
        Returns: True if completed, False if interrupted
        """
        logger.info(f"{'Resuming' if task.status == TaskStatus.INTERRUPTED else 'Starting'} task: {task.topic}")

        # Update task status
        if task.status != TaskStatus.INTERRUPTED:
            task.status = TaskStatus.IN_PROGRESS
            task.start_time = datetime.now()

        # Get checkpointer connection string
        checkpoint_conn = self.get_checkpointer(task)

        # Import necessary components to build the graph with checkpointer
        from src.ollama_deep_researcher.dtor_graph import create_main_graph

        # Use checkpointer in with statement for entire execution
        with SqliteSaver.from_conn_string(checkpoint_conn) as checkpointer:
            # Build main graph using shared checkpointer so DToR state is persisted
            app = create_main_graph(checkpointer=checkpointer)

            # Set the step timeout (24 hours)
            app.step_timeout = 86400  # 24 hours in seconds

            # Prepare run configuration matching original system
            run_config = {
                "configurable": {
                    "thread_id": task.thread_id,
                    **self.config_instance.model_dump(),
                },
                "recursion_limit": 1000,  # Allow deeper DToR recursion for long resumes
            }

            try:
                # Check if we can resume from checkpoint
                state = app.get_state(run_config)

                # Decision logic for resume vs fresh start
                should_resume = False
                has_checkpoint = False

                if state and state.values:
                    has_checkpoint = True
                    # Check if there's unfinished work
                    if state.next and len(state.next) > 0:
                        should_resume = True
                        logger.info("="*60)
                        logger.info("CHECKPOINT FOUND - RESUMING EXECUTION")
                        logger.info(f"Next nodes to execute: {state.next}")

                        # Log what's in the checkpoint for debugging
                        logger.info(f"State values type: {type(state.values)}")
                        logger.info(f"State values keys: {list(state.values.keys()) if hasattr(state.values, 'keys') else 'N/A'}")

                        if hasattr(state.values, 'branches') or (hasattr(state.values, 'get') and 'branches' in state.values):
                            branches = state.values.branches if hasattr(state.values, 'branches') else state.values.get('branches')
                            if branches:
                                logger.info(f"Existing branches: {len(branches)}")
                                for branch_id in list(branches.keys())[:3]:
                                    logger.info(f"  Branch {branch_id[:8]}...")

                        if 'active_branch_id' in state.values:
                            logger.info(f"Active branch: {state.values['active_branch_id'][:8]}...")

                        if 'research_loop_count' in state.values:
                            logger.info(f"Research loops completed: {state.values['research_loop_count']}")
                        logger.info("="*60)
                    else:
                        # Checkpoint exists but no next nodes - could be complete or at a stopping point
                        logger.info("Checkpoint exists but no pending nodes")

                        # Check if task was previously marked as interrupted
                        if task.status == TaskStatus.INTERRUPTED:
                            # Try to resume anyway
                            should_resume = True
                            logger.info("Task was interrupted - attempting resume")
                        else:
                            logger.info("Task appears complete or at natural stopping point")

                # Execute based on decision
                if should_resume:
                    # Resume from checkpoint - pass None to continue
                    stream = app.stream(None, config=run_config)
                else:
                    # Start fresh execution
                    if has_checkpoint:
                        logger.warning("Starting fresh despite existing checkpoint")
                    else:
                        logger.info("Starting fresh execution (no checkpoint)")

                    # Prepare inputs for fresh start
                    inputs = DToRStateInput(
                        research_topic=task.topic,
                        mode=self.config_instance.research_mode
                    )
                    stream = app.stream(asdict(inputs), config=run_config)
                event_counter = task.last_event_count
                last_event_data = None
                checkpoint_interval = 10  # Checkpoint every N events

                for event in stream:
                    event_counter += 1

                    # Capture event data and update progress
                    for node_name, node_output in event.items():
                        if node_output is not None:
                            last_event_data = node_output
                            logger.info(f"[{task.topic[:30]}...] Step {event_counter}: {node_name}")

                            # Update DToR progress if available
                            task.last_node_type = node_name
                            if isinstance(node_output, dict):
                                if 'active_branch_id' in node_output:
                                    task.dtor_current_branch = node_output['active_branch_id']
                                if 'branches' in node_output:
                                    # Count completed branches
                                    completed = sum(1 for b in node_output['branches'].values()
                                                  if b.get('is_complete', False))
                                    task.dtor_branches_completed = completed
                                    # Get current depth from active branch
                                    if task.dtor_current_branch in node_output['branches']:
                                        branch = node_output['branches'][task.dtor_current_branch]
                                        task.dtor_current_depth = branch.get('depth', 0)
                                        task.dtor_nodes_explored = sum(len(b.get('research_nodes', []))
                                                                     for b in node_output['branches'].values())

                    # Periodic checkpointing
                    if event_counter % checkpoint_interval == 0:
                        task.last_event_count = event_counter
                        self.save_state()

                    # Check for interruption conditions
                    if self.shutdown_requested:
                        logger.warning(f"Shutdown requested. Interrupting task: {task.topic}")
                        task.status = TaskStatus.INTERRUPTED
                        task.last_event_count = event_counter
                        self.save_state()
                        return False

                    # Check wall time
                    can_continue, hours_left = self.check_time_remaining()
                    if not can_continue:
                        logger.warning(f"Approaching wall time limit ({hours_left:.2f}h left). Interrupting task")
                        task.status = TaskStatus.INTERRUPTED
                        task.last_event_count = event_counter
                        self.save_state()
                        return False

                # Task completed successfully
                logger.info(f"Task completed: {task.topic} after {event_counter} events")

                # Extract and save final report
                final_report = self.extract_final_report(last_event_data)
                if final_report:
                    report_path = self.save_final_report(task, final_report)
                    task.final_report_path = str(report_path)

                task.status = TaskStatus.COMPLETED
                task.end_time = datetime.now()
                task.last_event_count = event_counter
                self.save_state()
                return True

            except Exception as e:
                logger.error(f"Error processing task {task.topic}: {e}", exc_info=True)
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.end_time = datetime.now()
                self.save_state()
                return False

    def extract_final_report(self, last_event_data: Any) -> Optional[str]:
        """Extract final report from graph output"""
        if not last_event_data:
            return None

        if isinstance(last_event_data, dict):
            # Try different keys where report might be
            for key in ['final_summary', 'running_summary', 'report']:
                if key in last_event_data and last_event_data[key]:
                    return last_event_data[key]

        return str(last_event_data) if last_event_data else None

    def save_final_report(self, task: TaskState, report: str) -> Path:
        """Save final report to file matching original directory structure"""
        # Create topic-specific directory as in original system
        safe_dirname = task.topic.replace(' ', '_').replace('/', '_')[:100]
        topic_dir = self.output_dir / safe_dirname
        topic_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Check if this is DToR mode to name appropriately
        if self.config_instance.research_mode == "dtor":
            report_path = topic_dir / f"final_report_{timestamp}.md"
        else:
            report_path = topic_dir / f"report_{timestamp}.md"

        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            # Write header matching original format
            f.write(f"# Research Report: {task.topic}\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Thread ID: {task.thread_id}\n")
            f.write(f"Mode: {self.config_instance.research_mode}\n")
            f.write(f"Max Web Research Loops: {self.config_instance.max_web_research_loops}\n")

            # Include FET mode if enabled
            if self.config_instance.enable_fet_raw_data:
                f.write(f"FET Sensor Mode: Enabled\n")

            f.write("\n---\n\n")
            f.write(report)

        logger.info(f"Report saved to {report_path}")
        return report_path

    def extract_checkpoint_state(self, checkpoint_file: str, thread_id: str) -> Optional[Dict[str, Any]]:
        """Extract saved state from checkpoint database"""
        checkpoint_path = Path(checkpoint_file)
        if not checkpoint_path.exists():
            return None

        try:
            conn = sqlite3.connect(checkpoint_path)
            cursor = conn.cursor()

            # Get latest checkpoint
            query = """
            SELECT checkpoint
            FROM checkpoints
            WHERE thread_id = ?
            ORDER BY checkpoint_id DESC
            LIMIT 1
            """

            result = cursor.execute(query, (thread_id,)).fetchone()
            conn.close()

            if result:
                checkpoint_blob = result[0]
                # Unpickle the checkpoint
                try:
                    checkpoint = pickle.loads(checkpoint_blob)

                    # Extract state from different possible locations
                    state_data = {}

                    # Check direct keys
                    if isinstance(checkpoint, dict):
                        for key in ['branches', 'active_branch_id', 'running_summary',
                                   'research_loop_count', 'complete', 'final_summary']:
                            if key in checkpoint:
                                state_data[key] = checkpoint[key]

                        # Check channel_values (LangGraph v0.1.x)
                        if 'channel_values' in checkpoint:
                            channel = checkpoint['channel_values']
                            for key in ['branches', 'active_branch_id', 'running_summary', 'research_loop_count']:
                                if key in channel:
                                    state_data[key] = channel[key]

                        # Check values (LangGraph v0.2.x)
                        if 'values' in checkpoint:
                            values = checkpoint['values']
                            for key in ['branches', 'active_branch_id', 'running_summary', 'research_loop_count']:
                                if key in values:
                                    state_data[key] = values[key]

                    return state_data if state_data else None

                except Exception as e:
                    logger.error(f"Failed to extract checkpoint state: {e}")
                    return None

        except Exception as e:
            logger.error(f"Failed to read checkpoint database: {e}")
            return None

    def print_status_report(self):
        """Print current batch status"""
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        interrupted = sum(1 for t in self.tasks if t.status == TaskStatus.INTERRUPTED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)

        _, hours_left = self.check_time_remaining()
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600

        logger.info("="*60)
        logger.info("BATCH STATUS REPORT")
        logger.info(f"Runtime: {runtime:.2f} hours | Remaining: {hours_left:.2f} hours")
        logger.info(f"Total Tasks: {len(self.tasks)}")
        logger.info(f"  Completed: {completed}")
        logger.info(f"  In Progress: {in_progress}")
        logger.info(f"  Interrupted: {interrupted}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Pending: {pending}")

        if self.current_task_index >= 0 and self.current_task_index < len(self.tasks):
            current = self.tasks[self.current_task_index]
            logger.info(f"Current Task: {current.topic[:50]}...")
            logger.info(f"  Events: {current.last_event_count} | Last Node: {current.last_node_type}")
            if self.config_instance.research_mode == "dtor":
                logger.info(f"  DToR Progress: Branch {current.dtor_current_branch} at depth {current.dtor_current_depth}")
                logger.info(f"  Branches: {current.dtor_branches_completed} completed | Nodes explored: {current.dtor_nodes_explored}")
        logger.info("="*60)

    def run_batch(self, topics: List[str]) -> Dict[str, Any]:
        """
        Run batch of research topics with cluster optimizations

        Returns: Summary dictionary of execution results
        """
        logger.info(f"Starting cluster batch run: {len(topics)} topics, {self.wall_time_hours}h wall time")

        # Load or create state
        self.load_or_create_state(topics)

        # Main execution loop
        while True:
            # Check if we should stop
            if self.shutdown_requested:
                logger.warning("Shutdown requested. Stopping batch execution.")
                break

            can_continue, hours_left = self.check_time_remaining()
            if not can_continue:
                logger.warning(f"Approaching wall time limit ({hours_left:.2f}h remaining). Stopping.")
                break

            # Get next task
            task = self.get_next_task()
            if not task:
                logger.info("All tasks completed or failed. Batch execution finished.")
                break

            # Run task
            logger.info(f"Processing task {self.current_task_index + 1}/{len(self.tasks)}: {task.topic}")
            completed = self.run_single_task(task)

            if not completed:
                logger.info(f"Task interrupted: {task.topic}")

            # Print periodic status
            if (self.current_task_index + 1) % 5 == 0:
                self.print_status_report()

        # Final status report
        self.print_status_report()

        # Generate summary
        summary = {
            'total_tasks': len(self.tasks),
            'completed': sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED),
            'interrupted': sum(1 for t in self.tasks if t.status == TaskStatus.INTERRUPTED),
            'failed': sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            'pending': sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
            'runtime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'reports_generated': [t.final_report_path for t in self.tasks if t.final_report_path],
            'can_resume': any(t.status in [TaskStatus.PENDING, TaskStatus.INTERRUPTED] for t in self.tasks)
        }

        # Save final state
        self.save_state()

        # Write summary file
        summary_file = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Batch summary saved to {summary_file}")

        return summary

def load_topics_from_file(file_path: str) -> List[str]:
    """Load topics from a text file (one per line)"""
    topics = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                topics.append(line)
    return topics

def main():
    """Main entry point for cluster batch runner"""
    parser = argparse.ArgumentParser(
        description="Cluster-optimized batch research runner with wall-time resilience\n" +
                    "Supports various cluster configurations (4h, 8h, 12h wall-time limits)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single topic with 4-hour wall time
  # 4-hour cluster
  python run_batch_cluster.py "quantum computing applications" --wall-time 3.83

  # 8-hour cluster
  python run_batch_cluster.py "quantum computing applications" --wall-time 7.83

  # 12-hour cluster
  python run_batch_cluster.py "quantum computing applications" --wall-time 11.83

  # Run multiple topics from file with 2-hour limit
  python run_batch_cluster.py --topics-file research_topics.txt --wall-time 2.0

  # Resume interrupted batch with custom directories
  python run_batch_cluster.py --topics-file topics.txt --checkpoint-dir my_checkpoints --output-dir my_reports

  # Override configuration settings
  python run_batch_cluster.py "topic" -c research_mode dtor -c max_web_research_loops 10

Signal handling:
  - SIGTERM/SIGINT: Graceful shutdown
  - SIGUSR1: Force checkpoint current state
  - SIGUSR2: Print status report

SLURM integration example:
  #!/bin/bash
  #SBATCH --time=04:00:00
  #SBATCH --signal=TERM@10:00  # Send SIGTERM 10 min before limit

  python run_batch_cluster.py --topics-file topics.txt --wall-time 3.83
        """
    )

    # Topic specification (mutually exclusive)
    topic_group = parser.add_mutually_exclusive_group(required=True)
    topic_group.add_argument(
        "topic",
        nargs='?',
        help="Single research topic to investigate"
    )
    topic_group.add_argument(
        "--topics-file",
        help="File containing research topics (one per line)"
    )

    # Cluster configuration
    parser.add_argument(
        "--wall-time",
        type=float,
        default=4.0,
        help="Wall time limit in hours (default: 4.0, adjust for your cluster: 4h/8h/12h)"
    )
    parser.add_argument(
        "--grace-period",
        type=int,
        default=10,
        help="Minutes before wall time to start graceful shutdown (default: 10)"
    )

    # Directory configuration
    parser.add_argument(
        "--checkpoint-dir",
        default="cluster_checkpoints",
        help="Directory for LangGraph checkpoints (default: cluster_checkpoints)"
    )
    parser.add_argument(
        "--output-dir",
        default="synthesis_branches_and_final",
        help="Directory for final reports (default: synthesis_branches_and_final)"
    )
    parser.add_argument(
        "--state-file",
        default="cluster_state.json",
        help="JSON file tracking batch state (default: cluster_state.json)"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional identifier to isolate checkpoints/output (defaults to SLURM_JOB_ID when available)"
    )

    # Research configuration overrides
    parser.add_argument(
        "-c", "--config",
        nargs=2,
        action='append',
        metavar=('KEY', 'VALUE'),
        help="Override configuration settings (e.g., -c research_mode dtor)"
    )

    # Logging
    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Load topics
    if args.topic:
        topics = [args.topic]
    else:
        topics = load_topics_from_file(args.topics_file)
        logger.info(f"Loaded {len(topics)} topics from {args.topics_file}")

    # Process configuration overrides
    config_overrides = {}
    if args.config:
        for key, value in args.config:
            # Convert values to appropriate types
            if value.lower() == 'true':
                config_overrides[key] = True
            elif value.lower() == 'false':
                config_overrides[key] = False
            elif value.isdigit():
                config_overrides[key] = int(value)
            else:
                try:
                    config_overrides[key] = float(value)
                except ValueError:
                    config_overrides[key] = value

    # Determine run identifier for concurrent jobs
    default_checkpoint_dir = parser.get_default('checkpoint_dir')
    default_state_file = parser.get_default('state_file')

    run_id = args.run_id or os.environ.get("SLURM_JOB_ID")
    checkpoint_dir = Path(args.checkpoint_dir)
    output_dir = Path(args.output_dir)
    state_file = Path(args.state_file)

    if run_id:
        logger.info(f"Using run identifier '{run_id}' for checkpoint scoping")
        checkpoint_dir = checkpoint_dir / run_id
        output_dir = output_dir / run_id
        if args.state_file == default_state_file:
            state_file = checkpoint_dir / default_state_file
        else:
            state_file = Path(args.state_file)
    else:
        state_file = Path(args.state_file)

    logger.info(f"Checkpoint directory: {checkpoint_dir}")
    logger.info(f"State file: {state_file}")
    logger.info(f"Output directory: {output_dir}")

    # Initialize and run batch runner
    runner = ClusterBatchRunner(
        wall_time_hours=args.wall_time,
        checkpoint_dir=str(checkpoint_dir),
        output_dir=str(output_dir),
        state_file=str(state_file),
        grace_period_minutes=args.grace_period
    )

    # Apply configuration overrides
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(runner.config_instance, key):
                setattr(runner.config_instance, key, value)
                logger.info(f"Configuration override: {key}={value}")

    # Run batch
    try:
        summary = runner.run_batch(topics)

        # Exit code based on completion status
        if summary['can_resume']:
            logger.info("Batch can be resumed. Some tasks remain incomplete.")
            sys.exit(2)  # Special exit code for resumable state
        elif summary['failed'] > 0:
            logger.warning(f"Batch completed with {summary['failed']} failed tasks.")
            sys.exit(1)
        else:
            logger.info("Batch completed successfully!")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error in batch execution: {e}", exc_info=True)
        sys.exit(3)

if __name__ == "__main__":
    main()
