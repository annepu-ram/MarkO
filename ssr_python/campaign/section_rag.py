"""Campaign-driven RAG for brand style prompts and section YAML."""
import json
import re
from datetime import datetime

import yaml

from campaign.model_backend import CampaignModelBackend
from campaign.prompt_loader import load_campaign_system, render_campaign_user
from campaign.rag_config import campaign_rag_config
from campaign.rag_logger import log_campaign_output, log_campaign_prompt, prompt_log_metadata
from campaign.theme import brand_to_theme
from rag.agent.yaml_fixer import auto_fix_yaml, quick_validate
from rag.retrieval.keyword_search import KeywordSearch


CAMPAIGN_SECTION_COMPILER = "campaign_section_rag.v1"
BRAND_STYLE_PROMPT_COMPILER = "campaign_brand_styler.v1"
BRAND_WORDING_PROMPT_COMPILER = "campaign_brand_wording.v1"


def generate_brand_content_wording_prompt(brand, *, site_shell_config=None, org_id=None):
    """Generate durable copy/wording guidance for one brand."""
    site_shell_config = site_shell_config or {}
    brand_context = brand.to_generation_context() if brand else {}
    theme = site_shell_config.get("theme") or brand_to_theme(brand)

    system = load_campaign_system("brand_wording")
    user_prompt = render_campaign_user(
        "brand_wording",
        brand_context=json.dumps(brand_context, indent=2, sort_keys=True),
        site_shell_theme=json.dumps(theme, indent=2, sort_keys=True),
    )
    metadata = prompt_log_metadata(
        org_id=org_id or getattr(brand, "org_id", None),
        brand_id=getattr(brand, "id", None),
        model=campaign_rag_config.brand_styler_model_name or campaign_rag_config.model_name,
        backend=campaign_rag_config.model_backend,
        prompt_type="brand_wording",
    )
    log_campaign_prompt("BRAND_WORDING", system, user_prompt, metadata=metadata)
    output = CampaignModelBackend().generate(
        system,
        user_prompt,
        model_override=campaign_rag_config.brand_styler_model_name,
        temperature_override=campaign_rag_config.brand_styler_temperature,
    )
    log_campaign_output("BRAND_WORDING", output, metadata=metadata)
    return output.strip(), {
        "compiler": BRAND_WORDING_PROMPT_COMPILER,
        "generated_at": datetime.utcnow().isoformat(),
        "model": campaign_rag_config.brand_styler_model_name or campaign_rag_config.model_name,
        "backend": campaign_rag_config.model_backend,
        "site_shell": {
            "source": site_shell_config.get("source") or "brand_site_shell",
            "site_id": site_shell_config.get("site_id"),
            "uses": ["theme.colors", "theme.fonts"],
        },
    }


def generate_brand_section_style_prompt(brand, *, site_shell_config=None, org_id=None, content_wording_prompt=None):
    """Generate durable section styling guidance for one brand."""
    site_shell_config = site_shell_config or {}
    search = KeywordSearch()
    search.load()
    style_context = _retrieve_style_context(search, brand)
    brand_context = brand.to_generation_context() if brand else {}
    theme = site_shell_config.get("theme") or brand_to_theme(brand)

    system = load_campaign_system("brand_styler")
    user_prompt = render_campaign_user(
        "brand_styler",
        brand_context=json.dumps(brand_context, indent=2, sort_keys=True),
        site_shell_theme=json.dumps(theme, indent=2, sort_keys=True),
        content_wording_prompt=(content_wording_prompt or getattr(brand, "content_wording_prompt", None) or "").strip() or "No saved brand wording guidance yet.",
        style_context=style_context,
    )
    metadata = prompt_log_metadata(
        org_id=org_id or getattr(brand, "org_id", None),
        brand_id=getattr(brand, "id", None),
        model=campaign_rag_config.brand_styler_model_name or campaign_rag_config.model_name,
        backend=campaign_rag_config.model_backend,
        prompt_type="brand_styler",
    )
    log_campaign_prompt("BRAND_STYLER", system, user_prompt, metadata=metadata)
    output = CampaignModelBackend().generate(
        system,
        user_prompt,
        model_override=campaign_rag_config.brand_styler_model_name,
        temperature_override=campaign_rag_config.brand_styler_temperature,
    )
    log_campaign_output("BRAND_STYLER", output, metadata=metadata)
    return output.strip(), {
        "compiler": BRAND_STYLE_PROMPT_COMPILER,
        "generated_at": datetime.utcnow().isoformat(),
        "model": campaign_rag_config.brand_styler_model_name or campaign_rag_config.model_name,
        "backend": campaign_rag_config.model_backend,
        "style_chunk_count": len(style_context.split("--- Style")) - 1 if style_context else 0,
        "site_shell": {
            "source": site_shell_config.get("source") or "brand_site_shell",
            "site_id": site_shell_config.get("site_id"),
            "uses": ["theme.colors", "theme.fonts"],
        },
    }


