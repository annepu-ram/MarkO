# Power Tools & Hardware — Product Pages

> Focus: Communicating professional-grade performance through motor specs, runtime benchmarks, ergonomic design details, and Pro vs DIY positioning that serves both tradespeople and weekend warriors.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Bosch Professional | bosch-professional.com | Blue (Pro) vs Green (DIY) product line separation; battery platform compatibility chart; brushless motor technology explainer; ProCORE battery ecosystem section; tool comparison across voltage classes (12V, 18V, 36V) |
| DeWalt | dewalt.com | Yellow/black industrial hero imagery; FLEXVOLT battery system hero; jobsite environment photography; trade-specific tool bundles (electrician, plumber, carpenter); ToughSystem storage integration section |
| Makita | makita.com | 18V LXT platform ecosystem (275+ products); teal brand consistency; Star Protection Computer Controls tech section; rapid-charging system comparison; dust management solutions section; combo kit bundles |
| Stanley | stanley.com | Heritage/legacy positioning ("Since 1843"); hand tools + power tools unified catalog; Pro vs DIY toggle filter; warranty comparison (lifetime on hand, 3-year on power); project inspiration gallery |
| Milwaukee | milwaukeetool.com | Red/black brand identity; ONE-KEY digital platform (tool tracking, customization); POWERSTATE brushless motor branding; REDLINK PLUS intelligence section; trade-focused navigation (HVAC, Plumbing, Electrical, Carpentry) |

**Patterns to incorporate:**
- Battery platform ecosystem visualization (how many tools share one battery)
- Motor power and RPM stats with torque ratings prominently displayed
- Brushless vs brushed motor comparison section
- Runtime benchmark with battery size options (2.0Ah, 4.0Ah, 6.0Ah, 8.0Ah)
- Ergonomic design callouts (weight, grip, vibration reduction, LED light)
- Pro vs DIY product line differentiation
- Accessory/bit compatibility chart
- Safety feature section (electronic brake, overload protection, kickback control)
- Combo kit / bundle configurator
- Warranty comparison (tool, battery, charger separate warranties)

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Cordless Drill / Impact Driver Detail**

