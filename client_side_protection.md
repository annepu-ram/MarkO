# Protecting Client-Side Rendering Code

Shipping the entire renderer to the browser inevitably exposes code to inspection. While you cannot make front-end JavaScript completely private, the following practices raise the bar for copying and clarify legal protections.

## Build & Delivery Practices
- **Bundle and minify:** Use a build step (esbuild/rollup/webpack) that tree-shakes modules, minifies output, and mangles identifiers. Ship only the compiled bundle; keep source modules out of the distribution.
- **Disable production source maps:** Do not expose `.map` files in production builds or gate them behind authentication for debugging.
- **Optional obfuscation:** Apply an obfuscation pass (e.g., Terser advanced mangling or specialized tools) for additional friction, balancing against debug needs and bundle size.

## Architectural Safeguards
- **Keep sensitive logic server-side:** Business rules, premium features, or LLM-driven transformations should live behind authenticated APIs. The client only orchestrates and renders results.
- **Tokenize rendering where possible:** If portions of the renderer are proprietary, consider serving pre-rendered snippets or using HTMX/SSR for those components while leaving standard rendering client-side.
- **Limit client secrets:** Never embed API keys or private models in the front end; use the backend as a gatekeeper.

## Legal & Monitoring Measures
- **Licensing:** Publish a clear license (commercial, proprietary, etc.) stating usage restrictions. Embed notices within the bundled code or about dialogs.
- **Watermarking & telemetry:** Consider subtle runtime markers or optional telemetry to identify unauthorized deployments, respecting privacy requirements.
- **Enforcement readiness:** Maintain documentation showing code ownership and change history (e.g., via git) to support DMCA takedowns or legal action if necessary.

## Trade-offs
- **Obfuscation vs. maintainability:** Heavy obfuscation can hinder debugging; apply it selectively.
- **Performance impact:** Some obfuscation techniques increase bundle size or runtime overhead—test before shipping.
- **Security theater:** All client-side code is ultimately downloadable; focus on friction and legal clarity rather than absolute secrecy.

## When to Reevaluate
- If the renderer gains highly proprietary algorithms or premium templates, reassess moving those parts to server-side rendering or LLM-backed services.
- As the product scales, monitor competitor activity and upgrade build/monitoring practices accordingly.

