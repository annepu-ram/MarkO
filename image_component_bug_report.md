# Image Component Comprehensive Implementation Plan

## Executive Summary
The image component has multiple architectural and functional issues that prevent it from working consistently with other components. This document consolidates findings on schema gaps, container layout problems, and architectural inconsistencies, providing a comprehensive implementation plan.

## Critical Issues Overview

### Issue 1: Schema Gap - Missing Properties
Background images and appearance properties are not exposed in the properties panel, even though rendering logic supports them.

### Issue 2: Container Layout Incompatibility
The image component container uses `display: block` by default, making it incompatible with flexbox layouts and preventing images from sitting side-by-side with text components.

### Issue 3: Architectural Inconsistency
Image component uses custom rendering logic instead of the modern `renderSimpleComponent()` → `generateComponentInnerHTML()` pattern, causing feature gaps and maintenance burden.

## Component Analysis

### Current Schema (`component_schemas.yaml` lines 828-862)
```yaml
image:
  groups:
  - id: source
    label: Source
    fields:
    - path: source.url
      type: text
      label: Image URL
    - path: source.altText
      type: text
      label: Alt Text
  - id: presentation
    label: Presentation
    fields:
    - path: presentation.height
      type: text
      label: Height (px or auto)
    - path: presentation.fit
      type: select
      label: Object Fit
      options:
      - cover
      - contain
      - fill
      - none
    - path: presentation.cornerStyle
      type: select
      label: Corners
      tokens: borderRadiusScale
  - id: overlay
    label: Overlay
    fields:
    - path: overlay.enabled
      type: checkbox
      label: Enable Overlay
```

**Missing:** No `background` group or appearance settings for the container

### Current Render Logic (`js/render/index.js` lines 636-664)
```javascript
function renderImageComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const src = getNestedValue(properties, ['source', 'url']);
    const alt = getNestedValue(properties, ['source', 'altText']);
    const height = getNestedValue(properties, ['presentation', 'height']);
    const link = properties.link;
    const styles = generateRemainingStyles(properties);  // Line 642: calls generateRemainingStyles
    let imageHTML = `<img src="${src || 'https://via.placeholder.com'}" alt="${alt || ''}" style="width: 100%; height: ${toRem(height) || 'auto'}; object-fit: cover;">`;
    if (link) {
        imageHTML = `<a href="${link}">${imageHTML}</a>`;
    }
    let nestedComponentsHTML = '';
    if (components.length > 0) {
        const componentsPath = [...path, 'components'];
        nestedComponentsHTML = renderComponentsList(components, componentsPath, mode);
    }
    const contentHTML = `<div class="image-component-container" style="${styles}">  /* Line 652: styles applied here */
        ${imageHTML}
        <div class="image-nested-components">
            ${nestedComponentsHTML}
        </div>
    </div>`;
    if (mode === 'preview') {
        const componentId = `comp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        registerComponentPath(componentId, path);
        return wrapComponentWithChrome(componentId, 'image', contentHTML, getComponentDepth(path));
    }
    return contentHTML;
}
```

**Current Behavior:**
- Line 642 calls `generateRemainingStyles(properties)` which DOES support background images
- Line 652 applies these styles to `.image-component-container` div
- However, there's no UI in the properties panel to configure background settings

### `generateRemainingStyles` Support
The `generateRemainingStyles` function (lines 1136-1239) DOES support background images:

```javascript
const backgroundGroup = props.background || appearance.background || {};
const backgroundImage = backgroundGroup.image || props.backgroundImage;
const backgroundColor = backgroundGroup.color || props.backgroundColor;
if (backgroundImage) {
    styles += `background-image: url('${backgroundImage}');`;
    styles += 'background-size: cover;';
    styles += 'background-position: center;';
} else if (backgroundColor) {
    styles += `background-color: ${backgroundColor};`;
}
```

## Root Cause

### Primary Issue: Schema Gap
The image component's schema is **missing** the background/appearance group in the properties panel. Users cannot configure:
- `background.color` - Container background color
- `background.image` - Container background image
- `appearance.radius` - Border radius for the container
- `appearance.padding` - Padding inside the container

The render logic supports these properties, but they are not exposed in the UI.

### Secondary Issue: Architectural Inconsistency
**The image component rendering logic is outdated and doesn't follow the modern component rendering pattern used by text components.**

**Current Image Component Approach:**
- Uses custom `renderImageComponent()` function with hardcoded HTML structure
- Manually constructs `<img>` tags with inline styles
- Manually wraps in `.image-component-container` div
- Does NOT use `generateComponentInnerHTML()`
- Does NOT respect `component_defaults.yaml` classes
- Manually handles link wrapping

**Modern Text Component Approach:**
- Uses `renderSimpleComponent()` which calls `generateComponentInnerHTML()`
- `generateComponentInnerHTML()` merges default classes from `component_defaults.yaml`
- Applies styles systematically through `generateRemainingStyles()`
- Handles spacing (padding/margin with logical properties)
- Respects width modes (fit/percentage/stretch)
- Centralized styling logic

**Consequences:**
1. **Inconsistent behavior:** Image components don't get the same layout features (width modes, spacing) as text components
2. **Maintenance burden:** Image-specific rendering code duplicates logic from `generateComponentInnerHTML()`
3. **Feature gaps:** Properties like `overlay.enabled` are defined in schema but not implemented in the custom renderer
4. **Missing features:** No width mode support, inconsistent spacing application

**Example: Overlay Property**
- Defined in [component_schemas.yaml:857-862](component_schemas.yaml#L857)
- Has default value in [component_defaults.yaml:242](component_defaults.yaml#L242)
- **Never read or applied** in `renderImageComponent()` at [js/render/index.js:636-664](js/render/index.js#L636)

### Tertiary Issue: Container Layout Problems
**The image component's root container is incompatible with flexbox layouts used throughout the application.**

#### Current Container Structure
**HTML:**
```html
<div class="image-component-container" style="[styles from generateRemainingStyles]">
    <img src="..." alt="..." style="width: 100%; height: auto; object-fit: cover;">
    <div class="image-nested-components">
        [nested components like overlays/captions]
    </div>