def generate_section_yaml(section_type, content_items, *, brand=None, product=None, site_shell_config=None, section_metadata=None):
    """Generate body-only section YAML from content and saved brand style prompt."""
    section_type = (section_type or "custom").strip() or "custom"
    items = content_items or []
    site_shell_config = site_shell_config or {}
    section_metadata = dict(section_metadata or {})
    theme = site_shell_config.get("theme") or brand_to_theme(brand)
    brand_style_prompt = (getattr(brand, "section_style_prompt", None) or "").strip()
    if not brand_style_prompt:
        raise ValueError("Brand section style prompt is missing. Regenerate the brand style prompt before generating sections.")

    search = KeywordSearch()
    search.load()
    retrieved_examples = _retrieve_section_examples(search, section_type, items, brand)
    component_examples = _retrieve_component_examples(search, section_type, items)
    context = build_section_context(section_type, items, brand, product, site_shell_config, section_metadata)

    system = load_campaign_system("section_builder")
    user_prompt = render_campaign_user(
        "section_builder",
        section_metadata=json.dumps(section_metadata or {"section_type": section_type}, indent=2, sort_keys=True),
        brand_style_prompt=brand_style_prompt,
        site_shell_theme=json.dumps(theme, indent=2, sort_keys=True),
        content_context=json.dumps(context["content_items"], indent=2, sort_keys=True),
        derived_atoms=json.dumps(context["derived_atoms"], indent=2, sort_keys=True),
        retrieved_examples=retrieved_examples,
        component_examples=component_examples,
    )
    metadata = prompt_log_metadata(
        org_id=getattr(brand, "org_id", None),
        brand_id=getattr(brand, "id", None),
        section_type=section_type,
        content_item_ids=[str(_field(item, "id")) for item in items if _field(item, "id")],
        model=campaign_rag_config.section_model_name or campaign_rag_config.model_name,
        backend=campaign_rag_config.model_backend,
        prompt_type="section_builder",
    )
    log_campaign_prompt("SECTION_BUILDER", system, user_prompt, metadata=metadata)
    output = CampaignModelBackend().generate(
        system,
        user_prompt,
        model_override=campaign_rag_config.section_model_name,
        temperature_override=campaign_rag_config.section_temperature,
    )
    log_campaign_output("SECTION_BUILDER", output, metadata=metadata)

    yaml_text, repairs = _extract_validate_and_repair_body_yaml(output)
    return yaml_text, {
        "compiler": CAMPAIGN_SECTION_COMPILER,
        "section_type": section_type,
        "source_content_ids": [str(_field(item, "id")) for item in items if _field(item, "id")],
        "brand_id": getattr(brand, "id", None),
        "site_id": site_shell_config.get("site_id"),
        "style_prompt": _style_prompt_metadata(brand),
        "retrieval": {
            "section_chunk_ids": [_chunk_id(chunk) for chunk in retrieved_examples],
            "component_chunk_ids": [_chunk_id(chunk) for chunk in component_examples],
            "repairs": repairs,
        },
        "render_wrapper": {
            "source": "brand_site_shell",
            "uses": ["theme.colors", "theme.fonts"],
        },
    }


def build_section_context(section_type, items, brand, product, site_shell_config, section_metadata=None):
    return {
        "section_type": section_type,
        "section_metadata": section_metadata or {},
        "brand": _model_summary(brand, ["id", "name", "slug", "industry", "tagline", "description", "brand_promise", "default_style"]),
        "product": _model_summary(product, ["id", "name", "slug", "description"]),
        "site_shell_config": site_shell_config,
        "content_items": [_content_item_context(item) for item in items],
        "derived_atoms": _derived_atoms(items),
    }


