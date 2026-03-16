# AGENTS.md

This file provides guidance to AI agents (Claude, Gemini, etc.) when working with the **Swift Sites** codebase.

## Project Overview

**Swift Sites** is a YAML-based website builder with server-side rendering. Users write YAML in an editor, and the application renders a live preview in an isolated iframe with component selection and properties editing. The YAML structure is the single source of truth - all changes flow through it, ensuring the preview, properties panel, history, and export stay synchronized.

**Architecture:** Server-Side Rendering (SSR) using Python Flask + Jinja2 templates. Preview renders in an iframe for complete style isolation.

DO NOT READ node_modules into context. They are not necessary.

---

## Commands

### SSR Development

```bash
cd ssr_python
pip install -r requirements.txt    # Install Python dependencies
python app.py                       # Start Flask server at http://localhost:5000
python -m pytest tests/ -v          # Run test suite (30 tests)
```

---

## SSR Architecture Overview

### Core Rendering Flow (with Iframe)

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
├── app.py                    # Flask application entry point
├── config.py                 # Configuration and path constants
├── renderer.py               # Core rendering engine
├── llm_service.py            # AI integration for chat (Ollama/Gemini)
├── tokens.yaml               # Design tokens (spacing, typography, etc.)
├── generate_tokens_css.py    # Token to CSS generator
├── requirements.txt          # Python dependencies
├── config/                   # Component metadata
│   ├── component_defaults.yaml   # Default properties per component type
│   ├── component_schemas.yaml    # Inspector form definitions
│   ├── schema_tokens.yaml        # Token-to-dropdown mappings
│   └── LLM_COMPONENT_GUIDE.md    # Guide for AI generation
├── templates/
│   ├── index.html            # Main application UI (with iframe)
│   ├── preview_frame.html    # Iframe preview template
│   └── components/           # Split Jinja2 component macros
└── static/
    ├── css/                  # Stylesheets
    └── js/                   # Frontend logic
```

---

## Iframe Preview Architecture

The preview renders inside an isolated iframe for complete CSS isolation.

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

---

## Template System (Jinja2)

### Architecture

**Macro-Based Component System:**
- Each component type has its own macro.
- Main dispatcher `render_component()` in `_dispatcher.html` routes to the appropriate macro.
- Macros call `render_component()` recursively for nested components.
- Style generation is handled by the `build_styles()` macro in `_utilities.html`.

---

## Client-Side JavaScript Modules

### Core Application

| Module | Purpose |
|--------|---------|
| `main.js` | Application bootstrap, DOM init, event wiring |
| `ssr_app.js` | SSR rendering bridge, iframe postMessage communication |
| `preview_bridge.js` | Runs in iframe, handles content updates and click relay |
| `swift-sites-runtime.js` | Standalone runtime for interactive components (carousel, tabs, etc.) |

---

## Metadata Files

The following metadata files in `ssr_python/config/` must stay synchronized:

| File | Purpose |
|------|---------|
| `component_defaults.yaml` | Default properties for each component type |
| `component_schemas.yaml` | Inspector form fields, types, labels, token refs |
| `schema_tokens.yaml` | Design token options for dropdowns |
| `LLM_COMPONENT_GUIDE.md` | LLM-friendly guide for YAML generation |

---

**Last Updated:** March 2026
