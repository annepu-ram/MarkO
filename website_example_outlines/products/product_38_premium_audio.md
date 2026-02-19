# Premium Audio & Home Theater -- Product Pages

> Focus: Audiophile-grade technical storytelling with trackable sections for driver technology, frequency response, build materials, and room calibration that let dealers measure which sonic specifications and heritage details drive demo-room bookings and high-end purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Bang & Olufsen Beolab 90 | bang-olufsen.com/beolab-90 | Full-bleed sculptural hero with dramatic lighting, exploded-view driver diagram, acoustic beam technology animation, room placement guide, "Book Home Demo" CTA |
| Bowers & Wilkins 801 D4 | bowerswilkins.com/801-d4 | Split-screen hero (speaker + lifestyle), Diamond tweeter technology deep-dive, crossover frequency charts, "Designed in England" heritage badge, dealer locator |
| Sonos Arc Ultra | sonos.com/arc-ultra | Lifestyle-first hero with soundbar in room, Dolby Atmos feature callouts, app integration demo, animated sound wave graphics, easy setup timeline |
| McIntosh MC901 | mcintoshlabs.com/mc901 | Classic dark-background hero with iconic blue meters, tube + solid-state hybrid technology section, hand-wired assembly photos, THD specifications, heritage timeline since 1949 |
| KEF Blade | kef.com/blade | 360-degree product viewer, Uni-Q driver technology cross-section, frequency response graph, award badges from professional reviewers, finish configurator |

**Patterns to incorporate:**
- Dark-themed hero with dramatic product photography and studio lighting
- Exploded-view or cross-section diagrams of driver technology
- Technical specifications presented with visual frequency response curves
- Material close-ups showing aluminum, wood veneer, or carbon fiber construction
- Room placement and acoustic calibration guidance section
- Professional review scores and award badges prominently displayed
- Heritage timeline connecting to decades of acoustic engineering
- Connectivity diagram showing analog, digital, and wireless options
- "Book Home Audition" or "Visit Listening Room" conversion CTA
- Sound comparison or demo video section

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Premium Speaker Detail (e.g., Bowers & Wilkins 801 D4 Signature)**

1. **titlebar**
   Brand logo, nav links (Speakers, Headphones, Home Theater, Technology, Heritage, Dealers), hamburger for mobile, "Find a Dealer" button.

2. **layout-row (Hero -- Product Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- front studio shot with dramatic lighting, 3/4 angle showing finish, rear panel connections, driver close-up, lifestyle in room, dimensional reference). Right column: **eyebrow** ("Floorstanding | 801 D4 Series"), **heading** ("801 D4 Signature"), **paragraph** ("The pinnacle of acoustic engineering. Sixty years of research distilled into a singular listening experience."), **badge** ("What Hi-Fi? 5 Stars"), **badge** ("Stereophile Class A"), **rating** (5 stars, "23 Professional Reviews"), **caption** ("GBP 36,000 / pair"), **button** ("Find a Dealer"), **button** ("Download Specifications").

3. **layout-row (Feature 1: Driver Technology)** -> `comp_0_components_2`
   Left column: **image** (exploded-view cross-section showing all driver units). Right column: **eyebrow** ("Acoustic Innovation"), **heading** ("Diamond Tweeter Technology"), **paragraph** ("The 801 D4 Signature features a solid diamond dome tweeter -- the hardest material ever applied to a loudspeaker, delivering frequencies up to 70kHz with zero audible distortion."). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Diamond Tweeter" / "1-inch solid diamond dome, breakup-free to 70kHz", "Continuum Midrange" / "6.5-inch woven composite cone, no coloration", "Aerofoil Bass" / "Dual 10-inch drivers with variable-thickness carbon fiber cones".

4. **layout-row (Feature 2: Frequency Response & THD)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Performance"), **heading** ("Measured Precision"), **paragraph** ("Every 801 D4 Signature is individually measured in our Steyning anechoic chamber and ships with its own frequency response certificate."). **columnsgrid** (2 columns): Column 1 with **heading** ("13Hz -- 35kHz") + **caption** ("-6dB Frequency Range"), **heading** ("<0.3%") + **caption** ("Total Harmonic Distortion"); Column 2 with **heading** ("90 dB") + **caption** ("Sensitivity (2.83V/1m)"), **heading** ("200W -- 1000W") + **caption** ("Recommended Amplification"). Right column: **image** (frequency response curve graph -- clean, technical visualization). **caption** ("Individual measurement certificate included with each pair").

5. **layout-row (Feature 3: DAC & Amplification Pairing)** -> `comp_0_components_4`
   Left column: **image** (rear panel showing connections with callout labels). Right column: **eyebrow** ("Connectivity"), **heading** ("Paired for Perfection"), **paragraph** ("The 801 D4 Signature reveals its full potential with reference-grade amplification. Our engineers recommend a minimum of 200W per channel from a high-current design."). **accordion** with items: "Recommended Amplifiers (Classé, Rotel, McIntosh)", "Bi-Wire / Bi-Amp Terminal Configuration", "Cable Recommendations (Nordost, AudioQuest)", "Optimal Source Components (DACs, Turntables)". **badge** ("Bi-Amp Ready").

