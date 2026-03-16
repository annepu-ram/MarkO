"""ssr_python/rag/agent/query_analyzer.py — Rule-based intent classification."""
import re
from dataclasses import dataclass, field


@dataclass
class QueryIntent:
    action: str            # create_page | create_section | modify | add | explain
    section_filter: str | None     # hero | pricing | footer | ...
    industry_filter: str | None    # saas | restaurant | ...
    style_filter: str | None = None  # glassmorphism | modern | retro | ...
    component_filter: list[str] = field(default_factory=list)
    sub_queries: list[str] = field(default_factory=list)


class QueryAnalyzer:
    """Rule-based intent classification with metadata filter extraction."""

    # Intent patterns ordered by specificity (first match wins)
    INTENT_RULES = [
        ("create_page",    r"(create|build|make|generate|design)\b.*(page|website|site|landing)"),
        ("create_section", r"(create|build|make|generate|add|design)\b.*(section|hero|pricing|footer|header|testimonial|faq|cta|features?)"),
        ("modify",         r"(change|update|modify|edit|replace|adjust|fix|set|make it)\b"),
        ("add",            r"(add|insert|include|put|append)\b.*(button|image|text|icon|badge|card|link)"),
        ("explain",        r"(what|how|explain|tell me|describe|show me|list|which)\b"),
    ]

    SECTION_KEYWORDS = {
        "hero": r"\bhero\b|banner|splash|above.?fold",
        "pricing": r"\bpricing\b|plans?\b|tiers?\b",
        "testimonial": r"\btestimonial\b|reviews?\b|social.?proof",
        "footer": r"\bfooter\b",
        "features": r"\bfeatures?\b|benefits?\b",
        "cta": r"\bcta\b|call.?to.?action|sign.?up",
        "faq": r"\bfaq\b|questions?\b",
        "contact": r"\bcontact\b",
        "navigation": r"\bheader\b|\bnav\b|navigation|titlebar|menu",
        "product": r"\bproduct\b|catalog",
        "team": r"\bteam\b|staff|members?\b",
        "gallery": r"\bgallery\b|showcase|portfolio",
        "blog": r"\bblog\b|article|post",
        "stats": r"\bstats?\b|numbers?\b|counter|metric",
        "schedule": r"\bschedule\b|timetable|agenda|appointment",
        "social_links": r"\bsocial.?link\b|\bsocial.?media\b",
        "banner": r"\bbanner\b|\bannouncement\b",
        "countdown": r"\bcountdown\b|timer",
        "ticker": r"\bticker\b|scrolling|marquee",
        "dashboard": r"\bdashboard\b|data.?card",
    }

    INDUSTRY_KEYWORDS = {
        "saas": r"\bsaas\b|software|app\b|platform|startup|tech",
        "restaurant": r"restaurant|food|menu|bakery|cafe|coffee|pizza",
        "ecommerce": r"shop|store|product|ecommerce|retail",
        "portfolio": r"portfolio|agency|freelanc|creative",
        "health": r"health|medical|clinic|wellness|fitness|gym",
        "education": r"education|school|course|learning|training",
        "realestate": r"real.?estate|property|housing",
        "logistics": r"logistics|shipping|delivery|transport",
    }

    STYLE_KEYWORDS = {
        "glassmorphism": r"\bglass(?:morphism)?\b|\bfrosted\b",
        "modern": r"\bmodern\b|\bminimalist\b|\bminimal\b",
        "retro": r"\bretro\b|\bvintage\b|\b70s\b|\b80s\b|\b90s\b",
        "neubrutalism": r"\bneubrutalis[mt]\b|\bbrutalist\b|\bneu.?brutal\b",
        "claymorphism": r"\bclaymorphi(?:sm)?\b|\bclay\b",
        "aurora": r"\baurora\b|\bliquid.?gradient\b",
        "monochrome": r"\bmonochrome\b|\bdark.?mode\b|\bnoir\b",
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
        section = self._match_first(q, self.SECTION_KEYWORDS)
        industry = self._match_first(q, self.INDUSTRY_KEYWORDS)
        style = self._match_first(q, self.STYLE_KEYWORDS)
        components = [
            name for name, pat in self.COMPONENT_KEYWORDS.items()
            if re.search(pat, q)
        ]

        # Decompose complex create_page queries
        sub_queries = self._decompose(q, action)

        return QueryIntent(
            action=action,
            section_filter=section,
            industry_filter=industry,
            style_filter=style,
            component_filter=components,
            sub_queries=sub_queries,
        )

    def _match_first(self, text: str, patterns: dict) -> str | None:
        for name, pat in patterns.items():
            if re.search(pat, text):
                return name
        return None

    def _decompose(self, query: str, action: str) -> list[str]:
        """Split complex queries into sub-queries for parallel retrieval."""
        if action != "create_page":
            return [query]

        # Look for enumerated sections: "with hero, pricing, and testimonials"
        match = re.search(r"with\s+(.+)", query)
        if not match:
            return [query]

        parts_text = match.group(1)
        parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", parts_text)
        sections = [p.strip() for p in parts if p.strip()]

        if len(sections) > 1:
            return [f"{s} section template" for s in sections]
        return [query]
