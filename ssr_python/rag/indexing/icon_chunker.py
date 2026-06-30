"""ssr_python/rag/indexing/icon_chunker.py — Create one Chunk per Lucide icon name."""
import json
import logging
import re

from rag.config import config
from rag.indexing.chunker import Chunk

logger = logging.getLogger(__name__)

# Semantic icon group rules. Each tuple is (group_name, regex_against_icon_name).
# Icon names are lucide-style kebab-case, so we can pattern-match substrings.
# An icon may belong to multiple groups (e.g. "shopping-cart" → ecommerce + cart).
_ICON_GROUP_RULES: list[tuple[str, re.Pattern]] = [
    ("navigation",     re.compile(r"\b(menu|home|nav|chevron|arrow|move|panel|sidebar|dock|compass|map(?!-)|map-pin|navigation)\b")),
    ("social",         re.compile(r"\b(facebook|twitter|x-(?:twitter)?|instagram|linkedin|youtube|tiktok|pinterest|reddit|discord|github|gitlab|slack|whatsapp|telegram|snapchat|twitch|spotify|threads)\b")),
    ("ecommerce",      re.compile(r"\b(shopping|cart|store|wallet|credit-card|gift|package|receipt|tag|ticket|coins|dollar|euro|pound|currency|banknote|piggy)\b")),
    ("media",          re.compile(r"\b(play|pause|stop|skip|rewind|fast-forward|volume|mute|video|film|camera|image(?:s)?|photo|music|headphones|mic|microphone|speaker|disc|radio)\b")),
    ("communication",  re.compile(r"\b(mail|inbox|message|chat|phone|call|send|reply|forward|bell|notification|at-sign|voicemail)\b")),
    ("file",           re.compile(r"\b(file|folder|archive|paperclip|clipboard|download|upload|save|disc(?:-)?|hard-drive|database|server)\b")),
    ("security",       re.compile(r"\b(lock|unlock|key|shield|fingerprint|scan|eye|eye-off|user-check|verified|certificate)\b")),
    ("user",           re.compile(r"\b(user|users|person|people|profile|circle-user|contact|crown|smile|heart-handshake)\b")),
    ("time",           re.compile(r"\b(clock|alarm|timer|hourglass|calendar|history|stopwatch)\b")),
    ("weather",        re.compile(r"\b(sun|moon|cloud|cloudy|rain|snow|wind|umbrella|thermometer|droplet|sunrise|sunset|tornado|sparkles|rainbow)\b")),
    ("transport",      re.compile(r"\b(car|truck|bus|bike|bicycle|plane|train|ship|boat|rocket|fuel|wheel|taxi|parking)\b")),
    ("health",         re.compile(r"\b(heart|pulse|activity|stethoscope|pill|syringe|first-aid|hospital|bandage|ambulance|brain|tooth|leaf|dna)\b")),
    ("food",           re.compile(r"\b(coffee|cup|utensils|pizza|cake|cookie|wine|beer|chef|salad|sandwich|soup|ice-cream|apple|carrot|wheat)\b")),
    ("nature",         re.compile(r"\b(tree|leaf|flower|sprout|seedling|mountain|waves|fish|bug|paw|bird|dog|cat|cherry)\b")),
    ("commerce",       re.compile(r"\b(award|badge|trophy|medal|star|thumbs-up|thumbs-down|like|trending|chart|bar-chart|line-chart|pie-chart|target|crosshair)\b")),
    ("education",      re.compile(r"\b(book|library|graduation|school|pen|pencil|notebook|edit|highlighter|bookmark)\b")),
    ("settings",       re.compile(r"\b(settings|cog|sliders|tool|wrench|hammer|screwdriver|gear|toggle|filter)\b")),
    ("dev",            re.compile(r"\b(code|terminal|braces|bracket|bug|git|merge|fork|api|webhook|cpu|server|cloud-upload|database)\b")),
    ("layout",         re.compile(r"\b(layout|grid|columns|rows|table|panel|window|maximize|minimize|fullscreen|expand|collapse|sidebar)\b")),
    ("feedback",       re.compile(r"\b(check|x\b|alert|info|help|circle-help|warning|circle-check|circle-x|circle-alert|ban)\b")),
    ("location",       re.compile(r"\b(map|map-pin|pin|locate|navigation|globe|flag|building|home|landmark|tent)\b")),
    ("communication2", re.compile(r"\b(rss|share|broadcast|antenna|wifi|bluetooth|satellite|signal)\b")),
]


def _classify(name: str) -> list[str]:
    """Return all matching semantic groups for an icon name."""
    n = f" {name} "  # pad so \b works at edges
    groups: list[str] = []
    for group_name, pat in _ICON_GROUP_RULES:
        # Strip the synthetic "2" suffix used to disambiguate duplicate group names
        canonical = group_name.rstrip("0123456789") if group_name[-1].isdigit() else group_name
        if pat.search(n):
            if canonical not in groups:
                groups.append(canonical)
    return groups


def chunk_icons() -> list[Chunk]:
    """Read lucide-icons.json and return one Chunk per icon name."""
    icon_path = config.icon_data_path
    if not icon_path.exists():
        logger.warning(f"Icon data file not found: {icon_path}")
        return []

    icons = json.loads(icon_path.read_text(encoding="utf-8"))
    logger.info(f"Loading {len(icons)} icon names from {icon_path.name}")

    chunks = []
    for name in icons:
        groups = _classify(name)
        # Embedding text includes the group hints so cosine search picks them up too.
        embed_extra = f" groups: {', '.join(groups)}" if groups else ""
        chunks.append(Chunk(
            id=f"icon__{name}",
            content=name,
            context_header="lucide icon",
            content_with_context=f"lucide icon: {name}{embed_extra}",
            source_file="lucide-icons.json",
            doc_type="icon",
            metadata={"groups": groups},
            token_count=len(name.split("-")) + 2,  # approximate
        ))

    return chunks
