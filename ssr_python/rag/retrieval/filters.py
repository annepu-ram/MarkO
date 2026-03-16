"""ssr_python/rag/retrieval/filters.py — Shared metadata filtering logic."""


def passes_metadata_filter(chunk: dict, filters: dict) -> bool:
    """Check if a chunk passes all metadata filter conditions.

    Shared by VectorSearch and KeywordSearch to avoid duplicating logic.

    Filter semantics:
    - component_types: set intersection (any match passes)
    - visual_style: item-in-list check
    - doc_type: exact match on chunk["doc_type"] (not in metadata)
    - all other keys: exact match on chunk["metadata"][key]
    """
    if not filters:
        return True

    meta = chunk.get("metadata", {})

    for key, val in filters.items():
        if key == "component_types":
            if not set(val) & set(meta.get("component_types", [])):
                return False
        elif key == "visual_style":
            if val not in meta.get("visual_style", []):
                return False
        elif key == "doc_type":
            if chunk.get("doc_type") != val:
                return False
        elif meta.get(key) != val:
            return False

    return True
