# The Claude Agent SDK — Powering Your Chat App

## What It Is

The Claude Agent SDK is the **agent harness that powers Claude Code**, exposed as a Python/TypeScript library. Same agent loop, same built-in tools (Read, Write, Edit, Bash, Glob, Grep, WebSearch...), same permission system, same `CLAUDE.md`/settings/MCP integration — but driven from your code instead of your keyboard.

```text
Claude Code CLI   =  agent loop + terminal UI
Claude Agent SDK  =  agent loop + your code        ← your chat app lives here
```

> **Naming note:** the SDK was renamed in late 2025. The old `claude-code-sdk` package is deprecated — the current packages are `claude-agent-sdk` (PyPI) and `@anthropic-ai/claude-agent-sdk` (npm). If a tutorial imports `claude_code_sdk`, it's stale.



### How This Compares to What You've Built

Since Session 2 you have hand-assembled agents from parts: a model client, a tool-calling loop, state, memory, retries. The SDK collapses all of that into one dependency:


| You get for free                                         | You give up                                                   |
| -------------------------------------------------------- | ------------------------------------------------------------- |
| Battle-tested agent loop with error handling and retries | Fine-grained control over each loop iteration                 |
| Production file/shell/search tools                       | Choice of model provider (Claude models only)                 |
| Permission system + hooks                                | Custom state graphs (no arbitrary LangGraph-style topologies) |
| Context management (auto-compaction)                     | —                                                             |
| MCP client support, subagents, session persistence       | —                                                             |


That trade-off is Question #3 in the README — form your own opinion as you build.

## 🔨 Task 5: Install the SDK and Run Your First `query()`

In your `chat-app/` directory from Breakout Room 1:

```bash
uv add claude-agent-sdk        # requires Python 3.10+
export ANTHROPIC_API_KEY="sk-ant-..."
```

(TypeScript equivalent: `npm install @anthropic-ai/claude-agent-sdk`, Node 18+. Both packages bundle the Claude Code runtime — no separate CLI install needed on the server. Programmatic use is billed via the API; Bedrock/Vertex are also supported.)

Before touching your endpoint, feel the primitive in isolation. The core of the SDK is `query()`: give it a prompt and options, get back an **async stream of messages** as the agent works. Write a small scratch script:

```python
# scratch_query.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What does this project do? Answer in two sentences.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            cwd="/path/to/any/repo/you/like",
        ),
    ):
        print(type(message).__name__)          # watch the loop's anatomy
        if hasattr(message, "result"):
            print("\n" + message.result)

asyncio.run(main())
```

```bash
uv run scratch_query.py
```



### The Message Stream

That `type(message).__name__` line is there for a reason. `query()` yields typed messages as the loop runs:

- `SystemMessage` (`subtype="init"`) — session started; carries the `session_id` (you'll need this in Task 7)
- `AssistantMessage` — model output: text blocks and tool-use blocks
- `UserMessage` — tool results being fed back to the model
- `ResultMessage` — the loop finished; has `.result`, plus cost and usage stats

Your chat app only *needs* the `ResultMessage`, but the stream is how you build real UX — progress indicators, visible tool calls, streaming text. Activity #1 option 1 lives here.

## 🔨 Task 6: Wire the Agent Into `/api/chat`

Now the connection. Fire up **Claude Code** in your `chat-app/` directory (it has your `CLAUDE.md` from Task 4 — it knows where the seam is) and work with it in plan mode to replace the echo stub. The requirements you're driving toward:

1. The stub function now calls `query()` and returns the `ResultMessage.result` as the reply
2. The agent is configured as a **codebase concierge** via `ClaudeAgentOptions`:
  - `system_prompt` — define the persona and answer style ("you are a concierge for this repository; answer concisely; cite file paths")
  - `allowed_tools=["Read", "Glob", "Grep"]` — **read-only**. This agent runs headless on a server; the allowlist is your safety story
  - `cwd` — the absolute path of the target repo it should answer questions about (make it configurable, e.g. an env var)
  - `max_turns` — a hard cap (say, 25) so no request can loop forever
3. Errors from the agent surface as a polite chat reply, not a 500

Then **verify like you mean it**: run the server, ask it "what does this repo do?" from the browser, and watch a real agent answer through the UI you built an hour ago.

> **Why these controls matter (Question #4):** in the terminal, *you* were the permission gate. On a server there's no human to click "approve" — so the tool allowlist, `permission_mode`, and `max_turns` **are** the gate. An agent with `Read`/`Glob`/`Grep` structurally cannot modify your filesystem, no matter what a user types into the chat box. (For finer control, the SDK also offers a `can_use_tool` callback and `hooks` like `PreToolUse`/`PostToolUse` — the programmatic versions of the CLI hooks from Guide 2.)



## 🔨 Task 7: Conversation Memory

Send two messages through your app: "what does this repo do?" then "what are its main dependencies?" — the second answer won't know about the first. Each `query()` is a fresh conversation.

The fix is **session resumption**. Capture the `session_id` from the init message on the first query:

```python
from claude_agent_sdk import SystemMessage

async for message in query(prompt=..., options=opts):
    if isinstance(message, SystemMessage) and message.subtype == "init":
        session_id = message.data["session_id"]
```

...and pass it back on subsequent queries (alongside the same options):

```python
options = ClaudeAgentOptions(..., resume=session_id)
```

Your job — again, with Claude Code as your pair — is the plumbing: remember that `conversation_id` field the skeleton spec put in your `/api/chat` request body? Map each `conversation_id` to its SDK `session_id` (an in-memory dict is fine for today) so every browser conversation continues where it left off.

Verify: ask the two-message sequence again. The follow-up should now understand "its".

> **Session 3 callback:** this is checkpointer-style short-term memory — thread-scoped state keyed by an ID — except the harness persists it for you.



## 🔨 Task 8: Give the Agent a Custom Tool

Built-in tools cover files, shell, and web. For anything else — your database, your API, your business logic — you define tools **in-process**. The SDK models these as an in-process MCP server (Session 8 concept, zero networking):

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("count_lines", "Count lines of code in a file", {"file_path": str})
async def count_lines(args):
    with open(args["file_path"]) as f:
        n = sum(1 for _ in f)
    return {"content": [{"type": "text", "text": f"{args['file_path']}: {n} lines"}]}

server = create_sdk_mcp_server(name="concierge", version="1.0.0", tools=[count_lines])
```

Two things to wire into your options — the server, and the tool's permission:

```python
options = ClaudeAgentOptions(
    mcp_servers={"concierge": server},
    allowed_tools=["Read", "Glob", "Grep", "mcp__concierge__count_lines"],
    ...
)
```

Note the naming convention: `mcp__<server-key>__<tool-name>` — custom tools must be allowlisted explicitly, exactly like built-ins.

Add a custom tool to your concierge — `count_lines` to start, but then design one that's actually useful for *your* target repo. Verify through the UI: ask a question that forces the tool ("how many lines is the biggest file in src/?") and confirm in your server logs that the agent called it.

**External MCP servers** plug into the same option — which is the entire Advanced Activity:

```python
mcp_servers={
    "catshop": {"type": "http", "url": "http://localhost:8002/mcp"},
}
```

Your Session 8 cat shop server, your Session 11 chat UI, one options dict between them.

## ✅ Checkpoint → Ship It

You're done with the main build when:

- [ ] The browser chat answers real questions about a target repo (Task 6)
- [ ] Follow-up messages carry context — sessions resume per conversation (Task 7)
- [ ] The agent uses at least one custom tool, visibly (Task 8)
- [ ] The agent is provably constrained: read-only allowlist + `max_turns`, and you can explain why (Question #4)

Then pick your Activity #1 upgrade from the README — streaming progress, multi-conversation support, or a second tool — and build it the same way you built everything today: plan it with Claude Code first.

## Docs

- [Agent SDK overview](https://docs.anthropic.com/en/api/agent-sdk/overview)
- [Python SDK reference](https://docs.anthropic.com/en/api/agent-sdk/python)
- [TypeScript SDK reference](https://docs.anthropic.com/en/api/agent-sdk/typescript)
- [Custom tools guide](https://docs.anthropic.com/en/api/agent-sdk/custom-tools)
- [Sessions guide](https://docs.anthropic.com/en/api/agent-sdk/sessions)

