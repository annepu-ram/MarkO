# Kitchen Appliances -- Product Pages

> Focus: Capacity and power specifications, ease of cleaning, included accessories, safety features, and recipe inspiration that bridge technical specs with everyday cooking confidence.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Philips | philips.co.in/c-m-ho/food-preparation | Feature cards with icon + short description, wattage/capacity hero stat, "What's in the box" flat-lay, recipe inspiration section with food photography |
| KitchenAid | kitchenaid.com/countertop-appliances | Color configurator for stand mixers, attachment ecosystem showcase, side-by-side model comparison, "Pinch of Help" recipe content |
| Instant Pot | instantpot.com/products | Multi-cooking modes grid with icons, capacity selector, step-by-step cooking guide, user community recipe feed |
| Bajaj | bajajelectricals.com/kitchen-appliances | Spec-first layout with wattage and jar count, price-value positioning, regional recipe suggestions, comparison chart |
| Prestige | prestigesmartchef.com | Warranty prominence, safety feature callouts (auto shut-off, cool-touch), energy star badge, accessory bundling |

**Patterns to incorporate:**
- Hero stat trio: Capacity + Wattage + Speed settings displayed prominently
- "What's in the box" flat-lay photograph of all included accessories
- Cleaning ease demonstration (dishwasher-safe parts, detachable blades)
- Multi-function cooking modes grid with descriptive icons
- Energy efficiency badge or rating with annual cost savings
- Safety feature section with certifications (BIS, UL, auto shut-off)
- Recipe inspiration cards linking appliance capability to finished dishes
- Comparison table across model lineup (Basic, Plus, Pro tiers)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Kitchen Appliance Detail**

1. **titlebar**
   Brand logo, nav links (Blenders, Mixers, Air Fryers, Cookers, Juicers, Accessories), search icon, support icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5 slides -- product front, in-use cooking shot, accessories spread, close-up control panel, kitchen countertop lifestyle). Right column: **eyebrow** ("Professional Series"), **heading** (product name "ProBlend 1200"), **rating** (4.6 stars, 1,850 reviews), **paragraph** (one-line pitch: "1200W motor with 6 pre-set programs for effortless cooking"), **badge** ("Best Seller"), color selector **button** components (Stainless Steel / Matte Black / Empire Red), **heading** (price "$189.99"), **button** ("Add to Cart"), **button** ("Find in Store" outline), **paragraph** ("Free shipping on orders over $50").

3. **layout-row (Feature: Capacity & Size)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Capacity"), **heading** ("3.5L Jug -- Serves the Whole Family"), **paragraph** (BPA-free Tritan pitcher, graduated markings, pour spout designed for drip-free pouring), **counter-up** components: "3.5L Capacity", "10 Cups", "Compact 15cm Footprint". Right column: **image** (size comparison diagram -- product next to common kitchen items with dimensions labeled: H 42cm x W 20cm x D 22cm).

4. **layout-row (Feature: Motor & Wattage)** -> `comp_0_components_3`
   Dark background. Left column: **image** (motor cross-section diagram). Right column: **eyebrow** ("Power"), **heading** ("1200W Commercial-Grade Motor"), **paragraph** (hardened steel blades spinning at 28,000 RPM, crushes ice in seconds, handles hot soups safely), **progress-bar** (power comparison: 600W Basic vs 900W Standard vs 1200W Pro -- this model highlighted), **badge** ("Most Powerful in Class").

5. **layout-row (Feature: Speed Settings)** -> `comp_0_components_4`
   **eyebrow** ("Control"), **heading** ("6 Pre-Set Programs + Variable Speed"), **columnsgrid** (3 columns, 2 rows = 6 cards) each with **icon** + **heading** + **caption**: "Smoothie -- 45 sec auto blend", "Soup -- Heat & blend in 6 min", "Ice Crush -- Pulse pattern for perfect ice", "Puree -- Ultra-smooth baby food", "Chop -- Short bursts for salsa", "Clean -- Self-cleaning in 60 sec". Below: **paragraph** ("Plus infinite variable speed dial for manual control").

6. **layout-row (Feature: Material & Build)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Build Quality"), **heading** ("Built to Last a Decade"), **paragraph** (die-cast metal base, stainless steel blades, BPA-free Tritan jar, rubber grip base prevents walking), **icon** + **caption** pairs: "Die-Cast Metal Base", "Stainless Steel Blades", "BPA-Free Tritan", "Suction Cup Feet". Right column: **image** (exploded view showing all material layers and components).

