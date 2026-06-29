<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center">Session 7: Advanced Retrievers</h1>

| Module Sheet | Recording     | Slides        | Repo         | Homework      | Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Session 7: Advanced Retrievers](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/07_Advanced_Retrievers) |[Recording!](https://us02web.zoom.us/rec/share/ZnvAlAg5k1YIMN_AcdBxdF06Dq0-YVfm98gZl13hOoZ9aB4J5csHwL6BptHV7yRv.o9HpmnwpCDDi2ExU) <br> passcode: `7!j49V6e`| [Session 7 Slides](https://canva.link/hq26752cgd4af2a) |You are here! | [Session 7 Assignment](https://forms.gle/AEu4b7eyTQsFtLDN9) | [Feedback 6/23](https://forms.gle/epfFyQqAd4WNmLZm9) |

## Main Assignment

In this session, you will improve the cat-health RAG application from Session 1
without changing its source corpus. You will begin with the familiar naive
dense RAG baseline, then layer BM25, parent-child retrieval, hybrid retrieval,
Cohere reranking, and finally multi-query expansion.

The main notebook is:

```text
01_Cat_Health_Advanced_Retrieval.ipynb
```

The notebook uses the bundled source document:

```text
data/cat_health_guidelines.pdf
```

The point is not to crown one universal winner. The point is to make a
retrieval choice using evidence from the same questions, corpus, and retrieval
depth.

## Teaching Ladder

```text
naive dense RAG in in-memory Qdrant
  -> BM25 over the same child chunks
  -> parent-child retrieval over dense search
  -> hybrid dense + BM25 with RRF
  -> Cohere reranking over recovered parent pages
  -> multi-query expansion over the complete hybrid pipeline
```

Dense plus BM25 is **hybrid retrieval** (also called hybrid search). RRF makes
it an **ensemble**. Adding Cohere after that makes the combined system a
**two-stage hybrid retrieve-then-rerank pipeline**.

## Minimal Eval Framework

The local [lib/](./lib) package uses the same shape as Evalite:

    run_eval(name, data=..., task=..., scorers=[...])

- EvalItem holds one reviewed input and its expected value.
- Scorer and create_scorer(...) define reusable 0-to-1 metrics with inspectable metadata.
- run_eval(...) executes the task for each item, runs every scorer, and retains inputs, outputs, scores, and timing.
- compare_eval_reports(...) compares runs that used the same data and scorers.

The RAG-specific helpers are thin layers over that core:

- run_retrieval_eval(...) uses reusable hit-rate, precision, recall, and MRR scorers while keeping its focused retrieval table.
- faithfulness_scorer(...) checks whether answer claims are supported by retrieved passages.
- answer_similarity_scorer(...) compares a generated answer with a reviewed reference answer.

Task 9 calls run_eval(...) directly for answer evaluation, so the data, task, and scorer boundary is visible in the notebook.

Retrieval metrics:

- Hit rate at k
- Precision at k
- Recall at k
- Mean reciprocal rank (MRR)
- Mean latency

Answer metrics:

- [Faithfulness](https://v1.evalite.dev/api/scorers/faithfulness): an OpenAI judge marks each factual answer claim as supported or unsupported by the retrieved passages.
- [Answer similarity](https://v1.evalite.dev/api/scorers/answer-similarity): cosine similarity between OpenAI embeddings of a generated answer and a reviewed reference answer.

Faithfulness and answer similarity answer different questions. A response can stay grounded in weak retrieved context yet fail to cover the reference answer.

## Setup

From this folder:

```bash
uv sync
```

You need an OpenAI key for embeddings, multi-query generation, grounded
answers, and the faithfulness judge, plus a Cohere key for second-stage
reranking:

```bash
export OPENAI_API_KEY="your-key"
export COHERE_API_KEY="your-key"
```

Optional model configuration:

```bash
export AIM_CHAT_MODEL="gpt-5.4-mini"
export AIM_EVAL_MODEL="gpt-5.4-mini"
export AIM_EMBEDDING_MODEL="text-embedding-3-small"
export AIM_RERANK_MODEL="rerank-v4.0-fast"
```

`rerank-v4.0-fast` is the classroom default for low latency. The notebook uses
LangChain's `CohereRerank` document compressor rather than a custom Cohere API
adapter. Change the
environment variable to `rerank-v4.0-pro` when you want to explore the
quality/latency trade-off. See the [Cohere Rerank guide](https://docs.cohere.com/docs/reranking)
for the API behavior and model details.

## Outline

### Breakout Room #1: Start Simple, Then Add Context

- Task 1: Set Up the Session Environment
- Task 2: Load and Chunk the Cat PDF for Naive RAG
- ❓ Question 1: Why does retrieval metadata matter?
- Task 3: Build Naive Dense RAG with OpenAI Embeddings and In-Memory Qdrant
- Task 4: Build BM25 Sparse Retrieval over the Same Chunks
- ❓ Question 2: When should BM25 win?
- 🚀 Activity 1: Diagnose Dense and BM25 Failure Modes
- Task 5: Build Parent-Child Retrieval over Dense Search
- ❓ Question 3: Why search children but return parents?

### Breakout Room #2: Combine, Rank, and Expand

- Task 6: Fuse Dense and BM25 Rankings with Reciprocal Rank Fusion
- Task 7: Rerank Hybrid Parent Candidates with Cohere Rerank
- Task 8: Generate Multiple Search Queries with an OpenAI Model
- Task 9: Compare Retrieval and Answer Results with `lib`
- ❓ Question 4: Is more retrieval always better?
- 🚀 Activity 2: Make and Defend a Retrieval Recommendation
- Advanced Build: Add MMR Diversification or HyDE

## Medical Safety

This is an information-retrieval exercise, not a veterinary-care tool. The
application must answer only from retrieved course context and recommend a
veterinarian for diagnosis, treatment, medication, or urgent-care decisions.

## Verify the Local Utilities

Run the small deterministic test suite before relying on the library:

```bash
uv run python -m unittest discover -s tests -v
```
