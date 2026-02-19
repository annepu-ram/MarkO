# Cosmetics & Makeup -- Product Pages

> Focus: Shade-matching, ingredient transparency, and tutorial-driven selling where each product feature (shade range, formula, application, longevity) is a trackable section helping brands understand whether customers convert on ingredients, tutorials, or social proof.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| MAC Cosmetics | maccosmetics.com/product | Shade finder quiz with selfie upload, swatchable shade grid, "Virtual Try-On" AR tool, artist tips section, "Complete Your Look" cross-sell |
| Maybelline | maybelline.com/product | Bold product hero with before/after slider, shade selector with model skin-tone preview, tutorial video, ingredients accordion, user-generated content grid |
| Nykaa | nykaa.com/product | Detailed ingredient list, skin type tags, user photos with shade-match reviews, shade comparison tool, EMI options, "Try On" AR feature |
| Fenty Beauty | fentybeauty.com/products | 50-shade foundation grid organized by undertone, AI shade finder from selfie, "How to Apply" video, shade range inclusivity messaging, bundle builder |
| Charlotte Tilbury | charlottetilbury.com/product | Luxury editorial hero, video tutorial by Charlotte herself, before/after transformation, "Magic" product naming, gifting options, virtual consultation CTA |

**Patterns to incorporate:**
- Shade grid organized by undertone (warm, cool, neutral) with swatches
- AR virtual try-on or shade finder quiz
- Before/after comparison for product effect
- Tutorial video showing application technique
- Ingredient list with callouts for hero ingredients
- Texture/finish visual (matte, dewy, satin preview)
- Cruelty-free/vegan/clean beauty badges
- User-submitted photos showing product on different skin tones

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Cosmetic Product Detail (e.g., "Fenty Beauty Pro Filt'r Soft Matte Foundation")**

1. **titlebar**
   Brand logo, nav links (Makeup, Skincare, Shade Finder, Bestsellers, Sets, New), search icon, account, wishlist, cart. **badge** ("Free Shipping Over $35").

2. **layout-row (Hero -- Product Image + Purchase Info)** -> `comp_0_components_1`
   Left column (50%): **carousel** (product bottle multiple angles, swatch on skin, texture close-up, lifestyle shot, model wearing product). Right column (50%): **eyebrow** ("Foundation"), **heading** ("Pro Filt'r Soft Matte Longwear Foundation"), **paragraph** ("Medium to full coverage foundation with a soft matte finish that lasts up to 12 hours"), **rating** (4.6 stars, 15,200 reviews), **heading** ("$42.00"), **caption** ("32 ml / 1.08 oz"), **badge** ("Bestseller"), **badge** ("Cruelty-Free"). Shade selector: **heading** ("Select Your Shade"), **paragraph** ("50 shades for every skin tone"), **button** ("Find My Shade" -- links to shade finder). **button** ("Add to Bag"), **button** ("Add to Wishlist"). **caption** ("Klarna: 4 payments of $10.50").

3. **layout-row (Feature 1: Shade Range & Finder)** -> `comp_0_components_2`
   **eyebrow** ("Shades"), **heading** ("50 Shades of Beautiful"), **paragraph** ("Organized by undertone so you find your match fast"). **tabs** with undertone tabs: "Warm" tab with **columnsgrid** (grid of shade swatch **image** circles, 15-18 shades), "Cool" tab (same), "Neutral" tab (same). Each swatch has **caption** (shade number + name). **button** ("Take the Shade Quiz"). **image** (diverse models lineup wearing different shades).

4. **layout-row (Feature 2: Ingredients & Formula)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Formula"), **heading** ("What's Inside"), **paragraph** ("Climate-adaptive formula that resists sweat, humidity, and oxidation"). **columnsgrid** (3 columns) hero ingredients: each with **image** (ingredient visual) + **heading** (ingredient name) + **paragraph** (benefit): "Vitamin E" + "Antioxidant protection", "Dimethicone" + "Smooth, blurred finish", "Iron Oxides" + "True-to-skin pigment". Right column: **accordion** with items: "Full Ingredient List", "What It's Free Of" (parabens, sulfates, phthalates), "Sustainability Info". **badge** ("Vegan"), **badge** ("Gluten-Free").

