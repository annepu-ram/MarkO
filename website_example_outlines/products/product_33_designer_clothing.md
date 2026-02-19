# Designer Clothing & Couture -- Product Pages

> Focus: Runway-to-retail editorial storytelling with trackable sections for fabric origin, tailoring construction, silhouette, and atelier heritage that let fashion houses measure which element of creative vision drives add-to-bag conversions and boutique appointments.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Gucci Ready-to-Wear | gucci.com/us/en/ca/women/ready-to-wear | High-resolution model photography on white background, fabric detail zoom, size guide overlay, "Check Availability in Store" CTA, runway video link, styling suggestions, "Complete the Look" cross-sell |
| Dior Couture | dior.com/en_us/fashion/womens-fashion | Full-bleed campaign hero, Monsieur Dior heritage storytelling, atelier savoir-faire video, fabric macro photography, "Book an Appointment" for couture, lookbook carousel, seasonal narrative |
| Prada Ready-to-Wear | prada.com/us/en/women/ready-to-wear | Minimal editorial layout, runway show integration, fabric and technical detail accordion, size and fit guide, "Find in Store" CTA, cultural collaboration narratives |
| Sabyasachi Bridal | sabyasachi.com/collections | Rich maximalist photography, textile heritage storytelling (Indian handloom traditions), embroidery close-up carousel, "Book a Bridal Appointment" CTA, flagship experience section |
| Manish Malhotra Couture | manishmalhotra.in/collections | Campaign video hero, embellishment macro photography, celebrity editorial carousel, "Made to Measure" custom service, atelier visit booking |

**Patterns to incorporate:**
- Full-bleed runway or campaign photography as hero with seasonal collection narrative
- Fabric and textile origin storytelling (mills, weaves, heritage techniques)
- Construction detail macro shots (hand-stitching, embroidery, beadwork)
- Silhouette and fit visualization with on-model and flat-lay views
- Seasonal lookbook carousel showing styling combinations
- Atelier/maison heritage section connecting garment to design house philosophy
- Size guide with measurements, fit descriptions, and alteration options
- "Complete the Look" styling cross-sell (accessories, shoes, bags)
- Care and preservation instructions for investment pieces
- "Book a Fitting" or "Visit a Boutique" for couture and made-to-measure

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Designer Garment Detail (e.g., Dior Bar Jacket -- Spring/Summer 2026)**

1. **titlebar**
   Maison wordmark, nav links (Women, Men, Baby & Kids, Maison, Beauty, Stories, Boutiques), hamburger for mobile, "Find in Store" button, wishlist icon, shopping bag.

2. **layout-row (Hero -- Garment Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- front on model, back view showing construction, fabric detail close-up, styling with accessories, flat-lay showing shape, runway shot from show). Right column: **eyebrow** ("Spring/Summer 2026"), **heading** ("Bar Jacket in Toile de Jouy Sauvage"), **paragraph** ("An homage to Monsieur Dior's revolutionary silhouette. Reimagined for the new season in archival Toile de Jouy."), **caption** ("Cotton & Silk Blend | French Made | Regular Fit"), **heading** ("$4,500"), **button** ("Add to Bag"), **button** ("Find in Store"), **button** ("Book a Fitting"), **caption** ("Complimentary alterations. Gift wrapping available.").

3. **layout-row (Feature 1: Runway Collection)** -> `comp_0_components_2`
   Full-width **video-background** (runway show excerpt -- models walking in the full Spring/Summer 2026 collection, audience reaction, closing walk). Overlay: **eyebrow** ("The Show"), **heading** ("Spring/Summer 2026"), **paragraph** ("Creative Director Maria Grazia Chiuri explores the tension between nature and structure."). Below: **paragraph** (collection narrative -- inspiration, mood, cultural references, key pieces). **carousel** (5-6 runway look shots from the collection featuring this garment and coordinating pieces). **link** ("Watch the Full Show").

