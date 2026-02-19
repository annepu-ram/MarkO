# Luxury Skincare & Spa -- Product Pages

> Focus: Science-meets-ritual storytelling with trackable sections for hero ingredients, clinical research, application rituals, and results timelines that let brands measure which sensory and scientific details convert browsers into premium skincare purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| La Mer Creme de la Mer | lamer.com/creme-de-la-mer | Origin story hero with Miracle Broth narrative, bio-fermentation process timeline, before/after clinical results, ritualistic application guide video, luxe packaging close-ups |
| SK-II Facial Treatment Essence | sk-ii.com/facial-treatment-essence | PITERA origin story with sake brewery narrative, "Crystal Clear Skin" before/after slider, skin type quiz, ingredient breakdown infographic, celebrity ambassador feature |
| La Prairie Skin Caviar | laprairie.com/skin-caviar | Ultra-premium dark aesthetic, caviar sourcing story from Swiss lakes, clinical study results with percentage improvements, texture visualization, art-meets-science brand philosophy |
| Augustinus Bader The Rich Cream | augustinusbader.com/the-rich-cream | Scientist founder story with TFC8 technology explanation, peer-reviewed research citations, celebrity testimonial grid, minimalist packaging showcase, results timeline chart |
| Tatcha The Dewy Skin Cream | tatcha.com/dewy-skin-cream | Japanese ritual storytelling, ingredient origin map (Okinawa algae, Kyoto silk), texture swatch visualization, layering guide, clean beauty certification badges |

**Patterns to incorporate:**
- Cinematic hero with product floating on a textured background (marble, silk, water)
- Hero ingredient deep-dive with sourcing story, origin map, and scientific explanation
- Clinical study results section with percentage improvement counter-ups
- Application ritual video or step-by-step guide with sensory language
- Results timeline showing expected improvements at week 1, 4, 8, 12
- Texture and sensory experience visualization (close-up of cream, serum drop, mist)
- Luxe packaging showcase with design philosophy explanation
- Celebrity or dermatologist endorsement section with credentials
- Regimen builder showing complementary products in routine order
- "Discover Your Ritual" quiz or consultation booking CTA

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Luxury Skincare Product Detail (e.g., La Mer Creme de la Mer)**

1. **titlebar**
   Brand logo, nav links (Skincare, Collections, The Story, Science, Consultation, Stores), hamburger for mobile, "Shop Now" button.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- hero jar on marble surface, texture close-up showing the cream, application on skin, ingredient botanical still life, packaging box, size comparison). Right column: **eyebrow** ("Moisturizers | Miracle Broth"), **heading** ("Creme de la Mer"), **paragraph** ("The moisturizer that started a legacy. Infused with cell-renewing Miracle Broth, this iconic cream transforms skin with the healing energies of the sea."), **badge** ("Iconic"), **rating** (4.8 stars, "2,400+ Reviews"), **caption** ("From USD 190 / 30ml"), **button** ("Add to Bag"), **button** ("Find in Store"), **link** ("View All Sizes").

3. **layout-row (Feature 1: Hero Ingredient & Source)** -> `comp_0_components_2`
   Left column: **eyebrow** ("The Ingredient"), **heading** ("Miracle Broth"), **paragraph** ("Born from the sea. Dr. Max Huber, a former aerospace physicist, spent 12 years and 6,000 experiments perfecting a bio-fermentation process that transforms nutrient-rich sea kelp into Miracle Broth -- La Mer's legendary healing elixir."), **blockquote** ("The sea holds the secret to skin's renewal. Every jar carries the energy of the ocean."), **caption** ("-- Inspired by Dr. Max Huber's vision"). Right column: **image** (giant kelp underwater photography from Miracle Broth sourcing location). **badge** ("Sustainably Harvested"). **badge** ("Bio-Fermented 3-4 Months").

4. **layout-row (Feature 2: Scientific Research)** -> `comp_0_components_3`
   Left column: **image** (laboratory setting -- scientist examining fermentation vessels or microscopy imagery of skin cells). Right column: **eyebrow** ("The Science"), **heading** ("Clinically Proven Results"), **paragraph** ("In an independent clinical study with 62 women over 8 weeks, Creme de la Mer demonstrated significant improvements across all key skin health markers."). **columnsgrid** (3 columns) each with **counter-up** (percentage) + **caption** (metric): "92" / "% Improved Skin Firmness", "89" / "% Visibly Reduced Fine Lines", "96" / "% Enhanced Skin Radiance". **caption** ("Independent clinical study, 62 women, 8 weeks. Results may vary."). **link** ("View Full Study Details").

