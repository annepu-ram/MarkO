# Smart Home & Security — Product Pages

> Focus: Demonstrating always-on protection through camera resolution demos, ecosystem integration visuals, privacy-first messaging, and subscription transparency that builds long-term trust.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Ring (Amazon) | ring.com | Hero with doorbell video feed; "See, Hear, Speak" 3-feature hero layout; Ring Protect subscription plans comparison; neighborhood safety map; product ecosystem diagram (doorbell + cameras + alarm) |
| Google Nest | store.google.com/category/nest_cameras | Clean material design; camera vs doorbell vs hub comparison grid; Google Home ecosystem integration section; 24/7 recording vs event-based plan comparison; Familiar Face detection feature highlight |
| Eufy Security | eufy.com/security | "No Monthly Fees" hero headline as primary differentiator; local storage emphasis; HomeBase hub diagram; AI-powered person detection section; solar-powered option highlights |
| Arlo | arlo.com | Night vision quality comparison; 2K/4K resolution toggle demo; wire-free emphasis with battery life counter; Arlo Secure subscription tiers; multi-camera bundle configurator |
| Amazon Echo | amazon.com/echo | Voice assistant demo section with conversation bubbles; smart home hub diagram showing connected devices; skill library showcase; privacy controls section with toggle visuals; family/room comparison chart |

**Patterns to incorporate:**
- Live camera feed simulation or day/night comparison visuals
- Ecosystem compatibility diagram showing connected devices
- Subscription plan comparison (free vs paid tiers, cloud vs local storage)
- Privacy and encryption messaging prominently displayed
- Battery life vs wired power comparison
- Installation difficulty indicator (DIY vs professional)
- App interface mockup showing real-time alerts and controls
- Resolution comparison side-by-side (1080p vs 2K vs 4K)
- Integration badges (Alexa, Google Home, Apple HomeKit, IFTTT)
- Weather resistance and durability certifications

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Smart Security Camera / Video Doorbell Detail**

1. **titlebar** — Brand logo, nav links (Cameras, Doorbells, Sensors, Hubs, Plans, Support), cart icon, search
2. **layout-row (Hero — Product Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (product front, mounted on wall, app view, night vision sample, package contents). Right column: eyebrow ("Outdoor Security"), heading (product name), rating (4.4 stars, review count), paragraph (tagline: "2K HDR video. Color night vision. No monthly fees."), heading (price), badge ("No Subscription Required"), button ("Add to Cart"), button ("Buy Now"), caption ("Free shipping. 30-day returns.").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Connectivity Protocol)** → `comp_0_components_2`
   Left column: heading ("Stays Connected, Always") + paragraph (dual-band Wi-Fi 6, Bluetooth 5.0 for setup, optional hub connectivity for extended range). columnsgrid (3 columns): Column 1 — icon + caption ("Wi-Fi 6"). Column 2 — icon + caption ("Bluetooth 5.0"). Column 3 — icon + caption ("Zigbee/Thread Hub"). Right column: image (connectivity range diagram showing coverage from router through walls).
5. **layout-row (Feature: Ecosystem Compatibility)** → `comp_0_components_3`
   Heading ("Works With Your Smart Home") + ticker (scrolling integration logos: Amazon Alexa, Google Home, Apple HomeKit, Samsung SmartThings, IFTTT). Paragraph ("Control via voice, automate with routines, view on any smart display."). columnsgrid (3 columns): Column 1 — icon + heading ("Alexa") + paragraph ("View live feed on Echo Show, arm/disarm by voice"). Column 2 — icon + heading ("Google Home") + paragraph ("Stream to Nest Hub, create automations"). Column 3 — icon + heading ("Apple HomeKit") + paragraph ("Control from iPhone, Apple TV, HomePod").
