"""
agents/base_agent.py
Abstract base class that every agent inherits.
Handles: Gemini calls, JSON parsing, DB logging, retry, timing.
"""
import re
import json
import os
import time
import streamlit as st

from config.settings import (
    GEMINI_MODEL, GEMINI_MAX_TOKENS,
    GEMINI_TEMPERATURE, GEMINI_RETRY_COUNT, GEMINI_RETRY_DELAY_S
)
from database import db


class BaseAgent:
    """
    Concrete agents only need to:
    1. Set `name` class attribute.
    2. Define a `system_prompt` class attribute.
    3. Call `self._call(prompt)` or `self._call_structured(prompt)`.
    """

    name: str = "Base Agent"
    system_prompt: str = "You are a helpful assistant."

    # ── Core LLM call ──────────────────────────────────────────────────────────

    def _call(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float | None = None,
        user_id: int | None = None,
        action: str = "call",
    ) -> str:
        """
        Call Gemini with the given prompt.
        Returns raw text. Retries on transient errors.
        """
        from google import genai
        from google.genai import types

        # ── Resolve API key (3 sources) ───────────────────────────────────────
        api_key = ""

        # 1. st.session_state (set via sidebar Save button)
        try:
            api_key = st.session_state.get("api_key", "").strip()
        except Exception:
            pass

        # 2. .streamlit/secrets.toml
        if not api_key:
            try:
                api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
            except Exception:
                pass

        # 3. .env / OS environment variable
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY", "").strip()

        if not api_key:
            raise ValueError(
                "❌ Gemini API key not found!\n\n"
                "How to fix:\n"
                "  • Open the sidebar → '🔑 API Key' → paste your key → click 'Save Key'\n"
                "  OR\n"
                "  • Add  GEMINI_API_KEY=your_key  to the .env file in the project folder\n\n"
                "Get a free key at: https://aistudio.google.com/app/apikey"
            )

        client = genai.Client(api_key=api_key)

        # Use model from sidebar selector, fall back to settings default
        model = (
            st.session_state.get("gemini_model", "").strip()
            or GEMINI_MODEL
        )

        sys = system if system is not None else self.system_prompt
        temp = temperature if temperature is not None else GEMINI_TEMPERATURE

        gen_cfg = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=GEMINI_MAX_TOKENS,
            system_instruction=sys if sys else None,
        )

        last_error = None
        for attempt in range(GEMINI_RETRY_COUNT):
            start = time.time()
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=gen_cfg,
                )
                text = response.text
                elapsed_ms = int((time.time() - start) * 1000)
                if user_id:
                    db.log_agent(
                        user_id, self.name, action,
                        prompt[:500], text[:500],
                        elapsed_ms, "success",
                    )
                return text
            except Exception as exc:
                last_error = exc
                elapsed_ms = int((time.time() - start) * 1000)
                if user_id:
                    db.log_agent(
                        user_id, self.name, action,
                        prompt[:500], "",
                        elapsed_ms, "error", str(exc),
                    )

                err_str = str(exc)

                # 429 quota exhausted — wait longer and warn user
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = 15 * (attempt + 1)   # 15s, 30s, 45s
                    if attempt < GEMINI_RETRY_COUNT - 1:
                        time.sleep(wait)
                    else:
                        raise RuntimeError(
                            "⚠️ Gemini API quota exhausted.\n\n"
                            "Quick fixes:\n"
                            "  1. Switch to **gemini-1.5-flash-8b** in the sidebar "
                            "(🤖 Gemini Model) — it has the highest free quota.\n"
                            "  2. Wait a minute and try again — free tier resets every 60 seconds.\n"
                            "  3. Enable billing at console.cloud.google.com for unlimited usage."
                        )
                elif attempt < GEMINI_RETRY_COUNT - 1:
                    time.sleep(GEMINI_RETRY_DELAY_S * (2 ** attempt))

        raise RuntimeError(
            f"{self.name} failed after {GEMINI_RETRY_COUNT} attempts: {last_error}"
        )

    def _call_structured(
        self,
        prompt: str,
        *,
        system: str | None = None,
        user_id: int | None = None,
        action: str = "call_structured",
    ) -> str:
        """
        Call Gemini expecting JSON output.
        Appends a strict JSON-only instruction and uses lower temperature.
        """
        json_suffix = (
            "\n\nCRITICAL: Respond with ONLY valid JSON. "
            "No markdown fences, no backtick blocks, no preamble, no explanation."
        )
        return self._call(
            prompt + json_suffix,
            system=system,
            temperature=0.2,
            user_id=user_id,
            action=action,
        )

    # ── JSON helpers ───────────────────────────────────────────────────────────

    def _parse_json(self, text: str) -> dict | list:
        """
        Strip markdown fences and parse JSON.
        Returns `{"raw": text}` on failure so callers can handle gracefully.
        """
        cleaned = text.strip()
        # Strip ```json … ``` or ``` … ```
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find the outermost JSON object / array
            for start_char, end_char in [("{", "}"), ("[", "]")]:
                start = cleaned.find(start_char)
                end   = cleaned.rfind(end_char)
                if start != -1 and end != -1 and end > start:
                    try:
                        return json.loads(cleaned[start: end + 1])
                    except json.JSONDecodeError:
                        pass

        return {"raw": text}

    def _call_and_parse(
        self,
        prompt: str,
        *,
        system: str | None = None,
        user_id: int | None = None,
        action: str = "call_and_parse",
    ) -> dict | list:
        """Convenience: structured call + parse in one step."""
        raw = self._call_structured(
            prompt, system=system, user_id=user_id, action=action
        )
        return self._parse_json(raw)

    # ── Conversation memory ────────────────────────────────────────────────────

    def save_message(self, user_id: int, role: str, content: str) -> None:
        db.save_message(user_id, self.name, role, content)

    def get_history(self, user_id: int, limit: int = 20) -> list[dict]:
        return db.get_conversation(user_id, self.name, limit)

    def build_history_prompt(self, user_id: int, new_user_message: str) -> str:
        """
        Prepend recent conversation history to the new prompt so the agent
        maintains context across turns.
        """
        history = self.get_history(user_id)
        if not history:
            return new_user_message

        lines = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        lines.append(f"User: {new_user_message}")
        return "\n".join(lines)

    # ── Utility ────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
