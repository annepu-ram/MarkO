# Cars & Automobiles -- Product Pages

> Focus: Feature-by-feature vehicle showcase with trackable sections for engine, design, safety, comfort, and configurator CTAs that let dealerships measure which specs drive test-drive bookings.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Hyundai Creta | hyundai.co.in/creta | Full-width hero with rotating angles, sticky "Book Now" bar, feature sections with parallax scroll, 360-degree exterior/interior viewer |
| Tata Nexon | tatamotors.com/nexon | Bold color-banded feature sections, animated spec counters (bhp, torque, mileage), variant comparison table at bottom |
| Maruti Suzuki Brezza | marutisuzuki.com/brezza | Video background hero, icon-grid feature highlights, downloadable brochure CTA, EMI calculator widget |
| Tesla Model 3 | tesla.com/model3 | Minimal dark design, full-bleed lifestyle imagery per feature, "Order Now" sticky CTA, performance stats animated on scroll |
| BMW 3 Series | bmw.in/3series | Cinematic video hero, tabbed specs (engine/dimensions/features), configurator link, dealer locator integration |

**Patterns to incorporate:**
- Full-bleed hero with car image + one-line tagline and price starting point
- Each feature section alternates image-left/image-right layout for visual rhythm
- Animated counter-up stats for horsepower, mileage, and safety ratings
- Sticky "Book Test Drive" CTA that follows user scroll
- Color/variant selector with live image swap
- 360-degree exterior and interior viewer via carousel
- Comparison table for trim/variant differences
- EMI calculator or price breakdown accordion

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Car Model Detail (e.g., Hyundai Creta 2026)**

1. **titlebar**
   Brand logo, nav links (Models, Features, Gallery, Compare, Price, Test Drive), hamburger for mobile, "Book Now" button.

2. **layout-row (Hero -- Vehicle Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5-6 hero shots -- front 3/4, rear 3/4, side profile, action shot, studio shot). Right column: **eyebrow** ("SUV | 2026"), **heading** ("Hyundai Creta"), **paragraph** (tagline: "Bold outside. Smart inside."), **badge** ("New Launch"), **heading** (price: "Starting at Rs 10.99 Lakh*"), **button** ("Book Test Drive"), **button** ("Download Brochure"), **rating** (4.5 stars, 12,400 reviews link).

3. **layout-row (Feature 1: Engine & Power)** -> `comp_0_components_2`
   Left column: **image** (engine close-up or powertrain graphic). Right column: **eyebrow** ("Performance"), **heading** ("Power That Moves You"), **paragraph** (engine description -- turbo petrol, diesel, options), **columnsgrid** (3 columns) each with **counter-up** + **caption** (e.g., "158 bhp", "253 Nm Torque", "6-Speed AT"). **badge** ("Turbo Available").

4. **layout-row (Feature 2: Design & Exterior)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Design"), **heading** ("Unmistakably Bold"), **paragraph** (design philosophy -- connected LED DRLs, parametric grille, shark-fin antenna). Right column: **image** (exterior beauty shot with dramatic lighting). **ticker** scrolling feature callouts: "Connected LED DRLs", "R17 Diamond-Cut Alloys", "Panoramic Sunroof".

5. **layout-row (Feature 3: Interior & Comfort)** -> `comp_0_components_4`
   Full-width **image** (interior cabin shot, wide angle). Below: **columnsgrid** (4 columns) each with **image** (detail shot) + **heading** (feature name) + **caption** (description): "Ventilated Seats", "10.25-inch Touchscreen", "Bose Premium Audio", "Ambient Lighting".

6. **layout-row (Feature 4: Safety & ADAS)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Safety"), **heading** ("Protection at Every Turn"), **paragraph** (ADAS overview -- Level 2 autonomous features). **accordion** with items: "Forward Collision Avoidance", "Lane Keep Assist", "Blind Spot Monitor", "6 Airbags", "ESC + Hill Assist". Right column: **image** (safety diagram or crash test visual). **badge** ("5-Star GNCAP").

7. **layout-row (Feature 5: Mileage & Efficiency)** -> `comp_0_components_6`
   Left column: **image** (eco-driving graphic or fuel efficiency visual). Right column: **eyebrow** ("Efficiency"), **heading** ("Go Further on Every Tank"), **columnsgrid** (2 columns): Petrol column with **counter-up** ("18.4 km/l") + **caption** ("Petrol MT"), Diesel column with **counter-up** ("21.8 km/l") + **caption** ("Diesel MT"). **progress-bar** (fuel efficiency rating visual, 85%). **paragraph** (driving modes explanation -- Eco, City, Sport).

8. **layout-row (Feature 6: Infotainment & Tech)** -> `comp_0_components_7`
   Left column: **eyebrow** ("Technology"), **heading** ("Stay Connected, Stay Ahead"), **paragraph** (infotainment features -- wireless Android Auto/CarPlay, connected car tech). **columnsgrid** (3 columns) each with **icon** + **caption**: "Wireless CarPlay", "Connected Car", "Voice Assistant". Right column: **image** (infotainment screen close-up showing navigation). **video** (tech feature demo video).

9. **layout-row (Feature 7: Price & Variants)** -> `comp_0_components_8`
   **eyebrow** ("Variants & Pricing"), **heading** ("Choose Your Creta"). **tabs** with tab per variant (E, EX, S, SX, SX(O)) each containing: **heading** (variant name + price), **paragraph** (key highlights), **columnsgrid** (feature checklist icons). **button** ("Compare Variants"). **paragraph** (disclaimer text, small).

