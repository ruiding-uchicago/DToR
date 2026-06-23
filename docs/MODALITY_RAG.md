# Modality Retrieval & RAG

The Local Deep Researcher agent can consult local knowledge sources before (or alongside) web search. Each modality is controlled through `Configuration` flags so you can enable only the stores that exist on a workstation.

## Configuration Summary

| Flag | Purpose | Default |
|------|---------|---------|
| `USE_LOCAL_RAG` | Master switch for local retrieval | `True` |
| `ENABLE_FET_RAW_DATA` | Hierarchical FET sensor data (Excel + unstructured) | `False` |
| `ENABLE_CODE_RETRIEVAL` | Source-code vector store | `False` |
| `ENABLE_PAPER_RETRIEVAL` | Academic papers vector store | `False` |
| `VECTOR_STORE_PATHS` | Legacy fallback for arbitrary Chroma stores | `None` |
| `EMBEDDING_MODEL` | Embeddings for local stores (`BAAI/bge-m3`) | `"BAAI/bge-m3"` |

When `USE_LOCAL_RAG` is true the `local_rag_research` node will call the relevant retrievers and label their outputs. Results are merged into a single comprehensive block so downstream summary nodes treat them as the first “modality” in each iteration.

## FET Sensor Data (Advanced RAG)

Enabling `ENABLE_FET_RAW_DATA` activates `advanced_fet_rag.FETSensorRAG`, a hierarchical retrieval pipeline tailored to electrochemical FET devices.

### Data Stores
1. **Excel vector store**: 5-view architecture (`metrics`, `semantic`, `json`, `context`, `table`) covering device folders and measurement runs.
2. **Non-Excel vector store** (optional): PDFs, notebooks, SOPs, and reports that complement the spreadsheets.

### Query Flow
1. **Intent parsing** – rule/LLM hybrid classifies the query into intents such as `sensor_analysis`, `manufacturing_recommendations`, `comparison`, or `drift_analysis`, detects target analytes, and extracts numeric thresholds (Ion/Ioff, SS, VT).
2. **Folder retrieval** – multi-view search with metadata filters (target, device state, thresholds). Results are deduplicated per folder, merging metadata from multiple views.
3. **Run analysis** – for top folders it samples runs across the timeline, extracts per-run metrics, and prepares tabular summaries.
4. **Context documents** – optional non-Excel retrieval seeded by intent (e.g., fabrication process optimisation, stability protocols).
5. **Manufacturing recommendations** – heuristic rule engine evaluates aggregated metrics and emits immediate actions, experimental improvements, or risk mitigation guidance.
6. **Output formatting** – returns results shaped like web search entries with explicit modality labels, Globus URL construction (`local://excel/<folder>` plus `app.globus.org` link), and metadata for source deduplication.

Rule heuristics include patterns such as:
- `SS > 200 mV/dec` ⟶ recommend dielectric passivation or gate-stack optimisation.
- `Ion/Ioff < 10^4` ⟶ highlight channel conductivity/contact resistance improvements.
- `|VT drift| > 1 mV/run` ⟶ suggest extended burn-in or bias-stress diagnostics.
- `VT std > 0.1 V` ⟶ flag process uniformity checks.
- `Ion/Ioff > 10^6` and `SS < 100 mV/dec` ⟶ prompt documentation of best-performing process parameters.

### Downstream Usage
- `summarize_local_rag_results` and FET-specific prompts (`fet_prompts.py`) recognise the labelled content and produce targeted summaries.
- `generate_complementary_query`, `reflect_on_summary`, and `finalize_summary` swap to FET prompts when the query or retrieved data includes FET indicators.
- When FET mode is enabled, `finalize_summary` makes a second LLM call to generate remote printing parameters (inkjet settings, anneal temperatures, surface functionalisation) using handbook context embedded in the prompt.

## Code Retrieval

When `ENABLE_CODE_RETRIEVAL` is true:
- `Configuration.code_vector_path` points to a directory containing one or more Chroma volumes (`vol_*`).
- `utils.find_volume_paths` discovers all volumes; each is queried through `query_local_vector_store` with `code_results_count` as the limit.
- Results include source paths in metadata so final reports can reference specific files.

Typical use cases: grounding research in existing repos, pairing with the code-improvement workflow, or surfacing implementation examples that complement web findings.

## Academic Papers

`ENABLE_PAPER_RETRIEVAL` works similarly:
- `paper_vector_path` (with optional `vol_*` subdirectories) serves as the persistence root.
- `paper_results_count` controls the number of chunks per iteration.
- Outputs are labelled “Academic Papers” to distinguish them from web results.

## Legacy Vector Stores

