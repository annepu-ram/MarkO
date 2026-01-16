# ColumnsGrid Layout Bug Report

**Date**: 2025-01-11
**Component**: `columnsgrid`
**Severity**: High
**Status**: Open

---

## Summary

The `columnsgrid` component is not rendering columns properly. It currently creates equal-width flexible columns that don't respect the column count specified in properties, and lacks responsive behavior for mobile devices.

---

## Current Behavior

### Desktop/Medium+ Screens
- All columns are rendered with `flex-grow: 1` (via `.col-sm` class)
- This makes all columns equal width **regardless** of the column count
- A 3-column grid appears correct by coincidence, but breaks with different column counts
- A 4-column grid would still show equal widths instead of 25% each

### Mobile Screens
- Columns remain side-by-side in a horizontal row
- Content becomes cramped and unreadable
- No responsive behavior to stack columns vertically

### CSS Implementation
```css
/* Current implementation in css/components.css:315-319 */
.col-sm {
    flex-grow: 1;
    padding: 0 1rem;
    box-sizing: border-box;
}
```

### Renderer Implementation
```javascript
// Current implementation in js/render/index.js:683
contentHTML += `<div class="col-sm" style="position: relative;">`;
```

**Problems:**
1. `col-sm` class applies to ALL columns regardless of grid size
2. No width calculation based on `columnCount`
3. No responsive classes for mobile breakpoints
4. CSS has no media queries for mobile stacking

---

## Expected Behavior

### Desktop/Medium+ Screens (768px+)
- Each column should have width = `100% / columnCount`
- 3-column grid: each column = ~33.33% width
- 4-column grid: each column = 25% width
- 2-column grid: each column = 50% width

### Mobile Screens (<768px)
- All columns should stack vertically (100% width each)
- Provides readable content on small screens
- Follows responsive design best practices

---

## Test Case

### Example: Bakery Template (3-column grid)

**YAML Configuration:**
```yaml
- name: columnsgrid
  properties:
    layout:
      columns: 3
      gap: md
  columns:
  - components:
    - name: image
      properties:
        source:
          url: https://images.pexels.com/photos/380954/...
    - name: heading
    - name: paragraph
  - components:
    - name: image
    # ... (column 2)
  - components:
    - name: image
    # ... (column 3)
```

**Current Output:**
- Desktop: Shows 3 columns (works by coincidence with flex-grow)
- Mobile: Shows 3 cramped columns side-by-side (broken)

**Expected Output:**
- Desktop: Shows 3 columns at 33.33% width each
- Mobile: Shows 3 stacked columns at 100% width each

---

## Root Causes

### 1. No Width Calculation
The renderer doesn't apply column-specific width based on `columnCount`:
```javascript
// js/render/index.js:675
const columnCount = parseInt(getNestedValue(properties, ['layout', 'columns'])) || 2;

// js/render/index.js:683 - Missing width calculation
contentHTML += `<div class="col-sm" style="position: relative;">`;
// Should calculate: width: ${100 / columnCount}%
```

### 2. No Responsive CSS
The `.col-sm` class has no responsive behavior:
```css
/* css/components.css - Missing media queries */
.col-sm {
    flex-grow: 1;  /* ❌ Equal width by flex, not by column count */
    padding: 0 1rem;
    box-sizing: border-box;
    /* ❌ Missing: width, min-width, or flex-basis */
}

/* ❌ Missing mobile breakpoint */
@media (max-width: 767px) {
    .col-sm {
        width: 100%;
        /* Stack vertically */
    }
}
```

---

## Proposed Solution

### Option A: Inline Width Styles (Recommended)
Calculate and apply width directly in the renderer:

**Renderer Update** ([js/render/index.js:673-706](js/render/index.js#L673-706)):
```javascript
function renderColumnsGrid(component, path, mode) {
    const { properties = {}, columns = [] } = component;
    const columnCount = parseInt(getNestedValue(properties, ['layout', 'columns'])) || 2;
    const columnWidth = 100 / columnCount;

    let contentHTML = `<div class="row">`;

    for (let i = 0; i < columnCount; i++) {
        const columnComponents = columns[i] ? columns[i].components || [] : [];
        const columnPath = [...path, 'columns', i, 'components'];

        // Apply calculated width with responsive behavior
        contentHTML += `<div class="col" style="position: relative; width: ${columnWidth}%; flex: 0 0 ${columnWidth}%; padding: 0 1rem; box-sizing: border-box;">`;

        if (mode === 'preview') {
            contentHTML += `<div class="column-label">Col ${i + 1}</div>`;
        }

        if (columnComponents.length > 0) {
            contentHTML += renderComponentsList(columnComponents, columnPath, mode);
        } else if (mode === 'preview') {
            contentHTML += '<div class="column-placeholder">Drop components here...</div>';
        }

        contentHTML += '</div>';
    }

    contentHTML += '</div>';
    // ... rest of function
}
```

**CSS Update** ([css/components.css:308-319](css/components.css#L308-319)):
```css
/* --- Grid System --- */
.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -1rem;
}

.col {
    padding: 0 1rem;
    box-sizing: border-box;
}

/* Mobile responsive: stack columns */
@media (max-width: 767px) {
    .col {
        width: 100% !important;
        flex: 0 0 100% !important;
    }
}
```

### Option B: CSS Classes (More Complex)
Create responsive CSS classes like Bootstrap:
- `.col-md-4` (33.33% on medium+)
- `.col-sm-12` (100% on small)

**Note**: This requires more extensive changes to both renderer and CSS.

---

## Impact Assessment

### Affected Components
- `columnsgrid` component (all instances)

### Affected Templates
- [bakery_template.yaml](example_templates/bakery_template.yaml#L67) - 3 columns
- [car_dealer_template.yaml](example_templates/car_dealer_template.yaml#L71) - 2 columns
- [logistics_template.yaml](example_templates/logistics_template.yaml#L78) - 3 columns
- Any user-created columnsgrid layouts

### Breaking Changes
- ✅ None - This is a bug fix that improves existing behavior
- ✅ Existing 3-column grids will look the same on desktop
- ✅ Mobile behavior will improve (columns now stack)

---

## Testing Checklist

### Desktop (>768px)
- [ ] 2-column grid shows 50% width columns
- [ ] 3-column grid shows ~33.33% width columns
- [ ] 4-column grid shows 25% width columns
- [ ] Gap spacing is applied correctly
- [ ] Images render properly in columns
- [ ] Chrome overlay doesn't interfere

### Mobile (<768px)
- [ ] All columns stack vertically (100% width)
- [ ] Content is readable on small screens
- [ ] Gap spacing is maintained
- [ ] No horizontal scrolling
- [ ] Images scale properly

### Edge Cases
- [ ] Empty columns render placeholder (preview mode)
- [ ] Single column grid (100% width)
- [ ] Nested components render correctly
- [ ] Export mode produces clean HTML

---

## Related Issues

- Fixed image/gif component style overwrite bug (prevents columnsgrid layout)
- Chrome zero-wrapper approach (ensures components participate in flex context)

---

## Priority

**HIGH** - This affects a fundamental layout component used across multiple templates and breaks mobile responsiveness entirely.

---

## Implementation Notes

1. **Phase 1**: Fix desktop column widths with inline styles
2. **Phase 2**: Add mobile responsive CSS
3. **Phase 3**: Test across all example templates
4. **Phase 4**: Update documentation in CLAUDE.md

---

## Additional Considerations

### Gap Property
The `layout.gap` property is defined but may not be properly applied. Verify that gap spacing uses the design token system correctly.

### Responsive Breakpoints
Consider adding responsive configuration to component schema:
```yaml
columnsgrid:
  layout:
    columns: 4        # Desktop
  responsive:
    breakpoints:
      md: 2          # Tablet
      sm: 1          # Mobile
```

This would allow fine-grained control over responsive behavior (already present in component_defaults.yaml but not used in renderer).

---

**Files to Modify:**
1. [js/render/index.js](js/render/index.js#L673-706) - Add width calculation
2. [css/components.css](css/components.css#L308-319) - Add responsive styles
3. Test files - Update/add columnsgrid tests
4. [CLAUDE.md](CLAUDE.md) - Document columnsgrid responsive behavior
