# Width, Padding & Margin Property Inconsistency Analysis

**Date:** January 29, 2025
**Files Analyzed:** `component_schemas.yaml`, `component_defaults.yaml`, `_components.html`

---

## Executive Summary

This report documents significant inconsistencies in how width, padding, and margin properties are defined across components in the Swift Sites codebase. The analysis reveals:

- **2 different padding path patterns** across components
- **12+ missing schema fields** (properties exist but aren't editable in UI)
- **Schema group misalignments** (widthMode in wrong group for some components)
- **Naming convention inconsistencies** (camelCase vs nested objects)

---

## TABLE 1: Complete Property Path Matrix

### A. Layout Containers

| Component | widthMode Path | widthMode Schema Group | Padding Path | Padding Schema Group | Margin Path | Margin Schema Group |
|-----------|---------------|----------------------|--------------|---------------------|-------------|---------------------|
| **page** | — | — | `spacing.paddingBlock/Inline` | spacing | — | — |
| **layout-row** | — | — | `spacing.paddingBlock/Inline` | spacing | `spacing.marginBlock/Inline` | spacing |
| **layout-column** | `layout.widthMode` | layout | `spacing.paddingBlock/Inline` | spacing | `spacing.marginBlock/Inline` | spacing |
| **columnsgrid** | — | — | `spacing.paddingBlock/Inline` | spacing | `spacing.marginBlock/Inline` | spacing |

**Pattern:** Layout containers use `spacing.paddingBlock/paddingInline` (flat camelCase)

---

### B. Text Components

| Component | widthMode Path | widthMode Schema Group | Padding Path | Padding Schema Group | Margin Path | Margin Schema Group |
|-----------|---------------|----------------------|--------------|---------------------|-------------|---------------------|
| **heading** | `layout.widthMode` | layout | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **paragraph** | `layout.widthMode` | layout | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **eyebrow** | `layout.widthMode` | layout | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **caption** | `layout.widthMode` | layout | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **blockquote** | `layout.widthMode` | layout | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **link** | — | — | `appearance.padding.block/inline` | **NO SCHEMA** | `spacing.marginBlock/Inline` | **NO SCHEMA** |

**Pattern:** Text components use `appearance.padding.block/inline` (nested object)

---

### C. Media Components

| Component | widthMode Path | widthMode Schema Group | Padding Path | Padding Schema Group | Margin Path | Margin Schema Group |
|-----------|---------------|----------------------|--------------|---------------------|-------------|---------------------|
| **image** | `layout.widthMode` | appearance (WRONG) | `appearance.padding.block/inline` | **NO SCHEMA** | `spacing.marginBlock/Inline` | spacing |
| **gif** | `layout.widthMode` | layout | `appearance.padding.block/inline` | **NO SCHEMA** | `spacing.marginBlock/Inline` | spacing |
| **video** | — | — | — | — | `spacing.marginBlock/Inline` | **NO SCHEMA** |
| **carousel** | — | — | — | — | `spacing.marginBlock/Inline` | spacing |
| **video-background** | `layout.widthMode` | layout | `content.padding` (scalar!) | content | `spacing.marginBlock/Inline` | spacing |

**Issues:**
- image `widthMode` is in "appearance" group in schema (should be "layout")
- image/gif padding exists in defaults but NO schema fields
- video margin exists in defaults but NO schema fields
- video-background uses scalar `content.padding` instead of block/inline split

---

### D. Form Components

| Component | widthMode Path | widthMode Schema Group | Padding Path | Padding Schema Group | Margin Path | Margin Schema Group |
|-----------|---------------|----------------------|--------------|---------------------|-------------|---------------------|
| **button** | — | — | `appearance.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **textbox** | — | — | `appearance.padding.block/inline` | **NO SCHEMA** | `spacing.marginBlock/Inline` | **NO SCHEMA** |
| **textarea** | — | — | `appearance.padding.block/inline` | **NO SCHEMA** | `spacing.marginBlock/Inline` | **NO SCHEMA** |
| **dropdown** | — | — | — | — | — | — |
| **checkbox** | — | — | — | — | — | — |
| **radio** | — | — | — | — | — | — |
| **calendar** | — | — | — | — | — | — |

**Issues:**
- textbox/textarea have padding + margin in defaults but NO schema fields

---

### E. Interactive Components

| Component | widthMode Path | widthMode Schema Group | Padding Path | Padding Schema Group | Margin Path | Margin Schema Group |
|-----------|---------------|----------------------|--------------|---------------------|-------------|---------------------|
| **accordion** | `layout.widthMode` | layout | `appearance.padding.block/inline` | spacing (WRONG) | `spacing.marginBlock/Inline` | spacing |
| **tabs** | `layout.widthMode` | layout | `appearance.content.padding.block/inline` | appearance | `spacing.marginBlock/Inline` | spacing |
| **hamburger** | — | — | — | — | — | — |
| **form** | — | — | — | — | — | — |

**Issues:**
- accordion: padding fields are in "spacing" group but path is `appearance.padding.*`
- tabs: uses unique nested path `appearance.content.padding.*`

---

## TABLE 2: Schema Field Status by Component

| Component | Padding in Schema | Margin in Schema | widthMode in Schema | Notes |
|-----------|------------------|------------------|--------------------|----|
| page | Yes | — | — | |
| layout-row | Yes | Yes | — | |
| layout-column | Yes | Yes | Yes | |
| columnsgrid | Yes | Yes | — | |
| titlebar | — | — | — | No spacing properties |
| heading | Yes | Yes | Yes | |
| paragraph | Yes | Yes | Yes | |
| eyebrow | Yes | Yes | Yes | |
| caption | Yes | Yes | Yes | |
| blockquote | Yes | Yes | Yes | |
| link | **NO** | **NO** | — | **MISSING BOTH** |
| image | **NO** | Yes | Yes | **MISSING PADDING** |
| gif | **NO** | Yes | Yes | **MISSING PADDING** |
| video | — | **NO** | — | **MISSING MARGIN** |
| carousel | — | Yes | — | |
| video-background | Yes (scalar) | Yes | Yes | Uses scalar padding |
| button | Yes | Yes | — | |
| textbox | **NO** | **NO** | — | **MISSING BOTH** |
| textarea | **NO** | **NO** | — | **MISSING BOTH** |
| dropdown | — | — | — | |
| checkbox | — | — | — | |
| radio | — | — | — | |
| calendar | — | — | — | |
| accordion | Yes | Yes | Yes | Group mismatch |
| tabs | Yes | Yes | Yes | Unique nested path |
| hamburger | — | — | — | |
| form | — | — | — | |
| br | — | — | — | |

**Legend:** Yes = In schema, **NO** = In defaults but NOT in schema, — = Not applicable

---

## TABLE 3: Default Values Comparison

### Padding Defaults

| Component | paddingBlock | paddingInline | Path Pattern |
|-----------|--------------|---------------|--------------|
| page | none | none | `spacing.*` |
| layout-row | sm | sm | `spacing.*` |
| layout-column | sm | sm | `spacing.*` |
| columnsgrid | none | none | `spacing.*` |
| heading | none | none | `appearance.padding.*` |
| paragraph | none | none | `appearance.padding.*` |
| eyebrow | none | none | `appearance.padding.*` |
| caption | none | none | `appearance.padding.*` |
| blockquote | md | md | `appearance.padding.*` |
| link | none | none | `appearance.padding.*` |
| image | none | none | `appearance.padding.*` |
| gif | none | none | `appearance.padding.*` |
| button | sm | md | `appearance.padding.*` |
| textbox | sm | sm | `appearance.padding.*` |
| textarea | sm | sm | `appearance.padding.*` |
| accordion | sm | sm | `appearance.padding.*` |
| tabs | md | md | `appearance.content.padding.*` |
| video-background | md | — | `content.padding` (scalar) |

### Margin Defaults

| Component | marginBlock | marginInline |
|-----------|-------------|--------------|
| layout-row | none | none |
| layout-column | none | none |
| columnsgrid | none | none |
| heading | md | none |
| paragraph | sm | none |
| eyebrow | xs | none |
| caption | xs | none |
| blockquote | lg | none |
| link | xs | xs |
| image | sm | none |
| gif | sm | none |
| video | md | none |
| button | sm | xs |
| textbox | sm | none |
| textarea | sm | none |
| accordion | md | none |
| tabs | md | none |
| carousel | lg | none |
| video-background | none | none |

---

## TABLE 4: Naming Convention Analysis

| Pattern | Path Example | Used By | Count |
|---------|--------------|---------|-------|
| **Flat camelCase** | `spacing.paddingBlock` | Layout containers | 4 |
| **Nested object** | `appearance.padding.block` | Text, form, media | 12 |
| **Deep nested** | `appearance.content.padding.block` | tabs only | 1 |
| **Scalar** | `content.padding` | video-background only | 1 |

### Inconsistency Impact

1. **Developer confusion:** Which pattern to use for new components?
2. **Macro complexity:** `build_styles()` must handle multiple patterns
3. **Documentation burden:** Multiple patterns to explain
4. **Migration risk:** Changing paths breaks existing YAML files

---

## TABLE 5: Schema Group Misalignments

| Component | Property | Current Group | Expected Group | Impact |
|-----------|----------|---------------|----------------|--------|
| image | `layout.widthMode` | appearance | layout | UI confusion |
| accordion | `appearance.padding.*` | spacing | appearance | UI confusion |

---

## TABLE 6: Missing Schema Fields (High Priority)

These properties exist in defaults and are read by macros, but users **cannot edit them** via the properties panel:

| Component | Missing Fields | Default Values | Priority |
|-----------|---------------|----------------|----------|
| **textbox** | `appearance.padding.block/inline` | sm/sm | HIGH |
| **textbox** | `spacing.marginBlock/Inline` | sm/none | HIGH |
| **textarea** | `appearance.padding.block/inline` | sm/sm | HIGH |
| **textarea** | `spacing.marginBlock/Inline` | sm/none | HIGH |
| **link** | `appearance.padding.block/inline` | none/none | MEDIUM |
| **link** | `spacing.marginBlock/Inline` | xs/xs | MEDIUM |
| **image** | `appearance.padding.block/inline` | none/none | MEDIUM |
| **gif** | `appearance.padding.block/inline` | none/none | MEDIUM |
| **video** | `spacing.marginBlock/Inline` | md/none | MEDIUM |

---

## TABLE 7: Unique Patterns (Special Cases)

| Component | Pattern | Description |
|-----------|---------|-------------|
| **tabs** | `appearance.content.padding.block/inline` | Deepest nesting, unique among all |
| **video-background** | `content.padding` (scalar) | Only scalar padding, not block/inline split |
| **accordion** | Mixed placement | Padding path in `appearance.*` but schema group is "spacing" |

---

## Recommendations

### 1. HIGH PRIORITY: Add Missing Schema Fields

Add schema definitions for these components to enable UI editing:

**textbox** (add to schema):
```yaml
- id: spacing
  label: Spacing
  fields:
  - path: appearance.padding.block
    type: select
    label: Padding (Vertical)
    tokens: spacingScale
  - path: appearance.padding.inline
    type: select
    label: Padding (Horizontal)
    tokens: spacingScale
  - path: spacing.marginBlock
    type: select
    label: Margin (Vertical)
    tokens: spacingScale
  - path: spacing.marginInline
    type: select
    label: Margin (Horizontal)
    tokens: spacingScale
```

Same pattern needed for: **textarea**, **link**, **image** (padding only), **gif** (padding only), **video** (margin only)

### 2. MEDIUM PRIORITY: Fix Schema Group Misalignment

**image**: Move `layout.widthMode` from "appearance" group to "layout" group
**accordion**: Move padding fields from "spacing" group to "appearance" group (or change path to `spacing.paddingBlock/Inline`)

### 3. LOW PRIORITY: Documentation

Document the two-pattern system:
- **Layout containers:** Use `spacing.paddingBlock/paddingInline`
- **Content components:** Use `appearance.padding.block/inline`

### 4. FUTURE: Standardization

Consider migrating to single pattern for all components (breaking change, requires YAML migration)

---

## Standardization Deep Dive

### The Problem

Currently, the codebase uses **4 different patterns** for the same conceptual property (padding):

```
Pattern A: spacing.paddingBlock         (layout containers)
Pattern B: appearance.padding.block     (text/form components)
Pattern C: appearance.content.padding.block  (tabs only)
Pattern D: content.padding              (video-background only)
```

This creates:
- **Cognitive load** for developers adding new components
- **Macro complexity** in `build_styles()` handling multiple patterns
- **User confusion** when property locations differ between similar components
- **Bug risk** when assumptions about paths are wrong

---

### Option A: Standardize to `spacing.*` Pattern

**Target:** All components use `spacing.paddingBlock/paddingInline` and `spacing.marginBlock/marginInline`

**Rationale:**
- Follows CSS logical properties naming (`padding-block`, `padding-inline`)
- Groups all spacing-related properties under one parent
- Simpler path structure (flat, not nested)

**Changes Required:**

| Component | Current Path | New Path |
|-----------|-------------|----------|
| heading | `appearance.padding.block` | `spacing.paddingBlock` |
| paragraph | `appearance.padding.block` | `spacing.paddingBlock` |
| eyebrow | `appearance.padding.block` | `spacing.paddingBlock` |
| caption | `appearance.padding.block` | `spacing.paddingBlock` |
| blockquote | `appearance.padding.block` | `spacing.paddingBlock` |
| link | `appearance.padding.block` | `spacing.paddingBlock` |
| image | `appearance.padding.block` | `spacing.paddingBlock` |
| gif | `appearance.padding.block` | `spacing.paddingBlock` |
| button | `appearance.padding.block` | `spacing.paddingBlock` |
| textbox | `appearance.padding.block` | `spacing.paddingBlock` |
| textarea | `appearance.padding.block` | `spacing.paddingBlock` |
| accordion | `appearance.padding.block` | `spacing.paddingBlock` |
| tabs | `appearance.content.padding.block` | `spacing.contentPaddingBlock` (special case) |
| video-background | `content.padding` | `spacing.contentPadding` or `spacing.paddingBlock` |

**Pros:**
- Consistent with CSS naming conventions
- All spacing in one place
- Simpler macro code

**Cons:**
- Breaking change for ALL existing YAML files
- Tabs needs special handling (content vs tab padding)

---

### Option B: Standardize to `appearance.padding.*` Pattern

**Target:** All components use `appearance.padding.block/inline`

**Rationale:**
- Padding is a visual/appearance property
- Keeps typography, background, and padding together in `appearance`
- Already used by majority of components

**Changes Required:**

| Component | Current Path | New Path |
|-----------|-------------|----------|
| page | `spacing.paddingBlock` | `appearance.padding.block` |
| layout-row | `spacing.paddingBlock` | `appearance.padding.block` |
| layout-column | `spacing.paddingBlock` | `appearance.padding.block` |
| columnsgrid | `spacing.paddingBlock` | `appearance.padding.block` |
| video-background | `content.padding` | `appearance.padding.block` + `appearance.padding.inline` |

**Pros:**
- Fewer files to change (only 4 layout containers)
- Groups visual properties together

**Cons:**
- Nested object syntax more verbose
- Inconsistent with CSS logical property naming

---

### Option C: Hybrid Approach (Recommended)

**Target:** Keep both patterns but document clearly and enforce consistency within categories

**Rules:**
1. **Layout containers** (page, layout-row, layout-column, columnsgrid, form): Use `spacing.paddingBlock/paddingInline`
2. **Content components** (all text, media, form inputs, interactive): Use `appearance.padding.block/inline`
3. **Margin** always uses `spacing.marginBlock/marginInline` (already consistent)

**Why This Works:**
- No breaking changes
- Clear mental model: "containers use spacing.*, content uses appearance.*"
- Matches the current majority pattern
- Can document in `LLM_COMPONENT_GUIDE.md` and `CLAUDE.md`

---

### Migration Plan (If Option A or B Chosen)

#### Phase 1: Backward Compatibility Layer

Add fallback handling in `build_styles()` macro:

```jinja2
{# Support both old and new padding paths #}
{% set padding_block = spacing.paddingBlock
    | default(appearance.padding.block)
    | default('none') %}
```

This allows old YAML to work while new YAML uses standardized paths.

#### Phase 2: Update Schema & Defaults

1. Update `component_schemas.yaml` with new paths
2. Update `component_defaults.yaml` with new structure
3. Both old and new paths work during transition

#### Phase 3: Migration Script

Create a Python script to migrate existing YAML files:

```python
def migrate_yaml(content):
    """Migrate old padding paths to new standardized paths"""
    # Convert appearance.padding.block → spacing.paddingBlock
    content = re.sub(
        r'appearance:\s*\n(\s*)padding:\s*\n\s*block:\s*(\w+)',
        r'spacing:\n\1paddingBlock: \2',
        content
    )
    return content
```

#### Phase 4: Remove Backward Compatibility

After all templates migrated:
1. Remove fallback handling from macros
2. Update documentation
3. Remove old paths from schemas

---

### Estimated Effort

| Option | Files Changed | YAML Files to Migrate | Complexity |
|--------|--------------|----------------------|------------|
| Option A | ~5 | All templates | High |
| Option B | ~5 | 4 layout containers only | Medium |
| Option C | ~2 (docs only) | None | Low |

---

### Recommendation

**Short-term:** Implement **Option C (Hybrid)** - document the pattern, fix missing schema fields, no breaking changes.

**Long-term:** If the codebase grows significantly, consider **Option A** with a proper migration path, as CSS logical properties (`padding-block`, `margin-inline`) are the modern standard.

---

## Files to Modify

| File | Action |
|------|--------|
| `component_schemas.yaml` | Add missing schema fields (~50 lines of new fields) |
| `component_schemas.yaml` | Fix group alignment for image and accordion |

---

## Verification Steps

After implementing changes:
1. Start Flask server: `python app.py`
2. Load bakery_template.yaml
3. Select each affected component (textbox, textarea, link, image, gif, video)
4. Verify new fields appear in properties panel
5. Change values and verify they apply correctly
6. Verify no regression in other components
