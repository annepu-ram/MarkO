# Electric Scooters & E-Bikes — Product Pages

> Focus: Converting range anxiety into range confidence through real-world range data, charging infrastructure maps, cost-of-ownership calculators, and test-ride booking CTAs that move prospects from browsing to showroom visits.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Ola Electric (S1 Pro) | olaelectric.com/s1-pro | Full-screen hero with scooter color rotation; range counter-up (170 km); performance stats (0-40 in 2.9s); color configurator with real-time price; Hypercharger network map; EMI calculator inline |
| Ather (450X) | atherenergy.com/450 | Scroll-triggered spec reveals; 7-inch touchscreen dashboard demo; ride mode comparison (Eco/Ride/Sport/Warp); Ather Grid charging map; connected features app mockup; test ride booking as primary CTA |
| TVS iQube | tvsmotor.com/electric-scooters/tvs-iqube | Variant comparison hero (iQube, iQube S, iQube ST); 118+ connected features counter; range per variant comparison chart; SmartXonnect app features section; EMI starts at pricing; dealer locator |
| Hero Vida V1 | vidaworld.com | Lifestyle-first hero (urban commuter scenes); 3 ride modes with animation; removable battery highlight; Hero MotoCorp trust heritage; charging time comparison; subsidy calculator by state |
| Bajaj Chetak | chetak.com | Premium retro design hero; neo-retro positioning; craftsmanship close-ups; Bajaj legacy messaging; test ride + booking CTA; color palette selector; city-wise pricing with subsidies |

**Patterns to incorporate:**
- Color configurator with 360-degree rotation and real-time price update
- Range per charge displayed prominently with riding mode breakdown (Eco vs Sport)
- Charging time visualization (0% to 100% progress bar with time markers)
- Hypercharger / charging station map with network coverage
- Cost-of-ownership calculator (EV vs petrol monthly/annual savings)
- Subsidy calculator by state (FAME II, state subsidy amounts)
- Test ride booking as primary CTA throughout the page
- Dashboard/display demo showing connected features
- Performance stats with 0-40 km/h acceleration time
- EMI calculator integrated near price section

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Electric Scooter Detail (e.g., Ather 450X / Ola S1 Pro)**

1. **titlebar** — Brand logo, nav links (Scooters, Charging, App, Ownership, Test Ride, Support), book test ride button
2. **layout-row (Hero — Scooter Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (scooter 360 views in different colors, dashboard close-up, riding action shot, charging, storage compartment). Right column: eyebrow ("Electric Performance"), heading (scooter name), paragraph (tagline: "170 km range. 0-40 in 2.9 seconds. Connected intelligence."), heading (price: "Ex-showroom from Rs 1,09,999"), badge ("FAME II Subsidy Applied"), caption ("On-road price varies by state"), button ("Book Test Ride"), button ("Reserve Now — Rs 999"), caption ("Refundable booking amount.").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Range per Charge)** → `comp_0_components_2`
   Heading ("Go Further on Every Charge") + columnsgrid (3 columns): Column 1 — counter-up (170) + heading ("km") + caption ("Eco Mode") + paragraph ("Optimized for maximum range at moderate speeds"). Column 2 — counter-up (120) + heading ("km") + caption ("Ride Mode") + paragraph ("Balanced performance and range for daily commute"). Column 3 — counter-up (90) + heading ("km") + caption ("Sport Mode") + paragraph ("Maximum acceleration and top speed"). Progress-bar (range visual: 170 km vs industry avg 100 km). Badge ("Certified Range — IDC Tested").
5. **layout-row (Feature: Top Speed & Performance)** → `comp_0_components_3`
   Left column: heading ("Instant Torque. Zero Lag.") + paragraph (mid-drive motor, regenerative braking, hill-start assist) + counter-up (90) + caption ("km/h Top Speed") + counter-up (2.9) + caption ("Seconds 0-40 km/h"). Right column: image (scooter in motion, speed blur). Badge ("Class-Leading Acceleration").
