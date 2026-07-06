from __future__ import annotations

from typing import Any
from typing import TypedDict

from langchain_core.messages import AIMessage
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.graph import StateGraph

from app.graphs.simple_agent import graph as simple_agent_graph
from app.models import get_chat_model

MAX_ATTEMPTS = 3
HELPFULNESS_SYSTEM_PROMPT = (
    "You are a strict helpfulness judge for cat-health assistant responses. "
    "Reply with exactly one character: Y (helpful) or N (not helpful)."
)
RETRY_NUDGE = (
    "That answer was not helpful enough. Try again and provide a clearer, more "
    "actionable answer for the user."
)


class HelpfulnessState(TypedDict, total=False):
    messages: list[BaseMessage]
    attempts: int
    helpfulness_verdict: str


def _latest_content(messages: list[BaseMessage], message_type: type[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, message_type):
            return str(message.content)
    return ""


def _parse_verdict(value: str) -> str:
    normalized = (value or "").strip().upper()
    return "Y" if normalized.startswith("Y") else "N"


def _agent_node(state: HelpfulnessState) -> dict[str, Any]:
    messages = state.get("messages", [])
    result = simple_agent_graph.invoke({"messages": messages})
    return {
        "messages": result["messages"],
        "attempts": int(state.get("attempts", 0)) + 1,
    }


def _helpfulness_node(state: HelpfulnessState) -> dict[str, Any]:
    messages = state.get("messages", [])
    user_query = _latest_content(messages, HumanMessage)
    latest_answer = _latest_content(messages, AIMessage)

    judge = get_chat_model()
    verdict_message = judge.invoke(
        [
            SystemMessage(content=HELPFULNESS_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "User query:\n"
                    f"{user_query}\n\n"
                    "Assistant answer:\n"
                    f"{latest_answer}\n\n"
                    "Is this answer helpful for the user? Respond Y or N only."
                )
            ),
        ]
    )
    verdict = _parse_verdict(str(verdict_message.content))

    if verdict == "N" and int(state.get("attempts", 0)) < MAX_ATTEMPTS:
        return {
            "messages": [*messages, HumanMessage(content=RETRY_NUDGE)],
            "helpfulness_verdict": verdict,
        }

    return {
        "messages": messages,
        "helpfulness_verdict": verdict,
    }


def _route_after_helpfulness(state: HelpfulnessState) -> str:
    if (
        state.get("helpfulness_verdict") == "N"
        and int(state.get("attempts", 0)) < MAX_ATTEMPTS
    ):
        return "agent"
    return "end"


builder = StateGraph(HelpfulnessState)
builder.add_node("agent", _agent_node)
builder.add_node("helpfulness", _helpfulness_node)
builder.set_entry_point("agent")
builder.add_edge("agent", "helpfulness")
builder.add_conditional_edges(
    "helpfulness",
    _route_after_helpfulness,
    {
        "agent": "agent",
        "end": END,
    },
)

graph = builder.compile()
