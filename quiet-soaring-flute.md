# Plan: Themes & Font Styles with YAML Anchors

## Overview

Add a Themes sidebar panel for managing page-level fonts and color themes. Theme values are defined as YAML anchors in the page component and referenced throughout components using aliases. This follows the existing architecture where YAML is the single source of truth.

---

## Architecture Principles

### 1. YAML as Single Source of Truth
- Theme anchors are defined in the page component's `theme` property
- Components reference theme values via YAML aliases (`*color-primary`)
- All theme changes update YAML first, then trigger re-render via existing `/render` endpoint

### 2. Smart Alias Injection
- **On Apply Theme**: Scan all components for color values matching theme colors
- **Matching colors**: Replace with alias references (e.g., `#3b82f6` → `*color-primary`)
- **Non-matching colors**: Leave as direct values (custom colors preserved)
- **Fonts**: Apply via alias only when component doesn't have explicit font override

### 3. js-yaml Anchor Handling
- Change `noRefs: false` in yamlUtils.js to preserve anchors
- js-yaml stores anchors internally and emits them when dumping
- Aliases are stored as object references in the parsed structure

---

## Data Flow

```
Themes Panel → Apply Theme → Parse YAML → Inject Theme Anchors
                                              ↓
                            Scan Components → Match Colors → Replace with Aliases
                                              ↓
                            Dump YAML (noRefs: false) → Update Editor
                                              ↓
                            Existing flow: POST /render → Preview Update
```

---

## YAML Structure

### Theme Definition (Page Component)
```yaml
- name: page
  properties:
    theme:
      fonts:
        headingMain: &font-heading-main "Georgia, serif"
        headingLevel2: &font-heading-level2 "Helvetica, sans-serif"
        content: &font-content "Arial, sans-serif"
      colors:
        primary: &color-primary "#3b82f6"
        secondary: &color-secondary "#1e40af"
        accent: &color-accent "#60a5fa"
        background: &color-background "#ffffff"
  components:
    - name: heading
      properties:
        typography:
          fontFamily: *font-heading-main
          color: *color-primary
    - name: button
      properties:
        appearance:
          background:
            color: *color-primary   # Uses theme
          border:
            color: "#custom123"      # Custom - not replaced
```

### Color Mapping Logic
| Theme Slot | Anchor Name | Typical Usage |
|------------|-------------|---------------|
| Primary | `&color-primary` | Headings, buttons, links |
| Secondary | `&color-secondary` | Secondary buttons, accents |
| Accent | `&color-accent` | Highlights, hover states |
| Background | `&color-background` | Page/section backgrounds |

---

## UI Layout (Themes Panel)

```
┌─────────────────────────────────────┐
│ Themes                          [X] │
├─────────────────────────────────────┤
│ FONTS                               │
│ ┌─────────────────────────────────┐ │
│ │ Main Headings    [Georgia     ▼]│ │
│ │ Level 2 Headings [Helvetica   ▼]│ │
│ │ Content          [Arial       ▼]│ │
│ └─────────────────────────────────┘ │
│                                     │
│ COLOR THEMES                        │
│ ┌─────────────────────────────────┐ │
│ │ Selected: Modern Blue           │ │
│ │ [■][■][■][■]  (editable)       │ │
│ │  Pri Sec Acc Bg                 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [■][■][■][■] Modern Blue       │ │
│ │ [■][■][■][■] Forest Green      │ │
│ │ [■][■][■][■] Sunset Orange     │ │
│ │ [■][■][■][■] Ocean Teal        │ │
│ │ ... (scrollable)                │ │
│ └─────────────────────────────────┘ │
│                                     │
│           [Apply Theme]             │
└─────────────────────────────────────┘
```

---

## Files to Modify

### 1. `ssr_python/static/js/yamlUtils.js`
**Enable YAML anchor preservation:**

```javascript
// Change noRefs from true to false
return yaml.dump(structure, {
    indent: 2,
    lineWidth: -1,
    noRefs: false,  // ← CRITICAL: Enable anchor/alias preservation
    sortKeys: false,
    skipInvalid: true
});
```

**Why:** js-yaml's `noRefs: true` converts all object references to inline values. Setting `false` preserves anchor/alias relationships.

---

### 2. `ssr_python/templates/index.html`
**Add Themes sidebar button and panel:**

Location: After layers button (`data-panel="layers"`), before the spacer div.

