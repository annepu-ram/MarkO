"""Model backend for campaign-driven RAG generation."""
import logging
import os
import re
import time
import traceback

from campaign.rag_config import campaign_rag_config


campaign_rag_config.logs_dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("campaign_rag_backend")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(campaign_rag_config.logs_dir / "campaign_rag_errors.log", encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

_THINK_BLOCK_RE = re.compile(r"<think\b[^>]*>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text):
    return _THINK_BLOCK_RE.sub("", text or "").lstrip()


class CampaignModelBackend:
    def generate(self, system, user_prompt, *, model_override="", temperature_override=None):
        backend = campaign_rag_config.model_backend
        model = model_override or campaign_rag_config.model_name
        temperature = temperature_override if temperature_override is not None else campaign_rag_config.temperature_ollama
        started = time.time()
        logger.info("CALL %s/%s | system=%s user=%s", backend, model, len(system or ""), len(user_prompt or ""))
        try:
            if backend == "ollama":
                raw = self._ollama(system, user_prompt, model=model, temperature=temperature)
            elif backend == "openai":
                raw = self._openai(system, user_prompt, model=model, temperature=temperature)
            elif backend == "anthropic":
                raw = self._anthropic(system, user_prompt, model=model, temperature=temperature)
            elif backend == "groq":
                raw = self._groq(system, user_prompt, model=model, temperature=temperature)
            else:
                raise ValueError(f"Unknown campaign RAG backend: {backend}")
            logger.info("OK %s/%s | chars=%s | %.1fs", backend, model, len(raw or ""), time.time() - started)
            return _strip_thinking(raw)
        except Exception as exc:
            logger.error(
                "FAIL %s/%s | %.1fs | %s: %s\n%s",
                backend,
                model,
                time.time() - started,
                type(exc).__name__,
                exc,
                traceback.format_exc(),
            )
            raise

    def _ollama(self, system, user_prompt, *, model, temperature):
        import ollama as ollama_pkg

        host = os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL")
        api_key = os.getenv("OLLAMA_API_KEY", "")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        client = ollama_pkg.Client(host=host, headers=headers)
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": temperature,
                "num_predict": campaign_rag_config.max_generation_tokens,
            },
        )
        return response.message.content

    def _openai(self, system, user_prompt, *, model, temperature):
        import openai

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=campaign_rag_config.max_generation_tokens,
        )
        return response.choices[0].message.content

    def _anthropic(self, system, user_prompt, *, model, temperature):
        import anthropic

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
            max_tokens=campaign_rag_config.max_generation_tokens,
        )
        return response.content[0].text

    def _groq(self, system, user_prompt, *, model, temperature):
        import groq

        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=campaign_rag_config.max_generation_tokens,
        )
        return response.choices[0].message.content