4. **layout-row (Feature 2: Fabric & Textile Origin)** -> `comp_0_components_3`
   Left column: **image** (fabric macro showing weave structure, thread count, print detail). Right column: **eyebrow** ("Fabric"), **heading** ("Toile de Jouy -- A French Tradition"), **paragraph** (textile narrative -- Toile de Jouy originated in 18th-century France at the Oberkampf manufactory in Jouy-en-Josas, this fabric is woven at a heritage mill in northern France, cotton-silk blend for structure with drape, printed using a technique that requires multiple passes). **accordion** with items: "Cotton-Silk Blend -- 65% cotton for structure, 35% silk for lustre and comfort", "Toile de Jouy Print -- Updated with Sauvage motifs featuring tropical fauna", "French Mill -- Woven at a family-owned mill operating since 1862", "Dyeing Process -- Reactive dyes for colorfastness, multiple wash tests". **badge** ("Made in France").

5. **layout-row (Feature 3: Tailoring & Construction)** -> `comp_0_components_4`
   Left column: **eyebrow** ("Construction"), **heading** ("The Architecture of Couture"), **paragraph** (tailoring narrative -- the Bar Jacket's defining feature is its sculpted waist and flared peplum, achieved through internal boning, canvas interfacing, and precise darting, construction techniques directly descended from the original 1947 New Look). **columnsgrid** (3 columns) each with **image** (construction detail) + **caption**: "Canvas Interfacing" ("Full canvas front for shape retention without stiffness"), "Hand-Set Darts" ("14 darts sculpt the waist and create the iconic silhouette"), "Boned Peplum" ("Internal boning maintains the flared structure"). Right column: **carousel** (construction close-ups -- interior showing canvas, dart seams, button attachment, hem finishing, label placement). **counter-up** ("40") + **caption** ("Hours of Construction Per Jacket").

6. **layout-row (Feature 4: Silhouette & Fit)** -> `comp_0_components_5`
   **eyebrow** ("Silhouette"), **heading** ("The New Look, Renewed"). **columnsgrid** (2 columns): Column 1: **image** (front view on model, full length showing proportions) + **caption** ("Front -- sculpted shoulders, nipped waist, flared peplum"), Column 2: **image** (side profile on model) + **caption** ("Side -- structured shoulder line, cinched waist, dramatic flare"). **paragraph** (fit description -- fitted through the shoulder and bust, nipped at natural waist, peplum falls 4 inches below waist, shoulder seam sits at natural shoulder point, single-breasted closure). **button** ("View Size Guide"). **caption** ("Available in sizes 34-46. Model wears size 38.").

7. **layout-row (Feature 5: Season & Lookbook)** -> `comp_0_components_6`
   **eyebrow** ("Lookbook"), **heading** ("Ways to Wear"). **carousel** (editorial lookbook shots showing the jacket styled multiple ways): Slide 1: **image** (with matching skirt -- formal) + **caption** ("With Toile de Jouy Midi Skirt"), Slide 2: **image** (with jeans -- casual) + **caption** ("Over Denim for Weekend Chic"), Slide 3: **image** (with evening trousers) + **caption** ("Evening: Paired with Cigarette Pants"), Slide 4: **image** (layered over dress) + **caption** ("Spring Layering: Over a Slip Dress"). **paragraph** ("The Bar Jacket transcends occasion. From the atelier to everyday.").

8. **layout-row (Feature 6: Styling Editorial)** -> `comp_0_components_7`
   Full-width **image** (editorial spread -- styled complete look with accessories). Below: **eyebrow** ("Style"), **heading** ("Complete the Look"). **columnsgrid** (4 columns) each with **image** (accessory/complementary piece) + **heading** + **caption** (price) + **button** ("Shop"): "Dior Book Tote" (matching print, $3,350), "J'Adior Slingback" (patent, $1,050), "30 Montaigne Belt" (calfskin, $720), "Toile de Jouy Scarf" (silk twill, $490). **paragraph** ("Each piece echoes the collection's dialogue between heritage and modernity.").

9. **layout-row (Feature 7: Size & Alterations)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Fit"), **heading** ("Find Your Perfect Fit"). **tabs** with tabs per measurement: "Bust" (size chart), "Waist" (size chart), "Hip" (size chart), "Length" (measurement guide). Each tab: **paragraph** (measurement instructions), **columnsgrid** (size table with measurements). Right column: **paragraph** (alteration service -- complimentary alterations on ready-to-wear purchases, sleeve length, hem, waist adjustment, first fitting within 2 weeks). **button** ("Download Size Guide"), **button** ("Book a Fitting"). **caption** ("Dior offers complimentary alterations at all boutiques.").

10. **layout-row (Feature 8: Brand Atelier Story)** -> `comp_0_components_9`
    Full-width dark background. **eyebrow** ("Atelier"), **heading** ("30 Avenue Montaigne"). **carousel** (atelier imagery): Slide 1: **image** (exterior of 30 Montaigne) + **caption** ("The Maison, since 1946"), Slide 2: **image** (1947 New Look debut) + **caption** ("February 12, 1947 -- The New Look"), Slide 3: **image** (atelier today) + **caption** ("The Dior atelier, where couture lives"), Slide 4: **image** (Maria Grazia Chiuri) + **caption** ("Maria Grazia Chiuri, Artistic Director"). **blockquote** ("'I wanted to make women beautiful again.' -- Christian Dior, 1947"). **paragraph** ("From a single revolutionary collection in 1947, Christian Dior redefined fashion. The Bar Jacket remains the maison's most iconic silhouette.").

11. **layout-row (Feature 9: Price)** -> `comp_0_components_10`
    **eyebrow** ("Pricing"), **heading** ("$4,500"). **paragraph** (value narrative -- an investment in French craftsmanship, 40 hours of construction, heritage fabric, complimentary alterations and lifetime care included). **button** ("Add to Bag"), **button** ("Book a Fitting"), **button** ("Find in Store"). **caption** ("Complimentary shipping. Gift wrapping available. Returns within 30 days."). **paragraph** ("Financing available via Klarna -- 4 interest-free installments.").

12. **layout-row (Feature 10: Care & Preservation)** -> `comp_0_components_11`
    **eyebrow** ("Care"), **heading** ("Preserve Your Investment"). **accordion** with items: "Cleaning -- Professional dry clean only. Use a specialist familiar with luxury textiles.", "Storage -- Hang on a padded hanger in a breathable garment bag. Avoid wire hangers.", "Pressing -- Steam only, never iron directly on fabric. Use a pressing cloth for delicate prints.", "Repairs -- Dior boutiques offer restoration services for buttons, linings, and structural elements.", "Seasonal Storage -- Store in a cool, dry place. Add cedar blocks for moth protection.". **paragraph** ("For specialized care, contact your nearest Dior boutique."). **button** ("Care Guide PDF").

13. **layout-row (Reviews & Styling Stories)** -> `comp_0_components_12`
    **eyebrow** ("Reviews"), **heading** ("Client Perspectives"). **rating** (4.8 overall). **columnsgrid** (3 columns) each with **blockquote** (client review -- fit, quality, how they style it), **rating** (individual rating), **caption** (reviewer, verified purchase). **button** ("Write a Review").

14. **layout-row (You May Also Love)** -> `comp_0_components_13`
    **heading** ("From the Collection"). **columnsgrid** (4 columns) each with **image** (product on model), **heading** (garment name), **caption** (price), **button** ("Shop"): complementary pieces from the same runway collection.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Women, Men, Maison, Services. **br** (divider). **caption** (legal, copyright, "Paris -- Since 1946").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new seasonal collection or couture show

**Page: Couture Collection Launch (e.g., "Sabyasachi Heritage Bridal 2026")**

1. **titlebar** -- Maison wordmark, minimal nav (The Collection, Heritage, Atelier, Appointments), "Book a Bridal Appointment" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic bridal campaign -- bride adorned in heritage lehenga, palatial Rajasthani backdrop, intricate embroidery in candlelight). Overlay: **eyebrow** ("Heritage Bridal"), **heading** ("The Udaipur Collection"), **paragraph** ("Where tradition meets artistry. Handwoven. Hand-embroidered. Handmade in India."), **button** ("Book a Bridal Appointment").

