# Luxury Watches -- Product Pages

> Focus: Horological artistry storytelling with trackable sections for movement, materials, dial craftsmanship, and heritage that let maisons measure which aspect of watchmaking mastery drives boutique appointments and purchase intent.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Rolex Submariner | rolex.com/watches/submariner | Clean white background, rotating product hero, tabbed specs (movement, case, bracelet), "Configure" button, "Find a Retailer" CTA, Rolex-certified superlative chronometer badge |
| Patek Philippe Nautilus | patek.com/en/collection/nautilus | Editorial photography on dark background, "Begin Your Own Tradition" tagline, movement macro photography, Geneva Seal certification highlight, "Request an Appointment" CTA |
| Omega Speedmaster | omegawatches.com/watches/speedmaster | Moon heritage storytelling, animated caseback reveal, Co-Axial movement explainer, METAS certification section, "Find a Boutique" integration |
| Audemars Piguet Royal Oak | audemarspiguet.com/royal-oak | Octagonal bezel design narrative, Le Brassus manufacture story, hand-finishing macro video, material selector (steel, gold, ceramic), "Discover in Boutique" CTA |
| TAG Heuer Monaco | tagheuer.com/watches/monaco | Racing heritage timeline, Steve McQueen legacy, square case design story, Calibre Heuer 02 movement breakdown, price displayed prominently |

**Patterns to incorporate:**
- Product hero with slow rotation or interactive 360-degree view on minimal background
- Movement macro photography revealing hand-finishing (Geneva stripes, perlage, beveled edges)
- Material storytelling with close-up textures (gold grain, titanium brushing, ceramic polish)
- Dial artistry section with extreme close-ups showing enamel, guilloche, or meteorite details
- Heritage timeline connecting the watch to brand history and iconic predecessors
- Certification badges prominently displayed (COSC, Geneva Seal, METAS, Poincon de Geneve)
- "Request Appointment" or "Discover in Boutique" as primary CTA (not e-commerce "Buy")
- Limited edition numbering and collector value narrative
- Caseback reveal showing movement through sapphire crystal

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Luxury Watch Detail (e.g., Patek Philippe Nautilus 5811/1G)**

1. **titlebar**
   Maison crest, nav links (Collection, Craftsmanship, Heritage, Boutiques, Magazine), hamburger for mobile, "Request an Appointment" button.

2. **layout-row (Hero -- Watch Showcase + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- dial face straight-on, angled wrist shot, caseback movement view, bracelet detail, lume shot in darkness, lifestyle on wrist). Right column: **eyebrow** ("Nautilus Collection"), **heading** ("Nautilus 5811/1G-001"), **paragraph** ("White Gold. Blue-Black Gradient Dial. The evolution of an icon."), **badge** ("New 2026"), **caption** ("White Gold | 41mm | Self-Winding"), **heading** ("CHF 56,950"), **button** ("Request an Appointment"), **button** ("Find a Boutique"), **caption** ("Available exclusively in Patek Philippe Boutiques.").

3. **layout-row (Feature 1: Movement & Complications)** -> `comp_0_components_2`
   Left column: **image** (caseback macro showing Caliber 26-330 S C movement -- Geneva stripes, gold rotor, hand-beveled bridges). Right column: **eyebrow** ("Movement"), **heading** ("Caliber 26-330 S C"), **paragraph** (movement narrative -- ultra-thin self-winding mechanical movement, Spiromax balance spring in Silinvar, 45-hour power reserve, date complication with patented rapid-correction mechanism). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "304 Components", "45 hr Power Reserve", "28,800 vph Frequency". **accordion** with items: "Self-Winding Mechanism -- 22K gold micro-rotor visible through sapphire caseback", "Spiromax Balance Spring -- Silinvar anti-magnetic technology for superior accuracy", "Date Complication -- Patented rapid-advance correction at the 3 o'clock position", "Hand Finishing -- Every bridge hand-decorated with Geneva stripes and beveled edges". **badge** ("Patek Philippe Seal").

4. **layout-row (Feature 2: Case Material -- White Gold)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Material"), **heading** ("18K White Gold"), **paragraph** (material narrative -- solid 18K white gold case, satin-brushed and polished surfaces, the same hand-finishing techniques used for over 180 years, each case requires 30+ hours of hand polishing). **counter-up** ("30") + **caption** ("Hours of Hand Polishing Per Case"). Right column: **carousel** (material close-ups -- side profile showing alternating brushed/polished finish, crown detail, bezel octagonal corners, lug attachment points). **paragraph** ("The Nautilus case is carved from a single block of 18K white gold, ensuring structural integrity and a seamless silhouette.").

5. **layout-row (Feature 3: Dial Artistry)** -> `comp_0_components_4`
   Full-width **image** (extreme macro of dial -- showing horizontal embossed pattern catching light, applied gold hour markers, luminescent coating). Below: **eyebrow** ("The Dial"), **heading** ("A Gradient of Mastery"), **paragraph** (dial artistry narrative -- blue-black graduated dial with horizontal embossed pattern, each dial stamped and lacquered in multiple layers, applied gold hour markers with luminescent coating). **columnsgrid** (3 columns) each with **image** (extreme close-up) + **caption**: "Horizontal Emboss Pattern" ("Stamped under 50 tonnes of pressure"), "Applied Gold Markers" ("Each index individually soldered by hand"), "Luminescent Hands" ("Dauphine hands with luminous coating for low-light readability"). **paragraph** ("No two dials are identical. The gradient effect shifts with every angle of light.").

