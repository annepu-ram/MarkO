# Gourmet Food & Beverages -- Product Pages

> Focus: Origin-to-table storytelling with trackable sections for flavor profiles, sourcing stories, serving suggestions, and subscription options that let artisanal brands measure which sensory details and convenience features convert browsers into gourmet purchases and recurring subscribers.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Blue Tokai Coffee | bluetokaicoffee.com/collections | Estate-specific hero with farm photography, flavor wheel visualization, roast profile chart, brewing guide per method, freshly roasted date badge, subscription builder |
| Nespresso Vertuo | nespresso.com/vertuo | Capsule hero with cup intensity slider, tasting notes radar chart, origin map, barista recipe suggestions, machine pairing guide, capsule recycling program badge |
| Godiva Chocolate | godiva.com/collections | Luxe gold-and-chocolate hero, flavor collection grid, cocoa sourcing story (Ghana, Ecuador), gift box configurator, pairing guide (wine + chocolate), seasonal limited editions |
| Fortnum & Mason | fortnumandmason.com/tea | Heritage packaging hero with illustrated tins, blender's notes per tea, steeping guide (time/temp), provenance map (Darjeeling, Assam, Ceylon), hamper gift builder, afternoon tea experience |
| Eataly | eataly.com/products | Italian marketplace aesthetic, producer portraits with farm stories, DOP/IGP certification badges, recipe suggestions with each product, regional cuisine groupings, curated box sets |

**Patterns to incorporate:**
- Hero with product in context (cup of coffee, plated chocolate, tea setting) with atmospheric lighting
- Flavor profile visualization (tasting wheel, intensity slider, or note descriptors)
- Origin and source story with farm/estate photography and producer portraits
- Serving or brewing suggestions with step-by-step preparation guide
- Packaging and freshness indicators (roast date, harvest date, best-by)
- Certification badges (Organic, Fair Trade, Single Origin, DOP, Kosher)
- Pairing guide connecting the product to complementary foods or beverages
- Subscription builder with frequency and quantity customization
- Gift option configurator with wrapping and personal message
- Recipe or serving suggestion cards using the product

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Gourmet Product Detail (e.g., Blue Tokai Attikan Estate -- Single Origin Coffee)**

1. **titlebar**
   Brand logo, nav links (Coffee, Tea, Equipment, Subscriptions, Our Estates, Brew Guides), hamburger for mobile, "Subscribe & Save" button.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- coffee bag front with label art, beans close-up showing roast color, estate landscape at sunrise, cupping session, pour-over brew, bag back with details). Right column: **eyebrow** ("Single Origin | Medium Roast"), **heading** ("Attikan Estate"), **paragraph** ("Grown at 1,200 meters in the misty hills of Chikmagalur, Karnataka. This washed-process coffee delivers notes of milk chocolate, roasted almond, and a clean citrus finish."), **badge** ("Freshly Roasted"), **badge** ("Single Estate"), **rating** (4.6 stars, "840 Reviews"), **caption** ("INR 550 / 250g"), **button** ("Add to Bag"), **button** ("Subscribe & Save 15%"), **link** ("View All Grind Options").

3. **layout-row (Feature 1: Flavor Profile & Tasting Notes)** -> `comp_0_components_2`
   Left column: **image** (stylized tasting wheel or flavor profile graphic showing the flavor notes visually). Right column: **eyebrow** ("Flavor Profile"), **heading** ("What You'll Taste"), **paragraph** ("A balanced, approachable cup with medium body and clean sweetness. The washed process brings clarity to the chocolate and nut notes, while the high altitude contributes a bright citrus acidity."). **columnsgrid** (3 columns) each with **heading** + **caption**: "Milk Chocolate" / "Dominant flavor -- smooth, sweet cocoa", "Roasted Almond" / "Nutty warmth in the mid-palate", "Citrus Finish" / "Bright mandarin acidity in the aftertaste". **progress-bar** labels + bars: "Acidity" at 65%, "Body" at 55%, "Sweetness" at 70%. **caption** ("Roast Level: Medium | SCA Cupping Score: 84.5").

