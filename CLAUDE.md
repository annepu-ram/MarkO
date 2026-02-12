# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Swift Sites** is a YAML-based website builder with server-side rendering. Users write YAML in an editor, and the application renders a live preview in an isolated iframe with component selection and properties editing. The YAML structure is the single source of truth - all changes flow through it, ensuring the preview, properties panel, history, and export stay synchronized.

**Architecture:** Server-Side Rendering (SSR) using Python Flask + Jinja2 templates. Preview renders in an iframe for complete style isolation. A legacy client-side rendering (CSR) version exists in the root `js/` directory.

DO NOT READ node_modules into context. They are not necessary.

---

## Commands

### SSR Development (Primary)

```bash
cd ssr_python
pip install -r requirements.txt    # Install Python dependencies
python app.py                       # Start Flask server at http://localhost:5000
```

### CSR Development (Legacy)

```bash
npm test                            # Run all Jest tests
npm test -- js/render/__tests__/index.test.js  # Run specific test file
npx jest <test> --updateSnapshot    # Update snapshot tests
npm run build:sprite                # Rebuild SVG icon sprite
```

---

## SSR Architecture Overview

### Core Rendering Flow (with Iframe)

```
YAML Editor → POST /render → Flask Backend
                              ↓
                         renderer.py: render_yaml_structure()
                              ↓
                         Jinja2 Macros (_components.html)
                              ↓
                         HTML Response
                              ↓
                    ssr_app.js: postMessage to iframe
                              ↓
                    preview_bridge.js: Update iframe DOM
                              ↓
                    Path Map Build → Component Selection Ready
```

**Key principle:** The YAML editor is the single source of truth. All state changes (property edits, component insertion, undo/redo) update the YAML first, then trigger server-side re-rendering.

---

## SSR Directory Structure

```
ssr_python/
├── app.py                    # Flask application entry point
├── renderer.py               # Core rendering engine
├── llm_service.py            # Ollama AI integration for chat
├── tokens.yaml               # Design tokens (spacing, typography, etc.)
├── generate_tokens_css.py    # Token to CSS generator
├── requirements.txt          # Python dependencies (Flask, PyYAML, ollama)
├── templates/
│   ├── index.html            # Main application UI (with iframe)
│   ├── preview_frame.html    # Iframe preview template
│   └── macros/
│       └── _components.html  # Jinja2 component macros (~1000 lines)
└── static/
    ├── css/
    │   ├── style.css         # Application UI styles
    │   ├── components.css    # Component-specific styles
    │   ├── preview-chrome.css # Chrome overlay styles for iframe
    │   ├── chat.css          # AI chat widget styles
    │   ├── images-panel.css  # Images panel styles (search, grid, upload)
    │   └── tokens.css        # Auto-generated CSS custom properties
    ├── js/
    │   ├── main.js           # Application bootstrap
    │   ├── ssr_app.js        # SSR rendering bridge, iframe communication
    │   ├── preview_bridge.js # Runs inside iframe, handles content/clicks
    │   ├── selectionManager.js   # Component selection
    │   ├── pathMapBuilder.js     # DOM-to-YAML mapping
    │   ├── propertiesPanel.js    # Properties inspector
    │   ├── historyManager.js     # Undo/redo
    │   ├── componentTree.js      # Component hierarchy tree
    │   ├── metadataLoader.js     # API metadata fetching
    │   ├── yamlUtils.js          # YAML manipulation
    │   ├── events.js             # Event wiring
    │   ├── customRenderers.js    # Complex property editors
    │   ├── component_interactions.js  # Interactive component init
    │   ├── chat.js               # AI chat UI component
    │   ├── chatService.js        # Chat API service
    │   ├── yamlWrapper.js        # YAML compatibility layer (eemeli/yaml)
    │   ├── yaml.bundle.js        # eemeli/yaml bundle (CSP-compliant)
    │   ├── yamlStorage.js        # SessionStorage persistence for YAML editor
    │   ├── themesPanel.js        # Theme selection and application
    │   ├── imagesPanel.js        # Stock photo search, selection, upload
    │   └── utils/
    │       ├── object.js     # Deep clone, merge, nested get/set
    │       └── timing.js     # Debounce helper
    └── icon-sprite.svg       # SVG icon sprite (includes sparkles icon)
```

---

## Iframe Preview Architecture

The preview renders inside an isolated iframe for complete CSS isolation between the app UI and preview content.

### Communication Flow

```
Parent Window (ssr_app.js)          Iframe (preview_bridge.js)
         │                                    │
         │──── IFRAME_READY (retry) ─────────>│
         │<─── IFRAME_READY_ACK ──────────────│
         │                                    │
         │──── UPDATE_CONTENT {html} ────────>│
         │<─── COMPONENTS_READY {ids} ────────│
         │                                    │
         │──── SET_SELECTION {id} ───────────>│
         │<─── COMPONENT_CLICKED {id} ────────│
```

### Key Files

| File | Location | Purpose |
|------|----------|---------|
| `index.html` | templates/ | Main UI with `<iframe id="preview-frame" src="/preview-frame">` |
| `preview_frame.html` | templates/ | Iframe HTML with preview-chrome.css and preview_bridge.js |
| `ssr_app.js` | static/js/ | Parent-side: sends content via postMessage, handles iframe messages |
| `preview_bridge.js` | static/js/ | Iframe-side: receives content, relays clicks, initializes components |
| `preview-chrome.css` | static/css/ | Selection highlighting styles for iframe |

### Message Types

| Message | Direction | Purpose |
|---------|-----------|---------|
| `IFRAME_READY` | iframe → parent | Iframe loaded, ready for content |
| `IFRAME_READY_ACK` | parent → iframe | Acknowledges ready, stops retry loop |
| `UPDATE_CONTENT` | parent → iframe | Sends rendered HTML to display |
| `COMPONENTS_READY` | iframe → parent | Lists all component IDs in DOM |
| `SET_SELECTION` | parent → iframe | Highlights a component |
| `CLEAR_SELECTION` | parent → iframe | Removes selection highlight |
| `COMPONENT_CLICKED` | iframe → parent | User clicked a component |

