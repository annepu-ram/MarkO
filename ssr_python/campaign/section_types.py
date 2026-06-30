"""Section type catalog for content-fit and AI section drafting."""

SECTION_TYPES = [
    {
        "key": "hero",
        "label": "Hero",
        "suggested_categories": ["headline", "subheadline", "tagline", "value_proposition", "cta"],
    },
    {
        "key": "features",
        "label": "Features",
        "suggested_categories": ["benefit", "product_feature"],
    },
    {
        "key": "pricing",
        "label": "Pricing",
        "suggested_categories": ["offer", "promotion", "comparison", "guarantee", "cta"],
    },
    {
        "key": "testimonials",
        "label": "Testimonials",
        "suggested_categories": ["testimonial", "case_study", "proof"],
    },
    {
        "key": "faq",
        "label": "FAQ",
        "suggested_categories": ["faq", "objection"],
    },
    {
        "key": "cta",
        "label": "CTA",
        "suggested_categories": ["cta", "headline", "offer", "announcement"],
    },
    {
        "key": "about",
        "label": "About",
        "suggested_categories": ["about", "boilerplate", "value_proposition"],
    },
    {
        "key": "offer",
        "label": "Offer",
        "suggested_categories": ["offer", "promotion", "guarantee", "announcement", "cta"],
    },
    {
        "key": "products",
        "label": "Products",
        "suggested_categories": ["product_feature", "product_spec", "comparison"],
    },
    {
        "key": "value_prop",
        "label": "Value proposition",
        "suggested_categories": ["value_proposition", "benefit"],
    },
    {
        "key": "stats",
        "label": "Stats",
        "suggested_categories": ["proof"],
    },
    {
        "key": "footer",
        "label": "Footer",
        "suggested_categories": [],
    },
    {
        "key": "custom",
        "label": "Custom",
        "suggested_categories": [],
    },
]

_SECTION_TYPE_MAP = {item["key"]: item for item in SECTION_TYPES}

_CATEGORY_TO_SECTION_TYPE = {}
for section_type in SECTION_TYPES:
    for category in section_type["suggested_categories"]:
        _CATEGORY_TO_SECTION_TYPE.setdefault(category, section_type["key"])


def valid_section_type_keys():
    return frozenset(_SECTION_TYPE_MAP.keys())


def is_valid_section_type(key):
    return key in _SECTION_TYPE_MAP


def normalize_section_type(key):
    key = (key or "custom").strip()
    return key if is_valid_section_type(key) else "custom"


def section_type_label(key):
    return _SECTION_TYPE_MAP[normalize_section_type(key)]["label"]


def suggested_categories(key):
    return list(_SECTION_TYPE_MAP[normalize_section_type(key)]["suggested_categories"])


def section_type_for_category(category):
    return _CATEGORY_TO_SECTION_TYPE.get((category or "").strip(), "custom")


def serializable_section_types():
    return [
        {
            "key": item["key"],
            "label": item["label"],
            "suggested_categories": list(item["suggested_categories"]),
        }
        for item in SECTION_TYPES
    ]
