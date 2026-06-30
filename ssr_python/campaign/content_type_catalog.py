"""Marketing content type metadata for the Content Library UI and APIs.

The catalog (CONTENT_TYPES + slot schemas) is DERIVED from the canonical
registry (campaign/content_registry.py) so it cannot drift from the recipe-engine
ontology in campaign/vocabulary.py. Add or edit a content type in the registry;
this catalog and the vocabulary both update. Every public function below keeps
its original signature so existing importers are unaffected.
"""

from campaign.content_registry import catalog_entries

CONTENT_TYPE_FAMILIES = [
    {"key": "core_message", "label": "Core Message"},
    {"key": "offer", "label": "Offer"},
    {"key": "proof", "label": "Proof"},
    {"key": "objections", "label": "Objections & FAQ"},
    {"key": "product", "label": "Product"},
    {"key": "brand", "label": "Brand / Company"},
    {"key": "channel_assets", "label": "Channel Assets"},
]


def _catalog_type_from_registry(entry):
    """Project a registry entry into the catalog's content-type dict shape."""
    return {
        "key": entry["catalog_key"],
        "label": entry["label"],
        "family": entry["family"],
        "description": entry.get("description", ""),
        "channel_affinity": list(entry.get("channel_affinity") or []),
        "page_usable": entry.get("page_usable", True),
        "proof_sensitive": entry.get("proof_sensitive", False),
        "slot_schema": [dict(slot) for slot in (entry.get("slot_schema") or [])],
    }


CONTENT_TYPES = [_catalog_type_from_registry(e) for e in catalog_entries()]


def _control_type(slot):
    explicit = slot.get("type")
    if explicit:
        return explicit
    primitive = slot.get("primitive_type")
    if primitive == "url":
        return "url"
    if primitive in {"paragraph", "answer", "quote", "proof"}:
        return "textarea"
    if primitive in {"date"}:
        return "date"
    if primitive in {"number"}:
        return "number"
    return "text"


def _normalized_slot_schema(slots):
    normalized = []
    for raw in slots or []:
        slot = dict(raw)
        slot.setdefault("type", _control_type(slot))
        slot.setdefault("required", False)
        if "placeholder" not in slot and slot.get("help_text"):
            slot["placeholder"] = slot["help_text"]
        normalized.append(slot)
    return normalized


for _content_type in CONTENT_TYPES:
    _content_type["slot_schema"] = _normalized_slot_schema(
        _content_type.get("slot_schema") or []
    )

_TYPE_MAP = {item["key"]: item for item in CONTENT_TYPES}


def content_type_keys():
    return frozenset(_TYPE_MAP.keys())


def content_type_label(key):
    item = _TYPE_MAP.get(key)
    return item["label"] if item else str(key or "").replace("_", " ").title()


def content_type_metadata(key):
    return _TYPE_MAP.get(key)


def content_type_slot_schema(key):
    item = _TYPE_MAP.get(key)
    return list((item or {}).get("slot_schema") or [])


CONTENT_SUMMARY_SLOT_ORDER = {
    "faq": ("answer", "question"),
    "testimonial": ("quote",),
    "cta": ("paragraph", "headline", "button_label"),
    "offer": ("details", "headline", "cta_label"),
    "value_proposition": ("paragraph", "headline"),
    "benefit": ("paragraph", "headline"),
    "product_feature": ("paragraph", "headline"),
    "objection": ("response", "concern"),
    "comparison": ("differentiator", "subject"),
}


def content_summary_slot_order(key):
    schema_keys = tuple(slot.get("key") for slot in content_type_slot_schema(key) if slot.get("key"))
    preferred = CONTENT_SUMMARY_SLOT_ORDER.get(key, ())
    ordered = [slot for slot in preferred if slot in schema_keys]
    ordered.extend(slot for slot in schema_keys if slot not in ordered)
    return ordered


def primary_slot_key(key):
    ordered = content_summary_slot_order(key)
    return ordered[0] if ordered else "content"


def derive_content_from_slots(key, slots):
    slots = slots or {}
    for slot_key in content_summary_slot_order(key):
        value = slots.get(slot_key)
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value if str(v).strip())
        if str(value or "").strip():
            return str(value).strip()
    return ""


def slots_from_content(key, content):
    value = str(content or "").strip()
    return {primary_slot_key(key): value} if value else {}


def is_composite_content_type(key):
    return bool(content_type_slot_schema(key))


def serializable_content_types():
    return [dict(item) for item in CONTENT_TYPES]


def serializable_content_families():
    return [dict(item) for item in CONTENT_TYPE_FAMILIES]
