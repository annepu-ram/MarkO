---
name: Layout Properties Audit
overview: Audit all layout-related YAML properties that are defined in schemas but not implemented in rendering, including responsive breakpoints and sizing constraints (min/max width/height).
todos:
  - id: analyze-columnsgrid-responsive
    content: Analyze columnsgrid responsive breakpoints implementation gap
    status: completed
  - id: analyze-layout-sizing
    content: Document layout-row and layout-column sizing properties gap (min/max width/height)
    status: completed
  - id: analyze-titlebar
    content: Document titlebar's hardcoded responsive behavior
    status: completed
  - id: analyze-generic-col
    content: Document legacy .col class media query
    status: pending
  - id: check-other-components
    content: Check tabs, accordion, carousel for responsive features
    status: completed
  - id: scan-bakery-template
    content: Count instances using non-functional properties in bakery template
    status: completed
  - id: document-hardcoded-constraints
    content: List all working hardcoded CSS min/max constraints
    status: completed
  - id: create-audit-doc
    content: Create comprehensive LAYOUT_PROPERTIES_AUDIT.md document
    status: completed
    dependencies:
      - analyze-columnsgrid-responsive
      - analyze-layout-sizing
      - analyze-titlebar
      - analyze-generic-col
      - check-other-components
      - scan-bakery-template
      - document-hardcoded-constraints
---

# Layout Properties Implementation Gap Audit

## Objective

Document all layout-related properties that are defined in YAML schemas and defaults but are **not actually implemented** in the rendering pipeline. This includes:
1. **Responsive breakpoints** (columnsgrid)
2. **Sizing constraints** (layout-row, layout-column: minWidth, maxWidth, minHeight, maxHeight)
3. **Redundant properties** (width, height - unnecessary if min/max are implemented)

## Issues Discovered

### Issue 1: Columnsgrid Responsive Breakpoints (Non-Functional)

**Problem:** Users can define responsive breakpoints in YAML, but they have no effect on rendering.

**YAML Schema defines:**
- `responsive.breakpoints.md` (columns at medium width)
- `responsive.breakpoints.sm` (columns at small width)

**What happens:**
- Macro generates CSS variables: `--cols`, `--cols-md`, `--cols-sm`
- **Missing:** No CSS media queries consume these variables
- **Result:** Columns remain fixed at desktop count on all screen sizes

### Issue 2: Layout Sizing Properties (Non-Functional)

**Problem:** `layout-row` and `layout-column` have sizing properties in their schemas, but these are completely ignored during rendering.

**YAML Schema defines:**
- `layout.minWidth`
- `layout.maxWidth`
- `layout.minHeight`
- `layout.maxHeight`
- `layout.width` *(redundant if min/max are implemented)*
- `layout.height` *(redundant if min/max are implemented)*

**What happens:**
- Properties appear in properties panel
- Users can set values
- **Missing:** Rendering macros don't read or apply these properties
- **Result:** Values are stored in YAML but have zero effect on output

**Note:** The `width` and `height` properties are **redundant** if min/max width/height are properly implemented. Users can achieve any fixed width by setting `minWidth` and `maxWidth` to the same value, or more commonly use min/max for flexible, constrained layouts.

## Scope

Based on investigation:

- **Components with responsive properties in schema**: `columnsgrid` (not working)
- **Components with sizing properties in schema**: `layout-row`, `layout-column` (not working)
- **Components with hardcoded media queries**: `titlebar`, generic `.col` class (working but not user-configurable)
- **Components to check**: `tabs`, `accordion`, `carousel` (may have implicit responsive behavior)

## Audit Steps

### 1. Columnsgrid Responsive Breakpoints Analysis

**Current State:**

- YAML Schema defines: `responsive.breakpoints.md` and `responsive.breakpoints.sm`
- Component defaults set: `md: 2, sm: 1`
- Macro generates CSS variables: `--cols`, `--cols-md`, `--cols-sm`
- **ISSUE**: No CSS media queries consume these variables

**Files to examine:**