6. **layout-row (Feature: Motor Power)** → `comp_0_components_4`
   Left column: image (motor diagram or cutaway showing PMSM motor). Right column: heading ("8.5 kW Peak Power PMSM Motor") + paragraph (permanent magnet synchronous motor, 26 Nm torque, IP67 rated, maintenance-free). Counter-up (8.5) + caption ("kW Peak Power"). Progress-bar (power output comparison vs competitors). Caption ("Brushless motor — zero maintenance for life.").
7. **layout-row (Feature: Battery & Charging Time)** → `comp_0_components_5`
   Heading ("Smart Battery. Fast Charging.") + columnsgrid (2 columns): Column 1 — heading ("Home Charging") + image (portable charger plugged in) + paragraph ("0-80% in 4.5 hours. Full charge in 6.5 hours via standard 5A socket.") + progress-bar (charging progress with time markers: 0%, 50% at 3h, 80% at 4.5h, 100% at 6.5h). Column 2 — heading ("Fast Charging") + image (fast charger station) + paragraph ("0-80% in 60 minutes at branded fast charger network.") + progress-bar (fast charge: 0%, 80% at 60 min). Badge ("3.97 kWh Li-Ion Battery"). Caption ("Battery management system with 9-stage protection.").
8. **layout-row (Feature: Frame & Weight)** → `comp_0_components_6`
   Left column: heading ("Engineered for Urban Agility") + paragraph (tubular steel frame, 108 kg kerb weight, 780 mm seat height, flat footboard) + counter-up (108) + caption ("kg Kerb Weight"). Right column: image (frame close-up showing build quality) + columnsgrid (2 columns): Column 1 — caption ("Seat Height: 780 mm"). Column 2 — caption ("Ground Clearance: 160 mm").
9. **layout-row (Feature: Braking System)** → `comp_0_components_7`
   Heading ("Confident Stopping Power") + columnsgrid (3 columns): Column 1 — icon + heading ("Disc Brake — Front") + paragraph ("220 mm disc with CBS"). Column 2 — icon + heading ("Disc Brake — Rear") + paragraph ("190 mm disc with regenerative braking"). Column 3 — icon + heading ("Regenerative Braking") + paragraph ("Recovers energy on deceleration, extends range up to 8%"). Badge ("Combined Braking System").
10. **layout-row (Feature: Display & App)** → `comp_0_components_8`
   Left column: image (7-inch touchscreen dashboard close-up showing navigation, speed, battery, call). Right column: heading ("7-Inch Smart Dashboard") + paragraph (Android-based OS, built-in navigation, Bluetooth music control, OTA updates, ride statistics). Accordion: Item 1 — "Turn-by-Turn Navigation" (built-in maps, no phone needed), Item 2 — "Ride Analytics" (trip history, efficiency score, ride patterns), Item 3 — "Smart Alerts" (theft alert, geofencing, tow detection), Item 4 — "OTA Updates" (new features delivered wirelessly), Item 5 — "Music & Calls" (Bluetooth audio, call handling). Badge ("4G + WiFi Connected").
11. **layout-row (Feature: Terrain Suitability)** → `comp_0_components_9`
    Heading ("Built for Indian Roads") + columnsgrid (3 columns): Column 1 — icon + heading ("City Commute") + paragraph ("Agile in traffic, tight turning radius") + rating (5 out of 5). Column 2 — icon + heading ("Highway Cruise") + paragraph ("Stable at top speed, wind-resistant") + rating (4 out of 5). Column 3 — icon + heading ("Rough Roads") + paragraph ("Telescopic suspension, 160 mm ground clearance") + rating (4 out of 5). Caption ("Tested across 50+ Indian city road conditions.").
12. **layout-row (Feature: Price & Subsidy)** → `comp_0_components_10`
    Heading ("Pricing & Subsidies") + columnsgrid (2 columns): Column 1 — heading ("Ex-Showroom Price") + heading (price) + caption ("Before state subsidy") + paragraph (FAME II subsidy applied). Column 2 — heading ("On-Road Price (Delhi)") + heading (price after subsidy) + caption ("Includes registration, insurance") + badge ("Save up to Rs 25,000 with state subsidy"). Tabs below: Tab 1 ("EMI Options" — 12/24/36/48 month EMI breakdowns), Tab 2 ("State Subsidies" — table of subsidies by state: Delhi, Gujarat, Maharashtra, etc.), Tab 3 ("Cost Comparison" — monthly cost EV vs petrol scooter: fuel, maintenance, insurance). Button ("Calculate Your On-Road Price").
