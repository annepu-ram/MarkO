# Smart Wearables — Product Pages

> Focus: Translating health sensor data into lifestyle benefits through real-time health metric demos, battery life comparisons, band customization visuals, and ecosystem integration that positions wearables as daily health companions.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Apple Watch | apple.com/apple-watch-ultra-2 | Scroll-triggered 3D product rotation; health feature sections with animated watch faces; ECG and blood oxygen demo; band studio configurator; comparison chart across Watch SE, Series, Ultra; Apple Fitness+ integration section |
| Samsung Galaxy Watch | samsung.com/galaxy-watch | Rotating bezel interaction demo; health monitoring dashboard mockup; sleep coaching feature section; Samsung Health ecosystem diagram; Galaxy ecosystem compatibility (phone + buds + watch); Wear OS app showcase |
| Fitbit (by Google) | fitbit.com | Health-first positioning ("Know your body better"); Daily Readiness Score demo; stress management section; sleep profile analysis; Fitbit Premium subscription tier comparison; active zone minutes gamification |
| Noise (India) | gonoise.com | Budget-friendly hero pricing ("starts at Rs 1,499"); Noise Health Suite feature grid; crown/button interaction demo; large display comparison; call/notification features; sport mode count badge ("100+ sports modes") |
| boAt (India) | boat-lifestyle.com | Lifestyle/fashion-first hero imagery; color variant grid; AMOLED display brightness demo; SpO2/HR monitoring badges; boat Crest app features; influencer/celebrity endorsement section; festival sale countdown |

**Patterns to incorporate:**
- Health sensor demo with animated readings (heart rate, SpO2, ECG waveform)
- Watch face gallery showing customization options
- Battery life counter-up with usage scenario breakdown (typical vs heavy)
- Band/strap configurator with color and material options
- Comparison chart across models (SE vs Standard vs Pro/Ultra)
- App ecosystem mockup showing health dashboard, notifications, controls
- Water resistance certification with depth rating visual
- Activity tracking mode showcase (running, swimming, cycling, yoga, etc.)
- Subscription tier for premium health features
- Size guide with wrist measurement recommendations

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Smartwatch Detail (e.g., Apple Watch Ultra / Galaxy Watch / Noise ColorFit)**

1. **titlebar** — Brand logo, nav links (Watches, Bands, Health, Compare, App, Support), cart icon, search
2. **layout-row (Hero — Watch Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (watch front face with health metrics, side profile showing crown, on-wrist lifestyle shot, band options, packaging). Right column: eyebrow ("Smart Health"), heading (watch name), rating (4.5 stars, review count), paragraph (tagline: "Advanced health sensors. 7-day battery. Always-on AMOLED."), heading (price), badge ("New Launch"), size selector (radio: 41mm, 45mm — each with price), button ("Buy Now"), button ("Add to Cart"), caption ("Free band included. 15-day returns.").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Health Sensors — HR, SpO2, ECG)** → `comp_0_components_2`
   Heading ("Your Health, On Your Wrist") + columnsgrid (3 columns): Column 1 — icon + heading ("Heart Rate") + paragraph ("24/7 continuous HR monitoring with optical sensors. Irregular rhythm notifications.") + image (animated HR waveform on watch face). Column 2 — icon + heading ("Blood Oxygen (SpO2)") + paragraph ("On-demand and background SpO2 measurement. Sleep-time tracking.") + image (SpO2 reading on watch). Column 3 — icon + heading ("ECG") + paragraph ("Single-lead ECG app. Detect atrial fibrillation. Share PDF with doctor.") + image (ECG trace on watch). Badge ("Clinically Validated").
