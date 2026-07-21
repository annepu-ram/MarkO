# Campaign & Routes Refactor — Technical Implementation Plan

> **Status:** Planned — not yet implemented.
> **Goal:** Rearrange the codebase into a human-readable structure: deduplicate LLM infrastructure, reorganize `campaign/` by pipeline stage, extract business logic out of the fat route files into a service layer, and bring the docs back in sync with the code. Behavior-preserving throughout — no functional changes.

---

## 1. Current State (measured, July 2026)

### 1.1 Where the code lives

| Area | Size | Notes |
|---|---|---|
| `campaign/` | ~4,255 lines / 23 modules | Largest: `content_registry.py` (660), `compiler.py` (644), `section_rag.py` (327) |
| `routes/brand.py` | 1,615 lines | 29 routes + ~60 private helpers (serializers, validators, YAML compile, previews) |
| `routes/chat.py` | 1,289 lines | Chat orchestration + image handling + business logic inline |
| `models.py` | 1,081 lines | All SQLAlchemy models in one file |
| `routes/site.py` | 944 lines | Site/page CRUD, publish, versions |
| `routes/campaign.py` | 900 lines | 15 routes; `generate_page` handler alone is ~120 lines of pipeline orchestration |

### 1.2 Problems

**P1 — Duplicated LLM infrastructure.** `campaign/model_backend.py` (`CampaignModelBackend`) reimplements `rag/agent/model_backend.py` (`ModelBackend`) with the same four providers (ollama/openai/anthropic/groq) and near-identical structure; the campaign copy adds per-call `model_override`/`temperature_override`. Every provider fix currently must be made twice. `campaign/prompt_loader.py` and `campaign/rag_logger.py` similarly parallel RAG machinery. (`campaign/rag_config.py` is deliberately separate — its docstring documents a different contract — and should stay a separate config *object*, but not justify a separate backend *implementation*.)

**P2 — `campaign/` module names don't reveal the pipeline.** `compiler.py`, `page_compiler.py`, `section_mapper.py`, `section_builders.py`, `content_to_section.py`, `section_rag.py` — run order and entry points are not discoverable without reading all six. Pure ontology data (`content_registry.py`, `vocabulary.py`, `section_types.py`, `section_purposes.yaml`) is mixed in with pipeline logic and LLM plumbing.

**P3 — Fat routes.** Route files hold serialization, validation, YAML compilation, and orchestration inline. `routes/brand.py` uses ~10 *deferred inline imports* of `campaign.*` inside function bodies (e.g. `brand.py:76,883,928,970,1308,1506`) — a symptom of circular-import pressure between routes and campaign.

**P4 — Docs describe a repo that no longer exists.** `CLAUDE.md` has no mention of `campaign/`, `routes/brand.py`, `routes/campaign.py`, `routes/product.py`, `routes/published.py`, `cms_options.py`, `brand_site_shell.py`, or `site_composer.py`.

### 1.3 External consumers of `campaign/` (import inventory)

Top-of-file imports (module → what it imports):

- `models.py:5` → `campaign.content_type_catalog.content_type_keys`
- `app.py:211` → `campaign.content_type_catalog.primary_slot_key` (inline)
- `routes/chat.py:15-16` → `content_type_catalog` (3 fns), `section_types`
- `routes/brand.py:18-26` → `content_type_catalog`, `offer_sync`, `section_types` (+10 inline imports: `section_rag`, `content_to_section`, `theme`, `section_builders`, `content_preview`)
- `routes/campaign.py` → inline: `offer_sync:414`, `compiler:559,586`, `theme:872`
- Tests: 12 `tests/test_campaign_*.py` files + `test_sections.py`, `test_content_preview.py`, `test_brand.py`

Internal dependency direction (already mostly clean):
`content_registry` ← `vocabulary` ← (`content`, `content_refs`, `validators`, `section_mapper`) and `content_registry` ← `content_type_catalog` ← (`offer_sync`); `section_builders` ← (`content_preview`, `page_compiler`); `section_rag` ← `content_to_section`.

