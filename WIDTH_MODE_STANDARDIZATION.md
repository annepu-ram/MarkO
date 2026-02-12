# Width Mode Standardization Enhancement

## Overview

Standardize width handling across all components using percentage-based `widthMode` property with gap-aware CSS calculations.

---

## Current State Analysis

### Components WITH widthMode Property

| Component | Path | Values | Implementation | Gap-Aware |
|-----------|------|--------|----------------|-----------|
| heading | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| paragraph | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| eyebrow | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| caption | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| blockquote | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| **image** | layout.widthMode | Token: 10-100% | **CSS data-attr** | **YES** |
| **gif** | layout.widthMode | Token: 10-100% | **CSS data-attr** | **YES** |
| accordion | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| tabs | layout.widthMode | fit, 25, 50, 75, stretch | Inline styles | No |
| video-background | layout.widthMode | fit, 25, 50, 75, stretch | Data-attr | Partial |

### Components WITHOUT widthMode Property

| Component | Current Behavior | Should Have widthMode? |
|-----------|------------------|------------------------|
| **layout-column** | Always 100% width | **YES - Critical** |
| button | inline-block, shrinks to content | YES |
| link | inline, shrinks to content | Optional |
| carousel | 100% width | YES |
| video | 100% width | YES |
| titlebar | 100% width | No (special nav) |
| layout-row | Container, always 100% | No (container) |
| form | Container, always 100% | No (container) |
| page | Root container | No |

### Key Inconsistencies Found

1. **Token reference vs hardcoded values**
   - Image/GIF use `widthPercentages` token: 10, 25, 30, 40, 50, 60, 75, 80, 90, 100
   - Text components use hardcoded: fit, 25, 50, 75, stretch
   - **Result:** Image can be 30% or 60%, but heading cannot

2. **Gap-aware vs simple percentage**
   - Image/GIF: `calc(50% - var(--row-gap) * 0.5)` - accounts for gap
   - Text: `width: 50%` or `flex: 1 0 48%` - doesn't account for gap
   - **Result:** Mixed text + images at 50% may not align perfectly

3. **Implementation approach**
   - Image/GIF: CSS via `data-width-mode` attribute (best practice)
   - Text: Inline styles generated in Jinja2 macro (harder to maintain)
   - **Result:** Inconsistent maintainability

4. **Layout-column has no width control**
   - Cannot create 25%/75% column layouts in a row
   - Current nowrap fix uses `min-width: 200px` (pixel value)
   - **Result:** User asked why pixel width instead of percentage

---

## Proposed Solution: Standardized widthMode

### Standard widthMode Values (Based on 12-Column Grid)

