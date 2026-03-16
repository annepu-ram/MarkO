"""ssr_python/rag/config.py — Central RAG configuration."""
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class RAGConfig:
    # ── Paths ──
    rag_dir: Path = Path(__file__).parent
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent / "data")
    icon_data_path: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "static" / "data" / "lucide-icons.json")
    source_dirs: list[Path] = field(default_factory=lambda: [
        # rag/ -> ssr_python/ -> project root
        Path(__file__).resolve().parent.parent.parent / "example_templates",
        Path(__file__).resolve().parent.parent.parent / "website_example_outlines",
        Path(__file__).resolve().parent.parent / "config" / "COMPONENT_SYNTAX_REFERENCE.md",
        Path(__file__).resolve().parent.parent / "config" / "STYLE_THEMES_REFERENCE.md",
    ])

    # ── Tiers ──
    tier_doc_types: dict = field(default_factory=lambda: {
        "section": {"template_section", "template_full_page"},
        "component": {"template"},
        "guide": {"guide", "outline", "other"},
        "style": {"style"},
        "icon": {"icon"},
    })

    # ── Chunking ──
    chunk_max_tokens: int = 400
    chunk_overlap_tokens: int = 50       # Context bleed between chunks
    yaml_split_on_top_level: bool = True  # Split at `- name:` boundaries
    section_chunk_max_chars: int = 4000  # Max YAML chars in section-level chunks

    # ── Embedding ──
    embedding_model: str = "nomic-embed-text"  # Ollama model name
    embedding_dim: int = 768
    embedding_fallback: str = "all-MiniLM-L6-v2"  # sentence-transformers
    embedding_backend: str = "ollama"    # "ollama" | "sentence-transformers"

    # ── Retrieval ──
    vector_top_k: int = 15              # Candidates from vector search
    bm25_top_k: int = 15               # Candidates from BM25
    rrf_k: int = 60                     # RRF constant
    final_top_k: int = 2               # Chunks sent to SLM after fusion
    use_reranker: bool = False          # V2 feature, off by default
    mmr_lambda: float = 0.8            # MMR diversity (0=diverse, 1=relevant)
    planner_top_k: int = 1            # Outline chunks for planner agent
    mmr_pool_multiplier: int = 3       # MMR candidates = top_k * this
    mmr_pool_min_size: int = 15        # Min MMR candidate pool
    min_fallback_results: int = 2      # Tier fallback threshold
    icon_top_k: int = 20               # Individual icon vectors to retrieve
    style_top_k: int = 2               # Style chunks for planner agent

    # ── Context Budget (tokens) ──
    context_budget_create_page: int = 4096
    context_budget_create_section: int = 3000
    context_budget_modify: int = 1500   # Leaves room for existing YAML
    context_budget_default: int = 1500
    system_prompt_budget: int = 400     # Condensed rules
    min_context_budget: int = 512       # Floor for context budget

    # ── Generation Model ──
    model_backend: str = os.getenv("RAG_MODEL_BACKEND", "ollama")
    model_name: str = os.getenv("RAG_MODEL_NAME", "phi4-mini")
    temperature_ollama: float = 1.3     # Temperature for Ollama backend
    temperature_cloud: float = 0.3      # Temperature for OpenAI/Anthropic/Groq
    max_generation_tokens: int = 4096   # Max tokens for all backends

    # ── Reranker ──
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # ── Theme Defaults ──
    default_theme: dict = field(default_factory=lambda: {
        "primary": "#1a1a1a",
        "text": "#374151",
        "secondary": "#6b7280",
        "accent": "#3b82f6",
        "background": "#ffffff",
        "heading_font": "'Inter', sans-serif",
        "content_font": "'Inter', sans-serif",
    })

    # ── YAML Output ──
    yaml_line_width: int = 200          # ruamel.yaml output width

    # ── Cache ──
    query_cache_size: int = 128         # LRU cache entries for embedding+retrieval

    # ── Index Versioning ──
    auto_rebuild_on_stale: bool = False  # Log warning only; don't auto-rebuild


config = RAGConfig()
TIER_NAMES = tuple(config.tier_doc_types.keys())