6. **layout-row (Feature: Camera Resolution)** → `comp_0_components_4`
   Heading ("Crystal-Clear 2K HDR Video") + paragraph (2560x1920 resolution, HDR, 160-degree field of view, 8x digital zoom). Left column: image (day-time capture sample at full resolution). Right column: image (night-time capture with color night vision). columnsgrid (2 columns) below: Column 1 — caption ("Day Mode — Full Color HDR"). Column 2 — caption ("Night Mode — Color Night Vision"). Badge ("2K Super HD").
7. **layout-row (Feature: Battery vs Wired)** → `comp_0_components_5`
   Heading ("Power Your Way") + columnsgrid (2 columns): Column 1 — image (battery version) + heading ("Battery Powered") + paragraph (6-month battery life, magnetic mount, tool-free install) + progress-bar (battery life: 6 months visual) + caption ("Recharge via USB-C in 4 hours"). Column 2 — image (wired version) + heading ("Wired Power") + paragraph (24/7 continuous recording, no battery concerns, hardwired installation) + badge ("Always On"). Caption ("Both options available — choose at checkout").
8. **layout-row (Feature: Storage — Cloud/Local)** → `comp_0_components_6`
   Heading ("Your Footage, Your Choice") + tabs: Tab 1 ("Local Storage" — icon + heading + paragraph: "16GB onboard eMMC + microSD up to 256GB. No subscription required. Full privacy."), Tab 2 ("Cloud Storage" — icon + heading + paragraph: "30-day rolling cloud backup. Access from anywhere. Auto-encrypted AES-256."), Tab 3 ("Hybrid" — icon + heading + paragraph: "Local recording + cloud backup for redundancy. Best of both worlds."). Badge ("No Monthly Fees for Local").
9. **layout-row (Feature: App Features)** → `comp_0_components_7`
   Left column: image (phone mockup showing app interface with live feed, alerts, zones). Right column: heading ("Smart App Control") + paragraph (live view, two-way audio, motion zones, activity alerts, sharing with family). Accordion: Item 1 — "Activity Zones" (draw custom detection areas), Item 2 — "Smart Alerts" (person, vehicle, animal, package detection), Item 3 — "Two-Way Audio" (talk through camera speaker), Item 4 — "Family Sharing" (share access without passwords), Item 5 — "Timeline View" (scrub through recorded events).
10. **layout-row (Feature: Privacy & Encryption)** → `comp_0_components_8`
   Heading ("Privacy-First Design") + columnsgrid (3 columns): Column 1 — icon + heading ("End-to-End Encryption") + paragraph ("AES-256 encryption for all video data"). Column 2 — icon + heading ("Physical Privacy Shutter") + paragraph ("Hardware switch to disable camera and mic"). Column 3 — icon + heading ("On-Device AI") + paragraph ("Face recognition and detection processed locally, never in cloud"). Badge ("GDPR Compliant"). Paragraph ("Your data is never sold, shared, or used for advertising.").
11. **layout-row (Feature: Installation)** → `comp_0_components_9`
    Heading ("Set Up in 10 Minutes") + columnsgrid (3 columns): Column 1 — icon + counter-up (10) + caption ("Minute Setup"). Column 2 — icon + heading ("No Drilling Required") + caption ("Magnetic mount included"). Column 3 — icon + heading ("In-App Guide") + caption ("Step-by-step walkthrough"). Paragraph ("Professional installation available for Rs 999 if preferred."). Image (person mounting camera on wall easily).
12. **layout-row (Feature: Price & Subscription Plans)** → `comp_0_components_10`
    Heading ("Choose Your Plan") + columnsgrid (3 columns): Column 1 — heading ("Camera Only") + heading (one-time price) + paragraph (local storage, basic alerts, no monthly cost) + badge ("No Subscription") + button ("Buy Camera Only"). Column 2 — heading ("Camera + Basic Plan") + heading (camera price + Rs 199/month) + paragraph (30-day cloud, smart alerts, person detection) + badge ("Most Popular") + button ("Buy with Basic"). Column 3 — heading ("Camera + Premium Plan") + heading (camera price + Rs 499/month) + paragraph (24/7 recording, AI detection, family sharing, priority support) + button ("Buy with Premium").