13. **layout-row (Feature: Colors & Variants)** → `comp_0_components_11`
    Heading ("Express Your Style") + columnsgrid (4-6 columns): Each color option — image (scooter in that color) + caption (color name). Badge ("New Color") on latest additions. Caption ("All colors available at same price.").
14. **layout-row (Reviews & Test Ride)** → `comp_0_components_12`
    Left column: heading ("Owner Reviews") + rating (4.3 stars) + counter-up (15,670 reviews) + progress-bar (star distribution). Right column: heading ("Experience It Yourself") + paragraph ("Book a free test ride at your nearest experience center.") + button ("Book Test Ride") + caption ("Available in 100+ cities.").
15. **layout-row (Accessories)** → `comp_0_components_13`
    Heading ("Accessories & Add-Ons") + columnsgrid (4 columns): Each — image + heading (helmet, leg guard, seat cover, phone mount) + caption (price) + button ("Add to Cart").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Scooters, Charging Network, App, Ownership). Column 3 — links (Test Ride, Dealers, Support, Careers). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Marketing-focused launch page for a next-gen electric scooter with range confidence and lifestyle appeal

**Page: "VoltRide Max — The Scooter That Goes the Distance"**

1. **titlebar** — Brand logo, minimal nav (Features, Range, Price), CTA button ("Book Test Ride")
2. **layout-row (Hero — Lifestyle Impact)** → Video-background (scooter cruising through city streets, sunrise commute, charge at home, ride to office montage). Centered overlay: eyebrow ("Introducing"), heading ("VoltRide Max"), paragraph ("200 km range. Smart dashboard. Zero emissions. From Rs 99,999."), button ("Reserve Now — Rs 999"), countdown (delivery date timer), badge ("Limited Launch Offer").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Range Confidence)** → Heading ("200 km on a Single Charge") + paragraph ("That's your daily commute, 5 days a week, on one charge.") + counter-up (200) + caption ("km Certified Range"). Image (route map visualization showing 200 km coverage area from city center).
5. **layout-row (Cost Savings)** → Heading ("Save Rs 50,000 Every Year") + columnsgrid (2 columns): Column 1 — heading ("Petrol Scooter") + counter-up (60,000) + caption ("Annual Running Cost") + paragraph (fuel + maintenance). Column 2 — heading ("VoltRide Max") + counter-up (10,000) + caption ("Annual Running Cost") + paragraph (electricity + zero maintenance). Badge ("5x Cheaper to Run").
6. **layout-row (Performance Stats)** → columnsgrid (4 columns): counter-up (200) + caption ("km Range"), counter-up (95) + caption ("km/h Top Speed"), counter-up (2.5) + caption ("sec 0-40"), counter-up (0) + caption ("Emissions").
7. **layout-row (Smart Features)** → Carousel: Slide 1 — Dashboard demo. Slide 2 — App features. Slide 3 — Navigation. Slide 4 — Theft protection. Slide 5 — OTA updates.
8. **layout-row (Charging Ecosystem)** → Heading ("Charge Everywhere") + image (charging station map) + columnsgrid (2 columns): Home Charging (time, cost per charge) vs Fast Charging (time, network size). Counter-up (5,000) + caption ("Fast Chargers Nationwide").
9. **layout-row (Color Configurator)** → Heading ("Choose Your Color") + columnsgrid of color swatches + large scooter image that represents selection.
10. **layout-row (Pricing & EMI)** → columnsgrid (2 columns): Column 1 — heading (launch price) + badge ("Launch Offer — Save Rs 10,000") + button ("Reserve Now"). Column 2 — heading ("EMI from Rs 2,499/month") + paragraph (0% down payment options) + button ("Calculate EMI").
11. **layout-row (Early Adopter Testimonials)** → Carousel of beta tester/reviewer quotes + ratings. Counter-up (10,000) + caption ("Pre-Orders").
12. **layout-row (FAQ)** → Accordion: 8 questions on range, charging, warranty, subsidy, servicing, insurance, test rides.
13. **layout-row (Final CTA)** → Heading ("Your City. Your Way. Zero Emissions.") + button ("Book Test Ride") + button ("Reserve Now") + caption ("Fully refundable. Deliveries starting March 2026.").
14. **layout-row (Footer)** → Minimal footer with brand, legal, contact, social.

