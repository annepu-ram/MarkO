# Plan: Update test_pipeline.py to Match RAG Agent Flow

## Problem

`ssr_python/scripts/test_pipeline.py` is out of sync with `rag_agent.py._create_page_pipeline()`. Key differences:

| Area | test_pipeline.py (current) | rag_agent.py (actual) |
|------|---------------------------|----------------------|
| **Planner** | Manually builds prompt with only outline chunks | Uses `PlannerAgent.plan()` which retrieves outlines, icons, AND style chunks |
| **Styler** | Missing entirely | Calls `StylerAgent.style()` to assign style_props per section |
| **Builder prompt** | Manually assembled, missing style_props, style_context, style_name | Uses `BuilderAgent.build_section()` with full style context |
| **Builder retrieval** | No style-filtered search, no tier="section" | Style-filtered → section_type-only → component tier fallback |
| **Stitcher** | Passes raw `outline` | Passes `styled_outline` (with style_props and style_name) |
| **Step count** | 5 steps | Should be 6 (intent → planner → styler → builder × N → stitcher → validation) |

## Goal

Rewrite test_pipeline.py to use the actual agent classes (`PlannerAgent.plan()`, `StylerAgent.style()`, `BuilderAgent.build_section()`) instead of manually reconstructing prompts. This keeps the script in sync with rag_agent.py automatically.

---

## Changes

### Step 1: Intent Analysis — no change
Keep as-is. `QueryAnalyzer.analyze()` is already called correctly.

### Step 2: Planner Agent — use `PlannerAgent.plan()` directly

**Current:** Manually retrieves outline chunks, builds prompt, calls `model.generate()`, parses JSON.

**New:** Call `planner.plan(prompt)` which internally handles:
- Outline chunk retrieval (guide tier)
- Icon name retrieval (icon tier)
- Style chunk retrieval (style tier)
- Prompt assembly with all context
- LLM call + JSON parsing

Display:
- The parsed outline JSON (from return value)
- The `style_context` string (second return value)
- Page title, theme, section list

Note: The system/user prompts and raw LLM response are already logged to `rag_agent.log` by the simplified logging we just implemented. The test script should focus on **inputs and outputs visible to the pipeline**, not duplicate the logging.

### Step 3: Styler Agent — NEW STEP

**Add:** Import and call `StylerAgent`:
```python
from rag.agent.styler_agent import StylerAgent

styler = StylerAgent(model)
styled_outline = styler.style(outline, style_context)
sections = styled_outline.get("sections", [])
style_name = styled_outline.get("style_name", "")
```

Display:
- `style_name`
- Per-section `style_props` summary

### Step 4: Builder Agent — use `BuilderAgent.build_section()` directly

**Current:** Manually retrieves chunks, builds prompt with hardcoded theme_str, calls `model.generate()`.

**New:** Call `builder.build_section(section, theme, ...)` which internally handles:
- Style-filtered retrieval with fallback cascade
- Reranking
- Component specs injection
- Style props block, style reference block, style notes
- LLM call

Pass the same args as rag_agent.py:
```python
theme = styled_outline.get("theme", outline.get("theme", {}))
yaml_str = builder.build_section(
    section, theme,
    image_context="",        # no images in test
    style_name=style_name,
    style_context=style_context,
)
```

Display:
- Extracted YAML per section (return value)

### Step 5: Stitcher — pass `styled_outline`

**Current:** `stitch_page(outline, section_yamls)`
**New:** `stitch_page(styled_outline, section_yamls)`

### Step 6: Validation — no change
Keep YAML syntax check and component name check as-is.

### Other changes

- Update `total_steps` from 5 to 6
- Update step numbering (builder is now step 4, stitcher step 5, validation step 6)
- Import `StylerAgent`
- Update summary to show `1 planner + 1 styler + N builders` LLM call breakdown
- Remove manual prompt construction code (the `build_component_specs`, `VALID_TOKENS` imports become unused — remove them)
- Remove `PLANNER_SYSTEM` and `BUILDER_SYSTEM` imports (no longer used for manual prompt display)
- Keep timing per-step for performance visibility

### What the script should NOT do

- Should not duplicate prompt/response logging (that's in `rag_agent.log` now)
- Should not manually reconstruct prompts that the agents already build
- Should not show intermediate retrieval details (chunk lists, rerank counts)

---

## Resulting Script Flow

```
Step 1: Intent Analysis         — QueryAnalyzer.analyze()
Step 2: Planner Agent           — PlannerAgent.plan() → outline + style_context
Step 3: Styler Agent            — StylerAgent.style() → styled_outline
Step 4: Builder Agent × N       — BuilderAgent.build_section() per section
Step 5: Stitcher                — stitch_page(styled_outline, section_yamls)
Step 6: Validation              — YAML parse + component name check

Summary: timing, LLM calls, line count, pass/fail
```
