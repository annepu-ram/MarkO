# Text Component Simplification & Expansion Plan

## Goals
- Consolidate the current `h1`/`h2`/`h3` components into a single `heading` component with configurable levels and shared typography tokens.
- Simplify the `paragraph` component to emphasize content-first properties and shared typography tokens.
- Introduce a cohesive set of text-centric components so users can compose descriptive copy without managing raw spacing.
- Lay groundwork for grouped property schemas (`typography`, `spacing`, `border`) that align with the broader spacing streamlining effort.

## Current State Snapshot
- `component_defaults.yaml` defines `h1`, `h2`, `h3`, and `paragraph` independently with duplicated typography and spacing props.
- `generateComponentInnerHTML` in `js/render/index.js` maps component names to static HTML tags (e.g., `h1` ? `<h1>`). Any new component requires explicit wiring.
- The properties panel surfaces every primitive property, so headings and paragraphs expose long lists of fields (color, margin, padding, etc.).
- Component buttons in the sidebar mirror the discrete heading types, leading to repeated defaults and extra YAML churn.

## Proposed Component Model
### Unified `heading`
- **Properties**
  - `level` (1–6) – drives the rendered tag and baseline typography token.
  - Font size is derived from the heading level (1 -> `xxxl`, 2 -> `xxl`, 3 -> `xl`, 4 -> `lg`, 5 -> `md`, 6 -> `sm`).
  - `text` – primary content.
  - `typography` group: { size, weight, transform, letterSpacing, align, color } with token-friendly defaults.
  - `spacing` group: optional margins (top/bottom) while padding is handled by layout containers.
- **Runtime**
  - `renderSimpleComponent` in `js/render/index.js` routes the component through a generator that constructs the correct `<hN>` tag based on `level`.
  - `generateRemainingStyles` in `js/render/index.js` evolves to read grouped props (typography tokens first, fallback to numeric overrides).
- **Editor UX**
  - Sidebar exposes a single "Heading" button that inserts `heading` with `level: 2` by default plus quick actions to cycle the level.
  - Properties panel shows compact controls: level selector, typography group, spacing group.

### Streamlined `paragraph`
- **Properties**
  - `text`.
  - `variant` options: `body`, `lead`, `muted`, `note` to swap typography tokens.
  - `typography` group: `{ size, lineHeight, color, align, weight }`.
  - `spacing` group: margin tokens only.
- **Rendering**
  - Generate `<p>` element with resolved typography tokens and optional inline overrides in `js/render/index.js`.

### Additional Text Components to Add
| Component  | Purpose                            | Variants / Notes                          |
|------------|------------------------------------|-------------------------------------------|
| `eyebrow`  | Small uppercase label above headings | Variants: `default`, `accent`; uppercase + letter spacing tokens |
| `lead`     | Intro paragraph for hero sections   | Essentially a paragraph variant but standalone button for discoverability |
| `caption`  | Supplemental text under media       | Supports `align`, `muted` variant, optional icon |
| `blockquote` | Highlighted quotation with citation | Properties: `quote`, `cite`, `variant` (`pull`, `card`) |
| `list`     | Ordered/ unordered textual lists    | Properties: `type` (`ol`/`ul`), `items`, optional `icon` token |
| `codeblock`| Preformatted text for snippets      | Properties: `content`, `language`, `wrap` toggle |

These components extend the content palette while leaning on shared typography tokens, reducing the need for manual spacing.

## Implementation Workstream
1. **Schema & Defaults**
   - Remove `h1`, `h2`, `h3` blocks from `component_defaults.yaml`; add unified `heading` with grouped props.
   - Refactor `paragraph` defaults to use grouped props and remove padding/margin where layout containers take over.
   - Define defaults for each new text component with minimal, token-driven properties.

2. **Rendering Logic**
   - Update `generateComponentInnerHTML` in `js/render/index.js` to:
     - Handle `heading` by reading `properties.level`.
     - Move paragraph logic to respect variants and grouped props.
     - Add cases for new components (`eyebrow`, `caption`, etc.).
   - Enhance `generateRemainingStyles` in `js/render/index.js` to flatten grouped typography/spacing props into inline styles until token classes exist.

3. **Properties Panel**
   - Extend `renderPropertiesPanel` in `js/properties/index.js` to detect nested groups (`typography`, `spacing`) and render collapsible sections.
   - Provide friendly controls for `level`, alignment, and text content.
   - Ensure new components have tailored panels (e.g., list editor for `list.items`).

4. **Component Insertion & Templates**
   - Update sidebar configuration to offer buttons for `heading`, `paragraph`, and curated text components.
   - Adjust example YAML (if any) and onboarding snippets to use the new components.

5. **Styling Support**
   - Add supporting styles in `css/components.css` for text variants (e.g., `.text-muted`).
   - Coordinate with upcoming layout primitives so typography spacing relies on container tokens instead of per-component padding.

6. **Testing & Validation**
   - Snapshot tests (YAML ? HTML) covering each variant to ensure consistent output.
   - Manual QA in the builder: insert headings, change levels, export HTML to verify semantic tags.