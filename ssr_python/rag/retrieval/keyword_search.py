"""ssr_python/rag/retrieval/keyword_search.py — Tiered BM25 sparse retrieval."""
import json
import pickle

from rag.config import config, TIER_NAMES
from rag.retrieval.filters import passes_metadata_filter


class KeywordSearch:
    def __init__(self):
        self._tiers: dict[str, dict] = {}  # tier_name -> {bm25, chunks}

    def load(self):
        """Load tiered BM25 indices. Falls back to combined index."""
        loaded_any = False
        for tier_name in TIER_NAMES:
            bm25_path = config.data_dir / f"{tier_name}_bm25.pkl"
            chunks_path = config.data_dir / f"{tier_name}_chunks.jsonl"
            if bm25_path.exists() and chunks_path.exists():
                with open(bm25_path, "rb") as f:
                    bm25 = pickle.load(f)
                with open(chunks_path, encoding="utf-8") as f:
                    chunks = [json.loads(line) for line in f]
                self._tiers[tier_name] = {"bm25": bm25, "chunks": chunks}
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
        """BM25 search within a specific tier, with optional metadata filtering."""
        top_k = top_k or config.bm25_top_k

        tier_data = self._tiers.get(tier)
        if not tier_data:
            return []

        tokens = query.lower().split()
        scores = tier_data["bm25"].get_scores(tokens)

        # Apply metadata filter
        if metadata_filter:
            for i, chunk in enumerate(tier_data["chunks"]):
                if not passes_metadata_filter(chunk, metadata_filter):
                    scores[i] = 0.0

        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(tier_data["chunks"][i], float(scores[i])) for i in top_idx if scores[i] > 0]
