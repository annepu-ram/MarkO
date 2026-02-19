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
python -m pytest tests/ -v          # Run test suite (30 tests)
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

### Core Rendering Flow

```
YAML Editor → POST /render → Flask Backend
                              ↓
                         renderer.py: render_yaml_structure()
                              ↓
                         Jinja2 Macros (templates/components/)
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
├── app.py                    # Flask app factory (create_app)
├── config.py                 # Config classes (Dev, Prod) with path constants
├── extensions.py             # Shared state: TOKENS, COMPONENT_DEFAULTS dicts
├── renderer.py               # Core rendering engine
├── llm_service.py            # Ollama AI integration for chat
├── tokens.yaml               # Design tokens (spacing, typography, etc.)
├── generate_tokens_css.py    # Token to CSS generator
├── requirements.txt          # Pinned Python dependencies
├── .env.example              # Environment variable template
├── config/                   # Config YAML files
│   ├── component_defaults.yaml   # Default properties per component type
│   ├── component_schemas.yaml    # Inspector form fields, types, token refs
│   └── schema_tokens.yaml        # Design token options for dropdowns
├── routes/                   # Flask Blueprint route modules
│   ├── __init__.py           # register_blueprints() function
│   ├── views.py              # GET /, GET /preview-frame
│   ├── render.py             # POST /render
│   ├── metadata.py           # GET /api/schemas, /api/defaults, /api/tokens
│   ├── images.py             # GET /api/images/search (Pexels/Pixabay proxy)
│   └── chat.py               # POST /api/chat (Ollama LLM)
├── tests/                    # pytest test suite (30 tests)
│   ├── conftest.py           # Fixtures: app, client, sample YAMLs
│   ├── fixtures/
│   │   └── sample_page.yaml  # Test fixture YAML
│   ├── test_renderer.py      # deep_merge + render tests
│   ├── test_routes.py        # API endpoint tests
│   └── test_security.py      # Security header + error sanitization tests
├── templates/
│   ├── index.html            # Main application UI (with iframe)
│   ├── preview_frame.html    # Iframe preview template
│   └── components/           # Split Jinja2 component macros (36 files)
│       ├── _assembly.html    # Include manifest (load order)
│       ├── _utilities.html   # build_styles + build_flex_styles macros
│       ├── _vars_builders.html # build_tabs_vars + build_accordion_vars
│       ├── _dispatcher.html  # render_component() dispatcher
│       ├── layout/           # page, layout-row, layout-column, columnsgrid, form
│       ├── interactive/      # tabs, accordion, carousel, hamburger, ticker
│       ├── text/             # heading, paragraph, eyebrow, caption, blockquote, link
│       ├── media/            # image, video, gif, video-background, media-caption
│       ├── ui/               # button, titlebar, br
│       ├── marketing/        # icon, badge, rating, progress-bar, counter-up, countdown
│       └── forms/            # textbox, textarea, dropdown, checkbox, radio, calendar
└── static/
    ├── css/
    │   ├── style.css         # Application UI styles
    │   ├── components.css    # Component-specific styles
    │   ├── preview-chrome.css # Chrome overlay styles for iframe
    │   ├── chat.css          # AI chat widget styles
    │   ├── images-panel.css  # Images panel styles (search, grid, upload)
    │   └── tokens.css        # Auto-generated CSS custom properties
    ├── js/
    │   ├── main.js           # Application bootstrap, toolbar actions, standalone export
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
    │   ├── customRenderers.js    # Complex property editors (accordion, tabs, links, ticker)
    │   ├── swift-sites-runtime.js # Standalone runtime for interactive components
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
    └── icon-sprite.svg       # SVG icon sprite
```

---

## App UI Layout

The application uses a two-row flex column layout:

```
.app-layout          (display: flex; flex-direction: column; height: 100vh)
  ├── .app-header    (flex-shrink: 0; height: 52px)   ← Toolbar row
  └── .app-container (flex: 1; display: flex)          ← Content row
       ├── .sidebar            ← Icon nav buttons
       ├── .sidebar-panels     ← Component tree, themes, images panels
       ├── .main-canvas        ← YAML editor + iframe preview
       └── .properties-section ← Properties inspector panel
```

