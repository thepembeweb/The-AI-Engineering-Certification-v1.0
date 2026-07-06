# The AI Engineering Certification

A hands-on course covering the foundations of production AI engineering — from dense vector retrieval to agentic RAG systems.

---

## Modules

| #   | Module                                                                                   | Description                                                                                                     |
| --- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 01  | [Dense Vector Retrieval](./01_Dense_Vector_Retrieval/)                                   | Build a RAG pipeline using LangChain, OpenAI embeddings, and an in-memory Qdrant vector store                   |
| 02  | [Agentic RAG with LangGraph & LangChain](./02_Agentic_RAG_LangGraph_LangChain/)          | Make retrieval an optional tool the agent calls on demand using LangChain middleware and LangGraph `StateGraph` |
| 03  | [Agent Memory & Knowledge Graph](./03_Agent_Memory_LangGraph_LangChain/)                 | Implement all major agent memory types and implement knowledge graph                                            |
| 04  | [Multi-Agent Systems](./04_Multi_Agent_Systems/)                                         | Build a multi-agent deep research system using LangChain and LangGraph                                          |
| 05  | [Synthetic Data Generation for RAG Evals](./05_Synthetic_Data_Generation_for_RAG_Evals/) | Synthetic data generation for rag evals                                                                         |
| 06  | [Agentic RAG Evaluation](./06_Agentic_RAG_Evaluation/)                                   | Agentic RAG evaluation                                                                                          |
| 07  | [Advanced Retrievers](./07_Advanced_Retrievers/)                                         | Advanced Retrievers                                                                                             |
| 08  | [MCP](./08_MCP/)                                                                         | MCP                                                                                                             |
| 09  | [MCP](./09_Agent_Servers/)                                                               | Agent Servers                                                                                                   |

---

## Prerequisites

| Requirement                      | Version |
| -------------------------------- | ------- |
| Python                           | >= 3.12 |
| [uv](https://docs.astral.sh/uv/) | latest  |
| OpenAI API key                   | —       |

---

## Getting Started

Each module is a self-contained project with its own virtual environment and dependencies managed via `uv`.

1. Navigate into the module directory:

   ```bash
   cd 01_Dense_Vector_Retrieval   # or 02_Agentic_RAG_LangGraph_LangChain
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Open the `.ipynb` notebook in VS Code or Cursor and select the `.venv` kernel created by `uv`.

4. Set your OpenAI API key (or the notebook will prompt for it via `getpass`):
   ```bash
   export OPENAI_API_KEY=<your key>
   ```

See each module's `README.md` for detailed setup and task descriptions.

---

## Repository Structure

```
The-AI-Engineering-Certification-v1.0-main/
├── README.md
├── 01_Dense_Vector_Retrieval/
│   ├── 01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── data/
│       └── cat_health_guidelines.pdf
├── 02_Agentic_RAG_LangGraph_LangChain/
│   ├── 01_Cat_Health_Agentic_RAG_LangGraph_LangChain.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── data/
│       └── cat_health_guidelines.md
├── 03_Agent_Memory_LangGraph_LangChain/
│   ├── 01_Cat_Health_Agent_Memory_LangGraph_LangChain.ipynb
│   ├── 02_Cat_Health_Agent_Memory_From_Scratch.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── data/
│       └── cat_health_guidelines.md
├── 04_Multi_Agent_Systems/
│   ├── 01_Cat_Health_Deep_Research_Multi_Agent_LangChain_LangGraph.ipynb
│   ├── pyproject.toml
│   └── README.md
├── 05_Synthetic_Data_Generation_for_RAG_Evals/
│   ├── 01_Cat_Health_Synthetic_Data_Generation_Ragas_LangSmith.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   ├── artifacts/
│   │   ├── cat_health_knowledge_graph.json
│   │   └── cat_health_synthetic_testset.jsonl
│   └── data/
├── 06_Agentic_RAG_Evaluation/
│   ├── 01_Metal_Price_Agent_Evaluation_Ragas_LangGraph.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── data/
│       ├── agent_regression_suite.jsonl
│       └── HealthWellnessGuide.txt
├── 07_Advanced_Retrievers/
│   ├── 01_Cat_Health_Advanced_Retrieval.ipynb
│   ├── pyproject.toml
│   ├── README.md
│   └── data/
│       └── cat_health_guidelines.pdf
├── 08_MCP/
│   ├── advanced_client.py
│   ├── client.py
│   ├── server.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── app/
│   └── catshop.db
└── 09_Agent_Servers/
   ├── main.py
   ├── pyproject.toml
   ├── README.md
   ├── langgraph.json
   ├── Dockerfile.generated
   ├── docker-compose.yml
   ├── app/
   ├── data/
   └── frontend/
```
