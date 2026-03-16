# RAG System with SLM — Detailed Implementation Plan v2

## 1. Problem Statement

Current `llm_service.py` sends the full 78KB `LLM_COMPONENT_GUIDE.md` as system prompt on every chat request. This causes:

- **Context overflow** — leaves little room for reasoning in smaller models
- **Wasted tokens** — 95%+ of the guide is irrelevant per query
- **Scaling ceiling** — can't add more templates/docs without blowing context limits
- **Cost** — cloud API calls billed per token; sending 78KB every time is expensive

**Goal:** Retrieve only the 2-5 relevant chunks per query, enabling a small local or cloud model to produce high-quality YAML with focused context.

**Relationship to fine-tuning:** Fine-tuning (per `FINETUNE_PLAN.md`) teaches YAML syntax. RAG provides runtime knowledge — templates, patterns, component specs. They complement each other; RAG is the higher-priority investment.

---

## 2. Architecture

```
User Query ("Create a bakery hero section")
         │
    ┌────▼─────────────────┐
    │ 1. Query Analysis     │  Rule-based intent classifier
    │    Intent + filters   │  (create_page | create_section | modify | explain | add)
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │ 2. Query Embedding    │  nomic-embed-text via Ollama
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │ 3. Hybrid Retrieval   │  Vector (brute-force cosine) + BM25 keyword
    │    + Metadata Filter  │  Reciprocal Rank Fusion
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │ 4. Context Assembly   │  Dynamic token budget by intent
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │ 5. SLM Generation     │  Pluggable: Ollama / OpenAI / Anthropic / Groq
    └────┬─────────────────┘
         │
    ┌────▼─────────────────┐
    │ 6. Validation + Retry │  Existing renderer.py + error-guided retry
    └────┬─────────────────┘
         │
    Response to Chat UI
```

---

## 3. Directory Structure

```
ssr_python/rag/
├── config.py                    # Central RAG configuration
├── requirements.txt             # Dependencies
├── embeddings/
│   ├── embed_service.py         # Embedding generation (Ollama / sentence-transformers)
│   └── batch_embed.py           # Bulk-embed all documents
├── indexing/
│   ├── chunker.py               # YAML-aware + markdown chunking
│   ├── metadata.py              # Extract component types, industry, section, tokens
│   └── index_builder.py         # Build vector + BM25 indexes from chunks
├── retrieval/
│   ├── vector_search.py         # Cosine similarity search (numpy, upgradable to FAISS)
│   ├── keyword_search.py        # BM25 sparse retrieval
│   ├── hybrid.py                # Reciprocal Rank Fusion combiner
│   └── reranker.py              # Cross-encoder reranking (V2, off by default)
├── agent/
│   ├── rag_agent.py             # Orchestrator: routes intent → single-call or multi-agent
│   ├── planner_agent.py         # Agent 1: site outline generator (create_page intent)
│   ├── builder_agent.py         # Agent 2: per-section YAML generator (called N times)
│   ├── stitcher.py              # Page assembler: combines sections into full page (no LLM)
│   ├── model_backend.py         # Unified interface: Ollama / OpenAI / Anthropic / Groq
│   ├── query_analyzer.py        # Intent classification + metadata filter extraction
│   ├── prompt_builder.py        # Assemble retrieved context into SLM prompt
│   └── response_parser.py       # Extract ACTION + YAML (reuse from llm_service.py)
├── data/
│   ├── vector_index.npz         # Persisted numpy embeddings matrix
│   ├── bm25_index.pkl           # Persisted BM25 corpus
│   ├── chunks.jsonl             # All chunks with metadata + context headers
│   └── index_meta.json          # Version stamp: source file hashes, build timestamp
└── scripts/
    ├── build_index.py           # Chunk → embed → index all documents
    └── evaluate_retrieval.py    # Test retrieval quality with sample queries
```

---

## 4. Configuration (`config.py`)

Centralize all tunables. Every magic number lives here.

```python
"""ssr_python/rag/config.py"""
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class RAGConfig:
    # ── Paths ──
    rag_dir: Path = Path(__file__).parent
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    source_dirs: list[Path] = field(default_factory=lambda: [
        Path("example_templates"),
        Path("website_outlines"),
        Path("LLM_COMPONENT_GUIDE.md"),
    ])

    # ── Chunking ──
    chunk_max_tokens: int = 400
    chunk_overlap_tokens: int = 50       # Context bleed between chunks
    yaml_split_on_top_level: bool = True # Split at `- name:` boundaries

    # ── Embedding ──
    embedding_model: str = "nomic-embed-text"  # Ollama model name
    embedding_dim: int = 768
    embedding_fallback: str = "all-MiniLM-L6-v2"  # sentence-transformers
    embedding_backend: str = "ollama"    # "ollama" | "sentence-transformers"

    # ── Retrieval ──
    vector_top_k: int = 15              # Candidates from vector search
    bm25_top_k: int = 15               # Candidates from BM25
    rrf_k: int = 60                     # RRF constant
    final_top_k: int = 5               # Chunks sent to SLM after fusion
    use_reranker: bool = False          # V2 feature, off by default

    # ── Context Budget (tokens) ──
    # Dynamic by intent; these are max ceilings
    context_budget_create_page: int = 2048
    context_budget_create_section: int = 1536
    context_budget_modify: int = 1024   # Leaves room for existing YAML
    context_budget_default: int = 1536
    system_prompt_budget: int = 300     # Condensed rules

    # ── Generation Model ──
    model_backend: str = os.getenv("RAG_MODEL_BACKEND", "ollama")
    model_name: str = os.getenv("RAG_MODEL_NAME", "phi4-mini")

    # ── Cache ──
    query_cache_size: int = 128         # LRU cache entries for embedding+retrieval

    # ── Index Versioning ──
    auto_rebuild_on_stale: bool = False  # Log warning only; don't auto-rebuild


config = RAGConfig()
```

---

## 5. Phase 1 — Document Ingestion & Chunking

Chunking quality is the single biggest determinant of RAG output quality. Get this wrong and no amount of retrieval optimization will help.

### 5.1 Chunking Strategy Comparison

| Approach | How It Works | Pros | Cons | Verdict |
|---|---|---|---|---|
| **Naive text split** (LangChain-style) | Split every N tokens with overlap | Simple, generic | Breaks YAML mid-component, loses structure | ❌ Reject |
| **Markdown header split** | Split at `##` headings | Good for guide docs | Doesn't understand YAML component boundaries | ⚠️ Only for `.md` files |
| **YAML-aware semantic split** | Split at top-level `- name:` in `components:` arrays | Preserves complete components | Requires custom parser | ✅ Use for templates |
| **AST-based split** | Parse YAML into tree, split at subtree boundaries | Most accurate | Over-engineered for this corpus size | ❌ Overkill for V1 |

**Decision: YAML-aware split for templates + markdown header split for guide docs.**

### 5.2 Chunker Implementation (`chunker.py`)

