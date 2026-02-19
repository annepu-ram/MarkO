# Headphones & Audio -- Product Pages

> Focus: Sound quality visualization, ANC technology explanation, battery life prominence, comfort ergonomics, and side-by-side model comparison that drive confident purchasing.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Sony | sony.com/en/headphones/wh-1000xm5 | Scroll-triggered feature reveals per section (ANC, sound, comfort), driver exploded diagram, Auto NC Optimizer animation, 30hr battery callout |
| Apple AirPods Pro | apple.com/airpods-pro | Full-bleed product hero, feature-per-scroll section with parallax product shots, H2 chip diagram, Adaptive Audio animation |
| Bose | bose.com/p/headphones/quietcomfort-headphones | Noise cancellation modes selector, comfort materials close-up, battery life countdown visual, EQ customization preview |
| JBL | jbl.com/over-ear-headphones | Bold color variants grid, bass visualization, IP rating badge, multi-device pairing diagram, app screenshots |
| Sennheiser | sennheiser.com/en-us/catalog/products/headphones | Audiophile-grade spec tables, frequency response chart, driver technology cross-section, studio-grade positioning |

**Patterns to incorporate:**
- Exploded product diagram showing internal components (drivers, microphones, cushions)
- ANC modes interactive comparison (Off / Transparency / Full ANC)
- Battery life timeline with quick-charge callout ("5 min charge = 3 hrs playback")
- Ear tip / cushion comfort close-up photography
- Codec and connectivity icons row (LDAC, aptX, AAC, Bluetooth 5.3)
- App integration screenshots showing EQ customizer
- Comparison table against competitor models or own product lineup
- Sound profile visualization (bass/mid/treble spectrum)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Headphones Detail**

1. **titlebar**
   Brand logo, nav links (Headphones, Earbuds, Speakers, Soundbars, Accessories), search icon, support icon, cart icon.

2. **layout-row (Hero -- Product Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5 slides -- front angle, side profile, folded/case, ear cushion detail, on-model lifestyle). Right column: **eyebrow** ("Wireless Noise Cancelling"), **heading** (product name "WH-1000XM5"), **rating** (4.7 stars, 2,340 reviews), **paragraph** (one-line pitch: "Industry-leading noise cancelling with exceptional sound"), **badge** ("Editor's Choice"), color selector using **button** components (Black / Silver / Midnight Blue), **heading** (price "$349.99"), **button** ("Add to Cart"), **button** ("Find a Retailer" outline), **paragraph** ("Free 2-day shipping. 30-day returns.").

3. **layout-row (Feature: Sound & Drivers)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Sound Quality"), **heading** ("30mm Precision Drivers"), **paragraph** (newly designed driver unit with edge winding for wider frequency range, DSEE Extreme upscaling for compressed audio, Hi-Res Audio certified), **columnsgrid** (3 columns) with **counter-up** + **caption**: "30mm Driver", "40kHz Range", "360 Reality Audio". Right column: **image** (exploded driver diagram with labeled parts).

4. **layout-row (Feature: Active Noise Cancellation)** -> `comp_0_components_3`
   Full-width dark background. **eyebrow** ("Noise Cancelling"), **heading** ("Silence the World Around You"), **paragraph** (8 microphones with dual-processor noise cancelling, Auto NC Optimizer adjusts to environment in real time), **columnsgrid** (3 columns) with **image** + **heading** + **paragraph** each: "Full ANC -- Block out everything", "Ambient Sound -- Hear conversations", "Adaptive -- Auto-adjusts as you move". **image** (microphone placement diagram on headphone).

5. **layout-row (Feature: Battery & Charging)** -> `comp_0_components_4`
   Left column: **image** (headphones with charging cable, battery indicator). Right column: **eyebrow** ("Battery Life"), **heading** ("30 Hours. Then 3 More in 3 Minutes."), **progress-bar** (30 hours full charge visualization), **paragraph** (USB-C quick charge: 3 minutes = 3 hours playback, full charge in 3.5 hours), **counter-up** components: "30hrs Playback", "3min Quick Charge", "3.5hrs Full Charge".

6. **layout-row (Feature: Comfort & Fit)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Comfort"), **heading** ("Designed for All-Day Wear"), **paragraph** (soft-fit leather headband, pressure-reducing ear cushions, lightweight 250g design, stepless slider adjusts smoothly), **icon** + **caption** pairs: "Ultra-Soft Leather", "Pressure-Free Cushions", "250g Lightweight". Right column: **image** (ear cushion cross-section close-up showing foam layers).