</div>
```

**CSS:**
```css
.image-component-container {
    position: relative;  /* Only positioning, no layout system */
}

.image-nested-components {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: stretch;
    padding: 1rem;
    box-sizing: border-box;
}
```

Source: [css/components.css:252-268](css/components.css#L252)

#### Container Type: Neither Grid nor Flexbox
The `.image-component-container` has:
- **`position: relative`** - Only positioning context, no layout system
- **No `display: flex` or `display: grid`** on the container
- **Inherits `display: block`** - Takes full width, forces line breaks
- **No width mode support** - Unlike text components (fit/percentage/stretch)

#### Comparison: Text vs Image Components

**Text Components (heading, paragraph):**
```html
<h2 style="display: inline-block; width: auto; flex: 0 0 auto;">Text</h2>
```
- `display: inline-block` with width modes
- Direct flex participation via `flex: 0 0 auto` or `flex-grow: 1`
- No wrapper divs - component IS the flex item
- Spacing applied directly (logical properties)

**Image Components:**
```html
<div class="image-component-container" style="[no display or flex properties]">
    <img style="width: 100%; ...">
</div>
```
- No display mode specified (defaults to `block`)
- No flex participation
- Wrapper div takes full width
- No width mode options

#### Real-World Layout Failures

**Example 1: Hero Section (Image + Text Side-by-Side)**
```yaml
- name: layout-row
  properties:
    layout:
      gap: 2rem
      align: center
  components:
    - name: image
      properties:
        source:
          url: hero.jpg
        layout:
          widthMode: percentage  # ❌ NOT SUPPORTED
          width: 40%
    - name: layout-column
      components:
        - name: heading
          properties:
            text: Welcome
        - name: paragraph
          properties:
            text: Description
