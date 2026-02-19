# Designer Handbags -- Product Pages

> Focus: Artisan craftsmanship and exclusivity storytelling with trackable sections for leather origin, hardware details, heritage, and waitlist mechanics that let maisons measure which luxury dimension drives boutique visits and purchase desire.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Hermes Birkin | hermes.com/us/en/content/310339-hermes-iconic-bag-lines | Minimal white-space editorial layout, single hero product shot, artisan craftsmanship film, leather swatch selector, "Visit a Store" CTA (no online purchase for Birkin), saddle-stitch close-up imagery |
| Louis Vuitton Capucines | louisvuitton.com/eng-us/women/handbags/capucines | Full-bleed lifestyle editorial, material story accordion, LV monogram heritage section, "Add to Wishlist" and "Book an Appointment" CTAs, styling lookbook carousel |
| Chanel Classic Flap | chanel.com/us/fashion/handbags | Rotating 360-degree product view, quilted leather macro photography, Mademoiselle lock detail, "Find a Boutique" CTA, black-and-white editorial heritage story |
| Gucci Bamboo 1947 | gucci.com/us/en/st/capsule/gucci-bamboo-1947 | Heritage archive imagery, bamboo handle craft process video, size guide overlay, color/material selector, "Check Availability in Store" CTA, runway editorial pairing |
| Bottega Veneta Intrecciato | bottegaveneta.com/en-us/women/bags | Weave macro close-up hero, artisan hand-weaving video, minimal text with maximum product imagery, earth-tone palette, discreet branding philosophy storytelling |

**Patterns to incorporate:**
- Minimal editorial hero with single product shot on clean white or tonal background
- Artisan craftsmanship video showing hand-stitching, hand-weaving, or hand-painting process
- Leather and material origin storytelling (tannery provenance, animal welfare, vegetable tanning)
- Hardware detail macro shots (gold, palladium, ruthenium finishing)
- Size and silhouette comparison with "how it looks when worn" lifestyle imagery
- Color and seasonal availability selector with live image swap
- Heritage section connecting the bag to its founding story or iconic moment
- Exclusivity and waitlist messaging for limited-allocation pieces
- Authentication and serial number explanation for resale confidence
- "Book an Appointment" or "Visit a Store" as primary CTA (no direct e-commerce for top-tier pieces)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Designer Handbag Detail (e.g., Hermes Birkin 30)**

1. **titlebar**
   Maison wordmark, nav links (Women, Men, Home, Silk, Fragrances, Stories, Stores), hamburger for mobile, "Visit a Store" button, wishlist heart icon.

2. **layout-row (Hero -- Product Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- front face straight-on, open with interior visible, side profile showing depth, hardware close-up, bottom angle showing feet, styled with scarf accessory). Right column: **eyebrow** ("Sac Birkin"), **heading** ("Birkin 30"), **paragraph** ("Togo calfskin. Gold hardware. The quintessence of Hermes craftsmanship."), **caption** ("Togo Calfskin | 30 x 22 x 16 cm | Gold Hardware"), **heading** ("Price available in store"), **button** ("Visit a Store"), **button** ("Book an Appointment"), **caption** ("This piece is available exclusively through Hermes boutiques.").

3. **layout-row (Feature 1: Leather & Material Origin)** -> `comp_0_components_2`
   Left column: **image** (Togo calfskin texture macro -- showing natural grain, supple drape, scratch-resistance). Right column: **eyebrow** ("Material"), **heading** ("Togo Calfskin"), **paragraph** (leather narrative -- Togo calfskin sourced from the finest European tanneries, full-grain leather with natural pebbled texture, known for its durability and resistance to scratches, develops a beautiful patina over time). **accordion** with items: "Origin -- Sourced from select European tanneries with centuries of expertise", "Characteristics -- Soft yet structured, natural pebbled grain, scratch-resistant", "Aging -- Develops a unique patina that tells your personal story", "Care -- Requires minimal maintenance, occasional conditioning with Hermes-recommended products". **paragraph** ("Hermes selects only the finest 20% of hides that meet its exacting standards.").

