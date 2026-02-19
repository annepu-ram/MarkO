# Luxury Cars & Supercars -- Product Pages

> Focus: Heritage-driven, emotionally immersive product storytelling with trackable sections for engine prowess, craftsmanship, design language, and bespoke configurator that let marques measure which aspiration triggers enquiry and configuration sessions.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Rolls-Royce Spectre | rolls-roycemotorcars.com/en_US/showroom/spectre.html | Cinematic full-bleed hero video, yacht-inspired design narrative, Starlight Headliner interactive 360-view, bespoke commissioning CTA, "Whispers" owner app integration |
| Lamborghini Revuelto | lamborghini.com/en-en/models/revuelto | Dark dramatic hero with engine sound on scroll, Y-shaped design language storytelling, hexagonal grid spec cards, aerodynamic detail zoom carousel, "Ad Personam" bespoke configurator link |
| Ferrari 296 GTB | ferrari.com/en-EN/auto/ferrari-296-gtb | Full-screen rotating hero, heritage lineage timeline, V6 hybrid powertrain explainer with animated diagrams, configurator integration, Maranello factory story |
| Porsche 911 | porsche.com/usa/models/911 | Clean editorial layout, driving experience video chapters, configurable variants tabs, performance data animated on scroll, heritage section linking to 911 history |
| Bentley Continental GT | bentleymotors.com/en/models/continental-gt | Handcrafted interior close-ups, Crewe factory craftsmanship video, veneer and leather material selector, Mulliner bespoke options showcase, concierge booking CTA |

**Patterns to incorporate:**
- Full-bleed cinematic hero with engine sound or ambient audio on interaction
- Heritage lineage timeline connecting current model to brand history
- Dramatic dark backgrounds with high-contrast product photography
- Bespoke/configurator integration as a primary CTA throughout the page
- Craftsmanship storytelling with close-up material shots (leather stitching, wood veneer, carbon fiber)
- Performance stats revealed through scroll-triggered counter-up animations
- Limited production numbers and exclusivity messaging with badge components
- Emotional driving experience conveyed through video-background sections
- Factory/atelier story section connecting the car to its birthplace

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Supercar Detail (e.g., Rolls-Royce Spectre)**

1. **titlebar**
   Marque emblem, nav links (Models, Bespoke, Heritage, Ownership, Locate Dealer), hamburger for mobile, "Enquire" button, "Configure" button.

2. **layout-row (Hero -- Vehicle Revelation + Key Info)** -> `comp_0_components_1`
   Full-width **video-background** (cinematic driving footage -- sweeping coastal road, dramatic lighting, engine note crescendo). Overlay: **eyebrow** ("The Rolls-Royce"), **heading** ("Spectre"), **paragraph** ("The most powerful Rolls-Royce in history. Silent. Electric. Extraordinary."), **button** ("Configure Yours"), **button** ("Book a Private Viewing"). Below overlay: **columnsgrid** (3 columns) with **counter-up** + **caption**: "577 bhp", "0-60 in 4.4s", "320 mi Range".

3. **layout-row (Feature 1: Engine & Power -- 0-100 Time)** -> `comp_0_components_2`
   Left column: **image** (powertrain architecture diagram -- dual motor, battery floor, all-wheel drive visualization). Right column: **eyebrow** ("Performance"), **heading** ("Effortless, Relentless Power"), **paragraph** (powertrain narrative -- twin electric motors deliver 577 bhp and 900 Nm of torque, whisper-silent surge, the most torque of any Rolls-Royce). **columnsgrid** (4 columns) each with **counter-up** + **caption**: "577 bhp", "900 Nm", "4.4s 0-60 mph", "155 mph Top Speed". **badge** ("All-Wheel Drive"). **paragraph** ("Power is not announced. It is simply, irrevocably present.").