```

**Current behavior:** Image takes full row width, text wraps below

**Expected behavior:** Image takes 40% width, text column takes remaining space

**Example 2: Inline Gallery**
```yaml
- name: layout-row
  properties:
    layout:
      gap: 1rem
      justify: space-between
  components:
    - name: image
      properties:
        layout:
          widthMode: fit  # ❌ NOT SUPPORTED
    - name: image
    - name: image
```

**Current behavior:** Each image takes full row, stacks vertically

**Expected behavior:** Images sit side-by-side in a row, each at intrinsic width

**Example 3: Mixed Content Row**
```yaml
- name: layout-row
  components:
    - name: heading        # flex item with flex: 0 0 auto ✓
    - name: image          # block element, takes full width ❌
    - name: paragraph      # flex item with flex: 0 0 auto ✓
```

**Result:**
- Text components flow inline as flex items
- Image component forces line break due to `display: block`
- Breaks intended horizontal layout

## Impact

### Severity Analysis
- **Issue 1 (Schema Gap):** Medium - Limits design flexibility
- **Issue 2 (Container Layout):** High - Breaks fundamental layout patterns
- **Issue 3 (Architecture):** High - Technical debt affecting maintainability

### User Impact
1. **Layout limitations:** Cannot create side-by-side layouts with images and text
2. **Missing properties:** Cannot configure background colors/images, spacing, width modes
3. **Inconsistent behavior:** Images don't work like other components
4. **Complex workarounds:** Must nest images in extra layout containers

### Workarounds
- Wrap image components in layout containers to control width
- Use nested layout-columns to fake side-by-side layouts
- Manual CSS overrides (not exposed in YAML)

## Proposed Solutions

### Decision Matrix

| Solution | Schema Gap | Layout Issues | Architecture | Effort | Risk |
|----------|-----------|---------------|--------------|--------|------|
| **Option A** | ✓ Partial | ✓ Partial | ❌ No | Low | Low |
| **Option B** | ✓ Full | ✓ Full | ✓ Full | High | Medium |

### Option A: Quick Fix (Minimal Changes)
This addresses the immediate issues with minimal changes but doesn't solve the underlying architectural problems.

#### A1. Fix Container Display Mode
**Update CSS** in `css/components.css`:
```css
.image-component-container {
    position: relative;
    display: inline-block;  /* ADD: Allow flex participation */
    box-sizing: border-box; /* ADD: Proper box model */
}
```

#### A2. Add Width Mode Support
**Update `renderImageComponent()`** in `js/render/index.js`:
```javascript
function renderImageComponent(component, path, mode) {
    const { properties = {}, components = [] } = component;
    const src = getNestedValue(properties, ['source', 'url']);
    const alt = getNestedValue(properties, ['source', 'altText']);
    const height = getNestedValue(properties, ['presentation', 'height']);
    const link = properties.link;

    // ADD: Width mode support
    const widthMode = getNestedValue(properties, ['layout', 'widthMode']) || 'stretch';
    const widthRule = getWidthModeRule(widthMode);

    let styles = generateRemainingStyles(properties);

    // ADD: Apply width mode styles
    styles += ' display: inline-block; box-sizing: border-box;';
    styles += ' ' + widthRule.component;
    if (Array.isArray(widthRule.flex)) {
        styles += ' ' + widthRule.flex.join(' ');
    }

    // ... rest of function
}
```

#### A3. Add Schema Groups
**Add to `component_schemas.yaml`** after the `overlay` group:

```yaml
  - id: layout
    label: Layout
    fields:
    - path: layout.widthMode
      type: select
      label: Width Mode
      options:
        - fit
        - percentage
        - stretch
    - path: layout.width
      type: text
      label: Width (when percentage mode)
  - id: appearance
    label: Appearance
    fields:
    - path: background.color
      type: color
      label: Background Color
    - path: background.image
      type: text
      label: Background Image URL
    - path: appearance.radius
      type: select
      label: Border Radius
      tokens: borderRadiusScale
    - path: appearance.padding.block
      type: select
      label: Padding (Top & Bottom)
      tokens: spacingScale
    - path: appearance.padding.inline
      type: select
      label: Padding (Left & Right)
      tokens: spacingScale
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top & Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left & Right)
      tokens: spacingScale
