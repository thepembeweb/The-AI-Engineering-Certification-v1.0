"""A2A client: discover an agent from its card and send it a message.

Deliberately shares no code with server.py — the card and the JSON-RPC
messages are the entire interface between the two sides. The small
`extract_text` helper is duplicated on purpose.

Run from this folder (with server.py running in another terminal):

    uv run python client.py "Do indoor cats need flea prevention?"
"""

import sys
import uuid

import httpx

BASE_URL = "http://127.0.0.1:9999"

def extract_text(message: dict) -> str:
    """Concatenate the text parts of an A2A message."""
    parts = message.get("parts", [])
    return "\n".join(
        part.get("text", "") for part in parts if part.get("kind") == "text"
    ).strip()


def fetch_agent_card(base_url: str) -> dict:
    response = httpx.get(f"{base_url}/.well-known/agent-card.json", timeout=10)
    response.raise_for_status()
    return response.json()


def send_message(base_url: str, text: str, timeout: float = 120.0) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": str(uuid.uuid4()),
            }
        },
    }
    response = httpx.post(base_url, json=payload, timeout=timeout)
    response.raise_for_status()
    body = response.json()
    if "error" in body:
        raise RuntimeError(f"A2A error {body['error']['code']}: {body['error']['message']}")
    return extract_text(body["result"])


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "How often should an adult indoor cat see the vet?"

    card = fetch_agent_card(BASE_URL)
    print(f"Discovered: {card['name']} (v{card['version']}, protocol {card['protocolVersion']})")
    print(f"  {card['description']}")
    for skill in card["skills"]:
        print(f"  skill: {skill['id']} - {skill['description']}")

    print(f"\nQ: {question}")
    print(f"A: {send_message(BASE_URL, question)}")
