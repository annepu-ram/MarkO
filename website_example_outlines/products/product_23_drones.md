# Drones & RC — Product Pages

> Focus: Showcasing aerial capabilities through camera quality samples, flight performance stats, intelligent flight modes, and portability visuals that inspire both hobbyists and professionals.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| DJI (Mini 4 Pro) | dji.com/mini-4-pro | "Mini to the Max" tagline hero; scroll-triggered product rotation; weight badge (<249g); camera sample gallery with 4K stills; omnidirectional obstacle sensing diagram; 3-tier bundle comparison (Fly More Combo tiers) |
| DJI (Mavic 3 Pro) | dji.com/mavic-3-pro | Triple-camera system hero with lens comparison; Hasselblad branding; flight time counter-up (43 min); O3+ transmission range (15 km); cinematic aerial footage auto-playing; ActiveTrack 360 demo |
| Autel Robotics | autelrobotics.com | EVO series lineup comparison; 8K camera spec hero; modular payload system section; enterprise vs consumer split navigation; obstacle avoidance sensor diagram with coverage angles |
| Skydio | skydio.com/x10 | Autonomous flight hero (hands-free tracking video); enterprise/defense positioning; AI-powered obstacle avoidance emphasis; 3D scan capability; rugged design with IP55 rating; fleet management software section |
| Holy Stone | holystone.com | Budget-friendly positioning; beginner-friendly features highlighted (altitude hold, headless mode); comparison chart across models; app interface screenshots; kids/family safety messaging |

**Patterns to incorporate:**
- Aerial photography/videography sample gallery (day, night, HDR, hyperlapse)
- Flight time and range counter-up stats prominently displayed
- Weight badge with regulatory significance (<249g = no registration)
- Obstacle avoidance sensor coverage diagram (omnidirectional view)
- Gimbal stabilization demo (smooth vs unstabilized comparison)
- Intelligent flight mode showcase (ActiveTrack, Waypoint, Hyperlapse, QuickShots)
- Folded vs unfolded size comparison for portability
- Controller and app interface mockup
- Bundle tier comparison (Standard, Fly More, Fly More Combo Pro)
- Regulatory compliance section (FAA/DGCA rules, no-fly zones)

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Camera Drone Detail (e.g., DJI Mini 4 Pro / Mavic 3)**