7. **layout-row (Feature: Ease of Cleaning)** -> `comp_0_components_6`
   Left column: **image** (dishwasher basket with detached blender parts). Right column: **eyebrow** ("Easy Clean"), **heading** ("Dishwasher Safe. Or Self-Cleans in 60 Seconds."), **paragraph** (removable blade assembly, wide-mouth jar for easy access, self-clean program with warm water and dish soap), **columnsgrid** (3 columns) with **icon** + **caption**: "Removable Blades", "Dishwasher Safe Parts", "Self-Clean Mode".

8. **layout-row (Feature: Accessories)** -> `comp_0_components_7`
   **heading** ("Everything You Need, Included"), **image** (flat-lay "what's in the box" photograph), **columnsgrid** (3 columns, 2 rows) each with **icon** + **heading** + **caption**: "3.5L Main Jar", "700ml Personal Cup", "Chopping Bowl", "Tamper Tool", "Spatula", "Recipe Book". Below: **heading** ("Optional Accessories"), **columnsgrid** (3 columns) with purchasable add-ons: **image** + **heading** + **heading** (price) + **button** ("Add").

9. **layout-row (Feature: Energy Efficiency)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Efficiency"), **heading** ("Energy Star Certified"), **paragraph** (consumes 30% less energy than comparable models, auto shut-off after idle, energy-saving standby mode), **badge** ("Energy Star"), **counter-up**: "30% Less Energy", "$18/yr Savings". Right column: **image** (energy rating label graphic).

10. **layout-row (Feature: Safety)** -> `comp_0_components_9`
    Left column: **image** (safety lock mechanism close-up). Right column: **eyebrow** ("Safety First"), **heading** ("Triple Safety Lock System"), **paragraph** (lid-lock detection prevents operation without lid, overload protection auto-stops motor, cool-touch exterior, non-slip base), **icon** + **caption** pairs: "Lid Lock Sensor", "Overload Protection", "Cool-Touch Body", "BIS Certified", "Anti-Slip Base".

11. **layout-row (Feature: Price & Warranty)** -> `comp_0_components_10`
    Left column: **heading** (price "$189.99"), **paragraph** ("or 3 EMIs of $63.33"), **button** ("Add to Cart"), **button** ("Buy on Amazon" outline). Right column: **icon** + **caption** rows: "5-Year Motor Warranty", "2-Year Product Warranty", "Free Replacement Parts (Year 1)", "24/7 Customer Support". **badge** ("Extended Warranty Available -- $29.99").

12. **layout-row (Feature: Recipe Ideas)** -> `comp_0_components_11`
    **eyebrow** ("Inspiration"), **heading** ("What Will You Make?"), **columnsgrid** (4 columns) each with **image** (finished dish photo), **heading** (recipe name: "Green Detox Smoothie", "Tomato Basil Soup", "Homemade Peanut Butter", "Frozen Margarita"), **caption** (time + program: "2 min -- Smoothie mode"), **button** ("View Recipe"). Below: **paragraph** ("100+ recipes included in the companion app").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Customer Reviews"), **rating** (4.6 overall), **progress-bar** rows for 5-star through 1-star distribution, **tabs** with 3 tabs: "Top Reviews" / "Most Recent" / "With Photos". Each tab: **accordion** with reviewer name, rating, date, review text, optional **image** (customer photo of dish made).

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your Kitchen"), **columnsgrid** (4 columns) each with **image**, **heading** (product name), **caption** (wattage/capacity), **heading** (price), **button** ("View Details").

15. **layout-row (Footer)** -> `comp_0_components_14`
    **columnsgrid** (4 columns): Products, Support, Company, Newsletter **textbox** + **button** ("Subscribe"). **br** divider. **paragraph** (copyright).

---

## Variant B -- Product Launch / Landing Page

**Page: New Appliance Launch**

1. **titlebar**
   Brand logo, "New Launch" badge, pre-order CTA.

2. **layout-row (Hero -- Product Reveal)**
   **video-background** (cinematic cooking montage -- ingredients going into appliance, finished dishes coming out). Overlay: **eyebrow** ("Introducing"), **heading** ("The SmartCook Pro"), **paragraph** ("10 appliances in one. One button to perfection."), **button** ("Pre-Order Now"), **countdown** (availability date).