---

## Python Files

### `app.py` - Flask Application

**Purpose:** Main Flask application handling HTTP requests and routes.

**Key Components:**
- `TOKENS` - Global dictionary storing design tokens from `tokens.yaml`
- `COMPONENT_DEFAULTS` - Loaded from `component_defaults.yaml`
- Custom Jinja2 filter: `transparency_to_hex()` - converts transparency (0-100) to hex alpha

**Routes:**
```python
@app.route('/')                    # Main UI
@app.route('/preview-frame')       # Iframe preview content
@app.route('/render', methods=['POST'])  # YAML to HTML
@app.route('/api/schemas')         # Component schemas JSON
@app.route('/api/defaults')        # Component defaults JSON
@app.route('/api/tokens')          # Schema tokens JSON
```

### `renderer.py` - Rendering Engine

**Purpose:** Core rendering logic converting YAML structures to HTML.

**Key Functions:**
- `render_yaml_structure(structure, tokens, defaults)` - Main entry point
- `deep_merge(base, override)` - Recursive dictionary merging
- `merge_component_with_defaults(component, defaults)` - Merges YAML with defaults

**Flow:**
1. Validates structure and tokens
2. Creates Jinja2 template string
3. Imports `_components.html` macros
4. Renders template with structure + tokens
5. Returns HTML string

---

## Flask API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main application UI |
| `/preview-frame` | GET | Iframe preview template |
| `/render` | POST | Renders YAML to HTML |
| `/api/chat` | POST | LLM chat endpoint (Ollama AI) |
| `/api/images/search` | GET | Proxy stock photo search (Pexels/Pixabay) |
| `/api/schemas` | GET | Component schemas as JSON |
| `/api/defaults` | GET | Component defaults as JSON |
| `/api/tokens` | GET | Schema tokens as JSON |

---

## Template System (`_components.html`)

### Architecture

**Macro-Based Component System:**
- Each component type has its own macro (e.g., `render_heading()`, `render_button()`)
- Main dispatcher `render_component()` routes to appropriate macro
- Macros call `render_component()` recursively for nested components

### Key Macros

#### `render_component(component, tokens, path=[])` - Main Dispatcher
Routes components based on `component.name`:
- **Layout:** page, layout-row, layout-column, columnsgrid, form
- **Interactive:** tabs, accordion, carousel, hamburger
- **Text:** heading, paragraph, eyebrow, caption, blockquote, link
- **Media:** image, video, gif
- **UI:** button, titlebar
- **Forms:** textbox, textarea, dropdown, checkbox, radio, calendar
- **Utility:** br

#### `build_styles(component, tokens, part=None)` - Style Generator
Generates inline CSS styles from component properties and design tokens.

#### `build_flex_styles(component, tokens, direction)` - Flex Layout
Generates flexbox styles for layout components.

---

## Client-Side JavaScript Modules

### Core Application

| Module | Purpose |
|--------|---------|
| `main.js` | Application bootstrap, DOM init, event wiring |
| `ssr_app.js` | SSR rendering bridge, iframe postMessage communication |
| `preview_bridge.js` | Runs in iframe, handles content updates and click relay |
| `events.js` | Event listeners (editor, preview, buttons, keyboard) |

### State Management

| Module | Purpose |
|--------|---------|
| `selectionManager.js` | Component selection state and highlighting |
| `pathMapBuilder.js` | Maps component IDs to YAML paths |
| `historyManager.js` | Undo/redo stacks (max 50 states) |
| `yamlStorage.js` | SessionStorage persistence (survives tab refresh) |

### Properties System

| Module | Purpose |
|--------|---------|
| `propertiesPanel.js` | Renders form fields from schema |
| `metadataLoader.js` | Loads schemas, defaults, tokens from API |
| `customRenderers.js` | Complex property editors (links, slides) |
| `yamlUtils.js` | YAML parsing, component updates |

### Component Support

| Module | Purpose |
|--------|---------|
| `componentTree.js` | Component hierarchy tree UI |
| `component_interactions.js` | Runtime init for carousels, tabs, etc. |

---

## Titlebar Component

The titlebar has special scroll behavior with a clone-based sticky implementation.

### How It Works
1. When titlebar initializes, `preview_bridge.js` creates a hidden clone
2. Clone has `position: fixed; top: 0` and is initially `opacity: 0`
3. On scroll, when original titlebar's bottom edge goes above viewport, clone shows
4. Both original and clone get `.scrolled` class for shrink effect when scrollY > 50

### Shrink Effect
- Logo and title shrink based on `shrinkPercentage` property (default: 30%)
- Menu items do NOT shrink - only logo and title
- CSS variable `--shrink-scale` controls shrink amount

### CSS Classes
- `.titlebar` - Base titlebar styles
- `.titlebar.scrolled` - Shrunk state (padding, height, logo, title)
- `.titlebar-clone` - Fixed position clone, hidden by default
- `.titlebar-clone.visible` - Clone visible when original out of view

---

## Component Styling Architecture

### Components Using CSS Variables

These components generate CSS variables consumed by `components.css`:

**1. Tabs Component**
- `--tabs-gap`, `--tabs-margin-block`, `--tabs-margin-inline`
- `--tabs-label-font-size`, `--tabs-label-font-weight`
- `--tabs-label-color-active`, `--tabs-label-color-inactive`

**2. Accordion Component**
- `--accordion-gap`, `--accordion-margin-*`, `--accordion-border-radius`
- `--accordion-title-*`, `--accordion-content-*`

**3. Titlebar Component**
- `--base-height`, `--title-font-size`, `--title-font-weight`, `--shrink-scale`
- `--titlebar-title-color`, `--titlebar-link-color`

**4. Blockquote Component**
- `--blockquote-border` - Accent border color

### Components Using Inline Styles Only

