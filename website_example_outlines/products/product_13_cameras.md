# Cameras & Photography -- Product Pages

> Focus: Sensor and image quality demonstration, autofocus technology visualization, video capability showcase, and sample photography that lets the camera's output speak for itself.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Canon | usa.canon.com/cameras/eos-r-system | Feature-per-scroll with full-bleed sample images, sensor diagram, Dual Pixel AF point overlay animation, 4K video reel, kit lens bundle options |
| Nikon | nikon.com/en/products/mirrorless-cameras | ISO comparison slider (low light vs bright), Z-mount explainer, EXPEED processor diagram, ergonomic grip close-up shots |
| Sony Alpha | sony.com/en/interchangeable-lens-cameras | Real-time Eye AF demo video, burst shooting speed counter-up, weather sealing callout, lens ecosystem cross-sell |
| GoPro | gopro.com | Hero product page with action video montage, stabilization before/after, waterproof depth rating, subscription bundle pricing |
| Fujifilm | fujifilm.com/us/en/digital-cameras/x | Film simulation mode gallery, retro design close-ups, hybrid viewfinder explainer, color science sample images |

**Patterns to incorporate:**
- Full-bleed sample photographs shot on the camera as hero backgrounds
- Sensor diagram with megapixel count and physical size comparison
- Autofocus point overlay visualization on sample image
- ISO comparison slider showing low-light performance
- Burst mode speed counter-up with rapid-fire sequence strip
- Video capability reel shot entirely on the camera
- Body/grip ergonomic close-ups with weather sealing callouts
- Lens ecosystem showcase with compatible mount options
- Kit option selector (body only, single lens kit, dual lens kit)

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Camera Detail**

1. **titlebar**
   Brand logo, nav links (Mirrorless, DSLR, Compact, Lenses, Accessories, Learn), search icon, support icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 slides -- front with lens, rear LCD, top dial layout, grip close-up, body without lens showing sensor, in-hand shooting). Right column: **eyebrow** ("Mirrorless Full-Frame"), **heading** (product name "EOS R6 Mark III"), **rating** (4.8 stars, 920 reviews), **paragraph** ("40MP full-frame sensor. 40fps burst. 8K internal video."), **badge** ("New Release"), **heading** (price "$2,499 Body Only"), **button** ("Add to Cart"), **button** ("Find a Dealer" outline), **paragraph** ("Free expedited shipping. 30-day trial.").

3. **layout-row (Feature: Sensor & Resolution)** -> `comp_0_components_2`
   Full-bleed **image** background (stunning landscape photo shot on this camera, credited). Overlay: **eyebrow** ("Image Quality"), **heading** ("40.2 Megapixel Full-Frame CMOS"), **paragraph** (back-illuminated sensor with expanded dynamic range, DIGIC X processor for rich detail and accurate color, ISO 100-102400 expandable), **counter-up** components: "40.2MP Resolution", "15 Stops Dynamic Range", "ISO 102,400".

4. **layout-row (Feature: Lens Mount)** -> `comp_0_components_3`
   Left column: **image** (lens mount close-up showing RF mount with short flange distance diagram). Right column: **eyebrow** ("Lens System"), **heading** ("RF Mount -- Shorter Flange, Sharper Images"), **paragraph** (20mm flange distance allows faster, sharper lens designs, fully compatible with 30+ RF lenses, EF/EF-S adapter available for legacy glass), **columnsgrid** (3 columns) with **image** + **caption**: "RF 24-105mm f/4L", "RF 50mm f/1.2L", "RF 70-200mm f/2.8L". **button** ("Explore All RF Lenses").

5. **layout-row (Feature: Autofocus)** -> `comp_0_components_4`
   **eyebrow** ("Autofocus"), **heading** ("1,053-Point Dual Pixel AF II"), **paragraph** (covers 100% of the sensor, AI-powered subject detection for people, animals, vehicles, aircraft, real-time Eye AF tracks even when partially obscured), **image** (sample photo with AF point overlay showing eye detection on a moving subject), **columnsgrid** (4 columns) with **icon** + **caption**: "People Detection", "Animal Eye AF", "Vehicle Tracking", "Bird in Flight". **counter-up** components: "1,053 AF Points", "100% Coverage", "-6.5 EV Sensitivity".

