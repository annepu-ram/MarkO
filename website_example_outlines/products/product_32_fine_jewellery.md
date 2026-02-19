# Fine Jewellery & Diamonds -- Product Pages

> Focus: Diamond science meets emotional storytelling with trackable sections for the 4Cs, setting design, certification, and bespoke options that let jewellers measure which trust signal or emotional trigger drives appointment bookings and engagement ring purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Tiffany & Co Engagement | tiffany.com/engagement | Clean white background, interactive diamond viewer with zoom/rotate, 4Cs education sidebar, "Complete the Look" upsell suggestions, "Book an Appointment" CTA, blue box iconography |
| Cartier Love Bracelet | cartier.com/en-us/jewelry/bracelets/love | Full-bleed editorial campaign imagery, material selector (yellow gold, white gold, rose gold), size guide overlay, "Check Availability in Store" CTA, Cartier red box heritage |
| De Beers Aura | debeers.com/en-us/high-jewellery | Diamond provenance storytelling, "Forevermark" inscription detail, 4Cs interactive explainer, GIA certification showcase, "Discover in Boutique" CTA, mine-to-finger journey |
| Tanishq | tanishq.co.in/jewellery | Product grid with "Try On" AR feature, gold purity badge (22K, 18K), Karatmeter trust seal, weight and making-charge breakdown, EMI options, "Visit a Store" locator |
| BlueStone | bluestone.com/rings | 360-degree product rotation, BIS hallmark badge, try-at-home service CTA, customization options (metal, stone, size), lifetime exchange guarantee, GIA/IGI certification filter |

**Patterns to incorporate:**
- Interactive 360-degree diamond/jewellery viewer with zoom capability
- 4Cs educational section with visual diagrams (cut brilliance, clarity scale, color grading)
- Certification badges prominently displayed (GIA, IGI, BIS Hallmark)
- Material and purity storytelling (gold karat explanation, platinum vs white gold)
- Bespoke design journey with before/after sketches and finished piece
- "Book an Appointment" or "Visit a Boutique" as primary CTA for high-value pieces
- Occasion and symbolism storytelling (engagement, anniversary, milestone)
- Insurance and valuation information for purchase confidence
- Try-on service (virtual AR or home try-on) as trust-building feature
- "Complete the Set" cross-sell (ring + band + earrings)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Fine Jewellery Detail (e.g., Tiffany Setting Engagement Ring)**

1. **titlebar**
   Maison wordmark, nav links (Engagement, Wedding Bands, Jewellery, Watches, Home, Gifts, Stores), hamburger for mobile, "Book an Appointment" button, wishlist icon, store locator.

2. **layout-row (Hero -- Product Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- ring face-on with diamond brilliance, three-quarter angle, side profile showing setting prongs, on hand lifestyle, with wedding band pairing, gift box presentation). Right column: **eyebrow** ("Engagement Rings"), **heading** ("The Tiffany Setting"), **paragraph** ("The ring that started it all. Six prongs. Maximum brilliance. Since 1886."), **caption** ("Platinum | Round Brilliant | 1.00 ct"), **rating** (4.9 stars, 3,200 reviews), **heading** ("From $13,900"), **button** ("Book an Appointment"), **button** ("Find a Store"), **button** ("Start Customizing"), **caption** ("Complimentary engraving. Lifetime diamond care.").

3. **layout-row (Feature 1: Carat, Cut, Clarity, Color -- The 4Cs)** -> `comp_0_components_2`
   **eyebrow** ("The 4Cs"), **heading** ("The Science of Brilliance"). **columnsgrid** (4 columns) each with **image** (educational diagram) + **heading** + **paragraph**: "Cut" ("The most important factor in a diamond's brilliance. Tiffany accepts only diamonds with ideal to excellent cut grades."), "Carat" ("A measure of weight, not size. A well-cut 0.90ct can appear larger than a poorly cut 1.00ct."), "Clarity" ("The presence of natural inclusions. Tiffany selects IF to VS2 grades for maximum purity."), "Color" ("Graded D (colorless) to Z. Tiffany selects D through I for exceptional transparency."). **paragraph** ("Tiffany rejects over 99.96% of gem-grade diamonds. Only the rarest meet our standard."). **badge** ("Tiffany Diamond Standard").

