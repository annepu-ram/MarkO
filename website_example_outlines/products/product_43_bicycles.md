# Bicycles & Sports Gear -- Product Pages

> Focus: Performance-specification storytelling with trackable sections for frame technology, drivetrain, brake systems, and terrain matching that let bike shops and brands measure which technical details and riding scenarios convert browsers into test-ride bookings and online purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Trek Madone SLR | trekbikes.com/madone-slr | Aero-optimized hero with wind tunnel data, IsoFlow technology explainer, frame material deep-dive (OCLV 800 carbon), component spec table with expandable rows, size calculator integration, "Find a Retailer" CTA |
| Specialized Tarmac SL8 | specialized.com/tarmac-sl8 | Race-focused hero with pro team imagery, FACT 12r carbon layup story, aero + weight data comparison charts, rider-first engineering explainer, S-Works vs Comp tier comparison, Retul fit system link |
| Giant Propel Advanced | giant-bicycles.com/propel-advanced | CFD aero visualization hero, Advanced Composite carbon technology section, AeroSystem Shaping Technology explainer, integrated cockpit detail, geometry chart with rider height mapping |
| Firefox Monsoon Pro | firefoxbikes.com/monsoon-pro | Terrain-focused hero with trail imagery, alloy frame specs, Shimano drivetrain breakdown, hydraulic disc brake feature, color variant selector, EMI option badge |
| Hero Lectro Kinza | herolectro.com/kinza | E-bike focused hero with range counter, motor + battery specs, pedal assist mode explanation, charging time indicator, terrain compatibility grid, test ride booking form |

**Patterns to incorporate:**
- Dynamic hero with the bike in action or in dramatic studio lighting
- Frame material and geometry technical section with diagrams
- Drivetrain and gear system breakdown with component hierarchy
- Brake technology explanation with stopping power visualization
- Wheel and tire specifications with terrain compatibility
- Weight as a prominent spec with comparison to competitors
- Color and variant selector with image swap
- Size guide with height-to-frame mapping calculator
- Price tier comparison showing different build kits
- Test ride booking or dealer locator CTA

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Bicycle Product Detail (e.g., Trek Madone SLR 9 -- Road Bike)**

1. **titlebar**
   Brand logo, nav links (Road, Mountain, Gravel, E-Bikes, Accessories, Find a Store), hamburger for mobile, "Book Test Ride" button.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- side profile studio shot, front 3/4 angle, rear drivetrain detail, cockpit/handlebar view, frame close-up showing carbon weave, action shot on road). Right column: **eyebrow** ("Road | Race | S-Works Level"), **heading** ("Madone SLR 9"), **paragraph** ("The fastest road bike in the world. Aerodynamic mastery meets IsoFlow comfort technology -- proven in the Tour de France, now in your hands."), **badge** ("Tour de France Winner"), **rating** (4.9 stars, "320 Reviews"), **caption** ("USD 12,499"), **button** ("Find in Store"), **button** ("Book Test Ride"), **link** ("Compare Madone Models").

3. **layout-row (Feature 1: Frame Material & Geometry)** -> `comp_0_components_2`
   Left column: **image** (frame close-up showing OCLV 800 carbon fiber layup pattern). Right column: **eyebrow** ("Frame Technology"), **heading** ("OCLV 800 Carbon"), **paragraph** ("Trek's highest-grade carbon fiber, hand-laid in Waterloo, Wisconsin. 800-series OCLV delivers the optimal balance of stiffness, compliance, and weight -- 500 grams lighter than the previous generation while maintaining power transfer at the bottom bracket."). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "800" / "g Frame Weight (56cm)", "68" / "mm BB Stiffness (Nm/deg)", "14" / "% More Compliant Than SLR 7". **accordion** with items: "Carbon Layup Schedule (800-series optimized ply orientation)", "Frame Geometry (Race-fit, aggressive stack/reach)", "IsoFlow Rear Decoupler (Isolates vibration without sacrificing stiffness)", "Headtube & BB Standards (Tapered 1-1/8 to 1-1/2, T47)".