6. **layout-row (Feature: Video Capability)** -> `comp_0_components_5`
   Left column: **video** (sample 4K footage shot on this camera -- cinematic short film). Right column: **eyebrow** ("Video"), **heading** ("8K RAW Internal. Cinema in Your Hands."), **paragraph** (8K 30p RAW, 4K 120p slow motion, Canon Log 3 with 16+ stops, HDR PQ output, no recording limit), **columnsgrid** (2 columns) with **counter-up** + **caption**: "8K RAW", "4K 120fps", "Canon Log 3", "No Record Limit". **badge** ("Cinema EOS Quality").

7. **layout-row (Feature: ISO & Low Light)** -> `comp_0_components_6`
   Dark background. **heading** ("See in the Dark"), **paragraph** (native ISO 100-102400, expanded to 204800, noise reduction preserves detail at high ISO, back-illuminated sensor gathers more light), **columnsgrid** (2 columns) with **image** + **caption**: side-by-side comparison "ISO 100 -- Daylight" and "ISO 12800 -- Available Light" showing clean low-light performance. **progress-bar** (ISO range visualization from 100 to 102400).

8. **layout-row (Feature: Body & Weight)** -> `comp_0_components_7`
   Left column: **eyebrow** ("Design"), **heading** ("Magnesium Alloy. Weather-Sealed. 680g."), **paragraph** (dust and moisture resistant sealing at every joint, deep ergonomic grip for large lenses, vari-angle touchscreen LCD, top info display), **icon** + **caption** pairs: "Weather Sealed", "Magnesium Body", "Vari-Angle LCD", "Top Info Display". Right column: **image** (camera in rain/dust conditions demonstrating weather sealing). **counter-up**: "680g Body Only".

9. **layout-row (Feature: Battery Life)** -> `comp_0_components_8`
   Left column: **image** (battery and USB-C charging). Right column: **eyebrow** ("Battery"), **heading** ("700 Shots Per Charge"), **paragraph** (LP-E6NH battery, USB-C in-body charging, USB Power Delivery for continuous power while shooting, battery grip option doubles capacity), **counter-up** components: "700 Shots", "USB-C Charging", "2x with Grip". **progress-bar** (battery comparison vs previous model: 550 vs 700 shots).

10. **layout-row (Feature: Connectivity)** -> `comp_0_components_9`
    **heading** ("Stay Connected"), **columnsgrid** (4 columns) each with **icon** + **heading** + **caption**: "Wi-Fi 6E -- Fastest wireless transfer", "Bluetooth 5.0 -- Always-on smartphone connection", "USB-C 3.2 -- 10Gbps wired transfer", "FTP -- Direct studio tethering". **paragraph** ("Transfer images to your phone in seconds with the Camera Connect app").

11. **layout-row (Feature: Price & Kit Options)** -> `comp_0_components_10`
    **heading** ("Choose Your Kit"), **columnsgrid** (3 columns) each with **image** (kit configuration), **heading** (kit name), **heading** (price), list of included items using **paragraph**, **badge** ("Best Value" on kit), **button** ("Select"): "Body Only -- $2,499", "With RF 24-105mm f/4-7.1 -- $2,899", "With RF 24-105mm f/4L -- $3,599".

12. **layout-row (Feature: Sample Photos)** -> `comp_0_components_11`
    **eyebrow** ("Gallery"), **heading** ("Shot on EOS R6 Mark III"), **carousel** (8 slides) each with full-resolution **image** (various genres -- landscape, portrait, wildlife, street, macro, sports, astro, wedding), **caption** (settings used: "RF 50mm f/1.2 | 1/500s | ISO 400 | f/1.2"). **button** ("Download Full-Res Samples").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Photographer Reviews"), **rating** (4.8 overall), **progress-bar** rows for star distribution, **tabs** with 3 tabs: "Professional" / "Enthusiast" / "Video Creator". Each tab: **accordion** with reviewer name, rating, use case, review text.

14. **layout-row (Accessories)** -> `comp_0_components_13`
    **heading** ("Essential Accessories"), **columnsgrid** (4 columns) each with **image**, **heading** (name), **heading** (price), **button** ("Add"): Battery Grip, Extra Battery, Memory Card (CFexpress), Camera Bag.

15. **layout-row (Related Products)** -> `comp_0_components_14`
    **heading** ("Explore the Lineup"), **columnsgrid** (3 columns) with other camera bodies: **image**, **heading** (model), **caption** (key differentiator), **heading** (price), **button** ("Compare").

16. **layout-row (Footer)** -> `comp_0_components_15`
    **columnsgrid** (4 columns): Products, Support, Learn (tutorials, workshops), Newsletter **textbox** + **button**. **br** divider. **paragraph** (copyright).

---

## Variant B -- Product Launch / Landing Page