```python
"""ssr_python/rag/indexing/chunker.py"""
import re
import yaml
from dataclasses import dataclass
from pathlib import Path

from rag.config import config


@dataclass
class Chunk:
    id: str                    # Unique: "{source_file}::{chunk_index}"
    content: str               # Raw YAML/markdown fragment
    context_header: str        # Parent context for embedding enrichment
    content_with_context: str  # context_header + content (used for embedding)
    source_file: str
    doc_type: str              # template | outline | guide | config
    metadata: dict             # Component types, industry, section, etc.
    token_count: int


class DocumentChunker:
    """Routes documents to the right chunking strategy."""

    def chunk_file(self, file_path: Path) -> list[Chunk]:
        suffix = file_path.suffix.lower()
        content = file_path.read_text(encoding="utf-8")

        if suffix in (".yaml", ".yml"):
            return self._chunk_yaml_template(content, file_path)
        elif suffix == ".md":
            return self._chunk_markdown(content, file_path)
        else:
            return self._chunk_plain_text(content, file_path)

    # ── YAML Template Chunking ──

    def _chunk_yaml_template(self, content: str, path: Path) -> list[Chunk]:
        """Split YAML at top-level component boundaries.

        Each `- name:` block under `components:` becomes a chunk.
        Site/page metadata is extracted as context_header for every chunk.
        """
        chunks = []
        try:
            doc = yaml.safe_load(content)
        except yaml.YAMLError:
            # Fallback to regex-based splitting if YAML is malformed
            return self._chunk_yaml_by_regex(content, path)

        # Extract site-level context (theme, fonts, colors)
        site_ctx = self._extract_site_context(doc)

        # NOTE: SwiftSites YAML uses list root: [{name: site, components: [{name: page, ...}]}]
        # Navigate: doc[0] → site → components → find page → components
        site_node = doc[0] if isinstance(doc, list) else doc
        pages = [c for c in site_node.get("components", []) if c.get("name") == "page"]
        for page in pages:
            page_name = page.get("slug", page.get("title", "unknown"))
            components = page.get("components", [])

            for i, comp in enumerate(components):
                comp_yaml = yaml.dump(
                    [comp], default_flow_style=False, allow_unicode=True
                )
                header = (
                    f"# Source: {path.name} | Page: {page_name}\n"
                    f"# Theme: {site_ctx}\n"
                    f"# Component {i+1}/{len(components)}"
                )
                chunk_id = f"{path.stem}::p{page_name}::c{i}"

                chunks.append(Chunk(
                    id=chunk_id,
                    content=comp_yaml,
                    context_header=header,
                    content_with_context=f"{header}\n{comp_yaml}",
                    source_file=str(path),
                    doc_type="template",
                    metadata={},   # Filled by metadata.py
                    token_count=0, # Filled by token counter
                ))

        # Also chunk the full-page as one unit for create_page intent
        if len(components) <= 8:  # Only if page isn't huge
            full_yaml = yaml.dump(doc, default_flow_style=False)
            chunks.append(Chunk(
                id=f"{path.stem}::full_page",
                content=full_yaml,
                context_header=f"# FULL PAGE: {path.name} | {site_ctx}",
                content_with_context=f"# FULL PAGE: {path.name}\n{full_yaml}",
                source_file=str(path),
                doc_type="template_full_page",
                metadata={},
                token_count=0,
            ))

        return chunks

    def _extract_site_context(self, doc) -> str:
        """Pull theme info (colors, fonts) into a one-line summary.

        NOTE: doc is list root: [{name: site, properties: {theme: {...}}}]
        """
        site = doc[0] if isinstance(doc, list) else doc
        props = site.get("properties", {})
        theme = props.get("theme", {})
        colors = theme.get("colors", {})
        fonts = theme.get("fonts", {})
        primary = colors.get("primary", "?")
        bg = colors.get("background", "?")
        font = fonts.get("heading", fonts.get("content", "?"))
        return f"primary={primary} bg={bg} font={font}"

    # ── Markdown Chunking ──

    def _chunk_markdown(self, content: str, path: Path) -> list[Chunk]:
        """Split markdown at ## headings. Each section = one chunk."""
        sections = re.split(r'^(## .+)$', content, flags=re.MULTILINE)
        chunks = []
        current_heading = "Introduction"

        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            if section.startswith("## "):
                current_heading = section.lstrip("# ").strip()
                continue

            chunk_id = f"{path.stem}::s{i}_{current_heading[:30]}"
            header = f"# Source: {path.name} | Section: {current_heading}"

            chunks.append(Chunk(
                id=chunk_id,
                content=section,
                context_header=header,
                content_with_context=f"{header}\n{section}",
                source_file=str(path),
                doc_type="guide",
                metadata={"section_heading": current_heading},
                token_count=0,
            ))

        return chunks

    def _chunk_yaml_by_regex(self, content: str, path: Path) -> list[Chunk]:
        """Fallback: split YAML at '- name:' lines if parsing fails."""
        blocks = re.split(r'(?=^  - name:)', content, flags=re.MULTILINE)
        chunks = []
        for i, block in enumerate(blocks):
            block = block.strip()
            if not block or len(block) < 20:
                continue
            chunk_id = f"{path.stem}::regex_{i}"
            chunks.append(Chunk(
                id=chunk_id,
                content=block,
                context_header=f"# Source: {path.name} (regex split)",
                content_with_context=f"# Source: {path.name}\n{block}",
                source_file=str(path),
                doc_type="template",
                metadata={},
                token_count=0,
            ))
        return chunks
```

### 5.3 Metadata Extraction (`metadata.py`)

```python
"""ssr_python/rag/indexing/metadata.py"""
import re
from rag.indexing.chunker import Chunk


# Known component types in SwiftSites (must match actual codebase)
COMPONENT_TYPES = {
    # Layout
    "layout-row", "layout-column", "columnsgrid", "form",
    # Text
    "heading", "paragraph", "eyebrow", "caption", "blockquote", "link",
    # Media
    "image", "video", "gif",
    # UI
    "button", "titlebar", "br",
    # Marketing
    "icon", "badge", "rating", "progress-bar", "counter-up", "countdown",
    # Interactive
    "tabs", "accordion", "carousel", "hamburger", "ticker",
    # Forms
    "textbox", "textarea", "dropdown", "checkbox", "radio", "calendar",
}

# Known section patterns
SECTION_PATTERNS = {
    "hero": r"hero|banner|splash|above.?fold",
    "pricing": r"pricing|plans?|tiers?",
    "testimonial": r"testimonial|review|quote|social.?proof",
    "footer": r"footer|bottom|copyright",
    "features": r"features?|benefits?|highlights?",
    "cta": r"call.?to.?action|cta|sign.?up",
    "faq": r"faq|questions?|q\s*&\s*a",
    "contact": r"contact|get.?in.?touch|reach.?us",
}

INDUSTRY_PATTERNS = {
    "saas": r"saas|software|app|platform|dashboard",
    "restaurant": r"restaurant|food|menu|dining|bakery|cafe|coffee",
    "ecommerce": r"shop|store|product|cart|ecommerce",
    "portfolio": r"portfolio|agency|creative|design",
    "health": r"health|medical|clinic|wellness|fitness",
}


def extract_metadata(chunk: Chunk) -> dict:
    """Enrich chunk with searchable metadata fields."""
    text_lower = (chunk.content + " " + chunk.source_file).lower()

    # Component types present in chunk
    comp_types = [t for t in COMPONENT_TYPES if t in text_lower]

    # Section type (first match wins)
    section = "other"
    for sec, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text_lower):
            section = sec
            break

    # Industry
    industry = "general"
    for ind, pattern in INDUSTRY_PATTERNS.items():
        if re.search(pattern, text_lower):
            industry = ind
            break

    # Design tokens used (e.g., xxl, bold, stretch, md)
    tokens = re.findall(
        r'\b(xxs|xs|sm|md|lg|xl|xxl|bold|semibold|stretch|contain|cover)\b',
        text_lower,
    )

    chunk.metadata.update({
        "component_types": comp_types,
        "section_type": section,
        "industry": industry,
        "design_tokens": list(set(tokens)),
        "has_theme": "theme" in text_lower or "colors" in text_lower,
        "is_full_page": chunk.doc_type == "template_full_page",
    })

    return chunk.metadata
```

---

## 6. Phase 2 — Embedding & Indexing

### 6.1 Embedding Model Comparison