5. **layout-row (Feature 3: Skin Type Match)** -> `comp_0_components_4`
   **eyebrow** ("Best For"), **heading** ("Is This Right for Your Skin?"). **columnsgrid** (4 columns) each with **icon** + **heading** + **paragraph**: "Oily Skin" + "Perfect -- controls shine", "Combination" + "Great -- balances T-zone", "Normal" + "Excellent -- lightweight feel", "Dry" + "Pair with primer for best results". **progress-bar** labels: "Oil Control" (90%), "Coverage" (85%), "Hydration" (60%). **paragraph** ("Pro tip: For dry skin, mix with a drop of Fenty Skin moisturizer").

6. **layout-row (Feature 4: Application Tutorial)** -> `comp_0_components_5`
   **eyebrow** ("How To"), **heading** ("Get the Fenty Face"). **video** (step-by-step application tutorial, 2-3 minutes). Below video: **columnsgrid** (4 columns) step-by-step: each with **counter-up** (step number "1", "2", "3", "4") + **heading** (step name) + **paragraph** (instruction): "Prep" + "Apply primer and let set", "Apply" + "Dot foundation on forehead, cheeks, chin", "Blend" + "Use brush or sponge in downward strokes", "Set" + "Dust with setting powder on T-zone". **paragraph** ("Tools used: Fenty Full Bodied Foundation Brush 110").

7. **layout-row (Feature 5: Before & After)** -> `comp_0_components_6`
   **eyebrow** ("Results"), **heading** ("See the Transformation"). **columnsgrid** (3 columns) each with side-by-side layout: **image** (before -- bare skin) + **image** (after -- with foundation), **caption** (model name + skin type + shade used). **paragraph** ("Real customers, unretouched photos"). **badge** ("No Filter").

8. **layout-row (Feature 6: Texture & Finish)** -> `comp_0_components_7`
   Left column: **image** (macro texture shot -- product on skin showing finish). Right column: **eyebrow** ("Finish"), **heading** ("Soft Matte, Never Flat"), **paragraph** ("Buildable medium-to-full coverage with a natural matte finish that doesn't cake or settle into fine lines"). **columnsgrid** (3 columns) with **progress-bar** + **caption**: "Coverage" (85%), "Matte Level" (75%), "Natural Skin Look" (90%). **caption** ("Finish comparison: Matte | Satin | Dewy -- this product is Soft Matte").

9. **layout-row (Feature 7: Longevity & Wear Time)** -> `comp_0_components_8`
   **eyebrow** ("Wear Time"), **heading** ("12-Hour Staying Power"). **image** (wear test timeline -- same face at 0hr, 4hr, 8hr, 12hr). **columnsgrid** (2 columns): Left: **counter-up** ("12") + **caption** ("Hours Wear"), **paragraph** ("Sweat-proof, humidity-proof, transfer-resistant"). Right: **counter-up** ("89%") + **caption** ("Say it lasts all day"), **paragraph** ("Based on consumer study of 500 participants"). **progress-bar** ("Longevity Rating", 92%).

10. **layout-row (Feature 8: Price & Sizes)** -> `comp_0_components_9`
    **eyebrow** ("Options"), **heading** ("Choose Your Size"). **columnsgrid** (2 columns): "Full Size" card: **heading** ("$42.00"), **caption** ("32 ml"), **button** ("Add to Bag"). "Mini Size" card: **heading** ("$22.00"), **caption** ("15 ml"), **badge** ("Travel-Friendly"), **button** ("Add to Bag"). **accordion** with items: "Shipping Info", "Return Policy" (30-day returns on unopened), "Rewards Points" ("Earn 420 points with this purchase").

11. **layout-row (Feature 9: Bundles & Sets)** -> `comp_0_components_10`
    **eyebrow** ("Save More"), **heading** ("Bundle & Save"). **columnsgrid** (3 columns) bundle cards: each with **image** (bundle set), **heading** (bundle name: "Complexion Essentials", "Full Face Kit", "Starter Set"), **paragraph** (products included), **heading** (bundle price), **caption** (savings amount), **badge** ("Save 20%"), **button** ("Add Bundle").

12. **layout-row (Feature 10: Cruelty-Free & Ethics)** -> `comp_0_components_11`
    **eyebrow** ("Our Values"), **heading** ("Beauty Without Compromise"). **columnsgrid** (4 columns) each with **icon** + **caption**: "Cruelty-Free" + "Never tested on animals", "Vegan" + "No animal ingredients", "Clean" + "Free from harmful ingredients", "Inclusive" + "50 shades for all". **paragraph** ("Fenty Beauty is Leaping Bunny certified and committed to cruelty-free beauty worldwide").