4. **layout-row (Feature 2: Heritage & Lineage)** -> `comp_0_components_3`
   Full-width dark background. **eyebrow** ("Heritage"), **heading** ("A Legacy Electrified"). **carousel** (heritage timeline slides): Slide 1: **image** (1904 original 10 HP) + **caption** ("1904 -- The Beginning"), Slide 2: **image** (Silver Ghost) + **caption** ("1907 -- The Silver Ghost"), Slide 3: **image** (Phantom) + **caption** ("1925 -- The Phantom"), Slide 4: **image** (Silver Shadow) + **caption** ("1965 -- The Silver Shadow"), Slide 5: **image** (Spectre) + **caption** ("2023 -- The Spectre"). **paragraph** ("Charles Rolls prophesied an electric future in 1900. Spectre fulfills that vision."). **blockquote** ("'The electric car is perfectly noiseless and clean.' -- The Hon. Charles Rolls, 1900").

5. **layout-row (Feature 3: Exterior Design Language)** -> `comp_0_components_4`
   Left column: **eyebrow** ("Design"), **heading** ("Sculpted by the Wind"), **paragraph** (exterior design narrative -- fastback silhouette inspired by ocean-going yachts, lowest drag coefficient of any Rolls-Royce at 0.25 Cd, 2.3-metre widest Rolls-Royce doors). **counter-up** ("0.25") + **caption** ("Cd -- Lowest drag in Rolls-Royce history"). Right column: **carousel** (exterior detail shots -- Pantheon Grille illuminated at night, Spirit of Ecstasy in motion, split headlamps, 23-inch wheels, coach door hinge mechanism). **ticker** scrolling design highlights: "Illuminated Pantheon Grille", "Widest Doors Ever", "Split Headlamp", "Fastback Silhouette", "23-inch Alloys".

6. **layout-row (Feature 4: Interior Craftsmanship)** -> `comp_0_components_5`
   Full-width **image** (panoramic interior shot -- Starlight Headliner, illuminated fascia, canadel panelling). Below: **eyebrow** ("Craftsmanship"), **heading** ("A Constellation of Detail"). **columnsgrid** (4 columns) each with **image** (extreme close-up) + **heading** (feature) + **caption** (description): "Starlight Headliner" ("4,796 hand-placed fiber-optic lights recreate the night sky"), "Illuminated Fascia" ("5,500 stars animate on startup around the Spectre nameplate"), "Canadel Panelling" ("Veneer slip-matched at a precise 55-degree angle"), "Open-Pore Wood" ("Natural grain preserved, hand-finished by master craftspeople"). **paragraph** ("Every Spectre interior requires 20 hides of leather, hand-selected and stitched by a single artisan.").

7. **layout-row (Feature 5: Driving Experience)** -> `comp_0_components_6`
   **video-background** (in-cabin driving footage -- silent glide through city at dusk, then sweeping mountain pass). Overlay: **eyebrow** ("The Drive"), **heading** ("Magic Carpet Ride, Perfected"), **paragraph** (driving experience narrative -- Planar Suspension System decouples road from cabin, 18 sensors read the road ahead, self-leveling air suspension). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Planar Suspension" ("Road-reading, self-leveling air springs"), "Satellite-Aided Transmission" ("GPS pre-selects gears for upcoming terrain"), "Active Anti-Roll" ("Eliminates body roll at any speed"). **blockquote** ("'It drives as if the road has been freshly laid with silk.' -- Top Gear").

8. **layout-row (Feature 6: Technology & Infotainment)** -> `comp_0_components_7`
   Left column: **image** (SPIRIT digital interface -- curved high-resolution screens, ambient lighting). Right column: **eyebrow** ("Technology"), **heading** ("SPIRIT -- The Digital Soul"), **paragraph** (technology narrative -- SPIRIT operating system manages every function, Whispers owner app for remote commands, head-up display, night vision, 360-degree camera). **columnsgrid** (3 columns) each with **icon** + **caption**: "Whispers App", "Head-Up Display", "Night Vision Camera". **accordion** with items: "SPIRIT Interface -- Full digital dashboard with haptic controls", "Whispers App -- Remote climate, location, concierge services", "18-Speaker Bespoke Audio -- Individually tuned to cabin acoustics", "Active Cruise Intelligence -- Level 2+ autonomous driving assist".

