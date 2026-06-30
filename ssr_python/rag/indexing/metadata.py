"""ssr_python/rag/indexing/metadata.py — Extract searchable metadata from chunks."""
import re
from rag.indexing.chunker import Chunk
from rag.config import CANONICAL_STYLES

# Canonical content volume values — describes how much content a template carries.
# light    — minimal copy, ≤1 paragraph, 0–2 CTAs, no grids
# standard — typical: 1 heading + 1–3 paragraphs + 3–4 supporting items
# rich     — heavy: multi-section composition, ≥6 grid items, deep tabs/accordions
CONTENT_VOLUMES = {"light", "standard", "rich"}

# Voice register of the sample copy — orthogonal to visual style.
TONES = {"formal", "neutral", "casual", "playful"}

# What action the section drives users toward.
CONVERSION_INTENTS = {"awareness", "lead", "purchase", "trust", "engagement"}

# How dependent the template is on real photography.
IMAGE_REQUIREMENTS = {"none", "decorative", "required", "many"}

# Dominant interaction surfaces. CSV in headers because a template may have
# multiple (e.g. "form, tabs"). First entry is the dominant one.
INTERACTIVITY_TYPES = {"static", "form", "carousel", "tabs", "accordion", "video"}

# Canonical industry keys — must match rag.config.INDUSTRY_DEFAULT_STYLE keys
# (the 22 industries the planner / styler operate on). Imported from config to
# stay in sync; redefining it here would invite drift.
def _canonical_industries() -> set[str]:
    from rag.config import INDUSTRY_DEFAULT_STYLE
    return set(INDUSTRY_DEFAULT_STYLE.keys())

# Closed-vocab Layout primary tokens (the first token in `Layout:` is validated;
# subsequent comma-separated tokens are free-text modifiers).
LAYOUT_PRIMARY = {
    "fullscreen", "split_screen", "grid", "stacked",
    "centered", "asymmetric", "overlay", "carousel_slider",
}

# Folders that contain component-only demos, not full sections. The chunker
# skips template_section emission for these so they don't pollute section-tier
# retrieval, but they still produce per-component template chunks.
COMPONENT_ONLY_FOLDERS = {"badge", "rating", "progress-bar", "icon", "br"}


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

# Known section patterns — aligned with planner_agent._SECTION_COMPONENTS (28 canonical types)
SECTION_PATTERNS = {
    # More specific patterns first (e.g. order_form before products, reservation before contact)
    "hero": r"hero|banner|splash|above.?fold|immersive",
    "pricing": r"pricing|plans?|tiers?",
    "testimonials": r"testimonial|review|quote|social.?proof|praise",
    "footer": r"footer|bottom|copyright",
    "features": r"features?|benefits?|highlights?",
    "services": r"service|offering|what.?we.?do|solutions?",
    "faq": r"faq|questions?|q\s*&\s*a",
    "navigation": r"nav|header|titlebar|mega.?menu|breadcrumb|sticky",
    "menu": r"\bmenu\b|dishes|courses|tasting",
    "order_form": r"order.?form|order.?online|place.?order",
    "reservation": r"reservation|reserve.?table|book.?table",
    "form_cta": r"form.?cta|enquiry|booking.?form|catering.?form",
    "contact": r"contact|get.?in.?touch|reach.?us",
    "about": r"about|our.?story|mission|who.?we.?are|meet.?the",
    "products": r"product|catalog|shop|item|retail|bundle|configurator",
    "team": r"team|staff|member|employee",
    "stats": r"stats?|numbers?|counter|metric|fundrais",
    "achievements": r"achievements?|awards?|milestones?|recognition",
    "gallery": r"gallery|portfolio|showcase|masonry|hover.?overlay|panorama",
    "blog": r"blog|article|post|story|editorial|listicle|podcast",
    "newsletter": r"newsletter|subscribe|sign.?up.?for.?(?:updates|news)",
    "dashboard": r"dashboard|data.?card|stat.?snapshot|trend|activity.?feed|progress.?card",
    "countdown": r"countdown|timer|flash.?sale|launch|event.?registration",
    "how_it_works": r"how.?it.?works|process|steps?|workflow",
    "delivery_areas": r"delivery.?area|service.?area|coverage.?area",
    "trusted_by": r"trusted.?by|as.?seen.?in|logo.?strip|client.?logos",
    "ticker": r"ticker|scrolling|marquee",
    "schedule": r"schedule|timetable|agenda|appointment|class.?time",
    "social_links": r"social.?link|social.?media|follow.?us",
    "banner": r"announcement|notice|alert|cookie.?banner",
    "cta": r"call.?to.?action|\bcta\b|sign.?up|conversion",
    "divider": r"divider|separator|breaker|section.?break",
}

