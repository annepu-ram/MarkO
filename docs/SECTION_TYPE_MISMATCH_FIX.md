# Fix Section Type Mismatches Between Templates and Outlines

**Status:** Completed
**Date:** March 2026

## Problem

The RAG system matches website outline sections to example templates using `section_type` metadata. When the planner generates sections (e.g., type `"hero"`, `"navigation"`), the builder filters templates by `metadata_filter={"section_type": section_type}`. Several mismatches prevented correct template retrieval:

1. **77% of templates (147/192) lacked `# Section type:` headers** — forced unreliable regex fallback
2. **`query_analyzer.py` used `"header"` but `metadata.py` used `"navigation"`** — queries for nav sections returned nothing
3. **Missing section types** in `SECTION_PATTERNS` (`schedule`, `social_links`, `banner`)
4. **`social links` (with space)** in templates didn't normalize to a valid key
5. **`banner_announcement/` templates** were tagged as `cta` instead of `banner`

---

## Changes Made

### Phase 1: Fix `metadata.py` dictionaries

**File:** `ssr_python/rag/indexing/metadata.py`

- Added missing section types to `SECTION_PATTERNS`:
  - `schedule`, `social_links`, `banner`
- Added missing entries to `SECTION_TO_OUTLINE_LABELS`:
  - `social_links`, `banner`
- Added space→underscore normalization in `extract_metadata()` for `header_section_type` values

### Phase 2: Fix `query_analyzer.py` key mismatch

**File:** `ssr_python/rag/agent/query_analyzer.py`

- Renamed `"header"` → `"navigation"` in `SECTION_KEYWORDS` (critical fix — was causing nav queries to never match template metadata)
- Added 6 missing section keywords: `schedule`, `social_links`, `banner`, `countdown`, `ticker`, `dashboard`

### Phase 3: Add full metadata headers to all legacy templates (147 files)

Added standardized 7-line metadata headers to all template YAML files that were missing them:

```yaml
# [Title]
# [Description]
# Base components: [comma-separated component names from YAML body]
# Section type: [section_type]
# Layout: [fullscreen | split_screen | grid | centered | stacked | carousel_slider | asymmetric | overlay]
# Visual style: [modern | dark_mode | glassmorphism | gradient | minimal | bold_typography | card_based | animated | retro | neubrutalism | claymorphism | aurora | monochrome]
# Perfect for: [comma-separated industries/use cases]
```

#### Directory → Section Type Mapping

| Directory | Files | Section Type | Notes |
|-----------|-------|-------------|-------|
| `hero/` | 27 | `hero` | |
| `navigation_footer/` | 10 | mixed | 01,02,06,07,08,09,10 → `navigation`; 03,04,05 → `footer` |
| `review_testimonial_cards/` | 10 | `testimonial` | |
| `pricing_plan_cards/` | 10 | `pricing` | |
| `product_cards/` | 10 | `product` | |
| `story_blog_cards/` | 10 | `blog` | |
| `portfolio_showcase_cards/` | 10 | mixed | 09 → `team`, 10 → `features`, rest → `gallery` |
| `dashboard_data_cards/` | 10 | `dashboard` | |
| `ticker/` | 11 | `ticker` | |
| `countdown/` | 3 | `countdown` | |
| `badge/` | 3 | `product` | |
| `rating/` | 3 | `product` | |
| `progress-bar/` | 3 | `stats` | |
| `icon/` | 3 | `features` | |
| `counter-up/` | 3 | `stats` | |
| `styles/` | 7 | `hero` | Styled hero variations |

### Phase 4: Normalize existing section types

- `social_links/` templates: Changed `social links` → `social_links` (3 files)
- `banner_announcement/` templates: Changed `cta` → `banner` (5 files)

### Phase 5: Exclude `tests/` from RAG indexing

**File:** `ssr_python/rag/indexing/index_builder.py`

Added `tests` to ignored directories in `_discover_files()` so test YAML files aren't indexed.

### Phase 6: Rebuild RAG index

Index rebuilt with 2874 chunks across 4 tiers:
- **section**: 103 chunks
- **component**: 313 chunks
- **guide**: 507 chunks
- **icon**: 1951 chunks

---

## Section Type Coverage (Post-Fix)

### Section Tier (103 chunks)
| Section Type | Chunks |
|---|---|
| hero | 16 |
| banner | 10 |
| contact | 10 |
| cta | 10 |
| faq | 10 |
| features | 10 |
| gallery | 10 |
| team | 9 |
| schedule | 6 |
| social_links | 6 |
| navigation | 6 |

### Component Tier (313 chunks)
| Section Type | Chunks |
|---|---|
| hero | 57 |
| gallery | 43 |
| navigation | 32 |
| features | 23 |
| product | 22 |
| team | 21 |
| ticker | 14 |
| pricing | 13 |
| dashboard | 12 |
| stats | 11 |
| testimonial | 10 |
| blog | 10 |
| footer | 9 |
| contact | 6 |
| countdown | 6 |
| schedule | 6 |
| banner | 5 |
| cta | 5 |
| faq | 5 |
| social_links | 3 |

---

## Verification

- All 1026 tests pass (`python -m pytest tests/ -v`)
- RAG index builds without errors
- All 177 non-test template files have `# Section type:` headers (100% coverage)
- No `other` section types in the built index — all templates properly classified

---

## Files Modified

### Code (4 files)
- `ssr_python/rag/indexing/metadata.py` — SECTION_PATTERNS, SECTION_TO_OUTLINE_LABELS, normalize spaces
- `ssr_python/rag/agent/query_analyzer.py` — SECTION_KEYWORDS `header`→`navigation` fix + new keywords
- `ssr_python/rag/indexing/index_builder.py` — Exclude `tests/` from file discovery
- `ssr_python/rag/indexing/chunker.py` — Reference only (parses `# Section type:` headers)

### Templates (177 files)
- 147 legacy templates across 16 directories — added full metadata headers
- 3 `social_links/` templates — normalized section type value
- 5 `banner_announcement/` templates — corrected section type from `cta` to `banner`