### Toolbar Buttons (Header Actions)

| Button | ID | Action | Notes |
|--------|----|--------|-------|
| Undo | `undoBtn` | `historyManager.undo()` | Disabled when nothing to undo |
| Redo | `redoBtn` | `historyManager.redo()` | Disabled when nothing to redo |
| Fullscreen | `fullscreenBtn` | Opens fullscreen modal | CSS overlay modal, not native Fullscreen API |
| Clear | `clearBtn` | Clears YAML editor | Also clears history and sessionStorage |
| Export | `exportBtn` | Downloads standalone HTML | Self-contained `index.html` with inlined CSS/JS |

### Fullscreen Preview & Export

Both use `buildStandaloneHtml(renderedHtml)` in `main.js` which:
1. Fetches `tokens.css`, `components.css`, `swift-sites-runtime.js`, and `icon-sprite.svg`
2. Inlines everything into a self-contained HTML document
3. Escapes `</script>` in JS content to prevent HTML parser breakage: `runtimeJs.replace(/<\/script>/gi, '<\\/script>')`

- **Fullscreen:** Sets `iframe.srcdoc` with the standalone HTML, shows CSS overlay modal. Close with Escape key or X button.
- **Export:** Creates a Blob download of `index.html`.

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

---

## Python Files

### `app.py` - Flask App Factory

**Purpose:** Application factory (`create_app()`) that wires together config, extensions, Blueprints, and security headers.

**Key Responsibilities:**
- Load config from `config.py` (DevelopmentConfig / ProductionConfig)
- Register custom Jinja2 filters (`transparency_to_hex`, `hex_to_rgb`)
- Load shared data via `extensions.load_shared_data(app)`
- Register all Blueprint route modules via `routes.register_blueprints(app)`
- Attach security headers via `@app.after_request`

### `config.py` - Configuration Classes

**Purpose:** Centralized config with path constants. All file paths are resolved from `BASE_DIR`.

**Key Config Values:**
- `TOKENS_PATH` - Path to `tokens.yaml`
- `DEFAULTS_PATH` - Path to `config/component_defaults.yaml`
- `SCHEMAS_PATH` - Path to `config/component_schemas.yaml`
- `SCHEMA_TOKENS_PATH` - Path to `config/schema_tokens.yaml`
- `LLM_GUIDE_PATH` - Path to `LLM_COMPONENT_GUIDE.md`

### `extensions.py` - Shared State

**Purpose:** Module-level `TOKENS` and `COMPONENT_DEFAULTS` dicts that are imported by route modules.

**Pattern:** Uses `.clear()` + `.update()` to mutate in-place (preserves references across imports).

### `routes/` - Flask Blueprints

| Module | Blueprint | Routes |
|--------|-----------|--------|
| `views.py` | `views_bp` | `GET /`, `GET /preview-frame` |
| `render.py` | `render_bp` | `POST /render` |
| `metadata.py` | `metadata_bp` | `GET /api/schemas`, `/api/defaults`, `/api/tokens` |
| `images.py` | `images_bp` | `GET /api/images/search` |
| `chat.py` | `chat_bp` | `POST /api/chat` |

### `renderer.py` - Rendering Engine

**Purpose:** Core rendering logic converting YAML structures to HTML.

**Key Functions:**
- `render_yaml_structure(structure, tokens, defaults)` - Main entry point
- `_build_component_template(templates_dir)` - Concatenates split template files into single Jinja2 template
- `deep_merge(base, override)` - Recursive dictionary merging
- `merge_component_with_defaults(component, defaults, tokens)` - Merges YAML with defaults

**Flow:**
1. Validates structure and tokens
2. Calls `_build_component_template()` to concatenate all macro files from `templates/components/`
3. Creates Jinja2 environment and renders template with structure + tokens
4. Returns HTML string

