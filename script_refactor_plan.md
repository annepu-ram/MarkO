# Script Refactor Planning

## Purpose
- Reduce the cognitive load of `js/script.js` (now ~2k LOC) by extracting cohesive modules.
- Improve maintainability and testability as new components and property editors are added.
- Enable future bundling or lazy-loading strategies without large rewrites.

## Current Pain Points
- **Monolithic file:** Rendering, state, YAML parsing, UI wiring, and component behavior live together, making navigation difficult.
- **Tight coupling:** Functions reach into shared globals (`yamlStructure`, `componentTemplates`, DOM nodes), hindering reuse and unit testing.
- **Limited dependency boundaries:** Adding new component types requires edits in multiple distant sections (templates, rendering switch, property panel) with no clear contracts.
- **Difficult hotfixes:** Small fixes often require parsing unrelated logic due to lack of separation.

## Guiding Principles
- Prefer small ES modules with clear responsibilities and explicit imports/exports.
- Maintain browser compatibility by continuing to ship a single bundle (via a lightweight build step) or a minimal loader that concatenates modules.
- Centralize shared utilities (deep merge, typography tokens, YAML helpers) instead of duplicating logic per feature.
- Keep developer ergonomics high: modules should mirror the mental model (state, parsing, rendering, UI, interactions).

## Proposed Module Map

| Module/Directory | Responsibility | Notes |
| ---------------- | -------------- | ----- |
| `core/state.js` | Owns editor history, selection, template cache, and exposes getters/setters. | Replaces scattered globals with a simple state store. |
| `core/yaml.js` | Wraps YAML parse/generate, structure traversal, update/delete helpers. | Encapsulates `componentIdToPathMap` creation and history pushes. |
| `render/index.js` | Exports `renderYamlStructure` and resolves component renderers. | Replaces the large switch with a registry pattern. |
| `render/components/*` | One file per component family (page, text, media, layout, interactive). | Each module returns preview/export HTML plus init registrations. |
| `properties/index.js` | Drives the properties panel composition and submit flow. | Plugins per component type live under `properties/plugins/`. |
| `ui/events.js` | Sets up DOM event handlers (editor, buttons, preview click, fullscreen). | Keeps `init` lean. |
| `ui/actions.js` | Houses user-triggered commands (insert, delete, apply changes, export). | Consumes state/yaml/render modules. |
| `utils/*` | Shared helpers (deep merge, typography tokens, rem conversion, color handling). | Pure functions, unit-test friendly. |
| `bootstrap.js` | Entry point executed on DOMContentLoaded; wires modules together. | Replaces existing `init` logic. |
| `component_interactions/` | Keeps carousel/titlebar initializers; can be imported on demand. | Allows future per-component enhancement modules. |

## Implementation Phases

1. **Foundation (Phase 0)**
   - Convert `js/script.js` to an ES module (or leave as IIFE) while preserving behavior.
   - Introduce a simple build script (e.g., npm + esbuild/rollup) to bundle modules back into `script.js` for `index.html`.
   - Document coding standards for modules (naming, default exports, dependency graph expectations).

2. **State & Utilities Extraction (Phase 1)**
   - Move shared constants (`TYPOGRAPHY_SIZE_MAP`, etc.) and utilities (`deepMerge`, `toRem`, color helpers) into `utils/`.
   - Extract state management (history, component template cache, selection) into `core/state.js`.
   - Update existing code to import from these modules while keeping everything else in place.

3. **YAML & Data Services (Phase 2)**
   - Create `core/yaml.js` for parsing, serializing, and path-based CRUD.
   - Route `applyYamlComponentProperties`, insert/delete helpers, and undo/redo through this service.
   - Ensure state transitions remain testable via unit tests on the YAML module.

4. **Rendering Pipeline Split (Phase 3)**
   - Introduce `render/index.js` with a registry of component renderers.
   - Move each renderer into `render/components/`. Start with text components to validate the pattern, then migrate layout/media groups.
   - Keep live preview/export parity by sharing core rendering utilities.

5. **Properties Panel Modularization (Phase 4)**
   - Build `properties/index.js` to manage rendering + submission.
   - Port text properties first, using plugin modules that receive component schema + defaults.
   - Remove inline HTML strings in favor of template helpers or lightweight DOM builders.

6. **UI & Actions Cleanup (Phase 5)**
   - Extract event listeners and command handlers into `ui/events.js` and `ui/actions.js`.
   - Ensure actions call into state/yaml/render modules instead of manipulating DOM/state directly.
   - Simplify `bootstrap.js` to: load templates, initialize state, attach listeners.

7. **Polish & Hardening (Phase 6)**
   - Add unit tests for utils, YAML services, state store, and renderer registry.
   - Update documentation (README, GEMINI, AGENTS) to reflect new file layout.
   - Evaluate opportunities for lazy loading interactions (e.g., only load carousel code when needed).

## Tooling Considerations
- Adopt `npm` scripts with `esbuild` or `rollup` for bundling; include a watch mode for local dev.
- Ensure linting/formatting (ESLint + Prettier) are configured across the new module structure.
- Maintain source maps so debugging still references original modules in the browser.

## Risks & Mitigations
- **Regression risk:** Break apart features carefully, validating after each phase with manual QA and regression snippets.
- **Bundle complexity:** Keep the bundler config minimal (single entry, no transpile) to avoid heavy setup overhead.
- **Global reliance:** Some modules may still need access to DOM nodes; introduce dependency injection where possible to limit globals.
- **Team onboarding:** Provide a high-level module map and update AGENTS.md/GEMINI.md to reflect navigation patterns.

## Open Questions
- Should interactions (carousel/titlebar) become separate dynamic imports to reduce initial bundle size?
- Do we want to preserve legacy browsers without module support (if yes, ensure the bundler targets ES2017 and emits an IIFE bundle)?
- Would a TypeScript migration aid maintainability during refactor, or is plain JS preferred for now?

