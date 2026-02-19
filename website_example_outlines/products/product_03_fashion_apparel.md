# Dresses & Fashion Apparel -- Product Pages

> Focus: Visual-first shopping experience where design details, fabric close-ups, size guidance, and styling inspiration each get trackable sections so brands can measure whether customers engage more with the look, the fit, or the price.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Zara | zara.com/us/en/woman-dresses | Minimalist layout, multiple model shots from different angles, hover-to-zoom, contextual styling (model wears full outfit), quick-add size selector |
| H&M | hm.com/en_us/productpage | Clean product card, "Complete the Look" carousel below, sustainability badge, size guide modal, member pricing highlight |
| ASOS | asos.com/product | Video catwalk clip on product card, "Buy the Look" section, detailed fit info ("Model is 5'10, wearing Size 8"), saved items heart icon |
| Nykaa Fashion | nykaafashion.com/product | Indian sizing chart, customer photo reviews, "Style It With" recommendations, festive/occasion tags, EMI options |
| Myntra | myntra.com/product | Size recommendation engine, supplier rating, customer photos tab, similar products grid, "Try & Buy" badge for returns |

**Patterns to incorporate:**
- Multiple model shots (front, back, close-up, styled outfit) as primary gallery
- Video clip showing fabric movement and fit on model
- Size guide with body measurement chart and fit predictor
- "Complete the Look" / "Style It With" cross-sell section
- Fabric & care details in collapsible accordion
- Customer photos alongside text reviews
- Color/pattern variant swatches with image swap
- Occasion/event tags (Wedding, Office, Casual, Party)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Dress Detail (e.g., "Zara Satin Midi Dress")**

1. **titlebar**
   Brand logo, nav links (Women, Men, Kids, Sale, Lookbook), search icon, wishlist heart, cart bag, account icon.

2. **layout-row (Hero -- Product Gallery + Purchase Info)** -> `comp_0_components_1`
   Left column (60%): **carousel** (6 images -- front on model, back view, side profile, close-up fabric detail, styled outfit, flat lay). Right column (40%): **eyebrow** ("Women | Dresses"), **heading** ("Satin Midi Dress"), **paragraph** (brief description: "Flowing satin midi with draped neckline and adjustable straps"), **badge** ("New In"), **rating** (4.3 stars, 842 reviews), **heading** (price: "$79.90"), **caption** (strikethrough old price "$99.90" + "20% Off"), color swatches: **columnsgrid** (row of small **image** color circles with **caption**: "Emerald", "Black", "Dusty Rose", "Ivory"). Size selector: **columnsgrid** (row of **button** per size: XS, S, M, L, XL), **button** ("Add to Bag" -- primary), **button** ("Save to Wishlist" -- secondary), **caption** ("Free shipping on orders over $50").

3. **layout-row (Feature 1: Design & Silhouette)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Design"), **heading** ("Effortless Elegance"), **paragraph** (silhouette details -- midi length falls below knee, V-neckline with drape, adjustable spaghetti straps, concealed side zip, slight A-line flare). **columnsgrid** (3 columns) with **icon** + **caption**: "Midi Length", "V-Neckline", "A-Line Fit". Right column: **image** (model in motion showing drape and flow of fabric).

4. **layout-row (Feature 2: Fabric & Material)** -> `comp_0_components_3`
   Left column: **image** (extreme close-up of fabric texture and weave). Right column: **eyebrow** ("Material"), **heading** ("Luxe Satin Feel"), **paragraph** (100% recycled polyester satin, smooth hand-feel, subtle sheen, lightweight and breathable). **badge** ("Sustainable Material"). **columnsgrid** (2 columns) with **icon** + **caption**: "Recycled Polyester" + "Eco-conscious", "Lightweight" + "180 GSM".

