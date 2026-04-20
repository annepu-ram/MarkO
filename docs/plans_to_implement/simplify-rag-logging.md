# Plan: Simplify RAG Agent Logging

## Problem

The RAG pipeline has 43 log statements across 4 files, logging retrieval counts, chunk details, image redistribution, structural fixes, and other intermediate steps. This makes logs noisy and hard to read. We only need the **final prompt sent to the LLM** and the **LLM response** for each agent.

## Goal

For each agent call, log exactly two things:
1. **PROMPT** — the full system prompt + user prompt (including retrieved chunks already assembled into the prompt)
2. **OUTPUT** — the raw LLM response

Everything else gets removed or downgraded to `DEBUG`.

---

## Files to Change

### 1. `ssr_python/rag/agent/rag_agent.py` (19 log statements)

**Keep (upgrade to structured format):**
- Line 96: Request start — simplify to one line: `logger.info(f"=== RAG CHAT: intent={intent.action} | {message}")`
- Line 193: Single-call RAG response — already logged, keep as `logger.info(f"SINGLE-CALL OUTPUT:\n{response}")`

**Add:**
- Log the full `system` + `user_prompt` before `model.generate()` at line 192:
  ```python
  logger.info(f"SINGLE-CALL SYSTEM PROMPT:\n{system}")
  logger.info(f"SINGLE-CALL USER PROMPT:\n{user_prompt}")
  ```

**Remove or downgrade to DEBUG:**
- Line 78: `"RAG indexes loaded"` → DEBUG
- Line 95: `"=" * 80` separator → remove
- Line 97: `"Selected Images: ..."` → remove
- Lines 103-107: Intent details → fold into the single request line
- Line 157: Tier fallback → DEBUG
- Lines 173-175: Retrieved chunk counts/details → remove (chunks are in the prompt)
- Line 189: Truncated user prompt → remove (we now log full prompt)
- Lines 222-223: `"PLANNER AGENT: starting"` separator → remove
- Lines 226-227: Planner section count + JSON output → remove (logged in planner_agent.py)
- Line 244: Unassigned images warning → DEBUG
- Line 266: Image redistribution → DEBUG
- Line 268: No visual sections → DEBUG
- Lines 273-274: `"STYLER AGENT: starting"` separator → remove
- Lines 278-279: Styler output → keep as `logger.info(f"STYLER OUTPUT:\n{json}")` (no LLM call, so this IS the output)
- Lines 287-289: Builder section start + input JSON → remove (logged in builder_agent.py)
- Line 301: Builder output → remove (logged in builder_agent.py)
- Lines 307-308: Stitcher separator → remove
- Line 310: Stitcher output → keep as final pipeline output
- Line 330: Validation failure → keep as WARNING

### 2. `ssr_python/rag/agent/planner_agent.py` (5 log statements)

**Keep (upgrade to structured format):**
- Before `model.generate()` at line 117, log full prompts:
  ```python
  logger.info(f"PLANNER SYSTEM PROMPT:\n{PLANNER_SYSTEM}")
  logger.info(f"PLANNER USER PROMPT:\n{user_prompt}")
  ```
- Line 118: Raw LLM response → keep as `logger.info(f"PLANNER OUTPUT:\n{response}")`

**Remove or downgrade to DEBUG:**
- Lines 68-70: Outline chunk counts/details → remove
- Line 75: Icon retrieval count → remove
- Line 90: Style chunk count → remove
- Line 114: Truncated user prompt → remove (we now log full prompt)

### 3. `ssr_python/rag/agent/builder_agent.py` (7 log statements)

**Keep (upgrade to structured format):**
- Before `model.generate()` at line 228, log full prompts:
  ```python
  logger.info(f"BUILDER [{section_type}] SYSTEM PROMPT:\n{BUILDER_SYSTEM}")
  logger.info(f"BUILDER [{section_type}] USER PROMPT:\n{user_prompt}")
  ```
- Line 229: Raw LLM response → keep as `logger.info(f"BUILDER [{section_type}] OUTPUT:\n{response}")`

**Remove or downgrade to DEBUG:**
- Lines 75-78: Style-tagged chunk counts → remove
- Line 91: Fallback to component tier → DEBUG
- Lines 99-101: Retrieved chunk counts/details → remove
- Line 110: Chunks after rerank → remove
- Line 226: Truncated user prompt → remove (we now log full prompt)
- Line 232: Extracted YAML → remove (redundant with raw response)

### 4. `ssr_python/rag/agent/stitcher.py` (12 log statements)

**No LLM calls** — stitcher is pure logic. Downgrade all to DEBUG except errors.

**Keep as WARNING/ERROR:**
- Line 308: Empty section warning
- Line 317: Empty after parsing warning
- Lines 327-328: Invalid YAML error

**Downgrade to DEBUG:**
- All `_fix_structure()` debug logs (lines 115, 120, 129, 135, 140, 145, 167) — already DEBUG, keep
- Line 325: Section stitched → DEBUG
- Line 341: Final output size → DEBUG

---

## Resulting Log Shape (per create_page request)

```
INFO  === RAG CHAT: intent=create_page | "build me a SaaS landing page"
INFO  PLANNER SYSTEM PROMPT: <full system prompt>
INFO  PLANNER USER PROMPT: <full user prompt with style chunks, outlines, icons, images>
INFO  PLANNER OUTPUT: <raw JSON response>
INFO  STYLER OUTPUT: <styled sections JSON>
INFO  BUILDER [hero] SYSTEM PROMPT: <full system prompt>
INFO  BUILDER [hero] USER PROMPT: <full user prompt with reference templates, specs, theme>
INFO  BUILDER [hero] OUTPUT: <raw YAML response>
INFO  BUILDER [pricing] SYSTEM PROMPT: ...
INFO  BUILDER [pricing] USER PROMPT: ...
INFO  BUILDER [pricing] OUTPUT: ...
INFO  BUILDER [testimonials] SYSTEM PROMPT: ...
INFO  BUILDER [testimonials] USER PROMPT: ...
INFO  BUILDER [testimonials] OUTPUT: ...
INFO  STITCHER OUTPUT: <final assembled YAML>
```

For single-call RAG (modify/add/explain):
```
INFO  === RAG CHAT: intent=modify | "change the hero background to blue"
INFO  SINGLE-CALL SYSTEM PROMPT: <full system prompt>
INFO  SINGLE-CALL USER PROMPT: <full user prompt with chunks>
INFO  SINGLE-CALL OUTPUT: <raw response>
```

---

## Implementation Notes

- All removed `logger.info()` calls become `logger.debug()` (not deleted) so they're available via log level config if needed
- The full prompts will be large (thousands of chars) — this is intentional; the point is to capture exactly what the LLM sees
- No changes to `query_analyzer.py`, `prompt_builder.py`, `component_specs.py`, `model_backend.py`, or `hybrid.py` (they have no logging)
- Styler agent has no LLM call (it's rule-based enrichment), so we log its output only in `rag_agent.py`
