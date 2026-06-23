"""
FET-specific prompts for the deep research graph.
These prompts are conditionally used when FET sensor queries are detected.
"""

FET_SUMMARY_PROMPT = """<GOAL>
You are analyzing FET (Field-Effect Transistor) sensor experimental data.
Create a comprehensive summary focusing on device performance metrics and trends.
</GOAL>

<RESEARCH_TOPIC>
{research_topic}
</RESEARCH_TOPIC>

<LOCAL_RAG_RESULTS>
{local_rag_result}
</LOCAL_RAG_RESULTS>

Please provide a structured analysis focusing on:

1. **Performance Metrics**:
   - Ion/Ioff ratio (target: >10^4, excellent: >10^5)
   - Subthreshold swing SS (target: <100 mV/dec)
   - Threshold voltage VT and stability
   - Transconductance gm_max
   - Health scores and quality indicators

2. **Device Characteristics**:
   - Target analyte (phosphate, pH, glucose, etc.)
   - Device configuration (Device 7 EC, Device 8 CNC, etc.)
   - Buffer/solution conditions
   - Concentration ranges tested

3. **Temporal Stability**:
   - VT drift patterns (mV/cycle or mV/hour)
   - Degradation indicators
   - Burn-in vs stable phase behavior
   - Cycle-to-cycle reproducibility

4. **Key Observations**:
   - Best performing folders/devices
   - Anomalies or concerning trends
   - Cross-folder patterns

5. **Data Quality**:
   - Number of folders analyzed
   - Number of runs per folder
   - Completeness of metrics

Format as structured sections. Use scientific notation where appropriate."""

FET_REFLECTION_PROMPT = """Reflect on the completeness and quality of this FET sensor analysis.

SUMMARY SO FAR:
{running_summary}

ORIGINAL TOPIC:
{research_topic}

Please evaluate:

1. **Metrics Coverage**:
   - Are all key FET metrics analyzed (Ion/Ioff, SS, VT, gm_max)?
   - Are performance values within expected ranges?
   - Any missing critical parameters?

2. **Statistical Significance**:
   - Sufficient data points for conclusions?
   - Are trends statistically meaningful?
   - Need more runs or folders?

3. **Manufacturing Insights**:
   - Clear correlations between process and performance?
   - Optimization pathways identified?
   - What experiments would validate hypotheses?

4. **Stability Analysis**:
   - Is temporal drift adequately characterized?
   - Are degradation mechanisms identified?
   - Need longer-term data?

5. **Missing Information**:
   - What additional FET data would strengthen conclusions?
   - Should we search for fabrication process literature?
   - Are there unexplored parameter spaces?

Based on this reflection:
- If analysis is comprehensive, suggest finalizing
- If local FET data gaps exist, identify specific folders/parameters needed
- If external literature would help, suggest specific search topics

Provide a brief reflection focusing on what's missing or could be improved."""

FET_COMPLEMENTARY_QUERY_PROMPT = """Generate a complementary search query for FET sensor research.

ORIGINAL QUERY: {search_query}
CURRENT FINDINGS SUMMARY: {local_rag_summary}

Based on the FET data analyzed so far, generate a search query to find:
1. Academic papers on similar FET sensor configurations
2. Manufacturing process optimizations for the observed issues
3. Stability improvement techniques
4. Alternative materials or fabrication methods

REQUIREMENTS:
- Generate a search query with 5-10 keywords, not a complete sentence
- Focus on key terms and concepts, avoid questions
- Maximum 50 characters recommended

Output a single, specific search query that would find relevant academic literature to support the FET analysis.
The query should be different from the original and focus on gaps identified in the current findings."""

FET_FINAL_SUMMARY_PROMPT = """Generate a comprehensive FET sensor analysis report.

RESEARCH TOPIC: {research_topic}
CURRENT DATE: {current_date}

ALL FINDINGS:
{running_summary}

Create a professional FET sensor analysis report with:

# FET Sensor Analysis Report

## Executive Summary
- Key performance metrics achieved
- Main findings and insights
- Critical recommendations

## 1. Performance Analysis
### 1.1 Electrical Characteristics
- Ion/Ioff: [best value, average, trend]
- SS: [best value, average, unit: mV/dec]
- VT: [value, stability, drift rate]
- gm_max: [peak value, conditions]

### 1.2 Sensor Performance
- Target analyte sensitivity
- Detection limits
- Response characteristics
- Selectivity

## 2. Stability Assessment
### 2.1 Temporal Stability
- VT drift analysis (mV/cycle)
- Long-term degradation patterns
- Environmental sensitivity

### 2.2 Reproducibility
- Cycle-to-cycle variation
- Device-to-device consistency
- Batch reliability

## 3. Manufacturing Recommendations

### Immediate Actions
- Specific process parameters to adjust
- Quick optimization steps
- Quality control improvements

### Experimental Validation
- Proposed experiments with expected outcomes
- Resource requirements
- Timeline estimates

### Risk Mitigation
- Identified failure modes
- Preventive measures
- Monitoring protocols

## 4. Next Steps
1. Priority experiments
2. Process optimizations
3. Additional characterization needs
4. Scale-up considerations

## Technical Details
- Folders analyzed: [count]
- Runs processed: [count]
- Data completeness: [percentage]
- Confidence level: [High/Medium/Low]

Format the report professionally with clear sections and actionable insights."""

FET_WEB_SEARCH_ENHANCEMENT = """FET sensor {base_query} fabrication optimization stability characterization"""