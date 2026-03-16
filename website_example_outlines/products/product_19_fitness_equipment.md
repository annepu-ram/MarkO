# Fitness & Gym Equipment — Product Pages

> Focus: Building trust through weight capacity specs, build quality visuals, foldability demos, and workout program previews that convert browsers into buyers.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Decathlon (Domyos) | decathlon.com/collections/gym-equipment | Category grid with filter sidebar; each product card shows weight capacity, dimensions, star rating; "Add to Cart" always visible |
| PowerMax Fitness | powermaxfitness.in | Hero carousel of treadmills; spec table front-and-center; foldability comparison images; EMI options below price |
| Cult Sport | cultsport.com/fitness-equipment | Lifestyle hero imagery; category tabs (cardio, strength, yoga); badge overlays ("Bestseller", "New"); video demos inline |
| Lifeline Fitness | lifelinefitness.com | Commercial-grade positioning; heavy use of counter-up stats (lbs capacity, warranty years); before/after transformation gallery |
| NordicTrack | nordictrack.com | Full-width video hero; interactive console preview; iFIT subscription integration section; comparison table for models |

**Patterns to incorporate:**
- Spec tables with weight capacity, dimensions, and motor power prominently displayed
- Foldability comparison images (folded vs unfolded) for home gym appeal
- Video demos showing the equipment in use with real people
- EMI/financing options placed directly below price
- Badge overlays for bestsellers, new arrivals, and limited stock
- Workout program library preview as value-add
- Assembly difficulty indicator (easy/moderate/professional)
- Counter-up stats for brand trust (units sold, years in market)
- Before/after transformation testimonials
- Comparison table across model variants

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Treadmill / Home Gym Equipment Detail**

1. **titlebar** — Brand logo, nav links (Cardio, Strength, Accessories, Support), cart icon, search
2. **layout-row (Hero — Product Gallery + Key Info)** → `comp_0_components_1`
   Left column: carousel with 5-6 product images (front, side, folded, console close-up, in-use). Right column: eyebrow ("Bestseller"), heading (product name), rating (4.5 stars, review count), paragraph (one-line tagline), heading (price with strikethrough MRP), badge ("EMI from Rs 999/mo"), button ("Add to Cart"), button ("Buy Now"), caption (free delivery + return policy).
3. **br (wave divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Weight Capacity)** → `comp_0_components_2`
   Left column: icon (weight icon) + heading ("Supports Up to 120 kg") + paragraph (load-tested steel frame, reinforced deck, anti-vibration pads). Right column: image (person on equipment, stress-test visual). Badge ("Heavy-Duty Certified").
5. **layout-row (Feature: Dimensions & Footprint)** → `comp_0_components_3`
   Left column: image (overhead dimension diagram with measurements). Right column: heading ("Compact Footprint for Any Room") + paragraph (L x W x H specs, room-size recommendations) + caption ("Fits in a 6x4 ft space").
6. **layout-row (Feature: Material & Build Quality)** → `comp_0_components_4`
   columnsgrid (3 columns): Column 1 — icon + heading ("Alloy Steel Frame") + paragraph (corrosion-resistant, powder-coated). Column 2 — icon + heading ("Multi-Layer Belt") + paragraph (anti-slip, shock-absorbing). Column 3 — icon + heading ("Rubber Grip Handles") + paragraph (ergonomic, sweat-proof).
7. **layout-row (Feature: Resistance Levels / Motor Power)** → `comp_0_components_5`
   Left column: heading ("5.0 HP Peak Motor") + paragraph (whisper-quiet, continuous duty, auto-incline up to 15 levels) + progress-bar (motor power visual: 5.0 HP out of 7.0 HP scale). Right column: image (motor close-up or incline animation).
8. **layout-row (Feature: Console & Tracking)** → `comp_0_components_6`
   Left column: image (console/display close-up showing metrics). Right column: heading ("Smart LCD Console") + paragraph (tracks speed, distance, calories, heart rate, time) + ticker (scrolling metric icons: speed, distance, calories, heart rate, incline). Badge ("Bluetooth Enabled").