# Normalize common header/planner variations to canonical keys.
# Canonical keys match planner_agent._SECTION_COMPONENTS (plural where applicable).
SECTION_TYPE_ALIASES = {
    "testimonial": "testimonials",       # singular legacy → plural canonical
    "reviews": "testimonials",
    "review": "testimonials",
    "toppers": "testimonials",
    "dividers": "divider",
    "status": "dashboard",
    "product": "products",               # singular legacy → plural canonical
    "booking_form": "form_cta",
    "enquiry_form": "form_cta",
    "catering_form": "form_cta",
    "custom_orders": "form_cta",
    "download_cta": "cta",
    "subjects": "features",
    "levels": "features",
    "courses": "features",
    "methodology": "how_it_works",
    "categories": "products",
    "combos": "products",
    "events": "schedule",
    "style": "other",                    # legacy "styles/" folder section_type
}

INDUSTRY_PATTERNS = {
    # All 22 canonical industries from rag.config.INDUSTRY_DEFAULT_STYLE.
    # Order matters — more specific patterns must come BEFORE generic ones to
    # avoid being shadowed (matches "Perfect for:" header text and YAML body).
    "homeservices":          r"plumb(?:ing|er)|electric(?:ian|al)|hvac|roofing|roofer|handyman|pest.?control|landscap|cleaning.?service|carpet|pressure.?wash|garage.?door|locksmith|home.?repair|gutter",
    "construction":          r"construction|contractor|renovation|remodel",
    "beauty":                r"salon|barber|\bspa\b|\bnail\b|stylist|beauty|cosmetic|\blash\b|\bbrow\b|tattoo|piercing",
    "automotive_services":   r"mechanic|auto.?repair|oil.?change|body.?shop|towing|car.?wash|detailing",
    "food_services":         r"catering|food.?truck|meal.?prep|juice|smoothie|ice.?cream|brewery|winery|distillery",
    "retail_local":          r"hardware|florist|gift.?(?:shop|store)|pet.?(?:store|shop)|thrift|antique|optical",
    "professional_services": r"account(?:ant|ing)|insurance|financ|mortgage|dental|dentist|chiropract|veterinar|optometr|therapy|counsel|architect",
    "trades":                r"weld(?:ing|er)|carpent|masonry|concrete|paving|fencing|siding|insulation|drywall|flooring|cabinet|countertop|septic",
    "community":             r"church|mosque|temple|synagogue|nonprofit|charity|volunteer|community.?center|library|daycare|preschool",
    "fitness_recreation":    r"yoga|pilates|martial.?art|boxing|crossfit|dance.?studio|\bgym\b|fitness.?(?:center|studio)|recreation|bowling|golf|skating",
    # Broader buckets
    "saas":          r"\bsaas\b|software|\bapp\b|platform|dashboard|fintech|b2b|startup|tech",
    "restaurant":    r"restaurant|food|menu|dining|bakery|cafe|coffee|pizza|gourmet|beverage|eatery|bistro",
    "ecommerce":     r"\bshop\b|\bstore\b|product|cart|ecommerce|retail|flash.?sale|new.?arrival|boutique",
    "portfolio":     r"portfolio|agency|freelanc|creative|design|photography",
    "health":        r"health|medical|clinic|wellness|healthcare|hospital",
    "education":     r"education|school|course|learning|training|tutoring|coaching",
    "realestate":    r"real.?estate|property|housing|apartment|interior.?design|realtor",
    "logistics":     r"logistics|shipping|delivery|transport|courier",
    "hospitality":   r"hospitality|hotel|travel|tourism|resort|luxury.?brand|airbnb",
    "automotive":    r"\bauto\b|\bcar\b|vehicle|dealer|motor",
    "entertainment": r"entertainment|gaming|\bmusic\b|event|conference|festival|concert",
    "legal":         r"\blegal\b|\blaw\b|attorney|consulting",
}

