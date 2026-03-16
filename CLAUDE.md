# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
python -m pytest tests/ -v          # Run test suite (1026 tests)
```

### RAG Index Management

```bash
cd ssr_python
python -m rag.scripts.build_index   # Rebuild RAG index from source documents
# Or via API: POST /api/rag/rebuild-index
# Check status: GET /api/rag/status
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
│   ├── schema_tokens.yaml        # Design token options for dropdowns
│   ├── style_presets.yaml        # Visual style presets
│   ├── COMPONENT_SYNTAX_REFERENCE.md  # Component syntax reference (RAG guide tier)
│   ├── STYLE_THEMES_REFERENCE.md     # 22 style chunks with themes (RAG style tier)
│   └── COMMON_MISTAKES_REFERENCE.md  # Common YAML mistakes (not indexed)
├── routes/                   # Flask Blueprint route modules
│   ├── __init__.py           # register_blueprints() function
│   ├── views.py              # GET /, GET /preview-frame
│   ├── render.py             # POST /render
│   ├── metadata.py           # GET /api/schemas, /api/defaults, /api/tokens
│   ├── images.py             # GET /api/images/search (Pexels/Pixabay proxy)
│   ├── uploads.py            # POST /api/images/upload, download, GET /uploads/
│   ├── chat.py               # POST /api/chat (RAG pipeline)
│   ├── rag.py                # GET/POST /api/rag/* (index management, debug search)
│   ├── site.py               # Site/page CRUD, publish, versions
│   ├── media.py              # GET /api/sites/<id>/media
│   └── submissions.py        # Form submission management
├── rag/                      # RAG pipeline for AI website generation
│   ├── config.py             # RAGConfig: paths, tiers, retrieval params, model settings
│   ├── agent/                # AI agent pipeline
│   │   ├── planner_agent.py  # Site outline generator (create_page intent)
│   │   ├── builder_agent.py  # Per-section YAML generator
│   │   ├── stitcher.py       # Assembles sections into full site YAML
│   │   ├── rag_agent.py      # Orchestrator: planner → builder × N → stitcher
│   │   ├── query_analyzer.py # Intent detection + metadata filters
│   │   ├── model_backend.py  # LLM backend abstraction (Ollama/OpenAI/Anthropic/Groq)
│   │   ├── component_specs.py # Build component specs for builder prompt
│   │   └── prompt_builder.py # Context budget management
│   ├── embeddings/
│   │   └── embed_service.py  # Embedding via Ollama or sentence-transformers
│   ├── indexing/
│   │   ├── chunker.py        # YAML-aware + markdown chunking
│   │   ├── icon_chunker.py   # Lucide icon name vectorization
│   │   ├── index_builder.py  # Full index build pipeline
│   │   └── metadata.py       # Chunk metadata extraction (section, industry, style)
│   ├── retrieval/
│   │   ├── hybrid.py         # Tiered RRF + MMR diversity search
│   │   ├── vector_search.py  # FAISS vector search
│   │   ├── keyword_search.py # BM25 keyword search
│   │   ├── reranker.py       # Cross-encoder reranker (optional)
│   │   └── filters.py        # Metadata filtering
│   ├── scripts/
│   │   ├── build_index.py    # CLI index rebuild
│   │   └── evaluate_retrieval.py  # Retrieval quality evaluation
│   └── data/                 # Built index files (JSONL + FAISS)
├── models.py                 # SQLAlchemy models (Site, SitePage, SiteImage, etc.)
├── storage.py                # File storage abstraction (local/S3)
├── guards.py                 # Auth/org guards
├── tests/                    # pytest test suite (1026 tests)
│   ├── conftest.py           # Fixtures: app, client, sample YAMLs
│   ├── fixtures/
│   │   └── sample_page.yaml  # Test fixture YAML
│   ├── test_renderer.py      # deep_merge + render tests
│   ├── test_routes.py        # API endpoint tests
│   ├── test_security.py      # Security header + error sanitization tests
│   ├── test_dashboard.py     # Dashboard, sites, pages, versions, submissions
│   ├── test_settings.py      # Settings API tests
│   └── test_yaml_validation.py  # YAML template validation (all example_templates)
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
    │   ├── themesPanel.js        # Theme selection and application
    │   ├── imagesPanel.js        # Stock photo search, selection, upload
    │   ├── pageManager.js        # Multi-page management
    │   ├── siteManager.js        # Site save/load
    │   ├── settingsPanel.js      # Settings panel
    │   ├── dashboard.js          # Dashboard UI
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
- `LLM_GUIDE_PATH` - Path to `config/COMPONENT_SYNTAX_REFERENCE.md`

