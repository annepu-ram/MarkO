"""ssr_python/rag/retrieval/reranker.py — Cross-encoder reranker (V2, off by default)."""
from rag.config import config


class Reranker:
    """Cross-encoder reranker. Disabled by default (config.use_reranker)."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(config.reranker_model)

    def rerank(self, query: str, chunks: list[dict], top_k: int = None) -> list[dict]:
        top_k = top_k or config.final_top_k
        if not config.use_reranker:
            return chunks[:top_k]

        self._load_model()
        pairs = [(query, c["content_with_context"]) for c in chunks]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [c for c, _ in ranked[:top_k]]
