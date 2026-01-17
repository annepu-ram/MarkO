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
├── tokens.yaml               # Design tokens (spacing, typography, etc.)
├── generate_tokens_css.py    # Token to CSS generator
├── requirements.txt          # Python dependencies (Flask, PyYAML)
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
    │   ├── js-yaml.min.js        # YAML parser library (local copy)
    │   └── utils/
    │       ├── object.js     # Deep clone, merge, nested get/set
    │       └── timing.js     # Debounce helper
    └── icon-sprite.svg       # SVG icon sprite
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
| `COMPONENT_PROPERTIES_MATRIX.md` | Cross-tabulation of components vs properties |
| `LLM_COMPONENT_GUIDE.md` | LLM-friendly guide for YAML generation |

---

## Recent Fixes (January 2025)

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

**Last Updated:** January 2025