9. **layout-row (Feature 7: Bespoke Options)** -> `comp_0_components_8`
   Full-width dark background. **eyebrow** ("Bespoke"), **heading** ("Yours, and Yours Alone"), **paragraph** (bespoke commissioning story -- 44,000 exterior paint options, any Starlight constellation, monogrammed headrests, personally sourced materials). **carousel** (bespoke examples -- unique color commissions, personalized clocks, custom coachlines, embroidered headrests, bespoke luggage set). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "44,000+ Paint Options", "Infinite Starlight Patterns", "1:1 Designer Consultation". **button** ("Begin Your Commission"). **caption** ("Every Rolls-Royce is built for one patron alone.").

10. **layout-row (Feature 8: Limited Production Numbers)** -> `comp_0_components_9`
    **eyebrow** ("Exclusivity"), **heading** ("Rarity by Design"). **paragraph** (production exclusivity -- hand-built at Goodwood, England, limited annual production, each car takes months to complete). **columnsgrid** (2 columns): Column 1: **counter-up** ("6") + **caption** ("Months to Handcraft"), Column 2: **counter-up** ("1") + **caption** ("Dedicated Craftsperson Per Car"). **image** (Goodwood factory -- artisan at work on a Spectre). **badge** ("Handbuilt in Goodwood, England"). **paragraph** ("Rolls-Royce does not mass-produce. Each motor car is a commission.").

11. **layout-row (Feature 9: Price & Ownership)** -> `comp_0_components_10`
    **eyebrow** ("Ownership"), **heading** ("The Spectre Experience"). **paragraph** (ownership experience -- dedicated lifestyle manager, Whispers member events, global service network, complimentary collection and delivery). **tabs** with tabs: "Spectre" (base configuration + starting price), "Spectre Black Badge" (enhanced performance variant + price). Each tab: **heading** (variant + price), **paragraph** (key differentiators), **button** ("Configure"), **button** ("Request a Private Consultation"). **caption** ("Pricing reflects base configuration. Bespoke commissions quoted individually.").

12. **layout-row (Feature 10: Brand Heritage Film)** -> `comp_0_components_11`
    Full-width **video-background** (brand heritage film -- montage of Rolls-Royce through the decades, ending with Spectre). Overlay: **eyebrow** ("The Film"), **heading** ("Inspiring Greatness"), **button** ("Watch the Full Film"). Below: **paragraph** ("For over a century, Rolls-Royce has defined the pinnacle of automotive luxury. The Spectre writes the next chapter.").

13. **layout-row (Reviews & Press Acclaim)** -> `comp_0_components_12`
    **eyebrow** ("Acclaim"), **heading** ("The World Responds"). **columnsgrid** (3 columns) each with **blockquote** (press review excerpt), **rating** (editorial rating), **caption** (publication name -- "Top Gear", "Car and Driver", "Robb Report"). **ticker** scrolling accolades: "Car of the Year -- Robb Report", "Best Luxury EV -- Top Gear", "Design Award -- Red Dot".

14. **layout-row (Enquiry & Private Viewing)** -> `comp_0_components_13`
    **heading** ("Experience Spectre"), **paragraph** ("Arrange a private viewing at your nearest atelier."), **form** with **textbox** (Full Name), **textbox** (Email), **textbox** (Phone), **dropdown** (Preferred Atelier Location), **dropdown** (Interest -- "Purchase" / "Bespoke Commission" / "Test Drive"), **textarea** (Personal Message), **button** ("Submit Enquiry"). **caption** ("A personal liaison will respond within 24 hours.").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Models, Bespoke, Ownership, Heritage. **br** (divider). **caption** (legal disclaimers, copyright, "Handbuilt in Goodwood, England").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a supercar world premiere

**Page: Supercar World Premiere (e.g., "Lamborghini Temerario -- Unveiled")**

1. **titlebar** -- Marque emblem, minimal nav (Overview, Power, Design, Configure), "Register Interest" button.

2. **layout-row (Hero)** -- Full-width **video-background** (dramatic reveal -- car emerging from darkness, engine roar crescendo, track footage). Overlay: **eyebrow** ("World Premiere"), **heading** ("Temerario"), **paragraph** ("920 CV. Twin-Turbo V8. Hybrid Fury."), **countdown** (to configurator launch or first deliveries), **button** ("Register Your Interest").

