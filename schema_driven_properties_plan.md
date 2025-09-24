# Schema-Driven Property Panel Plan

## Goal
Let YAML (component defaults + metadata) describe the property UI so JavaScript only interprets the schema and renders inputs. This reduces hard-coded HTML in `renderTextComponentProperties` and makes it easy to add new components without touching JS.

## Current Gaps
- Property panel logic is handwritten per component (e.g., large `renderTextComponentProperties` function).
- Input types (text, select, color) are inferred in JS via ad hoc lists.
- Complex editors (links, carousel slides) are embedded in JS functions.
- No unified schema to describe field order, grouping, validation, or conditional logic.

## Proposed Architecture
### 1. Property Schema Definition
- Extend `component_defaults.yaml` (or a new `component_schemas.yaml`) with a `ui` section per component.
```yaml
heading:
  defaults:
    text: Section Heading
    typography:
      size: xl
      weight: bold
  ui:
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
- On init, load both `component_defaults.yaml` and `component_schemas.yaml`.
- Merge defaults with schema to build a `componentMeta` map (`name -> { defaults, ui }`).
- Create a `renderPropertiesFromSchema(componentName, resolvedProps)` function that:
  - Looks up the schema.
  - Iterates groups/fields to build markup.
  - For each field, uses a registry of `renderField[type]` functions to output HTML.
  - Adds data attributes (`data-path`, `data-type`) so save logic can walk inputs generically.

### 3. Generic Input Handlers
- Replace `renderProperty`, `renderTextComponentProperties`, etc. with type-driven helpers:
  - `renderTextField(fieldConfig, value)`
  - `renderSelectField(fieldConfig, value, tokens)`
  - `renderColorField(fieldConfig, value)`
- All inputs carry `data-field-path` and optional metadata (e.g., `data-list-token`).

### 4. Apply Changes Pipeline
- Update `applyYamlComponentProperties` to read all `[data-field-path]` elements.
- Use helper `setValueByPath()`/`deleteValueByPath()` based on field type and empty-state rules defined in schema (e.g., `clearWhenEmpty: true`).
- Support complex fields via `field.type = 'repeatable'` with nested definitions (e.g., arrays of links). JS loops through repeated groups using schema instructions.

### 5. Custom/Advanced Editors
- For components needing bespoke UIs (carousel, links), allow `type: custom` with a `renderer` key.
- JS checks `customRenderers[rendererId]` to delegate.
- Keep only a handful of custom renderers; most fields should be schema-driven.

### 6. Validation & Help
- Schema can include validation hints (`required`, `pattern`, `min`, `max`).
- Add optional tooltips/help text via `description` entries.

### 7. Migration Steps
1. **Schema groundwork**
   - Create `component_schemas.yaml` with entries for text components.
   - Introduce loader to read schemas + tokens and attach to global metadata.
2. **Generic renderer**
   - Implement `renderPropertiesFromSchema` using a field renderer registry.
   - Hook it into `renderPropertiesPanel` when component schemas exist.
3. **Saving logic refactor**
   - Convert `applyYamlComponentProperties` to iterate `data-field-path` inputs.
   - Remove component-specific property parsing once generic flow handles them.
4. **Incremental component migration**
   - Move heading/paragraph/blockquote to schema control.
   - Then forms, media, layout components.
   - For each migration, remove the old hard-coded logic.
5. **Deprecate legacy code**
   - Delete `renderTextComponentProperties`, `renderProperty`, etc., once all components use the schema pipeline.
6. **Docs & testing**
   - Update AGENTS.md/GEMINI.md to describe the schema system.
   - Add tests verifying schema-driven render + save produce expected YAML.

## Supporting Files
- `component_defaults.yaml`: continues to hold default property values and sample content.
- `component_schemas.yaml`: describes the property UI (groups, fields, conditions) per component.
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
          - path: level
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
- `schema_tokens.yaml`: central catalog of reusable option lists.
  ```yaml
  typographySizes:
    type: selectOptions
    options:
      - value: xxs
        label: "XXS"
      - value: xs
        label: "XS"
      - value: sm
        label: "SM"
      - value: md
        label: "MD"
      - value: lg
        label: "LG"
      - value: xl
        label: "XL"
      - value: xxl
        label: "XXL"
  spacingScale:
    type: selectOptions
    options:
      - value: none
        label: "None"
      - value: xs
        label: "XS"
      - value: sm
        label: "SM"
      - value: md
        label: "MD"
      - value: lg
        label: "LG"
      - value: xl
        label: "XL"
  ```
- `schema_custom_renderers.js`: exports helpers for fields marked with `type: custom` (e.g., carousel slide editors).

### Schema Structure Guidelines
- Component schema entries define ordered `groups` for sections.
- Each field supports:
  - `path`: dotted path into component properties.
  - `type`: `text`, `textarea`, `select`, `color`, `checkbox`, `repeatable`, `custom`, etc.
  - `label`, `placeholder`, `rows`, `min`, `max`, `step`: render hints.
  - `tokens`: link to a token list in `schema_tokens.yaml`.
  - `options`: inline option definitions when tokens aren’t used.
  - `clearWhenEmpty`, `defaultValue`, `help`, `condition`: behavior and UX metadata.
- Groups can define `description`, `collapsedByDefault`, `inline`, or layout hints.

### Loader Responsibilities
- Load `component_schemas.yaml` and `schema_tokens.yaml` alongside component defaults.
- Validate schema integrity (unknown field types, missing tokens) and log warnings.
- Expose helpers:
  - `getComponentSchema(name)`
  - `getTokenOptions(tokenName)`
  - `renderField(fieldConfig, value)`
- Allow overrides/merging so plugins can augment schemas if needed.
## Pros
- **Consistency:** One schema format governs all components, preventing property panel drift.
- **Extensibility:** Adding a new component or field means editing YAML, not JavaScript.
- **Separation of concerns:** UI structure lives alongside defaults, improving discoverability.
- **Testability:** The renderer becomes a small interpreter that’s easier to unit test.
- **Localization-friendly:** Schema can hold labels/help text for future i18n efforts.

## Cons
- **Initial complexity:** Requires building the schema loader plus generic render/save pipeline before benefits appear.
- **Schema verbosity:** Complex components may have long YAML definitions unless broken into shared fragments.
- **Runtime overhead:** Rendering from schema could be slower if not cached or optimized.
- **Learning curve:** Contributors must understand the schema format and available field types.
- **Edge cases:** Highly bespoke editors (e.g., carousel slide builder) still need custom renderers, slightly reducing purity.