| Model | Dims | Context | Speed (CPU) | Quality (MTEB) | Cost | Verdict |
|---|---|---|---|---|---|---|
| **nomic-embed-text** (Ollama) | 768 | 8192 tokens | ~50ms/query | 62.4 avg | $0 local | ✅ Primary |
| **all-MiniLM-L6-v2** (sentence-transformers) | 384 | 512 tokens | ~15ms/query | 56.3 avg | $0 local | ✅ Fallback |
| **text-embedding-3-small** (OpenAI) | 1536 | 8191 tokens | ~100ms/query | 62.3 avg | $0.02/1M tok | ❌ Unnecessary cost |
| **BGE-large-en-v1.5** (HuggingFace) | 1024 | 512 tokens | ~80ms/query | 63.5 avg | $0 local | ⚠️ Heavy for marginal gain |

**Decision: nomic-embed-text via Ollama.** Best quality-to-cost ratio. Falls back to MiniLM if Ollama unavailable.

### 6.2 Vector Index Comparison

| Approach | Lookup Speed (500 docs) | Storage | Complexity | Scale Ceiling | Verdict |
|---|---|---|---|---|---|
| **NumPy brute-force** | <5ms | ~1.5MB `.npz` | Trivial | ~10K chunks | ✅ V1 choice |
| **FAISS Flat** | <3ms | ~1.5MB | Low (pip install) | ~100K chunks | ✅ V1 alt / V2 upgrade |
| **FAISS HNSW** | <1ms | ~3MB | Medium | ~1M chunks | ⚠️ V2 if needed |
| **LEANN** | <5ms | ~54KB | Medium (niche dep) | ~50K chunks | ❌ Risk: small community, limited docs |
| **ChromaDB** | <10ms | ~5MB (with metadata) | Low | ~1M chunks | ❌ Heavy for 500 chunks |

**Decision: NumPy brute-force for V1.** At 500 chunks, brute-force cosine similarity is fast enough and has zero dependencies beyond numpy. Upgrade path to FAISS if the corpus grows past 5K chunks.

### 6.3 Embedding Service (`embed_service.py`)

```python
"""ssr_python/rag/embeddings/embed_service.py"""
import numpy as np
import requests
from functools import lru_cache

from rag.config import config


class EmbedService:
    """Generate embeddings via Ollama or sentence-transformers fallback."""

    def __init__(self):
        self._st_model = None  # Lazy-loaded fallback

    def embed(self, text: str) -> np.ndarray:
        if config.embedding_backend == "ollama":
            return self._embed_ollama(text)
        return self._embed_sentence_transformers(text)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts. Returns (N, dim) array."""
        if config.embedding_backend == "ollama":
            # Ollama doesn't support batch natively; loop
            vecs = [self._embed_ollama(t) for t in texts]
            return np.array(vecs)
        return self._embed_sentence_transformers_batch(texts)

    # ── Ollama backend ──

    def _embed_ollama(self, text: str) -> np.ndarray:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": config.embedding_model, "prompt": text},
            timeout=30,
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
```

### 6.4 Index Builder (`index_builder.py`)

```python
"""ssr_python/rag/indexing/index_builder.py"""
import json
import hashlib
import pickle
import numpy as np
from pathlib import Path
from rank_bm25 import BM25Okapi

from rag.config import config
from rag.indexing.chunker import DocumentChunker, Chunk
from rag.indexing.metadata import extract_metadata
from rag.embeddings.embed_service import EmbedService

import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


class IndexBuilder:
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embed_service = EmbedService()

    def build(self) -> dict:
        """Full pipeline: discover files → chunk → enrich → embed → persist."""
        # 1. Discover all source files
        files = self._discover_files()
        print(f"Found {len(files)} source files")

        # 2. Chunk all files
        all_chunks = []
        for f in files:
            chunks = self.chunker.chunk_file(f)
            all_chunks.extend(chunks)
        print(f"Produced {len(all_chunks)} chunks")

        # 3. Enrich metadata + count tokens
        for chunk in all_chunks:
            extract_metadata(chunk)
            chunk.token_count = len(_enc.encode(chunk.content))

        # 4. Embed (using content_with_context for richer embeddings)
        texts = [c.content_with_context for c in all_chunks]
        embeddings = self.embed_service.embed_batch(texts)
        print(f"Embedded {embeddings.shape[0]} chunks → {embeddings.shape[1]}d")

        # 5. Build BM25 index
        tokenized = [c.content_with_context.lower().split() for c in all_chunks]
        bm25 = BM25Okapi(tokenized)

        # 6. Persist everything
        config.data_dir.mkdir(parents=True, exist_ok=True)

        np.savez_compressed(
            config.data_dir / "vector_index.npz",
            embeddings=embeddings,
        )

        with open(config.data_dir / "bm25_index.pkl", "wb") as f:
            pickle.dump(bm25, f)

        with open(config.data_dir / "chunks.jsonl", "w") as f:
            for chunk in all_chunks:
                f.write(json.dumps({
                    "id": chunk.id,
                    "content": chunk.content,
                    "context_header": chunk.context_header,
                    "content_with_context": chunk.content_with_context,
                    "source_file": chunk.source_file,
                    "doc_type": chunk.doc_type,
                    "metadata": chunk.metadata,
                    "token_count": chunk.token_count,
                }) + "\n")

        # 7. Write version stamp
        source_hash = self._hash_sources(files)
        with open(config.data_dir / "index_meta.json", "w") as f:
            json.dump({
                "source_hash": source_hash,
                "chunk_count": len(all_chunks),
                "embedding_model": config.embedding_model,
                "embedding_dim": config.embedding_dim,
            }, f, indent=2)

        print(f"Index built: {len(all_chunks)} chunks, hash={source_hash[:12]}")
        return {"chunk_count": len(all_chunks), "source_hash": source_hash}

    def is_stale(self) -> bool:
        """Check if source files have changed since last build."""
        meta_path = config.data_dir / "index_meta.json"
        if not meta_path.exists():
            return True
        meta = json.loads(meta_path.read_text())
        current_hash = self._hash_sources(self._discover_files())
        return current_hash != meta.get("source_hash")

    def _discover_files(self) -> list[Path]:
        files = []
        for src in config.source_dirs:
            src = Path(src)
            if src.is_file():
                files.append(src)
            elif src.is_dir():
                files.extend(src.rglob("*.yaml"))
                files.extend(src.rglob("*.yml"))
                files.extend(src.rglob("*.md"))
        return sorted(files)

    def _hash_sources(self, files: list[Path]) -> str:
        h = hashlib.sha256()
        for f in files:
            h.update(f.read_bytes())
        return h.hexdigest()
```

---

## 7. Phase 3 — Retrieval Pipeline

### 7.1 Vector Search (`vector_search.py`)

