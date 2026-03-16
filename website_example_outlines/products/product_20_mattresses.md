# Mattresses & Bedding — Product Pages

> Focus: Conveying comfort through layer-by-layer material breakdowns, firmness visualizations, sleep position guides, and risk-free trial confidence that overcomes the "can't try before you buy" online barrier.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Wakefit | wakefit.co/mattress | Layer-by-layer cross-section visuals; 100-day trial badge above fold; firmness slider (soft to firm); size selector with price change; sleep position recommendation grid |
| SleepyCat | sleepycat.in | Playful brand voice; "AirGen Memory Foam" technology hero; video testimonials; comparison chart vs competitors; free pillow bundle upsell |
| Duroflex | duroflex.com | Premium lifestyle imagery; doctor-recommended badges; technology-first naming (Duropedic, NeoSense); orthopaedic certification callouts; EMI calculator inline |
| The Sleep Company | thesleepcompany.in | Patented SmartGRID technology hero animation; celebrity endorsement (Sachin Tendulkar); firmness comparison tool; 100-night trial + 10-year warranty prominently above fold |
| Sleepyhead (Sleepwell) | sleepyhead.com | Budget-friendly positioning; "starts at Rs 3,999" pricing hero; comfort level icons; mattress quiz for personalized recommendation; unboxing video section |

**Patterns to incorporate:**
- Layer-by-layer cross-section diagrams showing foam/spring/latex composition
- Firmness level indicator (visual scale from soft to firm)
- Size selector grid with real-time price updates (Single, Double, Queen, King)
- Sleep position guide (side, back, stomach) with mattress recommendation
- 100-day/night trial prominently displayed as risk-removal
- 10-year warranty counter as trust signal
- Cooling technology section with temperature comparison visuals
- Certification badges (CertiPUR-US, OEKO-TEX, ISO)
- Video unboxing showing bed-in-a-box expansion
- Edge support demonstration with weight distribution visual

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Memory Foam / Orthopaedic Mattress Detail**

1. **titlebar** — Brand logo, nav links (Mattresses, Pillows, Bedding, Sleep Quiz, Support), cart icon, search
2. **layout-row (Hero — Product Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel with images (mattress top view, cross-section layers, lifestyle bedroom shot, packaging/unboxing, close-up fabric texture). Right column: eyebrow ("Orthopaedic Collection"), heading (product name), rating (4.6 stars, review count), paragraph (one-line: "7-zone support with cooling gel memory foam"), heading (price), caption (MRP strikethrough + savings), badge ("100-Night Free Trial"), size selector (radio buttons: Single, Double, Queen, King — each with price), button ("Buy Now"), button ("Add to Cart"), caption ("Free delivery in 5-7 days. Easy returns.").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Material — Foam/Spring/Latex)** → `comp_0_components_2`
   Left column: image (cross-section diagram showing all layers with labels). Right column: heading ("5-Layer Comfort Architecture") + paragraph describing each layer. Accordion: Item 1 — "Layer 1: Breathable Knitted Cover" (description), Item 2 — "Layer 2: Cooling Gel Memory Foam" (description), Item 3 — "Layer 3: HR Foam Transition Layer" (description), Item 4 — "Layer 4: 7-Zone Pocket Spring Core" (description), Item 5 — "Layer 5: Anti-Skid Base" (description).
5. **layout-row (Feature: Firmness Level)** → `comp_0_components_3`
   Centered: heading ("Medium-Firm Comfort") + paragraph ("Rated 6.5 out of 10 on the firmness scale — ideal for back and combination sleepers"). Progress-bar (firmness level: 65% filled, labeled "Medium-Firm"). columnsgrid (3 columns): Column 1 — icon + heading ("Soft") + paragraph ("Best for side sleepers"). Column 2 — icon + heading ("Medium-Firm") + badge ("This Mattress") + paragraph ("Best for back & combo sleepers"). Column 3 — icon + heading ("Firm") + paragraph ("Best for stomach sleepers").
6. **layout-row (Feature: Sizes Available)** → `comp_0_components_4`
   Heading ("Available in All Standard Sizes") + columnsgrid (4 columns): Each column — heading (size name: Single, Double, Queen, King) + paragraph (dimensions: "72 x 36 x 8 inches") + caption (price for that size) + badge ("Most Popular" on Queen). Caption below: "Custom sizes available on request."
7. **layout-row (Feature: Cooling Technology)** → `comp_0_components_5`
   Left column: heading ("Sleep 3 Degrees Cooler") + paragraph (open-cell foam structure, gel-infused layer, breathable cover) + counter-up (3) + caption ("Degrees cooler than regular foam"). Right column: image (thermal imaging comparison — regular foam vs cooling foam). Badge ("CoolTech Certified").
8. **layout-row (Feature: Edge Support)** → `comp_0_components_6`
   Left column: image (person sitting on mattress edge without sinking). Right column: heading ("Reinforced Edge Support") + paragraph (high-density perimeter foam, no roll-off, full surface usable) + paragraph ("Use 100% of your mattress surface — sit, sleep, or stretch right to the edge.").
