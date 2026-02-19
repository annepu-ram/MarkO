# Luxury Furniture & Decor -- Product Pages

> Focus: Heritage-driven craftsmanship storytelling with trackable sections for designer credentials, material provenance, customization options, and interior styling inspiration that let showrooms measure which artisanal details convert browsers into consultation bookings.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| B&B Italia Camaleonda | bebitalia.com/camaleonda | Full-bleed lifestyle hero with room-set photography, designer biography section, modular configuration visualizer, material swatch grid, dimensions diagram |
| Roche Bobois Aqua Table | roche-bobois.com/aqua | Cinematic video hero of marble craftsmanship, "Made in France" provenance badge, split-screen material close-ups, interior styling gallery |
| Poltrona Frau Archibald | poltronafrau.com/archibald | 21-step leather tanning process timeline, 360-degree product viewer, customizable leather/finish selector, heritage timeline since 1912 |
| BoConcept Modena | boconcept.com/modena | 3D room planner integration, 120+ fabric/leather configurator, lifestyle + studio shot toggle, delivery timeline, "Book Design Consultation" CTA |
| Minotti Freeman | minotti.com/freeman | Architectural photography with dramatic lighting, designer interview video, dimensional drawings, collection context showing full room compositions |

**Patterns to incorporate:**
- Full-bleed room-set hero photography with the piece in a styled interior
- Designer/artisan biography section with portrait and philosophy statement
- Material provenance story with origin maps and close-up texture photography
- Interactive configuration section for fabrics, leathers, finishes, and dimensions
- Craftsmanship process timeline or video showing handmade production steps
- Dimensional drawings and scale reference imagery
- Interior styling gallery showing the piece in multiple room settings
- Lead time indicator and white-glove delivery explanation
- Brand heritage timeline connecting to Italian/European design tradition
- "Book Design Consultation" or "Visit Showroom" conversion CTA

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Luxury Furniture Product Detail (e.g., Poltrona Frau Archibald Armchair)**

1. **titlebar**
   Brand logo, nav links (Collections, Designers, Craftsmanship, Showrooms, Contact), hamburger for mobile, "Book Consultation" button.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- room-set lifestyle, front angle, side profile, back detail, material close-up, dimensional view). Right column: **eyebrow** ("Armchairs | Pelle Frau Leather"), **heading** ("Archibald"), **paragraph** ("Designed by Jean-Marie Massaud. A sculptural embrace of comfort and Italian craftsmanship."), **badge** ("Handmade in Italy"), **caption** ("From EUR 5,800"), **button** ("Configure Yours"), **button** ("Book Showroom Visit"), **link** ("Download Product Sheet").

3. **layout-row (Feature 1: Designer & Artisan)** -> `comp_0_components_2`
   Left column: **image** (designer portrait -- Jean-Marie Massaud in studio). Right column: **eyebrow** ("The Designer"), **heading** ("Jean-Marie Massaud"), **paragraph** (design philosophy -- "Massaud approaches furniture as architecture at an intimate scale, seeking the essential form that merges beauty and function."), **blockquote** ("I wanted to create a chair that feels like a second skin -- protective yet liberating."), **caption** ("Collaboration with Poltrona Frau since 2009").

4. **layout-row (Feature 2: Material & Origin)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Materials"), **heading** ("Pelle Frau Heritage Leather"), **paragraph** (material story -- full-grain leather sourced from certified European tanneries, chrome-free tanning, hand-selected for uniformity and natural grain). **accordion** with items: "Leather Types (Pelle Frau, Soul, Century)", "Wood Frame (Italian Beech)", "Cushion Fill (Multi-Density Polyurethane + Goose Down)", "Metal Base (Die-Cast Aluminum)". Right column: **image** (close-up leather texture shot with visible grain). **badge** ("FSC Certified Wood"). **badge** ("Chrome-Free Tanning").

5. **layout-row (Feature 3: Dimensions & Scale)** -> `comp_0_components_4`
   Left column: **image** (dimensional line drawing with measurements annotated). Right column: **eyebrow** ("Specifications"), **heading** ("Dimensions & Scale"), **columnsgrid** (2 columns): Column 1 with **caption** ("Width") + **heading** ("86 cm"), **caption** ("Depth") + **heading** ("89 cm"); Column 2 with **caption** ("Height") + **heading** ("79 cm"), **caption** ("Seat Height") + **heading** ("42 cm"). **paragraph** ("Weight: 32 kg. Available in standard and oversized proportions."). **caption** ("Scale reference: shown beside 180 cm figure").

