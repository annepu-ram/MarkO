# ColumnsGrid Bug Fix - Stretch Overflow Issue

## Problem Summary

When `verticalAlign: stretch` is set on columnsgrid, `.columnsgrid__col` overflows `.columnsgrid__row`. This does NOT happen with `top`, `center`, or `bottom` values.

---

## UPDATE: New Issue After maxHeight Fix (January 29, 2025)

### Observation

After adding `maxHeight: 15` to images in the columnsgrid:
- **verticalAlign: top** - Works correctly, all content visible
- **verticalAlign: stretch** - Content is CLIPPED at the bottom (buttons cut off)

### Screenshots Analysis

| Mode | Behavior |
|------|----------|
| `top` | Each column's height = own content. Buttons visible. No clipping. |
| `stretch` | All columns stretched to tallest. Buttons CLIPPED at bottom. |

### Root Cause: `overflow: hidden` on Outer Container

**Line 260 in `_components.html`:**
```jinja2
<div class="columnsgrid" ... style="{{ outer_styles }} overflow: hidden;">
```

The `overflow: hidden` was added to prevent unbounded growth when images had no maxHeight. Now that images have `maxHeight: 15`, this is no longer needed and is CAUSING the clipping issue.

### Why Clipping Occurs

1. `.columnsgrid` has `overflow: hidden`
2. With `stretch`, columns match tallest column's height
3. Tallest column (middle) has more paragraph text
4. Row height grows to accommodate
5. But `overflow: hidden` clips content that extends beyond expected bounds

### Solution Options

**Option 1: Remove `overflow: hidden` entirely (Recommended)**
- Now that images have maxHeight constraints, unbounded growth is prevented
- Simply remove `overflow: hidden` from line 260

**Option 2: Move `overflow: hidden` to columns only**
- Keep row able to grow naturally
- Clip only within individual columns if needed

**Option 3: Conditional `overflow: hidden`**
- Only apply `overflow: hidden` when `stretch` is NOT selected

---

## Proposed Implementation (Option 1)

### Change Required (Line 260 in `_components.html`)

**Current:**
```jinja2
<div class="columnsgrid chrome-target" data-component-id="{{ component_id }}" style="{{ outer_styles }} overflow: hidden;">
```

**Proposed:**
```jinja2
<div class="columnsgrid chrome-target" data-component-id="{{ component_id }}" style="{{ outer_styles }}">
```

Simply remove `overflow: hidden` from the outer container. The maxHeight constraint on images now prevents unbounded growth.

### Why This Works

| Scenario | Before (no maxHeight) | After (with maxHeight) |
|----------|----------------------|------------------------|
| `top/center/bottom` | Works fine | Works fine |
| `stretch` | Images expand infinitely → need overflow:hidden | Images capped at maxHeight → no infinite growth |

With `maxHeight: 15` (rem) on images:
- Images cannot exceed 15rem (240px) regardless of stretch
- Row height is bounded by content
- No need for `overflow: hidden` to clip

---

## Current Implementation

### Macro Structure (lines 260-266 in `_components.html`)

```jinja2
<div class="columnsgrid" style="{{ outer_styles }} overflow: hidden;">
    <div class="columnsgrid__row" style="display: flex; gap: {{ gap_value }}; align-items: {{ v_align_css }}; width: 100%; box-sizing: border-box; min-height: 0;">
        <div class="columnsgrid__col" style="position: relative; flex: 1 1 0; min-width: 0; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;">
            <!-- child components -->
        </div>
    </div>
</div>
```

### Vertical Alignment Mapping (lines 253-255)

```jinja2
{% set v_align = layout_props.verticalAlign | default('center') %}
{% set v_align_map = {'top': 'flex-start', 'center': 'center', 'bottom': 'flex-end', 'stretch': 'stretch'} %}
{% set v_align_css = v_align_map[v_align] | default('center') %}
```

---

## Root Cause Analysis

### Why `stretch` Causes Overflow

| Value | CSS | Column Height Behavior | Overflow? |
|-------|-----|------------------------|-----------|
| `top` | `align-items: flex-start` | Height = own content only | No |
| `center` | `align-items: center` | Height = own content only | No |
| `bottom` | `align-items: flex-end` | Height = own content only | No |
| `stretch` | `align-items: stretch` | **Forced to match tallest sibling** | **Yes** |

### The Flex Height Feedback Loop

With `align-items: stretch`:

1. **Row tells columns:** "Match the row's height"
2. **Row's height:** Determined by tallest column's content (no fixed height)
3. **Column is nested flex:** `display: flex; flex-direction: column`
4. **Images inside:** Have `min-height: 12.5rem` but **NO max-height**
5. **Feedback loop:** Image drives row height → stretch makes columns match → more space available → image can expand more

