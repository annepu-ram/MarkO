# Refactoring Plan: Productionalize Swift Sites

## Context

The Swift Sites SSR app works well but has structural issues that make it hard to maintain at scale:

- **`_components.html`** is a 1577-line monolith with 28 macros (all component renderers + style utilities in one file)
- **`app.py`** (395 lines) handles all routes, config loading, image search providers, and security middleware
- **Config YAML files** live in the project root instead of with the Flask app
- **Security issues** exist: debug telemetry in `object.js`, Flask debug mode on all interfaces, unpinned deps
- **No Python tests** exist
- **Root directory clutter**: orphaned legacy files (`coverage/`, `package-lock.json`)

This plan ensures **zero functional regressions** at every step. Each phase is independently verifiable.

---

## Phase 1: Security Fixes (Low Risk)

These changes fix vulnerabilities without touching any rendering or application logic.

### 1a. Remove telemetry from `utils/object.js`

**File:** `static/js/utils/object.js`

The `deepMerge()` and `setNestedValue()` functions contain 10 `#region agent log` blocks that `fetch()` data to `http://127.0.0.1:7242`. These send internal object structures to an external endpoint on every merge operation.

**Action:** Remove all lines between `// #region agent log` and `// #endregion` markers (inclusive). The 4 exported functions (`deepClone`, `deepMerge`, `getNestedValue`, `setNestedValue`) remain unchanged in behavior.

**Verification:** Load any template, edit properties, verify no console fetch errors. The functions work identically without the logging.

### 1b. Fix Flask debug mode and host binding

**File:** `app.py` line 395

```python
# BEFORE:
app.run(host='0.0.0.0', port=5000, debug=True)

# AFTER:
import os
debug_mode = os.environ.get('FLASK_ENV') == 'development'
app.run(host='127.0.0.1', port=5000, debug=debug_mode)
```

**Why safe:** Only changes startup binding. Set `FLASK_ENV=development` in `.env` to keep debug mode during dev.

### 1c. Pin dependency versions

**File:** `requirements.txt`

```
Flask>=3.0.0,<4.0
PyYAML>=6.0.1,<7.0
ollama>=0.4.0,<1.0
python-dotenv>=1.0.0,<2.0
requests>=2.31.0,<3.0
```

### 1d. Create `.env.example`

**New file:** `ssr_python/.env.example`

```bash
# Copy to .env and fill in values. NEVER commit .env
FLASK_ENV=development

# LLM Chat (Ollama)
OLLAMA_API_KEY=
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT=120

# Image Search (at least one required)
PEXELS_API_KEY=
PIXABAY_API_KEY=
```

**Also:** Verify `ssr_python/.env` is gitignored (`git ls-files ssr_python/.env` should return nothing).

**Verification:** `python app.py` starts normally. All features work as before.

---

## Phase 2: Template Refactoring (Medium Risk)

Split `_components.html` (1577 lines) into individual component files using Jinja2 `{% include %}`.

### Why This Is Safe

Verified through thorough analysis:
- **No module-level state** in `_components.html` (file starts with `{% macro %}` at line 2)
- **No `caller()` or `{% call %}` usage** anywhere in the file
- **No namespace-prefixed calls** - all internal macro calls use direct names (e.g., `render_button(...)` not `components.render_button(...)`)
- **Custom filters remain available** - registered on Flask app AND merged into renderer.py's Jinja2 Environment
- **Only `renderer.py` uses `_components.html`** - no other templates import it
- **Only one public entry point** - `render_component()` is the only macro called from renderer.py
- **Each macro is stateless** - receives data as parameters, no shared caches or instance variables

### Strategy: Include-Based Assembly

`{% include %}` inlines file contents into the current scope (unlike `{% import %}` which creates an isolated scope). This naturally resolves the circular dependency: `render_component` calls component macros, and component macros call `render_component` back recursively.

### New File Structure