10. **layout-row (Feature 8: Warranty & Service)** -> `comp_0_components_9`
    **columnsgrid** (3 columns): Column 1: **counter-up** ("3") + **caption** ("Years Warranty"), Column 2: **counter-up** ("1500+") + **caption** ("Service Centers"), Column 3: **counter-up** ("100000") + **caption** ("km Warranty"). **paragraph** (roadside assistance, maintenance packages). **button** ("View Service Plans").

11. **layout-row (Feature 9: Colors & Customization)** -> `comp_0_components_10`
    **eyebrow** ("Personalize"), **heading** ("Pick Your Perfect Shade"). **carousel** (car in each available color). Below carousel: **columnsgrid** (row of color swatches as small **image** tiles with **caption** color names): "Abyss Black", "Atlas White", "Titan Grey", "Fiery Red", "Robust Emerald". **paragraph** ("Dual-tone options available on SX and above").

12. **layout-row (Feature 10: Test Drive CTA)** -> `comp_0_components_11`
    Full-width **video-background** (driving footage). Overlay: **heading** ("Experience It Yourself"), **paragraph** ("Book a test drive at your nearest dealership"), **form** with **textbox** (Name), **textbox** (Phone), **dropdown** (City), **dropdown** (Preferred Variant), **calendar** (Preferred Date), **button** ("Book Test Drive").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **eyebrow** ("What Owners Say"), **heading** ("Reviews"). **rating** (4.5 overall). **columnsgrid** (3 columns) each with **blockquote** (owner review), **rating** (individual rating), **caption** (reviewer name + city). **button** ("Read All Reviews").

14. **layout-row (Related Models)** -> `comp_0_components_13`
    **heading** ("Explore More Models"). **columnsgrid** (4 columns) each with **image** (car thumbnail), **heading** (model name), **caption** (starting price), **button** ("Explore").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Quick Links, Popular Models, Connect With Us (social icons), Download App. **br** (divider). **caption** (legal disclaimers, copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new car launch event

**Page: New Model Launch (e.g., "The All-New Tata Curvv")**

1. **titlebar** -- Brand logo, minimal nav (Overview, Reserve, Locate Dealer), "Reserve Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic reveal video). Overlay: **eyebrow** ("Introducing"), **heading** ("The All-New Tata Curvv"), **paragraph** ("Born Electric. Built Bold."), **countdown** (to launch date), **button** ("Reserve Yours").

3. **layout-row (Teaser Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "500 km Range", "0-100 in 5.2s", "5-Star Safety", "30+ Connected Features".

4. **layout-row (Design Story)** -- Alternating image-text sections. **eyebrow** + **heading** ("Coupe Meets SUV"), **paragraph** (design narrative), **image** (dramatic angle shot).

5. **layout-row (Innovation)** -- **heading** ("Intelligence Redefined"), **carousel** (feature highlight slides with image + text overlay).

6. **layout-row (Color Reveal)** -- **heading** ("6 Stunning Shades"), **ticker** (car images in each color scrolling horizontally).

7. **layout-row (Reservation CTA)** -- **heading** ("Be Among the First"), **paragraph** ("Reserve with just Rs 21,000"), **button** ("Reserve Now"), **caption** ("*Fully refundable").

8. **layout-row (Footer)** -- Minimal footer with legal text, social links.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-model browsing layout for a brand's full lineup

**Page: Brand Model Lineup (e.g., "Maruti Suzuki Cars")**

1. **titlebar** -- Brand logo, nav (Hatchbacks, Sedans, SUVs, MPVs, Electric, Commercial), search, dealer locator.

2. **layout-row (Hero)** -- **heading** ("Find Your Perfect Maruti Suzuki"), **paragraph** ("Explore our complete range"), **layout-row** with filter: **dropdown** (Body Type), **dropdown** (Budget Range), **dropdown** (Fuel Type), **button** ("Search").

3. **layout-row (Category: SUVs)** -- **eyebrow** ("SUVs"), **heading** ("Adventure Starts Here"). **columnsgrid** (3 columns) each card: **image** (car), **badge** ("New"/"Bestseller" where applicable), **heading** (model name), **caption** (starting price), **rating** (stars), **paragraph** (one-line USP), **button** ("Explore"), **button** ("Compare").

4. **layout-row (Category: Hatchbacks)** -- Same card pattern as above for hatchback models.

5. **layout-row (Category: Sedans)** -- Same card pattern for sedan models.

6. **layout-row (Comparison Tool)** -- **heading** ("Compare Models Side by Side"). **columnsgrid** (3 columns): Column headers with **dropdown** (select model) each. Below: rows of specs with **paragraph** (spec name) + **paragraph** (value) per column. Specs: Price, Engine, Power, Mileage, Safety Rating, Boot Space, Transmission.

7. **layout-row (Quick Filters)** -- **tabs** (By Budget: "Under 8L", "8-12L", "12-18L", "18L+") each showing filtered **columnsgrid** of matching models.

8. **layout-row (Why Brand)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "3M+ Happy Customers", "4000+ Touchpoints", "#1 in Resale Value", "26 Years #1".

9. **layout-row (CTA)** -- **heading** ("Visit a Showroom Near You"), **form** with **textbox** (Pincode), **button** ("Find Dealer").

10. **layout-row (Footer)** -- Full footer with model links, service links, social, legal.
