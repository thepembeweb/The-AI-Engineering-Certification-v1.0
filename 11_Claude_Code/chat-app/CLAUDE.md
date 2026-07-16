# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                    # install dependencies
uv run uvicorn main:app    # run the dev server at http://127.0.0.1:8000
```

There is no lint, type-check, or test tooling configured in this project — don't assume any exists.

**Do not pass `--reload` on Windows.** It's been confirmed reproducible: with `--reload`,
every `/api/chat` request fails and falls back to the generic error reply; restarting
without `--reload` fixes it immediately. Likely cause is WatchFiles' reloader subprocess
model interfering with the Claude Agent SDK's own CLI subprocess spawning. After editing
`main.py`, kill and manually restart the server instead of relying on autoreload.

## Architecture

This is a two-piece skeleton: a FastAPI backend (`main.py`) and a single self-contained
static frontend (`static/index.html`, no framework, no build step).

- `GET /` returns `static/index.html` directly via `FileResponse`.
- `POST /api/chat` accepts `{"message": "...", "conversation_id": "..."}` (Pydantic
  `ChatRequest`) and returns a `StreamingResponse` of `text/event-stream` — NOT a single
  JSON body. Each SSE frame is `event: <type>\ndata: <json>\n\n` where `<type>` is
  `progress` (one per tool call, `{"text": "Reading main.py…"}`-shaped) or `reply`
  (exactly one, terminal, `{"text": "<final answer>"}`-shaped).
- All reply logic is isolated in one async generator: `stream_agent_events(message,
  conversation_id)` in `main.py`, which the `/api/chat` handler wraps into SSE frames.
  It runs a read-only Claude Code agent via `claude_agent_sdk.ClaudeSDKClient`,
  configured as a codebase concierge for the repo at `REPO_PATH`:
  - `system_prompt` sets the concierge persona (concise answers, cite file paths).
  - `tools=["Read", "Glob", "Grep"]` restricts which *built-in* tools are available at
    all; `allowed_tools` (below) only controls which tools skip the permission prompt —
    it does **not** restrict availability. Both are required for the read-only safety
    story: `allowed_tools` alone leaves `Bash`/`Write`/`Edit` reachable (confirmed via
    server logs during testing — the agent called `Bash` before `tools` was added).
  - `allowed_tools` pre-approves the built-ins, our two custom `repo` MCP tools, and all
    seven `catshop` MCP tools (see below) so nothing prompts for permission (there's no
    human to answer a prompt on a headless server).
  - `mcp_servers` also connects to an external HTTP MCP server, `catshop` (a demo "Cat
    Shop" server), via `_catshop_mcp_config()`. Its bearer token comes from the
    `CATSHOP_MCP_TOKEN` env var (see `.env.example`) — **never hardcode a real token in
    source**; `python-dotenv`'s `load_dotenv()` at module load reads a local `.env`
    (gitignored via the repo root `.gitignore`'s `.env` entry). `catshop` exposes
    `list_products`, `search_products`, `get_product`, `add_to_cart`, `view_cart`,
    `remove_from_cart`, and `checkout` — **all seven are approved in `allowed_tools`,
    including `checkout`, per explicit user instruction.** This means the agent can
    complete a real purchase autonomously with no per-action human approval step; this
    was a deliberate, explicitly-confirmed choice, not an oversight — `checkout` was
    excluded earlier in this project's history and only added back after the user named
    it specifically. If you're extending this further, don't assume a mutating/
    transactional MCP tool is safe to auto-approve by default — it was excluded here
    until asked for by name.
    If you add a new external MCP server, don't assume `allowed_tools` omission alone
    blocks a *built-in* tool (it doesn't — see the `tools` note above); for MCP tools
    specifically, omission from `allowed_tools` is the correct and sufficient way to
    block them, confirmed empirically (an unlisted `catshop` tool was not called even
    when the prompt explicitly asked for it).
  - The system prompt explicitly mentions the `catshop` tools — without that, the model
    reflexively treated any shop-related question as out of scope for a "repository
    concierge" and never attempted to call them, even though they were available.
  - Two custom tools, defined with `@tool` and served via `create_sdk_mcp_server`
    (`mcp_servers={"repo": REPO_TOOLS_SERVER}`), both scoped to `REPO_ROOT`:
    - `count_lines(path)` — line count for one file; refuses paths that escape the repo.
    - `list_routes()` — regex-scans this repo's `*.py` files for `@app.<method>(...)`
      decorators and returns method/path/handler/file:line. Chosen because "what does
      this API expose" is the single highest-value canned question for a FastAPI
      service's concierge, and a regex scan is exact where an LLM's own Grep-based
      reasoning could miss or hallucinate a route.
    - Every `ToolUseBlock` in the agent's `AssistantMessage`s is logged
      (`logger.info("tool_use: %s(%s)", ...)`) so tool calls are visible in the uvicorn
      console — this is how you verify the agent actually used a given tool — and also
      turned into a friendly `progress` SSE event via `_describe_tool_use()` (e.g.
      `Read` → "Reading main.py…") so the browser shows live activity instead of a
      spinner. Add a branch there when adding a new tool, or it falls back to a generic
      "Using `<tool name>`…" line.
  - `cwd=REPO_PATH` — absolute path of the target repo, configurable via the `REPO_PATH`
    env var (defaults to this project's own directory).
  - `max_turns=25` — hard cap so a request can't loop forever.
  - Any exception, or a `ResultMessage` with `is_error`/no `result`, is caught and turned
    into a polite chat reply instead of a 500.
  - Session resumption: the module-level `_agent_sessions` dict maps our
    `conversation_id` to the Claude Agent SDK's own `session_id`, captured from
    `ResultMessage.session_id` after a successful turn and passed back via
    `ClaudeAgentOptions.resume` on later turns for that `conversation_id`. In-memory
    only — lost on restart, no eviction/TTL.
  - **Every turn — not just a conversation's first — uses the persistent
    `ClaudeSDKClient` and waits via `_wait_for_catshop_ready()`** before sending the
    message. This took two wrong turns to land on: caching the session at `init` time,
    then caching only after a full successful turn, both still produced resumed turns
    permanently missing `catshop`'s tools. The actual cause: **every** `query()`/client
    call — resumed or not — spins up its own subprocess and independently reconnects
    all MCP servers from scratch; `resume` restores conversation history, not an
    already-connected MCP server. So every single turn needs this wait, confirmed by
    testing (a resumed turn that skipped it hit the exact same race as an unwaited
    fresh one; adding the wait to every turn fixed it end-to-end, including a cart
    mutation on a 3rd resumed turn). `_wait_for_catshop_ready()` polls
    `client.get_mcp_status()` for up to ~4.5s (`_CATSHOP_MAX_WAIT_ATTEMPTS` ×
    `_CATSHOP_POLL_INTERVAL_S`) and logs only `status`/`error` on failure — never the
    full status dict, which embeds the bearer token in `config.headers.Authorization`.
    Shared message handling (tool-use progress events, the terminal reply, caching the
    session_id from `ResultMessage.session_id`) lives in `_consume_agent_messages()`.
  - `catshop`'s bearer token has already expired once mid-project (`HTTP 401` reported
    via `get_mcp_status()`) and been refreshed by the user. If shop questions stop
    working, check the server log for a `catshop MCP connection did not succeed`
    warning before assuming the wait logic regressed — it's very likely just the token
    again (demo/tunneled tokens like this one are often short-lived).
- The frontend is plain HTML/CSS/JS in `static/index.html`. It generates a
  `conversation_id` client-side once per page load (`crypto.randomUUID()`) and reuses it
  for every `/api/chat` call in that session. `streamChat()` reads the SSE response body
  manually via `response.body.getReader()` + `TextDecoder` (not the `EventSource` API,
  which only supports GET requests and can't send the JSON body this endpoint needs),
  parsing `\n\n`-delimited frames with `parseSSEFrame()`. Each `progress` event
  overwrites the pending assistant bubble's text (shown in mono, dimmed) until the
  terminal `reply` event replaces it with the final answer.

### Frontend design concept — "Echo Bench"

The UI is themed around channel-tagged message rows (`you` / `echo`), a header status
readout (`listening` / `receiving`), and an animated dashed "trace" connector between a
sent message and its reply — originally chosen because `/api/chat` was a literal echo
stub. **That's no longer true**: the backend now runs a real concierge agent, so the
literal "echo" framing is stale relative to what the app does. Flag this to the user
rather than silently reworking the design — it may still want to be evolved (e.g. drop
the echo framing, keep the instrument-panel concept) but that's a design decision, not
an incidental cleanup.

There is a project-scoped skill at `.claude/skills/frontend-design/SKILL.md` — use it for
any further UI/visual design work in this project so changes stay intentional rather than
defaulting to generic styling.
