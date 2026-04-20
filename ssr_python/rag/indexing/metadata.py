"""ssr_python/rag/indexing/metadata.py — Extract searchable metadata from chunks."""
import re
from rag.indexing.chunker import Chunk
from rag.config import CANONICAL_STYLES


# Known component types in SwiftSites (must match actual codebase)
COMPONENT_TYPES = {
    # Layout
    "layout-row", "layout-column", "columnsgrid", "form",
    # Text
    "heading", "paragraph", "eyebrow", "caption", "blockquote", "link",
    # Media
    "image", "video", "gif",
    # UI
    "button", "titlebar", "br",
    # Marketing
    "icon", "badge", "rating", "progress-bar", "counter-up", "countdown",
    # Interactive
    "tabs", "accordion", "carousel", "hamburger", "ticker",
    # Forms
    "textbox", "textarea", "dropdown", "checkbox", "radio", "calendar",
}

# Known section patterns
SECTION_PATTERNS = {
    "hero": r"hero|banner|splash|above.?fold|immersive",
    "pricing": r"pricing|plans?|tiers?",
    "testimonial": r"testimonial|review|quote|social.?proof|praise",
    "footer": r"footer|bottom|copyright",
    "features": r"features?|benefits?|highlights?",
    "cta": r"call.?to.?action|cta|sign.?up|conversion",
    "faq": r"faq|questions?|q\s*&\s*a",
    "contact": r"contact|get.?in.?touch|reach.?us",
    "navigation": r"nav|menu|header|titlebar|mega.?menu|breadcrumb|sticky",
    "product": r"product|catalog|shop|item|retail|bundle|configurator",
    "team": r"team|staff|member|employee|meet the",
    "stats": r"stats?|numbers?|counter|metric|achievement|fundrais",
    "gallery": r"gallery|portfolio|showcase|masonry|hover.?overlay",
    "blog": r"blog|article|post|story|editorial|listicle|podcast|newsletter",
    "dashboard": r"dashboard|data.?card|stat.?snapshot|trend|activity.?feed|progress.?card",
    "countdown": r"countdown|timer|flash.?sale|launch|event.?registration",
    "ticker": r"ticker|scrolling|marquee|logo.?strip",
    "schedule": r"schedule|timetable|agenda|appointment|class.?time",
    "social_links": r"social.?link|social.?media|follow.?us",
    "banner": r"banner|announcement|notice|alert|cookie",
    "divider": r"divider|separator|breaker|section.?break",
}

# Normalize common header variations to canonical keys
SECTION_TYPE_ALIASES = {
    "testimonials": "testimonial",
    "reviews": "testimonial",
    "dividers": "divider",
    "status": "dashboard",
}

INDUSTRY_PATTERNS = {
    "saas": r"saas|software|app\b|platform|dashboard|fintech|b2b|startup|tech",
    "restaurant": r"restaurant|food|menu|dining|bakery|cafe|coffee|pizza|gourmet|beverage",
    "ecommerce": r"shop|store|product|cart|ecommerce|retail|flash.?sale|new.?arrival",
    "portfolio": r"portfolio|agency|freelanc|creative|design|photography",
    "health": r"health|medical|clinic|wellness|fitness|gym|healthcare",
    "education": r"education|school|course|learning|training|tutoring",
    "realestate": r"real.?estate|property|housing|apartment|interior.?design",
    "logistics": r"logistics|shipping|delivery|transport",
    "hospitality": r"hospitality|hotel|travel|tourism|resort|luxury.?brand",
    "automotive": r"auto|car|vehicle|dealer|motor",
    "entertainment": r"entertainment|gaming|music|event|conference|festival",
    "legal": r"legal|law|attorney|consulting",
}

# Layout pattern descriptors for enriched context
LAYOUT_PATTERNS = {
    "split_screen": r"split|50.?50|two.?column|side.?by.?side",
    "fullscreen": r"full.?screen|full.?width|immersive|100vh",
    "grid": r"grid|masonry|columns?grid|card.?grid",
    "centered": r"centered|center.?align|minimal",
    "asymmetric": r"asymmetric|off.?center|creative.?layout",
    "stacked": r"stacked|vertical|single.?column",
    "overlay": r"overlay|hover|tint|glass|blur",
    "carousel_slider": r"carousel|slider|slideshow|swipe",
}

