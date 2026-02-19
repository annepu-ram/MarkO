# Shoes & Footwear -- Product Pages

> Focus: Performance-meets-style storytelling where sole technology, comfort features, and fit guidance each get dedicated trackable sections so brands can measure whether customers convert on innovation, aesthetics, or practicality.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Nike | nike.com/product | 360-degree product viewer, size selector with "Find Your Fit" link, "How It's Made" sustainability section, member-exclusive color drops, "Complete the Look" outfit carousel |
| Adidas | adidas.com/product | Bold product hero with tech callout overlays on shoe image, Boost/Lightstrike technology explainer, size chart with brand comparison, user reviews with fit feedback ("Runs Small/Large") |
| Puma | puma.com/product | Lifestyle-first photography (athlete in action), tech spec icons below hero, color selector with instant image swap, "More From This Collection" grid, personalizable options |
| Bata | bata.com/product | Value-focused layout, occasion tags (Formal, Casual, Sports), EMI options, detailed material description, "Customers Also Bought" cross-sell section |
| Woodland | woodland.co.in/product | Rugged outdoor photography, durability callouts (waterproof, anti-skid), terrain-specific use-case sections, adventure lifestyle storytelling |

**Patterns to incorporate:**
- Multiple angles hero with 360-degree spin view
- Sole technology explainer with cross-section diagram or animation
- Comfort feature callouts with icon grid (cushioning, arch support, breathability)
- Size and fit guide with measurement instructions and fit feedback from reviews
- Color selector with instant product image swap
- Weight specification with comparison context
- Use-case matching (running, walking, training, casual, formal)
- Sustainability/materials story for eco-conscious buyers

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Shoe Detail (e.g., "Nike Air Zoom Pegasus 41")**

1. **titlebar**
   Brand logo, nav links (Men, Women, Kids, New Releases, Sale, Jordan, Running), search icon, wishlist, cart. **badge** ("Free Shipping Over $50").

2. **layout-row (Hero -- Product Gallery + Purchase Info)** -> `comp_0_components_1`
   Left column (55%): **carousel** (7 shots -- lateral view, medial view, top-down, sole bottom, heel close-up, on-foot action, lifestyle). Right column (45%): **eyebrow** ("Men's Running Shoes"), **heading** ("Air Zoom Pegasus 41"), **paragraph** ("Your reliable daily trainer, now with more responsive cushioning and a secure fit for every run."), **badge** ("New Release"), **rating** (4.6 stars, 3,840 reviews), **heading** ("$140.00"), **caption** ("Members get 20% off"). Color selector: **columnsgrid** (row of color swatch circles with **caption**): "Black/White", "Wolf Grey", "University Blue", "Volt/Black". Size selector: **columnsgrid** (grid of **button** per size: 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13), **caption** ("Select Size"), **button** ("Size Guide"). **button** ("Add to Bag"), **button** ("Favorite"), **caption** ("Free shipping and 60-day returns").

3. **layout-row (Feature 1: Design & Style)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Design"), **heading** ("Built to Move"), **paragraph** ("Updated Flywire cables wrap the midfoot for a locked-in feel. Engineered mesh upper delivers breathability without sacrificing structure. Reflective elements for low-light visibility."). **columnsgrid** (3 columns) with **icon** + **caption**: "Engineered Mesh", "Flywire Cables", "Reflective Details". Right column: **image** (close-up of upper mesh texture and Flywire detail).

4. **layout-row (Feature 2: Material & Build)** -> `comp_0_components_3`
   Left column: **image** (exploded view or layered diagram showing shoe construction). Right column: **eyebrow** ("Materials"), **heading** ("Engineered for Performance"), **paragraph** ("Breathable engineered mesh upper, synthetic overlays for structure, foam midsole with embedded Zoom Air unit, rubber outsole with waffle pattern."). **accordion** with items: "Upper: Engineered Mesh + Synthetic" (breathable, lightweight, supports natural foot movement), "Midsole: React Foam + Zoom Air" (responsive cushioning that returns energy), "Outsole: Rubber Waffle Pattern" (durable grip on road and track surfaces). **badge** ("Made with at least 20% recycled content").

5. **layout-row (Feature 3: Sole Technology)** -> `comp_0_components_4`
   **eyebrow** ("Innovation"), **heading** ("React Foam + Zoom Air"), full-width **image** (cross-section of midsole showing Zoom Air unit embedded in React foam). Below: **columnsgrid** (3 columns) each with **image** (tech diagram) + **heading** + **paragraph**: "React Foam" + "Lightweight, durable, and responsive -- smooth transitions from heel to toe", "Zoom Air Unit" + "Pressurized air pockets under the forefoot deliver a snappy, springy sensation on push-off", "Waffle Outsole" + "Multi-directional traction pattern grips wet and dry surfaces equally". **counter-up** ("13%") + **caption** ("More energy return than previous generation").

