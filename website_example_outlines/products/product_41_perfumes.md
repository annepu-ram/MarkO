# Perfumes & Fragrances -- Product Pages

> Focus: Sensory storytelling with trackable sections for fragrance notes, concentration levels, bottle design, and layering guides that let fragrance houses measure which olfactory narratives and presentation details drive discovery set and full-bottle purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Dior Sauvage | dior.com/sauvage | Cinematic video hero with desert landscapes, Francis Kurkdjian perfumer spotlight, fragrance pyramid visualization (top/heart/base), concentration comparison (EDT/EDP/Parfum/Elixir), "Try Before You Buy" sample CTA |
| Chanel No. 5 | chanel.com/no5 | Iconic heritage hero with Marilyn Monroe narrative, minimal note disclosure (mystique preservation), bottle evolution timeline, Grasse jasmine sourcing story, Art Deco packaging showcase |
| Jo Malone Peony & Blush Suede | jomalone.com/peony-blush-suede | Light editorial hero, fragrance combining guide (layering pairs), seasonal recommendations, "Fragrance Profiling" quiz, gift wrapping customization, crème + candle companion products |
| Le Labo Santal 33 | lelabo.com/santal-33 | Raw minimalist aesthetic, ingredient sourcing narrative (Australian sandalwood), hand-labeled bottle story, made-to-order freshness badge, city-exclusive collection concept |
| Maison Francis Kurkdjian Baccarat Rouge 540 | franciskurkdjian.com/baccarat-rouge-540 | Luminous hero with crystal-refracted light, perfumer's personal note, saffron + cedar ingredient story, Baccarat crystal collaboration narrative, wardrobe concept (layering EDP + Extrait) |

**Patterns to incorporate:**
- Atmospheric hero with mood-setting imagery that evokes the fragrance character
- Fragrance pyramid visualization with top, heart, and base notes clearly presented
- Concentration comparison (EDT vs EDP vs Parfum vs Extrait) with longevity indicators
- Ingredient sourcing story with origin photography and provenance details
- Bottle design showcase with packaging philosophy and material details
- Occasion and season recommendation guide
- Layering guide showing complementary fragrance combinations
- Perfumer biography with creative process narrative
- Discovery set or sample CTA to lower purchase barrier
- Size and price tier presentation with value comparison

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Fragrance Product Detail (e.g., Maison Francis Kurkdjian Baccarat Rouge 540 Eau de Parfum)**

1. **titlebar**
   Brand logo, nav links (Fragrances, Collections, The Maison, Francis Kurkdjian, Boutiques, Gifting), hamburger for mobile, "Find a Boutique" button.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- bottle front with refracted light, bottle on marble surface, ingredient still life with saffron threads and cedarwood, spray mist macro, packaging box, size lineup). Right column: **eyebrow** ("Eau de Parfum | Unisex"), **heading** ("Baccarat Rouge 540"), **paragraph** ("A luminous and addictive fragrance that envelops the wearer in a warm, radiant aura. Created by Francis Kurkdjian for Maison Francis Kurkdjian in collaboration with Baccarat."), **badge** ("Signature Scent"), **rating** (4.9 stars, "3,200+ Reviews"), **caption** ("From EUR 215 / 70ml"), **button** ("Add to Bag"), **button** ("Try a Sample -- EUR 14"), **link** ("Find in Store").

3. **layout-row (Feature 1: Top / Middle / Base Notes)** -> `comp_0_components_2`
   **eyebrow** ("The Fragrance"), **heading** ("A Luminous Composition"). **columnsgrid** (3 columns) each styled as a note tier: Column 1 -- **eyebrow** ("Top Notes"), **heading** ("Saffron, Jasmine"), **image** (saffron threads and jasmine petals), **paragraph** ("A bright, sparkling opening that catches the light -- precious saffron meets delicate jasmine absolute for an immediate sense of warmth and radiance."); Column 2 -- **eyebrow** ("Heart Notes"), **heading** ("Ambergris, Maison Cedar"), **image** (ambergris and cedar bark), **paragraph** ("The heart reveals an enveloping woody warmth. Ambergris brings a mineral sweetness while cedarwood adds structure and depth."); Column 3 -- **eyebrow** ("Base Notes"), **heading** ("Fir Resin, Musk"), **image** (resin droplets and musk accord visualization), **paragraph** ("The dry-down is where Baccarat Rouge 540 becomes unforgettable -- a luminous trail of resinous warmth and clean musk that lingers for hours."). **paragraph** ("Development time: Top notes (0-30 min) -> Heart (30 min-3 hr) -> Base (3-12+ hr)").

