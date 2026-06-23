# Chainlit Research Workflows

This guide explains how to use the Chainlit web interface to interact with the Deep Tree of Research system. The Chainlit UI provides real-time progress tracking, iteration summaries, and an intuitive way to conduct both single-path and DToR research investigations.

## Quick Start Summary

### Using Chainlit

**Basic Usage:**
```bash
# Launch Chainlit interface
chainlit run src/ollama_deep_researcher/chainlit_app.py

# Access at http://localhost:8000
```

**Input Format:**
- Single-path mode (default): `Research quantum computing`
- DToR mode: `Research quantum computing in dtor mode`

The interface automatically:
- Parses your input to extract research topic and mode
- Streams real-time progress updates as nodes execute
- Organizes iterations into clear visual sections
- Displays iteration summaries and final results

### Using Chainlit with Phoenix Observability

**Setup Phoenix Tracing:**

1. **Install Phoenix dependencies:**
   ```bash
   pip install arize-phoenix openinference-instrumentation-langchain
   ```

2. **Start Phoenix server** (in a separate terminal):
   ```bash
   phoenix serve
   # Phoenix UI available at http://localhost:6006
   ```

3. **Enable Phoenix in Chainlit:**
   ```bash
   export PHOENIX_ENABLED=true
   chainlit run src/ollama_deep_researcher/chainlit_app.py
   ```

4. **Access both interfaces:**
   - **Chainlit UI**: `http://localhost:8000` - Interactive research interface
   - **Phoenix UI**: `http://localhost:6006` - Trace observability and debugging

**What Phoenix Provides:**
- Automatic tracing of all LLM calls and LangGraph node executions
- Token usage analysis and cost tracking
- Performance monitoring and debugging
- Link to Phoenix UI appears in Chainlit welcome message when enabled

**Configuration Options:**
```bash
# Optional: Customize Phoenix settings
export PHOENIX_HOST=localhost      # Default: localhost
export PHOENIX_PORT=6006           # Default: 6006
export PHOENIX_PROJECT_NAME=my-research  # Default: deep-research
```

**Note:** Phoenix setup happens automatically before LangGraph imports, ensuring all traces are captured from the start. If Phoenix is not available or the server isn't running, Chainlit will continue to work normally without tracing.

---

## Overview

The Chainlit interface (`chainlit_app.py`) wraps the LangGraph research workflows with a user-friendly web UI. It streams execution events in real-time, displays progress updates with user-friendly node names, and organizes research iterations into clear visual sections.

## Getting Started

### Launching the Chainlit Interface

```bash
# From the project root directory
chainlit run src/ollama_deep_researcher/chainlit_app.py

# Or with custom port
chainlit run src/ollama_deep_researcher/chainlit_app.py --port 8000
```

The interface will be available at `http://localhost:8000` (or your specified port).

### Initial Setup

When you first open the Chainlit interface, you'll see a welcome message that explains:
- **Single-path mode**: Fast, linear research for focused topics
- **DToR mode**: Deep Tree of Research with multiple branches and perspectives
- **Phoenix observability**: If enabled, a link to view traces in Phoenix

## User Interface Structure

The Chainlit UI organizes research execution into clear visual sections:

### 1. Initialization Phase

```
### 🔧 Initialize Session
  • 🔧 Initializing research session
  • 🔍 Starting single-path research
  (or)
  • 🌳 Starting Deep Tree of Research
```

The initialization phase sets up the research session and routes to either single-path or DToR mode based on your input.

### 2. Research Iterations

Each iteration is clearly marked with a header:

```
### 🔄 Research Iteration 1
  • 💭 Generating research query
  • 📚 Searching local knowledge base
  • 📄 Summarizing local research
  • 🔄 Generating complementary query
  • 🌐 Searching the web
  • 🌐 Conducting complementary web search
  • 📋 Summarizing research sources
  • 🤔 Reflecting on research quality
```

### 3. Iteration Summaries

At the end of each iteration (or when transitioning to a new iteration), you'll see:

```
  📝 **Iteration Summary:**
  [Summary of findings from this iteration]
```

### 4. Final Results

The final research summary is displayed with:

```
## Final Research Summary

[Comprehensive final summary]

## Sources

1. [Source 1]
2. [Source 2]
...
```

## Input Format

The Chainlit interface automatically parses your input to extract:
- **Research topic**: The main subject to investigate
- **Mode selection**: Single-path or DToR mode

### Examples

**Single-path mode (default):**
```
Research quantum computing
```

**DToR mode:**
```
Research quantum computing in dtor mode
Research machine learning deep tree
```

The parser recognizes keywords like "dtor", "deep tree" to switch to DToR mode. All other text is treated as the research topic.

## Single-Path Mode Workflow

In single-path mode, the UI displays a linear progression through the research loop:

```
### 🔧 Initialize Session
  • 🔧 Initializing research session
  • 🔍 Starting single-path research

### 🔄 Research Iteration 1
  • 💭 Generating research query
  • 📚 Searching local knowledge base
  • 📄 Summarizing local research
  • 🔄 Generating complementary query
  • 🌐 Searching the web
  • 🌐 Conducting complementary web search
  • 📋 Summarizing research sources
  • 🤔 Reflecting on research quality

  📝 **Iteration Summary:**
  [Summary of iteration 1]

### 🔄 Research Iteration 2
  • 📚 Searching local knowledge base
  [continues until max_web_research_loops reached]

  📝 **Iteration Summary:**
  [Summary of iteration 2]

### 🔄 Research Iteration N
  • ✅ Finalizing research summary

## Final Research Summary
[Final comprehensive report]
```

The system automatically loops through iterations until `max_web_research_loops` is reached, then finalizes the summary.

## Deep Tree of Research (DToR) Mode Workflow

In DToR mode, the UI shows the multi-branch exploration:

```
### 🔧 Initialize Session
  • 🔧 Initializing research session
  • 🌳 Starting Deep Tree of Research

### 🔄 Research Iteration 1
  • 💡 Diversifying initial research query
  • 🌿 Selecting next research branch
  • 🔬 Conducting research on current topic
    [Single-path research loop executes here]
  • 📊 Analyzing research findings
  • ❓ Generating follow-up research queries
  • 🔬 Conducting research on current topic
  • 📝 Synthesizing branch findings

  📝 **Iteration Summary:**
  [Branch synthesis summary]

### 🔄 Research Iteration 2
  [Next branch exploration]
  ...

### 🔄 Research Iteration N
  • ✨ Creating final research synthesis

## Final Research Summary
[Final multi-branch synthesis report]
```

DToR mode shows branch selection, research node execution (which internally runs the single-path loop), analysis, and synthesis steps.

## Real-Time Progress Tracking

The Chainlit interface uses LangGraph's `astream_events` API to stream execution events in real-time. This means:

1. **Immediate feedback**: You see each node execute as it happens
2. **No waiting**: Progress updates appear incrementally, not all at once
3. **Clear organization**: Nodes are grouped under iteration headers
4. **Summary tracking**: Iteration summaries appear at natural breakpoints

### Event Processing

The UI processes two types of events:
- **`on_chain_start`**: When a node begins execution (displays the node step)
- **`on_chain_end`**: When a node completes (extracts summaries and final results)

### Node Filtering

The UI automatically filters out internal/technical nodes to keep the display clean:
- Internal LangGraph nodes (`__start__`, `__end__`, `write`, `read`)
- ChannelWrite operations (internal state management)
- Empty or placeholder nodes

Only user-facing research steps are displayed.

## Phoenix Observability Integration

If Phoenix tracing is enabled (`PHOENIX_ENABLED=true`), the Chainlit interface:

1. **Initializes tracing** before any LangGraph imports (required for proper instrumentation)
2. **Displays Phoenix URL** in the welcome message
3. **Captures all traces** automatically via OpenTelemetry instrumentation

### Enabling Phoenix

```bash
# Set environment variable
export PHOENIX_ENABLED=true

# Start Phoenix server (in a separate terminal)
phoenix serve

# Launch Chainlit
chainlit run src/ollama_deep_researcher/chainlit_app.py
```

The welcome message will include a link to view traces in Phoenix, allowing you to:
- Inspect LLM calls and responses
- Analyze token usage
- Debug execution flow
- Monitor performance

## State Management

The Chainlit interface maintains a `ResearchSessionState` object that tracks:

- **Iteration count**: Current research iteration number
- **Current iteration nodes**: Nodes executed in the current iteration
- **Initialization phase**: Whether we're still in setup
- **Iteration summaries**: Collected summaries per iteration
- **Final summary**: The final research result
- **Displayed summaries**: Prevents duplicate summary display
- **Route research completion**: Tracks when routing decisions are made

This state ensures:
- Proper iteration boundaries are detected
- Summaries are displayed at the right time
- No duplicate messages appear
- Final results are always captured and displayed

## Error Handling

The Chainlit interface includes error handling:

1. **Graph initialization errors**: Displays clear error message if graph fails to initialize
2. **Missing input validation**: Prompts user for research topic if none provided
3. **Streaming errors**: Catches exceptions during event streaming
4. **Fallback mechanism**: If final summary isn't captured from events, synchronously invokes the graph to retrieve it

### Fallback Behavior

If the event stream completes without producing a final summary, the UI:
1. Attempts to extract final summary from state
2. Falls back to synchronous graph invocation
3. Displays appropriate error message if all attempts fail

## Configuration

The Chainlit interface respects the same configuration as the underlying research workflows:

- **LLM provider**: Set via `LLM_PROVIDER` environment variable
- **Search API**: Set via `SEARCH_API` environment variable
- **Research mode**: Determined from user input (or defaults to "single")
- **Recursion limit**: Set to 500 to handle deep research graphs
- **Phoenix tracing**: Enabled via `PHOENIX_ENABLED` environment variable