### `extensions.py` - Shared State

**Purpose:** Module-level `TOKENS` and `COMPONENT_DEFAULTS` dicts that are imported by route modules.

**Pattern:** Uses `.clear()` + `.update()` to mutate in-place (preserves references across imports).

### `routes/` - Flask Blueprints

| Module | Blueprint | Routes |
|--------|-----------|--------|
| `views.py` | `views_bp` | `GET /`, `GET /preview-frame` |
| `render.py` | `render_bp` | `POST /render` |
| `metadata.py` | `metadata_bp` | `GET /api/schemas`, `/api/defaults`, `/api/tokens` |
| `images.py` | `images_bp` | `GET /api/images/search` (Pexels/Pixabay proxy) |
| `uploads.py` | `uploads_bp` | `POST /api/images/upload`, `/download`, `/download-batch`, `GET /uploads/` |
| `chat.py` | `chat_bp` | `POST /api/chat` (RAG pipeline) |
| `rag.py` | `rag_bp` | `GET/POST /api/rag/*` (index status, rebuild, debug search) |
| `site.py` | `site_bp` | Site/page CRUD, publish, versions |
| `media.py` | `media_bp` | `GET /api/sites/<id>/media`, `DELETE .../media/<id>` |
| `submissions.py` | `submissions_bp` | Form submission management |

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

---

## Ticker Component

A horizontally scrolling strip of content using `columns:` array (columnsgrid-like pattern). Background is always transparent; column background is configurable.

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
```

---

## Metadata Files

The following metadata files must stay synchronized:

| File | Purpose |
|------|---------|
| `component_defaults.yaml` | Default properties for each component type |
| `component_schemas.yaml` | Inspector form fields, types, labels, token refs |
| `schema_tokens.yaml` | Design token options for dropdowns |
| `tokens.yaml` | CSS token values (snake_case keys) |
| `COMPONENT_SYNTAX_REFERENCE.md` | Component syntax reference for LLM + RAG |
| `STYLE_THEMES_REFERENCE.md` | 22 visual style chunks with themes for RAG |

---

## RAG Pipeline (AI Website Generation)

### Architecture: Planner → Builder × N → Stitcher

```
User Query → QueryAnalyzer (intent detection)
                ↓
          PlannerAgent (outline + theme + image assignment)
                ↓
          BuilderAgent × N (one per section, parallel YAML generation)
                ↓
          Stitcher (assembles sections into full site YAML)
                ↓
          Final YAML response
```

Orchestrated by `rag_agent.py`. Each agent uses RAG-retrieved context from the tiered index.

### RAG Tiers and Doc Types

| Tier | Doc Types | Used By | Source |
|------|-----------|---------|--------|
| `section` | `template_section`, `template_full_page` | Builder agent | YAML templates |
| `component` | `template` | Builder fallback | YAML templates |
| `guide` | `guide`, `outline`, `other` | Planner (outlines) | `.md` files, `website_example_outlines/` |
| `style` | `style` | Planner (style/theme) | `STYLE_THEMES_REFERENCE.md` |
| `icon` | `icon` | Planner (icon names) | `lucide-icons.json` |

Config: `rag/config.py` (`RAGConfig` dataclass). Source dirs, tier mappings, retrieval params, model settings.

### Planner Agent Prompt Structure

The planner receives a compact system prompt (~40 lines) + RAG-retrieved user context:

```
[Style]     — 1-2 style chunks from STYLE_THEMES_REFERENCE.md (via tier="style")
[Outline]   — 1-2 website outline chunks (via tier="guide")
[Available Icons] — top-k icon names (via tier="icon")
[Available Images] — images with alt text, orientation, photographer
[User Request] — the user's message
```

Output: JSON outline with `page_title`, `theme`, `sections[]` (each with `type`, `description`, `components`, `icons`, `images`, `style_notes`).

### Builder Agent

Receives one section from the planner outline. Searches `tier="section"` for matching YAML templates, reranks, and generates YAML. Receives:
- Component specs from `component_specs.py`
- Reference templates from RAG
- Theme string with color aliases
- Image context (pre-assigned images for this section)
- Style notes from planner (layout/color instructions)

### Style System (STYLE_THEMES_REFERENCE.md)

22 visual styles, each a self-contained `##` chunk (~30-40 lines). RAG retrieves by mood/keyword match.

