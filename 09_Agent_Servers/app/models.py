from __future__ import annotations

import os

from langchain_openai import ChatOpenAI

DEFAULT_CHAT_MODEL = "gpt-5.4-mini"


def get_chat_model(model_name: str | None = None, *, temperature: float = 0) -> ChatOpenAI:
    name = model_name or os.environ.get("OPENAI_CHAT_MODEL", DEFAULT_CHAT_MODEL)
    return ChatOpenAI(
        model=name,
        temperature=temperature,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )
