"""ssr_python/rag/agent/planner_agent.py — Site outline generator (create_page intent).

Outputs markdown (not JSON). Structure only — no theme, no style, no images.
Images are assigned by the styler agent.
"""
import re
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.agent.model_backend import ModelBackend
from rag.agent.prompt_loader import load_system, render_user
from rag.agent.prompt_logger import log_prompt, log_output

logger = logging.getLogger(__name__)


# Default component suggestions per section type.
# Used by plan_from_context() (deterministic planning) so the builder
# receives sensible component specs even without an LLM-generated outline.
# Every section type referenced in INDUSTRY_REGISTRY variants should have
# an entry here; missing types fall back to a generic set.
_SECTION_COMPONENTS: dict[str, list[str]] = {
    "navigation": ["titlebar", "layout-row", "button", "heading"],
    "hero": ["layout-row", "heading", "paragraph", "button", "image", "eyebrow"],
    "about": ["layout-row", "heading", "paragraph", "image", "button"],
    "features": ["columnsgrid", "icon", "heading", "paragraph"],
    "services": ["columnsgrid", "icon", "heading", "paragraph", "button"],
    "menu": ["columnsgrid", "heading", "paragraph", "image", "badge"],
    "products": ["columnsgrid", "image", "heading", "paragraph", "button", "badge"],
    "pricing": ["columnsgrid", "heading", "paragraph", "button", "badge"],
    "testimonials": ["columnsgrid", "heading", "paragraph", "rating", "image"],
    "stats": ["columnsgrid", "counter-up", "heading", "paragraph"],
    "gallery": ["columnsgrid", "image"],
    "team": ["columnsgrid", "image", "heading", "paragraph"],
    "faq": ["accordion", "heading"],
    "cta": ["layout-row", "heading", "paragraph", "button"],
    "form_cta": ["layout-row", "heading", "paragraph", "form", "textbox", "textarea", "button"],
    "contact": ["layout-row", "heading", "paragraph", "form", "textbox", "textarea", "button", "icon"],
    "order_form": ["layout-row", "heading", "form", "textbox", "textarea", "dropdown", "button"],
    "reservation": ["layout-row", "heading", "form", "textbox", "calendar", "dropdown", "button"],
    "countdown": ["layout-row", "heading", "paragraph", "countdown", "button"],
    "how_it_works": ["columnsgrid", "icon", "heading", "paragraph"],
    "schedule": ["columnsgrid", "heading", "paragraph", "badge"],
    "delivery_areas": ["columnsgrid", "icon", "heading", "paragraph"],
    "trusted_by": ["layout-row", "image", "heading"],
    "achievements": ["columnsgrid", "counter-up", "heading", "paragraph"],
    "footer": ["layout-row", "layout-column", "heading", "paragraph", "link", "icon"],
    "banner": ["layout-row", "heading", "paragraph", "button"],
    "newsletter": ["layout-row", "heading", "paragraph", "textbox", "button"],
    "blog": ["columnsgrid", "image", "heading", "paragraph", "eyebrow", "link"],
    "dashboard": ["columnsgrid", "counter-up", "heading", "paragraph", "progress-bar", "icon"],
    "ticker": ["ticker", "heading", "paragraph", "image"],
    "social_links": ["layout-row", "icon", "link", "heading"],
    "divider": ["br"],
}

_DEFAULT_COMPONENTS = [
    "layout-row", "heading", "paragraph", "button", "image",
]


# Suggested icon group(s) per section type — biases icon retrieval to
# semantically relevant icons (e.g. "navigation" sections want navigation
# icons, "contact" wants communication icons).
_SECTION_ICON_GROUPS: dict[str, list[str]] = {
    "navigation": ["navigation", "user", "ecommerce"],
    "footer": ["social", "navigation", "communication"],
    "social_links": ["social", "communication"],
    "contact": ["communication", "location", "user"],
    "features": ["feedback", "settings", "commerce"],
    "services": ["settings", "feedback", "commerce"],
    "how_it_works": ["feedback", "settings", "navigation"],
    "stats": ["commerce", "feedback"],
    "team": ["user", "social"],
    "pricing": ["commerce", "feedback", "ecommerce"],
    "testimonials": ["user", "commerce"],
    "products": ["ecommerce", "commerce", "feedback"],
    "menu": ["food", "commerce"],
    "schedule": ["time", "user"],
    "countdown": ["time", "feedback"],
    "delivery_areas": ["location", "transport"],
    "trusted_by": ["commerce", "user"],
    "achievements": ["commerce", "feedback"],
    "newsletter": ["communication", "user"],
    "banner": ["feedback", "commerce"],
}