```python
"""ssr_python/rag/retrieval/vector_search.py"""
import json
import numpy as np
from pathlib import Path

from rag.config import config
from rag.embeddings.embed_service import EmbedService


class VectorSearch:
    def __init__(self):
        self.embed_service = EmbedService()
        self._embeddings = None
        self._chunks = None

    def load(self):
        data = np.load(config.data_dir / "vector_index.npz")
        self._embeddings = data["embeddings"]
        # Precompute norms for cosine similarity
        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True)
        self._normed = self._embeddings / np.maximum(norms, 1e-10)
        self._chunks = self._load_chunks()

    def search(
        self,
        query: str,
        top_k: int = None,
        metadata_filter: dict = None,
    ) -> list[tuple[dict, float]]:
        """Return (chunk_dict, score) pairs sorted by descending similarity."""
        top_k = top_k or config.vector_top_k

        q_vec = self.embed_service.embed(query)
        q_norm = q_vec / np.maximum(np.linalg.norm(q_vec), 1e-10)

        # Cosine similarity via dot product (both normalized)
        scores = self._normed @ q_norm

        # Apply metadata filter before ranking
        if metadata_filter:
            mask = self._build_mask(metadata_filter)
            scores = scores * mask  # Zero out filtered-out chunks

        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(self._chunks[i], float(scores[i])) for i in top_idx]

    def _build_mask(self, filters: dict) -> np.ndarray:
        """Create binary mask: 1 = passes filter, 0 = excluded."""
        mask = np.ones(len(self._chunks), dtype=np.float32)
        for i, chunk in enumerate(self._chunks):
            meta = chunk.get("metadata", {})
            for key, val in filters.items():
                if key == "component_types":
                    # Check if any requested type is present
                    if not set(val) & set(meta.get("component_types", [])):
                        mask[i] = 0.0
                elif meta.get(key) != val:
                    mask[i] = 0.0
        return mask

    def _load_chunks(self) -> list[dict]:
        chunks = []
        with open(config.data_dir / "chunks.jsonl") as f:
            for line in f:
                chunks.append(json.loads(line))
        return chunks
```

### 7.2 BM25 Keyword Search (`keyword_search.py`)

```python
"""ssr_python/rag/retrieval/keyword_search.py"""
import json
import pickle

from rag.config import config


class KeywordSearch:
    def __init__(self):
        self._bm25 = None
        self._chunks = None

    def load(self):
        with open(config.data_dir / "bm25_index.pkl", "rb") as f:
            self._bm25 = pickle.load(f)
        with open(config.data_dir / "chunks.jsonl") as f:
            self._chunks = [json.loads(line) for line in f]

    def search(self, query: str, top_k: int = None) -> list[tuple[dict, float]]:
        top_k = top_k or config.bm25_top_k
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self._chunks[i], float(scores[i])) for i in top_idx if scores[i] > 0]
```

### 7.3 Hybrid Fusion (`hybrid.py`)

**Comparison of fusion strategies:**

| Strategy | How It Works | Pros | Cons | Verdict |
|---|---|---|---|---|
| **Reciprocal Rank Fusion (RRF)** | `1/(k + rank)` per method, sum | Robust, no tuning needed, works well with different score scales | Ignores absolute score magnitude | ✅ Use |
| **Weighted linear combination** | `α * vec_score + (1-α) * bm25_score` | Tunable | Requires score normalization; α is fragile | ❌ Harder to maintain |
| **Interleaving** | Round-robin from each list | Simple | Doesn't consider relative quality | ❌ Naive |

```python
"""ssr_python/rag/retrieval/hybrid.py"""
from collections import defaultdict

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
    ) -> list[dict]:
        """Hybrid retrieval via Reciprocal Rank Fusion."""
        top_k = top_k or config.final_top_k

        # Get results from both methods
        vec_results = self.vector.search(query, metadata_filter=metadata_filter)
        bm25_results = self.keyword.search(query)

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

        # Sort by fused score, return top_k
        sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
        return [chunk_map[cid] for cid in sorted_ids]
```

### 7.4 Reranker — V2 (Off by Default) (`reranker.py`)

```python
"""ssr_python/rag/retrieval/reranker.py"""
from rag.config import config


class Reranker:
    """Cross-encoder reranker. Disabled by default (config.use_reranker)."""

    def __init__(self):
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
        if not config.use_reranker:
            return chunks[:top_k]

        self._load_model()
        pairs = [(query, c["content_with_context"]) for c in chunks]
        scores = self._model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [c for c, _ in ranked[:top_k]]
```

---

## 8. Phase 4 — Agent Layer

### 8.1 Query Analyzer (`query_analyzer.py`)

**Comparison of intent classification approaches:**

| Approach | Accuracy | Latency | Complexity | Verdict |
|---|---|---|---|---|
| **Rule-based (keyword + regex)** | ~85% for this domain | <1ms | Low | ✅ V1 |
| **SLM classification prompt** | ~92% | 200-500ms (extra LLM call) | Medium | ⚠️ V2 if rules fail |
| **Trained classifier (sklearn/BERT)** | ~95% | <10ms | High (needs training data) | ❌ Overkill for V1 |

```python
"""ssr_python/rag/agent/query_analyzer.py"""
import re
from dataclasses import dataclass


@dataclass
class QueryIntent:
    action: str            # create_page | create_section | modify | add | explain
    section_filter: str | None     # hero | pricing | footer | ...
    industry_filter: str | None    # saas | restaurant | ...
    component_filter: list[str]    # ["button", "image", ...]
    sub_queries: list[str]         # Decomposed queries for complex requests


class QueryAnalyzer:
    """Rule-based intent classification with metadata filter extraction."""

    # Intent patterns ordered by specificity (first match wins)
    INTENT_RULES = [
        ("create_page",    r"(create|build|make|generate|design)\b.*(page|website|site|landing)"),
        ("create_section", r"(create|build|make|generate|add|design)\b.*(section|hero|pricing|footer|header|testimonial|faq|cta|features?)"),
        ("modify",         r"(change|update|modify|edit|replace|adjust|fix|set|make it)\b"),
        ("add",            r"(add|insert|include|put|append)\b.*(button|image|text|icon|badge|card|link)"),
        ("explain",        r"(what|how|explain|tell me|describe|show me|list|which)\b"),
    ]

    SECTION_KEYWORDS = {
        "hero": r"\bhero\b|banner|splash|above.?fold",
        "pricing": r"\bpricing\b|plans?\b|tiers?\b",
        "testimonial": r"\btestimonial\b|reviews?\b|social.?proof",
        "footer": r"\bfooter\b",
        "features": r"\bfeatures?\b|benefits?\b",
        "cta": r"\bcta\b|call.?to.?action|sign.?up",
        "faq": r"\bfaq\b|questions?\b",
        "contact": r"\bcontact\b",
        "header": r"\bheader\b|\bnav\b|navigation",
    }

    INDUSTRY_KEYWORDS = {
        "saas": r"\bsaas\b|software|app\b|platform|startup|tech",
        "restaurant": r"restaurant|food|menu|bakery|cafe|coffee|pizza",
        "ecommerce": r"shop|store|product|ecommerce|retail",
        "portfolio": r"portfolio|agency|freelanc|creative",
        "health": r"health|medical|clinic|wellness|fitness|gym",
    }

    COMPONENT_KEYWORDS = {
        "button": r"\bbutton\b|\bcta\b",
        "image": r"\bimage\b|\bphoto\b|\bpicture\b",
        "badge": r"\bbadge\b|\btag\b|\blabel\b",
        "icon": r"\bicon\b",
        "card": r"\bcard\b",
        "form": r"\bform\b|\binput\b|\bfield\b",
        "video": r"\bvideo\b",
    }

    def analyze(self, query: str) -> QueryIntent:
        q = query.lower().strip()

        # Classify intent
        action = "create_section"  # default
        for intent_name, pattern in self.INTENT_RULES:
            if re.search(pattern, q):
                action = intent_name
                break

        # Extract filters
        section = self._match_first(q, self.SECTION_KEYWORDS)
        industry = self._match_first(q, self.INDUSTRY_KEYWORDS)
        components = [
            name for name, pat in self.COMPONENT_KEYWORDS.items()
            if re.search(pat, q)
        ]

        # Decompose complex create_page queries
        sub_queries = self._decompose(q, action)

        return QueryIntent(
            action=action,
            section_filter=section,
            industry_filter=industry,
            component_filter=components,
            sub_queries=sub_queries,
        )

    def _match_first(self, text: str, patterns: dict) -> str | None:
        for name, pat in patterns.items():
            if re.search(pat, text):
                return name
        return None

    def _decompose(self, query: str, action: str) -> list[str]:
        """Split complex queries into sub-queries for parallel retrieval."""
        if action != "create_page":
            return [query]

        # Look for enumerated sections: "with hero, pricing, and testimonials"
        match = re.search(r"with\s+(.+)", query)
        if not match:
            return [query]

        parts_text = match.group(1)
        parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", parts_text)
        sections = [p.strip() for p in parts if p.strip()]

        if len(sections) > 1:
            return [f"{s} section template" for s in sections]
        return [query]
```

