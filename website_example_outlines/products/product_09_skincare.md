# Skincare & Personal Care -- Product Pages

> Focus: Science-backed ingredient storytelling with trackable sections for key ingredients, skin type matching, clinical results, and routine integration so brands can measure whether customers convert on ingredient science, visible results, or dermatologist endorsements.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| The Ordinary | theordinary.com/product | Ingredient-first naming, clinical concentration front and center, regimen builder tool, minimal packaging aesthetic, targets/concerns tags, pH and formulation details |
| CeraVe | cerave.com/product | Dermatologist-developed badge, ceramide science explainer, 3-step routine builder, skin type quiz, "Developed with Dermatologists" trust bar, simple clean layout |
| Minimalist | beminimalist.co/product | Indian D2C approach, ingredient percentage in product name, clinical study references, "Works Well With / Don't Mix" compatibility chart, transparent pricing |
| Dot & Key | dotandkey.com/product | Fun colorful packaging hero, before/after customer photos, skin concern tags, routine step indicator ("Step 2: Treat"), ingredient callout cards, subscription option |
| Paula's Choice | paulaschoice.com/product | Expert-level ingredient analysis, "Research" tab with cited studies, Beautypedia ratings, ingredient dictionary, "Why It's Great" and "Why You'll Love It" sections |

**Patterns to incorporate:**
- Hero product shot with ingredient concentration prominently displayed
- Key ingredient cards with scientific name, percentage, and benefit explanation
- Skin type compatibility matrix (oily, dry, combination, sensitive)
- Before/after clinical result photos with timeline
- Application routine step with morning/night placement guidance
- Ingredient transparency with full INCI list and explanations
- Dermatologist or clinical study endorsements
- Routine builder showing how product fits with other products

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Skincare Product Detail (e.g., "The Ordinary Niacinamide 10% + Zinc 1%")**

