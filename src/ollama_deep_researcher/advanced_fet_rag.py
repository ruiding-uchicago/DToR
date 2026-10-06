#!/usr/bin/env python3
"""
Advanced FET Sensor RAG System
Implements hierarchical retrieval for FET sensor data with manufacturing recommendations
Based on ADVANCED_RAG_INTEGRATION_PLAN.md and Chinese collaborator's design
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from collections import defaultdict

# LangChain imports
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
    
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_core.messages import SystemMessage, HumanMessage
from ollama_deep_researcher.configuration import Configuration
from ollama_deep_researcher.dtor_nodes import invoke_with_failover

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class QueryPlan:
    """Structured query plan after intent parsing"""
    intent: str  # sensor_analysis, manufacturing, comparison, drift_analysis
    target: Optional[str] = None  # phosphate, pH, glucose
    filters: Dict[str, Any] = None
    required_views: List[str] = None
    k_folders: int = 8  # Top folders to retrieve
    k_runs_per_folder: int = 4  # Runs per folder
    k_non_excel: int = 3  # Non-Excel context documents
    min_health_score: int = 60  # Quality threshold

    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.required_views is None:
            self.required_views = ["metrics", "semantic"]

@dataclass
class FolderResult:
    """Result from folder-level retrieval"""
    folder_id: str
    score: float
    metrics: Dict[str, Any]
    state: str
    drift_severity: Optional[str]
    target: Optional[str]
    content: str
    metadata: Dict[str, Any]
    recommendations: Dict[str, str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = {}

class FETSensorRAG:
    """Advanced RAG system for FET sensor data with multi-view vectorization"""

    def __init__(self,
                 excel_vectorstore_path: str,
                 non_excel_vectorstore_path: Optional[str] = None,
                 embedding_model: str = "BAAI/bge-m3",
                 k_folders: int = 8,
                 k_runs_per_folder: int = 4,
                 k_non_excel: int = 3,
                 llm_model: Optional[str] = None,
                 use_llm_parsing: bool = True,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the advanced FET RAG system.
        
        Args:
            excel_vectorstore_path: Path to Excel FET data vectorstore
            non_excel_vectorstore_path: Optional path to non-Excel documents vectorstore
            embedding_model: Embedding model name (MUST be BAAI/bge-m3 for compatibility)
        """
        logger.info(f"Initializing FETSensorRAG with excel_vectorstore: {excel_vectorstore_path}")

        # Store hyperparameters
        self.k_folders = k_folders
        self.k_runs_per_folder = k_runs_per_folder
        self.k_non_excel = k_non_excel
        self.config = config  # Store config for LLM initialization

        # Initialize embeddings - MUST use BAAI/bge-m3 for unity with vectorization
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info(f"Loaded embedding model: {embedding_model}")
        
        # Load Excel vectorstore (primary)
        self.excel_vectorstore = Chroma(
            persist_directory=excel_vectorstore_path,
            embedding_function=self.embeddings
        )
        logger.info("Loaded Excel FET vectorstore")
        
        # Load non-Excel vectorstore if available (secondary)
        self.non_excel_vectorstore = None
        if non_excel_vectorstore_path and Path(non_excel_vectorstore_path).exists():
            self.non_excel_vectorstore = Chroma(
                persist_directory=non_excel_vectorstore_path,
                embedding_function=self.embeddings
            )
            logger.info("Loaded non-Excel vectorstore for cross-reference")
        
        # Manufacturing rules engine (heuristic rules - no LLM needed)
        self.manufacturing_rules = self._initialize_manufacturing_rules()
        
        # View priority for retrieval (from Chinese plan)
        self.views_priority = ["metrics", "semantic", "json", "context", "table"]
        
    def query(self, query: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for RAG queries with hierarchical retrieval flow.
        Implements: Query → Parse → Folder Retrieval → Run Analysis → Recommendations
        
        Args:
            query: Natural language query
            config: Optional configuration overrides
            
        Returns:
            Structured results with documents, metrics, and recommendations
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Parse query intent
        query_plan = self._parse_query(query)
        logger.info(f"Query plan: intent={query_plan.intent}, target={query_plan.target}, filters={query_plan.filters}")
        
        # Step 2: Hierarchical retrieval
        # 2.1: Folder-level retrieval
        folder_results = self._retrieve_folders(query, query_plan)
        logger.info(f"Retrieved {len(folder_results)} folders")
        
        # 2.2: Run-level analysis
        run_results = self._analyze_runs(folder_results, query_plan)
        logger.info(f"Analyzed runs for {len(run_results)} folders")
        
        # Step 3: Cross-reference with non-Excel docs if available
        context_docs = []
        if self.non_excel_vectorstore:
            context_docs = self._get_context_documents(query, query_plan)
            logger.info(f"Retrieved {len(context_docs)} context documents")
        
        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(folder_results, run_results)
        logger.info(f"Generated {sum(len(v) for v in recommendations.values())} recommendations")
        
        # Step 5: Format output for deep research agent
        return self._format_output(
            query=query,
            query_plan=query_plan,
            folders=folder_results,
            runs=run_results,
            context=context_docs,
            recommendations=recommendations
        )
    
    def _parse_query(self, query: str) -> QueryPlan:
        """
        Parse user query to extract intent and parameters.
        Hybrid approach: Try rules first, then LLM for complex cases.
        """
        # First try rule-based parsing
        plan = self._parse_query_rules(query)

        # If rule-based parsing didn't find much and config is available, try LLM
        if self.config:
            # Check if rules found minimal information
            has_target = plan.target is not None
            has_filters = bool(plan.filters)
            has_specific_intent = plan.intent != "general_search"

            # Use LLM if query seems complex but rules didn't extract much
            if not (has_target or has_filters or has_specific_intent):
                if self._is_complex_query(query):
                    logger.info("Complex query detected, using LLM parsing")
                    llm_plan = self._parse_query_llm(query)
                    if llm_plan:
                        return llm_plan

        return plan

    def _is_complex_query(self, query: str) -> bool:
        """
        Check if query is complex enough to warrant LLM parsing.
        """
        # Complex if contains vague terms or multiple conditions
        complex_indicators = [
            "good", "best", "excellent", "stable", "reliable",
            "high performance", "low drift", "minimal",
            "find good", "performance", "stable", "reliable", "best"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complex_indicators)

    def _parse_query_llm(self, query: str) -> Optional[QueryPlan]:
        """
        Use LLM to parse complex natural language queries into structured format.
        """
        if not self.config:
            return None

        try:
            if isinstance(self.config, Configuration):
                config_obj = self.config
            elif self.config is None:
                config_obj = Configuration()
            elif isinstance(self.config, dict) and 'configurable' in self.config:
                config_obj = Configuration.from_runnable_config(self.config)
            elif isinstance(self.config, dict):
                config_obj = Configuration.from_runnable_config({"configurable": self.config})
            else:
                config_obj = Configuration.from_runnable_config(self.config)
        except Exception as e:
            logger.warning(f"Failed to construct configuration for LLM parsing: {e}")
            return None

        prompt = """You are a FET sensor data query parser. Convert natural language queries into structured JSON format.

RULES FOR PARSING:

1. TARGET DETECTION - Identify the sensor target/analyte:
   - "phosphate", "PO4" → target: "phosphate"
   - "pH", "acidity" → target: "ph"
   - "glucose", "sugar" → target: "glucose"
   - "nitrate", "NO3" → target: "nitrate"
   - "potassium", "K+" → target: "potassium"

2. PERFORMANCE METRICS - Extract numerical constraints:
   - "Ion/Ioff", "on-off ratio" → filter: "ion_ioff_mean"
   - "SS", "subthreshold swing" → filter: "ss_mean" (units: mV/dec)
   - "VT", "threshold voltage" → filter: "vt_mean" (units: V)
   - "gm_max", "transconductance" → filter: "gm_max_mean" (units: μS or mS)
   - "drift" → filter: "vt_drift_per_cycle" (units: mV/cycle)

3. OPERATORS - Parse comparison operators:
   - "greater than", ">", "above" → operator: "$gt"
   - "less than", "<", "below" → operator: "$lt"
   - "around", "~", "approximately" → operator: "$eq" (with tolerance)

4. INTENT CLASSIFICATION:
   - Performance queries → intent: "performance_search"
   - Manufacturing/optimization → intent: "manufacturing_recommendations"
   - Drift/stability analysis → intent: "drift_analysis"
   - Comparison → intent: "comparison"
   - General → intent: "general_search"

5. VAGUE TERMS MAPPING:
   - "good performance" → ion_ioff_mean > 10000, ss_mean < 100
   - "stable" → vt_drift_per_cycle < 5, device_state: "stable"
   - "low drift" → vt_drift_per_cycle < 10
   - "high sensitivity" → gm_max_mean > 50

OUTPUT JSON FORMAT:
{
  "intent": "<intent_type>",
  "target": "<target_name or null>",
  "filters": {
    "<metric_field>": {"<operator>": <value>},
    ...
  },
  "required_views": ["metrics", "semantic"]
}

EXAMPLES:

Query: "Find me a good phosphate sensor"
Output: {
  "intent": "performance_search",
  "target": "phosphate",
  "filters": {
    "ion_ioff_mean": {"$gt": 10000},
    "ss_mean": {"$lt": 100}
  },
  "required_views": ["metrics", "semantic"]
}

Query: "Find a sensor with excellent performance"
Output: {
  "intent": "performance_search",
  "target": null,
  "filters": {
    "ion_ioff_mean": {"$gt": 10000},
    "ss_mean": {"$lt": 100}
  },
  "required_views": ["metrics", "semantic"]
}

Query: "Stable pH sensor with minimal drift"
Output: {
  "intent": "drift_analysis",
  "target": "ph",
  "filters": {
    "vt_drift_per_cycle": {"$lt": 5},
    "device_state": "stable"
  },
  "required_views": ["metrics", "semantic", "context"]
}

Now parse this query:"""

        try:
            result = invoke_with_failover(
                config_obj,
                [
                    SystemMessage(content=prompt),
                    HumanMessage(content=f"Query: {query}"),
                ],
                temperature=0,
                json_mode=True,
            )

            # Parse LLM response
            parsed = json.loads(result.content)

            # Convert to QueryPlan
            plan = QueryPlan(
                intent=parsed.get("intent", "general_search"),
                target=parsed.get("target"),
                filters=parsed.get("filters", {}),
                required_views=parsed.get("required_views", ["metrics", "semantic"]),
                k_folders=self.k_folders,
                k_runs_per_folder=self.k_runs_per_folder,
                k_non_excel=self.k_non_excel
            )

            # Adjust k values based on intent (same logic as rule-based)
            if plan.intent == "comparison":
                plan.k_folders = 12
            elif plan.intent == "drift_analysis":
                plan.k_runs_per_folder = 8

            logger.info(f"LLM parsed query - intent: {plan.intent}, target: {plan.target}, filters: {plan.filters}")
            return plan

        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}. Falling back to rule-based.")
            return None

    def _parse_query_rules(self, query: str) -> QueryPlan:
        """
        Original rule-based parsing logic.
        """
        query_lower = query.lower()

        # Initialize plan with defaults (using instance hyperparameters)
        plan = QueryPlan(
            intent="general_search",
            filters={},
            required_views=["metrics", "semantic"],
            k_folders=self.k_folders,
            k_runs_per_folder=self.k_runs_per_folder,
            k_non_excel=self.k_non_excel
        )

        # Detect target analyte
        targets = {
            "phosphate": ["phosphate", "po4"],
            "ph": ["ph", "acidity"],
            "glucose": ["glucose", "sugar"],
            "nitrate": ["nitrate", "no3"],
            "potassium": ["potassium", "k+"]
        }

        for target_name, keywords in targets.items():
            if any(kw in query_lower for kw in keywords):
                plan.target = target_name
                # Don't add target as a hard filter - it should be used for semantic search
                # plan.filters["target"] = target_name  # REMOVED: This breaks semantic view
                break

        # Detect numerical constraints (CORRECTED based on actual field names)
        if "ion/ioff" in query_lower or "ion_ioff" in query_lower:
            # Extract numerical threshold if present
            numbers = re.findall(r'\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b', query)
            if numbers:
                threshold = float(numbers[0])
                if threshold > 100:  # Likely Ion/Ioff value
                    # Use actual field name from vectorizer (lines 446-451 in excel_vectorizer.py)
                    plan.filters["ion_ioff_mean"] = {"$gt": threshold}

        # VT threshold detection
        if "vt" in query_lower:
            vt_match = re.search(r'vt\s*[<>]\s*([\d.]+)', query_lower)
            if vt_match:
                vt_value = float(vt_match.group(1))
                op = "$gt" if ">" in vt_match.group(0) else "$lt"
                plan.filters["vt_mean"] = {op: vt_value}

        # SS (subthreshold swing) detection
        if "ss" in query_lower or "subthreshold" in query_lower:
            ss_match = re.search(r'ss\s*[<>]\s*([\d.]+)', query_lower)
            if ss_match:
                ss_value = float(ss_match.group(1))
                op = "$gt" if ">" in ss_match.group(0) else "$lt"
                plan.filters["ss_mean"] = {op: ss_value}

        # Detect device state requirements
        if "stable" in query_lower:
            plan.filters["device_state"] = "stable"
        elif "degraded" in query_lower:
            plan.filters["device_state"] = "degraded"
        elif "burn" in query_lower:
            plan.filters["device_state"] = "burn_in"

        # Detect intent type
        if any(word in query_lower for word in ["manufactur", "recommend", "next step"]):
            plan.intent = "manufacturing_recommendations"
            plan.required_views.append("json")  # Need structured data for recommendations
        elif any(word in query_lower for word in ["compar", "versus", "vs"]):
            plan.intent = "comparison"
        elif any(word in query_lower for word in ["drift", "stability"]):
            plan.intent = "drift_analysis"
            plan.required_views.append("json")
        elif any(word in query_lower for word in ["progress", "timeline", "history"]):
            plan.intent = "temporal_analysis"

        # Adjust k values based on intent
        if plan.intent == "comparison":
            plan.k_folders = 12  # More folders for comparison
        elif plan.intent == "drift_analysis":
            plan.k_runs_per_folder = 8  # More runs for temporal analysis

        return plan

    def _retrieve_folders(self, original_query: str, query_plan: QueryPlan) -> List[FolderResult]:
        """
        Retrieve relevant folders using metadata filters and vector search.
        First use metadata filtering, then vector search
        Implements multi-view retrieval: metrics → semantic → context
        """
        # Build search query - combine target and intent
        search_terms = []
        if query_plan.target:
            search_terms.append(query_plan.target)
        if query_plan.intent == "drift_analysis":
            search_terms.append("drift stability temporal")
        elif query_plan.intent == "manufacturing_recommendations":
            search_terms.append("performance optimization manufacturing")

        search_query = " ".join(search_terms) if search_terms else "FET sensor"

        # Multi-view retrieval following Chinese plan priority
        all_results = []
        views_to_search = self.views_priority[:3]  # Search top 3 views: metrics, semantic, context

        for view in views_to_search:
            # Determine search query and filters based on view type
            if view == "semantic":
                # Semantic view: Use full original query for maximum context
                # Only basic structural filters, no content filters
                view_search_query = original_query  # Use complete original query!
                filter_conditions = [
                    {"level": {"$eq": "folder"}},
                    {"view": {"$eq": view}}
                ]
                # No target filter, no numerical filters for semantic view
                logger.info(f"Semantic view using full query: {view_search_query}")
            else:
                # Metrics/JSON views: Use structured search with filters
                view_search_query = search_query  # Use simplified target-based query
                filter_conditions = [
                    {"level": {"$eq": "folder"}},
                    {"view": {"$eq": view}}
                ]

                # Add target filter for structured views
                if query_plan.target:
                    filter_conditions.append({"target": {"$eq": query_plan.target}})

                # Add numerical and other filters for structured views
                if query_plan.filters:
                    for key, value in query_plan.filters.items():
                        if isinstance(value, dict):  # Range operators
                            for op, val in value.items():
                                filter_conditions.append({key: {op: val}})
                        else:
                            filter_conditions.append({key: {"$eq": value}})

            # Build final filter
            chroma_filter = {"$and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]

            logger.info(f"Searching {view} view with filter: {chroma_filter}")

            try:
                # Query this view with appropriate search query
                view_results = self.excel_vectorstore.similarity_search_with_score(
                    query=view_search_query,  # Different query for different views!
                    k=query_plan.k_folders,
                    filter=chroma_filter
                )
                all_results.extend(view_results)
                logger.info(f"Found {len(view_results)} results in {view} view")
            except Exception as e:
                logger.warning(f"Error searching {view} view: {e}")
                # Fallback: try with simpler filter
                try:
                    simple_filter = {"$and": [
                        {"level": {"$eq": "folder"}},
                        {"view": {"$eq": view}}
                    ]}
                    view_results = self.excel_vectorstore.similarity_search_with_score(
                        query=search_query,
                        k=query_plan.k_folders,
                        filter=simple_filter
                    )
                    all_results.extend(view_results)
                except Exception as e2:
                    logger.error(f"Fallback also failed for {view}: {e2}")

        # Merge and deduplicate results from different views
        if all_results:
            results = self._merge_multi_view_results(all_results, query_plan.k_folders)
        else:
            # Ultimate fallback: search without view filter
            logger.warning("No results from multi-view search, trying without view filter")
            results = self.excel_vectorstore.similarity_search_with_score(
                query=search_query,
                k=query_plan.k_folders * 2
            )

        # Extract and enrich folder data
        folders = []
        seen_folders = set()  # Deduplicate

        for doc, score in results:
            folder_id = doc.metadata.get("folder_id")

            # Skip if already seen (different views of same folder)
            if folder_id in seen_folders:
                continue
            seen_folders.add(folder_id)

            # Build FolderResult with actual field names from vectorizer
            folder_result = FolderResult(
                folder_id=folder_id,
                score=float(score),
                metrics={
                    # Use exact field names from excel_vectorizer.py lines 415-459
                    "vt_mean": doc.metadata.get("vt_mean"),
                    "vt_std": doc.metadata.get("vt_std"),
                    "vt_cv_percent": doc.metadata.get("vt_cv_percent"),
                    "ion_ioff_mean": doc.metadata.get("ion_ioff_mean"),
                    "ion_ioff_min": doc.metadata.get("ion_ioff_min"),
                    "ion_ioff_max": doc.metadata.get("ion_ioff_max"),
                    "ss_mean": doc.metadata.get("ss_mean"),
                    "ss_std": doc.metadata.get("ss_std"),
                    "vt_drift_per_run": doc.metadata.get("vt_drift_per_run"),
                    "health_score": doc.metadata.get("health_score", 100)
                },
                state=doc.metadata.get("device_state", "unknown"),
                drift_severity=doc.metadata.get("drift_severity"),
                target=doc.metadata.get("target"),
                content=doc.page_content[:500],  # Truncate for summary
                metadata=doc.metadata
            )

            # Extract LLM-generated recommendations if available (from generate_cards.py)
            if "next_experiment" in doc.metadata:
                folder_result.recommendations["next_experiment"] = doc.metadata["next_experiment"]
            if "recommended_focus" in doc.metadata:
                folder_result.recommendations["recommended_focus"] = doc.metadata["recommended_focus"]
            if "drift_pattern" in doc.metadata:
                folder_result.recommendations["drift_pattern"] = doc.metadata["drift_pattern"]

            folders.append(folder_result)

            # Stop when we have enough
            if len(folders) >= query_plan.k_folders:
                break

        logger.info(f"Retrieved {len(folders)} unique folders")
        return folders

    def _merge_multi_view_results(self, all_results: List[Tuple], k_folders: int) -> List[Tuple]:
        """
        Merge and deduplicate results from multiple views.
        Prioritize by: 1) folder uniqueness, 2) best score, 3) view priority
        Based on Chinese plan: views_priority = ["metrics","semantic","context"]
        """
        # Group by folder_id
        folder_groups = {}
        for doc, score in all_results:
            folder_id = doc.metadata.get("folder_id", doc.metadata.get("folder_path", ""))
            if folder_id not in folder_groups:
                folder_groups[folder_id] = []
            folder_groups[folder_id].append((doc, score, doc.metadata.get("view", "unknown")))

        # For each folder, pick the best representation
        merged_results = []
        view_priority = {"metrics": 0, "semantic": 1, "json": 2, "context": 3, "table": 4}

        for folder_id, folder_docs in folder_groups.items():
            # Sort by score (lower is better) and view priority
            folder_docs.sort(key=lambda x: (x[1], view_priority.get(x[2], 5)))
            best_doc, best_score, best_view = folder_docs[0]

            # Merge metadata from different views if available
            merged_metadata = best_doc.metadata.copy()
            for doc, _, view in folder_docs:
                if view != best_view:
                    # Enrich with additional metadata from other views
                    for key, value in doc.metadata.items():
                        if key not in merged_metadata and value is not None:
                            merged_metadata[key] = value

            # Create merged document with enriched metadata
            best_doc.metadata = merged_metadata
            merged_results.append((best_doc, best_score))

        # Sort by score and return top k
        merged_results.sort(key=lambda x: x[1])
        return merged_results[:k_folders]

    def _analyze_runs(self, folders: List[FolderResult], query_plan: QueryPlan) -> Dict[str, List[Dict]]:
        """
        Deep dive into individual runs for selected folders.
        Pre-filter and temporal sampling strategy
        """
        run_results = {}

        # Analyze top folders in detail (limit to top 3-5 for performance)
        folders_to_analyze = folders[:min(5, len(folders))]

        for folder in folders_to_analyze:
            folder_id = folder.folder_id

            # Build run filter using Chroma's $and syntax
            filter_conditions = [
                {"level": "run"},
                {"parent_id": f"excel/{folder_id}"},
                {"view": "metrics"}
            ]

            # Add quality filter
            if "health_score" in query_plan.filters:
                filter_conditions.append({"health_score": query_plan.filters["health_score"]})
            else:
                filter_conditions.append({"health_score": {"$gte": query_plan.min_health_score}})

            run_filter = {"$and": filter_conditions}

            # Query runs for this folder
            try:
                runs = self.excel_vectorstore.similarity_search(
                    query=f"runs for {folder_id}",
                    k=query_plan.k_runs_per_folder * 3,  # Get extra for temporal sampling
                    filter=run_filter
                )
            except Exception as e:
                logger.warning(f"Error retrieving runs for {folder_id}: {e}")
                continue

            # Temporal sampling: get early, middle, late runs
            folder_runs = self._temporal_sampling(runs, query_plan.k_runs_per_folder)

            # Extract run data with actual field names
            processed_runs = []
            for run_doc in folder_runs:
                run_data = {
                    "run_id": run_doc.metadata.get("run_id"),
                    "sheet": run_doc.metadata.get("original_sheet"),
                    "metrics": {
                        # Individual run metrics (from run_*_retrieval.txt parsing)
                        "vt": run_doc.metadata.get("vt"),
                        "ion": run_doc.metadata.get("ion"),
                        "ioff": run_doc.metadata.get("ioff"),
                        "ion_ioff": run_doc.metadata.get("ion_ioff"),
                        "ss_mv_dec": run_doc.metadata.get("ss_mv_dec"),
                        "ss_r2": run_doc.metadata.get("ss_r2"),
                        "gm_max": run_doc.metadata.get("gm_max"),
                        "hysteresis_V": run_doc.metadata.get("hysteresis_V"),
                        "drift_percent_hour": run_doc.metadata.get("drift_percent_hour")
                    },
                    "health_score": run_doc.metadata.get("health_score", 100),
                    "temporal_position": run_doc.metadata.get("sheet_number", 0),  # For timeline
                    "source": run_doc.metadata.get("source"),
                    "content_preview": run_doc.page_content[:200]
                }
                processed_runs.append(run_data)

            run_results[folder_id] = processed_runs
            logger.info(f"Analyzed {len(processed_runs)} runs for folder {folder_id}")

        return run_results

    def _temporal_sampling(self, runs: List, k: int) -> List:
        """
        Sample runs from early/middle/late periods for temporal diversity.
        Ensure trend visualization
        """
        if len(runs) <= k:
            return runs

        # Sort by temporal position (sheet number or run number)
        sorted_runs = sorted(runs, key=lambda r: r.metadata.get("sheet_number", 0))

        # Divide into periods and sample
        sampled = []
        period_size = len(sorted_runs) // k

        for i in range(k):
            start_idx = i * period_size
            end_idx = start_idx + period_size if i < k - 1 else len(sorted_runs)
            period_runs = sorted_runs[start_idx:end_idx]

            if period_runs:
                # Take the best from each period (highest health score)
                best_run = max(period_runs, key=lambda r: r.metadata.get("health_score", 0))
                sampled.append(best_run)

        return sampled

    def _get_context_documents(self, query: str, query_plan: QueryPlan) -> List[Dict]:
        """
        Retrieve relevant non-Excel documents for context.
        Supplement with non-Excel documents
        """
        if not self.non_excel_vectorstore:
            return []

        # Build context query based on intent
        context_terms = []
        if query_plan.target:
            context_terms.append(f"{query_plan.target} detection protocol")
        if query_plan.intent == "manufacturing_recommendations":
            context_terms.append("fabrication process optimization")
        elif query_plan.intent == "drift_analysis":
            context_terms.append("stability measurement protocols")

        context_query = " ".join(context_terms) if context_terms else query

        # Query non-Excel vectorstore
        try:
            context_docs = self.non_excel_vectorstore.similarity_search(
                query=context_query,
                k=query_plan.k_non_excel
            )
        except Exception as e:
            logger.warning(f"Error retrieving context documents: {e}")
            return []

        # Format results
        formatted_docs = []
        for doc in context_docs:
            formatted_docs.append({
                "source": doc.metadata.get("source"),
                "type": doc.metadata.get("file_type", "document"),
                "content": doc.page_content[:500],  # Truncate for summary
                "metadata": doc.metadata
            })

        return formatted_docs

    def _generate_recommendations(self, folders: List[FolderResult], runs: Dict) -> Dict[str, List[str]]:
        """
        Generate manufacturing recommendations based on metrics.
        Use structured labels first, then simple heuristics
        Priority: 1) LLM keywords, 2) Heuristic rules, 3) Cross-folder patterns
        """
        recommendations = {
            "immediate": [],  # Immediate actions
            "experimental": [],  # Needs experiments
            "risk_mitigation": []  # Risk points
        }

        # Step 1: Extract existing LLM-generated recommendations (from generate_cards.py)
        for folder in folders:
            if folder.recommendations:
                if "next_experiment" in folder.recommendations:
                    recommendations["experimental"].append(
                        f"[{folder.folder_id}] {folder.recommendations['next_experiment']}"
                    )
                if "recommended_focus" in folder.recommendations:
                    recommendations["immediate"].append(
                        f"[{folder.folder_id}] {folder.recommendations['recommended_focus']}"
                    )
                if "drift_pattern" in folder.recommendations:
                    drift_info = folder.recommendations["drift_pattern"]
                    if "significant" in drift_info.lower() or "high" in drift_info.lower():
                        recommendations["risk_mitigation"].append(
                            f"[{folder.folder_id}] Drift issue: {drift_info}"
                        )

        # Step 2: Apply heuristic rules based on aggregated metrics
        # Aggregate metrics across folders
        all_metrics = {}
        metric_keys = ["vt_mean", "ion_ioff_mean", "ss_mean", "vt_drift_per_run"]

        for key in metric_keys:
            values = [f.metrics.get(key) for f in folders if f.metrics.get(key) is not None]
            if values:
                all_metrics[f"{key}_avg"] = np.mean(values)
                all_metrics[f"{key}_std"] = np.std(values)
                all_metrics[f"{key}_min"] = np.min(values)
                all_metrics[f"{key}_max"] = np.max(values)

        # Apply rules from Chinese plan
        for rule_name, rule in self.manufacturing_rules.items():
            if rule["condition"](all_metrics):
                category = rule.get("category", "experimental")
                recommendations[category].append(rule["recommendation"])

        # Step 3: Analyze run-level patterns for additional insights
        if runs:
            run_insights = self._analyze_run_patterns(runs)
            for insight in run_insights:
                recommendations[insight["category"]].append(insight["message"])

        # Step 4: Deduplicate and prioritize
        for category in recommendations:
            # Remove duplicates while preserving order
            seen = set()
            unique = []
            for rec in recommendations[category]:
                if rec not in seen:
                    seen.add(rec)
                    unique.append(rec)
            recommendations[category] = unique[:5]  # Limit to top 5 per category

        return recommendations

    def _analyze_run_patterns(self, runs: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Analyze patterns across runs for additional insights.
        """
        insights = []

        for folder_id, folder_runs in runs.items():
            if not folder_runs:
                continue

            # Check for temporal degradation
            temporal_positions = [r["temporal_position"] for r in folder_runs]
            ion_ioff_values = [r["metrics"].get("ion_ioff") for r in folder_runs
                             if r["metrics"].get("ion_ioff") is not None]

            if len(ion_ioff_values) >= 3:
                # Check if performance degrades over time
                if temporal_positions[0] < temporal_positions[-1]:  # Ensure temporal order
                    if ion_ioff_values[0] > ion_ioff_values[-1] * 1.5:  # 50% degradation
                        insights.append({
                            "category": "risk_mitigation",
                            "message": f"[{folder_id}] Significant performance degradation over time (Ion/Ioff dropped {(1 - ion_ioff_values[-1]/ion_ioff_values[0])*100:.1f}%)"
                        })

            # Check for high variability
            if len(ion_ioff_values) >= 2:
                cv = np.std(ion_ioff_values) / np.mean(ion_ioff_values) if np.mean(ion_ioff_values) > 0 else 0
                if cv > 0.3:  # CV > 30%
                    insights.append({
                        "category": "immediate",
                        "message": f"[{folder_id}] High variability in Ion/Ioff (CV={cv:.1%}), consider process control improvements"
                    })

        return insights

    def _initialize_manufacturing_rules(self) -> Dict[str, Dict]:
        """
        Initialize heuristic rules for manufacturing recommendations.
        Heuristic rules engine (no LLM needed)
        """
        return {
            "high_SS": {
                "condition": lambda m: m.get("ss_mean_avg", 0) > 200,
                "recommendation": "SS > 200 mV/dec: Reduce interface traps - optimize gate dielectric deposition, consider surface passivation",
                "category": "experimental"
            },
            "low_ion_ioff": {
                "condition": lambda m: m.get("ion_ioff_mean_avg", float('inf')) < 1e4,
                "recommendation": "Ion/Ioff < 10^4: Enhance channel conductivity - optimize doping concentration, improve contact resistance",
                "category": "experimental"
            },
            "high_vt_drift": {
                "condition": lambda m: abs(m.get("vt_drift_per_run_avg", 0)) > 0.001,
                "recommendation": "VT drift > 1 mV/run: Improve stability - extended burn-in cycles, investigate bias stress effects",
                "category": "risk_mitigation"
            },
            "high_vt_variability": {
                "condition": lambda m: m.get("vt_mean_std", 0) > 0.1,
                "recommendation": "High VT variability (std > 0.1V): Improve process uniformity, check fabrication consistency",
                "category": "immediate"
            },
            "excellent_performance": {
                "condition": lambda m: m.get("ion_ioff_mean_avg", 0) > 1e6 and m.get("ss_mean_avg", float('inf')) < 100,
                "recommendation": "Excellent performance achieved (Ion/Ioff > 10^6, SS < 100 mV/dec): Document process parameters for reproducibility",
                "category": "immediate"
            },
            "optimize_ss_priority": {
                "condition": lambda m: m.get("ss_mean_avg", 0) > 150 and m.get("ion_ioff_mean_avg", 0) > 1e4,
                "recommendation": "SS is limiting factor (>150 mV/dec with good Ion/Ioff): Focus on gate stack optimization",
                "category": "experimental"
            }
        }

    def _format_output(self, **kwargs) -> Dict[str, Any]:
        """
        Format the final output for the deep research agent.
        Compatible with existing local RAG interface.
        """
        query = kwargs.get("query", "")
        query_plan = kwargs.get("query_plan")
        folders = kwargs.get("folders", [])
        runs = kwargs.get("runs", {})
        context = kwargs.get("context", [])
        recommendations = kwargs.get("recommendations", {})

        # Convert to format expected by deep research agent
        results = []

        # Add folder summaries as primary results
        for i, folder in enumerate(folders[:10]):  # Limit to top 10
            # Create a comprehensive summary for each folder
            summary_parts = []

            # Add metrics summary
            if folder.metrics:
                metrics_text = self._format_metrics(folder.metrics)
                if metrics_text:
                    summary_parts.append(metrics_text)

            # Add device state and drift info
            if folder.state and folder.state != "unknown":
                summary_parts.append(f"Device State: {folder.state}")
            if folder.drift_severity:
                summary_parts.append(f"Drift Severity: {folder.drift_severity}")

            # Add content preview
            summary_parts.append(folder.content)

            # Add source path information to the content
            source_info = f"[Source Path: {folder.folder_id}]"

            result = {
                "title": f"FET Dataset: {folder.folder_id}",
                "url": f"local://excel/{folder.folder_id}",
                "snippet": " | ".join(summary_parts[:3]),  # Brief snippet
                "raw_content": f"{source_info}\n\n" + "\n\n".join(summary_parts),  # Full content with source
                "metadata": {
                    "source_type": "fet_data",
                    "folder_id": folder.folder_id,
                    "source_path": folder.folder_id,  # Explicitly add source path
                    "relevance_score": folder.score,
                    "target": folder.target,
                    **folder.metrics  # Include all metrics in metadata
                }
            }
            results.append(result)

        # Add run details for top folders
        if runs:
            for folder_id, folder_runs in list(runs.items())[:3]:  # Top 3 folders
                if folder_runs:
                    run_summary = self._format_run_table(folder_runs)
                    source_info = f"[Source Path: {folder_id}/runs]"
                    results.append({
                        "title": f"Run Analysis: {folder_id}",
                        "url": f"local://excel/{folder_id}/runs",
                        "snippet": f"Detailed analysis of {len(folder_runs)} runs",
                        "raw_content": f"{source_info}\n\n{run_summary}",
                        "metadata": {
                            "source_type": "fet_runs",
                            "folder_id": folder_id,
                            "source_path": f"{folder_id}/runs",  # Add source path
                            "run_count": len(folder_runs)
                        }
                    })

        # Add context documents (non-Excel documents)
        for doc in context:
            source_path = doc.get("source", "unknown")
            source_info = f"[Source Path: {source_path}]"
            results.append({
                "title": doc.get("source", "Context Document"),
                "url": f"file://{source_path}" if source_path != "unknown" else f"local://docs/unknown",
                "snippet": doc.get("content", "")[:200],
                "raw_content": f"{source_info}\n\n{doc.get('content', '')}",
                "metadata": {
                    **doc.get("metadata", {}),
                    "source_path": source_path  # Ensure source path is in metadata
                }
            })

        # Add recommendations as a special high-priority result
        if any(recommendations.values()):
            rec_text = self._format_recommendations(recommendations)
            results.insert(0, {  # Insert at beginning for visibility
                "title": "Manufacturing Recommendations & Insights",
                "url": "local://recommendations",
                "snippet": f"Generated {sum(len(v) for v in recommendations.values())} recommendations based on FET sensor analysis",
                "raw_content": rec_text,
                "metadata": {
                    "source_type": "recommendations",
                    "query_intent": query_plan.intent if query_plan else "unknown",
                    "recommendation_count": sum(len(v) for v in recommendations.values())
                }
            })

        # Add metrics summary
        metrics_summary = self._generate_metrics_summary(folders)
        if metrics_summary:
            results.insert(1, {
                "title": "FET Performance Metrics Summary",
                "url": "local://metrics_summary",
                "snippet": "Aggregated statistics across all analyzed datasets",
                "raw_content": self._format_metrics_summary(metrics_summary),
                "metadata": {
                    "source_type": "metrics_summary",
                    **metrics_summary
                }
            })

        # Collect folder IDs with Globus URLs
        folder_sources = []
        for folder in folders[:10]:  # Same folders we added to results
            globus_url = self._generate_globus_url(folder.folder_id)
            folder_sources.append({
                "folder_id": folder.folder_id,
                "url": globus_url,
                "target": folder.target,
                "score": folder.score
            })

        return {
            "results": results,
            "source": "advanced_fet_rag",
            "query_plan": {
                "intent": query_plan.intent if query_plan else "unknown",
                "target": query_plan.target if query_plan else None,
                "filters": query_plan.filters if query_plan else {}
            },
            "stats": {
                "folders_analyzed": len(folders),
                "runs_analyzed": sum(len(r) for r in runs.values()),
                "context_docs": len(context),
                "recommendations": sum(len(v) for v in recommendations.values())
            },
            "folder_sources": folder_sources  # Add this for source tracking
        }

    def _generate_globus_url(self, folder_id: str) -> str:
        """
        Generate Globus file manager URL for a given folder ID.

        Args:
            folder_id: Folder ID in format like "Thrust 3__Data from Hyun-June__..."

        Returns:
            Globus URL for the folder
        """
        # Base Globus configuration
        GLOBUS_ORIGIN_ID = "af7bda53-6d04-11e5-ba46-22000b92c6ec"
        GLOBUS_BASE_PATH = "/project2/chenyuxin/2025MADEPUBLICsnapshot"

        # Convert folder_id to path format
        # Replace double underscores with single forward slash
        path_parts = folder_id.split("__")

        # For FET Excel data, we need to keep the numeric folder (like /1 or /2)
        # but remove the final run identifier (like 1mg, di_4, etc.)
        if len(path_parts) >= 2:
            last_part = path_parts[-1]
            second_last = path_parts[-2] if len(path_parts) > 1 else ""

            # Check if this looks like FET data with pattern: .../__number__identifier
            # e.g., "1__di_4" or "2__1mg"
            if second_last.isdigit():
                # Keep the number folder, remove only the last identifier
                # e.g., keep "1" but remove "di_4" or "1mg"
                path_parts = path_parts[:-1]
            elif last_part.isdigit():
                # If the last part is just a number, keep it (it's the folder we want)
                pass
            elif len(last_part) <= 10 and ('mg' in last_part or 'pg' in last_part or 'di' in last_part):
                # Remove run identifiers that aren't preceded by a number folder
                path_parts = path_parts[:-1]

        # For Globus, we need to use + for spaces and properly encode special characters
        # Build the path manually with proper encoding
        encoded_parts = []
        for part in path_parts:
            # Replace spaces with + for Globus
            encoded_part = part.replace(' ', '+')
            # Handle special characters (but keep + as is)
            # Only encode parentheses and other special chars
            encoded_part = encoded_part.replace('(', '%28').replace(')', '%29')
            encoded_parts.append(encoded_part)

        # Join the parts with %2F (encoded forward slash)
        encoded_path = "%2F".join(encoded_parts)

        # Construct full Globus URL
        globus_url = f"https://app.globus.org/file-manager?origin_id={GLOBUS_ORIGIN_ID}&origin_path=%2Fproject2%2Fchenyuxin%2F2025MADEPUBLICsnapshot%2F{encoded_path}"

        return globus_url

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics dictionary into readable text."""
        parts = []

        # Format key metrics with proper units
        if metrics.get("vt_mean") is not None:
            parts.append(f"VT: {metrics['vt_mean']:.3f}V")
            if metrics.get("vt_std") is not None:
                parts.append(f"(±{metrics['vt_std']:.3f}V)")

        if metrics.get("ion_ioff_mean") is not None:
            parts.append(f"Ion/Ioff: {metrics['ion_ioff_mean']:.1e}")
            if metrics.get("ion_ioff_min") is not None and metrics.get("ion_ioff_max") is not None:
                parts.append(f"[{metrics['ion_ioff_min']:.1e}-{metrics['ion_ioff_max']:.1e}]")

        if metrics.get("ss_mean") is not None:
            parts.append(f"SS: {metrics['ss_mean']:.1f} mV/dec")
            if metrics.get("ss_std") is not None:
                parts.append(f"(±{metrics['ss_std']:.1f})")

        if metrics.get("vt_drift_per_run") is not None:
            parts.append(f"VT drift: {metrics['vt_drift_per_run']*1000:.2f} mV/run")

        return " ".join(parts)

    def _format_run_table(self, runs: List[Dict]) -> str:
        """Format run data as a readable table."""
        if not runs:
            return "No run data available"

        lines = ["Run Analysis Table:", "-" * 80]

        # Header
        lines.append("Run ID | Sheet | VT(V) | Ion/Ioff | SS(mV/dec) | Health | Temporal")
        lines.append("-" * 80)

        # Data rows
        for run in runs:
            run_id = run.get("run_id", "unknown")[:15]
            sheet = run.get("sheet", "-")[:10]

            metrics = run.get("metrics", {})
            vt = f"{metrics.get('vt', 0):.3f}" if metrics.get('vt') is not None else "-"
            ion_ioff = f"{metrics.get('ion_ioff', 0):.1e}" if metrics.get('ion_ioff') is not None else "-"
            ss = f"{metrics.get('ss_mv_dec', 0):.1f}" if metrics.get('ss_mv_dec') is not None else "-"

            health = run.get("health_score", "-")
            temporal = run.get("temporal_position", "-")

            lines.append(f"{run_id:15} | {sheet:10} | {vt:5} | {ion_ioff:9} | {ss:10} | {health:6} | {temporal}")

        return "\n".join(lines)

    def _format_recommendations(self, recommendations: Dict[str, List[str]]) -> str:
        """Format recommendations as structured text."""
        if not any(recommendations.values()):
            return "No specific recommendations generated."

        text = "MANUFACTURING RECOMMENDATIONS & INSIGHTS\n" + "=" * 50 + "\n\n"

        if recommendations.get("immediate"):
            text += "IMMEDIATE ACTIONS:\n"
            for i, rec in enumerate(recommendations["immediate"], 1):
                text += f"  {i}. {rec}\n"
            text += "\n"

        if recommendations.get("experimental"):
            text += "EXPERIMENTAL IMPROVEMENTS:\n"
            for i, rec in enumerate(recommendations["experimental"], 1):
                text += f"  {i}. {rec}\n"
            text += "\n"

        if recommendations.get("risk_mitigation"):
            text += "RISK MITIGATION:\n"
            for i, rec in enumerate(recommendations["risk_mitigation"], 1):
                text += f"  ⚠️ {i}. {rec}\n"
            text += "\n"

        return text

    def _generate_metrics_summary(self, folders: List[FolderResult]) -> Dict[str, Any]:
        """Generate summary statistics across all folders."""
        if not folders:
            return {}

        summary = {}

        # Aggregate key metrics
        metric_keys = ["vt_mean", "ion_ioff_mean", "ss_mean", "vt_drift_per_run"]

        for key in metric_keys:
            values = [f.metrics.get(key) for f in folders if f.metrics.get(key) is not None]
            if values:
                summary[key] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "count": len(values)
                }

        # Count device states
        state_counts = defaultdict(int)
        for folder in folders:
            state_counts[folder.state] += 1
        summary["device_states"] = dict(state_counts)

        # Count targets
        target_counts = defaultdict(int)
        for folder in folders:
            if folder.target:
                target_counts[folder.target] += 1
        summary["targets"] = dict(target_counts)

        return summary

    def _format_metrics_summary(self, summary: Dict) -> str:
        """Format metrics summary as readable text."""
        lines = ["AGGREGATED FET SENSOR PERFORMANCE METRICS", "=" * 50, ""]

        # Format each metric
        metric_names = {
            "vt_mean": "Threshold Voltage (VT)",
            "ion_ioff_mean": "Ion/Ioff Ratio",
            "ss_mean": "Subthreshold Swing (SS)",
            "vt_drift_per_run": "VT Drift Rate"
        }

        for key, name in metric_names.items():
            if key in summary and isinstance(summary[key], dict):
                stats = summary[key]
                lines.append(f"{name}:")
                lines.append(f"  Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
                lines.append(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
                lines.append(f"  Samples: {stats['count']}")
                lines.append("")

        # Device states
        if "device_states" in summary:
            lines.append("Device State Distribution:")
            for state, count in summary["device_states"].items():
                lines.append(f"  {state}: {count} datasets")
            lines.append("")

        # Targets
        if "targets" in summary:
            lines.append("Detection Targets:")
            for target, count in summary["targets"].items():
                lines.append(f"  {target}: {count} datasets")

        return "\n".join(lines)
