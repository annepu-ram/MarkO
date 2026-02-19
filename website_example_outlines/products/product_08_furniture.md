# Furniture & Home Decor -- Product Pages

> Focus: Spatial visualization and material transparency where dimensions, room context, assembly information, and fabric/finish options each get trackable sections so retailers can measure whether customers convert on room fit, material quality, or price/delivery convenience.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| IKEA | ikea.com/product | Lifestyle room-set hero photos, AR "View in Your Room" tool (IKEA Kreativ), detailed assembly info with estimated time, sustainability labels, modular configuration options |
| Urban Ladder | urbanladder.com/product | 3D room visualization tool, fabric/finish swatches with live image swap, assembly service toggle, EMI calculator, detailed dimension diagrams with room context |
| Pepperfry | pepperfry.com/product | Multiple lifestyle shots + plain background shots, AR preview in your space, customer photo reviews, delivery timeline by pincode, "Design Consultation" CTA |
| West Elm | westelm.com/product | Editorial lifestyle photography, "Shop the Room" cross-sell, fabric swatch ordering, sustainability certifications, design services CTA, registry integration |
| Wayfair | wayfair.com/product | 360-degree product viewer, "View in Room" AR, dimension overlay on images, massive review section with customer photos, financing options, room style quizzes |

**Patterns to incorporate:**
- Lifestyle room-set photography showing product in context alongside plain-background shots
- AR "View in Your Room" visualization or 3D room planner
- Detailed dimension diagram with measurements labeled
- Fabric/finish/color selector with live image swap
- Assembly information (included hardware, time estimate, service option)
- Delivery timeline calculator by location/pincode
- Customer photos showing product in real homes
- "Complete the Room" or "Shop the Look" cross-sell suggestions

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Furniture Detail (e.g., "IKEA KIVIK 3-Seat Sofa")**

1. **titlebar**
   Brand logo, nav links (Living Room, Bedroom, Dining, Office, Storage, Outdoor, Sale), search, wishlist, cart. **badge** ("Free Delivery Over $249").

2. **layout-row (Hero -- Product Gallery + Purchase Info)** -> `comp_0_components_1`
   Left column (55%): **carousel** (8 images -- sofa in styled living room, front view on white, side angle, close-up cushion detail, back view, fabric texture, lifestyle with people, room overhead shot). Right column (45%): **eyebrow** ("Sofas | Living Room"), **heading** ("KIVIK 3-Seat Sofa"), **paragraph** ("Generous seating with supportive pocket-spring cushions and durable, washable covers in your choice of fabric."), **rating** (4.4 stars, 2,180 reviews), **heading** ("$599.00"), **caption** ("Price includes cover"). Fabric selector: **columnsgrid** (row of fabric swatch **image** circles): "Tibbleby Beige", "Tresund Anthracite", "Kelinge Grey-Turquoise", "Hillared Dark Blue". **button** ("Add to Cart"), **button** ("Save to List"), **button** ("View in Your Room" -- AR CTA). **caption** ("Check delivery availability"), **textbox** (pincode input) + **button** ("Check").

3. **layout-row (Feature 1: Design & Style)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Design"), **heading** ("Clean Scandinavian Lines"), **paragraph** ("Low, wide armrests and generous seat depth create a relaxed, inviting look. Removable covers make it easy to refresh the style. Combine with KIVIK chaise and corner sections for a custom configuration."). **columnsgrid** (3 columns) with **icon** + **caption**: "Low Profile", "Wide Armrests", "Modular System". Right column: **image** (sofa in minimalist Scandinavian-styled room).

4. **layout-row (Feature 2: Material & Finish)** -> `comp_0_components_3`
   Left column: **image** (extreme close-up of fabric weave and texture). Right column: **eyebrow** ("Material"), **heading** ("Durable & Washable Covers"), **paragraph** ("Covers made from a durable cotton-polyester blend that's machine-washable. Frame built from solid wood and plywood. Legs in stained solid wood."). **accordion** with items: "Cover Material" (65% polyester, 35% cotton, 240 g/m2), "Frame Construction" (solid pine, plywood, particleboard, fiberboard), "Cushion Fill" (high-resilience foam, polyester fiber wadding), "Legs" (stained solid beech). **badge** ("Machine Washable"), **badge** ("Replaceable Covers").

