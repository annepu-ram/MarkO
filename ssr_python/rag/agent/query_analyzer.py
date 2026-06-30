"""ssr_python/rag/agent/query_analyzer.py — Rule-based intent classification."""
import re
from dataclasses import dataclass, field


@dataclass
class QueryIntent:
    action: str            # create_page | create_section | modify | add | explain
    section_filter: str | None     # First section keyword matched (back-compat)
    industry_filter: str | None    # saas | restaurant | ...
    style_filter: str | None = None  # glassmorphism | modern | retro | ...
    style_keywords: str = ""       # comma-separated style words from query (e.g. "modern, clean, sleek")
    color_keywords: str = ""       # comma-separated color words from query (e.g. "navy, gold")
    component_filter: list[str] = field(default_factory=list)
    content_volume_filter: str | None = None  # light | standard | rich (None = no preference)
    tone_filter: str | None = None        # formal | neutral | casual | playful
    intent_filter: str | None = None      # awareness | lead | purchase | trust | engagement
    interactivity_filter: str | None = None  # form | tabs | accordion | carousel | video | static
    sub_queries: list[str] = field(default_factory=list)
    # All section keywords matched in the query (multi-section requests).
    # Used by sub-query expansion and downstream icon/outline retrieval.
    section_filters: list[str] = field(default_factory=list)


# ── Comprehensive color pattern ──
_BASIC_COLORS = (
    r"red|blue|green|yellow|orange|purple|violet|pink|black|white|gray|grey|brown"
)
_EXTENDED_COLORS = (
    r"gold|silver|navy|teal|coral|maroon|burgundy|beige|cream|ivory|indigo|"
    r"turquoise|magenta|lavender|olive|tan|peach|mint|aqua|crimson|scarlet|"
    r"amber|emerald|sapphire|ruby|charcoal|slate|plum|orchid|salmon|sienna|"
    r"khaki|fuchsia|cyan|lime|periwinkle|mauve|lilac|taupe|rust|copper|"
    r"bronze|champagne|mustard|blush|terracotta|cobalt|cerulean|vermillion|"
    r"ochre|mahogany|auburn|sepia|mocha|espresso|caramel|honey|sand|"
    r"apricot|tangerine|papaya|persimmon|raspberry|cranberry|cherry|"
    r"strawberry|rose|carnation|flamingo|bubblegum|cerise|"
    r"jade|sage|moss|fern|seafoam|pistachio|chartreuse|"
    r"azure|denim|steel|powder|cornflower|"
    r"eggplant|amethyst|grape|wine|mulberry|boysenberry|"
    r"lemon|canary|buttercup|sunflower|saffron|marigold|"
    r"pearl|bone|linen|vanilla|oatmeal|wheat|parchment|"
    r"graphite|ash|smoke|pewter|titanium|onyx|obsidian|jet|ebony|raven"
)
# Compound colors (two-word) — listed first so "sky blue" matches before "blue" alone
_COMPOUND_COLORS = (
    r"sky\s*blue|royal\s*blue|baby\s*blue|powder\s*blue|steel\s*blue|"
    r"midnight\s*blue|dark\s*blue|light\s*blue|ice\s*blue|electric\s*blue|"
    r"ocean\s*blue|dusty\s*blue|cornflower\s*blue|"
    r"forest\s*green|dark\s*green|light\s*green|lime\s*green|olive\s*green|"
    r"sage\s*green|mint\s*green|emerald\s*green|hunter\s*green|sea\s*green|"
    r"kelly\s*green|neon\s*green|"
    r"dark\s*red|bright\s*red|cherry\s*red|wine\s*red|brick\s*red|"
    r"rose\s*gold|burnt\s*orange|burnt\s*sienna|dusty\s*rose|dusty\s*pink|"
    r"hot\s*pink|blush\s*pink|soft\s*pink|neon\s*pink|pastel\s*pink|"
    r"pale\s*yellow|bright\s*yellow|"
    r"deep\s*purple|dark\s*purple|light\s*purple|royal\s*purple|"
    r"off\s*white|warm\s*white|cool\s*white|antique\s*white|"
    r"dark\s*gray|dark\s*grey|light\s*gray|light\s*grey|"
    r"warm\s*gray|warm\s*grey|cool\s*gray|cool\s*grey"
)
COLOR_PATTERN = re.compile(
    rf"\b({_COMPOUND_COLORS}|{_BASIC_COLORS}|{_EXTENDED_COLORS})\b"
    rf"|#[0-9a-fA-F]{{3,8}}\b",
    re.IGNORECASE,
)


