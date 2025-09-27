# Script Refactor Plan

## Purpose
- This document outlines the modular architecture of the JavaScript code, which was refactored from a single `js/script.js` file to improve maintainability and testability.

## Guiding Principles
- The code is organized into small ES modules with clear responsibilities and explicit imports/exports.
- Shared utilities are centralized in the `js/utils` directory.
- The module structure mirrors the mental model of the application (state, parsing, rendering, UI, interactions).

## Current Module Map

| Module/Directory | Responsibility | Notes |
| ---------------- | -------------- | ----- |
| `core/state.js` | Owns editor history, selection, template cache, and exposes getters/setters. | Replaces scattered globals with a simple state store. |
| `core/yaml.js` | Wraps YAML parse/generate, structure traversal, update/delete helpers. | Encapsulates `componentPathMap` creation and history pushes. |
| `core/app.js` | Initializes the application. |
| `core/templates.js` | Loads component templates, schemas, and tokens. |
| `render/index.js` | Exports `renderYamlStructure` and resolves component renderers. | Replaces a large switch statement with a more modular approach. |
| `properties/index.js` | Drives the properties panel composition and submit flow. |
| `properties/customRenderers.js` | Provides custom UI for editing complex properties. |
| `ui/events.js` | Sets up DOM event handlers (editor, buttons, preview click, fullscreen). |
| `ui/actions.js` | Houses user-triggered commands (insert, delete, apply changes, export). | Consumes state/yaml/render modules. |
| `utils/*` | Shared helpers (deep merge, typography tokens, rem conversion, color handling). | Pure functions, unit-test friendly. |
| `script.js` | Entry point executed on DOMContentLoaded; wires modules together. |
| `component_interactions.js` | Keeps carousel/titlebar initializers; can be imported on demand. |