6. **layout-row (Feature 4: Craftsmanship Process)** -> `comp_0_components_5`
   Full-width **video** (Poltrona Frau atelier craftsmanship video). Below: **eyebrow** ("Craftsmanship"), **heading** ("21 Steps to Perfection"). **columnsgrid** (4 columns) each with **image** (process photo) + **heading** (step name) + **caption** (description): "Frame Construction" / "Hand-selected Italian beech, joined with traditional doweling", "Leather Selection" / "Each hide inspected for natural markings and consistency", "Hand Cutting" / "Master craftsman cuts leather following the grain", "Final Assembly" / "Stitched, upholstered, and inspected by a single artisan".

7. **layout-row (Feature 5: Customization Options)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Personalize"), **heading** ("Make It Yours"), **paragraph** ("Choose from over 200 leathers and fabrics, 15 wood finishes, and 8 metal options to create a piece that reflects your personal style."). **tabs** with tabs: "Leather" (grid of leather swatches as **columnsgrid** of **image** + **caption** tiles), "Fabric" (fabric swatch grid), "Wood Finish" (wood sample grid), "Metal Base" (metal finish options). Right column: **image** (the chair rendered in a custom configuration). **button** ("Request Samples"). **caption** ("Complimentary material samples shipped to your door").

8. **layout-row (Feature 6: Interior Styling)** -> `comp_0_components_7`
   **eyebrow** ("Styling Inspiration"), **heading** ("See It in Your Space"). **carousel** (6 slides showing the piece in different interior settings -- minimalist loft, classic study, modern living room, boutique hotel, penthouse, architect's office). Each slide: full-width **image** with **caption** overlay (room description + complementary pieces shown). **paragraph** ("Our interior design team can create a bespoke layout for your space. Complimentary with qualifying orders.").

9. **layout-row (Feature 7: Lead Time & Production)** -> `comp_0_components_8`
   Left column: **image** (atelier workshop wide shot). Right column: **eyebrow** ("Production"), **heading** ("Bespoke Lead Time"), **progress-bar** (showing production stages at 100% for illustration). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "8" / "Weeks Standard", "12" / "Weeks Custom Leather", "16" / "Weeks Bespoke Configuration". **paragraph** ("Each piece is made to order in our Tolentino atelier. Your dedicated production coordinator will provide regular updates."). **badge** ("Made to Order").

10. **layout-row (Feature 8: Delivery & Installation)** -> `comp_0_components_9`
    Left column: **eyebrow** ("White-Glove Service"), **heading** ("Delivered with Care"), **paragraph** ("Our white-glove delivery service includes scheduled appointment, room-of-choice placement, full unpacking, assembly, and packaging removal."). **accordion** with items: "Delivery Coverage (40+ countries)", "Room-of-Choice Placement", "Professional Assembly & Setup", "Packaging Removal & Recycling", "Post-Delivery Inspection". Right column: **image** (delivery team carefully placing furniture in a home). **icon** (shield icon) + **caption** ("Fully insured transit").

11. **layout-row (Feature 9: Price & Investment)** -> `comp_0_components_10`
    **eyebrow** ("Investment"), **heading** ("Pricing"). **tabs** with tab per configuration: "Pelle Frau Leather" (EUR 5,800), "Soul Leather" (EUR 6,400), "Century Leather" (EUR 7,200), "COM (Customer's Own Material)" (EUR 5,200). Each tab: **heading** (configuration + price), **paragraph** (what's included), **caption** (lead time for this option). **button** ("Configure & Quote"). **paragraph** ("Financing available. Interior trade pricing on request."). **caption** ("*Prices exclude delivery. VAT included where applicable.").

12. **layout-row (Feature 10: Brand Heritage)** -> `comp_0_components_11`
    Left column: **image** (historic Poltrona Frau archival photo from 1912). Right column: **eyebrow** ("Heritage"), **heading** ("Since 1912"), **paragraph** ("Renzo Frau founded Poltrona Frau in Turin with a vision to create furniture of uncompromising quality. Over a century later, every piece still bears the founder's commitment to excellence."). **columnsgrid** (4 columns) with **counter-up** + **caption**: "112" / "Years of Craft", "200+" / "Leather Colors", "80+" / "Countries", "1" / "Founding Vision". **link** ("Explore Our Heritage").

13. **layout-row (Reviews & Testimonials)** -> `comp_0_components_12`
    **eyebrow** ("Client Voices"), **heading** ("What Our Clients Say"). **columnsgrid** (3 columns) each with **blockquote** (client testimonial), **rating** (5 stars), **caption** (client name + location + "Verified Purchase"). **button** ("Read All Reviews").

14. **layout-row (Related Collection)** -> `comp_0_components_13`
    **heading** ("Complete the Collection"). **columnsgrid** (4 columns) each with **image** (complementary piece), **heading** (product name), **caption** (designer + starting price), **button** ("View").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Collections, Designers & Craftsmanship, Showroom Locator, Client Services. **br** (divider). **caption** (copyright, legal, "Made in Italy" mark).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new luxury furniture collection launch

**Page: New Collection Launch (e.g., "B&B Italia -- The Camaleonda Reissue")**

1. **titlebar** -- Brand logo, minimal nav (The Collection, Craftsmanship, Configure, Showrooms), "Reserve" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic atelier footage showing artisans crafting the piece, ending with finished product in a stunning interior). Overlay: **eyebrow** ("A Design Icon Returns"), **heading** ("Camaleonda"), **paragraph** ("Originally designed by Mario Bellini in 1970. Reimagined for today."), **button** ("Explore the Collection").

3. **layout-row (Design Heritage)** -- Split screen: **image** (1970 original archival photo) on left, **image** (2026 reissue in contemporary interior) on right. **heading** ("1970 -- 2026"), **paragraph** ("Fifty-six years of modular innovation. Same soul, new sustainability.").

4. **layout-row (Modular Story)** -- **eyebrow** ("Infinite Configurations"), **heading** ("One Design. Endless Possibilities."). **carousel** (configurations -- 2-seater, corner, chaise, island, daybed). **counter-up** stats in **columnsgrid**: "1000+" / "Configurations", "8" / "Module Types", "200+" / "Fabrics & Leathers".

5. **layout-row (Sustainability)** -- **heading** ("Crafted for Generations"), **paragraph** (recycled foam, FSC wood, chrome-free leather). **columnsgrid** (3 columns) with **icon** + **caption**: "Recyclable Materials", "Carbon-Neutral Shipping", "Lifetime Repair Service".

6. **layout-row (Configurator CTA)** -- Dark background. **heading** ("Design Your Camaleonda"), **paragraph** ("Start with a base module and build your perfect sofa"), **image** (configurator preview), **button** ("Open Configurator"), **button** ("Visit Showroom").

7. **layout-row (Press Quotes)** -- **ticker** scrolling press accolades: "Architectural Digest: 'The definitive modular sofa'", "Wallpaper*: 'Bellini's masterpiece, perfected'", "Elle Decor: 'Investment furniture at its finest'".

8. **layout-row (Footer)** -- Minimal footer with showroom locator link, social links, newsletter signup, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a luxury furniture brand's full collection

**Page: Brand Collection Catalog (e.g., "Roche Bobois -- All Sofas")**

1. **titlebar** -- Brand logo, nav (Sofas, Chairs, Tables, Storage, Beds, Outdoor, Designers), search, showroom locator.

2. **layout-row (Hero)** -- **heading** ("The Art of Living"), **paragraph** ("Explore our curated collection of designer sofas, handcrafted in European ateliers"), **image** (editorial wide-shot of a styled living room with multiple pieces).

3. **layout-row (Filter Bar)** -- **layout-row** with filters: **dropdown** (Designer), **dropdown** (Material: Leather / Fabric / Velvet), **dropdown** (Style: Modern / Classic / Modular), **dropdown** (Price Range), **dropdown** (Seats: 2 / 3 / Corner / Sectional), **button** ("Apply Filters").

4. **layout-row (Category: Modular Sofas)** -- **eyebrow** ("Modular"), **heading** ("Infinite Configurations"). **columnsgrid** (3 columns) each card: **image** (product in room-set), **heading** (model name), **caption** (designer name), **caption** (starting price), **badge** ("New" / "Bestseller" / "Exclusive" where applicable), **button** ("Explore"), **button** ("Configure").

5. **layout-row (Category: Fixed Sofas)** -- Same card pattern for fixed sofa models. **eyebrow** ("Fixed Frame"), **heading** ("Timeless Silhouettes").

6. **layout-row (Category: Sectional & Corner)** -- Same card pattern. **eyebrow** ("Sectional"), **heading** ("Grand Living").

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Pieces Side by Side"). **columnsgrid** (3 columns): each with **dropdown** (select model). Below: comparison rows with **paragraph** (spec name) + **paragraph** (value) per column. Specs: Price, Designer, Material Options, Width Range, Seat Depth, Weight, Lead Time, Customization Level.

8. **layout-row (Interior Consultation CTA)** -- **heading** ("Complimentary Interior Design Service"), **paragraph** ("Our in-house designers will create a bespoke layout for your space"), **columnsgrid** (3 columns) with **counter-up** + **caption**: "500+" / "Interior Projects / Year", "40+" / "Showrooms Worldwide", "Free" / "Design Consultation". **button** ("Book Consultation").

9. **layout-row (Material Guide)** -- **tabs** (Leather, Fabric, Velvet, Outdoor) each showing **columnsgrid** of material swatches with **image** + **caption** (material name + origin). **button** ("Order Sample Kit").

10. **layout-row (Footer)** -- Full footer with collection links, designer directory, showroom locator, client services, social links, legal.