```
templates/
  components/                    # NEW directory
    _assembly.html               # Entry point: includes everything in order
    _utilities.html              # build_styles (~340 lines), build_flex_styles (~60 lines)
    _vars_builders.html          # build_tabs_vars (~112 lines), build_accordion_vars (~100 lines)
    _dispatcher.html             # render_component() dispatcher (~63 lines)
    layout/
      _page.html                 # render_page
      _layout_row.html           # render_layout_row
      _layout_column.html        # render_layout_column
      _columnsgrid.html          # render_columnsgrid
      _form.html                 # render_form
    interactive/
      _tabs.html                 # render_tabs
      _accordion.html            # render_accordion
      _hamburger.html            # render_hamburger
      _carousel.html             # render_carousel
    text/
      _text_component.html       # render_text_component (heading/paragraph/eyebrow/caption/blockquote/link)
    media/
      _image.html                # render_image
      _video.html                # render_video
      _gif.html                  # render_gif
      _video_background.html     # render_video_background
      _media_caption.html        # render_media_caption
    ui/
      _button.html               # render_button
      _titlebar.html             # render_titlebar
      _br.html                   # render_br
    forms/
      _textbox.html              # render_textbox
      _textarea.html             # render_textarea
      _dropdown.html             # render_dropdown
      _checkbox.html             # render_checkbox
      _radio.html                # render_radio
      _calendar.html             # render_calendar
  macros/
    _components.html             # KEEP as backup until verified
```

### `_assembly.html` (the orchestrator)

```jinja2
{#- Assembles all component macros into a single scope via include.
    Include ORDER matters: utilities first, components second, dispatcher last. -#}

{#- 1. Shared utility macros (no dependencies) -#}
{% include "components/_utilities.html" %}
{% include "components/_vars_builders.html" %}

{#- 2. Component macros (depend on utilities via build_styles/build_flex_styles) -#}
{% include "components/media/_media_caption.html" %}
{% include "components/layout/_page.html" %}
{% include "components/layout/_layout_row.html" %}
{% include "components/layout/_layout_column.html" %}
{% include "components/layout/_columnsgrid.html" %}
{% include "components/layout/_form.html" %}
{% include "components/interactive/_tabs.html" %}
{% include "components/interactive/_accordion.html" %}
{% include "components/interactive/_hamburger.html" %}
{% include "components/interactive/_carousel.html" %}
{% include "components/text/_text_component.html" %}
{% include "components/media/_image.html" %}
{% include "components/media/_video.html" %}
{% include "components/media/_gif.html" %}
{% include "components/media/_video_background.html" %}
{% include "components/ui/_button.html" %}
{% include "components/ui/_titlebar.html" %}
{% include "components/ui/_br.html" %}
{% include "components/forms/_textbox.html" %}
{% include "components/forms/_textarea.html" %}
{% include "components/forms/_dropdown.html" %}
{% include "components/forms/_checkbox.html" %}
{% include "components/forms/_radio.html" %}
{% include "components/forms/_calendar.html" %}

{#- 3. Dispatcher LAST (references all component macros above) -#}
{% include "components/_dispatcher.html" %}
```

### renderer.py Change (line 256-261)

```python
# BEFORE:
template_str = """
    {% import 'macros/_components.html' as components %}
    {% for component in structure %}
        {{ components.render_component(component, tokens, [loop.index0]) }}
    {% endfor %}
"""

# AFTER:
template_str = """
    {% include 'components/_assembly.html' %}
    {% for component in structure %}
        {{ render_component(component, tokens, [loop.index0]) }}
    {% endfor %}
"""
```

**Only 2 lines change:** the import statement and the removal of `components.` prefix.

### Migration Steps

