"""ssr_python/rag/agent/prompt_logger.py — Shared prompt monitoring utilities."""
import re
import logging

logger = logging.getLogger(__name__)


def log_prompt(label: str, system: str, user_prompt: str, max_chunk_lines: int = 5):
    """Log system + user prompts with collapsed chunks and char counts.

    - Collapses each chunk block (between --- markers) to max_chunk_lines
    - Logs char counts for system, user, and total input
    """
    collapsed = collapse_chunks(user_prompt, max_chunk_lines)
    total = len(system) + len(user_prompt)
    logger.info(f"{label} SYSTEM PROMPT ({len(system)} chars):\n{system}")
    logger.info(f"{label} USER PROMPT ({len(user_prompt)} chars):\n{collapsed}")
    logger.info(f"{label} TOTAL INPUT: {total} chars")


def log_output(label: str, response: str):
    """Log LLM output with char count."""
    logger.info(f"{label} OUTPUT ({len(response)} chars):\n{response}")


def collapse_chunks(text: str, max_lines: int = 5) -> str:
    """Collapse each chunk block (between --- markers) to max_lines.

    Chunk blocks start with '--- ' markers. Content between consecutive
    markers is truncated to max_lines with a summary of omitted lines.
    """
    def _truncate_block(match):
        header = match.group(1)
        body = match.group(2)
        lines = body.strip().splitlines()
        if len(lines) <= max_lines:
            return match.group(0)
        kept = '\n'.join(lines[:max_lines])
        return f"{header}{kept}\n... ({len(lines) - max_lines} more lines)\n"

    return re.sub(
        r'(--- .+? ---\n)(.*?)(?=--- |\[Component Specs|\[Valid Tokens|\Z)',
        _truncate_block,
        text,
        flags=re.DOTALL,
    )


def chunk_summary(chunks: list[dict]) -> str:
    """One-line summary of retrieved chunks: count, sources, total chars."""
    if not chunks:
        return "0 chunks"
    sources = [c.get("source_file", "?") for c in chunks]
    total_chars = sum(len(c.get("content", "")) for c in chunks)
    return f"{len(chunks)} chunks ({total_chars} chars) from: {', '.join(sources)}"