---

## 2. Target Architecture

```
ssr_python/
├── campaign/
│   ├── __init__.py            # package docstring with pipeline diagram + public API re-exports
│   ├── ontology/              # THE DATA — frozen vocabulary, no LLM calls, no DB
│   │   ├── content_registry.py
│   │   ├── vocabulary.py
│   │   ├── content_type_catalog.py
│   │   ├── section_types.py
│   │   ├── section_purposes.yaml
│   │   └── schema.py
│   ├── content/               # content-item domain logic (DB-adjacent)
│   │   ├── content.py
│   │   ├── content_refs.py
│   │   ├── content_preview.py
│   │   └── offer_sync.py
│   ├── generation/            # THE PIPELINE, files named in run order
│   │   ├── recipes.py
│   │   ├── section_mapper.py
│   │   ├── section_builders.py
│   │   ├── section_rag.py
│   │   ├── content_to_section.py
│   │   ├── compiler.py
│   │   ├── page_compiler.py
│   │   ├── theme.py
│   │   └── validators.py
│   ├── prompts/               # unchanged (j2 templates)
│   ├── rag_config.py          # stays: deliberate separate config contract
│   ├── prompt_loader.py       # stays (thin, campaign-prompt-specific)
│   └── rag_logger.py          # stays (thin, campaign-log-specific)
├── services/                  # NEW — business logic extracted from routes
│   ├── brand_service.py
│   ├── brand_serializers.py
│   ├── content_service.py
│   └── campaign_page_service.py
└── rag/agent/model_backend.py # single canonical ModelBackend (P1)
```

**Import direction rule (enforced going forward):**
`ontology` ← `content` ← `generation` ← `services` ← `routes`. Never the reverse. `ontology/` may not import from `extensions`, `models`, or anything with side effects.

---

## 3. Guiding Rules (apply to every phase)

1. **One move per commit.** Never rename + move + edit in the same commit.
2. **`git mv` for every relocation** so file history survives `git log --follow`.
3. **Tests green at every commit**: `cd ssr_python && python -m pytest tests/ -v`.
4. **Shim, migrate, delete**: when moving a module, leave a re-export at the old path first, migrate importers in a follow-up commit, delete the shim last.
5. **Grep before every move**: `grep -rn "from campaign.X\|import campaign.X" --include="*.py" .` — update the full list, including *inline* imports inside function bodies (routes/brand.py has many).
6. Behavior-preserving only. Any bug found during the refactor gets a TODO + separate ticket, not an inline fix.

---

## 4. Phase 0 — Baseline & Tripwires (½ day)

1. Run the full suite; record pass count as the baseline.
2. Add coarse endpoint smoke tests (only where not already covered) for the surfaces Phases 2–3 will touch:
   - `POST /api/campaigns/<id>/compile`
   - `POST /api/campaigns/<id>/generate-page` (mock `ModelBackend`)
   - `GET  /api/campaigns/<id>/preview`
   - `POST /api/brands/<id>/site` + `GET /api/brands/<id>/site/preview`
   - Content item CRUD happy path (`routes/brand.py` content endpoints)
3. Commit: `test: add refactor tripwire smoke tests`.

**Exit criteria:** suite green; smoke tests cover every endpoint whose implementation will move.

## 5. Phase 1 — Unify the LLM Backend (1 day)

Canonical implementation: `rag/agent/model_backend.py`.

