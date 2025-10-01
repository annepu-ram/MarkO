# Text Components Multiline Rendering Plan

## Objective
Ensure any multiline 	ext property captured via the editor persists in YAML and renders with visible line breaks (convert \n to <br> equivalents) without regressing existing text component behaviour, YAML serialization, or property editing flows.

## Current Behaviour Snapshot
- Textual components (e.g., heading, paragraph, eyebrow, caption, blockquote) route through generateComponentInnerHTML (js/render/index.js), which currently calls escapeHtml and injects the result directly into HTML, dropping newline intent.
- YAML roundtrip (parseYamlContent / generateYamlFromStructure in js/core/yaml.js) preserves literal \n characters inside strings, but rendering ignores them.
- Property edit flow (
enderPropertiesPanel / applyPropertiesForComponent in js/properties/index.js) stores blank text as a single space to keep keys present. Multiline entries are stored as raw \n characters but preview flattening hides them.
- insertComponent scaffolds defaults that contain single-line text, so no multiline defaults exist today.

## Hurdles & Considerations
1. **Safe HTML with Line Breaks**: escapeHtml already neutralizes HTML; introducing <br> conversion must keep XSS protections intact. Need a helper that escapes first, then replaces \n with <br> without double-encoding.
2. **Component Coverage**: All text-bearing components share generateComponentInnerHTML; ensure the transformation applies only where appropriate (avoid affecting attributes, blockquote citation, etc.).
3. **Blank Text Normalization**: Current applyPropertiesForComponent converts empty text inputs to ' ' (js/properties/index.js:197). Must confirm this logic coexists with multiline updates (e.g., avoid trimming trailing newlines to blank, keep intentional empty lines).
4. **YAML Serialization Format**: jsyaml.dump may emit block scalars (|) for multiline strings. Need to confirm downstream consumers (history, undo/redo, export) tolerate the format and ensure diff-friendly output.
5. **Preview vs Export Parity**: Rendering path diverges for preview/export. Both must inject <br> tags consistently; ensure export HTML (used in downloads/fullscreen) receives identical processing.
6. **Property Editor UX**: Multiline text is edited via <textarea> controls. Confirm 
renderPropertiesPanel keeps newline characters intact when loading defaults + instance overrides, and that re-render does not collapse them.
7. **Testing & Coverage**: Must extend unit tests (likely in js/render/__tests__/index.test.js and add new ones for the helper) to assert newline conversions, plus integration tests covering applyPropertiesForComponent roundtrip to YAML.
8. **Interplay with insertComponent / Templates**: Verify inserting components with multiline text via example templates or future variants doesn�t regress. May need fixture updates.
9. **Historic Compatibility**: Legacy YAML files lacking <br> conversion should continue to render (single-line behaviour should remain unchanged when no newline present).

## Implementation Plan
1. **Helper Introduction**: Create a utility (e.g., escapeHtmlWithBreaks) in js/utils/strings.js that wraps escapeHtml then swaps \n for <br> (consider double newline -> <br><br> semantics). Add targeted unit tests.
2. **Renderer Update**: In js/render/index.js, replace direct escapeHtml usage for textual nodes with the new helper. Ensure blockquote citation/text follow same rule while preserving existing markup.
3. **Property Handling Audit**:
   - Confirm text areas feed newline characters into component props; adjust blank-normalization logic to avoid stripping intentional newlines (possibly only coerce truly empty strings post-trim).
   - Validate insertComponent path writes multiline default values unchanged.
4. **YAML Verification**: Manually and via automated tests, ensure generateYamlFromStructure outputs expected multiline YAML (add regression test covering parse -> dump -> parse roundtrip with multiline 	ext).
5. **Preview/Export Sync**: Confirm <br> conversion applies in both preview and export rendering modes. Update export-related tests if necessary.
6. **Testing Strategy**:
   - Extend js/render/__tests__/index.test.js to cover newline rendering for paragraph/heading.
   - Add property roundtrip test in js/properties/__tests__/applyProperties.test.js to ensure multiline values survive apply -> YAML -> parse.
   - Run full 
pm test ensuring coverage stability.
7. **Regression Pass**: After implementation, manually verify:
   - Editing text with newlines in the sidebar reflects in preview/export.
   - Undo/redo retains multiline content.
   - Example templates render as before (no unintended <br> when single-line).

## Risk Mitigation
- Keep the conversion logic isolated so non-text content isn�t affected.
- Gate behaviour behind newline detection to avoid extra <br> injection for plain strings.
- Maintain existing space-for-empty safeguard but revisit if it conflicts with intentional blank lines (documented fallback).
- Ensure tests cover both presence and absence of newline characters.

## Next Steps
- Validate feasibility by prototyping the helper and running serialization tests.
- Sequence work: helper + tests ? renderer adjustments ? property/YAML audits ? regression testing.
- Coordinate with future text component enhancements to avoid overlapping changes.
