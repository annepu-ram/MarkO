# Fine Wines & Spirits -- Product Pages

> Focus: Terroir-driven sensory storytelling with trackable sections for vintage, tasting notes, aging process, and food pairing that let merchants and estates measure which aspect of the drinking experience drives add-to-cart conversions and collector purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Wine.com | wine.com/product | Clean product layout with bottle hero, community rating, professional critic scores (Parker, Wine Spectator), tasting notes with flavor profile tags, food pairing suggestions, vintage chart, "Add to Cart" with case discount, similar wines recommendation |
| Vivino | vivino.com/wines | Community-driven rating with 5-star system, taste characteristics spectrum (light-bold, dry-sweet, soft-acidic), flavor profile word cloud, highlights section, vintage comparison, "Meet the Winery" story, buy links with price comparison |
| The Whisky Exchange | thewhiskyexchange.com/p | Bottle hero with tasting notes (nose, palate, finish), distillery story section, age statement badge, region map, awards badges, "Add to Basket" with ABV and volume, expert review quotes, similar bottles carousel |
| Master of Malt | masterofmalt.com/whiskies | Structured tasting notes (nose, palate, finish), flavor map spider diagram, "Order a Dram" sample option, production details accordion, awards shelf, "Drinks With" cocktail suggestions, collector value note |
| Opus One Winery | opusonewinery.com/wine | Full-bleed vineyard hero, vintage storytelling (weather, harvest, blend), winemaker video, tasting notes as poetic narrative, food pairing editorial, Napa Valley terroir section, mailing list for allocation, "Request Allocation" CTA |

**Patterns to incorporate:**
- Bottle hero with label detail and vintage prominently displayed
- Structured tasting notes (nose, palate, finish) with descriptive language
- Flavor profile visualization (spectrum, spider diagram, or tag cloud)
- Professional scores and awards prominently badged (Robert Parker, Wine Spectator, Decanter)
- Region and terroir storytelling with vineyard/distillery photography
- Vintage-specific weather and harvest narrative
- Aging process with barrel type, duration, and cellar imagery
- Food pairing editorial with suggested dishes and serving temperature
- Decanting guide and serving recommendations
- Collector/investment value for premium vintages and limited releases

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Fine Wine Detail (e.g., Opus One 2021 Napa Valley Red Wine)**

1. **titlebar**
   Estate wordmark, nav links (Wines, Vineyard, Winemaking, Visit, Cellar Club, Shop), hamburger for mobile, "Shop" button, account icon.

