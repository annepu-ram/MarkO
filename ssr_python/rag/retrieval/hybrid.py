"""ssr_python/rag/retrieval/hybrid.py — Tiered Reciprocal Rank Fusion + MMR diversity."""
from collections import defaultdict

import numpy as np

from rag.config import config
from rag.retrieval.vector_search import VectorSearch
from rag.retrieval.keyword_search import KeywordSearch


class HybridSearch:
    def __init__(self):
        self.vector = VectorSearch()
        self.keyword = KeywordSearch()

    def load(self):
        self.vector.load()
        self.keyword.load()

    def search(
        self,
        query: str,
        top_k: int = None,
        metadata_filter: dict = None,
        tier: str = "section",
    ) -> list[dict]:
        """Hybrid retrieval via Reciprocal Rank Fusion + MMR diversity."""
        top_k = top_k or config.final_top_k

        # Get results from both methods (tier-aware, filter-aware)
        vec_results = self.vector.search(
            query, metadata_filter=metadata_filter, tier=tier
        )
        bm25_results = self.keyword.search(
            query, metadata_filter=metadata_filter, tier=tier
        )

        # RRF scoring
        rrf_scores = defaultdict(float)
        chunk_map = {}

        for rank, (chunk, _score) in enumerate(vec_results):
            cid = chunk["id"]
            rrf_scores[cid] += 1.0 / (config.rrf_k + rank + 1)
            chunk_map[cid] = chunk

        for rank, (chunk, _score) in enumerate(bm25_results):
            cid = chunk["id"]
            rrf_scores[cid] += 1.0 / (config.rrf_k + rank + 1)
            chunk_map[cid] = chunk

        # Sort by fused score
        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)

        # Apply MMR for diversity on top candidates
        mmr_pool_size = min(len(sorted_ids), max(top_k * config.mmr_pool_multiplier, config.mmr_pool_min_size))
        rrf_candidates = [chunk_map[cid] for cid in sorted_ids[:mmr_pool_size]]

        if len(rrf_candidates) <= top_k:
            return rrf_candidates

        query_emb = self.vector.embed_service.embed(query)
        return self._mmr_select(rrf_candidates, query_emb, top_k, tier)

    def _mmr_select(
        self,
        candidates: list[dict],
        query_embedding: np.ndarray,
        top_k: int,
        tier: str,
    ) -> list[dict]:
        """Select top_k diverse results using Maximal Marginal Relevance.

        Balances relevance to query vs. diversity among selected results.
        lambda_param from config: 0.0 = max diversity, 1.0 = max relevance
        """
        lambda_param = config.mmr_lambda
        q_norm = query_embedding / np.maximum(np.linalg.norm(query_embedding), 1e-10)

        # Get embeddings for all candidates
        candidate_embeddings = []
        for c in candidates:
            emb = self.vector.get_embedding(c["id"], tier=tier)
            if emb is None:
                # Fallback: use zero vector (will get low relevance score)
                emb = np.zeros(config.embedding_dim, dtype=np.float32)
            candidate_embeddings.append(emb)

        # Normalize candidate embeddings
        cand_norms = [e / np.maximum(np.linalg.norm(e), 1e-10) for e in candidate_embeddings]

        selected = []
        selected_norms = []
        remaining_indices = list(range(len(candidates)))

        for _ in range(min(top_k, len(candidates))):
            best_score = -float("inf")
            best_idx_pos = 0

            for pos, idx in enumerate(remaining_indices):
                # Relevance: cosine similarity to query
                relevance = float(np.dot(q_norm, cand_norms[idx]))

                # Redundancy: max cosine similarity to already selected
                if selected_norms:
                    redundancy = max(
                        float(np.dot(cand_norms[idx], sn)) for sn in selected_norms
                    )
                else:
                    redundancy = 0.0

                mmr_score = lambda_param * relevance - (1 - lambda_param) * redundancy
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx_pos = pos

            chosen_idx = remaining_indices.pop(best_idx_pos)
            selected.append(candidates[chosen_idx])
            selected_norms.append(cand_norms[chosen_idx])

        return selected