# Folder name (parent dir) → canonical section_type. Folder rename in Phase 2
# of the RAG reorg makes most entries identity mappings. Aliases remain only
# for folders deliberately left un-renamed.
FOLDER_TO_SECTION_TYPE = {
    # Identity mappings — folder name IS canonical key
    "hero": "hero",
    "navigation": "navigation",
    "footer": "footer",
    "features": "features",
    "services": "services",
    "cta": "cta",
    "faq": "faq",
    "contact": "contact",
    "gallery": "gallery",
    "blog": "blog",
    "dashboard": "dashboard",
    "countdown": "countdown",
    "ticker": "ticker",
    "schedule": "schedule",
    "social_links": "social_links",
    "banner": "banner",
    "products": "products",
    "pricing": "pricing",
    "testimonials": "testimonials",
    "team": "team",
    "about": "about",
    "stats": "stats",
    "achievements": "achievements",
    "newsletter": "newsletter",
    "how_it_works": "how_it_works",
    "delivery_areas": "delivery_areas",
    "trusted_by": "trusted_by",
    "menu": "menu",
    "order_form": "order_form",
    "reservation": "reservation",
    "form_cta": "form_cta",
    "divider": "divider",
    # Component-only folders — chunker skips template_section emission for these.
    "badge": "other",
    "rating": "other",
    "progress-bar": "other",
    "icon": "other",
    "br": "other",
    # Transitional aliases — for any folder kept under its legacy name.
    "team_about": "about",
    "titlebar": "navigation",
    "navigation_footer": "navigation",
    "cta_banners": "cta",
    "features_benefits": "features",
    "pricing_plan_cards": "pricing",
    "review_testimonial_cards": "testimonials",
    "portfolio_showcase_cards": "gallery",
    "panorama-display": "gallery",
    "story_blog_cards": "blog",
    "dashboard_data_cards": "dashboard",
    "contact_section": "contact",
    "faq_section": "faq",
    "banner_announcement": "banner",
    "product_cards": "products",
    "counter-up": "stats",
    "styles": "other",
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
    "testimonials": ["Customer Reviews", "Client Testimonials", "Customer Love", "Resident Testimonials"],
    "footer": ["Footer"],
    "features": ["Feature Grid", "Why Choose Us", "Capabilities", "How It Works"],
    "cta": ["Consultation CTA", "Download App CTA"],
    "faq": ["FAQs", "House Rules & FAQs"],
    "contact": ["Enquiry Form", "Book a Service", "Property Enquiry", "Request for Quote"],
    "navigation": ["titlebar"],
    "products": ["Shop by Category", "Product Categories"],
    "team": ["The Team", "Meet the Author", "Our Attorneys"],
    "about": ["About Us", "Our Story", "Mission", "Who We Are"],
    "services": ["Services", "Offerings", "What We Do", "Solutions"],
    "menu": ["Menu", "Tasting Menu", "Signature Dishes"],
    "form_cta": ["Enquiry Form", "Booking Form", "Catering Form"],
    "order_form": ["Order Online", "Place an Order"],
    "reservation": ["Reserve a Table", "Book a Table"],
    "how_it_works": ["How It Works", "Our Process", "The Steps"],
    "delivery_areas": ["Delivery Areas", "Service Areas", "Coverage Areas"],
    "trusted_by": ["Trusted By", "As Seen In", "Client Logos"],
    "achievements": ["Achievements", "Awards", "Milestones"],
    "newsletter": ["Newsletter Signup", "Subscribe", "Stay Updated"],
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
    # Style and icon chunks already have authoritative structured metadata
    # populated by their dedicated chunkers — do not overwrite.
    if chunk.doc_type in ("style", "icon"):
        # Ensure baseline keys exist so retrieval filters never KeyError.
        chunk.metadata.setdefault("section_type", "other")
        chunk.metadata.setdefault("industry", "general")
        chunk.metadata.setdefault("industries", [])
        chunk.metadata.setdefault("component_types", [])
        chunk.metadata.setdefault("visual_style", chunk.metadata.get("visual_style", []))
        chunk.metadata.setdefault("content_volume", "standard")
        chunk.metadata.setdefault("tone", "neutral")
        chunk.metadata.setdefault("conversion_intent", "awareness")
        chunk.metadata.setdefault("image_requirement", "decorative")
        chunk.metadata.setdefault("interactivity", ["static"])
        chunk.metadata.setdefault("layout_primary", "")
        chunk.metadata.setdefault("layout_modifiers", [])
        return chunk.metadata

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
    # Prefer AST-derived list populated by the chunker (chunker._walk_component_types).
    # When present, this is the authoritative set — no need for regex inference.
    ast_types = chunk.metadata.get("component_types") or []
    if ast_types:
        # Filter to known component types only (drops "site"/"page" wrappers)
        comp_types = [t for t in ast_types if t in COMPONENT_TYPES]
        # De-duplicate while preserving order
        seen = set()
        comp_types = [t for t in comp_types if not (t in seen or seen.add(t))]
    else:
        # Fallback: regex-detected types from content
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
        # Try folder name → canonical mapping (high-confidence signal)
        category = chunk.metadata.get("category", "")
        section = FOLDER_TO_SECTION_TYPE.get(category, "")
        if not section:
            # Fall back to regex detection
            section = "other"
            for sec, pattern in SECTION_PATTERNS.items():
                if re.search(pattern, text_lower):
                    section = sec
                    break
        section = SECTION_TYPE_ALIASES.get(section, section)

    # ── Industry ──
    # Match ONLY authoritative comment text (Perfect for: > title + description).
    # Scanning the full YAML body produces false positives (e.g. component names
    # like "eyebrow" matching beauty regex).
    industry = "general"
    use_cases_lower = comment_uses.lower() if comment_uses else ""
    comment_text_lower = " ".join(filter(None, [
        comment_title.lower() if comment_title else "",
        comment_desc.lower() if comment_desc else "",
    ]))
    for ind, pattern in INDUSTRY_PATTERNS.items():
        if use_cases_lower and re.search(pattern, use_cases_lower):
            industry = ind
            break
    if industry == "general" and comment_text_lower:
        for ind, pattern in INDUSTRY_PATTERNS.items():
            if re.search(pattern, comment_text_lower):
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
    # Prefer authoritative header field (same pattern as section_type, layout).
    # If header is present but non-canonical (e.g. "default"), trust it as an
    # explicit signal that the template has no canonical style — do NOT fall
    # through to regex, which produces noisy phantom matches.
    header_style = chunk.metadata.get("template_visual_style", "")
    if header_style:
        visual_style = []
        for tag in header_style.split(","):
            key = tag.strip().lower().replace(" ", "_")
            if key in CANONICAL_STYLES:
                visual_style.append(key)
    else:
        visual_style = _extract_visual_style(text_lower)

    # ── Content volume ──
    header_volume = chunk.metadata.get("template_content_volume", "")
    if header_volume:
        cv = header_volume.strip().lower()
        content_volume = cv if cv in CONTENT_VOLUMES else "standard"
    else:
        content_volume = "standard"

    # ── Tone ──
    header_tone = chunk.metadata.get("template_tone", "")
    tone_val = header_tone.strip().lower() if header_tone else ""
    tone = tone_val if tone_val in TONES else "neutral"

    # ── Conversion intent ──
    header_intent = chunk.metadata.get("template_conversion_intent", "")
    ci = header_intent.strip().lower() if header_intent else ""
    conversion_intent = ci if ci in CONVERSION_INTENTS else "awareness"

    # ── Image requirement ──
    header_imreq = chunk.metadata.get("template_image_requirement", "")
    ir = header_imreq.strip().lower() if header_imreq else ""
    image_requirement = ir if ir in IMAGE_REQUIREMENTS else "decorative"

    # ── Interactivity (CSV; first entry = primary) ──
    header_interact = chunk.metadata.get("template_interactivity", "")
    interactivity = []
    if header_interact:
        for tag in header_interact.split(","):
            key = tag.strip().lower()
            if key in INTERACTIVITY_TYPES and key not in interactivity:
                interactivity.append(key)
    if not interactivity:
        interactivity = ["static"]

    # ── Industries (canonical CSV; falls back to inferred industry if absent) ──
    header_industries = chunk.metadata.get("template_industries", "")
    canonical_industries = _canonical_industries()
    industries: list[str] = []
    if header_industries:
        for tag in header_industries.split(","):
            key = tag.strip().lower().replace(" ", "_")
            if key in canonical_industries and key not in industries:
                industries.append(key)
    if not industries and industry != "general":
        industries = [industry]

    # ── Layout primary + modifiers (header is "primary, modifier1, modifier2") ──
    layout_primary = ""
    layout_modifiers: list[str] = []
    if header_layout:
        parts = [p.strip().lower().replace(" ", "_") for p in header_layout.split(",") if p.strip()]
        if parts:
            layout_primary = parts[0] if parts[0] in LAYOUT_PRIMARY else ""
            layout_modifiers = parts[1:] if layout_primary else parts

    # ── Outline labels ──
    outline_labels = SECTION_TO_OUTLINE_LABELS.get(section, [])

    chunk.metadata.update({
        "component_types": comp_types,
        "section_type": section,
        "industry": industry,
        "industries": industries,
        "design_tokens": list(set(tokens)),
        "has_theme": "theme" in text_lower or "colors" in text_lower,
        "is_full_page": chunk.doc_type == "template_full_page",
        "layout_pattern": layout_pattern,
        "layout_primary": layout_primary or layout_pattern,
        "layout_modifiers": layout_modifiers,
        "visual_style": visual_style,
        "content_volume": content_volume,
        "tone": tone,
        "conversion_intent": conversion_intent,
        "image_requirement": image_requirement,
        "interactivity": interactivity,
        "outline_labels": outline_labels,
        "business_keywords": _business_keywords(comment_uses),
        "layout_style_keywords": _layout_style_keywords(comment_title, header_layout),
    })

    return chunk.metadata


def _business_keywords(use_cases: str) -> list[str]:
    """Split 'Perfect for:' header text into lowercase tokens for filtering."""
    if not use_cases:
        return []
    return [t.strip().lower().rstrip(".") for t in use_cases.split(",") if t.strip()]


def _layout_style_keywords(title: str, header_layout: str) -> list[str]:
    """Combine header Layout: with noun tokens from the template title."""
    tokens: list[str] = []
    if header_layout:
        tokens.append(header_layout.strip().lower().replace(" ", "_"))
    if title:
        for w in re.findall(r"[a-z]{4,}", title.lower()):
            if w not in tokens:
                tokens.append(w)
    return tokens


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