1. **titlebar** — Brand logo, nav links (Power Tools, Hand Tools, Batteries, Accessories, Pro, DIY, Support), cart icon, search
2. **layout-row (Hero — Tool Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (tool front angle, side profile, in-use action shot, chuck close-up, LED light detail, kit contents with case). Right column: eyebrow ("Professional 18V"), heading (tool name + model number), rating (4.6 stars, review count), paragraph (tagline: "Brushless motor. 90 Nm torque. All-metal chuck. Under 1.5 kg."), heading (price), badge ("Kit includes 2x 4.0Ah batteries + charger"), button ("Add to Cart"), button ("Buy Now"), caption ("Free delivery. 30-day returns.").
3. **layout-row (Feature: Motor Power & RPM)** → `comp_0_components_2`
   Left column: heading ("Brushless Powerhouse") + paragraph (brushless motor delivers 30% more runtime, 50% longer life, 10% more compact than brushed. Electronic motor management for consistent power under load). Counter-up (90) + caption ("Nm Max Torque"). Counter-up (2100) + caption ("RPM No-Load Speed"). Right column: image (motor cutaway or in-action drilling into concrete). Badge ("Brushless Motor").
4. **layout-row (Feature: Battery Type & Runtime)** → `comp_0_components_3`
   Heading ("Power That Lasts All Day") + columnsgrid (3 columns): Column 1 — image (2.0Ah compact battery) + heading ("2.0Ah Compact") + paragraph ("Light jobs, overhead work") + progress-bar (runtime: 45 min label) + caption ("250 screws per charge"). Column 2 — image (4.0Ah standard) + heading ("4.0Ah Standard") + badge ("Included") + paragraph ("All-day professional use") + progress-bar (runtime: 90 min label) + caption ("500 screws per charge"). Column 3 — image (8.0Ah high-cap) + heading ("8.0Ah High Capacity") + paragraph ("Heavy-duty, continuous drilling") + progress-bar (runtime: 180 min label) + caption ("1000+ screws per charge"). Paragraph ("All batteries compatible with 75+ tools in the 18V platform."). Badge ("Universal Battery Platform").
5. **layout-row (Feature: Build Material)** → `comp_0_components_4`
   columnsgrid (3 columns): Column 1 — icon + heading ("All-Metal Gear Housing") + paragraph ("Die-cast aluminum for heat dissipation and impact resistance"). Column 2 — icon + heading ("13mm All-Metal Chuck") + paragraph ("Precision keyless chuck, auto-lock, no bit slip"). Column 3 — icon + heading ("Rubber Over-Mold Grip") + paragraph ("Anti-vibration, sweat-resistant, comfortable all-day use"). Image below (exploded view showing internal components). Badge ("Professional Grade Build").
6. **layout-row (Feature: Weight & Ergonomics)** → `comp_0_components_5`
   Left column: heading ("Light Enough for Overhead. Tough Enough for Concrete.") + paragraph (1.5 kg bare tool, compact head length 178 mm, LED worklight, belt clip) + counter-up (1.5) + caption ("kg — Tool Only"). Right column: image (person using tool overhead, showing compact design). columnsgrid (2 columns): Column 1 — caption ("Head Length: 178 mm"). Column 2 — caption ("Balanced center of gravity").
7. **layout-row (Feature: Chuck/Blade Type & Compatibility)** → `comp_0_components_6`
   Heading ("Versatile Compatibility") + accordion: Item 1 — "Chuck Size & Type" (13mm keyless, auto-lock, accepts round and hex shank bits), Item 2 — "Speed Settings" (2-speed gearbox: Speed 1 for high-torque driving, Speed 2 for high-speed drilling), Item 3 — "Torque Settings" (21+1 torque clutch settings for precise screw depth control), Item 4 — "Mode Selector" (drill, drive, hammer modes on combo drills). Image (bit assortment showing compatible types).
8. **layout-row (Feature: Accessories Included)** → `comp_0_components_7`
   Heading ("Everything You Need in the Box") + columnsgrid (2 columns): Column 1 — heading ("Kit Contents") + paragraph (list: tool, 2x 4.0Ah batteries, rapid charger, belt clip, auxiliary handle, carrying case). Column 2 — image (open carrying case with all contents visible). Heading below ("Expand Your Kit") + columnsgrid (4 columns): Each — image + heading (drill bit set, driver bit set, hole saw set, magnetic holder) + caption (price) + button ("Add").
9. **layout-row (Feature: Safety Features)** → `comp_0_components_8`
   Heading ("Built-In Protection") + columnsgrid (3 columns): Column 1 — icon + heading ("Electronic Brake") + paragraph ("Instant stop when trigger released. Zero rundown."). Column 2 — icon + heading ("Overload Protection") + paragraph ("Motor shuts down before overheating. Extends tool life."). Column 3 — icon + heading ("Kickback Control") + paragraph ("Electronic clutch detects sudden rotation and stops motor immediately."). Badge ("Triple Safety System"). Caption ("Star Protection Computer Controls monitor temperature, current, and voltage in real-time.").
10. **layout-row (Feature: Warranty)** → `comp_0_components_9`
    Heading ("Industry-Leading Warranty") + columnsgrid (3 columns): Column 1 — counter-up (3) + heading ("Year") + caption ("Tool Warranty") + paragraph ("Covers manufacturing defects"). Column 2 — counter-up (2) + heading ("Year") + caption ("Battery Warranty") + paragraph ("Covers cell degradation"). Column 3 — counter-up (1) + heading ("Year") + caption ("Charger Warranty"). Paragraph ("Register your tool online for extended warranty options."). Accordion: Item 1 — "What's covered?" (details), Item 2 — "How to claim?" (process), Item 3 — "Service center locations?" (finder).
11. **layout-row (Feature: Price & Kit Options)** → `comp_0_components_10`
    Heading ("Choose Your Kit") + columnsgrid (3 columns): Column 1 — image + heading ("Bare Tool") + paragraph ("Tool only — use your existing batteries") + heading (price) + button ("Buy Bare Tool"). Column 2 — image + heading ("Standard Kit") + badge ("Most Popular") + paragraph ("Tool + 2x 4.0Ah + charger + case") + heading (price) + button ("Buy Standard Kit"). Column 3 — image + heading ("Pro Kit") + paragraph ("Tool + 2x 6.0Ah + rapid charger + bit set + case") + heading (price) + badge ("Best Value") + button ("Buy Pro Kit").
12. **layout-row (Feature: Pro vs DIY)** → `comp_0_components_11`
    Heading ("Professional or Home Use?") + columnsgrid (2 columns): Column 1 — heading ("Professional Series") + badge ("Pro") + paragraph ("Higher torque, metal internals, longer warranty, dust/water protection, all-day runtime. For daily trade use.") + rating (5 out of 5 for durability). Column 2 — heading ("Home / DIY Series") + badge ("DIY") + paragraph ("Lighter weight, lower price, adequate power for weekend projects, furniture assembly, home repairs.") + rating (4 out of 5 for value). Caption ("Both lines share the same battery platform.").
13. **layout-row (Reviews)** → `comp_0_components_12`
    Left column: heading ("Pro & DIY Reviews") + rating (4.6 stars) + counter-up (6,120 reviews) + progress-bar (star distribution). Right column: carousel of blockquote reviews with trade/project context (e.g., "Used it on a 3-month renovation — still going strong").
14. **layout-row (Battery Platform)** → `comp_0_components_13`
    Heading ("One Battery. 75+ Tools.") + paragraph ("Invest in batteries once. Use across drills, saws, grinders, lights, vacuums, and more."). Ticker (scrolling tool silhouettes: drill, impact driver, circular saw, reciprocating saw, angle grinder, jigsaw, sander, flashlight). Button ("Explore the 18V Platform").
15. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Power Tools, Hand Tools, Batteries, Accessories). Column 3 — links (Support, Warranty, Service Centers, Where to Buy). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Marketing-focused launch page for a new battery platform or flagship tool with jobsite storytelling