1. Extend `rag.agent.model_backend.ModelBackend.generate()` with the two capabilities the campaign copy added: per-call `model_override: str = ""` and `temperature_override: float | None = None`, threading them into all four provider methods (`_ollama/_openai/_anthropic/_groq`). Verify existing RAG callers (`builder_agent`, `planner_agent`, `section_rag` equivalents) are unaffected (new params are keyword-only with defaults).
2. Make `ModelBackend` accept its config at construction (`ModelBackend(config=rag_config)`), so `campaign/section_rag.py` can instantiate `ModelBackend(config=campaign_rag_config)`. The two config dataclasses (`RAGConfig`, `CampaignRAGConfig`) both already expose the needed fields (`model_backend`, `model_name`, `temperature_ollama`, `max_generation_tokens`).
3. Update `campaign/section_rag.py:8` to import the canonical backend.
4. Convert `campaign/model_backend.py` into a one-line deprecation shim (`CampaignModelBackend = ModelBackend`), then delete it once `section_rag` + tests are migrated.
5. Keep `campaign/rag_config.py`, `prompt_loader.py`, `rag_logger.py` as-is (thin, genuinely campaign-specific). Optional later cleanup: fold shared log-formatting helpers into one module.

**Commits:** (a) extend canonical backend + tests, (b) switch campaign to it, (c) delete duplicate.
**Exit criteria:** `campaign/model_backend.py` gone; suite green; ~120 duplicated lines removed.

## 6. Phase 2 — Reorganize `campaign/` by Pipeline Stage (1–2 days)

### Step 2.1 — Create subpackages and move files (one commit per subpackage)

| New location | Moved modules (git mv) |
|---|---|
| `campaign/ontology/` | `content_registry.py`, `vocabulary.py`, `content_type_catalog.py`, `section_types.py`, `section_purposes.yaml`, `schema.py` |
| `campaign/content/` | `content.py`, `content_refs.py`, `content_preview.py`, `offer_sync.py` |
| `campaign/generation/` | `recipes.py`, `section_mapper.py`, `section_builders.py`, `section_rag.py`, `content_to_section.py`, `compiler.py`, `page_compiler.py`, `theme.py`, `validators.py` |

Note: `section_purposes.yaml` is loaded by path — search for `section_purposes` to update the loader's `Path(...)` reference when it moves.

### Step 2.2 — Compatibility shims

In `campaign/__init__.py`, re-export old names so `from campaign.compiler import ...` etc. keep working during migration — via lightweight module aliases:

```python
# campaign/__init__.py (transitional; delete in Step 2.4)
import sys
from campaign.generation import compiler as _compiler
sys.modules['campaign.compiler'] = _compiler
# ... repeat per moved module
```

### Step 2.3 — Migrate importers (one commit per consumer file)

Update, in order (leaf-most first): internal `campaign/*` cross-imports → `tests/test_campaign_*.py` (12 files), `test_sections.py`, `test_content_preview.py`, `test_brand.py` → `models.py:5`, `app.py:211` → `routes/chat.py:15-16` → `routes/brand.py` (top-of-file *and* all inline imports at lines ~76, 883, 928, 970, 1308, 1506) → `routes/campaign.py` (inline at 414, 559, 586, 872).

### Step 2.4 — Delete shims, add the map

1. Remove the `sys.modules` aliases; run suite.
2. Write the `campaign/__init__.py` package docstring: ASCII pipeline diagram —
   `Campaign(DB) → compiler.compile_to_business_context() → generation/section pipeline (recipes → section_mapper → section_builders / section_rag) → page_compiler → site YAML`
   plus one line per subpackage stating its role and the import-direction rule (§2).
3. Each moved module keeps its name (renames are out of scope for this pass — naming changes multiply diff noise; revisit only `compiler.py` → consider `business_context.py` in a later, standalone commit).

**Exit criteria:** no module left at `campaign/` top level except `__init__.py`, `rag_config.py`, `prompt_loader.py`, `rag_logger.py`, `prompts/`; zero grep hits for old import paths; suite green.

## 7. Phase 3 — Extract Service Layer from Routes (3–5 days, one blueprint at a time)

Routes become: parse/authorize → call service → serialize → respond. Target ≤ ~300 lines per route file.

### 3a. `routes/brand.py` (worst first)

