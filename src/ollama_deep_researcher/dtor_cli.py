# Standard imports
import argparse
import dataclasses
import datetime
import hashlib
import logging
import os
import pathlib
import sys
import typing
from typing import Optional, Dict, List, Set, Any

# Load .env file before any other imports that might use environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src directory to Python path for direct script execution
# This allows Python to find ollama_deep_researcher package
src_dir = pathlib.Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Application imports
from ollama_deep_researcher.graph import create_single_research_graph
from ollama_deep_researcher.dtor_graph import build_dtor_graph
from ollama_deep_researcher.dtor_state import DToRStateInput
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver


# Constants
STEP_TIMEOUT_SECONDS = 86400  # 24 hours
DEFAULT_RECURSION_LIMIT = 500
DEFAULT_CHECKPOINT_NAME = "checkpoint.sqlite"
DEFAULT_FINAL_REPORT_NAME = "final_report.md"
DEFAULT_INTERIM_REPORTS_NAME = "interim_reports"
DEFAULT_SOURCES_NAME = "sources.md"
MAX_SOURCE_LENGTH = 200
TOPIC_NAME_LENGTH = 10

# Configure logging
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=logging.INFO
)


@dataclasses.dataclass
class Config:
    """Configuration for the CLI application."""
    research_topic: str = dataclasses.field(metadata={
        "help": "String topic of research or a file path to a topic file",
        "short": "t"
    })
    mode: str = dataclasses.field(default="single", metadata={
        "help": "Research mode: 'single' for single-path research or 'tree' for Deep Tree of Research",
        "choices": ["single", "tree"],
        "short": "m"
    })
    recursion_limit: int = dataclasses.field(default=DEFAULT_RECURSION_LIMIT, metadata={
        "help": "Recursion limit for the research",
        "short": "r"
    })
    no_resume: bool = dataclasses.field(default=False, metadata={
        "help": "Do not resume from checkpoint",
        "short": "n"
    })
    out_dir: pathlib.Path = dataclasses.field(default=pathlib.Path("output"), metadata={
        "help": "Output directory for the research",
        "short": "o"
    })

    # Class constants
    CHECKPOINT_NAME: typing.ClassVar[str] = DEFAULT_CHECKPOINT_NAME
    FINAL_REPORT_NAME: typing.ClassVar[str] = DEFAULT_FINAL_REPORT_NAME
    INTERIM_REPORTS_NAME: typing.ClassVar[str] = DEFAULT_INTERIM_REPORTS_NAME
    SOURCES_NAME: typing.ClassVar[str] = DEFAULT_SOURCES_NAME


class ResearchConfigBuilder:
    """Builder for creating research configuration objects."""

    @staticmethod
    def create_thread_id(research_topic: str) -> str:
        """Generate a unique thread ID based on research topic."""
        return f"research_{hashlib.md5(research_topic.encode()).hexdigest()[:12]}"

    @staticmethod
    def build(research_topic: str, recursion_limit: int = DEFAULT_RECURSION_LIMIT) -> RunnableConfig:
        """Build a RunnableConfig for research execution."""
        use_local_rag = os.getenv("USE_LOCAL_RAG", "false").lower() == "true"
        thread_id = ResearchConfigBuilder.create_thread_id(research_topic)

        return RunnableConfig(
            configurable={
                "thread_id": thread_id,
                "use_local_rag": use_local_rag,
            },
            recursion_limit=recursion_limit
        )