4. **layout-row (Feature 2: Gear System)** -> `comp_0_components_3`
   Left column: **eyebrow** ("Drivetrain"), **heading** ("SRAM Red AXS"), **paragraph** ("Wireless electronic shifting with 12-speed precision. The SRAM Red AXS groupset delivers instant, silent gear changes at the touch of a button, with a power meter integrated into the crankset for real-time performance data."). **columnsgrid** (2 columns): Column 1 -- **heading** ("Front") + **paragraph** ("50/37T chainrings, power meter spider"), **heading** ("Rear") + **paragraph** ("10-33T cassette, 12-speed"); Column 2 -- **heading** ("Shifting") + **paragraph** ("Wireless electronic, 2x12, eTap AXS"), **heading** ("Chain") + **paragraph** ("SRAM Red Flattop, 12-speed"). Right column: **image** (rear derailleur and cassette close-up). **badge** ("Integrated Power Meter").

5. **layout-row (Feature 3: Brake Type)** -> `comp_0_components_4`
   Left column: **image** (hydraulic disc brake caliper and rotor close-up, showing heat dissipation fins). Right column: **eyebrow** ("Braking"), **heading** ("Hydraulic Disc Brakes"), **paragraph** ("SRAM Red AXS hydraulic disc brakes with 160mm rotors front and rear deliver confident, consistent stopping power in all conditions -- wet or dry, steep descents or technical corners."). **columnsgrid** (3 columns) with **icon** + **caption**: "All-Weather" / "Consistent power in rain and heat", "Modulation" / "Progressive feel, no lock-up", "Low Maintenance" / "Self-adjusting pads, easy bleed". **paragraph** ("Rotor size: 160mm flat-mount. Pad compound: sintered metallic for extended life.").

6. **layout-row (Feature 4: Wheel Size & Tires)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Wheels & Tires"), **heading** ("Bontrager Aeolus RSL 51"), **paragraph** ("Purpose-built for the Madone, these full-carbon clincher wheels feature a 51mm deep rim profile optimized in Trek's wind tunnel. Wide internal width (21mm) supports tubeless tires for lower rolling resistance and better grip."). Right column: **image** (wheel side profile showing rim depth and tire width). **columnsgrid** (2 columns): Column 1 -- **heading** ("Wheels") + **paragraph** ("51mm depth, 21mm internal, tubeless-ready, DT Swiss 240 hubs"); Column 2 -- **heading** ("Tires") + **paragraph** ("Bontrager R4 320 TLR, 700x28c, tubeless, 120 TPI"). **caption** ("Tire clearance: up to 32mm for versatility on mixed surfaces.").

7. **layout-row (Feature 5: Suspension / Comfort System)** -> `comp_0_components_6`
   Left column: **image** (IsoFlow technology diagram -- cutaway view of the seat tube junction showing the decoupler). Right column: **eyebrow** ("Comfort Technology"), **heading** ("IsoFlow"), **paragraph** ("Trek's patented IsoFlow technology replaces the traditional seat tube junction with a structural void that flexes to absorb road vibration. The result: 14% more compliance than a standard frame with zero loss of power transfer."). **video** (slow-motion footage of the IsoFlow section flexing over cobblestones). **paragraph** ("Proven over 3,000 km of cobblestoned classics racing. Less fatigue means more power in the final kilometers.").

8. **layout-row (Feature 6: Weight)** -> `comp_0_components_7`
   **eyebrow** ("Weight"), **heading** ("Every Gram Counts"). **columnsgrid** (4 columns) each with **counter-up** + **caption**: "7.1" / "kg Complete Bike (56cm)", "800" / "g Frame Only", "1380" / "g Wheelset", "190" / "g Saddle (Bontrager Aeolus RSL)". **progress-bar** labeled "UCI Legal Weight" at 100% (at 6.8kg UCI minimum reference). **paragraph** ("The Madone SLR 9 arrives race-ready at 7.1 kg -- just 300 grams above the UCI minimum weight limit. Additional weight savings possible with tubular wheels.").