Each style chunk contains:
- **Mood** keywords for search matching
- **Industries** — best-fit verticals
- **4 named theme palettes** (primary/secondary/accent/background + fonts)
- **Property rules** (radius, shadow, border, blur, etc.)
- **Section style_notes** (per-section styling guidance copied to builder)

Style names: Modern Minimalist, Glassmorphism, Retro Vintage, Neubrutalism, Claymorphism, Aurora Gradient, Monochrome Dark, Elegant Luxury, Organic Natural, Corporate Professional, Bold Editorial, Cyberpunk Neon, Pastel Soft, Scandinavian Clean, Art Deco Geometric, Tropical Vibrant, Dark Academia, Memphis Design, Zen Japanese, Industrial Grunge, Y2K Retro-futurism, Bohemian Eclectic.

### Index Building

Source documents: `example_templates/` (YAML), `website_example_outlines/` (MD), `config/COMPONENT_SYNTAX_REFERENCE.md`, `config/STYLE_THEMES_REFERENCE.md`.

Chunking: YAML split at `- name:` boundaries (component level) + full section chunks. Markdown split at `## ` headings. Icons split per-name.

Metadata extraction (`metadata.py`): section_type, industry, visual_style, layout_pattern, component_types — used for filtering and enrichment.

Rebuild: `python -m rag.scripts.build_index` or `POST /api/rag/rebuild-index`.

---

## Image Storage and Management

### Image Flow

```
Stock Search (Pexels/Pixabay)     User Upload
     ↓                                 ↓
  /api/images/search              /api/images/upload
     ↓                                 ↓
  Frontend selects image          File uploaded
     ↓                                 ↓
  /api/images/download            Convert to WebP
     ↓                                 ↓
  Download + WebP convert         Store via storage backend
     ↓                                 ↓
  SiteImage record in DB          SiteImage record in DB
     ↓                                 ↓
  /api/sites/<id>/media ← DB is single source of truth
```

### Key Details

- **Storage**: All raster images converted to WebP on ingest. SVGs stored as-is. Tenant-scoped paths: `org_id/site_id/uuid.webp`.
- **Alt text**: Stock images get alt text from API (Pexels `alt`, Pixabay `tags`). Uploaded images derive alt text from original filename (`hero-banner.jpg` → `hero banner`). Fallback chain in chat.py: `alt_text → cleaned original_name → filename`.
- **Resolution**: Stock downloads use `fullUrl` (Pexels `original`, Pixabay `largeImageURL`) for full resolution.
- **Original name**: For stock downloads, `original_name` = alt text (human-readable). For uploads, `original_name` = uploaded filename.
- **Deduplication**: `_download_and_store()` checks `source_url` to skip re-downloading the same stock image.
- **Model**: `SiteImage` in `models.py` — fields: `id`, `site_id`, `filename`, `original_name`, `alt_text`, `orientation`, `photographer`, `source`, `source_url`, `storage_path`, `width`, `height`.

### Image → Planner Flow

Chat endpoint (`chat.py`) queries `SiteImage` by `site_id`, builds `selected_images` list with `{url, altText, orientation, photographer}`. Planner receives these as `[Available Images]` context and assigns each to a section based on content and orientation.

---

## Chat & Intent System

### Chat Request Flow