### 8.2 Prompt Builder (`prompt_builder.py`)

```python
"""ssr_python/rag/agent/prompt_builder.py"""
import tiktoken

from rag.config import config
from rag.agent.query_analyzer import QueryIntent

_enc = tiktoken.get_encoding("cl100k_base")


# Condensed system rules (~350 tokens instead of 78KB)
# NOTE: This prompt MUST match actual SwiftSites components from LLM_COMPONENT_GUIDE.md.
# If the guide changes, regenerate this condensed version.
CONDENSED_SYSTEM = """You are SwiftSites, a YAML website generator.

OUTPUT FORMAT: Always respond with an ACTION line then a YAML code block.
Actions: create, modify, delete, insert_child, insert_after, explain, settings

STRUCTURE: site > page.components[] (theme is at site.properties.theme, NOT page level)
- Every component has: name, properties, optional components (children)
- Array properties (items, tabs, slides, columns) go at COMPONENT LEVEL, NOT inside properties

VALID COMPONENTS:
- Layout: layout-row, layout-column, columnsgrid, form
- Text: heading, paragraph, eyebrow, caption, blockquote, link
- Media: image, video, gif, video-background, br
- UI: button, titlebar, hamburger
- Interactive: tabs, accordion, carousel, ticker
- Marketing: icon, badge, rating, progress-bar, counter-up, countdown
- Forms: textbox, textarea, dropdown, checkbox, radio, calendar

KEY PROPERTIES:
- heading: text, level (1-6), typography: {size, weight, color, align}
- paragraph: text (supports | multiline), typography: {size, color}
- button: text, link: {url, target}, appearance: {background: {color}, radius}
- image: source: {url, altText}, appearance: {fit: cover, aspectRatio, minHeight}
- layout-row: layout: {horizontalAlign, verticalAlign, wrap, gap}, components: [...]
- layout-column: layout: {horizontalAlign, widthMode}, components: [...]
- widthMode goes in layout.widthMode (NOT appearance). Values: fit, 25, 33, 50, 66, 75, stretch
- Theme colors: primary, secondary, accent, background. Theme fonts: heading, content.
- Spacing tokens: none, xxs, xs, sm, md, lg, xl, xxl, xxxl (t-shirt sizes)
- Wrap ALL text values containing special chars in quotes.

Follow the patterns in the examples below exactly. Do not invent component types or properties."""


class PromptBuilder:
    def build(
        self,
        intent: QueryIntent,
        chunks: list[dict],
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
    ) -> tuple[str, str]:
        """Build (system_prompt, user_prompt) for the SLM.

        Returns a tuple so model_backend can pass them separately.
        """
        # Dynamic budget based on intent
        budget = self._get_budget(intent, current_yaml)

        # Assemble retrieved context within budget
        ctx_parts = []
        tokens_used = 0
        for chunk in chunks:
            chunk_tokens = chunk.get("token_count", len(_enc.encode(chunk["content"])))
            if tokens_used + chunk_tokens > budget:
                break
            source = chunk.get("source_file", "unknown")
            ctx_parts.append(
                f"--- Example from: {source} ---\n{chunk['content']}"
            )
            tokens_used += chunk_tokens

        context_block = "\n\n".join(ctx_parts)

        # System prompt
        system = CONDENSED_SYSTEM

        # User prompt
        user_parts = []

        if context_block:
            user_parts.append(f"[Reference Examples]\n{context_block}")

        if current_yaml:
            user_parts.append(f"[Current YAML]\n{current_yaml}")

        if selected_component:
            user_parts.append(f"[Selected Component]\n{selected_component}")

        user_parts.append(f"[User Request]\n{message}")

        user_prompt = "\n\n".join(user_parts)
        return system, user_prompt

    def _get_budget(self, intent: QueryIntent, current_yaml: str | None) -> int:
        """Dynamic token budget — reserve room for existing YAML in modify tasks."""
        if intent.action == "create_page":
            return config.context_budget_create_page
        if intent.action == "modify" and current_yaml:
            yaml_tokens = len(_enc.encode(current_yaml))
            # Shrink retrieval budget if existing YAML is large
            return max(512, config.context_budget_modify - yaml_tokens // 2)
        if intent.action == "create_section":
            return config.context_budget_create_section
        return config.context_budget_default
```

### 8.3 Model Backend (`model_backend.py`)

```python
"""ssr_python/rag/agent/model_backend.py"""
import os
import requests

from rag.config import config


class ModelBackend:
    """Pluggable generation backend. Switch via config.model_backend."""

    def generate(self, system: str, user_prompt: str) -> str:
        backend = config.model_backend
        if backend == "ollama":
            return self._ollama(system, user_prompt)
        elif backend == "openai":
            return self._openai(system, user_prompt)
        elif backend == "anthropic":
            return self._anthropic(system, user_prompt)
        elif backend == "groq":
            return self._groq(system, user_prompt)
        raise ValueError(f"Unknown backend: {backend}")

    # ── Ollama (local) ──

    def _ollama(self, system: str, user_prompt: str) -> str:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": config.model_name,
                "system": system,
                "prompt": user_prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 4096},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    # ── OpenAI ──

    def _openai(self, system: str, user_prompt: str) -> str:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return resp.choices[0].message.content

    # ── Anthropic ──

    def _anthropic(self, system: str, user_prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model=config.model_name,
            system=system,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        return resp.content[0].text

    # ── Groq ──

    def _groq(self, system: str, user_prompt: str) -> str:
        import groq
        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        return resp.choices[0].message.content
```

### 8.4 RAG Agent Orchestrator (`rag_agent.py`)