1. **titlebar** — Brand logo, nav links (Drones, Cameras, Accessories, Enterprise, Learn, Support), cart icon, search
2. **layout-row (Hero — Drone Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (drone in flight, folded in hand, controller + drone, camera close-up, aerial sample photo, package contents). Right column: eyebrow ("Consumer Drone"), heading (product name), rating (4.7 stars, review count), paragraph (tagline: "4K/60fps HDR. 34-min flight. Omnidirectional sensing. Under 249g."), heading (price), badge ("Under 249g — No Registration"), button ("Buy Now"), button ("Fly More Combo — Rs XX,XXX"), caption ("Free shipping. 15-day returns.").
3. **layout-row (Feature: Camera Quality & Gimbal)** → `comp_0_components_2`
   Left column: heading ("Cinematic 4K Aerial Imaging") + paragraph (1/1.3-inch CMOS sensor, 48MP photos, 4K/60fps HDR video, 10-bit D-Log M color, 3-axis mechanical gimbal). Counter-up (48) + caption ("Megapixel Sensor"). Right column: carousel (5-6 aerial sample photos/videos — landscape, cityscape, sunset, night, portrait). Badge ("Hasselblad Color Science" or "Professional Grade").
4. **layout-row (Feature: Flight Time & Range)** → `comp_0_components_3`
   Heading ("Fly Longer. Go Further.") + columnsgrid (3 columns): Column 1 — counter-up (34) + heading ("Minutes") + caption ("Max Flight Time") + progress-bar (34 min out of 45 min scale). Column 2 — counter-up (20) + heading ("Kilometers") + caption ("Max Transmission Range"). Column 3 — counter-up (16) + heading ("m/s") + caption ("Max Speed"). Paragraph ("Extended battery option available: 47-minute flight time."). Image (range diagram showing drone-to-controller distance).
5. **layout-row (Feature: GPS & Return-to-Home)** → `comp_0_components_4`
   Left column: image (GPS satellite lock diagram / RTH flight path visualization). Right column: heading ("Always Knows the Way Home") + paragraph (GPS + GLONASS + Galileo tri-satellite positioning, Advanced Return-to-Home with obstacle avoidance, automatic RTH on low battery or signal loss). Accordion: Item 1 — "Smart RTH" (optimal return path calculation), Item 2 — "Low Battery RTH" (auto-triggers at 20%), Item 3 — "Signal Loss RTH" (continues mission or returns), Item 4 — "Precision Landing" (visual positioning for accurate landing).
6. **layout-row (Feature: Obstacle Avoidance)** → `comp_0_components_5`
   Left column: heading ("Omnidirectional Obstacle Sensing") + paragraph (forward, backward, lateral, upward, downward sensors, APAS 5.0 automatic path adjustment). Counter-up (360) + caption ("Degree Sensing Coverage"). Right column: image (drone with sensor coverage angles illustrated — 360-degree diagram). Badge ("APAS 5.0").
7. **layout-row (Feature: Wind Resistance)** → `comp_0_components_6`
   Left column: heading ("Stable in Strong Winds") + paragraph (Level 5 wind resistance, up to 38 km/h, stabilization algorithm, lightweight yet rigid airframe). Progress-bar (wind resistance: Level 5 out of 7). Right column: image (drone hovering steady in windy conditions / wind speed gauge visual). Caption ("Tested and rated for outdoor reliability.").
8. **layout-row (Feature: Weight & Portability)** → `comp_0_components_7`
   Heading ("Fits in Your Palm. Flies Like a Pro.") + columnsgrid (2 columns): Column 1 — image (drone folded in hand, scale reference) + caption ("Folded: 148 x 94 x 64 mm"). Column 2 — image (drone unfolded in flight) + caption ("Unfolded: 298 x 373 x 101 mm"). Counter-up (249) + caption ("Grams — Under Registration Threshold"). Paragraph ("Folds to the size of a smartphone. Carry it anywhere."). Badge ("Sub-250g Class").
9. **layout-row (Feature: Controller & App)** → `comp_0_components_8`
   Left column: image (controller with phone mounted, app showing live feed). Right column: heading ("Intuitive Control") + paragraph (DJI RC 2 with 5.5-inch built-in screen, O4 HD video transmission, low-latency live feed). Accordion: Item 1 — "Built-In Screen Controller" (no phone needed), Item 2 — "Phone Controller Option" (lightweight, app-based), Item 3 — "DJI Fly App" (flight planning, editing, sharing), Item 4 — "Firmware Updates" (OTA via app). Badge ("O4 Transmission").
10. **layout-row (Feature: Flight Modes)** → `comp_0_components_9`
    Heading ("Intelligent Flight Modes") + columnsgrid (4 columns): Column 1 — icon + heading ("ActiveTrack 360") + paragraph ("Lock onto a subject, drone follows automatically"). Column 2 — icon + heading ("Waypoint Flight") + paragraph ("Pre-plan GPS route, drone flies autonomously"). Column 3 — icon + heading ("Hyperlapse") + paragraph ("Cinematic time-lapse in motion"). Column 4 — icon + heading ("QuickShots") + paragraph ("Dronie, Circle, Helix, Rocket, Boomerang"). Carousel below showing sample clips from each flight mode.
11. **layout-row (Feature: Price & Bundles)** → `comp_0_components_10`
    Heading ("Choose Your Kit") + columnsgrid (3 columns): Column 1 — image + heading ("Standard") + paragraph (drone + RC-N2 + 1 battery) + heading (price) + button ("Buy Standard"). Column 2 — image + heading ("Fly More Combo") + badge ("Most Popular") + paragraph (drone + RC-N2 + 3 batteries + charging hub + shoulder bag) + heading (price) + button ("Buy Fly More"). Column 3 — image + heading ("Fly More Combo Plus") + paragraph (drone + DJI RC 2 + 3 Plus batteries + charging hub + ND filters + shoulder bag) + heading (price) + badge ("Best Value") + button ("Buy Combo Plus").
12. **layout-row (Feature: Regulations & Compliance)** → `comp_0_components_11`
    Heading ("Fly Responsibly") + paragraph ("Under 249g drones have simplified regulations in most countries."). Accordion: Item 1 — "Do I need to register?" (registration rules by weight class), Item 2 — "Where can I fly?" (no-fly zones, airport restrictions), Item 3 — "Do I need a license?" (recreational vs commercial), Item 4 — "What about insurance?" (liability considerations), Item 5 — "DGCA/FAA compliance" (built-in geofencing, ADS-B receiver). Badge ("GEO 2.0 Geofencing").
13. **layout-row (Reviews & Sample Gallery)** → `comp_0_components_12`
    Left column: heading ("Pilot Reviews") + rating (4.7 stars) + counter-up (5,640 reviews) + progress-bar (star distribution). Right column: carousel of aerial photography samples submitted by customers + blockquote reviews.
14. **layout-row (Accessories)** → `comp_0_components_13`
    Heading ("Essential Accessories") + columnsgrid (4 columns): Each — image + heading (extra batteries, ND filters, propeller guards, landing pad) + caption (price) + button ("Add to Cart").
15. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Drones, Cameras, Enterprise, Learn to Fly). Column 3 — links (Support, Warranty, Repair, Where to Buy). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Cinematic marketing page for a new drone launch with aerial footage showcase and pre-order urgency