- [`component_schemas.yaml`](component_schemas.yaml) lines 284-296
- [`component_defaults.yaml`](component_defaults.yaml) lines 76-79
- [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html) lines 226-260 (render_columnsgrid macro)
- [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html) lines 863-867 (CSS variable generation)
- [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 56-98 (columnsgrid styles)

**Expected behavior:** When viewport narrows to medium width (e.g., <992px), columns should reflow to `md` count. At small width (e.g., <768px), columns should reflow to `sm` count.**Actual behavior:** Columns remain at fixed `columns` count regardless of viewport width.

### 2. Titlebar Component Analysis

**Current State:**

- No responsive properties in YAML schema
- Has hardcoded `@media (max-width: 768px)` for mobile menu collapse
- **STATUS**: Working as intended (not user-configurable)

**Files to examine:**

- [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 468-478

### 3. Generic Column Class Analysis

**Current State:**

- Legacy `.col` class has hardcoded media query
- Forces 100% width at `@media (max-width: 767px)`
- **STATUS**: May conflict with columnsgrid if both used

**Files to examine:**

- [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css) lines 613-618

### 4. Layout Sizing Properties Analysis

**Components affected:** `layout-row`, `layout-column`

**Files to examine:**

- Schema: [`component_schemas.yaml`](component_schemas.yaml)
  - layout-row: lines 76-93
  - layout-column: lines 185-202
- Defaults: [`component_defaults.yaml`](component_defaults.yaml)
  - layout-row: lines 23-27 (all default to `auto`)
  - layout-column: lines 50-54 (all default to `auto`)
- Macros: [`ssr_python/templates/macros/_components.html`](ssr_python/templates/macros/_components.html)
  - `render_layout_row`: lines 175-203
  - `render_layout_column`: lines 205-224
  - **ZERO references** to width/minWidth/maxWidth/minHeight/maxHeight properties

**Expected behavior:** Users set min/max width/height values, and they're applied as inline styles or CSS constraints.

**Actual behavior:** Properties are defined and editable but completely ignored by rendering macros.

### 5. Hardcoded CSS Constraints Documentation

Document all working min/max constraints in [`ssr_python/static/css/components.css`](ssr_python/static/css/components.css):

- `.preview-area`: `min-height: 200px`
- `.columnsgrid__col`: `min-height: 100px`
- `.titlebar-logo`: `max-height: calc(var(--base-height) - 2rem)`
- `button`: `min-height: 36px`, `min-width: 80px`
- And others...

### 6. Other Components Check

Verify if `tabs`, `accordion`, `carousel` have any responsive features:

- Check schemas for responsive properties
- Check CSS for media queries
- Check JavaScript for viewport-based behavior

## Deliverable

Create a comprehensive audit document: `LAYOUT_PROPERTIES_AUDIT.md` containing:

1. **Executive Summary**
   - Two critical issues found: responsive breakpoints and sizing properties
   - Properties defined in schemas but not implemented in rendering
   - Impact on user experience (settings appear to work but don't)
   - List of working vs broken features

2. **Issue 1: Columnsgrid Responsive Breakpoints**
   - Current YAML schema definition
   - Current rendering implementation (CSS variables generated)
   - What's missing (CSS media queries)
   - Root cause analysis
   - Code example showing expected behavior
   - Fix recommendations (Option A: media queries, Option B: CSS Grid)

3. **Issue 2: Layout Sizing Properties**
   - Current YAML schema (layout-row, layout-column)
   - Properties defined: minWidth, maxWidth, minHeight, maxHeight, width, height
   - Current rendering implementation (properties completely ignored)
   - What's missing (inline style generation in `build_styles()` macro)
   - **Important note:** `width` and `height` properties are **redundant** if min/max are implemented
   - Code example showing expected implementation
   - Fix recommendation (add to `build_styles()` macro, consider removing width/height)

4. **Bakery Template Impact Analysis**
   - Count of columnsgrid instances with responsive breakpoints
   - Count of layout-row/layout-column instances with sizing properties
   - Which non-functional properties are being used in the template

5. **Hardcoded Constraints Reference**
   - List all CSS min/max constraints in components.css
   - Note which are working (hardcoded) vs broken (YAML-defined)
   - Document titlebar responsive behavior (working, hardcoded)

6. **Other Components Analysis**
   - Tabs: any responsive features?
   - Accordion: any responsive features?
   - Carousel: any responsive features?

7. **Recommendations**
   - **Priority 1:** Implement layout sizing properties (simpler fix)
     - Add minWidth, maxWidth, minHeight, maxHeight to `build_styles()` macro
     - Consider removing redundant `width` and `height` from schema
   - **Priority 2:** Implement columnsgrid responsive breakpoints (more complex)
     - Option A: Add CSS media queries to consume `--cols-md` and `--cols-sm`
     - Option B: Redesign using CSS Grid's auto-fit/auto-fill
   - **Priority 3:** Remove non-functional schema properties if not planning to implement

8. **Implementation Examples**
   - Show CSS inline styles for sizing properties
   - Show CSS media queries for responsive breakpoints
   - Show example YAML configurations that currently don't work

## Files to Create

- [`LAYOUT_PROPERTIES_AUDIT.md`](LAYOUT_PROPERTIES_AUDIT.md) - Comprehensive audit document covering:
  - Columnsgrid responsive breakpoints issue
  - Layout sizing properties issue (min/max width/height)
  - Width/height redundancy analysis
  - Bakery template impact
  - Implementation recommendations

## Key Findings to Document

**Non-Working YAML Properties:**
1. `columnsgrid.responsive.breakpoints.md` and `.sm` - defined but no CSS media queries
2. `layout-row.layout.minWidth/maxWidth/minHeight/maxHeight` - defined but not read by macros
3. `layout-column.layout.minWidth/maxWidth/minHeight/maxHeight` - defined but not read by macros
4. `layout-row.layout.width` and `.height` - **redundant** if min/max implemented
5. `layout-column.layout.width` and `.height` - **redundant** if min/max implemented

**Working Features (Hardcoded):**
- Titlebar mobile menu collapse at 768px
- Generic .col class stacks at 767px
- Various component min-height/min-width constraints in CSS