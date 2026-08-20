import operator
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from typing_extensions import Annotated, TypedDict

from ollama_deep_researcher.state import SummaryState


class DToRStateInput(TypedDict, total=False):
    """Input for the Deep Tree of Research system."""
    research_topic: str
    mode: str  # "single" or "dtor"


@dataclass(kw_only=True)
class ResearchBranch:
    """Represents a single research branch in the Deep Tree of Research."""
    branch_id: str  # Unique identifier for this branch
    parent_branch_id: Optional[str] = None  # ID of the parent branch (None for root branches)
    depth: int = 0  # Current depth of this branch
    perspective: str = ""  # The perspective/approach this branch is exploring
    research_nodes: List[SummaryState] = field(default_factory=list)  # Research states in this branch
    branch_summary: str = ""  # Summary of findings for this branch
    is_complete: bool = False  # Whether this branch has been completed
    remaining_budget: int = 3  # Default budget for each branch
    
@dataclass(kw_only=True)
class DToRState:
    """State for the Deep Tree of Research system."""
    # Original research topic from the user
    research_topic: str = field(default="")
    
    # Mode selection (single or DToR)
    mode: str = field(default="single")  # "single" or "dtor"
    
    # Tree structure
    branches: Dict[str, ResearchBranch] = field(default_factory=dict)  # Map of branch_id to ResearchBranch
    active_branch_id: Optional[str] = field(default=None)  # Currently active branch ID
    
    # Resources management
    max_branch_depth: int = field(default=1)  # Maximum depth of any branch
    max_branches: int = field(default=3)  # Maximum number of concurrent branches
    nodes_per_branch: int = field(default=100)  # Default budget of research nodes per branch
    
    # Knowledge gaps identified during analysis
    knowledge_gaps: List[Dict] = field(default_factory=list)  # Knowledge gaps for query generation
    
    # Final synthesis
    final_summary: str = field(default="")  # Final synthesized report
    is_complete: bool = field(default=False)  # Whether the entire research process is complete
    
    # For results
    all_sources: Annotated[list, operator.add] = field(default_factory=list)  # All sources from all branches

class DToRStateOutput(TypedDict, total=False):
    """Output for the Deep Tree of Research system."""
    final_summary: str  # Final synthesized report
    all_sources: List[str]  # All sources from all branches
    branch_summaries: Dict[str, str]  # perspective -> branch synthesis (dtor mode)
