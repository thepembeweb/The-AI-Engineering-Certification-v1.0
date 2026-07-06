from __future__ import annotations

from langchain.agents import create_agent

from app.models import get_chat_model
from app.tools import get_tool_belt

SYSTEM_PROMPT = (
    "You are a helpful assistant specialized in feline (cat) health. "
    "Use the retrieve_information tool for cat-health questions, web search for "
    "current information, and Arxiv for research papers. Cite tool results when "
    "they inform your answer."
)

graph = create_agent(
    model=get_chat_model(),
    tools=get_tool_belt(),
    system_prompt=SYSTEM_PROMPT,
)
