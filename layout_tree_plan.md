# Layout Hierarchy Tree Plan

## Objective
- Replace direct YAML editing with a visual hierarchy tree that represents the page/component structure.
- Preserve the YAML document as the single source of truth feeding rendering, export, and properties flows.
- Provide intuitive controls to add, reorder, and remove components without exposing indentation-sensitive YAML.

## Success Criteria
- Users can build a page by interacting solely with the hierarchy tree and preview.
- Every tree operation updates the underlying YAML structure, triggers re-render, and keeps properties/state in sync.
- Existing rendering, export, history, and properties editing remain fully functional.
- Solution is accessible, performant for large trees, and test-covered.

## Current Workflow Snapshot
- `textarea#editor` holds YAML; debounced `input` events call `actions.handleEditorInput` -> `parseAndRender`.
- `parseAndRender` uses `parseYamlContent` (jsyaml) -> `renderYamlStructure`; preview selection maps via `componentPathMap`.
- Component insertion (`insertComponent`) mutates parsed YAML, regenerates YAML string, writes it back to editor.
- History/undo/redo store serialized YAML text (state.history).
- Properties panel edits call `applySelectedComponentProperties`, which clones structure, applies differences, regenerates YAML.

## Guiding Principles & Constraints
- YAML remains canonical; tree manipulations must operate on parsed structure and regenerate YAML through `generateYamlFromStructure`.
- The YAML editor stays in read-only mode for end users: tree actions clone the current editor text, enforce a `page` root, update the central YAML structure map.
- Keep `componentPathMap` and selection model intact so properties panel and preview highlighting continue to work.
- Avoid regressions in export/fullscreen flows that rely on `editor.value` (keep the read-only editor in the DOM or provide an equivalent state-driven accessor).
- Maintain undo/redo fidelity; tree actions must push serialized snapshots just as editor edits did.
- Treat the hierarchy tree as a GUI overlay on top of the read-only editor; all source-of-truth operations continue to flow through the YAML text.
- Progressive delivery: support toggling back to YAML editor for debugging until new workflow is hardened.

## Proposed Architecture
### Data Flow
1. Centralize YAML string + parsed structure in state (`state.yamlStructure` + new `state.yamlText`) by cloning the sanitized editor text and ensuring the top-level `page` component exists before persisting.
2. Expose helper actions to mutate structure (insert, reorder, delete, wrap/unwrap) that:
   - clone current structure,
   - apply change using path utilities from `js/core/yaml.js`,
   - regenerate YAML (`generateYamlFromStructure`),
   - write the refreshed YAML back into the read-only textarea (`editor.value`) before any rendering,
   - update state (`setYamlStructure`, new `setYamlText`),
   - invoke `parseAndRender` so preview, tree, and path maps follow the editor,
   - refresh selection and push history.
3. Keep the read-only textarea synchronized for governance and downstream automation (export/fullscreen, MCP server, LLM agents); longer-term, refactor those flows to consume state instead of DOM queries while retaining the textarea as the authoritative text surface.
4. Route structure and text updates through existing helpers (`parseAndRender`, `applySelectedComponentProperties`, `generateYamlFromStructure`) so new tree actions blend seamlessly with legacy YAML workflows.

This keeps the hierarchy tree as a GUI over the editor: tree interactions mutate the YAML text first, and the preview follows by re-parsing that canonical source.

### Tree Model
- Build a normalized representation of components: nodes with `id`, `label`, `path`, `component`, `children` (for `components`, `columns`, `tabs`, etc.), excluding non-component nodes such as `properties`.
- Generate nodes from `state.yamlStructure` using existing render traversal logic as reference (e.g., share `renderComponentsList` path mapping rules to ensure parity).
- Persist expanded/collapsed state per node (local state/UI only).

### UI Layer
- Replace the YAML editor pane and legacy component sidebar with:
  - Tree view component (virtual DOM or template-driven HTML) supporting keyboard navigation, context menus, and drag handles.
  - Action affordances: add child, duplicate, delete, move up/down, drag-and-drop reorder.
  - Context-specific insertion menus (respect `childComponentContainers` definitions and schema-specified slots like `columns`, `tabs`, `slides`).
  - Node-level "Add component" controls open grouped menus that list component groups with nested component options for direct insertion.
- Provide optional toggle/backdoor to show raw YAML (developer mode) until stable (feature flag or localStorage preference).