5. **layout-row (Feature: Activity Tracking)** → `comp_0_components_3`
   Heading ("Track Every Move") + paragraph ("100+ workout modes with auto-detection for the 8 most common activities."). Counter-up (100) + caption ("Workout Modes"). columnsgrid (4 columns): Column 1 — icon + heading ("Running") + caption ("GPS pace, cadence, elevation"). Column 2 — icon + heading ("Swimming") + caption ("Lap count, stroke type, SWOLF"). Column 3 — icon + heading ("Cycling") + caption ("Speed, distance, heart rate zones"). Column 4 — icon + heading ("Yoga") + caption ("Stress level, breathing exercises"). Ticker below (scrolling additional modes: hiking, rowing, weight training, dancing, martial arts, cricket, badminton).
6. **layout-row (Feature: Battery Life)** → `comp_0_components_4`
   Heading ("7-Day Battery. Charge Once a Week.") + columnsgrid (2 columns): Column 1 — counter-up (7) + heading ("Days") + caption ("Typical Usage") + paragraph ("Includes 24/7 HR, notifications, 30-min daily workout, always-on display off") + progress-bar (7 days out of 14-day scale). Column 2 — counter-up (14) + heading ("Days") + caption ("Battery Saver Mode") + paragraph ("Essential features only: time, steps, HR, notifications") + progress-bar (14 days out of 14-day scale). Caption ("Full charge in 90 minutes via magnetic charger."). Badge ("Industry-Leading Battery").
7. **layout-row (Feature: Display)** → `comp_0_components_5`
   Left column: image (watch face close-up showing vibrant AMOLED colors, outdoor visibility). Right column: heading ("1.43-inch AMOLED Always-On Display") + paragraph (466x466 resolution, 1000 nits peak brightness, Corning Gorilla Glass 3, anti-fingerprint coating). Counter-up (1000) + caption ("Nits Peak Brightness"). columnsgrid (2 columns): Column 1 — caption ("Always-On Display: read time without wrist raise"). Column 2 — caption ("Auto-Brightness: adapts to indoor/outdoor light").
8. **layout-row (Feature: Water Resistance)** → `comp_0_components_6`
   Heading ("Swim-Proof. Rain-Proof. Sweat-Proof.") + columnsgrid (2 columns): Column 1 — counter-up (5) + heading ("ATM") + caption ("Water Resistance") + paragraph ("Suitable for swimming, showering, and water sports up to 50m depth."). Column 2 — image (watch submerged in water / swimmer wearing watch). Badge ("IP68 + 5ATM Certified"). Caption ("Not recommended for scuba diving or high-velocity water activities.").
9. **layout-row (Feature: App & Ecosystem)** → `comp_0_components_7`
   Left column: image (phone mockup showing companion app — health dashboard, sleep analysis, workout history). Right column: heading ("Companion App — Your Health Dashboard") + paragraph (sync all health data, trend analysis, share with doctor, set goals). Accordion: Item 1 — "Health Dashboard" (HR, SpO2, sleep, steps in one view), Item 2 — "Sleep Analysis" (sleep stages, quality score, recommendations), Item 3 — "Workout History" (detailed logs with maps and zones), Item 4 — "Smart Notifications" (calls, messages, app alerts), Item 5 — "Watch Face Store" (500+ downloadable faces). columnsgrid (3 columns) below: icon + caption ("iOS"), icon + caption ("Android"), icon + caption ("HarmonyOS").
10. **layout-row (Feature: Band Options)** → `comp_0_components_8`
   Heading ("Express Your Style") + columnsgrid (4 columns): Each — image (band type on watch) + heading (band name: "Silicone Sport", "Leather Classic", "Metal Link", "Nylon Adventure") + caption (color options count) + caption (price). Paragraph ("Quick-release mechanism — swap bands in seconds without tools."). Badge ("20+ Band Options").
11. **layout-row (Feature: Notifications & Smart Features)** → `comp_0_components_9`
    Heading ("Stay Connected Without Your Phone") + columnsgrid (3 columns): Column 1 — icon + heading ("Calls") + paragraph ("Bluetooth calls via built-in speaker and mic."). Column 2 — icon + heading ("Messages") + paragraph ("Read and reply to messages, WhatsApp, emails."). Column 3 — icon + heading ("Voice Assistant") + paragraph ("Google Assistant / Siri / Alexa built-in."). Paragraph ("Music control, camera shutter, find my phone, SOS emergency.").