9. **layout-row (Feature: Trial Period)** → `comp_0_components_7`
   Centered: counter-up (100) + heading ("Night Risk-Free Trial") + paragraph ("Sleep on it for 100 nights. If you don't love it, we'll pick it up and refund you — no questions asked."). columnsgrid (3 columns): Column 1 — icon + heading ("Free Delivery") + paragraph ("Compressed & rolled, delivered to your door"). Column 2 — icon + heading ("100-Night Trial") + paragraph ("Try it at home, return if unsatisfied"). Column 3 — icon + heading ("Free Returns") + paragraph ("We pick up at no charge").
10. **layout-row (Feature: Warranty)** → `comp_0_components_8`
   Left column: counter-up (10) + heading ("Year Warranty") + paragraph ("Covers manufacturing defects, sagging >1.5 inches, foam deterioration. Terms apply."). Right column: accordion — Item 1: "What does the warranty cover?" (details), Item 2: "What's not covered?" (exclusions), Item 3: "How to claim warranty?" (process).
11. **layout-row (Feature: Price & Payment Plans)** → `comp_0_components_9`
    Left column: heading (price) + caption (MRP strikethrough) + badge ("Save Rs 4,000"). Right column: tabs — Tab 1: "Pay Full" (price, button "Buy Now"), Tab 2: "EMI Options" (3/6/12 month breakdowns with monthly amount), Tab 3: "Pay Later" (buy now pay in 30 days). Caption ("No-cost EMI available on select cards").
12. **layout-row (Feature: Sleep Position Guide)** → `comp_0_components_10`
    Heading ("Find Your Perfect Match by Sleep Position") + columnsgrid (3 columns): Column 1 — image (side sleeper illustration) + heading ("Side Sleepers") + paragraph ("Need pressure relief at shoulders and hips. Soft to medium-firm recommended.") + rating (4 out of 5 suitability). Column 2 — image (back sleeper) + heading ("Back Sleepers") + paragraph ("Need lumbar support with even weight distribution. Medium-firm recommended.") + rating (5 out of 5 suitability, badge "Best Match"). Column 3 — image (stomach sleeper) + heading ("Stomach Sleepers") + paragraph ("Need firm support to prevent spine misalignment. Firm recommended.") + rating (3 out of 5 suitability).
13. **layout-row (Feature: Certifications)** → `comp_0_components_11`
    Heading ("Certified Safe & Sustainable") + ticker (scrolling certification badges): CertiPUR-US, OEKO-TEX Standard 100, ISO 9001, Green Guard Gold, Hypoallergenic Tested. Paragraph ("All materials tested for harmful chemicals, emissions, and allergens.").
14. **layout-row (Reviews & Ratings)** → `comp_0_components_12`
    Left column: heading ("Customer Reviews") + rating (4.6 stars) + counter-up (12,450 reviews) + progress-bar set (5-star to 1-star distribution). Right column: carousel of blockquote testimonials — each with rating, quote text, caption (reviewer name + "Verified Purchase").
15. **layout-row (Complete Your Sleep Setup)** → `comp_0_components_13`
    Heading ("Complete Your Sleep Setup") + columnsgrid (4 columns): Each — image + heading (product: pillow, protector, bed frame, comforter) + caption (price) + button ("Add to Cart").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand story + paragraph. Column 2 — links (Mattresses, Pillows, Bedding, Accessories). Column 3 — links (Trial Policy, Warranty, Shipping, Returns). Column 4 — paragraph (contact info) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Marketing-focused layout for a new mattress technology launch with storytelling and sleep science

**Page: "CloudRest Pro — The Mattress That Learns Your Body"**

1. **titlebar** — Brand logo, minimal nav (Home, Technology, Reviews), CTA button ("Try for 100 Nights")
2. **layout-row (Hero — Cinematic Impact)** → Video-background (slow-motion person sinking into mattress). Centered overlay: eyebrow ("Introducing"), heading ("CloudRest Pro"), paragraph ("Adaptive foam that responds to your body temperature and weight — every night."), button ("Shop Now — From Rs 12,999"), badge ("100-Night Trial").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Pain Point)** → Heading ("68% of Indians Wake Up With Back Pain") + paragraph (poor mattress quality stats, sleep deprivation impact) + counter-up stats: 68% back pain, 4.2 crore affected, Rs 15,000 avg annual medical cost.
5. **layout-row (Technology Reveal)** → Full-width cross-section image with animated layer labels. Heading ("5 Layers. Zero Compromises.") + paragraph (brief on each layer). Badge ("Patented AdaptFoam Technology").
6. **layout-row (Before & After)** → columnsgrid (2 columns): Column 1 — heading ("Regular Mattress") + image (poor spine alignment) + list of problems. Column 2 — heading ("CloudRest Pro") + image (proper spine alignment) + list of benefits. Badges highlighting differences.
7. **layout-row (Celebrity / Expert Endorsement)** → Blockquote from orthopaedic doctor + image (doctor portrait) + caption (name, credentials). Rating (5 stars, "Doctor Recommended").
8. **layout-row (Feature Carousel)** → Carousel: Slide 1 — Cooling tech. Slide 2 — Edge support. Slide 3 — Motion isolation. Slide 4 — Hypoallergenic cover. Slide 5 — Zero partner disturbance.
9. **layout-row (Social Proof Wall)** → Heading ("50,000+ Happy Sleepers") + columnsgrid (3 columns) of review cards with ratings, quotes, reviewer photos.
10. **layout-row (Size & Price Grid)** → Heading ("Choose Your Size") + columnsgrid (4 columns): Each size (Single, Double, Queen, King) with dimensions, price, badge on bestseller, button ("Buy Now").
11. **layout-row (Risk Removal)** → columnsgrid (3 columns): counter-up (100) + "Night Trial", counter-up (10) + "Year Warranty", counter-up (0) + "Risk — Free Returns". Paragraph ("We believe in our mattress so much, we'll let you sleep on it for 100 nights risk-free.").
12. **layout-row (FAQ)** → Accordion: 8 questions covering firmness, delivery, trial, warranty, sizes, EMI, care instructions, certification.
13. **layout-row (Final CTA)** → Heading ("Your Best Sleep Starts Tonight") + button ("Shop CloudRest Pro") + caption ("Free delivery. 100-night trial. 10-year warranty.").
14. **layout-row (Footer)** → Minimal footer with brand, contact, policies, social links.

