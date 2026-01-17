# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

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

**`js/script.js`** - Main entry point. Initializes the application.

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
-.logical spacing: `marginBlock`, `marginInline`, `paddingBlock`, `paddingInline`

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

## Component Styling Architecture: Inline Styles vs CSS Variables

This section documents which component properties are configured using inline styles (via `build_styles()`) versus CSS variables (via `vars.append()`). This is critical for understanding how to add new properties or modify existing ones.

### Components Using CSS Variables

These components generate CSS variables that are consumed by `components.css`:

#### **1. Tabs Component**
**CSS Variables Generated:**
- `--tabs-gap` - Layout gap between tabs
- `--tabs-margin-block` - Vertical margin
- `--tabs-margin-inline` - Horizontal margin
- `--tabs-label-font-size` - Tab label font size
- `--tabs-label-font-weight` - Tab label font weight
- `--tabs-label-color-inactive` - Inactive tab text color
- `--tabs-label-color-active` - Active tab text color
- `--tabs-active-color` - Active tab color (alias)
- `--tabs-label-bg-active` - Active tab background
- `--tabs-label-bg-inactive` - Inactive tab background
- `--tabs-active-bg` - Active tab background (alias)
- `--tabs-border-width` - Tab border width
- `--tabs-border-style` - Tab border style (solid/dashed/none)
- `--tabs-content-bg` - Tab content background
- `--tabs-content-border-width` - Content border width
- `--tabs-content-border-style` - Content border style
- `--tabs-content-border-color` - Content border color
- `--tabs-content-padding-block` - Content vertical padding
- `--tabs-content-padding-inline` - Content horizontal padding

**Macro:** `build_tabs_vars()` in `_components.html`
**Properties:** `spacing`, `layout.gap`, `typography.label`, `appearance.tab`, `appearance.content`

#### **2. Accordion Component**
**CSS Variables Generated:**
- `--accordion-gap` - Gap between accordion items
- `--accordion-margin-block` - Vertical margin
- `--accordion-margin-inline` - Horizontal margin
- `--accordion-border-radius` - Border radius
- `--accordion-title-font-size` - Title font size
- `--accordion-title-font-weight` - Title font weight
- `--accordion-title-color` - Title text color
- `--accordion-title-bg` - Title background color
- `--accordion-title-padding-block` - Title vertical padding
- `--accordion-title-padding-inline` - Title horizontal padding
- `--accordion-border-width` - Border width
- `--accordion-border-style` - Border style (solid/dashed/none)
- `--accordion-border-color` - Border color
- `--accordion-content-font-size` - Content font size
- `--accordion-content-font-weight` - Content font weight
- `--accordion-content-color` - Content text color
- `--accordion-content-bg` - Content background color
- `--accordion-content-padding-block` - Content vertical padding
- `--accordion-content-padding-inline` - Content horizontal padding

**Macro:** `build_accordion_vars()` in `_components.html`
**Properties:** `spacing`, `typography.title`, `typography.content`, `appearance`

#### **3. Titlebar Component**
**CSS Variables Generated:**
- `--base-height` - Header height (from `layout.height`)
- `--title-font-size` - Title font size (from `typography.title.size`)
- `--title-font-weight` - Title font weight (from `typography.title.weight`)
- `--titlebar-title-color` - Title text color (from `typography.title.color`)
- `--menu-font-size` - Link font size (from `typography.menu.size`)
- `--menu-font-weight` - Link font weight (from `typography.menu.weight`)
- `--titlebar-link-color` - Link text color (from `typography.menu.color`)
- `--titlebar-link-hover-bg` - Link hover background (from `appearance.focus.background`)
- `--titlebar-link-hover-color` - Link hover color (from `appearance.focus.color`)

**Macro:** `render_titlebar()` generates CSS variables inline
**Properties:** `layout.height`, `typography.title`, `typography.menu`, `appearance.focus`

**Note:** Titlebar also uses `build_styles()` for container-level styles (background, border, spacing).

#### **4. Blockquote Component** (Partial CSS Variable)
**CSS Variables Generated:**
- `--blockquote-border` - Accent border color (from `appearance.border.accentColor`)

**Macro:** `render_text_component()` generates this variable inline for blockquote
**Properties:** `appearance.border.accentColor`

**Note:** Blockquote also uses `build_styles()` for other properties.

---

### Components Using Inline Styles Only

These components use `build_styles()` to generate inline styles directly on the element:

#### **1. Page Component**
**Inline Styles:** All properties via `build_styles(component, tokens, part='outer')`
**Properties:** `layout`, `spacing`, `appearance` (background, border, radius, shadow, padding)

#### **2. Layout Row Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`

#### **3. Layout Column Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`

#### **4. Columnsgrid Component**
**Inline Styles:** All properties via `build_styles()`
**CSS Variables Generated:** `--cols`, `--cols-md`, `--cols-sm` (for grid columns)
**Properties:** `layout.columns`, `layout.gap`, `responsive.breakpoints`, `spacing`, `appearance`

#### **5. Form Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`

#### **6. Text Components** (heading, paragraph, eyebrow, caption, blockquote, link)
**Inline Styles:** All properties via `build_styles()`
**Properties:** `typography` (size, weight, color, alignment, line-height, transform), `spacing`, `appearance`, `layout.widthMode`

**Special Cases:**
- **Blockquote:** Also generates `--blockquote-border` CSS variable for accent color
- **Link:** Uses wrapper div with inline styles, anchor tag has separate underline styles

#### **7. Image Component**
**Inline Styles:** All properties via `build_styles()`
**Additional Inline:** `height` from `presentation.height`, `object-fit` from `presentation.fit`
**Properties:** `layout.widthMode`, `spacing`, `appearance`, `presentation`

#### **8. Video Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout.widthMode`, `spacing`, `appearance`, `presentation`

#### **9. GIF Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout.widthMode`, `spacing`, `appearance`, `presentation`

#### **10. Button Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `typography`, `spacing`, `appearance`, `layout`

#### **11. Carousel Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`

#### **12. Hamburger Component**
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`

#### **13. Form Input Components** (textbox, textarea, dropdown, checkbox, radio, calendar)
**Inline Styles:** All properties via `build_styles()`
**Properties:** `layout`, `spacing`, `appearance`, `label`, `field`

---

### Properties Handled by `build_styles()` Macro

The `build_styles()` macro generates inline styles for these property categories:

#### **Layout Properties:**
- `display: flex` / `flex-direction` (row/column)
- `align-items`
- `gap` (from tokens)
- `flex-wrap`
- `--cols`, `--cols-md`, `--cols-sm` (for columnsgrid)

#### **Spacing Properties:**
- `margin-block` (from tokens)
- `margin-inline` (from tokens)
- `padding-block` (from tokens)
- `padding-inline` (from tokens)
- `padding-top`, `padding-right`, `padding-bottom`, `padding-left` (individual)

#### **Appearance Properties:**
- `background-color` (with transparency conversion)
- `border` (width, style, color) - handles `none` style
- `border-radius` (from tokens)
- `box-shadow`

#### **Typography Properties:**
- `font-size` (from tokens)
- `font-weight` (from tokens)
- `color`
- `text-align`
- `line-height`
- `text-transform`

#### **Width Mode Properties** (for text components and images):
- `display: inline-block`
- `box-sizing: border-box`
- `width` and `flex` properties based on `widthMode` (fit/25/50/75/stretch)

---

### Decision Guidelines: When to Use CSS Variables vs Inline Styles

**Use CSS Variables When:**
1. Component has nested elements that need different styling (e.g., tabs have labels and content)
2. Component needs dynamic styling based on state (e.g., active/inactive tabs)
3. Component has complex sub-parts (e.g., accordion title vs content)
4. CSS needs to reference values in calculations (e.g., `calc(var(--base-height) * 0.5)`)
5. Component has hover/focus states that need different colors

**Use Inline Styles When:**
1. Component is a simple single element
2. All styles apply directly to the component element
3. No nested elements need different styling
4. No state-based styling needed
5. Simpler implementation is preferred

**Hybrid Approach:**
- Some components use both (e.g., titlebar uses inline styles for container and CSS variables for nested elements)
- Blockquote uses inline styles for most properties but CSS variable for accent border color

---

### Adding New Properties

When adding a new property to a component:

1. **Check existing pattern:** Look at similar components to see if they use CSS variables or inline styles
2. **For CSS Variables:** Add variable generation in the component macro (or `build_tabs_vars()` / `build_accordion_vars()`)
3. **For Inline Styles:** Add property handling in `build_styles()` macro
4. **Update CSS:** Add CSS variable usage in `components.css` if using CSS variables
5. **Update Defaults:** Add default value in `component_defaults.yaml`
6. **Update Schema:** Add field definition in `component_schemas.yaml`

---

**Last Updated:** December 2024