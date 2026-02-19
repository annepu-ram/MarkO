# Gaming Consoles & Accessories — Product Pages

> Focus: Showcasing raw performance specs (CPU/GPU, FPS, storage), immersive game library previews, controller innovation demos, and ecosystem value that justifies the console investment.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| PlayStation (PS5) | playstation.com/ps5 | Cinematic scroll-triggered animations; full-width game trailers auto-playing; DualSense haptic feedback feature section with close-up renders; edition comparison (Standard vs Digital); PS Plus subscription tie-in |
| Xbox Series X | xbox.com/consoles/xbox-series-x | "Most powerful console" hero claim; 12 TFLOPS stat prominently displayed; Game Pass integration as primary value prop; backward compatibility spanning 4 generations; Quick Resume feature demo |
| Nintendo Switch | nintendo.com/switch | Hybrid design hero (TV + handheld transition video); family/social gaming lifestyle imagery; game library carousel as primary selling point; Joy-Con color configurator; Nintendo Switch Online subscription section |
| Steam Deck | steamdeck.com | PC gaming heritage positioning; "your Steam library anywhere" messaging; tech specs section with expandable details; 3 edition comparison (storage tiers); community/mod-friendly messaging |
| Valve Index | store.steampowered.com/valveindex | VR-first hero with immersive imagery; field-of-view and refresh rate specs front-center; controller finger-tracking demo; full kit vs individual component pricing; compatible games showcase |

**Patterns to incorporate:**
- Cinematic hero with auto-playing game footage or console beauty shots
- Performance counter-up stats (TFLOPS, FPS, storage speed)
- Game library carousel as ecosystem proof
- Edition/bundle comparison table (Digital vs Disc, storage tiers)
- Controller feature deep-dive with close-up renders
- Online service subscription tie-in (PS Plus, Game Pass, NSO)
- Backward compatibility list as value multiplier
- Resolution and frame rate comparison visuals (1080p vs 4K vs 8K)
- Bundle deal configurator (console + extra controller + game)
- Competitor comparison table for head-to-head specs

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Gaming Console Detail (e.g., PlayStation 5 / Xbox Series X)**

1. **titlebar** — Brand logo, nav links (Console, Games, Accessories, PS Plus/Game Pass, Support), cart icon, search
2. **layout-row (Hero — Console Showcase + Key Info)** → `comp_0_components_1`
   Left column: carousel (console front, back, side, with controller, size comparison). Right column: eyebrow ("Next-Gen Gaming"), heading (console name), paragraph (tagline: "Lightning-fast load times. Stunning 4K visuals. Immersive haptics."), heading (price), badge (edition: "Disc Edition" / "Digital Edition"), button ("Buy Now"), button ("Find a Retailer"), caption ("In stock. Free shipping.").
3. **layout-row (Feature: CPU/GPU Specs)** → `comp_0_components_2`
   Left column: heading ("Raw Power Under the Hood") + paragraph (custom AMD Zen 2 CPU, RDNA 2 GPU, hardware ray tracing) + counter-up (10.28) + caption ("TFLOPS GPU Performance") + counter-up (3.5) + caption ("GHz CPU Clock Speed"). Right column: image (die shot or architecture diagram). Badge ("Custom Silicon").
4. **layout-row (Feature: Storage)** → `comp_0_components_3`
   Left column: image (SSD close-up or speed comparison visual). Right column: heading ("Ultra-Fast SSD Storage") + paragraph (825GB custom NVMe SSD, 5.5 GB/s read speed, near-instant load times) + progress-bar (load speed comparison: SSD vs HDD — 2 seconds vs 30 seconds visual). Caption ("Expandable with M.2 NVMe SSD slot").
5. **layout-row (Feature: Game Library)** → `comp_0_components_4`
   Heading ("Thousands of Games. Your Favorites and More.") + carousel (game cover art: 10-12 exclusive and popular titles with name + genre caption). Counter-up (4,000+) + caption ("Games Available at Launch"). Badge ("Platform Exclusives").
6. **layout-row (Feature: Controller Features)** → `comp_0_components_5`
   Left column: heading ("Controller Innovation") + paragraph (adaptive triggers, haptic feedback, built-in mic, motion sensors, USB-C charging). Accordion: Item 1 — "Haptic Feedback" (description), Item 2 — "Adaptive Triggers" (description), Item 3 — "Built-In Microphone" (description), Item 4 — "Ergonomic Design" (description). Right column: image (controller close-up beauty shot with callout labels).
7. **layout-row (Feature: Online Services)** → `comp_0_components_6`
   Heading ("Unlock the Full Experience") + columnsgrid (3 columns): Column 1 — icon + heading ("Free Tier") + paragraph (online store, basic features) + caption ("Free"). Column 2 — icon + heading ("Essential") + paragraph (monthly games, online multiplayer, cloud storage) + caption ("Rs 499/month") + badge ("Most Popular"). Column 3 — icon + heading ("Premium") + paragraph (classic game catalog, game trials, exclusive discounts) + caption ("Rs 749/month"). Button ("Compare Plans").