2. **layout-row (Hero -- Bottle Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **image** (bottle shot -- label facing forward, dramatic lighting on dark background, vintage year visible). Right column: **eyebrow** ("Napa Valley Red Wine"), **heading** ("Opus One 2021"), **paragraph** ("A dialogue between two great wine traditions. Bordeaux meets Napa Valley."), **caption** ("Red Blend | 750ml | 14.5% ABV"), **badge** ("98 Points -- Robert Parker"), **badge** ("96 Points -- Wine Spectator"), **rating** (4.8 stars, 1,240 community ratings), **heading** ("$425"), **button** ("Add to Cart"), **button** ("Request Allocation"), **caption** ("Ships in temperature-controlled packaging. 6-bottle case discount available.").

3. **layout-row (Feature 1: Vintage & Year)** -> `comp_0_components_2`
   Left column: **image** (vineyard during 2021 harvest -- workers picking grapes at dawn, golden light, Oakville hills in background). Right column: **eyebrow** ("Vintage"), **heading** ("The 2021 Vintage"), **paragraph** (vintage narrative -- the 2021 growing season in Napa Valley was marked by a dry winter, a warm spring with early bud break, and a long, temperate summer that allowed slow, even ripening, harvest began on September 8th and concluded on October 15th, yielding fruit of exceptional concentration and balance). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "2021 Vintage", "38-Day Harvest", "Sept 8 -- Oct 15". **paragraph** ("'The 2021 is among the most complete and harmonious wines we have ever produced.' -- Michael Silacci, Winemaker").

4. **layout-row (Feature 2: Region & Terroir)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Terroir"), **heading** ("Oakville, Napa Valley"), **paragraph** (terroir narrative -- the Opus One estate spans the western benchlands of Oakville, one of the most prized viticultural areas in the world, alluvial soils with gravel, clay, and volcanic ash create a complex root environment, elevation and exposure to both morning fog and afternoon sun produce wines of extraordinary depth). Right column: **image** (aerial vineyard photograph showing block layout, surrounding hills, and To Kalon context). **accordion** with items: "Soil -- Alluvial gravels over clay and volcanic ash, excellent drainage", "Climate -- Mediterranean with Pacific fog influence, warm days and cool nights", "Elevation -- 150-250 feet, western benchland orientation", "Blocks -- 170 acres planted across multiple soil types for blending complexity". **caption** ("The estate was selected by Baron Philippe de Rothschild and Robert Mondavi in 1979.").

5. **layout-row (Feature 3: Grape Variety / Blend)** -> `comp_0_components_4`
   **eyebrow** ("The Blend"), **heading** ("Five Noble Varieties"). **columnsgrid** (5 columns) each with **progress-bar** (percentage) + **heading** + **caption**: "Cabernet Sauvignon" (79%, "Structure and power"), "Merlot" (7%, "Softness and plum fruit"), "Cabernet Franc" (6%, "Aromatic lift and spice"), "Petit Verdot" (5%, "Color and tannic grip"), "Malbec" (3%, "Floral notes and depth"). **paragraph** ("Each vintage's blend is determined by exhaustive tasting of individual barrel lots -- the proportions shift to reflect what the year has given."). **badge** ("Bordeaux-Style Blend").

6. **layout-row (Feature 4: Tasting Notes -- Nose, Palate, Finish)** -> `comp_0_components_5`
   Full-width dark background. **eyebrow** ("Tasting Notes"), **heading** ("A Sensory Journey"). **columnsgrid** (3 columns): Column 1: **heading** ("Nose") + **paragraph** ("Intense aromas of blackcurrant, violet, and graphite, with secondary notes of cedar, tobacco leaf, and dark chocolate. A whisper of crushed stone and dried herbs emerges with time in the glass."), Column 2: **heading** ("Palate") + **paragraph** ("Full-bodied yet remarkably elegant, the palate opens with layers of black cherry, cassis, and espresso. Tannins are finely grained and integrated, providing structure without austerity. Mid-palate reveals notes of fig, anise, and iron minerality."), Column 3: **heading** ("Finish") + **paragraph** ("Exceptionally long and resonant, with echoes of dark fruit, graphite, and a subtle salinity that lingers for over a minute. The wine's precision and balance become most apparent in the lingering finish."). **ticker** scrolling flavor descriptors: "Blackcurrant", "Violet", "Graphite", "Cedar", "Espresso", "Dark Cherry", "Fig", "Minerality".

7. **layout-row (Feature 5: Aging Process)** -> `comp_0_components_6`
   Left column: **image** (barrel cellar -- rows of French oak barrels in the Opus One cave, dramatic lighting). Right column: **eyebrow** ("Aging"), **heading** ("18 Months in French Oak"), **paragraph** (aging narrative -- after fermentation in stainless steel and concrete vats, the wine is transferred to French oak barrels from select cooperages, predominantly new oak, for 18 months of aging, the barrels contribute structure, spice, and micro-oxidation while allowing the fruit to integrate and the tannins to soften). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "18 Months in Barrel", "100% French Oak", "85% New Barrels". **accordion** with items: "Cooperages -- Barrels sourced from Darnajou, Taransaud, and Sylvain for complexity", "Toast Level -- Medium to medium-plus for balanced spice without charring", "Racking -- Gentle racking every 4 months to clarify and aerate", "Bottling -- Unfined and unfiltered to preserve full complexity".

8. **layout-row (Feature 6: Awards & Scores)** -> `comp_0_components_7`
   **eyebrow** ("Acclaim"), **heading** ("Recognized by the World's Palates"). **columnsgrid** (4 columns) each with **image** (critic/publication logo) + **counter-up** (score) + **caption** (critic name): "98 Points" ("Robert Parker -- Wine Advocate"), "96 Points" ("Wine Spectator"), "97 Points" ("Decanter"), "95 Points" ("James Suckling"). **paragraph** ("'A wine of breathtaking precision and beauty. One of the great Opus Ones.' -- Robert Parker"). **ticker** scrolling accolades: "Top 100 Wines of 2024", "Gold Medal Decanter", "Best of Napa Valley", "Collector's Choice".

9. **layout-row (Feature 7: Food Pairing)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Pairing"), **heading** ("At the Table"), **paragraph** (food pairing narrative -- the 2021 Opus One pairs beautifully with dishes that match its richness and structure: dry-aged ribeye with herb butter, braised lamb shanks with rosemary, wild mushroom risotto with truffle, aged Comte and fig compote). Right column: **carousel** (food pairing editorial shots -- each dish beautifully plated): "Dry-Aged Ribeye", "Braised Lamb Shanks", "Wild Mushroom Risotto", "Aged Comte Board". **columnsgrid** (2 columns) each with **icon** + **caption**: "Serving Temperature" ("16-18C / 60-65F -- slightly below room temperature"), "Decanting" ("Recommended 1-2 hours before serving for full expression").

10. **layout-row (Feature 8: Decanting Guide)** -> `comp_0_components_9`
    Left column: **image** (wine being decanted into a crystal decanter, ruby color catching light). Right column: **eyebrow** ("Service"), **heading** ("Decanting the 2021"), **paragraph** (decanting guide -- young vintages like the 2021 benefit from 1-2 hours of decanting to open the bouquet and soften the youthful tannins, pour slowly against the side of the decanter, the wine will evolve continuously over 4-6 hours in the decanter). **columnsgrid** (3 columns) each with **icon** + **caption**: "Decant 1-2 Hours" ("For current drinking"), "Cellar 5-25 Years" ("Optimal drinking window: 2026-2046"), "Serve at 17C" ("Slightly below room temperature"). **paragraph** ("For aged vintages (10+ years), stand the bottle upright for 24 hours before opening, and decant carefully to separate any sediment.").

11. **layout-row (Feature 9: Price & Bottle Size)** -> `comp_0_components_10`
    **eyebrow** ("Purchase"), **heading** ("Acquire the 2021"). **tabs** with tabs: "750ml Standard" ($425), "1.5L Magnum" ($900), "3L Double Magnum" ($1,850), "6-Bottle Case" ($2,400). Each tab: **heading** (format + price), **paragraph** (format description and aging recommendation), **button** ("Add to Cart"). **caption** ("Magnums and larger formats age more gracefully due to the cork-to-wine ratio. Ideal for collectors."). **button** ("Request Allocation for Future Vintages").

12. **layout-row (Feature 10: Collector & Investment Value)** -> `comp_0_components_11`
    **eyebrow** ("Cellar"), **heading** ("A Wine Worth Keeping"), **paragraph** (collector narrative -- Opus One has demonstrated consistent appreciation across secondary markets, the 2021 vintage's critical scores position it among the estate's most collectible releases, proper cellaring at 55F and 70% humidity ensures optimal development over 25+ years). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Drinking Window" ("2026-2046 for optimal expression"), "Cellar Conditions" ("55F / 13C, 70% humidity, dark and vibration-free"), "Secondary Market" ("Strong demand for 95+ point Napa Valley Cabernets"). **progress-bar** (maturity timeline -- currently at year 3 of 25-year window, 12%). **caption** ("Wine is a living product. Cellar conditions directly affect development and value.").

13. **layout-row (Reviews & Community)** -> `comp_0_components_12`
    **eyebrow** ("Community"), **heading** ("What Collectors Say"). **rating** (4.8 overall). **columnsgrid** (3 columns) each with **blockquote** (collector tasting note -- personal experience, cellaring plans, food pairing used), **rating** (individual rating), **caption** (reviewer name + vintage tried date). **button** ("Share Your Tasting Note").

14. **layout-row (Related Wines)** -> `comp_0_components_13`
    **heading** ("Explore Further"). **columnsgrid** (4 columns) each with **image** (bottle), **heading** (wine name), **caption** (vintage + price), **badge** (score), **button** ("Shop"): Opus One 2020, Overture by Opus One, similar Napa Cabernets.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Wines, Vineyard, Visit, Cellar Club. **br** (divider). **caption** (legal, "Please drink responsibly. Must be 21+.", copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new vintage release

**Page: Vintage Release (e.g., "The Macallan Edition No. 7 -- Released")**

1. **titlebar** -- Distillery wordmark, minimal nav (The Whisky, The Cask, The Story, Shop), "Shop Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic release film -- Highland landscape, oak casks in cathedral-like warehouse, amber liquid being poured). Overlay: **eyebrow** ("Single Malt Scotch Whisky"), **heading** ("Edition No. 7"), **paragraph** ("A collaboration between whisky maker and master perfumer. Scent and spirit, intertwined."), **button** ("Shop Now").

3. **layout-row (Vital Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "43% ABV", "7 Cask Types", "Natural Color", "No. 7 of the Edition Series".

4. **layout-row (The Story)** -- **eyebrow** + **heading** ("Inspired by Scent"), **paragraph** (collaboration narrative -- master perfumer inspired the cask selection, scent and taste share molecular pathways), **image** (perfumer and whisky maker side by side).

5. **layout-row (Tasting Notes)** -- Dark background. **columnsgrid** (3 columns): "Nose" (honey, vanilla, ginger), "Palate" (citrus, oak, dried fruit), "Finish" (warm spice, lingering sweetness). **ticker** scrolling: "Honey", "Vanilla", "Ginger", "Citrus Peel", "Oak", "Dried Fig".

6. **layout-row (The Cask Journey)** -- **heading** ("Seven Cask Types"), **carousel** (cask type details -- sherry, bourbon, virgin oak, refill, etc.), **image** (warehouse interior).

7. **layout-row (Serving)** -- **heading** ("How to Enjoy"), **columnsgrid** (3 columns) each: **icon** + **caption**: "Neat" ("Room temperature, tulip glass"), "With Water" ("A few drops to open the bouquet"), "On the Rocks" ("One large cube for slow dilution").

8. **layout-row (Purchase CTA)** -- **heading** ("$350 / 700ml"), **button** ("Shop Now"), **button** ("Find a Stockist"), **caption** ("Limited allocation. Ships in branded presentation tube.").

9. **layout-row (Footer)** -- Minimal footer with legal, drinking age, social.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a wine merchant's or distillery's full range

**Page: Wine Collection (e.g., "Wine.com -- Red Wines")**

1. **titlebar** -- Merchant logo, nav (Red, White, Rose, Sparkling, Spirits, Gifts, Wine Club), search, cart, account.

2. **layout-row (Hero)** -- **heading** ("Red Wines"), **paragraph** ("Explore the world's finest reds, from Napa Cabernet to Burgundy Pinot Noir."), **image** (editorial -- wine glasses with different red wines). **layout-row** with filters: **dropdown** (Region -- Napa Valley, Bordeaux, Burgundy, Tuscany, Rioja), **dropdown** (Grape -- Cabernet Sauvignon, Pinot Noir, Merlot, Syrah), **dropdown** (Price Range), **dropdown** (Rating -- 90+, 95+), **button** ("Search").

3. **layout-row (Category: Staff Picks)** -- **eyebrow** ("Staff Picks"), **heading** ("Our Sommelier Recommends"). **columnsgrid** (3 columns) each card: **image** (bottle), **badge** ("98 pts"/"Staff Pick" where applicable), **heading** (wine name + vintage), **caption** (price), **rating** (critic score or community stars), **paragraph** (brief tasting note -- one sentence), **button** ("Add to Cart"), **button** ("Quick View").

4. **layout-row (Category: By Region)** -- **tabs** (By Region: "Napa Valley", "Bordeaux", "Burgundy", "Tuscany", "Rioja") each showing **columnsgrid** of wines from that region.

5. **layout-row (Category: Value Finds)** -- **eyebrow** ("Under $30"), **heading** ("Exceptional Value"). Same card grid for value-priced wines.

6. **layout-row (Wine Education)** -- **heading** ("Understanding Red Wine"). **accordion** with items: "Cabernet Sauvignon -- Full-bodied, tannic, blackcurrant and cedar", "Pinot Noir -- Light to medium, earthy, cherry and mushroom", "Merlot -- Medium-bodied, soft tannins, plum and chocolate", "Syrah/Shiraz -- Full-bodied, peppery, dark fruit and smoke".

7. **layout-row (Trust Signals)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "25,000+ Wines Available", "Expert Ratings on Every Bottle", "Temperature-Controlled Shipping", "100% Satisfaction Guarantee".

8. **layout-row (Wine Club CTA)** -- **heading** ("Join Our Wine Club"), **paragraph** ("Curated selections delivered monthly. Save 20% on every bottle."), **button** ("Join Now").

9. **layout-row (Footer)** -- Full footer with categories, customer service, wine education, legal, drinking age disclaimer.
