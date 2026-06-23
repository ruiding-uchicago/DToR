from datetime import datetime

# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

query_writer_instructions="""Your goal is to generate a targeted web search query.

<CONTEXT>
Current date: {current_date}
Please ensure your queries account for the most current information available as of this date.
</CONTEXT>

<TOPIC>
{research_topic}
</TOPIC>

<REQUIREMENTS>
- Generate a search query with 5-10 keywords, not a complete sentence
- Focus on key terms and concepts, avoid questions
- Maximum 50 characters recommended
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with ALL three of these exact keys:
   - "query": The actual search query string
   - "rationale": Brief explanation of why this query is relevant
</FORMAT>

<EXAMPLE>
Example output:
{{
    "query": "transformer architecture attention mechanism BERT",
    "rationale": "Key concepts for understanding transformer models"
}}
</EXAMPLE>

Provide your response in JSON format:"""

complementary_query_writer_instructions="""Your goal is to generate a COMPLEMENTARY web search query that explores a different angle of the research topic.

<CONTEXT>
Current date: {current_date}
Original research topic: {research_topic}
Original search query: {original_query}
</CONTEXT>

<LOCAL_KNOWLEDGE>
{local_rag_results}
</LOCAL_KNOWLEDGE>

<MODALITY_AWARENESS>
The local knowledge may contain data from multiple modalities, indicated by labels:
- "=== MODALITY: FET Sensor Experimental Data ===" - Laboratory sensor measurements and performance metrics
- "=== MODALITY: Code Repository ===" - Source code implementations and technical documentation
- "=== MODALITY: Academic Papers ===" - Scientific literature and research papers

Consider which modalities are present and what complementary information from OTHER sources would be valuable.
</MODALITY_AWARENESS>

<GOAL>
You must carefully analyze the local knowledge provided above to identify areas to explore that are DIFFERENT from but still RELEVANT to the original query.
Rather than enhancing the original query, your task is to create a GENERALLY DIFFERENT query that:
1. Explores an alternative aspect or perspective of the topic
2. Targets information that is NOT present in the local knowledge but would be valuable
3. Complements the original query by investigating related but distinct concepts
4. Maintains relevance to the scientific domain (chemistry, materials science, engineering, etc.)
5. Is GENERALLY DIFFERENT from the original query (avoid just adding words like "advanced" or "technical details")
6. If local data is from experiments (FET), consider searching for theoretical explanations or similar work
7. If local data is from code, consider searching for algorithmic improvements or best practices
8. If local data is from papers, consider searching for practical implementations or recent developments
</GOAL>

<REQUIREMENTS>
- Generate a search query with 5-10 keywords, not a complete sentence
- Focus on key terms and concepts, avoid questions
- Maximum 50 characters recommended
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with these exact keys:
   - "complementary_query": A search query that explores a different angle of the research topic
   - "divergent_aspect": Explain what different aspect of the topic this query explores
   - "rationale": Why this complementary angle will provide valuable additional information
</FORMAT>

<EXAMPLE>
Example for original query about transformers:
{{
    "complementary_query": "attention mechanism limitations scaling",
    "divergent_aspect": "While the original query focuses on the architecture and structure, this explores the limitations and weaknesses",
    "rationale": "Understanding both the strengths and limitations provides a more complete picture of transformer technology"
}}
</EXAMPLE>

<EXAMPLE>
Example for original query about PFOA binding:
{{
    "complementary_query": "PFAS remediation photocatalysis oxidation",
    "divergent_aspect": "This explores different approaches to PFAS remediation beyond binding mechanisms",
    "rationale": "A comprehensive solution may involve multiple remediation strategies working together"
}}
</EXAMPLE>

Provide your response in JSON format:"""

summarizer_instructions="""
<GOAL>
Generate a high-quality summary of the provided context.
</GOAL>

<MODALITY_AWARENESS>
The context may include data from multiple modalities, indicated by these labels:
- "=== MODALITY: FET Sensor Experimental Data ===" - Laboratory measurements, performance metrics, Ion/Ioff ratios, etc.
- "=== MODALITY: Code Repository ===" - Implementation details, algorithms, technical documentation
- "=== MODALITY: Academic Papers ===" - Research findings, theoretical frameworks, citations

When summarizing multi-modal data:
- Clearly indicate which insights come from which modality
- Look for synergies between different data types (e.g., experimental results supporting theoretical papers)
- Highlight when different modalities provide complementary perspectives
</MODALITY_AWARENESS>

<REQUIREMENTS>
When creating a NEW summary:
1. Highlight the most relevant information related to the user topic from the search results
2. Ensure a coherent flow of information
3. If multiple modalities are present, organize insights by source type when appropriate

When EXTENDING an existing summary:
1. Read the existing summary and new search results carefully.
2. Compare the new information with the existing summary.
3. For each piece of new information:
    a. If it's related to existing points, integrate it into the relevant paragraph.
    b. If it's entirely new but relevant, add a new paragraph with a smooth transition.
    c. If it's not relevant to the user topic, skip it.
4. Ensure all additions are relevant to the user's topic.
5. Verify that your final output differs from the input summary.
< /REQUIREMENTS >

< FORMATTING >
- Start directly with the updated summary, without preamble or titles. Do not use XML tags in the output.
- Always write a complete summary, even if complex. If you're thinking through the process, always conclude with the final summary output.  
< /FORMATTING >

<Task>
Think carefully about the provided Context first. Then generate a summary of the context to address the User Input.
</Task>
"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.

<GOAL>
1. Identify knowledge gaps or areas that need deeper exploration
2. Generate a follow-up question that would help expand your understanding
3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered
</GOAL>

<MODALITY_AWARENESS>
The summary may integrate insights from multiple data sources:
- FET Sensor Data: Laboratory measurements and device performance metrics
- Code Repositories: Implementation details and algorithms
- Academic Papers: Theoretical frameworks and research findings

Consider which modalities have been consulted and what complementary information might be missing.
For example:
- If only experimental data is available, theoretical explanations might be needed
- If only papers are cited, practical implementations or real-world data might be valuable
- If only code is analyzed, best practices or performance benchmarks might be missing
</MODALITY_AWARENESS>

<REQUIREMENTS>
- Generate a search query with 5-10 keywords, not a complete sentence
- Focus on key terms and concepts, avoid questions
- Maximum 50 characters recommended
- Consider gaps across different modalities when selecting keywords
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with these exact keys:
- knowledge_gap: Describe what information is missing or needs clarification
- follow_up_query: Search keywords to address this gap
</FORMAT>

<Task>
Reflect carefully on the Summary to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:
{{
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks",
    "follow_up_query": "performance benchmarks metrics evaluation standards"
}}
</Task>

Provide your analysis in JSON format:"""

