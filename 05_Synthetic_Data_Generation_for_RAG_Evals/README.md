<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 5: Synthetic Data Generation for RAG Evals</h1>

### [Quicklinks]()

| Session Sheet | Recording | Slides | Repo | Homework | Feedback |
|:--------------|:----------|:-------|:-----|:---------|:---------|
| [Session 5: Synthetic Data for Evals](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/05_Synthetic_Data_Generation_for_Evals) |[Recording!](https://us02web.zoom.us/rec/share/hrSnunPHSLtrcxBV1TTwniYgSLhlWSkkcIVnxxODVUR0KWtcGscRBRoXPRcrCj1v.45qWYwlZEeH_PPE9) <br> passcode: `jt38+r$W`| [Session 5 Slides](https://canva.link/fpaffi4z92fwb0v) |You are here! | [Session 5 Assignment](https://forms.gle/H43rfDg7Y5X5gZkb8) | [Feedback 6/16](https://forms.gle/LXwuChFyA6PaUiME6) |

## Main Assignment

In this assignment, you will turn the course's cat health guideline PDF into a
reviewed evaluation dataset, upload it to LangSmith, and use it to compare two
versions of a RAG application. Every model and embedding request is routed
through Vercel AI Gateway.

The workflow is:

```text
source corpus
    -> Ragas knowledge graph
    -> synthetic questions, contexts, and reference answers
    -> human review
    -> LangSmith dataset
    -> baseline and candidate RAG experiments
```

The main notebook is:

```text
01_Cat_Health_Synthetic_Data_Generation_Ragas_LangSmith.ipynb
```

The notebook uses:

```text
data/cat_health_guidelines.pdf
```

Synthetic references are candidates for review, not automatic ground truth. The
assignment deliberately includes a curation step before the examples are uploaded
to LangSmith.

## Outline

### Breakout Room #1: Synthetic Test Data with Ragas

- Task 1: Environment Setup
- Task 2: Load the Cat Health Corpus
- Task 3: Build and Enrich a Knowledge Graph
- Task 4: Inspect the Query Distribution
- Task 5: Generate and Inspect a Synthetic Test Set
- Activity #1: Review and Curate the Dataset

### Breakout Room #2: RAG Evaluation with LangSmith

- Task 6: Create a LangSmith Dataset
- Task 7: Build a Baseline RAG Application
- Task 8: Define RAG Evaluators
- Task 9: Run the Baseline Experiment
- Task 10: Change One Retrieval Variable and Re-Evaluate
- Activity #2: Compare, Diagnose, and Iterate
- Advanced Build: Add Robustness and Adversarial Cases

## Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter
environment created by uv.

You will need:

```bash
export AI_GATEWAY_API_KEY="your-key"
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_TRACING=true
```

Create the gateway key in the
[Vercel AI Gateway dashboard](https://vercel.com/docs/ai-gateway/authentication-and-byok).
The notebook prompts for missing API keys, so they do not need to be stored in a
file. A Vercel OIDC token is also supported when the notebook runs in a configured
Vercel environment. A direct `OPENAI_API_KEY` is not used by this notebook.

Optional model and cost controls:

```bash
export AIM_GENERATOR_MODEL="openai/gpt-5.4-mini"
export AIM_RAG_MODEL="openai/gpt-5.4-mini"
export AIM_JUDGE_MODEL="openai/gpt-5.4-mini"
export AIM_EMBEDDING_MODEL="openai/text-embedding-3-small"
export AIM_TESTSET_SIZE=6
export AIM_MAX_CONCURRENCY=2
```

All generation, embedding, RAG, and judge requests use Vercel AI Gateway's
OpenAI-compatible endpoint. Ragas generation and LLM-as-judge evaluation both
make several model calls. Keep the default test set small while developing,
inspect the results, and scale only after the workflow is behaving as expected.

## Experiment Design

The worked comparison changes retrieval from `k=3` to `k=6` while keeping the
corpus, chunks, embeddings, model, and prompt fixed. This makes the result easier
to interpret than changing several parts of the application at once.

The evaluators measure:

- Answer correctness against the reviewed synthetic reference
- Answer groundedness against the context retrieved during that run
- Retrieval relevance against the input question

These scores are useful directional signals. They still require trace inspection,
human judgment, and eventually production examples.

## Medical Safety

This notebook is an educational evaluation exercise. Its corpus and generated
answers are not veterinary advice, diagnoses, prescriptions, or substitutes for a
veterinarian. Review generated examples carefully, especially any example that
describes urgent symptoms or treatment.

## Submitting Your Homework

1. Complete the notebook questions and both activities.
2. Review the generated examples before uploading them to LangSmith.
3. Keep useful dataset and experiment links or screenshots in your notes.
4. Remove secrets, stale experiments, and excessively noisy outputs.
5. Document the variable you changed and what happened to each metric.
6. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your course repository.