4. **layout-row (Feature 2: Setting & Design)** -> `comp_0_components_3`
   Left column: **image** (extreme close-up of the six-prong setting -- showing how prongs lift the diamond above the band to maximize light entry from all angles). Right column: **eyebrow** ("The Setting"), **heading** ("Six Prongs. One Revolution."), **paragraph** (setting narrative -- Charles Lewis Tiffany introduced the six-prong setting in 1886, lifting the diamond off the band to allow light to enter from every angle, creating unmatched fire and brilliance, a design so revolutionary it became simply "The Tiffany Setting"). **columnsgrid** (3 columns) each with **icon** + **caption**: "360-Degree Light Entry" ("Prongs lift diamond for maximum brilliance"), "Knife-Edge Band" ("Slender platinum band focuses attention on the diamond"), "Secure Mount" ("Six prongs provide superior security without bulk"). **counter-up** ("1886") + **caption** ("Year of the Original Tiffany Setting").

5. **layout-row (Feature 3: Metal Type & Purity)** -> `comp_0_components_4`
   Left column: **eyebrow** ("Metal"), **heading** ("Platinum -- The Purest Choice"), **paragraph** (metal narrative -- Tiffany uses 950 platinum for engagement rings, denser and more durable than white gold, naturally white color never fades or yellows, hypoallergenic). **accordion** with items: "Platinum 950 -- 95% pure platinum, the industry's highest standard", "18K Yellow Gold -- Classic warmth, 75% pure gold", "18K Rose Gold -- Romantic blush tone, copper alloy", "Comparison -- Platinum vs White Gold durability, color, and maintenance". Right column: **carousel** (same ring in different metals -- platinum, yellow gold, rose gold side by side). **badge** ("Pt950").

