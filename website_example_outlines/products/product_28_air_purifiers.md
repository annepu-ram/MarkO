# Air Purifiers & Health Tech -- Product Pages

> Focus: Technical spec-driven product showcase with trackable sections for filtration, coverage, noise, smart features, and filter lifecycle that let brands measure which health benefit drives purchase conversions.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Dyson Purifier | dyson.com/air-treatment/air-purifiers | Full-width hero with 360-degree product rotation, animated airflow visualization, side-by-side HEPA vs activated carbon comparison, sticky "Buy Now" bar |
| Mi Air Purifier | mi.com/global/product/mi-air-purifier-4-pro | Minimal white-space design, real-time AQI dashboard screenshot, CADR stats as bold counter-ups, app integration showcase, filter cross-section diagram |
| Philips Air Purifier 3000 | philips.com/c-p/AC3036_10 | Three-layer filtration explainer, room coverage calculator, allergy/asthma certification badges, before/after air quality comparison, subscription filter plan CTA |
| Coway Airmega | cowaymega.com/products/airmega-400 | Real-time air quality ring indicator, 4-stage filtration accordion breakdown, noise level comparison chart, energy star badge, washable filter highlight |
| IQAir HealthPro Plus | iqair.com/us/air-purifiers/healthpro-plus | Medical-grade positioning, HyperHEPA filtration deep-dive, hospital/lab endorsements, 3D filter cutaway, Swiss-made heritage story |

**Patterns to incorporate:**
- Hero with product on clean background + animated airflow particle visualization
- Filtration explainer using cross-section diagram or layered visual with accordion details
- CADR and coverage area as bold animated counter-up stats
- Noise level comparison (library, whisper, normal conversation) with progress-bar visualization
- Smart features showcase with app screenshot and connected device icons
- Filter lifecycle and cost-of-ownership calculator or breakdown
- Certification badges row (HEPA, Energy Star, AHAM, allergy associations)
- Real-time AQI monitoring feature demonstration with before/after air quality
- Side-by-side model comparison table for product lines

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Air Purifier Detail (e.g., Dyson Purifier Big Quiet Formaldehyde)**

1. **titlebar**
   Brand logo, nav links (Purifiers, Fans, Heaters, Humidifiers, Filters, Support), hamburger for mobile, "Shop Now" button, cart icon.

2. **layout-row (Hero -- Product Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5-6 product shots -- front view, side profile, filter exposed, top airflow, lifestyle room shot, detail close-up). Right column: **eyebrow** ("Air Purifier | 2026"), **heading** ("Dyson Purifier Big Quiet Formaldehyde"), **paragraph** (tagline: "Purifies the whole room. Quietly."), **badge** ("New"), **badge** ("HEPA H13"), **rating** (4.6 stars, 2,840 reviews), **heading** (price: "$899.99"), **button** ("Buy Now"), **button** ("Find a Store"), **caption** ("Free shipping. 30-day returns.").

3. **layout-row (Feature 1: Filtration Type -- HEPA & Carbon)** -> `comp_0_components_2`
   Left column: **image** (cross-section cutaway showing filter layers -- pre-filter, HEPA H13, activated carbon, catalytic oxidation). Right column: **eyebrow** ("Filtration"), **heading** ("4-Stage Advanced Filtration"), **paragraph** (filtration technology explanation -- captures 99.97% of particles as small as 0.3 microns, destroys formaldehyde continuously). **accordion** with items: "Pre-Filter -- Large dust and pet hair", "HEPA H13 -- Allergens, pollen, bacteria", "Activated Carbon -- VOCs, odors, NO2", "Catalytic Oxidation -- Formaldehyde destruction". **badge** ("99.97% Capture Rate").

4. **layout-row (Feature 2: Coverage Area)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Coverage"), **heading** ("Whole-Room Purification"), **paragraph** (coverage explanation -- engineered airflow projects purified air to every corner, covers up to 1,076 sq ft rooms). **counter-up** ("1076") + **caption** ("Sq Ft Coverage"). **image** (floor plan diagram showing airflow circulation arrows in room). Right column: **image** (lifestyle shot -- purifier in large living room with visible clean-air visualization).

5. **layout-row (Feature 3: CADR Rating)** -> `comp_0_components_4`
   Full-width dark background. **eyebrow** ("Performance"), **heading** ("Certified Clean Air Delivery"). **columnsgrid** (3 columns): Column 1: **counter-up** ("400") + **caption** ("Smoke CADR (CFM)"), Column 2: **counter-up** ("400") + **caption** ("Dust CADR (CFM)"), Column 3: **counter-up** ("387") + **caption** ("Pollen CADR (CFM)"). **progress-bar** (overall efficiency at 98%). **paragraph** ("Independently tested and AHAM Verifide certified."). **badge** ("AHAM Certified").

