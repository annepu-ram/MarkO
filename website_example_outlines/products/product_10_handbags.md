# Handbags & Bags -- Product Pages

> Focus: Material craftsmanship, size/compartment visualization, color swatches, carry-style versatility, and brand heritage that justify premium pricing.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Coach | coach.com/shop/women/bags | Hero carousel with lifestyle shots, color swatch selector, detachable strap callouts, "Complete the Look" cross-sell section |
| Michael Kors | michaelkors.com/women/handbags | Grid-to-detail flow, structured product images on white, interior compartment photography, adjustable strap highlight |
| Hidesign | hidesign.com/collections/womens-handbags | Artisan craft story ("hand-knotted stitches"), vegetable-tanned leather callout, brass hardware closeups, heritage timeline |
| Lavie | lavieworld.com/collections/handbags-for-women | Trend-driven hero banners, occasion-based filtering (Work / Party / Casual), bold color grid, price-first layout |
| Fossil | fossil.com/en-us/bags | Material selector (leather vs. canvas), dimension diagram with ruler overlay, "What Fits Inside" visual guide |

**Patterns to incorporate:**
- High-res gallery with interior/detail shots and lifestyle context images
- Color swatch selector with instant image swap on hover
- Dimension diagram showing height x width x depth with visual scale reference
- "What Fits Inside" compartment visualization (phone, wallet, keys overlay)
- Material and hardware close-up photography as separate feature sections
- Occasion tags (Work, Weekend, Evening, Travel) for styling context
- Brand heritage/craft story section with artisan imagery
- Cross-sell "Complete the Look" or "Style It With" accessory row

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Handbag Detail**

1. **titlebar**
   Brand logo, nav links (New Arrivals, Handbags, Wallets, Accessories, Sale), search icon, wishlist icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 slides -- front, back, side, interior, strap detail, lifestyle shot). Right column: **eyebrow** ("New Arrival"), **heading** (product name), **rating** (4.5 stars, 128 reviews), **paragraph** (one-line description), **badge** ("Bestseller"), color swatch row using **button** components (Tan / Black / Burgundy / Olive), **heading** (price "$298"), **button** ("Add to Bag"), **button** ("Add to Wishlist" outline variant), **paragraph** (shipping info: "Free shipping & returns").

3. **layout-row (Feature: Material & Craft)** -> `comp_0_components_2`
   Left column: **image** (leather texture close-up). Right column: **eyebrow** ("Craftsmanship"), **heading** ("Full-Grain Italian Leather"), **paragraph** (material story -- vegetable-tanned, develops patina, hand-finished edges), **icon** + **caption** pairs for: "Vegetable Tanned", "Hand-Stitched", "Chrome-Free Dye".

4. **layout-row (Feature: Size & Compartments)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Dimensions"), **heading** ("Perfectly Sized for Every Day"), **paragraph** (H 25cm x W 32cm x D 12cm), **columnsgrid** (3 columns) with **icon** + **caption** each: "Main Zip Compartment", "2 Slip Pockets", "Interior Zip Pocket", "Pen Holder", "Key Clip", "Card Slots". Right column: **image** ("What Fits Inside" overlay -- phone, sunglasses, wallet, keys shown inside bag).

5. **layout-row (Feature: Color Options)** -> `comp_0_components_4`
   **eyebrow** ("Available In"), **heading** ("Choose Your Shade"), **columnsgrid** (4 columns) each with **image** (bag in different color), **caption** (color name: Cognac, Noir, Bordeaux, Sage), **badge** ("Limited" on one variant).

6. **layout-row (Feature: Strap & Carry Styles)** -> `comp_0_components_5`
   **heading** ("Four Ways to Carry"), **columnsgrid** (4 columns) each with **image** (model demonstrating carry style), **heading** (style name), **caption** (description): "Top Handle -- Polished and professional", "Shoulder -- Hands-free comfort", "Crossbody -- Adjustable leather strap", "Clutch -- Remove strap for evening".

7. **layout-row (Feature: Hardware Details)** -> `comp_0_components_6`
   Left column: **image** (zipper and clasp macro shot). Right column: **eyebrow** ("Details"), **heading** ("Solid Brass Hardware"), **paragraph** (custom-engraved zippers, magnetic snap closure, antique gold finish), **icon** + **caption** pairs: "Anti-Tarnish Coating", "Logo-Engraved Pulls", "Reinforced Rivets".

8. **layout-row (Feature: Brand Story)** -> `comp_0_components_7`
   Full-width **video-background** (artisan workshop footage) with overlay: **eyebrow** ("Since 1978"), **heading** ("Handcrafted with Purpose"), **paragraph** (brand heritage -- family workshop, sustainable sourcing, slow fashion philosophy), **button** ("Our Story").

9. **layout-row (Feature: Occasion Styling)** -> `comp_0_components_8`
   **heading** ("Styled for Every Moment"), **tabs** with 3 tabs: "Work" / "Weekend" / "Evening". Each tab contains **image** (styled outfit flat-lay or model) + **paragraph** (styling tips) + **button** ("Shop the Look").

10. **layout-row (Feature: Weight & Specs)** -> `comp_0_components_9`
    **heading** ("Specifications"), **columnsgrid** (2 columns). Left: spec list using **paragraph** pairs -- Weight: 580g, Closure: Magnetic Snap + Top Zip, Lining: Cotton Twill, Strap Drop: 22-26cm adjustable. Right: **image** (weight comparison infographic or bag on scale).

