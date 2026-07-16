<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 11: Claude Code & the Claude Agent SDK</h1>

| 📰 Session Sheet                                                                                                                                                | ⏺️ Recording                                                                                                                                                | 🖼️ Slides                                               | 👨‍💻 Repo                                                                                                                                                               | 📝 Homework                                                                                                                                          | 📁 Feedback                                         |
| :-------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- |
| [Session 11: Claude Code & Claude Agent SDK ](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/11_Claude_Code) | [Recording!](https://us02web.zoom.us/rec/share/2I5HA6DwVFgmtyjPaq1SJDgkaVEuYZoWYyMCK8DOAZ99Zm6f7dTi0IGONXj6mRel.YHFzKF03mI5v6JAM) <br> passcode: `&Qhi!cf0` | [Session 11 Slides](https://canva.link/uw1cl42x84tm6zh) | You are here! <br><br> [Certification Challenge](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Certification%20Challenge) | [Optional Session 11 Assignment](https://forms.gle/sAyr5BgBLTfgJV8EA) <br><br> [Cert Challenge Submission Form](https://forms.gle/xtM9F38nfRKcdjH97) | [Feedback 7/7](https://forms.gle/oDrguLDNvva65mtM8) |

## Useful Resources

**Claude Code**

- [Claude Code Documentation](https://code.claude.com/docs) — official docs: setup, workflows, settings
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart) — from install to first session
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) — Anthropic engineering guide

**Claude Agent SDK**

