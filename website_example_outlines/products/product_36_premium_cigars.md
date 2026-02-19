# Premium Cigars -- Product Pages

> Focus: Tobacco connoisseurship storytelling with trackable sections for wrapper origin, strength profile, flavor notes, and pairing suggestions that let tobacconists and brands measure which sensory dimension drives individual stick and box purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| JR Cigars | jrcigars.com/cigars/handmade-cigars | Product card with hero shot, strength meter (mild-medium-full), wrapper/binder/filler breakdown, ring gauge and length specs, community star rating, "Add to Cart" with single/5-pack/box pricing tiers, flavor profile tags |
| Famous Smoke Shop | famous-smoke.com | Structured tasting notes (pre-light, first third, second third, final third), flavor wheel color-coded reference, strength and body badges, construction quality rating, "Order a 5-Pack" CTA, cigar advisor expert review embedded |
| Davidoff | davidoff.com/cigars | Luxury editorial photography on dark background, "Tasting Kit" sample CTA, cigar lifestyle storytelling, master blender interview video, humidor accessory cross-sell, "Find a Davidoff Store" CTA, white-glove presentation |
| Cohiba Official | cohiba.com | Heritage-driven design, Cuban tobacco field photography, Taino elder heritage story, band/ring detail macro shots, limited edition numbering, humidor storage guidelines, tasting note poetic narrative |
| Arturo Fuente | arturofuente.com | Family saga storytelling across generations, tobacco farm origin photography, hand-rolling craft video, "Forbidden X" rarity narrative, Don Carlos legacy section, box art and presentation |

**Patterns to incorporate:**
- Cigar hero shot on dark, moody background with ring band detail visible
- Wrapper/binder/filler composition as structured breakdown with origin details
- Ring gauge and length with visual scale for size context
- Strength profile spectrum (mild to full) with visual indicator
- Flavor notes organized by smoking stage (first third, second third, final third)
- Aging and storage recommendations with humidor specifications
- Drink pairing suggestions (whisky, rum, coffee, port)
- Brand and blender heritage storytelling with farm/factory photography
- Box vs single pricing with quantity options
- Humidor recommendation and cigar care accessories cross-sell

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Premium Cigar Detail (e.g., Davidoff Winston Churchill "The Late Hour" Toro)**

1. **titlebar**
   Brand wordmark, nav links (Cigars, Accessories, Humidors, Lifestyle, Stores, The Academy), hamburger for mobile, "Find a Store" button, account icon, shopping bag.

2. **layout-row (Hero -- Cigar Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- full cigar horizontal on dark wood surface, ring band macro showing Churchill portrait, foot showing wrapper/binder cross-section, cigar in hand with smoke, box presentation with cedar lining, ash in ashtray showing burn line). Right column: **eyebrow** ("Winston Churchill Collection"), **heading** ("The Late Hour -- Toro"), **paragraph** ("Inspired by the hours after midnight when Churchill did his finest thinking. Rich, complex, contemplative."), **caption** ("Toro | 6 x 52 | Medium-Full"), **badge** ("92 Points -- Cigar Aficionado"), **rating** (4.7 stars, 890 reviews), **heading** ("$22.50 / Single | $215 / Box of 20"), **button** ("Add Single to Cart"), **button** ("Buy Box of 20"), **button** ("Find in Store"), **caption** ("Ships in sealed humidity pouch. Humidor storage recommended.").