3. **layout-row (Vital Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "920 CV Total Power", "0-100 in 2.7s", "340 km/h Top Speed", "V8 Twin-Turbo Hybrid".

4. **layout-row (Design DNA)** -- Alternating image-text. **eyebrow** + **heading** ("Forged in Fury"), **paragraph** (Y-shaped design language, hexagonal grille, active aerodynamics narrative), **carousel** (dramatic angle shots -- front, side, rear, detail).

5. **layout-row (Power Story)** -- **video-background** (engine assembly footage at Sant'Agata). Overlay: **heading** ("Heart of a Bull"), **paragraph** (new twin-turbo V8 + triple electric motor breakdown). **counter-up** ("10,000 RPM Redline").

6. **layout-row (Heritage)** -- **heading** ("From Miura to Temerario"), **carousel** (lineage timeline -- Miura, Countach, Diablo, Murcielago, Aventador, Temerario).

7. **layout-row (Ad Personam)** -- **heading** ("Make It Yours"), **paragraph** ("Infinite personalization through Ad Personam"), **image** (bespoke color and material samples), **button** ("Explore Ad Personam").

8. **layout-row (Registration CTA)** -- **heading** ("Secure Your Allocation"), **paragraph** ("Contact your authorized dealer to register"), **button** ("Register Interest"), **button** ("Locate Dealer").

9. **layout-row (Footer)** -- Minimal footer with legal text, marque heritage link, social icons.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-model showroom for a luxury marque's complete range

**Page: Brand Model Range (e.g., "Porsche Models")**

1. **titlebar** -- Marque emblem, nav (Sports Cars, SUVs, Sedans, Electric, Heritage, Configure), search, dealer locator.

2. **layout-row (Hero)** -- **heading** ("The Porsche Range"), **paragraph** ("Every Porsche is a sports car."), **video-background** (montage of range in motion). **layout-row** with filters: **dropdown** (Body Style -- Sports Car, SUV, Sedan), **dropdown** (Drivetrain -- Petrol, Hybrid, Electric), **button** ("Explore").

3. **layout-row (Category: Sports Cars)** -- **eyebrow** ("Sports Cars"), **heading** ("Born on the Track"). **columnsgrid** (3 columns) each card: **image** (hero shot), **badge** ("New"/"GTS"/"GT3" where applicable), **heading** (model name -- "911 Carrera", "718 Cayman"), **caption** (starting price), **paragraph** (power + 0-100 time), **button** ("Discover"), **button** ("Configure").

4. **layout-row (Category: SUVs)** -- **eyebrow** ("SUVs"), **heading** ("Performance Meets Versatility"). Same card grid for Cayenne, Macan.

5. **layout-row (Category: Electric)** -- **eyebrow** ("Electric"), **heading** ("Soul, Electrified"). Same card grid for Taycan range.

6. **layout-row (Performance Comparison)** -- **heading** ("Compare Performance"). **columnsgrid** (4 columns): Column headers with **dropdown** (select model). Below: spec rows -- Power, 0-100, Top Speed, Weight, Drivetrain, Starting Price.

7. **layout-row (Configurator CTA)** -- **heading** ("Build Your Porsche"), **paragraph** ("Over 1 billion possible combinations"), **image** (configurator interface preview), **button** ("Start Configuring").

8. **layout-row (Heritage)** -- **eyebrow** ("Since 1948"), **heading** ("A Legacy of Performance"). **columnsgrid** (4 columns) with **counter-up** + **caption**: "75+ Years Heritage", "911 Generations Built", "33,000+ Race Wins", "1 Driving Philosophy".

9. **layout-row (Locate Dealer CTA)** -- **heading** ("Experience the Drive"), **paragraph** ("Visit your nearest Porsche Centre"), **form** with **textbox** (Postcode), **button** ("Find Dealer").

10. **layout-row (Footer)** -- Full footer with model links, ownership, motorsport, heritage, social, legal.
