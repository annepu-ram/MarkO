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
}

_DEFAULT_COMPONENTS = [
    "layout-row", "heading", "paragraph", "button", "image",
]


def _suggest_components_for(section_type: str) -> list[str]:
    """Return a default component suggestion list for a section type."""
    return list(_SECTION_COMPONENTS.get(section_type, _DEFAULT_COMPONENTS))


class PlannerAgent:
    def __init__(self, search: HybridSearch, model: ModelBackend):
        self.search = search
        self.model = model

    def plan(self, query: str) -> str:
        """Generate a site outline from user query as markdown.

        Returns:
            Raw markdown string with # Page Title and ## SectionType headings.
        """
        # Retrieve relevant website outlines for structural guidance (guide tier)
        outline_chunks = self.search.search(
            query,
            top_k=config.planner_top_k,
            tier="guide",
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

            components = _suggest_components_for(stype)

            # Retrieve a handful of icon candidates relevant to this section.
            # Best-effort: silently fall back to an empty list on any failure.
            icons: list[str] = []
            try:
                icon_query = f"{stype.replace('_', ' ')} {industry} {business_name}".strip()
                icon_chunks = self.search.search(
                    icon_query,
                    top_k=config.icon_top_k,
                    tier="icon",
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

            outline_sections.append({
                "type": stype,
                "description": description_str,
                "components": components,
                "icons": icons,
                "raw_md": "\n".join(raw_md_lines),
                # Retain real user-provided content for downstream use by builder.
                "business_content": {k: v for k, v in (content or {}).items()
                                      if v is not None and str(v).strip()},
            })

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
