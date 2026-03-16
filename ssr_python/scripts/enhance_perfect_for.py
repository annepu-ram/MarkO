"""Batch-update '# Perfect for:' lines in example_templates with specific business names.

Replaces abstract industry terms (e.g., 'ecommerce', 'health') with concrete business/service
names users would actually type (e.g., 'online store', 'dental clinic').
"""
import re
from pathlib import Path

# Map abstract terms → concrete business names
TERM_REPLACEMENTS = {
    # Ecommerce / Retail
    "ecommerce": "online store",
    "retail": "boutique",
    "shop": "gift shop",
    "marketplace": "online marketplace",
    "consumer goods": "consumer products store",
    "wholesale": "wholesale supplier",
    "department store": "department store",

    # Tech / SaaS
    "SaaS": "SaaS platform",
    "software": "software company",
    "startup": "tech startup",
    "tech": "technology company",
    "platform": "digital platform",
    "cloud services": "cloud hosting provider",
    "B2B": "B2B service provider",
    "enterprise": "enterprise solution",
    "analytics": "analytics dashboard",
    "fintech": "fintech app",
    "web3": "web3 platform",

    # Professional Services
    "consulting": "consulting firm",
    "legal": "law firm",
    "law": "law office",
    "agency": "digital agency",
    "professional services": "accounting firm",
    "corporate": "corporate office",
    "accounting": "accounting practice",
    "finance": "financial advisor",
    "insurance": "insurance agency",

    # Education
    "education": "tutoring center",
    "school": "private school",
    "course": "online course platform",
    "training center": "training center",
    "university": "university",

    # Health / Wellness
    "health": "medical clinic",
    "wellness": "wellness center",
    "fitness": "gym",
    "healthcare": "healthcare provider",

    # Food / Hospitality
    "restaurant": "restaurant",
    "food": "food truck",
    "bakery": "bakery",
    "cafe": "coffee shop",
    "hospitality": "resort",
    "hotel": "hotel",
    "travel": "travel agency",
    "tourism": "tour operator",

    # Creative
    "portfolio": "design portfolio",
    "creative": "creative studio",
    "design studio": "design studio",
    "photography": "photography studio",
    "entertainment": "entertainment venue",
    "music": "music studio",
    "event": "event planner",

    # Real Estate
    "real estate": "real estate agency",
    "property": "property listing",

    # Automotive
    "auto": "auto dealership",
    "automotive": "car dealership",

    # Logistics
    "logistics": "logistics company",
    "shipping": "shipping service",
    "delivery": "delivery service",

    # Other
    "blog": "blog",
    "newsletter": "newsletter",
    "media": "media company",
    "publishing": "publishing house",
    "community": "community organization",
    "freelance": "freelancer",
    "freelancer": "freelancer",
}

# Category-specific business name sets (override generic replacements)
CATEGORY_BUSINESSES = {
    "hero": [
        "SaaS platform", "online store", "digital agency", "law firm", "consulting firm",
        "dental clinic", "real estate agency", "restaurant", "gym", "photography studio",
        "tech startup", "hotel", "travel agency", "car dealership", "tutoring center",
        "coffee shop", "architecture firm", "event planner", "wellness spa", "bakery"
    ],
    "pricing_plan_cards": [
        "SaaS platform", "cloud hosting provider", "software company", "digital agency",
        "consulting firm", "online course platform", "subscription box service",
        "project management tool", "CRM platform", "email marketing service",
        "web hosting company", "freelancer", "design studio", "accounting firm"
    ],
    "product_cards": [
        "online store", "fashion boutique", "electronics shop", "furniture store",
        "beauty products shop", "sports equipment store", "jewelry store",
        "pet supplies shop", "grocery delivery", "home decor store",
        "subscription box service", "organic food store", "sneaker shop"
    ],
    "review_testimonial_cards": [
        "SaaS platform", "consulting firm", "dental clinic", "auto dealership",
        "online store", "restaurant", "law firm", "real estate agency",
        "fitness studio", "software company", "hotel", "medical clinic"
    ],
    "portfolio_showcase_cards": [
        "design portfolio", "creative studio", "digital agency", "architecture firm",
        "photography studio", "web developer", "interior designer", "video production company",
        "branding agency", "tech startup", "consulting firm", "freelance designer"
    ],
    "story_blog_cards": [
        "tech blog", "wellness blog", "travel blog", "food blog",
        "digital agency", "educational platform", "news outlet", "creative studio",
        "consulting firm", "photography studio", "health clinic blog", "podcast"
    ],
    "navigation_footer": [
        "SaaS platform", "online store", "digital agency", "consulting firm",
        "university website", "hotel chain", "real estate portal", "news portal",
        "fashion brand", "software company", "restaurant chain", "marketplace"
    ],
    "dashboard_data_cards": [
        "SaaS dashboard", "analytics platform", "fintech app", "CRM system",
        "project management tool", "admin panel", "e-learning platform",
        "inventory management", "HR software", "marketing dashboard"
    ],
    "features_benefits": [
        "SaaS platform", "mobile app", "software company", "online store",
        "consulting firm", "logistics company", "tutoring center", "dental clinic",
        "gym", "digital agency", "cloud hosting provider", "B2B service"
    ],
    "faq_section": [
        "SaaS platform", "online store", "consulting firm", "dental clinic",
        "law firm", "tutoring center", "real estate agency", "insurance company",
        "software company", "subscription service"
    ],
    "contact_section": [
        "consulting firm", "law firm", "dental clinic", "real estate agency",
        "digital agency", "photography studio", "architecture firm",
        "accounting firm", "tutoring center", "wellness center"
    ],
    "banner_announcement": [
        "online store", "SaaS platform", "fashion brand", "tech startup",
        "restaurant", "event venue", "hotel", "university website"
    ],
    "cta_banners": [
        "SaaS platform", "mobile app", "online store", "software company",
        "fitness app", "online course platform", "subscription service",
        "B2B platform", "consulting firm", "digital agency"
    ],
    "ticker": [
        "online store", "SaaS platform", "news portal", "digital agency",
        "fashion brand", "tech startup", "restaurant chain", "event planner",
        "creative studio", "consulting firm"
    ],
    "badge": [
        "online store", "SaaS platform", "software company", "consulting firm",
        "law firm", "tech startup", "digital agency", "tutoring center"
    ],
    "countdown": [
        "online store", "event planner", "conference website", "SaaS platform",
        "fashion brand", "tech startup", "restaurant", "fitness studio"
    ],
    "counter-up": [
        "consulting firm", "SaaS platform", "nonprofit organization", "tech startup",
        "real estate agency", "digital agency", "university website", "law firm"
    ],
    "icon": [
        "SaaS platform", "consulting firm", "digital agency", "real estate agency",
        "dental clinic", "law firm", "tech startup", "tutoring center"
    ],
    "progress-bar": [
        "SaaS dashboard", "project management tool", "freelance portfolio",
        "tech startup", "digital agency", "software company", "consulting firm"
    ],
    "rating": [
        "restaurant", "online store", "hotel", "dental clinic", "salon",
        "auto dealership", "tutoring center", "fitness studio"
    ],
    "panorama-display": [
        "real estate agency", "hotel", "travel agency", "architecture firm",
        "event venue", "restaurant", "resort", "museum", "shopping mall"
    ],
    "team_about": [
        "digital agency", "tech startup", "consulting firm", "law firm",
        "restaurant", "bakery", "creative studio", "architecture firm",
        "dental clinic", "accounting firm"
    ],
    "schedule": [
        "dental clinic", "salon", "barbershop", "yoga studio", "fitness studio",
        "conference", "workshop", "tutoring center", "cooking class", "music school"
    ],
    "titlebar": [
        "consulting firm", "law firm", "online store", "fashion brand",
        "photography studio", "design portfolio", "creative studio", "wellness spa"
    ],
    "styles": [
        "SaaS platform", "creative portfolio", "fashion brand", "design studio",
        "tech startup", "luxury brand", "photography studio", "music platform"
    ],
}


