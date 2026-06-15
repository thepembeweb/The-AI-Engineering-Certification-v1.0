<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 4: Multi-Agent Deep Research</h1>

### [Quicklinks]()

| Session Sheet | Recording | Slides | Repo | Homework | Feedback |
|:--------------|:----------|:-------|:-----|:---------|:---------|
| [Session 4: Multi-Agent Applications & Deep Research](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/04_Multi-Agents_and_Deep_Research) |[Recording!](https://us02web.zoom.us/rec/share/pgJD6YlyDWRiOFvmHM7-CiRKbpRJliFZQqdVoZ3XftpQgNoePo-rzmmM7WnNJkkJ.lLQHPrPywa4OuCW3) <br> passcode: `zuG8$L^2`| [Session 4 Slides](https://canva.link/o08r40dpeivhsbv) |You are here! | [Session 4 Assignment](https://forms.gle/mtKgcLg7DqXv5jSW7) | [Feedback 6/11](https://forms.gle/drC5bJkK2wKMbWEg9) |
## Main Assignment

In this assignment, you will build a multi-agent deep research system for investigating feline nutrition and obesity.

The system combines two levels of abstraction:

```text
LangChain create_agent -> each actor's model/tool loop
LangGraph StateGraph   -> scope, clarify, research, verify, write, audit, evaluate
```

The research pipeline is:

```text
user request
    -> structured scope
    -> optional clarification interrupt
    -> supervisor delegates three tasks
    -> guideline and evidence researchers search independently
    -> verifier checks claims and URLs
    -> one writer creates a coherent report
    -> deterministic citation audit
    -> evaluator scores the result
```

The main notebook is:

```text
01_Cat_Health_Deep_Research_Multi_Agent_LangChain_LangGraph.ipynb
```

Complete all questions and activities directly in the notebook.

## Outline

### Breakout Room #1: Specialized Agents and Delegation

- Task 1: Environment Setup
- Task 2: Define Typed Handoff Contracts
- Task 3: Configure Tavily Search and Extract
- Task 4: Build Specialized Research Workers
- Task 5: Wrap Workers as Supervisor Tools
- Task 6: Build the Research Supervisor
- Activity #1: Add a New Specialist

### Breakout Room #2: End-to-End Deep Research Workflow

- Task 7: Build the Scoper and Clarification Path
- Task 8: Build Verification, Writing, and Evaluation Agents
- Task 9: Define LangGraph State and Nodes
- Task 10: Audit Citations Deterministically
- Task 11: Compile and Visualize the Workflow
- Task 12: Stream and Run the Full Deep Research System
- Activity #2: Compare Research Depth and Cost
- Advanced Build: Add a Local-Corpus Specialist

## Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will need:

```bash
export OPENAI_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
```

Optional LangSmith tracing:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="your-key"
export LANGSMITH_PROJECT="aim-session-4-multi-agent-deep-research"
```

Optional model and budget overrides:

```bash
export AIM_CHAT_MODEL="gpt-5.4-mini"
export AIM_WRITER_MODEL="gpt-5.4-mini"
export AIM_SEARCH_DEPTH="advanced"
export AIM_SEARCH_CALL_LIMIT=3
export AIM_EXTRACT_CALL_LIMIT=2
export AIM_WORKER_MODEL_CALL_LIMIT=8
```

## What Makes This Multi-Agent?

The lead research agent does not receive every low-level tool and every instruction.
Instead, it sees two high-level worker tools:

- A guideline specialist focused on professional organizations and veterinary guidance
- An evidence specialist focused on peer-reviewed research and competing claims

Each worker gets a clean context window, a focused prompt, and its own search budget. The supervisor receives only structured findings, which reduces context growth and makes each role easier to inspect and improve.

## Medical Safety

This notebook teaches research-system architecture. Its generated reports are educational research summaries, not diagnoses, prescriptions, feeding plans, or substitutes for a veterinarian. Any individualized weight-loss plan should be reviewed by a veterinarian because overly rapid weight loss can be dangerous for cats.

## Submitting Your Homework

1. Complete the notebook questions and both activities.
2. Keep useful graph, trace, source, and report outputs.
3. Remove secrets, stale experiments, and excessively noisy outputs.
4. Document any budget or prompt changes and their effect on the result.
5. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your course repository.