```
Frontend (chatService.js)
  ↓ POST /api/chat { message, currentYaml, selectedComponent, siteId }
  ↓
chat.py → queries SiteImage by siteId → builds selected_images list
  ↓
llm_service.py (singleton LLMService)
  ├── RAG_ENABLED=true  → rag_agent.chat() → multi-agent pipeline
  └── RAG_ENABLED=false → legacy single-call (system prompt + Ollama)
  ↓
_parse_response() → extracts ACTION comment + YAML block
  ↓
{ response, yaml, action } → frontend applies action
```

### Intent Detection (`query_analyzer.py`)

Rule-based `QueryAnalyzer` classifies user messages into intents using regex patterns. First match wins (ordered by specificity).

| Intent | Trigger Pattern | RAG Tier | Pipeline |
|--------|----------------|----------|----------|
| `create_page` | "create/build/make a page/website/site" | section | Multi-agent (planner → builder × N → stitcher) |
| `create_section` | "create/add a section/hero/pricing" | section | Single-call RAG |
| `modify` | "change/update/modify/edit/fix" | component | Single-call RAG |
| `add` | "add/insert a button/image/text" | component | Single-call RAG |
| `explain` | "what/how/explain/tell me" | guide | Single-call RAG |

**Metadata filters** extracted alongside intent:
- `section_filter`: hero, pricing, testimonial, footer, features, cta, faq, etc.
- `industry_filter`: saas, restaurant, ecommerce, portfolio, health, education, etc.
- `style_filter`: glassmorphism, modern, retro, neubrutalism, claymorphism, etc.
- `component_filter`: button, image, badge, accordion, carousel, tabs, etc.
- `sub_queries`: Complex `create_page` requests decomposed into per-section queries (e.g., "with hero, pricing, and testimonials" → 3 sub-queries)

### Action Types (LLM Response Format)

The LLM response starts with `<!-- ACTION: type -->` and optionally contains a `yaml` code block.

| Action | When | YAML? | Frontend Behavior |
|--------|------|-------|-------------------|
| `create` | New page/site generation | Yes (full page) | Replace editor content |
| `modify` | Component property changes | Yes (component only) | Merge at selected path |
| `delete` | Remove selected component | No | Remove from YAML tree |
| `insert_child` | Add inside selected container | Yes (new component) | Append to container's components |
| `insert_after` | Add after selected component | Yes (new component) | Insert as sibling |
| `explain` | Questions/help | No | Display text response |
| `settings` | SEO/meta generation | Yes (settings fields) | Update site settings |
| `error` | Cannot fulfill request | No | Display error message |

### RAG Agent Routing (`rag_agent.py`)

- `create_page` intent → `_create_page_pipeline()` (multi-agent)
- All other intents → `_single_call_rag()` (retrieve → prompt → generate)

Single-call RAG includes:
1. Tiered search with metadata filters from intent
2. Fallback to `section` tier if initial tier returns too few results
3. Reranking (optional, via `config.use_reranker`)
4. Context-budgeted prompt building (`prompt_builder.py`)
5. Validation-guided retry (1 retry if YAML has parse/structural errors)

### Legacy Pipeline (RAG_ENABLED=false)

`llm_service.py` sends the full `COMPONENT_SYNTAX_REFERENCE.md` as system context + structured user prompt with `[CURRENT YAML STATE]`, `[SELECTED COMPONENT]`, `[AVAILABLE IMAGES]`, and `[USER REQUEST]` sections. Single Ollama API call, response parsed by `_parse_response()`.

### Progress Tracking

Chat endpoint exposes `GET /api/chat/status` polled by the frontend. Status updates flow via `progress_fn` callback through the pipeline stages: "Analyzing request..." → "Planning site structure..." → "Building components..." → "Assembling page..." → "Finalizing...".

---

## Troubleshooting SSR

**Preview not updating?**
- Check browser console for `[SSR App]` and `[Preview Bridge]` messages
- Verify IFRAME_READY handshake completed (look for "acknowledged by parent")
- Check Network tab for `/render` response

**YAML not persisting across refresh?**
- Uses `sessionStorage` (tab-scoped) - each tab has isolated storage
- Content is lost when browser/tab closes

---

**Last Updated:** March 14, 2026