1. Create `templates/components/` directory and subdirectories
2. Extract `build_styles` + `build_flex_styles` macros (lines 1171-1577) into `_utilities.html`
3. Extract `build_tabs_vars` + `build_accordion_vars` (lines 955-1169) into `_vars_builders.html`
4. Extract each component macro verbatim (copy-paste, no logic changes) into its own file
5. Extract `render_component` dispatcher (lines 1-63) into `_dispatcher.html`
6. Create `_assembly.html` with includes in correct order
7. Update `renderer.py` template string (2 lines)
8. **Test:** Render every example template, visually compare output. Diff HTML if possible.
9. Once verified, delete `macros/_components.html`

### Fallback Plan

If anything breaks, revert `renderer.py` to use the original import:
```python
template_str = """
    {% import 'macros/_components.html' as components %}
    ...
"""
```
The old file is kept as backup until the new structure is fully verified.

### Verification Checklist

- [ ] Load `bookstore_template.yaml` - all sections render correctly
- [ ] Load `freshchoice_template.yaml` - all sections render correctly
- [ ] Load `all_components_showcase.yaml` - every component type renders
- [ ] Click components in preview - selection highlighting works
- [ ] Edit properties - changes apply correctly
- [ ] Undo/redo works
- [ ] Titlebar scroll behavior works
- [ ] Carousel navigation works
- [ ] Tabs switching works
- [ ] Accordion expand/collapse works
- [ ] No console errors in browser

---

## Phase 3: Move Config YAMLs (Low Risk)

Move the 3 config YAML files from project root into `ssr_python/config/`.

### Current paths (in `app.py`)

```python
# Line 38: defaults loaded from PROJECT_ROOT (parent of ssr_python/)
defaults_path = os.path.join(PROJECT_ROOT, 'component_defaults.yaml')

# Line 52: schemas loaded from PROJECT_ROOT
schemas_path = os.path.join(PROJECT_ROOT, 'component_schemas.yaml')

# Line 72: schema tokens loaded from PROJECT_ROOT
tokens_path = os.path.join(PROJECT_ROOT, 'schema_tokens.yaml')
```

### New paths

```
ssr_python/config/
  component_defaults.yaml    # moved from project root
  component_schemas.yaml     # moved from project root
  schema_tokens.yaml         # moved from project root
```

### Code changes in `app.py`

```python
# Change all 4 references from PROJECT_ROOT to:
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

defaults_path = os.path.join(CONFIG_DIR, 'component_defaults.yaml')  # lines 38, 62
schemas_path = os.path.join(CONFIG_DIR, 'component_schemas.yaml')    # line 52
tokens_path = os.path.join(CONFIG_DIR, 'schema_tokens.yaml')         # line 72
```

### Also update `llm_service.py`

Check if `llm_service.py` references any of these files. It loads `LLM_COMPONENT_GUIDE.md` from the project root - this path stays unchanged since that file remains at root.

### Verification

- [ ] `python app.py` starts without "not found" warnings
- [ ] GET `/api/schemas` returns JSON
- [ ] GET `/api/defaults` returns JSON
- [ ] GET `/api/tokens` returns JSON
- [ ] Properties panel populates when selecting a component

---

## Phase 4: Python Refactoring with Blueprints (Medium Risk)

Split `app.py` (395 lines) into focused modules using Flask Blueprints.

### New Python structure

```
ssr_python/
  app.py              # Slim: create_app() factory, register blueprints
  config.py           # NEW: Config classes (Dev/Prod/Test), path constants
  extensions.py       # NEW: Load tokens + defaults into shared state
  renderer.py         # Unchanged (only template_str was modified in Phase 2)
  llm_service.py      # Unchanged
  generate_tokens_css.py  # Unchanged
  routes/
    __init__.py       # register_blueprints(app) function
    views.py          # GET / and GET /preview-frame
    render.py         # POST /render
    metadata.py       # GET /api/schemas, /api/defaults, /api/tokens
    images.py         # GET /api/images/search + Pexels/Pixabay providers
    chat.py           # POST /api/chat
```

### `config.py`

