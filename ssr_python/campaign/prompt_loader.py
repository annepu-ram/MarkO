"""Prompt loading for campaign-driven section RAG."""
from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from campaign.rag_config import campaign_rag_config


_env = Environment(
    loader=FileSystemLoader(str(campaign_rag_config.prompts_dir)),
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)

_component_ref_path = Path(__file__).resolve().parent.parent / "config" / "COMPONENT_REFERENCE_CONDENSED.md"
_component_reference = None


def _get_component_reference():
    global _component_reference
    if _component_reference is None:
        _component_reference = _component_ref_path.read_text(encoding="utf-8")
    return _component_reference


@lru_cache(maxsize=16)
def load_campaign_system(name):
    template = _env.get_template(f"{name}_system.j2")
    if name == "section_builder":
        return template.render(component_reference=_get_component_reference())
    return template.render()


def render_campaign_user(name, **kwargs):
    template = _env.get_template(f"{name}_user.j2")
    return template.render(**kwargs)