13. **layout-row (Feature: Integration & Automation)** → `comp_0_components_11`
    Heading ("Automate Your Security") + paragraph ("Create routines that trigger lights, locks, and alarms automatically."). columnsgrid (2 columns): Column 1 — heading ("Example Routines") + accordion: Item 1 ("Motion detected → Turn on porch light"), Item 2 ("Person at door → Unlock smart lock"), Item 3 ("Night mode → Arm all cameras"), Item 4 ("Away from home → Enable all alerts"). Column 2 — image (smart home ecosystem diagram with camera, lights, lock, alarm connected).
14. **layout-row (Reviews & Ratings)** → `comp_0_components_12`
    Left column: heading ("Customer Reviews") + rating (4.4 stars) + counter-up (8,320 reviews) + progress-bar (star distribution). Right column: carousel of blockquote reviews with rating and "Verified Purchase" badge.
15. **layout-row (Complete Your Setup)** → `comp_0_components_13`
    Heading ("Build Your Security System") + columnsgrid (4 columns): Each — image + heading (doorbell, indoor camera, sensor, hub) + caption (price) + button ("Add to Cart").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Products, Plans, App, Support). Column 3 — links (Privacy Policy, Warranty, Returns, Shipping). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Marketing-focused layout for a new smart home ecosystem launch emphasizing seamless protection and privacy

**Page: "SecureNest 360 — Whole-Home Intelligence"**

1. **titlebar** — Brand logo, minimal nav (Features, Products, Plans), CTA button ("Shop the System")
2. **layout-row (Hero — Cinematic Protection)** → Video-background (family arriving home, camera detecting, lights turning on, lock opening). Centered overlay: eyebrow ("Introducing"), heading ("SecureNest 360"), paragraph ("See everything. Control everything. Trust everything."), button ("Shop Now"), badge ("No Monthly Fees").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Problem Statement)** → Heading ("Your Home Deserves Better Than a Dumb Lock") + paragraph (break-in stats, blind spots in current systems, subscription fatigue). Counter-up stats: 2.5 million break-ins/year, 60% happen while home, Rs 3,600/year average subscription cost.
5. **layout-row (Ecosystem Reveal)** → Full-width image (product family: camera, doorbell, sensor, hub, keypad). Heading ("One System. Complete Protection.") + paragraph (all devices work together out of the box).
6. **layout-row (Feature Highlights)** → Carousel: Slide 1 — 2K Resolution (day/night comparison). Slide 2 — On-Device AI (privacy emphasis). Slide 3 — 10-Minute DIY Install. Slide 4 — No Monthly Fees. Slide 5 — Works with Alexa/Google/HomeKit.
7. **layout-row (Privacy Promise)** → Dark background. Heading ("Your Privacy. Non-Negotiable.") + columnsgrid (3 columns): encryption, physical shutter, on-device processing. Blockquote from privacy expert.
8. **layout-row (Day in the Life)** → Heading ("A Day With SecureNest") + accordion timeline: "7 AM — Motion detected, sends alert", "9 AM — Delivery person identified, unlocks package box", "3 PM — Kids arrive home, notification sent", "11 PM — Night mode activates all cameras".
9. **layout-row (Bundle Pricing)** → Heading ("Protect Every Corner") + columnsgrid (3 columns): Starter Kit (1 camera, Rs X), Home Kit (camera + doorbell + sensor, Rs X, badge "Most Popular"), Whole Home (4 cameras + doorbell + hub + sensors, Rs X, badge "Best Value"). Buttons on each.
10. **layout-row (Testimonials)** → Carousel of video testimonial thumbnails + blockquote excerpts. Counter-up (50,000) + caption ("Homes Protected").
11. **layout-row (Comparison vs Subscriptions)** → Heading ("Stop Paying Monthly Fees") + columnsgrid comparing SecureNest (one-time cost) vs Ring/Nest (annual subscription costs over 3 years). Counter-up showing 3-year savings.
12. **layout-row (Final CTA)** → Heading ("Protect What Matters Most") + button ("Shop SecureNest 360") + caption ("Free shipping. 30-day returns. 2-year warranty.").
13. **layout-row (Footer)** → Minimal footer with brand, privacy policy, contact, social links.