3. **layout-row (Feature 1: Wrapper, Binder, Filler)** -> `comp_0_components_2`
   Left column: **image** (cross-section macro of cigar foot -- showing dark Habano Ecuador wrapper, Broadleaf binder, and Dominican/Nicaraguan filler blend). Right column: **eyebrow** ("Composition"), **heading** ("The Tobaccos"), **paragraph** (tobacco composition narrative -- the Late Hour blend features a dark, oily Habano Ecuador wrapper aged in Scotch whisky casks, giving it a unique sweetness and depth, over a Connecticut Broadleaf binder known for richness, with a filler blend of Dominican Piloto Seco and Nicaraguan Visus for complexity and body). **columnsgrid** (3 columns) each with **heading** + **paragraph** + **caption**: "Wrapper" ("Habano Ecuador, aged in Scotch whisky casks" + "Dark, oily, sweet with whisky undertones"), "Binder" ("Connecticut Broadleaf" + "Rich, full-bodied, excellent combustion"), "Filler" ("Dominican Piloto Seco & Nicaraguan Visus" + "Creamy, earthy, with pepper and cedar"). **badge** ("Whisky-Cask Aged Wrapper").

4. **layout-row (Feature 2: Origin -- Dominican Republic)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Origin"), **heading** ("Crafted in the Dominican Republic"), **paragraph** (origin narrative -- rolled at the Davidoff factory in Santiago de los Caballeros, Dominican Republic, where master rollers with decades of experience hand-craft each cigar, the Dominican Republic's unique climate and soil produce tobaccos with a distinctive creaminess and balance). Right column: **image** (Davidoff factory -- roller at their station, tobacco leaves hanging in curing barn). **accordion** with items: "Dominican Piloto Seco -- Grown in the Cibao Valley, sun-cured for sweetness and body", "Nicaraguan Visus -- Jalapa Valley origin, provides pepper and earthiness", "Habano Ecuador -- Grown at cloud-forest elevation, thin leaf with rich oils", "Connecticut Broadleaf -- Shade-grown in the Connecticut River Valley, dark and robust". **caption** ("Each tobacco variety is aged 2-5 years before blending.").

5. **layout-row (Feature 3: Ring Gauge & Length)** -> `comp_0_components_4`
   **eyebrow** ("Specifications"), **heading** ("Toro -- 6 x 52"). **columnsgrid** (2 columns): Column 1: **counter-up** ("6") + **caption** ("Inches Length") + **paragraph** ("A Toro provides a generous smoking time of 60-90 minutes, allowing the blend to develop fully through all stages."), Column 2: **counter-up** ("52") + **caption** ("Ring Gauge (64ths of inch)") + **paragraph** ("A 52 ring gauge balances a cool, easy draw with concentrated flavor delivery."). **image** (size comparison chart showing the cigar alongside other vitolas -- Robusto, Corona, Churchill, Toro, Gordo). **paragraph** ("The Late Hour is also available in Robusto (5 x 52), Churchill (7 x 48), and Petit Corona (4 x 41).").

6. **layout-row (Feature 4: Strength Profile)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Strength"), **heading** ("Medium to Full Body"), **paragraph** (strength narrative -- the Late Hour begins with a medium-bodied creaminess that gradually builds to full strength by the final third, the whisky-cask aged wrapper introduces a sweetness that tempers the power, making this an accessible entry point into full-bodied smoking). Right column: **progress-bar** (strength indicator -- positioned at 70% on mild-to-full scale). **columnsgrid** (3 columns) each with **heading** + **caption**: "First Third" ("Medium -- creamy, sweet, approachable"), "Second Third" ("Medium-Full -- pepper emerges, complexity builds"), "Final Third" ("Full -- rich, bold, satisfying crescendo"). **caption** ("Strength perception varies by individual. Pair with food to moderate nicotine impact.").