def enhance_perfect_for_line(line: str, category: str) -> str:
    """Replace abstract terms with concrete business names in a Perfect for line."""
    prefix = "# Perfect for: "
    if not line.strip().startswith(prefix):
        return line

    # Get the current terms
    content = line.strip()[len(prefix):]

    # Check if already using specific business names (slash-grouped format or specific terms)
    # Some hero templates already have good format like "SaaS/software/startup/tech"
    # We'll still enhance these

    # Split terms (handle both comma-separated and slash-grouped)
    if "/" in content:
        # Slash-grouped format: "SaaS/software/startup/tech, portfolio/agency/creative"
        groups = [g.strip() for g in content.split(",")]
        terms = []
        for group in groups:
            terms.extend([t.strip() for t in group.split("/")])
    else:
        terms = [t.strip() for t in content.split(",")]

    # Build new terms: use category-specific businesses if available
    if category in CATEGORY_BUSINESSES:
        new_terms = CATEGORY_BUSINESSES[category]
    else:
        # Fallback: replace individual terms
        new_terms = []
        seen = set()
        for term in terms:
            replacement = TERM_REPLACEMENTS.get(term, term)
            if replacement not in seen:
                seen.add(replacement)
                new_terms.append(replacement)

    # Cap at 10 terms
    new_terms = new_terms[:10]
    indent = line[:len(line) - len(line.lstrip())]
    return f"{indent}{prefix}{', '.join(new_terms)}\n"


def get_category(filepath: Path) -> str:
    """Get category from parent folder name."""
    parent = filepath.parent.name
    if parent == "example_templates":
        return "uncategorized"
    return parent


def process_file(filepath: Path) -> bool:
    """Update Perfect for line in a single file. Returns True if modified."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return False

    lines = content.splitlines(keepends=True)
    category = get_category(filepath)
    modified = False

    for i, line in enumerate(lines):
        if line.strip().startswith("# Perfect for:"):
            new_line = enhance_perfect_for_line(line, category)
            if new_line != line:
                lines[i] = new_line
                modified = True
            break  # Only first Perfect for line

    if modified:
        filepath.write_text("".join(lines), encoding="utf-8")

    return modified


def main():
    templates_dir = Path(__file__).parent.parent.parent / "example_templates"
    if not templates_dir.exists():
        print(f"Templates dir not found: {templates_dir}")
        return

    yaml_files = sorted(templates_dir.rglob("*.yaml"))
    modified_count = 0
    skipped_count = 0

    for f in yaml_files:
        if process_file(f):
            modified_count += 1
            print(f"  Updated: {f.relative_to(templates_dir)}")
        else:
            skipped_count += 1

    print(f"\nDone: {modified_count} files updated, {skipped_count} unchanged")


if __name__ == "__main__":
    main()