1. **titlebar**
   Brand logo, nav links (Skincare, Haircare, Regimen Builder, The Guide, Sets, What's New), search icon, account, cart. **badge** ("Free Shipping Over $25").

2. **layout-row (Hero -- Product Image + Purchase Info)** -> `comp_0_components_1`
   Left column (50%): **carousel** (product bottle front, side, texture swatch on hand, product in routine lineup, packaging). Right column (50%): **eyebrow** ("Serums | Blemish & Congestion"), **heading** ("Niacinamide 10% + Zinc 1%"), **paragraph** ("A high-strength vitamin and mineral blemish formula that targets the look of blemishes, congestion, and uneven skin tone."), **rating** (4.5 stars, 48,200 reviews), **heading** ("$5.90"), **caption** ("30 ml / 1 fl oz"), **badge** ("Bestseller"), **badge** ("Vegan"), **badge** ("Cruelty-Free"). Size selector: **columnsgrid** (2 options): "30 ml -- $5.90", "60 ml -- $9.80". **button** ("Add to Cart"), **button** ("Add to Regimen"), **caption** ("Subscribe & Save 15%: $5.02/month"). **paragraph** ("Targets: Blemishes, Congestion, Oiliness, Uneven Tone").

3. **layout-row (Feature 1: Key Ingredients)** -> `comp_0_components_2`
   **eyebrow** ("Ingredients"), **heading** ("What's Inside & Why"). **columnsgrid** (2 columns) hero ingredients: each with **image** (ingredient molecule/visual) + **heading** (ingredient) + **paragraph** (science-backed benefit): "Niacinamide (Vitamin B3) -- 10%" + "Reduces the appearance of blemishes and pore congestion. Balances visible sebum activity. Brightens uneven skin tone by inhibiting melanin transfer.", "Zinc PCA -- 1%" + "Regulates sebum production. Anti-inflammatory properties calm active breakouts. Works synergistically with niacinamide for enhanced oil control." Below: **paragraph** ("Formulation Facts: Water-based serum, pH 5.0-6.5, Lightweight texture"). **badge** ("No fragrance"), **badge** ("No alcohol"), **badge** ("No oils").

4. **layout-row (Feature 2: Skin Type Match)** -> `comp_0_components_3`
   **eyebrow** ("Skin Type"), **heading** ("Is This Right for You?"). **columnsgrid** (4 columns) each with **icon** + **heading** + **paragraph** + suitability indicator: "Oily Skin" + "Excellent -- reduces excess oil production" + **progress-bar** (95%), "Combination" + "Great -- targets T-zone without drying" + **progress-bar** (85%), "Normal" + "Good -- preventive blemish care" + **progress-bar** (70%), "Dry/Sensitive" + "Use with caution -- start at lower frequency" + **progress-bar** (40%). **paragraph** ("Not recommended for: Very sensitive skin or those with niacinamide sensitivity. Always patch test first."). **button** ("Take the Skin Type Quiz").

5. **layout-row (Feature 3: Before & After Results)** -> `comp_0_components_4`
   **eyebrow** ("Results"), **heading** ("Real Results, Real People"). **columnsgrid** (3 columns) each with side-by-side **image** (before) + **image** (after), **caption** (person's skin type + duration): "Oily Skin -- 4 Weeks", "Combination -- 8 Weeks", "Acne-Prone -- 12 Weeks". **paragraph** ("Results from consistent twice-daily use. Individual results may vary."). **counter-up** ("89%") + **caption** ("noticed reduced blemishes in 4 weeks"), **counter-up** ("76%") + **caption** ("saw improved skin texture in 8 weeks"). **caption** ("*Based on a consumer perception study of 312 participants over 12 weeks"). **badge** ("Clinically Tested").

6. **layout-row (Feature 4: Application Routine)** -> `comp_0_components_5`
   **eyebrow** ("How to Use"), **heading** ("Your Application Guide"). **columnsgrid** (4 columns) step-by-step: each with **counter-up** (step number) + **heading** (step) + **paragraph** (instruction): "1" + "Cleanse" + "Start with clean, damp skin", "2" + "Apply Serum" + "Dispense 2-3 drops onto fingertips. Pat gently across face avoiding eye area", "3" + "Wait" + "Allow 30 seconds to absorb before next step", "4" + "Moisturize" + "Follow with moisturizer to seal in benefits". **tabs** with tabs for "Morning Routine" and "Night Routine": Morning: **paragraph** ("Cleanser -> Niacinamide -> SPF Moisturizer"), Night: **paragraph** ("Cleanser -> Niacinamide -> Retinoid (alternate nights) -> Moisturizer"). **paragraph** ("Frequency: Use AM and PM daily. Can be used up to twice daily.").

7. **layout-row (Feature 5: Texture & Feel)** -> `comp_0_components_6`
   Left column: **image** (texture swatch on skin, close-up showing serum consistency). Right column: **eyebrow** ("Texture"), **heading** ("Lightweight, Non-Greasy"), **paragraph** ("Clear, slightly viscous serum that absorbs quickly without residue. No sticky feel. Layers beautifully under makeup and sunscreen. Slight tingling on first use is normal and typically subsides."). **columnsgrid** (3 columns) with **progress-bar** + **caption**: "Absorption Speed" (90%), "Lightweight Feel" (95%), "Under-Makeup Compatibility" (88%). **caption** ("Texture: Watery serum | Scent: Fragrance-free | Color: Clear").

8. **layout-row (Feature 6: Dermatologist Endorsed)** -> `comp_0_components_7`
   **eyebrow** ("Expert Backed"), **heading** ("Dermatologist Recommended"). **layout-row**: **image** (dermatologist portrait or clinical setting), **blockquote** ("Niacinamide at 10% is one of the most versatile and well-tolerated active ingredients. It addresses multiple skin concerns simultaneously -- from oil control to barrier repair -- making it suitable for most skin types."), **caption** ("Dr. [Name], Board-Certified Dermatologist"). **columnsgrid** (3 columns) with **icon** + **caption**: "Dermatologist Tested", "Non-Comedogenic", "Hypoallergenic". **paragraph** ("Referenced in 500+ published dermatological studies").

9. **layout-row (Feature 7: Size & Price)** -> `comp_0_components_8`
   **eyebrow** ("Value"), **heading** ("Effective Skincare, Honestly Priced"). **columnsgrid** (2 columns): "30 ml" card: **heading** ("$5.90"), **caption** ("60+ applications"), **paragraph** ("$0.10 per application"), **button** ("Add to Cart"). "60 ml" card: **heading** ("$9.80"), **badge** ("Best Value"), **caption** ("120+ applications"), **paragraph** ("$0.08 per application"), **button** ("Add to Cart"). Below: **accordion** with items: "Subscribe & Save" ("15% off every delivery, cancel anytime: $5.02/month for 30 ml"), "Shipping" ("Free standard shipping over $25, Express $5.95"), "Returns" ("Opened products not returnable for hygiene reasons. Sealed returns within 30 days"). **counter-up** ("0.10") + **caption** ("per application -- cost per use").

10. **layout-row (Feature 8: Ingredient Transparency)** -> `comp_0_components_9`
    **eyebrow** ("Full Transparency"), **heading** ("Complete Ingredient List"). **accordion** with items: "INCI List" (**paragraph** with full ingredient list: "Aqua, Niacinamide, Pentylene Glycol, Zinc PCA, Dimethyl Isosorbide, Tamarindus Indica Seed Gum, Xanthan Gum, Isoceteth-20, Ethoxydiglycol, Phenoxyethanol, Chlorphenesin")), "What Each Ingredient Does" (breakdown of each ingredient's function), "What We Don't Include" (parabens, sulfates, phthalates, mineral oil, formaldehyde, artificial fragrance), "Allergen Information" (suitable for most, patch test recommended). **badge** ("100% Transparent"), **badge** ("EWG Verified").

11. **layout-row (Feature 9: Routine Builder)** -> `comp_0_components_10`
    **eyebrow** ("Build Your Routine"), **heading** ("Works Best With"). **columnsgrid** (3 columns) recommended pairings: each with **image** (product) + **heading** (name) + **paragraph** (why it pairs well) + **button** ("Add"): "Squalane Cleanser" + "Gentle cleansing without stripping", "Hyaluronic Acid 2% + B5" + "Layer before niacinamide for hydration boost", "Natural Moisturizing Factors + HA" + "Seal everything in with barrier-repairing moisture". **heading** ("Don't Mix With"), **columnsgrid** (2 columns) with **image** + **heading** + **paragraph**: "Vitamin C (L-Ascorbic Acid)" + "Can cause flushing. Use at different times of day", "Direct Acids (AHA/BHA at high %)" + "May cause irritation when layered". **button** ("Build My Full Regimen").

12. **layout-row (Feature 10: Reviews & Results)** -> `comp_0_components_11`
    **heading** ("Reviews"). **rating** (4.5 overall, 48,200 reviews). **tabs** with tabs: "All Reviews", "With Photos", "5 Star", "By Skin Type", "By Concern". "All Reviews" tab: **columnsgrid** (2 columns): Left: **progress-bar** per star (5-star 55%, 4-star 25%, 3-star 11%, 2-star 5%, 1-star 4%). Right: **paragraph** ("Would Repurchase: 91%"), **paragraph** ("Saw Results: 84%"), **paragraph** ("Top Concern Addressed: Blemishes"). Below: **columnsgrid** (3 review cards) each with **rating**, **heading** (review title), **paragraph** (review body), **caption** (reviewer: skin type, age, concern, usage duration). "With Photos" tab: **columnsgrid** (4 columns) customer result photos. **button** ("Write a Review").

13. **layout-row (FAQ)** -> `comp_0_components_12`
    **heading** ("Common Questions"). **accordion** with items: "Can I use this with retinol?" ("Yes, niacinamide pairs well with retinoids and may reduce retinol irritation"), "Will it break me out?" ("Niacinamide is non-comedogenic. A small percentage may experience initial purging in the first 2 weeks"), "How long until I see results?" ("Most users notice improvements in 4-8 weeks with consistent twice-daily use"), "Can I use this if I'm pregnant?" ("Niacinamide is generally considered safe during pregnancy. Consult your dermatologist"), "Why is it so affordable?" ("We focus on efficacy over marketing. No celebrity endorsements, minimal packaging, direct-to-consumer model").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("You Might Also Like"). **columnsgrid** (4 columns): each **image** + **heading** + **caption** (price) + **rating** + **button** ("Quick Add"): "Alpha Arbutin 2%", "Azelaic Acid Suspension 10%", "Salicylic Acid 2% Solution", "Multi-Peptide Serum".

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop, Learn, Help, Follow. **br** (divider). **caption** (copyright, legal, "Not intended to diagnose, treat, cure, or prevent any disease").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new product line or breakthrough formula

**Page: New Product Launch (e.g., "CeraVe Retinol Resurfacing Serum -- New Formula")**

1. **titlebar** -- Brand logo, minimal nav (The Science, Ingredients, Routine, Buy), "Shop Now" button.

2. **layout-row (Hero)** -- Clean white background. **image** (product hero shot with ingredient molecules floating around it). **eyebrow** ("New from CeraVe"), **heading** ("Retinol Resurfacing Serum"), **paragraph** ("Clinically proven to smooth fine lines in 4 weeks. Developed with dermatologists."), **badge** ("Dermatologist Developed"), **button** ("Shop Now -- $19.99").

3. **layout-row (The Science)** -- **heading** ("MVE Delivery Technology"), **paragraph** (time-release encapsulation that delivers retinol gradually to minimize irritation), **image** (technology diagram showing encapsulated retinol releasing over 24 hours), **counter-up** ("24") + **caption** ("Hour Sustained Release").

4. **layout-row (Clinical Results)** -- **heading** ("Clinically Proven"), **columnsgrid** (3 columns) with **counter-up** + **caption**: "92%" + "Improved Skin Texture", "87%" + "Reduced Fine Lines", "95%" + "Tolerable for Sensitive Skin". **paragraph** ("8-week clinical study, 150 participants, twice-daily use").

5. **layout-row (Key Ingredients)** -- **heading** ("Powered By"), **columnsgrid** (3 columns): **image** + **heading** + **paragraph**: "Encapsulated Retinol" + "Smooths and renews", "3 Essential Ceramides" + "Restores skin barrier", "Niacinamide" + "Calms and brightens". **badge** ("Fragrance-Free").

6. **layout-row (3-Step Routine)** -- **heading** ("Simple 3-Step Night Routine"), **columnsgrid** (3 columns) with **counter-up** (step) + **image** (product) + **heading** + **paragraph**: "1 Cleanse", "2 Treat (This Product)", "3 Moisturize". **button** ("Shop the Routine -- $45").

7. **layout-row (Dermatologist Quote)** -- **blockquote** (dermatologist endorsement), **image** (doctor portrait), **caption** (credentials).

8. **layout-row (Purchase CTA)** -- **heading** ("$19.99"), **button** ("Buy Now"), **button** ("Find in Stores"), **paragraph** ("Available at CVS, Target, Walgreens, Amazon").

9. **layout-row (Footer)** -- Minimal footer with legal, safety disclaimer.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing for a skincare concern or routine

**Page: Skincare Routine Builder (e.g., "Minimalist -- Build Your Routine")**

1. **titlebar** -- Brand logo, nav (Serums, Moisturizers, Cleansers, Sunscreens, Sets, Skin Quiz), search, account, cart.

2. **layout-row (Hero)** -- **heading** ("Build Your Skincare Routine"), **paragraph** ("Science-backed products for every skin concern"), **button** ("Take the Skin Quiz"), **badge** ("Dermatologist Approved").

3. **layout-row (By Concern)** -- **tabs** ("Acne & Blemishes", "Anti-Aging", "Hyperpigmentation", "Hydration", "Sensitivity") each with curated **columnsgrid** (3 columns) product cards: **image**, **heading** (name with percentage), **caption** (key ingredient), **heading** (price), **rating**, **badge** ("Bestseller" where applicable), **button** ("Add to Routine").

4. **layout-row (Routine Steps)** -- **heading** ("Your Complete Routine"). **columnsgrid** (4 columns) routine steps: "Step 1: Cleanse" with **dropdown** (select cleanser), "Step 2: Treat" with **dropdown** (select serum), "Step 3: Moisturize" with **dropdown** (select moisturizer), "Step 4: Protect" with **dropdown** (select SPF). **button** ("Add Routine to Cart").

5. **layout-row (Ingredient Dictionary)** -- **heading** ("Ingredient Guide"), **accordion** with popular ingredients: "Niacinamide" (what it does, who it's for, concentration guide), "Retinol" (same), "Hyaluronic Acid" (same), "Vitamin C" (same), "Salicylic Acid" (same), "AHA/BHA" (same).

6. **layout-row (Compatibility Chart)** -- **heading** ("What Works Together"), **image** (ingredient compatibility matrix chart showing which ingredients can and cannot be mixed).

7. **layout-row (Compare Products)** -- **heading** ("Compare Serums"), **columnsgrid** (3 columns) with **dropdown** (select product) each. Comparison rows: Key Ingredient, Concentration, Skin Type, Concern, Texture, Price, Rating.

8. **layout-row (Expert Guidance)** -- **heading** ("Ask a Skin Expert"), **paragraph** ("Free consultation with our dermatology team"), **form** with **textbox** (Name), **textbox** (Email), **dropdown** (Skin Concern), **textarea** (Describe your skin), **button** ("Get Advice").

9. **layout-row (Reviews Aggregate)** -- **heading** ("What Our Community Says"), **counter-up** ("4.7") + **caption** ("Average Rating Across All Products"), **counter-up** ("250K+") + **caption** ("Reviews"), **columnsgrid** (3 columns) top-reviewed products.

10. **layout-row (Footer)** -- Full footer with shop, ingredients glossary, research, about, social links.
