"""ssr_python/rag/agent/prompt_loader.py — Load and render Jinja2 prompt templates."""
from pathlib import Path
from functools import lru_cache
from jinja2 import Environment, FileSystemLoader

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_CONDENSED_REF_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "COMPONENT_REFERENCE_CONDENSED.md"

_env = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)

_condensed_ref: str | None = None


def _get_condensed_ref() -> str:
    global _condensed_ref
    if _condensed_ref is None:
        _condensed_ref = _CONDENSED_REF_PATH.read_text(encoding="utf-8")
    return _condensed_ref


@lru_cache(maxsize=16)
def load_system(name: str) -> str:
    """Load a static system prompt template (cached after first load)."""
    template = _env.get_template(f"{name}_system.j2")
    if name == "builder":
        return template.render(component_reference=_get_condensed_ref())
    return template.render()


def render_user(name: str, **kwargs) -> str:
    """Render a dynamic user prompt template with variables."""
    template = _env.get_template(f"{name}_user.j2")
    return template.render(**kwargs)