5. **layout-row (Feature 3: Size Guide & Fit)** -> `comp_0_components_4`
   **eyebrow** ("Fit"), **heading** ("Find Your Perfect Size"). **paragraph** ("Model is 5'9\" / 175cm, wearing Size S"). **tabs** with tabs for size chart views: "Size Chart" tab with **columnsgrid** table (Size, Bust, Waist, Hip measurements in cm and inches), "Fit Guide" tab with **image** (body measurement diagram) + **paragraph** (how to measure yourself), "Fit Reviews" tab with **paragraph** ("87% of customers say this fits true to size") + **progress-bar** (true to size indicator, 87%). **caption** ("Not sure? Our 30-day free return policy has you covered").

6. **layout-row (Feature 4: Color & Pattern Options)** -> `comp_0_components_5`
   **eyebrow** ("Colors"), **heading** ("Available in 4 Shades"). **columnsgrid** (4 columns) each with **image** (dress in that color on model), **caption** (color name), **badge** ("Bestseller" on popular color). **paragraph** ("All colors available in sizes XS-XL").

7. **layout-row (Feature 5: Styling Suggestions)** -> `comp_0_components_6`
   **eyebrow** ("Style It"), **heading** ("Complete the Look"). **columnsgrid** (3 columns) each styled outfit card: **image** (model wearing dress with accessories), **heading** ("Date Night" / "Office Chic" / "Weekend Brunch"), **paragraph** (styling tip), **button** ("Shop the Look"). Below: **ticker** scrolling accessory suggestions (shoes, bags, jewelry) with **image** + **caption** + **caption** (price).

8. **layout-row (Feature 6: Care Instructions)** -> `comp_0_components_7`
   **eyebrow** ("Care"), **heading** ("Keep It Beautiful"). **columnsgrid** (4 columns) with **icon** + **caption** each: "Machine Wash Cold", "Do Not Bleach", "Low Iron", "Hang Dry". **paragraph** (additional care tips: "Store on padded hanger to maintain shape. Steam to remove wrinkles."). **accordion** with items: "Washing Instructions", "Storage Tips", "Wrinkle Removal".

9. **layout-row (Feature 7: Price & Discounts)** -> `comp_0_components_8`
   **eyebrow** ("Offers"), **heading** ("Get the Best Deal"). **columnsgrid** (2 columns): Left: **heading** ("$79.90"), **caption** (original "$99.90"), **badge** ("20% Off"), **paragraph** ("Member price: $71.91 -- Join free for 10% extra"). Right: **accordion** with items: "Delivery Options" (standard, express, store pickup), "Payment Options" (credit card, PayPal, Klarna 4 installments), "Return Policy" (30-day free returns). **button** ("Add to Bag").

10. **layout-row (Feature 8: Customer Photos)** -> `comp_0_components_9`
    **eyebrow** ("#ZaraStyle"), **heading** ("How Customers Wear It"). **columnsgrid** (4 columns) each with **image** (customer-submitted photo), **caption** (customer name + size worn). **paragraph** ("Share your look with #ZaraStyle for a chance to be featured"). **button** ("Upload Your Photo").

11. **layout-row (Feature 9: Similar Styles)** -> `comp_0_components_10`
    **heading** ("You May Also Like"). **columnsgrid** (4 columns) each card: **image** (product), **heading** (dress name), **caption** (price), **rating** (stars), **button** ("Quick Add").

12. **layout-row (Feature 10: Occasion Match)** -> `comp_0_components_11`
    **eyebrow** ("Dress For"), **heading** ("Perfect For Every Occasion"). **tabs** with occasion tabs: "Wedding Guest", "Office", "Date Night", "Casual", "Party". Each tab: **paragraph** (why this dress works), **image** (styled for that occasion), **columnsgrid** (2-3 recommended accessories). **button** ("Shop [Occasion] Edit").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Customer Reviews"). **rating** (4.3 overall, 842 reviews). **columnsgrid** (2 columns): Left: **progress-bar** per star level (5-star 52%, 4-star 28%, etc.). Right: **paragraph** ("Fit: True to Size"), **paragraph** ("Quality: Excellent"), **paragraph** ("Value: Great"). Below: **columnsgrid** (3 review cards) each with **rating**, **heading** (review title), **paragraph** (review text), **caption** (reviewer + date). **button** ("See All Reviews").