**Page: "SkyVision X1 — See the World From Above"**

1. **titlebar** — Brand logo, minimal nav (Features, Gallery, Specs), CTA button ("Pre-Order Now")
2. **layout-row (Hero — Cinematic Aerial)** → Video-background (breathtaking aerial footage montage — mountains, oceans, cityscapes). Centered overlay: eyebrow ("Introducing"), heading ("SkyVision X1"), paragraph ("4K/120fps. 45-minute flight. Omnidirectional AI sensing."), button ("Pre-Order — Rs 74,990"), countdown (launch date timer).
3. **layout-row (Hero Stats)** → Dark background. columnsgrid (4 columns): counter-up (4) + caption ("K / 120fps"), counter-up (45) + caption ("Min Flight Time"), counter-up (25) + caption ("km Range"), counter-up (249) + caption ("Grams"). Heading ("Redefining What's Possible").
4. **layout-row (Camera System Reveal)** → Full-width aerial photo. Heading ("Triple-Lens Camera System") + columnsgrid (3 columns): Wide, Tele, Ultra-Wide — each with focal length, aperture, use case. Sample photos from each lens.
5. **layout-row (Obstacle Avoidance Demo)** → Left: animated diagram showing 360-degree sensor coverage. Right: heading ("AI-Powered Sensing") + paragraph (next-gen APAS, real-time 3D mapping, forest/urban/indoor capable). Badge ("Zero Collision Guarantee").
6. **layout-row (Portability Story)** → Heading ("From Pocket to Sky in 30 Seconds") + image (folding/unfolding sequence) + counter-up (249) + caption ("Grams") + paragraph (folds smaller than a water bottle, carbon fiber arms).
7. **layout-row (Flight Mode Showcase)** → Carousel: Slide 1 — ActiveTrack 360 demo. Slide 2 — Waypoint Flight. Slide 3 — Hyperlapse. Slide 4 — MasterShots. Slide 5 — Panorama.
8. **layout-row (Aerial Gallery)** → Heading ("Shot on SkyVision X1") + columnsgrid (3 columns, 2 rows) of stunning aerial photographs with location captions.
9. **layout-row (Bundle Pre-Orders)** → columnsgrid (3 columns): Standard, Fly More Combo, Pro Combo — each with contents list, price, button. Badge ("Early Bird Price") on Pro Combo.
10. **layout-row (Pro Endorsements)** → Ticker (photographer/videographer names). Carousel of blockquotes from professional drone pilots.
11. **layout-row (Final CTA)** → Heading ("Your Next Masterpiece is Waiting Above") + button ("Pre-Order Now") + countdown + caption ("Free priority shipping on pre-orders.").
12. **layout-row (Footer)** → Minimal footer with brand, specs link, legal, social.

