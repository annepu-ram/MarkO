# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Swift Sites** is a client-side YAML-based website builder. Users write YAML in an editor, and the application renders a live preview with interactive chrome for selection and editing. The YAML structure is the single source of truth — all changes flow through it, ensuring the preview, properties panel, history, and export stay synchronized.

DO NOT READ node_modules into context. they are not necessary.

## Commands

### Testing
```bash
npm test                                    # Run all Jest tests
npm test -- js/render/__tests__/index.test.js  # Run specific test file
npx jest <test> --updateSnapshot            # Update snapshot tests
```

### Build
```bash
npm run build:sprite                        # Rebuild SVG icon sprite from Feather icons subset
```

### Development
- Open `index.html` in a browser with Live Server or equivalent
- No build step required for runtime; it's a static SPA

## Architecture Overview

The application is organized into distinct subsystems:

### Core Flow

```
YAML Editor → parseYamlContent() → State.yamlStructure
    ↓
    ├→ User edits/inserts component → State mutation → renderYamlStructure() → Preview DOM
    │                                                      ├→ Preview mode: wrapComponentWithChrome()
    │                                                      └→ Export mode: clean HTML
    └→ generateYamlFromStructure() → History / Export
```

**Key principle:** The YAML editor is the single source of truth. All state changes (property edits, component insertion, undo/redo) update the YAML first, then trigger re-rendering.

### Module Responsibilities

**`js/core/`** — Application foundation
- `app.js`: Bootstrap, DOM initialization, metadata loading orchestration
- `state.js`: Global state manager (YAML structure, selection, history, component path map)
- `yaml.js`: YAML parsing/serialization using `js-yaml`, tree mutation helpers
- `templates.js`: Loads `component_defaults.yaml`, `component_schemas.yaml`, `schema_tokens.yaml`

**`js/render/`** — Rendering engine
- `index.js`: Main renderer. Routes components to specialized renderers or `renderSimpleComponent()`
- Modes: `preview` (with chrome) vs `export` (clean HTML)
- `wrapComponentWithChrome()`: Wraps preview components in interactive overlay with `rendered-component` wrapper, `chrome-overlay` for UI, `component-anchor` with `display: contents` for actual HTML
- `generateComponentInnerHTML()`: Merges default classes, applies inline styles from tokens/properties
- `registerComponentPath()`: Maps DOM IDs to YAML paths for selection/deletion

**`js/properties/`** — Properties inspector
- `index.js`: Renders properties panel from `component_schemas.yaml`, applies changes back to YAML
- `customRenderers.js`: Custom UI for complex properties (links editor, accordion items, carousel slides, tabs)

**`js/ui/`** — User interaction
- `events.js`: Wires up all event listeners (editor input, preview clicks, buttons, keyboard shortcuts)
- `actions.js`: Performs actions like parsing/rendering YAML, inserting/deleting components, applying properties, undo/redo

**`js/utils/`** — Shared utilities
- `object.js`: Deep cloning, merging, nested get/set
- `strings.js`: `escapeHtml()` and string helpers
- `styles.js`: Unit conversion (`toRem()`), resolving design tokens to CSS values
- `timing.js`: `debounce()`
- `sprite.js`: SVG sprite management for icons

**`js/component_interactions.js`** — Runtime initializers for interactive components (carousels, titlebars, etc.)

### Data Model

**YAML Structure:**
- Root: array with single `{ name: 'page', properties, components }` object
- **Simple components**: `{ name, properties }` where properties contain typography, spacing, layout, appearance, content
- **Container components**: Add nested structures like `components` (generic array), `columns` (grid columns), `tabs`, `slides`, `content.components`

**Metadata Files:**
- `component_defaults.yaml`: Default properties for each component type (used on insertion)
- `component_schemas.yaml`: Defines inspector form fields, types, labels, token references
- `schema_tokens.yaml`: Design token maps (spacing scales, typography sizes, colors, etc.)

**Component Path Map (`js/core/state.js`):**
- Maps DOM IDs → YAML paths (e.g., `comp-0-components-1` → `[0].components[1]`)
- Enables selection, deletion, focus restoration after re-render

## Rendering Pipeline Details

1. **Entry**: `renderYamlStructure(structure, mode)` in `js/render/index.js`
   - Clears component path map (preview only)
   - Iterates root-level components, calls `renderComponent()` for each

2. **Component Routing**: `renderComponent(component, path, mode)`
   - Routes known components (`layout-row`, `titlebar`, `image`, `form`, etc.) to specialized renderers
   - Falls back to `renderSimpleComponent()` for text components

3. **Chrome Wrapping** (preview mode only):
   - `wrapComponentWithChrome()` injects chrome directly into component HTML (zero wrapper approach):
     - Adds `.chrome-target` class and `data-component-id` attribute to component element
     - Injects `<span class="chrome-label">` and `<button class="chrome-delete">` as first children
     - Adds `position: relative` to component for chrome positioning
   - Chrome elements are absolutely positioned above component using CSS
   - This approach ensures zero layout interference - component participates directly in parent's flex/grid context

4. **HTML Generation**: `generateComponentInnerHTML()`
   - Merges default classes from `component_defaults.yaml`
   - Applies inline styles from properties and design tokens
   - Handles special cases: text components with multiline, width modes, spacing

5. **Post-render**: `initializeAllComponents()`
   - Runs after every preview render
   - Initializes interactive components (carousels, titlebars) via `js/component_interactions.js`

## Critical Patterns

### State Mutation Flow
Always update state through `js/core/state.js` helpers:
- `setYamlStructure(structure)` — Updates YAML structure
- `setSelectedComponent(path, id)` — Updates selection
- `pushHistory(yamlText)` — Snapshots for undo/redo