11. **layout-row (Feature: Price & Guarantee)** -> `comp_0_components_10`
    Left column: **heading** (price "$298"), **paragraph** ("or 4 interest-free payments of $74.50"), **button** ("Add to Bag"), **button** ("Find in Store"). Right column: **icon** + **caption** rows: "1-Year Warranty", "Free Repairs", "Authenticity Certificate", "Complimentary Dust Bag".

12. **layout-row (Feature: Authentication)** -> `comp_0_components_11`
    Left column: **eyebrow** ("Authenticity"), **heading** ("Guaranteed Genuine"), **paragraph** (serial number verification, certificate of authenticity included, QR code for product registration). Right column: **image** (authentication card and serial number detail).

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Customer Reviews"), **rating** (4.5 overall), **progress-bar** rows for 5-star through 1-star distribution, **accordion** (3 featured reviews with reviewer name, rating, date, review text, and "Verified Purchase" badge).

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your Collection"), **columnsgrid** (4 columns) each with **image**, **heading** (product name), **caption** (material), **heading** (price), **button** ("Quick View").

15. **layout-row (Footer)** -> `comp_0_components_14`
    **columnsgrid** (4 columns): Shop links, Customer Care links, About Us links, Newsletter **textbox** + **button** ("Subscribe"). **br** divider. **paragraph** (copyright).

---

## Variant B -- Product Launch / Landing Page

**Page: New Collection Launch**

1. **titlebar**
   Minimal brand logo, "New Collection" highlight link, shop CTA.

2. **layout-row (Hero -- Full Impact)**
   **video-background** (cinematic campaign video -- model walking through city with bag). Overlay: **eyebrow** ("Introducing"), **heading** ("The Atlas Collection"), **paragraph** ("Where timeless craft meets modern silhouette"), **button** ("Explore the Collection").

3. **layout-row (Collection Story)**
   Split layout. Left: **image** (designer sketch to finished product). Right: **heading** ("Designed in Milan. Crafted by Hand."), **paragraph** (collection inspiration narrative -- architecture, travel, the idea of carrying your world), **blockquote** ("Every bag should tell the story of where it's been." -- Creative Director).

4. **layout-row (Hero Product Spotlight)**
   Centered **image** (hero bag on pedestal, 360-degree feel). **heading** (product name), **paragraph** (key differentiator), **badge** ("Limited Edition"), **heading** (price), **button** ("Pre-Order Now").

5. **layout-row (Material Innovation)**
   **heading** ("A New Standard in Leather"), **columnsgrid** (3 columns): each with **image** (material swatch macro) + **heading** (material name) + **paragraph** (description -- e.g., "Pebbled Calfskin -- soft to touch, resistant to scratches").

6. **layout-row (Craft Process -- Timeline)**
   **heading** ("48 Hours of Handcraft"), **carousel** (6 slides showing production stages: leather selection, cutting, stitching, edge finishing, hardware fitting, quality inspection) each with **image** + **caption**.

7. **layout-row (Color Story)**
   **heading** ("This Season's Palette"), full-width **image** (all colorways arranged artistically), below: **ticker** scrolling color name **badge** components.

8. **layout-row (Social Proof)**
   **heading** ("As Seen On"), **ticker** (scrolling press logos -- Vogue, Elle, Harper's Bazaar), **columnsgrid** (3 columns) with **image** (influencer/celebrity carrying the bag) + **caption** (name and context).

9. **layout-row (Pre-Order CTA)**
   Dark background. **heading** ("Be the First"), **paragraph** ("Pre-order now and receive complimentary monogramming"), **button** ("Pre-Order -- $398"), **countdown** (launch date timer).

10. **layout-row (Footer)**
    Newsletter signup, social links, legal links.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Handbags Catalog**

1. **titlebar**
   Brand logo, category nav (Totes, Crossbody, Shoulder, Clutch, Backpack, Travel), search, filters, cart.

2. **layout-row (Category Hero)**
   **image** (lifestyle banner -- multiple bags styled together). **heading** ("Women's Handbags"), **paragraph** ("Find your perfect everyday companion"), **eyebrow** ("142 styles").

3. **layout-row (Filter Bar)**
   **layout-row** with **button** filters: Category, Material, Color, Size, Price Range, Sort By. **badge** showing active filter count.

4. **layout-row (Quick Compare Tool)**
   **heading** ("Compare Up To 3 Bags"), **columnsgrid** (3 columns) each with placeholder **image** + **button** ("+ Add to Compare"). Below: comparison **accordion** sections for Dimensions, Material, Compartments, Weight, Price.

5. **layout-row (Bestsellers Spotlight)**
   **eyebrow** ("Most Loved"), **heading** ("Bestselling Bags"), **carousel** (8 slides) each with **image**, **heading** (name), **rating** (stars), **heading** (price), **badge** ("Bestseller").

6. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating rows) each card: **image** (product on white), hover **image** (alternate angle), **eyebrow** (category), **heading** (product name), **caption** (material), **rating** (stars + count), **heading** (price), color dots using small **button** components, **button** ("Quick Add").

7. **layout-row (Size Guide)**
   **heading** ("Find Your Size"), **tabs** with 3 tabs: "Mini" / "Medium" / "Large". Each tab: **image** (size comparison with everyday items) + **paragraph** (dimensions) + **paragraph** (ideal for).

8. **layout-row (Material Guide)**
   **heading** ("Material Guide"), **columnsgrid** (4 columns): each with **image** (material swatch), **heading** (material name), **paragraph** (care instructions), **badge** (durability rating: "Most Durable", "Softest Feel").

9. **layout-row (Recently Viewed)**
   **heading** ("Recently Viewed"), **ticker** scrolling recently viewed product **image** + **caption** components.

10. **layout-row (Footer)**
    Store locator, customer service, brand links, newsletter signup, payment icons, social links.