---

## Variant C — Product Catalog / Comparison Page

> Multi-drone browsing experience for comparing models and finding the right drone for any skill level

**Page: "Drones — From Beginner to Professional"**

1. **titlebar** — Brand logo (retailer), nav (Consumer, Professional, FPV, Enterprise, Accessories, Learn to Fly), search, cart
2. **layout-row (Category Hero)** → Full-width aerial landscape photo. Heading ("Drones for Every Pilot") + paragraph ("Compare specs, explore bundles, and find your perfect drone") + eyebrow ("Free shipping on orders over Rs 9,999").
3. **layout-row (Skill Level Quick Nav)** → columnsgrid (3 columns): Column 1 — icon + heading ("Beginner") + paragraph ("Easy to fly, GPS-assisted, under Rs 30K") + button ("Browse Beginner"). Column 2 — icon + heading ("Intermediate") + paragraph ("4K camera, longer flights, obstacle sensing") + button ("Browse Intermediate"). Column 3 — icon + heading ("Professional") + paragraph ("Cinematic quality, maximum range, pro accessories") + button ("Browse Professional").
4. **layout-row (Model Comparison Table)** → Heading ("Compare Popular Drones") + columnsgrid (5 columns): Column 1 (spec labels: Camera, Flight Time, Range, Weight, Obstacle Sensing, Max Speed, Price), Columns 2-5 (DJI Mini 4 Pro, DJI Air 3, Autel EVO Nano+, DJI Mavic 3 Pro). Badges on "Best Budget", "Best Value", "Best Pro".
5. **layout-row (Bestsellers)** → Heading ("Bestsellers") + columnsgrid (4 columns): Each — image, badge, heading (drone name), rating, paragraph (key specs), heading (price), button ("View Details").
6. **layout-row (Under 250g Collection)** → Heading ("Under 250g — No Registration Required") + paragraph ("Fly without the paperwork.") + columnsgrid (3 columns): Sub-250g drones with image, name, flight time, camera spec, price, button. Badge ("No Registration").
7. **layout-row (FPV & Racing)** → Heading ("FPV & Racing Drones") + columnsgrid (3 columns): FPV drone cards with image, name, max speed, goggles compatibility, price, button. Badge ("Adrenaline Rush").
8. **layout-row (Buying Guide)** → Heading ("Drone Buying Guide") + accordion: Item 1 ("Which drone is best for beginners?"), Item 2 ("Do I need a license to fly?"), Item 3 ("What camera specs matter most?"), Item 4 ("How important is obstacle avoidance?"), Item 5 ("Battery life — what's realistic?"), Item 6 ("What accessories do I need on day one?").
9. **layout-row (Accessories)** → Heading ("Essential Accessories") + tabs: Tab 1 ("Batteries" — grid), Tab 2 ("ND Filters" — grid), Tab 3 ("Cases & Bags" — grid), Tab 4 ("Propellers & Guards" — grid). Each product: image, name, compatibility, price, button.
10. **layout-row (Customer Aerial Gallery)** → Heading ("Shot by Our Customers") + carousel of aerial photos with drone model + photographer credit.
11. **layout-row (Learn to Fly)** → Heading ("New to Drones?") + columnsgrid (3 columns): Column 1 — link ("Beginner's Guide"). Column 2 — link ("Flight Regulations"). Column 3 — link ("Best First Flights Near You"). Button ("Join Our Pilot Community").
12. **layout-row (Newsletter)** → Left column: heading ("Drone News & Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help Choosing?") + paragraph + button ("Ask a Drone Expert").
13. **layout-row (Footer)** → columnsgrid (4 columns): Store info, product categories, support, contact + social.
