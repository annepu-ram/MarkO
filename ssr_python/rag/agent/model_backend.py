"""ssr_python/rag/agent/model_backend.py — Pluggable generation backend."""
import logging
import os
import re
import time
import traceback

from rag.config import config

_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
os.makedirs(_log_dir, exist_ok=True)

_logger = logging.getLogger("llm_backend")
if not _logger.handlers:
    _logger.setLevel(logging.DEBUG)
    _fh = logging.FileHandler(os.path.join(_log_dir, "llm_errors.log"), encoding="utf-8")
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    _logger.addHandler(_fh)

_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text: str) -> str:
    if not text:
        return text
    return _THINK_BLOCK_RE.sub("", text).lstrip()


class ModelBackend:
    """Pluggable generation backend. Switch via config.model_backend."""

    def generate(self, system: str, user_prompt: str, *, model_override: str = "", temperature_override: float | None = None) -> str:
        backend = config.model_backend
        model = model_override or config.model_name
        temperature = temperature_override if temperature_override is not None else config.temperature_ollama
        _logger.info(f"CALL {backend}/{model} | system={len(system)} chars | user={len(user_prompt)} chars")
        t0 = time.time()
        try:
            if backend == "ollama":
                raw = self._ollama(system, user_prompt, model=model, temperature=temperature)
            elif backend == "openai":
                raw = self._openai(system, user_prompt)
            elif backend == "anthropic":
                raw = self._anthropic(system, user_prompt)
            elif backend == "groq":
                raw = self._groq(system, user_prompt)
            else:
                raise ValueError(f"Unknown backend: {backend}")
            elapsed = time.time() - t0
            _logger.info(f"OK {backend}/{model} | {len(raw)} chars | {elapsed:.1f}s")
            return _strip_thinking(raw)
        except Exception as e:
            elapsed = time.time() - t0
            _logger.error(
                f"FAIL {backend}/{model} | {elapsed:.1f}s | {type(e).__name__}: {e}\n"
                f"{traceback.format_exc()}"
            )
            raise

    # -- Ollama (local or cloud) --

    def _ollama(self, system: str, user_prompt: str, *, model: str, temperature: float) -> str:
        import ollama as _ollama_pkg

        host = os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL")
        api_key = os.getenv("OLLAMA_API_KEY", "")
        _logger.debug(f"Ollama host={host} api_key={'set' if api_key else 'missing'}")

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        client = _ollama_pkg.Client(host=host, headers=headers)

        resp = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": temperature, "num_predict": config.max_generation_tokens},
        )
        return resp.message.content

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