5. **layout-row (Feature 3: Application Ritual)** -> `comp_0_components_4`
   **eyebrow** ("The Ritual"), **heading** ("The Art of Application"). **video** (close-up cinematic video of the warming and pressing application technique). Below: **columnsgrid** (4 columns) each with **image** (step illustration) + **heading** (step number + name) + **caption** (instruction): "Step 1: Warm" / "Take a small amount and warm between fingertips until it becomes translucent", "Step 2: Press" / "Gently press the cream into skin using La Mer's signature press-and-release technique", "Step 3: Smooth" / "Smooth from the center of the face outward with gentle upward strokes", "Step 4: Activate" / "Cup palms over face, allowing body heat to activate the Miracle Broth". **paragraph** ("Apply morning and evening after cleansing and treatment essence for optimal results.").

6. **layout-row (Feature 4: Results Timeline)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Your Journey"), **heading** ("Visible Transformation"), **paragraph** ("Experience progressive improvement as Miracle Broth works in harmony with your skin's natural renewal cycle."). Right column: **columnsgrid** (1 column, stacked timeline): **layout-row** with **badge** ("Week 1") + **paragraph** ("Immediate comfort and deep hydration. Skin feels softer and more supple."), **layout-row** with **badge** ("Week 4") + **paragraph** ("Visibly brighter complexion. Fine lines begin to soften. Skin barrier strengthened."), **layout-row** with **badge** ("Week 8") + **paragraph** ("Firmer, plumper skin. Dark spots begin to fade. Even-toned radiance."), **layout-row** with **badge** ("Week 12") + **paragraph** ("Transformed skin with visible reduction in wrinkles, improved elasticity, and luminous glow."). **progress-bar** (showing "Your Skin Journey" at various stages, visual representation).

7. **layout-row (Feature 5: Texture & Sensory Experience)** -> `comp_0_components_6`
   Left column: **image** (ultra-close-up macro shot of the cream texture -- rich, dewy, showing the characteristic slight shimmer). Right column: **eyebrow** ("The Sensation"), **heading** ("A Sensory Experience"), **paragraph** ("Rich yet weightless, Creme de la Mer melts from a luxurious balm to a silky veil upon skin contact. The subtle marine scent -- a blend of eucalyptus, citrus, and oceanic notes -- transforms your routine into a moment of calm."). **accordion** with items: "Texture Profile (Rich balm that transforms to fluid)", "Scent Notes (Eucalyptus, citrus, marine)", "Absorption Time (30-60 seconds)", "Finish (Dewy, luminous, never greasy)", "Skin Feel (Plump, cushioned, protected)".

8. **layout-row (Feature 6: Packaging & Design)** -> `comp_0_components_7`
   Left column: **eyebrow** ("The Design"), **heading** ("An Object of Beauty"), **paragraph** ("The iconic sea-green jar, designed to preserve the potency of Miracle Broth, has remained essentially unchanged since Dr. Huber's original formulation. Each jar is sealed with precision to maintain bio-ferment integrity."). Right column: **image** (packaging beauty shot -- jar, box, spatula on styled surface). **columnsgrid** (3 columns) with **icon** + **caption**: "UV-Protective Glass" / "Preserves active ingredients", "Airless Architecture" / "Minimizes oxidation", "Recyclable Components" / "Jar, lid, and outer box". **badge** ("Refillable Jar Available").

9. **layout-row (Feature 7: Celebrity & Dermatologist Endorsement)** -> `comp_0_components_8`
   **eyebrow** ("Trusted By"), **heading** ("Endorsed by Skin Experts"). **columnsgrid** (3 columns) each with **image** (portrait) + **blockquote** (endorsement quote) + **caption** (name + credential): "Portrait" / "'The gold standard in luxury moisturizers. I recommend it for patients seeking transformative hydration.'" / "Dr. [Name], Board-Certified Dermatologist", "Portrait" / "'My skin has never looked this luminous. It's the one product I never travel without.'" / "[Celebrity Name], Brand Ambassador", "Portrait" / "'The Miracle Broth bio-fermentation is genuinely innovative. The clinical data supports the results.'" / "Dr. [Name], Cosmetic Chemist". **ticker** scrolling press quotes: "Vogue: 'The holy grail of moisturizers'", "Allure: 'Best of Beauty Hall of Fame'", "Harper's Bazaar: 'Worth every penny'".

