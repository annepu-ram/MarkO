# RAG-Driven Brand-Aware Header/Footer via Semantic (Hybrid) Retrieval

## Context
A brand's site shell header (titlebar/nav) and footer are generated **deterministically** in pure Python
(`_header_components`/`_footer_components` in [brand_site_shell.py](../../ssr_python/brand_site_shell.py)):
hardcoded nav items, a static footer. No RAG, no brand/industry-aware styling, ignoring the indexed
navigation/footer template library.

The user wants:
1. **Header/footer become RAG-generated and brand-aware** — footer driven by social links + brand fields;
   header driven by brand name/tagline/industry/logo/CTA. RAG-only — surface errors, no deterministic fallback.
2. **Semantic search instead of keyword matching.** The campaign path uses BM25-only `KeywordSearch` and
   passes `industry`/`tone` as raw query text. Switching to embedding-based retrieval makes the brand↔template
   tone/industry vocabulary mismatch **moot** — embeddings capture meaning, so no normalization/filter layer
   is needed (decided: **semantic-only, no metadata filters**).

### Why no explicit metadata-alignment layer is needed
Template `tone` (4 values) vs `Brand.tone` (17) and free-text `Brand.industry` vs 22 canonical keys only
mattered for *keyword* filtering. With semantic retrieval, "authoritative" embeds near "formal/professional"
templates without a lookup table. So the previously-deferred metadata alignment is resolved **by adopting
semantic search**, not by building a normalizer.

### Key discovery: semantic + hybrid search already exist and are used by the main pipeline
- `rag/retrieval/vector_search.py` — `VectorSearch` (NumPy cosine over `*_embeddings.npz`).
- `rag/retrieval/hybrid.py` — `HybridSearch` = vector + BM25 fused by RRF, then MMR diversity. Used by `RAGAgent`/`BuilderAgent`/`PlannerAgent`.
- `rag/embeddings/embed_service.py` — Ollama `nomic-embed-text` (768-dim), sentence-transformers fallback.
- Vector indices already built for all tiers incl. `section` (272 chunks): `rag/data/section_embeddings.npz` — **no index rebuild needed**.
- Campaign path (`campaign/section_rag.py:14`) is **BM25-only** today.

### Critical API difference (must handle)
- `KeywordSearch.search()` → `list[(chunk, score)]`; campaign's `_keyword_chunks`
  (`section_rag.py:211-212`) unpacks tuples.
- `HybridSearch.search()` → `list[dict]` plain chunks (`hybrid.py:26,60,63`).
  The accessor must be adapted when swapping.

---

## Workstream A — Switch campaign retrieval to HybridSearch (semantic), hybrid-only
**Goal:** Replace BM25-only retrieval with semantic hybrid retrieval everywhere in the campaign path. No
metadata filters, no keyword fallback toggle (decided: **hybrid only**).

In `campaign/section_rag.py`:
- Replace `from rag.retrieval.keyword_search import KeywordSearch` with `from rag.retrieval.hybrid import HybridSearch`.
- Instantiate `HybridSearch()` in `generate_brand_section_style_prompt` (line 65) and `generate_section_yaml` (line 119).
- Replace `_keyword_chunks` with `_hybrid_chunks(results)` that returns the list as-is (hybrid already
  returns plain dicts). Update `_retrieve_style_context`, `_retrieve_section_examples`,
  `_retrieve_component_examples` (`section_rag.py:186-208`).
  Keep `_chunk_id` / `chunk.get("content")` — chunk shape is identical.
- Call sites stay `search.search(query, top_k=..., tier=...)` (no `metadata_filter`).

**Reuse:** `HybridSearch`/`VectorSearch`/`EmbedService` + prebuilt `*_embeddings.npz`.

## Workstream B — RAG header/footer generators

### B1. Generators in `campaign/section_rag.py`
Add `generate_header_yaml(brand, *, site_shell_config=None, org_id=None)` and `generate_footer_yaml(...)`,
modeled on `generate_section_yaml` (`section_rag.py:108-171`):
- Retrieve references with `HybridSearch.search(query, tier="section")` where `section_type` ⇒
  `"navigation"` / `"footer"`. Query text from brand industry/tone/name + "header"/"footer" (semantic — the
  embedding does the matching).
- Brand context: **header** = name/tagline/industry/logo_url/cta_style/default_style; **footer** =
  name/tagline/brand_promise/website_url + `brand.get_social_links()`.
- Style with the brand's saved `section_style_prompt` + `brand_to_theme(brand)`.
- Generate via `CampaignModelBackend().generate(...)`; validate/repair with existing
  `_extract_validate_and_repair_body_yaml` (`section_rag.py:215-227`).
- Return `(yaml_text, metadata)` with compiler tags `brand_header_rag.v1` / `brand_footer_rag.v1`.

### B2. Prompt pairs in `campaign/prompts/`
Four new `.j2` files: `brand_header_system/user`, `brand_footer_system/user`. Adapt
`section_builder_system.j2` but **invert** the no-header/footer rule:
- Header: "Output exactly one `titlebar` (body-only YAML list). Use brand identity for branding.title/logo;
  derive `navigation.links` from brand industry + standard pages. No `site`/`page`."
- Footer: "Output a footer `layout-row`/`layout-column`. One `link` per provided social link; include website
  link + tagline/promise. No `site`/`page`." Both use theme token aliases (`*color-primary`, etc.).

Extend `load_campaign_system` (`prompt_loader.py:28-33`) to inject the component reference for
`brand_header`/`brand_footer` (set-membership instead of the lone `section_builder` check) so titlebar/layout
component docs are available.

### B3. Wire into shell generation — `brand_site_shell.py`
In `ensure_brand_site` (`brand_site_shell.py:199-204`) on `created or regenerate`:
- Build `site_shell_config = {'source':'brand_site_shell','site_id':site.id,'theme':brand_to_site_theme(brand)}`.
- `header_yaml,_ = generate_header_yaml(...)` → `_upsert_shared_block(site,'header','Header',yaml.safe_load(header_yaml),0)`.
- `footer_yaml,footer_meta = generate_footer_yaml(...)` → `_upsert_shared_block(site,'footer',...)` **and**
  `_upsert_footer_section(brand, components=..., metadata=footer_meta)` — refactor
  `_upsert_footer_section` (`brand_site_shell.py:234-260`) to accept generated components instead
  of rebuilding from `_footer_components`.
- **RAG-only:** let generation errors propagate; remove `_header_components`/`_footer_components` (keep only if a test needs them).

### B4. Sequencing — `routes/brand.py`
Header/footer generators need `brand.section_style_prompt` to exist (same precondition as
`generate_section_yaml`). Re-order `_refresh_brand_campaign_assets` (`routes/brand.py:74-96`) to:
(a) ensure site row + theme/settings, (b) wording prompt, (c) section_style prompt saved, (d) **then**
header/footer generation + shared-block upsert.
Ensure shell endpoints surface generation failures cleanly (not a 500 stacktrace):
`create_or_refresh_brand_site` / `preview_brand_site` (`routes/brand.py:443-527`) and the create/update
rollback path (`routes/brand.py:390-394`).

---

## Files to modify
- `campaign/section_rag.py` — hybrid swap (`_hybrid_chunks`); `generate_header_yaml`/`generate_footer_yaml`.
- `campaign/prompt_loader.py` — component reference for new prompts.
- **new** `campaign/prompts/` — 4 `.j2` files.
- `brand_site_shell.py` — `ensure_brand_site`, `_upsert_footer_section`; drop deterministic builders.
- `routes/brand.py` — re-order `_refresh_brand_campaign_assets`; clean error surfacing.
- Tests: `tests/test_brand.py` — mock `CampaignModelBackend.generate` and `HybridSearch`; assert
  header/footer shared blocks + footer SectionItem stored with new compiler tags.

## Reuse (do not reinvent)
- `HybridSearch`/`VectorSearch`/`EmbedService` + prebuilt `*_embeddings.npz` (no rebuild).
- `_extract_validate_and_repair_body_yaml`, `brand_to_theme`, `_upsert_shared_block`, `brand_to_site_theme`.
- `load_campaign_system`/`render_campaign_user`; `CampaignModelBackend.generate`.
- `compose_page_yaml` render path (site_composer) — unchanged.

## Verification
1. **Tests** (model + hybrid mockable):
   `cd ssr_python && python -m pytest tests/test_brand.py tests/test_campaign_brand_wording.py -v`.
   - Hybrid swap: assert campaign retrieval helpers consume `HybridSearch.search` plain-dict results (no tuple unpacking).
   - Shell creation: mock `CampaignModelBackend.generate` → valid titlebar/footer YAML; assert header/footer
     SiteSharedBlock + footer SectionItem stored with `brand_header_rag.v1`/`brand_footer_rag.v1` metadata.
   - Failure path: generation raises → shell endpoint returns readable error, not a 500 stacktrace.
2. **Manual (real model + Ollama embeddings)** via `python app.py`: create a brand (name/tagline/industry +
   2-3 social links), POST `/api/brands/<id>/site`, GET `/api/brands/<id>/site/preview` → header reflects
   brand identity + industry-aware nav; footer renders one link per social link; styling matches brand theme.
   Regenerate (`{regenerate:true}`) → header/footer refresh, page body preserved.
3. **Semantic spot-check:** for a brand with an off-vocabulary tone (e.g. "authoritative"), confirm retrieved
   nav/footer templates are relevant — validating that semantic retrieval bridges the vocabulary gap that
   BM25 query text would have missed.