---

## Template System (Split Component Macros)

### Architecture

The component templates are split into individual files under `templates/components/`. The `renderer.py` function `_build_component_template()` reads the manifest file `_assembly.html`, parses its `{% include %}` directives, and concatenates all files into a single template string at render time. This preserves Jinja2 macro scoping (macros from one file can call macros from another).

**Important:** Jinja2 `{% include %}` does NOT export macros to parent scope. That's why `renderer.py` concatenates file contents in Python rather than using Jinja2's native include.

**File Organization:**
| Directory | Files | Components |
|-----------|-------|------------|
| `components/` | `_utilities.html` | `build_styles()`, `build_flex_styles()` |
| `components/` | `_vars_builders.html` | `build_tabs_vars()`, `build_accordion_vars()` |
| `components/` | `_dispatcher.html` | `render_component()` main dispatcher |
| `layout/` | 5 files | page, layout-row, layout-column, columnsgrid, form |
| `interactive/` | 5 files | tabs, accordion, carousel, hamburger, ticker |
| `text/` | 1 file | All text components (heading, paragraph, eyebrow, caption, blockquote, link) |
| `media/` | 5 files | image, video, gif, video-background, media-caption |
| `ui/` | 3 files | button, titlebar, br |
| `marketing/` | 6 files | icon, badge, rating, progress-bar, counter-up, countdown |
| `forms/` | 6 files | textbox, textarea, dropdown, checkbox, radio, calendar |

### Key Macros

#### `render_component(component, tokens, path=[])` - Main Dispatcher (`_dispatcher.html`)
Routes components based on `component.name`:
- **Layout:** page, layout-row, layout-column, columnsgrid, form
- **Interactive:** tabs, accordion, carousel, hamburger, ticker
- **Text:** heading, paragraph, eyebrow, caption, blockquote, link
- **Media:** image, video, gif, video-background
- **UI:** button, titlebar, br
- **Marketing:** icon, badge, rating, progress-bar, counter-up, countdown
- **Forms:** textbox, textarea, dropdown, checkbox, radio, calendar

#### `build_styles(component, tokens, part=None)` - Style Generator (`_utilities.html`)
Generates inline CSS styles from component properties and design tokens.

#### `build_flex_styles(component, tokens, direction)` - Flex Layout (`_utilities.html`)
Generates flexbox styles for layout components.

---

## Complete Component Reference

### Layout Components
| Component | Container | Children Key | Purpose |
|-----------|-----------|-------------|---------|
| `page` | Yes | `components` | Root page wrapper with background, min-height |
| `layout-row` | Yes | `components` | Horizontal flex container with wrap control |
| `layout-column` | Yes | `components` | Vertical flex container with gap support |
| `columnsgrid` | Yes | `columns[].components` | CSS grid with configurable column count |
| `form` | Yes | `components` | HTML form element |

### Interactive Components
| Component | Container | Children Key | Purpose |
|-----------|-----------|-------------|---------|
| `tabs` | Yes | `tabs[].components` | Tabbed content panels |
| `accordion` | Yes | `items[].components` | Collapsible content sections |
| `carousel` | Yes | `slides[].components` | Image/content slideshow |
| `hamburger` | Yes | `components` | Mobile-friendly collapsible menu |
| `ticker` | Yes | `columns[].components` | Horizontally scrolling content strip |

### Text Components
| Component | Purpose |
|-----------|---------|
| `heading` | H1-H6 headings |
| `paragraph` | Body text |
| `eyebrow` | Small label above headings |
| `caption` | Small descriptive text |
| `blockquote` | Styled quotation |
| `link` | Hyperlink |

### Media Components
| Component | Purpose |
|-----------|---------|
| `image` | Responsive image with hover effects, filters, shadows |
| `video` | Embedded video (YouTube/Vimeo iframe) |
| `gif` | Animated GIF |
| `video-background` | Full-width video with overlay content |

