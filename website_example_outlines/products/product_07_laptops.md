# Laptops & Computers -- Product Pages

> Focus: Benchmark-driven spec storytelling where processor performance, display quality, battery life, and build quality each get dedicated trackable sections so brands can identify whether buyers are motivated by raw performance, portability, or value.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Apple MacBook Pro | apple.com/macbook-pro | Full-viewport feature scroll sections, chip benchmark animations, app-specific performance demos, configuration builder with price updater, trade-in estimator |
| Dell XPS | dell.com/xps | Detailed spec comparison tables, 360-degree product viewer, configuration customizer with real-time pricing, "Why XPS" feature callout cards, financing calculator |
| HP Spectre | hp.com/spectre | Lifestyle-first imagery, material close-ups (ceramic, gem-cut design), Intel Evo platform badges, sustainability section, bundle deals with peripherals |
| Lenovo ThinkPad | lenovo.com/thinkpad | Business-focused layout, MIL-STD durability certifications, keyboard quality section, docking/peripheral ecosystem, IT admin deployment features |
| ASUS ROG | rog.asus.com/laptops | Gaming-dark theme, RGB showcase, thermal system diagrams, gaming benchmark charts, refresh rate specs, esports partnership badges |

**Patterns to incorporate:**
- Configuration builder with RAM/storage/GPU options updating price in real-time
- Chip/processor benchmark visualizations with progress bars or animated counters
- Display quality section with color accuracy specs and content previews
- Battery life visualization with use-case breakdowns (video, browsing, coding)
- Build quality section with weight, thickness measurements, and material close-ups
- Port diagram with labeled connectivity options
- Performance comparison against previous generation or competitors
- Real-world workflow demonstrations (video editing, coding, gaming benchmarks)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Laptop Detail (e.g., "MacBook Pro 14-inch M5")**

1. **titlebar**
   Brand logo, nav links (Mac, MacBook Air, MacBook Pro, iMac, Compare, Accessories, Support), search icon, cart. **button** ("Buy").

2. **layout-row (Hero -- Product Reveal + Key Info)** -> `comp_0_components_1`
   Dark background. Center-aligned **image** (MacBook Pro open at angle, screen showing vivid content). Below: **eyebrow** ("MacBook Pro"), **heading** ("Mind-Blowing. Head-Turning."), **paragraph** ("The most advanced Mac laptop. Now with the M5 chip."), **heading** ("From $1,999"), **layout-row**: **button** ("Buy"), **button** ("Compare Models"). **caption** ("Available in Space Black and Silver").

3. **layout-row (Feature 1: Processor & Benchmark)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Performance"), **heading** ("M5 Chip"), **paragraph** ("12-core CPU, up to 40-core GPU, and 16-core Neural Engine. The fastest chip ever in a pro laptop."). **columnsgrid** (3 columns) with **counter-up** + **caption**: "12-Core" + "CPU", "40-Core" + "GPU", "16-Core" + "Neural Engine". **progress-bar** ("CPU vs M4" -- 25% faster, shown as 125%), **progress-bar** ("GPU vs M4" -- 30% faster, shown as 130%). Right column: **image** (M5 chip render with glow effect). **paragraph** ("Up to 2.5x faster than the fastest Intel-based MacBook Pro ever made").

4. **layout-row (Feature 2: Display)** -> `comp_0_components_3`
   Full-width **image** (display close-up showing vibrant HDR content, XDR brightness). Below: **eyebrow** ("Display"), **heading** ("Liquid Retina XDR"), **paragraph** ("14.2-inch Liquid Retina XDR display with ProMotion adaptive refresh up to 120Hz. 1,600 nits peak HDR brightness, 1,000 nits sustained, P3 wide color gamut."). **columnsgrid** (4 columns) with **counter-up** + **caption**: "14.2\"" + "Liquid Retina XDR", "120Hz" + "ProMotion", "1600 nits" + "Peak HDR", "1B+" + "Colors". **badge** ("True Tone"), **badge** ("ProMotion 120Hz").

5. **layout-row (Feature 3: RAM & Storage)** -> `comp_0_components_4`
   Left column: **eyebrow** ("Memory"), **heading** ("Unified Memory Architecture"), **paragraph** ("Start at 24GB and configure up to 128GB of unified memory. Ultra-fast SSD storage starting at 512GB, up to 8TB."). **tabs** with configuration tabs: "24GB / 512GB" tab: **heading** ("$1,999"), **paragraph** ("Ideal for coding, photo editing, everyday pro tasks"), "36GB / 1TB" tab: **heading** ("$2,499"), **paragraph** ("Great for video editing, 3D rendering, large projects"), "48GB / 2TB" tab: **heading** ("$2,999"), **paragraph** ("Best for professional workflows, multiple VMs, massive datasets"). Right column: **image** (speed comparison graphic). **counter-up** ("7.4") + **caption** ("GB/s SSD Read Speed").