**Page: "ProForce 20V MAX — Built Without Compromise"**

1. **titlebar** — Brand logo, minimal nav (Tools, Battery Platform, Find a Dealer), CTA button ("Shop Now")
2. **layout-row (Hero — Jobsite Impact)** → Video-background (construction site montage — framing, drilling, cutting, driving). Centered overlay: eyebrow ("Introducing"), heading ("ProForce 20V MAX"), paragraph ("Brushless power. 120 Nm torque. The last drill you'll ever need."), button ("Shop Now — Rs 12,999"), badge ("Free 6.0Ah Battery Worth Rs 3,999").
3. **layout-row (Problem Statement)** → Heading ("Your Tools Should Work as Hard as You Do") + paragraph (underpowered tools slow down projects, cheap tools break mid-job, multiple battery platforms waste money). Counter-up stats: 120 Nm torque, 2x longer motor life, 75+ compatible tools.
4. **layout-row (Motor Technology Reveal)** → Left: image (brushless motor exploded view). Right: heading ("POWERCORE Brushless Motor") + paragraph (30% more efficient, 50% longer life, zero maintenance) + progress-bar (efficiency comparison: brushless vs brushed).
5. **layout-row (Battery Ecosystem)** → Heading ("One Battery Powers Everything") + image (battery surrounded by 75+ tool silhouettes in circle). Counter-up (75) + caption ("Tools on One Platform"). Paragraph ("Buy the battery once. Build your collection over a career.").
6. **layout-row (Feature Highlights)** → Carousel: Slide 1 — Torque (120 Nm demo). Slide 2 — Runtime (1000 screws). Slide 3 — Durability (drop test). Slide 4 — LED Worklight. Slide 5 — Electronic Brake.
7. **layout-row (Trade Bundles)** → Heading ("Bundles for Every Trade") + columnsgrid (3 columns): Electrician Kit (drill + driver + flashlight), Carpenter Kit (drill + circular saw + sander), Plumber Kit (drill + reciprocating saw + pipe cutter). Each with price, contents list, savings badge, button.
8. **layout-row (Pro Testimonials)** → Carousel of tradesperson blockquotes with name, trade, and years of experience. Images of tools in real jobsite conditions.
9. **layout-row (Pricing)** → columnsgrid (3 columns): Bare Tool, Standard Kit, Pro Kit — image, contents, price, badge, button.
10. **layout-row (Warranty & Trust)** → counter-up (3) + "Year Warranty" + counter-up (500) + "Service Centers" + counter-up (25) + "Years in Market". Paragraph ("Backed by a brand that professionals trust.").
11. **layout-row (Final CTA)** → Heading ("Built for Professionals. Available for Everyone.") + button ("Shop ProForce 20V MAX") + caption ("Free shipping. 3-year warranty. 30-day returns.").
12. **layout-row (Footer)** → Minimal footer with brand, dealer finder, contact, social.

