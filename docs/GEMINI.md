# GEMINI.md

This file provides foundational mandates and expert guidance for Gemini CLI when working with the **Swift Sites** codebase.

## 🚨 Critical Mandates

1. **YAML as Single Source of Truth**: The YAML editor/structure is the absolute source of truth. All state changes (property edits, component insertions, theme updates) MUST update the YAML first, which then triggers a server-side re-render.
2. **SSR Architecture**: The application uses Python/Flask for SSR in `ssr_python/`. All rendering and metadata management occurs in this directory.
3. **Metadata Synchronization**: When adding or modifying component properties, you MUST synchronize three files in `ssr_python/config/`:
   - `component_defaults.yaml`: Default values for insertion.
   - `component_schemas.yaml`: Inspector UI field definitions.
   - `schema_tokens.yaml`: Token-to-dropdown mappings.
4. **No `node_modules`**: Never read or search `node_modules` directories.
5. **Security**: Rigorously protect `.env` files and API keys (Pexels, Pixabay, Ollama). Never include secrets in logs or responses.

---

## SSR Architecture Overview

### Core Rendering Flow

```
YAML Editor → POST /render → Flask Backend (routes/render.py)
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
```

### Iframe Communication Handshake

The preview renders in an isolated iframe. Communication follows this protocol:
1. **`IFRAME_READY`**: Iframe signals it's loaded.
2. **`UPDATE_CONTENT`**: Parent sends rendered HTML to iframe.
3. **`COMPONENTS_READY`**: Iframe confirms DOM update and provides component IDs.
4. **`COMPONENT_CLICKED`**: Iframe relays user selection to parent via ID.
5. **`SET_SELECTION`**: Parent tells iframe which ID to highlight.

---

## Directory Structure (SSR)

- `ssr_python/app.py`: Flask entry point and configuration.
- `ssr_python/renderer.py`: Core logic for merging defaults and rendering Jinja2 templates.
- `ssr_python/templates/components/`: Split Jinja2 macro files (the "view" layer).
- `ssr_python/static/js/`:
  - `ssr_app.js`: Parent-side bridge.
  - `preview_bridge.js`: Iframe-side bridge.
  - `swift-sites-runtime.js`: Standalone JS for interactive components (carousel, tabs, etc.).
  - `propertiesPanel.js`: Renders the inspector UI from schemas.
- `ssr_python/config/`: Component metadata (defaults, schemas, tokens, and LLM guide).

---

## Component Styling Architecture

Styles are applied using two primary methods in Jinja2 macros:

### 1. Inline Styles (`build_styles` macro)
Used for 90% of components. Generates `style="..."` strings directly on elements.
- **File**: `ssr_python/templates/components/_utilities.html`
- **Handles**: Spacing (margins/padding), Appearance (bg, border, radius, shadow), Typography, and "Width Mode".

### 2. CSS Variables (`build_vars` macros)
Used for complex components with nested elements or state-based styling.
- **File**: `ssr_python/templates/components/_vars_builders.html`
- **Used by**: `tabs`, `accordion`, `ticker`, `titlebar`.
- **Logic**: Generates variables like `--tabs-active-color` which are consumed by `static/css/components.css`.

---

## Engineering Standards

### State Mutation
Always use the `Document` API from `yaml.bundle.js` (wrapped in `yamlUtils.js`) to update YAML. This preserves anchors and aliases used by the theme system.

### Component Selection
- Components MUST have a `data-component-id` attribute in the preview.
- Use the `chrome-target` class to enable selection highlighting.
- Path Map: `comp_0_components_1` maps to the YAML path `[0, 'components', 1]`.

### Interactive Components
- Must use the `data-ss-initialized` guard pattern in `swift-sites-runtime.js` to prevent double-initialization during re-renders.
- Must implement a cleanup routine in `SwiftSites.reset()`.

### Adding New Components
1. Create macro in `templates/components/<category>/_name.html`.
2. Register in `_assembly.html` and `_dispatcher.html`.
3. Add CSS to `components.css`.
4. Add metadata to `ssr_python/config/component_defaults.yaml` and `ssr_python/config/component_schemas.yaml`.
5. Add runtime logic to `swift-sites-runtime.js` if interactive.

---

## AI & Media Integration

### AI Chat (Ollama)
- **Backend**: `llm_service.py` handles prompt engineering and YAML extraction.
- **Frontend**: `chat.js` manages the conversation UI and applies YAML actions (`create`, `modify`).
- **Guide**: `ssr_python/config/LLM_COMPONENT_GUIDE.md` is the source of truth for the AI's understanding of available components.

### Images Panel
- Proxy routes in `routes/images.py` handle Pexels/Pixabay API calls.
- `imagesPanel.js` provides search, filtering by color/category, and selection.

---

**Last Updated**: March 2026