6. **layout-row (Feature 4: Bracelet Craftsmanship)** -> `comp_0_components_5`
   Left column: **image** (bracelet laid flat showing articulation, alternating satin and polished links). Right column: **eyebrow** ("Bracelet"), **heading** ("The Nautilus Bracelet"), **paragraph** (bracelet narrative -- integrated bracelet design with alternating satin-brushed and polished surfaces, fold-over clasp with Patek Philippe engraving, each link individually hand-adjusted for perfect drape). **counter-up** ("168") + **caption** ("Individual Components in the Bracelet"). **image** (close-up of clasp mechanism -- fold-over with security lock). **caption** ("Seamless integration between case and bracelet -- a hallmark of the Nautilus since 1976.").

7. **layout-row (Feature 5: Water Resistance)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Engineering"), **heading** ("120 Metres Water Resistance"), **paragraph** (water resistance story -- screw-down crown and caseback, rubber gaskets tested under pressure, the porthole-inspired case construction that gives the Nautilus both its name and its strength). **counter-up** ("120") + **caption** ("Metres / 12 ATM"). **progress-bar** (depth rating visual -- 120m on a scale). Right column: **image** (underwater product shot or porthole-inspired design overlay). **badge** ("Screw-Down Crown & Back").

8. **layout-row (Feature 6: Brand Maison Heritage)** -> `comp_0_components_7`
   Full-width dark background. **eyebrow** ("Heritage"), **heading** ("Begin Your Own Tradition"). **carousel** (heritage timeline slides): Slide 1: **image** (1839 founding) + **caption** ("1839 -- Antoine Norbert de Patek founds the Maison"), Slide 2: **image** (1932 Calatrava) + **caption** ("1932 -- The Calatrava defines dress watch elegance"), Slide 3: **image** (1976 original Nautilus) + **caption** ("1976 -- Gerald Genta designs the Nautilus"), Slide 4: **image** (current Nautilus) + **caption** ("2026 -- The Nautilus 5811 continues the legacy"). **blockquote** ("'You never actually own a Patek Philippe. You merely look after it for the next generation.'"). **paragraph** ("For over 185 years, Patek Philippe has represented the pinnacle of Genevan watchmaking.").

9. **layout-row (Feature 7: Limited Edition Story)** -> `comp_0_components_8`
   **eyebrow** ("Rarity"), **heading** ("Coveted by Collectors"), **paragraph** (limited production narrative -- Patek Philippe produces fewer than 70,000 watches annually across all models, the Nautilus in white gold represents one of the most sought-after references in modern horology). **columnsgrid** (2 columns): Column 1: **counter-up** ("70000") + **caption** ("Annual Production, All Models"), Column 2: **image** (archival image of original 1976 Nautilus alongside current model). **paragraph** ("Demand for the Nautilus consistently exceeds availability. Each piece is allocated through authorized boutiques."). **badge** ("Boutique Exclusive").

10. **layout-row (Feature 8: Investment Value)** -> `comp_0_components_9`
    **eyebrow** ("Value"), **heading** ("An Enduring Asset"), **paragraph** (investment and value retention narrative -- Patek Philippe timepieces consistently appreciate, auction records demonstrate enduring desirability, the Nautilus family holds some of the highest secondary market premiums in horology). **columnsgrid** (3 columns) each with **icon** + **heading** + **caption**: "Heritage Value" ("185+ years of unbroken Genevan tradition"), "Auction Records" ("Patek Philippe holds the world record for most expensive watch sold"), "Generational Legacy" ("Designed to be passed down through generations"). **caption** ("Investment value is never guaranteed. Past performance is not indicative of future value.").

11. **layout-row (Feature 9: Price & Boutique)** -> `comp_0_components_10`
    **eyebrow** ("Acquire"), **heading** ("Visit a Patek Philippe Boutique"). **paragraph** (boutique experience -- personal consultation with a specialist, try-on experience, understanding of the caliber and complications, authentication and registration). **heading** ("CHF 56,950"). **button** ("Request an Appointment"), **button** ("Find a Boutique"). **caption** ("Pricing may vary by region. Please contact your nearest boutique for exact pricing and availability.").

12. **layout-row (Feature 10: Certification -- Patek Philippe Seal)** -> `comp_0_components_11`
    **eyebrow** ("Certification"), **heading** ("The Patek Philippe Seal"), **paragraph** (certification narrative -- exceeds all industry standards including COSC, the Patek Philippe Seal guarantees accuracy to -3/+2 seconds per day, finishing quality, and lifetime serviceability). **columnsgrid** (3 columns) each with **image** (seal/certification visual) + **caption**: "Patek Philippe Seal" ("The most demanding quality standard in watchmaking"), "Lifetime Service" ("Your timepiece will be maintained for generations"), "Accuracy Guarantee" ("-3/+2 seconds per day, surpassing COSC standards"). **image** (Patek Philippe Seal emblem -- large, centered).

