"""ssr_python/rag/retrieval/vector_search.py — Tiered cosine similarity search (numpy)."""
import json
import numpy as np
from pathlib import Path

from rag.config import config, TIER_NAMES
from rag.embeddings.embed_service import EmbedService
from rag.retrieval.filters import passes_metadata_filter


class VectorSearch:
    def __init__(self):
        self.embed_service = EmbedService()
        self._tiers: dict[str, dict] = {}  # tier_name -> {embeddings, normed, chunks, id_to_idx}

    def load(self):
        """Load tiered indices. Falls back to combined index if tiers not found."""
        loaded_any = False
        for tier_name in TIER_NAMES:
            emb_path = config.data_dir / f"{tier_name}_embeddings.npz"
            chunks_path = config.data_dir / f"{tier_name}_chunks.jsonl"
            if emb_path.exists() and chunks_path.exists():
                data = np.load(emb_path)
                embs = data["embeddings"]
                norms = np.linalg.norm(embs, axis=1, keepdims=True)
                normed = embs / np.maximum(norms, 1e-10)
                chunks = self._load_chunks(chunks_path)
                id_to_idx = {c["id"]: i for i, c in enumerate(chunks)}
                self._tiers[tier_name] = {
                    "embeddings": embs,
                    "normed": normed,
                    "chunks": chunks,
                    "id_to_idx": id_to_idx,
                }
                loaded_any = True

        if not loaded_any:
            raise FileNotFoundError(
                f"No tier index files found in {config.data_dir}. Run index build first."
            )

    def search(
        self,
        query: str,
        top_k: int = None,
        metadata_filter: dict = None,
        tier: str = "section",
    ) -> list[tuple[dict, float]]:
        """Return (chunk_dict, score) pairs sorted by descending similarity."""
        top_k = top_k or config.vector_top_k

        tier_data = self._tiers.get(tier)
        if not tier_data:
            return []

        q_vec = self.embed_service.embed(query)
        q_norm = q_vec / np.maximum(np.linalg.norm(q_vec), 1e-10)

        # Cosine similarity via dot product (both normalized)
        scores = tier_data["normed"] @ q_norm

        # Apply metadata filter before ranking
        if metadata_filter:
            mask = self._build_mask(tier_data["chunks"], metadata_filter)
            scores = scores * mask

        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(tier_data["chunks"][i], float(scores[i])) for i in top_idx if scores[i] > 0]

    def get_embedding(self, chunk_id: str, tier: str = "section") -> np.ndarray | None:
        """Return embedding vector for a chunk by ID. Used by MMR."""
        tier_data = self._tiers.get(tier)
        if not tier_data:
            return None
        idx = tier_data["id_to_idx"].get(chunk_id)
        if idx is None:
            return None
        return tier_data["embeddings"][idx]

    def _build_mask(self, chunks: list[dict], filters: dict) -> np.ndarray:
        """Create binary mask using shared filter logic."""
        mask = np.ones(len(chunks), dtype=np.float32)
        for i, chunk in enumerate(chunks):
            if not passes_metadata_filter(chunk, filters):
                mask[i] = 0.0
        return mask

    def _load_chunks(self, path: Path = None) -> list[dict]:
        if path is None:
            path = config.data_dir / "chunks.jsonl"
        chunks = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                chunks.append(json.loads(line))
        return chunks
