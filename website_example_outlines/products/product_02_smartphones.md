# Smartphones & Mobiles -- Product Pages

> Focus: Spec-driven storytelling where each hardware feature (display, camera, processor, battery) gets its own immersive scroll section with animated benchmarks, sample photos, and variant/color selectors that let brands track which feature converts to purchase.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Apple iPhone 16 Pro | apple.com/iphone-16-pro | Dark cinematic hero, each feature = full-viewport scroll section with parallax product shots, animated chip benchmarks, sample photo gallery, sticky "Buy" nav |
| Samsung Galaxy S25 Ultra | samsung.com/galaxy-s25-ultra | Feature sections with bold typography + device mockup, AI-powered feature demos, camera comparison slider, trade-in value calculator |
| OnePlus 13 | oneplus.com/13 | Specs-forward dark design, scroll-triggered counter-up animations for benchmarks, camera sample grid, community reviews section |
| Google Pixel 9 Pro | store.google.com/pixel-9-pro | Clean white design, AI photography focus with before/after samples, feature cards with iconography, color picker with live device preview |
| Nothing Phone 3 | nothing.tech/phone-3 | Unique transparent design hero, glyph interface showcase, minimalist spec sections, community-driven testimonials |

**Patterns to incorporate:**
- Full-viewport hero with device floating on dark/gradient background + tagline
- Each major spec (display, camera, chip, battery) is its own immersive scroll section
- Camera section with sample photo grid and zoom/night-mode comparison
- Animated benchmark scores (Geekbench, AnTuTu) using counter-up
- Color selector that swaps device image in real-time
- Storage/RAM variant selector tied to price display
- Trade-in or EMI calculator widget
- Sticky buy bar with price and CTA that persists on scroll

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Smartphone Detail (e.g., iPhone 16 Pro)**

1. **titlebar**
   Brand logo, nav links (Overview, Camera, Performance, Battery, Specs, Buy), hamburger for mobile, "Buy" button aligned right.

2. **layout-row (Hero -- Product Reveal + Key Info)** -> `comp_0_components_1`
   Dark background. Center-aligned **image** (device floating with dramatic lighting, front and back). Below: **eyebrow** ("iPhone 16 Pro"), **heading** ("Built for Apple Intelligence"), **paragraph** (tagline: "The most advanced iPhone ever."), **heading** (price: "From $999"), **layout-row** with **button** ("Buy") + **button** ("Compare Models"). **caption** ("Available in 4 finishes").

3. **layout-row (Feature 1: Display)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Display"), **heading** ("Brilliant in Every Light"), **paragraph** (Super Retina XDR, ProMotion 120Hz, Always-On, 2000 nits peak brightness), **columnsgrid** (2 columns) with **counter-up** + **caption**: "6.3-inch" + "Super Retina XDR", "2000 nits" + "Peak Brightness". **badge** ("ProMotion 120Hz"). Right column: **image** (display close-up showing vivid content, edge-to-edge).

4. **layout-row (Feature 2: Camera System)** -> `comp_0_components_3`
   Left column: **image** (camera module close-up). Right column: **eyebrow** ("Camera"), **heading** ("Capture Every Detail"), **paragraph** (48MP Fusion camera, 5x Telephoto, Ultra Wide, Photographic Styles), **columnsgrid** (3 columns) with **counter-up** + **caption**: "48 MP" + "Fusion Camera", "5x" + "Optical Zoom", "4K120" + "Dolby Vision". Below: **heading** ("Shot on iPhone"), **carousel** (6-8 sample photos -- portrait, landscape, night, macro, zoom, action). **tabs** with tabs for "Photo", "Night Mode", "Portrait", "Video" each showing sample **image** + **paragraph** description.

5. **layout-row (Feature 3: Processor & Performance)** -> `comp_0_components_4`
   Dark background. **eyebrow** ("Performance"), **heading** ("A18 Pro Chip"), **paragraph** (fastest chip ever in a smartphone, 6-core CPU, 6-core GPU, 16-core Neural Engine). **columnsgrid** (3 columns) with animated **counter-up** + **caption**: "17%" + "Faster CPU", "20%" + "Faster GPU", "16-Core" + "Neural Engine". **progress-bar** (benchmark comparison vs previous gen, 85%). **image** (chip render with glow effect).

