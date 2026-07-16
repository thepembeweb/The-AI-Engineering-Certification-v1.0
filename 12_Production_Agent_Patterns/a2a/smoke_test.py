"""Protocol smoke test for the A2A server — no API key or network needed.

Stands a stub agent (echo) behind the real server plumbing and checks the
protocol surface: card discovery, message/send round-trip, and the JSON-RPC
error codes. Run from this folder:

    uv run python smoke_test.py
"""

from fastapi.testclient import TestClient

from server import SPECIALIST_CARD, build_a2a_app, extract_text


def main() -> None:
    app = build_a2a_app(SPECIALIST_CARD, answer=lambda text: f"ECHO:{text}")
    client = TestClient(app)

    card = client.get("/.well-known/agent-card.json").json()
    assert card["name"] == SPECIALIST_CARD["name"], card
    assert card["skills"][0]["id"] == "cat-health-qa", card
    print("PASS  agent card served at /.well-known/agent-card.json")

    body = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "role": "user",
                    "parts": [{"kind": "text", "text": "hello specialist"}],
                    "messageId": "m1",
                }
            },
        },
    ).json()
    assert extract_text(body["result"]) == "ECHO:hello specialist", body
    assert body["result"]["role"] == "agent", body
    print("PASS  message/send round-trip")

    body = client.post(
        "/", json={"jsonrpc": "2.0", "id": "2", "method": "tasks/get", "params": {}}
    ).json()
    assert body["error"]["code"] == -32601, body
    print("PASS  unknown method returns -32601")

    body = client.post(
        "/",
        json={
            "jsonrpc": "2.0",
            "id": "3",
            "method": "message/send",
            "params": {"message": {"parts": []}},
        },
    ).json()
    assert body["error"]["code"] == -32602, body
    print("PASS  empty message returns -32602")

    body = client.post("/", json={"id": "4", "method": "message/send"}).json()
    assert body["error"]["code"] == -32600, body
    print("PASS  missing jsonrpc envelope returns -32600")

    print("\nAll A2A protocol smoke tests passed.")


if __name__ == "__main__":
    main()
