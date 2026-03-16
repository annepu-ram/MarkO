"""ssr_python/rag/embeddings/embed_service.py — Embedding generation."""
import numpy as np
import requests
import logging

from rag.config import config

logger = logging.getLogger(__name__)


# nomic-embed-text via Ollama fails on long texts (>~6K chars empirically).
# Truncate to 5000 chars (~1250 tokens) — individual component chunks are typically <2000 chars.
MAX_CHARS = 5000


class EmbedService:
    """Generate embeddings via Ollama or sentence-transformers fallback."""

    def __init__(self):
        self._st_model = None  # Lazy-loaded fallback

    def _truncate(self, text: str) -> str:
        """Truncate text to fit within embedding model context window."""
        if len(text) > MAX_CHARS:
            return text[:MAX_CHARS]
        return text

    def embed(self, text: str) -> np.ndarray:
        text = self._truncate(text)
        if config.embedding_backend == "ollama":
            try:
                return self._embed_ollama(text)
            except Exception as e:
                logger.warning(f"Ollama embedding failed: {e}, falling back to sentence-transformers")
                return self._embed_sentence_transformers(text)
        return self._embed_sentence_transformers(text)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts. Returns (N, dim) array."""
        texts = [self._truncate(t) for t in texts]
        if config.embedding_backend == "ollama":
            vecs = []
            total = len(texts)
            failed = 0
            for i, t in enumerate(texts):
                if (i + 1) % 100 == 0 or i == 0:
                    print(f"  Embedding {i+1}/{total}...")
                try:
                    vecs.append(self._embed_ollama(t))
                except Exception as e:
                    # Use zero vector for failed embeddings instead of aborting
                    logger.warning(f"Embedding failed for chunk {i} (len={len(t)}): {e}")
                    vecs.append(np.zeros(config.embedding_dim, dtype=np.float32))
                    failed += 1
            if failed > 0:
                print(f"  Warning: {failed}/{total} embeddings failed (zero vectors used)")
            return np.array(vecs)
        return self._embed_sentence_transformers_batch(texts)

    # ── Ollama backend ──

    def _embed_ollama(self, text: str) -> np.ndarray:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": config.embedding_model, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return np.array(resp.json()["embedding"], dtype=np.float32)

    # ── Sentence-transformers fallback ──

    def _get_st_model(self):
        if self._st_model is None:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(config.embedding_fallback)
        return self._st_model

    def _embed_sentence_transformers(self, text: str) -> np.ndarray:
        model = self._get_st_model()
        return model.encode(text, normalize_embeddings=True)

    def _embed_sentence_transformers_batch(self, texts: list[str]) -> np.ndarray:
        model = self._get_st_model()
        return model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