These use `build_styles()` to generate inline styles directly:
- page, layout-row, layout-column, columnsgrid, form
- heading, paragraph, eyebrow, caption, link
- image, video, gif, button, carousel, hamburger
- Form inputs (textbox, textarea, dropdown, checkbox, radio, calendar)

---

## Component Selection & Properties Editing

### Component ID Generation

**Server-Side (Jinja2):**
```jinja2
{% set component_id = 'comp_' ~ path | join('_') %}
```

**Path Examples:**
- `[0]` → `comp_0`
- `[0, 'components', 1]` → `comp_0_components_1`
- `[0, 'columns', 0, 'components', 2]` → `comp_0_columns_0_components_2`

### Selection Flow (with Iframe)

```
1. User clicks in iframe preview
   ↓
2. preview_bridge.js: handleClick() finds [data-component-id]
   ↓
3. postMessage COMPONENT_CLICKED to parent
   ↓
4. ssr_app.js: dispatches 'iframe-component-clicked' event
   ↓
5. selectionManager handles selection
   ↓
6. postMessage SET_SELECTION back to iframe for highlighting
   ↓
7. Properties panel renders form for component
```

---

## Adding New Components to SSR

1. **Add Component Macro** (`_components.html`):
   ```jinja2
   {% macro render_mycomponent(component, tokens, path, component_id) %}
       {% set properties = component.properties | default({}) %}
       <div class="my-component chrome-target"
            data-component-id="{{ component_id }}"
            style="{{ build_styles(component, tokens) }}">
           {{ properties.text }}
       </div>
   {% endmacro %}
   ```

2. **Add to Dispatcher** (`render_component()` macro)

3. **Add CSS** (`static/css/components.css`)

4. **Add Defaults** (`component_defaults.yaml`)

5. **Add Schema** (`component_schemas.yaml`)

---

## Metadata Files

The following metadata files must stay synchronized:

| File | Purpose |
|------|---------|
| `component_defaults.yaml` | Default properties for each component type |
| `component_schemas.yaml` | Inspector form fields, types, labels, token refs |
| `schema_tokens.yaml` | Design token options for dropdowns |
| `tokens.yaml` | CSS token values (snake_case keys) |
| `COMPONENT_PROPERTIES_MATRIX.md` | Cross-tabulation of components vs properties |
| `LLM_COMPONENT_GUIDE.md` | LLM-friendly guide for YAML generation |
| `MEDIA_CAROUSEL_ENHANCEMENTS.md` | Implementation plan for media component enhancements |

---

## Recent Fixes (January 2025)

### Layout-Row Wrapping Fix
- **Fixed:** Images and other components in layout-row now wrap correctly when using `wrap: wrap`
- **Root cause:** `flex-basis: 0%` allowed children to shrink infinitely instead of wrapping
- **Solution:** Changed flex-basis to actual percentage values (23%, 48%, 73%, 100%) so items have minimum widths that trigger wrapping
- **File:** `_components.html` lines 1324-1347

**Updated width modes for row context:**
| widthMode | Before | After |
|-----------|--------|-------|
| 25% | `flex: 1 1 0%` | `flex: 1 0 23%; max-width: 25%;` |
| 50% | `flex: 2 1 0%` | `flex: 1 0 48%; max-width: 50%;` |
| 75% | `flex: 3 1 0%` | `flex: 1 0 73%; max-width: 75%;` |
| stretch | `flex: 4 1 0%` | `flex: 1 0 100%;` |

### Image Hover Effects with Filters Fix
- **Fixed:** Hover effects (brighten, darken) now work correctly with filtered images (grayscale, saturate, etc.)
- **Root cause:** CSS `filter` property doesn't stack - hover filter replaced inline filter instead of combining
- **Solution:** Use CSS custom property `--base-filter` to combine filters
- **Files Modified:**
  - `_components.html` - Output filter as `--base-filter` CSS variable
  - `components.css` - Hover effects combine with base filter: `filter: var(--base-filter, none) brightness(0.85);`

### Caption Property Removed from Media Components
- **Removed:** `caption` property from image, gif, and video components
- **Reason:** Simplifying component structure; use nested text components for captions instead
- **Files Modified:**
  - `component_schemas.yaml` - Removed caption groups from image, gif, video
  - `component_defaults.yaml` - Removed caption defaults
  - `_components.html` - Removed caption rendering code from macros
  - `LLM_COMPONENT_GUIDE.md` - Updated component examples

### YAML Library Migration (eemeli/yaml)
- **Migrated:** From `js-yaml` to `eemeli/yaml` for native anchor/alias support
- **Added:** `yamlWrapper.js` - Compatibility layer providing js-yaml-like API
- **Added:** `yaml.bundle.js` - CSP-compliant local bundle of eemeli/yaml
- **Purpose:** Preserve YAML anchors (`&anchor`) and aliases (`*alias`) when editing via properties panel

**Key Functions:**
- `parse(content)` - Simple parse, returns plain JS objects (anchors resolved)
- `parseDocument(content)` - Returns YAML Document (preserves anchors/aliases)
- `stringify(value)` - Simple stringify
- `stringifyDocument(doc)` - Stringify with anchors preserved
- `YAML.isMap()`, `YAML.isSeq()`, `YAML.isAlias()` - Type checks

**Document API Usage:**
```javascript
// When editing properties while preserving anchors:
const doc = parseDocument(yamlContent);
const componentNode = navigateToComponent(doc, componentPath);
componentNode.set('properties', updatedProps);
const yamlText = stringifyDocument(doc);  // Anchors preserved!
```

### Themes Panel Implementation
- **Added:** `themesPanel.js` - Theme selection and application UI
- **Added:** Theme color aliases in YAML templates using anchors
- **Example:** `primary: &color-primary '#1e293b'` with `color: *color-primary`
- Theme colors flow through YAML anchors, automatically updating all references