```html
<!-- Themes button -->
<button class="sidebar-btn" data-panel="themes" title="Themes">
    <svg aria-hidden="true"><use href="#icon-paintbrush"></use></svg>
    <span class="sidebar-btn-tooltip">Themes</span>
</button>

<!-- Themes panel (after other panels) -->
<div class="sidebar-panel" id="themesPanel">
    <div class="panel-header">
        <span class="panel-title">Themes</span>
        <button class="panel-close" onclick="window.closePanel()">
            <svg aria-hidden="true"><use href="#icon-x"></use></svg>
        </button>
    </div>
    <div class="panel-content" id="themesContent">
        <!-- Rendered by themesPanel.js -->
    </div>
</div>
```

The existing `data-panel` mechanism in `events.js` will auto-bind the button click.

---

### 3. `ssr_python/static/js/themesPanel.js` (NEW FILE)
**Theme management module:**

#### Exports
```javascript
export function renderThemesPanel()     // Render fonts + color themes UI
export function applyTheme()            // Inject anchors + replace matching colors
export function getCurrentTheme()       // Read theme from page component
```

#### Core Functions

**`renderThemesPanel()`**
- Reads current theme from YAML (if exists)
- Renders 3 font dropdowns with current selections
- Renders color theme list with selection state
- Renders editable selected theme with color swatches

**`applyTheme()`**
Algorithm:
1. Parse current YAML to structure
2. Get/create page component's `theme` property
3. Set theme anchors with selected fonts/colors
4. Walk all components recursively:
   - For each color property (typography.color, background.color, border.color)
   - If value matches a theme color → replace with alias reference
   - If value doesn't match → leave unchanged (custom color)
5. Dump structure with `noRefs: false`
6. Update editor content
7. Trigger render (existing flow handles this)

**`walkAndReplaceColors(component, themeColors)`**
```javascript
// themeColors = { '#3b82f6': 'color-primary', '#1e40af': 'color-secondary', ... }
// Recursively walk component tree
// Check: typography.color, appearance.background.color, appearance.border.color
// Replace matching hex values with object references to theme anchors
```

#### Data Structures

```javascript
const COLOR_THEMES = [
    { name: 'Modern Blue', colors: { primary: '#3b82f6', secondary: '#1e40af', accent: '#60a5fa', background: '#ffffff' }},
    { name: 'Forest Green', colors: { primary: '#10b981', secondary: '#065f46', accent: '#34d399', background: '#f0fdf4' }},
    { name: 'Sunset Orange', colors: { primary: '#f59e0b', secondary: '#b45309', accent: '#fbbf24', background: '#fffbeb' }},
    { name: 'Ocean Teal', colors: { primary: '#14b8a6', secondary: '#0f766e', accent: '#5eead4', background: '#f0fdfa' }},
    { name: 'Midnight Purple', colors: { primary: '#8b5cf6', secondary: '#5b21b6', accent: '#a78bfa', background: '#faf5ff' }},
    { name: 'Rose Pink', colors: { primary: '#ec4899', secondary: '#be185d', accent: '#f472b6', background: '#fdf2f8' }},
    { name: 'Slate Gray', colors: { primary: '#64748b', secondary: '#334155', accent: '#94a3b8', background: '#f8fafc' }},
    { name: 'Warm Earth', colors: { primary: '#d97706', secondary: '#92400e', accent: '#fbbf24', background: '#fef3c7' }},
];

const FONT_OPTIONS = [
    { value: 'Georgia, serif', label: 'Georgia' },
    { value: '"Times New Roman", serif', label: 'Times New Roman' },
    { value: 'Palatino, serif', label: 'Palatino' },
    { value: 'Arial, sans-serif', label: 'Arial' },
    { value: 'Helvetica, sans-serif', label: 'Helvetica' },
    { value: 'Verdana, sans-serif', label: 'Verdana' },
    { value: '"Trebuchet MS", sans-serif', label: 'Trebuchet MS' },
    { value: '"Courier New", monospace', label: 'Courier New' },
    { value: 'system-ui, sans-serif', label: 'System UI' },
];
```

---

### 4. `ssr_python/static/css/style.css`
**Theme panel styles:**

