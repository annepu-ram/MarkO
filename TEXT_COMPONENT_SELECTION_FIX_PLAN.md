# Text Component Selection Fix Plan

## Problem Analysis

Text components are not selectable in the SSR app, despite having the correct attributes and classes. The issue is caused by CSS conflicts between the width mode implementation and the selection system.

## Root Causes

### 1. **Inline Style Conflicts**
Text components have inline styles added in two places:
- Width mode styles: `display: inline-block; flex: ...; width: ...;`
- Selection styles: `position: relative;`

The styles are concatenated as a string, which creates this pattern:
```html
style="display: inline-block; box-sizing: border-box; width: 100%; flex: 1 1 100%; position: relative;"
```

Problem: The `position: relative` is being added AFTER all other styles, which is correct, but the combination of `display: inline-block` with `position: relative` can cause issues with click detection and pseudo-element positioning.

### 2. **Link Component Wrapper Issue**
The link component has a special structure:
```html
<div style="text-align: left;">
    <a class="chrome-target" data-component-id="comp_0">Link text</a>
</div>
```

The wrapper `<div>` doesn't have:
- `chrome-target` class
- `data-component-id` attribute
- `position: relative`

This means:
- Clicking the padding around the link won't select it
- The chrome border won't extend to the full width

### 3. **Inline-Block Display Issues**
`display: inline-block` can cause these issues:
- Click events might not register on the full element area
- The `::before` pseudo-element (used for selection border) might not cover the full area
- Whitespace around inline-block elements can cause confusion

### 4. **Position: Relative Placement**
Currently, `position: relative` is added as an inline style at the end:
```jinja2
style="{{ styles }} position: relative;"
```

This approach:
- Is inconsistent (not part of the `styles` array)
- Might be overridden if styles end with a semicolon
- Makes the code harder to maintain

## Solution Strategy

### Phase 1: Move Position Relative to Build Styles ✅
**Goal:** Make `position: relative` part of the computed styles, not a tacked-on inline style.

**Implementation:**
- Add `position: relative` to the `styles` array in `build_styles()` macro
- Apply it to ALL components that need selection (not just text components)
- Remove the inline `position: relative;` from all component templates

**Benefits:**
- Cleaner code
- Consistent style application
- Easier to debug

### Phase 2: Fix Link Component Wrapper ✅
**Goal:** Make the entire link area selectable, not just the `<a>` tag.

**Options:**

**Option A: Add attributes to wrapper div**
```jinja2
<div class="chrome-target" data-component-id="{{ component_id }}" style="text-align: {{ text_align }}; {{ styles }}">
    <a href="..." class="link">{{ text }}</a>
</div>
```
- Pros: Full width selectable
- Cons: Chrome border on div, not link

