# Swift Sites - YAML-Based Website Builder

## Overview

**Swift Sites** is a fully client-side YAML-based website authoring environment that transforms structured YAML documents into live, interactive website previews. The application provides a powerful yet intuitive interface for building websites through direct YAML editing, with real-time preview, properties inspection, and export capabilities.

### Key Features

- 🎯 **YAML-First Authoring**: Write structured YAML to define your entire website
- 👁️ **Live Preview**: See changes instantly with interactive component selection
- 🎨 **Visual Properties Editor**: Edit component properties through an intuitive inspector panel
- 📦 **Component-Based Architecture**: 20+ pre-built components (layouts, text, media, forms)
- 🔄 **Undo/Redo Support**: Full history management for all changes
- 💾 **Export to HTML**: Generate clean, production-ready HTML
- 🎭 **Fullscreen Preview**: View your site in fullscreen mode
- 🎪 **Zero Build Step**: Pure client-side application, no compilation required

## Quick Start

### Installation

1. Clone the repository
2. Open `index.html` in a modern browser (Chrome, Firefox, Safari, Edge)
3. Start editing YAML in the left editor panel!

### Development Setup

```bash
# Install dependencies
npm install

# Run tests
npm test

# Rebuild icon sprite (after modifying icon subset)
npm run build:sprite

# Development
# Simply open index.html with Live Server or similar tool
```

## Architecture

### Core Data Flow

```
┌──────────────┐
│ YAML Editor  │ ← User types YAML
└──────┬───────┘
       │ parseYamlContent()
       ↓
┌──────────────────────┐
│ State.yamlStructure  │ ← Single source of truth
└──────┬───────────────┘
       │
       ├→ User selects component → State mutation
       │                               ↓
       ├→ renderYamlStructure() → Preview DOM (with chrome)
       │                               ↓
       ├→ Properties Panel ← Component selection
       │       ↓
       └→ Apply changes → Update YAML → Re-render
```

**Key Principle**: The YAML editor is the authoritative source of truth. All state changes flow through YAML updates, ensuring perfect synchronization between editor, preview, properties panel, history, and export.

### Directory Structure

```
swift-sites/
├── index.html                      # Application shell
├── css/
│   ├── style.css                   # Workspace UI styles
│   └── components.css              # Component default styles
├── js/
│   ├── script.js                   # Application entry point
│   ├── core/                       # Core runtime
│   │   ├── app.js                  # Bootstrap & initialization
│   │   ├── state.js                # Global state management
│   │   ├── yaml.js                 # YAML parsing/serialization
│   │   └── templates.js            # Metadata loading
│   ├── render/                     # Rendering engine
│   │   └── index.js                # Component renderers
│   ├── properties/                 # Properties inspector
│   │   ├── index.js                # Inspector UI builder
│   │   └── customRenderers.js      # Custom property editors
│   ├── ui/                         # User interactions
│   │   ├── actions.js              # User actions (insert, delete, etc.)
│   │   └── events.js               # Event listeners
│   ├── utils/                      # Utility functions
│   │   ├── object.js               # Deep cloning, merging
│   │   ├── strings.js              # HTML escaping, formatting
│   │   ├── styles.js               # CSS value resolution
│   │   ├── timing.js               # Debouncing
│   │   └── sprite.js               # SVG sprite management
│   └── component_interactions.js   # Interactive component init
├── component_defaults.yaml          # Default component properties
├── component_schemas.yaml           # Inspector form definitions
└── schema_tokens.yaml               # Design tokens (colors, sizes, etc.)
```

## YAML Data Model

### Page Structure

Every document starts with a `page` component:

```yaml
- name: page
  properties:
    background:
      color: '#ffffff'
    layout:
      padding:
        top: md
        right: md
        bottom: md
        left: md
  components:
    # Your components here
```

### Component Types

#### Simple Components
Components with properties only:

```yaml
- name: heading
  properties:
    text: |
      My Heading
      Supports multiline
    level: 2
    typography:
      size: xl
      weight: bold
      color: '#111827'
    spacing:
      marginBlock: md
```

#### Container Components
Components that nest other components:

```yaml
- name: layout-row
  properties:
    layout:
      gap: md
      align: center
  components:
    - name: heading
      properties:
        text: Column 1
    - name: paragraph
      properties:
        text: Column 2
```