12. **layout-row (Feature: Price & Comparison)** → `comp_0_components_10`
    Heading ("Choose Your Model") + columnsgrid (3 columns): Column 1 — image + heading ("SE / Lite") + paragraph (basic health, 3-day battery, BT calling) + heading (price) + button ("Buy SE"). Column 2 — image + heading ("Standard") + badge ("Most Popular") + paragraph (full health suite, 7-day battery, GPS, AMOLED) + heading (price) + button ("Buy Standard"). Column 3 — image + heading ("Pro / Ultra") + paragraph (ECG, temperature, titanium, 14-day battery, diving-rated) + heading (price) + button ("Buy Pro"). Caption ("All models include 1-year warranty and free band.").
13. **layout-row (Feature: Comparison Table)** → `comp_0_components_11`
    Heading ("Feature Comparison") + tabs: Tab 1 ("Health Sensors" — checkmark grid across 3 models), Tab 2 ("Display & Battery" — specs per model), Tab 3 ("Smart Features" — feature availability per model), Tab 4 ("Build & Design" — materials, weight, water resistance).
14. **layout-row (Reviews & Ratings)** → `comp_0_components_12`
    Left column: heading ("Customer Reviews") + rating (4.5 stars) + counter-up (24,320 reviews) + progress-bar (star distribution). Right column: carousel of blockquote reviews with rating, reviewer name + "Verified Purchase" badge.
15. **layout-row (Accessories)** → `comp_0_components_13`
    Heading ("Accessories") + columnsgrid (4 columns): Each — image + heading (extra charger, screen protector, band, carry case) + caption (price) + button ("Add to Cart").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Watches, Bands, Health Features, App). Column 3 — links (Support, Warranty, Size Guide, Where to Buy). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Health-focused marketing launch for a next-gen smartwatch with clinical-grade sensors and lifestyle appeal

**Page: "PulseX Pro — Your Personal Health Lab"**

1. **titlebar** — Brand logo, minimal nav (Health, Features, Price), CTA button ("Pre-Order Now")
2. **layout-row (Hero — Health Impact)** → Video-background (person exercising, sleeping, commuting — watch on wrist throughout day). Centered overlay: eyebrow ("Introducing"), heading ("PulseX Pro"), paragraph ("ECG. Blood Oxygen. Skin Temperature. 14-Day Battery."), button ("Pre-Order — Rs 12,999"), badge ("Clinically Validated"), countdown (launch timer).
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Health Crisis Stat)** → Heading ("Every 33 Seconds, Someone Has a Heart Event") + paragraph (cardiovascular disease stats, importance of early detection). Counter-up stats: 33 seconds, 18.6 million deaths/year, 80% preventable with early detection.
5. **layout-row (Sensor Reveal)** → Full-width watch close-up showing sensor array on back. Heading ("6 Health Sensors. One Watch.") + columnsgrid (3x2 grid): HR, SpO2, ECG, Skin Temp, Stress, Sleep Stages — each with icon and one-line description.
6. **layout-row (ECG Deep Dive)** → Left: animated ECG trace on watch face. Right: heading ("Clinical-Grade ECG on Your Wrist") + paragraph (FDA/CE cleared, AFib detection, shareable PDF reports). Blockquote from cardiologist.
7. **layout-row (Battery Showcase)** → Heading ("14 Days. No Charger Anxiety.") + progress-bar (14-day battery vs competitor average 1-2 days). Counter-up (14) + caption ("Days Battery Life").
8. **layout-row (Design & Bands)** → Carousel: Slide 1 — Titanium finish. Slide 2 — Silicone sport band. Slide 3 — Leather strap. Slide 4 — Metal bracelet. Slide 5 — Limited edition colors.
9. **layout-row (App Dashboard)** → Phone mockup + heading ("Your Health, Visualized") + paragraph (trends, insights, doctor sharing, family health monitoring). Image (app screenshots: health dashboard, sleep analysis, workout log).
10. **layout-row (Pricing)** → columnsgrid (2 columns): PulseX (basic, price, features, button) vs PulseX Pro (full sensors, price, badge "Recommended", button).
11. **layout-row (Early Reviews)** → Carousel of tech reviewer quotes + publication logos. Rating (4.8 average).
12. **layout-row (Final CTA)** → Heading ("Know Your Body Better") + button ("Pre-Order PulseX Pro") + caption ("Free shipping. 30-day returns. 2-year warranty.").
13. **layout-row (Footer)** → Minimal footer with brand, health disclaimer, contact, social.