7. **layout-row (Feature 5: Flavor Notes)** -> `comp_0_components_6`
   Full-width dark background. **eyebrow** ("Flavor"), **heading** ("A Journey in Three Acts"). **columnsgrid** (3 columns): Column 1: **heading** ("First Third") + **paragraph** ("Opens with creamy cedar and toasted almonds, underscored by a subtle sweetness from the whisky-cask wrapper. Notes of vanilla and white pepper emerge on the retrohale. Draw is effortless with thick, aromatic smoke production."), Column 2: **heading** ("Second Third") + **paragraph** ("The blend deepens with leather, dark chocolate, and espresso. A gentle spice builds -- black pepper and cinnamon. The whisky sweetness evolves into dried fruit and toffee. The burn line remains razor-sharp."), Column 3: **heading** ("Final Third") + **paragraph** ("Full complexity arrives -- cocoa, charred oak, and a hint of peaty smokiness. The retrohale delivers dark caramel and nutmeg. Finishes long with lingering sweetness and a satisfying earthiness."). **ticker** scrolling flavor descriptors: "Cedar", "Vanilla", "Toasted Almond", "Leather", "Dark Chocolate", "Espresso", "Black Pepper", "Toffee", "Charred Oak", "Caramel".

8. **layout-row (Feature 6: Aging & Storage)** -> `comp_0_components_7`
   Left column: **image** (humidor interior -- cigars resting on Spanish cedar shelves, hygrometer showing 65-70% RH). Right column: **eyebrow** ("Storage"), **heading** ("Aging Gracefully"), **paragraph** (aging and storage narrative -- like fine wine, premium cigars benefit from controlled aging, the Late Hour improves with 6-12 months of additional humidor rest as the whisky-cask flavors further integrate with the filler blend, store at 65-70% relative humidity and 65-70F for optimal preservation). **columnsgrid** (3 columns) each with **icon** + **counter-up** + **caption**: "65-70%" ("Relative Humidity"), "65-70F" ("Temperature"), "6-12 Mo" ("Recommended Rest"). **accordion** with items: "New Purchase -- Rest cigars 2-4 weeks after shipping to stabilize humidity", "Short-Term (1-6 months) -- Flavors begin to marry, wrapper oils develop", "Long-Term (1-5 years) -- Complex aging notes emerge, tannins soften", "Rotation -- Rotate cigars monthly for even humidity distribution". **caption** ("Never store cigars in a refrigerator or freezer. Cedar-lined humidors are essential.").

9. **layout-row (Feature 7: Pairing -- Drinks)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Pairing"), **heading** ("The Perfect Companion"), **paragraph** (pairing narrative -- the Late Hour was designed with evening rituals in mind, its whisky-cask heritage makes it a natural partner for aged spirits, though it also pairs beautifully with rich coffee and fortified wines). Right column: **carousel** (pairing editorial shots -- each drink beautifully photographed alongside the cigar): Slide 1: "Single Malt Scotch" + **caption** ("Peated or sherried Scotch echoes the cask-aged wrapper"), Slide 2: "Aged Rum" + **caption** ("Dark rum's caramel sweetness complements the vanilla notes"), Slide 3: "Espresso" + **caption** ("A double espresso amplifies the chocolate and nut flavors"), Slide 4: "Port Wine" + **caption** ("Vintage port's dried fruit richness mirrors the final third"). **columnsgrid** (4 columns) each with **icon** + **caption**: "Scotch Whisky", "Aged Rum", "Espresso", "Vintage Port".

10. **layout-row (Feature 8: Brand Story)** -> `comp_0_components_9`
    Full-width dark background. **eyebrow** ("Heritage"), **heading** ("Davidoff -- Since 1911"). **carousel** (heritage timeline): Slide 1: **image** (Zino Davidoff) + **caption** ("1911 -- Zino Davidoff opens his first tobacco shop in Geneva"), Slide 2: **image** (original shop) + **caption** ("1946 -- Davidoff becomes the exclusive purveyor of Cuban cigars in Switzerland"), Slide 3: **image** (Dominican factory) + **caption** ("1990 -- Davidoff establishes its own factory in the Dominican Republic"), Slide 4: **image** (Winston Churchill collection) + **caption** ("2014 -- The Winston Churchill collection launches, honoring the great cigar connoisseur"), Slide 5: **image** (Late Hour) + **caption** ("2018 -- The Late Hour introduces whisky-cask aging to the Churchill line"). **blockquote** ("'I smoke for the pleasure of it. Not because I think it good for my health.' -- Winston Churchill"). **paragraph** ("Davidoff's master blender carries forward a tradition of uncompromising quality established over a century ago.").