```

#### A4. Update Component Defaults
**Add to `component_defaults.yaml`:**

```yaml
image:
  source:
    url: https://via.placeholder.com/150
    altText: Placeholder image
  presentation:
    height: auto
    fit: cover
    cornerStyle: none
  overlay:
    enabled: false
  layout:                # ADD THIS
    widthMode: stretch
    width: 100%
  spacing:               # ADD THIS
    marginBlock: none
    marginInline: none
  background:            # ADD THIS
    color: transparent
    image: ''
  appearance:            # ADD THIS
    radius: none
    padding:
      block: none
      inline: none
```

#### Option A Summary
**Pros:**
- Minimal code changes
- Low risk of breaking existing functionality
- Preserves nested components architecture
- Quick to implement and test

**Cons:**
- Maintains separate rendering pipeline (technical debt persists)
- Duplicates width mode logic from text components
- Still doesn't use modern `generateComponentInnerHTML()` pattern
- `cornerStyle` and `overlay.enabled` still not implemented

**Files to modify:**
1. `css/components.css` - Update `.image-component-container` display mode
2. `js/render/index.js` - Add width mode logic to `renderImageComponent()`
3. `component_schemas.yaml` - Add layout, appearance, spacing groups
4. `component_defaults.yaml` - Add new property defaults

### Option B: Full Refactor (Recommended)
**Refactor the image component to follow the modern rendering pattern used by text components.**

#### Benefits:
- **Architectural consistency:** All components use the same rendering pipeline
- **Automatic features:** Width modes, spacing, and all standard properties work automatically
- **Less code:** Remove custom rendering logic, reduce maintenance burden
- **Feature completeness:** `overlay.enabled`, `cornerStyle`, and all schema properties work immediately
- **Future-proof:** New universal features automatically apply to images

#### Implementation Steps:

**B1. Add Image Support to `generateComponentInnerHTML()`**

In `js/render/index.js`, add image handling inside `generateComponentInnerHTML()`:

```javascript
export function generateComponentInnerHTML(type, props, classes, styleAttr, mode) {
    // ... existing code ...

    if (componentType === 'image') {
        const src = getNestedValue(componentProps, ['source', 'url']) || 'https://via.placeholder.com';
        const alt = getNestedValue(componentProps, ['source', 'altText']) || '';
        const height = getNestedValue(componentProps, ['presentation', 'height']);
        const fit = getNestedValue(componentProps, ['presentation', 'fit']) || 'cover';
        const cornerStyle = getNestedValue(componentProps, ['presentation', 'cornerStyle']);

        let imgStyles = `width: 100%; height: ${toRem(height) || 'auto'}; object-fit: ${fit};`;

        // Apply cornerStyle to the <img> element
        if (cornerStyle) {
            const radius = resolveBorderRadiusToken(cornerStyle);
            if (radius) {
                imgStyles += ` border-radius: ${radius};`;
            }
        }

        const link = componentProps.link;
        let imageHTML = `<img src="${src}" alt="${alt}" style="${imgStyles}">`;

        if (link) {
            imageHTML = `<a href="${link}">${imageHTML}</a>`;
        }

        // Handle overlay
        const overlayEnabled = getNestedValue(componentProps, ['overlay', 'enabled']);
        if (overlayEnabled) {
            const overlayColor = getNestedValue(componentProps, ['overlay', 'color']) || 'rgba(0,0,0,0.5)';
            const overlayOpacity = getNestedValue(componentProps, ['overlay', 'opacity']) || '0.5';
            imageHTML += `<div class="image-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: ${overlayColor}; opacity: ${overlayOpacity}; pointer-events: none;"></div>`;
        }

        return `<div${attrSegment} style="position: relative;">${imageHTML}</div>`;
    }

    // ... existing code for other components ...
}
```

**B2. Add Image to Width Mode Components**

Update the constant at the top of `js/render/index.js`:

```javascript
const TEXT_COMPONENTS_WITH_WIDTH_MODE = new Set([
    'heading',
    'paragraph',
    'eyebrow',
    'caption',
    'blockquote',
    'image'  // ADD THIS
]);
```

**B3. Update Component Switch to Use `renderSimpleComponent()`**

In the `renderComponent()` switch statement:

```javascript
switch (name) {
    // ... other cases ...
    case 'image':
        return renderSimpleComponent(component, path, mode);  // CHANGE: was renderImageComponent
    // ... other cases ...
}
```

**B4. Handle Nested Components (for overlays/captions)**

**Option B4a:** Keep nested components support by checking in `renderSimpleComponent()`:

```javascript
export function renderSimpleComponent(component, path, mode) {
    const { name, properties = {}, components = [] } = component;
    const styles = generateRemainingStyles(properties, name);
    let componentHTML = generateComponentInnerHTML(name, properties, '', styles, mode);

    // Handle nested components for image (for overlays/captions)
    if (name === 'image' && components.length > 0) {
        const componentsPath = [...path, 'components'];
        const nestedHTML = renderComponentsList(components, componentsPath, mode);
        // Inject nested components before closing div
        componentHTML = componentHTML.replace('</div>', `<div class="image-nested-components">${nestedHTML}</div></div>`);
    }

    // ... rest of function ...
}
```

**B5. Update Schema**

Add to `component_schemas.yaml`:

```yaml
image:
  groups:
  - id: source
    # ... existing source fields ...
  - id: presentation
    # ... existing presentation fields ...
  - id: layout               # ADD THIS
    label: Layout
    fields:
    - path: layout.widthMode
      type: select
      label: Width Mode
      options:
        - fit
        - percentage
        - stretch
    - path: layout.width
      type: text
      label: Width (when percentage mode)
  - id: spacing              # ADD THIS
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top & Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left & Right)
      tokens: spacingScale
    - path: appearance.padding.block
      type: select
      label: Padding (Top & Bottom)
      tokens: spacingScale
    - path: appearance.padding.inline
      type: select
      label: Padding (Left & Right)
      tokens: spacingScale
  - id: overlay              # ENHANCE THIS
    label: Overlay
    fields:
    - path: overlay.enabled
      type: checkbox
      label: Enable Overlay
    - path: overlay.color
      type: color
      label: Overlay Color
    - path: overlay.opacity
      type: text
      label: Overlay Opacity (0-1)
  - id: appearance           # ADD THIS
    label: Appearance
    fields:
    - path: background.color
      type: color
      label: Background Color
    - path: background.image
      type: text
      label: Background Image URL
    - path: appearance.radius
      type: select
      label: Border Radius
      tokens: borderRadiusScale
