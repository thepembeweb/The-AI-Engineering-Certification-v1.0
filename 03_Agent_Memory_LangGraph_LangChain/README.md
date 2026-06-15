<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 3: Agent Memory and Graph-Enhanced Agentic RAG</h1>

### [Quicklinks]()

| 📰 Session Sheet | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo | 📝 Homework | 📁 Feedback |
|:-----------------|:-------------|:----------|:----------|:------------|:------------|
| [Session 3: Agent Memory](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/03_memory) |[Recording!](https://us02web.zoom.us/rec/share/Se_On_Sxl-It_2dP1Uo1cS8XgDM_VxuDhIK5c3viAnVcyybHWc5f4lfntbCZOTDv.hKjpX2JjzbDCfpxR) <br> passcode: `am4=Qgq+`| [Session 3 Slides](https://canva.link/28esllo4r4m0ro9) |You are here! | [Session 3 Assignment](https://forms.gle/Q8f4j6kB4vYViSYNA) | [Feedback 6/9](https://forms.gle/Got49t4zZxX2aR5u7) |

## Main Assignment

In this assignment, you will implement all major agent memory types, then extend the cat health agent's retrieval system with a small knowledge graph.

Breakout Room #1 focuses on two memory scopes:

```text
thread-scoped state -> checkpointer -> short-term memory
cross-thread data   -> store        -> long-term memory
```

Within long-term memory, you will implement:

```text
semantic memory   -> facts and preferences
episodic memory   -> experiences and outcomes
procedural memory -> approved instructions
```

Breakout Room #2 focuses on graph-enhanced Agentic RAG:

```text
dense retrieval -> semantically similar chunks
graph retrieval -> connected entities and source chunks
agent -> decides which retrieval tool to call
```

This is a compact teaching implementation inspired by GraphRAG concepts. It is not the full Microsoft GraphRAG indexing and query pipeline.

The main notebook is:

```text
01_Cat_Health_Agent_Memory_LangGraph_LangChain.ipynb
```

Complete all questions and activities directly in the notebook.

## Outline

### Breakout Room #1: Memory Foundations

- Task 1: Environment Setup
- Task 2: A Practical Memory Model
- Task 3: Short-Term Memory with a Checkpointer
- Task 4: Long-Term Memory with a Store
- Task 5: Context Management with Summarization
- Activity #1: Build a Consent-Aware Cat Profile
- Task 6: Semantic Memory - Facts and Preferences
- Task 7: Episodic Memory - Experiences and Outcomes
- Task 8: Procedural Memory - Reviewed Instructions
- Task 9: Build a Unified Memory Agent

### Breakout Room #2: Graph-Enhanced Agentic RAG

- Task 10: See the Dense Retrieval Limitation
- Task 11: Build a Small Source-Grounded Knowledge Graph
- Task 12: Traverse the Graph and Recover Source Chunks
- Task 13: Let an Agent Choose Dense or Graph Retrieval
- Activity #2: Extend the Graph
- Advanced Extension: Extraction and Community Detection

### Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will need an OpenAI API key available when running the notebook.

Optional LangSmith tracing:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="your-key"
```

## Optional Deep Dive: Agent Memory From Scratch

If you want to look underneath the framework abstractions, run the optional reference notebook:

```text
02_Cat_Health_Agent_Memory_From_Scratch.ipynb
```

It rebuilds the memory portion of Session 3 with Python standard-library HTTP requests and handcrafted chat persistence, namespaced long-term storage, semantic search, context compaction, memory tools, and agent-loop primitives.

The application-facing names are inspired by Vercel AI SDK, including `ModelMessage`, `tool()`, `generate_text()`, `ToolExecutionOptions`, call options, `prepare_call`, and `ToolLoopAgent`. The notebook follows the AI SDK custom-memory-tool approach while keeping storage, consent, user isolation, retrieval, and deletion visible.

## Submitting Your Homework

1. Complete the notebook questions and activities.
2. Keep useful outputs that support your observations.
3. Remove secrets, stale experiments, and excessively noisy output.
4. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your course repository.