```python
import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')

    TOKENS_PATH = os.path.join(BASE_DIR, 'tokens.yaml')
    DEFAULTS_PATH = os.path.join(CONFIG_DIR, 'component_defaults.yaml')
    SCHEMAS_PATH = os.path.join(CONFIG_DIR, 'component_schemas.yaml')
    SCHEMA_TOKENS_PATH = os.path.join(CONFIG_DIR, 'schema_tokens.yaml')
    LLM_GUIDE_PATH = os.path.join(PROJECT_ROOT, 'LLM_COMPONENT_GUIDE.md')

class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000

class ProductionConfig(Config):
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = 5000
```

### `extensions.py`

```python
import yaml, os

TOKENS = {}
COMPONENT_DEFAULTS = {}

def load_shared_data(app):
    global TOKENS, COMPONENT_DEFAULTS
    # Load tokens.yaml and component_defaults.yaml
    # Log results to app.logger
```

### `app.py` (refactored to ~40 lines)

```python
from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from renderer import transparency_to_hex, hex_to_rgb
import os

load_dotenv()

def create_app(config_name=None):
    app = Flask(__name__)
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    configs = {'development': DevelopmentConfig, 'production': ProductionConfig}
    app.config.from_object(configs.get(config_name, DevelopmentConfig))

    app.template_filter('transparency_to_hex')(transparency_to_hex)
    app.template_filter('hex_to_rgb')(hex_to_rgb)

    from extensions import load_shared_data
    load_shared_data(app)

    from routes import register_blueprints
    register_blueprints(app)

    register_security_headers(app)
    return app

def register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        # Same headers as current app.py
        ...

if __name__ == '__main__':
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
```

### Blueprint example: `routes/images.py`

```python
from flask import Blueprint, request, jsonify, current_app
import requests as http_requests

images_bp = Blueprint('images', __name__)

# Move Pexels/Pixabay provider functions here (~150 lines from app.py)

@images_bp.route('/api/images/search')
def search_images():
    # Same logic as current app.py
    ...
```

### Verification

- [ ] `python app.py` starts normally
- [ ] All 7 routes return correct responses
- [ ] Image search works
- [ ] Chat widget works
- [ ] Rendering works
- [ ] No import errors in console

---

## Phase 5: Root Directory Cleanup (Low Risk)

### Delete orphaned files

| File/Directory | Reason |
|---|---|
| `coverage/` | Old Jest coverage from legacy CSR (Sept 2024) |
| `package-lock.json` | No `package.json` exists |
| `ssr_python/=2.31.0` | Accidental pip artifact |
| `ssr_python/swift-sites-ui-wireframe.html` | Outdated wireframe |

### Move planning docs to `docs/`

Move all planning/reference `.md` files (except `README.md`, `CLAUDE.md`, `LLM_COMPONENT_GUIDE.md`) to a `docs/` directory:

```
docs/
  ARCHITECTURE.md
  API_ROUTES_DATA_FLOW.md
  COMPONENT_PROPERTIES_MATRIX.md
  MEDIA_CAROUSEL_ENHANCEMENTS.md
  LLM_CHAT_DESIGN.md
  IFRAME_PREVIEW_PLAN.md
  ... (other planning docs)
```

### Move test YAMLs

Move root-level test YAML files to `example_templates/tests/`:
- `blockquote_showcase.yaml`, `interactive_components_test.yaml`, `layout_components_test.yaml`, etc.

### Verification

- [ ] `python ssr_python/app.py` starts normally
- [ ] No broken file references

---

## Phase 6: Testing Foundation (Low Risk)

### Test structure

```
ssr_python/tests/
  __init__.py
  conftest.py              # Flask test client, sample fixtures
  test_renderer.py         # Core rendering tests
  test_routes.py           # API endpoint tests
  test_security.py         # Security header/leak tests
  fixtures/
    sample_page.yaml       # Minimal page YAML for testing
```

### Priority tests

