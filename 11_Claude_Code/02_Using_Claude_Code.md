# Using Claude Code — and Scaffolding Your Chat App

## The Mental Model

Claude Code is an agent loop with a terminal UI:

```text
your prompt
    ↓
model picks a tool  →  Read / Grep / Edit / Bash / ...
    ↓
tool runs (behind a permission gate)
    ↓
model observes the result, picks the next tool ... until done
    ↓
final answer
```

Everything in this guide is about steering that loop: what context it starts with (`CLAUDE.md`), what it's allowed to do (permission modes), and what tools it can reach. Keep this picture in mind — in Guide 3 you will drive this **same loop from Python code**.

## Starting and Managing Sessions


| Command                           | What it does                                                                    |
| --------------------------------- | ------------------------------------------------------------------------------- |
| `claude`                          | Start an interactive session in the current directory                           |
| `claude "fix the failing test"`   | Start a session with an initial prompt                                          |
| `claude -p "explain src/auth.py"` | **Print mode**: run one query non-interactively and exit (great for scripts/CI) |
| `claude -c`                       | Continue the most recent session in this directory                              |
| `claude -r`                       | Resume an older session (interactive picker)                                    |


Useful flags:


| Flag                       | Purpose                                                       |
| -------------------------- | ------------------------------------------------------------- |
| `--model <name>`           | Pick a model (e.g. `claude --model claude-sonnet-5`)          |
| `--permission-mode <mode>` | Start in a specific permission mode (e.g. `plan`)             |
| `--add-dir <path>`         | Grant access to an extra directory outside the cwd            |
| `--output-format json`     | Structured output in print mode — pipe it into other programs |




### 🔨 Task 2: Learn the Loop

Before building anything, watch the loop work. Open a repo you **didn't** write (clone any open-source project, or use this course repo) and run:

```bash
claude "walk me through the architecture of this codebase — what are the main components and how do they talk to each other?"
```

Watch the tool calls scroll by: Glob to map the tree, Grep to find entry points, Read to inspect them. This is the agent loop from Session 2, live. Ask a follow-up. Notice you never told it *which* files to read — and notice this "answer questions about a codebase" capability is **exactly what your chat app will productize**.

## The Essential Slash Commands

Type `/` inside a session to see everything. The ones you'll use daily:


| Command        | Purpose                                                    |
| -------------- | ---------------------------------------------------------- |
| `/help`        | List available commands                                    |
| `/clear`       | Wipe conversation history (start fresh, keep the session)  |
| `/compact`     | Summarize-and-compress the conversation to reclaim context |
| `/context`     | Show what's eating your context window                     |
| `/model`       | Switch models mid-session                                  |
| `/init`        | Generate a starter `CLAUDE.md` for the project             |
| `/memory`      | Browse and edit memory files                               |
| `/permissions` | View/manage allowed and denied tools                       |
| `/mcp`         | Manage MCP server connections                              |
| `/agents`      | Manage subagents                                           |
| `/review`      | Ask for a code review of your current diff                 |
| `/exit`        | Leave (or `Ctrl+D`)                                        |


> **Context management callback:** `/compact` and `/clear` are the manual versions of the summarization middleware you built in Session 3. Same problem — finite context — same solution: compress or drop history.



## Permission Modes

Every tool call passes a permission gate. Cycle modes with **Shift+Tab**:


| Mode                  | Behavior                                                                               | Use when                                                |
| --------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| **default**           | Asks before file edits and commands                                                    | Getting started; sensitive repos                        |
| **acceptEdits**       | Auto-approves file edits and safe commands                                             | You trust the direction and want speed                  |
| **plan**              | **Read-only.** Claude explores and proposes a plan; nothing executes until you approve | Before any non-trivial change                           |
| **bypassPermissions** | No gate at all (`--dangerously-skip-permissions`)                                      | Only in throwaway containers/VMs. Never on your laptop. |


