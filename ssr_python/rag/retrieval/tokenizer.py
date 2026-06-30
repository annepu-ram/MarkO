"""ssr_python/rag/retrieval/tokenizer.py — Shared BM25 tokenizer.

Used by both `index_builder` (when building the BM25 index) and
`keyword_search` (at query time). MUST be identical on both sides or
BM25 scores will be junk.
"""
import re

# Compact stopword set — only words that appear constantly in template/yaml
# noise and never carry section-type signal.
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "being", "as", "at", "by",
    "this", "that", "these", "those", "it", "its", "from", "into", "via",
    "i", "me", "my", "we", "our", "you", "your", "they", "them", "their",
})

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")


def _stem(word: str) -> str:
    """Tiny suffix-stripping stemmer covering common plural/verb forms."""
    if len(word) <= 3:
        return word
    for suffix in ("ies",):
        if word.endswith(suffix):
            return word[: -len(suffix)] + "y"
    for suffix in ("ing", "ers", "ies"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[: -len(suffix)]
    for suffix in ("ed", "es", "er", "ly"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[: -len(suffix)]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    """Lowercase + strip-punct + remove stopwords + light s-stemmer.

    Splits hyphenated component names like ``layout-row`` into both the
    full token and its parts so a query for ``layout`` still hits a
    chunk that contains ``layout-row``.
    """
    if not text:
        return []
    out: list[str] = []
    for raw in _TOKEN_RE.findall(text.lower()):
        if raw in _STOPWORDS:
            continue
        out.append(_stem(raw))
        # Also index hyphen-split parts ("layout-row" -> ["layout", "row"])
        if "-" in raw:
            for part in raw.split("-"):
                if part and part not in _STOPWORDS and len(part) > 1:
                    out.append(_stem(part))
    return out
