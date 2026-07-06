"""Model utilities for constructing chat LLM clients.

Centralizes configuration of the default chat model and temperature so graphs can
import a single helper without repeating provider-specific wiring.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def get_chat_model(model_name: str | None = None, *, temperature: float = 0) -> Any:
    """Return a configured LangChain chat model based on LLM_PROVIDER env var.
    
    Supports:
    - "fireworks" (default): Uses Fireworks AI via OpenAI-compatible API
    - "ollama": Uses local Ollama server
    """
    provider = os.environ.get("LLM_PROVIDER", "fireworks").lower()
    
    if provider == "ollama":
        ollama_model = os.environ.get("OLLAMA_CHAT_MODEL", "llama3.2")
        return ChatOllama(
            model=ollama_model,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
        )
    else:  # fireworks (default)
        name = model_name or os.environ.get(
            "FIREWORKS_CHAT_MODEL", "accounts/fireworks/models/gpt-oss-20b"
        )
        return ChatOpenAI(
            model=name,
            temperature=temperature,
            openai_api_key=os.environ["FIREWORKS_API_KEY"],
            openai_api_base=FIREWORKS_BASE_URL,
        )


def fix_tool_calls(response: AIMessage) -> AIMessage:
    """Fix invalid tool calls caused by models appending extra tokens like <|call|>."""
    if not response.invalid_tool_calls:
        return response

    fixed = list(response.tool_calls)
    remaining_invalid = []

    for tc in response.invalid_tool_calls:
        cleaned = re.sub(r"\s*<\|call\|>\s*$", "", tc["args"])
        try:
            parsed = json.loads(cleaned)
            fixed.append(
                {
                    "name": tc["name"],
                    "args": parsed,
                    "id": tc["id"],
                    "type": "tool_call",
                }
            )
        except (json.JSONDecodeError, TypeError):
            remaining_invalid.append(tc)

    response.tool_calls = fixed
    response.invalid_tool_calls = remaining_invalid
    return response
