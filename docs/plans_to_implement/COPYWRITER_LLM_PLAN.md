# MarkO Copywriter LLM — Implementation Plan

> **Status:** Planned — not yet implemented.
> **Origin:** Adapted from the "WordsyAI: Fine-Tuned Marketing Copywriting AI" technical plan, mapped onto MarkO's actual section vocabulary, content ontology, and business outlines.

## Context

Build a fine-tuned marketing-copywriter LLM for MarkO/Swift Sites. The model takes a structured business brief and emits schema-valid JSON copy for the **section types MarkO actually renders**, so generated content plugs straight into the existing RAG page-building pipeline. Training data is generated from the **96 business outlines** already in the repo (`website_example_outlines/`: 16 events, 52 products, 28 services), not from web scraping — legally clean and immediately available.

Key adaptation vs. the original WordsyAI plan: **do not invent a generic 8-type taxonomy** — MarkO already has a canonical copy ontology to derive it from:

- **Section vocabulary (~33 types)**: `ssr_python/rag/agent/planner_agent.py` (`_SECTION_COMPONENTS`) and `ssr_python/rag/indexing/metadata.py` (`FOLDER_TO_SECTION_TYPE`): hero, navigation, about, features, services, menu, products, pricing, testimonials, stats, gallery, team, faq, cta, form_cta, contact, order_form, reservation, countdown, how_it_works, schedule, delivery_areas, trusted_by, achievements, footer, banner, newsletter, blog, dashboard, ticker, social_links, divider.
- **Copy slot primitives**: `ssr_python/campaign/content_registry.py` — headline, paragraph, cta_label, quote, question/answer, stat, proof — with per-slot `max_length` already defined for some.
- **Section→content-type mapping**: `ssr_python/campaign/section_types.py` and `ssr_python/campaign/section_purposes.yaml`.
- **LLM backend abstraction already supports a fine-tuned model**: `ssr_python/rag/agent/model_backend.py` (ollama/openai/anthropic/groq) — an Ollama- or vLLM-(OpenAI-compatible)-served fine-tune plugs in via env vars (`RAG_MODEL_BACKEND`, `RAG_MODEL_NAME` in `rag/config.py`).
- No fine-tuning/training code exists in the repo today.

Baseline decisions: full code path (taxonomy → dataset pipeline → training configs → serving hook); synthetic data from outlines with a teacher LLM; base model Qwen3-8B + LoRA SFT + DPO. Training itself runs off-repo on a rented GPU.

## Deliverables (new package `ssr_python/copywriter/`)

### 1. `copywriter/taxonomy.py` — frozen `taxonomy_v1`
- Pydantic models, one per **copy-bearing section type** (~24 of the 33 — skip copy-free ones: gallery, divider, social_links, dashboard, ticker-images-only; navigation/footer get link-label schemas).
- Field types reuse the campaign primitives with char limits (e.g. `headline ≤ 60`, `paragraph ≤ 160`, `button_label ≤ 25`, `eyebrow ≤ 20`, `badge ≤ 15`; repeated items as `list[Item]` with min/max counts — e.g. features: 3–6 items of `{icon_hint, headline ≤ 30, paragraph ≤ 100}`).
- `MODEL_FOR: dict[str, type[BaseModel]]` + `CopyBrief` input schema (`section_type`, `industry` (enum derived from outline categories + `metadata.py` INDUSTRY_PATTERNS), `business_name`, `business_context`, `brand_voice` (2–3 from a 12-value enum), `audience`, `goal`, `awareness_stage`, `constraints`).
- Single source of truth imported by validator, dataset generator, and serving.