6. **layout-row (Feature 4: Comfort Features)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Comfort"), **heading** ("All-Day Wearability"), **paragraph** ("Plush padded collar and tongue cushion the ankle. Internal heel counter locks the foot in place. Wide toe box accommodates natural splay."). **columnsgrid** (4 columns) with **icon** + **caption**: "Padded Collar", "Cushioned Tongue", "Heel Counter", "Wide Toe Box". Right column: **image** (on-foot shot from behind showing collar and heel fit). **progress-bar** ("Cushioning Level", 85%), **progress-bar** ("Breathability", 90%), **progress-bar** ("Arch Support", 75%).

7. **layout-row (Feature 5: Size & Fit Guide)** -> `comp_0_components_6`
   **eyebrow** ("Fit"), **heading** ("Find Your Perfect Fit"). **tabs** with tabs: "Size Chart" tab with **columnsgrid** (table: US, UK, EU, CM sizes), "How to Measure" tab with **image** (foot measurement diagram) + **paragraph** (instructions: stand on paper, mark heel and toe, measure in cm), "Fit Feedback" tab with **paragraph** ("Based on 3,840 reviews: 72% say true to size") + **progress-bar** ("True to Size" 72%, "Runs Small" 18%, "Runs Large" 10%). **caption** ("Between sizes? We recommend going half a size up for running shoes").

8. **layout-row (Feature 6: Color Options)** -> `comp_0_components_7`
   **eyebrow** ("Colors"), **heading** ("Find Your Colorway"). **columnsgrid** (4 columns) each with **image** (shoe in that colorway), **caption** (color name), **badge** ("Bestseller" on top seller, "New" on latest drop). **paragraph** ("Additional member-exclusive colorways available. Sign in to view."). **button** ("Join Nike Membership -- Free").

