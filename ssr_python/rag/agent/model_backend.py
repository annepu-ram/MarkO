"""ssr_python/rag/agent/model_backend.py — Pluggable generation backend."""
import os
import re
import requests

from rag.config import config


_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text: str) -> str:
    if not text:
        return text
    return _THINK_BLOCK_RE.sub("", text).lstrip()


class ModelBackend:
    """Pluggable generation backend. Switch via config.model_backend."""

    def generate(self, system: str, user_prompt: str) -> str:
        backend = config.model_backend
        if backend == "ollama":
            raw = self._ollama(system, user_prompt)
        elif backend == "openai":
            raw = self._openai(system, user_prompt)
        elif backend == "anthropic":
            raw = self._anthropic(system, user_prompt)
        elif backend == "groq":
            raw = self._groq(system, user_prompt)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        return _strip_thinking(raw)

    # -- Ollama (local or cloud) --

    def _ollama(self, system: str, user_prompt: str) -> str:
        # Reuse the same OLLAMA_BASE_URL / OLLAMA_API_KEY from .env
        # so RAG works with both local and Ollama Cloud
        base_url = os.getenv("RAG_OLLAMA_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        api_key = os.getenv("OLLAMA_API_KEY", "")

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        resp = requests.post(
            f"{base_url}/api/generate",
            headers=headers,
            json={
                "model": config.model_name,
                "system": system,
                "prompt": user_prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": config.temperature_ollama, "num_predict": config.max_generation_tokens},
            },
            timeout=600,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    # -- OpenAI --

    def _openai(self, system: str, user_prompt: str) -> str:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=config.temperature_cloud,
            max_tokens=config.max_generation_tokens,
        )
        return resp.choices[0].message.content

    # -- Anthropic --

    def _anthropic(self, system: str, user_prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model=config.model_name,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=config.temperature_cloud,
            max_tokens=config.max_generation_tokens,
        )
        return resp.content[0].text

    # -- Groq --

    def _groq(self, system: str, user_prompt: str) -> str:
        import groq
        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=config.temperature_cloud,
            max_tokens=config.max_generation_tokens,
        )
        return resp.choices[0].message.content