9. **layout-row (Feature 7: Terrain Match)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Where It Excels"), **heading** ("Built for Speed"), **paragraph** ("The Madone SLR 9 is purpose-built for road racing, flat-to-rolling terrain, and situations where aerodynamic advantage matters most."). Right column: **columnsgrid** (2 columns): Column 1 -- **heading** ("Ideal For") + **accordion** with items: "Road Racing & Criteriums (Aero advantage in pack riding)", "Time Trials & Triathlons (With clip-on bar option)", "Flat to Rolling Terrain (Where aero beats weight)", "Gran Fondos & Sportives (IsoFlow comfort for long days)"; Column 2 -- **heading** ("Consider Instead") + **accordion** with items: "Pure Climbing: Emonda SLR (5.9 kg)", "Gravel & Adventure: Checkpoint SLR", "Endurance & Comfort: Domane SLR", "All-Road: Domane+ LT (e-assist)". **badge** ("Aero Optimized").

10. **layout-row (Feature 8: Colors)** -> `comp_0_components_9`
    **eyebrow** ("Finishes"), **heading** ("Choose Your Colorway"). **carousel** (bike in each available color -- "Viper Red/Carbon Smoke", "Trek Black/Carbon Smoke", "Icon Yellow" limited edition). Below: **columnsgrid** (color swatch tiles as **image** + **caption** per color). **paragraph** ("Project One custom paint available -- choose from 40+ colors and patterns. 6-8 week lead time."). **button** ("Open Project One Configurator").

11. **layout-row (Feature 9: Price & Variants)** -> `comp_0_components_10`
    **eyebrow** ("Models"), **heading** ("Choose Your Build"). **tabs** with tab per build: "SLR 9 AXS" (USD 12,499), "SLR 7 AXS" (USD 8,499), "SLR 6 AXS" (USD 5,999), "SL 6" (USD 3,999). Each tab: **heading** (model + price), **columnsgrid** (2 columns) with key spec differences (groupset, wheels, seatpost, cockpit), **button** ("Find in Store"). **paragraph** ("Financing available: from USD 167/month with Trek Card. 0% APR for 36 months on purchases over USD 2,000."). **button** ("Compare All Madone Models").

12. **layout-row (Feature 10: Size Guide)** -> `comp_0_components_11`
    **eyebrow** ("Fit"), **heading** ("Find Your Size"). **columnsgrid** (2 columns): Left -- size chart table as **paragraph** entries per size (47, 50, 52, 54, 56, 58, 60, 62) mapped to rider height ranges; Right -- **image** (geometry diagram with labeled dimensions -- stack, reach, seat tube, wheelbase). **paragraph** ("For precise fit, visit a Trek retailer for a professional bike fit session using our Precision Fit system."). **button** ("Use Size Calculator"). **caption** ("All sizes share identical ride characteristics through our H1.5 Race Fit geometry.").

13. **layout-row (Reviews)** -> `comp_0_components_12`
    **eyebrow** ("Rider Reviews"), **heading** ("What Riders Say"). **rating** (4.9 overall). **columnsgrid** (3 columns) each with **rating**, **blockquote** (review), **caption** (rider + size purchased + "Verified Purchase"). **ticker** scrolling professional review snippets: "BikeRadar: 9.5/10", "Cycling Weekly: Bike of the Year", "Road.cc: Editors' Choice". **button** ("Read All Reviews").

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your Setup"). **columnsgrid** (4 columns) each with **image**, **heading** (product name), **caption** (category + price), **button** ("View"): "Bontrager Aeolus RSL Helmet" / "USD 299", "Bontrager Velocis Jersey" / "USD 149", "Bontrager R4 Shoes" / "USD 399", "Bontrager Flare RT Taillight" / "USD 99".

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Bikes (Road, Mountain, Gravel, E-Bikes), Support (Size Guide, Bike Fit, Warranty), Find Us (Store Locator, Test Rides, Events), Company (About Trek, Sustainability, Racing). **br** (divider). **caption** (copyright, "Handmade in Waterloo, Wisconsin").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new bike model launch

**Page: New Model Launch (e.g., "Specialized Tarmac SL8 -- The Fastest All-Road")**

1. **titlebar** -- Brand logo, minimal nav (The Bike, Technology, Ride, Configure), "Pre-Order" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic race footage -- Soudal Quick-Step team descending a mountain pass, slow-motion sprint finish, studio beauty shots). Overlay: **eyebrow** ("The Next Generation"), **heading** ("Tarmac SL8"), **paragraph** ("Lighter. Faster. Everything."), **button** ("Pre-Order"), **caption** ("Deliveries begin April 2026").