#### Special Structure Components

**Accordion** (items-based):
```yaml
- name: accordion
  properties:
    items:
      - title: Section 1
        content: |
          Multiline content
          supported here
      - title: Section 2
        content: More content
    behavior:
      allowMultipleOpen: false
```

**Tabs** (tabs array):
```yaml
- name: tabs
  properties:
    layout:
      orientation: horizontal
  tabs:
    - title: Tab 1
      components:
        - name: paragraph
          properties:
            text: Tab 1 content
```

**Carousel** (slides array):
```yaml
- name: carousel
  properties:
    behavior:
      autoplay: true
      delay: 3000
  slides:
    - components:
        - name: image
          properties:
            source:
              url: slide1.jpg
```

## Component Catalog

### Layout Components
- **layout-row**: Horizontal flexbox container
- **layout-column**: Vertical flexbox container
- **columnsgrid**: Responsive CSS grid layout
- **form**: Form container with fields

### Text Components
- **heading**: H1-H6 headings with levels
- **paragraph**: Body text with multiline support
- **eyebrow**: Small uppercase label text
- **caption**: Small secondary text
- **blockquote**: Quotations with citation

### Interactive Components
- **accordion**: Collapsible content sections
- **tabs**: Tabbed content interface
- **carousel**: Image/content slideshow
- **button**: Clickable buttons with actions
- **link**: Hyperlinks with optional arrows

### Media Components
- **image**: Images with overlay support
- **video**: Embedded videos
- **gif**: Animated GIFs

### Form Components
- **textbox**: Single-line text input
- **textarea**: Multi-line text input
- **dropdown**: Select dropdown
- **checkbox**: Checkbox input
- **radio**: Radio button input
- **calendar**: Date picker

### Navigation Components
- **titlebar**: Site header with logo and links
- **hamburger**: Mobile menu

### Utility Components
- **br**: Spacing break

## Rendering Pipeline

### Preview Mode (with Chrome)

1. **Parse YAML** → Convert YAML text to JavaScript structure
2. **Clear Component Path Map** → Reset DOM ID → YAML path mappings
3. **Route Components** → Each component type uses specialized renderer
4. **Generate HTML** → Apply properties, styles, and tokens
5. **Wrap in Chrome** → Add interactive selection overlay:
   - Inject `.chrome-target` class directly on component
   - Add `.chrome-label` and `.chrome-delete` as first children
   - Apply `position: relative` for chrome positioning
   - Chrome is absolutely positioned over component
   - **Zero layout interference** - component participates directly in parent layout
6. **Register Paths** → Map component IDs to YAML paths
7. **Initialize Interactive Components** → Setup carousels, accordions, etc.

### Export Mode (Clean HTML)

Same pipeline but skips chrome wrapping, producing clean, production-ready HTML.

## Chrome Architecture (Zero-Wrapper Approach)

The preview chrome system uses a revolutionary **zero-wrapper** approach that eliminates layout interference:

### Traditional Approach (❌ Problems)
```html
<div class="chrome-wrapper">  <!-- Extra wrapper affects layout -->
  <div class="chrome-overlay">...</div>
  <div class="actual-component">...</div>
</div>
```
**Problems**: Wrapper div interferes with parent's flex/grid layout, causes width calculation issues.

### Zero-Wrapper Approach (✅ Solution)
```html
<div class="accordion chrome-target" data-component-id="comp-123" style="position: relative; ...">
  <span class="chrome-label">accordion</span>
  <button class="chrome-delete">×</button>
  <!-- Original component content here -->
</div>
```

**Benefits**:
- Component element participates directly in parent layout (flex item, grid item)
- No wrapper div to interfere with CSS calculations
- Chrome elements are absolutely positioned above content
- All width/flex styles applied directly to component element

**Implementation**: See `wrapComponentWithChrome()` in `js/render/index.js`

## Properties Panel System

### How It Works

1. **Component Selection** → User clicks component in preview
2. **Fetch Schema** → Load definition from `component_schemas.yaml`
3. **Resolve Values** → Merge component properties with defaults
4. **Render Form** → Generate input fields based on schema
5. **Custom Renderers** → Special UI for complex properties (links, accordion items)
6. **Apply Changes** → User edits → Update YAML → Re-render preview