11. **layout-row (Feature 9: Box / Single Price)** -> `comp_0_components_10`
    **eyebrow** ("Purchase"), **heading** ("Choose Your Format"). **tabs** with tabs: "Single" ($22.50), "5-Pack" ($105 -- "Save $7.50"), "Box of 10" ($210 -- "Save $15"), "Box of 20" ($400 -- "Save $50"). Each tab: **image** (format presentation), **heading** (format + price), **paragraph** (description and savings), **button** ("Add to Cart"). **caption** ("Boxes ship sealed with humidity control. Singles ship in sealed pouches."). **badge** ("Box = Best Value").

12. **layout-row (Feature 10: Humidor Recommendation)** -> `comp_0_components_11`
    **eyebrow** ("Accessories"), **heading** ("Store It Right"). **columnsgrid** (3 columns) each with **image** (humidor/accessory) + **heading** + **caption** (price) + **button** ("Shop"): "Davidoff Explorer Humidor" ("Desktop humidor, holds 60 cigars, digital hygrometer included", $495), "Boveda 69% Humidity Packs" ("Maintenance-free 2-way humidity control", $18/4-pack), "Davidoff Winston Churchill Cutter" ("Double-blade guillotine, stainless steel", $85). **paragraph** ("A quality humidor is the single most important investment for cigar enjoyment.").

13. **layout-row (Reviews & Community)** -> `comp_0_components_12`
    **eyebrow** ("Reviews"), **heading** ("The Smoking Room"). **rating** (4.7 overall). **columnsgrid** (3 columns) each with **blockquote** (smoker review -- flavor description, pairing used, smoking time, occasion), **rating** (individual rating), **caption** (reviewer name + experience level). **button** ("Write a Review").

