# RAG System with LEANN + SLM — Implementation Plan

## Context

Current `llm_service.py` sends the full 78KB LLM_COMPONENT_GUIDE.md as system prompt on every chat request. This wastes context window, limits the SLM's reasoning capacity, and prevents scaling the knowledge base. A RAG system retrieves only relevant chunks per query, enabling a small model — local or cloud-hosted — to produce high-quality YAML with less context and greater accuracy.

**Complements FINETUNE_PLAN.md** — fine-tuning teaches the model YAML syntax; RAG provides runtime knowledge (templates, patterns, industry context).

---

## Architecture Overview

```
User Query ("Create a bakery hero section")
         |
    [1. Query Embedding]  ←  nomic-embed-text (Ollama)
         |
    [2. LEANN Vector Search]  ←  97% storage savings vs ChromaDB
         |
    [3. Hybrid Fusion]  ←  BM25 keyword + vector semantic results
         |
    [4. Reranking]  ←  Cross-encoder scores top-20 → top-5
         |
    [5. Context Assembly]  ←  Retrieved chunks + condensed system rules
         |
    [6. SLM Generation]  ←  Local (Ollama) or Cloud API (OpenAI, Claude, etc.)
         |
    [7. YAML Validation]  ←  Existing renderer.py pipeline
         |
    Response to Chat UI
```

---

## Directory Structure

```
ssr_python/rag/
├── config.py                    # RAG configuration (models, paths, chunk sizes)
├── requirements.txt             # LEANN, rank-bm25, sentence-transformers
├── embeddings/
│   ├── embed_service.py         # Embedding generation via Ollama
│   └── batch_embed.py           # Bulk embed all documents on startup/rebuild
├── indexing/
│   ├── chunker.py               # Smart document chunking (YAML-aware + markdown)
│   ├── metadata.py              # Extract component types, industry, tokens per chunk
│   └── index_builder.py         # Build LEANN index from chunks + embeddings
├── retrieval/
│   ├── vector_search.py         # LEANN nearest-neighbor search
│   ├── keyword_search.py        # BM25 sparse retrieval
│   ├── hybrid.py                # Reciprocal Rank Fusion (RRF) combiner
│   └── reranker.py              # Cross-encoder reranking (optional)
├── agent/
│   ├── rag_agent.py             # Orchestrator: query → retrieve → generate
│   ├── model_backend.py         # Unified interface: Ollama / OpenAI / Anthropic / Groq
│   ├── query_analyzer.py        # Intent classification + query decomposition
│   ├── prompt_builder.py        # Assemble retrieved context into SLM prompt
│   └── response_parser.py       # Extract ACTION + YAML (reuse from llm_service.py)
├── data/
│   ├── leann_index/             # Persisted LEANN graph index
│   ├── bm25_index/              # Persisted BM25 corpus
│   └── chunks.jsonl             # All chunks with metadata
└── scripts/
    ├── build_index.py           # One-time: chunk → embed → index all documents
    ├── rebuild_index.py         # Incremental rebuild when templates change
    └── evaluate_retrieval.py    # Test retrieval quality with sample queries
```

---

## Phase 1: Document Ingestion & Chunking

### 1.1 YAML-Aware Chunker (`chunker.py`)

YAML templates need semantic chunking, not naive text splitting:

| Document Type | Chunking Strategy | Avg Chunk Size |
|---|---|---|
| **YAML templates** | Per top-level component (hero section, card, footer) | 200-400 tokens |
| **Website outlines** | Per section heading (## Hero, ## Pricing) | 150-300 tokens |
| **LLM Component Guide** | Per component spec + per token category | 200-500 tokens |
| **Config YAML** | Per component type block | 100-300 tokens |

**YAML chunking rules:**
- Split at top-level `- name:` boundaries within `components:` arrays
- Preserve the `site > page` wrapper as chunk metadata (theme colors, fonts)
- Keep parent layout context (row/column containment) in chunk header
- Overlap: include parent component name + theme anchors in every chunk

**Estimated chunks: 400-600 total**

### 1.2 Metadata Extraction (`metadata.py`)

Each chunk gets tagged with:
```python
{
    "source_file": "example_templates/hero/02_split_screen.yaml",
    "doc_type": "template",          # template | outline | guide | config
    "component_types": ["layout-row", "layout-column", "heading", "button"],
    "industry": "saas",              # from filename or outline content
    "section_type": "hero",          # hero | pricing | footer | testimonial | etc
    "tokens_used": ["xxl", "bold", "md", "stretch"],
    "has_theme": true,
    "complexity": "medium"           # simple | medium | complex
}
```

Metadata enables **filtered retrieval** — "show me hero templates" retrieves only `section_type=hero` chunks.

---

## Phase 2: Embedding & LEANN Index

### 2.1 Embedding Model

**Primary: `nomic-embed-text`** via Ollama
- 768 dimensions, 8192 token context
- Surpasses OpenAI text-embedding-3-small on MTEB benchmarks
- Runs locally, zero cost

```bash
ollama pull nomic-embed-text
```

**Fallback: `all-MiniLM-L6-v2`** via sentence-transformers
- 384 dimensions, lightweight
- For machines that can't run nomic

### 2.2 LEANN Index (`index_builder.py`)

LEANN's key advantage: **97% storage savings** by recomputing embeddings on-the-fly instead of storing all vectors.

```python
# Pseudocode for LEANN index build
from leann import LEANNIndex

index = LEANNIndex(
    embedding_dim=768,
    metric="cosine",
    ef_construction=200,      # HNSW build parameter
    M=16,                     # HNSW connections per node
    pruning_ratio=0.02        # Keep top 2% hub nodes
)

for chunk in all_chunks:
    embedding = embed_service.embed(chunk.text)
    index.add(embedding, metadata=chunk.metadata)

index.save("data/leann_index/")
```

**Storage estimate:**
- Traditional (ChromaDB): ~600 chunks × 768 dims × 4 bytes = ~1.8MB vectors + metadata
- LEANN: ~54KB index (97% savings) + on-demand recomputation

### 2.3 BM25 Keyword Index (`keyword_search.py`)

Complements vector search for exact term matching (component names, token values):

```python
from rank_bm25 import BM25Okapi

corpus = [chunk.text for chunk in all_chunks]
bm25 = BM25Okapi([doc.split() for doc in corpus])
```

---

## Phase 3: Retrieval Pipeline

### 3.1 Hybrid Search (`hybrid.py`)

Combine vector (semantic) + BM25 (keyword) using Reciprocal Rank Fusion:

```
score(doc) = Σ 1/(k + rank_i(doc))   for each retrieval method i
```

Where `k=60` (standard RRF constant).

**Why hybrid?**
- Vector catches "make a landing page for a coffee shop" → bakery_template
- BM25 catches "layout-row with widthMode 50" → exact component patterns
- Together: >15% improvement over either alone

### 3.2 Metadata-Filtered Retrieval

Pre-filter based on query intent:
- "Create a pricing section" → filter `section_type=pricing`
- "Add a badge to the image" → filter `component_types contains badge`
- "Build a restaurant website" → filter `industry=restaurant`

### 3.3 Reranking (`reranker.py`)

Optional cross-encoder pass on top-20 results → top-5:

```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
# Lightweight, CPU-only, ~22MB
```

---

## Phase 4: Task-Specific Agent

### 4.1 Query Analyzer (`query_analyzer.py`)

Classifies user intent before retrieval:

| Intent | Action | Retrieval Strategy |
|---|---|---|
| `create_page` | Generate full page | Retrieve full-page templates + industry outline |
| `create_section` | Generate section | Retrieve matching section chunks |
| `modify_component` | Edit existing | Retrieve component spec + similar examples |
| `explain` | Answer question | Retrieve guide chunks + examples |
| `add_component` | Insert new child/sibling | Retrieve component defaults + usage patterns |

**Decomposition for complex queries:**
- "Create a SaaS landing page with hero, pricing, and testimonials"
- → Sub-queries: [hero patterns, pricing patterns, testimonial patterns]
- → Parallel retrieval → merged context

### 4.2 Prompt Builder (`prompt_builder.py`)

Assembles the final SLM prompt from retrieved context:

```
[System] You are SwiftSites, a YAML website generator.
         CRITICAL RULES: (condensed ~200 words from LLM guide)

[Retrieved Context]
--- Example: bakery hero section ---
<yaml chunk>
--- Example: split-screen hero ---
<yaml chunk>
--- Component spec: layout-row ---
<yaml chunk>

[User] Create a hero section for a coffee shop with...
[Current YAML] (if modifying existing)
[Selected Component] (if editing specific component)
```

**Context budget:** 2048 tokens for retrieved chunks (leaves room for generation in 4096 context window).

### 4.3 RAG Agent Orchestrator (`rag_agent.py`)

```python
class RAGAgent:
    def chat(self, message, current_yaml=None, selected_component=None):
        # 1. Analyze query intent
        intent = self.query_analyzer.classify(message)

        # 2. Build retrieval query (may decompose)
        queries = self.query_analyzer.decompose(message, intent)

        # 3. Retrieve relevant chunks
        chunks = []
        for q in queries:
            results = self.hybrid_search(q, top_k=10)
            reranked = self.reranker.rerank(q, results, top_k=3)
            chunks.extend(reranked)

        # 4. Deduplicate and budget-fit
        chunks = self.dedupe_and_trim(chunks, max_tokens=2048)

        # 5. Build prompt
        prompt = self.prompt_builder.build(
            intent=intent,
            chunks=chunks,
            current_yaml=current_yaml,
            selected_component=selected_component,
            message=message
        )

        # 6. Generate with SLM
        response = self.slm.generate(prompt)

        # 7. Parse and validate
        return self.response_parser.parse(response)
```

---

## Phase 5: SLM Selection (Local or Cloud)

The generation model is **pluggable** — RAG retrieval is model-agnostic. The same retrieved context can be fed to a local SLM or a cloud API model.

### 5.1 Local Models (via Ollama) — Zero Cost, Full Privacy

| Model | Params | VRAM | Strengths | Use Case |
|---|---|---|---|---|
| **Phi-4-mini** | 3.8B | 4GB | Reasoning, code, instruction following | Default local choice |
| **Qwen2.5-Coder-7B** | 7B | 6GB | Code understanding, structured output | If hardware allows |
| **Gemma-2-2B** | 2B | 2GB | Lightweight, fast | Low-resource fallback |

```bash
ollama pull phi4-mini
# or after fine-tuning:
ollama create swiftsites-phi4-mini -f Modelfile
```

### 5.2 Cloud API Models — Higher Quality, Pay-per-Use

| Provider | Model | Strengths | Cost Tier |
|---|---|---|---|
| **Anthropic** | Claude Sonnet 4.6 | Excellent structured output, reasoning | Medium |
| **OpenAI** | GPT-4o-mini | Fast, cheap, good code generation | Low |
| **Google** | Gemini 2.0 Flash | Large context, fast | Low |
| **Groq** | Llama 3.3 70B | Ultra-fast inference, free tier | Free/Low |
| **Together AI** | Mixtral, Llama variants | Competitive pricing, many models | Low |

### 5.3 Unified Model Interface (`rag/agent/model_backend.py`)

Abstract the generation backend so switching between local and cloud is a config change:

```python
class ModelBackend:
    """Unified interface for local Ollama and cloud API models."""

    def generate(self, prompt: str, system: str = None) -> str:
        if self.backend_type == "ollama":
            return self._ollama_generate(prompt, system)
        elif self.backend_type == "openai":
            return self._openai_generate(prompt, system)
        elif self.backend_type == "anthropic":
            return self._anthropic_generate(prompt, system)
        elif self.backend_type == "groq":
            return self._groq_generate(prompt, system)
```

**Strategy:** Default to local Phi-4-mini for privacy and zero cost. Allow users to configure a cloud model for higher quality when needed. If fine-tuned (per FINETUNE_PLAN.md), use `swiftsites-phi4-mini` locally for best cost/quality ratio.

---

## Phase 6: Integration with Existing App

### 6.1 Modify `llm_service.py`

Add RAG as the primary path, keep direct LLM as fallback:

```python
class LLMService:
    def __init__(self):
        self.rag_agent = RAGAgent()        # New
        self.use_rag = True                 # Toggle

    def chat(self, message, current_yaml, selected_component):
        if self.use_rag:
            return self.rag_agent.chat(message, current_yaml, selected_component)
        else:
            return self._legacy_chat(...)   # Current implementation
```

### 6.2 New API Endpoints

```python
# routes/rag.py
POST /api/rag/rebuild-index    # Trigger index rebuild
GET  /api/rag/status           # Index stats (chunk count, last built)
POST /api/rag/search           # Debug: test retrieval without generation
```

### 6.3 Environment Variables

```env
# RAG Configuration
RAG_ENABLED=true
RAG_EMBEDDING_MODEL=nomic-embed-text
RAG_TOP_K=5
RAG_USE_RERANKER=true
RAG_CHUNK_MAX_TOKENS=400
RAG_CONTEXT_BUDGET=2048

# Generation Model — choose one backend
RAG_MODEL_BACKEND=ollama           # ollama | openai | anthropic | groq
RAG_MODEL_NAME=phi4-mini           # Model name for the chosen backend

# Cloud API keys (only needed if using a cloud backend)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GROQ_API_KEY=gsk_...
```

---

## Phase 7: Additional Ideas

### 7.1 Self-Improving RAG Loop

When a user applies generated YAML (clicks "Apply Changes"), save the query-YAML pair as a validated example. Periodically re-index these to improve future retrieval — the system learns from actual usage.

### 7.2 Component-Specific Retrieval Chains

For modification tasks, build a specialized chain:
1. Identify the component type being modified
2. Retrieve: component schema → component defaults → 3 similar examples
3. Generate modification with full context of what's valid

### 7.3 Multi-Turn Conversation Memory

Store last 3-5 turns in a sliding window. On each turn:
- Embed the conversation so far
- Retrieve chunks relevant to the *evolving* conversation, not just the latest message
- Enables "now make it dark mode" after "create a hero section"

### 7.4 Template Recommendation Engine

Before generating, suggest existing templates that match the query:
- "Want to create a bakery site? Here are 3 similar templates you can start from"
- Reduces generation load — modify an existing template vs. generate from scratch

### 7.5 Validation-Guided Regeneration

If YAML validation fails after generation:
1. Identify the specific error (invalid token, wrong nesting, missing field)
2. Retrieve the correct pattern from the knowledge base
3. Re-prompt the SLM with the error + correct example
4. Up to 2 retries before returning error

### 7.6 Offline Index Pre-warming

Build and persist the LEANN index at app startup. If index files exist and templates haven't changed (check file hashes), skip rebuild. Otherwise, rebuild in background thread.

### 7.7 Query Caching

Cache embedding + retrieval results for identical queries (LRU cache, 100 entries). Most users ask similar things — "create a hero", "add a button", "make a pricing page".

### 7.8 Agentic Retrieval for Complex Pages

For full-page generation, decompose into an agent workflow:
1. **Planner step:** SLM generates a section outline (hero, features, pricing, footer)
2. **Per-section retrieval:** Each section gets its own RAG retrieval
3. **Assembly step:** SLM combines sections into a coherent page with shared theme

---

## Dependencies

```txt
# ssr_python/rag/requirements.txt
leann>=0.1.0                     # LEANN vector index
rank-bm25>=0.2.2                 # BM25 keyword search
sentence-transformers>=3.0.0     # Cross-encoder reranking (optional)
tiktoken>=0.7.0                  # Token counting for chunk budgeting

# Cloud API backends (install only what you need)
# openai>=1.0.0                  # For OpenAI / GPT models
# anthropic>=0.40.0              # For Claude models
# groq>=0.11.0                   # For Groq-hosted models
```

Ollama models (pulled separately, only if using local backend):
- `nomic-embed-text` — embedding model
- `phi4-mini` — generation SLM (or fine-tuned variant)

---

## Execution Order

```bash
# 1. Install dependencies
cd ssr_python
pip install leann rank-bm25 sentence-transformers tiktoken

# 2a. LOCAL backend: Pull Ollama models
ollama pull nomic-embed-text
ollama pull phi4-mini

# 2b. CLOUD backend: Install API SDK + set key
# pip install openai          # or anthropic, groq
# export OPENAI_API_KEY=sk-...

# 3. Build index (one-time, ~2-5 minutes)
python -m rag.scripts.build_index

# 4. Test retrieval quality
python -m rag.scripts.evaluate_retrieval

# 5. Enable RAG in .env (choose backend)
# echo "RAG_ENABLED=true" >> .env
# echo "RAG_MODEL_BACKEND=ollama" >> .env      # or openai, anthropic, groq
# echo "RAG_MODEL_NAME=phi4-mini" >> .env       # or gpt-4o-mini, claude-sonnet-4-6, etc.

# 6. Restart Flask app
python app.py
```

---

## Verification

1. **Index quality:** `evaluate_retrieval.py` with 20 sample queries — target >80% relevant results in top-5
2. **Retrieval speed:** <200ms per query (LEANN is optimized for this)
3. **Generation quality:** Compare RAG-assisted vs direct prompt on 10 test queries — RAG should produce more accurate YAML with fewer token errors
4. **End-to-end:** Chat UI → RAG agent → valid YAML → renders in preview
5. **Storage:** LEANN index <100KB vs ~2MB for equivalent ChromaDB
6. **Fallback:** Disable RAG (`RAG_ENABLED=false`) — app falls back to legacy direct prompt

---

## Comparison: RAG vs Current Approach vs Fine-Tuning

| Metric | Current (Direct Prompt) | RAG + Local SLM | RAG + Cloud API | Fine-Tuned + RAG |
|---|---|---|---|---|
| Context per request | 78KB system prompt | ~2KB retrieved chunks | ~2KB retrieved chunks | ~0.5KB system + 2KB chunks |
| Model size | Any (llama3 70B) | 3.8B (Phi-4-mini) | Cloud-hosted (any size) | 3.8B (fine-tuned Phi-4) |
| Knowledge updates | Edit guide → restart | Re-index → instant | Re-index → instant | Retrain → hours |
| API cost | $0 (local Ollama) | $0 (local) | Pay-per-use (~$0.001/req) | $0 (local) |
| Accuracy | Medium (context overflow) | High (focused context) | Highest (large model + focus) | Highest (learned + focused) |
| Privacy | Full (local) | Full (local) | Data sent to cloud | Full (local) |
| Hardware needed | GPU recommended | 4-6GB VRAM | None (API calls) | 4-6GB VRAM |
| Setup effort | Low | Medium | Low (just API key) | High |