### UI Components
| Component | Purpose |
|-----------|---------|
| `button` | Clickable button with gradient support |
| `titlebar` | Navigation bar with sticky scroll behavior |
| `br` | Visual divider (solid, dashed, wave, slant) |

### Marketing Components
| Component | Purpose | Key Properties |
|-----------|---------|----------------|
| `icon` | SVG vector symbols from sprite | name, size, color |
| `badge` | Status/highlight labels (Sale, New) | text, variant, pill |
| `rating` | Star/heart trust indicators (1-5) | value, iconType, showCount, color |
| `progress-bar` | Completion/stock visualization | percent, thickness, color |
| `counter-up` | Animated number on viewport entry | endValue, duration, prefix, suffix |
| `countdown` | Live countdown timer | targetDate, format, expiredText |

### Form Components
| Component | Purpose |
|-----------|---------|
| `textbox` | Single-line text input |
| `textarea` | Multi-line text input |
| `dropdown` | Select dropdown |
| `checkbox` | Checkbox input |
| `radio` | Radio button group |
| `calendar` | Date picker |

---

## Ticker Component

A horizontally scrolling strip of content using `columns:` array (columnsgrid-like pattern). Background is always transparent; column background is configurable.

### YAML Structure
```yaml
- name: ticker
  properties:
    behavior:
      direction: left           # left, right
      speed: 40                 # pixels per second (continuous mode)
      mode: continuous          # continuous, step
      pauseOnHover: true
      pauseDuration: 3000       # ms between items (step mode only)
    layout:
      width: "280"              # pixel-based column width (120, 200, 280, 360, 480, fit)
    spacing:
      marginBlock: md
      marginInline: none
      gap: lg
    appearance:
      columnBackground: '#ffffff'  # uniform background for all columns
      columnTransparency: 0        # 0=transparent, 100=opaque (same default as layout-column)
      columnRadius: none           # border radius token (none, xs, sm, md, lg, xl, xxl, pill)
      columnBorder:
        width: 0                   # border width px (0=no border)
        style: solid               # solid, dashed, none
        color: '#000000'           # border color
  columns:                      # component-level array (NOT inside properties)
    - components:
        - name: heading
          properties:
            text: Card Title
    - components:
        - name: paragraph
          properties:
            text: Content
```

### How It Works

**ColumnsGrid-like structure:**
- Uses `columns:` array at component level (same pattern as columnsgrid)
- Each column is a data container with `components:` — no need to specify `layout-column`
- Children are rendered with `'column'` parent direction
- Any component type can be placed directly inside a column

**Ticker-level `layout.width` (pixel-based with CSS clamp):**
- Applied uniformly to ALL columns via `data-width-mode` attribute on the ticker element
- Default (`fit`) = content-sized columns, no explicit width set
- Pixel sizes use CSS `clamp(min, preferred-vw, max)` for responsive behavior:
  - `"120"` → `clamp(80px, 12vw, 120px)` — compact (logos, badges)
  - `"200"` → `clamp(120px, 18vw, 200px)` — small text cards
  - `"280"` → `clamp(180px, 24vw, 280px)` — standard cards
  - `"360"` → `clamp(240px, 30vw, 360px)` — featured cards
  - `"480"` → `clamp(300px, 38vw, 480px)` — hero cards
- Width applied via CSS data-attribute selectors in `components.css` — no JS needed

**Column duplication (all modes):**
- Columns duplicated in Jinja2 template for seamless infinite looping
- Duplicates have `class="ticker-item-duplicate"` and `aria-hidden="true"`

**Continuous mode:**
- CSS `@keyframes ticker-scroll` uses `var(--ticker-offset)` for precise translateX
- Pause on hover via `animation-play-state: paused` (pure CSS)

**Step mode:**
- JS `setInterval` moves track one item width at a time
- CSS `transition: transform 0.6s ease-in-out` for smooth movement

**Gap parsing — use computed `gap`, not CSS variables:**
- `getComputedStyle(track).gap` returns computed pixel values (e.g., `"32px"`)
- Never use `getPropertyValue('--ticker-gap')` which returns raw `"2rem"`