```css
/* Theme panel sections */
.theme-section {
    margin-bottom: 1.5rem;
}
.theme-section-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
}

/* Font dropdowns */
.theme-font-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.theme-font-label {
    font-size: 0.875rem;
    color: var(--text-primary);
}
.theme-font-select {
    width: 140px;
    padding: 0.375rem 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg-secondary);
    font-size: 0.875rem;
}

/* Selected theme (editable) */
.theme-selected-box {
    background: var(--bg-secondary);
    border: 2px solid var(--accent);
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 1rem;
}
.theme-selected-name {
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}
.theme-selected-colors {
    display: flex;
    gap: 0.5rem;
}
.theme-color-swatch {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 2px solid var(--border);
    cursor: pointer;
    position: relative;
}
.theme-color-swatch:hover {
    border-color: var(--accent);
}
.theme-color-swatch input[type="color"] {
    position: absolute;
    opacity: 0;
    width: 100%;
    height: 100%;
    cursor: pointer;
}
.theme-color-label {
    font-size: 0.625rem;
    text-align: center;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

/* Theme list (scrollable) */
.theme-list {
    max-height: 240px;
    overflow-y: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
}
.theme-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    transition: background 0.15s;
}
.theme-row:hover {
    background: var(--bg-tertiary);
}
.theme-row.selected {
    background: var(--accent-soft);
}
.theme-row-colors {
    display: flex;
    gap: 0.25rem;
}
.theme-row-pill {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 1px solid rgba(0,0,0,0.1);
}
.theme-row-name {
    font-size: 0.875rem;
    color: var(--text-primary);
}

/* Apply button */
.theme-apply-btn {
    width: 100%;
    padding: 0.75rem;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    margin-top: 1rem;
}
.theme-apply-btn:hover {
    background: var(--accent-hover);
}
```

---

### 5. `ssr_python/templates/macros/_components.html`
**Add font-family CSS rendering:**

In `build_styles()` macro, add font-family handling after color handling:

```jinja2
{# Font family from typography #}
{% if typography.fontFamily %}
    {% set _ = styles.append('font-family: ' ~ typography.fontFamily ~ ';') %}
{% endif %}
```

This allows theme fonts to be applied via the fontFamily property.

---

### 6. `ssr_python/static/js/main.js`
**Wire up themes panel:**

```javascript
import { renderThemesPanel, applyTheme } from './themesPanel.js';

// In init or DOMContentLoaded:
window.renderThemesPanel = renderThemesPanel;
window.applyTheme = applyTheme;

// Render themes panel when panel opens (add to panel toggle logic)
```

---

## Implementation Order

1. **Enable anchors** - Change `noRefs: false` in yamlUtils.js
2. **Add sidebar UI** - Button + panel HTML in index.html
3. **Create themesPanel.js** - Core theme logic
4. **Add CSS styles** - Theme panel styling in style.css
5. **Add font-family rendering** - Update build_styles macro
6. **Wire up in main.js** - Import and expose functions
7. **Test** - Apply theme to bookstore template

---

## Deferred (Phase 2)

- **Properties panel integration**: Show theme alias names in color pickers
- **Component schema updates**: Add fontFamily to typography fields
- **Theme inheritance**: Child components inherit parent theme colors

---

---

## Reference: Theme Anchor System - Complete Flow

This document explains how the marker-based anchor system works from theme definition through to YAML output.

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THEME ANCHOR SYSTEM FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. USER SELECTS THEME           2. APPLY THEME CLICKED
   ┌─────────────────┐             ┌─────────────────────────────────────┐
   │ Themes Panel    │             │ themesPanel.js: applyTheme()        │
   │                 │             │                                     │
   │ [■][■][■][■]   │  ────────►  │ selectedTheme = {                   │
   │ Modern Blue     │             │   primary: '#3b82f6',               │
   │                 │             │   secondary: '#1e40af',             │
   │ [Apply Theme]   │             │   accent: '#60a5fa',                │
   └─────────────────┘             │   background: '#ffffff'             │
                                   │ }                                   │
                                   └─────────────────────────────────────┘
                                                    │
                                                    ▼
3. INJECT MARKERS INTO STRUCTURE
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ JavaScript Object Structure (in memory)                                  │
   │                                                                          │
   │ page.properties.theme = {                                                │
   │   colors: {                                                              │
   │     primary: '___ANCHOR_PRIMARY___',      ◄── Marker inserted           │
   │     secondary: '___ANCHOR_SECONDARY___',                                 │
   │     accent: '___ANCHOR_ACCENT___',                                       │
   │     background: '___ANCHOR_BACKGROUND___'                                │
   │   }                                                                      │
   │ }                                                                        │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
4. WALK COMPONENTS & REPLACE MATCHING COLORS
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ walkAndReplaceColors() scans all components                              │
   │                                                                          │
   │ BEFORE:                              AFTER:                              │
   │ button:                              button:                             │
   │   typography:                          typography:                       │
   │     color: '#3b82f6' ─────────────►      color: '___ANCHOR_PRIMARY___'  │
   │                                                                          │
   │ heading:                             heading:                            │
   │   typography:                          typography:                       │
   │     color: '#ff6b35' ─────────────►      color: '#ff6b35'  (unchanged)  │
   │                     (no match)                                           │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