# Outline label mapping: section_type -> descriptive labels from website_example_outlines
SECTION_TO_OUTLINE_LABELS = {
    "hero": ["Hero Split", "Hero", "Hero — Portfolio Showcase"],
    "pricing": ["Pricing", "Pricing Plans", "Pricing Table", "Bulk Pricing", "Service Plans"],
    "testimonial": ["Customer Reviews", "Client Testimonials", "Customer Love", "Resident Testimonials"],
    "footer": ["Footer"],
    "features": ["Feature Grid", "Why Choose Us", "Capabilities", "How It Works"],
    "cta": ["Consultation CTA", "Download App CTA"],
    "faq": ["FAQs", "House Rules & FAQs"],
    "contact": ["Enquiry Form", "Book a Service", "Property Enquiry", "Request for Quote"],
    "navigation": ["titlebar"],
    "product": ["Shop by Category", "Product Categories"],
    "team": ["The Team", "Meet the Author", "Our Attorneys"],
    "stats": ["Trust Stats", "Results", "At a Glance", "Platform Stats"],
    "gallery": ["Project Gallery", "Property Gallery"],
    "blog": ["Featured Authors by Genre", "Past Readings Archive"],
    "dashboard": ["Stat Snapshot", "Trend Indicator", "Activity Feed"],
    "countdown": ["Next Batch Starting", "Launch Day", "Festival Begins"],
    "ticker": ["Achievements Scroll", "Trusted By", "Client Logos", "Certifications"],
    "schedule": ["Daily Schedule", "Event Schedule"],
    "social_links": ["Social Links", "Follow Us", "Connect With Us"],
    "banner": ["Announcement Bar", "Notice Banner", "Cookie Banner"],
    "divider": ["Section Divider", "Visual Break"],
}


def extract_metadata(chunk: Chunk) -> dict:
    """Enrich chunk with searchable metadata fields.

    Uses both the YAML content and comment-derived fields (template_title,
    template_description, template_use_cases) for classification.
    Prefers authoritative header fields over regex inference.
    """
    # Combine content + source path + comment fields for pattern matching
    comment_title = chunk.metadata.get("template_title", "")
    comment_desc = chunk.metadata.get("template_description", "")
    comment_uses = chunk.metadata.get("template_use_cases", "")

    text_lower = " ".join([
        chunk.content,
        chunk.source_file,
        comment_title,
        comment_desc,
        comment_uses,
    ]).lower()

    # ── Component types ──
    # Start with regex-detected types from content
    comp_types = [t for t in COMPONENT_TYPES if t in text_lower]
    # Merge authoritative header_base_components if present
    header_comps = chunk.metadata.get("header_base_components", "")
    if header_comps:
        for comp_name in header_comps.split(", "):
            comp_name = comp_name.strip()
            if comp_name in COMPONENT_TYPES and comp_name not in comp_types:
                comp_types.append(comp_name)

    # ── Section type ──
    # Prefer authoritative header field
    header_section = chunk.metadata.get("header_section_type", "")
    if header_section:
        # Header may have comma-separated values like "contact, faq"
        section = header_section.split(",")[0].strip().lower().replace(" ", "_")
        section = SECTION_TYPE_ALIASES.get(section, section)
    else:
        # Fall back to regex detection
        section = "other"
        for sec, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, text_lower):
                section = sec
                break

    # ── Industry ──
    # "Perfect for:" lines are the strongest signal
    industry = "general"
    use_cases_lower = comment_uses.lower() if comment_uses else ""
    for ind, pattern in INDUSTRY_PATTERNS.items():
        if use_cases_lower and re.search(pattern, use_cases_lower):
            industry = ind
            break
    if industry == "general":
        for ind, pattern in INDUSTRY_PATTERNS.items():
            if re.search(pattern, text_lower):
                industry = ind
                break

    # ── Design tokens ──
    tokens = re.findall(
        r'\b(xxs|xs|sm|md|lg|xl|xxl|xxxl|bold|semibold|extrabold|stretch|contain|cover|pill)\b',
        text_lower,
    )

    # ── Layout pattern ──
    # Prefer header field
    header_layout = chunk.metadata.get("header_layout", "")
    if header_layout:
        layout_pattern = header_layout.split(",")[0].strip().lower()
    else:
        layout_pattern = "other"
        for pat_name, pattern in LAYOUT_PATTERNS.items():
            if re.search(pattern, text_lower):
                layout_pattern = pat_name
                break

    # ── Visual style ──
    # Prefer authoritative header field (same pattern as section_type, layout)
    header_style = chunk.metadata.get("template_visual_style", "")
    if header_style:
        # Parse comma-separated canonical keys, normalize to snake_case
        visual_style = []
        for tag in header_style.split(","):
            key = tag.strip().lower().replace(" ", "_")
            if key in CANONICAL_STYLES:
                visual_style.append(key)
        if not visual_style:
            # Header exists but no canonical keys found — fall back to regex
            visual_style = _extract_visual_style(text_lower)
    else:
        # No header — fall back to regex detection
        visual_style = _extract_visual_style(text_lower)

    # ── Outline labels ──
    outline_labels = SECTION_TO_OUTLINE_LABELS.get(section, [])

    chunk.metadata.update({
        "component_types": comp_types,
        "section_type": section,
        "industry": industry,
        "design_tokens": list(set(tokens)),
        "has_theme": "theme" in text_lower or "colors" in text_lower,
        "is_full_page": chunk.doc_type == "template_full_page",
        "layout_pattern": layout_pattern,
        "visual_style": visual_style,
        "outline_labels": outline_labels,
    })

    return chunk.metadata