3. **layout-row (Problem-Solution)**
   **heading** ("Your Kitchen, Simplified"), **columnsgrid** (2 columns). Left: "Before" -- **image** (cluttered countertop with multiple appliances). Right: "After" -- **image** (clean countertop with single SmartCook Pro). **paragraph** ("Replaces your blender, food processor, slow cooker, steamer, and more").

4. **layout-row (Power Story)**
   Dark background. **heading** ("1500W of Precision Power"), **image** (motor diagram with glow effect), **counter-up** components: "1500W Motor", "35,000 RPM", "10 Cooking Modes", "4.5L Capacity".

5. **layout-row (Cooking Modes Showcase)**
   **heading** ("One Machine. Endless Possibilities."), **carousel** (10 slides) each showing a cooking mode: **image** (dish made with that mode) + **heading** (mode name) + **paragraph** (description) + **caption** (cooking time).

6. **layout-row (Smart Technology)**
   **heading** ("Wi-Fi Connected. App Controlled."), split layout: left **image** (app screenshots), right **paragraph** (guided cooking, remote monitoring, recipe library with 500+ recipes, firmware updates), **button** ("Download the App").

7. **layout-row (Design & Materials)**
   **heading** ("German-Engineered. Built to Last."), **columnsgrid** (3 columns): material close-ups with **image** + **heading** + **paragraph** for: "Surgical Steel Blades", "Borosilicate Glass Jar", "Die-Cast Aluminum Base".

8. **layout-row (Chef Endorsement)**
   **blockquote** ("This is the only kitchen appliance I'd recommend to a home cook." -- Chef Name), **image** (chef portrait), **caption** (credentials).

9. **layout-row (Pre-Order Bundle)**
   **heading** ("Launch Bundle -- Save $80"), **image** (bundle contents), list of included items, **heading** (original price crossed out + launch price), **button** ("Pre-Order Bundle -- $249"), **countdown** (offer expiry).

10. **layout-row (Footer)**
    Newsletter, social, support links.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Kitchen Appliances Catalog**

1. **titlebar**
   Brand logo, category nav (Blenders, Mixers, Air Fryers, Pressure Cookers, Juicers, Food Processors), search, cart.

2. **layout-row (Category Hero)**
   **image** (kitchen lifestyle banner). **heading** ("Kitchen Appliances"), **paragraph** ("Professional-grade tools for home chefs"), **eyebrow** ("84 products").

3. **layout-row (Shop by Need)**
   **heading** ("What Are You Making?"), **columnsgrid** (4 columns) each with **image** (food category) + **heading** + **caption**: "Smoothies & Drinks -- Blenders & Juicers", "Meals & Soups -- Cookers & Processors", "Baking -- Mixers & Ovens", "Healthy Cooking -- Air Fryers & Steamers". Each card is a clickable **button**.

4. **layout-row (Model Comparison)**
   **heading** ("Compare Our Blender Range"), comparison using **columnsgrid** (4 columns). Header row: Spec / Basic / Plus / Pro. Rows for Wattage, Capacity, Speed Settings, Programs, Material, Warranty, Price -- using **paragraph** and **icon** (checkmark) components. **badge** ("Best Value") on recommended model. **button** ("Select") under each.

5. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating) each card: **image** (product on white), **badge** (category: "Blender" / "Mixer" / "Air Fryer"), **heading** (product name), **rating** (stars + count), **heading** (price), key specs using **caption** (wattage, capacity), **button** ("Add to Cart") + **button** ("Compare").

6. **layout-row (Buying Guide)**
   **heading** ("How to Choose"), **tabs** with 4 tabs: "Blenders" / "Air Fryers" / "Mixers" / "Cookers". Each tab: **image** (decision flowchart or feature diagram) + **paragraph** (what to look for: capacity for family size, wattage for food types, features by cooking style).

7. **layout-row (Bestsellers)**
   **heading** ("Customer Favorites"), **carousel** (6 slides) with product cards including **rating**, **badge** ("Top Rated"), **counter-up** ("12,000+ Sold").

8. **layout-row (Accessories & Parts)**
   **heading** ("Accessories & Replacement Parts"), **ticker** scrolling accessory cards: extra jars, blade assemblies, gaskets, lids -- each with **image** + **caption** + **heading** (price).

9. **layout-row (Recipe Hub CTA)**
   **image** (collage of dishes). **heading** ("500+ Free Recipes"), **paragraph** ("Download our app for guided cooking with any appliance"), **button** ("Explore Recipes").

10. **layout-row (Footer)**
    Product links, support, warranty info, newsletter, social, copyright.
