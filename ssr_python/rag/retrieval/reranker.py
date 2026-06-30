"""ssr_python/rag/retrieval/reranker.py — Cross-encoder reranker."""
import logging
from rag.config import config

logger = logging.getLogger(__name__)


class Reranker:
    """Cross-encoder reranker. Lazy-loads the model on first use."""

    def __init__(self):
        self._model = None
        self._load_failed = False

    def _load_model(self):
        if self._model is not None or self._load_failed:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(config.reranker_model)
        except Exception as e:
            logger.warning(f"Reranker model failed to load ({e!r}); falling back to RRF order")
            self._load_failed = True

    def rerank(self, query: str, chunks: list[dict], top_k: int = None) -> list[dict]:
        top_k = top_k or config.final_top_k
        if not config.use_reranker or not chunks:
            return chunks[:top_k]

        self._load_model()
        if self._model is None:
            return chunks[:top_k]

        pairs = [(query, c["content_with_context"]) for c in chunks]
        try:
            scores = self._model.predict(pairs)
        except Exception as e:
            logger.warning(f"Reranker.predict failed ({e!r}); falling back to RRF order")
            return chunks[:top_k]
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [c for c, _ in ranked[:top_k]]