1. **Render simple page** - POST `/render` with page+heading YAML, verify HTML contains expected tags
2. **Render nested components** - layout-row with columns, verify `data-component-id` attributes
3. **Merge with defaults** - component without properties gets defaults applied
4. **API endpoints return JSON** - `/api/schemas`, `/api/defaults`, `/api/tokens` all return 200
5. **Security headers present** - every response has `X-Frame-Options`, `CSP`, `X-Content-Type-Options`
6. **Error responses safe** - render errors don't leak tracebacks or API keys
7. **Invalid YAML handled** - POST `/render` with garbage returns error, not crash

### Run tests

```bash
cd ssr_python
pip install pytest
python -m pytest tests/ -v
```

---

## Implementation Order Summary

| Step | What | Risk | Functional Impact |
|------|------|------|-------------------|
| 1 | Security fixes (Phase 1) | Low | None - removes dead code and changes startup config |
| 2 | Template split (Phase 2) | Medium | None if done correctly - exact same macros, just in separate files |
| 3 | Move config YAMLs (Phase 3) | Low | None - just path updates |
| 4 | Python blueprints (Phase 4) | Medium | None - same routes, same logic, just reorganized |
| 5 | Root cleanup (Phase 5) | Low | None - removes unused files |
| 6 | Add tests (Phase 6) | None | None - adds new files only |

**Key safety measure:** After EACH phase, start the server and verify the full verification checklist. Do not proceed to the next phase until the current phase is confirmed working.

---

## Files Modified Summary

### Phase 1
- `static/js/utils/object.js` - Remove telemetry blocks
- `app.py` line 395 - Fix debug/host
- `requirements.txt` - Pin versions
- NEW: `.env.example`

### Phase 2
- NEW: `templates/components/` directory with 28 files
- `renderer.py` lines 256-261 - Change import to include
- DELETE (after verification): `templates/macros/_components.html`

### Phase 3
- MOVE: `component_defaults.yaml` -> `config/component_defaults.yaml`
- MOVE: `component_schemas.yaml` -> `config/component_schemas.yaml`
- MOVE: `schema_tokens.yaml` -> `config/schema_tokens.yaml`
- `app.py` - Update 4 path references

### Phase 4
- REWRITE: `app.py` (395 lines -> ~40 lines)
- NEW: `config.py`, `extensions.py`, `routes/__init__.py`, `routes/views.py`, `routes/render.py`, `routes/metadata.py`, `routes/images.py`, `routes/chat.py`

### Phase 5
- DELETE: `coverage/`, `package-lock.json`, `ssr_python/=2.31.0`
- MOVE: Planning docs to `docs/`
- MOVE: Test YAMLs to `example_templates/tests/`

### Phase 6
- NEW: `tests/` directory with test files

---

## Final Target Directory Structure

```
python-vibe-coding/
  README.md
  CLAUDE.md
  LLM_COMPONENT_GUIDE.md
  .gitignore
  docs/                              # Planning/reference docs
  example_templates/                 # User templates + tests/
  ssr_python/
    app.py                           # Slim app factory (~40 lines)
    config.py                        # Configuration classes
    extensions.py                    # Shared data loading
    renderer.py                      # Core rendering engine
    llm_service.py                   # LLM service
    generate_tokens_css.py           # Token CSS generator
    requirements.txt                 # Pinned dependencies
    tokens.yaml                      # Design tokens
    .env.example                     # Environment template
    config/
      component_defaults.yaml
      component_schemas.yaml
      schema_tokens.yaml
    routes/
      __init__.py
      views.py
      render.py
      metadata.py
      images.py
      chat.py
    templates/
      index.html
      preview_frame.html
      components/
        _assembly.html
        _utilities.html
        _vars_builders.html
        _dispatcher.html
        layout/     (5 files)
        interactive/ (4 files)
        text/       (1 file)
        media/      (5 files)
        ui/         (3 files)
        forms/      (6 files)
    static/
      css/          (6 files - unchanged)
      js/           (25+ files - object.js cleaned)
    tests/
      conftest.py
      test_renderer.py
      test_routes.py
      test_security.py
      fixtures/
    logs/           (gitignored)
```