4. **layout-row (Feature 2: Artisan Craftsmanship)** -> `comp_0_components_3`
   Full-width **video-background** (artisan at work in Hermes atelier -- hand-cutting leather, saddle-stitching with two needles, burnishing edges, attaching hardware). Overlay: **eyebrow** ("Savoir-Faire"), **heading** ("48 Hours. One Artisan. One Birkin."). Below video: **paragraph** (craftsmanship narrative -- each Birkin is handmade start to finish by a single artisan, the saddle stitch uses two waxed linen threads and two needles, a technique unchanged since the 1837 founding). **columnsgrid** (3 columns) each with **image** (process close-up) + **caption**: "Hand-Cutting" ("Each panel cut by hand from a single hide"), "Saddle Stitch" ("Two needles, two threads -- stronger than machine stitching"), "Edge Painting" ("Multiple coats of pigment, hand-burnished between layers"). **counter-up** ("48") + **caption** ("Hours of Hand Work Per Bag").

5. **layout-row (Feature 3: Hardware -- Gold & Palladium)** -> `comp_0_components_4`
   Left column: **eyebrow** ("Hardware"), **heading** ("Precious Metal, Precisely Set"), **paragraph** (hardware narrative -- each clasp, lock, key, and clochette crafted from solid brass with precious metal plating, available in gold, palladium, rose gold, and ruthenium finishes, the turn-lock closure is both functional and iconic). **columnsgrid** (2 columns) each with **image** (hardware close-up) + **heading** + **caption**: "Gold-Plated Hardware" ("Warm lustre, classic Hermes elegance"), "Palladium-Plated Hardware" ("Cool silver tone, contemporary refinement"). Right column: **carousel** (hardware details -- lock and key, clochette with stamped serial, zipper pull, base feet, sangles/straps). **caption** ("Each lock is engraved with a unique number, corresponding to its key.").

6. **layout-row (Feature 4: Size & Silhouette)** -> `comp_0_components_5`
   **eyebrow** ("Dimensions"), **heading** ("The Perfect Silhouette"). **tabs** with tab per size (Birkin 25, Birkin 30, Birkin 35, Birkin 40) each containing: **image** (size on model for scale), **heading** (size name), **paragraph** (dimensions: W x H x D), **paragraph** (ideal use -- "Evening and compact essentials" to "Travel and generous capacity"). **columnsgrid** (4 columns) each with **caption** (size) + **counter-up** (width in cm): "25 cm", "30 cm", "35 cm", "40 cm". **paragraph** ("The Birkin 30 is the most versatile, fitting everyday essentials with room to spare.").

7. **layout-row (Feature 5: Color & Season)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Colors"), **heading** ("A Palette of Possibility"), **paragraph** (color narrative -- Hermes releases new colors each season, some colors become classics while others remain seasonal exclusives, certain leathers take certain colors differently). Right column: **carousel** (Birkin in different colors -- Gold, Etoupe, Black, Bleu Nuit, Rouge Casaque, Vert Cypres, Rose Sakura). **columnsgrid** (4 columns) color swatches: each with small **image** (leather swatch) + **caption** (color name). **caption** ("Seasonal colors are available for a limited time. Consult your boutique for current availability.").

8. **layout-row (Feature 6: Brand Heritage)** -> `comp_0_components_7`
   Full-width dark background. **eyebrow** ("Heritage"), **heading** ("Since 1837"). **carousel** (heritage timeline): Slide 1: **image** (Thierry Hermes, 1837) + **caption** ("1837 -- Thierry Hermes founds the house as a harness maker"), Slide 2: **image** (first leather goods) + **caption** ("1922 -- First handbag created for Emile Hermes' wife"), Slide 3: **image** (Jane Birkin and Jean-Louis Dumas) + **caption** ("1984 -- The Birkin is born from a chance encounter on a flight"), Slide 4: **image** (modern Birkin) + **caption** ("Today -- The most iconic handbag in the world"). **blockquote** ("Jane Birkin spilled the contents of her straw bag on a plane. Jean-Louis Dumas, seated beside her, sketched the Birkin on a sick bag."). **paragraph** ("From saddler to the world's most coveted luxury house -- Hermes has never wavered from handcraft.").

