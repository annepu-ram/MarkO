# AI Security Notes

## Purpose

AI endpoints can consume paid model capacity and can influence generated marketing content. They must be treated as protected application actions, not public utility APIs.

The goal is to ensure AI calls are triggered through Swift Sites UI flows, scoped to the current organization, constrained by allowed use cases, and auditable.

## Current Implementation

The shared chat AI routes now require an app-issued request gate before execution:

- `X-Requested-With: SwiftSitesApp`
- `X-AI-Request-Token` matching the per-session token rendered into app pages
- Same-origin `Origin` or `Referer`
- Editor role or higher for AI generation/enhancement endpoints
- Payload allowlisting for brand field enhancement

Protected routes:

- `POST /api/chat`
- `POST /api/chat/guided`
- `POST /api/chat/enhance`
- `POST /api/chat/campaign-handoff`
- `POST /api/chat/cancel`

Important limitation: no HTTP endpoint can be made impossible to call manually by a user who already has a valid browser session and can inspect network requests. The current gate blocks plain/manual calls and cross-origin browser calls, but it is not a substitute for real authentication, authorization, quotas, and abuse monitoring.

## Required Before Production

1. Real authentication

Replace the current default-org/default-owner development stub with real login/session handling. Every AI request must be tied to:

- user id
- organization id
- role
- session id
- request source

2. CSRF-grade protection

Keep per-session request tokens, but move toward a standard CSRF mechanism for all mutating app APIs. AI endpoints should continue to reject missing/invalid tokens.

3. Per-user and per-org quotas

Add rate limits and usage budgets:

- requests per minute per user
- requests per hour per organization
- daily AI token/cost budget per organization
- stricter limits for expensive actions like full page generation
- separate lower limits for anonymous/public-facing actions, if any are added later

4. AI action allowlist

Do not expose generic prompt execution for CMS users. Each AI endpoint should declare:

- allowed action type
- allowed fields or entities
- max input size
- max output size
- expected response shape

For example, brand field enhancement should only accept known brand fields, not arbitrary prompt names or database fields.

5. Audit logging

Log every AI call:

- user id
- organization id
- endpoint/action
- entity type and id, when applicable
- prompt template/version
- model/backend used
- token count/cost estimate, when available
- success/failure
- fallback usage
- timestamp

Do not log secrets. Be careful when logging full prompts because they may contain customer content.

6. Cost protection

Add hard stops:

- reject oversized payloads
- timeout slow model calls
- cap retries
- disable AI when org budget is exhausted
- show clear UI messaging when the action is blocked by quota

7. Prompt and output safety

AI should use structured prompts and structured outputs where possible. Outputs must be validated before writing to the CMS:

- select fields must match known options
- list fields must be capped
- generated claims must respect brand guardrails
- unsupported fields must be rejected
- generated content should not invent proof, testimonials, awards, prices, compliance claims, or customer names

8. Public site separation

Published websites should not be able to trigger internal AI endpoints. AI routes must remain app-only and should not be referenced from published pages, embeds, or public form submissions.

## Product Direction

AI should behave as a field-level and workflow-level assistant inside the Marketing CMS:

- improve a specific brand field
- draft content library items
- adapt approved content into campaign messages
- suggest page sections from campaign goals
- rewrite landing page sections
- summarize campaign results

The safer product model is constrained assistance, not open-ended chat as the main interface. Marketers should see AI outputs directly inside the field, card, campaign step, or page section they are working on.

## Open Engineering Tasks

- Replace development auth stub with real authentication and org membership lookup.
- Add a general CSRF helper for all mutating APIs.
- Add AI usage tables for audit and quota tracking.
- Add per-org AI budget settings.
- Add model call token/cost accounting.
- Add request-size validation on all AI endpoints.
- Add UI states for quota exceeded, AI disabled, and fallback suggestions.
