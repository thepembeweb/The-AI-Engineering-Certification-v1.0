import argparse
import asyncio
import json
import os
import webbrowser
from typing import Any
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
from pydantic import AnyUrl


DEFAULT_SERVER_URL = "http://localhost:8000"
DEFAULT_MODEL = "gpt-5.4-mini"
SYSTEM_PROMPT = """You are a helpful Cat Shop assistant.

Use the Cat Shop MCP tools to answer catalog and cart questions. Never invent
product information. Only call checkout when the user explicitly asks to place
their order.
"""


class InMemoryTokenStorage(TokenStorage):
    def __init__(self) -> None:
        self._tokens: OAuthToken | None = None
        self._client_info: OAuthClientInformationFull | None = None

    async def get_tokens(self) -> OAuthToken | None:
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._tokens = tokens

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        return self._client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._client_info = client_info


class OAuthCallbackServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self._server: asyncio.AbstractServer | None = None
        self._callback: asyncio.Future[tuple[str, str | None]] | None = None

    @property
    def callback_url(self) -> str:
        return f"http://{self.host}:{self.port}/callback"

    async def __aenter__(self) -> "OAuthCallbackServer":
        self._callback = asyncio.get_running_loop().create_future()
        self._server = await asyncio.start_server(
            self._handle_request, self.host, self.port
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    async def wait_for_callback(self) -> tuple[str, str | None]:
        if self._callback is None:
            raise RuntimeError("The OAuth callback server has not started.")
        return await self._callback

    async def _handle_request(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            request_line = (await reader.readline()).decode("utf-8").strip()
            parts = request_line.split(" ", maxsplit=2)
            target = parts[1] if len(parts) >= 2 else "/"

            # Consume HTTP headers before responding to the browser.
            while await reader.readline() not in (b"", b"\r\n"):
                pass

            parsed = urlsplit(target)
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            state = params.get("state", [None])[0]
            error = params.get("error", [None])[0]

            if parsed.path == "/callback" and code:
                if self._callback is not None and not self._callback.done():
                    self._callback.set_result((code, state))
                status = "200 OK"
                body = "<h1>Signed in</h1><p>You can return to the Cat Shop client.</p>"
            elif error:
                if self._callback is not None and not self._callback.done():
                    self._callback.set_exception(
                        RuntimeError(f"OAuth authorization failed: {error}")
                    )
                status = "400 Bad Request"
                body = "<h1>Sign-in failed</h1><p>You can close this window.</p>"
            else:
                status = "400 Bad Request"
                body = "<h1>Invalid callback</h1><p>You can close this window.</p>"

            response = (
                f"HTTP/1.1 {status}\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                "Connection: close\r\n\r\n"
                f"{body}"
            )
            writer.write(response.encode("utf-8"))
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()


async def open_authorization_page(auth_url: str, *, open_browser: bool) -> None:
    print(f"\nSign in to Cat Shop: {auth_url}\n")
    if open_browser:
        webbrowser.open(auth_url)


def format_agent_response(result: dict[str, Any]) -> str:
    messages = result["messages"]
    content = messages[-1].content
    if isinstance(content, str):
        return content
    return json.dumps(content, indent=2, default=str)


async def ask_agent(agent: Any, prompt: str) -> None:
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )
    print("\nCat Shop:\n")
    print(format_agent_response(result))


async def run_client(
    server_url: str,
    callback_port: int,
    open_browser: bool,
    model_name: str,
    prompt: str,
    interactive: bool,
) -> None:
    server_url = server_url.rstrip("/")
    mcp_url = f"{server_url}/mcp"

    async with OAuthCallbackServer(port=callback_port) as callback_server:
        async def redirect_handler(auth_url: str) -> None:
            await open_authorization_page(auth_url, open_browser=open_browser)

        oauth = OAuthClientProvider(
            server_url=server_url,
            client_metadata=OAuthClientMetadata(
                client_name="Cat Shop LangChain Client",
                redirect_uris=[AnyUrl(callback_server.callback_url)],
                grant_types=["authorization_code", "refresh_token"],
                response_types=["code"],
                scope="read write",
            ),
            storage=InMemoryTokenStorage(),
            redirect_handler=redirect_handler,
            callback_handler=callback_server.wait_for_callback,
        )

        mcp_client = MultiServerMCPClient(
            {
                "cat_shop": {
                    "transport": "streamable_http",
                    "url": mcp_url,
                    "auth": oauth,
                }
            }
        )
        tools = await mcp_client.get_tools()
        print("\nLoaded LangChain tools:", ", ".join(tool.name for tool in tools))

        agent = create_agent(
            ChatOpenAI(model=model_name, temperature=0),
            tools,
            system_prompt=SYSTEM_PROMPT,
        )

        if not interactive:
            await ask_agent(agent, prompt)
            return

        print("\nAsk about the catalog or your cart. Type 'quit' to exit.")
        while True:
            user_prompt = await asyncio.to_thread(input, "\nYou: ")
            if user_prompt.strip().lower() in {"quit", "exit"}:
                return
            if user_prompt.strip():
                await ask_agent(agent, user_prompt)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use a LangChain agent with the Cat Shop MCP server."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Show me the available cat toys and their prices.",
        help="Request for the LangChain agent.",
    )
    parser.add_argument(
        "--server-url",
        default=os.getenv("MCP_SERVER_URL", DEFAULT_SERVER_URL),
        help="Base URL of the MCP server (default: %(default)s).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        help="OpenAI model used by the LangChain agent (default: %(default)s).",
    )
    parser.add_argument(
        "--callback-port",
        type=int,
        default=8765,
        help="Local port that receives the OAuth callback (default: %(default)s).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the sign-in URL without opening a browser.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Keep the LangChain agent running for multiple requests.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in .env before running the LangChain client.")

    asyncio.run(
        run_client(
            server_url=args.server_url,
            callback_port=args.callback_port,
            open_browser=not args.no_browser,
            model_name=args.model,
            prompt=args.prompt,
            interactive=args.interactive,
        )
    )


if __name__ == "__main__":
    main()