_SECTION_LAYOUT_OPTIONS: dict[str, list[str]] = {
    "hero": ["split_screen", "fullscreen", "centered", "stacked"],
    "features": ["grid", "stacked", "split_screen"],
    "services": ["grid", "stacked", "split_screen"],
    "pricing": ["grid", "stacked", "centered"],
    "testimonials": ["grid", "carousel_slider", "stacked", "centered"],
    "cta": ["centered", "split_screen", "stacked"],
    "contact": ["split_screen", "stacked", "centered"],
    "about": ["split_screen", "stacked", "centered"],
    "team": ["grid", "stacked"],
    "gallery": ["grid", "carousel_slider"],
    "faq": ["stacked", "centered", "split_screen"],
    "footer": ["stacked", "split_screen"],
    "stats": ["grid", "centered", "stacked"],
    "blog": ["grid", "stacked"],
    "products": ["grid", "carousel_slider", "stacked"],
    "menu": ["grid", "stacked"],
    "how_it_works": ["stacked", "grid"],
    "newsletter": ["centered", "split_screen"],
    "countdown": ["centered", "stacked"],
    "banner": ["centered", "stacked"],
}


def _assign_layout_hints(sections: list[dict]) -> None:
    """Assign layout_hint to each section, rotating for repeated types."""
    type_count: dict[str, int] = {}
    for section in sections:
        stype = section.get("type", "other")
        options = _SECTION_LAYOUT_OPTIONS.get(stype, ["stacked"])
        idx = type_count.get(stype, 0) % len(options)
        section["layout_hint"] = options[idx]
        type_count[stype] = type_count.get(stype, 0) + 1


def _suggest_components_for(section_type: str) -> list[str]:
    """Return a default component suggestion list for a section type."""
    return list(_SECTION_COMPONENTS.get(section_type, _DEFAULT_COMPONENTS))


def _suggest_icon_groups_for(section_type: str) -> list[str]:
    """Return suggested icon group filters for a section type."""
    return list(_SECTION_ICON_GROUPS.get(section_type, []))