### Files
| File | Purpose |
|------|---------|
| `templates/components/interactive/_ticker.html` | Jinja2 macro, columnsgrid-like columns pattern |
| `static/css/components.css` | Ticker CSS with `@keyframes ticker-scroll` using `var(--ticker-offset)` |
| `static/js/swift-sites-runtime.js` | Continuous/step init, cleanup, resize handlers (widths via CSS) |
| `config/component_defaults.yaml` | Default ticker config with `columns:` structure |
| `config/component_schemas.yaml` | Schema with behavior, layout, spacing, appearance groups |

---

## Titlebar Component

The titlebar has special scroll behavior with a clone-based sticky implementation.

### How It Works
1. When titlebar initializes, `swift-sites-runtime.js` creates a hidden clone
2. Clone has `position: fixed; top: 0` and is initially hidden
3. On scroll, when original titlebar's bottom edge goes above viewport, clone shows
4. Both original and clone get `.scrolled` class for shrink effect

### Shrink Effect
- Logo and title shrink based on `shrinkPercentage` property (default: 30%)
- Menu items do NOT shrink - only logo and title
- CSS variable `--shrink-scale` controls shrink amount

---

## Runtime JavaScript (`swift-sites-runtime.js`)

Standalone JavaScript for interactive components in both the preview and exported sites.

### Initialization
```javascript
SwiftSites.init() → calls:
    initCarousels()
    initTabs()
    initAccordions()
    initTitlebars()
    initTickers()
    initCounterUps()
    initCountdowns()
```

### Reset (called before re-render)
```javascript
SwiftSites.reset() → calls:
    cleanupCountdowns()
    cleanupTickers()
    // Removes data-ss-initialized from all elements
    // Cleans up titlebar clones
```

### Init Guard Pattern
All components use `data-ss-initialized` to prevent double-initialization:
```javascript
if (element.dataset.ssInitialized === 'true') return;
element.dataset.ssInitialized = 'true';
```

---

## Client-Side JavaScript Modules

### Core Application

| Module | Purpose |
|--------|---------|
| `main.js` | Application bootstrap, toolbar actions (undo/redo/fullscreen/export), standalone HTML builder |
| `ssr_app.js` | SSR rendering bridge, iframe postMessage communication |
| `preview_bridge.js` | Runs in iframe, handles content updates and click relay |
| `events.js` | Event listeners (editor, preview, buttons, keyboard, Escape key for fullscreen) |

### State Management

| Module | Purpose |
|--------|---------|
| `selectionManager.js` | Component selection state and highlighting |
| `pathMapBuilder.js` | Maps component IDs to YAML paths |
| `historyManager.js` | Undo/redo stacks (max 50 states) |
| `yamlStorage.js` | SessionStorage persistence (survives tab refresh, lost on tab close) |

### Properties System

| Module | Purpose |
|--------|---------|
| `propertiesPanel.js` | Renders form fields from schema, theme color swatches |
| `metadataLoader.js` | Loads schemas, defaults, tokens from API |
| `customRenderers.js` | Complex editors: accordionItems, tabsEditor, linksEditor, tickerItems |
| `yamlUtils.js` | YAML parsing, component updates, Document API for anchor preservation |

### Component Support

| Module | Purpose |
|--------|---------|
| `componentTree.js` | Component hierarchy tree UI |
| `swift-sites-runtime.js` | Standalone runtime for interactive components (carousel, tabs, accordion, titlebar, ticker, counter-up, countdown) |

### UI Panels

| Module | Purpose |
|--------|---------|
| `themesPanel.js` | Theme selection, `THEME_COLOR_CONFIG` constant, color anchor management |
| `imagesPanel.js` | Stock photo search (Pexels/Pixabay), selection, upload |
| `chat.js` + `chatService.js` | AI chat widget using Ollama |

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

### Selection Flow