14. **layout-row (Related Cigars)** -> `comp_0_components_13`
    **heading** ("Explore the Churchill Collection"). **columnsgrid** (4 columns) each with **image** (cigar), **heading** (cigar name), **caption** (vitola + price), **badge** (strength indicator), **button** ("Shop"): Churchill Original, Churchill Belicoso, Late Hour Petit Corona, Late Hour Churchill.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Cigars, Accessories, The Academy, Stores. **br** (divider). **caption** (legal, age verification notice, "Must be 21+ to purchase. Surgeon General's Warning.", copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new cigar line or limited edition release

**Page: Limited Edition Release (e.g., "Arturo Fuente Opus X -- Lost City")**

1. **titlebar** -- Family crest, minimal nav (The Cigar, The Legend, The Tobaccos, Shop), "Shop Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic -- Dominican tobacco fields at golden hour, hand-rolling process, aging room with Opus X bands, smoke rising in dramatic light). Overlay: **eyebrow** ("Limited Release"), **heading** ("Opus X -- Lost City"), **paragraph** ("Aged in the ruins. Born from legend. The rarest Fuente."), **button** ("Shop Now").

3. **layout-row (Rarity Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "Limited to 2,500 Boxes", "5 Years Barrel-Aged", "100% Dominican Puro", "95 Points CA".

4. **layout-row (The Legend)** -- **eyebrow** + **heading** ("Chateau de la Fuente"), **paragraph** (the Fuente family's quest to grow wrapper tobacco in the Dominican Republic -- decades of failed attempts before achieving the impossible), **image** (Carlos Fuente Sr. and Jr. in the tobacco field).

5. **layout-row (The Tobaccos)** -- **heading** ("Tobaccos Lost and Found"), **carousel** (tobacco process -- seed selection, sun-grown wrapper cultivation, curing, 5-year aging in Dominican oak). **counter-up** ("5") + **caption** ("Years of Aging Before Rolling").

6. **layout-row (Tasting)** -- Dark background. **columnsgrid** (3 columns): "Nose" ("Aged cedar, dark cocoa, dried cherry"), "Palate" ("Creamy leather, cinnamon, toasted oak, honey"), "Finish" ("Long, warm, cedar and baking spice lingering for minutes").

7. **layout-row (Pairing)** -- **heading** ("Pair With"), **columnsgrid** (3 columns) each: **image** + **caption**: "25-Year Rum", "Vintage Port", "Single-Origin Espresso".

8. **layout-row (Purchase CTA)** -- **heading** ("$38 Single | $650 Box of 32"), **paragraph** ("Extremely limited allocation. Available while supplies last."), **button** ("Shop Now"), **badge** ("Limited Edition"). **caption** ("Ships in humidity-sealed packaging with Certificate of Authenticity.").

9. **layout-row (Footer)** -- Minimal footer with legal, age verification, social.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a cigar retailer's full inventory

**Page: Cigar Collection (e.g., "Famous Smoke Shop -- Handmade Cigars")**

1. **titlebar** -- Retailer logo, nav (All Cigars, Sampler Packs, Accessories, Humidors, Deals, Cigar Advisor), search, cart, account.

2. **layout-row (Hero)** -- **heading** ("Premium Handmade Cigars"), **paragraph** ("The world's largest selection. Expert-curated. Shipped fresh."), **image** (editorial -- open humidor with premium cigars). **layout-row** with filters: **dropdown** (Brand -- Davidoff, Padron, Arturo Fuente, My Father, Oliva), **dropdown** (Strength -- Mild, Medium, Medium-Full, Full), **dropdown** (Wrapper -- Connecticut, Habano, Maduro, Corojo, Oscuro), **dropdown** (Price -- Under $5, $5-10, $10-20, $20+), **button** ("Search").

3. **layout-row (Category: Bestsellers)** -- **eyebrow** ("Bestsellers"), **heading** ("Top-Rated Smokes"). **columnsgrid** (3 columns) each card: **image** (cigar), **badge** ("95 pts"/"Editor's Pick" where applicable), **heading** (cigar name + vitola), **caption** (price -- single/box), **rating** (stars), **paragraph** (one-line tasting note), **progress-bar** (strength indicator), **button** ("Add to Cart"), **button** ("Quick View").

4. **layout-row (Category: By Strength)** -- **tabs** (By Strength: "Mild & Mellow", "Medium-Bodied", "Medium to Full", "Full-Bodied") each showing **columnsgrid** of cigars matching that strength profile.

5. **layout-row (Category: Samplers)** -- **eyebrow** ("Samplers"), **heading** ("Try Before You Commit"). Same card grid for curated sampler packs and variety packs.

6. **layout-row (Flavor Wheel Guide)** -- **heading** ("Discover Your Flavor Profile"), **image** (Famous Smoke flavor wheel), **paragraph** ("Use our cigar flavor wheel to identify the tasting notes you enjoy most."). **accordion** with items: "Earthy -- Soil, leather, mushroom, moss", "Spicy -- Black pepper, cinnamon, clove, red pepper", "Sweet -- Vanilla, caramel, honey, dried fruit", "Woody -- Cedar, oak, sandalwood, mesquite", "Nutty -- Almond, hazelnut, walnut, peanut".

7. **layout-row (Trust Signals)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "80+ Years in Business", "10,000+ Cigars in Stock", "Humidity-Controlled Shipping", "Expert Staff Reviews".

8. **layout-row (Cigar Club)** -- **heading** ("Join the Cigar of the Month Club"), **paragraph** ("Hand-selected premium cigars delivered monthly. Save up to 30%."), **button** ("Join the Club").

9. **layout-row (Footer)** -- Full footer with brand directory, strength guide, accessories, customer service, legal, age verification.