4. **layout-row (Feature 2: Concentration -- EDT / EDP / Parfum)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Concentrations"), **heading** ("Find Your Intensity"), **paragraph** ("Baccarat Rouge 540 is available in two concentrations, each offering a distinct interpretation of the same luminous accord."). Right column: **columnsgrid** (2 columns) each with **image** (bottle in that concentration) + **heading** (concentration name) + **caption** (price) + **progress-bar** (longevity visualization): "Eau de Parfum" / "EUR 215 / 70ml" / progress-bar at 75% + **caption** ("Longevity: 8-10 hours") + **paragraph** ("Radiant, balanced, versatile. The signature expression."), "Extrait de Parfum" / "EUR 310 / 70ml" / progress-bar at 95% + **caption** ("Longevity: 12-16+ hours") + **paragraph** ("Deeper, richer, more intimate. The concentrated essence."). **paragraph** ("Oil concentration: EDP 15-20% | Extrait 25-30%").

5. **layout-row (Feature 3: Longevity & Sillage)** -> `comp_0_components_4`
   Left column: **image** (atmospheric imagery -- trails of light or mist representing sillage). Right column: **eyebrow** ("Performance"), **heading** ("Presence That Lasts"), **paragraph** ("Baccarat Rouge 540 is renowned for its exceptional longevity and distinctive sillage -- the invisible trail that announces your arrival and lingers after you leave."). **columnsgrid** (3 columns) with **counter-up** + **caption**: "10" / "Hours Average Longevity (EDP)", "4" / "Arm's Length Sillage (Moderate-Strong)", "6" / "Sprays Recommended Application". **paragraph** ("Best applied to pulse points: wrists, neck, behind ears. Fragrance develops beautifully on clothing as well."). **caption** ("Performance varies with skin chemistry, temperature, and humidity.").

6. **layout-row (Feature 4: Bottle Design)** -> `comp_0_components_5`
   Left column: **eyebrow** ("The Flacon"), **heading** ("Crystal-Inspired Design"), **paragraph** ("The bottle captures the essence of Baccarat crystal in glass form. Its clean, geometric silhouette is crowned by a faceted cap inspired by the iconic Baccarat Harcourt glass. The warm, rosé-tinted juice glows like liquid crystal when light passes through."). Right column: **image** (bottle beauty shot with dramatic lighting showing the juice color and cap detail). **columnsgrid** (2 columns) with **icon** + **caption**: "Faceted Crystal Cap" / "Inspired by Baccarat Harcourt", "Rosé-Tinted Glass" / "Reveals the luminous juice color". **caption** ("Bottle designed by Maison Francis Kurkdjian atelier, produced in France.").

7. **layout-row (Feature 5: Occasion & Season)** -> `comp_0_components_6`
   Left column: **eyebrow** ("When to Wear"), **heading** ("A Fragrance for Every Moment"), **paragraph** ("While Baccarat Rouge 540 transcends seasonal boundaries, its warm character makes it particularly captivating in cooler weather and evening settings."). Right column: **columnsgrid** (2 columns): Column 1 -- **heading** ("Best Seasons") + **accordion** with items: "Autumn (Perfect -- warmth complements cooler air)", "Winter (Excellent -- cozy and enveloping)", "Spring (Good -- lighter application recommended)", "Summer (Fair -- one spray suffices in heat)"; Column 2 -- **heading** ("Best Occasions") + **accordion** with items: "Evening Events (Gala, dinner, theatre)", "Date Night (Intimate, memorable)", "Professional (Moderate application)", "Daily Signature (For the devoted)". **badge** ("Unisex -- Beloved by all genders").

8. **layout-row (Feature 6: Fragrance Family)** -> `comp_0_components_7`
   Left column: **image** (mood board collage -- amber crystals, cedar forest, saffron fields, crystal glassware). Right column: **eyebrow** ("Classification"), **heading** ("Amber Floral"), **paragraph** ("Baccarat Rouge 540 belongs to the Amber Floral family -- a warm, luminous category characterized by precious resins, golden florals, and woody depth. It occupies a unique space between sweetness and sophistication."). **tabs** with tabs: "Fragrance Family" (**paragraph** explaining Amber Floral classification), "Similar Scents" (**paragraph** describing comparable fragrances for reference), "Complementary Families" (**paragraph** on Oriental and Woody families that pair well).