5. **layout-row (Feature 3: Dimensions & Space)** -> `comp_0_components_4`
   **eyebrow** ("Dimensions"), **heading** ("Will It Fit?"). **image** (technical drawing with measurements labeled -- width, depth, height, seat height, seat depth). **columnsgrid** (2 columns): Left column specs: **paragraph** ("Width: 228 cm / 89 3/4\""), **paragraph** ("Depth: 95 cm / 37 3/8\""), **paragraph** ("Height: 83 cm / 32 5/8\""), **paragraph** ("Seat height: 45 cm / 17 3/4\""). Right column: **paragraph** ("Seat depth: 60 cm / 23 5/8\""), **paragraph** ("Seat width: 186 cm / 73 1/4\""), **paragraph** ("Weight: 67 kg / 147 lbs"), **paragraph** ("Packages: 3"). **paragraph** ("Pro tip: Leave 80-100cm walking space in front of the sofa and at least 45cm between sofa and coffee table."). **button** ("Download Dimension Guide").

6. **layout-row (Feature 4: Comfort & Ergonomics)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Comfort"), **heading** ("Sink In, Stay Awhile"), **paragraph** ("Pocket springs in the seat cushions provide even support and maintain shape over time. High-resilience foam in back cushions offers flexible lumbar support. Seat depth of 60cm accommodates various sitting positions."). **progress-bar** ("Cushion Firmness: Medium", 60%), **progress-bar** ("Back Support", 75%), **progress-bar** ("Seat Depth", 85%). Right column: **image** (cross-section diagram of cushion layers showing springs and foam). **columnsgrid** (3 columns) with **icon** + **caption**: "Pocket Springs", "Memory Foam", "Lumbar Support".

7. **layout-row (Feature 5: Assembly Info)** -> `comp_0_components_6`
   **eyebrow** ("Assembly"), **heading** ("Easy Assembly, Your Way"). **columnsgrid** (2 columns): Left: **image** (assembly illustration or opened flat-pack), **counter-up** ("45") + **caption** ("Minutes Average Assembly"), **paragraph** ("2-person assembly recommended. Allen key and basic tools included. Step-by-step instructions with clear diagrams."). Right: **heading** ("Assembly Options"), **accordion** with items: "Self-Assembly" ("Free -- tools and instructions included in package"), "IKEA Assembly Service" ("$99 -- professional assembly within 48 hours of delivery"), "TaskRabbit" ("From $69 -- book independent assembly pros"). **button** ("Book Assembly Service").

8. **layout-row (Feature 6: Color & Fabric Options)** -> `comp_0_components_7`
   **eyebrow** ("Fabrics"), **heading** ("Choose Your Cover"). **columnsgrid** (4 columns) each with **image** (sofa in that fabric), **heading** (fabric name), **caption** (material composition), **caption** (price if different). **paragraph** ("All covers are removable and machine-washable. Replacement covers available for purchase separately."). **button** ("Order Fabric Swatches -- Free"). **badge** ("Extra covers available").

9. **layout-row (Feature 7: Room Visualization)** -> `comp_0_components_8`
   **eyebrow** ("Visualize"), **heading** ("See It in Your Space"). **image** (screenshot of AR room visualization tool). **paragraph** ("Use the IKEA app to place this sofa in your room using augmented reality. See exactly how it fits with your existing furniture and decor."). **columnsgrid** (3 columns) with **image** + **caption**: "Scan Your Room", "Place Furniture", "See the Result". **button** ("Open IKEA App"), **button** ("Try IKEA Kreativ Online").

