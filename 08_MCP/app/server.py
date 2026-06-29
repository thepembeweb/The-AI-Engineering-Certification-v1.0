import os
import socket

from mcp.server.auth.settings import (
    AuthSettings,
    ClientRegistrationOptions,
    RevocationOptions,
)
from mcp.server.fastmcp import FastMCP

from .oauth import CatShopOAuthProvider

SERVER_HOST = os.environ.get("HOST", "0.0.0.0")
REQUESTED_PORT = int(os.environ.get("PORT", "8000"))


def _find_available_port(start_port: int, search_limit: int = 100) -> int:
    for port in range(start_port, start_port + search_limit):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((SERVER_HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No available port found starting at {start_port}")


SERVER_PORT = _find_available_port(REQUESTED_PORT)
ISSUER_URL = os.environ.get("ISSUER_URL", f"http://localhost:{SERVER_PORT}")

oauth_provider = CatShopOAuthProvider(issuer_url=ISSUER_URL)

mcp = FastMCP(
    "Cat Shop",
    auth_server_provider=oauth_provider,
    auth=AuthSettings(
        issuer_url=ISSUER_URL,
        resource_server_url=ISSUER_URL,
        client_registration_options=ClientRegistrationOptions(
            enabled=True,
            valid_scopes=["read", "write"],
            default_scopes=["read", "write"],
        ),
        revocation_options=RevocationOptions(enabled=True),
    ),
    host=SERVER_HOST,
    port=SERVER_PORT,
)