6. **layout-row (Feature 4: Battery & Charging)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Battery"), **heading** ("Power That Lasts All Day"), **paragraph** (all-day battery life, MagSafe wireless charging, USB-C fast charging). **columnsgrid** (2 columns): **counter-up** ("33") + **caption** ("Hours Video Playback"), **counter-up** ("50%") + **caption** ("in 30 Min Fast Charge"). **progress-bar** (battery life bar, 95%). Right column: **image** (phone with battery indicator or charging accessories).

7. **layout-row (Feature 5: Design & Build)** -> `comp_0_components_6`
   Full-width **image** (device side profile, titanium finish close-up). Below: **eyebrow** ("Design"), **heading** ("Forged in Titanium"), **paragraph** (Grade 5 titanium, Ceramic Shield front, surgical-grade stainless steel), **columnsgrid** (3 columns) with **icon** + **caption**: "Titanium Frame", "Ceramic Shield", "IP68 Water Resistance". **badge** ("Thinnest Borders Ever").

8. **layout-row (Feature 6: Storage Variants)** -> `comp_0_components_7`
   **eyebrow** ("Storage"), **heading** ("Choose Your Capacity"). **tabs** with tab per storage option (128GB, 256GB, 512GB, 1TB), each showing: **heading** (capacity), **paragraph** (use case description: "Perfect for..." ), **heading** (price), **button** ("Select"). **caption** ("All models include 8GB RAM").

9. **layout-row (Feature 7: OS & Software)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Intelligence"), **heading** ("Apple Intelligence"), **paragraph** (AI-powered writing tools, Genmoji, Image Playground, Siri upgrades). **columnsgrid** (3 columns) each with **image** (feature screenshot) + **caption** (feature name). Right column: **image** (iOS interface showcase). **badge** ("iOS 18").

10. **layout-row (Feature 8: 5G & Connectivity)** -> `comp_0_components_9`
    **eyebrow** ("Connectivity"), **heading** ("Fast Everywhere"). **columnsgrid** (4 columns) each with **icon** + **heading** + **caption**: "5G" + "Sub-6 & mmWave", "Wi-Fi 7" + "Fastest Wi-Fi", "USB-C 3" + "10Gbps Transfer", "UWB" + "Precision Finding". **paragraph** (satellite SOS, Crash Detection, emergency features).

11. **layout-row (Feature 9: Price & Offers)** -> `comp_0_components_10`
    **eyebrow** ("Pricing"), **heading** ("Choose Your iPhone 16 Pro"). **columnsgrid** (4 columns) for each storage variant: **heading** (storage), **heading** (price), **paragraph** (monthly installment option), **button** ("Buy"). Below: **accordion** with items: "Trade-In Values", "Carrier Deals", "AppleCare+ Options", "Student Discount". **caption** ("*Prices include applicable taxes").

12. **layout-row (Feature 10: Color Options)** -> `comp_0_components_11`
    **heading** ("Find Your Finish"). **carousel** (device in each color: Desert Titanium, Natural Titanium, White Titanium, Black Titanium). Below: **columnsgrid** (4 color swatch tiles) each with **image** (color swatch circle) + **caption** (color name). **paragraph** ("All finishes feature a premium titanium frame").

13. **layout-row (Specs Table)** -> `comp_0_components_12`
    **heading** ("Technical Specifications"). **accordion** with sections: "Display", "Camera", "Chip", "Battery", "Connectivity", "Dimensions & Weight", "In the Box". Each section contains **paragraph** elements with spec details.

14. **layout-row (Reviews & Ratings)** -> `comp_0_components_13`
    **eyebrow** ("Reviews"), **heading** ("What People Are Saying"). **rating** (4.7 stars, 28,000+ ratings). **columnsgrid** (3 columns) with **blockquote** (expert review quote), **caption** (publication name), **rating** (individual score). **button** ("Read All Reviews").