10. **layout-row (Feature 8: Size & Price)** -> `comp_0_components_9`
    **eyebrow** ("Sizes"), **heading** ("Choose Your Jar"). **columnsgrid** (4 columns) each with **image** (jar in size) + **heading** (size) + **caption** (price) + **button** ("Add to Bag"): "15ml Travel" / "USD 100", "30ml Classic" / "USD 190", "60ml Luxe" / "USD 350", "100ml Grande" / "USD 530". **paragraph** ("Complimentary gift wrapping and personalized message available."). **badge** ("Best Value", on 60ml). **caption** ("Subscribe & Save: 10% off with auto-replenishment every 60 or 90 days").

11. **layout-row (Feature 9: Regimen Builder)** -> `comp_0_components_10`
    **eyebrow** ("Your Ritual"), **heading** ("Build Your Complete La Mer Regimen"). **columnsgrid** (5 columns) each with **image** (product) + **eyebrow** (step number) + **heading** (product name) + **caption** (description) + **button** ("Add"): "Step 1" / "The Cleansing Foam" / "Purify", "Step 2" / "The Treatment Lotion" / "Energize", "Step 3" / "The Concentrate" / "Target", "Step 4" / "Creme de la Mer" / "Moisturize" (highlighted), "Step 5" / "The Eye Concentrate" / "Brighten". **paragraph** ("Complete regimen: USD 785. Save 15% when you purchase the full ritual."). **button** ("Add Full Regimen to Bag").

12. **layout-row (Feature 10: Brand Philosophy)** -> `comp_0_components_11`
    Left column: **image** (ocean coastline -- Pacific kelp forest or Patagonian seascape). Right column: **eyebrow** ("Our Promise"), **heading** ("Born from the Sea"), **paragraph** ("La Mer is committed to the health of the world's oceans. Through the Blue Heart Oceans Fund, every purchase supports marine conservation, kelp reforestation, and ocean education programs."). **columnsgrid** (3 columns) with **counter-up** + **caption**: "50" / "Years of Discovery", "12" / "Ocean Conservation Projects", "1" / "Planet to Protect". **link** ("Learn About Our Sustainability Commitment").

13. **layout-row (Reviews & Testimonials)** -> `comp_0_components_12`
    **eyebrow** ("Real Results"), **heading** ("What Our Community Says"). **rating** (4.8 overall, "2,400+ reviews"). **columnsgrid** (3 columns) each with **rating** (individual), **blockquote** (review text), **caption** (reviewer + skin type + "Verified Purchase"). **button** ("Read All Reviews"). **paragraph** ("95% of reviewers recommend this product.").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("You May Also Love"). **columnsgrid** (4 columns) each with **image** (product), **heading** (product name), **caption** (category + price), **button** ("Quick Add").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop By Category, The La Mer Story, Client Services, Connect. **br** (divider). **caption** (copyright, legal, "Complimentary shipping on all orders").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new luxury skincare product launch

**Page: New Product Launch (e.g., "Augustinus Bader -- The Serum")**

1. **titlebar** -- Brand logo, minimal nav (The Science, The Product, Results, Shop), "Pre-Order" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic macro footage of serum drops falling onto skin, golden light, extreme slow-motion absorption). Overlay: **eyebrow** ("The Next Chapter in Skin Science"), **heading** ("The Serum"), **paragraph** ("TFC8 technology, now in its most concentrated form."), **button** ("Pre-Order Now"), **countdown** (to launch date).

3. **layout-row (The Scientist)** -- Split screen. Left: **image** (Professor Augustinus Bader portrait in lab). Right: **eyebrow** ("The Visionary"), **heading** ("Professor Augustinus Bader"), **paragraph** ("30 years of stem cell research at the University of Leipzig. One breakthrough formula."), **blockquote** ("The skin already knows how to heal itself. We simply provide the optimal environment.").