---

## Variant C — Product Catalog / Comparison Page

> Multi-mattress browsing experience with filtering, comparison, and sleep quiz entry

**Page: "Mattresses — Find Your Perfect Match"**

1. **titlebar** — Brand logo, nav (Memory Foam, Spring, Latex, Orthopaedic, Kids, Pillows, Accessories), search, cart
2. **layout-row (Category Hero)** → Full-width lifestyle image (couple sleeping peacefully). Heading ("Mattresses for Every Sleeper") + paragraph ("100-night trial on every mattress. Free delivery.") + badge ("Up to 50% Off").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Sleep Quiz CTA)** → Centered: heading ("Not Sure Which Mattress?") + paragraph ("Take our 2-minute sleep quiz") + button ("Find My Mattress") + caption ("Personalized recommendation based on your sleep style").
5. **layout-row (Category Quick Nav)** → Ticker or columnsgrid (horizontal): Memory Foam, Pocket Spring, Latex, Orthopaedic, Hybrid, Kids, Guest Room — each with icon + label + "from Rs X,XXX".
6. **layout-row (Filter Bar)** → Layout-row with form elements: dropdown (material type), dropdown (firmness), dropdown (size), dropdown (price range), dropdown (brand). Button ("Apply Filters").
7. **layout-row (Bestsellers)** → Heading ("Our Bestsellers") + columnsgrid (3 columns): Each — image, badge ("Bestseller" / "Editor's Pick"), heading (product name), rating, paragraph (material + firmness + key feature), heading (price + strikethrough), button ("View Details").
8. **layout-row (Comparison Table)** → Heading ("Compare Our Top Mattresses") + columnsgrid (5 columns): Column 1 (feature labels: Material, Firmness, Layers, Cooling, Trial, Warranty, Price), Columns 2-5 (4 mattresses compared). Badges on "Best Value" and "Premium Pick".
9. **layout-row (By Sleep Position)** → Heading ("Shop by Sleep Position") + columnsgrid (3 columns): Side Sleepers (image + recommended mattresses + button), Back Sleepers (image + recommended + button), Stomach Sleepers (image + recommended + button).
10. **layout-row (Budget Picks)** → Heading ("Under Rs 10,000") + columnsgrid (4 columns): Budget mattress cards with image, name, firmness badge, price, rating, button.
11. **layout-row (Premium Collection)** → Heading ("Premium Collection — Rs 25,000+") + columnsgrid (3 columns): Premium cards with image, name, technology highlight, price, rating, button.
12. **layout-row (Buying Guide)** → Heading ("Mattress Buying Guide") + accordion: Item 1 ("Memory Foam vs Spring vs Latex — which is best?"), Item 2 ("How firm should my mattress be?"), Item 3 ("What size do I need?"), Item 4 ("How often should I replace my mattress?"), Item 5 ("Is online mattress buying safe?"), Item 6 ("What certifications should I look for?").
13. **layout-row (Customer Reviews)** → Heading ("What Our Sleepers Say") + carousel of review cards: rating + blockquote + caption (product purchased + verified badge).
14. **layout-row (Bundle Deals)** → Heading ("Sleep Bundles — Save Up to 30%") + columnsgrid (3 columns): Bundle 1 (mattress + 2 pillows), Bundle 2 (mattress + protector + pillows), Bundle 3 (complete bedroom set). Each with original price strikethrough, bundle price, savings badge, button.
15. **layout-row (Newsletter)** → Left column: heading ("Sleep Tips & Exclusive Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help?") + paragraph + button ("Chat With Sleep Expert").
16. **layout-row (Footer)** → columnsgrid (4 columns): Brand info, product categories, policies + support, contact + social.