def _extract_visual_style(text: str) -> list[str]:
    """Extract visual style keywords from text (regex fallback).

    All keys are canonical compound names from CANONICAL_STYLES, matching
    the builder_agent's normalization: style_name.lower().replace(" ", "_").
    """
    styles = []
    style_patterns = {
        "modern_minimalist": r"modern.?minimal|clean.?design|simple.?layout|sleek.?professional|visual style: modern",
        "glassmorphism": r"glass(?:morphism)?|blur.*transparen|frosted|translucent",
        "retro_vintage": r"retro|vintage|nostalgic|70s|80s|90s",
        "neubrutalism": r"neubrutalis[mt]|neo.?brutal|brutalist|thick.?border",
        "claymorphism": r"claymorphi|clay.?style|playful.?3d|pastel.?rounded|bubbly",
        "aurora_gradient": r"\baurora\b|liquid.?gradient|flowing.?gradient|northern.?lights",
        "monochrome_dark": r"\bmonochrome\b|dark.?mode|dark.?theme|dark.?background|dark.?sleek|noir|neon.?on.?dark",
        "elegant_luxury": r"elegant|luxury|sophisticated|premium|upscale|refined|high.?end|jewel",
        "organic_natural": r"organic|natural|earth|eco|sustain|handcraft|warm.?tone|rustic",
        "corporate_professional": r"corporate|enterprise|formal|structured|business|reliable|institutional",
        "bold_editorial": r"editorial|magazine|newspaper|bold.?typ|dramatic.?text|bold.?layout",
        "cyberpunk_neon": r"cyberpunk|neon|sci.?fi|digital|high.?tech|futuristic.?dark",
        "pastel_soft": r"pastel|gentle|calm|soothing|airy|delicate|soft.?color",
        "scandinavian_clean": r"scandinavian|nordic|hygge|cozy|understated|balanced.?design",
        "art_deco_geometric": r"art.?deco|gatsby|geometric|glamorous|1920|ornamental|gold.?accent",
        "tropical_vibrant": r"tropical|vibrant|beach|summer|paradise|island|colorful.?bold",
        "dark_academia": r"dark.?academia|scholarly|literary|classical|bookish|academic",
        "memphis_design": r"memphis|80s.?geometric|abstract.?shape|squiggle|confetti.?design",
        "zen_japanese": r"\bzen\b|japanese|wabi.?sabi|tranquil|serene|minimalist.?zen",
        "industrial_grunge": r"industrial|grunge|warehouse|raw.?urban|loft|iron|rust",
        "y2k_retro-futurism": r"y2k|2000s|chrome|iridescent|digital.?nostalgia|retro.?future",
        "bohemian_eclectic": r"bohemian|boho|eclectic|artisan|handmade|free.?spirit|gypsy",
    }
    for style, pattern in style_patterns.items():
        if re.search(pattern, text):
            styles.append(style)
    return styles
