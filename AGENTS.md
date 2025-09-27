# Website Builder Explanation

## Project Snapshot
- Client-side visual website builder driven entirely by a YAML document.
- Core runtime: `index.html` bootstraps Mini.css, js-yaml, and `/js/script.js` which serves as the main entry point.
- The application logic is modular, with different responsibilities handled by scripts in the `js/core`, `js/properties`, `js/render`, `js/ui`, and `js/utils` directories.
- Users edit YAML in the left-hand editor; the preview pane renders the interpreted structure in real time.
- Component defaults live in `component_defaults.yaml`, ensuring consistent starter props across insertions and property panels.
- Component property schemas are defined in `component_schemas.yaml`, and design tokens are in `schema_tokens.yaml`.

## Application Lifecycle
1. `DOMContentLoaded` triggers `initializeApp()` from `js/script.js` (via `js/core/app.js`).
2. `loadMetadata()` (in `js/core/templates.js`) loads component defaults, schemas, and tokens.
3. Event listeners are initialized in `js/ui/events.js`.
4. The initial editor content is parsed, and the initial preview is rendered.

## YAML Data Model
- Expected top-level array with a single object: `{ name: 'page', properties, components }`.
- Simple components carry a `properties` object (text, color, sizing, etc.).
- Container components add nested collections: `components` (generic), `columns`, `tabs`, `slides`, or `content.components` for accordions.
- `componentPathMap` (in `js/core/state.js`) links rendered DOM nodes back to their YAML path for selection, deletion, and property editing.

## Rendering Pipeline
- `renderYamlStructure()` (in `js/render/index.js`) dispatches by `name`, delegating to helpers for page, grids, accordion, tabs, carousel, forms, images, or simple elements.
- Simple components call `generateComponentInnerHTML()` which merges Mini.css classes with inline styles.
- Containers recursively call `renderComponentsList()` on nested paths, adding editor-only chrome (labels, drop zones, delete buttons) when in preview mode.
- Export mode omits editor wrappers, returning clean HTML for downloads and fullscreen preview.

## User Interaction Flow
- Preview clicks are handled by `handlePreviewClick()` in `js/ui/actions.js`, which highlights selections and loads their properties into the side panel.
- The property panel UI is built by `renderPropertiesPanel()` in `js/properties/index.js`, combining defaults with instance props.
- "Apply Changes" invokes `applySelectedComponentProperties()` in `js/ui/actions.js`, which serializes updated props back into YAML, re-parses, re-renders, and restores selection.
- Sidebar component buttons call `insertComponent()` in `js/ui/actions.js`, cloning defaults and injecting scaffolding.

## Styling Strategy
- Component defaults own all typography and color baselines.
- `css/style.css` controls the builder shell.
- `css/components.css` augments Mini.css for rendered components.
- `generateRemainingStyles()` (in `js/render/index.js`) converts user props to inline styles.

## Dynamic Components
- `js/component_interactions.js` exposes initializers for complex components like carousels and titlebars.
- `registerComponentForInitialization()` queues these during rendering.

## Key Files
- `index.html`: Application shell, script/style includes, help panel content.
- `js/script.js`: Main entry point.
- `js/core/app.js`: Core application initialization.
- `js/core/state.js`: State management.
- `js/core/templates.js`: Loading component templates and schemas.
- `js/core/yaml.js`: YAML parsing and manipulation.
- `js/properties/index.js`: Properties panel rendering.
- `js/properties/customRenderers.js`: Custom property editors.
- `js/render/index.js`: Component rendering engine.
- `js/ui/actions.js`: UI actions.
- `js/ui/events.js`: Event listeners.
- `js/utils/`: Utility functions.
- `js/component_interactions.js`: Client-side behaviors for interactive components.
- `css/style.css`: UI styling for builder workspace.
- `css/components.css`: Supplementary styling for rendered components.
- `component_defaults.yaml`: Template props for every component type.
- `component_schemas.yaml`: Schema for component properties.
- `schema_tokens.yaml`: Design tokens for property editors.