---

## Variant C — Product Catalog / Comparison Page

> Multi-tool browsing experience for building a tool collection with cross-brand comparison

**Page: "Power Tools — Drills, Saws, Grinders & More"**

1. **titlebar** — Brand logo (retailer), nav (Drills, Saws, Grinders, Sanders, Impact Drivers, Combo Kits, Batteries, Accessories), search, cart
2. **layout-row (Category Hero)** → Full-width workshop/jobsite image. Heading ("Power Tools for Every Job") + paragraph ("Professional-grade and DIY tools from top brands") + eyebrow ("Free delivery on orders over Rs 4,999").
3. **layout-row (Shop by Category)** → columnsgrid or ticker (horizontal): Drills, Impact Drivers, Circular Saws, Jigsaws, Angle Grinders, Sanders, Reciprocating Saws, Multi-Tools, Combo Kits — each with icon + label + "from Rs X".
4. **layout-row (Brand Quick Nav)** → Ticker (brand logos horizontal): Bosch, DeWalt, Makita, Milwaukee, Stanley, Hilti, Metabo — each clickable.
5. **layout-row (Brand Comparison Table)** → Heading ("Compare Top Drill Brands") + columnsgrid (5 columns): Column 1 (spec labels: Torque, RPM, Weight, Battery Platform, Tools on Platform, Warranty, Price Range), Columns 2-5 (Bosch, DeWalt, Makita, Milwaukee). Badges on "Best Torque", "Lightest", "Most Tools".
6. **layout-row (Bestsellers)** → Heading ("Bestsellers") + columnsgrid (4 columns): Each — image, badge, heading (tool name), rating, paragraph (power + battery + key feature), heading (price), button ("View Details").
7. **layout-row (Combo Kits)** → Heading ("Combo Kits — Save Up to 30%") + columnsgrid (3 columns): Each kit — image (open case showing tools), heading (kit name), paragraph (contents: "Drill + Impact Driver + 2 Batteries + Charger + Case"), heading (original vs kit price), badge ("Save Rs X"), button ("Buy Kit").
8. **layout-row (Pro vs DIY)** → Heading ("Shop by User Type") + columnsgrid (2 columns): Column 1 — heading ("Professional") + paragraph ("Heavy-duty, all-metal, extended warranty") + image (pro tools) + button ("Shop Pro Tools"). Column 2 — heading ("DIY / Home") + paragraph ("Lightweight, affordable, weekend-ready") + image (DIY tools) + button ("Shop DIY Tools").
9. **layout-row (Battery Platform Guide)** → Heading ("Choose a Battery Platform") + accordion: Item 1 ("Bosch 18V — 200+ tools"), Item 2 ("DeWalt 20V MAX — 300+ tools"), Item 3 ("Makita 18V LXT — 275+ tools"), Item 4 ("Milwaukee M18 — 250+ tools"). Each with tool count, battery options, key advantage.
10. **layout-row (Buying Guide)** → Heading ("Power Tool Buying Guide") + accordion: Item 1 ("Brushless vs brushed — which motor type?"), Item 2 ("How much torque do I need?"), Item 3 ("Corded vs cordless — which is better?"), Item 4 ("What battery voltage do I need?"), Item 5 ("How to choose the right drill for my project?"), Item 6 ("Tool warranty — what to look for?").
11. **layout-row (Customer Reviews)** → Heading ("Tradesperson & DIY Reviews") + carousel of review cards with tool used, project type, rating, blockquote.
12. **layout-row (Newsletter)** → Left column: heading ("Tool Deals & Project Tips") + form (textbox + button "Subscribe"). Right column: heading ("Need Expert Advice?") + paragraph + button ("Talk to a Tool Specialist").
13. **layout-row (Footer)** → columnsgrid (4 columns): Store info, tool categories, brands, support + contact.
