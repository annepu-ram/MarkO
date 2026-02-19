# Watches -- Product Pages

> Focus: Craftsmanship storytelling with trackable sections for movement, materials, design heritage, and strap options so watch brands can measure whether buyers are drawn by technical specs, brand story, or visual appeal.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Titan | titan.co.in/product | Clean product gallery with zoom, dial color selector, strap material filter, EMI calculator, "Try On" AR feature, detailed specs accordion |
| Fossil | fossil.com/product | Lifestyle-first imagery, strap swapper with live preview, engraving personalization option, "Complete the Look" with matching accessories, membership rewards |
| Casio G-Shock | gshock.com/watches | Rugged dark theme, durability test videos, module number tech specs, shock resistance diagrams, limited edition countdown timers |
| Apple Watch | apple.com/apple-watch | Configuration builder (case + band combinations), health feature sections with data visualizations, lifestyle use-case carousel, comparison table across series |
| Rolex | rolex.com/watches | Luxury editorial photography, expansive white space, meticulous detail shots of dial/bezel/bracelet, brand heritage narrative, no prices displayed, dealer locator CTA |

**Patterns to incorporate:**
- Hero with dramatic close-up of watch face on dark background
- Movement type explanation with cutaway or X-ray diagram
- Material callouts with extreme close-up photography
- Strap/band selector with visual preview swap
- Water resistance depth rating with visual indicator
- Brand heritage story with timeline or history section
- Limited edition badge with availability countdown
- Size guide with wrist measurement reference

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Watch Detail (e.g., "Titan Nebula 18K Gold Analog Watch")**

1. **titlebar**
   Brand logo, nav links (Collections, Men, Women, Smart Watches, Accessories, Find a Store), search icon, wishlist, cart.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column (55%): **carousel** (watch face front, angled view, on-wrist lifestyle, case back showing movement, clasp detail, packaging). Right column (45%): **eyebrow** ("Nebula Collection | Women"), **heading** ("Nebula 18K Gold Analog"), **paragraph** ("Handcrafted elegance with a mother-of-pearl dial and real diamond hour markers"), **badge** ("Premium"), **rating** (4.8 stars, 320 reviews), **heading** ("Rs 1,25,000"), **caption** ("Inclusive of all taxes"), **paragraph** ("EMI from Rs 5,208/month"). Dial color selector: **columnsgrid** (row of color swatch **image** circles): "Mother of Pearl", "Rose Gold", "Midnight Blue". **button** ("Add to Cart"), **button** ("Add to Wishlist"), **caption** ("Free shipping | 2-year warranty").

3. **layout-row (Feature 1: Movement Type)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Movement"), **heading** ("Japanese Quartz Precision"), **paragraph** ("Powered by a Miyota quartz movement delivering +/- 20 seconds per month accuracy. Battery life of approximately 3 years with standard use."), **columnsgrid** (3 columns) with **icon** + **caption**: "Quartz" + "Japanese Miyota", "3 Years" + "Battery Life", "+/- 20s" + "Monthly Accuracy". Right column: **image** (case back opened showing movement mechanism, or X-ray style diagram).

4. **layout-row (Feature 2: Case Material & Size)** -> `comp_0_components_3`
   Left column: **image** (extreme close-up of case side profile showing finish and crown). Right column: **eyebrow** ("Case"), **heading** ("18K Gold-Plated Solid Brass"), **paragraph** ("36mm case diameter with a slim 7.5mm profile. Mineral crystal glass with anti-reflective coating protects the dial from scratches and glare."), **columnsgrid** (2 columns): **counter-up** ("36") + **caption** ("mm Case Diameter"), **counter-up** ("7.5") + **caption** ("mm Thickness"). **accordion** with items: "Case Material Details" (18K gold plating over solid brass), "Crystal Type" (hardened mineral crystal with AR coating), "Case Back" (stainless steel snap-fit back).

5. **layout-row (Feature 3: Dial Design)** -> `comp_0_components_4`
   **eyebrow** ("Dial"), **heading** ("A Canvas of Light"), full-width **image** (macro shot of dial showing texture, indices, and hands). Below: **paragraph** ("Mother-of-pearl dial with real diamond hour markers at 3, 6, 9, and 12. Dauphine-style hands in gold finish. Applied Titan logo at 12 o'clock."). **columnsgrid** (4 columns) detail callouts: each with **image** (cropped detail) + **caption**: "Diamond Markers", "Dauphine Hands", "Mother-of-Pearl", "Applied Logo". **badge** ("Real Diamonds").

