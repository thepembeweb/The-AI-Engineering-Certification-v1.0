"""A2A server exposing the cat health specialist agent.

The protocol surface is a minimal, spec-faithful subset of A2A:

- GET /.well-known/agent-card.json  -> the agent card (discovery)
- POST /                            -> JSON-RPC 2.0, method "message/send"

The protocol plumbing (`build_a2a_app`) is deliberately separated from the
intelligence (`specialist_answer`): any agent that maps str -> str can stand
behind the same server. Production systems should use the official a2a-sdk;
this implementation exists so nothing about agent interop is magic.

Run from this folder:

    uv run python server.py
"""

import os
import uuid
from getpass import getpass

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

HOST = "127.0.0.1"
PORT = 9999
SPECIALIST_URL = f"http://{HOST}:{PORT}"

SPECIALIST_CARD = {
    "protocolVersion": "0.3.0",
    "name": "Cat Health Specialist",
    "description": (
        "Educational feline health agent. Answers questions about cat health, "
        "care routines, and behavior. Educational information only - not a "
        "veterinary service; emergencies belong at a clinic."
    ),
    "url": SPECIALIST_URL,
    "version": "1.0.0",
    "capabilities": {"streaming": False, "pushNotifications": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "cat-health-qa",
            "name": "Cat health Q&A",
            "description": (
                "Answers educational questions about feline health, preventive care, "
                "nutrition, and behavior."
            ),
            "tags": ["cats", "health", "education"],
            "examples": [
                "Do indoor cats need flea prevention?",
                "How often should an adult cat see the vet?",
            ],
        }
    ],
}

FELINE_REFERENCE = {
    "dental": (
        "Feline dental disease is common from age three onward. Daily brushing with "
        "cat-specific toothpaste is the gold standard; professional cleanings are "
        "typically needed periodically."
    ),
    "parasites": (
        "Indoor cats still need parasite prevention: fleas arrive on clothing and "
        "other pets, and deworming schedules depend on lifestyle and region."
    ),
    "nutrition": (
        "Cats are obligate carnivores. Adults need meat-based protein and taurine; "
        "senior cats often benefit from higher-moisture diets."
    ),
    "vaccines": (
        "Core feline vaccines include rabies and FVRCP. Boosters follow an initial "
        "kitten series; schedules vary by risk and local regulation."
    ),
}


@tool
def feline_reference(topic: str) -> str:
    """Look up a reference note on a feline health topic such as dental, parasites, nutrition, or vaccines."""
    key = topic.lower().strip()
    for name, entry in FELINE_REFERENCE.items():
        if name in key or key in name:
            return entry
    return f"No reference entry for {topic!r}. Topics: {', '.join(FELINE_REFERENCE)}."


SPECIALIST_SYSTEM_PROMPT = """You are a cat health specialist agent.

Answer questions about feline health, care, and behavior, using the reference
tool when it has a relevant entry. You provide educational information only:
do not diagnose, prescribe, or give dosages, and direct emergencies and
medical decisions to a veterinarian. Answer in at most four sentences."""


def build_specialist_answer():
    """Build the agent and return a plain str -> str callable around it."""
    llm = ChatOpenAI(model=os.environ.get("AIM_CHAT_MODEL", "gpt-5.4-mini"))
    specialist_agent = create_agent(
        model=llm,
        tools=[feline_reference],
        system_prompt=SPECIALIST_SYSTEM_PROMPT,
    )

    def specialist_answer(question: str) -> str:
        result = specialist_agent.invoke(
            {"messages": [{"role": "user", "content": question}]}
        )
        return str(result["messages"][-1].content)

    return specialist_answer


def extract_text(message: dict) -> str:
    """Concatenate the text parts of an A2A message."""
    parts = message.get("parts", [])
    return "\n".join(
        part.get("text", "") for part in parts if part.get("kind") == "text"
    ).strip()


def build_a2a_app(agent_card: dict, answer) -> FastAPI:
    """A minimal A2A server: an agent card plus JSON-RPC message/send."""
    app = FastAPI(title=agent_card["name"])

    @app.get("/.well-known/agent-card.json")
    def get_agent_card() -> dict:
        return agent_card

    @app.post("/")
    def handle_rpc(request: dict) -> JSONResponse:
        request_id = request.get("id")

        def rpc_error(code: int, message: str) -> JSONResponse:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": code, "message": message},
                }
            )

        if request.get("jsonrpc") != "2.0":
            return rpc_error(-32600, "Invalid request: expected jsonrpc '2.0'")
        if request.get("method") != "message/send":
            return rpc_error(-32601, f"Method not found: {request.get('method')!r}")

        text = extract_text(request.get("params", {}).get("message", {}))
        if not text:
            return rpc_error(-32602, "Invalid params: message contains no text parts")

        reply = {
            "kind": "message",
            "role": "agent",
            "parts": [{"kind": "text", "text": answer(text)}],
            "messageId": str(uuid.uuid4()),
        }
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": reply})

    return app


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass("OpenAI API Key: ")

    app = build_a2a_app(SPECIALIST_CARD, build_specialist_answer())
    print(f"{SPECIALIST_CARD['name']} serving A2A at {SPECIALIST_URL}")
    print(f"Agent card: {SPECIALIST_URL}/.well-known/agent-card.json")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