5. GENERATE YAML STRING (with markers)
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ generateYamlFromStructure() produces:                                    │
   │                                                                          │
   │ - name: page                                                             │
   │   properties:                                                            │
   │     theme:                                                               │
   │       colors:                                                            │
   │         primary: ___ANCHOR_PRIMARY___                                    │
   │         secondary: ___ANCHOR_SECONDARY___                                │
   │   components:                                                            │
   │     - name: button                                                       │
   │       properties:                                                        │
   │         typography:                                                      │
   │           color: ___ANCHOR_PRIMARY___                                    │
   │     - name: heading                                                      │
   │       properties:                                                        │
   │         typography:                                                      │
   │           color: '#ff6b35'                                               │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
6. POST-PROCESS: REPLACE MARKERS WITH YAML ANCHORS
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Step 6a: Replace FIRST occurrence (theme definition) with ANCHOR        │
   │                                                                          │
   │ yamlText.replace(                                                        │
   │   'primary: ___ANCHOR_PRIMARY___',                                       │
   │   "primary: &color-primary '#3b82f6'"  ◄── Anchor definition            │
   │ )                                                                        │
   │                                                                          │
   │ Result in theme section:                                                 │
   │   colors:                                                                │
   │     primary: &color-primary '#3b82f6'                                    │
   │     secondary: &color-secondary '#1e40af'                                │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Step 6b: Replace ALL remaining markers with ALIASES                      │
   │                                                                          │
   │ yamlText.replaceAll('___ANCHOR_PRIMARY___', '*color-primary')           │
   │                                                                          │
   │ Result in components:                                                    │
   │   - name: button                                                         │
   │     properties:                                                          │
   │       typography:                                                        │
   │         color: *color-primary  ◄── Alias reference                      │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
7. FINAL YAML OUTPUT
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ - name: page                                                             │
   │   properties:                                                            │
   │     theme:                                                               │
   │       fonts:                                                             │
   │         headingMain: &font-heading-main 'Georgia, serif'                 │
   │         content: &font-content 'Arial, sans-serif'                       │
   │       colors:                                                            │
   │         primary: &color-primary '#3b82f6'     ◄── ANCHOR defined        │
   │         secondary: &color-secondary '#1e40af'                            │
   │         accent: &color-accent '#60a5fa'                                  │
   │         background: &color-background '#ffffff'                          │
   │   components:                                                            │
   │     - name: button                                                       │
   │       properties:                                                        │
   │         typography:                                                      │
   │           color: *color-primary               ◄── ALIAS used            │
   │         appearance:                                                      │
   │           background:                                                    │
   │             color: *color-primary             ◄── ALIAS used            │
   │     - name: heading                                                      │
   │       properties:                                                        │
   │         typography:                                                      │
   │           color: '#ff6b35'                    ◄── Custom color kept     │
   └─────────────────────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
8. YAML PARSED BY JINJA (SERVER-SIDE)
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ When Flask/Jinja parses this YAML:                                       │
   │                                                                          │
   │ - Anchors (&color-primary) define a value                                │
   │ - Aliases (*color-primary) resolve to that value                         │
   │ - build_styles() receives: typography.color = '#3b82f6'                  │
   │ - CSS output: color: #3b82f6;                                            │
   │                                                                          │
   │ The anchor/alias system is transparent to rendering!                     │
   └─────────────────────────────────────────────────────────────────────────┘
```

### Key Code Locations

| Step | File | Function/Line |
|------|------|---------------|
| Theme selection | `themesPanel.js` | `selectTheme()`, line ~215 |
| Marker injection | `themesPanel.js` | `applyTheme()`, lines 260-273 |
| Color walking | `themesPanel.js` | `walkAndReplaceColors()`, lines 350-432 |
| YAML generation | `yamlUtils.js` | `generateYamlFromStructure()`, line 82 |
| Anchor replacement | `themesPanel.js` | `applyTheme()`, lines 292-319 |
| Alias replacement | `themesPanel.js` | `applyTheme()`, lines 322-328 |

### When User Selects a New Theme

1. User clicks different theme row → `selectTheme(newIndex)` called
2. `selectedTheme` object updated with new colors
3. User clicks "Apply Theme"
4. `applyTheme()` re-runs the entire flow:
   - New markers injected with new color values
   - All matching colors in components replaced with markers
   - Post-processing creates anchors with new color values
   - Aliases automatically reference new anchor values

### Color Matching Rules

```javascript
// Normalization: Case-insensitive, expand 3-digit hex
normalizeColor('#3B82F6')  → '#3b82f6'
normalizeColor('#FFF')     → '#ffffff'

