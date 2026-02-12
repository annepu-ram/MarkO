# API Routes & Data Flow Documentation

This document explains how data flows through the Flask application, from API requests to rendered HTML output.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Initialization](#application-initialization)
3. [API Routes](#api-routes)
   - [GET /](#get--main-ui)
   - [GET /preview-frame](#get-preview-frame)
   - [POST /render](#post-render-main-rendering-route)
   - [GET /api/schemas](#get-apischemas)
   - [GET /api/defaults](#get-apidefaults)
   - [GET /api/tokens](#get-apitokens)
   - [POST /api/chat](#post-apichat)
4. [The Render Route Deep Dive](#the-render-route-deep-dive)
5. [Component Rendering Pipeline](#component-rendering-pipeline)
6. [Data Flow Diagrams](#data-flow-diagrams)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Browser)                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ YAML Editor  │───>│  ssr_app.js  │───>│ Iframe (preview_bridge)  │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ POST /render
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           SERVER (Flask)                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │    app.py    │───>│ renderer.py  │───>│ _components.html (Jinja) │  │
│  │              │    │              │    │                          │  │
│  │ - Parse YAML │    │ - Merge      │    │ - render_component()     │  │
│  │ - Load tokens│    │   defaults   │    │ - build_styles()         │  │
│  │ - Route req  │    │ - Validate   │    │ - Component macros       │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Application Initialization

When Flask starts (`python app.py`), these files are loaded into memory:

### 1. Design Tokens (`tokens.yaml`)
```python
# Location: ssr_python/tokens.yaml
TOKENS = yaml.safe_load(open('tokens.yaml'))
# Contains: typography_sizes, font_weights, spacing, border_radius, etc.
```

### 2. Component Defaults (`component_defaults.yaml`)
```python
# Location: project_root/component_defaults.yaml
COMPONENT_DEFAULTS = yaml.safe_load(open('component_defaults.yaml'))
# Contains: default properties for each component type (heading, button, etc.)
```

### 3. Custom Jinja2 Filter
```python
app.template_filter('transparency_to_hex')(transparency_to_hex)
# Converts transparency (0-100) to hex alpha (00-ff) for CSS colors
```

---

## API Routes

### GET / (Main UI)

**Purpose:** Serve the main application interface

**File:** [app.py:75-77](ssr_python/app.py#L75-L77)

```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Data Flow:**
```
Request GET / → Flask → render_template('index.html') → HTML Response
```

**Returns:** Full HTML page with:
- YAML editor
- Preview iframe
- Properties panel
- Component tree

---

### GET /preview-frame

**Purpose:** Serve the isolated iframe content for preview rendering

**File:** [app.py:79-82](ssr_python/app.py#L79-L82)

```python
@app.route('/preview-frame')
def preview_frame():
    return render_template('preview_frame.html')
```

**Data Flow:**
```
Request GET /preview-frame → Flask → render_template('preview_frame.html') → HTML Response
```

**Returns:** Empty iframe template with:
- `preview-chrome.css` (selection highlighting)
- `preview_bridge.js` (handles postMessage communication)

---

### POST /render (Main Rendering Route)

**Purpose:** Convert YAML structure to rendered HTML

**File:** [app.py:84-112](ssr_python/app.py#L84-L112)

```python
@app.route('/render', methods=['POST'])
def render_from_yaml():
    yaml_data = request.get_data(as_text=True)
    structure = yaml.safe_load(yaml_data)
    html_content = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    return html_content
```

**Request:**
- Method: `POST`
- Content-Type: `text/plain` (raw YAML)
- Body: YAML string

**Response:**
- Success: HTML string (200)
- YAML Error: JSON with error details (400)
- Render Error: JSON with traceback (500)

**Complete Data Flow:** See [The Render Route Deep Dive](#the-render-route-deep-dive)

---

### GET /api/schemas

**Purpose:** Provide component schemas for the properties panel

**File:** [app.py:45-53](ssr_python/app.py#L45-L53)

```python
@app.route('/api/schemas')
def get_schemas():
    schemas = yaml.safe_load(open('component_schemas.yaml'))
    return jsonify(schemas)
```

**Data Flow:**
```
Request GET /api/schemas
    → Load component_schemas.yaml
    → Parse YAML to dict
    → Convert to JSON
    → Response
```

**Returns:** JSON object mapping component names to their property schemas
```json
{
  "heading": {
    "sections": [
      {
        "title": "Typography",
        "fields": [
          { "key": "typography.size", "label": "Size", "type": "select", "tokenRef": "typographySizes" }
        ]
      }
    ]
  }
}
```

---

### GET /api/defaults

**Purpose:** Provide default property values for components

**File:** [app.py:55-63](ssr_python/app.py#L55-L63)

```python
@app.route('/api/defaults')
def get_defaults():
    defaults = yaml.safe_load(open('component_defaults.yaml'))
    return jsonify(defaults)
```

**Data Flow:**
```
Request GET /api/defaults
    → Load component_defaults.yaml
    → Parse YAML to dict
    → Convert to JSON
    → Response
```

**Returns:** JSON object with default properties for each component type
```json
{
  "heading": {
    "typography": { "size": "xl", "weight": "bold" },
    "spacing": { "marginBlock": "md" }
  }
}
```

---

### GET /api/tokens

**Purpose:** Provide design token options for property dropdowns

**File:** [app.py:65-73](ssr_python/app.py#L65-L73)

```python
@app.route('/api/tokens')
def get_schema_tokens():
    tokens = yaml.safe_load(open('schema_tokens.yaml'))
    return jsonify(tokens)
```

**Data Flow:**
```
Request GET /api/tokens
    → Load schema_tokens.yaml
    → Parse YAML to dict
    → Convert to JSON
    → Response
```

**Returns:** JSON object with token values for select dropdowns
```json
{
  "typographySizes": ["xxs", "xs", "sm", "md", "lg", "xl", "xxl", "xxxl"],
  "fontWeights": ["light", "regular", "medium", "semibold", "bold"],
  "spacingScale": ["none", "xxs", "xs", "sm", "md", "lg", "xl", "xxl"]
}
```

---

### POST /api/chat

**Purpose:** AI-powered YAML generation using Google Gemini

**File:** [app.py:115-188](ssr_python/app.py#L115-L188)

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    current_yaml = data.get('currentYaml')
    selected_component = data.get('selectedComponent')

    llm_service = get_llm_service()
    result = llm_service.chat(message, current_yaml, selected_component)
    return jsonify(result)
```

**Request:**
```json
{
  "message": "Add a hero section with a large heading",
  "currentYaml": "- name: page\n  components: []",
  "selectedComponent": {
    "id": "comp_0",
    "path": [0],
    "name": "page"
  }
}
```

**Response:**
```json
{
  "response": "I've added a hero section...",
  "yaml": "- name: layout-row\n  components:\n    - name: heading...",
  "action": "modify"
}
```

**Data Flow:**
```
Request POST /api/chat
    │
    ├── Validate API key exists
    ├── Parse JSON body
    ├── Import llm_service.py
    │       │
    │       ├── Load LLM_COMPONENT_GUIDE.md (context)
    │       ├── Build prompt with YAML + selection
    │       └── Call Gemini API
    │
    ├── Parse LLM response for YAML blocks
    └── Return JSON with action + YAML
```

---

## The Render Route Deep Dive

The `/render` route is the core of the application. Here's the complete data flow:

### Step 1: Request Reception

```
Client (ssr_app.js) → POST /render
                      Body: Raw YAML string
```

Example YAML input:
```yaml
- name: page
  properties:
    appearance:
      background:
        color: "#ffffff"
  components:
    - name: heading
      properties:
        content: "Hello World"
        typography:
          size: xl
```

### Step 2: YAML Parsing (app.py:87-89)

```python
yaml_data = request.get_data(as_text=True)  # Get raw YAML string
structure = yaml.safe_load(yaml_data)        # Parse to Python list/dict
```

**Result:** Python data structure
```python
[
    {
        'name': 'page',
        'properties': {
            'appearance': {'background': {'color': '#ffffff'}}
        },
        'components': [
            {
                'name': 'heading',
                'properties': {
                    'content': 'Hello World',
                    'typography': {'size': 'xl'}
                }
            }
        ]
    }
]
```

### Step 3: Call Renderer (app.py:91)

```python
html_content = render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
```

### Step 4: Merge with Defaults (renderer.py:227-230)

```python
merged_structure = [
    merge_component_with_defaults(component, defaults, tokens, f"[{i}]")
    for i, component in enumerate(structure)
]
```

**What happens:**
1. For each component, get its defaults from `COMPONENT_DEFAULTS`
2. Deep merge user properties over defaults (user values take precedence)
3. Validate token-based values exist in `TOKENS`
4. Recursively process nested components (in `components`, `columns`, `tabs`, `slides`)

**Example merge:**
```python
# Defaults for 'heading':
{
    'typography': {'size': 'xl', 'weight': 'bold', 'align': 'left'},
    'spacing': {'marginBlock': 'md'}
}

# User properties:
{
    'content': 'Hello World',
    'typography': {'size': 'xl'}  # Only size specified
}

# Merged result:
{
    'content': 'Hello World',
    'typography': {'size': 'xl', 'weight': 'bold', 'align': 'left'},  # weight, align from defaults
    'spacing': {'marginBlock': 'md'}  # From defaults
}
```

### Step 5: Create Jinja2 Environment (renderer.py:243-254)

```python
env = Environment(
    loader=FileSystemLoader(templates_dir),
    trim_blocks=True,      # Remove newlines after block tags
    lstrip_blocks=True     # Strip whitespace before block tags
)
env.filters.update(current_app.jinja_env.filters)  # Add custom filters
```

### Step 6: Render Template (renderer.py:234-240, 255)

```python
template_str = """
    {% import 'macros/_components.html' as components %}
    {% for component in structure %}
        {{ components.render_component(component, tokens, [loop.index0]) }}
    {% endfor %}
"""
return template.render(structure=merged_structure, tokens=tokens)
```

### Step 7: Jinja2 Macro Dispatch (_components.html:2-61)

The `render_component` macro routes to specific component macros:

```jinja2
{% macro render_component(component, tokens, path=[], parent_direction='row') %}
    {% set name = component.name %}
    {% set component_id = 'comp_' ~ path | join('_') %}

    {% if name == 'page' %}
        {{ render_page(component, tokens, path, component_id) }}
    {% elif name == 'heading' %}
        {{ render_text_component(component, tokens, path, component_id, parent_direction) }}
    {% elif name == 'button' %}
        {{ render_button(component, tokens, path, component_id) }}
    {# ... more component types ... #}
    {% endif %}
{% endmacro %}
```

### Step 8: Component-Specific Rendering

Each component macro:
1. Extracts properties from component dict
2. Calls `build_styles()` to generate inline CSS
3. Outputs HTML with `data-component-id` attribute
4. Recursively renders child components

**Example: render_page macro**
```jinja2
{% macro render_page(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set components = component.components | default([]) %}
    {% set page_styles = build_styles(component, tokens, part='outer') %}

    <div class="page" data-component-id="{{ component_id }}"
         style="display: flex; flex-direction: column; {{ page_styles }}">
        {% for child in components %}
            {% set child_path = path + ['components', loop.index0] %}
            {{ render_component(child, tokens, child_path) }}
        {% endfor %}
    </div>
{% endmacro %}
```

### Step 9: Style Generation (build_styles macro)

The `build_styles` macro converts properties + tokens to CSS:

```
properties.typography.size = 'xl'
    + tokens.typography_sizes.xl = '1.5rem'
    = font-size: 1.5rem;

properties.spacing.marginBlock = 'md'
    + tokens.spacing.md = '1.5rem'
    = margin-block: 1.5rem;

properties.appearance.background.color = '#ffffff'
    + properties.appearance.background.transparency = 100
    = background-color: #ffffffff;
```

### Step 10: Return HTML Response

Final HTML output:
```html
<div class="page" data-component-id="comp_0"
     style="display: flex; flex-direction: column; background-color: #ffffffff;">
    <h1 class="heading chrome-target" data-component-id="comp_0_components_0"
        style="font-size: 1.5rem; font-weight: 700; margin-block: 1.5rem;">
        Hello World
    </h1>
</div>
```

---

## Component Rendering Pipeline

### Component ID Generation

Component IDs are generated from the YAML path for selection tracking:

| YAML Path | Component ID |
|-----------|--------------|
| `[0]` | `comp_0` |
| `[0, 'components', 1]` | `comp_0_components_1` |
| `[0, 'columns', 0, 'components', 2]` | `comp_0_columns_0_components_2` |
| `[0, 'tabs', 1, 'components', 0]` | `comp_0_tabs_1_components_0` |

### Nested Structure Handling

Different component types have different nesting patterns:

| Component | Nesting Property | Path Pattern |
|-----------|------------------|--------------|
| page, layout-row, layout-column | `components` | `path + ['components', index]` |
| columnsgrid | `columns[n].components` | `path + ['columns', col_idx, 'components', index]` |
| tabs | `tabs[n].components` | `path + ['tabs', tab_idx, 'components', index]` |
| carousel | `slides[n].components` | `path + ['slides', slide_idx, 'components', index]` |
| accordion | `items[n].components` | `path + ['items', item_idx, 'components', index]` |

### Style Building Order

1. **Base styles** - Component-specific defaults (display, position)
2. **Typography** - size, weight, align, color, letterSpacing, lineHeight, transform
3. **Spacing** - marginBlock, marginInline, paddingBlock, paddingInline
4. **Layout** - width, height, gap, justifyContent, alignItems
5. **Appearance** - background color/image, border, radius, shadow

---

## Data Flow Diagrams

### Complete Render Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                          │
│                                                                             │
│   YAML Editor                    ssr_app.js                 Iframe          │
│   ┌─────────┐                   ┌─────────┐               ┌─────────┐      │
│   │  YAML   │ ─── onChange ──>  │ debounce│ ─── POST ──>  │ preview │      │
│   │  text   │                   │ /render │               │ bridge  │      │
│   └─────────┘                   └─────────┘               └─────────┘      │
│                                      │                         ▲            │
│                                      │                         │            │
│                                 (wait for                 postMessage       │
│                                  response)              UPDATE_CONTENT      │
│                                      │                         │            │
└──────────────────────────────────────┼─────────────────────────┼────────────┘
                                       │                         │
                                       ▼                         │
┌──────────────────────────────────────────────────────────────────────────────┐
│                              SERVER                                          │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                           app.py                                     │   │
│   │                                                                      │   │
│   │   yaml.safe_load(yaml_data)                                         │   │
│   │          │                                                           │   │
│   │          ▼                                                           │   │
│   │   ┌──────────────┐                                                  │   │
│   │   │   structure  │  (Python list of dicts)                          │   │
│   │   └──────────────┘                                                  │   │
│   │          │                                                           │   │
│   │          ▼                                                           │   │
│   │   render_yaml_structure(structure, TOKENS, COMPONENT_DEFAULTS)      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                       │                                      │
│                                       ▼                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                         renderer.py                                   │  │
│   │                                                                       │  │
│   │   for each component:                                                 │  │
│   │       merge_component_with_defaults()                                 │  │
│   │           │                                                           │  │
│   │           ├── deep_merge(defaults, user_props)                        │  │
│   │           ├── validate_component_properties()                         │  │
│   │           └── recursively process children                            │  │
│   │                                                                       │  │
│   │   Jinja2 Environment:                                                 │  │
│   │       template.render(structure=merged, tokens=TOKENS)                │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                       │                                      │
│                                       ▼                                      │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                    _components.html (Jinja2)                          │  │
│   │                                                                       │  │
│   │   render_component(component, tokens, path)                           │  │
│   │       │                                                               │  │
│   │       ├── Generate component_id from path                             │  │
│   │       ├── Dispatch to specific macro (render_page, render_heading...) │  │
│   │       │       │                                                       │  │
│   │       │       ├── build_styles(component, tokens)                     │  │
│   │       │       ├── Output HTML with data-component-id                  │  │
│   │       │       └── Recursively render_component() for children         │  │
│   │       │                                                               │  │
│   │       └── Return HTML string                                          │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                       │                                      │
│                                       ▼                                      │
│                               HTML Response ─────────────────────────────────┘
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Metadata Loading Flow (on page load)

```
Page Load
    │
    ├── GET /api/schemas ────> component_schemas.yaml ────> propertiesPanel.js
    │                                                       (field definitions)
    │
    ├── GET /api/defaults ───> component_defaults.yaml ───> main.js
    │                                                       (default values)
    │
    └── GET /api/tokens ─────> schema_tokens.yaml ────────> propertiesPanel.js
                                                            (dropdown options)
```

---

## Error Handling

### YAML Parse Errors (400)

```python
except yaml.YAMLError as e:
    return jsonify({
        'error': 'Invalid YAML Format',
        'details': f"Line {mark.line + 1}, Column {mark.column + 1}: {e.problem}"
    }), 400
```

### Render Errors (500)

```python
except Exception as e:
    return jsonify({
        'error': 'An unexpected error occurred during rendering.',
        'details': f"{error_message}\n\nFull traceback:\n{traceback.format_exc()}"
    }), 500
```

### Validation Errors

Token validation in `renderer.py` catches invalid property values:
```python
if value not in token_values:
    raise ValueError(f"Invalid value '{value}' for property '{property_path}'")
```

---

## Security Headers

All responses include security headers (app.py:191-218):

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Frame-Options` | `SAMEORIGIN` | Prevent clickjacking |
| `Content-Security-Policy` | (multiple directives) | Restrict resource loading |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |

---

---

## Jinja2 Advanced Concepts

The template system uses several advanced Jinja2 features. This section explains each concept with examples from the codebase.

### 1. Macros (Functions)

Macros are reusable template functions. They accept parameters and return rendered output.

**Definition:**
```jinja2
{% macro render_button(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    <button class="btn" data-component-id="{{ component_id }}">
        {{ properties.text | default('Button') }}
    </button>
{% endmacro %}
```

**Calling a macro:**
```jinja2
{{ render_button(component, tokens, path, component_id) }}
```

**Key macros in `_components.html`:**

| Macro | Purpose | Line |
|-------|---------|------|
| `render_component()` | Main dispatcher - routes to specific macros | 2-61 |
| `build_styles()` | Generates inline CSS from properties + tokens | 849-1039 |
| `build_flex_styles()` | Generates flexbox CSS for layout containers | 1043-1083 |
| `build_tabs_vars()` | Generates CSS variables for tabs component | ~650 |
| `build_accordion_vars()` | Generates CSS variables for accordion | 753-845 |

### 2. Filters

Filters transform values using the pipe (`|`) syntax. They can be chained.

**Built-in filters used:**

```jinja2
{# default - provides fallback value if undefined/falsy #}
{{ properties.text | default('Button') }}

{# join - joins array elements with separator #}
{{ path | join('_') }}          {# [0, 'components', 1] → "0_components_1" #}
{{ styles | join(' ') }}        {# ['color: red;', 'margin: 0;'] → "color: red; margin: 0;" #}

{# length - returns length of array/string #}
{% if components | length > 0 %}

{# int - converts to integer #}
{% set column_count = layout.columns | default(2) | int %}

{# replace - string replacement #}
{{ properties.text | replace('\n', '<br>') }}

{# safe - marks string as safe HTML (no escaping) #}
{{ properties.text | replace('\n', '<br>') | safe }}

{# random - generates random number in range #}
{% set tabs_id = 'tabs_' ~ range(1000, 9999) | random %}
```

**Custom filter (defined in `renderer.py`, registered in `app.py`):**

```python
# renderer.py
def transparency_to_hex(transparency):
    """Convert transparency (0-100) to hex alpha (00-ff)."""
    alpha = int(transparency * 255 / 100)
    return format(alpha, '02x')

# app.py
app.template_filter('transparency_to_hex')(transparency_to_hex)
```

**Usage in template:**
```jinja2
{% set alpha_hex = bg.transparency | transparency_to_hex %}
{% set color_with_alpha = '#ffffff' ~ alpha_hex %}  {# e.g., #ffffffcc #}
```

### 3. Variables with `{% set %}`

Variables store computed values for later use.

```jinja2
{# Simple assignment #}
{% set properties = component.properties | default({}) %}

{# Computed value #}
{% set component_id = 'comp_' ~ path | join('_') %}

{# Array building pattern (used extensively for styles) #}
{% set styles = [] %}
{% set _ = styles.append('color: red;') %}
{% set _ = styles.append('margin: 0;') %}
{{ styles | join(' ') }}
```

**Important pattern - discarding return values:**
```jinja2
{# The _ variable discards append()'s return value (None) #}
{% set _ = styles.append('font-size: 16px;') %}
```

### 4. Conditionals (`{% if %}`)

Standard conditional logic with `if`, `elif`, `else`.

```jinja2
{% if name == 'page' %}
    {{ render_page(component, tokens, path, component_id) }}
{% elif name == 'heading' %}
    {{ render_text_component(component, tokens, path, component_id) }}
{% elif name in ['button', 'link'] %}
    {# 'in' operator for multiple matches #}
    {{ render_interactive(component, tokens, path, component_id) }}
{% else %}
    <div>Unknown component: {{ name }}</div>
{% endif %}
```

**Inline conditional (ternary):**
```jinja2
{% set direction = layout_direction if layout_direction else 'column' %}
```

**Truthiness checks:**
```jinja2
{# Check if value exists and is truthy #}
{% if props.typography and props.typography.size %}
{% if styles %}style="{{ styles }}"{% endif %}

{# Check if key exists in dict #}
{% if 'components' in item %}

{# is defined - check if variable exists #}
{% if properties.underline is defined %}
```

### 5. Loops (`{% for %}`)

Iterate over arrays with access to loop metadata.

```jinja2
{% for child in components | default([]) %}
    {% set child_path = path + ['components', loop.index0] %}
    {{ render_component(child, tokens, child_path) }}
{% endfor %}
```

**Loop variables:**

| Variable | Description |
|----------|-------------|
| `loop.index` | Current iteration (1-indexed) |
| `loop.index0` | Current iteration (0-indexed) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total number of items |

**Example with loop variables:**
```jinja2
{% for tab in tabs_list %}
    <input type="radio"
           id="tab_{{ loop.index0 }}"
           {% if loop.first %}checked{% endif %}>
    <label for="tab_{{ loop.index0 }}">{{ tab.title }}</label>
{% endfor %}
```

### 6. Template Inheritance & Import

**Importing macros:**
```jinja2
{% import 'macros/_components.html' as components %}
{{ components.render_component(component, tokens, path) }}
```

**Include (not used in this project but available):**
```jinja2
{% include 'partials/header.html' %}
```

### 7. Whitespace Control

Control whitespace in output with `-` trim markers.

```jinja2
{#- Comment that doesn't add whitespace -#}

{%- set x = 1 -%}    {# No whitespace before/after #}

{% macro my_macro() -%}  {# Trim after opening #}
    content
{%- endmacro %}          {# Trim before closing #}
```

**Environment configuration in `renderer.py`:**
```python
env = Environment(
    loader=FileSystemLoader(templates_dir),
    trim_blocks=True,      # Remove newline after block tags
    lstrip_blocks=True     # Strip leading whitespace before block tags
)
```

### 8. String Concatenation with `~`

The tilde operator concatenates strings.

```jinja2
{% set component_id = 'comp_' ~ path | join('_') %}
{# Result: "comp_0_components_1" #}

{% set css = 'color: ' ~ color ~ ';' %}
{# Result: "color: #ffffff;" #}

{# Complex concatenation #}
{% set calc = 'calc((100% - (' ~ gap ~ ' * ' ~ (count - 1) ~ ')) / ' ~ count ~ ')' %}
{# Result: "calc((100% - (1rem * 2)) / 3)" #}
```

### 9. Dictionary/Object Access

Multiple ways to access nested properties.

```jinja2
{# Dot notation #}
{{ component.properties.typography.size }}

{# Bracket notation (for dynamic keys) #}
{{ tokens['typography_sizes'][size] }}
{{ tokens.spacing[gap_token] }}

{# Safe nested access with default #}
{% set typo = props.typography.title | default({}) if props.typography else {} %}

{# get() method for safe access #}
{% set css_value = h_align_css.get(h_align, 'stretch') %}
```

### 10. Tests (is/is not)

Tests check variable properties.

```jinja2
{# is defined - check existence #}
{% if properties.underline is defined %}

{# is mapping - check if dict #}
{% if item is mapping and 'components' in item %}

{# Other useful tests (not all used in this project) #}
{% if value is none %}
{% if value is string %}
{% if value is number %}
{% if value is iterable %}
```

### 11. Dynamic HTML Tags

Generate HTML tags dynamically.

```jinja2
{% set tag = layout_props.tag | default('section') %}
<{{ tag }} class="layout-row" data-component-id="{{ component_id }}">
    {# content #}
</{{ tag }}>

{# Outputs: <section class="layout-row">...</section> #}
{# Or: <div class="layout-row">...</div> depending on tag value #}
```

### 12. Range Function

Generate sequences of numbers.

```jinja2
{# Iterate n times #}
{% for col_index in range(column_count) %}
    <div class="col-{{ col_index }}">...</div>
{% endfor %}

{# Generate random ID #}
{% set tabs_id = 'tabs_' ~ range(1000, 9999) | random %}
```

---

## Style Generation Deep Dive

The `build_styles()` macro is the heart of CSS generation. Here's how it transforms YAML properties to CSS:

### Input → Output Mapping

```yaml
# YAML Input (component properties)
typography:
  size: xl
  weight: bold
  color: "#333333"
  align: center
spacing:
  marginBlock: md
  paddingInline: lg
appearance:
  background:
    color: "#ffffff"
    transparency: 80
  radius: md
  border:
    width: 1
    style: solid
    color: "#e5e7eb"
```

```css
/* CSS Output */
font-size: 1.5rem;           /* tokens.typography_sizes.xl */
font-weight: 700;            /* tokens.font_weights.bold */
color: #333333;
text-align: center;
margin-block: 1.5rem;        /* tokens.spacing.md */
padding-inline: 2rem;        /* tokens.spacing.lg */
background-color: #ffffffcc; /* color + transparency_to_hex(80) */
border-radius: 0.5rem;       /* tokens.border_radius.md */
border: 1px solid #e5e7eb;
```

### Token Lookup Pattern

```jinja2
{# Pattern: Check tokens exist, check category exists, check value exists #}
{% if typo.size and tokens and tokens.typography_sizes and typo.size in tokens.typography_sizes %}
    {% set _ = styles.append('font-size: ' ~ tokens.typography_sizes[typo.size] ~ ';') %}
{% endif %}
```

This defensive pattern prevents errors when:
- `tokens` is None/empty
- Token category doesn't exist
- Property value isn't a valid token

---

## Summary

| Route | Method | Input | Output | Purpose |
|-------|--------|-------|--------|---------|
| `/` | GET | - | HTML | Main application UI |
| `/preview-frame` | GET | - | HTML | Isolated preview iframe |
| `/render` | POST | YAML string | HTML | Convert YAML to rendered HTML |
| `/api/schemas` | GET | - | JSON | Property field definitions |
| `/api/defaults` | GET | - | JSON | Default property values |
| `/api/tokens` | GET | - | JSON | Token options for dropdowns |
| `/api/chat` | POST | JSON (message, yaml, selection) | JSON | AI-powered YAML generation |

---

## Jinja2 Quick Reference

| Concept | Syntax | Example |
|---------|--------|---------|
| Variable output | `{{ }}` | `{{ component.name }}` |
| Statement | `{% %}` | `{% if x %}...{% endif %}` |
| Comment | `{# #}` | `{# This is a comment #}` |
| Filter | `\|` | `{{ text \| default('') }}` |
| Concatenate | `~` | `{{ 'id_' ~ index }}` |
| Macro define | `{% macro %}` | `{% macro foo(x) %}...{% endmacro %}` |
| Macro call | `{{ }}` | `{{ foo(value) }}` |
| Set variable | `{% set %}` | `{% set x = 1 %}` |
| Loop | `{% for %}` | `{% for i in items %}...{% endfor %}` |
| Conditional | `{% if %}` | `{% if x %}...{% elif y %}...{% else %}...{% endif %}` |
| Import | `{% import %}` | `{% import 'file' as alias %}` |
| Whitespace trim | `-` | `{%- set x = 1 -%}` |
