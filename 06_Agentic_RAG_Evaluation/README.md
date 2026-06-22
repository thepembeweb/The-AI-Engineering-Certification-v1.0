<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 6: Agentic RAG Evaluation</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_AIEC_Quicklinks)

| 📰 Module | ⏺️ Recording | 🖼️ Slides     | 👨‍💻 Repo     | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Session 6: Agentic RAG Evals](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/06_Agentic_RAG_Evaluation) | [Recording!](https://us02web.zoom.us/rec/share/tfvtQxJ1h0CH9NS0s8R1Nh4NFay085xU00aoLbpdFIKBowwl4cYeYRlhPGvr2Xq5.N6Z_BNdvCMfWDBLW) <br> passcode: `g?M4pGu0` | [Session 6 Slides](https://canva.link/kxsdgi5timxi0yt) |You are here! | [Session 6 Assignment](https://forms.gle/ZQB4CfZnfu4kQAWT8) | [Feedback 6/18](https://forms.gle/t1DP8VQLXEgNhYmE6) |

## Main Assignment

In this assignment, you will first generate and review synthetic evaluation
examples for a source-grounded wellness RAG application. You will score a
baseline and a controlled retrieval change with Ragas. Then you will continue
to a small LangGraph ReAct agent that retrieves live metal spot prices and
evaluate its tool use, goal completion, and scope adherence.

Every model request—both the agent and the LLM-as-judge metrics—goes through
Vercel AI Gateway. Metals.dev supplies live price data; it is the only external
data API in the exercise.

Breakout Room #1 is the RAG-evaluation foundation. Breakout Room #2 continues
from outcome evaluation into process evaluation for a tool-using agent.

```text
wellness corpus
    -> Ragas synthetic examples
    -> baseline and candidate LangGraph RAG
    -> Ragas outcome and retrieval signals

live-price request
    -> LangGraph agent
    -> tool call and live-price result
    -> normalized Ragas trace
    -> process and outcome metrics
```

The main notebook is:

```text
01_Metal_Price_Agent_Evaluation_Ragas_LangGraph.ipynb
```

Complete all questions and activities directly in the notebook.

## Outline

### Breakout Room #1: Synthetic RAG Evaluation

- Task 1: Environment Setup
- Task 2: Configure Vercel AI Gateway and Model Roles
- Task 3: Load the Wellness Corpus
- Task 4: Generate and Review Synthetic Test Data with Ragas
- Task 5: Construct a Baseline LangGraph RAG Application
- Task 6: Evaluate the Baseline with Ragas
- Task 7: Change One Retrieval Variable and Re-Evaluate
- Activity #1: Try a Different Retrieval Strategy

### Breakout Room #2: Agent Evaluation with Ragas

- Task 8: Build a ReAct Agent with a Metal-Price Tool
- Task 9: Implement a LangGraph ReAct Loop
- Task 10: Normalize a LangGraph Trace for Ragas
- Task 11: Evaluate Tool-Call Accuracy, Goal Accuracy, and Topic Adherence
- Activity #2: Add a Tool-Call Regression Case
- Activity #3: Design a Scope-Safety Regression
- Advanced Build: Make Evaluation a Repeatable Regression Suite

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
```

Create the Gateway key in the [Vercel AI Gateway
dashboard](https://vercel.com/docs/ai-gateway/authentication). The notebook
prompts for missing keys, so they do not need to be stored in a file. A Vercel
OIDC token is also supported when the notebook runs in a configured Vercel
environment.

Breakout Room #2 additionally needs a live-price key:

~~~bash
export METALS_API_KEY="your-key"
~~~

Create it at [Metals.dev](https://metals.dev/). The notebook also recognizes the
earlier `METAL_API_KEY` spelling as a fallback, but new setups should use
`METALS_API_KEY`.

A direct `OPENAI_API_KEY` is not used. Vercel AI Gateway exposes an
[OpenAI-compatible API](https://vercel.com/docs/ai-gateway/openai-compat), so
LangChain, the OpenAI SDK, and Ragas use the Gateway base URL with
provider-qualified model IDs.

Optional model and endpoint controls:

```bash
export AIM_AGENT_MODEL="openai/gpt-5.4-mini"
export AIM_GENERATOR_MODEL="openai/gpt-5.4-mini"
export AIM_RAG_MODEL="openai/gpt-5.4-mini"
export AIM_JUDGE_MODEL="openai/gpt-5.4-mini"
export AIM_EMBEDDING_MODEL="openai/text-embedding-3-small"
export AIM_TESTSET_SIZE=4
export AIM_RAG_EVAL_LIMIT=3
export AIM_MAX_CONCURRENCY=2
export AIM_GATEWAY_BASE_URL="https://ai-gateway.vercel.sh/v1"
```

## Evaluation Design

Breakout Room #1 compares a baseline similarity retriever with maximal marginal
relevance (MMR), keeping the corpus, embeddings, prompt, answer model, and
reviewed evaluation rows fixed. It measures:

- **Context recall:** Did retrieval surface enough information to support the
  reference answer?
- **Faithfulness:** Is the generated answer supported by its retrieved context?
- **Answer accuracy:** Does the answer achieve the reference outcome?
- **Context-entity recall and noise sensitivity:** What useful information was
  recovered, and how much irrelevant context may be distorting the answer?

Breakout Room #2 separates three agent questions that are easy to conflate:

- **Tool-call accuracy:** Did the agent call `get_metal_price` with the expected
  argument?
- **Goal accuracy:** Did the final outcome satisfy the user's request?
- **Topic adherence:** Did the agent stay in its intended live-metal-price scope?

The last exercise deliberately compares a permissive baseline with a
scope-guarded variant. A score is evidence, not a verdict: inspect the trace,
tool output, prompts, and real user requirements before deciding that a change
is an improvement.

LLM-as-judge metrics and synthetic generation make several billable calls. Keep
the examples small while developing, review generated rows, and rerun only the
cases affected by a change.

## Wellness and Financial-Information Safety

This is an educational evaluation exercise. The wellness corpus is not a source
of diagnosis, treatment, or individualized health advice; its generated examples
must preserve that boundary. Live spot prices can be delayed, market-specific, or
unavailable; the agent is not an investment adviser and does not provide trading,
allocation, or tax advice. Verify consequential health and financial information
independently.

## Submitting Your Homework

1. Complete the notebook questions and all three activities.
2. Review the synthetic examples before using them for RAG evaluation.
3. Keep a representative RAG trace plus one passing and one failing agent trace.
4. State the expected behavior for every regression case you add.
5. Explain whether each controlled change moved metrics for the reason you expected.
6. Remove secrets and excessively noisy outputs.
7. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your course repository.