For backward compatibility, `VECTOR_STORE_PATHS` accepts a comma-separated list of directories. Each directory is scanned for `vol_*` subfolders; if none are present the directory itself is queried as a single Chroma DB. These results are labelled “Legacy Documents.”

## Result Integration

`local_rag_research` consolidates all enabled modalities into one list item per iteration:
```
=== MODALITY: FET Sensor Experimental Data ===
... raw content and run analysis ...

=== MODALITY: Code Repository ===
... retrieved snippets ...

=== MODALITY: Academic Papers ===
... literature extracts ...
```

The corresponding source entries (Globus links, local file paths, web URLs) are collected in `local_sources_gathered` so `finalize_summary` can de-duplicate them and segment the “Sources” section into web, FET, code, papers, and other categories.

## Troubleshooting
- Ensure all vector stores were generated with the same embedding model as `EMBEDDING_MODEL` (default `BAAI/bge-m3`). A mismatch results in poor recall or empty results.
- Large Chroma stores may exhaust file descriptors; `_query_simple_stores` proactively raises `RLIMIT_NOFILE` when it detects >50 stores but you may still need to increase OS limits.
- For FET stores, keep an eye on globus catalogue paths and update `advanced_fet_rag._generate_globus_url` if directory structures change.

Refer back to `docs/RESEARCH_WORKFLOWS.md` for how these modalities are invoked within the research loop.

## FET RAG Operations

### Quickstart
1. Copy the FET-ready environment template: `cp .env.fet_rag .env`.
2. Start LangGraph (for example `uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev`).
3. In LangGraph Studio select `ollama_deep_researcher` (single) or `deep_researcher_dtor` (DToR).
4. Check logs for messages such as “Using advanced FET sensor RAG system” to confirm the modality is active.

> **Tip:** Large Excel stores can require many file handles—raise the open-file limit before launching (`ulimit -n 1048575` on macOS/Linux).

### Query Cookbook (English)
- **Performance Filtering**
  - `Find FET sensors with Ion/Ioff ratio > 100000 and SS < 100 mV/dec`
  - `Show phosphate sensors with VT < 0.5V and stable performance`
  - `List all devices with health score > 80 and minimal drift`
- **Target Specific**
  - `pH sensitive FET sensors with Ion/Ioff > 10000`
  - `Glucose FET biosensors with detection limit below 1 mM`
  - `Potassium ion selective FET sensors for agricultural soil monitoring`
- **Manufacturing Optimisation**
  - `Manufacturing recommendations to reduce subthreshold swing in CNT-based FET sensors`
  - `Process optimization for reducing VT drift in HEPES buffer`
- **Drift & Stability**
  - `Analyze VT drift patterns in Device 8 CNC experiments`
  - `FET sensors operating with VT drift less than 5% over 100 cycles`
- **Comparative Studies**
  - `Compare graphene vs CNT performance in phosphate detection FET sensors`
  - `Contrast Device 7 EC vs Device 8 CNC sensor characteristics`
- **Application Focus**
  - `FET biosensors for real-time dopamine detection in neural interfaces`
  - `Heavy metal detection using FET sensors with ppb level sensitivity`

### Additional Query Ideas
- **Performance Screening**
  - `Find FET sensors with Ion/Ioff ratio > 1000000 and SS < 100 mV/dec`
  - `Show phosphate sensors with VT drift < 5% per hour`
- **Manufacturing Optimisation**
  - `What manufacturing steps reduce SS in CNC graphene FET devices?`
  - `Process optimization for reducing VT drift in HEPES buffer`
- **Drift Analysis**
  - `Analyze VT drift patterns in Device 8 CNC experiments`
  - `Compare drift behavior between burn-in and stable phases`
- **Comparative Analysis**
  - `Compare HEPES buffer vs DI water performance for bio-graphene`
  - `Differences between 1mg/mL and 10mg/mL concentration results`
- **Composite Exploration**
  - `Find stable phosphate sensors with Ion/Ioff > 50000 and provide manufacturing insights`
  - `Which experiments show both high sensitivity and low drift for glucose detection?`

### Data Flow (Plain-Language Analogy)
Think of the FET retrieval pipeline as navigating a supermarket:

1. **Clarify the request** – parse the query, extract targets, and capture performance thresholds.
2. **Find the aisle** – run multi-view folder retrieval to identify the most relevant experimental folders.
3. **Pick the items** – sample runs over time to capture per-measurement metrics (Ion/Ioff, SS, VT drift, etc.).
4. **Read the label** – add non-Excel context (reports, SOPs, notebooks) to understand experimental conditions.
5. **Get advice** – apply the rules engine to output manufacturing recommendations, quick wins, and risk alerts.

This hierarchy delivers both breadth (finding the right experiments) and depth (analysing specific runs and fabrication guidance).
