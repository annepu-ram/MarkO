"""ssr_python/rag/agent/prompt_builder.py — Condensed system prompt + dynamic context assembly."""
import tiktoken

from rag.config import config
from rag.agent.query_analyzer import QueryIntent
from rag.agent.component_specs import build_component_specs, VALID_TOKENS

_enc = tiktoken.get_encoding("cl100k_base")


CONDENSED_SYSTEM = """You are SwiftSites, a YAML website generator.

OUTPUT FORMAT: Always respond with an ACTION line then a YAML code block.
Actions: create, modify, delete, insert_child, insert_after, explain, settings

STRUCTURE (MANDATORY):
- site > page.components[] (theme is at site.properties.theme, NOT page level)
- Every component MUST use: `- name: component-type` then `properties:` then optional `components:`
- NEVER use inline format like `- layout-row:` — ALWAYS use `- name: layout-row`
- Nest child components under `components:` — NEVER use `children:`
- Array properties (items, tabs, slides, columns) go at COMPONENT LEVEL (same indent as name/properties) — NOT inside properties
- columnsgrid uses `columns:` at component level (not components or children)

VALID COMPONENTS:
- Layout: layout-row, layout-column, columnsgrid, form
- Text: heading, paragraph, eyebrow, caption, blockquote, link
- Media: image, video, gif, video-background, br
- UI: button, titlebar, hamburger
- Interactive: tabs, accordion, carousel, ticker
- Marketing: icon, badge, rating, progress-bar, counter-up, countdown
- Forms: textbox, textarea, dropdown, checkbox, radio, calendar

PROPERTY NESTING (CRITICAL — most common error):
- ALL properties (layout, appearance, spacing, typography, label, field, etc.) MUST be nested under `properties:`
- The ONLY keys allowed at component level are: name, properties, components, items, tabs, slides, columns
- WRONG: `- name: layout-row\n  layout: {horizontalAlign: center}`
- RIGHT: `- name: layout-row\n  properties:\n    layout: {horizontalAlign: center}`

PROPERTY RULES:
- ONLY use properties shown in the [Component Specifications] section below.
- Unspecified properties are auto-filled by defaults — omit them for cleaner YAML.
- Do NOT invent properties. No padding: {top, bottom}, no gradient: {colors: [...]}.
- Spacing and size values MUST use t-shirt tokens from [Valid Tokens] — never pixel numbers.
- widthMode goes in layout.widthMode (NOT appearance). Values: fit, "25", "33", "50", "66", "75", "stretch"
- NEVER use typography.fontFamily on individual components — fonts are set at site.properties.theme.fonts only.
- Wrap ALL text values containing special chars in quotes.

THEME COLORS (MANDATORY — use aliases, NEVER hardcode hex):
- Define YAML anchors in site.properties.theme.colors: primary (&color-primary), secondary (&color-secondary), accent (&color-accent), background (&color-background)
- Define font anchors: heading (&font-heading), content (&font-content)
- ALWAYS reference colors using aliases: *color-primary, *color-secondary, *color-accent, *color-background
- NEVER hardcode hex like '#1a1a1a' when a theme alias exists — use *color-primary instead
- Only use raw hex/rgba for special cases: semi-transparent overlays (rgba(0,0,0,0.4)), white text on dark backgrounds

ICON COMPONENT:
- Use `- name: icon` with `properties.name: <material-icon-name>` (e.g., star, favorite, search)
- NEVER use icon names directly as component names (WRONG: `- name: instagram`, RIGHT: `- name: icon` with `properties: {name: instagram}`)

TRANSPARENCY: 0 = fully transparent (invisible), 100 = fully opaque (default). For visible backgrounds use 100.

Follow the patterns in the examples below exactly. Do not invent component types or properties."""


class PromptBuilder:
    def build(
        self,
        intent: QueryIntent,
        chunks: list[dict],
        message: str,
        current_yaml: str | None = None,
        selected_component: str | None = None,
    ) -> tuple[str, str]:
        """Build (system_prompt, user_prompt) for the SLM.

        Returns a tuple so model_backend can pass them separately.
        """
        budget = self._get_budget(intent, current_yaml)

        ctx_parts = []
        tokens_used = 0
        for chunk in chunks:
            chunk_tokens = chunk.get("token_count", len(_enc.encode(chunk["content"])))
            if tokens_used + chunk_tokens > budget:
                break
            source = chunk.get("source_file", "unknown")
            ctx_parts.append(
                f"--- Example from: {source} ---\n{chunk['content']}"
            )
            tokens_used += chunk_tokens

        context_block = "\n\n".join(ctx_parts)

        comp_names = list(intent.component_filter) if intent.component_filter else []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            comp_names.extend(meta.get("component_types", []))
        if not comp_names:
            comp_names = ["heading", "paragraph", "button", "image"]
        comp_specs = build_component_specs(comp_names)

        system = CONDENSED_SYSTEM
        user_parts = []

        if comp_specs:
            user_parts.append(
                f"[Component Specifications — ONLY these properties are valid]\n{comp_specs}\n"
                f"Properties not listed here are auto-filled by defaults — do NOT invent new ones."
            )

        user_parts.append(f"[Valid Tokens]\n{VALID_TOKENS}")

        if context_block:
            user_parts.append(f"[Reference Examples]\n{context_block}")

        if current_yaml:
            user_parts.append(f"[Current YAML]\n{current_yaml}")

        if selected_component:
            user_parts.append(f"[Selected Component]\n{selected_component}")

        user_parts.append(f"[User Request]\n{message}")

        user_prompt = "\n\n".join(user_parts)
        return system, user_prompt

    def _get_budget(self, intent: QueryIntent, current_yaml: str | None) -> int:
        """Dynamic token budget — reserve room for existing YAML in modify tasks."""
        if intent.action == "create_page":
            return config.context_budget_create_page
        if intent.action == "modify" and current_yaml:
            yaml_tokens = len(_enc.encode(current_yaml))
            return max(config.min_context_budget, config.context_budget_modify - yaml_tokens // 2)
        if intent.action == "create_section":
            return config.context_budget_create_section
        return config.context_budget_default