**Option B: Remove wrapper, use CSS for alignment**
```jinja2
<a href="..." class="link chrome-target" data-component-id="{{ component_id }}" style="{{ link_styles }} text-align: {{ text_align }};">{{ text }}</a>
```
- Pros: Simpler structure
- Cons: Text-align on inline element (doesn't work)

**Option C: Keep wrapper, but make it part of the component (RECOMMENDED)**
```jinja2
<div class="link-wrapper chrome-target" data-component-id="{{ component_id }}" style="{{ styles }} text-align: {{ text_align }};">
    <a href="..." class="link {{ 'link-arrow' if showArrow }}">{{ text }}</a>
</div>
```
- Pros: Clean separation, full width selectable, proper alignment
- Cons: Need to adjust width mode to account for wrapper

### Phase 3: Ensure Display Property Doesn't Break Selection ✅
**Goal:** Make sure inline-block and other display modes work with selection.

**Implementation:**
- Keep `display: inline-block` for text components (needed for width modes)
- Ensure `position: relative` is applied
- Verify `::before` pseudo-element uses correct positioning

**CSS to verify:**
```css
.chrome-target {
    position: relative; /* Should be in inline styles now */
    box-sizing: border-box;
    cursor: pointer;
}

.chrome-target::before {
    content: '';
    position: absolute;
    inset: -2px; /* Should work with inline-block + relative */
    border: 2px dashed var(--color-secondary);
    pointer-events: none; /* Critical - allows clicks through */
    opacity: 0;
    transition: opacity 0.2s;
}
```

### Phase 4: Add Width Mode to Link Wrapper ✅
**Goal:** Make width modes work correctly for link components.

**Implementation:**
Since link now uses a wrapper div:
- Apply width mode styles to the wrapper, not the `<a>` tag
- Move `link_styles` (underline, etc.) to the `<a>` tag only
- Keep `styles` (width mode, etc.) on the wrapper

## Implementation Steps

### Step 1: Add Position Relative to Build Styles
**File:** `ssr_python/templates/macros/_components.html` - `build_styles()` macro

**Before:**
```jinja2
{{ styles | join(' ') }}
```

**After:**
```jinja2
{# Always add position relative for selection to work #}
{% set _ = styles.append('position: relative;') %}
{{ styles | join(' ') }}
```

**Affected Components:** ALL components (ensures consistent selection behavior)

### Step 2: Remove Inline Position Relative
**File:** `ssr_python/templates/macros/_components.html` - `render_text_component()` macro

**Before:**
```jinja2
<h{{ level }} class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }} position: relative;"{% else %} style="position: relative;"{% endif %}>
```

**After:**
```jinja2
<h{{ level }} class="chrome-target" data-component-id="{{ component_id }}"{% if styles %} style="{{ styles }}"{% endif %}>
```

**Apply to:**
- heading
- paragraph
- eyebrow
- caption
- blockquote
- All other components that have inline `position: relative;`

### Step 3: Fix Link Component Structure
**File:** `ssr_python/templates/macros/_components.html` - link section in `render_text_component()`

**Before:**
```jinja2
<div style="text-align: {{ text_align }};">
    <a href="{{ href }}" class="{{ classes | join(' ') }}" data-component-id="{{ component_id }}" style="{{ link_styles }} position: relative;">{{ text }}</a>
</div>
```

**After:**
```jinja2
{# Apply width mode and selection to wrapper div #}
<div class="link-wrapper chrome-target" data-component-id="{{ component_id }}" style="{{ styles }} text-align: {{ text_align }};">
    {# Apply link-specific styles (underline) to the anchor #}
    <a href="{{ href }}" class="link {% if showArrow %}link-arrow{% endif %}" style="{% if underline %}text-decoration: underline;{% else %}text-decoration: none;{% endif %}">{{ text }}</a>
</div>
```

**Changes:**
- Wrapper gets: `chrome-target`, `data-component-id`, `styles` (width mode), text-align
- Anchor gets: `link` class, arrow class, underline style only
- Cleaner separation of concerns

### Step 4: Update Link CSS (if needed)
**File:** `ssr_python/static/css/components.css`

Add wrapper styles:
```css
.link-wrapper {
    /* Ensures proper click area */
    display: inline-block;
}

.link-wrapper a.link {
    /* Link inherits most properties from parent */
    color: inherit;
}
```

## Testing Checklist

### Text Components
- [ ] Heading: Click to select, verify properties panel shows
- [ ] Paragraph: Click to select, verify properties panel shows
- [ ] Eyebrow: Click to select, verify properties panel shows
- [ ] Caption: Click to select, verify properties panel shows
- [ ] Blockquote: Click figure, verify selection
- [ ] Link: Click anywhere in link area, verify selection

### Width Modes (All text components)
- [ ] Fit mode: Still works after selection fix
- [ ] 25% mode: Still works after selection fix
- [ ] 50% mode: Still works after selection fix
- [ ] 75% mode: Still works after selection fix
- [ ] Stretch mode: Still works after selection fix

### Selection Behavior
- [ ] Chrome border appears on hover
- [ ] Chrome border turns red when selected
- [ ] Properties panel updates when component is selected
- [ ] Selection persists after YAML re-render
- [ ] Clicking outside clears selection

### Edge Cases
- [ ] Multiline text components are fully selectable
- [ ] Components in flex containers are selectable
- [ ] Nested components (blockquote in layout) are selectable
- [ ] Link wrapper area (padding) is selectable

## Potential Issues & Solutions

### Issue 1: Inline-block causes selection gaps
**Symptom:** Clicking between components doesn't select anything
**Solution:** This is expected behavior - only click on the component itself

### Issue 2: Text alignment breaks in links
**Symptom:** Center/right alignment doesn't work
**Solution:** The wrapper div handles alignment, links inherit it

### Issue 3: Width modes don't apply to links
**Symptom:** Link width mode properties don't work
**Solution:** Width mode applies to wrapper, which is correct

### Issue 4: Chrome border doesn't match link width
**Symptom:** Border is too narrow or too wide
**Solution:** Border is on wrapper, which includes padding - this is correct

## Summary

**Root Cause:** Mixing inline style addition with computed styles, and link wrapper missing selection attributes.

**Fix Strategy:**
1. Consolidate `position: relative` into `build_styles()`
2. Remove redundant inline `position: relative;`
3. Move link selection attributes to wrapper
4. Separate link-specific styles from width mode styles

**Expected Outcome:**
- All text components are selectable
- Width modes continue to work correctly
- Cleaner, more maintainable code
- Consistent selection behavior across all components

**Files to Modify:**
1. `ssr_python/templates/macros/_components.html` - Build styles & text components
2. `ssr_python/static/css/components.css` - Link wrapper styles (optional)

**Risk Level:** LOW
- Changes are localized
- Width mode logic is untouched
- Only moving where `position: relative` is applied
- Link wrapper change is isolated