15. **layout-row (Accessories)** -> `comp_0_components_14`
    **heading** ("Complete Your Setup"). **columnsgrid** (4 columns) each with **image** (accessory), **heading** (name), **caption** (price), **button** ("Add"). Items: MagSafe Charger, Clear Case, AirPods Pro, Apple Watch.

16. **layout-row (Footer)**
    **columnsgrid** (4 columns): Shop & Learn, Services, Account, Quick Links. **br** (divider). **caption** (legal text, copyright).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new smartphone launch

**Page: Smartphone Launch (e.g., "OnePlus 13 -- Never Settle")**

1. **titlebar** -- Brand logo, minimal nav (Discover, Specs, Buy), "Notify Me" button.

2. **layout-row (Hero)** -- Dark gradient background. **image** (phone reveal shot with light trails). **eyebrow** ("The New Flagship"), **heading** ("OnePlus 13"), **paragraph** ("Redefining Speed."), **countdown** (to sale date), **button** ("Get Notified").

3. **layout-row (Headline Stats)** -- **columnsgrid** (4 columns) with **counter-up** + **caption**: "Snapdragon 8 Elite", "6000 mAh", "50 MP Hasselblad", "100W SUPERVOOC".

4. **layout-row (Camera Story)** -- **heading** ("Hasselblad. In Your Pocket."), full-width **carousel** (5 stunning sample photos), **caption** ("Shot on OnePlus 13").

5. **layout-row (Performance)** -- **heading** ("Raw Power"), **paragraph** (Snapdragon narrative), **progress-bar** (benchmark vs competition), **image** (chip graphic).

6. **layout-row (Display)** -- Full-bleed **image** (display showcase), **heading** ("2K 120Hz LTPO"), **counter-up** ("4500 nits") + **caption** ("Peak Brightness").

7. **layout-row (Design Reveal)** -- **heading** ("Crafted to Perfection"), **ticker** (rotating device angles in different colors).

8. **layout-row (Early Bird Offer)** -- **heading** ("Launch Offer"), **paragraph** ("Rs 5,000 off + free earbuds"), **button** ("Buy Now"), **badge** ("Limited Time").

9. **layout-row (Footer)** -- Minimal footer, social links, legal.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-phone browsing layout for a brand's lineup or retailer

**Page: Smartphone Lineup (e.g., "Samsung Galaxy Phones")**

1. **titlebar** -- Brand logo, nav (Galaxy S, Galaxy A, Galaxy Z, Galaxy M, Accessories), search bar, cart.

2. **layout-row (Hero)** -- **heading** ("Find Your Galaxy"), **paragraph** ("From flagship to everyday"), **layout-row** filters: **dropdown** (Series), **dropdown** (Price Range), **dropdown** (Camera MP), **button** ("Filter").

3. **layout-row (Flagship Series)** -- **eyebrow** ("Galaxy S Series"), **heading** ("Ultimate Performance"). **columnsgrid** (3 columns) each card: **image** (phone), **badge** ("Flagship"/"AI-Powered"), **heading** (model name), **caption** (key spec line), **rating** (stars), **heading** (price), **button** ("Buy Now"), **button** ("Learn More").

4. **layout-row (Mid-Range Series)** -- Same card grid for Galaxy A series phones.

5. **layout-row (Foldable Series)** -- Same card grid for Galaxy Z Fold and Flip models.

6. **layout-row (Comparison Tool)** -- **heading** ("Compare Galaxy Phones"). **columnsgrid** (3 columns) with **dropdown** (select phone) header each. Comparison rows: **paragraph** (spec label) + values per column. Specs: Display, Camera, Processor, Battery, RAM, Storage, Price.

7. **layout-row (Quick Pick)** -- **tabs** (By Need: "Best Camera", "Best Battery", "Best Value", "Best Performance") each showing curated **columnsgrid** of top picks.

8. **layout-row (Trade-In)** -- **heading** ("Trade In & Save"), **paragraph** ("Get up to $800 off"), **form** with **dropdown** (current phone brand), **dropdown** (model), **button** ("Check Value").

9. **layout-row (Footer)** -- Full footer with product links, support, social, legal.