```
1. User clicks in iframe preview
   ↓
2. preview_bridge.js: handleClick() finds [data-component-id]
   ↓
3. postMessage COMPONENT_CLICKED to parent
   ↓
4. ssr_app.js: dispatches 'iframe-component-clicked' event
   ↓
5. selectionManager handles selection, dispatches 'swift-selection-changed' event
   ↓
6. postMessage SET_SELECTION back to iframe for highlighting
   ↓
7. Properties panel renders form for component
```

### Selection Event System

```javascript
// selectionManager.js dispatches on select/clear
window.dispatchEvent(new CustomEvent('swift-selection-changed', {
    detail: { componentId, path }
}));
```

Multiple modules listen: properties panel, chat widget, component tree.

---

## Adding New Components to SSR

1. **Create Template** in `templates/components/<category>/_mycomponent.html`:
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

2. **Add to Assembly** (`_assembly.html`) - include the new file

3. **Add to Dispatcher** (`_dispatcher.html`) - add `{% elif name == 'mycomponent' %}` route

4. **Add CSS** (`static/css/components.css`)

5. **Add Defaults** (`config/component_defaults.yaml`)

6. **Add Schema** (`config/component_schemas.yaml`)

7. **Add Runtime JS** (if interactive) - add init method to `swift-sites-runtime.js`

8. **Add Custom Renderer** (if needed) - add to `customRenderers.js` for complex property editors

**Note:** `renderer.py` auto-discovers template files via `_assembly.html` — no changes needed there.

---

## Architecture Conventions

### Boolean Data Attributes
Jinja2 templates must use lowercase string `'true'`/`'false'` for boolean data attributes:
```jinja2
data-autoplay="{{ 'true' if behavior.autoplay else 'false' }}"
```
JavaScript reads these with `element.dataset.autoplay === 'true'`. Using `{{ behavior.autoplay }}` outputs Python `True`/`False` which won't match.

### Component-Level vs Properties Arrays
Some components have arrays at the component level (not inside `properties`):
- `carousel` → `component.slides`
- `tabs` → `component.tabs`
- `accordion` → `component.items`
- `ticker` → `component.columns`

These use `target: component` in the schema and are handled separately from properties during YAML updates.

### YAML Anchor/Alias Preservation
When editing properties through the panel, use the Document API to preserve theme anchors:
```javascript
const doc = parseDocument(yamlContent);
const componentNode = navigateToComponent(doc, componentPath);
updateComponentPropertiesInDocument(doc, path, values);
const yamlText = stringifyDocument(doc);  // Anchors preserved!
```

### Theme Color System
Theme colors use YAML anchors for global updates:
```yaml
primary: &color-primary '#1e293b'
# ... referenced as:
color: *color-primary
```

`THEME_COLOR_CONFIG` in `themesPanel.js` is the single source of truth for color keys, anchor names, and labels. The properties panel shows theme color swatches below every color field.

### Inline Styles vs CSS Variables
- **CSS Variables:** Tabs, accordion, titlebar, blockquote (complex styles consumed by `components.css`)
- **Inline Styles:** Everything else via `build_styles()` macro

### Gradient Background Support
```yaml
appearance:
  background:
    type: gradient  # 'solid' or 'gradient'
    gradient:
      colorStart: '#ff0000'
      colorEnd: '#0000ff'
      direction: 'to right'
```

### Image Hover Effects with Filters
CSS `--base-filter` custom property combines inline filters with hover effects:
```css
filter: var(--base-filter, none) brightness(0.85);
```

### Responsive Font Sizing
Preview uses fluid typography: `clamp(12px, 1vw + 8px, 18px)` on root. Component fonts use `rem` units. UI fonts remain fixed.

---

## Metadata Files

The following metadata files must stay synchronized:

| File | Purpose |
|------|---------|
| `component_defaults.yaml` | Default properties for each component type |
| `component_schemas.yaml` | Inspector form fields, types, labels, token refs |
| `schema_tokens.yaml` | Design token options for dropdowns |
| `tokens.yaml` | CSS token values (snake_case keys) |
| `LLM_COMPONENT_GUIDE.md` | LLM-friendly guide for YAML generation |

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