13. **layout-row (Related Timepieces)** -> `comp_0_components_12`
    **heading** ("Explore the Nautilus Collection"). **columnsgrid** (3 columns) each with **image** (watch on wrist), **heading** (reference number), **caption** (material + complication), **button** ("Discover").

14. **layout-row (Magazine & Stories)** -> `comp_0_components_13`
    **eyebrow** ("Stories"), **heading** ("From the Patek Philippe Magazine"). **columnsgrid** (3 columns) each with **image** (editorial photo), **heading** (article title), **caption** (date), **link** ("Read More").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Collections, Craftsmanship, Heritage, Boutiques. **br** (divider). **caption** (legal disclaimers, copyright, "Geneva, Switzerland").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new watch reference launch

**Page: New Reference Reveal (e.g., "Omega Speedmaster Silver Snoopy Award 50th Anniversary")**

1. **titlebar** -- Maison logo, minimal nav (The Watch, The Story, Specifications, Boutiques), "Find a Boutique" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic reveal -- watch emerging from moonscape, Snoopy animation on caseback). Overlay: **eyebrow** ("50th Anniversary"), **heading** ("Silver Snoopy Award"), **paragraph** ("A tribute to space, precision, and a small beagle who saved a mission."), **button** ("Discover the Story").

3. **layout-row (Hero Stats)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** stats: "42mm Case", "Co-Axial Master Chronometer", "50 hr Power Reserve", "150m Water Resistance".

4. **layout-row (The Story)** -- **eyebrow** + **heading** ("Houston, We Have a Watch"), **paragraph** (NASA Silver Snoopy Award story -- Omega's role in Apollo 13), **image** (archival Apollo 13 mission photo).

5. **layout-row (Dial Detail)** -- **heading** ("A Universe on the Dial"), **carousel** (macro shots -- blue aventurine dial, earth subdial at 9 o'clock, animated Snoopy caseback).

6. **layout-row (Movement)** -- **heading** ("Calibre 3861"), **image** (movement macro), **paragraph** (Master Chronometer certification, anti-magnetic to 15,000 gauss).

7. **layout-row (Heritage Timeline)** -- **heading** ("From Moonwatch to Snoopy"), **carousel** (timeline -- 1965 NASA qualification, 1969 Moon landing, 1970 Snoopy Award, 2020 50th Anniversary).

8. **layout-row (Boutique CTA)** -- **heading** ("Visit an Omega Boutique"), **paragraph** ("Experience the Silver Snoopy Award in person"), **button** ("Find a Boutique"), **caption** ("Available in select Omega Boutiques worldwide.").

9. **layout-row (Footer)** -- Minimal footer with legal text, METAS certification note, social icons.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-reference browsing layout for a maison's collection range

**Page: Collection Range (e.g., "Rolex Collection")**

1. **titlebar** -- Maison crown, nav (Professional, Classic, Cellini, Configure, Find a Retailer), search.

2. **layout-row (Hero)** -- **heading** ("The Rolex Collection"), **paragraph** ("Every Rolex tells a story."), **image** (editorial collection spread). **layout-row** with filters: **dropdown** (Collection -- Professional, Classic, Cellini), **dropdown** (Material -- Oystersteel, Yellow Gold, Everose, Platinum), **dropdown** (Size), **button** ("Explore").

3. **layout-row (Category: Professional)** -- **eyebrow** ("Professional Watches"), **heading** ("Instruments of Achievement"). **columnsgrid** (3 columns) each card: **image** (watch face), **badge** ("Iconic" where applicable), **heading** (model name -- "Submariner", "GMT-Master II", "Daytona"), **caption** (starting reference price), **paragraph** (one-line heritage tagline), **button** ("Discover"), **button** ("Configure").

4. **layout-row (Category: Classic)** -- **eyebrow** ("Classic Watches"), **heading** ("Timeless Elegance"). Same card grid for Datejust, Day-Date, Sky-Dweller.

5. **layout-row (Category: Cellini)** -- **eyebrow** ("Cellini"), **heading** ("The Essence of Classicism"). Same card grid for Cellini range.

6. **layout-row (Collection Comparison)** -- **heading** ("Compare References"). **columnsgrid** (3 columns): Column headers with **dropdown** (select reference). Below: spec rows -- Case Size, Material, Movement, Water Resistance, Power Reserve, Complications, Reference Price.

7. **layout-row (Rolex Certified)** -- **heading** ("Superlative Chronometer"), **paragraph** ("Every Rolex is a Superlative Chronometer Officially Certified"), **columnsgrid** (3 columns) with **icon** + **caption**: "COSC Certified", "Rolex Superlative Testing", "-2/+2 Seconds Per Day".

8. **layout-row (Find a Retailer CTA)** -- **heading** ("Visit an Official Rolex Retailer"), **form** with **textbox** (City or Postcode), **button** ("Find Retailer").

9. **layout-row (Footer)** -- Full footer with collection links, about Rolex, find retailer, legal.