// Matching logic:
// 1. Get component's color value
// 2. Normalize it (lowercase, expand)
// 3. Check if it matches any theme color
// 4. If YES → replace with marker
// 5. If NO → keep original value (custom color)
```

### What Gets Replaced

| Property Path | Example | Replaced? |
|---------------|---------|-----------|
| `typography.color` | `#3b82f6` | ✅ Yes (if matches theme) |
| `appearance.background.color` | `#ffffff` | ✅ Yes (if matches theme) |
| `appearance.border.color` | `#1e40af` | ✅ Yes (if matches theme) |
| `background.color` | `#ffffff` | ✅ Yes (if matches theme) |
| `appearance.background.gradient.colorStart` | `#ff0000` | ❌ No (gradients skipped) |
| Any color not matching theme | `#ff6b35` | ❌ No (custom color kept) |

---

## Verification Steps

1. Start Flask: `cd ssr_python && python app.py`
2. Load bookstore template or create new page
3. Click Themes button (paintbrush icon) in sidebar
4. Verify panel renders with fonts + color themes
5. Select "Sunset Orange" theme
6. Edit one color swatch → verify color picker works
7. Click "Apply Theme"
8. **Check YAML**:
   - Page has `theme:` section with anchors (`&color-primary`)
   - Buttons/headings with matching colors now use aliases (`*color-primary`)
   - Custom colors (non-matching) remain as hex values
9. Check preview renders correctly with theme colors
10. Manually edit a color in YAML → verify it stays as custom (no alias)
11. Re-apply theme → verify only matching colors get aliases

---

## Key Technical Notes

### js-yaml Anchor Behavior - Important Limitation

**js-yaml only creates anchors for objects/arrays, NOT for primitive strings.**

When `noRefs: false`, js-yaml detects duplicate object references and creates anchors. However:
- Primitive strings are NEVER automatically anchored
- Same string value in multiple places = no anchor created

**Why NOT use object wrappers (e.g., `{ value: '#3b82f6' }`):**
1. The entire wrapper object would be aliased, coupling all usages
2. Breaks Jinja macros that expect string color values
3. More complex YAML structure
4. Editing one reference affects all others (unintended coupling)

### Marker-Based Approach (Current Implementation)

Since js-yaml won't anchor primitives, we use **post-processing string replacement**:

1. **Insert unique markers** as placeholder values: `___ANCHOR_PRIMARY___`
2. **Generate YAML** with markers as strings
3. **Replace markers** with anchor syntax at theme definition
4. **Replace remaining markers** with alias syntax

**Security Analysis:**
- ✅ **Safe markers**: `___ANCHOR_COLORNAME___` format won't collide with user content
- ✅ **No prototype pollution**: Unlike js-yaml 3.14.0 vulnerability, markers are string replacements
- ✅ **No ReDoS risk**: Simple substring matching, no complex regex
- ⚠️ **Edge case**: User color values containing marker strings could corrupt output

**Recommended safeguard** (add to `applyTheme()`):
```javascript
const MARKER_PATTERN = /___ANCHOR_\w+___/;
function validateColor(value) {
    if (MARKER_PATTERN.test(value)) {
        console.warn('Color value contains reserved marker string');
        return false;
    }
    return true;
}
```

### Color Matching Strategy
```javascript
// Build lookup: normalized hex → marker string
const colorToMarker = new Map();
colorToMarker.set(normalizeColor(selectedTheme.primary), '___ANCHOR_PRIMARY___');
colorToMarker.set(normalizeColor(selectedTheme.secondary), '___ANCHOR_SECONDARY___');

// Walk components and replace matching colors with markers
if (colorToMarker.has(normalizedColor)) {
    props.typography.color = colorToMarker.get(normalizedColor);
}

// Post-process YAML string:
// 1. Replace theme definitions with anchors: `primary: &color-primary '#3b82f6'`
// 2. Replace other occurrences with aliases: `*color-primary`
```

### Preserving Custom Colors
A color is "custom" if:
- It doesn't match any theme color (case-insensitive hex comparison)
- User explicitly set it different from theme
- Example: Theme primary is `#3b82f6`, button has `#ff6b35` → stays as `#ff6b35`