Never mutate `State.yamlStructure` directly without re-rendering.

### Preview Chrome Architecture
Chrome uses a zero-wrapper approach where chrome elements are injected directly into the component. If you modify chrome structure:
- Chrome class `.chrome-target` is added directly to the component element
- Chrome children (`.chrome-label` and `.chrome-delete`) are injected as first children
- Component must have `position: relative` for chrome absolute positioning
- Ensure component IDs are registered with `registerComponentPath()`
- All width/flex styles are applied directly to the component (no wrapper divs)

### Adding New Components
When adding a new component:
1. Add default properties to `component_defaults.yaml`
2. Add schema definition to `component_schemas.yaml`
3. Add renderer in `js/render/index.js` (or reuse existing renderer)
4. Update tests in `js/render/__tests__/index.test.js`
5. Add to component palette in `index.html` if needed

### Metadata Synchronization
The three metadata files must stay synchronized:
- `component_defaults.yaml` — provides fallback values
- `component_schemas.yaml` — defines inspector UI
- `schema_tokens.yaml` — provides dropdown options from design tokens

When adding a new property, update all three files and relevant tests.

## Testing Strategy

**Unit tests** cover:
- Renderer output (snapshot tests in `js/render/__tests__/`)
- State helpers (`js/core/__tests__/`)
- Utility functions (`js/utils/__tests__/`)
- UI behavior (`js/ui/__tests__/`)
- YAML round-tripping (multiline text, block scalars)

**Snapshot tests** ensure rendered HTML stays stable. Update intentionally with `--updateSnapshot` flag.

**Test organization:**
- Tests live in `__tests__/` directories adjacent to source files
- Use descriptive test names that explain the scenario being tested

## Known Constraints

1. **YAML Editor Only**: No visual drag-and-drop. Users must edit YAML directly or use properties panel. Layout tree UI is planned.

2. **Static Export**: Export produces static HTML. No asset bundling, CSS extraction, or build pipeline yet.

3. **Component Path Map Fragility**: Path map must be rebuilt on every preview render. Ensure all components call `registerComponentPath()`.

## Recent Work Context

### Accordion Component Fixes (October 2024)