### 2. `copywriter/briefs.py` — outline → briefs
- Parse the 96 markdown outlines (`website_example_outlines/{events,products,services}/*.md`). Each file has variants (A/B/C) whose numbered section lists name MarkO components + copy hints (e.g. `services/01_healthcare_clinic.md`).
- Emit `CopyBrief` rows: one per (business × variant × section), mapping outline section labels to canonical section types via `metadata.py` `SECTION_TO_OUTLINE_LABELS` / `SECTION_TYPE_ALIASES` (import, don't duplicate).
- Expected yield: roughly 96 businesses × ~2.5 variants × ~10 sections ≈ 2,400 base briefs; augmented with brand_voice/goal/awareness permutations → 5k–8k briefs.

### 3. `copywriter/generate_dataset.py` — teacher generation
- Uses the existing `ModelBackend` (`rag/agent/model_backend.py`) with the `anthropic` or `openai` backend as teacher; constant system prompt, brief JSON as user turn, strict-JSON assistant turn.
- Writes `copywriter/data/sft_v1.jsonl` (chat format: system/user/assistant), every row carrying `meta: {brief_id, source_outline, judge_score}`.

### 4. `copywriter/judge.py` + `copywriter/validate_dataset.py`
- Judge: 3-call median on rubric (clarity, specificity, voice_match, goal_alignment, constraint_compliance), threshold ≥ 4.0 for the positive set; 3.0–3.9 retained as DPO `rejected` material.
- Validator (CI-gated, runs in pytest): input/output schema valid via `taxonomy.py`, enum membership, placeholder detection, near-dup cosine check (reuse `rag/embeddings/embed_service.py`), industry cap ≤ 12%, quality floor. A failing row fails the build.

### 5. `copywriter/mine_pairs.py` — DPO pairs
- Since data is synthetic: generate `rejected` counterparts by instructing the teacher to inject one named flaw per a `RejectionReason` enum (generic_claim, feature_not_benefit, too_long, weak_verb, buried_cta, jargon, voice_mismatch, no_urgency_when_needed), plus judge-score-gap pairs from multi-sample generations. Target ≥ 30% of briefs paired → `copywriter/data/dpo_v1.jsonl`.

### 6. `copywriter/training/` — training configs (run off-repo on GPU)
- `sft_axolotl.yaml`: Qwen3-8B, LoRA r=32, α=64, lr 2e-4, 3 epochs, all attn+FFN projections, bf16.
- `dpo_axolotl.yaml`: from SFT checkpoint, β=0.1, lr 5e-6, 1–2 epochs.
- `train_unsloth.py`: single-GPU fast-iteration script (SFT + optional DPO), plus `README.md` with GPU-rental runbook and eval procedure (held-out 10% stratified by section×industry + 2–3 zero-data industries as unseen slice; targets: schema validity ≥95% pre-constrained-decoding, DPO win-rate ≥60%).

### 7. Serving integration (minimal, additive)
- `copywriter/serve.py`: thin client that formats a `CopyBrief`, calls the model via Ollama or an OpenAI-compatible vLLM endpoint (with `guided_json` schema from `taxonomy.py` when vLLM), re-validates with Pydantic.
- Config: `COPYWRITER_MODEL_BACKEND` / `COPYWRITER_MODEL_NAME` env vars added to `rag/config.py` (falling back to existing RAG model when unset).
- Hook: in `rag/agent/builder_agent.py.build_section()`, when the copywriter model is configured, pre-generate section copy from the brief and pass it through the existing `business_content` parameter (already threads per-section real content into the builder prompt). No behavior change when unconfigured.

### 8. Tests
- `tests/test_copywriter_taxonomy.py` — schema round-trips, char limits, MODEL_FOR completeness vs. section vocabulary.
- `tests/test_copywriter_briefs.py` — outline parsing on 3 fixture outlines (one per category), canonical section mapping.
- `tests/test_copywriter_validator.py` — validator catches each error class; validator green on a small checked-in seed JSONL (~20 hand-checked rows).
- Dataset generation/judge tests use a mocked `ModelBackend` (no API calls in CI).

## Execution order
1. `taxonomy.py` + tests (foundation)
2. `briefs.py` + tests (outline parsing)
3. Validator + judge + tests
4. `generate_dataset.py` + `mine_pairs.py` (+ small seed dataset generated with mocked/dry-run mode checked in; full generation is an offline run requiring an API key)
5. Training configs + runbook
6. `serve.py` + builder_agent hook + config wiring

## Verification
- `cd ssr_python && python -m pytest tests/ -v` — full existing suite plus new copywriter tests stay green.
- `python -m copywriter.briefs --stats` prints brief counts per industry/section; spot-check against 2–3 outlines.
- `python -m copywriter.validate_dataset copywriter/data/seed_v1.jsonl` exits 0 on seed set, non-zero when a corrupted row is injected.
- Dry-run `generate_dataset.py --limit 3 --backend anthropic` end-to-end if an API key is available; otherwise mocked-run in tests.
- Serving hook: with `COPYWRITER_MODEL_*` unset, `/render` and chat pipeline behave identically (regression = existing tests).

## Out of scope (first pass)
- Actually running the GPU fine-tune (off-repo; runbook provided).
- Web scraping data sources from the original WordsyAI doc (Wayback/ad libraries) — possible v2 data augmentation.
- Multilingual copy, per-customer brand fine-tunes.