### Themes Panel Refactoring (February 2026)
- **Added:** `THEME_COLOR_CONFIG` exported constant — single source of truth for color keys, anchor names, and labels
- **Changed:** Apply button moved from scrollable `panel-content` to a fixed `themesFooter` element (stays visible while scrolling)
- **Changed:** `applyTheme()` now uses `THEME_COLOR_CONFIG` to iterate color anchors instead of hardcoded calls
- **Changed:** `attachThemePanelEvents()` accepts both `container` and `footer` params to attach Apply button listener

```javascript
// Shared config used by themesPanel.js and potentially other modules
export const THEME_COLOR_CONFIG = [
    { key: 'primary', anchor: 'color-primary', label: 'Primary' },
    { key: 'secondary', anchor: 'color-secondary', label: 'Secondary' },
    { key: 'accent', anchor: 'color-accent', label: 'Accent' },
    { key: 'background', anchor: 'color-background', label: 'Background' },
];
```

**Panel HTML structure (in index.html):**
```html
<div class="sidebar-panel" id="themesPanel">
    <div class="panel-header">...</div>
    <div class="panel-content" id="themesContent">
        <!-- Scrollable theme list -->
    </div>
    <div class="panel-footer" id="themesFooter">
        <!-- Fixed Apply button rendered here by JS -->
    </div>
</div>
```

### Gradient Background Support
- **Added:** Gradient backgrounds for buttons, sections, and layout components
- **Structure:**
```yaml
appearance:
  background:
    type: gradient  # 'solid' or 'gradient'
    gradient:
      colorStart: '#ff0000'
      colorEnd: '#0000ff'
      direction: 'to right'  # or 'to bottom', 'to bottom right', etc.
```

### Media Component Enhancements (Implemented)
- **Scope:** Image, Video, GIF, Video-Background, Carousel components
- **Property Restructuring:** Unified all media components to use `appearance` category for consistency:
  - Renamed `presentation` → `appearance`
  - Merged `effects.*` properties into `appearance`
  - Merged `loading.*` properties into `appearance`
  - Moved `overlay` as nested object inside `appearance.overlay`

**New Properties (all under `appearance.*`):**
- `appearance.aspectRatio` - CSS aspect-ratio (auto, 16/9, 4/3, 1/1, 3/2, 21/9, 9/16)
- `appearance.objectPosition` - Focal point (center, top, bottom, left, right, corners)
- `appearance.filter` - CSS filters (none, grayscale, sepia, blur, brighten, darken, saturate)
- `appearance.shadow` - Box shadow scale (none, sm, md, lg, xl)
- `appearance.hoverEffect` - Hover animations (none, zoom, brighten, darken, lift)
- `appearance.lazy` - Lazy loading toggle
- `appearance.overlay.enabled/color/opacity` - Overlay configuration

**New Video-Background Component:**
- Full-width video background with nested overlay content
- Supports MP4/WebM direct URLs (not iframes)
- Auto-plays, loops, muted by default (mobile-friendly)
- Configurable overlay for text readability
- Content alignment options (vertical/horizontal)

**Files Modified:**
| File | Changes |
|------|---------|
| `component_schemas.yaml` | Image, GIF, Video, Video-Background schemas restructured |
| `component_defaults.yaml` | All media component defaults updated to `appearance.*` |
| `_components.html` | render_image, render_gif, render_video, render_video_background macros updated |
| `components.css` | Added hover effects, caption overlay, video-background styles |
| `swift-sites-runtime.js` | Carousel enhancements (swipe, keyboard nav, pause button) |

**Carousel Enhancements:**
- Touch swipe navigation with configurable threshold
- Keyboard navigation (arrow keys, Home/End)
- WCAG 2.2.2 compliant pause button for autoplay
- Fade/slide transition effects
- Multiple indicator styles (dots, numbers, dashes)

### Boolean Data Attributes Convention
- **Important:** Jinja2 templates must use lowercase string `'true'`/`'false'` for boolean data attributes
- **Correct:** `data-autoplay="{{ 'true' if behavior.autoplay else 'false' }}"`
- **Wrong:** `data-autoplay="{{ behavior.autoplay }}"` (outputs Python `True`/`False`)
- JavaScript reads these with `element.dataset.autoplay === 'true'`

### Page Background Color Path Fix
- **Fixed:** Page background color not rendering correctly
- **Root cause:** Property path mismatch between schema, defaults, and macro
- **Solution:** Standardized path to `properties.appearance.background.color` across all files

### Theme Color Alias Preservation Fix
- **Fixed:** Theme color aliases (`*color-primary`) being replaced with literal values when editing properties
- **Root cause:** `collectPropertyValues()` was overwriting alias nodes with plain values
- **Solution:** Use YAML Document API (`parseDocument`, `stringifyDocument`) to preserve anchors/aliases
- **Files Changed:** `main.js`, `yamlUtils.js` - now use Document API for property updates

### Accordion/Carousel Boolean Attributes Fix
- **Fixed:** Interactive components not responding to boolean settings (autoplay, loop, etc.)
- **Root cause:** Jinja2 outputting Python `True`/`False` instead of lowercase strings
- **Solution:** Use ternary in templates: `{{ 'true' if value else 'false' }}`
- **Affected Components:** carousel, accordion, tabs

### Properties Panel Merge Logic Fix
- **Fixed:** Property changes getting lost during merge with defaults
- **Root cause:** `applySelectedComponentProperties` was using plain structure instead of Document API
- **Solution:** Separate property updates from component-level updates (tabs, items, slides)
- **Code Pattern:**
```javascript
// Use Document API for properties (preserves anchors)
updateComponentPropertiesInDocument(yamlDoc, path, collectedValues.properties);

// Use direct set for component-level arrays
if (collectedValues.component) {
    const node = navigateToComponent(yamlDoc, path);
    node.set(key, value);
}
```