7. **layout-row (Feature: Bluetooth & Codec)** -> `comp_0_components_6`
   **heading** ("Seamless Connectivity"), **columnsgrid** (4 columns) each with **icon** + **heading** + **caption**: "Bluetooth 5.2 -- Stable, long-range connection", "LDAC -- Hi-Res wireless audio", "Multipoint -- Connect 2 devices simultaneously", "NFC -- One-touch pairing". **paragraph** ("Compatible with Google Fast Pair, Microsoft Swift Pair, and Apple devices").

8. **layout-row (Feature: Mic Quality)** -> `comp_0_components_7`
   Left column: **image** (person on video call wearing headphones). Right column: **eyebrow** ("Call Quality"), **heading** ("Crystal Clear Voice Pickup"), **paragraph** (beam-forming microphones with AI noise reduction isolate your voice from background noise, wind noise reduction structure for outdoor calls), **rating** (5 stars) + **caption** ("Rated best call quality -- RTINGS.com").

9. **layout-row (Feature: Controls & App)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Smart Controls"), **heading** ("Touch, Tap, and Customize"), **paragraph** (touch panel controls on right earcup, Speak-to-Chat auto-pauses music, Wear Detection pauses when removed), **accordion** with items: "Touch Controls Guide", "App EQ Customizer", "Speak-to-Chat Settings", "Wear Detection". Right column: **image** (app screenshot showing EQ sliders and ANC controls).

10. **layout-row (Feature: Water Resistance)** -> `comp_0_components_9`
    Left column: **image** (headphones in rain/gym setting). Right column: **eyebrow** ("Durability"), **heading** ("IPX4 Splash Resistant"), **paragraph** (sweat and splash proof for workouts and commutes, not for submersion), **badge** ("IPX4 Rated"), **icon** + **caption**: "Gym Ready", "Rain Protected", "Sweat Resistant".

11. **layout-row (Feature: Price & Variants)** -> `comp_0_components_10`
    **heading** ("Choose Your Model"), **columnsgrid** (3 columns) comparing models: each with **image** (product), **heading** (model name), **heading** (price), **paragraph** (key differentiator), bullet list of specs using **paragraph** components, **badge** ("Best Value" on mid-tier), **button** ("Select"). Below: **paragraph** ("All models include carrying case, USB-C cable, audio cable, and flight adapter").

12. **layout-row (Feature: Comparison)** -> `comp_0_components_11`
    **heading** ("How We Compare"), comparison table using **columnsgrid** (4 columns). Header row: Feature, Our Model, Competitor A, Competitor B. Rows for: ANC Performance, Battery Life, Weight, Driver Size, Codec Support, Price -- using **paragraph** and **icon** (checkmark/cross) components. **badge** ("Winner") on leading specs.

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("What Listeners Say"), **rating** (4.7 overall), **progress-bar** rows for 5-star through 1-star, **tabs** with 3 tabs: "Most Helpful" / "Most Recent" / "Audiophile Reviews". Each tab: **accordion** with reviewer name, rating, review text, "Verified Purchase" badge.

14. **layout-row (In the Box)** -> `comp_0_components_13`
    **heading** ("What's in the Box"), **image** (flat-lay of all included items), **columnsgrid** (2 columns) listing: Headphones, Carrying Case, USB-C Cable, 3.5mm Audio Cable, Flight Adapter -- each with **icon** + **caption**.

15. **layout-row (Related Products)** -> `comp_0_components_14`
    **heading** ("Complete Your Setup"), **columnsgrid** (4 columns) each with **image**, **heading** (product name), **caption** (category), **heading** (price), **button** ("Add to Cart").

16. **layout-row (Footer)** -> `comp_0_components_15`
    **columnsgrid** (4 columns): Products, Support, Company, Newsletter signup with **textbox** + **button**. **br** divider. **paragraph** (copyright and legal).

---

## Variant B -- Product Launch / Landing Page

**Page: Next-Gen Headphones Launch**

1. **titlebar**
   Minimal logo, "New" badge, pre-order CTA button.

