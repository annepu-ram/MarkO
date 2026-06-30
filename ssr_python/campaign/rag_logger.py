"""Prompt/output logging for campaign-driven RAG generation."""
import logging
from datetime import datetime

from campaign.rag_config import campaign_rag_config


logger = logging.getLogger("campaign_rag")
if not logger.handlers:
    campaign_rag_config.logs_dir.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        campaign_rag_config.logs_dir / "campaign_rag_prompts.log",
        encoding="utf-8",
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)


def log_campaign_prompt(label, system, user_prompt, *, metadata=None):
    metadata = metadata or {}
    total = len(system or "") + len(user_prompt or "")
    logger.info(
        "%s PROMPT | total=%s system=%s user=%s metadata=%s\nSYSTEM:\n%s\nUSER:\n%s",
        label,
        total,
        len(system or ""),
        len(user_prompt or ""),
        metadata,
        system,
        user_prompt,
    )


def log_campaign_output(label, output, *, metadata=None):
    metadata = metadata or {}
    logger.info(
        "%s OUTPUT | chars=%s metadata=%s\n%s",
        label,
        len(output or ""),
        metadata,
        output,
    )


def prompt_log_metadata(**kwargs):
    data = {"logged_at": datetime.utcnow().isoformat()}
    data.update({key: value for key, value in kwargs.items() if value not in (None, "", [])})
    return data