class CheckpointManager:
    """Manages checkpoint operations and state."""

    @staticmethod
    def check_status(app: Any, research_config: RunnableConfig) -> tuple[bool, Optional[Any]]:
        """Check if a checkpoint exists and if we should resume from it."""
        try:
            state = app.get_state(research_config)

            if state and state.values:
                has_unfinished_work = state.next and len(state.next) > 0

                if has_unfinished_work:
                    CheckpointManager._log_checkpoint_info(state)
                    return True, state
                else:
                    logging.info("CHECKPOINT FOUND - Research appears complete")
                    return False, state
            else:
                logging.info("No checkpoint found - starting fresh")
                return False, None
        except Exception as e:
            logging.warning(f"Error checking checkpoint: {e}. Starting fresh.")
            return False, None

    @staticmethod
    def _log_checkpoint_info(state: Any) -> None:
        """Log checkpoint state information."""
        logging.info("=" * 60)
        logging.info("CHECKPOINT FOUND - Can resume execution")
        logging.info(f"Next nodes to execute: {state.next}")

        if hasattr(state.values, 'research_topic'):
            logging.info(f"Research topic: {state.values.research_topic}")
        if hasattr(state.values, 'research_loop_count'):
            logging.info(f"Current iteration: {state.values.research_loop_count}")
        if hasattr(state.values, 'running_summary') and state.values.running_summary:
            summary_preview = state.values.running_summary[:100]
            logging.info(f"Latest summary preview: {summary_preview}...")