9. **layout-row (Feature 7: Size & Price)** -> `comp_0_components_8`
   **eyebrow** ("Sizes"), **heading** ("Choose Your Flacon"). **columnsgrid** (4 columns) each with **image** (bottle in size) + **heading** (size) + **caption** (price) + **button** ("Add to Bag"): "5ml Travel Spray" / "EUR 55" / "Perfect for discovery", "35ml" / "EUR 175" / "The essential", "70ml" / "EUR 215" / "The signature" + **badge** ("Most Popular"), "200ml" / "EUR 455" / "The collector's edition". **paragraph** ("Gift sets available during holiday season."). **caption** ("Complimentary gift wrapping on all orders.").

10. **layout-row (Feature 8: Ingredient Story)** -> `comp_0_components_9`
    **eyebrow** ("Ingredients"), **heading** ("The Art of Sourcing"). **columnsgrid** (3 columns) each with **image** (ingredient in its natural setting) + **heading** (ingredient) + **paragraph** (story): "Saffron" / "Harvested by hand in Iran's Khorasan province, each crocus yields only three stigmas -- the most precious spice in the world" + **image** (saffron crocus fields), "Jasmine Absolute" / "Night-picked Egyptian jasmine, extracted through a labor-intensive enfleurage-inspired process to preserve its delicate facets" + **image** (jasmine fields at dawn), "Virginia Cedarwood" / "Sustainably sourced from the Blue Ridge Mountains, steam-distilled to capture the warm, pencil-shaving character that anchors the base" + **image** (cedar forest). **paragraph** ("All ingredients are sourced in compliance with IFRA safety standards and sustainability guidelines.").

11. **layout-row (Feature 9: Layering Guide)** -> `comp_0_components_10`
    Left column: **eyebrow** ("Layering"), **heading** ("Create Your Fragrance Wardrobe"), **paragraph** ("Francis Kurkdjian designed his fragrances as a wardrobe -- meant to be combined, layered, and personalized. Baccarat Rouge 540 serves as an exceptional layering base."). Right column: **columnsgrid** (2 columns) each with **image** (companion bottle) + **heading** (fragrance name) + **caption** (layering effect): "Grand Soir" / "Layer under BR540 for deeper amber warmth", "Aqua Universalis" / "Layer over BR540 for a fresh daytime expression". **paragraph** ("Layering tip: Apply the lighter fragrance first, then the stronger one on top."). **button** ("Shop the Wardrobe").

12. **layout-row (Feature 10: Niche vs Designer Context)** -> `comp_0_components_11`
    Left column: **image** (Francis Kurkdjian in his Parisian atelier). Right column: **eyebrow** ("The Perfumer"), **heading** ("Francis Kurkdjian"), **paragraph** ("One of the most celebrated perfumers of his generation, Francis Kurkdjian has created over 40 fragrances for prestigious houses before founding his own Maison in 2009. As Perfume Creation Director at Dior, he brings the same visionary approach to both his personal creations and one of fashion's greatest fragrance legacies."), **blockquote** ("I wanted to create a fragrance that had the luminosity of crystal -- something that catches the light and transforms it into warmth on the skin."). **caption** ("-- Francis Kurkdjian on Baccarat Rouge 540"). **link** ("Meet the Perfumer").

13. **layout-row (Reviews & Community)** -> `comp_0_components_12`
    **eyebrow** ("Community"), **heading** ("Fragrance Lovers Speak"). **rating** (4.9 overall, "3,200+ reviews"). **columnsgrid** (3 columns) each with **rating**, **blockquote** (review), **caption** (reviewer name + "Verified Purchase"). **ticker** scrolling community accolades: "Fragrantica Top 10 All Time", "#1 Most Complimented", "TikTok 2B+ Views", "Celebrity Favorite". **button** ("Read All Reviews").

14. **layout-row (Discovery & Sampling)** -> `comp_0_components_13`
    **heading** ("Discover Before You Commit"). **columnsgrid** (3 columns) each with **image** + **heading** + **caption** + **button**: "Sample Vial (2ml)" / "EUR 14" / "Single fragrance trial" / "Add", "Discovery Set (8 x 2ml)" / "EUR 85" / "Explore the Maison's signatures" / "Add", "Travel Set (5 x 11ml)" / "EUR 255" / "Full wardrobe on the go" / "Add". **caption** ("Sample value redeemable on full-bottle purchase").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Fragrances, The Maison, Boutiques & Stockists, Client Services. **br** (divider). **caption** (copyright, "Created in Paris").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new fragrance launch