---

## Variant C — Product Catalog / Comparison Page

> Multi-product browsing for building a complete smart home security system

**Page: "Smart Home Security — Cameras, Doorbells, Sensors & More"**

1. **titlebar** — Brand logo (retailer), nav (Cameras, Doorbells, Sensors, Hubs, Locks, Bundles, Plans), search, cart
2. **layout-row (Category Hero)** → Full-width smart home lifestyle image. Heading ("Smart Home Security") + paragraph ("Build your perfect security system. Mix and match devices.") + badge ("Free shipping on bundles").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Shop by Category)** → columnsgrid or ticker (horizontal): Indoor Cameras, Outdoor Cameras, Video Doorbells, Motion Sensors, Smart Locks, Hub/Base Stations, Bundles — each with icon + label + "from Rs X,XXX".
5. **layout-row (Brand Comparison)** → Heading ("Compare Top Brands") + columnsgrid (5 columns): Column 1 (feature labels: Resolution, Night Vision, Storage, Monthly Fee, Ecosystem, Battery Life, Price), Columns 2-5 (Ring, Nest, Eufy, Arlo). Badges on "Best for" each category.
6. **layout-row (Bestsellers)** → Heading ("Bestsellers") + columnsgrid (4 columns): Each — image, badge ("Bestseller" / "No Subscription"), heading (product name), rating, paragraph (key spec: resolution, storage type, power), heading (price), button ("View Details").
7. **layout-row (Bundle Builder)** → Heading ("Build Your System") + columnsgrid (4 columns): Step 1 — dropdown (choose camera type), Step 2 — dropdown (add doorbell), Step 3 — dropdown (add sensors), Step 4 — heading (total bundle price) + badge ("Bundle Savings") + button ("Add Bundle to Cart").
8. **layout-row (Subscription-Free Options)** → Heading ("No Monthly Fees — Local Storage Devices") + columnsgrid (3 columns): Eufy, Reolink, TP-Link products — each with image, name, "No Subscription" badge, local storage spec, price, button.
9. **layout-row (Subscription Plans Compared)** → Heading ("Cloud Storage Plans") + columnsgrid (4 columns): Ring Protect, Nest Aware, Arlo Secure, Eufy Cloud — each with monthly price, storage duration, features included, button ("Learn More").
10. **layout-row (Buying Guide)** → Heading ("Smart Home Security Buying Guide") + accordion: Item 1 ("Indoor vs Outdoor — which cameras do I need?"), Item 2 ("Battery vs Wired — pros and cons"), Item 3 ("Do I need a subscription?"), Item 4 ("Which ecosystem is best for me?"), Item 5 ("How many cameras for a 3BHK home?"), Item 6 ("Can I install it myself?").
11. **layout-row (Customer Reviews)** → Heading ("Customer Reviews") + carousel of review cards with rating, blockquote, product purchased.
12. **layout-row (Smart Home Integration Guide)** → Heading ("Works With") + columnsgrid (4 columns): Alexa Compatible (product list), Google Home Compatible (list), Apple HomeKit Compatible (list), SmartThings Compatible (list).
13. **layout-row (Newsletter)** → Left column: heading ("Smart Home Tips & Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help Building Your System?") + paragraph + button ("Chat With an Expert").
14. **layout-row (Footer)** → columnsgrid (4 columns): Store info, product categories, support, contact + social.