- [Agent SDK Overview](https://docs.anthropic.com/en/api/agent-sdk/overview) — what the SDK is and when to use it
- [Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — Anthropic engineering deep dive

## Main Assignment

**Build a chat web app powered by the Claude Agent SDK** — and build it _with_ Claude Code.

This session is markdown-only on purpose. There is no starter code and no notebook: every line of code in your final app will be written in collaboration with Claude Code. The session has one build arc across a single breakout room:

```text
you → Claude Code → chat app skeleton → wire in Agent SDK query()
      (FastAPI + chat UI, echo stub)      ├─ tools: Read / Glob / Grep
                                           └─ your custom tool
```

The finished product: a **codebase concierge** — a chat interface in the browser where an agent (with real tools) answers questions about any repository you point it at. In Session 10 you served models behind endpoints; today you serve an _agent_ behind one.

Work through the three guides in order:

```text
01_Installing_Claude_Code.md   # install, authenticate, verify
02_Using_Claude_Code.md        # drive Claude Code; scaffold the chat app skeleton
03_Claude_Agent_SDK.md         # add the agent and connect it to your website
```

## Outline

### Breakout Room #1: Claude Code, the Agent SDK, and the Connection

- Task 1: Install Claude Code and authenticate ([guide](./01_Installing_Claude_Code.md))
- Task 2: Learn the loop — explore a repo you didn't write ([guide](./02_Using_Claude_Code.md))
- Task 3: Scaffold the chat app skeleton with Claude Code (plan → implement → verify)
- Task 4: Write the project's `CLAUDE.md`
- Question #1 and Question #2
- Task 5: Install the Agent SDK and run your first `query()` ([guide](./03_Claude_Agent_SDK.md))
- Task 6: Wire the agent into `/api/chat` — replace the echo stub
- Task 7: Conversation memory — resume sessions across messages
- Task 8: Give the agent a custom tool
- Question #3 and Question #4
- Activity #1: Level Up the Chat App

## Questions

### ❓ Question #1

While scaffolding in Task 3 you used **plan mode** before letting Claude Code write anything. Why does an agent that can execute shell commands need a permission system at all, and why is plan mode particularly valuable when starting a project from an empty directory?

#### ✅ Answer

I think a shell-capable agent still needs a permission system because its tools have real side effects: it can create files, edit code, install packages, and run commands much faster than I can manually supervise, so the permission gate keeps me in control of intent and reduces the chance of accidental damage or unnecessary changes. Plan mode felt especially useful in an empty directory because there was no existing codebase to constrain the agent's choices, which made the first decisions about structure, dependencies, and separation of concerns the most important; reviewing the plan first let me correct the architecture while the cost of change was still low and approve a cleaner foundation before anything was written.

### ❓ Question #2

`CLAUDE.md` is loaded into context at the start of every session. What belongs in it — and what _doesn't_? How does this relate to what you learned about context management and memory in Session 3?

#### ✅ Answer

To me, `CLAUDE.md` should contain the small set of project instructions that every future session benefits from having up front: how to run and test the app, the key architectural seam where the agent will be wired in, and conventions that are easy to violate but important to preserve. It should not contain information the agent can recover by reading the code, long prose, or stale implementation details, because that wastes context and increases the risk of anchoring on outdated guidance. That matches what I learned in Session 3 about context management and memory: persistent context is only valuable when it stores compressed, high-signal information, so `CLAUDE.md` should act like a curated memory layer rather than a dump of everything about the project.

### ❓ Question #3

The Agent SDK gives you the same agent loop that powers Claude Code. Compare this to the agent loops you hand-built with LangGraph in Sessions 2–4: what does the SDK give you for free, and what control do you give up?

#### ✅ Answer

My takeaway is that the Agent SDK gives you most of the hard infrastructure for free: a production-ready tool loop, built-in file and shell tools, retries, permission controls, automatic context management, session persistence, and MCP integration, so you can focus on the app instead of rebuilding the harness. The tradeoff is that you give up some of the low-level control you had with LangGraph, where you could design custom state graphs, swap providers more freely, and control each transition yourself; with the SDK, you accept a more opinionated agent architecture in exchange for speed, reliability, and much less plumbing.

### ❓ Question #4

Your chat app could have called a chat completions API directly, the way you did early in the course. What do you gain by routing every message through the Agent SDK's `query()` instead — and what new risks does an agent with tools introduce that a plain chat completion doesn't have? How did your tool allowlist and permission mode address them?

#### ✅ Answer

For me, routing each message through the Agent SDK's `query()` gives the app more than a plain chat completion. It gives me an agent loop that can inspect the repository with tools, do multi-step reasoning, resume sessions, and return answers grounded in files instead of just producing a best-effort reply from the prompt alone. The tradeoff is that a tool-using agent introduces real operational risk, because exposing write or shell capabilities means a bad prompt or weak configuration can turn a chat request into unintended side effects. The tool allowlist and permission mode addressed that by making the agent structurally read-only in the app: limiting it to `Read`, `Glob`, and `Grep` meant it could inspect code but not modify it, and settings like `max_turns` replaced the human approval step I had in the CLI with explicit server-side safety boundaries.

## Activity 1: Level Up the Chat App

Extend your working chat app with **at least one** of the following (built with Claude Code, of course):

1. **Live progress streaming** — stream the agent's activity to the browser (e.g. via Server-Sent Events) so users see tool calls ("reading `app.py`…") while the agent works, instead of a spinner
2. **Multi-conversation support** — a sidebar of separate conversations, each mapped to its own SDK session
3. **A second custom tool** — something genuinely useful for your target repo (e.g. `git_log` for recent changes, or a test-runner summary tool)

Whichever you pick, demo it in your Loom video and explain the design decision in one paragraph.

## Design Decision

The core design decision:

- `generate_reply()` was replaced with an async-generator, `stream_agent_events()`, that yields SSE-ready dicts while the agent works.
- The backend emits:
  - one `{"type": "progress", ...}` event per tool call;
  - translated via `_describe_tool_use()` into friendly present-progressive text (for example: "Reading `main.py`..." or "Searching for files matching `...`...");
  - followed by one terminal `{"type": "reply", ...}` event.
- `/api/chat` now returns a `StreamingResponse` (`text/event-stream`) instead of a single JSON body.
- On the frontend, the client intentionally does not use `EventSource` (it only supports `GET`, while this endpoint needs a `POST` body).
- Instead, it reads the response manually via `getReader()`/`TextDecoder`, parses SSE frames, and updates the pending assistant bubble live.
- The in-progress bubble remains dimmed monospace to preserve the existing "instrument chrome vs. human reply" visual distinction until the final reply swaps in.

## Advanced Activity: The Cat Shop Concierge

Connect your Session 8 cat shop MCP server to your chat app's agent via the SDK's `mcp_servers` option. Your chat app becomes a shopping concierge: users can browse the catalog, fill a cart, and check out — in natural language, through the UI you built, hitting the OAuth-protected server you wrote in Session 8.

Include your findings and a demo in your Loom video.

## Ship 🚢

The working chat app!

### Deliverables

- A short Loom showing:
  - Claude Code scaffolding or extending the app (plan → implement → verify — show the plan!); and
  - the chat app answering real questions about a repository, including at least one visible custom-tool use

## Share 🚀

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped a chat app powered by the Claude Agent SDK — scaffolded entirely with Claude Code! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI agents. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#ClaudeCode #AgentSDK #AIAgents #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework (Optional For Extra Mark)

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Work through `01_Installing_Claude_Code.md`, `02_Using_Claude_Code.md`, and `03_Claude_Agent_SDK.md` in order.
3. Build your chat app in a new `chat-app/` folder inside this session directory (include its `CLAUDE.md` — we want to see it!).
4. Fill in your answers to Questions #1–#4 in this README.
5. Complete Activity #1 and record your Loom video.
6. Add, commit, and push your work to your origin repository. Remove `.env` files and API keys before committing.

When submitting your homework, provide the GitHub URL to your repo.