9. **layout-row (Feature: Foldability & Storage)** → `comp_0_components_7`
   Left column: heading ("Hydraulic Fold System") + paragraph (one-touch fold, soft-drop mechanism, transport wheels) + caption ("Folds to 50% footprint"). Right column: image (side-by-side folded vs unfolded comparison).
10. **layout-row (Feature: Assembly)** → `comp_0_components_8`
   Left column: icon (tools icon) + heading ("Easy 30-Minute Assembly") + paragraph (pre-assembled main unit, only 6 bolts, tool kit included). Right column: accordion — Item 1: "What's in the box?" (parts list), Item 2: "Do I need professional assembly?" (answer), Item 3: "Assembly video available?" (link).
11. **layout-row (Feature: Warranty & After-Sales)** → `comp_0_components_9`
    columnsgrid (3 columns): Column 1 — counter-up (3) + caption ("Year Frame Warranty"). Column 2 — counter-up (1) + caption ("Year Motor Warranty"). Column 3 — counter-up (500) + caption ("Service Centers Nationwide"). Paragraph below: "Free annual maintenance for first year."
12. **layout-row (Feature: Price & Payment Options)** → `comp_0_components_10`
    Left column: heading (price) + paragraph (MRP strikethrough, savings amount) + badge ("Save 25%"). Right column: tabs — Tab 1: "Full Payment" (price + button), Tab 2: "EMI Plans" (3/6/12 month options with monthly amount), Tab 3: "Exchange Offer" (trade-in old equipment).
13. **layout-row (Feature: Workout Programs)** → `comp_0_components_11`
    heading ("12 Built-In Workout Programs") + columnsgrid (4 columns): Each column — icon + heading (program name: "Fat Burn", "Interval", "Hill Climb", "Heart Rate Zone") + paragraph (brief description). Badge ("Free App Access for 1 Year").
14. **layout-row (Reviews & Ratings)** → `comp_0_components_12`
    Left column: heading ("Customer Reviews") + rating (4.5 stars) + counter-up (2,847 reviews) + progress-bar (5-star distribution). Right column: carousel of blockquote testimonials with rating per review.
15. **layout-row (Related Products)** → `comp_0_components_13`
    heading ("Complete Your Home Gym") + columnsgrid (4 columns): Each column — image + heading (product name) + paragraph (key spec) + caption (price) + button ("View").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Products, Support, Blog). Column 3 — links (Warranty, Returns, Shipping). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Marketing-focused layout for a new equipment line launch with storytelling, social proof, and urgency

**Page: "PowerFit Pro Series — Redefine Your Home Gym"**

1. **titlebar** — Brand logo, minimal nav (Home, Shop, About), CTA button ("Pre-Order Now")
2. **layout-row (Hero — Full-Width Impact)** → Video-background with gym footage overlay. Centered: eyebrow ("Introducing"), heading ("PowerFit Pro Series"), paragraph ("Commercial-grade performance. Living-room friendly."), button ("Pre-Order — Launch Price Rs 29,999"), countdown (launch date timer).
3. **br (wave divider)**
   Visual separator between hero and content sections.