class FileWriter:
    """Handles writing reports and sources to files."""

    @staticmethod
    def write_interim_report(update: dict, out_dir: pathlib.Path, research_topic: str) -> None:
        """Write an interim report to the output directory."""
        summary_history = update.get("summary_history", [])
        if not summary_history:
            logging.warning("No summary_history found in update, skipping interim report")
            return

        last_entry = summary_history[-1] if isinstance(summary_history[-1], dict) else {}
        iteration = last_entry.get("iteration", 0)
        query = last_entry.get("query", "")
        complementary_query = last_entry.get("complementary_query", "")
        running_summary = update.get("running_summary", "")

        # Format markdown content
        if complementary_query:
            markdown_content = f"## Iteration {iteration}\n\n{query}\n\n{complementary_query}\n\n{running_summary}"
        else:
            markdown_content = f"## Iteration {iteration}\n\n{query}\n\n{running_summary}"

        filename = f"report_iteration_{iteration:02d}.md"
        report_path = out_dir / Config.INTERIM_REPORTS_NAME / filename

        FileWriter._write_file(report_path, markdown_content)
        logging.info(f"Wrote interim report for iteration {iteration} to {report_path}")

    @staticmethod
    def write_branch_summary(
        branch_summary: str,
        branch_perspective: str,
        branch_id: str,
        out_dir: pathlib.Path,
        research_topic: str
    ) -> None:
        """Write a branch summary as an interim report for DToR mode."""
        markdown_content = f"## Branch: {branch_perspective}\n\n{branch_summary}"
        safe_perspective = FileWriter._sanitize_filename(branch_perspective)
        filename = f"branch_{branch_id[:8]}_{safe_perspective}.md"
        report_path = out_dir / Config.INTERIM_REPORTS_NAME / filename

        FileWriter._write_file(report_path, markdown_content)
        logging.info(f"Wrote branch summary for {branch_perspective} to {report_path}")

    @staticmethod
    def write_final_report(update: dict, out_dir: pathlib.Path, research_topic: str) -> None:
        """Write a final report to the output directory."""
        final_summary = update.get("final_summary", "")
        report_path = out_dir / Config.FINAL_REPORT_NAME

        FileWriter._write_file(report_path, final_summary)
        logging.info(f"Wrote final report to {report_path}")

    @staticmethod
    def write_sources(sources: List[str], out_dir: pathlib.Path) -> None:
        """Write sources to the output directory."""
        sources.sort()
        report_path = out_dir / Config.SOURCES_NAME

        FileWriter._write_file(report_path, "\n".join(sources))
        logging.info(f"Wrote sources to {report_path}")

    @staticmethod
    def _write_file(path: pathlib.Path, content: str) -> None:
        """Write content to a file, creating parent directories if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _sanitize_filename(text: str, max_len: int = 50) -> str:
        """Sanitize text for use in filenames."""
        safe = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).rstrip()[:max_len]
        return safe.replace(' ', '_')


class SourceExtractor:
    """Extracts and processes sources from graph updates."""

    SOURCE_FIELDS = {
        'sources_gathered',
        'web_research_results',
        'complementary_sources_gathered',
        'local_sources_gathered',
        'complementary_web_research_results'
    }

    @staticmethod
    def parse_source_strings(source_list: List[str], skip_no_sources: bool = True) -> List[str]:
        """Parse a list of multi-line source strings into individual source entries.

        Handles both simple source lists and formatted source strings from
        deduplicate_and_format_sources which have structure:
        Source: title
        ===
        URL: url
        ===
        ...
        """
        parsed_sources = []
        for source_str in source_list:
            if skip_no_sources and 'No sources found' in source_str:
                continue

            # Check if this is a formatted source string (from deduplicate_and_format_sources)
            if 'URL:' in source_str and 'Source:' in source_str:
                # Extract URLs from formatted string
                import re
                url_pattern = r'URL:\s*(https?://[^\s\n]+)'
                urls = re.findall(url_pattern, source_str)
                parsed_sources.extend(urls)
            else:
                # Simple format - just split by newlines
                for line in source_str.split('\n'):
                    stripped_line = line.strip()
                    # Skip separator lines and empty lines
                    if stripped_line and not stripped_line.startswith('===') and stripped_line != 'Sources:':
                        # If it looks like a URL, add it
                        if stripped_line.startswith('http://') or stripped_line.startswith('https://'):
                            parsed_sources.append(stripped_line)
                        # Otherwise, check if line contains a URL
                        elif 'http://' in stripped_line or 'https://' in stripped_line:
                            import re
                            url_pattern = r'https?://[^\s\n\)]+'
                            urls = re.findall(url_pattern, stripped_line)
                            parsed_sources.extend(urls)
                        elif stripped_line:  # Non-empty line that's not a URL
                            parsed_sources.append(stripped_line)

        return parsed_sources

    @staticmethod
    def extract_from_update(update: dict) -> List[str]:
        """Extract and parse all sources from a graph update."""
        sources = []

        # Extract from DToR mode nodes
        sources.extend(SourceExtractor._extract_dtor_sources(update))

        # Extract from single mode nodes
        sources.extend(SourceExtractor._extract_single_mode_sources(update))

        return sources

    @staticmethod
    def _extract_dtor_sources(update: dict) -> List[str]:
        """Extract sources from DToR mode nodes.

        Note: Source aggregation for DToR mode is disabled because sources are not
        gathered by the underlying graph. The research_node function in dtor_graph.py
        explicitly discards sources in DToR mode, and nothing populates the all_sources
        field in DToRState.
        """
        # Source aggregation for DToR mode is disabled
        return []

    @staticmethod
    def _extract_single_mode_sources(update: dict) -> List[str]:
        """Extract sources from single mode nodes."""
        sources = []

        web_sources = update.get("web_research", {}).get("sources_gathered", [])
        if web_sources:
            sources.extend(SourceExtractor.parse_source_strings(web_sources, skip_no_sources=True))

        complementary_sources = update.get("complementary_web_research", {}).get("complementary_sources_gathered", [])
        if complementary_sources:
            sources.extend(SourceExtractor.parse_source_strings(complementary_sources, skip_no_sources=False))

        local_sources = update.get("local_rag_research", {}).get("local_sources_gathered", [])
        if local_sources:
            sources.extend(SourceExtractor.parse_source_strings(local_sources, skip_no_sources=True))

        return sources

    @staticmethod
    def _parse_source_list(source_list: List[Any]) -> List[str]:
        """Parse a list of source items (strings or lists of strings).

        Handles nested structures where all_sources accumulates as lists of lists
        due to operator.add annotation in DToRState.
        """
        sources = []
        for source_item in source_list:
            if isinstance(source_item, str):
                # Direct string - parse it (may contain multiple sources separated by newlines)
                sources.extend(SourceExtractor.parse_source_strings([source_item], skip_no_sources=True))
            elif isinstance(source_item, list):
                # Nested list - recursively parse each item
                sources.extend(SourceExtractor._parse_source_list(source_item))
        return sources

    @staticmethod
    def extract_from_state(app: Any, research_config: RunnableConfig) -> List[str]:
        """Extract sources from the final state's all_sources field.

        The all_sources field accumulates via operator.add, so it may be:
        - A list of strings (formatted source strings)
        - A list of lists (when multiple branches add sources)
        - A dict-like object (when accessed from LangGraph state)
        """
        sources = []
        try:
            final_state = app.get_state(research_config)
            if not final_state:
                logging.debug("No final state available")
                return sources

            logging.debug(f"Final state type: {type(final_state)}")
            logging.debug(f"Final state attributes: {dir(final_state)}")

            # Handle different state structures
            state_values = None
            if hasattr(final_state, 'values'):
                state_values = final_state.values
                logging.debug(f"State values type: {type(state_values)}")
            elif isinstance(final_state, dict):
                state_values = final_state
            else:
                state_values = final_state

            # Extract all_sources - handle both dict and object access
            all_sources = None
            if isinstance(state_values, dict):
                all_sources = state_values.get('all_sources', [])
                logging.debug(f"Extracted all_sources from dict: type={type(all_sources)}, length={len(all_sources) if all_sources else 0}")
            elif hasattr(state_values, 'all_sources'):
                all_sources = state_values.all_sources
                logging.debug(f"Extracted all_sources from object: type={type(all_sources)}, length={len(all_sources) if all_sources else 0}")
            elif hasattr(state_values, 'get'):
                # Try dict-like access
                all_sources = state_values.get('all_sources', [])
                logging.debug(f"Extracted all_sources via get(): type={type(all_sources)}, length={len(all_sources) if all_sources else 0}")

            if all_sources:
                logging.info(f"Found {len(all_sources)} source entries in final state")
                # Log first entry structure for debugging
                if all_sources and len(all_sources) > 0:
                    logging.debug(f"First source entry type: {type(all_sources[0])}, preview: {str(all_sources[0])[:100] if isinstance(all_sources[0], str) else str(all_sources[0])}")
                sources.extend(SourceExtractor._parse_source_list(all_sources))
                logging.info(f"Extracted {len(sources)} individual sources from state")
            else:
                logging.warning("No all_sources found in final state")
        except Exception as e:
            logging.warning(f"Could not extract final sources from state: {e}")
            import traceback
            logging.debug(traceback.format_exc())
        return sources

    @staticmethod
    def deduplicate(sources: List[str]) -> List[str]:
        """Deduplicate a list of sources."""
        seen = set()
        unique = []
        for source in sources:
            if source not in seen:
                seen.add(source)
                unique.append(source)
        return unique


class UpdateProcessor:
    """Processes graph updates and triggers appropriate actions."""

    def __init__(self, research_topic_dir: pathlib.Path, research_topic: str):
        self.research_topic_dir = research_topic_dir
        self.research_topic = research_topic
        self.written_branches: Set[str] = set()

    def process_single_mode_update(self, update: dict) -> None:
        """Process an update from single mode execution."""
        if update.get("summarize_sources"):
            FileWriter.write_interim_report(
                update.get("summarize_sources"),
                self.research_topic_dir,
                self.research_topic
            )

        if update.get("finalize_summary"):
            final_update = update.get("finalize_summary", {})
            if final_update.get("running_summary"):
                FileWriter.write_final_report(
                    {"final_summary": final_update.get("running_summary")},
                    self.research_topic_dir,
                    self.research_topic
                )

    def process_tree_mode_update(self, update: dict) -> None:
        """Process an update from tree mode execution."""
        # Handle branch synthesis
        if "synthesize_branch" in update:
            self._process_branch_synthesis(update.get("synthesize_branch", {}))

        # Handle final synthesis
        if "synthesize_final" in update:
            self._process_final_synthesis(update.get("synthesize_final", {}))

    def _process_branch_synthesis(self, branch_update: dict) -> None:
        """Process a branch synthesis update."""
        branches = branch_update.get("branches", {})
        if not isinstance(branches, dict):
            return

        for branch_id, branch in branches.items():
            if branch_id in self.written_branches:
                continue

            branch_summary, branch_perspective = self._extract_branch_info(branch, branch_id)
            if branch_summary:
                FileWriter.write_branch_summary(
                    branch_summary,
                    branch_perspective,
                    branch_id,
                    self.research_topic_dir,
                    self.research_topic
                )
                self.written_branches.add(branch_id)

    def _process_final_synthesis(self, final_update: dict) -> None:
        """Process a final synthesis update."""
        final_summary = None
        if isinstance(final_update, dict):
            final_summary = final_update.get("final_summary")
        elif hasattr(final_update, "final_summary"):
            final_summary = final_update.final_summary

        if final_summary:
            FileWriter.write_final_report(
                {"final_summary": final_summary},
                self.research_topic_dir,
                self.research_topic
            )

    @staticmethod
    def _extract_branch_info(branch: Any, branch_id: str) -> tuple[Optional[str], str]:
        """Extract branch summary and perspective from branch object."""
        if isinstance(branch, dict):
            return branch.get("branch_summary", ""), branch.get("perspective", f"Branch {branch_id[:8]}")
        elif hasattr(branch, 'branch_summary'):
            return branch.branch_summary, getattr(branch, 'perspective', f"Branch {branch_id[:8]}")
        return None, f"Branch {branch_id[:8]}"


class GraphExecutor:
    """Executes research graphs and processes updates."""

    def __init__(
        self,
        app: Any,
        research_config: RunnableConfig,
        input_state: Any,
        processor: UpdateProcessor
    ):
        self.app = app
        self.research_config = research_config
        self.input_state = input_state
        self.processor = processor
        self.sources: List[str] = []

    def execute(self, mode: str) -> List[str]:
        """Execute the graph and process all updates."""
        self.app.step_timeout = STEP_TIMEOUT_SECONDS

        for update in self.app.stream(
            self.input_state,
            config=self.research_config,
            stream_mode="updates"
        ):
            logging.info(f"GRAPH UPDATE: {UpdateFormatter.truncate(update)}")

            # Process updates based on mode
            if mode == "single":
                self.processor.process_single_mode_update(update)
            elif mode == "tree":
                self.processor.process_tree_mode_update(update)

            # Collect sources (skip for tree mode - sources not gathered by underlying graph)
            if mode != "tree":
                self.sources.extend(SourceExtractor.extract_from_update(update))

        # Extract final sources from state (only for single mode)
        if mode == "single":
            self.sources.extend(SourceExtractor.extract_from_state(self.app, self.research_config))
            self.sources = SourceExtractor.deduplicate(self.sources)

        return self.sources


class UpdateFormatter:
    """Formats updates for logging."""

    @staticmethod
    def truncate_string(value: Any, max_length: int = MAX_SOURCE_LENGTH) -> Any:
        """Truncate a string to a maximum length."""
        if isinstance(value, str) and len(value) > max_length:
            return value[:max_length] + f"... [truncated {len(value) - max_length} chars]"
        return value

    @staticmethod
    def truncate(update: dict, max_source_length: int = MAX_SOURCE_LENGTH) -> dict:
        """Truncate long source fields in an update for cleaner logging."""
        if not isinstance(update, dict):
            return update

        source_fields = SourceExtractor.SOURCE_FIELDS
        truncated = {}

        for key, value in update.items():
            if isinstance(value, dict):
                truncated[key] = UpdateFormatter._truncate_nested_dict(value, source_fields, max_source_length)
            elif key in source_fields:
                truncated[key] = UpdateFormatter._truncate_value(value, max_source_length)
            else:
                truncated[key] = value

        return truncated

    @staticmethod
    def _truncate_nested_dict(nested_dict: dict, source_fields: set, max_length: int) -> dict:
        """Truncate source fields in nested dictionaries."""
        truncated = {}
        for nested_key, nested_value in nested_dict.items():
            if nested_key in source_fields:
                truncated[nested_key] = UpdateFormatter._truncate_value(nested_value, max_length)
            else:
                truncated[nested_key] = nested_value
        return truncated

    @staticmethod
    def _truncate_value(value: Any, max_length: int) -> Any:
        """Truncate a value (string or list of strings)."""
        if isinstance(value, list):
            return [UpdateFormatter.truncate_string(item, max_length) for item in value]
        return UpdateFormatter.truncate_string(value, max_length)


class ResearchRunner:
    """Orchestrates research execution for different modes."""

    @staticmethod
    def run_single_mode(
        research_topic: str,
        research_topic_dir: pathlib.Path,
        checkpoint: str = DEFAULT_CHECKPOINT_NAME,
        resume: bool = True,
        recursion_limit: int = DEFAULT_RECURSION_LIMIT
    ) -> None:
        """Run the single-path research mode."""
        logging.info("Running in single mode")

        with SqliteSaver.from_conn_string(checkpoint) as checkpointer:
            app = create_single_research_graph(checkpointer=checkpointer)
            research_config = ResearchConfigBuilder.build(research_topic, recursion_limit)

            should_resume, checkpoint_state = CheckpointManager.check_status(app, research_config)
            input_state = ResearchRunner._prepare_input_state(
                research_topic, should_resume, resume, checkpoint_state
            )

            processor = UpdateProcessor(research_topic_dir, research_topic)
            executor = GraphExecutor(app, research_config, input_state, processor)
            sources = executor.execute("single")

            ResearchRunner._finalize_sources(sources, research_topic_dir)

    @staticmethod
    def run_tree_mode(
        research_topic: str,
        research_topic_dir: pathlib.Path,
        checkpoint: str = DEFAULT_CHECKPOINT_NAME,
        resume: bool = True,
        recursion_limit: int = DEFAULT_RECURSION_LIMIT
    ) -> None:
        """Run the DToR (tree) research mode."""
        logging.info("Running in tree mode")

        with SqliteSaver.from_conn_string(checkpoint) as checkpointer:
            app = build_dtor_graph(checkpointer=checkpointer)
            research_config = ResearchConfigBuilder.build(research_topic, recursion_limit)

            should_resume, checkpoint_state = CheckpointManager.check_status(app, research_config)
            input_state = ResearchRunner._prepare_dtor_input_state(
                research_topic, should_resume, resume, checkpoint_state
            )

            processor = UpdateProcessor(research_topic_dir, research_topic)
            executor = GraphExecutor(app, research_config, input_state, processor)
            sources = executor.execute("tree")

            # Skip source writing for tree mode - sources are not gathered by the underlying graph
            # ResearchRunner._finalize_sources(sources, research_topic_dir)

    @staticmethod
    def _prepare_input_state(
        research_topic: str,
        should_resume: bool,
        resume: bool,
        checkpoint_state: Optional[Any]
    ) -> Optional[dict]:
        """Prepare input state for single mode."""
        if should_resume and resume:
            logging.info("Resuming from checkpoint...")
            return None
        else:
            if checkpoint_state and not resume:
                logging.info("Checkpoint exists but --no-resume flag set. Starting fresh.")
            logging.info("Starting new research session...")
            return {"research_topic": research_topic.strip()}

    @staticmethod
    def _prepare_dtor_input_state(
        research_topic: str,
        should_resume: bool,
        resume: bool,
        checkpoint_state: Optional[Any]
    ) -> Optional[DToRStateInput]:
        """Prepare input state for tree mode."""
        if should_resume and resume:
            logging.info("Resuming from checkpoint...")
            return None
        else:
            if checkpoint_state and not resume:
                logging.info("Checkpoint exists but --no-resume flag set. Starting fresh.")
            logging.info("Starting new research session...")
            return DToRStateInput(research_topic=research_topic, mode="dtor")

    @staticmethod
    def _finalize_sources(sources: List[str], research_topic_dir: pathlib.Path) -> None:
        """Write sources and log completion."""
        if sources:
            FileWriter.write_sources(sources, research_topic_dir)
            logging.info(f"Total sources collected: {len(sources)}")
        logging.info("Research session completed. Checkpoint saved.")


# Utility functions
def create_args() -> argparse.ArgumentParser:
    """Create an ArgumentParser from the Config dataclass."""
    parser = argparse.ArgumentParser(description="Run Deep Tree of Research (DToR)")

    for field in dataclasses.fields(Config):
        long_flag = f"--{field.name.replace('_', '-')}"
        flags = [long_flag]

        if "short" in field.metadata:
            flags.append(f"-{field.metadata['short']}")

        kwargs = {
            "help": field.metadata.get("help", ""),
            "default": field.default
        }

        if "choices" in field.metadata:
            kwargs["choices"] = field.metadata["choices"]

        if field.type == bool:
            kwargs["action"] = "store_true" if field.default is False else "store_false"
        else:
            kwargs["type"] = field.type

        parser.add_argument(*flags, **kwargs)

    return parser


def get_args() -> Config:
    """Get arguments from the command line and return a Config object."""
    arg_parser = create_args()
    args = arg_parser.parse_args()
    for key, val in vars(args).items():
        logging.info(f"{key}: {val}")
    return Config(**vars(args))


def load_research_topic(research_topic: str) -> str:
    """Load the research topic from a file or return as-is."""
    topic_path = pathlib.Path(research_topic)
    if topic_path.exists() and topic_path.is_file():
        with open(topic_path, 'r') as f:
            return f.read()
    return research_topic


def setup_data(
    out_dir: pathlib.Path,
    research_topic: str,
    interim_reports_name: str = Config.INTERIM_REPORTS_NAME,
    checkpoint_name: str = Config.CHECKPOINT_NAME
) -> tuple[pathlib.Path, pathlib.Path]:
    """Set up output directory structure and return paths."""
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped research topic directory
    safe_topic = research_topic[:TOPIC_NAME_LENGTH].replace(" ", "_")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    research_topic_dir = out_dir / f"{safe_topic}_{timestamp}"
    research_topic_dir.mkdir(parents=True, exist_ok=True)

    # Create interim reports directory
    interim_reports = research_topic_dir / interim_reports_name
    interim_reports.mkdir(parents=True, exist_ok=True)

    # Create checkpoint directory and file
    checkpoint = research_topic_dir / "checkpoints" / checkpoint_name
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint.touch(exist_ok=True)

    return research_topic_dir, checkpoint


def main() -> None:
    """Main entry point for the CLI."""
    cfg = get_args()
    research_topic = load_research_topic(cfg.research_topic)
    research_topic_dir, checkpoint = setup_data(cfg.out_dir, cfg.research_topic)

    mode_handlers = {
        "single": ResearchRunner.run_single_mode,
        "tree": ResearchRunner.run_tree_mode,
    }

    handler = mode_handlers.get(cfg.mode)
    if handler:
        handler(
            research_topic,
            research_topic_dir,
            str(checkpoint),
            not cfg.no_resume,
            cfg.recursion_limit
        )
    else:
        logging.error(f"Invalid mode specified: {cfg.mode}. Must be 'single' or 'tree'")
        sys.exit(1)


if __name__ == '__main__':
    main()