4. **layout-row (Feature 2: Origin & Source Story)** -> `comp_0_components_3`
   Left column: **eyebrow** ("The Estate"), **heading** ("Attikan Estate, Chikmagalur"), **paragraph** ("Nestled in the Western Ghats of Karnataka, Attikan Estate has been growing specialty coffee under shade-grown canopy for three generations. The Sethuraman family cultivates Arabica varieties -- SL795 and Chandragiri -- using traditional composting methods alongside modern quality controls."), **blockquote** ("Every batch is hand-picked at peak ripeness. We know every tree on this estate by name."), **caption** ("-- Ravi Sethuraman, Third-Generation Farmer"). Right column: **image** (estate landscape photo -- coffee cherries on branches with misty hills in background). **columnsgrid** (3 columns) with **counter-up** + **caption**: "1200" / "Meters Altitude", "75" / "Acres Under Canopy", "3" / "Generations of Growing".

5. **layout-row (Feature 3: Ingredients & Nutrition)** -> `comp_0_components_4`
   Left column: **image** (coffee beans in various stages -- green, roasted, ground). Right column: **eyebrow** ("Details"), **heading** ("What's Inside"), **paragraph** ("100% Arabica coffee beans. Single origin, single estate. No blending, no additives."). **columnsgrid** (2 columns): Column 1 -- **heading** ("Bean Details") + **accordion** with items: "Variety: SL795, Chandragiri", "Process: Washed (fully washed)", "Roast Date: Printed on every bag", "Best Before: 45 days from roast", "Caffeine: ~95mg per cup (drip)"; Column 2 -- **heading** ("Certifications") + **columnsgrid** (1 column) with **badge** items: "Rainforest Alliance", "Direct Trade", "Shade Grown", "Chemical Free". **caption** ("Allergen info: Processed in a facility that handles tree nuts.").

6. **layout-row (Feature 4: Serving / Brewing Suggestions)** -> `comp_0_components_5`
   **eyebrow** ("Brew Guide"), **heading** ("How to Brew Attikan Estate"). **tabs** with tab per brew method: "Pour Over" (step-by-step with **columnsgrid** of 4 steps: **image** + **heading** + **caption** -- "Grind: Medium-Fine", "Water: 92C, 250ml", "Time: 3:30 total", "Ratio: 1:16"), "French Press" (coarser grind, 4 min steep), "AeroPress" (inverted method, 2 min), "Espresso" (18g dose, 36g yield, 28 sec), "Cold Brew" (coarse grind, 12 hr steep). **paragraph** ("This coffee is most expressive as a pour-over, where the clean citrus notes shine. For milk-based drinks, pull as espresso."). **video** (barista brewing demonstration).

7. **layout-row (Feature 5: Packaging & Freshness)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Freshness"), **heading** ("Roasted to Order"), **paragraph** ("We roast Attikan Estate every Tuesday and Thursday. Your bag is roasted within 48 hours of your order and ships the same day. The one-way degassing valve ensures peak freshness for up to 45 days."). Right column: **image** (close-up of the bag showing degassing valve, roast date stamp, and resealable zipper). **columnsgrid** (3 columns) with **icon** + **caption**: "One-Way Valve" / "CO2 escapes, freshness stays", "Resealable Zip" / "Keeps beans protected between brews", "Roast Date Printed" / "Transparency you can trust". **badge** ("Ships Within 48 Hours of Roasting").

8. **layout-row (Feature 6: Certifications)** -> `comp_0_components_7`
   Left column: **image** (Rainforest Alliance certification ceremony at the estate / farmer with certification plaque). Right column: **eyebrow** ("Certifications"), **heading** ("Ethically Sourced, Transparently Traded"), **paragraph** ("We pay 40% above the Fairtrade minimum price directly to Attikan Estate. Every transaction is published in our annual Transparency Report."). **columnsgrid** (4 columns) each with **icon** + **heading** + **caption**: "Rainforest Alliance" / "Biodiversity and farmer welfare", "Direct Trade" / "No middlemen, fair pricing", "Shade Grown" / "Under native canopy trees", "Plastic-Free Packaging" / "Compostable bag and labels". **link** ("View Our Transparency Report").

