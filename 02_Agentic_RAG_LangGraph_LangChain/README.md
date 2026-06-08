# Agentic RAG with LangChain and LangGraph

Session 2 of the AI Engineering Certification. Builds an agentic RAG system where retrieval is an **optional tool** the agent calls on demand, rather than a mandatory first step.

```text
# Session 1 (fixed pipeline)
question → retrieve → generate

# Session 2 (agentic)
question → agent decides whether to retrieve → optional tool call → answer
```

## Notebook

**`01_Cat_Health_Agentic_RAG_LangGraph_LangChain.ipynb`** — demonstrates the same agentic RAG loop two ways over a cat health guidelines corpus:

| Breakout Room | Approach                                    | Key Concepts                                                    |
| ------------- | ------------------------------------------- | --------------------------------------------------------------- |
| BOR 1         | High-level with `create_agent` + middleware | Retriever tool, middleware logging, tool-call budget, streaming |
| BOR 2         | Explicit loop with LangGraph `StateGraph`   | `ToolNode`, `tools_condition`, deterministic scope routing      |

### Tasks

1. **Environment Setup** — install dependencies with `uv sync`
2. **Load and Index** — chunk and embed cat health guidelines into a Qdrant vector store
3. **Create a Retriever Tool** — wrap the vector store as a LangChain `@tool`
4. **`create_agent` + Middleware** — build the agent loop with middleware for logging and tool-call limits
5. **Visualize and Stream** — inspect retrieval decisions via streamed events
6. **LangGraph Explicit Loop** — rebuild the same loop with explicit nodes and conditional edges

### Activities

- **Activity #1**: Add a retriever tool-call budget using `ToolCallLimitMiddleware`
- **Activity #2**: Add deterministic scope routing to short-circuit out-of-scope questions
- **Advanced Build** (optional): Retrieval quality control — document grader, query rewrite, loop limit, guardrail

## Setup

Requires Python 3.12+. Uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
uv sync
```

Select the `.venv` Python interpreter in VS Code or Cursor, then open the notebook.

### Dependencies

| Package                    | Purpose                                         |
| -------------------------- | ----------------------------------------------- |
| `langchain`                | Agent loop, tools, middleware                   |
| `langchain-openai`         | OpenAI LLM and embeddings                       |
| `langchain-qdrant`         | Qdrant vector store integration                 |
| `langchain-text-splitters` | Document chunking                               |
| `langgraph`                | Explicit agent graph (`StateGraph`, `ToolNode`) |
| `qdrant-client`            | In-memory Qdrant vector store                   |

### Environment Variables

```bash
OPENAI_API_KEY=<your key>
```

## Key Takeaways

- Agentic RAG makes retrieval an available action instead of a mandatory pre-step.
- Tool contracts and system prompts strongly influence retrieval decisions.
- Middleware handles cross-cutting concerns (logging, limits, retries) without rebuilding the graph.
- Explicit LangGraph graphs are preferred when you need custom state or control flow.
- Inspect intermediate streamed events — a plausible final answer can hide a poor agent path.

## Further Reading

- [LangChain Agents](https://python.langchain.com/docs/modules/agents/)
- [LangChain Middleware](https://python.langchain.com/docs/modules/agents/agent_middleware/)
- [LangGraph Overview](https://langchain-ai.github.io/langgraph/)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