All configuration from `.env` files and environment variables is automatically applied.

## Best Practices

### For Single-Path Research

1. **Use for focused topics**: Single-path mode is ideal when you have a specific, narrow question
2. **Monitor iterations**: Watch the iteration count to see how many research loops are executed
3. **Review summaries**: Each iteration summary shows incremental progress

### For DToR Research

1. **Use for broad topics**: DToR mode excels when exploring complex topics from multiple angles
2. **Watch branch selection**: The UI shows which branch is being explored
3. **Track synthesis**: Branch synthesis summaries show how different perspectives are integrated

### General Tips

1. **Be specific**: Clear research topics produce better results
2. **Monitor progress**: The real-time updates help you understand what's happening
3. **Check Phoenix**: If enabled, use Phoenix traces to debug issues or analyze performance
4. **Review sources**: The final summary includes all sources for verification

## Troubleshooting

### No Progress Updates

If you don't see progress updates:
- Check that the graph is properly initialized (should see welcome message)
- Verify your research topic is valid
- Check browser console for JavaScript errors

### Missing Final Summary

If the final summary doesn't appear:
- The fallback mechanism should retrieve it automatically
- Check that the research completed successfully (no errors in UI)
- Review Phoenix traces (if enabled) to see what happened

### Phoenix Not Capturing Traces

If Phoenix isn't showing traces:
- Verify Phoenix server is running: `phoenix serve`
- Check `PHOENIX_ENABLED=true` is set
- Ensure Phoenix is installed: `pip install arize-phoenix openinference-instrumentation-langchain`
- Check that Phoenix initialization happens before LangGraph imports (this is handled automatically)

### Duplicate Messages

The UI includes deduplication logic to prevent duplicate node displays. If you see duplicates:
- This may indicate a bug in event processing
- Check the `seen_node_starts` set in the state management
- Review event stream for duplicate run_ids

## Comparison with Other Interfaces

### Chainlit vs LangGraph Studio

| Feature | Chainlit | LangGraph Studio |
|---------|----------|------------------|
| **User-friendly node names** | ✅ Yes | ❌ Technical names |
| **Iteration organization** | ✅ Clear sections | ⚠️ Flat view |
| **Real-time streaming** | ✅ Yes | ✅ Yes |
| **Summary display** | ✅ Automatic | ⚠️ Manual inspection |
| **Web interface** | ✅ Yes | ✅ Yes |
| **Checkpointing** | ❌ No | ✅ Yes |
| **Configuration UI** | ❌ No | ✅ Yes |

## Advanced Usage

### Custom Node Descriptions

To customize the node descriptions shown in the UI, edit the `NODE_DESCRIPTIONS` dictionary in `chainlit_app.py`:

```python
NODE_DESCRIPTIONS = {
    "your_node": "🎯 Your custom description",
    ...
}
```

### Adjusting Recursion Limit

The recursion limit is set to 500 by default. To change it, modify `RECURSION_LIMIT` in `chainlit_app.py`:

```python
RECURSION_LIMIT = 1000  # Increase for very deep graphs
```

### Session Management

Each Chainlit session maintains its own graph instance and state. This means:
- Multiple users can use the interface simultaneously
- Each session is independent
- State is not persisted between sessions (unlike checkpointed batch runs)

## Related Documentation

- **`docs/RESEARCH_WORKFLOWS.md`**: Detailed explanation of the underlying research workflows
- **`docs/SYSTEM_OVERVIEW.md`**: System architecture and module structure
- **`docs/MODALITY_RAG.md`**: Modality-aware retrieval system details

## Example Session

Here's what a complete Chainlit session looks like:

```
User: Research quantum computing applications in dtor mode

[Welcome message appears]

### 🔧 Initialize Session
  • 🔧 Initializing research session
  • 🌳 Starting Deep Tree of Research

### 🔄 Research Iteration 1
  • 💡 Diversifying initial research query
  • 🌿 Selecting next research branch
  • 🔬 Conducting research on current topic
  • 💭 Generating research query
  • 📚 Searching local knowledge base
  • 📄 Summarizing local research
  • 🔄 Generating complementary query
  • 🌐 Searching the web
  • 🌐 Conducting complementary web search
  • 📋 Summarizing research sources
  • 🤔 Reflecting on research quality
  • 📊 Analyzing research findings
  • ❓ Generating follow-up research queries

  📝 **Iteration Summary:**
  [Branch 1 synthesis summary]

### 🔄 Research Iteration 2
  [Branch 2 exploration...]

### 🔄 Research Iteration 3
  [Branch 3 exploration...]

### 🔄 Research Iteration 4
  • ✨ Creating final research synthesis

## Final Research Summary

[Comprehensive multi-branch synthesis covering:
- Quantum computing in cryptography
- Quantum computing in optimization
- Quantum computing in machine learning
...]

## Sources

1. [Source citations...]
```

