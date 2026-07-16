"""Front-desk agent that delegates cat health questions to the remote specialist via A2A.

The front desk handles greetings, clinic hours, and appointment guidance
itself, and consults the specialist for substantive cat health questions.
Two things make this real delegation rather than a hardcoded pipeline:

- Its knowledge of the specialist comes from the *fetched agent card*: the
  discovered description is injected into the system prompt. Publish a better
  card and every client that discovers you routes better — no client changes.
- The specialist is just a tool from the front desk's point of view; the
  front desk's model decides per-question whether to use it.

Run from this folder (with server.py running in another terminal):

    uv run python front_desk.py "My kitten keeps sneezing. Should I be worried?"
"""

import os
import sys
from getpass import getpass

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from client import BASE_URL, fetch_agent_card, send_message


@tool
def consult_cat_health_specialist(question: str) -> str:
    """Consult the remote cat health specialist agent with one clearly-phrased question about cats."""
    return send_message(BASE_URL, question)


def build_front_desk(specialist_card: dict):
    system_prompt = f"""You are the front-desk assistant for the Whisker Falls veterinary clinic website.

Handle these yourself: greetings, clinic information, and appointment guidance.
Clinic hours: Monday-Saturday 9am-6pm. Appointments are booked by phone.

For substantive cat health questions, consult this remote specialist and relay
its answer, attributing it to the specialist by name:

- {specialist_card["name"]}: {specialist_card["description"]}

For emergencies, skip the specialist and direct the user to the nearest
emergency clinic immediately."""

    llm = ChatOpenAI(model=os.environ.get("AIM_CHAT_MODEL", "gpt-5.4-mini"))
    return create_agent(
        model=llm,
        tools=[consult_cat_health_specialist],
        system_prompt=system_prompt,
    )


def visit_front_desk(front_desk_agent, question: str) -> None:
    """Ask the front desk one question and print the delegation trace."""
    result = front_desk_agent.invoke({"messages": [{"role": "user", "content": question}]})
    print(f"Q: {question}")
    for message in result["messages"]:
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"   [front desk -> A2A] {call['name']}({call['args']})")
        elif message.type == "tool":
            preview = str(message.content).replace("\n", " ")[:100]
            print(f"   [A2A -> front desk] {preview}...")
    print(f"A: {result['messages'][-1].content}")
    print("-" * 72)


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass("OpenAI API Key: ")

    specialist_card = fetch_agent_card(BASE_URL)
    print(f"Discovered specialist via A2A card: {specialist_card['name']}\n")
    front_desk_agent = build_front_desk(specialist_card)

    if len(sys.argv) > 1:
        visit_front_desk(front_desk_agent, " ".join(sys.argv[1:]))
    else:
        # Default demo: one question the front desk answers itself,
        # one it delegates across the protocol.
        visit_front_desk(front_desk_agent, "What are your clinic hours?")
        visit_front_desk(front_desk_agent, "My kitten keeps sneezing. Should I be worried?")
