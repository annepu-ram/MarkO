"""ssr_python/rag/retrieval/filters.py — Shared metadata filtering logic."""


def passes_metadata_filter(chunk: dict, filters: dict) -> bool:
    """Check if a chunk passes all metadata filter conditions.

    Shared by VectorSearch and KeywordSearch to avoid duplicating logic.

    Filter semantics:
    - component_types: set intersection (any match passes)
    - visual_style / mood / industries / sections / groups: item-in-list check
      (filter value can be a single string or a list — any overlap passes)
    - doc_type: exact match on chunk["doc_type"] (not in metadata)
    - all other keys: exact match on chunk["metadata"][key]
    """
    if not filters:
        return True

    meta = chunk.get("metadata", {})
    LIST_OVERLAP_KEYS = {
        "visual_style", "mood", "industries", "sections", "groups", "palette_names",
        "interactivity", "outline_labels", "layout_modifiers",
    }

    for key, val in filters.items():
        if key == "component_types":
            if not set(val) & set(meta.get("component_types", [])):
                return False
        elif key in LIST_OVERLAP_KEYS:
            chunk_vals = meta.get(key, [])
            if not isinstance(chunk_vals, list):
                chunk_vals = [chunk_vals]
            wanted = val if isinstance(val, list) else [val]
            if not set(wanted) & set(chunk_vals):
                return False
        elif key == "doc_type":
            if chunk.get("doc_type") != val:
                return False
        elif meta.get(key) != val:
            return False

    return True
