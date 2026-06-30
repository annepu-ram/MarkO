"""Campaign section RAG configuration.

This is intentionally separate from ``rag.config`` because campaign-driven
section generation has a different contract from full website generation:
brand-owned style direction is persisted, and section generation consumes
approved content plus that saved brand style prompt.
"""
from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass
class CampaignRAGConfig:
    prompts_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "prompts")
    logs_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "logs" / "campaign_rag")

    model_backend: str = field(default_factory=lambda: os.getenv("CAMPAIGN_RAG_MODEL_BACKEND", os.getenv("RAG_MODEL_BACKEND", "ollama")))
    model_name: str = field(default_factory=lambda: os.getenv("CAMPAIGN_RAG_MODEL_NAME", os.getenv("RAG_MODEL_NAME", "phi4-mini")))
    section_model_name: str = field(default_factory=lambda: os.getenv("CAMPAIGN_SECTION_MODEL_NAME", os.getenv("RAG_BUILDER_MODEL_NAME", "")))
    brand_styler_model_name: str = field(default_factory=lambda: os.getenv("CAMPAIGN_BRAND_STYLER_MODEL_NAME", ""))

    temperature_ollama: float = field(default_factory=lambda: float(os.getenv("CAMPAIGN_RAG_TEMPERATURE", "0.4")))
    brand_styler_temperature: float = field(default_factory=lambda: float(os.getenv("CAMPAIGN_BRAND_STYLER_TEMPERATURE", "0.35")))
    section_temperature: float = field(default_factory=lambda: float(os.getenv("CAMPAIGN_SECTION_TEMPERATURE", "0.35")))
    max_generation_tokens: int = field(default_factory=lambda: int(os.getenv("CAMPAIGN_RAG_MAX_TOKENS", "4096")))

    style_top_k: int = field(default_factory=lambda: int(os.getenv("CAMPAIGN_STYLE_TOP_K", "2")))
    section_top_k: int = field(default_factory=lambda: int(os.getenv("CAMPAIGN_SECTION_TOP_K", "3")))
    component_top_k: int = field(default_factory=lambda: int(os.getenv("CAMPAIGN_COMPONENT_TOP_K", "2")))

    prompt_log_max_chunk_lines: int = field(default_factory=lambda: int(os.getenv("CAMPAIGN_PROMPT_LOG_MAX_CHUNK_LINES", "8")))


campaign_rag_config = CampaignRAGConfig()
