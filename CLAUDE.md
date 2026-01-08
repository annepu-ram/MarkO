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
