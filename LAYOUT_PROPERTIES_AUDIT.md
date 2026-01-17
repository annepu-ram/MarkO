# Layout Properties Implementation Gap Audit

**Date:** January 8, 2026  
**Issue:** YAML schema properties that are defined but not implemented in rendering  
**Scope:** Responsive breakpoints and sizing constraints

---

## Executive Summary

This audit has identified **two critical implementation gaps** where properties are defined in YAML schemas, appear in the properties panel, and can be set by users, but have **zero effect on the rendered output**.

### Issues Found

1. **Columnsgrid Responsive Breakpoints** - Properties defined, CSS variables generated, but no media queries to consume them
2. **Layout Sizing Properties** - Properties defined in schema but completely ignored by rendering macros

### Impact

- **5 columnsgrid instances** in bakery template are using responsive breakpoints that don't work
- **0 instances** using layout sizing properties (fortunate, as they don't work)
- Users waste time configuring non-functional settings
- Documentation gap creates confusion about expected behavior

### Status Summary

| Component | Property | Schema | Defaults | Rendering | Status |
|-----------|----------|--------|----------|-----------|--------|
| `columnsgrid` | `responsive.breakpoints.md` | ✅ Defined | ✅ `2` | ❌ **Not working** | 🔴 **BROKEN** |
| `columnsgrid` | `responsive.breakpoints.sm` | ✅ Defined | ✅ `1` | ❌ **Not working** | 🔴 **BROKEN** |
| `layout-row` | `layout.minWidth` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-row` | `layout.maxWidth` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-row` | `layout.minHeight` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-row` | `layout.maxHeight` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-row` | `layout.width` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | ⚠️ **REDUNDANT** |
| `layout-row` | `layout.height` | ✅ Defined | ⚠️ Not in defaults | ❌ **Ignored** | ⚠️ **REDUNDANT** |
| `layout-column` | `layout.minWidth` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-column` | `layout.maxWidth` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-column` | `layout.minHeight` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-column` | `layout.maxHeight` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | 🔴 **BROKEN** |
| `layout-column` | `layout.width` | ✅ Defined | ✅ `auto` | ❌ **Ignored** | ⚠️ **REDUNDANT** |
| `layout-column` | `layout.height` | ✅ Defined | ⚠️ Not in defaults | ❌ **Ignored** | ⚠️ **REDUNDANT** |

---

## Issue 1: Columnsgrid Responsive Breakpoints

### Problem Statement

Users can configure responsive column counts for medium and small viewports, but these settings have **no effect**. Columns remain at the desktop count regardless of screen size.

### Current Implementation

#### 1. YAML Schema Definition

**File:** [`component_schemas.yaml`](component_schemas.yaml) lines 284-296

```yaml
columnsgrid:
  groups:
  - id: responsive
    label: Responsive
    fields:
    - path: responsive.breakpoints.md
      type: number
      label: Columns at Medium Width
      min: 1
      max: 4
    - path: responsive.breakpoints.sm
      type: number
      label: Columns at Small Width
      min: 1
      max: 3
```

#### 2. Component Defaults

**File:** [`component_defaults.yaml`](component_defaults.yaml) lines 76-79

```yaml
columnsgrid:
  layout:
    columns: 2
    gap: md
    align: center
  responsive:
    breakpoints:
      md: 2  # Columns at medium width
      sm: 1  # Columns at small width
```

#### 3. CSS Variable Generation

**File:** [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html) lines 863-867

```jinja2
{# Columnsgrid specific properties #}
{% if component.name == 'columnsgrid' %}
     {% set _ = styles.append('--cols: ' ~ (layout.columns | default(2)) ~ ';') %}
     {% if props.responsive and props.responsive.breakpoints %}
        {% if props.responsive.breakpoints.md %}{% set _ = styles.append('--cols-md: ' ~ props.responsive.breakpoints.md ~ ';') %}{% endif %}
        {% if props.responsive.breakpoints.sm %}{% set _ = styles.append('--cols-sm: ' ~ props.responsive.breakpoints.sm ~ ';') %}{% endif %}
     {% endif %}
{% endif %}
```

**Result:** CSS variables are generated on the columnsgrid element:
```html
<div class="columnsgrid" style="--cols: 3; --cols-md: 2; --cols-sm: 1;">
```

#### 4. Rendering Implementation

**File:** [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html) lines 226-265

The macro renders columns using inline Flexbox:

```jinja2
{% set column_count = layout_props.columns | default(2) | int %}
{% set column_width = 'calc((100% - (gap × (n-1))) / n)' %}

<div class="columnsgrid__row" style="display: flex; gap: {{ gap_value }};">
    {% for col_index in range(column_count) %}
        <div class="columnsgrid__col" style="width: {{ column_width }}; flex: 0 0 {{ column_width }};">
            <!-- column content -->
        </div>
    {% endfor %}
</div>
```

**Problem:** The `column_count` is hardcoded from `layout.columns` at render time. There's no way for CSS to change the number of columns or their widths responsively.

#### 5. CSS Styles

**File:** [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 56-98

```css
.columnsgrid {
    width: 100%;
    box-sizing: border-box;
}

.columnsgrid__row {
    display: flex;
    width: 100%;
    box-sizing: border-box;
}

.columnsgrid__col {
    min-height: 100px;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}
```

**Missing:** No media queries that reference `--cols-md` or `--cols-sm` variables.

### Root Cause Analysis

The implementation generates CSS variables (`--cols-md`, `--cols-sm`) but **never uses them**. The column count and widths are baked into inline styles at server render time and cannot be changed by CSS.

**Chain of events:**
1. ✅ User sets `responsive.breakpoints.md: 2` in YAML
2. ✅ Macro reads property and generates `--cols-md: 2;` CSS variable
3. ❌ **NO CSS MEDIA QUERIES** consume this variable
4. ❌ Columns remain at desktop count on all screen sizes

### Expected Behavior

When the viewport narrows:
- **Desktop (>992px)**: Show `layout.columns` columns (e.g., 3)
- **Medium (768px-992px)**: Show `responsive.breakpoints.md` columns (e.g., 2)
- **Small (<768px)**: Show `responsive.breakpoints.sm` columns (e.g., 1)

### Actual Behavior

Columns always show `layout.columns` count, regardless of viewport width.

### Bakery Template Impact

**5 columnsgrid instances** using responsive breakpoints:

1. **Line 548**: Today's Specials - 3 cols → 2 (md) → 1 (sm)
2. **Line 894**: Breads Tab - 4 cols → 1 (sm)
3. **Line 1013**: Cakes Tab - 2 cols → 1 (sm)
4. **Line 1132**: Pastries Tab - 2 cols → 1 (sm)
5. **Line 1432**: Testimonials - 3 cols → 2 (md) → 1 (sm)

**All 5 instances are non-functional.** The bakery template expects responsive behavior that doesn't exist.

### Example YAML (Not Working)

```yaml
- name: columnsgrid
  properties:
    layout:
      columns: 3      # Desktop: 3 columns
      gap: lg
    responsive:
      breakpoints:
        md: 2         # ❌ Doesn't work - still 3 columns
        sm: 1         # ❌ Doesn't work - still 3 columns
  columns:
    - components: [...]
    - components: [...]
    - components: [...]
```

### Fix Recommendations

#### **Option A: CSS Media Queries (Recommended)**

Add media queries to [`components.css`](ssr_python/static/css/components.css) that consume the CSS variables:

```css
/* Desktop: use --cols variable */
.columnsgrid__col {
    width: calc((100% - (var(--gap, 1rem) * (var(--cols, 2) - 1))) / var(--cols, 2));
    flex: 0 0 calc((100% - (var(--gap, 1rem) * (var(--cols, 2) - 1))) / var(--cols, 2));
}

/* Medium screens: use --cols-md if defined */
@media (max-width: 992px) {
    .columnsgrid__col {
        width: calc((100% - (var(--gap, 1rem) * (var(--cols-md, var(--cols, 2)) - 1))) / var(--cols-md, var(--cols, 2)));
        flex: 0 0 calc((100% - (var(--gap, 1rem) * (var(--cols-md, var(--cols, 2)) - 1))) / var(--cols-md, var(--cols, 2)));
    }
}

/* Small screens: use --cols-sm if defined */
@media (max-width: 768px) {
    .columnsgrid__col {
        width: calc((100% - (var(--gap, 1rem) * (var(--cols-sm, var(--cols, 2)) - 1))) / var(--cols-sm, var(--cols, 2)));
        flex: 0 0 calc((100% - (var(--gap, 1rem) * (var(--cols-sm, var(--cols, 2)) - 1))) / var(--cols-sm, var(--cols, 2)));
    }
}
```

**Note:** This requires also generating a `--gap` CSS variable for the gap value.

**Pros:**
- Minimal changes to existing code
- Leverages already-generated CSS variables
- Maintains current Flexbox approach

**Cons:**
- Complex calc() formulas
- Requires generating gap as CSS variable too
- Still renders all columns in HTML (not hidden, just resized)

#### **Option B: CSS Grid with auto-fit (Alternative)**

Redesign columnsgrid to use CSS Grid instead of Flexbox:

```css
.columnsgrid__row {
    display: grid;
    grid-template-columns: repeat(var(--cols, 2), 1fr);
    gap: var(--gap, 1rem);
}

@media (max-width: 992px) {
    .columnsgrid__row {
        grid-template-columns: repeat(var(--cols-md, var(--cols, 2)), 1fr);
    }
}

@media (max-width: 768px) {
    .columnsgrid__row {
        grid-template-columns: repeat(var(--cols-sm, var(--cols, 2)), 1fr);
    }
}
```

**Pros:**
- Cleaner, simpler CSS
- Grid is better suited for this use case
- Easier to understand and maintain

**Cons:**
- Requires changing rendering macro (remove individual column widths)
- Breaking change to existing implementation

#### **Option C: Remove Property from Schema**

If responsive breakpoints won't be implemented, remove the properties from the schema to avoid confusion.

**Pros:**
- Honest about capabilities
- Prevents users from wasting time on broken features

**Cons:**
- Removes useful feature from documentation
- Bakery template would need updates

---

## Issue 2: Layout Sizing Properties

### Problem Statement

`layout-row` and `layout-column` components have sizing properties (`minWidth`, `maxWidth`, `minHeight`, `maxHeight`, `width`, `height`) defined in their schemas, but these properties are **completely ignored** by the rendering macros.

### Current Implementation

#### 1. YAML Schema Definition

**File:** [`component_schemas.yaml`](component_schemas.yaml)

**layout-row** (lines 76-93):
```yaml
layout-row:
  groups:
  - id: sizing
    label: Sizing
    fields:
    - path: layout.width
      type: text
      label: Width
    - path: layout.minWidth
      type: text
      label: Min Width
    - path: layout.maxWidth
      type: text
      label: Max Width
    - path: layout.minHeight
      type: text
      label: Min Height
    - path: layout.maxHeight
      type: text
      label: Max Height
```

**layout-column** (lines 185-202): Same structure

#### 2. Component Defaults

**File:** [`component_defaults.yaml`](component_defaults.yaml)

**layout-row** (lines 23-27):
```yaml
layout-row:
  layout:
    width: auto
    minWidth: auto
    maxWidth: auto
    minHeight: auto
    maxHeight: auto
```

**layout-column** (lines 50-54): Same structure

#### 3. Rendering Implementation

**File:** [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html)

**layout-row** (lines 184-203):
```jinja2
{% macro render_layout_row(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set layout_props = properties.layout | default({}) %}
    {% set tag = layout_props.tag | default('section') %}
    
    {# Outer wrapper styles: box model properties #}
    {% set outer_styles = build_styles(component, tokens, part='outer') %}
    
    {# Inner wrapper styles: flex layout properties #}
    {% set inner_styles = build_flex_styles(component, tokens, 'row') %}
    
    <{{ tag }} class="layout-row chrome-target" data-component-id="{{ component_id }}" style="{{ outer_styles }}">
        <div class="layout-row__content" style="{{ inner_styles }}">
            {% for child in component.components | default([]) %}
                {% set child_path = path + ['components', loop.index0] %}
                {{ render_component(child, tokens, child_path) }}
            {% endfor %}
        </div>
    </{{ tag }}>
{% endmacro %}
```

**layout-column** (lines 205-224): Same structure with `'column'` orientation

#### 4. Style Generation Macros

**File:** [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html)

**`build_styles()` macro** (lines 775-980): Generates spacing, appearance, background, border, shadow styles, but **NO WIDTH/HEIGHT properties**.

**Search for sizing properties in macro:**
```bash
# Result: 0 matches for minWidth, maxWidth, minHeight, maxHeight
```

### Root Cause Analysis

The sizing properties are:
1. ✅ Defined in schema
2. ✅ Have default values
3. ✅ Appear in properties panel UI
4. ✅ Stored in YAML when user sets them
5. ❌ **NEVER READ** by `build_styles()` macro
6. ❌ **NEVER APPLIED** to rendered HTML

**The properties are completely orphaned.**

### Expected Behavior

When a user sets sizing constraints:

```yaml
- name: layout-row
  properties:
    layout:
      minWidth: 300px
      maxWidth: 1200px
      minHeight: 400px
```

**Expected output:**
```html
<section class="layout-row" style="min-width: 300px; max-width: 1200px; min-height: 400px; ...">
```

### Actual Behavior

The sizing properties are silently ignored:

```html
<section class="layout-row" style="..."> 
<!-- NO min-width, max-width, or min-height styles -->
```

### Bakery Template Impact

**0 instances** using sizing properties in the bakery template.

This is fortunate—nobody is trying to use these broken properties. However, the properties still appear in the UI, which could confuse users.

### Width and Height Properties: Redundancy Analysis

#### The Problem with `width` and `height`

The schema also defines `layout.width` and `layout.height` properties. However, these are **redundant** if `minWidth`/`maxWidth` and `minHeight`/`maxHeight` are properly implemented.

#### Why They're Redundant

**1. Fixed Width Can Be Achieved with Min/Max:**
```css
/* Using width property */
width: 500px;

/* Equivalent using min/max */
min-width: 500px;
max-width: 500px;
```

**2. Flexible Width is Better with Min/Max:**
```css
/* Constrained flexible width */
width: 100%;
min-width: 300px;
max-width: 1200px;

/* More common and useful than fixed width */
```

**3. Common Use Cases Don't Need `width`:**
- **Centered container:** `max-width: 1200px; margin: 0 auto;`
- **Responsive card:** `min-width: 250px; max-width: 400px;`
- **Flexible sidebar:** `min-width: 200px; max-width: 300px;`

#### Current State of `width` and `height`

**In Defaults:**
- `layout-row.layout.width`: `auto` ✅
- `layout-row.layout.height`: ⚠️ **Not in defaults** (inconsistent!)
- `layout-column.layout.width`: `auto` ✅
- `layout-column.layout.height`: ⚠️ **Not in defaults** (inconsistent!)

**In Rendering:**
- Both completely ignored (same as min/max properties)

### Fix Recommendations

#### **Priority 1: Implement Min/Max Sizing (Recommended)**

Add sizing property handling to the `build_styles()` macro:

**File:** [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html) (around line 860)

```jinja2
{# Sizing constraints (min/max width/height) #}
{% if layout.minWidth and layout.minWidth != 'auto' %}
    {% set _ = styles.append('min-width: ' ~ layout.minWidth ~ ';') %}
{% endif %}
{% if layout.maxWidth and layout.maxWidth != 'auto' %}
    {% set _ = styles.append('max-width: ' ~ layout.maxWidth ~ ';') %}
{% endif %}
{% if layout.minHeight and layout.minHeight != 'auto' %}
    {% set _ = styles.append('min-height: ' ~ layout.minHeight ~ ';') %}
{% endif %}
{% if layout.maxHeight and layout.maxHeight != 'auto' %}
    {% set _ = styles.append('max-height: ' ~ layout.maxHeight ~ ';') %}
{% endif %}
```

**Apply to:** `layout-row` and `layout-column` components only (check `component.name`).

**Pros:**
- Simple fix (10 lines of code)
- Enables powerful responsive layouts
- Matches user expectations from schema

**Cons:**
- Requires testing to ensure no conflicts with existing styles

#### **Priority 2: Remove `width` and `height` Properties**

After implementing min/max, remove redundant properties:

1. **Remove from schema** ([`component_schemas.yaml`](component_schemas.yaml)):
   - Delete `layout.width` field from layout-row and layout-column
   - Delete `layout.height` field from layout-row and layout-column (already missing from defaults)

2. **Remove from defaults** ([`component_defaults.yaml`](component_defaults.yaml)):
   - Delete `width: auto` from layout-row and layout-column

**Pros:**
- Simplifies UI (fewer confusing options)
- Prevents users from setting properties that don't work well with min/max
- Cleaner mental model (only min/max for sizing)

**Cons:**
- Breaking change if any templates use `width` property (bakery template doesn't)

#### **Alternative: Implement All Sizing Properties**

If `width` and `height` must be kept, implement them too:

```jinja2
{% if layout.width and layout.width != 'auto' %}
    {% set _ = styles.append('width: ' ~ layout.width ~ ';') %}
{% endif %}
{% if layout.height and layout.height != 'auto' %}
    {% set _ = styles.append('height: ' ~ layout.height ~ ';') %}
{% endif %}
```

**Not recommended** because:
- Less flexible than min/max
- Can cause layout issues if combined with min/max
- Adds complexity without clear benefit

---

## Other Components Analysis

### Tabs Component

**Schema:** [`component_schemas.yaml`](component_schemas.yaml) lines 1376-1426

**Responsive features:** None

**Properties:**
- `layout.orientation` (horizontal/vertical)
- `layout.widthMode` (fit, 25%, 50%, 75%, stretch)
- Typography and appearance settings

**Status:** ✅ No responsive breakpoints defined

---

### Accordion Component

**Schema:** [`component_schemas.yaml`](component_schemas.yaml) lines 1254-1304

**Responsive features:** None

**Properties:**
- `behavior.allowMultipleOpen`
- Typography (title and content)
- Appearance (colors, borders, padding)

**Status:** ✅ No responsive breakpoints defined

---

### Carousel Component

**Schema:** [`component_schemas.yaml`](component_schemas.yaml) lines 1579-1609

**Responsive features:** None

**Properties:**
- `behavior.autoplay`, `behavior.delay`, `behavior.loop`
- `navigation.showArrows`, `navigation.showDots`

**Status:** ✅ No responsive breakpoints defined

---

## Hardcoded Constraints Reference

These CSS min/max constraints are **working** (hardcoded in CSS, not user-configurable):

### File: [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css)

| Selector | Property | Value | Purpose |
|----------|----------|-------|---------|
| `.preview-area` | `min-height` | `200px` | Prevent preview area from collapsing |
| `.columnsgrid__col` | `min-height` | `100px` | Ensure columns are visible even when empty |
| `.column-placeholder` | `min-height` | `100px` | Make empty column drop zones clickable |
| `.titlebar-logo` | `max-height` | `calc(var(--base-height) - 2rem)` | Scale logo to fit titlebar height |
| `.titlebar-logo` (scrolled) | `max-height` | `calc((var(--base-height) - 2rem) * 0.5)` | Shrink logo when titlebar shrinks |
| `.col` | `min-width` | `0` | Prevent flex items from overflowing |
| `.carousel-slide` | `min-width` | `100%` | Force each slide to fill carousel width |
| `button` | `min-height` | `36px` | Ensure buttons are tall enough to click |
| `button` | `min-width` | `80px` | Ensure buttons are wide enough to read |
| `input, textarea, select` | `min-height` | `36px` | Consistent form field height |
| `.titlebar` | `min-height` | `60px` | Prevent titlebar from collapsing |
| `.accordion-summary` | `min-height` | `48px` | Ensure accordion headers are clickable |
| `.tabs label` | `min-height` | `40px` | Ensure tab labels are tall enough |

### Working Responsive Behavior (Hardcoded)

#### Titlebar Mobile Menu

**File:** [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 468-478

```css
@media (max-width: 768px) {
    .titlebar-nav {
        display: none;
        flex-direction: column;
        position: absolute;
        top: var(--base-height, 6rem);
        left: 0;
        width: 100%;
        background-color: #fff;
        border-top: 1px solid #ddd;
        padding: 1rem;
    }
}
```

**Status:** ✅ Working (not user-configurable, always collapses at 768px)

#### Generic Column Class

**File:** [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 613-618

```css
@media (max-width: 767px) {
    .col {
        width: 100% !important;
        flex: 0 0 100% !important;
    }
}
```

**Status:** ✅ Working (legacy class, may conflict with columnsgrid if both used)

**Note:** This is a generic `.col` class that forces stacking on mobile. It's separate from the columnsgrid component and not user-configurable.

---

## Implementation Priority Recommendations

### Priority 1: Layout Sizing Properties (Easiest Fix)

**Time Estimate:** 1-2 hours

**Steps:**
1. Add sizing property handling to `build_styles()` macro (10 lines of code)
2. Test with layout-row and layout-column components
3. Verify no conflicts with existing spacing/appearance properties
4. Update CSS_CONFLICTS_AUDIT.md to reflect fixed properties

**Impact:** 
- Enables flexible, constrained layouts
- Low risk (properties are unused in bakery template)
- High value (common use case for responsive design)

**Follow-up:**
- Consider removing redundant `width` and `height` properties from schema

### Priority 2: Columnsgrid Responsive Breakpoints (More Complex)

**Time Estimate:** 4-6 hours

**Steps:**
1. **Option A (Recommended):** Add CSS media queries to consume `--cols-md` and `--cols-sm`
   - Generate `--gap` CSS variable alongside `--cols`
   - Add media queries with calc() formulas to components.css
   - Test across different viewport widths
   
2. **Option B (Alternative):** Redesign with CSS Grid
   - Modify `render_columnsgrid()` macro to use Grid instead of Flex
   - Simplify CSS with grid-template-columns
   - More maintainable long-term but bigger change

**Impact:**
- **5 broken instances** in bakery template would start working
- Medium risk (changes affect existing rendering)
- High value (responsive grids are essential for modern layouts)

### Priority 3: Schema Cleanup (Low Effort, High Clarity)

**Time Estimate:** 30 minutes

**Steps:**
1. Remove `layout.width` and `layout.height` from layout-row and layout-column schemas
2. Keep min/max properties (more flexible and useful)
3. Update any documentation mentioning these properties

**Impact:**
- Reduces UI clutter
- Prevents confusion about property usage
- Aligns schema with best practices

---

## Testing Checklist

### For Layout Sizing Properties Fix

- [ ] Set `minWidth: 300px` on layout-row, verify applied
- [ ] Set `maxWidth: 1200px` on layout-row, verify applied
- [ ] Set `minHeight: 400px` on layout-column, verify applied
- [ ] Combine with existing spacing properties, verify no conflicts
- [ ] Test with `auto` value (should not output style)
- [ ] Test with centered layout (`margin-inline: auto` + `maxWidth`)

### For Columnsgrid Responsive Breakpoints Fix

- [ ] Set 3 cols desktop, 2 cols md, 1 col sm - verify at each breakpoint
- [ ] Test with different gap values (xs, md, xl)
- [ ] Test with different alignments (stretch, start, center)
- [ ] Verify columns wrap at exact breakpoint pixels (768px, 992px)
- [ ] Test bakery template "Today's Specials" section
- [ ] Test bakery template "Testimonials" section
- [ ] Verify no conflicts with legacy `.col` class

---

## Conclusion

This audit has identified two significant gaps between YAML schema definitions and actual rendering behavior. Both issues stem from the same root cause: properties are defined and exposed to users but never consumed by the rendering pipeline.

**Key Takeaways:**

1. **Columnsgrid responsive breakpoints** generate CSS variables but lack media queries to use them (5 broken instances in bakery template)
2. **Layout sizing properties** are defined but completely ignored by rendering macros (0 instances in bakery template, fortunately)
3. **Width and height properties** are redundant if min/max are implemented and should be removed from schemas
4. **Other components** (tabs, accordion, carousel) don't have responsive properties and are working as designed
5. **Hardcoded constraints** in CSS are working correctly but aren't user-configurable

**Recommended Action Plan:**

1. ✅ **Immediate:** Fix layout sizing properties (easy win, low risk)
2. ⚠️ **Short-term:** Implement columnsgrid responsive breakpoints (moderate complexity, high value)
3. 🔧 **Follow-up:** Remove redundant width/height properties from schemas (cleanup)

These fixes will eliminate user confusion, make the bakery template work as intended, and enable proper responsive layouts throughout the application.

---

**Audit completed:** January 8, 2026