### Interaction Hooks
- Selecting a node sets selection via `setSelection` & highlights preview (reuse `refreshSelection`).
- Adding component from tree invokes new `insertComponentAtPath(path, index, componentName)` helper (reusing template cloning logic).
- Reordering uses drag-and-drop: compute source/target paths, adjust arrays accordingly, regenerate YAML.
- Deleting uses existing `deleteComponentByPath` helper.
- Duplicating clones component JSON (deepClone) and inserts at adjacent index.
- Support moving nodes between compatible containers only (validate based on schema's allowed child types or predetermined rules).

### Properties Integration
- When selection changes via tree, keep properties panel behavior identical (pass component + path to `renderPropertiesPanel`).
- Applying property changes should update tree labels (e.g., show component titles) immediately after YAML regeneration.

### Undo/Redo Strategy
- Wrap every tree mutation in a shared `commitStructureChange({ structure, description })` helper that:
  - Calls `generateYamlFromStructure`.
  - Updates the read-only textarea value (for governance and external integrations).
  - Pushes to history stack (existing `pushHistory`).
  - Renders preview & tree (using central render function to avoid double work).
- Ensure undo/redo also re-sync tree (listen to `undoAction`/`redoAction` to trigger tree rebuild after `parseAndRender`).

### Rendering Safeguards
- Tree should consume the same parsed structure that feeds renderer; avoid bespoke parsing to prevent divergence.
- Keep existing preview markup wrappers intact; tree changes only influence order/content of `structure` arrays.
- Validate that operations preserve `componentPathMap` integrity.

## Implementation Phases
1. **State groundwork**
   - Introduce `state.yamlText`, `setYamlText`, `getYamlText`.
   - Refactor `parseAndRender`/`applySelectedComponentProperties`/`insertComponent` to use central `commitStructureChange` helper.
   - Flip the editor textarea to read-only for users while keeping it programmatically synchronized and visible as the canonical YAML view.
   - Ensure the commit helper reuses existing YAML update functions (`parseAndRender`, `applySelectedComponentProperties`) so tree-driven mutations and legacy flows remain aligned.
2. **Tree data utilities**
   - Implement `buildHierarchyTree(structure)` in new module (e.g., `js/ui/tree.js`).
   - Define node types for special containers (columns, tabs, slides, accordion content).
3. **Tree UI skeleton**
   - Create tree rendering template (vanilla DOM, lit, or simple HTML builder) within sidebar panel.
   - Support selection + expand/collapse, read-only view first.
4. **Mutation actions**
   - Wire add/delete/reorder/duplicate actions through tree controls into state helpers.
   - Implement drag-and-drop reordering (mouse + keyboard alternatives).
5. **YAML editor deprecation**
   - Hide textarea by default; provide optional toggle.
   - Redirect insert buttons to tree (remove dependency on cursor position).
   - Retire the legacy components section in favor of the hierarchy tree workspace and grouped insertion menus.
6. **QA & polish**
   - Accessibility (ARIA tree role, keyboard navigation).
   - Performance profiling on large structures.
   - Update documentation/help panel.

## Testing & Validation
- Unit tests for new state helpers (insert/reorder) using sample structures.
- Integration tests covering tree operations triggering preview updates (jsdom or DOM-based tests).
- Regression tests for export/fullscreen ensuring outputs unchanged.
- Manual QA checklist: add nested components, reorder across levels, undo/redo, properties edits, delete root child.
- End-to-end smoke tests (if Cypress or similar available) for typical flows.

## Risks & Mitigations
- **Desynchronization between tree and YAML**: centralize mutations in one helper; rebuild tree from state after each commit.
- **Breaking history/undo**: ensure history entries mirror pre-existing behavior by pushing serialized YAML for every change.
- **Complex container rules**: leverage schemas (`component_schemas.yaml`) to validate allowed child insertions.
- **Performance on big documents**: lazy render tree nodes, memoize label generation, or virtualize list if needed.
- **User learning curve**: provide onboarding tooltip, allow optional YAML view until stable.

## Open Questions / Follow-ups
- Do we keep free-form YAML editing as an advanced toggle for power users?
- QA should verify the tree excludes non-component nodes (e.g., `properties`) while advanced edits remain available via YAML.
- Drag-and-drop library vs. custom implementation - evaluate dependencies/policy (no external libs preferred?).
- Need for diff highlighting when committing changes (future enhancement).

## Rollout Strategy
- Stage behind feature flag/localStorage toggle for internal testing.
- Ship with updated docs and help panel section describing tree usage.
- Collect feedback, then remove YAML editor entirely once parity is confirmed.



