9. **layout-row (Feature 7: Waiting List & Exclusivity)** -> `comp_0_components_8`
   **eyebrow** ("Exclusivity"), **heading** ("The Art of Patience"), **paragraph** (exclusivity narrative -- the Birkin is not available for online purchase or direct order, allocation is managed through boutique relationships, there is no official waiting list but rather a relationship-based system of availability). **columnsgrid** (2 columns): Column 1: **icon** + **heading** ("Boutique Relationship") + **caption** ("Building a relationship with your Sales Associate is the traditional path"), Column 2: **icon** + **heading** ("Patience & Serendipity") + **caption** ("Availability varies by color, leather, and size -- each discovery is unique"). **paragraph** ("The Birkin's rarity is not manufactured scarcity -- it is the natural result of 48 hours of handcraft per piece."). **badge** ("Boutique Exclusive").

10. **layout-row (Feature 8: Authentication & Serial)** -> `comp_0_components_9`
    Left column: **eyebrow** ("Authenticity"), **heading** ("Unmistakably Hermes"), **paragraph** (authentication details -- each Birkin bears a craftsman's stamp, a date stamp indicating year and atelier, a unique serial number on the lock, and specific construction hallmarks that experts use to verify authenticity). Right column: **image** (close-up of craftsman's stamp on interior leather). **columnsgrid** (3 columns) each with **icon** + **caption**: "Craftsman Stamp" ("Identifies the individual artisan"), "Date Code" ("Year of production and atelier"), "Lock Serial" ("Unique number matching the key"). **paragraph** ("Hermes bags can be authenticated and serviced at any Hermes boutique worldwide.").

11. **layout-row (Feature 9: Resale Value)** -> `comp_0_components_10`
    **eyebrow** ("Value"), **heading** ("An Investment in Beauty"), **paragraph** (resale and investment narrative -- the Birkin has consistently outperformed traditional investment assets, certain colors and exotic leathers achieve significant premiums at auction, Hermes bags are among the only luxury goods that reliably appreciate). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Appreciation" ("Birkins have shown consistent value appreciation over decades"), "Auction Records" ("Record-breaking prices at Christie's, Sotheby's, and Bonhams"), "Generational Heirloom" ("Designed to last a lifetime and beyond with proper care"). **caption** ("Resale value varies by condition, color, leather, and hardware. Past performance is not indicative of future value.").

12. **layout-row (Feature 10: Price & Boutique)** -> `comp_0_components_11`
    **eyebrow** ("Discover"), **heading** ("Begin Your Hermes Journey"). **paragraph** (boutique experience -- a visit to an Hermes boutique is an experience in itself, from the signature orange packaging to the personal attention of your Sales Associate). **button** ("Find a Boutique"), **button** ("Book an Appointment"). **caption** ("Pricing is available in-store. Your Sales Associate will guide you through the collection."). **image** (Hermes boutique interior -- warm wood, orange accents, scarves displayed as art).

13. **layout-row (Styling & Editorial)** -> `comp_0_components_12`
    **eyebrow** ("Style"), **heading** ("Ways to Carry"). **carousel** (editorial lifestyle shots -- Birkin styled with different outfits: business attire, casual weekend, evening wear, travel outfit). **paragraph** ("The Birkin adapts to every moment, from boardroom to boulevard.").

14. **layout-row (Related Pieces)** -> `comp_0_components_13`
    **heading** ("Complete the Ensemble"). **columnsgrid** (4 columns) each with **image** (product), **heading** (item name), **caption** (category), **button** ("Discover"): silk scarf, twilly, bag charm, card holder.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Collections, Heritage, Stores, Services. **br** (divider). **caption** (legal, copyright, "Paris, since 1837").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new handbag collection launch

**Page: New Collection Launch (e.g., "Gucci Bamboo 1947 -- Reimagined")**