6. **layout-row (Feature 4: Build Material & Construction)** -> `comp_0_components_5`
   **eyebrow** ("Craftsmanship"), **heading** ("Built Without Compromise"). **columnsgrid** (4 columns) each with **image** (material close-up) + **heading** (material name) + **caption** (detail): "Solid Hardwood Cabinet" / "Curved, CNC-milled hardwood with constrained-layer damping eliminates resonance", "Aluminum Spine" / "Aerospace-grade spine provides rigid driver alignment and thermal management", "Midnight Blue Metallic Finish" / "Exclusive Signature finish -- hand-polished over 12 coats", "Hand-Laced Tweeter Grille" / "Acoustically transparent stainless steel mesh, hand-assembled". Below: **video** (factory tour showing cabinet construction process).

7. **layout-row (Feature 5: Connectivity)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Connections"), **heading** ("Analog & Digital Ready"), **paragraph** ("Pure analog signal path with premium binding posts, compatible with all amplification topologies."). **columnsgrid** (2 columns): Column 1 with **heading** ("Analog") + **paragraph** ("Dual bi-wire binding posts, gold-plated, WBT NextGen compatible"); Column 2 with **heading** ("Digital") + **paragraph** ("Optional wireless streaming via Formation module (sold separately)"). Right column: **image** (clean shot of connection panel with labeled ports). **icon** (wireless icon) + **caption** ("Formation wireless streaming compatible").

8. **layout-row (Feature 6: Room Requirements)** -> `comp_0_components_7`
   Left column: **image** (room placement diagram -- top-down view showing optimal positioning). Right column: **eyebrow** ("Room Guide"), **heading** ("Your Room, Optimized"), **paragraph** ("The 801 D4 Signature performs best in rooms of 30-80 square meters with a minimum distance of 2.5 meters between speakers and 3 meters to the listening position."). **columnsgrid** (3 columns) with **counter-up** + **caption**: "30" / "sqm Minimum Room", "2.5" / "m Speaker Spacing", "3" / "m Listening Distance". **paragraph** ("For rooms outside these parameters, our acoustic engineers offer complimentary room analysis.").

9. **layout-row (Feature 7: Setup & Calibration)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Installation"), **heading** ("White-Glove Setup"), **paragraph** ("Every 801 D4 Signature purchase includes professional installation by a certified Bowers & Wilkins installer."). **accordion** with items: "Site Survey & Room Analysis", "Delivery & Placement (180kg per speaker)", "Acoustic Measurement with Calibrated Microphone", "Amplifier Matching & Level Calibration", "Final Listening Session with Owner". Right column: **image** (installer using measurement microphone in a listening room). **badge** ("Professional Install Included").

10. **layout-row (Feature 8: Audiophile Heritage)** -> `comp_0_components_9`
    Left column: **image** (archival black-and-white photo of John Bowers in the Steyning research facility). Right column: **eyebrow** ("Heritage"), **heading** ("Since 1966"), **paragraph** ("John Bowers founded the company with one mission: True Sound. From Abbey Road studios to the world's finest listening rooms, our speakers have been the reference for professional and discerning listeners for nearly six decades."). **columnsgrid** (4 columns) with **counter-up** + **caption**: "58" / "Years of Innovation", "80" / "% of Abbey Road Studios", "70" / "Countries", "1" / "Unwavering Mission". **link** ("Explore Our Story").

11. **layout-row (Feature 9: Price & Configurations)** -> `comp_0_components_10`
    **eyebrow** ("Investment"), **heading** ("Configurations & Pricing"). **tabs** with tab per finish: "Midnight Blue Metallic" (GBP 36,000/pair), "Gloss Black" (GBP 32,000/pair), "Satin Rosenut" (GBP 34,000/pair). Each tab: **heading** (finish name + price), **image** (speaker in that finish), **paragraph** (finish description), **caption** (lead time). **button** ("Configure & Quote"). **paragraph** ("Trade-in program available for existing Bowers & Wilkins owners.").

12. **layout-row (Feature 10: Professional Reviews)** -> `comp_0_components_11`
    **eyebrow** ("Critical Acclaim"), **heading** ("What the Experts Say"). **columnsgrid** (3 columns) each with **blockquote** (review excerpt), **rating** (stars), **caption** (publication name + reviewer + date), **image** (publication logo). **ticker** scrolling award badges: "Stereophile Class A", "What Hi-Fi? Product of the Year", "Absolute Sound Golden Ear", "Hi-Fi News Outstanding", "EISA Best Product".