9. **layout-row (Feature 7: Weight)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Lightweight"), **heading** ("Only 272g"), **counter-up** ("272") + **caption** ("grams (Men's Size 10)"), **paragraph** ("One of the lightest daily trainers in its class. React foam sheds weight without sacrificing cushioning."). Right column: **columnsgrid** (2 columns) comparison: "Pegasus 41" **counter-up** ("272g") vs "Previous Gen" **counter-up** ("285g"), **paragraph** ("4.6% lighter than Pegasus 40"). **progress-bar** ("Weight Class: Lightweight", 80%).

10. **layout-row (Feature 8: Use Case)** -> `comp_0_components_9`
    **eyebrow** ("Built For"), **heading** ("Your Everyday Running Partner"). **columnsgrid** (4 columns) use cases: each with **icon** + **heading** + **paragraph**: "Daily Training" + "Reliable cushioning for 5-15km runs", "Recovery Runs" + "Soft enough for easy days", "Tempo Runs" + "Zoom Air adds push-off snap", "Walking" + "All-day comfort beyond running". **paragraph** ("Not recommended for: Trail running, sprinting, or competition racing"). **badge** ("Road Running").

11. **layout-row (Feature 9: Price & Member Benefits)** -> `comp_0_components_10`
    **eyebrow** ("Price"), **heading** ("$140.00"). **columnsgrid** (2 columns): Left: **heading** ("Standard Price: $140"), **paragraph** ("Free shipping on all orders"), **button** ("Add to Bag"). Right: **heading** ("Member Price: $112"), **badge** ("20% Off"), **paragraph** ("Plus free 60-day wear test returns"), **button** ("Join Free & Save"). **accordion** with items: "Payment Options" (credit card, PayPal, Afterpay 4x $35), "Shipping" (standard 5-7 days free, express 2-3 days $12), "Returns" (60-day wear test -- try them on runs and return if not satisfied).

12. **layout-row (Feature 10: Durability)** -> `comp_0_components_11`
    **eyebrow** ("Durability"), **heading** ("Built to Last"). **paragraph** ("High-abrasion rubber outsole in heel and toe strike zones withstands 500+ miles of road running. Reinforced stitching at stress points."). **columnsgrid** (3 columns) with **icon** + **caption**: "500+ Miles" + "Outsole Lifespan", "Reinforced Toe" + "Extra Stitching", "Abrasion-Resistant" + "Heel Strike Zone". **counter-up** ("800") + **caption** ("km average lifespan based on runner feedback"). **image** (worn shoe vs new shoe comparison -- showing minimal wear).

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Runner Reviews"). **rating** (4.6 overall, 3,840 reviews). **columnsgrid** (2 columns): Left: **progress-bar** per star (5-star 62%, 4-star 24%, 3-star 9%, 2-star 3%, 1-star 2%). Right: **paragraph** ("Comfort: 4.7/5"), **paragraph** ("Durability: 4.4/5"), **paragraph** ("Style: 4.5/5"), **paragraph** ("Value: 4.3/5"). Below: **columnsgrid** (3 review cards) each with **rating**, **heading** (title), **paragraph** (review), **caption** (runner profile + distance logged). **button** ("See All Reviews").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Runners Also Bought"). **columnsgrid** (4 columns): each **image** + **heading** + **caption** (price) + **button** ("Shop"). Items: Running Socks, Pegasus 41 Shield (waterproof), Dri-FIT Running Shorts, Nike Run Club App link.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Resources (Find a Store, Membership, Journal), Help (Order Status, Returns, Contact), Company (About, Careers, News), Social icons. **br** (divider). **caption** (legal, copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new shoe technology or signature release

**Page: New Technology Launch (e.g., "Adidas Ultraboost 5X -- New Energy Returns")**

1. **titlebar** -- Brand logo, minimal nav (The Tech, Performance, Colorways, Buy), "Shop Now" button.

2. **layout-row (Hero)** -- Dark background. **video-background** (athlete running in slow motion). Overlay: **eyebrow** ("Introducing"), **heading** ("Ultraboost 5X"), **paragraph** ("5x More Energy Return. Zero Compromise."), **button** ("Shop Now"), **button** ("Explore the Tech").

3. **layout-row (Innovation Story)** -- **heading** ("The Science of Bounce"), **image** (Boost foam cross-section), **paragraph** (energy return technology narrative), **counter-up** ("5x") + **caption** ("More energy return vs standard EVA").

4. **layout-row (Performance Data)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "20%" + "Lighter", "5x" + "Energy Return", "40%" + "More Cushion", "500+ km" + "Lifespan".

5. **layout-row (Athlete Testimonial)** -- **image** (athlete portrait), **blockquote** (athlete quote about the shoe), **caption** (athlete name and discipline).

6. **layout-row (Colorways)** -- **heading** ("Launch Colorways"), **carousel** (6 colorways, each with dramatic product photography).

7. **layout-row (Sustainability)** -- **heading** ("Made with Parley Ocean Plastic"), **paragraph** (recycled ocean plastic story), **columnsgrid** (3 columns) with **icon** + **caption**: "Recycled Upper", "Primegreen", "Low Carbon Footprint". **badge** ("Parley").

8. **layout-row (Pre-Order CTA)** -- **heading** ("$190"), **countdown** (to launch date), **button** ("Pre-Order Now"), **caption** ("Limited quantities available").

9. **layout-row (Footer)** -- Minimal footer with legal and social.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-shoe browsing for a brand's category

**Page: Running Shoes Catalog (e.g., "Puma Running")**

1. **titlebar** -- Brand logo, nav (Men, Women, Kids, Sport, Lifestyle, Sale), search, account, cart.

2. **layout-row (Hero)** -- **heading** ("Running Shoes"), **paragraph** ("Find your stride"), **image** (hero banner -- runner in motion).

3. **layout-row (Filter Bar)** -- **dropdown** (Gender), **dropdown** (Terrain: Road, Trail, Track), **dropdown** (Cushioning: Max, Moderate, Minimal), **dropdown** (Size), **dropdown** (Price Range), **dropdown** (Sort By), **button** ("Filter").

4. **layout-row (Featured Collection)** -- **eyebrow** ("Editor's Pick"), **ticker** (top 6 running shoes scrolling with **image** + **heading** + **caption** price).

5. **layout-row (Product Grid)** -- **columnsgrid** (4 columns) cards: **image**, **heading** (shoe name), **caption** (category), **heading** (price), **badge** ("New" / "Bestseller"), **rating**, **button** ("Shop Now").

6. **layout-row (By Running Type)** -- **tabs** ("Daily Training", "Speed/Racing", "Trail", "Recovery") each with curated **columnsgrid** of recommended shoes + **paragraph** (what to look for in each category).

7. **layout-row (Technology Guide)** -- **heading** ("Our Tech"), **columnsgrid** (3 columns) tech explainers: **image** (tech icon/diagram) + **heading** ("NITRO Foam" / "PROPLATE" / "PWRTAPE") + **paragraph** (what it does).

8. **layout-row (Size & Fit)** -- **heading** ("Size Guide"), **columnsgrid** (size chart table), **paragraph** ("Puma runs true to size. Wide options available in select styles.").

9. **layout-row (Compare)** -- **heading** ("Compare Running Shoes"), **columnsgrid** (3 columns) with **dropdown** (select shoe) each, comparison rows: Weight, Drop, Cushioning, Terrain, Price.

10. **layout-row (Footer)** -- Full footer with shop, help, company, social links.