8. **layout-row (Feature: Backward Compatibility)** → `comp_0_components_7`
   Left column: heading ("Play Your Entire Collection") + paragraph (backward compatible with previous generation, enhanced performance on older titles, save transfer) + counter-up (4) + caption ("Console Generations Supported"). Right column: columnsgrid (2 columns) showing logos/covers of classic games playable on new console. Badge ("Enhanced for Next-Gen").
9. **layout-row (Feature: Resolution & FPS)** → `comp_0_components_8`
   Heading ("See Every Detail. Feel Every Frame.") + columnsgrid (3 columns): Column 1 — counter-up (4) + heading ("K Resolution") + paragraph ("Native 4K output with HDR10 support"). Column 2 — counter-up (120) + heading ("FPS") + paragraph ("Silky-smooth gameplay at up to 120 frames per second"). Column 3 — counter-up (8) + heading ("K Ready") + paragraph ("8K output support for future-proof visuals"). Image below: split-screen comparison (1080p vs 4K game screenshot).
10. **layout-row (Feature: Price & Bundles)** → `comp_0_components_9`
    Heading ("Choose Your Edition") + columnsgrid (3 columns): Column 1 — image (Digital Edition) + heading ("Digital Edition") + paragraph (specs, no disc drive) + heading (price) + button ("Buy Now"). Column 2 — image (Standard) + heading ("Standard Edition") + badge ("Most Popular") + paragraph (specs, disc drive included) + heading (price) + button ("Buy Now"). Column 3 — image (Bundle) + heading ("Launch Bundle") + paragraph (console + extra controller + game) + heading (bundle price) + badge ("Save Rs 3,000") + button ("Buy Bundle").
11. **layout-row (Feature: Editions Comparison)** → `comp_0_components_10`
    Heading ("Edition Comparison") + tabs: Tab 1 ("Digital Edition" — feature list with checkmarks), Tab 2 ("Standard Edition" — feature list), Tab 3 ("Pro / Slim" — if applicable). Checkmarks and X marks for feature availability.
12. **layout-row (Feature: Competitor Comparison)** → `comp_0_components_11`
    Heading ("How We Stack Up") + columnsgrid (4 columns): Column 1 (spec labels: CPU, GPU, Storage, Frame Rate, Exclusive Count, Price), Columns 2-4 (this console vs 2 competitors). Badges on winning specs. Caption ("Specifications as of launch date.").
13. **layout-row (Reviews & Media Praise)** → `comp_0_components_12`
    Heading ("Critics Love It") + ticker (scrolling publication logos: IGN, GameSpot, Polygon, Kotaku, Digital Foundry). columnsgrid (3 columns) of blockquote review excerpts with rating and publication name.
14. **layout-row (Accessories)** → `comp_0_components_13`
    Heading ("Essential Accessories") + columnsgrid (4 columns): Each — image + heading (controller, headset, charging dock, media remote) + caption (price) + button ("Add to Cart").
15. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand info + paragraph. Column 2 — links (Console, Games, Accessories, Online Service). Column 3 — links (Support, Warranty, Where to Buy). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Cinematic marketing page for a new console generation reveal with hype-building and pre-order conversion

**Page: "Next-Gen Arrives — Console X Pro"**

1. **titlebar** — Brand logo, minimal nav (Features, Games, Pre-Order), CTA button ("Pre-Order Now")
2. **layout-row (Hero — Cinematic Reveal)** → Video-background (cinematic console reveal trailer, game footage montage). Centered overlay: heading ("The Future of Gaming"), paragraph ("Unmatched power. Unrivaled experiences."), button ("Pre-Order — Rs 49,990"), countdown (launch date timer), badge ("Limited First Edition").
3. **layout-row (Performance Stats)** → Dark background. columnsgrid (4 columns): counter-up (13.5) + caption ("TFLOPS"), counter-up (2) + caption ("TB SSD"), counter-up (120) + caption ("FPS"), counter-up (8) + caption ("K Output"). Heading ("The Most Powerful Console Ever Built").
4. **layout-row (Design Reveal)** → Full-width image (console beauty shot, multiple angles). Heading ("Designed for the Future") + paragraph (design philosophy, materials, cooling system). Carousel (close-up details: vents, ports, LED, finish).
5. **layout-row (Exclusive Game Showcase)** → Heading ("Launch Exclusives") + carousel (6-8 game trailers/key art with title, genre, release date). Badge ("Console Exclusive") on each.
6. **layout-row (Controller Deep Dive)** → Left: image (controller exploded view). Right: heading ("Feel the Game") + paragraph (next-gen haptics, adaptive triggers, precision analog) + accordion with feature breakdowns.
7. **layout-row (Backward Compatibility Promise)** → Heading ("Your Library. Enhanced.") + counter-up (thousands) + paragraph (all previous gen games playable, enhanced resolution and frame rates, save transfer). Carousel of enhanced game comparisons.
8. **layout-row (Online Service Tie-In)** → Heading ("Day One Game Pass / PS Plus") + paragraph (hundreds of games at launch, cloud gaming, multiplayer) + columnsgrid (2 columns): Free tier vs Premium tier comparison.
9. **layout-row (Edition Pre-Order)** → columnsgrid (3 columns): Standard, Pro, Collector's Edition — each with image, specs, price, badge, button ("Pre-Order"). Countdown timer on Collector's Edition ("Only X available").
10. **layout-row (Developer Quotes)** → Carousel of blockquotes from game developers praising the hardware + studio logos.
11. **layout-row (Final CTA)** → Heading ("Don't Miss Launch Day") + button ("Pre-Order Now") + countdown (launch date) + caption ("Free shipping on pre-orders. Cancel anytime.").
12. **layout-row (Footer)** → Minimal footer with brand, legal, social links.