**Page: New Fragrance Launch (e.g., "Dior -- L'Or de J'adore")**

1. **titlebar** -- Brand logo, minimal nav (The Fragrance, The Ingredients, The Bottle, Find), "Discover" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic campaign film -- golden light, flowing fabrics, perfumer's hands with ingredients, ending with bottle reveal). Overlay: **eyebrow** ("A New Dior Fragrance by Francis Kurkdjian"), **heading** ("L'Or de J'adore"), **paragraph** ("Light made essence."), **button** ("Discover Now").

3. **layout-row (The Perfumer's Vision)** -- Split screen: **image** (Francis Kurkdjian portrait) left, right: **eyebrow** ("The Vision"), **heading** ("Francis Kurkdjian"), **blockquote** ("I wanted to capture the moment when sunlight turns golden -- that warmth you feel on your skin at the end of a summer day."), **paragraph** ("The first fragrance created by Kurkdjian since joining Dior as Perfume Creation Director.").

4. **layout-row (Fragrance Pyramid)** -- Dark background. **heading** ("The Composition"). **columnsgrid** (3 columns) with atmospheric ingredient imagery and note descriptions for top, heart, and base. **video** (ingredient sourcing journey -- Grasse fields, Indian sandalwood forests).

5. **layout-row (The Bottle)** -- **heading** ("A Golden Icon"), **image** (bottle hero shot with refracted golden light), **paragraph** ("The amphora silhouette reimagined -- a tribute to J'adore's iconic form, now bathed in a warm golden hue that captures the essence of the fragrance within.").

6. **layout-row (Campaign)** -- **carousel** (campaign imagery -- celebrity ambassador editorial shots). **paragraph** (campaign narrative).

7. **layout-row (Shop CTA)** -- **heading** ("Experience L'Or de J'adore"), **columnsgrid** (3 columns) with size/price options. **button** ("Shop Now"), **button** ("Request Sample"). **caption** ("Complimentary engraving available in Dior boutiques.").

8. **layout-row (Footer)** -- Minimal footer with boutique locator, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a fragrance house's full collection

**Page: Fragrance Collection (e.g., "Jo Malone London -- All Fragrances")**

1. **titlebar** -- Brand logo, nav (Colognes, Body & Hand, Home, Candles, Gifting, Fragrance Combining), search, "Book Appointment" button.

2. **layout-row (Hero)** -- **heading** ("The Art of Fragrance Combining"), **paragraph** ("Layer scents to create something entirely your own"), **image** (curated flatlay of multiple Jo Malone bottles with ingredient botanicals). **button** ("Take the Fragrance Quiz").

3. **layout-row (Filter Bar)** -- **tabs** (By Family: "Citrus", "Fruity", "Light Floral", "Floral", "Spicy", "Woody") each filtering the product grid below.

4. **layout-row (Category: Signature Colognes)** -- **eyebrow** ("Colognes"), **heading** ("Our Signatures"). **columnsgrid** (3 columns) each card: **image** (bottle), **badge** ("Bestseller" / "New" / "Limited" where applicable), **heading** (fragrance name), **caption** (fragrance family + price), **paragraph** (one-line note description), **button** ("Shop"), **button** ("Pair With").

5. **layout-row (Category: Cologne Intense)** -- Same card pattern. **eyebrow** ("Intense"), **heading** ("Deeper, Bolder").

6. **layout-row (Category: Limited & Seasonal)** -- Same card pattern. **eyebrow** ("Limited Edition"), **heading** ("Seasonal Discoveries").

7. **layout-row (Combining Guide)** -- **heading** ("Fragrance Combining"), **paragraph** ("Jo Malone London was built on the art of layering. Discover unexpected pairings."). **columnsgrid** (3 columns) each showing a pairing: **image** (two bottles together) + **heading** ("Pairing Name") + **paragraph** ("Scent A over Scent B creates...") + **button** ("Shop the Pair").

8. **layout-row (Fragrance Quiz)** -- **heading** ("Find Your Scent"), **paragraph** ("Answer a few questions and we'll recommend your perfect Jo Malone wardrobe"), **button** ("Start Quiz"). **counter-up** + **caption**: "500K+" / "Quizzes Completed".

9. **layout-row (Gift Builder)** -- **heading** ("Create a Gift"), **paragraph** ("Choose a fragrance, add a candle, wrap it in our signature box"), **image** (gift box), **button** ("Build a Gift Set").

10. **layout-row (Footer)** -- Full footer with fragrance families, gifting, store locator, complimentary services, social links, legal.