14. **layout-row (Footer)**
    **columnsgrid** (4 columns): Help, Company, Shop, Follow Us. **br** (divider). **caption** (copyright, terms, privacy).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new seasonal collection or designer collaboration

**Page: Collection Launch (e.g., "H&M x Designer Spring Collection")**

1. **titlebar** -- Brand logo, minimal nav (The Collection, Lookbook, Shop, Stores), "Shop Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (runway/campaign video). Overlay: **eyebrow** ("Spring/Summer 2026"), **heading** ("The New Edit"), **paragraph** ("Where bold meets beautiful"), **button** ("Explore Collection").

3. **layout-row (Campaign Story)** -- Alternating **image** + **paragraph** blocks telling the design inspiration story. **blockquote** (designer quote).

4. **layout-row (Key Pieces)** -- **heading** ("Hero Pieces"). **carousel** (6-8 key items from collection, each slide: large **image** + **heading** + **caption** price).

5. **layout-row (Lookbook Grid)** -- **heading** ("The Lookbook"). **columnsgrid** (3 columns, masonry-style) with editorial **image** shots, each with **caption** (item names).

6. **layout-row (Sustainability)** -- **heading** ("Conscious Choice"), **paragraph** (sustainability story), **columnsgrid** (3 columns) with **icon** + **caption**: "Organic Cotton", "Recycled Materials", "Fair Wage".

7. **layout-row (Shop by Occasion)** -- **tabs** ("Workwear", "Evening", "Weekend", "Active") each with curated **columnsgrid** product cards.

8. **layout-row (Newsletter CTA)** -- **heading** ("Get Early Access"), **form** with **textbox** (Email), **button** ("Subscribe"), **caption** ("Plus 10% off your first order").

9. **layout-row (Footer)** -- Standard footer with links, social, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a fashion category

**Page: Women's Dresses Catalog (e.g., "ASOS Dresses")**

1. **titlebar** -- Brand logo, nav (New In, Clothing, Shoes, Accessories, Sale), search bar, account, wishlist, cart.

2. **layout-row (Hero)** -- **heading** ("Dresses"), **paragraph** ("From midi to mini, satin to cotton"), **badge** ("2,400+ styles").

3. **layout-row (Filter Bar)** -- **layout-row** with: **dropdown** (Category: Midi, Maxi, Mini, Wrap), **dropdown** (Size), **dropdown** (Color), **dropdown** (Price Range), **dropdown** (Occasion), **dropdown** (Sort By), **button** ("Apply Filters").

4. **layout-row (Featured Picks)** -- **eyebrow** ("Editor's Pick"), **ticker** (horizontal scroll of 8 featured dresses with **image** + **heading** + **caption** price).

5. **layout-row (Product Grid)** -- **columnsgrid** (4 columns) repeating product cards: **image** (model wearing dress), hover **image** (back view), **heading** (dress name), **caption** (brand if multi-brand), **heading** (price), **badge** ("Sale" / "New" where applicable), **rating** (if reviewed), **button** ("Quick View").

6. **layout-row (Style Guide)** -- **heading** ("Dress by Body Type"). **tabs** ("Pear", "Hourglass", "Rectangle", "Apple") each with **paragraph** (style advice) + curated **columnsgrid** of recommended dresses.

7. **layout-row (Trending Now)** -- **heading** ("Trending This Week"). **columnsgrid** (3 columns) with top-selling items.

8. **layout-row (Size Help)** -- **heading** ("Not Sure About Sizing?"), **paragraph** ("Our size guide helps you find the right fit"), **button** ("Open Size Guide"), **caption** ("Free returns within 30 days").

9. **layout-row (Footer)** -- Full footer with delivery info, returns, help, social links.