**Page: New Camera System Launch**

1. **titlebar**
   Minimal logo, "New" badge, pre-order CTA.

2. **layout-row (Hero -- Cinematic Reveal)**
   **video-background** (film shot entirely on the new camera -- fast action, low light, slow motion montage). Overlay: **heading** ("This Was Shot on [Camera Name]"), **paragraph** ("Every frame. Every scene. No cinema rig."), **button** ("Pre-Order Now"), **countdown** (shipping date).

3. **layout-row (The Sensor)**
   Full-bleed sample **image** (landscape with extreme detail). **eyebrow** ("Next-Gen Sensor"), **heading** ("50 Megapixels. Zero Compromise."), **paragraph** (new BSI sensor architecture narrative), **counter-up** components: "50MP", "16 Stops", "ISO 204,800".

4. **layout-row (Autofocus Revolution)**
   **heading** ("AI Sees What You See"), **video** (real-time AF tracking demo -- bird in flight, athlete, dancer), **paragraph** (deep learning AF with new subject categories), **columnsgrid** (5 columns) with **icon** + **caption** for each detection type.

5. **layout-row (Video Capabilities)**
   Dark background. **heading** ("8K. 120fps. RAW. Internal."), **video** (cinematic reel), **counter-up** stats, **paragraph** (technical narrative about codec options and color science).

6. **layout-row (Design Evolution)**
   **carousel** (design process: sketches, clay models, prototypes, final). **blockquote** ("We redesigned every surface for the way photographers actually hold cameras." -- Product Manager).

7. **layout-row (Pro Testimonials)**
   **columnsgrid** (3 columns) each with **image** (photographer portrait), **heading** (name), **caption** (specialty), **blockquote** (endorsement), sample **image** (their shot on the camera).

8. **layout-row (Kit Pre-Order)**
   **heading** ("Pre-Order Configurations"), **columnsgrid** (3 columns) with kit options, prices, **badge** ("Early Bird Bonus: Free Memory Card"), **button** ("Pre-Order").

9. **layout-row (Sample Gallery)**
   Masonry-style **columnsgrid** (3 columns, varying heights) of sample images shot on camera with EXIF data captions.

10. **layout-row (Footer)**
    Newsletter, social, support links.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Camera Catalog**

1. **titlebar**
   Brand logo, category nav (Mirrorless, DSLR, Compact, Cinema, Action, Instant), search, cart.

2. **layout-row (Category Hero)**
   **image** (collage of different cameras). **heading** ("Find Your Camera"), **paragraph** ("From first camera to professional tool"), **eyebrow** ("42 models").

3. **layout-row (Skill Level Selector)**
   **heading** ("What's Your Level?"), **columnsgrid** (4 columns) each with **icon** + **heading** + **caption** + **button** ("Shop"): "Beginner -- Easy auto modes, lightweight, affordable", "Enthusiast -- Manual control, interchangeable lenses", "Professional -- Maximum performance, weather-sealed", "Filmmaker -- Cinema-grade video, RAW output".

4. **layout-row (Side-by-Side Comparison)**
   **heading** ("Compare Models"), **columnsgrid** (4 columns). Header: Spec / Entry / Mid / Pro. Rows for Sensor, Resolution, AF Points, Burst Speed, Video, Weight, Price using **paragraph** + **icon** components. **badge** ("Best Value") on recommended. **button** ("Select") under each.

5. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating) each card: **image**, **badge** ("Mirrorless" / "DSLR" / "Compact"), **heading** (model), **rating**, **heading** (price), key specs using **caption** (MP, AF points, fps), **button** ("View Details") + **button** ("Compare").

6. **layout-row (Lens Compatibility Guide)**
   **heading** ("Lens Compatibility"), **tabs** with 3 tabs: "RF Mount" / "EF Mount" / "Third-Party". Each tab: **columnsgrid** grid of compatible lenses with **image** + **caption** (focal length and aperture) + **heading** (price).

7. **layout-row (Buying Guide)**
   **heading** ("Camera Buying Guide"), **accordion** with sections: "Sensor Size Explained", "Megapixels -- How Many Do You Need?", "Autofocus Types", "Video Specs Decoded", "Weather Sealing Guide". Each with educational **paragraph** + **image** (diagram).

8. **layout-row (Bestsellers)**
   **heading** ("Most Popular"), **carousel** (6 slides) with product cards, **badge** ("Top Seller" / "Award Winner").

9. **layout-row (Footer)**
    Product categories, support, learn resources, newsletter, social, copyright.