6. **layout-row (Feature 4: Strap Options)** -> `comp_0_components_5`
   **eyebrow** ("Straps"), **heading** ("Choose Your Strap"). **columnsgrid** (3 columns) strap options: each with **image** (watch with that strap), **heading** (strap type), **paragraph** (description), **caption** (price if different): "Genuine Leather -- Tan" + "Italian calfskin with butterfly clasp" + "Included", "Mesh Bracelet -- Gold" + "Milanese mesh with adjustable clasp" + "+ Rs 3,500", "Satin Ribbon -- Black" + "Interchangeable satin with pin buckle" + "+ Rs 1,200". **paragraph** ("All straps feature quick-release spring bars for easy swapping").

7. **layout-row (Feature 5: Water Resistance)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Durability"), **heading** ("Built for Life"), **counter-up** ("30") + **caption** ("Meters Water Resistance"), **progress-bar** (water resistance level, 30% -- indicating splash-proof, not diving). **paragraph** ("Rated 3 ATM: withstands rain, hand washing, and light splashes. Not suitable for swimming or diving."). Right column: **image** (water splash on watch or resistance rating diagram). **columnsgrid** (3 columns) with **icon** + **caption**: "Rain Proof", "Splash Safe", "Hand-Wash OK".

8. **layout-row (Feature 6: Brand Story)** -> `comp_0_components_7`
   **eyebrow** ("Heritage"), **heading** ("Titan: India's Watchmaker Since 1984"). **layout-row** with **image** (brand heritage photo or factory shot) + **paragraph** (brand narrative: Tata Group subsidiary, India's largest watchmaker, 60% market share, craftsmanship tradition). **columnsgrid** (3 columns) with **counter-up** + **caption**: "40+" + "Years of Craft", "200M+" + "Watches Sold", "8000+" + "Retail Points". **blockquote** ("Every Titan watch carries a promise of precision and beauty -- passed down through four decades of Indian watchmaking.").

9. **layout-row (Feature 7: Price & Collection Positioning)** -> `comp_0_components_8`
   **eyebrow** ("Collection"), **heading** ("Nebula: Where Art Meets Time"). **paragraph** ("The Nebula collection represents Titan's luxury tier, featuring precious metals, gemstones, and limited production runs"). **tabs** with tabs per collection tier: "Nebula" (luxury), "Raga" (women's fashion), "Classique" (men's classic), "Edge" (ultra-slim). Each tab: **paragraph** (collection description), **heading** (price range), **button** ("Explore Collection").

10. **layout-row (Feature 8: Limited Edition Badge)** -> `comp_0_components_9`
    **eyebrow** ("Exclusive"), **heading** ("Limited to 500 Pieces"), **paragraph** ("Each watch is individually numbered and comes with a certificate of authenticity"). **counter-up** ("127") + **caption** ("Remaining"), **progress-bar** (sold out indicator, 75% -- 373 of 500 sold). **badge** ("Limited Edition"), **image** (numbered case back close-up). **button** ("Reserve Yours").

11. **layout-row (Feature 9: Warranty & Service)** -> `comp_0_components_10`
    **eyebrow** ("Assurance"), **heading** ("Protected Purchase"). **columnsgrid** (3 columns) each with **icon** + **heading** + **paragraph**: "2-Year Warranty" + "Comprehensive coverage against manufacturing defects", "Free Battery Replacement" + "First battery replacement complimentary at any Titan store", "Certified Service" + "Pan-India service network with 800+ centers". **accordion** with items: "Warranty Terms", "Service Center Locator", "Extended Warranty Options". **button** ("Register Your Watch").

12. **layout-row (Feature 10: Comparison with Similar)** -> `comp_0_components_11`
    **heading** ("Compare Nebula Models"). **columnsgrid** (3 columns) comparison: column headers with **image** + **heading** (model name) each. Rows of specs: Dial, Case Size, Movement, Water Resistance, Strap, Price. Each cell a **paragraph** or **caption**. **button** ("View All Nebula Watches").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Owner Reviews"). **rating** (4.8 overall, 320 reviews). **columnsgrid** (3 columns) review cards: each with **rating**, **heading** (review title), **paragraph** (review text), **caption** (reviewer name + purchase date). **button** ("Write a Review").

14. **layout-row (Related Watches)** -> `comp_0_components_13`
    **heading** ("You May Also Like"). **columnsgrid** (4 columns) each: **image** (watch), **heading** (name), **caption** (collection + price), **button** ("View").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop by Collection, Customer Service, About Titan, Connect. **br** (divider). **caption** (copyright, terms).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new watch collection or limited edition launch

**Page: Limited Edition Launch (e.g., "Casio G-Shock x [Collab] Anniversary Edition")**

1. **titlebar** -- Brand logo, minimal nav (The Watch, Heritage, Specs, Reserve), "Reserve" button.

2. **layout-row (Hero)** -- Dark background. **image** (watch on dramatic black backdrop with spotlight). **eyebrow** ("50th Anniversary"), **heading** ("G-Shock x [Collab]"), **paragraph** ("Toughness Redefined"), **countdown** (to release date), **button** ("Get Notified").

3. **layout-row (Heritage)** -- **heading** ("50 Years of Absolute Toughness"), **paragraph** (origin story of G-Shock -- the 1983 dream of a watch that never breaks). Timeline: **columnsgrid** (5 columns) with **counter-up** (year) + **caption** (milestone): "1983 Launch", "1994 Frogman", "2002 Carbon Fiber", "2018 Full Metal", "2026 Anniversary".

4. **layout-row (Durability Tests)** -- **heading** ("Tested Beyond Limits"), **video** (durability test reel -- drop, shock, water, vibration). **columnsgrid** (3 columns) with **icon** + **counter-up** + **caption**: "Shock Resistant" + "10m Drop", "Water Resistant" + "200m Depth", "Magnetic Resistant" + "2000 Gauss".

5. **layout-row (Design Details)** -- **heading** ("Every Detail Matters"), **carousel** (extreme close-ups: dial, bezel, band, case back, packaging).

6. **layout-row (Specs)** -- **heading** ("Specifications"), **accordion** (Movement, Case, Band, Functions, Size & Weight). Each expandable with detailed specs.

7. **layout-row (Reserve CTA)** -- **heading** ("Only 2,000 Pieces Worldwide"), **counter-up** ("2000") + **caption** ("Total Units"), **progress-bar** (availability, 60%), **button** ("Reserve Now -- $650"), **caption** ("Ships [date]").

8. **layout-row (Footer)** -- Minimal footer, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-watch browsing for a brand's full collection

**Page: Watch Collection (e.g., "Fossil Men's Watches")**

1. **titlebar** -- Brand logo, nav (Men, Women, Smartwatches, Jewelry, Bags, Sale), search, account, cart.

2. **layout-row (Hero)** -- **heading** ("Men's Watches"), **paragraph** ("Classic design meets modern craft"), **image** (lifestyle banner -- watches on wrist, styled).

3. **layout-row (Filter Bar)** -- **dropdown** (Style: Dress, Sport, Casual, Smart), **dropdown** (Movement: Automatic, Quartz, Solar, Smart), **dropdown** (Material: Leather, Steel, Silicone), **dropdown** (Price Range), **dropdown** (Case Size), **button** ("Filter").

4. **layout-row (Bestsellers)** -- **eyebrow** ("Bestsellers"), **ticker** (horizontal scroll of top 8 watches with **image** + **heading** + **caption** price).

5. **layout-row (Product Grid)** -- **columnsgrid** (4 columns) product cards: **image** (watch on white), **heading** (model name), **caption** (collection), **heading** (price), **badge** ("New" / "Sale"), **rating** (stars), **button** ("Shop Now").

6. **layout-row (By Collection)** -- **tabs** ("Grant", "Machine", "Neutra", "Townsman", "Hybrid HR") each with **paragraph** (collection description) + curated **columnsgrid** of watches.

7. **layout-row (Size Guide)** -- **heading** ("Find Your Fit"), **image** (wrist measurement guide), **paragraph** ("Use a flexible tape measure around your wrist bone"), **columnsgrid** (table: Wrist Size -> Recommended Case Size).

8. **layout-row (Engraving)** -- **heading** ("Make It Yours"), **paragraph** ("Free engraving on select styles"), **image** (engraved case back example), **button** ("Shop Engravable Watches").

9. **layout-row (Compare)** -- **heading** ("Compare Watches"). **columnsgrid** (3 columns) with **dropdown** (select model) each, spec rows below.

10. **layout-row (Footer)** -- Full footer with shop links, help, about, social.