class QueryAnalyzer:
    """Rule-based intent classification with metadata filter extraction."""

    # Intent patterns ordered by specificity (first match wins)
    INTENT_RULES = [
        ("create_page",
         r"(?:"
         r"(?:create|build|make|generate|design|start|launch|set.?up|spin.?up|put.?together|whip.?up)\b.*?(?:web.?page|webpage|page|website|web.?site|site|landing|online.?presence|homepage|home.?page)"
         r"|"
         r"(?:need|want|looking.?for|require|would.?like|help.?me.?(?:with|make|build))\b.*?(?:web.?page|webpage|page|website|web.?site|site|landing|homepage|home.?page)"
         r"|"
         r"(?:web.?page|webpage|website|web.?site|landing.?page|homepage|home.?page)\b.*?(?:for|about)\b"
         r")"),
        ("create_section", r"(create|build|make|generate|add|design)\b.*(section|hero|pricing|footer|header|testimonial|faq|cta|features?)"),
        ("modify",         r"(change|update|modify|edit|replace|adjust|fix|set|make it)\b"),
        ("add",            r"(add|insert|include|put|append)\b.*(button|image|text|icon|badge|card|link)"),
        ("explain",        r"(what|how|explain|tell me|describe|show me|list|which)\b"),
    ]

    # Aligned with planner_agent._SECTION_COMPONENTS (28 canonical types) and
    # indexing/metadata.py SECTION_PATTERNS. Keys MUST match that vocabulary.
    SECTION_KEYWORDS = {
        "hero": r"\bhero\b|banner|splash|above.?fold",
        "pricing": r"\bpricing\b|plans?\b|tiers?\b",
        "testimonial": r"\btestimonial\b|reviews?\b|social.?proof",
        "footer": r"\bfooter\b",
        "features": r"\bfeatures?\b|benefits?\b",
        "services": r"\bservices?\b|\boffering\b|what.?we.?do|solutions?",
        "about": r"\babout\b|\bour.?story\b|mission|who.?we.?are",
        "cta": r"\bcta\b|call.?to.?action|sign.?up",
        "form_cta": r"enquiry.?form|booking.?form|catering.?form|form.?cta",
        "faq": r"\bfaq\b|questions?\b",
        "contact": r"\bcontact\b",
        "navigation": r"\bheader\b|\bnav\b|navigation|titlebar",
        "menu": r"\bmenu\b|dishes|tasting",
        "products": r"\bproducts?\b|catalog",
        "team": r"\bteam\b|staff|members?\b",
        "gallery": r"\bgallery\b|showcase|portfolio|panorama",
        "blog": r"\bblog\b|article|post",
        "stats": r"\bstats?\b|numbers?\b|counter|metric",
        "achievements": r"\bachievements?\b|awards?|milestones?",
        "schedule": r"\bschedule\b|timetable|agenda|appointment",
        "order_form": r"order.?form|order.?online|place.?order",
        "reservation": r"\breservation\b|reserve.?table|book.?table",
        "how_it_works": r"how.?it.?works|\bprocess\b|\bsteps?\b",
        "delivery_areas": r"delivery.?area|service.?area|coverage",
        "trusted_by": r"trusted.?by|as.?seen.?in|client.?logos|logo.?strip",
        "social_links": r"\bsocial.?link\b|\bsocial.?media\b|follow.?us",
        "banner": r"\bbanner\b|\bannouncement\b",
        "newsletter": r"newsletter|subscribe",
        "countdown": r"\bcountdown\b|timer",
        "ticker": r"\bticker\b|scrolling|marquee",
        "dashboard": r"\bdashboard\b|data.?card",
    }

    # Ordered by specificity: more specific patterns first to avoid broad matches
    INDUSTRY_KEYWORDS = {
        # specific retail / services — must come BEFORE generic buckets
        "bookstore":          r"\bbookstore\b|book.?store|book.?shop|books(?:eller|hop)\b|indie.?book|book.?retail\b|\blibrary.?shop\b",
        "apparel":            r"\bapparel\b|clothing.?(?:store|brand|shop|boutique)|fashion.?(?:store|brand|shop|boutique|label)|streetwear|sneaker(?:head)?\b|bridal(?:.?wear)?|formal.?wear|menswear|womenswear|kidswear|athleisure|outfit.?store",
        "grocery":            r"\bgrocery\b|grocer\b|supermarket|supermart|\bbodega\b|corner.?store|organic.?market|produce.?market|farmer.?market|whole.?food|greengrocer",
        "electronics_retail": r"electronics.?(?:store|shop|retail)|\bgadget(?:s|.?store|.?shop)?\b|consumer.?electronics|appliance.?store|mobile.?(?:shop|store)|phone.?(?:shop|store)|smartphone.?store|laptop.?(?:shop|store)|computer.?(?:shop|store)|tv.?(?:shop|store)",
        "furniture_decor":    r"\bfurniture\b|sofa.?(?:store|shop)|mattress.?(?:store|shop)|home.?decor|home.?goods|homegoods|lighting.?(?:store|shop)|rug.?(?:store|shop)|interior.?decor|home.?furnishings",
        "jewelry_store":      r"jewel(?:ry|l?ery|l?er|l?ers)\b|diamond.?(?:store|shop)|gold.?(?:store|shop)|silver.?(?:store|shop)|\bgem(?:stone)?.?(?:store|shop)?\b|engagement.?ring|wedding.?ring",
        "toy_hobby":          r"\btoys?\b.?(?:store|shop)?|kids.?(?:store|shop)|game.?(?:store|shop)|board.?game|tabletop|trading.?card|hobby.?(?:store|shop)|\bcollectibles?\b|comic.?(?:store|shop)|craft.?(?:store|shop)|model.?(?:kit|shop)",
        "sports_gear":        r"sports.?(?:gear|equipment|goods|store|shop)|sporting.?goods|athletic.?wear|outdoor.?gear|adventure.?gear|camping.?gear|bike.?(?:store|shop)|ski.?(?:store|shop)|fishing.?(?:store|shop)",
        "cafe_bakery":        r"\bcafe\b|cafeteria|coffee.?shop|coffee.?house|coffeehouse|\bbakery\b|\bbakeries\b|patisserie|boulangerie|pastry.?(?:shop|store)|doughnut.?(?:shop|store)|donut.?(?:shop|store)|\btea.?house\b|\bteahouse\b|\bbaker\b",
        "pharmacy":           r"\bpharmacy\b|pharmacies|pharmacist|drugstore|drug.?store|\bchemist\b|apothecary|compounding.?pharmacy",
        "art_gallery":        r"art.?gallery|\bgalleries\b|exhibition.?(?:space|hall)|art.?studio|art.?space|contemporary.?art|fine.?art.?gallery|art.?exhibit(?:ion)?",
        "photo_video":        r"photograph(?:y|er|ic)\b|photo.?studio|video.?production|video.?studio|videograph(?:y|er)|content.?studio|film.?studio|cinematograph",
        "bar_pub":            r"\bpub\b|gastropub|cocktail.?(?:bar|lounge)|sports.?bar|nightclub|speakeasy|tap.?room|taproom|brewpub|wine.?bar|beer.?garden|tavern|bar.?and.?grill|\blounge\b(?!.?(?:chair|suite))",

        # existing broader buckets (overlapping tokens pruned)
        "saas":                r"\bsaas\b|software|\bapp\b|platform|startup|tech",
        "restaurant":          r"restaurant|\bdine.?in\b|diner|fine.?dining|casual.?dining|food.?court|\bmenu\b|pizza|steakhouse|sushi|eatery|bistro|brasserie",
        "homeservices":        r"plumbing|plumber|electric(?:ian|al)|hvac|roofing|roofer|handyman|pest.?control|landscap|cleaning.?service|carpet|pressure.?wash|garage.?door|locksmith|home.?repair|gutter",
        "construction":        r"construction|contractor|renovation|remodel",
        "beauty":              r"salon|barber|\bspa\b|\bnail\b|\bhair\b|stylist|beauty|cosmetic|\blash\b|\bbrow\b|tattoo|piercing",
        "automotive_services": r"mechanic|auto.?repair|tire\b|oil.?change|body.?shop|towing|car.?wash|detailing",
        "food_services":       r"catering|food.?truck|meal.?prep|juice|smoothie|ice.?cream|brewery|winery|distillery",
        "retail_local":        r"hardware|florist|flower|gift.?(?:shop|store)|pet.?(?:store|shop)|thrift|antique|optical",
        "professional_services": r"account(?:ant|ing)|tax\b|insurance|financ|mortgage|dental|dentist|chiropract|veterinar|vet\b|optometr|therapy|counsel|architect",
        "trades":              r"weld(?:ing|er)|carpent|masonry|concrete|paving|fencing|siding|insulation|drywall|flooring|cabinet|countertop|pool.?service|septic",
        "community":           r"church|mosque|temple|synagogue|nonprofit|charity|volunteer|community.?center|library|daycare|preschool|camp\b",
        "fitness_recreation":  r"yoga\b|pilates|martial.?art|boxing|crossfit|\bswim\b|dance.?studio|\bgym\b|fitness.?(?:center|studio)|recreation|bowling|golf|skating",
        "portfolio":           r"portfolio|agency|freelanc|creative",
        "health":              r"health|medical|clinic|wellness|fitness|hospital",
        "education":           r"education|school|course|learning|training|coaching|tutor(?:ing)?",
        "realestate":          r"real.?estate|property|housing|realtor",
        "logistics":           r"logistics|shipping|delivery|transport|courier",
        "hospitality":         r"hospitality|hotel|travel|tourism|resort|airbnb",
        "automotive":          r"\bauto\b|\bcar\b|vehicle|dealer|motor",
        "entertainment":       r"entertainment|gaming|\bmusic\b|concert|conference|event",
        "legal":               r"legal|\blaw\b|attorney|consulting",
        "ecommerce":           r"\bshop\b|\bstore\b|\bproduct\b|ecommerce|retail|boutique",
    }

    # All 22 canonical styles from STYLE_THEMES_REFERENCE.md
    # Keys match builder_agent.py normalization: style_name.lower().replace(" ", "_")
    STYLE_KEYWORDS = {
        "modern_minimalist": r"\bmodern\b|\bminimalist\b|\bminimal\b|\bclean\b|\bsleek\b",
        "glassmorphism": r"\bglass(?:morphism)?\b|\bfrosted\b|\btranslucent\b",
        "retro_vintage": r"\bretro\b|\bvintage\b|\b70s\b|\b80s\b|\b90s\b|\bnostalgic\b",
        "neubrutalism": r"\bneubrutalis[mt]\b|\bbrutalist\b|\bneu.?brutal\b",
        "claymorphism": r"\bclaymorphi(?:sm)?\b|\bclay\b|\bplayful.?3d\b",
        "aurora_gradient": r"\baurora\b|\bliquid.?gradient\b|\bnorthern.?lights\b",
        "monochrome_dark": r"\bmonochrome\b|\bdark.?mode\b|\bnoir\b|\bdark.?sleek\b",
        "elegant_luxury": r"\belegant\b|\bluxury\b|\bpremium\b|\bsophisticated\b|\bupscale\b",
        "organic_natural": r"\borganic\b|\bnatural\b|\bearth\b|\beco\b|\brustic\b",
        "corporate_professional": r"\bcorporate\b|\bprofessional\b|\benterprise\b|\bformal\b",
        "bold_editorial": r"\beditorial\b|\bmagazine\b|\bnewspaper\b|\bbold.?layout\b",
        "cyberpunk_neon": r"\bcyberpunk\b|\bneon\b|\bsci.?fi\b|\bfuturistic\b",
        "pastel_soft": r"\bpastel\b|\bsoft\b|\bgentle\b|\bcalm\b|\bairy\b",
        "scandinavian_clean": r"\bscandinavian\b|\bnordic\b|\bhygge\b",
        "art_deco_geometric": r"\bart.?deco\b|\bgatsby\b|\b1920\b|\bgeometric\b",
        "tropical_vibrant": r"\btropical\b|\bvibrant\b|\bbeach\b|\bparadise\b",
        "dark_academia": r"\bdark.?academia\b|\bscholarly\b|\bliterary\b|\bbookish\b",
        "memphis_design": r"\bmemphis\b|\bsquiggle\b|\babstract.?shape\b",
        "zen_japanese": r"\bzen\b|\bjapanese\b|\bwabi.?sabi\b|\btranquil\b|\bserene\b",
        "industrial_grunge": r"\bindustrial\b|\bgrunge\b|\bwarehouse\b|\braw.?urban\b",
        "y2k_retro-futurism": r"\by2k\b|\b2000s\b|\bchrome\b|\biridescent\b|\bretro.?future\b",
        "bohemian_eclectic": r"\bbohemian\b|\bboho\b|\beclectic\b|\bartisan\b",
    }

    COMPONENT_KEYWORDS = {
        "button": r"\bbutton\b|\bcta\b",
        "image": r"\bimage\b|\bphoto\b|\bpicture\b",
        "badge": r"\bbadge\b|\btag\b|\blabel\b",
        "icon": r"\bicon\b",
        "card": r"\bcard\b",
        "form": r"\bform\b|\binput\b|\bfield\b",
        "video": r"\bvideo\b",
        "accordion": r"\baccordion\b|\bfaq\b",
        "carousel": r"\bcarousel\b|\bslider\b|\bslideshow\b",
        "tabs": r"\btabs?\b",
        "ticker": r"\bticker\b|\bscrolling\b|\bmarquee\b",
    }

    def analyze(self, query: str) -> QueryIntent:
        q = query.lower().strip()

        # Classify intent
        action = "create_section"  # default
        for intent_name, pattern in self.INTENT_RULES:
            if re.search(pattern, q):
                action = intent_name
                break

        # Extract filters
        section_matches = self._match_all(q, self.SECTION_KEYWORDS)
        section = section_matches[0] if section_matches else None
        industry = self._match_first(q, self.INDUSTRY_KEYWORDS)
        style = self._match_first(q, self.STYLE_KEYWORDS)
        style_keywords = self._extract_style_keywords(q)
        color_keywords = self._extract_color_keywords(q)

        # Hard-assign default style when industry is known but no style specified
        if not style and industry:
            from rag.config import INDUSTRY_DEFAULT_STYLE
            style = INDUSTRY_DEFAULT_STYLE.get(industry)
        components = [
            name for name, pat in self.COMPONENT_KEYWORDS.items()
            if re.search(pat, q)
        ]
        content_volume = self._match_content_volume(q)
        tone = self._match_tone(q)
        intent_axis = self._match_intent_axis(q)
        interactivity = self._match_interactivity(q)

        # Decompose complex create_page queries (and inject any extra sections
        # that the multi-match found but the regex decomposition missed).
        sub_queries = self._decompose(q, action, extra_sections=section_matches[1:])

        return QueryIntent(
            action=action,
            section_filter=section,
            industry_filter=industry,
            style_filter=style,
            style_keywords=style_keywords,
            color_keywords=color_keywords,
            component_filter=components,
            content_volume_filter=content_volume,
            tone_filter=tone,
            intent_filter=intent_axis,
            interactivity_filter=interactivity,
            sub_queries=sub_queries,
            section_filters=section_matches,
        )

    @staticmethod
    def _match_tone(text: str) -> str | None:
        if re.search(r"\b(formal|professional|corporate|polished|serious)\b", text):
            return "formal"
        if re.search(r"\b(casual|friendly|approachable|laid.?back|chill)\b", text):
            return "casual"
        if re.search(r"\b(playful|fun|whimsical|quirky|energetic|cheeky)\b", text):
            return "playful"
        return None

    @staticmethod
    def _match_intent_axis(text: str) -> str | None:
        if re.search(r"\b(lead.?gen|capture.?lead|sign.?up|subscribe|book.?(now|a.?demo)|contact.?us|enquir(y|e))\b", text):
            return "lead"
        if re.search(r"\b(purchase|buy|checkout|order|add.?to.?cart|sales?)\b", text):
            return "purchase"
        if re.search(r"\b(trust|credibility|social.?proof|reviews?|testimonial|reassur)\b", text):
            return "trust"
        if re.search(r"\b(engage|engagement|interact(ive)?|browse|discover|explore)\b", text):
            return "engagement"
        if re.search(r"\b(awareness|landing|introduce|launch|announce)\b", text):
            return "awareness"
        return None

    @staticmethod
    def _match_interactivity(text: str) -> str | None:
        if re.search(r"\b(form|input|enquiry|contact.?form|signup|sign.?up.?form)\b", text):
            return "form"
        if re.search(r"\b(carousel|slider|slideshow|swipe)\b", text):
            return "carousel"
        if re.search(r"\b(tabs|tabbed)\b", text):
            return "tabs"
        if re.search(r"\b(accordion|collapsible|expandable|faq)\b", text):
            return "accordion"
        if re.search(r"\b(video|background.?video|hero.?video)\b", text):
            return "video"
        return None

    @staticmethod
    def _match_content_volume(text: str) -> str | None:
        """Detect content-volume hints in the query.

        Soft signal — None means "no preference" so the retrieval filter is
        applied as a soft prefer rather than a hard filter.
        """
        rich_pat = r"\b(detailed|comprehensive|in.?depth|content.?rich|info.?dense|long.?form|extensive|multi.?section)\b"
        light_pat = r"\b(minimal|simple|sparse|terse|barebones|short|brief|stripped.?down|skeletal)\b"
        if re.search(rich_pat, text):
            return "rich"
        if re.search(light_pat, text):
            return "light"
        return None

    @staticmethod
    def _extract_color_keywords(text: str) -> str:
        """Extract all color words/hex codes found in the query as comma-separated string."""
        found = []
        for m in COLOR_PATTERN.finditer(text):
            word = m.group(0).strip()
            if word and word not in found:
                found.append(word)
        return ", ".join(found)

    def _extract_style_keywords(self, text: str) -> str:
        """Extract all style-related words found in the query as comma-separated string."""
        found = []
        for _name, pattern in self.STYLE_KEYWORDS.items():
            for m in re.finditer(pattern, text):
                word = m.group(0).strip()
                if word and word not in found:
                    found.append(word)
        return ", ".join(found)

    def _match_first(self, text: str, patterns: dict) -> str | None:
        for name, pat in patterns.items():
            if re.search(pat, text):
                return name
        return None

    def _match_all(self, text: str, patterns: dict) -> list[str]:
        """Return all keyword names whose pattern matches the text (order preserved)."""
        return [name for name, pat in patterns.items() if re.search(pat, text)]

    # Catches "with X, Y, and Z" / "containing X and Y" / "including X, Y, Z" /
    # "page that has X, Y, and Z" — the patterns most users actually type.
    _SECTION_LIST_PATTERNS = (
        r"\bwith\s+(.+)",
        r"\bcontaining\s+(.+)",
        r"\bincluding\s+(.+)",
        r"\bthat\s+(?:has|have|includes?|contains?)\s+(.+)",
        r"\b(?:that\s+)?features?\s+(.+)",
    )

    def _decompose(self, query: str, action: str, extra_sections: list[str] | None = None) -> list[str]:
        """Split complex queries into sub-queries for parallel retrieval.

        For ``create_page`` we look for a list of sections in the user message.
        Patterns covered: "with X, Y, and Z", "containing X and Y",
        "including X, Y, Z", "page that has X, Y, and Z".
        ``extra_sections`` are section_type names already detected by the
        multi-match SECTION_KEYWORDS pass — used as a safety net so we never
        miss a known section type even if the regex decomposition fails.
        """
        if action != "create_page":
            return [query]

        sections: list[str] = []
        for pat in self._SECTION_LIST_PATTERNS:
            m = re.search(pat, query)
            if not m:
                continue
            parts_text = m.group(1)
            parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", parts_text)
            sections = [p.strip() for p in parts if p.strip()]
            if len(sections) > 1:
                break

        # Fall back to multi-matched section keywords if the natural-language
        # split didn't produce ≥2 entries.
        if len(sections) < 2 and extra_sections:
            sections = list(dict.fromkeys(extra_sections))  # de-dup, preserve order

        if len(sections) > 1:
            return [f"{s} section template" for s in sections]
        return [query]