1. **titlebar** -- Maison logo, minimal nav (The Bag, Craftsmanship, The Campaign, Boutiques), "Discover in Store" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic campaign film -- model walking through Italian palazzo with Bamboo bag, intercut with artisan heating bamboo in flame). Overlay: **eyebrow** ("Reimagined"), **heading** ("Bamboo 1947"), **paragraph** ("Born in Florence. Reborn for today."), **button** ("Discover the Collection").

3. **layout-row (Origin Story)** -- **eyebrow** + **heading** ("From Post-War Ingenuity"), **paragraph** (1947 material shortage story -- Guccio Gucci turned to Japanese bamboo as leather alternatives were scarce), **image** (archival 1947 original Bamboo bag photograph).

4. **layout-row (Craft Process)** -- **heading** ("Shaped by Fire"), **carousel** (craft process -- bamboo selection, flame-bending, hand-wrapping, lacquering, attachment to bag body). **counter-up** ("13") + **caption** ("Hours to Hand-Shape Each Handle").

5. **layout-row (The Collection)** -- **heading** ("Three Silhouettes"), **columnsgrid** (3 columns) each: **image** (bag variant), **heading** (name), **caption** (material + price), **button** ("Discover").

6. **layout-row (Campaign Editorial)** -- **carousel** (campaign imagery -- editorial shots from the advertising campaign, runway looks).

7. **layout-row (Boutique CTA)** -- **heading** ("Experience Bamboo 1947"), **paragraph** ("Available in select Gucci boutiques worldwide"), **button** ("Find a Boutique"), **button** ("Book an Appointment").

8. **layout-row (Footer)** -- Minimal footer with maison links, social icons, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a maison's handbag collection

**Page: Handbag Collection (e.g., "Louis Vuitton Women's Handbags")**

1. **titlebar** -- Maison monogram, nav (All Bags, Totes, Shoulder Bags, Cross-Body, Clutches, Travel, Personalization), search, wishlist, stores.

2. **layout-row (Hero)** -- **heading** ("Women's Handbags"), **paragraph** ("From iconic monogram to contemporary design -- discover your signature."), **image** (editorial flatlay of collection highlights). **layout-row** with filters: **dropdown** (Collection -- Capucines, Neverfull, Speedy, Alma, Twist), **dropdown** (Material -- Monogram Canvas, Epi Leather, Empreinte), **dropdown** (Price Range), **button** ("Filter").

3. **layout-row (Category: Iconic Collections)** -- **eyebrow** ("Icons"), **heading** ("Timeless Louis Vuitton"). **columnsgrid** (3 columns) each card: **image** (product), **badge** ("Iconic"/"New Color" where applicable), **heading** (collection name -- "Neverfull", "Speedy", "Alma"), **caption** (starting price), **paragraph** (one-line heritage description), **button** ("Shop Collection"), **button** ("Personalize").

4. **layout-row (Category: New Season)** -- **eyebrow** ("Spring 2026"), **heading** ("New Arrivals"). Same card grid for seasonal pieces.

5. **layout-row (Category: Travel)** -- **eyebrow** ("Travel"), **heading** ("The Art of Travel"). Same card grid for Keepall, Horizon, and trunk-inspired pieces.

6. **layout-row (Size & Style Guide)** -- **heading** ("Find Your Perfect Bag"). **tabs** (By Occasion: "Everyday", "Evening", "Weekend", "Travel") each showing **columnsgrid** of recommended styles with **image**, **heading**, **caption** (dimensions), **button** ("Shop").

7. **layout-row (Personalization)** -- **heading** ("Make It Yours"), **paragraph** ("Hot stamping, painting, and custom patches"), **image** (personalization examples), **button** ("Explore Personalization").

8. **layout-row (Heritage)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "170+ Years of Craft", "1 Signature Monogram", "500+ Artisans", "6 Generations of Savoir-Faire".

9. **layout-row (Boutique CTA)** -- **heading** ("Visit a Louis Vuitton Store"), **form** with **textbox** (City or Postcode), **button** ("Find a Store").

10. **layout-row (Footer)** -- Full footer with collection links, services, about, social, legal.
