"""ssr_python/rag/indexing/icon_chunker.py — Create one Chunk per Lucide icon name."""
import json
import logging

from rag.config import config
from rag.indexing.chunker import Chunk

logger = logging.getLogger(__name__)


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
        chunks.append(Chunk(
            id=f"icon__{name}",
            content=name,
            context_header="lucide icon",
            content_with_context=f"lucide icon: {name}",
            source_file="lucide-icons.json",
            doc_type="icon",
            metadata={},
            token_count=len(name.split("-")) + 2,  # approximate
        ))

    return chunks