3. **layout-row (Craftsmanship Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "2,000 Hours Per Lehenga", "12 Artisan Disciplines", "100% Handloom Fabric", "3 Generations of Craft".

4. **layout-row (Heritage Textiles)** -- **eyebrow** + **heading** ("The Art of Indian Handloom"), **paragraph** (textile heritage -- Banarasi brocade, Kanjeevaram silk, hand-block printing, zardozi embroidery), **carousel** (textile process shots -- spinning, weaving, dyeing, embroidering).

5. **layout-row (The Looks)** -- **heading** ("The Collection"), **columnsgrid** (3 columns) each: **image** (complete bridal look), **heading** (look name), **caption** (textile + technique), **button** ("Enquire").

6. **layout-row (Editorial)** -- Full-width **carousel** (campaign editorial -- dramatic shots of collection in palatial settings).

7. **layout-row (Atelier Experience)** -- **heading** ("The Sabyasachi Experience"), **paragraph** ("Private bridal consultations at our Mumbai, Delhi, and Kolkata ateliers"), **image** (atelier interior), **button** ("Book an Appointment").

8. **layout-row (Footer)** -- Minimal footer with atelier locations, social, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a fashion house's seasonal collection

**Page: Seasonal Collection (e.g., "Prada Women's Spring/Summer 2026")**

1. **titlebar** -- Maison logo, nav (New Arrivals, Ready-to-Wear, Bags, Shoes, Accessories, Runway), search, wishlist, bag.

2. **layout-row (Hero)** -- **heading** ("Spring/Summer 2026"), **paragraph** ("Exploring the intersection of utility and beauty."), **video** (runway show highlight reel). **layout-row** with filters: **dropdown** (Category -- Jackets, Dresses, Tops, Trousers, Skirts, Knitwear), **dropdown** (Color), **dropdown** (Material), **dropdown** (Size), **button** ("Filter").

3. **layout-row (Category: Key Looks)** -- **eyebrow** ("Key Looks"), **heading** ("The Runway Edit"). **columnsgrid** (3 columns) each card: **image** (model shot), **heading** (garment name), **caption** (price), **badge** ("Runway" where applicable), **button** ("Shop"), **button** ("Complete the Look").

4. **layout-row (Category: Dresses)** -- **eyebrow** ("Dresses"), **heading** ("Effortless Forms"). Same card grid for dress category.

5. **layout-row (Category: Outerwear)** -- **eyebrow** ("Outerwear"), **heading** ("Structured Statements"). Same card grid for jackets and coats.

6. **layout-row (The Runway)** -- **heading** ("Watch the Show"), **video** (embedded runway show), **paragraph** (show notes from the creative director).

7. **layout-row (Style Guide)** -- **heading** ("Styled for You"). **tabs** (By Occasion: "Office", "Weekend", "Evening", "Travel") each showing curated **columnsgrid** of pieces.

8. **layout-row (Maison Values)** -- **columnsgrid** (4 columns) with **icon** + **caption**: "Responsibly Sourced", "Italian Craftsmanship", "Complimentary Alterations", "Worldwide Shipping".

9. **layout-row (Store CTA)** -- **heading** ("Visit a Prada Store"), **form** with **textbox** (City), **button** ("Find a Store").

10. **layout-row (Footer)** -- Full footer with collection links, client services, sustainability, about Prada, legal.