class PlannerAgent:
    def __init__(self, search: HybridSearch, model: ModelBackend):
        self.search = search
        self.model = model

    def plan(self, query: str, intent=None) -> str:
        """Generate a site outline from user query as markdown.

        Args:
            query: User's natural-language request.
            intent: Optional QueryIntent from QueryAnalyzer; used to bias
                outline retrieval by industry.

        Returns:
            Raw markdown string with # Page Title and ## SectionType headings.
        """
        # Retrieve relevant website outlines for structural guidance (guide tier).
        # When the user query has an industry signal, restrict to outlines from
        # that industry — generic SaaS outlines should not bleed into a "vegan
        # bakery" plan.
        outline_filter = None
        if intent is not None and getattr(intent, "industry_filter", None):
            outline_filter = {"industry": intent.industry_filter}
        outline_chunks = self.search.search(
            query,
            top_k=config.planner_top_k,
            tier="guide",
            metadata_filter=outline_filter,
        )
        # Fall back to unfiltered when the industry filter excluded everything.
        if not outline_chunks and outline_filter:
            outline_chunks = self.search.search(
                query, top_k=config.planner_top_k, tier="guide"
            )

        # Retrieve relevant icon names from icon tier
        icon_chunks = self.search.search(query, top_k=config.icon_top_k, tier="icon")
        icon_names = [c["content"] for c in icon_chunks]

        system = load_system("planner")
        user_prompt = render_user("planner",
            outline_chunks=outline_chunks,
            icon_names=icon_names,
            query=query,
        )
        log_prompt("PLANNER", system, user_prompt)

        # Generate outline
        response = self.model.generate(system, user_prompt)
        log_output("PLANNER", response)

        return response

    def plan_from_context(self, business_context: dict) -> dict:
        """Deterministically build an outline dict from guided-flow business context.

        No LLM call. Uses the user's selected sections (with content) as the
        source of truth. For each section, queries the icon tier to attach
        relevant icon names, and assembles a default component suggestion
        list from `_SECTION_COMPONENTS`.

        Args:
            business_context: Dict from the guided wizard with shape:
                {
                    business_name, industry, variant_id, variant_label,
                    description,
                    sections: [{type, content: {...}}, ...],
                    style_preference, color_preference,
                }

        Returns:
            Outline dict matching parse_outline() shape:
                {"page_title": str, "sections": [{type, description,
                    components, icons, raw_md}, ...]}
        """
        bc = business_context or {}
        business_name = (bc.get("business_name") or "").strip()
        industry = (bc.get("industry") or "").strip()
        description = (bc.get("description") or "").strip()
        page_title = business_name or bc.get("variant_label") or "New Page"

        raw_sections = bc.get("sections") or []
        outline_sections: list[dict] = []

        for s in raw_sections:
            stype = (s.get("type") or "").strip().lower()
            if not stype:
                continue
            content = s.get("content") or {}
            # A recipe-driven section (campaign spine) may pre-provide its
            # component allow-list, style notes, and conversion intent. Honor
            # them instead of the generic per-type defaults.
            preset_components = s.get("components") or None
            preset_style_notes = s.get("style_notes") or ""
            preset_conversion_intent = s.get("conversion_intent") or None

            # Build a per-section description from business metadata + section content.
            # This feeds into the builder's search query and the styler's outline summary.
            desc_parts = []
            if business_name:
                desc_parts.append(f"{stype.replace('_', ' ').title()} section for {business_name}")
            else:
                desc_parts.append(f"{stype.replace('_', ' ').title()} section")
            if industry:
                desc_parts.append(f"({industry})")
            # Add the most salient content snippet (first non-empty value) for context.
            for v in (content or {}).values():
                val = str(v).strip() if v is not None else ""
                if val:
                    # Use a short excerpt to avoid bloating the search query.
                    desc_parts.append("— " + (val[:140] + "..." if len(val) > 140 else val))
                    break
            description_str = " ".join(desc_parts).strip()

            components = preset_components or _suggest_components_for(stype)

            # Retrieve a handful of icon candidates relevant to this section.
            # Best-effort: silently fall back to an empty list on any failure.
            icons: list[str] = []
            try:
                icon_query = f"{stype.replace('_', ' ')} {industry} {business_name}".strip()
                # Bias retrieval to icon groups relevant to this section type
                # so e.g. "contact" sections pull communication/location icons,
                # not arbitrary high-cosine-match icons.
                groups = _suggest_icon_groups_for(stype)
                icon_filter = {"groups": groups} if groups else None
                icon_chunks = self.search.search(
                    icon_query,
                    top_k=config.icon_top_k,
                    tier="icon",
                    metadata_filter=icon_filter,
                )
                if not icon_chunks and icon_filter:
                    # Fallback: groups too narrow → unfiltered
                    icon_chunks = self.search.search(
                        icon_query, top_k=config.icon_top_k, tier="icon",
                    )
                icons = [c.get("content", "").strip() for c in icon_chunks if c.get("content")]
            except Exception as e:
                logger.debug(f"plan_from_context: icon retrieval failed for {stype}: {e}")

            # Build a markdown-shaped `raw_md` for parity with parse_outline(),
            # which downstream code (stitcher, logging) may inspect.
            raw_md_lines = [
                f"## {stype.replace('_', ' ').title()}",
                f"- {description_str}",
                f"- Components: {', '.join(components)}",
            ]
            if icons:
                raw_md_lines.append(f"- Icons: {', '.join(icons)}")

            section_dict = {
                "type": stype,
                "description": description_str,
                "components": components,
                "icons": icons,
                "raw_md": "\n".join(raw_md_lines),
                # Retain real user-provided content for downstream use by builder.
                "business_content": {k: v for k, v in (content or {}).items()
                                      if v is not None and str(v).strip()},
            }
            # Carry recipe-driven hints through to the styler/builder.
            if preset_style_notes:
                section_dict["style_notes"] = preset_style_notes
            if preset_conversion_intent:
                section_dict["conversion_intent"] = preset_conversion_intent
            outline_sections.append(section_dict)

        _assign_layout_hints(outline_sections)

        logger.info(
            f"plan_from_context: built outline with {len(outline_sections)} sections "
            f"(business='{business_name}', industry='{industry}', "
            f"variant='{bc.get('variant_id')}')"
        )

        return {
            "page_title": page_title,
            "sections": outline_sections,
            # Expose description so the styler/builder can see the business pitch.
            "business_description": description,
        }

    def parse_outline(self, md: str) -> dict:
        """Parse planner markdown into structured outline dict.

        Returns:
            {"page_title": str, "sections": [{type, description, components, icons, raw_md}, ...]}
        """
        lines = md.strip().split("\n")

        # Extract page title from first # heading
        page_title = "New Page"
        for line in lines:
            m = re.match(r'^#\s+(.+)', line)
            if m and not line.startswith("##"):
                page_title = m.group(1).strip()
                break

        # Split at ## headings
        sections = []
        current_section = None
        current_lines = []

        for line in lines:
            m = re.match(r'^##\s+(.+)', line)
            if m:
                # Save previous section
                if current_section is not None:
                    sections.append(self._parse_section(current_section, current_lines))
                current_section = m.group(1).strip()
                current_lines = []
            elif current_section is not None:
                current_lines.append(line)

        # Save last section
        if current_section is not None:
            sections.append(self._parse_section(current_section, current_lines))

        _assign_layout_hints(sections)

        return {"page_title": page_title, "sections": sections}

    def _parse_section(self, heading: str, lines: list[str]) -> dict:
        """Parse a single ## section into a structured dict."""
        section_type = heading.lower().replace(" ", "_")
        description = ""
        components = []
        icons = []
        raw_lines = [f"## {heading}"] + lines

        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            bullet = stripped[2:].strip()

            if bullet.lower().startswith("components:"):
                comp_str = bullet.split(":", 1)[1].strip()
                components = [c.strip() for c in comp_str.split(",") if c.strip()]
            elif bullet.lower().startswith("icons:"):
                icon_str = bullet.split(":", 1)[1].strip()
                icons = [i.strip() for i in icon_str.split(",") if i.strip()]
            elif not description:
                description = bullet

        return {
            "type": section_type,
            "description": description,
            "components": components,
            "icons": icons,
            "raw_md": "\n".join(raw_lines),
        }