```

**B6. Update Defaults**

Update `component_defaults.yaml`:

```yaml
image:
  source:
    url: https://via.placeholder.com/150
    altText: Placeholder image
  presentation:
    height: auto
    fit: cover
    cornerStyle: none
  layout:
    widthMode: stretch
    width: 100%
  spacing:
    marginBlock: none
    marginInline: none
  overlay:
    enabled: false
    color: rgba(0,0,0,0.5)
    opacity: 0.5
  background:
    color: transparent
    image: ''
  appearance:
    radius: none
    padding:
      block: none
      inline: none
```

**B7. Remove Old Rendering Function**

Delete the `renderImageComponent()` function from `js/render/index.js` (lines 636-664).

**B8. Update CSS**

Remove or update `.image-component-container` in `css/components.css` since it's no longer used:

```css
/* Image overlay for nested components */
.image-nested-components {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: stretch;
    padding: 1rem;
    box-sizing: border-box;
    pointer-events: none;
}

.image-nested-components > * {
    pointer-events: auto;
}
```

#### Option B Summary
**Pros:**
- Full architectural consistency with text components
- All features work automatically (width modes, spacing, overlay, cornerStyle)
- Less code to maintain (remove ~30 lines, add ~20)
- Future features automatically apply to images
- Cleaner, more maintainable codebase

**Cons:**
- More extensive refactoring required
- Need careful testing of nested components
- Medium risk of breaking existing image usage
- Requires understanding of rendering pipeline

**Files to modify:**
1. `js/render/index.js` - Add image to `generateComponentInnerHTML()`, update switch, remove `renderImageComponent()`
2. `component_schemas.yaml` - Add layout, spacing, appearance, enhanced overlay groups
3. `component_defaults.yaml` - Add full modern structure
4. `css/components.css` - Update/remove `.image-component-container` styles
5. Tests - Update image component snapshot tests

## Additional Notes & Context
- The `generateRemainingStyles()` function already handles `appearance.padding` with `block`/`inline` structure (added recently for text components)
- Border radius resolution via `resolveBorderRadiusToken()` is already in place
- Width mode infrastructure (`TEXT_COMPONENTS_WITH_WIDTH_MODE`, `getWidthModeRule()`) is established and working for text components
- Chrome wrapping system supports any component type - no special handling needed for images
- **Option A requires minimal changes** - Quick fix for immediate layout issues
- **Option B is the proper architectural fix** - Aligns image component with modern rendering patterns and eliminates technical debt

## Testing Checklist

### Option A (Quick Fix):
- [ ] Images participate in flexbox layouts correctly (side-by-side with text)
- [ ] Width mode `fit` works (image shrinks to intrinsic size)
- [ ] Width mode `percentage` works (image takes specified width)
- [ ] Width mode `stretch` works (image fills available space)
- [ ] Background color applies to container
- [ ] Background image applies to container
- [ ] Border radius applies to container
- [ ] Padding (block/inline) applies to container
- [ ] Margin (block/inline) applies to container
- [ ] Nested components render correctly
- [ ] Test in both preview and export modes
- [ ] Chrome interaction works correctly
- [ ] Test all layout examples (hero section, inline gallery, mixed content row)

### Option B (Full Refactor):
- [ ] Image renders correctly through `generateComponentInnerHTML()`
- [ ] All width modes (fit/percentage/stretch) work for images
- [ ] Images participate correctly in flex layouts with text components
- [ ] Spacing properties (margin/padding with logical properties) apply correctly
- [ ] `cornerStyle` applies border-radius to `<img>` element
- [ ] Overlay feature renders when enabled (with color and opacity options)
- [ ] Nested components still work (for captions/overlays)
- [ ] Background and appearance properties work on wrapper
- [ ] Link wrapping still functions
- [ ] No regression in existing image functionality
- [ ] Test in both preview and export modes
- [ ] Verify chrome interaction works correctly
- [ ] Test all layout examples (hero section, inline gallery, mixed content row)
- [ ] Snapshot tests updated and passing

## Implementation Priority & Recommendation

### Priority Assessment
- **Issue 1 (Schema Gap):** Medium severity
- **Issue 2 (Layout Incompatibility):** High severity - Blocks fundamental use cases
- **Issue 3 (Architecture):** High severity - Technical debt affecting maintainability

### Overall Priority: **High**
The layout incompatibility issue is blocking users from creating common patterns like hero sections and inline galleries.

### Recommended Approach: **Option B (Full Refactor)**

**Rationale:**
1. **Solves all three issues comprehensively** - Schema, layout, and architecture
2. **Reduces code complexity** - Removes ~30 lines of custom logic, adds ~20 lines to existing function
3. **Future-proof** - New universal features automatically apply to images
4. **Eliminates technical debt** - Prevents accumulation of more custom rendering code
5. **Better user experience** - Images work consistently with other components

**Implementation timeline:**
- Estimated effort: 4-6 hours (including testing)
- Risk level: Medium (mitigated by comprehensive testing)
- Payoff: High (architectural consistency + feature completeness)

**If Option B is too risky or time-consuming:**
Implement **Option A** as a temporary fix to unblock layout use cases, then plan Option B refactor for next iteration.

## Related Documentation
- [CLAUDE.md - Rendering Pipeline](CLAUDE.md#rendering-pipeline-details)
- [CLAUDE.md - Chrome Wrapping](CLAUDE.md#preview-chrome-architecture)
- [image_component_container_analysis.md](image_component_container_analysis.md) - Detailed container analysis (now merged into this document)