3. **layout-row (The Numbers)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** + **caption**: "685" / "g Frame (56cm)", "45" / "Seconds Faster Over 40km", "32" / "mm Tire Clearance", "1" / "Bike to Rule Them All". **paragraph** ("For the first time, one bike is the lightest, most aero, and most comfortable in its class.").

4. **layout-row (Rider-First Engineering)** -- **heading** ("Rider-First Engineered"), **paragraph** ("Every frame size has unique carbon layup, tube shapes, and ride characteristics. A 49cm rides like a 56cm -- same stiffness-to-weight ratio, same compliance, same handling."), **image** (comparison diagram of different frame sizes with engineering callouts).

5. **layout-row (FACT 12r Carbon)** -- **heading** ("FACT 12r Carbon"), **image** (microscopic carbon fiber visualization), **paragraph** ("Our fastest carbon layup ever. 500 hours of CFD simulation and 200+ prototypes."). **carousel** (manufacturing process shots).

6. **layout-row (Pro Proven)** -- **heading** ("Race Proven"), **ticker** scrolling race wins: "Tour de France Stage 1", "Paris-Roubaix", "World Championships ITT", "Giro d'Italia GC". **carousel** (pro rider imagery with quotes).

7. **layout-row (Configure CTA)** -- **heading** ("Build Your Tarmac SL8"), **paragraph** ("From S-Works to Sport -- 6 build kits starting at USD 3,500"), **image** (tier comparison), **button** ("Open Configurator"), **button** ("Find a Retailer").

8. **layout-row (Footer)** -- Minimal footer with retailer locator, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a bike brand's full lineup

**Page: Brand Lineup (e.g., "Giant -- All Bikes")**

1. **titlebar** -- Brand logo, nav (Road, Mountain, Gravel, City, E-Bikes, Kids, Accessories), search, "Find a Dealer" button.

2. **layout-row (Hero)** -- **heading** ("Find Your Perfect Ride"), **paragraph** ("Performance bikes for every rider and every terrain"), **image** (editorial -- lineup of bikes against mountain backdrop).

3. **layout-row (Filter Bar)** -- **layout-row** with filters: **dropdown** (Category: Road / Mountain / Gravel / City / E-Bike), **dropdown** (Riding Style: Race / Endurance / Trail / Cross-Country / Commute), **dropdown** (Frame Material: Carbon / Aluminum / Chromoly), **dropdown** (Price Range), **dropdown** (Wheel Size: 700c / 29" / 27.5"), **button** ("Apply Filters").

4. **layout-row (Category: Road Bikes)** -- **eyebrow** ("Road"), **heading** ("Speed on Tarmac"). **columnsgrid** (3 columns) each card: **image** (bike), **badge** ("New" / "Bestseller" where applicable), **heading** (model name), **caption** (sub-category + starting price), **paragraph** (one-line USP), **button** ("Explore"), **button** ("Compare").

5. **layout-row (Category: Mountain Bikes)** -- Same card pattern. **eyebrow** ("Mountain"), **heading** ("Command the Trail").

6. **layout-row (Category: E-Bikes)** -- Same card pattern. **eyebrow** ("E-Bikes"), **heading** ("Amplify Your Ride"). **badge** ("Electric Assist") on all cards.

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Bikes Side by Side"). **columnsgrid** (3 columns) each with **dropdown** (select bike). Comparison rows: Price, Frame Material, Weight, Groupset, Brake Type, Wheel Size, Tire Width, Suspension Travel, Terrain Type.

8. **layout-row (Size Guide Hub)** -- **heading** ("Find Your Size"), **paragraph** ("Enter your height and inseam for a personalized recommendation"), **columnsgrid** (2 columns): **textbox** (Height in cm) + **textbox** (Inseam in cm) + **button** ("Calculate"), and size chart reference by category.

9. **layout-row (Test Ride CTA)** -- **heading** ("Try Before You Buy"), **paragraph** ("Book a free test ride at your nearest Giant dealer"), **form** with **textbox** (Pincode/Zip), **button** ("Find Nearest Dealer"). **counter-up** + **caption**: "3000+" / "Dealers Worldwide".

10. **layout-row (Footer)** -- Full footer with bike categories, technology pages, dealer network, warranty, events, social links, legal.