### Property Resolution Order

```
1. Component instance properties (from YAML)
2. Default values (from component_defaults.yaml)
3. Schema fallbacks (from component_schemas.yaml)
```

### Custom Renderers

For complex properties that can't be edited with simple inputs:

- **linksEditor**: Edit arrays of `{ label, href }` objects (titlebar, hamburger)
- **accordionItems**: Edit accordion items with title/content pairs
- **tabsEditor**: Edit tab definitions
- **carouselSlides**: Placeholder for slide editing (edit in YAML directly)

## Metadata Files

### component_defaults.yaml

Defines default properties for each component type. Used when inserting new components.

```yaml
heading:
  text: |
    Elevate your message
    with a bold statement
  level: 2
  typography:
    size: xl
    weight: bold
    color: '#111827'
  spacing:
    marginBlock: md
```

### component_schemas.yaml

Defines the properties inspector form for each component:

```yaml
heading:
  groups:
    - id: content
      label: Content
      fields:
        - path: text
          type: textarea
          label: Text
          rows: 3
        - path: level
          type: select
          label: Level
          options: [1, 2, 3, 4, 5, 6]
    - id: typography
      label: Typography
      fields:
        - path: typography.size
          type: select
          label: Font Size
          tokens: typographySizes
```

### schema_tokens.yaml

Defines design token scales:

```yaml
typographySizes:
  - { value: xs, label: Extra Small }
  - { value: sm, label: Small }
  - { value: md, label: Medium }
  - { value: lg, label: Large }
  - { value: xl, label: Extra Large }

spacingScale:
  - { value: none, label: None }
  - { value: xs, label: Extra Small }
  - { value: sm, label: Small }
  - { value: md, label: Medium }
  - { value: lg, label: Large }
  - { value: xl, label: Extra Large }
```

## State Management

### Global State (`js/core/state.js`)

```javascript
State = {
  yamlStructure: null,           // Parsed YAML tree
  componentTemplates: null,      // Defaults from component_defaults.yaml
  componentSchemas: null,        // Schemas from component_schemas.yaml
  schemaTokens: null,           // Tokens from schema_tokens.yaml
  selectedComponentPath: null,   // Currently selected component path
  selectedComponentId: null,     // Currently selected component DOM ID
  componentPathMap: new Map(),   // DOM ID → YAML path mapping
  history: [],                  // Undo stack (YAML snapshots)
  historyIndex: -1,            // Current position in history
  maxHistory: 50               // Max undo steps
};
```

### State Mutation Rules

✅ **Correct**:
```javascript
setYamlStructure(newStructure);  // Updates state AND triggers re-render
pushHistory(yamlText);            // Saves undo snapshot
setSelectedComponent(path, id);   // Updates selection
```

❌ **Incorrect**:
```javascript
State.yamlStructure = newStructure;  // Direct mutation - breaks sync!
```

## Component Path Map

Maps DOM element IDs to YAML paths for selection and deletion:

```javascript
// Component in YAML at structure[0].components[2].components[1]
// Gets DOM ID: comp_1234_abcd
// Path map: comp_1234_abcd → [0, 'components', 2, 'components', 1]

registerComponentPath('comp_1234_abcd', [0, 'components', 2, 'components', 1]);

// Later, when clicked:
const path = getComponentPathById('comp_1234_abcd');
const component = getComponentByPath(structure, path);
```

## Testing

### Test Structure

```
js/
├── render/__tests__/
│   ├── index.test.js          # Main renderer tests
│   ├── accordion.test.js      # Accordion-specific tests
│   ├── columnsgrid.test.js    # Grid layout tests
│   └── __snapshots__/         # Snapshot files
├── core/__tests__/
│   └── yaml_multiline.test.js # YAML parsing tests
├── ui/__tests__/
│   └── ...                    # UI behavior tests
└── utils/__tests__/
    └── ...                    # Utility function tests
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- js/render/__tests__/accordion.test.js

# Update snapshots (after intentional changes)
npx jest --updateSnapshot

# Watch mode
npm test -- --watch
```

### Snapshot Tests

Snapshot tests ensure rendered HTML output stays consistent. When you intentionally change component rendering:

1. Run tests - they will fail showing the diff
2. Review the changes carefully
3. Update snapshots: `npx jest --updateSnapshot`
4. Commit the updated snapshot files