1. **`services/brand_serializers.py`** ← `_serialize_brand`, `_serialize_content_item`, `_serialize_content_folder`, `_serialize_section_item`, `_content_ref_preview` (pure functions, zero risk — move first).
2. **`services/brand_service.py`** ← brand CRUD/business helpers: `_slugify`, `_unique_brand_slug`, `_refresh_brand_campaign_assets`, `_apply_brand_fields`, `_ensure_single_default`, `_suggested_brand_strategy_from_model`, `_clean_social_links`, normalization helpers.
3. **`services/content_service.py`** ← content-item logic: `_apply_content_fields`, `_apply_section_fields`, validation helpers (`_validate_slots`, `_validate_component_list_yaml`, `_validate_section_body_yaml`, `_validate_content_scope`, …), section compile/preview helpers (`_compile_section_yaml*`, `_build_section_*_preview_structure`, `_smoke_render_section_body_yaml`, `_resolve_section_brand`, `_section_site_shell_config`).
4. Converting the service modules to top-of-file imports of `campaign.*` eliminates brand.py's inline-import workarounds; if a true cycle appears, it marks a real layering violation to fix by moving the offending logic down into `campaign/`, not by re-inlining.
5. One commit per extracted module; route file shrinks incrementally.

### 3b. `routes/campaign.py`

1. **`services/campaign_page_service.py`** ← body of `generate_page` (~574–694): compile business context, drive the RAG pipeline, persist results. Also home for `compile_campaign` orchestration.
2. Serializers (`_serialize_brief/_offer/_message/_campaign_*`) → `services/brand_serializers.py` or a sibling `campaign_serializers.py`.
3. CRUD field-apply helpers (`_apply_brief_fields`, `_sync_campaign_products`, validators) → the service module.

### 3c. `routes/chat.py` (optional in this pass; largest blast radius)

Extract the request-orchestration block (image query + `selected_images` build + LLM dispatch) into `services/chat_service.py`. Defer if time-boxed — 3a/3b deliver most of the readability win.

**Exit criteria per blueprint:** route file contains only route handlers + request parsing; all smoke tests from Phase 0 green.

## 8. Phase 4 — Documentation & Guardrails (½ day)

1. Update `CLAUDE.md`: directory tree (add `campaign/` subpackages, `services/`, missing routes/modules), pipeline description, and the import-direction rule.
2. Update `docs/ARCHITECTURE.md` and `docs/API_ROUTES_DATA_FLOW.md` for the new layout.
3. Add a lightweight import-direction test (`tests/test_architecture.py`): assert `campaign.ontology` modules import nothing from `campaign.content`, `campaign.generation`, `models`, `extensions`, or `routes` (walk `ast.parse` over the files — no new dependency needed).

---

## 9. Verification

- **Every commit:** `cd ssr_python && python -m pytest tests/ -v` — count matches Phase 0 baseline (plus new tests).
- **After Phase 2:** `grep -rn "from campaign\.\(compiler\|content\|vocabulary\|section_types\|content_registry\|content_type_catalog\|offer_sync\|section_rag\|theme\|section_builders\|content_preview\|content_to_section\|recipes\|section_mapper\|page_compiler\|validators\|schema\|content_refs\)" --include="*.py" | grep -v "campaign/ontology\|campaign/content\|campaign/generation"` returns nothing.
- **After Phase 3:** manual end-to-end: start the app, create a brand → campaign → compile → generate-page → preview in the UI; export a site.
- **App boots:** `python app.py` starts clean with no import errors (catches circulars pytest may mask).

## 10. Rollback & Sequencing

- Phases are strictly ordered (1 before 2 — don't move code about to be deleted; 2 before 3 — extracted route logic needs its proper home).
- Each phase lands as its own PR; each commit is independently revertable because moves and edits are never mixed.
- If a phase stalls mid-way, the shim layer (Phase 2) / partially-extracted services (Phase 3) are safe to ship — old paths keep working.

## 11. Out of Scope

- Splitting `models.py` (worthwhile, but DB-migration-adjacent; separate plan).
- Renaming modules (`compiler.py` etc.) — follow-up commits after the structure settles.
- Any behavior change, bug fix, or performance work.
- Frontend/static JS reorganization.
