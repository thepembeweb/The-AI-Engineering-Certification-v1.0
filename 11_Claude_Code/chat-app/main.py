import asyncio
import json
import logging
import os
import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("concierge")

app = FastAPI()

STATIC_DIR = Path(__file__).parent / "static"

# Absolute path of the repository the concierge agent answers questions about.
# Configurable so the same server can be pointed at a different checkout in
# other environments; defaults to this project's own directory for local dev.
REPO_PATH = str(Path(os.environ.get("REPO_PATH", Path(__file__).parent)).resolve())
REPO_ROOT = Path(REPO_PATH)

# Bearer token for the external "catshop" MCP server. Read from the environment
# (see .env.example) — never hardcode a real token here.
CATSHOP_MCP_URL = "https://gear-apache-griminess.ngrok-free.dev/mcp"
CATSHOP_MCP_TOKEN = os.environ.get("CATSHOP_MCP_TOKEN")


def _catshop_mcp_config() -> dict:
    config: dict = {"type": "http", "url": CATSHOP_MCP_URL}
    if CATSHOP_MCP_TOKEN:
        config["headers"] = {"Authorization": f"Bearer {CATSHOP_MCP_TOKEN}"}
    return config

# Directories a repo-wide scan should never descend into: dependency trees and
# VCS/tooling metadata, not the source code the concierge answers about.
_IGNORED_DIR_NAMES = {".venv", "venv", "__pycache__", ".git", "node_modules", ".claude"}

CONCIERGE_SYSTEM_PROMPT = (
    "You are a concierge for this repository. Answer questions about its code "
    "concisely and cite file paths for anything you reference. You also have tools "
    "for browsing the connected cat shop (products, cart) via the catshop MCP server "
    "— use them for shop-related questions instead of assuming they're out of scope."
)


def _iter_repo_files(pattern: str) -> list[Path]:
    return [
        path
        for path in REPO_ROOT.rglob(pattern)
        if path.is_file()
        and not any(part in _IGNORED_DIR_NAMES for part in path.relative_to(REPO_ROOT).parts)
    ]


def _relative_to_repo(path_str: str) -> str:
    path = Path(path_str)
    if path.is_absolute():
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            pass
    return path_str


def _describe_tool_use(name: str, tool_input: dict) -> str:
    """Turn a raw tool call into a short present-progressive status line for the UI."""
    if name == "Read":
        return f"Reading {_relative_to_repo(tool_input.get('file_path', 'a file'))}…"
    if name == "Glob":
        return f"Searching for files matching '{tool_input.get('pattern', '*')}'…"
    if name == "Grep":
        return f"Searching for '{tool_input.get('pattern', '')}'…"
    if name == "mcp__repo__count_lines":
        return f"Counting lines in {tool_input.get('path', 'a file')}…"
    if name == "mcp__repo__list_routes":
        return "Listing API routes…"
    if name == "mcp__catshop__list_products":
        return "Listing products…"
    if name == "mcp__catshop__search_products":
        return f"Searching products for '{tool_input.get('query', '')}'…"
    if name == "mcp__catshop__get_product":
        return "Looking up product details…"
    if name == "mcp__catshop__add_to_cart":
        return "Adding to cart…"
    if name == "mcp__catshop__view_cart":
        return "Checking the cart…"
    if name == "mcp__catshop__remove_from_cart":
        return "Removing from cart…"
    if name == "mcp__catshop__checkout":
        return "Checking out…"
    return f"Using {name}…"


@tool(
    "count_lines",
    "Count the number of lines in one file in this repo.",
    {"path": Annotated[str, "File path relative to the repo root, e.g. 'main.py' or 'static/index.html'"]},
)
async def count_lines(args: dict) -> dict:
    target = (REPO_ROOT / args["path"]).resolve()
    if not target.is_relative_to(REPO_ROOT):
        return {
            "content": [{"type": "text", "text": f"Refused: '{args['path']}' is outside the repo."}],
            "is_error": True,
        }
    if not target.is_file():
        return {
            "content": [{"type": "text", "text": f"No such file: '{args['path']}'"}],
            "is_error": True,
        }
    line_count = sum(1 for _ in target.open(encoding="utf-8", errors="replace"))
    return {"content": [{"type": "text", "text": f"{args['path']}: {line_count} lines"}]}


_ROUTE_RE = re.compile(r'@\w+\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']')
_DEF_RE = re.compile(r"\s*(?:async\s+)?def\s+(\w+)")


@tool(
    "list_routes",
    "List every FastAPI route defined in this repo's Python files: method, path, "
    "handler function, and the file:line it's defined at.",
    {},
)
async def list_routes(_args: dict) -> dict:
    routes = []
    for path in sorted(_iter_repo_files("*.py")):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            match = _ROUTE_RE.search(line)
            if not match:
                continue
            method, route_path = match.group(1).upper(), match.group(2)
            handler = ""
            for follow in lines[i + 1 : i + 3]:
                def_match = _DEF_RE.match(follow)
                if def_match:
                    handler = def_match.group(1)
                    break
            rel = path.relative_to(REPO_ROOT)
            routes.append(f"{method} {route_path} -> {handler}() [{rel}:{i + 1}]")

    text = "\n".join(routes) if routes else "No FastAPI routes found."
    return {"content": [{"type": "text", "text": text}]}


REPO_TOOLS_SERVER = create_sdk_mcp_server(
    name="repo_tools",
    tools=[count_lines, list_routes],
)