10. **layout-row (Feature 8: Care Instructions)** -> `comp_0_components_9`
    **eyebrow** ("Care"), **heading** ("Keep It Looking New"). **columnsgrid** (4 columns) with **icon** + **caption**: "Machine Wash" + "Covers at 40C, gentle cycle", "No Tumble Dry" + "Hang or line dry only", "Iron Low" + "Low heat if needed", "Vacuum Weekly" + "Remove cushions and vacuum frame". **accordion** with items: "Stain Removal Guide" (specific instructions for coffee, wine, ink, pet stains), "Seasonal Maintenance" (rotate and flip cushions monthly, vacuum under cushions), "Cover Replacement" (replacement covers available at ikea.com/covers). **paragraph** ("Tip: Apply fabric protector spray before first use for easier cleaning").

11. **layout-row (Feature 9: Price & Delivery)** -> `comp_0_components_10`
    **eyebrow** ("Purchase"), **heading** ("$599.00"). **columnsgrid** (2 columns): Left: **heading** ("Delivery Options"), **accordion** with items: "Standard Delivery" ("$49 -- 5-7 business days"), "Express Delivery" ("$99 -- 2-3 business days"), "Click & Collect" ("Free -- pick up from your local IKEA"), "Room of Choice" ("$149 -- delivered and placed in your room"). Right: **heading** ("Payment Options"), **accordion** with items: "Credit/Debit Card" (all major cards accepted), "IKEA Financing" ("$25/mo for 24 months at 0% APR"), "PayPal" (pay in full or 4 installments), "IKEA Gift Card" (accepted). **button** ("Add to Cart"). **caption** ("30-day return policy on all furniture").

12. **layout-row (Feature 10: Warranty)** -> `comp_0_components_11`
    **eyebrow** ("Guarantee"), **heading** ("10-Year Limited Warranty"). **paragraph** ("KIVIK sofas come with a 10-year limited warranty covering manufacturing defects in frame, cushions, and covers. Normal wear and tear not covered."). **columnsgrid** (3 columns) with **icon** + **heading** + **caption**: "10 Years" + "Frame Warranty", "10 Years" + "Cushion Warranty", "Lifetime" + "Cover Availability". **button** ("View Warranty Terms"). **accordion** with items: "What's Covered" (structural defects, cushion foam degradation beyond normal use), "What's Not Covered" (fabric wear, stains, accidental damage, modifications), "How to Claim" (visit store with receipt or contact customer service).

13. **layout-row (Customer Photos & Reviews)** -> `comp_0_components_12`
    **heading** ("In Real Homes"). **columnsgrid** (4 columns) customer-submitted **image** photos showing sofa in different homes and styles. Below: **heading** ("Reviews"), **rating** (4.4 overall, 2,180 reviews). **columnsgrid** (2 columns): Left: **progress-bar** per star (5-star 48%, 4-star 30%, etc.). Right: **paragraph** ("Comfort: 4.5"), **paragraph** ("Assembly: 3.8"), **paragraph** ("Value: 4.6"), **paragraph** ("Durability: 4.2"). **columnsgrid** (3 review cards) each with **rating**, **heading**, **paragraph**, **caption**. **button** ("Write a Review").

14. **layout-row (Complete the Room)** -> `comp_0_components_13`
    **heading** ("Complete Your Living Room"). **columnsgrid** (4 columns) complementary products: each with **image** + **heading** + **caption** (price) + **button** ("Add"): "LACK Coffee Table", "KALLAX Shelf Unit", "VINDSTYRKA Throw Pillow", "STOENSE Rug".

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop, Services, About IKEA, Help. **br** (divider). **caption** (copyright, legal).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new collection or designer collaboration

**Page: New Collection Launch (e.g., "Urban Ladder x Designer -- The Modern Living Collection")**

1. **titlebar** -- Brand logo, minimal nav (The Collection, Room Ideas, Shop, Stores), "Shop Now" button.

