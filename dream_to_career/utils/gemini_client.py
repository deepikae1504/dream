"""
utils/gemini_client.py
Thin Gemini API wrapper using the modern `google-genai` SDK.

NOTE: agents/base_agent.py now calls the SDK directly for full control
over retries and logging. This module is kept as a lightweight standalone
helper for any one-off script or notebook usage outside the agent framework.
"""
import time
import os
import streamlit as st
from google import genai
from google.genai import types

from config.settings import GEMINI_MODEL, GEMINI_MAX_TOKENS, GEMINI_KEY_ENV


def get_api_key() -> str:
    key = st.session_state.get("api_key") if hasattr(st, "session_state") else ""
    return key or os.environ.get(GEMINI_KEY_ENV, "")


def call_gemini(prompt: str, system_prompt: str = "", max_retries: int = 3,
                temperature: float = 0.7) -> str:
    """Call Gemini with retry logic. Returns text response."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Please enter your API key in the sidebar.")

    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=GEMINI_MAX_TOKENS,
        system_instruction=system_prompt if system_prompt else None,
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_error


def call_gemini_structured(prompt: str, system_prompt: str = "") -> str:
    """Call Gemini expecting JSON output."""
    json_instruction = (
        "\n\nIMPORTANT: Respond ONLY with valid JSON. "
        "No markdown, no backticks, no explanation."
    )
    return call_gemini(prompt + json_instruction, system_prompt, temperature=0.3)