# Maps our conversation_id to the Claude Agent SDK session_id captured from that
# conversation's first query, so later turns resume the same agent session
# in-process only; lost on restart, with no eviction.
_agent_sessions: dict[str, str] = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


def _tool_use_events(msg: AssistantMessage) -> list[dict]:
    events = []
    for block in msg.content:
        if isinstance(block, ToolUseBlock):
            logger.info("tool_use: %s(%s)", block.name, block.input)
            events.append({"type": "progress", "text": _describe_tool_use(block.name, block.input)})
    return events


def _build_agent_options(conversation_id: str) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=CONCIERGE_SYSTEM_PROMPT,
        # `tools` restricts which built-in tools are even available; `allowed_tools`
        # only controls which of those (plus our MCP tools) skip the permission
        # prompt. Both are required — allowed_tools alone does not block Bash/Write/Edit.
        tools=["Read", "Glob", "Grep"],
        allowed_tools=[
            "Read",
            "Glob",
            "Grep",
            "mcp__repo__count_lines",
            "mcp__repo__list_routes",
            # catshop: all tools approved per explicit user instruction, including
            # `checkout` — the agent can complete a real purchase autonomously, with no
            # per-action human approval step.
            "mcp__catshop__list_products",
            "mcp__catshop__search_products",
            "mcp__catshop__get_product",
            "mcp__catshop__add_to_cart",
            "mcp__catshop__view_cart",
            "mcp__catshop__remove_from_cart",
            "mcp__catshop__checkout",
        ],
        mcp_servers={
            "repo": REPO_TOOLS_SERVER,
            "catshop": _catshop_mcp_config(),
        },
        cwd=REPO_PATH,
        max_turns=25,
        resume=_agent_sessions.get(conversation_id),
    )


_CATSHOP_MAX_WAIT_ATTEMPTS = 15
_CATSHOP_POLL_INTERVAL_S = 0.3


async def _wait_for_catshop_ready(client: ClaudeSDKClient) -> None:
    """Poll MCP status until catshop settles (or ~4.5s elapses), before the first turn.

    A resumed session's tool manifest turns out to be fixed at that session's true
    genesis — earlier than any message we can observe (confirmed empirically: even
    caching the session_id only after a full successful turn still produced a resumed
    session missing catshop tools). Waiting *after* the fact can't fix this. The only
    thing that works is holding off the conversation's first real message until
    catshop's connection has already settled, so the session is born with it.
    """
    for attempt in range(_CATSHOP_MAX_WAIT_ATTEMPTS):
        status = await client.get_mcp_status()
        catshop = next((s for s in status["mcpServers"] if s["name"] == "catshop"), None)
        # Log only status/error — never the full dict, which embeds the bearer token
        # in config.headers.Authorization.
        if catshop is None:
            return
        if catshop["status"] != "pending":
            if catshop["status"] != "connected":
                logger.warning(
                    "catshop MCP connection did not succeed: status=%s error=%s",
                    catshop["status"],
                    catshop.get("error"),
                )
            return
        logger.info("catshop still connecting (attempt %d/%d)", attempt + 1, _CATSHOP_MAX_WAIT_ATTEMPTS)
        await asyncio.sleep(_CATSHOP_POLL_INTERVAL_S)
    logger.warning("catshop wait exhausted all attempts, proceeding anyway")


async def _consume_agent_messages(messages: AsyncIterator, conversation_id: str) -> AsyncIterator[dict]:
    """Yields progress events, then exactly one terminal reply event, always."""
    async for msg in messages:
        if isinstance(msg, AssistantMessage):
            for event in _tool_use_events(msg):
                yield event
        if isinstance(msg, ResultMessage):
            if msg.is_error or not msg.result:
                yield {"type": "reply", "text": "Sorry, I couldn't find an answer to that. Please try rephrasing."}
            else:
                _agent_sessions[conversation_id] = msg.session_id
                yield {"type": "reply", "text": msg.result}
            return
    yield {"type": "reply", "text": "Sorry, I didn't get a response. Please try again."}


async def stream_agent_events(message: str, conversation_id: str) -> AsyncIterator[dict]:
    """Answer a question about the repo at REPO_PATH via a read-only Claude Code agent.

    Yields ``{"type": "progress", "text": ...}`` for each tool call as it happens, then
    exactly one ``{"type": "reply", "text": ...}`` with the final answer (or a polite
    apology in place of a 500 if the agent errors).
    """
    options = _build_agent_options(conversation_id)

    try:
        # Every call — fresh or resumed — spins up its own subprocess and independently
        # reconnects all MCP servers from scratch; resuming a session does not carry
        # forward an already-connected catshop. So every turn needs to wait for
        # catshop's connection to settle before its message is sent, not just a
        # conversation's first turn (confirmed by testing: a resumed turn that skipped
        # the wait hit the exact same race as an unwaited fresh one).
        async with ClaudeSDKClient(options=options) as client:
            await _wait_for_catshop_ready(client)
            await client.query(message)
            async for event in _consume_agent_messages(client.receive_response(), conversation_id):
                yield event
    except Exception:
        yield {"type": "reply", "text": "Sorry, something went wrong while looking that up. Please try again."}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    async def event_stream() -> AsyncIterator[str]:
        async for event in stream_agent_events(request.message, request.conversation_id):
            yield f"event: {event['type']}\ndata: {json.dumps(event)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