---

## Variant C — Product Catalog / Comparison Page

> Multi-model browsing with comparison tools, subsidy calculators, and test ride booking

**Page: "Electric Scooters & E-Bikes — Compare and Choose"**

1. **titlebar** — Brand logo (multi-brand or dealer), nav (Scooters, E-Bikes, Compare, Charging, Subsidies, Test Rides), search, cart
2. **layout-row (Category Hero)** → Full-width urban lifestyle image. Heading ("Electric Scooters & E-Bikes") + paragraph ("Compare range, performance, and price. Book a test ride.") + badge ("Subsidies up to Rs 25,000").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Quick Nav by Brand)** → Ticker or columnsgrid (horizontal): Ola, Ather, TVS, Hero Vida, Bajaj Chetak, Revolt, Simple Energy — each with brand logo + flagship model name + "from Rs X".
5. **layout-row (Head-to-Head Comparison)** → Heading ("Compare Top Electric Scooters") + columnsgrid (6 columns): Column 1 (spec labels: Range, Top Speed, Battery, Charging Time, Motor Power, Weight, Price), Columns 2-6 (Ola S1 Pro, Ather 450X, TVS iQube ST, Hero Vida V1, Bajaj Chetak). Badges on "Best Range", "Best Performance", "Best Value".
6. **layout-row (Bestsellers)** → Heading ("Most Popular") + columnsgrid (4 columns): Each — image, badge, heading (model name), rating, paragraph (range + speed + price), button ("View Details").
7. **layout-row (Budget Picks)** → Heading ("Under Rs 1 Lakh") + columnsgrid (3 columns): Budget EV cards with image, name, range, price after subsidy, button.
8. **layout-row (Premium Picks)** → Heading ("Premium — Rs 1.5 Lakh+") + columnsgrid (3 columns): Premium EV cards with image, name, highlight feature, price, button.
9. **layout-row (Subsidy Calculator)** → Heading ("Calculate Your On-Road Price") + form: dropdown (select state), dropdown (select model), heading (calculated on-road price), paragraph (breakdown: ex-showroom - FAME II - state subsidy + registration + insurance). Button ("Get Exact Quote").
10. **layout-row (Charging Infrastructure Map)** → Heading ("Charging Stations Near You") + image (India map with charger density) + paragraph ("Enter your city to find the nearest charging points.") + form (textbox for city + button "Find Chargers").
11. **layout-row (Buying Guide)** → Heading ("EV Scooter Buying Guide") + accordion: Item 1 ("What range do I need for my daily commute?"), Item 2 ("How much does it cost to charge at home?"), Item 3 ("Which state gives the best subsidy?"), Item 4 ("Battery warranty — what to look for?"), Item 5 ("Removable vs fixed battery — pros and cons"), Item 6 ("E-scooter vs petrol scooter — total cost comparison").
12. **layout-row (Customer Reviews)** → Heading ("Owner Reviews") + carousel of review cards with rating, model purchased, range feedback, blockquote.
13. **layout-row (Test Ride Booking)** → Heading ("Book a Free Test Ride") + columnsgrid (2 columns): Column 1 — form (dropdown model, dropdown city, textbox name, textbox phone, button "Book Now"). Column 2 — image (happy rider on test ride) + caption ("Test rides available in 150+ cities").
14. **layout-row (Footer)** → columnsgrid (4 columns): Store info, brands + models, support + policies, contact + social.