13. **layout-row (Reviews & Customer Photos)** -> `comp_0_components_12`
    **heading** ("Reviews & Photos"). **rating** (4.6 overall). **tabs** with tabs: "All Reviews", "With Photos", "5 Star", "By Skin Type". "All Reviews" tab: **columnsgrid** (2 review cards) each with **rating**, **heading** (review title), **paragraph** (review body), **caption** (reviewer + skin type + shade purchased), **image** (customer photo if provided). "With Photos" tab: **columnsgrid** (4 columns) customer photo grid. **button** ("Write a Review").

14. **layout-row (Similar Products)** -> `comp_0_components_13`
    **heading** ("You Might Also Love"). **columnsgrid** (4 columns) each: **image**, **heading** (product name), **caption** (price), **rating**, **button** ("Quick Add").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop, About, Help, Follow. **br** (divider). **caption** (copyright, legal).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new product drop or collection launch

**Page: New Product Launch (e.g., "MAC x Celebrity Collection")**

1. **titlebar** -- Brand logo, minimal nav (The Collection, Shades, Tutorial, Shop), "Shop Now" button.

2. **layout-row (Hero)** -- **video-background** (campaign film with celebrity). Overlay: **eyebrow** ("Limited Edition"), **heading** ("MAC x [Celebrity] Collection"), **paragraph** ("Bold. Unapologetic. Beautiful."), **countdown** (to launch date), **button** ("Shop the Collection").

3. **layout-row (Campaign Story)** -- **blockquote** (celebrity quote about the collaboration), **image** (editorial campaign shot), **paragraph** (inspiration story).

4. **layout-row (Product Grid)** -- **heading** ("The Collection"). **columnsgrid** (4 columns) each product: **image**, **heading** (product name), **caption** (shade/finish), **heading** (price), **badge** ("Limited Edition"), **button** ("Add to Bag").

5. **layout-row (Tutorial)** -- **heading** ("Get the Look"), **video** (celebrity-led tutorial), step-by-step **columnsgrid** below.

6. **layout-row (Shade Showcase)** -- **heading** ("Every Shade, Every Skin"), **ticker** scrolling diverse model close-ups wearing the products.

7. **layout-row (Bundle Offer)** -- **heading** ("Get the Complete Collection"), **image** (full set), **heading** (bundle price), **badge** ("Save 25%"), **button** ("Buy the Set").

8. **layout-row (Social Buzz)** -- **heading** ("#MACxCollection"), **columnsgrid** (4 columns) social media post screenshots/images.

9. **layout-row (Footer)** -- Minimal footer with links and legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a makeup category

**Page: Foundation Finder (e.g., "Maybelline Foundations")**

1. **titlebar** -- Brand logo, nav (Face, Eyes, Lips, Nails, Tools, Virtual Try-On), search, cart.

2. **layout-row (Hero)** -- **heading** ("Find Your Perfect Foundation"), **paragraph** ("Match your skin type, coverage, and finish"), **button** ("Take the Quiz").

3. **layout-row (Filter Bar)** -- **dropdown** (Skin Type: Oily, Dry, Combination, Normal), **dropdown** (Coverage: Light, Medium, Full), **dropdown** (Finish: Matte, Dewy, Natural, Satin), **dropdown** (Price Range), **button** ("Filter Results").

4. **layout-row (Product Grid)** -- **columnsgrid** (3 columns) product cards: **image** (product), **heading** (name), **caption** (finish + coverage), **rating** (stars + count), **heading** (price), **badge** ("Bestseller" / "New" where relevant), shade count **caption** ("24 shades"), **button** ("Shop Now"), **button** ("Try On").

5. **layout-row (Comparison)** -- **heading** ("Compare Foundations"). **columnsgrid** (3 columns) with **dropdown** (select product) each. Comparison rows: Coverage, Finish, Wear Time, Skin Type, Price, Shade Count, SPF.

6. **layout-row (By Skin Concern)** -- **tabs** ("Oil Control", "Hydrating", "Anti-Aging", "Sensitive") each with curated product **columnsgrid**.

7. **layout-row (Ingredient Glossary)** -- **heading** ("Know Your Ingredients"), **accordion** with common ingredients explained.

8. **layout-row (Expert Picks)** -- **heading** ("Makeup Artist Favorites"), **columnsgrid** (3 columns) with **blockquote** (artist recommendation) + **image** (product) + **caption** (artist name).

9. **layout-row (Footer)** -- Full footer with category links, beauty tips, contact, social.
