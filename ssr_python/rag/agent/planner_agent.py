"""ssr_python/rag/agent/planner_agent.py — Site outline generator (create_page intent)."""
import json
import re
import logging

from rag.config import config
from rag.retrieval.hybrid import HybridSearch
from rag.agent.model_backend import ModelBackend

logger = logging.getLogger(__name__)

PLANNER_SYSTEM = """You are a website architect. Given a user request, generate a JSON outline.

OUTPUT: Return ONLY valid JSON (no markdown, no explanation).
{
  "page_title": "Page Title",
  "theme": {
    "primary": "#hex", "text": "#hex", "secondary": "#hex", "accent": "#hex", "background": "#hex",
    "heading_font": "'Font Name', serif",
    "content_font": "'Font Name', sans-serif"
  },
  "sections": [
    {
      "type": "hero|features|pricing|testimonials|cta|faq|contact|footer|...",
      "description": "Brief description of section content and layout",
      "components": ["layout-row", "image", "heading", "paragraph", "button"],
      "icons": ["icon-name-1"],
      "images": [{"url": "/uploads/...", "altText": "description", "orientation": "landscape"}],
      "style_notes": "Brief layout and color instructions for the builder"
    }
  ]
}

COLOR ROLES: primary = heading color (brand), text = paragraph/body (must contrast background), secondary = borders/cards, accent = CTAs, background = page bg.

IMAGES:
- Assign EVERY provided image to exactly one section. No duplicates, no unassigned images.
- Orientation: landscape → hero/features/CTA, portrait → team/testimonials, landscape/square → cards/grids.
- Text-only sections (FAQ, footer, pricing) get "images": []. No images provided → all "images": [].

ICONS:
- Only on sections that benefit (features, services, footer). Pick from [Available Icons] only.

RULES:
- Valid components: layout-row, layout-column, columnsgrid, heading, paragraph, eyebrow, caption, blockquote, link, image, video, gif, button, titlebar, br, icon, badge, rating, progress-bar, counter-up, countdown, tabs, accordion, carousel, hamburger, ticker, textbox, textarea, dropdown, checkbox, radio, calendar
- 3-8 sections per page. Match industry/tone to request. Use [Outline] as structural inspiration."""


class PlannerAgent:
    def __init__(self, search: HybridSearch, model: ModelBackend):
        self.search = search
        self.model = model

    def plan(self, query: str, selected_images: list | None = None) -> tuple[dict, str]:
        """Generate a site outline from user query, optionally assigning images to sections.

        Returns:
            (outline, style_context) tuple — outline is the parsed JSON dict,
            style_context is the raw style chunk text for the Styler Agent.
        """
        # Retrieve relevant website outlines for structural guidance (guide tier)
        outline_chunks = self.search.search(
            query,
            top_k=config.planner_top_k,
            tier="guide",
        )

        logger.info(f"Planner retrieved {len(outline_chunks)} outline chunks")
        for i, c in enumerate(outline_chunks):
            logger.debug(f"  Outline chunk {i}: {c.get('source_file', '?')} | {c.get('id', '?')}")

        # Retrieve relevant icon names from icon tier
        icon_chunks = self.search.search(query, top_k=config.icon_top_k, tier="icon")
        icon_names = [c["content"] for c in icon_chunks]
        logger.info(f"Planner retrieved {len(icon_names)} icons: {icon_names[:10]}")

        # Build context from retrieved outlines
        context = "\n\n".join([
            f"--- Reference: {c['source_file']} ---\n{c['content']}"
            for c in outline_chunks
        ])

        # Retrieve matching style/theme chunks via dedicated style tier
        style_chunks = self.search.search(
            query,
            top_k=config.style_top_k,
            tier="style",
        )
        style_context = "\n\n".join([c['content'] for c in style_chunks])
        logger.info(f"Planner retrieved {len(style_chunks)} style chunks, {len(style_context)} chars")

        user_parts = []
        if style_context:
            user_parts.append(f"[Style]\n{style_context}")
        user_parts.append(f"[Outline]\n{context}")
        if icon_names:
            user_parts.append(
                f"[Available Icons]\n{', '.join(icon_names)}\n"
                f"Use `- name: icon` with `properties.name: <icon-name>` for any of these."
            )
        if selected_images:
            img_lines = [f"[Available Images — you MUST assign ALL {len(selected_images)} images to sections]"]
            for i, img in enumerate(selected_images, 1):
                url = img.get('url', '')
                alt = img.get('altText', '')
                orientation = img.get('orientation', 'unknown')
                photographer = img.get('photographer', '')
                credit = f" (Photo by {photographer})" if photographer else ""
                img_lines.append(f"{i}. {url} — \"{alt}\" [{orientation}]{credit}")
            user_parts.append("\n".join(img_lines))

        user_parts.append(f"[User Request]\n{query}")
        user_prompt = "\n\n".join(user_parts)
        logger.debug(f"Planner user prompt ({len(user_prompt)} chars):\n{user_prompt[:500]}...")

        # Generate outline
        response = self.model.generate(PLANNER_SYSTEM, user_prompt)
        logger.info(f"Planner raw LLM response ({len(response)} chars):\n{response}")

        # Parse JSON (strip markdown if model wraps it)
        outline = self._parse_outline(response)
        return outline, style_context

    def _parse_outline(self, response: str) -> dict:
        """Extract JSON from model response."""
        # Try to extract JSON from code block
        match = re.search(r'```(?:json)?\s*\n(.+?)```', response, re.DOTALL)
        text = match.group(1) if match else response

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to find JSON object in response
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Could not parse outline JSON from response: {text[:200]}")