Based on [Bootstrap's 12-column grid system](https://getbootstrap.com/docs/5.0/layout/grid/) - the industry standard used by most frameworks. The number 12 has more divisors than any number before it (up to 60), allowing flexible layouts.

```yaml
# Standard widthMode values based on 12-column grid
widthMode: fit | 16 | 25 | 33 | 50 | 66 | 75 | 83 | stretch
```

**Value mapping to 12-column grid:**

| widthMode | Grid Columns | Actual % | Common Use Case |
|-----------|--------------|----------|-----------------|
| `fit` | auto | content | Shrink to content |
| `16` | 2/12 | 16.67% | Narrow sidebar, icon column |
| `25` | 3/12 | 25% | Quarter width, 4-column layout |
| `33` | 4/12 | 33.33% | Third width, 3-column layout |
| `50` | 6/12 | 50% | Half width, 2-column layout |
| `66` | 8/12 | 66.67% | Two-thirds, main content + sidebar |
| `75` | 9/12 | 75% | Three-quarters, main content |
| `83` | 10/12 | 83.33% | Wide content, narrow margin |
| `stretch` | 12/12 | 100% | Full width |

**Popular layout patterns:**
- **50% + 50%** - Equal two-column layout
- **33% + 33% + 33%** - Equal three-column layout
- **25% + 25% + 25% + 25%** - Equal four-column layout
- **25% + 75%** or **33% + 66%** - Sidebar + main content
- **16% + 66% + 16%** - Centered content with margins

### Gap-Aware Formula

**IMPORTANT:** The gap multiplier is based on **typical item count**, not the percentage value itself.

| Width | Typical Layout | Gaps | Correct Multiplier |
|-------|----------------|------|-------------------|
| 16%   | pairs with 83% | 1 gap | **0.8333** (5/6) |
| 25%   | 4 equal items  | 3 gaps | **0.75** (3/4) |
| 33%   | 3 equal items  | 2 gaps | **0.6667** (2/3) |
| 50%   | 2 equal items  | 1 gap | **0.5** (1/2) |
| 66%   | pairs with 33% | 1 gap | **0.3333** (1/3) |
| 75%   | pairs with 25% | 1 gap | **0.25** (1/4) |
| 83%   | pairs with 16% | 1 gap | **0.1667** (1/6) |

```css
/* CORRECT gap-aware formulas */
[data-width-mode="fit"]     { flex: 0 0 auto; }
[data-width-mode="16"]      { flex: 0 0 calc(16.67% - var(--row-gap, 0px) * 0.8333); }
[data-width-mode="25"]      { flex: 0 0 calc(25% - var(--row-gap, 0px) * 0.75); }
[data-width-mode="33"]      { flex: 0 0 calc(33.33% - var(--row-gap, 0px) * 0.6667); }
[data-width-mode="50"]      { flex: 0 0 calc(50% - var(--row-gap, 0px) * 0.5); }
[data-width-mode="66"]      { flex: 0 0 calc(66.67% - var(--row-gap, 0px) * 0.3333); }
[data-width-mode="75"]      { flex: 0 0 calc(75% - var(--row-gap, 0px) * 0.25); }
[data-width-mode="83"]      { flex: 0 0 calc(83.33% - var(--row-gap, 0px) * 0.1667); }
[data-width-mode="stretch"] { flex: 0 0 100%; }
```

**Example verification (3 items at 33%):**
- 3 × (33.33% - gap × 0.6667) = 100% - 2×gap
- Plus 2 gaps between = 100% - 2×gap + 2×gap = 100% ✓

**Example verification (25% + 75%):**
- (25% - gap × 0.75) + gap + (75% - gap × 0.25) = 100% - gap + gap = 100% ✓

### Implementation Pattern

All components should follow the image/gif pattern:

1. **Template:** Output `data-width-mode="{{ width_mode }}"` attribute
2. **CSS:** Handle all sizing via CSS selectors on `[data-width-mode]`
3. **No inline width styles** - CSS handles everything

---

## Components to Update

### 1. layout-column (Priority: HIGH)

**Why:** User's main request - enable percentage-based column widths

**Schema changes (`component_schemas.yaml`):**
```yaml
layout-column:
  - id: layout
    fields:
    - path: layout.widthMode
      type: select
      label: Width
      options:
        - value: stretch
          label: Full Width (100%)
        - value: '83'
          label: 83% (10/12 columns)
        - value: '75'
          label: 75% (9/12 columns)
        - value: '66'
          label: 66% (8/12 columns)
        - value: '50'
          label: 50% (6/12 columns)
        - value: '33'
          label: 33% (4/12 columns)
        - value: '25'
          label: 25% (3/12 columns)
        - value: '16'
          label: 16% (2/12 columns)
        - value: fit
          label: Fit Content
```

**Defaults changes (`component_defaults.yaml`):**
```yaml
layout-column:
  layout:
    widthMode: stretch  # Default to full width
```

**Template changes (`_components.html`):**
```jinja2
{% macro render_layout_column(component, tokens, path, component_id) %}
    {% set layout_props = properties.layout | default({}) %}
    {% set width_mode = layout_props.widthMode | default('stretch') %}

    <{{ tag }} class="layout-column chrome-target"
            data-component-id="{{ component_id }}"
            data-width-mode="{{ width_mode }}"
            style="{{ outer_styles }}">
```

**CSS changes (`components.css`):**
```css
/* Layout-column width modes - NO responsive breakpoints (keeps percentage on all viewports) */
.layout-column[data-width-mode] {
    box-sizing: border-box;
    flex-shrink: 0;  /* Don't shrink in nowrap rows */
}

.layout-column[data-width-mode="fit"] {
    flex: 0 0 auto;
    max-width: none;
    width: auto;
}

/* 16% - pairs with 83%, subtracts 5/6 of gap */
.layout-column[data-width-mode="16"] {
    flex: 0 0 calc(16.67% - var(--row-gap, 0px) * 0.8333);
    max-width: calc(16.67% - var(--row-gap, 0px) * 0.8333);
    width: auto;
}

/* 25% - assumes 4 items with 3 gaps, subtracts 3/4 of gap */
.layout-column[data-width-mode="25"] {
    flex: 0 0 calc(25% - var(--row-gap, 0px) * 0.75);
    max-width: calc(25% - var(--row-gap, 0px) * 0.75);
    width: auto;
}

/* 33% - assumes 3 items with 2 gaps, subtracts 2/3 of gap */
.layout-column[data-width-mode="33"] {
    flex: 0 0 calc(33.33% - var(--row-gap, 0px) * 0.6667);
    max-width: calc(33.33% - var(--row-gap, 0px) * 0.6667);
    width: auto;
}

/* 50% - assumes 2 items with 1 gap, subtracts 1/2 of gap */
.layout-column[data-width-mode="50"] {
    flex: 0 0 calc(50% - var(--row-gap, 0px) * 0.5);
    max-width: calc(50% - var(--row-gap, 0px) * 0.5);
    width: auto;
}

/* 66% - pairs with 33%, subtracts 1/3 of gap */
.layout-column[data-width-mode="66"] {
    flex: 0 0 calc(66.67% - var(--row-gap, 0px) * 0.3333);
    max-width: calc(66.67% - var(--row-gap, 0px) * 0.3333);
    width: auto;
}

/* 75% - pairs with 25%, subtracts 1/4 of gap */
.layout-column[data-width-mode="75"] {
    flex: 0 0 calc(75% - var(--row-gap, 0px) * 0.25);
    max-width: calc(75% - var(--row-gap, 0px) * 0.25);
    width: auto;
}

/* 83% - pairs with 16%, subtracts 1/6 of gap */
.layout-column[data-width-mode="83"] {
    flex: 0 0 calc(83.33% - var(--row-gap, 0px) * 0.1667);
    max-width: calc(83.33% - var(--row-gap, 0px) * 0.1667);
    width: auto;
}

.layout-column[data-width-mode="stretch"] {
    flex: 0 0 100%;
    max-width: 100%;
    width: 100%;
}
```

**Remove:** The pixel-based `min-width: 200px` rule added for nowrap rows

### 2. button (Priority: MEDIUM)

**Why:** Button cannot stretch to fill parent width

**Changes needed:**
- Add `layout.widthMode` to schema
- Add default `widthMode: fit`
- Output `data-width-mode` attribute
- CSS: Change `display: inline-block` to `display: inline-flex` or handle via flex
- Add width mode CSS rules

### 3. carousel (Priority: LOW)

**Why:** Consistency with tabs and accordion

**Changes needed:**
- Add `layout.widthMode` to schema
- Add default `widthMode: stretch`
- Output `data-width-mode` attribute
- Add CSS rules

### 4. video (Priority: LOW)

**Why:** Consistency with image/gif

**Changes needed:**
- Add `layout.widthMode` to schema
- Output `data-width-mode` attribute
- Add CSS rules (similar to image)

### 5. Text components (Priority: LOW - refactor)

**Why:** Move from inline styles to CSS-based approach

**Changes needed:**
- Remove inline width style generation from `build_styles` macro
- Output `data-width-mode` attribute instead
- Add CSS rules with gap-aware calculations

---

## Drawbacks Analysis

### 1. Gap Calculation Complexity

**Problem:** Current formula assumes components adding to 100%
- `25% - gap*0.25` + `75% - gap*0.75` + `gap` = 100% ✓
- But what about `25% + 25% + 25%`? That's only 75% total

**Mitigation:**
- This is acceptable - users expect 25% to mean approximately 25%
- Gap deduction ensures items don't wrap unexpectedly
- Document that percentages are approximate due to gap handling

### 2. Nested Layout Complexity

**Problem:** Layout-column inside layout-row with its own children
- Parent row has `--row-gap`
- Column children need different gap context

**Mitigation:**
- CSS custom properties scope correctly - child column creates new `--row-gap` for its children
- Each layout-row/column sets its own `--row-gap` which overrides parent
- Already working correctly for image/gif

### 3. Responsive Behavior Differences

**Problem:** What should 25% layout-column become on mobile?
- Images: 100% on mobile, 50% on tablet, 25% on desktop
- Columns: Should they follow same pattern?

**Decision (user confirmed):**
- **Option B: Keep percentage on all viewports** - columns are structural, user wants precise control
- 25% column stays 25% even on mobile
- This differs from image behavior but makes sense for layout control
- Note: Gap deduction still applies via `--row-gap` CSS variable

### 4. Breaking Changes

**Problem:** Existing YAML templates assume layout-column is always 100%

**Mitigation:**
- Default `widthMode: stretch` maintains current behavior
- Only explicit `widthMode` values change behavior
- Backward compatible

### 5. CSS File Size Increase

**Problem:** Each new component adds ~30 lines of CSS

**Mitigation:**
- Can use CSS nesting or preprocessor to reduce duplication
- Or create shared `.width-mode-25` utility classes
- Acceptable trade-off for consistency

### 6. Mixed Component Types in Same Row

**Problem:** Row with button (fit) + image (50%) + layout-column (25%)
- Each component type has different CSS rules
- May not align perfectly if one doesn't support widthMode

**Mitigation:**
- Standardize ALL components to have widthMode
- Until then, document which components support it

---

## Files to Modify

| File | Changes |
|------|---------|
| `component_schemas.yaml` | Add widthMode to layout-column, button, carousel, video |
| `component_defaults.yaml` | Add widthMode defaults |
| `_components.html` | Add data-width-mode to layout-column, button, carousel, video macros |
| `components.css` | Add width mode rules for new components, remove pixel min-width |
| `schema_tokens.yaml` | Standardize widthPercentages token with 12-column grid values |
| `LLM_COMPONENT_GUIDE.md` | Document widthMode usage |
| `media_components_test.yaml` | Update tests to use percentage widths for columns |

### schema_tokens.yaml Changes

Replace the current widthPercentages token with standardized 12-column grid values:

```yaml
widthPercentages:
  type: selectOptions
  options:
    - value: stretch
      label: Full Width (100%)
    - value: '83'
      label: 83% (10/12 columns)
    - value: '75'
      label: 75% (9/12 columns)
    - value: '66'
      label: 66% (8/12 columns)
    - value: '50'
      label: 50% (6/12 columns)
    - value: '33'
      label: 33% (4/12 columns)
    - value: '25'
      label: 25% (3/12 columns)
    - value: '16'
      label: 16% (2/12 columns)
    - value: fit
      label: Fit Content
```

This replaces the old arbitrary values (10, 30, 40, 60, 80, 90, 100) with industry-standard 12-column grid percentages.

---

## Verification Plan

1. **Load `media_components_test.yaml`**
2. **Test 8 (Cards):** Change layout-columns from `min-width: 200px` to `widthMode: '25'`
3. **Verify:**
   - 4 cards fit in one row on desktop (25% each with gap)
   - Cards maintain 25% width on mobile too
   - Horizontal scroll works when >4 cards in nowrap row
4. **Create new test:** 25%/75% column split
5. **Verify:** Both columns fit side-by-side with gap
6. **Regression:** Ensure image widthMode still works correctly

---

## Implementation Order

1. **Phase 1:** layout-column widthMode (user's request)
2. **Phase 2:** button widthMode
3. **Phase 3:** carousel, video widthMode
4. **Phase 4:** Refactor text components to CSS-based approach (optional)

---

## Sources

- [Bootstrap 5 Grid System](https://getbootstrap.com/docs/5.0/layout/grid/) - Industry standard 12-column grid
- [CSS Grid Layout Guide | CSS-Tricks](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [MDN Grid Template Columns](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/grid-template-columns)
- [Why Bootstrap Uses 12 Columns](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/why-12-column-bootstrap-grid-system-60-seconds-360-circle)

---

**Last Updated:** January 28, 2025
