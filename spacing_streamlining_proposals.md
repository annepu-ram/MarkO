# Component Spacing Streamlining Proposals

## 1. Dedicated Spacing Container
The core idea is to shift spacing and background concerns into wrapper components so that text and media nodes stay focused on content. A new `section` (or `layout`/`block`) component would:
- Own layout-related props such as `padding`, `margin`, `backgroundColor`, `backgroundImage`, `maxWidth`, `minHeight`, `align` (horizontal alignment), and optional `gap` for child spacing.
- Support a `variant` field to capture common presets (e.g. `hero`, `card`, `banner`) that preconfigure spacing and background tokens. This gives non-designers a quick starting point without touching raw numbers.
- Render as a semantic container (`section`, `div`, `main`) decided by a `tag` property or inferred from context. The renderer would treat it similarly to `page` by applying inline styles via `generateRemainingStyles` while leaving child components untouched.

Implementation details:
1. **Defaults**: Add the container definition to `component_defaults.yaml` with sensible starting values (`padding: 40`, `margin: 0 auto`, `maxWidth: 1200`). Remove `padding`/`margin` from most other component defaults so they inherit spacing from the container.
2. **Rendering**: Update `renderComponent` in `js/render/index.js` to route `section` to a new `renderSectionComponent` helper that wraps `renderComponentsList` output and applies spacing styles. Reuse the existing editor chrome so the container can be selected to edit layout.
3. **Insertion Workflow**: When users drop text, media, or form elements directly onto the page, automatically nest them inside a `section` scaffold (unless they explicitly target another container). The sidebar could expose both "Section" and "Component" tabs so advanced users can compose their own layout.
4. **Properties Panel**: Provide a dedicated layout editor UI block (padding sliders, background picker, alignment toggles) in `js/properties/index.js`.

## 2. Property Grouping & Tokens
- Reshape YAML to nest related styling under buckets (e.g. `spacing: { padding, margin }`, `border: { width, style, color, radius }`, `typography: { size, weight, style, color, lineHeight }`). This keeps YAML readable when multiple style knobs are set.
- Update `renderPropertiesPanel` in `js/properties/index.js` to detect grouped objects and render expandable sections, using friendly labels ("Spacing", "Border", "Typography") rather than a long flat form.
- Introduce optional design tokens for common sizing and color presets. For example, `padding: md` or `typography.size: h2`. `generateRemainingStyles` in `js/render/index.js` translates tokens to rem or hex values. Users who want custom numbers can still provide explicit values.

Example: grouped properties for a heading component
```yaml
- name: heading
  properties:
    level: 2
    content: "Our Mission"
    typography:
      size: xl
      weight: bold
      align: center
    spacing:
      margin: { top: 32, bottom: 24 }
    border:
      width: 0
      radius: 0
```
In the properties panel this becomes collapsible sections ("Typography", "Spacing") with token pickers and numeric overrides.

## 3. Heading Consolidation
- The `h1`, `h2`, `h3` components have been replaced with a single `heading` component that exposes a `level` property (`1-6`).
- Defaults supply level-specific typography presets, while the properties panel shows a level selector and optional overrides (size, weight, alignment). The renderer outputs the correct `<h1>`...`<h6>` tag at runtime.

## 4. Layout Primitives & Variants
Introduce three layout primitives that own spacing, background, and structural configuration. Each exposes a shared `variant` property that selects a preset bundle of spacing tokens, background styles, and responsive behavior. Users can still override individual values after selecting a variant.

### Section
- **Role:** Broad content wrapper for large page areas.
- **Variants:**
  - `hero`: generous vertical padding, full-width background image, centered alignment.
  - `card`: constrained `maxWidth`, subtle drop shadow, medium padding.
  - `banner`: narrow height, horizontal layout for CTAs, accent background color.
- **Overrides:** Users can adjust `backgroundColor`, `padding`, `maxWidth`, `align`, `gap`, and `tag`. When no variant is chosen, defaults mirror today’s page-level behavior.

### Stack
- **Role:** Vertical flow that evenly spaces children.
- **Variants:**
  - `default`: moderate `gap`, left alignment.
  - `centered`: same gap, but center-aligned and width-constrained.
  - `timeline`: larger `gap`, decorative border/line for storytelling layouts.
- **Overrides:** `gap`, `align`, `responsive.direction` (switch to horizontal on large screens), optional `divider` styling between items.

### Grid
- **Role:** Multi-column layout with automatic child placement.
- **Variants:**
  - `two-column`: equal columns, moderate `gap`.
  - `sidebar-left`: narrow left column (`1fr 2fr`), used for navigation/content.
  - `gallery`: fluid columns using `minmax` and auto-fit behavior, tighter gaps.
- **Overrides:** `columns` definition, `gap`, breakpoint-specific templates, and optional `rowGap` vs `columnGap` controls.

### Variant Handling
- **Definition:** `component_defaults.yaml` lists a `variants` map under each primitive. Selecting a variant merges the preset property bundle into the component before rendering.
- **Properties Panel:** Shows a variant dropdown with preview thumbnails or short descriptions in `js/properties/index.js`. Changing the variant re-applies its base tokens while preserving user overrides unless the user opts to reset.
- **Renderer:** When rendering, `js/render/index.js` will resolve the variant first, then apply user-defined overrides, and finally run through `generateRemainingStyles`. This ensures variants remain a starting point rather than a lock-in.
- **YAML Output:** Store the chosen variant (`variant: hero`) alongside any overrides the user makes. This keeps documents brief while still allowing fine-tuning.

### Columns Grid Alignment
The existing `columnsgrid` component can evolve into the new `grid` primitive instead of coexisting as a separate construct. Suggested path:
- **Rename & Expand:** Rebrand `columnsgrid` to `grid`, bringing over current behavior while broadening configuration (explicit column templates, responsive breakpoints, shared variants).
- **YAML Compatibility:** Update defaults and insertion buttons to reference `grid`; adjust rendering helpers in `js/render/index.js` to read the new `properties.columns` schema.
- **Feature Parity:** Preserve conveniences such as per-column component lists while adding optional layout primitives like `stack` inside each column for consistent spacing.
- **User Experience:** Present a single, powerful grid component so users aren’t left choosing between similar options. Documentation can highlight simple two-column usage alongside more advanced layouts powered by variants.

These layout primitives let creators think in terms of sections, stacks, and grids rather than micro-managing spacing on every component, while the variant system gives quick access to best-practice presets.