4. **layout-row (The Technology)** -- Dark background. **heading** ("TFC8 -- Trigger Factor Complex"), **paragraph** ("A patented complex of natural amino acids, vitamins, and synthesized molecules that guide your skin's own renewal processes."), **columnsgrid** (3 columns) with **counter-up** + **caption**: "40+" / "Active Compounds", "8" / "Key Trigger Factors", "98" / "% Saw Visible Improvement".

5. **layout-row (Results)** -- **heading** ("Clinically Proven"), **carousel** (before/after imagery with clinical study data overlays per slide). **progress-bar** (showing improvement percentages). **caption** ("12-week independent clinical study, 50 participants").

6. **layout-row (The Ritual)** -- **heading** ("Morning & Evening"), **video** (application tutorial). **columnsgrid** (3 columns) with **image** + **caption** for each step: "Cleanse", "Apply 3-4 drops", "Follow with The Rich Cream".

7. **layout-row (Celebrity Endorsements)** -- **ticker** scrolling celebrity names and quotes. **columnsgrid** (4 columns) with **image** + **caption** (celebrity name).

8. **layout-row (Pre-Order CTA)** -- **heading** ("Be First to Experience"), **paragraph** ("USD 350 / 30ml. Ships March 2026."), **button** ("Pre-Order"), **caption** ("Complimentary overnight shipping on pre-orders").

9. **layout-row (Footer)** -- Minimal footer with social links, press inquiries, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a luxury skincare brand's full collection

**Page: Brand Collection (e.g., "SK-II -- All Products")**

1. **titlebar** -- Brand logo, nav (Cleansers, Essences, Serums, Moisturizers, Masks, Eye Care, Sets), search, "Skin Quiz" button.

2. **layout-row (Hero)** -- **heading** ("Discover Your Crystal Clear Skin"), **paragraph** ("Powered by PITERA, our signature ingredient born from sake fermentation"), **image** (editorial beauty shot with model and product lineup). **button** ("Take the Skin Quiz").

3. **layout-row (Skin Concern Filter)** -- **tabs** (By Concern: "Anti-Aging", "Brightening", "Hydration", "Firmness", "Pore Care") each showing filtered **columnsgrid** of matching products.

4. **layout-row (Category: Essences & Lotions)** -- **eyebrow** ("Step 2: Treat"), **heading** ("Essences & Treatment Lotions"). **columnsgrid** (3 columns) each card: **image** (product), **badge** ("Bestseller" / "New" where applicable), **heading** (product name), **rating** (stars + review count), **caption** (price + size), **paragraph** (key benefit), **button** ("Shop Now"), **button** ("Compare").

5. **layout-row (Category: Serums & Concentrates)** -- Same card pattern. **eyebrow** ("Step 3: Target"), **heading** ("Serums & Concentrates").

6. **layout-row (Category: Moisturizers)** -- Same card pattern. **eyebrow** ("Step 4: Moisturize"), **heading** ("Moisturizers & Creams").

7. **layout-row (Regimen Builder)** -- **heading** ("Build Your PITERA Ritual"). Interactive step-by-step: **columnsgrid** (5 columns) each with **dropdown** (select product for step) + **image** (selected product) + **caption** (step name). **heading** ("Your Ritual Total") + **caption** (calculated price). **button** ("Add Ritual to Bag").

8. **layout-row (Ingredient Spotlight)** -- **heading** ("The Power of PITERA"), **paragraph** ("Over 50 micro-nutrients working in harmony"), **image** (PITERA ingredient visualization), **counter-up** stats: "50+" / "Micro-Nutrients", "90" / "% Natural Origin", "40" / "Years of Research". **button** ("Learn More About PITERA").

9. **layout-row (Consultation CTA)** -- **heading** ("Find Your Perfect Routine"), **paragraph** ("Take our 3-minute skin diagnostic"), **button** ("Start Skin Quiz"), **button** ("Book Virtual Consultation"). **counter-up** + **caption**: "2M+" / "Skin Diagnostics Completed".

10. **layout-row (Footer)** -- Full footer with product categories, skin concerns, brand story, store locator, social links, legal.
