import argparse
import asyncio
import json
import os
import webbrowser
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken
from pydantic import AnyUrl

DEFAULT_SERVER_URL = "http://localhost:8000"
DEFAULT_CALLBACK_PORT = 8765
DEFAULT_SEARCH_QUERY = "toy"


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
    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_CALLBACK_PORT) -> None:
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

            while True:
                line = await reader.readline()
                if line in (b"", b"\r\n"):
                    break

            parsed = urlsplit(target)
            params = parse_qs(parsed.query)
            code = params.get("code", [None])[0]
            state = params.get("state", [None])[0]
            error = params.get("error", [None])[0]

            if parsed.path == "/callback" and code:
                if self._callback is not None and not self._callback.done():
                    self._callback.set_result((code, state))
                status = "200 OK"
                body = "<h1>Signed in</h1><p>You can return to the advanced MCP client.</p>"
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
        await asyncio.to_thread(webbrowser.open, auth_url)


def _extract_single_text(raw: Any) -> str | None:
    if not isinstance(raw, list) or len(raw) != 1 or not isinstance(raw[0], dict):
        return None
    if raw[0].get("type") != "text":
        return None
    text_value = raw[0].get("text")
    return text_value if isinstance(text_value, str) else None


def normalize_tool_result(raw: Any) -> Any:
    text_value = _extract_single_text(raw)
    if text_value is None:
        return raw

    stripped = text_value.strip()
    if not stripped:
        return ""

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return stripped


def unwrap_result_payload(payload: Any) -> Any:
    if isinstance(payload, dict) and "result" in payload and len(payload) == 1:
        return payload["result"]
    return payload


class AdvancedMCPClient:
    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def list_tools(self) -> list[str]:
        tool_result = await self.session.list_tools()
        return [tool.name for tool in tool_result.tools]

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        result = await self.session.call_tool(tool_name, arguments)
        if result.structuredContent is not None:
            return unwrap_result_payload(normalize_tool_result(result.structuredContent))

        content_payload = [item.model_dump(mode="json") for item in result.content]
        return unwrap_result_payload(normalize_tool_result(content_payload))

    async def run_workflow(self, query: str, category: str | None, quantity: int) -> None:
        print("\nRunning workflow: browse -> search -> add_to_cart -> view_cart -> checkout\n")

        products = await self.call_tool("list_products")
        print("list_products =>")
        print(json.dumps(products, indent=2, ensure_ascii=True))

        search_args: dict[str, Any] = {"query": query}
        if category:
            search_args["category"] = category

        search_results = await self.call_tool("search_products", search_args)
        print("\nsearch_products =>")
        print(json.dumps(search_results, indent=2, ensure_ascii=True))

        chosen = None
        if isinstance(search_results, list) and search_results:
            chosen = search_results[0]
        elif isinstance(products, list) and products:
            chosen = products[0]

        if not isinstance(chosen, dict) or "id" not in chosen:
            raise RuntimeError("No product available to continue workflow.")

        product_id = int(chosen["id"])
        details = await self.call_tool("get_product", {"product_id": product_id})
        print("\nget_product =>")
        print(json.dumps(details, indent=2, ensure_ascii=True))

        add_result = await self.call_tool(
            "add_to_cart", {"product_id": product_id, "quantity": quantity}
        )
        print("\nadd_to_cart =>")
        print(json.dumps(add_result, indent=2, ensure_ascii=True))

        cart_before = await self.call_tool("view_cart")
        print("\nview_cart (before checkout) =>")
        print(json.dumps(cart_before, indent=2, ensure_ascii=True))

        order = await self.call_tool("checkout")
        print("\ncheckout =>")
        print(json.dumps(order, indent=2, ensure_ascii=True))

        cart_after = await self.call_tool("view_cart")
        print("\nview_cart (after checkout) =>")
        print(json.dumps(cart_after, indent=2, ensure_ascii=True))


async def run_client(
    server_url: str,
    callback_port: int,
    open_browser_flag: bool,
    query: str,
    category: str | None,
    quantity: int,
) -> None:
    server_url = server_url.rstrip("/")
    mcp_url = f"{server_url}/mcp"

    async with OAuthCallbackServer(port=callback_port) as callback_server:
        async def redirect_handler(auth_url: str) -> None:
            await open_authorization_page(auth_url, open_browser=open_browser_flag)

        oauth = OAuthClientProvider(
            server_url=server_url,
            client_metadata=OAuthClientMetadata(
                client_name="Cat Shop Advanced MCP Client",
                redirect_uris=[AnyUrl(callback_server.callback_url)],
                grant_types=["authorization_code", "refresh_token"],
                response_types=["code"],
                scope="read write",
            ),
            storage=InMemoryTokenStorage(),
            redirect_handler=redirect_handler,
            callback_handler=callback_server.wait_for_callback,
        )

        async with httpx.AsyncClient(auth=oauth, timeout=30.0) as http_client:
            async with streamable_http_client(mcp_url, http_client=http_client) as streams:
                read_stream, write_stream, _ = streams
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    app = AdvancedMCPClient(session)

                    tools = await app.list_tools()
                    print("\nAvailable tools:", ", ".join(tools))

                    await app.run_workflow(query=query, category=category, quantity=quantity)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Advanced custom MCP client using Streamable HTTP + OAuth."
    )
    parser.add_argument(
        "--server-url",
        default=os.getenv("MCP_SERVER_URL", DEFAULT_SERVER_URL),
        help="Base URL of the MCP server (default: %(default)s).",
    )
    parser.add_argument(
        "--callback-port",
        type=int,
        default=DEFAULT_CALLBACK_PORT,
        help="Local port that receives OAuth callback (default: %(default)s).",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_SEARCH_QUERY,
        help="Keyword used for search_products in the workflow.",
    )
    parser.add_argument(
        "--category",
        default=None,
        help="Optional category filter used with search_products.",
    )
    parser.add_argument(
        "--quantity",
        type=int,
        default=1,
        help="Quantity used when adding selected product to cart.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print sign-in URL without opening a browser window.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    if args.quantity < 1:
        raise SystemExit("--quantity must be at least 1")

    asyncio.run(
        run_client(
            server_url=args.server_url,
            callback_port=args.callback_port,
            open_browser_flag=not args.no_browser,
            query=args.query,
            category=args.category,
            quantity=args.quantity,
        )
    )


if __name__ == "__main__":
    main()