---

## Variant C — Product Catalog / Comparison Page

> Multi-console and accessories browsing experience for informed purchase decisions

**Page: "Gaming Consoles & Accessories — Find Your Perfect Setup"**

1. **titlebar** — Brand logo (retailer), nav (Consoles, Controllers, Headsets, Storage, Games, Deals), search, cart
2. **layout-row (Category Hero)** → Full-width gaming lifestyle image (gaming setup with multiple consoles). Heading ("Gaming Consoles & Accessories") + paragraph ("Compare specs, explore bundles, find your next gaming setup") + eyebrow ("Free shipping on orders over Rs 999").
3. **layout-row (Console Quick Nav)** → columnsgrid or ticker (horizontal): PlayStation, Xbox, Nintendo, Steam Deck, VR Headsets — each with brand icon + latest model name + "from Rs XX,XXX".
4. **layout-row (Head-to-Head Comparison)** → Heading ("Console Showdown") + columnsgrid (5 columns): Column 1 (spec labels: CPU, GPU, TFLOPS, Storage, Max Resolution, Max FPS, Exclusive Count, Online Service, Price), Columns 2-5 (PS5, Xbox Series X, Nintendo Switch, Steam Deck). Badges on "Best for" each category.
5. **layout-row (Bestselling Consoles)** → Heading ("Bestsellers") + columnsgrid (3 columns): Each — image, badge ("Bestseller" / "Editor's Pick"), heading (console name), rating, paragraph (key specs: storage, resolution, exclusive count), heading (price), button ("View Details").
6. **layout-row (Bundles & Deals)** → Heading ("Bundle Deals — Save Up to Rs 5,000") + columnsgrid (3 columns): Each bundle — image (console + accessories), heading (bundle name), paragraph (what's included), heading (original price strikethrough + bundle price), badge ("Save Rs X"), button ("Buy Bundle").
7. **layout-row (By Gaming Style)** → Heading ("Shop by Gaming Style") + columnsgrid (4 columns): Column 1 — icon + heading ("Casual Gamer") + paragraph + button (link to Nintendo). Column 2 — icon + heading ("Competitive Gamer") + paragraph + button (link to PS5/Xbox). Column 3 — icon + heading ("PC Gamer on the Go") + paragraph + button (link to Steam Deck). Column 4 — icon + heading ("VR Explorer") + paragraph + button (link to VR headsets).
8. **layout-row (Accessories Grid)** → Heading ("Essential Accessories") + tabs: Tab 1 ("Controllers" — product grid), Tab 2 ("Headsets" — product grid), Tab 3 ("Storage" — product grid), Tab 4 ("Charging" — product grid). Each product: image, name, compatibility badge, price, button.
9. **layout-row (Buying Guide)** → Heading ("Console Buying Guide") + accordion: Item 1 ("PS5 vs Xbox — which should I buy?"), Item 2 ("Digital vs Disc — which edition?"), Item 3 ("Is the Nintendo Switch still worth it?"), Item 4 ("How much storage do I really need?"), Item 5 ("Is Game Pass / PS Plus worth the subscription?"), Item 6 ("Best console for kids?").
10. **layout-row (Customer Reviews)** → Heading ("Gamer Reviews") + carousel of review cards: rating + blockquote + caption (console purchased + verified badge).
11. **layout-row (Upcoming Releases)** → Heading ("Coming Soon") + columnsgrid (3 columns): upcoming consoles/limited editions with image, name, expected date, button ("Notify Me").
12. **layout-row (Newsletter)** → Left column: heading ("Gaming News & Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help Choosing?") + paragraph + button ("Talk to a Gaming Expert").
13. **layout-row (Footer)** → columnsgrid (4 columns): Store info, product categories, support links, contact + social.