6. **layout-row (Feature 4: Noise Level)** -> `comp_0_components_5`
   Left column: **image** (sound wave visualization or bedroom scene at night). Right column: **eyebrow** ("Acoustics"), **heading** ("Engineered for Silence"), **paragraph** (noise engineering story -- acoustic baffles, helmholtz resonators, aerodynamic blade design). **columnsgrid** (2 columns): Column 1: **counter-up** ("24") + **caption** ("dBA Night Mode") + **paragraph** ("Quieter than a whisper"), Column 2: **counter-up** ("52") + **caption** ("dBA Max Speed") + **paragraph** ("Normal conversation level"). **progress-bar** (noise level visual -- 24dB positioned low on scale). **caption** ("Library: 40dB | Conversation: 60dB | Traffic: 80dB").

7. **layout-row (Feature 5: Filter Life & Cost)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Maintenance"), **heading** ("Long-Life Filters, Lower Cost"), **paragraph** (filter lifecycle details -- HEPA filter lasts 12 months, carbon filter lasts 12 months based on 12hrs/day usage). **columnsgrid** (3 columns): Column 1: **counter-up** ("12") + **caption** ("Month HEPA Life"), Column 2: **counter-up** ("12") + **caption** ("Month Carbon Life"), Column 3: **counter-up** ("69") + **caption** ("$ Replacement Cost"). Right column: **image** (filter being inserted/replaced -- easy maintenance visual). **button** ("Subscribe for Filters -- Save 15%"). **caption** ("Auto-delivery ensures you never forget.").

8. **layout-row (Feature 6: Smart Features)** -> `comp_0_components_7`
   Left column: **image** (smartphone showing app dashboard with AQI readings, filter life, scheduling). Right column: **eyebrow** ("Connected"), **heading** ("Smart Purification"), **paragraph** (app and smart home integration -- real-time AQI monitoring, auto mode, scheduling, filter reminders). **columnsgrid** (3 columns) each with **icon** + **caption**: "Auto Mode" (adjusts fan speed to air quality), "App Control" (monitor and control remotely), "Voice Assistant" (Alexa, Google, Siri). **ticker** scrolling features: "Real-Time AQI", "Filter Life Alerts", "Night Mode Schedule", "Air Quality History", "Multi-Room Control".

9. **layout-row (Feature 7: Energy Use)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Efficiency"), **heading** ("Energy Smart"), **paragraph** (energy consumption details -- low power consumption, auto mode reduces energy by adjusting to actual air quality). **columnsgrid** (2 columns): Column 1: **counter-up** ("40") + **caption** ("Watts Max Power"), Column 2: **counter-up** ("6") + **caption** ("Watts Sleep Mode"). **progress-bar** (energy efficiency rating at 92%). Right column: **image** (Energy Star certification badge and eco-friendly graphic). **badge** ("Energy Star Certified"). **caption** ("Costs less than $0.10/day to run 24/7.").

10. **layout-row (Feature 8: Display & Controls)** -> `comp_0_components_9`
    Left column: **image** (close-up of LCD display showing PM2.5, PM10, VOC, NO2 readings with color-coded AQI ring). Right column: **eyebrow** ("Interface"), **heading** ("See What You're Breathing"), **paragraph** (display features -- real-time particle count, AQI color indicator, filter life percentage, Wi-Fi status). **columnsgrid** (4 columns) each with **icon** + **caption**: "PM2.5 Sensor", "VOC Sensor", "Temperature", "Humidity". **paragraph** ("Color-coded air quality ring: Green (Good), Yellow (Fair), Orange (Poor), Red (Very Poor).").

11. **layout-row (Feature 9: Price & Models)** -> `comp_0_components_10`
    **eyebrow** ("Choose Your Purifier"), **heading** ("Find the Right Fit"). **tabs** with tab per model (Compact, Standard, Big Quiet, Big Quiet Formaldehyde) each containing: **heading** (model name + price), **paragraph** (coverage area + key differentiator), **columnsgrid** (feature checklist: HEPA, Carbon, Formaldehyde, App, Display). **button** ("Buy Now"). **button** ("Compare All Models").

12. **layout-row (Feature 10: Certifications)** -> `comp_0_components_11`
    **eyebrow** ("Trust & Safety"), **heading** ("Tested. Certified. Trusted."). **columnsgrid** (5 columns) each with **image** (certification logo) + **caption**: "HEPA H13 Certified", "AHAM Verifide", "Energy Star", "Allergy UK Approved", "Asthma & Allergy Foundation". **paragraph** ("All claims independently verified by accredited laboratories.").

