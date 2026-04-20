"""
ssr_python/rag/industry_defaults.py
───────────────────────────────────
Git-tracked seed data for the guided chat flow.

This file is the *source of truth* for the default `IndustryConfig` rows.
On first app startup (or whenever the `industry_configs` table is empty),
`rag/scripts/seed_industry_config.py` upserts these dicts into DB rows keyed
by `config_key`:

    industries       → INDUSTRY_REGISTRY
    section_questions → SECTION_QUESTIONS
    recommendations  → {"section_pairs": SECTION_RECOMMENDATIONS,
                        "category_flows": CATEGORY_FLOWS}
    page_purposes    → PAGE_PURPOSES

At runtime the `/api/chat/industry-config` endpoint reads from DB; this
module is used only as a fallback (and as the seed source).

The INDUSTRY_REGISTRY is hand-curated from `website_example_outlines/` and
aligned with the industry keywords in `rag/agent/query_analyzer.py`. To
regenerate / extend from outlines, run:

    python -m rag.scripts.extract_industry_config

which parses every `website_example_outlines/**/*.md` and prints a Python
dict you can merge back into this file.
"""
from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
# PAGE PURPOSES — cross-industry page intents
# ─────────────────────────────────────────────────────────────────────────────
# Surfaces in Step 3 of the guided flow alongside industry variants, so users
# whose goal doesn't map cleanly onto a variant (e.g. "I just want a landing
# page for a promo") have an escape hatch.
PAGE_PURPOSES: list[dict] = [
    {
        "id": "promote_business",
        "label": "Promote My Business",
        "description": "General business website to attract customers",
    },
    {
        "id": "launch_product",
        "label": "Launch a Product",
        "description": "Showcase and sell a new product or collection",
    },
    {
        "id": "promote_event",
        "label": "Promote an Event",
        "description": "Event page with schedule, tickets, registration",
    },
    {
        "id": "new_store_opening",
        "label": "New Store / Location Opening",
        "description": "Announce a new physical location",
    },
    {
        "id": "new_batch_enrollment",
        "label": "New Batch / Course Enrollment",
        "description": "Promote enrollment for a new class, batch, or program",
    },
    {
        "id": "portfolio_showcase",
        "label": "Portfolio / Showcase",
        "description": "Display work, projects, or portfolio",
    },
    {
        "id": "hiring_careers",
        "label": "Hiring / Careers Page",
        "description": "Attract job applicants",
    },
    {
        "id": "seasonal_promotion",
        "label": "Seasonal Sale / Promotion",
        "description": "Limited-time offers, flash sales, seasonal campaigns",
    },
    {
        "id": "flash_sale",
        "label": "Flash Sale / Limited-Time Offer",
        "description": "Urgency-driven landing page with countdown and featured deals",
    },
    {
        "id": "book_reading",
        "label": "Book Reading / Author Meet",
        "description": "In-store or venue event with an author reading, Q&A, and signing",
    },
    {
        "id": "workshop_webinar",
        "label": "Workshop / Webinar / Masterclass",
        "description": "Promote a paid or free learning session with signup form",
    },
    {
        "id": "popup_shop",
        "label": "Pop-up Shop / Pop-up Event",
        "description": "Temporary retail experience with dates, location, and featured products",
    },
    {
        "id": "anniversary_milestone",
        "label": "Anniversary / Milestone Celebration",
        "description": "Celebrate a business milestone with a story, stats, and thank-you offer",
    },
    {
        "id": "pre_launch_coming_soon",
        "label": "Coming Soon / Pre-Launch",
        "description": "Teaser page with countdown and waitlist signup before a launch",
    },
    {
        "id": "holiday_campaign",
        "label": "Holiday / Seasonal Campaign",
        "description": "Holiday-themed page for gift guides, festive menus, or holiday hours",
    },
    {
        "id": "rebrand_announcement",
        "label": "Rebrand / Relaunch Announcement",
        "description": "Announce a new identity, name, or direction for an existing business",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# INDUSTRY REGISTRY — industry → variants → recommended sections
# ─────────────────────────────────────────────────────────────────────────────
# Keys match `rag/agent/query_analyzer.py` INDUSTRY_KEYWORDS so that when the
# analyzer classifies a query, the guided flow can look up the matching entry.
#
# Each variant's `sections` list names the section types (NOT component names).
# Section types must be keys in SECTION_QUESTIONS below so the wizard can render
# content-capture forms for them. New section types require a companion entry
# in SECTION_QUESTIONS.
#
# `source_outline` points back to the source markdown file so the outline text
# can be surfaced as additional context (e.g. example patterns, real sites).
INDUSTRY_REGISTRY: dict[str, dict] = {
    # ── SERVICES ──────────────────────────────────────────────────────────
    "restaurant": {
        "label": "Restaurant / Food & Beverage",
        "category": "services",
        "source_outline": "services/04_food_beverage.md",
        "variants": [
            {
                "id": "restaurant_dinein",
                "label": "Restaurant / Dine-In",
                "description": "Full-service restaurant with reservations and menu showcase",
                "purpose": "Showcase menu, take reservations, tell your story",
                "sections": ["navigation", "hero", "menu", "about", "gallery", "stats", "testimonials", "reservation", "contact", "footer"],
            },
            {
                "id": "restaurant_homebaker",
                "label": "Home Baker / Cake Artist",
                "description": "Personal bakery brand with custom orders and delivery",
                "purpose": "Showcase creations, take custom orders, build personal brand",
                "sections": ["navigation", "hero", "products", "about", "gallery", "testimonials", "stats", "order_form", "contact", "footer"],
            },
            {
                "id": "restaurant_cloudkitchen",
                "label": "Cloud Kitchen / Delivery-Only",
                "description": "Delivery-focused food business with online ordering",
                "purpose": "Drive online orders, show menu, build delivery trust",
                "sections": ["navigation", "hero", "how_it_works", "menu", "stats", "testimonials", "delivery_areas", "order_form", "contact", "footer"],
            },
        ],
    },
    "food_services": {
        "label": "Catering / Food Truck / Specialty Food",
        "category": "services",
        "source_outline": "services/33_food_services.md",
        "variants": [
            {
                "id": "food_catering",
                "label": "Catering Service",
                "purpose": "Book events, showcase menus, build trust for large orders",
                "sections": ["navigation", "hero", "services", "menu", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "food_truck",
                "label": "Food Truck",
                "purpose": "Show location/schedule, menu, and booking options",
                "sections": ["navigation", "hero", "menu", "schedule", "gallery", "stats", "order_form", "contact", "footer"],
            },
            {
                "id": "food_specialty",
                "label": "Specialty Food (Brewery / Juice Bar / Ice Cream)",
                "purpose": "Showcase product range, build brand story, drive local visits",
                "sections": ["navigation", "hero", "about", "menu", "gallery", "stats", "testimonials", "contact", "footer"],
            },
        ],
    },
    "education": {
        "label": "Education / Tutoring",
        "category": "services",
        "source_outline": "services/02_education_tutoring.md",
        "variants": [
            {
                "id": "education_tutor",
                "label": "Individual Tutor / Home Tutor",
                "purpose": "Attract students, showcase results, book demo classes",
                "sections": ["navigation", "hero", "stats", "services", "features", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
            {
                "id": "education_institute",
                "label": "Coaching Institute",
                "purpose": "Enroll students, showcase toppers, promote new batches",
                "sections": ["navigation", "hero", "services", "stats", "features", "testimonials", "countdown", "faq", "order_form", "contact", "footer"],
            },
            {
                "id": "education_edtech",
                "label": "Online Learning Platform",
                "purpose": "Drive signups, showcase courses, offer free trials",
                "sections": ["navigation", "hero", "features", "services", "how_it_works", "stats", "testimonials", "pricing", "cta", "footer"],
            },
        ],
    },
    "health": {
        "label": "Healthcare / Clinic / Wellness",
        "category": "services",
        "source_outline": "services/01_healthcare_clinic.md",
        "variants": [
            {
                "id": "health_clinic",
                "label": "Doctor's Clinic / Specialty Practice",
                "purpose": "Book appointments, build trust, show credentials",
                "sections": ["navigation", "hero", "services", "about", "stats", "testimonials", "faq", "order_form", "contact", "footer"],
            },
            {
                "id": "health_hospital",
                "label": "Multi-Specialty Hospital / Diagnostic Centre",
                "purpose": "Showcase departments, specialists, and services",
                "sections": ["navigation", "hero", "services", "features", "stats", "team", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "health_wellness",
                "label": "Wellness / Therapy / Alternative Medicine",
                "purpose": "Promote holistic services, build emotional trust",
                "sections": ["navigation", "hero", "about", "services", "gallery", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "beauty": {
        "label": "Beauty / Salon / Spa",
        "category": "services",
        "source_outline": "services/11_beauty_wellness.md",
        "variants": [
            {
                "id": "beauty_salon",
                "label": "Hair Salon / Barbershop",
                "purpose": "Book appointments, showcase work, list services",
                "sections": ["navigation", "hero", "menu", "gallery", "stats", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
            {
                "id": "beauty_spa",
                "label": "Spa / Wellness Centre",
                "purpose": "Promote relaxation experience, book treatments",
                "sections": ["navigation", "hero", "menu", "about", "gallery", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
            {
                "id": "beauty_nail_brow",
                "label": "Nail / Lash / Brow Studio",
                "purpose": "Showcase intricate work, drive walk-ins and bookings",
                "sections": ["navigation", "hero", "gallery", "menu", "stats", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "fitness_recreation": {
        "label": "Fitness / Gym / Sports Coaching",
        "category": "services",
        "source_outline": "services/12_fitness.md",
        "variants": [
            {
                "id": "fitness_gym",
                "label": "Gym / Fitness Studio",
                "purpose": "Sign up members, showcase trainers and facilities",
                "sections": ["navigation", "hero", "features", "services", "team", "stats", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
            {
                "id": "fitness_coaching",
                "label": "Sports Academy / Coaching",
                "purpose": "Enroll students, showcase results, promote new batches",
                "sections": ["navigation", "hero", "services", "stats", "features", "gallery", "testimonials", "pricing", "countdown", "order_form", "contact", "footer"],
            },
            {
                "id": "fitness_studio",
                "label": "Yoga / Pilates / Dance Studio",
                "purpose": "Fill class schedules, build calm brand presence",
                "sections": ["navigation", "hero", "schedule", "services", "about", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "homeservices": {
        "label": "Home Services (Plumbing / HVAC / Handyman)",
        "category": "services",
        "source_outline": "services/07_home_services.md",
        "variants": [
            {
                "id": "home_trades",
                "label": "Plumbing / Electrical / HVAC",
                "purpose": "Drive emergency calls and service bookings",
                "sections": ["navigation", "hero", "services", "stats", "features", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "home_cleaning",
                "label": "Cleaning / Pest Control / Landscaping",
                "purpose": "Book recurring service visits",
                "sections": ["navigation", "hero", "services", "pricing", "features", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "construction": {
        "label": "Construction / Contracting",
        "category": "services",
        "source_outline": "services/31_construction.md",
        "variants": [
            {
                "id": "construction_residential",
                "label": "Residential Contractor / Renovation",
                "purpose": "Showcase completed projects, build trust, book consultations",
                "sections": ["navigation", "hero", "services", "gallery", "about", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "construction_commercial",
                "label": "Commercial Construction",
                "purpose": "Showcase scale, team, and process to win contracts",
                "sections": ["navigation", "hero", "services", "gallery", "stats", "team", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "professional_services": {
        "label": "Accounting / Legal / Insurance / Financial",
        "category": "services",
        "source_outline": "services/08_professional_services.md",
        "variants": [
            {
                "id": "prof_legal",
                "label": "Law Firm / Attorney",
                "purpose": "Generate consult leads, signal expertise and reputation",
                "sections": ["navigation", "hero", "services", "about", "stats", "testimonials", "faq", "order_form", "contact", "footer"],
            },
            {
                "id": "prof_financial",
                "label": "Accountant / Financial Advisor / Insurance",
                "purpose": "Book discovery calls, explain service areas, build credibility",
                "sections": ["navigation", "hero", "services", "features", "about", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "legal": {
        "label": "Legal Services",
        "category": "services",
        "source_outline": "services/08_professional_services.md",
        "variants": [
            {
                "id": "legal_firm",
                "label": "Law Firm / Attorney",
                "purpose": "Generate consult leads, signal expertise",
                "sections": ["navigation", "hero", "services", "about", "stats", "testimonials", "faq", "order_form", "contact", "footer"],
            },
        ],
    },
    "dental": {
        "label": "Dental Practice",
        "category": "services",
        "source_outline": "services/28_dental.md",
        "variants": [
            {
                "id": "dental_general",
                "label": "General / Family Dentist",
                "purpose": "Book appointments, reduce dentist anxiety with trust signals",
                "sections": ["navigation", "hero", "services", "about", "team", "testimonials", "stats", "order_form", "contact", "footer"],
            },
            {
                "id": "dental_specialty",
                "label": "Orthodontist / Cosmetic Dentist",
                "purpose": "Showcase before/after work, premium positioning",
                "sections": ["navigation", "hero", "services", "gallery", "team", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "realestate": {
        "label": "Real Estate",
        "category": "services",
        "source_outline": "services/13_real_estate.md",
        "variants": [
            {
                "id": "realestate_agent",
                "label": "Real Estate Agent / Broker",
                "purpose": "Generate buyer/seller leads, showcase sold listings",
                "sections": ["navigation", "hero", "services", "gallery", "about", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "realestate_developer",
                "label": "Property Developer / Builder",
                "purpose": "Sell units in a specific development",
                "sections": ["navigation", "hero", "features", "gallery", "pricing", "stats", "testimonials", "countdown", "order_form", "contact", "footer"],
            },
        ],
    },
    "hospitality": {
        "label": "Hotels / Travel / Tourism",
        "category": "services",
        "source_outline": "services/16_travel_tourism.md",
        "variants": [
            {
                "id": "hospitality_hotel",
                "label": "Hotel / Resort",
                "purpose": "Drive bookings, showcase amenities and experience",
                "sections": ["navigation", "hero", "features", "gallery", "services", "stats", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
            {
                "id": "hospitality_tour",
                "label": "Tour Operator / Travel Agency",
                "purpose": "Sell curated experiences and packages",
                "sections": ["navigation", "hero", "services", "gallery", "features", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "automotive": {
        "label": "Automotive Dealer / Service",
        "category": "services",
        "source_outline": "services/14_automotive.md",
        "variants": [
            {
                "id": "auto_dealer",
                "label": "Car Dealership",
                "purpose": "Drive test drives, showcase inventory",
                "sections": ["navigation", "hero", "products", "features", "testimonials", "stats", "order_form", "contact", "footer"],
            },
            {
                "id": "auto_service",
                "label": "Mechanic / Auto Repair",
                "purpose": "Book service appointments, build trust",
                "sections": ["navigation", "hero", "services", "pricing", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "automotive_services": {
        "label": "Mechanic / Auto Services",
        "category": "services",
        "source_outline": "services/14_automotive.md",
        "variants": [
            {
                "id": "auto_service_general",
                "label": "Auto Repair / Tire / Oil Change",
                "purpose": "Book service appointments, build trust",
                "sections": ["navigation", "hero", "services", "pricing", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "portfolio": {
        "label": "Portfolio / Creative Agency / Freelancer",
        "category": "services",
        "source_outline": "services/10_photography.md",
        "variants": [
            {
                "id": "portfolio_freelancer",
                "label": "Freelancer / Solo Creative",
                "purpose": "Showcase work, land clients",
                "sections": ["navigation", "hero", "about", "gallery", "services", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "portfolio_agency",
                "label": "Creative / Design Agency",
                "purpose": "Show case studies, team, process",
                "sections": ["navigation", "hero", "gallery", "services", "team", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "portfolio_photographer",
                "label": "Photographer / Videographer",
                "purpose": "Showcase visual portfolio, book sessions",
                "sections": ["navigation", "hero", "gallery", "services", "pricing", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "community": {
        "label": "Community / NGO / Nonprofit",
        "category": "services",
        "source_outline": "services/25_ngo_nonprofits.md",
        "variants": [
            {
                "id": "community_nonprofit",
                "label": "Nonprofit / Charity",
                "purpose": "Drive donations, volunteer signups, share impact",
                "sections": ["navigation", "hero", "about", "stats", "services", "gallery", "testimonials", "cta", "order_form", "contact", "footer"],
            },
            {
                "id": "community_religious",
                "label": "Church / Temple / Religious Centre",
                "purpose": "Share service times, community activities",
                "sections": ["navigation", "hero", "schedule", "about", "services", "gallery", "testimonials", "contact", "footer"],
            },
            {
                "id": "community_daycare",
                "label": "Daycare / Preschool / Camp",
                "purpose": "Enroll children, reassure parents with safety and care",
                "sections": ["navigation", "hero", "features", "services", "team", "gallery", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "trades": {
        "label": "Specialty Trades (Welding / Masonry / Flooring)",
        "category": "services",
        "source_outline": "services/32_trades.md",
        "variants": [
            {
                "id": "trades_specialty",
                "label": "Specialty Trade Contractor",
                "purpose": "Showcase work quality, book project consultations",
                "sections": ["navigation", "hero", "services", "gallery", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "retail_local": {
        "label": "Local Retail (Hardware / Florist / Pet Store)",
        "category": "services",
        "source_outline": "products/product_46_retail_local.md",
        "variants": [
            {
                "id": "retail_hardware",
                "label": "Hardware / Building Supplies",
                "purpose": "Drive foot traffic, show departments and services",
                "sections": ["navigation", "hero", "services", "features", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "retail_florist",
                "label": "Florist / Flower Shop",
                "purpose": "Take occasion-based orders, drive same-day delivery",
                "sections": ["navigation", "hero", "products", "gallery", "services", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "retail_petstore",
                "label": "Pet Store / Supplies",
                "purpose": "Showcase product range, promote services like grooming",
                "sections": ["navigation", "hero", "products", "services", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "logistics": {
        "label": "Logistics / Shipping / Delivery",
        "category": "services",
        "source_outline": "services/20_logistics_courier.md",
        "variants": [
            {
                "id": "logistics_courier",
                "label": "Courier / Last-Mile Delivery",
                "purpose": "Sign up businesses, show coverage area and SLAs",
                "sections": ["navigation", "hero", "services", "how_it_works", "features", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "entertainment": {
        "label": "Entertainment / Gaming / Music",
        "category": "services",
        "source_outline": "services/27_music_dance.md",
        "variants": [
            {
                "id": "entertainment_studio",
                "label": "Music / Dance Studio",
                "purpose": "Enroll students, promote upcoming events",
                "sections": ["navigation", "hero", "services", "gallery", "team", "testimonials", "pricing", "order_form", "contact", "footer"],
            },
        ],
    },
    "cafe_bakery": {
        "label": "Cafe / Bakery / Coffee Shop",
        "category": "services",
        "source_outline": None,
        "variants": [
            {
                "id": "cafe_coffee",
                "label": "Coffee Shop / Cafe",
                "description": "Neighborhood cafe with specialty drinks, light food, and cozy vibes",
                "purpose": "Drive footfall, showcase menu and ambience, take online orders",
                "sections": ["navigation", "hero", "menu", "about", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "bakery_patisserie",
                "label": "Bakery / Patisserie",
                "description": "Artisan bakery with breads, pastries, cakes, and custom orders",
                "purpose": "Showcase bakes, take custom cake orders, promote daily specials",
                "sections": ["navigation", "hero", "menu", "about", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "pharmacy": {
        "label": "Pharmacy / Drugstore",
        "category": "services",
        "source_outline": None,
        "variants": [
            {
                "id": "pharmacy_community",
                "label": "Community Pharmacy",
                "description": "Neighborhood pharmacy with prescriptions, OTC, and health services",
                "purpose": "Advertise services, build trust, drive prescription transfers",
                "sections": ["navigation", "hero", "services", "features", "about", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "pharmacy_specialty",
                "label": "Specialty / Compounding Pharmacy",
                "description": "Compounding or specialty pharmacy with custom formulations",
                "purpose": "Explain specialty offerings, earn clinician and patient trust",
                "sections": ["navigation", "hero", "services", "about", "features", "team", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "art_gallery": {
        "label": "Art Gallery / Studio",
        "category": "services",
        "source_outline": None,
        "variants": [
            {
                "id": "gallery_exhibits",
                "label": "Gallery / Exhibition Space",
                "description": "Art gallery hosting rotating exhibitions and artist events",
                "purpose": "Promote current exhibitions, drive gallery visits, grow collector base",
                "sections": ["navigation", "hero", "about", "schedule", "gallery", "team", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "art_studio",
                "label": "Working Artist Studio",
                "description": "Individual artist's studio with commissions, classes, and open studios",
                "purpose": "Showcase work, take commissions, sell classes or originals",
                "sections": ["navigation", "hero", "about", "gallery", "services", "pricing", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "photo_video": {
        "label": "Photography / Video Studio",
        "category": "services",
        "source_outline": None,
        "variants": [
            {
                "id": "photo_studio",
                "label": "Photography Studio",
                "description": "Professional photographer for weddings, portraits, or commercial work",
                "purpose": "Showcase portfolio, book sessions, explain packages",
                "sections": ["navigation", "hero", "gallery", "services", "pricing", "about", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "video_production",
                "label": "Video Production / Content Studio",
                "description": "Video and content creation studio for brands, weddings, or events",
                "purpose": "Show reels, explain production process, book projects",
                "sections": ["navigation", "hero", "gallery", "services", "how_it_works", "team", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "bar_pub": {
        "label": "Bar / Pub / Nightlife",
        "category": "services",
        "source_outline": None,
        "variants": [
            {
                "id": "bar_cocktail",
                "label": "Cocktail Bar / Lounge",
                "description": "Upscale bar with crafted cocktails, ambience, and special events",
                "purpose": "Drive reservations, promote events, showcase drink menu",
                "sections": ["navigation", "hero", "menu", "about", "gallery", "schedule", "testimonials", "reservation", "contact", "footer"],
            },
            {
                "id": "pub_gastropub",
                "label": "Pub / Gastropub / Sports Bar",
                "description": "Neighborhood pub with food, drinks, live events, or game nights",
                "purpose": "Fill tables during events, showcase menu, promote live screenings",
                "sections": ["navigation", "hero", "menu", "schedule", "gallery", "testimonials", "reservation", "contact", "footer"],
            },
        ],
    },

    # ── PRODUCTS ──────────────────────────────────────────────────────────
    "ecommerce": {
        "label": "E-commerce / Online Store",
        "category": "products",
        "source_outline": "products/03_retail_boutique.md",
        "variants": [
            {
                "id": "ecom_boutique",
                "label": "Boutique / Fashion Brand",
                "purpose": "Sell curated products with strong brand voice",
                "sections": ["navigation", "hero", "products", "features", "gallery", "testimonials", "pricing", "cta", "footer"],
            },
            {
                "id": "ecom_catalog",
                "label": "Multi-Product Catalog",
                "purpose": "Drive volume sales across many SKUs",
                "sections": ["navigation", "hero", "products", "features", "pricing", "testimonials", "faq", "cta", "footer"],
            },
            {
                "id": "ecom_single_product",
                "label": "Single-Product Landing Page",
                "purpose": "Convert visitors into buyers for one hero product",
                "sections": ["navigation", "hero", "features", "gallery", "testimonials", "stats", "pricing", "faq", "cta", "footer"],
            },
        ],
    },
    "luxury_products": {
        "label": "Luxury Products (Watches / Jewellery / Cars)",
        "category": "products",
        "source_outline": "products/product_30_luxury_watches.md",
        "variants": [
            {
                "id": "luxury_single",
                "label": "Single Luxury Brand",
                "purpose": "Build brand prestige, drive inquiries for high-ticket items",
                "sections": ["navigation", "hero", "about", "products", "gallery", "features", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    # SaaS / software — no direct outline, synthesized from common patterns
    "saas": {
        "label": "SaaS / Software / Startup",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "saas_product",
                "label": "SaaS Product Landing Page",
                "purpose": "Drive free trials and demo bookings",
                "sections": ["navigation", "hero", "features", "how_it_works", "stats", "testimonials", "pricing", "faq", "cta", "footer"],
            },
            {
                "id": "saas_enterprise",
                "label": "Enterprise / B2B SaaS",
                "purpose": "Generate qualified demo requests from enterprise buyers",
                "sections": ["navigation", "hero", "features", "services", "stats", "testimonials", "faq", "order_form", "contact", "footer"],
            },
        ],
    },
    "bookstore": {
        "label": "Bookstore / Book Retail",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "bookstore_indie",
                "label": "Independent Bookstore",
                "description": "Neighborhood bookshop with curated picks, events, and community vibe",
                "purpose": "Drive footfall, promote in-store events, sell featured books online",
                "sections": ["navigation", "hero", "products", "about", "gallery", "schedule", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "bookstore_chain",
                "label": "Specialty / Chain Bookstore",
                "description": "Larger bookstore with multiple genres, author events, and loyalty program",
                "purpose": "Promote bestsellers, events, memberships; drive store visits",
                "sections": ["navigation", "hero", "products", "features", "gallery", "schedule", "stats", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "apparel": {
        "label": "Apparel / Clothing Store",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "apparel_boutique",
                "label": "Clothing Boutique",
                "description": "Curated fashion brand with a strong visual identity",
                "purpose": "Showcase collections, build brand voice, drive online and in-store sales",
                "sections": ["navigation", "hero", "products", "features", "gallery", "testimonials", "pricing", "cta", "footer"],
            },
            {
                "id": "apparel_streetwear",
                "label": "Streetwear / Sneaker Brand",
                "description": "Youth-focused drop-based brand with strong cultural identity",
                "purpose": "Hype upcoming drops, sell limited-edition products, build community",
                "sections": ["navigation", "hero", "countdown", "products", "gallery", "stats", "testimonials", "cta", "footer"],
            },
            {
                "id": "apparel_formal",
                "label": "Formalwear / Bridal",
                "description": "Premium formal and bridal clothing with fittings and consultations",
                "purpose": "Book fittings, showcase collections, build trust for high-ticket purchases",
                "sections": ["navigation", "hero", "products", "about", "gallery", "services", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "grocery": {
        "label": "Grocery / Supermarket",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "grocery_local",
                "label": "Neighborhood Grocer",
                "description": "Local grocery store with weekly deals and delivery",
                "purpose": "Advertise weekly deals, drive store visits and delivery orders",
                "sections": ["navigation", "hero", "products", "features", "delivery_areas", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "grocery_organic",
                "label": "Organic / Specialty Market",
                "description": "Health-focused grocery with organic, local, or specialty products",
                "purpose": "Educate customers on quality sourcing, drive sign-ups and subscriptions",
                "sections": ["navigation", "hero", "about", "products", "features", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "electronics_retail": {
        "label": "Electronics / Gadgets",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "electronics_store",
                "label": "Electronics Store",
                "description": "Consumer electronics retailer covering TVs, laptops, appliances",
                "purpose": "Promote deals, showcase brands, drive in-store and online purchases",
                "sections": ["navigation", "hero", "products", "features", "pricing", "stats", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "electronics_mobile",
                "label": "Mobile / Accessories Shop",
                "description": "Phones, tablets, and accessories with repair services",
                "purpose": "Sell devices, promote repair services, drive trade-ins",
                "sections": ["navigation", "hero", "products", "services", "features", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "furniture_decor": {
        "label": "Furniture / Home Decor",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "furniture_store",
                "label": "Furniture Showroom",
                "description": "Living room, bedroom, and office furniture showroom with delivery",
                "purpose": "Drive showroom visits, showcase room setups, book consultations",
                "sections": ["navigation", "hero", "products", "gallery", "features", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "decor_homegoods",
                "label": "Home Goods / Decor",
                "description": "Curated home accessories, lighting, textiles, and decor",
                "purpose": "Sell curated decor items, inspire with lookbooks",
                "sections": ["navigation", "hero", "products", "gallery", "features", "testimonials", "cta", "footer"],
            },
        ],
    },
    "jewelry_store": {
        "label": "Jewelry Store",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "jewelry_fine",
                "label": "Fine Jewelry / Diamond Store",
                "description": "Premium fine jewelry with engagement and custom pieces",
                "purpose": "Book consultations, showcase collections, build brand prestige",
                "sections": ["navigation", "hero", "products", "about", "gallery", "features", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "jewelry_artisan",
                "label": "Artisan / Handmade Jewelry",
                "description": "Handcrafted, small-batch, or custom jewelry brand",
                "purpose": "Tell maker story, sell unique pieces, drive custom orders",
                "sections": ["navigation", "hero", "about", "products", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "toy_hobby": {
        "label": "Toys / Hobby / Games",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "toy_store",
                "label": "Toy / Kids Store",
                "description": "Toys, games, and kids' products for families",
                "purpose": "Promote seasonal lineups, drive in-store and online purchases",
                "sections": ["navigation", "hero", "products", "features", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "hobby_games",
                "label": "Board Games / Collectibles / Hobbies",
                "description": "Tabletop games, trading cards, models, and hobby supplies",
                "purpose": "Promote events, showcase product range, build community",
                "sections": ["navigation", "hero", "products", "schedule", "features", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },
    "sports_gear": {
        "label": "Sports Gear / Outdoor",
        "category": "products",
        "source_outline": None,
        "variants": [
            {
                "id": "sports_retail",
                "label": "Sports Equipment Store",
                "description": "Team sports, fitness gear, and athletic apparel",
                "purpose": "Sell gear, promote seasonal collections, support local teams",
                "sections": ["navigation", "hero", "products", "features", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
            {
                "id": "outdoor_gear",
                "label": "Outdoor / Adventure Gear",
                "description": "Camping, hiking, and adventure equipment retailer",
                "purpose": "Educate with guides, sell gear, build adventurer community",
                "sections": ["navigation", "hero", "products", "features", "how_it_works", "gallery", "testimonials", "order_form", "contact", "footer"],
            },
        ],
    },

    # ── EVENTS ────────────────────────────────────────────────────────────
    "event_product_launch": {
        "label": "Product Launch Event",
        "category": "events",
        "source_outline": "events/event_02_product_launch.md",
        "variants": [
            {
                "id": "event_launch",
                "label": "Product Launch",
                "purpose": "Build hype, capture signups, drive day-one attention",
                "sections": ["navigation", "hero", "countdown", "features", "gallery", "stats", "testimonials", "order_form", "footer"],
            },
        ],
    },
    "event_conference": {
        "label": "Conference / Summit",
        "category": "events",
        "source_outline": "events/event_10_summit_conference.md",
        "variants": [
            {
                "id": "event_summit",
                "label": "Industry Summit / Conference",
                "purpose": "Sell tickets, showcase speakers and agenda",
                "sections": ["navigation", "hero", "countdown", "schedule", "team", "features", "pricing", "faq", "order_form", "footer"],
            },
        ],
    },
    "event_festival": {
        "label": "Festival / Concert / Cultural Event",
        "category": "events",
        "source_outline": "events/event_03_musical_concert.md",
        "variants": [
            {
                "id": "event_concert",
                "label": "Concert / Live Music",
                "purpose": "Sell tickets, promote lineup",
                "sections": ["navigation", "hero", "countdown", "schedule", "gallery", "pricing", "faq", "order_form", "footer"],
            },
            {
                "id": "event_cultural",
                "label": "Cultural / Food / Film Festival",
                "purpose": "Drive attendance, showcase program highlights",
                "sections": ["navigation", "hero", "countdown", "schedule", "gallery", "features", "testimonials", "pricing", "order_form", "footer"],
            },
        ],
    },
    "event_wedding": {
        "label": "Wedding / Expo / Ceremony",
        "category": "events",
        "source_outline": "events/event_12_wedding_expo.md",
        "variants": [
            {
                "id": "event_wedding_expo",
                "label": "Wedding Expo / Bridal Show",
                "purpose": "Sell tickets, promote exhibitors",
                "sections": ["navigation", "hero", "countdown", "schedule", "gallery", "features", "pricing", "order_form", "footer"],
            },
            {
                "id": "event_graduation",
                "label": "Graduation / Ceremony",
                "purpose": "Share event details, RSVP",
                "sections": ["navigation", "hero", "countdown", "schedule", "gallery", "order_form", "footer"],
            },
        ],
    },
    "event_sports": {
        "label": "Sports Tournament / Marathon",
        "category": "events",
        "source_outline": "events/event_05_marathon_sports.md",
        "variants": [
            {
                "id": "event_sports",
                "label": "Sports Tournament / Marathon",
                "purpose": "Register participants, showcase categories",
                "sections": ["navigation", "hero", "countdown", "features", "schedule", "pricing", "stats", "faq", "order_form", "footer"],
            },
        ],
    },
    "event_fundraiser": {
        "label": "Gala / Fundraiser / Charity Event",
        "category": "events",
        "source_outline": "events/event_08_gala_fundraiser.md",
        "variants": [
            {
                "id": "event_gala",
                "label": "Gala / Fundraiser",
                "purpose": "Drive donations and ticket purchases",
                "sections": ["navigation", "hero", "countdown", "about", "schedule", "stats", "pricing", "testimonials", "order_form", "footer"],
            },
        ],
    },
    "event_hackathon": {
        "label": "Hackathon / Tech Event",
        "category": "events",
        "source_outline": "events/event_06_hackathon_tech.md",
        "variants": [
            {
                "id": "event_hackathon",
                "label": "Hackathon / Tech Conference",
                "purpose": "Register teams, showcase sponsors and prizes",
                "sections": ["navigation", "hero", "countdown", "features", "schedule", "pricing", "stats", "faq", "order_form", "footer"],
            },
        ],
    },
    "event_flash_sale": {
        "label": "Flash Sale / Limited-Time Offer",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_flash",
                "label": "Flash Sale Landing Page",
                "description": "Urgency-driven promo page with countdown, featured deals, and cart push",
                "purpose": "Drive conversions in a limited window with urgency and featured products",
                "sections": ["navigation", "hero", "countdown", "products", "features", "stats", "testimonials", "order_form", "footer"],
            },
        ],
    },
    "event_book_reading": {
        "label": "Book Reading / Author Meet",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_reading",
                "label": "In-Store Book Reading / Author Meet",
                "description": "Venue event with an author reading, Q&A, and signing",
                "purpose": "Invite attendees, share schedule, capture RSVPs",
                "sections": ["navigation", "hero", "countdown", "about", "schedule", "gallery", "order_form", "footer"],
            },
        ],
    },
    "event_book_launch": {
        "label": "Book Launch / Author Tour",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_book_release",
                "label": "Book Launch / Release Page",
                "description": "Promotional page for a new book release with tour dates and reviews",
                "purpose": "Build pre-orders, announce tour stops, highlight reviews",
                "sections": ["navigation", "hero", "countdown", "about", "features", "gallery", "testimonials", "order_form", "footer"],
            },
        ],
    },
    "event_workshop": {
        "label": "Workshop / Webinar / Masterclass",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_workshop_inperson",
                "label": "In-Person Workshop / Masterclass",
                "description": "Paid or free hands-on learning session at a physical venue",
                "purpose": "Explain curriculum, showcase instructor, drive signups",
                "sections": ["navigation", "hero", "countdown", "features", "schedule", "team", "pricing", "testimonials", "order_form", "footer"],
            },
            {
                "id": "event_webinar",
                "label": "Online Webinar / Virtual Class",
                "description": "Live or on-demand online learning session with signup form",
                "purpose": "Grow registrations, explain agenda and speaker credentials",
                "sections": ["navigation", "hero", "countdown", "features", "schedule", "team", "faq", "order_form", "footer"],
            },
        ],
    },
    "event_popup": {
        "label": "Pop-up Shop / Pop-up Event",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_popup_retail",
                "label": "Pop-up Shop / Experience",
                "description": "Temporary retail or brand experience with dates, location, and featured products",
                "purpose": "Drive visits during a limited window, showcase featured items",
                "sections": ["navigation", "hero", "countdown", "products", "gallery", "schedule", "order_form", "footer"],
            },
        ],
    },
    "event_anniversary": {
        "label": "Anniversary / Milestone Event",
        "category": "events",
        "source_outline": None,
        "variants": [
            {
                "id": "event_anniversary_celebration",
                "label": "Anniversary / Milestone Celebration",
                "description": "Celebrate a business milestone with story, stats, and thank-you offer",
                "purpose": "Honor a milestone, share story and stats, offer a thank-you promo",
                "sections": ["navigation", "hero", "countdown", "about", "stats", "gallery", "testimonials", "cta", "footer"],
            },
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION QUESTIONS — content fields the wizard asks for, per section type
# ─────────────────────────────────────────────────────────────────────────────
# Each entry has:
#   label        → human-readable section name shown in the UI
#   description  → one-liner explaining what the section does
#   base_fields  → list of form fields (key, label, type, placeholder)
#   industry_overrides (optional) → per-industry placeholder/label overrides
#
# `type` is one of: "text" | "textarea"
#
# Adding a new section type: add it here, then reference it in one or more
# INDUSTRY_REGISTRY variants. The guided wizard renders the fields verbatim —
# no backend changes required.
SECTION_QUESTIONS: dict[str, dict] = {
    "navigation": {
        "label": "Navigation / Header",
        "description": "Top navigation bar with logo, menu links, and primary CTA",
        "base_fields": [
            {"key": "nav_links", "label": "Navigation links (comma-separated)", "type": "text", "placeholder": "e.g., Home, About, Services, Contact"},
            {"key": "primary_cta", "label": "Primary button text (optional)", "type": "text", "placeholder": "e.g., Book Now, Sign Up"},
        ],
    },
    "hero": {
        "label": "Hero Section",
        "description": "The first thing visitors see — main headline, value prop, and primary action",
        "base_fields": [
            {"key": "tagline", "label": "Headline / Tagline", "type": "text", "placeholder": "Your main message to visitors"},
            {"key": "subtext", "label": "Supporting text", "type": "textarea", "placeholder": "1-2 sentences about what you do"},
            {"key": "cta_text", "label": "Primary button text", "type": "text", "placeholder": "e.g., Book Now, Order Online"},
            {"key": "cta2_text", "label": "Secondary button text (optional)", "type": "text", "placeholder": "e.g., Learn More, View Menu"},
        ],
        "industry_overrides": {
            "restaurant": {"cta_text": {"placeholder": "e.g., Reserve a Table, View Menu, Order Now"}},
            "education": {"cta_text": {"placeholder": "e.g., Book Free Trial, Explore Courses, Enroll Now"}},
            "health": {"cta_text": {"placeholder": "e.g., Book Appointment, Call Now"}},
            "dental": {"cta_text": {"placeholder": "e.g., Book Appointment, Request Consultation"}},
            "saas": {"cta_text": {"placeholder": "e.g., Start Free Trial, Get Started, See Demo"}},
            "ecommerce": {"cta_text": {"placeholder": "e.g., Shop Now, Browse Collection"}},
            "beauty": {"cta_text": {"placeholder": "e.g., Book Appointment, See Our Work"}},
            "fitness_recreation": {"cta_text": {"placeholder": "e.g., Start Free Trial, Join Now"}},
            "realestate": {"cta_text": {"placeholder": "e.g., Browse Listings, Book a Showing"}},
            "hospitality": {"cta_text": {"placeholder": "e.g., Book a Stay, Explore Rooms"}},
            "homeservices": {"cta_text": {"placeholder": "e.g., Get a Free Quote, Book Service"}},
        },
    },
    "about": {
        "label": "About / Our Story",
        "description": "Your story, mission, or what makes you different",
        "base_fields": [
            {"key": "story", "label": "Your story", "type": "textarea", "placeholder": "How you started, what drives you, what makes you different"},
            {"key": "since_year", "label": "Year established (optional)", "type": "text", "placeholder": "e.g., 2010"},
            {"key": "team_note", "label": "Team description (optional)", "type": "text", "placeholder": "e.g., Family-owned, 15-person team of experts"},
        ],
    },
    "features": {
        "label": "Features / Benefits",
        "description": "Key capabilities, differentiators, or benefits",
        "base_fields": [
            {"key": "features_list", "label": "Key features or benefits (3-6 items)", "type": "textarea", "placeholder": "Feature name - brief description\nOne per line"},
        ],
        "industry_overrides": {
            "saas": {"features_list": {"placeholder": "e.g., Real-time Analytics - Track metrics as they happen\nTeam Collaboration - Share dashboards with your team\nAPI Access - Integrate with your existing tools"}},
            "restaurant": {"features_list": {"placeholder": "e.g., Farm to Table - Locally sourced ingredients\nChef's Table - Private dining experience\nCatering - Events and corporate meals"}},
            "fitness_recreation": {"features_list": {"placeholder": "e.g., 24/7 Access - Train on your schedule\nPersonal Trainers - Certified experts\nGroup Classes - 50+ weekly"}},
            "health": {"features_list": {"placeholder": "e.g., Board-Certified Doctors - 20+ years experience\nSame-Day Appointments - No long waits\nInsurance Accepted - Major plans welcome"}},
        },
    },
    "services": {
        "label": "Services / What We Offer",
        "description": "A list of services, service categories, or tiers",
        "base_fields": [
            {"key": "services_list", "label": "Services or categories (3-8 items)", "type": "textarea", "placeholder": "Service name - brief description\nOne per line"},
        ],
        "industry_overrides": {
            "beauty": {"services_list": {"placeholder": "e.g., Haircut & Style - Wash, cut, and blow-dry - $45\nBalayage - Hand-painted highlights - $180\nManicure - Classic polish - $25"}},
            "homeservices": {"services_list": {"placeholder": "e.g., Emergency Plumbing - Available 24/7\nWater Heater Install - Same-day service\nDrain Cleaning - Starting at $99"}},
            "education": {"services_list": {"placeholder": "e.g., Math Tutoring - Grades 1-12\nScience Coaching - Physics, Chem, Bio\nExam Prep - SAT, ACT, Board Exams"}},
            "health": {"services_list": {"placeholder": "e.g., General Checkup - Preventive care\nLab Tests - On-site diagnostics\nVaccinations - All age groups"}},
            "legal": {"services_list": {"placeholder": "e.g., Family Law - Divorce, custody, adoption\nCorporate Law - LLC, contracts, compliance\nEstate Planning - Wills, trusts"}},
        },
    },
    "menu": {
        "label": "Menu / Offerings",
        "description": "A menu of items, dishes, treatments, or courses",
        "base_fields": [
            {"key": "section_title", "label": "Section heading", "type": "text", "placeholder": "e.g., Our Menu, Treatment Menu"},
            {"key": "categories", "label": "Categories", "type": "textarea", "placeholder": "List categories, one per line"},
            {"key": "featured_items", "label": "Featured items with prices", "type": "textarea", "placeholder": "Item name - description - price\nOne per line"},
        ],
        "industry_overrides": {
            "restaurant": {
                "categories": {"placeholder": "e.g., Starters, Mains, Desserts, Beverages, Chef's Specials"},
                "featured_items": {"placeholder": "e.g., Sourdough Bread - Our signature 24hr fermented loaf - $8\nCroissant - Buttery, flaky, freshly baked - $4"},
            },
            "beauty": {
                "section_title": {"placeholder": "e.g., Our Services, Treatment Menu"},
                "categories": {"placeholder": "e.g., Haircuts, Coloring, Facials, Nails, Waxing"},
                "featured_items": {"placeholder": "e.g., Classic Haircut - Wash, cut & style - $45\nBalayage - Custom hand-painted highlights - $180"},
            },
        },
    },
    "products": {
        "label": "Products / Catalog",
        "description": "A product grid or featured product showcase",
        "base_fields": [
            {"key": "section_title", "label": "Section heading", "type": "text", "placeholder": "e.g., Our Products, Shop Best Sellers"},
            {"key": "product_list", "label": "Products (name - price - short description)", "type": "textarea", "placeholder": "Product name - $price - brief description\nOne per line"},
        ],
    },
    "pricing": {
        "label": "Pricing / Plans",
        "description": "Pricing tiers or a price list",
        "base_fields": [
            {"key": "plans", "label": "Plan names, prices, and features", "type": "textarea", "placeholder": "Plan Name - Price - Key features\nOne plan per line"},
            {"key": "billing_note", "label": "Billing note (optional)", "type": "text", "placeholder": "e.g., All plans billed monthly, Cancel anytime"},
        ],
        "industry_overrides": {
            "saas": {"plans": {"placeholder": "e.g., Free - $0/mo - 5 projects, 1 user\nPro - $29/mo - Unlimited projects, 5 users\nEnterprise - Custom - Everything + dedicated support"}},
            "education": {"plans": {"placeholder": "e.g., Individual - $50/month - 1-on-1 sessions\nGroup of 3 - $35/month each\nGroup of 5 - $25/month each"}},
            "fitness_recreation": {"plans": {"placeholder": "e.g., Monthly - $60/month - All classes\nQuarterly - $150/quarter - Save 17%\nAnnual - $500/year - Best value"}},
            "beauty": {"plans": {"placeholder": "e.g., Bronze Package - $99 - Haircut + Style\nSilver Package - $180 - Cut, Color, Style\nGold Package - $300 - Full Transformation"}},
        },
    },
    "testimonials": {
        "label": "Testimonials / Reviews",
        "description": "Customer testimonials or reviews",
        "base_fields": [
            {"key": "testimonials_list", "label": "Customer testimonials (2-4)", "type": "textarea", "placeholder": "\"Quote text\" - Customer Name, Title/Location\nOne per line"},
        ],
    },
    "stats": {
        "label": "Stats / Numbers",
        "description": "Counter-style stats showcasing scale or impact",
        "base_fields": [
            {"key": "stats_list", "label": "Key numbers (3-4 stats)", "type": "textarea", "placeholder": "Number - Label\nOne per line"},
        ],
        "industry_overrides": {
            "restaurant": {"stats_list": {"placeholder": "e.g., 12+ - Years in business\n50,000+ - Happy diners\n200+ - Menu items\n4.7 - Google rating"}},
            "education": {"stats_list": {"placeholder": "e.g., 500+ - Students taught\n95% - Score improvement\n8+ - Years experience\n4.9 - Parent rating"}},
            "health": {"stats_list": {"placeholder": "e.g., 10,000+ - Patients treated\n15+ - Years of practice\n98% - Patient satisfaction\n4.8 - Google rating"}},
            "saas": {"stats_list": {"placeholder": "e.g., 10,000+ - Active users\n99.9% - Uptime\n50+ - Countries\n4.8/5 - G2 rating"}},
        },
    },
    "team": {
        "label": "Team / Leadership",
        "description": "Team members, leadership, or featured staff",
        "base_fields": [
            {"key": "team_list", "label": "Team members (3-6)", "type": "textarea", "placeholder": "Name - Role - One-line bio\nOne per line"},
        ],
    },
    "gallery": {
        "label": "Gallery / Portfolio",
        "description": "Image grid or portfolio showcase",
        "base_fields": [
            {"key": "gallery_description", "label": "What should the gallery show?", "type": "text", "placeholder": "e.g., Our food, store interior, past events, completed projects"},
            {"key": "gallery_items", "label": "Gallery captions (optional, one per line)", "type": "textarea", "placeholder": "e.g., Wedding setup at The Ritz\nBirthday cake for 50 guests"},
        ],
    },
    "schedule": {
        "label": "Schedule / Timetable",
        "description": "Class schedules, event agendas, or availability",
        "base_fields": [
            {"key": "schedule_items", "label": "Schedule items", "type": "textarea", "placeholder": "Day/Time - Item name - Details\nOne per line, e.g., Mon 6pm - Morning Yoga - All levels"},
        ],
    },
    "how_it_works": {
        "label": "How It Works",
        "description": "3-5 step process explaining your service or product",
        "base_fields": [
            {"key": "steps", "label": "Steps (3-5)", "type": "textarea", "placeholder": "Step title - Short description\nOne per line"},
        ],
        "industry_overrides": {
            "restaurant": {"steps": {"placeholder": "e.g., Browse Menu - Pick your favorites\nPlace Order - Select delivery window\nEnjoy - Fresh food, delivered hot"}},
            "saas": {"steps": {"placeholder": "e.g., Sign Up - Create your free account\nConnect - Link your tools\nGrow - Watch your metrics improve"}},
        },
    },
    "delivery_areas": {
        "label": "Delivery / Service Areas",
        "description": "Locations or areas you serve",
        "base_fields": [
            {"key": "areas_list", "label": "Service areas (comma-separated)", "type": "textarea", "placeholder": "e.g., Downtown, Westside, Northshore, Bay Area"},
            {"key": "delivery_note", "label": "Delivery note (optional)", "type": "text", "placeholder": "e.g., Free delivery over $25, Same-day within 5 miles"},
        ],
    },
    "reservation": {
        "label": "Reservation",
        "description": "Table reservation or booking form for dine-in",
        "base_fields": [
            {"key": "headline", "label": "Section headline", "type": "text", "placeholder": "e.g., Reserve Your Table"},
            {"key": "subtext", "label": "Supporting text", "type": "text", "placeholder": "e.g., Book your dining experience online"},
            {"key": "cta_text", "label": "Button text", "type": "text", "placeholder": "e.g., Reserve Now"},
        ],
    },
    "order_form": {
        "label": "Contact / Order / Booking Form",
        "description": "Lead capture form for orders, inquiries, or bookings",
        "base_fields": [
            {"key": "form_title", "label": "Form heading", "type": "text", "placeholder": "e.g., Request a Quote, Book Your Session"},
            {"key": "form_subtext", "label": "Supporting text", "type": "text", "placeholder": "e.g., We'll get back to you within 24 hours"},
            {"key": "form_fields", "label": "Fields to collect (comma-separated)", "type": "text", "placeholder": "e.g., Name, Phone, Email, Message"},
            {"key": "submit_text", "label": "Submit button text", "type": "text", "placeholder": "e.g., Get Quote, Book Now"},
        ],
    },
    "contact": {
        "label": "Contact Info",
        "description": "Address, phone, email, hours",
        "base_fields": [
            {"key": "address", "label": "Business address", "type": "text", "placeholder": "Street, City, Postal Code"},
            {"key": "phone", "label": "Phone number", "type": "text"},
            {"key": "email", "label": "Email address", "type": "text"},
            {"key": "hours", "label": "Business hours", "type": "textarea", "placeholder": "e.g., Mon-Fri: 9am-6pm\nSat: 10am-4pm\nSun: Closed"},
        ],
        "industry_overrides": {
            "health": {
                "phone": {"label": "Appointment / Emergency number"},
                "hours": {"placeholder": "e.g., Mon-Sat: 9am-8pm\nSunday: Emergency only\nEmergency: 24/7"},
            },
            "restaurant": {
                "hours": {"placeholder": "e.g., Lunch: 12pm-3pm\nDinner: 6pm-11pm\nClosed: Mondays"},
            },
        },
    },
    "faq": {
        "label": "FAQ",
        "description": "Frequently asked questions and answers",
        "base_fields": [
            {"key": "faq_list", "label": "Common questions & answers", "type": "textarea", "placeholder": "Q: Question?\nA: Answer\n\nQ: Another question?\nA: Another answer"},
        ],
    },
    "countdown": {
        "label": "Countdown Timer",
        "description": "Countdown to an event, launch, or deadline",
        "base_fields": [
            {"key": "event_name", "label": "What's the countdown for?", "type": "text", "placeholder": "e.g., Grand Opening, New Batch, Flash Sale"},
            {"key": "event_date", "label": "Event date", "type": "text", "placeholder": "YYYY-MM-DD"},
            {"key": "cta_text", "label": "Button text", "type": "text", "placeholder": "e.g., Reserve Your Seat, Register Now"},
        ],
    },
    "cta": {
        "label": "Call to Action",
        "description": "A focused banner pushing visitors toward one action",
        "base_fields": [
            {"key": "headline", "label": "CTA headline", "type": "text", "placeholder": "e.g., Ready to get started?"},
            {"key": "subtext", "label": "Supporting text", "type": "text", "placeholder": "e.g., Join 1000+ happy customers"},
            {"key": "button_text", "label": "Button text", "type": "text", "placeholder": "e.g., Get Started, Sign Up Free"},
        ],
    },
    "footer": {
        "label": "Footer",
        "description": "Bottom footer with links, social, and legal info",
        "base_fields": [
            {"key": "tagline", "label": "Footer tagline (optional)", "type": "text", "placeholder": "e.g., Crafted with care since 2018"},
            {"key": "social_links", "label": "Social links (comma-separated)", "type": "text", "placeholder": "e.g., Instagram, Facebook, Twitter, LinkedIn"},
            {"key": "legal_links", "label": "Legal / policy links (optional)", "type": "text", "placeholder": "e.g., Privacy Policy, Terms of Service"},
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION RECOMMENDATIONS — co-occurrence upsells
# ─────────────────────────────────────────────────────────────────────────────
# Derived from co-occurrence analysis of 100+ website_example_outlines variants.
# When the user selects a key section, surface the suggested sections as a
# subtle hint chip: "Sites with {key} also add: {suggest}". Non-blocking.
SECTION_RECOMMENDATIONS: dict[str, dict] = {
    "hero": {
        "suggest": ["stats", "order_form"],
        "reason": "95% of sites pair hero with stats and a lead capture form",
    },
    "stats": {
        "suggest": ["testimonials", "order_form"],
        "reason": "Stats → Testimonials → Form is the #1 conversion sequence",
    },
    "testimonials": {
        "suggest": ["order_form", "stats"],
        "reason": "Social proof drives action — 93% pair with a form",
    },
    "pricing": {
        "suggest": ["faq", "testimonials", "order_form"],
        "reason": "Pricing needs objection handling (FAQ) and proof (testimonials)",
    },
    "features": {
        "suggest": ["testimonials", "about", "stats"],
        "reason": "Features need validation — testimonials and stats reinforce claims",
    },
    "countdown": {
        "suggest": ["order_form", "stats"],
        "reason": "Urgency without action is wasted — 77% pair with a form",
    },
    "faq": {
        "suggest": ["order_form", "stats"],
        "reason": "FAQ resolves objections — 94% also have stats nearby",
    },
    "about": {
        "suggest": ["testimonials", "order_form"],
        "reason": "Story + proof = trust — 84% of about sections pair with forms",
    },
    "gallery": {
        "suggest": ["testimonials", "order_form"],
        "reason": "Visual showcase needs social proof and action step",
    },
    "menu": {
        "suggest": ["order_form", "testimonials", "gallery"],
        "reason": "Menu/products need ordering path and visual reinforcement",
    },
    "products": {
        "suggest": ["testimonials", "features", "order_form"],
        "reason": "Products sell better with proof, differentiation, and a CTA path",
    },
    "services": {
        "suggest": ["testimonials", "pricing", "order_form"],
        "reason": "Services need proof, clear pricing, and a booking path",
    },
    "team": {
        "suggest": ["testimonials", "about", "order_form"],
        "reason": "Team credibility pairs with story and social proof",
    },
    "schedule": {
        "suggest": ["pricing", "order_form"],
        "reason": "Schedules need a booking/pricing path",
    },
    "how_it_works": {
        "suggest": ["features", "testimonials", "cta"],
        "reason": "Process explanation is strongest before features and proof",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY FLOWS — proven conversion funnels per category
# ─────────────────────────────────────────────────────────────────────────────
# When the user's selected sections are out of the optimal order, the wizard
# can suggest reordering to match these funnels (source: aggregated outline
# analysis).
CATEGORY_FLOWS: dict[str, list[str]] = {
    "services": ["navigation", "hero", "stats", "about", "services", "features", "testimonials", "pricing", "order_form", "contact", "footer"],
    "products": ["navigation", "hero", "features", "products", "pricing", "gallery", "testimonials", "faq", "cta", "footer"],
    "events":   ["navigation", "hero", "countdown", "features", "schedule", "stats", "testimonials", "pricing", "order_form", "footer"],
}