9. **layout-row (Feature 7: Size & Price)** -> `comp_0_components_8`
   **eyebrow** ("Sizes"), **heading** ("Choose Your Bag"). **columnsgrid** (3 columns) each with **image** (bag) + **heading** (size) + **caption** (price) + **dropdown** (Grind: Whole Bean / Espresso / Filter / French Press / AeroPress) + **button** ("Add to Bag"): "100g Taster" / "INR 250", "250g Classic" / "INR 550" + **badge** ("Popular"), "500g Value" / "INR 999". **paragraph** ("Bulk orders (5kg+) available for cafes and offices. Contact us for wholesale pricing.").

10. **layout-row (Feature 8: Pairing Guide)** -> `comp_0_components_9`
    Left column: **eyebrow** ("Pairings"), **heading** ("Best Enjoyed With"), **paragraph** ("The milk chocolate and almond notes in Attikan Estate pair beautifully with baked goods and light desserts."). Right column: **columnsgrid** (3 columns) each with **image** (food pairing) + **heading** (pairing name) + **caption** (why it works): "Almond Croissant" / "Nutty flavors echo the coffee's roasted almond notes", "Dark Chocolate (70%)" / "Cocoa intensity complements the milk chocolate profile", "Banana Bread" / "Sweetness balances the citrus brightness". **link** ("See All Pairing Suggestions").

11. **layout-row (Feature 9: Subscription)** -> `comp_0_components_10`
    **eyebrow** ("Subscribe"), **heading** ("Never Run Out"). **columnsgrid** (2 columns): Left -- **paragraph** ("Get Attikan Estate delivered fresh on your schedule. Subscribe and save 15% on every bag. Pause, skip, or cancel anytime."), **dropdown** (Size: 250g / 500g), **dropdown** (Grind), **dropdown** (Frequency: Every 2 Weeks / Monthly / Every 6 Weeks), **button** ("Start Subscription"); Right -- **columnsgrid** (3 columns) with **icon** + **caption**: "15% Off" / "Every delivery", "Free Shipping" / "On all subscriptions", "Flexible" / "Pause or cancel anytime". **counter-up** + **caption**: "12000" / "Active Subscribers". **caption** ("First bag ships within 48 hours of roasting.").

12. **layout-row (Feature 10: Gift Options)** -> `comp_0_components_11`
    Left column: **image** (gift box with coffee, brewing equipment, and tasting notes card). Right column: **eyebrow** ("Gifting"), **heading** ("Gift the Experience"), **paragraph** ("Send freshly roasted Attikan Estate in our signature gift box with a personal message, tasting notes card, and brewing guide."). **columnsgrid** (2 columns) with **image** + **heading** + **caption** + **button**: "Single Origin Gift Box" / "INR 750 (250g + tasting card + brew guide)" / "Add to Bag", "Coffee Enthusiast Hamper" / "INR 2,200 (3 estates + ceramic dripper + filters)" / "Add to Bag". **paragraph** ("Add a personal message at checkout.").

13. **layout-row (Reviews)** -> `comp_0_components_12`
    **eyebrow** ("Reviews"), **heading** ("What Coffee Lovers Say"). **rating** (4.6 overall, "840 reviews"). **columnsgrid** (3 columns) each with **rating**, **blockquote** (review), **caption** (reviewer + brew method used + "Verified Purchase"). **button** ("Read All Reviews").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("You Might Also Enjoy"). **columnsgrid** (4 columns) each with **image**, **heading** (coffee name), **caption** (estate + roast level + price), **button** ("Quick Add").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop (Coffee, Tea, Equipment, Merch), Learn (Brew Guides, Estate Stories, Sustainability), Account (Subscriptions, Orders, Rewards), Connect (Social, Blog, Cafe Locations). **br** (divider). **caption** (copyright, "Freshly Roasted in India").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a limited-edition gourmet product launch

**Page: Limited Release Launch (e.g., "Nespresso -- Exclusive Sumatra Mandheling Vertuo")**

1. **titlebar** -- Brand logo, minimal nav (The Coffee, The Origin, Taste, Order), "Order Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic footage of Sumatra highlands, coffee cherry picking, rain on canopy, cup being poured). Overlay: **eyebrow** ("Limited Edition | Master Origin"), **heading** ("Sumatra Mandheling"), **paragraph** ("From the volcanic highlands of Lake Toba. Intensity 10."), **badge** ("Limited Quantity"), **button** ("Order Now"), **countdown** (until stock runs out or season ends).