(Two specialized modes exist beyond these — `auto`, an autonomous mode with a background safety classifier, and `dontAsk` for locked-down CI — you won't need them today.)

The workflow that makes permission modes click is **plan → implement → verify**: explore and agree on a plan in plan mode (the cheap moment to steer), switch to acceptEdits to implement fast, then make Claude prove the result by running it. You're about to do exactly that.

## 🔨 Task 3: Scaffold the Chat App Skeleton

Time to build. Create an empty project and start Claude Code **in plan mode**:

```bash
mkdir chat-app && cd chat-app
claude --permission-mode plan
```

Give it the spec. Don't copy-paste blindly — read it, adjust names and preferences to taste, make it yours:

```text
Build the skeleton of a chat web app in this directory:

- Python 3.12+ project managed with uv; FastAPI + uvicorn
- GET /            → serves static/index.html: a clean chat UI (message history,
                     text input, send button) in plain HTML/CSS/JS — no frontend framework
- POST /api/chat   → accepts {"message": "...", "conversation_id": "..."} and returns
                     {"reply": "..."}. For now, STUB IT: reply with an echo of the message.
                     This stub gets replaced by a real agent later — keep it isolated in
                     one clearly-named function.
- The frontend calls /api/chat with fetch() and renders both sides of the conversation
- A README.md with run instructions
```

Then:

1. **Read the plan it proposes.** Does the structure make sense? Is the stub isolated so it's easy to swap out later? Push back until you're happy — this is the whole point of plan mode.
2. Approve, and let it implement (Shift+Tab to **acceptEdits** if you want fewer prompts).
3. **Verify — never skip this.** Make Claude prove it works:

```text
Run the server, then curl /api/chat with a test message and show me the response.
```

1. Open `http://localhost:8000` yourself. Send a message. See it echo.

> **You just did the canonical Claude Code workflow.** Plan → implement → verify is the highest-leverage habit in this session. Also: read the code it wrote. You are the engineer of record — Question #1 asks you to reflect on exactly this division of responsibility.



## 🔨 Task 4: Write the Project's [CLAUDE.md](http://CLAUDE.md)

`CLAUDE.md` is a markdown file loaded into context at the start of **every** session in this project — it's how the next session (and Breakout Room 2!) starts smart instead of rediscovering everything. The hierarchy, broadest first:

```text
~/.claude/CLAUDE.md        # user level: your personal preferences, all projects
./CLAUDE.md                # project level: checked into git, shared with the team
./CLAUDE.local.md          # personal, per-project (add to .gitignore)
```

In your `chat-app/` directory, run `/init` to generate a draft, then **edit it down**. For this project it should capture things like:

- How to run the server and test the endpoint (`uv run uvicorn ...`, the curl command)
- The architecture decision that matters: *the chat logic lives in one swappable function;* `/api/chat` *is the seam where the agent gets wired in*
- Conventions you care about (plain JS, no frameworks; keep the stub isolated)

What does **not** belong: anything discoverable by reading the code, long prose, stale info. Every line costs context in every future session — keep it lean. This is Question #2; form your answer while you edit.

**Test it:** start a fresh `claude` session and ask it to run the server. It should know how without being told.

## Worth Knowing (You'll Meet These Again)

- **Custom slash commands** — `.claude/commands/<name>.md`: a prompt template invoked as `/<name>`, with `$ARGUMENTS` interpolation. **Skills** (`.claude/skills/<name>/SKILL.md`) are the richer successor. Version your team's workflows with the code.
- **Subagents** — `.claude/agents/<name>.md`: specialized workers with their own system prompt, tool restrictions, and context window. The supervisor/worker pattern from Session 4, productized. Run `/agents`.
- **Hooks** — shell commands that fire deterministically on lifecycle events (`PreToolUse`, `PostToolUse`, ...). Use them to *guarantee* behavior (run the formatter after every edit; block edits to protected paths) rather than asking the model nicely.
- **MCP** — Claude Code is an MCP *client*. `claude mcp add --transport http <name> <url>` (or a project-level `.mcp.json`) hands it any MCP server's tools — including the cat shop server you built in Session 8. The Advanced Activity connects that server to your chat app's agent.
- **Settings** — same layering as `CLAUDE.md`: `~/.claude/settings.json` → `.claude/settings.json` → `.claude/settings.local.json`.



## Bridge to Breakout Room 2

Your skeleton has a chat UI talking to an echo stub. Here's the thing to sit with: **Claude Code just demonstrated the exact capability your app needs.** In Task 2 it answered architecture questions about an arbitrary repo; your app's whole purpose is to serve that ability through a web UI.

So how do you get *the thing Claude Code does* behind *your* endpoint? That's the Claude Agent SDK — the same agent loop, as a library.

**Next:** `[03_Claude_Agent_SDK.md](./03_Claude_Agent_SDK.md)` — replace the echo stub with a real agent.