1. **Background Color Application** ([js/render/index.js](js/render/index.js#L746-L801))
   - Background color now applies to `.accordion-summary` and `.card-body` instead of container
   - Container remains transparent for proper visual separation

2. **Duplicate Items Array Bug** ([js/properties/index.js](js/properties/index.js#L524))
   - Fixed by moving default merge BEFORE custom editor values are applied
   - Prevents duplicate `items` arrays in YAML when adding new items

3. **Unwanted Components Element** ([js/ui/actions.js](js/ui/actions.js#L271-L275))
   - Removed `content: { components: [] }` from accordion insertion
   - Accordion is now a simple component, not a container

4. **Multiline Content Support** ([component_defaults.yaml](component_defaults.yaml#L413-L415))
   - Accordion content now uses YAML pipe operator (`|`) for multiline text
   - Leverages existing `escapeHtmlWithLineBreaks()` rendering

5. **Default Colors Updated** ([component_defaults.yaml](component_defaults.yaml#L422-L426))
   - Title and content text: `#000000` (black)
   - Background: `#ffffff` (white)

### Chrome Architecture
- **Zero-wrapper chrome**: Chrome elements injected directly into components
  - No wrapper divs interfering with layout
  - Component participates directly in parent's flex/grid context
  - All width/flex styles applied to component element

### Text Components
- Multiline text support using YAML block scalars (`|`)
- Width modes: fit/percentage/stretch
- Logical spacing: `marginBlock`, `marginInline`, `paddingBlock`, `paddingInline`

### Other
- **Titlebar**: Resizing bars, layout adjustments
- **SVG sprite system**: Icon management via `js/utils/sprite.js`

## Troubleshooting

**Preview not updating?**
- Check browser console for YAML parse errors
- Ensure `renderYamlStructure()` is called after state changes
- Verify component path map is being rebuilt

**Properties panel empty?**
- Check that component schema exists in `component_schemas.yaml`
- Verify selection state is set correctly
- Check console for schema resolution errors

**Component not rendering?**
- Verify default exists in `component_defaults.yaml`
- Check renderer routing in `js/render/index.js`
- Look for HTML escaping issues in text content

**Tests failing?**
- Run `npm test -- --updateSnapshot` if intentional changes to output
- Check that metadata files are synchronized
- Verify test mocks match current component structure

---

# Server-Side Rendering (SSR) Architecture

## Overview

**Swift Sites SSR** is a Python Flask-based server-side rendering implementation that converts YAML structures to HTML on the server. Unlike the client-side version, rendering happens server-side using Jinja2 templates, providing better SEO, faster initial page loads, and server-side validation.

**Key Differences from Client-Side:**
- Rendering happens on the server (Flask + Jinja2)
- No interactive chrome overlays (preview-only mode)
- Design tokens loaded from `ssr_python/tokens.yaml`
- HTML generated server-side and sent to client
- Client-side JavaScript only handles UI interactions (editor, preview updates)

## SSR Directory Structure

```
ssr_python/
├── app.py                    # Flask application entry point
├── renderer.py               # Core rendering engine
├── tokens.yaml               # Design tokens (spacing, typography, etc.)
├── requirements.txt          # Python dependencies
├── templates/
│   ├── index.html           # Main application UI
│   └── macros/
│       └── _components.html # Jinja2 component macros
└── static/
    ├── css/                 # Stylesheets
    │   ├── style.css        # Application UI styles
    │   └── components.css   # Component styles
    └── js/                  # Client-side JavaScript
        ├── main.js          # Application entry point
        ├── ssr_app.js       # SSR-specific client code
        └── component_interactions.js  # Interactive component init
```

## Python Files Explained

### `ssr_python/app.py` - Flask Application

**Purpose:** Main Flask application that handles HTTP requests and routes.

**Key Functions & Variables:**

#### **Global Variables:**
- `app = Flask(__name__)` - Flask application instance
- `TOKENS = {}` - Global dictionary storing design tokens loaded from `tokens.yaml`
- `BASE_DIR` - Directory where `app.py` is located (for finding `tokens.yaml`)
- `tokens_path` - Absolute path to `tokens.yaml` file

#### **Token Loading (Lines 8-20):**
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
tokens_path = os.path.join(BASE_DIR, 'tokens.yaml')

if os.path.exists(tokens_path):
    with open(tokens_path, 'r') as f:
        TOKENS = yaml.safe_load(f)
    print(f"Loaded tokens from {tokens_path}")
    print(f"Tokens keys: {TOKENS.keys() if TOKENS else 'None'}")
else:
    print(f"Warning: tokens.yaml not found at {tokens_path}")
```

**How it works:**
1. Gets the directory where `app.py` is located
2. Constructs absolute path to `tokens.yaml` in the same directory
3. Loads YAML file using `yaml.safe_load()` (safe from code injection)
4. Stores tokens in global `TOKENS` dictionary
5. Prints debug info about loaded tokens

**Why absolute path?** Ensures tokens load correctly regardless of where Flask is run from.

#### **Route: `@app.route('/')` (Lines 22-24)**
```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Purpose:** Serves the main application UI page.

**Returns:** Rendered `templates/index.html` with Flask template variables (like `url_for()` for static files).

#### **Route: `@app.route('/render', methods=['POST'])` (Lines 26-54)**
```python
@app.route('/render', methods=['POST'])
def render_from_yaml():
    try:
        yaml_data = request.get_data(as_text=True)
        structure = yaml.safe_load(yaml_data)
        html_content = render_yaml_structure(structure, tokens=TOKENS)
        return html_content
    except yaml.YAMLError as e:
        # Handle YAML parsing errors
    except Exception as e:
        # Handle rendering errors
```

**Purpose:** Main rendering endpoint. Accepts YAML, returns HTML.

**Flow:**
1. **Receive YAML** - Gets raw YAML text from POST request body
2. **Parse YAML** - Uses `yaml.safe_load()` to convert YAML string to Python dict/list
3. **Render HTML** - Calls `render_yaml_structure()` with parsed structure and tokens
4. **Return HTML** - Sends rendered HTML back to client

**Error Handling:**
- **YAML Errors** (Lines 35-41): Catches `yaml.YAMLError` and provides detailed error messages with line/column numbers
- **Rendering Errors** (Lines 42-54): Catches all other exceptions (template errors, iteration errors) and returns full traceback for debugging

**Why `safe_load()`?** Prevents code injection attacks by only loading safe YAML constructs.

---

### `ssr_python/renderer.py` - Rendering Engine

**Purpose:** Core rendering logic that converts YAML structures to HTML using Jinja2 templates.

#### **Function: `render_yaml_structure(structure, tokens=None)` (Lines 5-38)**

**Signature:**
```python
def render_yaml_structure(structure, tokens=None):
```

**Parameters:**
- `structure` - Parsed YAML structure (list of component dictionaries)
- `tokens` - Design tokens dictionary (defaults to empty dict if None)

**Returns:** HTML string

**Flow:**

1. **Token Validation (Lines 9-14):**
   ```python
   if tokens is None:
       tokens = {}
   if not isinstance(tokens, dict):
       raise Exception(f"Tokens must be a dict, got {type(tokens)}")
   ```
   - Ensures tokens is a dictionary (prevents iteration errors)

2. **Structure Validation (Lines 16-17):**
   ```python
   if not isinstance(structure, list) or not structure:
       return "<!-- Invalid YAML: Root should be a list of components -->"
   ```
   - Validates root structure is a non-empty list
   - Returns HTML comment if invalid (graceful degradation)

3. **Template Definition (Lines 21-26):**
   ```python
   template = """
       {% import 'macros/_components.html' as components %}
       {% for component in structure %}
           {{ components.render_component(component, tokens) }}
       {% endfor %}
   """
   ```
   - Defines Jinja2 template string
   - Imports component macros from `_components.html`
   - Iterates through root-level components
   - Calls `render_component()` macro for each component

4. **Template Rendering (Line 28):**
   ```python
   return render_template_string(template, structure=structure, tokens=tokens)
   ```
   - Uses Flask's `render_template_string()` to render Jinja2 template
   - Passes `structure` and `tokens` as template variables
   - Returns final HTML string

5. **Error Handling:**
   - **TemplateSyntaxError** (Lines 29-32): Catches Jinja2 syntax errors, provides file/line info
   - **TypeError** (Lines 33-37): Catches iteration errors (e.g., trying to iterate over dict methods), provides detailed debugging info

**Key Design Decisions:**
- **Template String vs File:** Uses `render_template_string()` because template is simple and dynamic
- **Macro Import:** Imports `_components.html` macros to keep component logic separate
- **Recursive Rendering:** Each component macro can call `render_component()` recursively for nested components
- **Token Passing:** Tokens passed through entire rendering chain for style generation

---

## Design Tokens System (`tokens.yaml`)

### File Location
`ssr_python/tokens.yaml` - Loaded at Flask startup

### Structure

```yaml
spacing:
  none: '0'
  xxs: '0.3rem'
  xs: '0.6rem'
  sm: '1.2rem'
  md: '2rem'
  lg: '3rem'
  xl: '5rem'
  xxl: '8rem'
  xxxl: '12rem'
  auto: 'auto'

typography_sizes:
  xxs: '0.9rem'
  xs: '1.1rem'
  sm: '1.4rem'
  md: '1.8rem'
  lg: '2.2rem'
  xl: '3rem'
  xxl: '4.5rem'
  xxxl: '6rem'
  auto: 'auto'

font_weights:
  light: '300'
  regular: '400'
  medium: '500'
  semibold: '600'
  bold: '700'
  extrabold: '800'

border_radius:
  none: '0'
  sm: '0.3rem'
  md: '0.75rem'
  lg: '1.5rem'
  pill: '9999px'

letter_spacing:
  normal: 'normal'
  tight: '-0.025em'
  wide: '0.025em'
  wider: '0.05em'
```

### How Tokens Are Used

#### **1. Loading (app.py)**
- Loaded once at Flask startup
- Stored in global `TOKENS` dictionary
- Available to all rendering requests

#### **2. Passing to Templates (renderer.py)**
- Passed as `tokens` parameter to `render_yaml_structure()`
- Available in all Jinja2 templates via `tokens` variable

#### **3. Style Generation (`_components.html`)**
The `build_styles()` macro uses tokens to convert semantic values to CSS:

**Example - Spacing:**
```jinja2
{# YAML: spacing: { marginBlock: 'md' } #}
{% if spacing.marginBlock and tokens and tokens.spacing and spacing.marginBlock in tokens.spacing %}
    {% set _ = styles.append('margin-block: ' ~ tokens.spacing[spacing.marginBlock] ~ ';') %}
{% endif %}
{# Result: margin-block: 2rem; #}
```

**Example - Typography:**
```jinja2
{# YAML: typography: { size: 'xl', weight: 'bold' } #}
{% if typo.size and tokens and tokens.typography_sizes and typo.size in tokens.typography_sizes %}
    {% set _ = styles.append('font-size: ' ~ tokens.typography_sizes[typo.size] ~ ';') %}
{% endif %}
{# Result: font-size: 3rem; #}
```

**Example - Border Radius:**
```jinja2
{# YAML: appearance: { radius: 'md' } #}
{% if appearance.radius and tokens and tokens.border_radius and appearance.radius in tokens.border_radius %}
    {% set _ = styles.append('border-radius: ' ~ tokens.border_radius[appearance.radius] ~ ';') %}
{% endif %}
{# Result: border-radius: 0.75rem; #}
```

### Token Resolution Pattern

All token lookups follow this safe pattern:
```jinja2
{% if property and tokens and tokens.category and property in tokens.category %}
    {% set _ = styles.append('css-property: ' ~ tokens.category[property] ~ ';') %}
{% endif %}
```

**Why this pattern?**
1. Checks property exists
2. Checks tokens dict exists
3. Checks token category exists
4. Checks property key exists in category
5. Only then accesses token value

**Prevents:** `KeyError`, `TypeError`, `AttributeError` when tokens are missing or malformed.

---

## SSR Rendering Pipeline

### Complete Flow

```
1. Client sends YAML POST request to /render
   ↓
2. app.py: render_from_yaml()
   - Receives YAML text
   - Parses with yaml.safe_load()
   - Calls render_yaml_structure(structure, TOKENS)
   ↓
3. renderer.py: render_yaml_structure()
   - Validates structure and tokens
   - Creates Jinja2 template string
   - Imports _components.html macros
   - Renders template with structure + tokens
   ↓
4. _components.html: render_component() macro
   - Routes to specific component macro based on name
   - Each macro calls build_styles() for CSS generation
   - Recursively renders nested components
   ↓
5. _components.html: build_styles() macro
   - Reads component properties
   - Looks up tokens for semantic values
   - Generates inline CSS styles
   - Returns style string
   ↓
6. HTML returned to client
   - Injected into preview div via innerHTML
   - CSS classes applied from components.css
   - JavaScript initializes interactive components
```

### Component Rendering Example

**Input YAML:**
```yaml
- name: heading
  properties:
    text: Hello World
    level: 1
    typography:
      size: xl
      weight: bold
      color: '#111827'
    spacing:
      marginBlock: md
```

**Rendering Steps:**

1. **render_component()** routes to `render_text_component()` macro
2. **render_text_component()** detects `name == 'heading'`
3. **build_styles()** is called:
   - Checks `typography.size == 'xl'` → looks up `tokens.typography_sizes['xl']` → `'3rem'`
   - Checks `typography.weight == 'bold'` → looks up `tokens.font_weights['bold']` → `'700'`
   - Checks `typography.color == '#111827'` → uses directly
   - Checks `spacing.marginBlock == 'md'` → looks up `tokens.spacing['md']` → `'2rem'`
4. **Output HTML:**
```html
<h1 style="font-size: 3rem; font-weight: 700; color: #111827; margin-block: 2rem;">Hello World</h1>
```

---

## Template System (`templates/macros/_components.html`)

### Architecture

**Macro-Based Component System:**
- Each component type has its own macro (e.g., `render_heading()`, `render_button()`)
- Main dispatcher macro `render_component()` routes to appropriate macro
- Macros can call `render_component()` recursively for nested components

### Key Macros

#### **`render_component(component, tokens)`** - Main Dispatcher
Routes components to specialized renderers based on `component.name`:
- Layout: `page`, `layout-row`, `layout-column`, `columnsgrid`, `form`
- Interactive: `tabs`, `accordion`, `carousel`, `hamburger`
- Text: `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`, `link`
- Media: `image`, `video`, `gif`
- UI: `button`, `titlebar`
- Forms: `textbox`, `textarea`, `dropdown`, `checkbox`, `radio`, `calendar`
- Utility: `br`

#### **`build_styles(component, tokens, part=None, layout_direction=None)`** - Style Generator

**Purpose:** Generates inline CSS styles from component properties and design tokens.

**Parameters:**
- `component` - Component object with `name` and `properties`
- `tokens` - Design tokens dictionary
- `part` - Optional sub-part identifier (`'accordion_title'`, `'accordion_content'`, `'row'`, `'column'`)
- `layout_direction` - Override flex direction (`'row'` or `'column'`)

**Returns:** Space-separated CSS style string

**Style Categories Generated:**

1. **Layout Properties:**
   - Flexbox: `display: flex`, `flex-direction`, `align-items`, `gap`, `flex-wrap`
   - Grid: CSS custom properties for columns (`--cols`, `--cols-md`, `--cols-sm`)

2. **Spacing:**
   - Logical: `margin-block`, `margin-inline`, `padding-block`, `padding-inline`
   - Individual: `padding-top`, `padding-right`, `padding-bottom`, `padding-left`

3. **Appearance:**
   - Background: `background-color`
   - Border: `border` (width, style, color)
   - Radius: `border-radius` (from tokens)
   - Shadow: `box-shadow`

4. **Typography:**
   - Size: `font-size` (from tokens)
   - Weight: `font-weight` (from tokens)
   - Color: `color`
   - Alignment: `text-align`
   - Line height: `line-height`
   - Transform: `text-transform`

**Safe Token Access Pattern:**
All token lookups use defensive checks:
```jinja2
{% if property and tokens and tokens.category and property in tokens.category %}
    {% set _ = styles.append('css-property: ' ~ tokens.category[property] ~ ';') %}
{% endif %}
```

---

## Client-Side Integration

### JavaScript Flow (`static/js/ssr_app.js`)

#### **Function: `renderPreview(yamlContent)`**
```javascript
export const renderPreview = async (yamlContent) => {
    const response = await fetch('/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-yaml' },
        body: yamlContent
    });
    
    const htmlContent = await response.text();
    preview.innerHTML = htmlContent;
    initializeAllComponents();
};
```

**Flow:**
1. Sends YAML to `/render` endpoint
2. Receives HTML response
3. Injects HTML into `#preview` div
4. Initializes interactive components (carousels, tabs, etc.)

#### **Function: `initializeAllComponents()`**
```javascript
export const initializeAllComponents = () => {
    const preview = document.getElementById('preview');
    for (const componentName in componentInitializers) {
        const elements = preview.querySelectorAll(`[data-component-type="${componentName}"]`);
        elements.forEach(element => {
            componentInitializers[componentName](element, {});
        });
    }
};
```

**Purpose:** Finds all interactive components and initializes their JavaScript behavior.

---

## Differences from Client-Side Architecture

| Aspect | Client-Side | SSR |
|--------|------------|-----|
| **Rendering Location** | Browser (JavaScript) | Server (Python/Jinja2) |
| **YAML Parsing** | `js-yaml` library | `PyYAML` library |
| **Template Engine** | JavaScript functions | Jinja2 macros |
| **Design Tokens** | `schema_tokens.yaml` (loaded via JS) | `tokens.yaml` (loaded at startup) |
| **Chrome Overlays** | ✅ Interactive selection/deletion | ❌ Not implemented |
| **State Management** | `State` object in JavaScript | Stateless (each request independent) |
| **History/Undo** | ✅ Full undo/redo | ❌ Not implemented |
| **Properties Panel** | ✅ Visual editor | ❌ Not implemented |
| **Export** | ✅ Clean HTML export | ✅ HTML returned from server |

---

## Running SSR Version

### Setup
```bash
cd ssr_python
pip install -r requirements.txt
```

### Start Server
```bash
python app.py
```

### Access Application
Open browser to: `http://localhost:5000`

### Development Mode
Flask runs in debug mode (`debug=True`), which provides:
- Auto-reload on code changes
- Detailed error pages
- Interactive debugger

---

## Troubleshooting SSR

**Tokens not loading?**
- Check `tokens.yaml` exists in `ssr_python/` directory
- Check Flask console for token loading messages
- Verify tokens are dict (not None)

**Rendering errors?**
- Check error response JSON for details
- Look for template syntax errors in `_components.html`
- Verify YAML structure is valid (list of components)

**Styles not applying?**
- Check CSS files load (Network tab in DevTools)
- Verify `build_styles()` is called in component macros
- Check tokens contain expected keys

**Components not rendering?**
- Verify component name matches macro name
- Check component has required properties
- Look for errors in Flask console

---

## Adding New Components to SSR

1. **Add Component Macro** (`_components.html`):
   ```jinja2
   {% macro render_mycomponent(component, tokens) %}
       {% set properties = component.properties | default({}) %}
       <div class="my-component" style="{{ build_styles(component, tokens) }}">
           {{ properties.text }}
       </div>
   {% endmacro %}
   ```

2. **Add to Dispatcher** (`render_component()` macro):
   ```jinja2
   {% elif name == 'mycomponent' %}
       {{ render_mycomponent(component, tokens) }}
   ```

3. **Add CSS** (`static/css/components.css`):
   ```css
   .my-component {
       /* Component styles */
   }
   ```

4. **Test:** Paste YAML with new component, verify rendering

---

## SSR Component Selection & Properties Editing

### Overview

The SSR implementation includes full component selection and properties editing functionality, matching the CSR app behavior. Users can click components in the preview, edit their properties in the properties panel, and see changes reflected immediately.

### Implementation Phases

The implementation was completed in 5 phases:

#### **Phase 1: Server-Side Component ID Generation**

**Goal:** Add unique component IDs to all rendered components.

**Files Modified:**

1. **`ssr_python/renderer.py`**:
   - Updated template to pass path information `[loop.index0]` to component macros

2. **`ssr_python/templates/macros/_components.html`**:
   - Updated `render_component()` macro to accept `path=[]` parameter
   - Generates component ID from path: `comp_0`, `comp_0_components_1`, etc.
   - All component macros now accept `path` and `component_id` parameters
   - Added `data-component-id="{{ component_id }}"` to all HTML elements
   - Added `chrome-target` or `chrome-target-page` classes for selection
   - Added `position: relative` for chrome positioning
   - Updated nested component calls to pass correct paths

**Component ID Format:**
- Root component: `comp_0`
- Nested in components: `comp_0_components_1`
- Nested in columns: `comp_0_columns_0_components_1`
- Nested in tabs: `comp_0_tabs_0_components_1`
- Nested in slides: `comp_0_slides_0_components_1`

**All 23 Component Macros Updated:**
- Layout: `page`, `layout-row`, `layout-column`, `columnsgrid`, `form`
- Interactive: `tabs`, `accordion`, `carousel`, `hamburger`
- Text: `heading`, `paragraph`, `eyebrow`, `caption`, `blockquote`, `link`
- Media: `image`, `video`, `gif`
- UI: `button`, `titlebar`
- Forms: `textbox`, `textarea`, `dropdown`, `checkbox`, `radio`, `calendar`
- Utility: `br`

---

#### **Phase 2: Client-Side Path Map Building**

**Goal:** Build a map of component IDs to YAML paths from rendered HTML.

**Files Created:**

1. **`ssr_python/static/js/pathMapBuilder.js`**:
   - `ComponentPathMapBuilder` class
   - `buildPathMap()` — builds ID → path map from rendered HTML and YAML structure
   - `traverseYamlStructure()` — recursively traverses YAML and matches with DOM elements
   - `generateComponentId()` — generates IDs matching server-side format
   - Handles nested structures: `components`, `columns`, `tabs`, `slides`

**Files Modified:**

2. **`ssr_python/static/js/ssr_app.js`**:
   - Imported `ComponentPathMapBuilder`
   - Created singleton instance `pathMapBuilder`
   - Added `parseYaml()` helper function
   - Updated `renderPreview()` to:
     - Accept optional `yamlStructure` parameter
     - Parse YAML if structure not provided
     - Build path map after rendering HTML
     - Clear path map on errors
   - Exported `getPathMapBuilder()` for other modules

3. **`ssr_python/templates/index.html`**:
   - Added js-yaml CDN script for client-side YAML parsing
   - Made `jsyaml` available globally

**How Path Map Works:**

```javascript
// Example mapping:
'comp_0' → [0]
'comp_0_components_1' → [0, 'components', 1]
'comp_0_columns_0_components_2' → [0, 'columns', 0, 'components', 2]
```

---

#### **Phase 3: Component Selection & Highlighting**

**Goal:** Enable clicking components to select them and highlight selected components.

**Files Created:**

1. **`ssr_python/static/js/selectionManager.js`**:
   - `SelectionManager` class
   - `handlePreviewClick()` — handles clicks and finds component elements
   - `selectComponent()` — selects component by ID and highlights it
   - `clearSelection()` — clears selection and highlights
   - `highlightComponent()` — adds `.selected` class and scrolls into view
   - `clearHighlight()` — removes `.selected` from all elements
   - `getSelection()` — returns current selection
   - `restoreSelection()` — restores selection after re-render

**Files Modified:**

2. **`ssr_python/static/js/main.js`**:
   - Imported `SelectionManager`
   - Created singleton `selectionManager` instance
   - Updated `handlePreviewClick` action to use selection manager
   - Updated `handleEditorInput` to restore selection after re-render
   - Updated `clearCanvas` to clear selection

3. **`ssr_python/static/js/ssr_app.js`**:
   - Made `renderPreview()` return a Promise for selection restoration

**CSS Selection Styles:**

Already present in `ssr_python/static/css/style.css`:
- `.chrome-target.selected::before` — red dashed border for selected components
- `.chrome-target-page.selected::before` — red dashed border for page component
- `.form-element-wrapper.selected::before` — red dashed border for form elements

**Selection Behavior:**
- Click component → selects and highlights
- Click outside → clears selection
- Click interactive elements (inputs, buttons) → selects parent component
- Selection persists after YAML re-render

---

#### **Phase 4: Properties Panel Integration**

**Goal:** Display component properties in the properties panel when a component is selected.

**Files Created:**

1. **`ssr_python/static/js/metadataLoader.js`**:
   - `loadMetadata()` — loads all metadata from Flask API endpoints
   - `getComponentSchema()` — gets schema by component name
   - `getComponentDefaults()` — gets defaults by component name
   - `getSchemaTokens()` — gets schema tokens
   - `isMetadataLoaded()` — checks if metadata is loaded

2. **`ssr_python/static/js/utils/object.js`**:
   - `deepClone()` — deep clone objects
   - `deepMerge()` — merge objects recursively
   - `getNestedValue()` — get nested property values
   - `setNestedValue()` — set nested property values

3. **`ssr_python/static/js/propertiesPanel.js`**:
   - `renderPropertiesPanel()` — renders properties form for selected component
   - `clearPropertiesPanel()` — clears properties panel
   - `collectPropertyValues()` — collects form values for applying
   - Field renderers: text, textarea, number, select, checkbox, color, range
   - Groups fields by schema groups
   - Stores field metadata for applying changes

4. **`ssr_python/static/js/yamlUtils.js`**:
   - `getYamlStructureFromEditor()` — parses YAML from editor
   - `getComponentByPath()` — gets component from YAML structure by path

**Files Modified:**

5. **`ssr_python/app.py`**:
   - Added `/api/schemas` endpoint — serves `component_schemas.yaml` as JSON
   - Added `/api/defaults` endpoint — serves `component_defaults.yaml` as JSON
   - Added `/api/tokens` endpoint — serves `schema_tokens.yaml` as JSON
   - Uses `PROJECT_ROOT` to find metadata files in project root

6. **`ssr_python/static/js/main.js`**:
   - Loads metadata on app initialization
   - Connects selection manager to properties panel
   - Updates properties panel when component is selected
   - Clears properties panel when selection is cleared
   - Restores properties panel after re-render

**Field Types Supported:**
- **Text/Textarea**: Standard text inputs
- **Number**: Number input with min/max/step
- **Select**: Dropdown with options from schema or tokens
- **Checkbox**: Checkbox with label
- **Color**: HTML5 color picker (converts rgba to hex)
- **Range**: Slider with live value display

**Properties Panel Flow:**
1. Component selected → `onSelectionChange` callback triggered
2. Get component from YAML structure → `getComponentByPath()`
3. Get component schema → `getComponentSchema()`
4. Get component defaults → `getComponentDefaults()`
5. Merge defaults with component properties → `deepMerge()`
6. Render form fields based on schema groups
7. Store field metadata for applying changes

---

#### **Phase 5: YAML Update & Re-rendering**

**Goal:** Update YAML when properties change and re-render preview.

**Files Modified:**

1. **`ssr_python/static/js/yamlUtils.js`**:
   - Added `updateComponentByPath()` — updates component in YAML structure
   - Added `generateYamlFromStructure()` — converts structure to YAML string
   - Added `updateYamlEditor()` — updates editor content without triggering auto-render

2. **`ssr_python/static/js/propertiesPanel.js`**:
   - Updated `collectPropertyValues()` — merges defaults before collecting form values
   - Added `getActiveComponentInfo()` — returns active component info for applying

3. **`ssr_python/static/js/main.js`**:
   - Implemented `applySelectedComponentProperties()` action:
     - Gets active component info
     - Parses current YAML structure
     - Gets current component from structure
     - Collects property values from form
     - Creates updated component with new properties
     - Updates YAML structure
     - Generates YAML string
     - Updates editor
     - Re-renders preview
     - Restores selection and properties panel

**Complete Apply Flow:**

```
1. User clicks "Apply Changes" button
   ↓
2. Get active component info (componentId, path)
   ↓
3. Parse YAML structure from editor
   ↓
4. Get current component from structure
   ↓
5. Collect form values → collectPropertyValues()
   ↓
6. Merge defaults + form values → updatedProperties
   ↓
7. Create updated component → { ...component, properties: updatedProperties }
   ↓
8. Update YAML structure → updateComponentByPath()
   ↓
9. Generate YAML string → generateYamlFromStructure()
   ↓
10. Update editor → updateYamlEditor()
    ↓
11. Re-render preview → renderPreview()
    ↓
12. Build path map → pathMapBuilder.buildPathMap()
    ↓
13. Restore selection → selectionManager.selectComponent()
    ↓
14. Restore properties panel → renderPropertiesPanel()
```

---

### SSR Component Selection Architecture

#### **Component ID Generation**

**Server-Side (Jinja2 Templates):**
```jinja2
{% macro render_component(component, tokens, path=[]) %}
    {% if path | length > 0 %}
        {% set component_id = 'comp_' ~ path | join('_') %}
    {% else %}
        {% set component_id = 'comp_root' %}
    {% endif %}
    {# ... render component with data-component-id="{{ component_id }}" #}
{% endmacro %}
```

**Client-Side (JavaScript):**
```javascript
generateComponentId(path) {
    if (!path || path.length === 0) {
        return 'comp_root';
    }
    return 'comp_' + path.join('_');
}
```

**Path Examples:**
- `[0]` → `comp_0`
- `[0, 'components', 1]` → `comp_0_components_1`
- `[0, 'columns', 0, 'components', 2]` → `comp_0_columns_0_components_2`

#### **Path Map Building**

The path map is built after each render by traversing the YAML structure and matching with DOM elements:

```javascript
// After renderPreview() completes:
pathMapBuilder.buildPathMap(previewElement, yamlStructure);

// The builder:
// 1. Traverses YAML structure recursively
// 2. Generates component ID for each component
// 3. Finds matching DOM element with data-component-id
// 4. Stores mapping: componentId → path
```

**Nested Structure Handling:**
- `components` array → `path + ['components', index]`
- `columns` array → `path + ['columns', colIndex, 'components', compIndex]`
- `tabs` array → `path + ['tabs', tabIndex, 'components', compIndex]`
- `slides` array → `path + ['slides', slideIndex, 'components', compIndex]`

#### **Selection Flow**

```
1. User clicks preview element
   ↓
2. selectionManager.handlePreviewClick(event)
   ↓
3. Find closest [data-component-id] element
   ↓
4. Get componentId from element
   ↓
5. Look up path: pathMapBuilder.getPath(componentId)
   ↓
6. Store selection: { componentId, path }
   ↓
7. Highlight element: element.classList.add('selected')
   ↓
8. Trigger callback: onSelectionChange({ componentId, path })
   ↓
9. Properties panel renders: renderPropertiesPanel(component, componentId, path)
```

#### **Properties Application Flow**

```
1. User edits properties in form
   ↓
2. User clicks "Apply Changes"
   ↓
3. collectPropertyValues() reads all form inputs
   ↓
4. Build updatedProperties object with nested values
   ↓
5. Get current YAML structure from editor
   ↓
6. Get current component: getComponentByPath(structure, path)
   ↓
7. Create updated component: { ...component, properties: updatedProperties }
   ↓
8. Update structure: updateComponentByPath(structure, path, updatedComponent)
   ↓
9. Generate YAML: generateYamlFromStructure(updatedStructure)
   ↓
10. Update editor: updateYamlEditor(yamlText)
    ↓
11. Re-render: renderPreview(yamlText, updatedStructure)
    ↓
12. Build new path map
    ↓
13. Restore selection and properties panel
```

---

### Key JavaScript Modules

#### **`ssr_python/static/js/pathMapBuilder.js`**

**Purpose:** Maps component IDs to YAML paths.

**Key Methods:**
- `buildPathMap(previewElement, yamlStructure)` — Builds the complete path map
- `getPath(componentId)` — Gets YAML path for a component ID
- `generateComponentId(path)` — Generates ID from path (matches server-side)

#### **`ssr_python/static/js/selectionManager.js`**

**Purpose:** Manages component selection state and highlighting.

**Key Methods:**
- `handlePreviewClick(event)` — Handles click events on preview
- `selectComponent(componentId)` — Selects and highlights a component
- `clearSelection()` — Clears selection
- `restoreSelection()` — Restores selection after re-render

#### **`ssr_python/static/js/metadataLoader.js`**

**Purpose:** Loads component schemas, defaults, and tokens from Flask API.

**Key Methods:**
- `loadMetadata()` — Loads all metadata (called on app init)
- `getComponentSchema(name)` — Gets schema for component type
- `getComponentDefaults(name)` — Gets defaults for component type
- `getSchemaTokens()` — Gets design token options

#### **`ssr_python/static/js/propertiesPanel.js`**

**Purpose:** Renders and manages the properties panel form.

**Key Methods:**
- `renderPropertiesPanel(component, componentId, path)` — Renders form for component
- `clearPropertiesPanel()` — Clears the panel
- `collectPropertyValues()` — Collects form values for applying
- `getActiveComponentInfo()` — Returns current selection info

**Field Renderers:**
- `renderTextInput()` — Text and number inputs
- `renderTextarea()` — Multi-line text
- `renderSelect()` — Dropdown with token options
- `renderCheckbox()` — Checkbox with label
- `renderColorInput()` — Color picker
- `renderRangeInput()` — Slider with value display

#### **`ssr_python/static/js/yamlUtils.js`**

**Purpose:** YAML manipulation utilities.

**Key Methods:**
- `getYamlStructureFromEditor()` — Parses YAML from editor
- `getComponentByPath(structure, path)` — Gets component from structure
- `updateComponentByPath(structure, path, newComponent)` — Updates component
- `generateYamlFromStructure(structure)` — Converts structure to YAML string
- `updateYamlEditor(yamlText)` — Updates editor without triggering auto-render

---

### Flask API Endpoints

#### **`GET /api/schemas`**

**Purpose:** Serves component schemas as JSON.

**Response:** JSON object mapping component names to schema definitions.

**Example:**
```json
{
  "heading": {
    "groups": [
      {
        "id": "content",
        "label": "Content",
        "fields": [...]
      }
    ]
  }
}
```

#### **`GET /api/defaults`**

**Purpose:** Serves component defaults as JSON.

**Response:** JSON object mapping component names to default properties.

**Example:**
```json
{
  "heading": {
    "properties": {
      "text": "Heading",
      "level": 2,
      "typography": {...}
    }
  }
}
```

#### **`GET /api/tokens`**

**Purpose:** Serves schema tokens as JSON.

**Response:** JSON object with token categories and options.

**Example:**
```json
{
  "spacingScale": [
    {"value": "none", "label": "None"},
    {"value": "xs", "label": "Extra Small"},
    ...
  ]
}
```

---

### Component Selection CSS

Selection highlighting uses existing CSS classes:

**Selected State:**
```css
.chrome-target.selected::before {
    border-color: var(--color-danger); /* Red dashed border */
    opacity: 1;
}
```

**Hover State:**
```css
.chrome-target:hover::before {
    border-color: var(--color-secondary); /* Blue dashed border */
    opacity: 1;
}
```

**Chrome Label:**
```css
.chrome-label {
    position: absolute;
    top: 0rem;
    left: 0;
    background: var(--color-primary);
    color: var(--color-base);
    /* ... */
}
```

---

### Testing Component Selection

**Test Selection:**
1. Load YAML in editor
2. Click any component in preview
3. Verify red dashed border appears
4. Verify properties panel displays

**Test Properties Editing:**
1. Select a component
2. Edit properties in panel
3. Click "Apply Changes"
4. Verify:
   - YAML editor updates
   - Preview re-renders with changes
   - Component remains selected
   - Properties panel shows updated values

**Test Selection Persistence:**
1. Select a component
2. Edit YAML manually in editor
3. Wait for auto-render
4. Verify component remains selected
5. Verify properties panel still shows correct component

---

### Differences from CSR Implementation

| Feature | CSR | SSR |
|---------|-----|-----|
| **Component IDs** | Generated client-side | Generated server-side (Jinja2) |
| **Path Map** | Built during render | Built after render from YAML + DOM |
| **Metadata Loading** | Loaded via fetch() | Loaded from Flask API endpoints |
| **YAML Parsing** | Client-side (js-yaml) | Client-side (js-yaml) + Server-side (PyYAML) |
| **Properties Application** | Updates state directly | Updates YAML editor, triggers re-render |
| **Selection Persistence** | Via state management | Via selection manager + path map |

---

### Troubleshooting Component Selection

**Components not selectable?**
- Check components have `data-component-id` attributes
- Verify path map is being built (check console logs)
- Check `chrome-target` class is present on elements

**Properties panel empty?**
- Verify metadata loaded (check console for "Metadata loaded successfully")
- Check component schema exists in `component_schemas.yaml`
- Verify selection callback is triggered

**Apply button not working?**
- Check browser console for errors
- Verify YAML structure is valid
- Check component path is correct
- Verify form values are being collected

**Selection lost after re-render?**
- Check `restoreSelection()` is called
- Verify component ID matches between renders
- Check path map is rebuilt after render

---

**SSR Component Selection Implementation Complete** ✅