# --- Prompts for Code Improvement Workflow ---

analyze_code_and_plan_research_instructions = """You are an expert ML code reviewer and research planner.

<GOAL>
Analyze the provided ML code context (description, code, performance, request) to:
1. Identify key weaknesses, potential bugs, or areas for improvement in the code.
2. Determine the most critical knowledge gaps that need to be addressed through targeted research.
3. Formulate a concise and actionable research topic focused on finding solutions or best practices for the identified issues.
</GOAL>

<INPUT_CONTEXT>
Problem Description: {problem_description}
---
Current Code:
```python
{current_code}
```
---
Current Performance: {current_performance}
---
Human Request: {human_request}
</INPUT_CONTEXT>

<REQUIREMENTS>
- Your critique should be specific and constructive.
- The research topic must directly address the most significant issues identified in the critique.
- The topic should be suitable for web search to find relevant papers, articles, or documentation.
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with these exact keys:
- "critique": A concise summary of the main issues found in the code and context.
- "research_topic": The specific research topic to investigate for solutions.
</FORMAT>

<EXAMPLE>
{{
    "critique": "The current data augmentation pipeline seems basic and might not be robust enough for the described dataset variability. Performance degradation suggests overfitting.",
    "research_topic": "advanced data augmentation techniques for image classification with limited data variability"
}}
</EXAMPLE>

Provide your analysis and research plan in JSON format:"""

generate_revision_plan_instructions = """You are an expert ML engineer responsible for planning code revisions based on research findings.

<GOAL>
Synthesize the original code context and the research report to create a **clear, concise, and actionable** high-level revision plan (under 500 words).
This plan should guide a developer on *what* to change and *why*, based on the research report.
</GOAL>

<ORIGINAL_CONTEXT>
Problem Description: {problem_description}
---
Current Code Snippet (for reference):
```python
{current_code_snippet}
```
---
Current Performance: {current_performance}
---
Human Request: {human_request}
</ORIGINAL_CONTEXT>

<RESEARCH_REPORT_REFERENCE>
{research_report}
</RESEARCH_REPORT_REFERENCE>

<REQUIREMENTS>
- Focus on actionable steps directly derived from the research report and relevant to the original context.
- Prioritize changes likely to have the most significant impact.
- Keep the plan concise and easy to understand (under 500 words).
- Output the plan in markdown format, preferably as a numbered or bulleted list.
- Do NOT include code snippets in the plan itself.
</REQUIREMENTS>

<FORMAT>
Output the revision plan directly in markdown format. Start with a brief introductory sentence if needed.
</FORMAT>

<EXAMPLE_PLAN_OUTPUT>
Based on the research, here is the plan to improve the model:

1.  **Implement Technique X:** Replace the current activation function in layer Y with the GELU activation, as suggested by the report for improved gradient flow.
2.  **Adjust Parameter Z:** Increase the dropout rate in the final dense layer to 0.3 to mitigate observed overfitting, following best practices highlighted in the research.
3.  **Add Preprocessing Step:** Incorporate normalization using StandardScaler before feeding data into the model, as the report indicates this can stabilize training.

</EXAMPLE_PLAN_OUTPUT>

Now, generate the revision plan based on the provided context and research report:"""

implement_code_revision_instructions = """You are an expert Python programmer acting as a code implementation engine.

<GOAL>
Revise the `Original Code` based *strictly* on the provided `Revision Plan`. Your task is to execute the plan precisely.
</GOAL>

<REVISION_PLAN>
{revision_plan}
</REVISION_PLAN>

<ORIGINAL_CODE>
```python
{current_code}
```
</ORIGINAL_CODE>

<REQUIREMENTS>
1.  Implement **only** the changes specified in the `Revision Plan`.
2.  Do **not** introduce any new logic, features, or changes not explicitly mentioned in the plan.
3.  Ensure the output is **complete, executable Python code** representing the fully revised script/module.
4.  If the plan is unclear or contradictory, make a reasonable interpretation but prioritize sticking to the plan's instructions.
5.  Output **only** the raw Python code. Do **not** include explanations, markdown formatting (like ```python), or any text other than the code itself.
</REQUIREMENTS>

<OUTPUT_FORMAT>
```python
# Revised Python code starts here
import ...

# ... (rest of the complete, revised code)
```
</OUTPUT_FORMAT>

Now, implement the changes specified in the Revision Plan into the Original Code and output the complete revised code:"""