```
┌──────────────────────────────────────────────────┐
│ .columnsgrid (overflow: hidden)                   │
│ ┌──────────────────────────────────────────────┐ │
│ │ .columnsgrid__row                            │ │
│ │ align-items: stretch ← FORCES HEIGHT MATCH  │ │
│ │ min-height: 0 ← NO HEIGHT CONSTRAINT        │ │
│ │                                              │ │
│ │ ┌─────────────────┬─────────────────┐       │ │
│ │ │ col (flex:1 1 0)│ col (flex:1 1 0)│       │ │
│ │ │ min-height: 0   │ min-height: 0   │       │ │
│ │ │                 │                 │       │ │
│ │ │ ┌─────────────┐ │ ┌─────────────┐ │       │ │
│ │ │ │ IMAGE       │ │ │ PARAGRAPH   │ │       │ │
│ │ │ │ min-h:12.5r │ │ │ (short)     │ │       │ │
│ │ │ │ NO max-h    │ │ │             │ │       │ │
│ │ │ │     ↓       │ │ │             │ │       │ │
│ │ │ │ EXPANDS     │ │ │ STRETCHED   │ │       │ │
│ │ │ │ INFINITELY  │ │ │ TO MATCH    │ │       │ │
│ │ │ └─────────────┘ │ └─────────────┘ │       │ │
│ │ └─────────────────┴─────────────────┘       │ │
│ └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Key CSS Properties Contributing to Issue

| Element | Property | Value | Effect |
|---------|----------|-------|--------|
| `.columnsgrid` | `overflow` | `hidden` | Clips overflow but doesn't prevent it |
| `.columnsgrid__row` | `align-items` | `stretch` | Forces columns to match height |
| `.columnsgrid__row` | `min-height` | `0` | No minimum constraint on row |
| `.columnsgrid__col` | `flex` | `1 1 0` | Grow/shrink equally, basis 0 |
| `.columnsgrid__col` | `min-height` | `0` | Can shrink to 0 (overrides CSS 100px) |
| `.columnsgrid__col` | `display` | `flex` | Nested flex container |
| Image | `min-height` | `12.5rem` | Has minimum but no maximum |

---

## Proposed Solution

### Option A: Fix at Column Level (Recommended)

When `verticalAlign: stretch`, add these styles to `.columnsgrid__col`:
- `overflow: hidden` - Clips content exceeding column bounds
- `align-items: flex-start` - Prevents children from stretching internally

**Code Change (line 266):**

```jinja2
{# Before the column div #}
{% set col_styles = 'position: relative; flex: 1 1 0; min-width: 0; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;' %}
{% if v_align == 'stretch' %}
    {% set col_styles = col_styles ~ ' overflow: hidden; align-items: flex-start;' %}
{% endif %}

<div class="columnsgrid__col" style="{{ col_styles }}">
```

### Option B: Fix at Image Level

Set default `max-height` on images when inside stretched container. More complex - requires parent context detection.

### Option C: Fix at Row Level

Add height constraint to row when stretch is enabled. May limit flexibility.

---

## Implementation

### File: `ssr_python/templates/macros/_components.html`

### Location: Lines 262-266 in `render_columnsgrid` macro

### Current Code:

```jinja2
{% for col_index in range(column_count) %}
    {% set column = columns[col_index] if col_index < columns | length else {} %}
    {% set column_components = column.components | default([]) %}

    <div class="columnsgrid__col" style="position: relative; flex: 1 1 0; min-width: 0; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;">
```

### Proposed Code:

```jinja2
{% for col_index in range(column_count) %}
    {% set column = columns[col_index] if col_index < columns | length else {} %}
    {% set column_components = column.components | default([]) %}

    {# Add overflow:hidden and align-items:flex-start when stretch to prevent column overflow #}
    {% set col_styles = 'position: relative; flex: 1 1 0; min-width: 0; min-height: 0; box-sizing: border-box; display: flex; flex-direction: column;' %}
    {% if v_align == 'stretch' %}
        {% set col_styles = col_styles ~ ' overflow: hidden; align-items: flex-start;' %}
    {% endif %}

    <div class="columnsgrid__col" style="{{ col_styles }}">
```

---

## Verification Steps

1. Start Flask server: `python app.py`
2. Load `bakery_template.yaml`
3. Find columnsgrid in "Today's Freshly Baked Specials" section
4. In properties panel, set `verticalAlign: stretch`
5. **Before fix:** Columns overflow, content pushed out
6. **After fix:** Columns constrained, content clipped if needed

---

## Related Fixes Completed

| Bug | Status | Description |
|-----|--------|-------------|
| Bug 1 | ✅ DONE | Width overflow - columns + gaps exceeding parent |
| Bug 2 | ✅ DONE | Stretch overflow - removed `overflow: hidden` from line 260 |
| Bug 3 | ✅ DONE | Image maxHeight + rem units |
| Bug 4 | ✅ DONE | Text components getting wrong flex styles |
| Bug 5 | ✅ DONE | Added spacing properties (padding/margin) to columnsgrid schema/defaults |
| Bug 6 | ✅ DONE | Image 25% + layout-column stacking - added widthMode: 75 to layout-columns in bakery_template |

---

## Action Required

~~**Remove `overflow: hidden` from line 260 in `_components.html`**~~

✅ **IMPLEMENTED** - Removed `overflow: hidden` from columnsgrid outer container.

Test by loading bakery_template.yaml and setting columnsgrid `verticalAlign: stretch` - buttons should now be visible.

---

## Notes

- The `overflow: hidden` may clip content in extreme cases - user can set explicit `maxHeight` on images if needed
- `align-items: flex-start` prevents nested flex children from stretching, keeping them at natural height
- This solution is backward compatible - only affects stretch mode
