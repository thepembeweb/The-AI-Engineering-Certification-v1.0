# Chat App

A chat web app with a FastAPI backend and a plain HTML/CSS/JS frontend (no frontend
framework). The backend answers questions about a codebase using a read-only Claude
Code agent — a "concierge" for the repo at `REPO_PATH`.

## Run

```bash
uv sync
uv run uvicorn main:app
```

Then open http://127.0.0.1:8000

By default the concierge answers questions about this project's own directory. To
point it at a different repo, set `REPO_PATH` to that repo's absolute path before
starting the server:

```bash
REPO_PATH=/path/to/other/repo uv run uvicorn main:app
```

The agent is also connected to an external "Cat Shop" MCP server. Copy `.env.example`
to `.env` and set `CATSHOP_MCP_TOKEN` to its bearer token (never commit a real token —
`.env` is gitignored).

> **On Windows, don't pass `--reload`.** Uvicorn's `--reload` (WatchFiles) subprocess
> model breaks the Claude Agent SDK's own CLI subprocess spawning here — every
> `/api/chat` request fails with the generic "something went wrong" reply. Restart the
> server manually after editing `main.py` instead.

## Structure

- `main.py` — FastAPI app with two routes:
  - `GET /` serves `static/index.html`
  - `POST /api/chat` accepts `{"message": "...", "conversation_id": "..."}` and streams
    the response as Server-Sent Events (see below) rather than a single JSON body.
- `static/index.html` — the chat UI (message history, input, send button) and the
  JS that reads the `/api/chat` SSE stream and renders it live.

## Notes

All reply logic lives in `stream_agent_events()` in `main.py`, an async generator that
runs a read-only Claude Code agent (`claude_agent_sdk.ClaudeSDKClient`) scoped to
`REPO_PATH`, restricted via both `tools` (which built-ins exist at all) and
`allowed_tools` (which skip the permission prompt) to `Read`, `Glob`, and `Grep`, plus
custom tools, and a `max_turns` cap so a request can't loop forever. Errors from the
agent are caught and yielded as a polite chat reply instead of a 500.

`POST /api/chat` streams that generator to the browser as `text/event-stream`: a
`progress` event per tool call (e.g. `Reading main.py…`) and exactly one terminal
`reply` event with the final answer. The frontend reads the stream with
`fetch()` + `response.body.getReader()` (not `EventSource`, since that only supports
GET) and updates the pending message bubble live instead of showing a spinner. To watch
the raw stream from the command line: `curl -N -X POST http://127.0.0.1:8000/api/chat
-H "Content-Type: application/json" -d '{"message":"hi","conversation_id":"x"}'`.

Two custom tools are exposed to the agent via an in-process MCP server
(`REPO_TOOLS_SERVER` in `main.py`):

- `count_lines(path)` — line count for a single file, sandboxed to the repo.
- `list_routes()` — lists every FastAPI route in the repo's `*.py` files (method, path,
  handler, file:line), found by scanning for `@app.<method>(...)` decorators.

The agent can also browse and manage a cart via the external `catshop` MCP server
(`list_products`, `search_products`, `get_product`, `add_to_cart`, `view_cart`,
`remove_from_cart`, `checkout`) — all seven tools are approved in `allowed_tools`,
including `checkout`. That means the agent can complete a real purchase autonomously,
with no per-action approval step. This was a deliberate choice made explicitly by the
project owner, not a default — think carefully before auto-approving a
mutating/transactional tool like this for any other MCP server you add.

Every tool call the agent makes is logged (`tool_use: <name>(<input>)`) to the uvicorn
console, so you can confirm in the server logs which tools a given question triggered.

Each `conversation_id` resumes its own agent session across turns (captured from the
first turn's `session_id` and passed back via `ClaudeAgentOptions.resume`), so the agent
remembers earlier messages in the same conversation. Session mapping is in-memory only
and is lost when the server restarts.

Every turn (not just a conversation's first) waits up to ~4.5s for the `catshop` MCP
connection to settle before sending the message, using the persistent `ClaudeSDKClient`.
This is needed because resuming a session restores conversation history, not an
already-connected external MCP server — each turn's subprocess reconnects `catshop`
from scratch, so each one needs the wait, not just the first.

If shop questions stop working, check the server log for a `catshop MCP connection did
not succeed` warning before assuming the code regressed — it may just mean
`CATSHOP_MCP_TOKEN` needs refreshing (tokens for demo/tunneled services like this one
can expire).
