# Titlebar Font Color Enhancement Plan

## Goal
- expose explicit font color controls for both the titlebar title and its navigation links through YAML/properties
- ensure rendering honours typography schema values while fixing the styling bugs discovered in the titlebar component

## Current Behaviour
- `component_defaults.yaml` and `component_schemas.yaml` omit `typography.title.color` and `typography.menu.color`, so editors cannot set colours even though `generateTitlebarHTML` expects `typography.menu.color`
- the title `<h1>` renders without an inline colour or CSS variable, forcing it to inherit the document colour rather than a titlebar-specific value
- link colour falls back to `inherit` because the schema cannot surface a value and no default CSS variable is emitted

## Existing Bugs
- `js/render/index.js:9-17` returns the generic classes `align-left|center|right`, but `css/components.css:168-176` defines `.titlebar-left|center|right`; alignment classes never apply to the DOM
- `css/components.css:126-131` hard-codes `font-weight: bold` for `.titlebar-title`, ignoring `typography.title.weight` that is already stored in YAML and defaults

## Proposed Changes

### 1. Schema & Defaults
- add `typography.title.color` and `typography.menu.color` to the `titlebar` entry in `component_schemas.yaml` as `color` inputs under the Typography group
- seed matching defaults in `component_defaults.yaml` (e.g. title `#111827`, menu `#333333`) so existing documents gain sensible styling

### 2. Rendering Pipeline
- in `generateTitlebarHTML` (`js/render/index.js`):
  - read the new colour fields and push `--titlebar-title-color` and `--titlebar-link-color` into `styleFragments`
  - resolve `typography.title.weight` with `resolveFontWeight` and expose it via a CSS variable (e.g. `--title-font-weight`) applied to `.titlebar-title`
  - keep `generateTitlebarLinks` focused on emitting markup, but set a CSS custom property on the wrapper instead of repeating inline `color` on every anchor
- update `getAlignmentClass` to return the actual `.titlebar-left|center|right` classes (or append them in addition to the existing ones if other components rely on `align-*`)

### 3. Styling Adjustments
- adjust `.titlebar-title` and `.titlebar-link` in `css/components.css` to use the new CSS variables for colour and weight, preserving current fallbacks
- ensure the scrolled state continues to inherit the same variables, so colours stay consistent while the title shrinks

### 4. Property Panel & Serialization
- no custom renderer changes needed, but verify the typography group now shows colour pickers; confirm `linksEditor` serialization persists the new defaults without wiping the colour fields when editing other properties

## Validation Plan
- create a titlebar in the editor, tweak title and link colours via the properties panel, and confirm the preview updates immediately
- edit YAML directly to change colour values and ensure parsing/re-rendering retains them
- verify exported HTML contains the CSS variables for colours and that hover/focus styling remains intact
- regression-test shrinking behaviour and mobile menu toggle after the alignment-class fix
- confirm legacy documents without the new colour fields still render with fallback colours and no runtime errors

## Risks & Open Questions
- updating CSS classes may impact any other component reusing `getAlignmentClass`; double-check call sites before implementation
- confirm whether inline link styles should remain for backwards compatibility or be replaced entirely by CSS variables during implementation