6. **layout-row (Feature 4: GPU & Graphics)** -> `comp_0_components_5`
   **eyebrow** ("Graphics"), **heading** ("Pro-Level Graphics"), **paragraph** ("Up to 40-core GPU delivers performance for 3D rendering, video editing, machine learning training, and AAA gaming."). **columnsgrid** (3 columns) workflow demos: each with **image** (app screenshot) + **heading** + **paragraph**: "DaVinci Resolve" + "8K multicam editing, no proxy needed", "Blender" + "Complex 3D scenes render 2x faster", "Xcode" + "Build and test apps at unprecedented speed". **progress-bar** ("GPU Performance vs M4", 130%). **image** (game screenshot -- showing macOS gaming capabilities).

7. **layout-row (Feature 5: Battery Life)** -> `comp_0_components_6`
   Left column: **eyebrow** ("Battery"), **heading** ("Up to 24 Hours"), **counter-up** ("24") + **caption** ("Hours Battery Life"), **paragraph** ("The longest battery life ever in a Mac. Power-efficient M5 architecture delivers all-day performance without compromising speed."). Right column: **columnsgrid** (2 columns) use-case breakdown: **counter-up** ("24") + **caption** ("Hours Video Playback"), **counter-up** ("18") + **caption** ("Hours Wireless Browsing"). **progress-bar** ("vs M4 MacBook Pro", 115% -- 15% longer). **paragraph** ("MagSafe fast charging delivers 50% in just 30 minutes").

8. **layout-row (Feature 6: Build & Weight)** -> `comp_0_components_7`
   Left column: **image** (side profile showing thinness, material close-up). Right column: **eyebrow** ("Design"), **heading** ("Precision-Milled Aluminum"), **paragraph** ("Recycled aluminum unibody, just 15.5mm thin and 1.55 kg. Available in Space Black with anodization that resists fingerprints."). **columnsgrid** (3 columns) with **counter-up** + **caption**: "15.5" + "mm Thin", "1.55" + "kg Weight", "100%" + "Recycled Aluminum". **badge** ("Space Black"), **badge** ("Silver").

9. **layout-row (Feature 7: Keyboard & Trackpad)** -> `comp_0_components_8`
   **eyebrow** ("Input"), **heading** ("Magic Keyboard & Force Touch"), **paragraph** ("Full-size Magic Keyboard with Touch ID, ambient light sensor, and full-height function keys. Industry-leading Force Touch trackpad with haptic feedback."). **columnsgrid** (3 columns) with **icon** + **caption**: "Touch ID" + "Fingerprint unlock & Apple Pay", "Backlit Keys" + "Ambient light sensor adjusts automatically", "Force Touch" + "Largest trackpad in class". **image** (keyboard close-up with backlighting).

10. **layout-row (Feature 8: Ports & Connectivity)** -> `comp_0_components_9`
    **eyebrow** ("Connectivity"), **heading** ("All the Ports You Need"). **image** (side view diagram with labeled ports). **columnsgrid** (3 columns) left-side ports + right-side ports + wireless: Left: **paragraph** ("MagSafe 3, 2x Thunderbolt 5 (USB-C), 3.5mm headphone jack"), Right: **paragraph** ("HDMI 2.1, SDXC card slot, 1x Thunderbolt 5 (USB-C)"), Wireless: **paragraph** ("Wi-Fi 7, Bluetooth 5.3"). **caption** ("Thunderbolt 5: Up to 120Gbps data transfer, supports up to 3 external displays").

11. **layout-row (Feature 9: Price & Configurations)** -> `comp_0_components_10`
    **eyebrow** ("Configure"), **heading** ("Build Your MacBook Pro"). **tabs** per base configuration: "M5 -- $1,999", "M5 Pro -- $2,499", "M5 Max -- $3,499". Each tab: **heading** (config name + price), **paragraph** (specs summary), **columnsgrid** with key specs, **button** ("Buy"). **accordion** with items: "Upgrade Options" (RAM, storage, GPU), "Apple Trade In" ("Get $400-$1200 for your current Mac"), "Financing" ("$83.29/mo for 24 months at 0% APR"), "AppleCare+" ("$299 for 3 years of coverage"). **button** ("Compare All Mac Models").

12. **layout-row (Feature 10: Performance Comparison)** -> `comp_0_components_11`
    **heading** ("How It Compares"). **columnsgrid** (3 columns) comparison: "MacBook Pro M5" vs "MacBook Air M4" vs "Dell XPS 14". Column headers: **image** + **heading**. Comparison rows with **paragraph** per cell: CPU Benchmark, GPU Benchmark, RAM Options, Battery Life, Weight, Price. **caption** ("Benchmarks from Geekbench 6, tested under standard conditions").

