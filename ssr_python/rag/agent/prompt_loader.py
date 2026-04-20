"""ssr_python/rag/agent/prompt_loader.py — Load and render Jinja2 prompt templates."""
from pathlib import Path
from functools import lru_cache
from jinja2 import Environment, FileSystemLoader

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

_env = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


@lru_cache(maxsize=16)
def load_system(name: str) -> str:
    """Load a static system prompt template (cached after first load)."""
    return _env.get_template(f"{name}_system.j2").render()


def render_user(name: str, **kwargs) -> str:
    """Render a dynamic user prompt template with variables."""
    template = _env.get_template(f"{name}_user.j2")
    return template.render(**kwargs)