2. **layout-row (Hero)** -- Full-width **image** (editorial room photography -- entire styled room with collection pieces). Overlay: **eyebrow** ("New Collection"), **heading** ("Modern Living"), **paragraph** ("Where comfort meets contemporary design"), **button** ("Explore the Collection").

3. **layout-row (Designer Story)** -- **image** (designer portrait), **blockquote** (designer quote about the inspiration), **paragraph** (collaboration narrative -- design philosophy, materials chosen, craftsmanship).

4. **layout-row (Room Scenes)** -- **heading** ("Room by Room"). **carousel** (4 styled rooms: Living Room, Bedroom, Dining, Home Office -- each slide a full-width room photograph with shoppable item callouts).

5. **layout-row (Key Pieces)** -- **heading** ("Hero Pieces"), **columnsgrid** (3 columns) featured furniture items: **image** (lifestyle shot), **heading** (name), **caption** (price), **button** ("Shop").

6. **layout-row (Materials Story)** -- **heading** ("Responsibly Sourced"), **columnsgrid** (3 columns) with **image** (material close-up) + **heading** + **paragraph**: "FSC Certified Teak" + "Sustainably harvested from managed forests", "OEKO-TEX Fabrics" + "Certified free from harmful substances", "Natural Marble" + "Ethically quarried, hand-polished".

7. **layout-row (Free Design Consultation)** -- **heading** ("Free Design Consultation"), **paragraph** ("Book a free session with our interior design team"), **form** with **textbox** (Name), **textbox** (Email), **textbox** (Phone), **dropdown** (Room Type), **button** ("Book Free Session").

8. **layout-row (Footer)** -- Standard footer.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing for a furniture category

**Page: Sofas Catalog (e.g., "Pepperfry Sofas")**

1. **titlebar** -- Brand logo, nav (Living, Bedroom, Dining, Office, Decor, Sale), search, account, cart.

2. **layout-row (Hero)** -- **heading** ("Sofas & Couches"), **paragraph** ("1,200+ designs for every living room"), **badge** ("Up to 50% Off").

3. **layout-row (Filter Bar)** -- **dropdown** (Type: 2-Seater, 3-Seater, L-Shape, Recliner, Sofa Bed), **dropdown** (Material: Fabric, Leather, Velvet, Leatherette), **dropdown** (Seating: 2, 3, 4, 5+), **dropdown** (Color), **dropdown** (Price Range), **dropdown** (Sort By), **button** ("Apply").

4. **layout-row (Trending)** -- **eyebrow** ("Trending Now"), **ticker** (horizontal scroll of top 8 sofas with **image** + **heading** + **caption** price).

5. **layout-row (Product Grid)** -- **columnsgrid** (3 columns) product cards: **image** (sofa in room), **heading** (name), **caption** (material + seating capacity), **heading** (sale price), **caption** (original price strikethrough), **badge** ("50% Off" / "Bestseller"), **rating** (stars + count), **button** ("View"), **button** ("Add to Cart").

6. **layout-row (By Room Style)** -- **tabs** ("Modern", "Scandinavian", "Industrial", "Traditional", "Bohemian") each with curated **columnsgrid** of sofas matching that style + **paragraph** (style description).

7. **layout-row (Sofa Buying Guide)** -- **heading** ("How to Choose the Right Sofa"), **accordion** with items: "Measure Your Space" (room size guidelines), "Choose Your Material" (fabric vs leather pros/cons), "Pick Your Style" (matching your decor), "Consider Your Lifestyle" (pets, kids, entertaining), "Delivery & Assembly" (what to expect).

8. **layout-row (Compare)** -- **heading** ("Compare Sofas"), **columnsgrid** (3 columns) with **dropdown** (select sofa) each. Comparison rows: Type, Seating, Material, Dimensions, Weight Capacity, Warranty, Price.

9. **layout-row (Interior Design Service)** -- **heading** ("Free Interior Design Advice"), **paragraph** ("Our experts help you pick the perfect sofa"), **button** ("Book Free Consultation").

10. **layout-row (Footer)** -- Full footer with categories, customer service, about, social.
