# Rendering Architecture Options

## Context
The builder currently renders YAML to HTML entirely in the browser. Upcoming work includes integrating a Python-based LLM service to mutate YAML structures and assist users. This document compares keeping all rendering in JavaScript vs. moving rendering to a backend service.

## Option 1: Client-Side Rendering (Status Quo)
- **How it works:** The browser parses YAML, generates DOM/HTML, and updates the preview instantly. Exporting HTML reuses the same render pipeline.
- **Pros**
  - Zero round-trips for preview updates; ideal for an interactive editor.
  - Users can work offline once assets are cached.
  - No scaling burden on a render backend; server cost stays with LLM endpoints only.
  - One rendering implementation to maintain (client), avoiding divergence.
- **Cons**
  - LLM integration must send YAML back to the client for preview updates.
  - Harder to reuse rendering for server-driven outputs (e.g., emails, PDFs) without Node bundling.

## Option 2: Server-Side Rendering (Python Backend)
- **How it works:** YAML is sent to a Python service, rendered to HTML, and returned to the client.
- **Pros**
  - Single source of truth on the backend; LLM edits and preview use identical rendering code.
  - Easier to generate server-side artifacts (PDF/email snapshots) without shipping front-end code.
- **Cons**
  - Adds latency and infrastructure requirements for every preview update.
  - Requires careful sync between live editing and backend calls; optimistic UI becomes complex.
  - Python renderer would need duplication of current rendering logic or a shared cross-language implementation.
  - Server scaling becomes tied to every live editing session.

## Option 3: Hybrid Server Rendering with HTMX
- **How it works:** The browser uses HTMX to fetch partial HTML snippets from a Python backend that renders components server-side. YAML edits (from the user or LLM) are sent via HTMX requests, and the server responds with updated component markup to swap into the DOM.
- **Pros**
  - Keeps the rendering source of truth on the backend while still offering snappy partial updates.
  - HTMX simplifies client code: minimal JavaScript, declarative `hx-get`/`hx-post` attributes handle DOM swaps.
  - Easier to audit/validate changes on the server before they hit the UI.
- **Cons**
  - Requires a Python render implementation duplicating current JavaScript logic (or a shared rendering library callable from Python).
  - Still introduces network latency for each update; complex interactions (drag/drop, rapid typing) may feel less fluid.
  - The front-end editor must remain aware of HTMX lifecycle events (e.g., reinitializing component interactions) after swaps.
- **Migration Path**
  1. Stand up HTMX endpoints per component (e.g., `/render/component?path=...`).
  2. Wrap YAML mutation + render logic in the Python service; reuse schema validation from the LLM integration layer.
  3. Gradually replace client-side render calls with `hx-post`/`hx-swap` requests—start with low-frequency updates (apply changes, component insert) before moving to keystroke-level updates.
  4. Maintain a fallback: during migration keep the client render path so the editor stays usable offline or if the backend is unreachable.
- **When to choose this**
  - You need server-rendered output for compliance or integration reasons and want to avoid running JS rendering on the server.
  - You prefer HTMX’s minimal JS footprint and are comfortable with Python-based templating for components.


## Recommended Approach
- **Keep client-side rendering** for the interactive editor to preserve responsiveness and minimize duplication.
- **Introduce a lightweight Python service** focused on LLM interactions:
  - Hosts endpoints that receive YAML + user prompt.
  - Applies schema-aware mutations to YAML and returns the updated document.
  - Optionally logs changes or runs validations before returning data.
- **Share schemas/contracts:** Define a YAML schema (JSON Schema or shared module) usable by both the front-end runtime and Python service to ensure consistency.
- **Expose reusable render functions:** As the JavaScript renderer is modularized, provide a pure render function that can run under Node. This enables future server-side rendering or export jobs without abandoning the client-renderer.

## Integration Flow with LLM Service
1. User triggers an LLM-assisted update (prompt from UI).
2. Front end sends current YAML + prompt metadata to the Python service.
3. Python service invokes the LLM, applies schema validation, and returns updated YAML (or diffs).
4. Front end replaces the YAML in the editor, triggering the existing preview render.
5. Optional: the service can store audit logs or suggestions for undo/redo coordination.

## Future Considerations
- Evaluate running the JavaScript render bundle in Node for exports, eliminating the need for a separate Python renderer.
- If heavy server-rendered exports become crucial, consider a dedicated rendering worker that reuses the JS modules via Deno/Node.
- Monitor latency and cost: if the LLM service sees heavy load, rate limit or queue requests without affecting the live preview.