13. **layout-row (Reviews & Health Impact)** -> `comp_0_components_12`
    **eyebrow** ("Real Results"), **heading** ("What Users Say"). **rating** (4.6 overall). **columnsgrid** (3 columns) each with **blockquote** (user testimonial focused on health improvement -- allergies, asthma, sleep quality), **rating** (individual rating), **caption** (reviewer name). **button** ("Read All Reviews").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your Air Quality Setup"). **columnsgrid** (4 columns) each with **image** (product), **heading** (product name), **caption** (price), **button** ("Shop Now"): replacement filters, humidifier, fan+purifier combo, air quality monitor.

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Product Support, Filter Subscriptions, Company Info, Connect With Us. **br** (divider). **caption** (legal disclaimers, copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new air purifier launch

**Page: New Purifier Launch (e.g., "Introducing Dyson Purifier HushJet")**

1. **titlebar** -- Brand logo, minimal nav (Overview, Technology, Specs, Buy), "Buy Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic product reveal with particle visualization). Overlay: **eyebrow** ("Introducing"), **heading** ("Dyson Purifier HushJet"), **paragraph** ("Whisper-quiet. Relentlessly powerful."), **button** ("Shop Now"), **button** ("Watch the Film").

3. **layout-row (Impact Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "99.97% Particle Capture", "24 dBA Night Mode", "5 Year Filter Life", "1,076 Sq Ft Coverage".

4. **layout-row (Filtration Story)** -- **eyebrow** + **heading** ("Engineered to Destroy"), **paragraph** (formaldehyde destruction narrative -- catalytic oxidation never stops working), **image** (dramatic filter cross-section with particle visualization).

5. **layout-row (Silence Technology)** -- **heading** ("Silence, Engineered"), **image** (acoustic engineering lab shot), **paragraph** (helmholtz resonator, aerodynamic blades), **counter-up** ("24 dBA") + **caption** ("Quieter than a library").

6. **layout-row (Smart Living)** -- **heading** ("Your Air, Your Control"), **carousel** (app screenshots -- AQI dashboard, scheduling, auto mode, filter alerts).

7. **layout-row (Before/After)** -- Split layout: **image** (polluted room haze) + **image** (clean room crystal clear), **heading** ("See the Difference"), **paragraph** ("Real-time air quality monitoring shows results within minutes.").

8. **layout-row (Certification Strip)** -- **ticker** scrolling certification badges and accolades: "HEPA H13", "Energy Star", "Allergy UK", "AHAM Verifide", "Quiet Mark Certified".

9. **layout-row (CTA)** -- **heading** ("Breathe Better, Starting Today"), **paragraph** (price and free shipping offer), **button** ("Buy Now"), **caption** ("Free 30-day trial. Free returns.").

10. **layout-row (Footer)** -- Minimal footer with legal text, support links, social icons.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for an air purifier brand's full lineup

**Page: Air Purifier Range (e.g., "Dyson Air Purifiers")**

1. **titlebar** -- Brand logo, nav (All Purifiers, Purifier-Fans, Purifier-Humidifiers, Formaldehyde Range, Filters, Support), search, store locator.

2. **layout-row (Hero)** -- **heading** ("Choose Your Purifier"), **paragraph** ("Find the right purifier for your space and needs."), **layout-row** with filters: **dropdown** (Room Size), **dropdown** (Feature -- HEPA / Formaldehyde / Humidifier), **dropdown** (Price Range), **button** ("Filter Results").

3. **layout-row (Category: Compact Purifiers)** -- **eyebrow** ("Small Rooms"), **heading** ("Compact Purifiers"). **columnsgrid** (3 columns) each card: **image** (product), **badge** ("New"/"Best Seller" where applicable), **heading** (model name), **caption** (price), **rating** (stars), **paragraph** (coverage area + key feature), **button** ("Shop"), **button** ("Compare").

4. **layout-row (Category: Whole-Room Purifiers)** -- **eyebrow** ("Large Rooms"), **heading** ("Whole-Room Purifiers"). Same card grid pattern for large-room models.

5. **layout-row (Category: Purifier Combos)** -- **eyebrow** ("Multi-Function"), **heading** ("Purifier + Fan / Humidifier Combos"). Same card grid pattern for combo products.

6. **layout-row (Comparison Tool)** -- **heading** ("Compare Purifiers Side by Side"). **columnsgrid** (3 columns): Column headers with **dropdown** (select model) each. Below: rows of specs with labels and values per column. Specs: Coverage Area, CADR, Filtration Type, Noise Level (dBA), Filter Life, Smart Features, Price.

7. **layout-row (Room Size Guide)** -- **tabs** (By Room: "Bedroom / 200 sq ft", "Living Room / 500 sq ft", "Open Plan / 1000 sq ft", "Office / 1500 sq ft") each showing recommended models with **columnsgrid** of matching purifiers.

8. **layout-row (Why Purify)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "99.97% Particles Removed", "50% Allergy Relief Reported", "2x Better Sleep", "365 Days Protection".

9. **layout-row (Filter Subscription CTA)** -- **heading** ("Never Run Out of Clean Air"), **paragraph** ("Subscribe and save 15% on replacement filters"), **button** ("Subscribe Now").

10. **layout-row (Footer)** -- Full footer with product links, support links, certifications, social, legal.