3. **layout-row (Intensity & Flavor)** -- Dark background. **heading** ("A Bold, Earthy Cup"). **columnsgrid** (3 columns) with large **heading** + **caption** flavor notes: "Dark Cocoa" / "Bittersweet depth", "Wet Earth" / "Distinctive Sumatran terroir", "Tobacco Leaf" / "Smoky, complex finish". **progress-bar** labeled "Intensity" at 100% (10/13 scale visual).

4. **layout-row (Origin Story)** -- Split screen: **image** (Sumatran farmer portrait at Lake Toba) + **eyebrow** ("The People") + **heading** ("Giling Basah Process") + **paragraph** ("Wet-hulled by Batak farming cooperatives using a centuries-old technique unique to Sumatra."). **counter-up** stats: "1500" / "Meters Altitude", "300" / "Farming Families", "1" / "Harvest Per Year".

5. **layout-row (Sustainability)** -- **heading** ("AAA Sustainable Quality Program"), **columnsgrid** (3 columns) with **icon** + **caption**: "Carbon Neutral by 2025", "Aluminum Capsule 100% Recyclable", "Fair Price Premium to Farmers". **image** (recycling program visual).

6. **layout-row (Recipe Suggestions)** -- **heading** ("Barista Creations"), **carousel** (recipe cards -- Flat White, Iced Latte, Affogato -- each with **image** + brief recipe).

7. **layout-row (Order CTA)** -- **heading** ("Available While Stocks Last"), **columnsgrid** (2 columns) with pack sizes and prices, **button** ("Add to Bag"), **caption** ("Compatible with Vertuo and Vertuo Next machines").

8. **layout-row (Footer)** -- Minimal footer with machine compatibility, recycling info, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a gourmet food brand's full collection

**Page: Brand Collection (e.g., "Fortnum & Mason -- All Teas")**

1. **titlebar** -- Brand logo, nav (Black Tea, Green Tea, Herbal, Chai, Iced, Gift Sets, Tea Accessories), search, "Afternoon Tea Experience" button.

2. **layout-row (Hero)** -- **heading** ("The World in a Cup"), **paragraph** ("Since 1707, Fortnum's has sourced the world's finest teas, blended by our master tea blender"), **image** (editorial -- ornate tea caddy with loose leaf tea spilling, fine china cup, Fortnum's interior). **button** ("Take the Tea Finder Quiz").

3. **layout-row (Filter Bar)** -- **tabs** (By Type: "Black", "Green", "Oolong", "White", "Herbal", "Chai") each filtering the product grid.

4. **layout-row (Category: Signature Blends)** -- **eyebrow** ("House Blends"), **heading** ("Fortnum's Signatures"). **columnsgrid** (3 columns) each card: **image** (tea caddy), **badge** ("Bestseller" / "New" / "Award Winner" where applicable), **heading** (blend name), **caption** (type + price + weight), **paragraph** (brief tasting note), **rating** (stars), **button** ("Shop"), **button** ("Compare").

5. **layout-row (Category: Single Estate)** -- Same card pattern. **eyebrow** ("Single Estate"), **heading** ("Garden Fresh").

6. **layout-row (Category: Herbal & Wellness)** -- Same card pattern. **eyebrow** ("Herbal & Wellness"), **heading** ("Nature's Remedies").

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Teas"). **columnsgrid** (3 columns) each with **dropdown** (select tea). Comparison rows: Origin, Caffeine Level, Steep Time, Water Temperature, Flavor Profile, Best Time of Day, Price per 100g.

8. **layout-row (Brewing Guide)** -- **heading** ("The Art of Steeping"), **columnsgrid** (5 columns) with **icon** + **heading** + **caption** per tea type: "Black" / "100C, 4 min", "Green" / "80C, 2 min", "Oolong" / "90C, 3 min", "White" / "75C, 5 min", "Herbal" / "100C, 5+ min".

9. **layout-row (Gift Builder)** -- **heading** ("Create a Tea Hamper"), **paragraph** ("Choose teas, add biscuits, select a hamper box"), **image** (gift hamper), **button** ("Build Your Hamper"). **counter-up** + **caption**: "300" / "Years of Gifting Tradition".

10. **layout-row (Footer)** -- Full footer with tea collections, food hall, afternoon tea booking, corporate gifts, social links, legal. **caption** ("Purveyors of fine teas since 1707").
