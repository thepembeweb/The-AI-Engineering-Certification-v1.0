# Dense Vector Retrieval

This project showcases a **Retrieval Augmented Generation (RAG)** application using LangChain v1, OpenAI embeddings, and Qdrant as an in-memory vector database.

---

## Overview

A cat health guideline assistant that answers questions grounded in a PDF document:

1. Load a cat health guideline PDF with `PyPDFLoader`
2. Split pages into overlapping chunks with `RecursiveCharacterTextSplitter`
3. Embed each chunk with OpenAI `text-embedding-3-small`
4. Store vectors in an in-memory Qdrant collection
5. Retrieve the most relevant chunks for a query using cosine similarity
6. Generate a cited, context-grounded answer with `gpt-4o-mini` via a RAG prompt chain

---

## Prerequisites

| Requirement                      | Version |
| -------------------------------- | ------- |
| Python                           | >= 3.12 |
| [uv](https://docs.astral.sh/uv/) | latest  |
| OpenAI API key                   | —       |

---

## Setup

From the `01_Dense_Vector_Retrieval` directory:

```bash
uv sync
```

Then open `01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb` in VS Code or Cursor and select the virtual environment created by uv as the kernel.

If `OPENAI_API_KEY` is not already set in your environment, the notebook will prompt for it securely via `getpass`.

---

## Project Structure

```
01_Dense_Vector_Retrieval/
├── 01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb   # Main notebook
├── pyproject.toml                                     # Dependencies (uv)
├── README.md                                          # This file
└── data/
    ├── README.md
    └── cat_health_guidelines.pdf                      # Bundled course PDF
```

---

## Notebook Tasks

| Task     | Description                                                         |
| -------- | ------------------------------------------------------------------- |
| Task 1   | Environment setup and imports                                       |
| Task 2   | Embedding similarity primer — cosine similarity from scratch        |
| Task 3   | Load the cat health guideline PDF into LangChain `Document` objects |
| Task 4   | Chunk documents with `RecursiveCharacterTextSplitter`               |
| Task 5   | Embed chunks and build an in-memory Qdrant vector store             |
| Task 6   | Retrieve chunks with similarity scores and inspect results          |
| Task 7   | Retrieval Augmented Generation — full retrieve-then-generate chain  |
| Activity | Tune retrieval quality by varying chunk size, overlap, and `k`      |

---

## Key Concepts

- **Dense vector retrieval** — embedding queries and documents in the same vector space, then ranking by cosine similarity
- **Chunking tradeoffs** — larger chunks preserve context but reduce retrieval precision; more overlap reduces lost context at boundaries but increases cost
- **Qdrant in-memory mode** — `location=":memory:"` requires no Docker or cloud account; state is lost when the kernel stops
- **Cite, don't hallucinate** — the RAG prompt instructs the model to cite `[Source N]` labels and defer clinical decisions to a veterinarian

---

## Dependencies

Managed via `pyproject.toml` and installed with `uv sync`:

- `langchain`, `langchain-community`, `langchain-openai`, `langchain-qdrant`, `langchain-text-splitters`
- `qdrant-client`
- `pypdf`
- `ipykernel`, `jupyterlab`

---