### Text Component Transparency Fix
- **Fixed:** Text invisible on dark backgrounds due to opaque white backgrounds
- **Root cause:** heading, paragraph, eyebrow, caption, blockquote had `transparency: 100` (fully opaque white)
- **Solution:** Changed `transparency` to `0` (fully transparent) in `component_defaults.yaml`
- Text components now have transparent backgrounds by default, allowing underlying colors/images to show through

### LLM Chat Widget Implementation
- **Added:** AI-powered chat widget using Ollama (`ollama` package)
- **Added:** `llm_service.py` for Ollama API integration with `LLM_COMPONENT_GUIDE.md` as context
- **Added:** `chat.js` and `chatService.js` for chat UI and API communication
- **Added:** `chat.css` with accent color styling (#9c9ef0)
- **Added:** `/api/chat` endpoint in `app.py`
- **Added:** Sparkles icon to `icon-sprite.svg` for chat bubble
- Chat bubble positioned at bottom-left corner
- Supports create, modify, and explain actions

### LLM Chat Enhancements (February 2026)
- **Fixed:** f-string escaping bug in system prompt - curly braces in YAML examples were being interpreted as Python variables
- **Added:** Configurable timeout via `OLLAMA_TIMEOUT` environment variable (default 120s)
- **Added:** Request/response logging to `ssr_python/logs/llm_chat.log`
- **Added:** YAML validation with warning display (shows Apply button even if YAML has issues)
- **Added:** Selection context synchronization via `swift-selection-changed` DOM event
- **Changed:** Response handling now discards LLM explanatory text, shows only YAML
- **Changed:** Chat selection indicator updates automatically when component is selected/deselected
- **Fixed:** Race condition where chat callback wrapper could be overwritten by main.js

**Selection Event System:**
```javascript
// SelectionManager dispatches on select/clear
window.dispatchEvent(new CustomEvent('swift-selection-changed', {
    detail: { componentId, path }
}));

// Chat listens for changes
window.addEventListener('swift-selection-changed', () => {
    this.updateSelectionIndicator();
});
```

### Bookstore Template
- **Added:** Comprehensive bookstore template (`example_templates/bookstore_template.yaml`)
- Uses Unsplash and Pexels images (open source)
- Sections: Navigation, Hero, New Arrivals, Second Hand Books (50% off), Children's Hard Board Books, Arts & Crafts, Testimonials, Newsletter, Footer
- Fixed color contrast issues (strikethrough prices, footer text)

### YAML Editor Persistence (SessionStorage)
- **Added:** New `yamlStorage.js` module for browser storage persistence
- YAML content now survives tab refresh (F5, Ctrl+R)
- Uses `sessionStorage` (tab-scoped) - content is lost when tab/browser closes
- Auto-saves on every editor change via `handleEditorInput()`
- Auto-loads on page initialization in `main.js`
- Clear button also clears stored content

**Key Functions:**
- `yamlStorage.save(content)` - Save YAML to sessionStorage
- `yamlStorage.load()` - Load YAML from sessionStorage
- `yamlStorage.clear()` - Clear stored content
- `yamlStorage.hasContent()` - Check if content exists

### Device Frame Dimensions
- **Changed:** Tablet viewport from portrait to landscape mode
  - Width: 1024px, Height: 600px (iPad landscape)
- **Changed:** Mobile viewport height to 790px
  - Width: 390px, Height: 790px (iPhone portrait)
- Defined in `style.css` under `.device-frame.tablet` and `.device-frame.mobile`

### Responsive Font Sizing
- **Added:** CSS `clamp()` for fluid responsive typography in `preview_frame.html`
- Root font-size scales with viewport: `clamp(12px, 1vw + 8px, 18px)`
- Component fonts use `rem` units, automatically scaling with viewport changes
- UI fonts remain fixed (only preview content is responsive)

### Properties Panel Value Collection Fix
- **Fixed:** Property changes not applying when value equals default
- **Root cause:** `collectPropertyValues()` in `propertiesPanel.js` was skipping values that matched defaults
- **Solution:** Always include collected values; let `main.js` merge handle defaults
- Example: Setting heading size to "xl" (default) when current was "lg" now works correctly

### Token & Schema Consistency Fixes
- **Fixed:** Token name mismatch `borderRadius` → `borderRadiusScale` in `component_schemas.yaml`
- **Fixed:** Titlebar schema path `layout.shrinkPercent` → `scroll.shrinkPercentage` to match macro and defaults
- **Added:** Missing `appearance.focus.color` to titlebar defaults

### letterSpacing CSS Rendering
- **Added:** `letter-spacing` CSS generation in `build_styles()` macro
- Uses `tokens.letter_spacing` mapping: `normal`, `tight`, `wide`, `wider`
- All text components now render letterSpacing property correctly

### Typography Property Standardization
All text components now have consistent typography properties:

| Property | heading | paragraph | eyebrow | caption | blockquote | link |
|----------|:-------:|:---------:|:-------:|:-------:|:----------:|:----:|
| size | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| weight | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| align | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| color | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| lineHeight | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| transform | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| letterSpacing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Both `component_schemas.yaml` and `component_defaults.yaml` updated for consistency.

### Viewport Switching Fix
- **Fixed:** Replaced inline `onclick` handlers with `data-viewport` attributes
- **Fixed:** Horizontal scrollbar by changing `overflow-x` to `hidden` on app container

### Component Selection & Properties Panel Fix
- **Fixed:** YAML parser not loading in ES modules - downloaded `js-yaml.min.js` locally to `static/js/` and updated loading in `index.html`
- **Fixed:** Properties panel not displaying when clicking components in iframe - fixed `window.jsyaml` access pattern in `yamlUtils.js` and `ssr_app.js`
- **Fixed:** Component tree not refreshing when YAML changes - ensured path map builds correctly from parsed YAML structure

### Iframe Preview Enhancement
- **Added:** Preview now renders in isolated iframe for complete CSS separation between app UI and preview content.
- **Fixed:** Race condition with IFRAME_READY handshake using retry pattern with acknowledgment.
- **Added:** Clone-based sticky titlebar that appears when original scrolls out of view with configurable shrink percentage (default 30%).
- **Fixed:** Removed page component chrome overlay label, simplified to `.page` class for cleaner rendering.

### Previous Fixes

**Font Size Property:** Removed UTF-8 BOM from `schema_tokens.yaml` - all 9 font size options now visible.

**Width Mode:** Changed from fixed percentages to proportional flex-grow for proper gap handling in layout-row.

**ColumnsGrid:** Calculate width as `100% / columnCount`, stack on mobile <768px.

**Layout-Column Width Mode:** Changed default `align-items` from `stretch` to `center` so child width modes work.

**Layout Containers:** Set `transparency: 0` (fully transparent) for layout-row and layout-column defaults.

---

## Troubleshooting SSR

**Preview not updating?**
- Check browser console for `[SSR App]` and `[Preview Bridge]` messages
- Verify IFRAME_READY handshake completed (look for "acknowledged by parent")
- Check Network tab for `/render` response

**Titlebar not sticking?**
- Titlebar uses clone-based approach, not CSS sticky
- Clone appears when original's `rect.bottom < 0`
- Check `.titlebar-clone.visible` class is being added

**Tokens not loading?**
- Check `tokens.yaml` exists in `ssr_python/` directory
- Check Flask console for token loading messages

**Selection not working?**
- Check components have `data-component-id` attributes
- Verify postMessage communication in console
- Check `chrome-target` class is present

**YAML parser not available?**
- Check console for `[Init] js-yaml loaded successfully` message
- Ensure `js-yaml.min.js` exists in `static/js/` directory
- Verify `index.html` loads it before the module script
- Check both `jsyaml` and `window.jsyaml` in browser console

**Properties panel not updating?**
- Check console for `[SSR App] Built path map with X components`
- Click component and look for `[SSR App] COMPONENT_CLICKED received`
- Verify `[SelectionManager] Path lookup result` shows array (not null)
- Check `[Main] onSelectionChange called with` has valid selection

**YAML not persisting across refresh?**
- Check console for `[Main] Restored YAML from sessionStorage` on page load
- Verify `sessionStorage.getItem('swift_sites_yaml_content')` in browser console
- Note: sessionStorage is tab-scoped - each tab has isolated storage
- Note: Content is lost when browser/tab closes (use localStorage for permanent storage)

---

## Data Model

### YAML Structure

- Root: array with single `{ name: 'page', properties, components }` object
- **Simple components**: `{ name, properties }` with typography, spacing, layout, appearance
- **Container components**: Add nested `components`, `columns`, `tabs`, `slides`

### Component Path Map

Maps DOM IDs to YAML paths:
- `comp_0` → `[0]`
- `comp_0_components_1` → `[0, 'components', 1]`
- `comp_0_columns_0_components_2` → `[0, 'columns', 0, 'components', 2]`

---

## Legacy CSR Reference

The client-side rendering version exists in the root directory:

**Location:** `js/` directory, entry point `index.html`

**Key Files:**
- `js/render/index.js` - Main renderer with `renderYamlStructure()`
- `js/core/state.js` - Global state manager
- `js/core/yaml.js` - YAML parsing/serialization

**Key Differences from SSR:**
| Feature | CSR | SSR |
|---------|-----|-----|
| Rendering | Browser (JavaScript) | Server (Python/Jinja2) |
| Preview Isolation | Same document | Iframe |
| Communication | Direct DOM | postMessage API |

---

## Design Tokens Reference

### Typography Tokens (`tokens.yaml`)

| Token | Values |
|-------|--------|
| `typography_sizes` | xxs, xs, sm, md, lg, xl, xxl, xxxl, auto |
| `font_weights` | light, regular, medium, semibold, bold, extrabold |
| `letter_spacing` | normal, tight, wide, wider |

### Spacing Tokens

| Token | Values |
|-------|--------|
| `spacing` | none, xxs, xs, sm, md, lg, xl, xxl, xxxl, auto |
| `border_radius` | none, xs, sm, md, lg, xl, xxl, pill |

### Schema Token References (`schema_tokens.yaml`)

When adding schema fields that reference tokens, use these token names:
- `typographySizes` - Font size dropdown
- `fontWeights` - Font weight dropdown
- `spacingScale` - Padding/margin dropdowns
- `gapScale` - Gap between items
- `borderRadiusScale` - Border radius dropdown
- `letterSpacingMap` - Letter spacing dropdown
- `alignmentHorizontal` - Text alignment (left, center, right, justify)

---

## AI Chat Feature (Implemented)

An AI-powered chat widget that generates and modifies YAML from natural language descriptions using Ollama AI (local or cloud).

### Architecture

```
User Message + Selected Component → Chat UI → POST /api/chat → Flask Backend
                                                                    ↓
                                              llm_service.py: Load LLM_COMPONENT_GUIDE.md
                                                                    ↓
                                              Build context (YAML + selection)
                                                                    ↓
                                              Call Ollama API (ollama)
                                                                    ↓
                                              Parse response for YAML blocks
                                                                    ↓
Chat UI ← JSON Response ← Return action + YAML
    ↓
Update Editor → Trigger /render → Preview Updates
```

### Key Files

| File | Purpose |
|------|---------|
| `llm_service.py` | Ollama API integration, prompt building, response parsing |
| `chat.js` | Chat UI component (bubble button, window, messages) |
| `chatService.js` | API communication with `/api/chat` endpoint |
| `chat.css` | Chat widget styling (positioned bottom-left) |

### Configuration

```bash
# Required for Ollama Cloud
OLLAMA_API_KEY=your_api_key_here    # Get from https://ollama.com/settings/keys

# Optional environment variables (defaults shown)
OLLAMA_BASE_URL=https://ollama.com  # Cloud URL (or http://localhost:11434 for local)
OLLAMA_MODEL=llama3:latest          # Model to use
LLM_MAX_TOKENS=4096                 # Max response tokens
LLM_TEMPERATURE=0.7                 # Response creativity (0-2)
OLLAMA_TIMEOUT=120                  # Request timeout in seconds (default 2 minutes)
```

**Cloud vs Local Usage:**
| Mode | OLLAMA_API_KEY | OLLAMA_BASE_URL |
|------|----------------|-----------------|
| Cloud | Required | `https://ollama.com` (default) |
| Local | Not needed | `http://localhost:11434` |

### Chat UI Features

- **Floating button:** Bottom-left corner with sparkles icon
- **Chat window:** 400x500px expandable panel
- **Selection awareness:** Shows "Editing: [component name]" badge when component selected (via `swift-selection-changed` event)
- **YAML responses:** Displayed with syntax highlighting and "Apply Changes" button
- **Action types:** `create` (new page), `modify` (update component), `explain` (text only)

### Selection Context Synchronization

The chat widget listens for component selection changes via a custom DOM event:

```javascript
// selectionManager.js dispatches this event on selection change
window.dispatchEvent(new CustomEvent('swift-selection-changed', {
    detail: { componentId, path: [...path] }
}));

// chat.js listens for the event
window.addEventListener('swift-selection-changed', () => {
    this.updateSelectionIndicator();
});
```

This event-based system allows multiple components (properties panel, chat, component tree) to all respond to selection changes without callback conflicts.

### Response Handling

The LLM returns responses with `<!-- ACTION: type -->` comments:
- `create`: Replace entire editor content with new YAML
- `modify`: Merge YAML at selected component path
- `explain`: Display text response only, no YAML changes
- `error`: Display error message

**Response Processing:**
1. YAML is extracted from markdown code blocks (`` ```yaml ... ``` ``)
2. YAML syntax is validated before display
3. If valid: Show "Here's the generated YAML:" with Apply button
4. If invalid: Show YAML with warning banner, Apply button still available
5. Explanatory text from LLM is discarded (only YAML is shown)

### LLM Request/Response Logging

All LLM interactions are logged to `ssr_python/logs/llm_chat.log` for debugging:

```
2026-02-05 10:30:15 | INFO | ================================================================================
2026-02-05 10:30:15 | INFO | NEW CHAT REQUEST
2026-02-05 10:30:15 | INFO | User Message: create a bakery landing page
2026-02-05 10:30:15 | INFO | Selected Component: None
2026-02-05 10:30:15 | INFO | Current YAML Length: 0 chars
2026-02-05 10:30:18 | INFO | RAW RESPONSE (1523 chars):
<!-- ACTION: create -->
...
2026-02-05 10:30:18 | INFO | PARSED: action=create, yaml_length=845
```

**Log Location:** `ssr_python/logs/llm_chat.log` (gitignored)

### Error Handling

| Error | User Message |
|-------|--------------|
| Connection refused | "Cannot connect to Ollama. Please ensure Ollama is running." |
| Timeout | "Request timed out after Xs. The model may be overloaded. Try a simpler request." |
| 401 Unauthorized | "AI authentication failed. Please contact the administrator." |
| YAML validation | Warning banner with error details, YAML still shown |
| Not configured | "AI chat is not configured. Please contact the administrator." |

---

## Images Panel (Stock Photo Search)

An integrated panel for searching, selecting, and uploading images from stock photo services.

### Architecture

```
Search Input → Debounce (300ms) → GET /api/images/search → Flask Backend
                                                               ↓
                                          Randomly pick Pexels or Pixabay API
                                                               ↓
                                          Normalize response to common format
                                                               ↓
Images Panel UI ← JSON Response ← Return results array
    ↓
Select/Upload → localStorage persistence → Copy URL to clipboard
```

### Key Files

| File | Purpose |
|------|---------|
| `imagesPanel.js` | Panel UI: search, color filters, category tabs, results grid, selection, upload |
| `images-panel.css` | Panel styling (search bar, color pills, grid, thumbnails, toast) |
| `app.py` | `/api/images/search` proxy route with Pexels + Pixabay providers |

### Configuration

```bash
# In ssr_python/.env — at least one key required
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
```

**Important:** After adding/changing API keys in `.env`, restart Flask (`python app.py`). The `load_dotenv()` call only runs at startup.

### API Provider Selection

- Both Pexels and Pixabay are available as providers
- On each request, available providers are **randomly shuffled** to spread rate limits
- If the selected provider fails (timeout, HTTP error), the other is tried as fallback
- Server normalizes both APIs to a common response format:

```json
{
  "results": [{
    "id": "string",
    "thumbUrl": "string",
    "smallUrl": "string",
    "regularUrl": "string",
    "fullUrl": "string",
    "photographer": "string",
    "photographerUrl": "string",
    "altText": "string",
    "width": 0,
    "height": 0,
    "source": "pexels|pixabay"
  }],
  "total": 0,
  "total_pages": 0,
  "source": "pexels|pixabay"
}
```

### Panel Features

- **Search bar** with debounced input (300ms) and Enter key support
- **Color filter pills** (red, orange, yellow, green, blue, purple, black, white)
- **Category tabs**: Backgrounds (landscape orientation) / Content (any orientation)
- **3-column results grid** with skeleton loading states
- **Selection**: Click card or + button to select; selected images persist in localStorage
- **Upload button**: Adds local files via `URL.createObjectURL()` (blob URLs)
- **Copy URL**: Click selected thumbnail to copy image URL to clipboard
- **Toast notifications** for user feedback

### Color Mapping

Colors are mapped differently per API:

| UI Color | Pexels Value | Pixabay Value |
|----------|-------------|---------------|
| purple | violet | lilac |
| (all others) | same | same |

---

## API Key Security

### Principles

- API keys are **NEVER** sent to the frontend or included in JSON responses
- API keys are **NEVER** included in user-facing error messages
- Full Python tracebacks are **NEVER** sent to frontend (logged server-side only)
- Environment variable names are **NEVER** revealed in error responses

### Implementation

**Server-side only access:**
- Pexels key: sent in `Authorization` HTTP header to Pexels API
- Pixabay key: sent as `key` query parameter to Pixabay API
- Ollama key: sent as `Bearer` token in `Authorization` header to Ollama API
- All three are read from `os.environ` (loaded from `.env` via `load_dotenv()`)

**Error sanitization pattern:**
```python
# CORRECT - log server-side, generic message to frontend
except Exception as e:
    app.logger.error(f"Detailed error: {traceback.format_exc()}")
    return jsonify({'error': 'Something went wrong. Please try again.'}), 500

# WRONG - never do this (may leak API keys in URLs or tracebacks)
except Exception as e:
    return jsonify({'error': str(e), 'details': traceback.format_exc()}), 500
```

**Gitignore protection:**
- `.env`, `*.env`, `.env.local` — all gitignored
- `ssr_python/logs/`, `*.log` — all gitignored
- Flask only serves `static/` directory — `.env` is not HTTP-accessible

### Sanitized Error Messages

| Endpoint | Error Condition | Frontend Message |
|----------|----------------|------------------|
| `/api/images/search` | No API keys configured | "Image search is not configured. Please contact the administrator." |
| `/api/images/search` | Search exception | "Image search failed. Please try again later." |
| `/api/chat` | No Ollama key | "AI chat is not configured. Please contact the administrator." |
| `/api/chat` | API exception | "Failed to get AI response. Please try again." |
| `/render` | Render exception | "A rendering error occurred. Check server logs for details." |

---

## Accent Color Highlights

All interactive elements in sidebar panels use the app accent color (`--accent: #9c9ef0`) for hover/active/focus states:

### Highlight Patterns

| Element | Hover Effect | Active/Selected Effect |
|---------|-------------|----------------------|
| `.sidebar-btn` | Accent color + accent-soft bg | Accent color + accent-soft bg |
| `.panel-close` | Accent color + accent-soft bg | — |
| `.viewport-btn` | Accent color + accent-soft bg | Accent border + accent-soft bg |
| `.tree-item-content` | Accent left border (3px) | Accent-soft bg + accent color |
| `.prop-section-header` | Accent left border (3px) | — |
| `.prop-input` | — | Accent border + glow ring on focus |
| `.token-pill` | Accent border + accent-soft bg | Solid accent bg + white text |
| `.color-input-swatch` | Accent border | — |
| `.theme-font-select` | Accent border | Accent border + glow ring on focus |
| `.theme-row` | Accent left border (3px) | Accent left border + accent-soft bg |
| `.images-color-pill` | Scale up | Accent border + glow |
| `.images-tab` | Text color change | Accent bottom border |

---

## Example Templates

Pre-built templates in `example_templates/` directory:

| Template | Description |
|----------|-------------|
| `bookstore_template.yaml` | Full bookstore website with navigation, hero, new arrivals, second-hand books (50% off), children's hard board books, arts & crafts, testimonials, newsletter, and footer |
| `freshchoice_template.yaml` | Patisserie/bakery/cafe website with navigation, store info bar, hero banner, shop categories (4-column grid), food items with "Add to Bag" buttons, signature cakes, beverages, about/story section, testimonials, location CTA, and footer. Uses Indian Rupee pricing. |

---

### Theme Color Swatches in Properties Panel
- **Added:** Quick-pick theme color swatches below every `color` type field in the Properties Panel
- **Source:** Reads current theme from `getCurrentTheme()` and iterates `THEME_COLOR_CONFIG` (imported from `themesPanel.js`)
- **Behavior:** Clicking a swatch sets the color value and stores the YAML anchor name in `data-yaml-alias`
- **Alias preservation:** When collecting property values, if a color field has `dataset.yamlAlias`, the alias (e.g., `*color-primary`) is preserved in YAML instead of the literal hex value
- **Files Modified:**
  - `propertiesPanel.js` — Imports `getCurrentTheme` and `THEME_COLOR_CONFIG` from `themesPanel.js`, renders `.color-theme-picks` row below color inputs
  - `style.css` — Added `.color-theme-picks` and `.color-theme-pick` styles (20x20px rounded buttons with accent hover)

```
┌─────────────────────────────────────┐
│  Color                              │
│  [██] [#4C4637              ]       │
│  (●)(●)(●)(●)  ← theme swatches    │
│  Pri Sec Acc Bg                     │
└─────────────────────────────────────┘
```

**Key code pattern (`propertiesPanel.js`):**
```javascript
for (const tc of THEME_COLOR_CONFIG) {
    const color = theme.colors[tc.key];
    pick.onclick = () => {
        textInput.value = color;
        swatch.style.background = color;
        colorPicker.value = color;
        textInput.dataset.yamlAlias = tc.anchor;  // Preserves *color-primary in YAML
    };
}
```

### Layout-Column Gap Property
- **Added:** `gap` property to `layout-column` component
- **Default:** `none` (no gap between children)
- **Schema:** `layout.gap` field with `gapScale` tokens (none, xxs, xs, sm, md, lg, xl, xxl, xxxl)
- **Rendering:** `build_flex_styles()` macro outputs `gap` CSS + `--layout-gap` CSS variable
- **Files Modified:**
  - `component_defaults.yaml` — Added `gap: none` under `layout-column.layout`
  - `component_schemas.yaml` — Added `layout.gap` select field with `gapScale` tokens
  - `_components.html` — `build_flex_styles()` macro reads `layout.gap`, maps to `tokens.spacing`, outputs CSS

```yaml
# Usage in YAML:
- name: layout-column
  properties:
    layout:
      gap: md           # Adds gap between child components
      horizontalAlign: center
```

```jinja2
{# In build_flex_styles() macro: #}
{% set gap_token = layout.gap | default('none') %}
{% if gap_token != 'none' %}
    {% set gap_value = tokens.spacing[gap_token] %}
    gap: {{ gap_value }};
    --layout-gap: {{ gap_value }};
{% endif %}
```

---

**Last Updated:** February 8, 2026