---

## Variant C — Product Catalog / Comparison Page

> Multi-brand smartwatch browsing with health feature comparison and price filtering

**Page: "Smart Watches & Fitness Trackers — Compare and Buy"**

1. **titlebar** — Brand logo (retailer), nav (Smartwatches, Fitness Bands, Accessories, Compare, Deals), search, cart
2. **layout-row (Category Hero)** → Full-width lifestyle image (wrist with smartwatch). Heading ("Smart Wearables") + paragraph ("Compare health features, battery life, and price across brands") + badge ("Up to 40% Off").
3. **br (minimal divider)**
   Visual separator between hero and content sections.

4. **layout-row (Quick Nav by Brand)** → Ticker (horizontal scrolling): Apple, Samsung, Fitbit, Noise, boAt, Amazfit, OnePlus, Garmin — each with logo + flagship model + "from Rs X".
5. **layout-row (Budget Quick Nav)** → columnsgrid (4 columns): Under Rs 2,000 (fitness bands), Rs 2,000-5,000 (budget smartwatches), Rs 5,000-15,000 (mid-range), Rs 15,000+ (premium). Each with image + count of products.
6. **layout-row (Head-to-Head Comparison)** → Heading ("Top Smartwatch Comparison") + columnsgrid (6 columns): Column 1 (labels: Health Sensors, Display, Battery, Water Rating, Calling, GPS, Price), Columns 2-6 (Apple Watch, Galaxy Watch, Fitbit Sense, Noise ColorFit, boAt Storm). Badges on winners.
7. **layout-row (Best for Health)** → Heading ("Best for Health Monitoring") + columnsgrid (3 columns): ECG-capable watches — image, name, health features list, price, rating, button.
8. **layout-row (Best Battery Life)** → Heading ("Longest Battery Life") + columnsgrid (3 columns): Long-battery watches — image, name, battery days counter-up, price, rating, button.
9. **layout-row (Best for Fitness)** → Heading ("Best for Fitness Tracking") + columnsgrid (3 columns): Fitness-focused watches with GPS — image, name, sport mode count, price, rating, button.
10. **layout-row (Buying Guide)** → Heading ("Smartwatch Buying Guide") + accordion: Item 1 ("Smartwatch vs Fitness Band — which do I need?"), Item 2 ("Which health sensors actually matter?"), Item 3 ("How important is battery life?"), Item 4 ("Apple Watch vs Samsung — which ecosystem?"), Item 5 ("Do I need built-in GPS?"), Item 6 ("What to look for under Rs 5,000?").
11. **layout-row (Accessories)** → Heading ("Bands & Accessories") + tabs: Tab 1 ("Replacement Bands" — grid), Tab 2 ("Screen Protectors" — grid), Tab 3 ("Chargers" — grid), Tab 4 ("Cases" — grid).
12. **layout-row (Customer Reviews)** → Heading ("Buyer Reviews") + carousel of review cards with rating, model purchased, top health feature mentioned.
13. **layout-row (Newsletter)** → Left column: heading ("Wearable Tech News & Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help Choosing?") + paragraph + button ("Chat With Wearable Expert").
14. **layout-row (Footer)** → columnsgrid (4 columns): Store info, brands + categories, support, contact + social.