```python
"""ssr_python/rag/agent/rag_agent.py"""
import logging
from functools import lru_cache

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.query_analyzer import QueryAnalyzer
from rag.agent.prompt_builder import PromptBuilder
from rag.agent.model_backend import ModelBackend

logger = logging.getLogger(__name__)


class RAGAgent:
    def __init__(self):
        self.search = HybridSearch()
        self.reranker = Reranker()
        self.analyzer = QueryAnalyzer()
        self.prompt_builder = PromptBuilder()
        self.model = ModelBackend()
        self._loaded = False

    def load(self):
        """Load indexes into memory. Call once at app startup."""
        if not self._loaded:
            self.search.load()
            self._loaded = True
            logger.info("RAG indexes loaded")

    def chat(
        self,
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
    ) -> str:
        """Full RAG pipeline: analyze → retrieve → build prompt → generate."""
        self.load()

        # 1. Analyze intent
        intent = self.analyzer.analyze(message)
        logger.info(f"Intent: {intent.action} | section={intent.section_filter} | industry={intent.industry_filter}")

        # 2. Build metadata filter from intent
        meta_filter = {}
        if intent.section_filter:
            meta_filter["section_type"] = intent.section_filter
        if intent.industry_filter:
            meta_filter["industry"] = intent.industry_filter

        # 3. Retrieve for each sub-query, deduplicate
        all_chunks = []
        seen_ids = set()
        for sub_q in intent.sub_queries:
            results = self.search.search(
                sub_q,
                top_k=config.vector_top_k,
                metadata_filter=meta_filter or None,
            )
            for chunk in results:
                if chunk["id"] not in seen_ids:
                    seen_ids.add(chunk["id"])
                    all_chunks.append(chunk)

        # 4. Rerank (no-op if config.use_reranker is False)
        ranked = self.reranker.rerank(message, all_chunks, top_k=config.final_top_k)
        logger.info(f"Retrieved {len(ranked)} chunks for generation")

        # 5. Build prompt
        system, user_prompt = self.prompt_builder.build(
            intent=intent,
            chunks=ranked,
            message=message,
            current_yaml=current_yaml,
            selected_component=selected_component,
        )

        # 6. Generate
        response = self.model.generate(system, user_prompt)

        # 7. Validation-guided retry (Phase 7.5 from original plan)
        response = self._validate_and_retry(response, message, system, ranked)

        return response

    def _validate_and_retry(
        self, response: str, message: str, system: str, chunks: list[dict],
        max_retries: int = 1,
    ) -> str:
        """If YAML validation fails, retry with error context. Up to max_retries."""
        for attempt in range(max_retries):
            error = self._quick_validate(response)
            if error is None:
                return response

            logger.warning(f"Validation failed (attempt {attempt+1}): {error}")

            # Re-prompt with error info
            retry_prompt = (
                f"Your previous output had a YAML error: {error}\n"
                f"Fix the error and regenerate. Original request: {message}"
            )
            _, user_prompt = self.prompt_builder.build(
                intent=self.analyzer.analyze(message),
                chunks=chunks,
                message=retry_prompt,
            )
            response = self.model.generate(system, user_prompt)

        return response

    def _quick_validate(self, response: str) -> str | None:
        """Fast validation: check YAML parses and has required structure.

        Returns error message string, or None if valid.
        """
        import yaml as pyyaml
        import re

        # Extract YAML block from response
        match = re.search(r"```(?:yaml)?\s*\n(.+?)```", response, re.DOTALL)
        if not match:
            # If no code block, check if response itself is YAML
            if "site:" not in response and "- name:" not in response:
                return None  # Probably an EXPLAIN response, skip validation
            yaml_str = response
        else:
            yaml_str = match.group(1)

        try:
            doc = pyyaml.safe_load(yaml_str)
        except pyyaml.YAMLError as e:
            return f"YAML parse error: {e}"

        if doc is None:
            return "Empty YAML document"

        return None
```

### 8.5 Sequential Multi-Agent Pipeline (for `create_page` intent)

Single-shot generation degrades with page complexity. Instead, use a **sequential multi-agent pipeline** where each agent has a focused task with minimal context:

```
User Query ("Create a bakery website with hero, menu, and testimonials")
         │
    ┌────▼───────────────────────┐
    │ AGENT 1: Site Planner       │  Generates structured outline
    │                             │  Input: user query + industry RAG chunks (outlines)
    │  Output: JSON outline       │  Output: [{section: "hero", elements: [...]}, ...]
    └────┬───────────────────────┘
         │  (list of sections/elements)
         │
    ┌────▼───────────────────────┐
    │ AGENT 2: Component Builder  │  Iterates over EACH outline element
    │  (called N times)           │  Input: element description + RAG template chunks
    │                             │  Output: YAML component for that element
    └────┬───────────────────────┘
         │  (N YAML fragments)
         │
    ┌────▼───────────────────────┐
    │ STITCHER: Page Assembler    │  Combines all components into one page
    │  (pure Python, no LLM)      │  Adds site wrapper, theme, page structure
    └────┬───────────────────────┘
         │
    Final complete YAML page
```

#### Agent 1: Site Planner (`planner_agent.py`)

**Input:** User query + RAG-retrieved outline chunks (from `website_example_outlines/`)
**Output:** Structured JSON outline listing sections with component hints

```python
"""ssr_python/rag/agent/planner_agent.py"""
import json
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.agent.model_backend import ModelBackend

logger = logging.getLogger(__name__)

PLANNER_SYSTEM = """You are a website architect. Given a user request, generate a JSON outline for a website page.

OUTPUT FORMAT: Return ONLY valid JSON (no markdown, no explanation). Structure:
{
  "page_title": "Page Title",
  "theme": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "heading_font": "'Font Name', serif",
    "content_font": "'Font Name', sans-serif"
  },
  "sections": [
    {
      "type": "hero|features|pricing|testimonials|cta|faq|contact|footer|...",
      "description": "Brief description of what this section contains and its layout",
      "components": ["layout-row", "image", "heading", "paragraph", "button"]
    }
  ]
}

RULES:
- Use ONLY valid SwiftSites components: layout-row, layout-column, columnsgrid, heading, paragraph, eyebrow, caption, blockquote, link, image, video, gif, button, titlebar, br, icon, badge, rating, progress-bar, counter-up, countdown, tabs, accordion, carousel, hamburger, ticker, textbox, textarea, dropdown, checkbox, radio, calendar
- Keep sections focused: 3-8 sections per page
- Match the industry and tone to the user's request
- Use the reference outlines below as structural inspiration"""


class PlannerAgent:
    def __init__(self, search: HybridSearch, model: ModelBackend):
        self.search = search
        self.model = model

    def plan(self, query: str) -> dict:
        """Generate a site outline from user query."""
        # Retrieve relevant website outlines for structural guidance
        outline_chunks = self.search.search(
            query,
            top_k=3,
            metadata_filter={"doc_type": "outline"},
        )

        # Build context from retrieved outlines
        context = "\n\n".join([
            f"--- Reference: {c['source_file']} ---\n{c['content'][:800]}"
            for c in outline_chunks
        ])

        user_prompt = f"[Reference Outlines]\n{context}\n\n[User Request]\n{query}"

        # Generate outline
        response = self.model.generate(PLANNER_SYSTEM, user_prompt)

        # Parse JSON (strip markdown if model wraps it)
        return self._parse_outline(response)

    def _parse_outline(self, response: str) -> dict:
        """Extract JSON from model response."""
        import re
        # Try to extract JSON from code block
        match = re.search(r'```(?:json)?\s*\n(.+?)```', response, re.DOTALL)
        text = match.group(1) if match else response

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to find JSON object in response
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Could not parse outline JSON from response: {text[:200]}")
```

#### Agent 2: Component Builder (`builder_agent.py`)

Called once per section from the planner's outline. Gets section-specific RAG chunks.

```python
"""ssr_python/rag/agent/builder_agent.py"""
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.retrieval.reranker import Reranker
from rag.agent.model_backend import ModelBackend

logger = logging.getLogger(__name__)

BUILDER_SYSTEM = """You are a SwiftSites YAML component builder. Given a section description and theme, generate the YAML components for that section.

OUTPUT FORMAT: Return ONLY valid YAML (in a ```yaml code block). Output the section's root component(s) — typically a layout-row or layout-column with nested children.

