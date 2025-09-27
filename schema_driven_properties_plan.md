# Schema-Driven Property Panel Plan

## Goal
Let YAML (component defaults + metadata) describe the property UI so JavaScript only interprets the schema and renders inputs. This reduces hard-coded HTML and makes it easy to add new components without touching JS.

## Current Gaps
- Property panel logic is handwritten per component.
- Input types (text, select, color) are inferred in JS via ad hoc lists.
- Complex editors (links, carousel slides) are embedded in JS functions.
- No unified schema to describe field order, grouping, validation, or conditional logic.

## Proposed Architecture
### 1. Property Schema Definition
- A `component_schemas.yaml` file will define the UI for the properties panel for each component.
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
    - id: typography
      label: Typography
      fields:
        - path: typography.level
          type: select
          label: Level
          options: [1,2,3,4,5,6]
        - path: typography.size
          type: select
          label: Font Size
          tokens: typographySizes
        - path: typography.color
          type: color
          label: Text Color
```
- `path` uses dot-notation to reach nested values; JS uses this to bind inputs.
- `type` maps to generic renderers (`text`, `textarea`, `select`, `multi`, `color`, `toggle`, custom).
- `tokens` reference shared option lists defined in a new `schema_tokens.yaml` (e.g., typography sizes, spacing scale).

### 2. JavaScript Schema Loader
- On init, `js/core/templates.js` will load `component_defaults.yaml`, `component_schemas.yaml`, and `schema_tokens.yaml`.
- `js/properties/index.js` will have a `renderPropertiesPanel` function that:
  - Looks up the schema.
  - Iterates groups/fields to build markup.
  - For each field, uses a registry of `renderField[type]` functions to output HTML.
  - Adds data attributes (`data-path`, `data-type`) so save logic can walk inputs generically.

### 3. Generic Input Handlers
- `js/properties/index.js` will contain type-driven helpers:
  - `renderTextInput(fieldConfig, value)`
  - `renderSelect(fieldConfig, value, tokens)`
  - `renderColorInput(fieldConfig, value)`
- All inputs carry `data-field-path` and optional metadata.

### 4. Apply Changes Pipeline
- `applyPropertiesForComponent` in `js/properties/index.js` will read all `[data-field-path]` elements.
- Use helper `setNestedValue()`/`deleteNestedValue()` based on field type and empty-state rules defined in schema.

### 5. Custom/Advanced Editors
- For components needing bespoke UIs (carousel, links), allow `type: custom` with a `renderer` key in `component_schemas.yaml`.
- `js/properties/index.js` checks `customRenderers[rendererId]` (from `js/properties/customRenderers.js`) to delegate.

### 6. Migration Steps
1. **Schema groundwork**
   - Create `component_schemas.yaml` and `schema_tokens.yaml`.
   - Update `js/core/templates.js` to load these files.
2. **Generic renderer**
   - Implement `renderPropertiesPanel` in `js/properties/index.js` using a field renderer registry.
3. **Saving logic refactor**
   - Convert `applyPropertiesForComponent` in `js/properties/index.js` to iterate `data-field-path` inputs.
4. **Incremental component migration**
   - Move components to schema control one by one.
5. **Docs & testing**
   - Update AGENTS.md/GEMINI.md to describe the schema system.
   - Add tests verifying schema-driven render + save produce expected YAML.

## Supporting Files
- `component_defaults.yaml`: continues to hold default property values and sample content.
- `component_schemas.yaml`: describes the property UI (groups, fields, conditions) per component.
- `schema_tokens.yaml`: central catalog of reusable option lists.
- `js/properties/customRenderers.js`: exports helpers for fields marked with `type: custom`.

## Pros
- **Consistency:** One schema format governs all components, preventing property panel drift.
- **Extensibility:** Adding a new component or field means editing YAML, not JavaScript.
- **Separation of concerns:** UI structure lives alongside defaults, improving discoverability.
- **Testability:** The renderer becomes a small interpreter that’s easier to unit test.

## Cons
- **Initial complexity:** Requires building the schema loader plus generic render/save pipeline before benefits appear.
- **Schema verbosity:** Complex components may have long YAML definitions.
- **Runtime overhead:** Rendering from schema could be slower if not cached or optimized.