def _retrieve_style_context(search, brand):
    query = " ".join(filter(None, [
        getattr(brand, "default_style", None),
        getattr(brand, "industry", None),
        getattr(brand, "tone", None),
        "brand section style",
    ]))
    chunks = _keyword_chunks(search.search(query or "brand section style", top_k=campaign_rag_config.style_top_k, tier="style"))
    return "\n\n".join(f"--- Style {i + 1} ---\n{chunk.get('content') or chunk.get('text') or ''}" for i, chunk in enumerate(chunks))


def _retrieve_section_examples(search, section_type, items, brand):
    query = " ".join(filter(None, [
        section_type,
        getattr(brand, "industry", None),
        " ".join(_category(item) for item in items),
    ]))
    return _keyword_chunks(search.search(query or f"{section_type} section", top_k=campaign_rag_config.section_top_k, tier="section"))


def _retrieve_component_examples(search, section_type, items):
    query = " ".join(filter(None, [section_type, " ".join(_category(item) for item in items), "components"]))
    return _keyword_chunks(search.search(query or f"{section_type} components", top_k=campaign_rag_config.component_top_k, tier="component"))


def _keyword_chunks(results):
    return [chunk for chunk, _score in (results or [])]


def _extract_validate_and_repair_body_yaml(output):
    yaml_text = _extract_yaml(output)
    yaml_text = _normalize_body_yaml(yaml_text)
    error = _validate_body_yaml(yaml_text)
    repairs = []
    if error:
        fixed, repairs = auto_fix_yaml(yaml_text)
        fixed = _normalize_body_yaml(fixed)
        fixed_error = _validate_body_yaml(fixed)
        if fixed_error:
            raise ValueError(f"Section YAML repair failed: {fixed_error}")
        yaml_text = fixed
    return yaml_text, repairs


def _extract_yaml(response):
    match = re.search(r"```(?:yaml)?\s*\n(.+?)```", response or "", re.DOTALL)
    return (match.group(1) if match else (response or "")).strip()


def _normalize_body_yaml(yaml_text):
    parsed = yaml.safe_load(yaml_text or "[]")
    if parsed is None:
        parsed = []
    return yaml.dump(parsed, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _validate_body_yaml(yaml_text):
    try:
        parsed = yaml.safe_load(yaml_text or "[]")
    except yaml.YAMLError as exc:
        return f"YAML parse error: {exc}"
    if not isinstance(parsed, list):
        return "Generated section YAML must be a list."
    wrappers = _find_component_names(parsed, {"site", "page"})
    if wrappers:
        return f"Generated section YAML must not include wrappers: {', '.join(sorted(wrappers))}."
    return quick_validate(yaml_text)


def _find_component_names(node, names):
    found = []
    if isinstance(node, list):
        for item in node:
            found.extend(_find_component_names(item, names))
    elif isinstance(node, dict):
        name = node.get("name")
        if name in names:
            found.append(name)
        for key in ("components", "items", "tabs", "slides", "columns"):
            found.extend(_find_component_names(node.get(key), names))
    return found


def _style_prompt_metadata(brand):
    raw = getattr(brand, "section_style_prompt_metadata", None)
    try:
        metadata = json.loads(raw) if raw else {}
    except (TypeError, json.JSONDecodeError):
        metadata = {}
    updated = getattr(brand, "section_style_prompt_updated_at", None)
    if updated:
        metadata["updated_at"] = updated.isoformat()
    return metadata


def _chunk_id(chunk):
    return chunk.get("id") or chunk.get("chunk_id") or chunk.get("source_file")


def _content_item_context(item):
    return {
        "id": str(_field(item, "id") or ""),
        "category": _category(item),
        "title": _field(item, "title") or "",
        "content": _field(item, "content") or "",
        "slots": _payload(item),
    }


def _derived_atoms(items):
    atoms = {}
    for item in items or []:
        category = _category(item)
        payload = _payload(item)
        for key, value in payload.items():
            if value not in (None, "", []):
                atoms[f"{category}.{key}"] = value
    return atoms


def _model_summary(model, keys):
    if model is None:
        return {}
    return {key: _field(model, key) for key in keys if _field(model, key)}


def _payload(item):
    if hasattr(item, "get_slots"):
        return item.get_slots() or {}
    if isinstance(item, dict):
        return item.get("slots") or {}
    return {}


def _field(item, key):
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def _category(item):
    return str(_field(item, "category") or "").strip()