## Data Model

### YAML Structure

- Root: array with single `{ name: 'page', properties, components }` object
- **Simple components**: `{ name, properties }` with typography, spacing, layout, appearance
- **Container components**: Add nested `components`, `columns`, `tabs`, `slides`, or `items`

### Component Path Map

Maps DOM IDs to YAML paths:
- `comp_0` → `[0]`
- `comp_0_components_1` → `[0, 'components', 1]`
- `comp_0_columns_0_components_2` → `[0, 'columns', 0, 'components', 2]`

---

## AI Chat Feature

An AI-powered chat widget that generates and modifies YAML from natural language using Ollama AI.

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
OLLAMA_API_KEY=your_api_key_here

# Optional (defaults shown)
OLLAMA_BASE_URL=https://ollama.com  # or http://localhost:11434 for local
OLLAMA_MODEL=llama3:latest
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120                  # seconds
```

### Response Handling
- LLM returns responses with `<!-- ACTION: type -->` comments: `create`, `modify`, `explain`, `error`
- YAML extracted from markdown code blocks, validated before display
- Logs to `ssr_python/logs/llm_chat.log` (gitignored)

---

## Images Panel (Stock Photo Search)

### Key Files

| File | Purpose |
|------|---------|
| `imagesPanel.js` | Panel UI: search, color filters, category tabs, results grid |
| `images-panel.css` | Panel styling |
| `routes/images.py` | `/api/images/search` proxy with Pexels + Pixabay providers |

### Configuration

```bash
# In ssr_python/.env - at least one key required
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
```

Providers are randomly shuffled per request to spread rate limits, with fallback to the other if one fails.

---

## API Key Security

- API keys are **NEVER** sent to the frontend or included in JSON responses
- API keys are **NEVER** included in user-facing error messages
- Full Python tracebacks are **NEVER** sent to frontend (logged server-side only)
- `.env`, `*.env`, `*.log` are all gitignored

**Error sanitization pattern:**
```python
except Exception as e:
    app.logger.error(f"Detailed error: {traceback.format_exc()}")
    return jsonify({'error': 'Something went wrong. Please try again.'}), 500
```

---

## Example Templates

Pre-built templates in `example_templates/` directory:

| Template | Description |
|----------|-------------|
| `bookstore_template.yaml` | Full bookstore with navigation, hero, book categories, testimonials, footer |
| `freshchoice_template.yaml` | Patisserie/bakery/cafe with navigation, shop categories grid, food items |
| `bakery_template.yaml` | Bakery landing page |
| `car_dealer_template.yaml` | Car dealership website |
| `restaurant_template.yaml` | Restaurant website |
| `logistics_template.yaml` | Logistics/shipping company |
| `conference_template.yaml` | Conference/event website |
| `hero_template.yaml` | Hero section examples |
| `all_components_showcase.yaml` | Showcase of all available components |
| `marketing_components_template.yaml` | Marketing component examples |

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

**Properties panel not updating?**
- Check console for `[SSR App] Built path map with X components`
- Click component and look for `[SSR App] COMPONENT_CLICKED received`
- Verify `[SelectionManager] Path lookup result` shows array (not null)

**YAML not persisting across refresh?**
- Uses `sessionStorage` (tab-scoped) - each tab has isolated storage
- Content is lost when browser/tab closes
- Check `sessionStorage.getItem('swift_sites_yaml_content')` in console

**Fullscreen showing raw JavaScript?**
- `buildStandaloneHtml()` escapes `</script>` in inlined JS content
- Do not put literal `</script>` tags in JS comments in `swift-sites-runtime.js`

---

## Legacy CSR Reference

The client-side rendering version exists in the root `js/` directory, entry point `index.html`.

| Feature | CSR | SSR |
|---------|-----|-----|
| Rendering | Browser (JavaScript) | Server (Python/Jinja2) |
| Preview Isolation | Same document | Iframe |
| Communication | Direct DOM | postMessage API |

---

**Last Updated:** February 16, 2026
