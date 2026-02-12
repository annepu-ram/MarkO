# Fix Nested Layout-Column Overflow in Parent Column

## Context

In the split-screen hero template, the social proof logos `layout-column` overflows beyond its parent column. This is a rendering engine bug affecting ALL nested layout-columns.

## Root Cause: Missing `parent_direction` in Layout-Column Rendering

**The call chain:**

1. `render_component(child, tokens, path, 'column')` — receives `parent_direction='column'` (line 234)
2. `render_layout_column(component, tokens, path, component_id)` — does NOT receive `parent_direction` (line 17)
3. `build_styles(component, tokens, part='outer')` — does NOT receive `layout_direction` (line 222)
4. Width mode section (line 1450): `{% if layout_direction == 'column' %}` → **False** (None != 'column')
5. Falls into **else branch (row context)** → generates `flex: 0 0 100%; min-width: 100%;`

**The problem:** `flex: 0 0 100%` in a flex **column** parent means `flex-basis: 100%` controls **HEIGHT** (not width). So the nested layout-column tries to be **100% of the parent's height** and **can't shrink** (flex-shrink: 0).

In the split-screen template: parent column is ~44rem tall (stretched by right image). The social proof section gets `flex: 0 0 100%` → tries to be 44rem tall → overflows because other children (badge, heading, form, etc.) also need space.

**This affects ALL nested layout-columns** — they all get row-context flex properties regardless of actual parent direction.

## Fix: Pass `parent_direction` Through the Call Chain

### Change 1: Dispatcher passes `parent_direction` to `render_layout_column`

**File:** `_components.html` lines 16-17

```jinja2
# Current:
{% elif name == 'layout-column' %}
    {{ render_layout_column(component, tokens, path, component_id) }}

# Fixed:
{% elif name == 'layout-column' %}
    {{ render_layout_column(component, tokens, path, component_id, parent_direction) }}
```

### Change 2: `render_layout_column` receives and passes `parent_direction`

**File:** `_components.html` line 207

```jinja2
# Current:
{% macro render_layout_column(component, tokens, path, component_id) %}
    ...
    {% set outer_styles = build_styles(component, tokens, part='outer') %}

# Fixed:
{% macro render_layout_column(component, tokens, path, component_id, parent_direction='row') %}
    ...
    {% set outer_styles = build_styles(component, tokens, part='outer', layout_direction=parent_direction) %}
```

### Change 3: Same fix for `render_layout_row`

**File:** `_components.html` line 186

Apply the same pattern so layout-rows also get correct context when nested.

```jinja2
# Current:
{% macro render_layout_row(component, tokens, path, component_id) %}
    ...
    {% set outer_styles = build_styles(component, tokens, part='outer') %}

# Fixed:
{% macro render_layout_row(component, tokens, path, component_id, parent_direction='row') %}
    ...
    {% set outer_styles = build_styles(component, tokens, part='outer', layout_direction=parent_direction) %}
```

And in dispatcher:
```jinja2
# Current:
{% elif name == 'layout-row' %}
    {{ render_layout_row(component, tokens, path, component_id) }}

# Fixed:
{% elif name == 'layout-row' %}
    {{ render_layout_row(component, tokens, path, component_id, parent_direction) }}
```

### Result

With this fix, a nested layout-column in a column parent gets:
- **Column context** (correct): `width: 100%;` — proper horizontal sizing
- **Before (buggy)**: `flex: 0 0 100%; min-width: 100%;` — forces 100% height, can't shrink

## Verification

1. Run Flask server: `cd ssr_python && python app.py`
2. Load split-screen hero template (`02_split_screen.yaml`)
3. Check social proof section stays within parent column bounds
4. Check other templates with nested layout-columns (bookstore, conference, restaurant)
5. **DevTools check**: Inspect nested layout-column — should have `width: 100%` NOT `flex: 0 0 100%`

## Critical Files

- `_components.html` line 2 — `render_component` dispatcher (lines 14-17)
- `_components.html` lines 186-205 — `render_layout_row` macro
- `_components.html` lines 207-238 — `render_layout_column` macro
- `_components.html` lines 1446-1500 — Width mode section that checks `layout_direction`
- `example_templates/hero/02_split_screen.yaml` — Primary test case