13. **layout-row (Reviews & Press)** -> `comp_0_components_12`
    **heading** ("What the Experts Say"). **columnsgrid** (3 columns) each with **blockquote** (review excerpt), **rating** (score), **caption** (publication name): "The Verge -- 9.5/10", "Tom's Guide -- 4.5/5", "MKBHD -- 'Best laptop ever made'". **button** ("Read All Reviews").

14. **layout-row (Accessories)** -> `comp_0_components_13`
    **heading** ("Accessories"). **columnsgrid** (4 columns): **image** + **heading** + **caption** (price) + **button** ("Add"): "96W USB-C Adapter", "Magic Mouse", "Pro Display XDR", "Thunderbolt 5 Dock".

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop & Learn, Services, Account, About Apple. **br** (divider). **caption** (copyright, legal).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused for a new laptop generation or chip launch

**Page: Chip Launch (e.g., "Introducing M5 -- The Next Generation")**

1. **titlebar** -- Brand logo, minimal nav (M5, Performance, Products, Order), "Order Now" button.

2. **layout-row (Hero)** -- Dark background. **image** (chip render with energy waves). **eyebrow** ("Apple Silicon"), **heading** ("M5"), **paragraph** ("The most powerful chip we've ever made."), **button** ("Explore M5"), **button** ("Order MacBook Pro").

3. **layout-row (Headline Stats)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "12-Core" + "CPU", "40-Core" + "GPU", "25%" + "Faster", "30%" + "Less Power".

4. **layout-row (Architecture Story)** -- **heading** ("Second-Generation 3nm"), **image** (transistor-level visualization), **paragraph** (process technology narrative), **counter-up** ("25B") + **caption** ("Transistors").

5. **layout-row (Real-World Performance)** -- **heading** ("See It in Action"), **carousel** (workflow demos: video editing, 3D rendering, ML training, gaming -- each slide with **image** + **heading** + **paragraph**).

6. **layout-row (Efficiency)** -- **heading** ("Performance Per Watt"), **progress-bar** ("vs Intel i9", 200%), **progress-bar** ("vs AMD Ryzen 9", 170%), **paragraph** ("Best performance per watt of any laptop chip").

7. **layout-row (Products with M5)** -- **heading** ("Available In"), **columnsgrid** (3 columns): MacBook Pro 14", MacBook Pro 16", Mac Studio. Each: **image** + **heading** + **caption** (starting price) + **button** ("Learn More").

8. **layout-row (Order CTA)** -- **heading** ("Order Now"), **paragraph** ("Starting at $1,999"), **button** ("Buy MacBook Pro"), **caption** ("Delivers in 1-2 weeks").

9. **layout-row (Footer)** -- Minimal footer.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-laptop browsing and comparison

**Page: Laptop Lineup (e.g., "Dell Laptops")**

1. **titlebar** -- Brand logo, nav (XPS, Inspiron, Latitude, Gaming, Workstations, Deals), search, cart.

2. **layout-row (Hero)** -- **heading** ("Find Your Perfect Dell Laptop"), **paragraph** ("From ultraportable to powerhouse"), **layout-row** filters: **dropdown** (Series), **dropdown** (Use Case: Business, Creative, Gaming, Student), **dropdown** (Screen Size), **dropdown** (Price), **button** ("Filter").

3. **layout-row (Premium: XPS)** -- **eyebrow** ("Premium"), **heading** ("XPS Series"). **columnsgrid** (3 columns) cards: **image** (laptop), **heading** (model), **caption** (key spec line), **heading** (price), **badge** ("Editors' Choice"), **rating**, **button** ("Configure & Buy").

4. **layout-row (Mainstream: Inspiron)** -- Same card pattern for Inspiron line.

5. **layout-row (Gaming: G Series)** -- Same card pattern for gaming laptops with additional **badge** ("RTX 4080") style gaming specs.

6. **layout-row (Comparison Tool)** -- **heading** ("Compare Laptops"). **columnsgrid** (3 columns) with **dropdown** (select laptop) each. Rows: Processor, RAM, Storage, Display, GPU, Battery, Weight, Price.

7. **layout-row (By Use Case)** -- **tabs** ("Students", "Business", "Creative", "Gaming") each with curated recommendations + **paragraph** (what specs matter for each use case).

8. **layout-row (Deals)** -- **heading** ("Current Offers"), **columnsgrid** (3 columns) deal cards with **badge** ("Save $200"), **image**, **heading**, original price with strikethrough, sale price, **button** ("Shop Deal").

9. **layout-row (Trade-In)** -- **heading** ("Trade In Your Old Laptop"), **paragraph** ("Get up to $500 instant credit"), **form** with **dropdown** (brand), **dropdown** (model), **button** ("Get Estimate").

10. **layout-row (Footer)** -- Full footer with product links, support, financing info, social.