2. **layout-row (Hero -- Cinematic Reveal)**
   **video-background** (slow-motion product reveal with sound wave visuals). Overlay: **heading** ("Hear Everything. Or Nothing."), **paragraph** ("The next generation of noise cancelling"), **button** ("Pre-Order Now"), **countdown** (launch date).

3. **layout-row (Sound Revolution)**
   Dark background. **eyebrow** ("Engineered Sound"), **heading** ("A New Driver. A New Standard."), split layout: left **image** (driver exploded view), right **paragraph** (technical narrative about driver innovation), **counter-up** components: "40mm Driver", "50kHz Range", "20% More Bass".

4. **layout-row (ANC Evolution)**
   Full-width **image** (sound wave visualization showing noise cancelled). **heading** ("ANC That Learns You"), **paragraph** (AI-powered adaptive noise cancelling story), **columnsgrid** (3 columns) with mode demonstrations.

5. **layout-row (Battery Breakthrough)**
   **heading** ("40 Hours of Uninterrupted Listening"), **progress-bar** (animated fill to 40hrs), **paragraph** (comparison to previous gen: "10 more hours than before"), **counter-up** ("40" hours prominent), **caption** ("5 min charge = 4 hrs play").

6. **layout-row (Design Philosophy)**
   **carousel** (5 slides of industrial design process -- sketch, prototype, material selection, testing, final), each with **image** + **caption**. **blockquote** ("We obsessed over every gram and every decibel." -- Lead Engineer).

7. **layout-row (Color Story)**
   **heading** ("Four Finishes"), **columnsgrid** (4 columns) each with **image** (product in color) + **heading** (color name) + **paragraph** (inspiration). **badge** ("Exclusive" on limited color).

8. **layout-row (Press Reviews)**
   **ticker** scrolling press quotes: **blockquote** + **caption** (publication name) for each. Logos of tech publications below.

9. **layout-row (Pre-Order CTA)**
   **heading** ("Reserve Yours"), **heading** (price), **paragraph** ("Ships March 15"), **button** ("Pre-Order -- $399"), **paragraph** ("Free expedited shipping for pre-orders"), **countdown** (to shipping date).

10. **layout-row (Footer)**
    Newsletter, social, legal links.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Headphones Catalog**

1. **titlebar**
   Brand logo, category nav (Over-Ear, On-Ear, True Wireless, Sports, Gaming, Kids), search, cart.

2. **layout-row (Category Hero)**
   **image** (lifestyle banner -- various headphone types). **heading** ("Find Your Perfect Sound"), **paragraph** ("From studio-grade to street-ready"), **eyebrow** ("56 models").

3. **layout-row (Use Case Selector)**
   **heading** ("What Do You Need?"), **columnsgrid** (5 columns) each with **icon** + **heading** + **caption**: "Commute -- Block noise, enjoy music", "Work From Home -- Clear calls, all-day comfort", "Workout -- Sweat-proof, secure fit", "Studio -- Flat response, open-back", "Gaming -- Low latency, spatial audio". Each is a **button** linking to filtered results.

4. **layout-row (Side-by-Side Comparison)**
   **heading** ("Compare Models"), **columnsgrid** (3 columns) each with **image**, **heading** (model), **heading** (price), key spec list using **paragraph** components (ANC, Battery, Weight, Codec), **rating**, **button** ("View Details"). Below: **accordion** expanding full spec comparison table rows.

5. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating) each card: **image** (product on white), **badge** (category tag -- "ANC" / "Sport" / "Studio"), **heading** (product name), **rating** (stars + count), **heading** (price), key specs using **caption** (battery, weight), color dots, **button** ("Compare") + **button** ("Add to Cart").

6. **layout-row (Buying Guide)**
   **heading** ("Headphone Buying Guide"), **tabs** with 4 tabs: "ANC Explained" / "Codec Guide" / "Fit Types" / "IP Ratings". Each tab: **image** (diagram) + **paragraph** (educational content) + **button** ("Shop This Type").

7. **layout-row (Bestsellers)**
   **heading** ("Most Popular"), **carousel** (6 slides) with product cards, **badge** ("Best Seller" / "Staff Pick" / "Best Value").

8. **layout-row (Accessories)**
   **heading** ("Essential Accessories"), **ticker** scrolling accessory cards: replacement ear cushions, cases, cables, adapters -- each with **image** + **caption** + **heading** (price).

9. **layout-row (Footer)**
    Support links, warranty info, newsletter, social, copyright.