CRITICAL RULES:
- Use 2-space YAML indentation
- Use ONLY valid SwiftSites component names and properties
- Apply the provided theme colors and fonts consistently
- Follow the example templates below for correct structure and property names
- Wrap text values containing special characters in quotes
- layout-row children need layout.widthMode (e.g., "50", "33", "stretch")
- Use t-shirt sizes for tokens: xxs, xs, sm, md, lg, xl, xxl"""


class BuilderAgent:
    def __init__(self, search: HybridSearch, reranker: Reranker, model: ModelBackend):
        self.search = search
        self.reranker = reranker
        self.model = model

    def build_section(self, section: dict, theme: dict) -> str:
        """Generate YAML for a single section.

        Args:
            section: {type, description, components} from planner outline
            theme: {primary, secondary, accent, background, heading_font, content_font}

        Returns:
            YAML string for this section's components
        """
        section_type = section.get("type", "other")
        description = section.get("description", "")

        # Retrieve template chunks matching this section type
        chunks = self.search.search(
            f"{section_type} section template",
            top_k=config.vector_top_k,
            metadata_filter={"section_type": section_type},
        )

        # Rerank for relevance (no-op if disabled)
        ranked = self.reranker.rerank(
            f"{section_type} {description}",
            chunks,
            top_k=3,
        )

        # Build context from retrieved templates
        context = "\n\n".join([
            f"--- Example: {c['source_file']} ---\n{c['content']}"
            for c in ranked
        ])

        # Build theme string
        theme_str = (
            f"Theme colors: primary={theme.get('primary', '#1a1a1a')}, "
            f"secondary={theme.get('secondary', '#666')}, "
            f"accent={theme.get('accent', '#3b82f6')}, "
            f"background={theme.get('background', '#ffffff')}\n"
            f"Theme fonts: heading={theme.get('heading_font', 'sans-serif')}, "
            f"content={theme.get('content_font', 'sans-serif')}"
        )

        user_prompt = (
            f"[Reference Templates]\n{context}\n\n"
            f"[Theme]\n{theme_str}\n\n"
            f"[Section to Build]\n"
            f"Type: {section_type}\n"
            f"Description: {description}\n"
            f"Suggested components: {', '.join(section.get('components', []))}"
        )

        response = self.model.generate(BUILDER_SYSTEM, user_prompt)
        return self._extract_yaml(response)

    def _extract_yaml(self, response: str) -> str:
        """Extract YAML from model response."""
        import re
        match = re.search(r'```(?:yaml)?\s*\n(.+?)```', response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()
```

#### Stitcher: Page Assembler (`stitcher.py`)

Pure Python — no LLM call. Combines planner theme + builder outputs into a complete page.

```python
"""ssr_python/rag/agent/stitcher.py"""
import yaml
import logging

logger = logging.getLogger(__name__)


def stitch_page(outline: dict, section_yamls: list[str]) -> str:
    """Combine planner outline + builder outputs into full page YAML.

    Args:
        outline: Planner JSON with page_title, theme, sections
        section_yamls: List of YAML strings from builder (one per section)

    Returns:
        Complete page YAML string ready for the editor
    """
    theme = outline.get("theme", {})

    page = [{
        "name": "site",
        "properties": {
            "theme": {
                "fonts": {
                    "heading": theme.get("heading_font", "'Inter', sans-serif"),
                    "content": theme.get("content_font", "'Inter', sans-serif"),
                },
                "colors": {
                    "primary": theme.get("primary", "#1a1a1a"),
                    "secondary": theme.get("secondary", "#6b7280"),
                    "accent": theme.get("accent", "#3b82f6"),
                    "background": theme.get("background", "#ffffff"),
                },
            },
        },
        "components": [{
            "name": "page",
            "slug": "home",
            "title": outline.get("page_title", "New Page"),
            "properties": {
                "appearance": {
                    "background": {
                        "color": theme.get("background", "#ffffff"),
                        "transparency": 100,
                    }
                }
            },
            "components": [],
        }],
    }]

    # Parse and merge each section's YAML into the page
    for i, section_yaml in enumerate(section_yamls):
        try:
            parsed = yaml.safe_load(section_yaml)
            if parsed is None:
                logger.warning(f"Section {i} produced empty YAML, skipping")
                continue
            if isinstance(parsed, list):
                page[0]["components"][0]["components"].extend(parsed)
            elif isinstance(parsed, dict):
                page[0]["components"][0]["components"].append(parsed)
        except yaml.YAMLError as e:
            logger.error(f"Section {i} has invalid YAML: {e}")
            # Skip bad sections rather than failing the whole page
            continue

    return yaml.dump(page, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

#### Updated RAG Agent with Multi-Agent Routing

The `rag_agent.py` `chat()` method routes `create_page` intent to the multi-agent pipeline:

```python
# Add to RAGAgent.__init__():
from rag.agent.planner_agent import PlannerAgent
from rag.agent.builder_agent import BuilderAgent
from rag.agent.stitcher import stitch_page

# In __init__:
self.planner = PlannerAgent(self.search, self.model)
self.builder = BuilderAgent(self.search, self.reranker, self.model)

# Replace chat() method:
def chat(self, message, current_yaml=None, selected_component=None):
    self.load()
    intent = self.analyzer.analyze(message)

    if intent.action == "create_page":
        return self._create_page_pipeline(message, intent)
    else:
        return self._single_call_rag(message, intent, current_yaml, selected_component)

def _create_page_pipeline(self, message: str, intent) -> str:
    """Multi-agent pipeline: planner → builder × N → stitcher."""
    # Agent 1: Plan the page structure
    outline = self.planner.plan(message)
    logger.info(f"Planner produced {len(outline.get('sections', []))} sections")

    # Agent 2: Build each section
    section_yamls = []
    theme = outline.get("theme", {})
    for i, section in enumerate(outline.get("sections", [])):
        logger.info(f"Building section {i+1}: {section.get('type')}")
        yaml_str = self.builder.build_section(section, theme)
        section_yamls.append(yaml_str)

    # Stitch into complete page
    full_yaml = stitch_page(outline, section_yamls)

    # Return in expected format
    return f"<!-- ACTION: create -->\nHere's your {outline.get('page_title', 'page')}:\n\n```yaml\n{full_yaml}```"
```

#### Why Multi-Agent Is Better Than Single-Shot

| Aspect | Single-Shot | Multi-Agent Sequential |
|---|---|---|
| **Context per call** | 2-4KB chunks for entire page | 1-2KB chunks per section (more focused) |
| **SLM accuracy** | Degrades with page complexity | Consistent (each call is simple) |
| **Error isolation** | One bad section ruins entire page | Retry just the failing section |
| **RAG precision** | Generic retrieval for whole query | Section-specific retrieval (hero chunks for hero, etc.) |
| **Scalability** | Limited by SLM context window | N sections = N focused calls |

#### Routing Summary

| Intent | Pipeline | Details |
|---|---|---|
| `create_page` | Multi-agent | Planner → Builder × N → Stitcher |
| `create_section` | Single builder call | Section-type RAG retrieval → builder |
| `modify` / `add` | Single RAG call | Existing rag_agent.py pattern |
| `explain` | Single RAG call | No YAML generation |

---

## 9. Phase 5 — Integration with Existing App

### 9.1 Modified `llm_service.py`

```python
# In llm_service.py — add RAG as primary path

from rag.agent.rag_agent import RAGAgent
from rag.config import config as rag_config

class LLMService:
    def __init__(self):
        self.rag_agent = RAGAgent()
        self.use_rag = os.getenv("RAG_ENABLED", "false").lower() == "true"

        if self.use_rag:
            self.rag_agent.load()

    def chat(self, message, current_yaml=None, selected_component=None):
        if self.use_rag:
            return self.rag_agent.chat(message, current_yaml, selected_component)
        return self._legacy_chat(message, current_yaml, selected_component)

    def _legacy_chat(self, message, current_yaml, selected_component):
        # ... existing implementation unchanged ...
        pass
```

### 9.2 API Endpoints

```python
# routes/rag.py
from flask import Blueprint, jsonify, request
from rag.indexing.index_builder import IndexBuilder
from rag.agent.rag_agent import RAGAgent

rag_bp = Blueprint("rag", __name__, url_prefix="/api/rag")

@rag_bp.route("/status", methods=["GET"])
def status():
    builder = IndexBuilder()
    stale = builder.is_stale()
    meta_path = config.data_dir / "index_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return jsonify({"stale": stale, **meta})

@rag_bp.route("/rebuild-index", methods=["POST"])
def rebuild():
    builder = IndexBuilder()
    result = builder.build()
    return jsonify(result)

@rag_bp.route("/search", methods=["POST"])
def debug_search():
    """Debug endpoint: test retrieval without generation."""
    data = request.json
    agent = RAGAgent()
    agent.load()
    intent = agent.analyzer.analyze(data["query"])
    meta_filter = {}
    if intent.section_filter:
        meta_filter["section_type"] = intent.section_filter
    results = agent.search.search(data["query"], metadata_filter=meta_filter or None)
    return jsonify({
        "intent": intent.__dict__,
        "results": [{"id": r["id"], "source": r["source_file"], "preview": r["content"][:200]} for r in results],
    })
```

### 9.3 Environment Variables

```env
# ── RAG Toggle ──
RAG_ENABLED=true

# ── Generation Backend (choose one) ──
RAG_MODEL_BACKEND=ollama              # ollama | openai | anthropic | groq
RAG_MODEL_NAME=phi4-mini              # Model for chosen backend

# ── Cloud API Keys (only if using cloud backend) ──
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GROQ_API_KEY=gsk_...
```

---

## 10. Dependencies

```txt
# ssr_python/rag/requirements.txt

# Core (always needed)
rank-bm25>=0.2.2                # BM25 keyword search
tiktoken>=0.7.0                 # Token counting
numpy>=1.24.0                   # Vector math
pyyaml>=6.0                     # YAML parsing (likely already installed)

# Reranker (V2, optional)
# sentence-transformers>=3.0.0  # Only if config.use_reranker=True

# Cloud backends (install only what you use)
# openai>=1.0.0
# anthropic>=0.40.0
# groq>=0.11.0
```

Ollama models (pulled separately):
```bash
ollama pull nomic-embed-text    # Embedding
ollama pull phi4-mini            # Generation (or fine-tuned variant)
```

---

## 11. Execution Order — Incremental Delivery

Build in phases. Each phase is independently testable and delivers value.

### Sprint 1: Retrieval Foundation (get feedback fast)

```bash
# 1. Install core deps
pip install rank-bm25 tiktoken numpy

# 2. Pull embedding model
ollama pull nomic-embed-text

# 3. Build index
python -m rag.scripts.build_index

# 4. Test retrieval quality (no generation yet)
python -m rag.scripts.evaluate_retrieval
```

**Deliverable:** `/api/rag/search` endpoint returns relevant chunks for test queries. Validate >80% relevance in top-5 before proceeding.

### Sprint 2: Multi-Agent Create Page Pipeline

Implement the sequential multi-agent pipeline for `create_page` intent — this is the highest-value feature.

1. Implement `planner_agent.py` — site outline generator
2. Implement `builder_agent.py` — per-section YAML generator
3. Implement `stitcher.py` — pure Python page assembler
4. Update `rag_agent.py` to route `create_page` → multi-agent pipeline
5. Wire into `llm_service.py` with `RAG_ENABLED=true`

```bash
# Enable RAG with current model
RAG_ENABLED=true
RAG_MODEL_BACKEND=ollama
RAG_MODEL_NAME=llama3    # Keep current model for now
```

**Deliverable:** "Create a bakery website" → planner outline → builder per section → stitched full page YAML. Test with 5 different industry/page requests.

### Sprint 3: Single-Call RAG for Modify/Add/Explain

Wire retrieved chunks into `modify`, `add`, `explain` intents using existing LLM backend.

```bash
# RAG already enabled from Sprint 2
# Test modify/add/explain with focused context retrieval
```

**Deliverable:** Side-by-side comparison — RAG path vs legacy 78KB prompt for modification tasks. Measure YAML validity rate and quality on 10 test queries.

### Sprint 4: SLM Swap + Polish

Now swap to a smaller model. The retrieval context compensates for smaller model size.

```bash
ollama pull phi4-mini
RAG_MODEL_NAME=phi4-mini
```

Polish:
- Add query caching (LRU on embedding + retrieval results)
- Add validation-guided retry
- Tune hybrid weights if BM25 vs vector balance is off
- Enable reranker only if retrieval quality metrics justify it

**Deliverable:** Phi-4-mini + RAG produces comparable quality to Llama3 + full prompt, with faster inference and lower memory.

---

## 12. Evaluation & Verification

| Test | Target | How |
|---|---|---|
| Retrieval relevance | >80% of top-5 are relevant | `evaluate_retrieval.py` with 20 sample queries, manual grading |
| Retrieval latency | <200ms per query | Timer in `hybrid.py` |
| YAML validity rate | >90% parse without errors | Parse all generated YAML with `pyyaml.safe_load` |
| Generation quality | RAG ≥ legacy on 10 test queries | Blind comparison: render both outputs, pick better |
| Index build time | <5 minutes | Timer in `build_index.py` |
| Index staleness | Correctly detected | Modify a template, check `is_stale()` returns True |
| Fallback | Legacy works when RAG disabled | Set `RAG_ENABLED=false`, verify chat still works |
| Memory | Index <10MB RSS | Profile with `tracemalloc` |

---

## 13. V2 Roadmap (Post-V1)

These are explicitly deferred. Only pursue after V1 is stable and evaluated.

| Feature | Trigger to Build | Effort |
|---|---|---|
| **Cross-encoder reranker** | Top-5 relevance <80% despite tuning | Low (code exists, just enable) |
| **FAISS index** | Chunk count exceeds 5K | Low (drop-in replacement for numpy) |
| **Multi-turn memory** | Users frequently do "now make it dark" follow-ups | Medium |
| **Self-improving loop** | Need more training examples for fine-tuning | Medium |
| **Agentic multi-section retrieval** | Full-page generation quality is poor | High |
| **Template recommendation** | Want to reduce generation load | Medium |
| **SLM-based intent classifier** | Rule-based accuracy drops below 80% | Low |

---

## 14. Comparison: Current vs RAG Approaches

| Metric | Current (78KB Prompt) | RAG + Local SLM | RAG + Cloud API | Fine-Tuned + RAG |
|---|---|---|---|---|
| Context per request | 78KB (all of it) | ~2-4KB (targeted) | ~2-4KB (targeted) | ~0.5KB system + 2KB chunks |
| Model size required | Large (70B recommended) | 3.8B (Phi-4-mini) | Any (cloud) | 3.8B (fine-tuned) |
| Knowledge updates | Edit guide → restart | Re-index (~5 min) | Re-index (~5 min) | Retrain (hours) |
| API cost | $0 (local) | $0 (local) | ~$0.001/req | $0 (local) |
| Accuracy | Medium (context dilution) | High (focused context) | Highest | Highest |
| Privacy | Full | Full | Data sent to cloud | Full |
| VRAM | 8-16GB | 4-6GB | None | 4-6GB |
| Setup effort | Low | Medium | Low | High |

---

## 15. Key Design Decisions Summary

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| Vector index | NumPy brute-force | LEANN, ChromaDB | 500 chunks → brute-force is <5ms; no dependency risk |
| Fusion strategy | RRF | Weighted linear, interleaving | Robust without score normalization |
| Intent classifier | Rule-based regex | SLM classification, trained model | <1ms latency, ~85% accuracy sufficient for V1 |
| Embedding model | nomic-embed-text (Ollama) | OpenAI, BGE-large | Best quality/cost; local, zero cost |
| Reranker | Off by default | Always-on | Adds latency; prove retrieval is insufficient first |
| Context budget | Dynamic by intent | Fixed budget | Modify tasks need room for existing YAML |
| Chunk context | context_header embedded with content | Embed content only | Isolated chunks lose meaning without parent context |