13. **layout-row (Demo Booking CTA)** -> `comp_0_components_12`
    **video-background** (cinematic footage of a listening session in a dedicated audio room). Overlay: **heading** ("Hear It for Yourself"), **paragraph** ("Book a private listening session at your nearest authorized dealer"), **form** with **textbox** (Name), **textbox** (Email), **dropdown** (Nearest City), **dropdown** (Preferred System: "Stereo" / "Home Theater" / "Both"), **calendar** (Preferred Date), **button** ("Book Listening Session").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your System"). **columnsgrid** (4 columns) each with **image** (product), **heading** (product name), **caption** (category + price), **button** ("Explore"): "HTM82 D4 Center" / "Center Channel", "DB4S Subwoofer" / "Subwoofer", "Classé Delta PRE" / "Preamplifier", "Classé Delta STEREO" / "Power Amplifier".

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Products, Technology & Innovation, Find a Dealer, Support & Warranty. **br** (divider). **caption** (copyright, "Designed in England, Crafted with Passion").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new premium audio product launch

**Page: New Product Launch (e.g., "Bang & Olufsen Beolab 50 -- Next Generation")**

1. **titlebar** -- Brand logo, minimal nav (The Speaker, Sound, Design, Experience), "Pre-Order" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic product reveal -- speaker emerging from darkness, acoustic lens deploying, light catching aluminum surfaces). Overlay: **eyebrow** ("Introducing"), **heading** ("Beolab 50"), **paragraph** ("Sound. Sculptured."), **button** ("Pre-Order Now"), **caption** ("Limited first-edition allocation").

3. **layout-row (Sound Story)** -- Dark background. **eyebrow** ("Sound"), **heading** ("Room-Adaptive Acoustics"), **paragraph** ("18 custom drivers, active room compensation, and a motorized acoustic lens that shapes sound to your space in real-time."). **image** (acoustic beam visualization -- sound waves adapting to room).

4. **layout-row (Design Story)** -- **heading** ("A Sculpture for Sound"), **carousel** (angles and finishes -- aluminum, bronze, oak). **counter-up** stats: "18" / "Custom Drivers", "4" / "Built-in Amplifiers", "2100W" / "Total Power".

5. **layout-row (Technology)** -- **heading** ("Inside the Lens"), **video** (acoustic lens deployment close-up). **columnsgrid** (3 columns) with **icon** + **caption**: "Active Room Compensation", "Beam Width Control", "Directivity Pattern Optimization".

6. **layout-row (In the Room)** -- **heading** ("Made for Living"), **carousel** (lifestyle shots in different room settings). **paragraph** ("Whether mounted on its floor stand or integrated into your architecture, Beolab 50 transforms any room into a concert hall.").

7. **layout-row (Pre-Order CTA)** -- **heading** ("Reserve Your Pair"), **paragraph** ("EUR 39,500 / pair. First deliveries begin March 2026."), **countdown** (to delivery date), **button** ("Pre-Order"), **button** ("Book Private Audition").

8. **layout-row (Footer)** -- Minimal footer with dealer locator, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a premium audio brand's speaker range

**Page: Speaker Collection (e.g., "Bowers & Wilkins -- All Speakers")**

1. **titlebar** -- Brand logo, nav (Floorstanding, Standmount, Center, Subwoofer, In-Wall, Wireless, Home Theater), search, dealer locator.

2. **layout-row (Hero)** -- **heading** ("Find Your True Sound"), **paragraph** ("From reference-grade floorstanding speakers to wireless multiroom systems, discover the speaker that suits your space and listening style."), **image** (curated lineup shot of the full range).

3. **layout-row (Filter Bar)** -- **layout-row** with filters: **dropdown** (Type: Floorstanding / Standmount / Center / Subwoofer / In-Wall), **dropdown** (Series: 800 D4 / 700 S3 / 600 S3 / Formation), **dropdown** (Price Range), **dropdown** (Use Case: Stereo / Home Theater / Multiroom), **button** ("Apply Filters").

4. **layout-row (Category: 800 Series Diamond)** -- **eyebrow** ("Flagship"), **heading** ("800 Series Diamond"). **badge** ("Reference Grade"). **columnsgrid** (3 columns) each card: **image** (speaker), **heading** (model name), **caption** (type + price), **rating** (professional review score), **badge** ("Award Winner" where applicable), **paragraph** (one-line description), **button** ("Explore"), **button** ("Compare").

5. **layout-row (Category: 700 Series)** -- Same card pattern. **eyebrow** ("Performance"), **heading** ("700 Series Signature").

6. **layout-row (Category: 600 Series)** -- Same card pattern. **eyebrow** ("Essential"), **heading** ("600 Series").

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Speakers Side by Side"). **columnsgrid** (3 columns) each with **dropdown** (select model). Below: comparison rows -- Frequency Range, Sensitivity, Impedance, Drivers, Dimensions, Weight, Price, Finish Options.

8. **layout-row (Home Theater Builder)** -- **heading** ("Build Your Home Theater System"), **paragraph** ("Select components for a complete surround sound experience"). **tabs** (5.1 System, 7.1 System, Dolby Atmos 7.1.4) each showing recommended component combination with images and total system price.

9. **layout-row (Dealer CTA)** -- **heading** ("Experience True Sound"), **paragraph** ("Visit an authorized dealer for a private listening session"), **form** with **textbox** (Postcode), **button** ("Find Nearest Dealer"). **counter-up** + **caption**: "500+" / "Authorized Dealers Worldwide".

10. **layout-row (Footer)** -- Full footer with product categories, technology pages, dealer directory, support, social links, legal.