4. **layout-row (Problem Statement)** → Heading ("Your Gym Membership Costs Rs 36,000/Year") + paragraph (commute time, crowded hours, hygiene concerns). Counter-up stats: Rs 36K/year gym cost, 2 hours/day commute, 365 days of excuses.
5. **layout-row (Solution Reveal)** → Full-width image (product hero shot) + heading ("One Machine. Zero Excuses.") + paragraph (key benefits in 3 bullet points). Badge ("Launching Soon").
6. **layout-row (Feature Highlights Carousel)** → Carousel: Slide 1 — Motor power + specs. Slide 2 — Foldability demo. Slide 3 — Console preview. Slide 4 — Workout programs. Slide 5 — Build quality close-ups.
7. **layout-row (Social Proof)** → Ticker (scrolling logos of fitness influencers/publications that reviewed it). Blockquote from fitness expert. Rating (press rating).
8. **layout-row (Comparison Table)** → Heading ("PowerFit Pro vs Competition") + columnsgrid comparing 3 models with specs (motor, weight capacity, programs, warranty, price).
9. **layout-row (Early Bird Pricing)** → Heading ("Launch Pricing — Limited Time") + tabs: Tab 1 ("Pro Basic" — price, specs, button), Tab 2 ("Pro Plus" — price, specs, button, badge "Most Popular"), Tab 3 ("Pro Elite" — price, specs, button).
10. **layout-row (FAQ)** → Accordion with 6-8 common questions about delivery, assembly, warranty, returns, EMI.
11. **layout-row (Final CTA)** → Heading ("Transform Your Home Into a Gym") + button ("Pre-Order Now") + caption ("100-day trial. Free returns.") + countdown (offer expiry).
12. **layout-row (Footer)** → Minimal footer with brand, contact, social links.

---

## Variant C — Product Catalog / Comparison Page

> Multi-product browsing experience for category exploration and side-by-side comparison

**Page: "Home Gym Equipment — Treadmills, Bikes & More"**

1. **titlebar** — Brand logo, nav (Treadmills, Exercise Bikes, Ellipticals, Strength, Accessories), search, cart
2. **layout-row (Category Hero)** → Full-width image (home gym lifestyle). Heading ("Home Gym Equipment") + paragraph ("Find the perfect machine for your fitness goals") + eyebrow ("Free delivery on orders over Rs 9,999").
3. **br (wave divider)**
   Visual separator between hero and content sections.

4. **layout-row (Category Quick Nav)** → Ticker or columnsgrid (horizontal scrolling category cards): Treadmills, Exercise Bikes, Ellipticals, Cross Trainers, Multi-Gyms, Dumbbells, Yoga — each with icon + label + product count.
5. **layout-row (Filter & Sort Bar)** → Layout-row with dropdowns: price range, weight capacity, brand, rating, foldable (yes/no), motor power. Button ("Apply Filters").
6. **layout-row (Featured / Bestsellers)** → Heading ("Bestsellers") + columnsgrid (3 columns): Each column — image, badge ("Bestseller"), heading (product name), rating, paragraph (key spec: "5 HP, 120 kg capacity, foldable"), heading (price), button ("View Details").
7. **layout-row (Comparison Table)** → Heading ("Compare Top Treadmills") + columnsgrid (4 columns): Column 1 (specs labels), Columns 2-4 (3 products compared on: motor power, weight capacity, dimensions, foldable, programs, warranty, price). Badges highlighting winner per row.
8. **layout-row (Budget Picks)** → Heading ("Under Rs 15,000") + columnsgrid (4 columns): budget-friendly product cards with image, name, price, rating, button.
9. **layout-row (Premium Picks)** → Heading ("Premium Collection — Rs 30,000+") + columnsgrid (3 columns): premium product cards with image, name, key feature highlight, price, rating, button.
10. **layout-row (Buying Guide)** → Heading ("How to Choose the Right Equipment") + accordion: Item 1 ("What motor power do I need?"), Item 2 ("How much space do I need?"), Item 3 ("Manual vs Motorized — which is better?"), Item 4 ("What weight capacity should I look for?"), Item 5 ("Foldable vs Non-foldable").
11. **layout-row (Customer Favorites)** → Heading ("What Our Customers Say") + carousel of review cards: image (customer photo) + rating + blockquote + caption (product purchased).
12. **layout-row (Newsletter + Support)** → Left column: heading ("Get Fitness Tips & Deals") + form (textbox for email + button "Subscribe"). Right column: heading ("Need Help Choosing?") + paragraph + button ("Talk to an Expert") + caption ("Mon-Sat, 9am-8pm").
13. **layout-row (Footer)** → columnsgrid (4 columns): Brand info, product categories, support links, contact + social.