6. **layout-row (Feature 4: Certification -- GIA & IGI)** -> `comp_0_components_5`
   Left column: **image** (GIA certificate close-up showing grading report with plotted inclusions diagram). Right column: **eyebrow** ("Certification"), **heading** ("Independently Verified"), **paragraph** (certification narrative -- every Tiffany diamond of 0.18 carats and above comes with a Tiffany Diamond Certificate, diamonds also graded by GIA, the world's foremost independent gemological authority, laser-inscribed serial number on girdle for traceability). **columnsgrid** (3 columns) each with **image** (certification logo) + **caption**: "GIA Certified" ("The global standard in diamond grading"), "Tiffany Certificate" ("Proprietary grading that exceeds GIA standards"), "Laser Inscription" ("Unique serial number on diamond girdle, visible under magnification"). **paragraph** ("Every Tiffany diamond can be traced from mine to finger.").

7. **layout-row (Feature 5: Craftsmanship Story)** -> `comp_0_components_6`
   Full-width **video-background** (artisan at work -- diamond being set under microscope, platinum band being shaped, final polish and quality inspection). Overlay: **eyebrow** ("Craftsmanship"), **heading** ("From Master Hands"). Below: **paragraph** (craftsmanship narrative -- each Tiffany engagement ring is set by hand by a master jeweller, the prong-setting process alone takes hours of precision work under 10x magnification). **columnsgrid** (3 columns) each with **image** (process shot) + **caption**: "Diamond Setting" ("Each prong hand-shaped to cradle the diamond"), "Band Forging" ("Platinum shaped, annealed, and polished multiple times"), "Quality Inspection" ("Every ring examined at 10x magnification before release"). **counter-up** ("1500") + **caption** ("Master Artisans at Tiffany Workshops").

8. **layout-row (Feature 6: Bespoke & Custom Options)** -> `comp_0_components_7`
   **eyebrow** ("Personalize"), **heading** ("Design Your Dream Ring"). **tabs** with tabs: "Diamond Shape" (round, princess, emerald, oval, pear, cushion), "Band Style" (knife-edge, channel-set, pave, plain), "Metal" (platinum, yellow gold, rose gold), "Engraving" (personal message, date, initials). Each tab: **carousel** (options with images) + **paragraph** (description). **button** ("Start Your Custom Design"), **button** ("Book a Consultation"). **caption** ("Our gemologists guide you through every decision.").

9. **layout-row (Feature 7: Occasion & Symbolism)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Meaning"), **heading** ("A Symbol Since 1837"), **paragraph** (symbolic narrative -- the diamond engagement ring tradition, what the Tiffany Setting represents -- strength, clarity, forever, the blue box as a symbol of anticipation and joy). Right column: **image** (iconic Tiffany Blue Box being opened -- hands revealing ring inside). **blockquote** ("'The Tiffany Blue Box can make the heart beat faster.' -- The New York Sun, 1906"). **ticker** scrolling occasions: "Engagement", "Anniversary", "Push Present", "Milestone Birthday", "Self-Purchase Celebration".

10. **layout-row (Feature 8: Insurance & Valuation)** -> `comp_0_components_9`
    **eyebrow** ("Protection"), **heading** ("Insure Your Investment"). **paragraph** (insurance and valuation narrative -- complimentary appraisal document with every purchase, recommended insurance partners, Tiffany provides replacement value documentation, annual cleaning and inspection service). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Appraisal Document" ("Detailed valuation for insurance purposes"), "Lifetime Care" ("Complimentary annual cleaning and prong inspection"), "Diamond Replacement" ("Coverage available through recommended insurance partners"). **button** ("Learn About Diamond Care").

11. **layout-row (Feature 9: Price & Payment)** -> `comp_0_components_10`
    **eyebrow** ("Investment"), **heading** ("Pricing Transparency"). **paragraph** (pricing narrative -- Tiffany engagement rings range from $2,500 to over $10,000,000, price is determined primarily by the 4Cs, metal choice, and setting complexity). **tabs** with tabs: "0.5 Carat" (from $3,400), "1.0 Carat" (from $13,900), "2.0 Carat" (from $38,000), "3.0 Carat" (from $85,000). Each tab: **heading** (carat + price range), **paragraph** (what to expect at this range). **button** ("Explore by Budget"), **button** ("Book a Consultation"). **caption** ("Financing available. Complimentary shipping and returns.").

12. **layout-row (Feature 10: Try-On & Appointment)** -> `comp_0_components_11`
    **eyebrow** ("Experience"), **heading** ("See It. Try It. Love It."). **columnsgrid** (2 columns): Column 1: **image** (boutique interior -- couple viewing rings with specialist) + **heading** ("In-Store Appointment") + **paragraph** ("Private consultation with a diamond expert") + **button** ("Book an Appointment"), Column 2: **image** (virtual try-on screenshot on phone) + **heading** ("Virtual Try-On") + **paragraph** ("See rings on your hand using AR technology") + **button** ("Try On Virtually"). **caption** ("Appointments are complimentary and without obligation.").

13. **layout-row (Reviews & Love Stories)** -> `comp_0_components_12`
    **eyebrow** ("Love Stories"), **heading** ("From Our Couples"). **rating** (4.9 overall). **columnsgrid** (3 columns) each with **blockquote** (couple's engagement story mentioning the ring), **rating** (individual rating), **caption** (couple name + location). **button** ("Share Your Story").

14. **layout-row (Complete the Set)** -> `comp_0_components_13`
    **heading** ("Complete the Moment"). **columnsgrid** (4 columns) each with **image** (product), **heading** (item name), **caption** (price), **button** ("Shop"): matching wedding band, diamond earrings, pendant necklace, eternity band.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Engagement, Jewellery, Services, About Tiffany. **br** (divider). **caption** (legal, copyright, "Since 1837, New York").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new jewellery collection launch

**Page: High Jewellery Launch (e.g., "Cartier Tutti Frutti -- The New Chapter")**

1. **titlebar** -- Maison crest, minimal nav (The Collection, Craftsmanship, Heritage, Boutiques), "Request a Viewing" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic campaign -- model adorned with Tutti Frutti pieces in opulent setting, camera sweeping across gemstone details). Overlay: **eyebrow** ("High Jewellery"), **heading** ("Tutti Frutti"), **paragraph** ("Rubies. Emeralds. Sapphires. A symphony of color revived."), **button** ("Discover the Collection").

3. **layout-row (Heritage)** -- **eyebrow** + **heading** ("Born in the 1920s"), **paragraph** (Tutti Frutti origin story -- Indian-inspired carved gemstones, Art Deco era), **carousel** (archival images -- original 1920s pieces, Maharaja commissions, Daisy Fellowes necklace).

4. **layout-row (The Stones)** -- Dark background. **columnsgrid** (3 columns) each with **image** (gemstone macro) + **heading** + **caption**: "Burmese Rubies" ("The world's most prized red"), "Colombian Emeralds" ("Muzo mine, extraordinary saturation"), "Kashmir Sapphires" ("Velvety blue, unmatched rarity").

5. **layout-row (Craftsmanship)** -- **heading** ("600 Hours Per Necklace"), **video-background** (artisan carving gemstones, wire-setting, final assembly). **counter-up** stats in **columnsgrid**: "600 hrs Craft", "180 Gemstones", "1 Master Jeweller".

6. **layout-row (The Pieces)** -- **heading** ("The Collection"), **carousel** (individual pieces with editorial photography -- necklace, bracelet, earrings, ring, brooch).

7. **layout-row (Private Viewing CTA)** -- **heading** ("A Private Viewing Awaits"), **paragraph** ("Experience Tutti Frutti in the intimacy of a Cartier salon"), **button** ("Request a Viewing"), **caption** ("Available by appointment in select Cartier boutiques.").

8. **layout-row (Footer)** -- Minimal footer with maison links, social, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a jeweller's full collection

**Page: Jewellery Collection (e.g., "Tanishq Gold & Diamond Jewellery")**

1. **titlebar** -- Brand logo, nav (Gold, Diamond, Platinum, Gemstone, Bridal, Gifts, Stores), search, wishlist, cart, Karatmeter badge.

2. **layout-row (Hero)** -- **heading** ("Discover Tanishq Jewellery"), **paragraph** ("India's most trusted jewellery brand. BIS Hallmarked. Karatmeter Tested."), **image** (editorial collection spread). **layout-row** with filters: **dropdown** (Category -- Rings, Necklaces, Earrings, Bangles, Bracelets), **dropdown** (Metal -- Gold 22K, Gold 18K, Platinum, Silver), **dropdown** (Price Range), **dropdown** (Occasion -- Wedding, Daily Wear, Festive), **button** ("Search").

3. **layout-row (Category: Bridal)** -- **eyebrow** ("Bridal"), **heading** ("For Your Forever Day"). **columnsgrid** (3 columns) each card: **image** (product on model), **badge** ("Bestseller"/"New" where applicable), **heading** (collection name), **caption** (starting price + gold weight), **rating** (stars), **paragraph** (one-line description), **button** ("Shop"), **button** ("Try at Home").

4. **layout-row (Category: Diamond)** -- **eyebrow** ("Diamonds"), **heading** ("Sparkle for Every Moment"). Same card grid for diamond collections.

5. **layout-row (Category: Daily Wear)** -- **eyebrow** ("Everyday"), **heading** ("Effortless Elegance"). Same card grid for lightweight daily wear pieces.

6. **layout-row (Comparison & Education)** -- **heading** ("Understanding Gold Purity"). **tabs** (By Purity: "22K Gold", "18K Gold", "Platinum", "Silver") each showing: **paragraph** (purity explanation), **columnsgrid** of recommended pieces.

7. **layout-row (Trust Signals)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "100% BIS Hallmarked", "Karatmeter Tested", "5,000+ Designs", "400+ Stores".

8. **layout-row (Services)** -- **heading** ("Our Promise"). **columnsgrid** (4 columns) each with **icon** + **caption**: "Lifetime Exchange", "Free Try-at-Home", "Certified Diamonds", "EMI Available".

9. **layout-row (Store Locator CTA)** -- **heading** ("Find a Tanishq Store"), **form** with **textbox** (City or Pincode), **button** ("Find Store").

10. **layout-row (Footer)** -- Full footer with collection links, services, trust certifications, social, legal.
