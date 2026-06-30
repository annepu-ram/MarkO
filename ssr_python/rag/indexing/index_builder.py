"""ssr_python/rag/indexing/index_builder.py — Build tiered vector + BM25 indexes from chunks."""
import json
import hashlib
import pickle
import logging
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi

from rag.config import config
from rag.indexing.chunker import DocumentChunker, Chunk
from rag.indexing.metadata import extract_metadata
from rag.indexing.icon_chunker import chunk_icons
from rag.embeddings.embed_service import EmbedService
from rag.retrieval.tokenizer import tokenize

import tiktoken

logger = logging.getLogger(__name__)
_enc = tiktoken.get_encoding("cl100k_base")


class IndexBuilder:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embed_service = EmbedService()

    def build(self) -> dict:
        """Full pipeline: discover files -> chunk -> enrich -> embed -> persist (tiered)."""
        # 0. Canonical-sync guard — log a warning if metadata.py drifts from
        # planner_agent's section keys. Doesn't abort the build.
        self._check_canonical_sync()

        # 1. Discover all source files
        files = self._discover_files()
        print(f"Found {len(files)} source files")

        # 2. Chunk all files
        all_chunks: list[Chunk] = []
        for f in files:
            try:
                chunks = self.chunker.chunk_file(f)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Failed to chunk {f}: {e}")
        # 2b. Add icon chunks (one per Lucide icon name)
        icon_chunks = chunk_icons()
        all_chunks.extend(icon_chunks)
        print(f"Produced {len(all_chunks)} chunks ({len(icon_chunks)} icons)")

        if not all_chunks:
            raise ValueError("No chunks produced. Check source_dirs in config.")

        # 3. Enrich metadata + count tokens
        for chunk in all_chunks:
            extract_metadata(chunk)
            chunk.token_count = len(_enc.encode(chunk.content))

        # 4. Partition chunks into tiers
        tiered_chunks = {tier: [] for tier in config.tier_doc_types}
        for chunk in all_chunks:
            placed = False
            for tier_name, doc_types in config.tier_doc_types.items():
                if chunk.doc_type in doc_types:
                    tiered_chunks[tier_name].append(chunk)
                    placed = True
                    break
            if not placed:
                tiered_chunks["guide"].append(chunk)  # Fallback

        config.data_dir.mkdir(parents=True, exist_ok=True)
        tier_counts = {}

        # 5. Build and persist each tier
        for tier_name, chunks in tiered_chunks.items():
            if not chunks:
                print(f"  Tier '{tier_name}': 0 chunks (skipped)")
                tier_counts[tier_name] = 0
                continue

            # Embed
            texts = [c.content_with_context for c in chunks]
            print(f"  Tier '{tier_name}': embedding {len(texts)} chunks...")
            embeddings = self.embed_service.embed_batch(texts)

            # Build BM25 — tokenizer MUST match query-time tokenization
            # (rag.retrieval.tokenizer.tokenize) or scores will be junk.
            tokenized = [tokenize(c.content_with_context) for c in chunks]
            bm25 = BM25Okapi(tokenized)

            # Persist tier-specific files
            np.savez_compressed(
                config.data_dir / f"{tier_name}_embeddings.npz",
                embeddings=embeddings,
            )

            with open(config.data_dir / f"{tier_name}_bm25.pkl", "wb") as f:
                pickle.dump(bm25, f)

            with open(config.data_dir / f"{tier_name}_chunks.jsonl", "w", encoding="utf-8") as f:
                for chunk in chunks:
                    f.write(json.dumps({
                        "id": chunk.id,
                        "content": chunk.content,
                        "context_header": chunk.context_header,
                        "content_with_context": chunk.content_with_context,
                        "source_file": chunk.source_file,
                        "doc_type": chunk.doc_type,
                        "metadata": chunk.metadata,
                        "token_count": chunk.token_count,
                    }, ensure_ascii=False) + "\n")

            tier_counts[tier_name] = len(chunks)
            print(f"  Tier '{tier_name}': {len(chunks)} chunks, {embeddings.shape[1]}d embeddings")

        # 6. Write version stamp
        source_hash = self._hash_sources(files)
        with open(config.data_dir / "index_meta.json", "w") as f:
            json.dump({
                "source_hash": source_hash,
                "chunk_count": len(all_chunks),
                "tier_counts": tier_counts,
                "embedding_model": config.embedding_model,
                "embedding_dim": config.embedding_dim,
            }, f, indent=2)

        print(f"Index built: {len(all_chunks)} total chunks, tiers={tier_counts}, hash={source_hash[:12]}")
        return {"chunk_count": len(all_chunks), "tier_counts": tier_counts, "source_hash": source_hash}

    def is_stale(self) -> bool:
        """Check if source files have changed since last build."""
        meta_path = config.data_dir / "index_meta.json"
        if not meta_path.exists():
            return True
        meta = json.loads(meta_path.read_text())
        current_hash = self._hash_sources(self._discover_files())
        return current_hash != meta.get("source_hash")

    def _check_canonical_sync(self) -> None:
        """Warn if metadata.FOLDER_TO_SECTION_TYPE produces values that the
        planner doesn't recognise. Cheap defensive check to catch future drift
        between metadata canonical lists and planner_agent._SECTION_COMPONENTS.
        """
        try:
            from rag.indexing.metadata import FOLDER_TO_SECTION_TYPE, SECTION_PATTERNS
            from rag.agent.planner_agent import _SECTION_COMPONENTS
        except Exception as e:
            logger.warning(f"canonical-sync guard skipped: {e}")
            return

        canonical = set(_SECTION_COMPONENTS.keys()) | {"other"}
        bad_folder = {f: s for f, s in FOLDER_TO_SECTION_TYPE.items() if s not in canonical}
        bad_pattern = [k for k in SECTION_PATTERNS if k not in canonical]
        if bad_folder:
            logger.warning(
                f"FOLDER_TO_SECTION_TYPE has non-canonical values: {bad_folder}. "
                f"Planner won't recognise these section types."
            )
        if bad_pattern:
            logger.warning(
                f"SECTION_PATTERNS has non-canonical keys: {bad_pattern}."
            )

    def _discover_files(self) -> list[Path]:
        ignored_dirs = {"tests"}
        files = []
        for src in config.source_dirs:
            src = Path(src)
            if src.is_file():
                files.append(src)
            elif src.is_dir():
                for ext in ("*.yaml", "*.yml", "*.md"):
                    for f in src.rglob(ext):
                        if not any(part in ignored_dirs for part in f.parts):
                            files.append(f)
        return sorted(files)

    def _hash_sources(self, files: list[Path]) -> str:
        h = hashlib.sha256()
        for f in files:
            h.update(f.read_bytes())
        return h.hexdigest()