## Recent Fixes & Improvements

### Accordion Component Fixes (October 2024)

1. **Background Color Application**
   - **Issue**: Background color applied to container instead of individual items
   - **Fix**: Moved `background-color` from `.accordion-container` to `.accordion-summary` and `.card-body`
   - **File**: `js/render/index.js`

2. **Duplicate Items Array Bug**
   - **Issue**: Adding items via properties panel created duplicate `items` arrays in YAML
   - **Fix**: Moved default merge to execute BEFORE custom editor values are applied
   - **File**: `js/properties/index.js` line 524

3. **Unwanted Components Element**
   - **Issue**: Accordion insertion added unnecessary `content: { components: [] }` to YAML
   - **Fix**: Removed special case that added container structure to accordion
   - **File**: `js/ui/actions.js` line 271-275

4. **Multiline Content Support**
   - **Enhancement**: Accordion content now supports multiline text using YAML pipe operator (`|`)
   - **Implementation**: Uses existing `escapeHtmlWithLineBreaks()` renderer
   - **File**: `component_defaults.yaml`

5. **Default Color Scheme**
   - **Update**: Changed accordion defaults to white background (`#ffffff`) with black text (`#000000`)
   - **File**: `component_defaults.yaml`

### Chrome Architecture Improvements

- Implemented zero-wrapper chrome approach
- Eliminated layout interference from chrome elements
- Chrome elements now injected directly into component as children
- Component participates directly in parent layout (flex/grid)

### Text Component Enhancements

- Multiline text support using YAML block scalars (`|`)
- Width modes: fit/25%/50%/75%/stretch
- Logical spacing properties: `marginBlock`, `marginInline`, `paddingBlock`, `paddingInline`

## Known Constraints

1. **YAML Editor Only**: No visual drag-and-drop interface yet. Layout tree UI is planned.

2. **Static Export**: Exports static HTML only. No asset bundling, CSS extraction, or build pipeline.

3. **Component Path Map Fragility**: Must be rebuilt on every render. All components must call `registerComponentPath()`.

4. **Properties Panel Limitations**: Some complex properties (carousel slides) must be edited in YAML directly.

## Troubleshooting

### Preview Not Updating?
- Check browser console for YAML parse errors
- Ensure `renderYamlStructure()` is called after state changes
- Verify component path map is being rebuilt

### Properties Panel Empty?
- Check that component schema exists in `component_schemas.yaml`
- Verify selection state is set correctly
- Check console for schema resolution errors

### Component Not Rendering?
- Verify default exists in `component_defaults.yaml`
- Check renderer routing in `js/render/index.js`
- Look for HTML escaping issues in text content

### Tests Failing?
- Run `npm test -- --updateSnapshot` if intentional changes to output
- Check that metadata files are synchronized
- Verify test mocks match current component structure

### Accordion Items Not Showing in Properties Panel?
- Check browser console for value resolution logs
- Verify `component.properties.items` exists in YAML
- Ensure items array is not empty or undefined

## Future Enhancements

- 🌳 **Layout Tree UI**: Visual component hierarchy with drag-and-drop
- 🎨 **Theme System**: Global color schemes and typography presets
- 📱 **Responsive Preview**: Multiple device sizes
- 💾 **Cloud Storage**: Save and load projects
- 🔌 **Plugin System**: Extensible component architecture
- 📦 **Build Pipeline**: CSS extraction, asset optimization
- 🌐 **Multi-page Support**: Create complete websites
- ⚡ **Performance Optimization**: Virtual scrolling for large documents

## Contributing

Contributions are welcome! When adding features:

1. **Follow Architecture**: Maintain YAML as single source of truth
2. **Update Tests**: Add/update tests for new functionality
3. **Sync Metadata**: Keep the three YAML files in sync
4. **Update Docs**: Document changes in relevant markdown files
5. **Test Thoroughly**: Run full test suite before committing

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [js-yaml](https://github.com/nodeca/js-yaml) - YAML parser
- [Mini.css](https://minicss.org/) - Base CSS framework
- [Feather Icons](https://feathericons.com/) - Icon set
- [Jest](https://jestjs.io/) - Testing framework

---

**Swift Sites** - Build websites with YAML, preview in real-time, export to HTML.
