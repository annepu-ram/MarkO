# Eyewear & Sunglasses -- Product Pages

> Focus: Virtual try-on experience, face shape guidance, lens technology explanation, UV protection reassurance, and frame material/comfort details that reduce return anxiety for online eyewear purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Lenskart | lenskart.com/eyeglasses | AI face shape analyzer, 3D virtual try-on with live camera, frame size guide (lens width, bridge, temple), Blu lens technology explainer, "Try at Home" free trial program |
| Ray-Ban | ray-ban.com/usa | Customization configurator (frame color + lens type + engraving), face shape guide with illustration, polarized lens explainer with split-screen demo, heritage brand timeline |
| Titan Eye+ | titaneyeplus.com | Prescription readiness callout, lens coating comparison chart, store locator integration, EMI payment options, virtual consultation booking |
| John Jacobs | johnjacobseyewear.com | Lifestyle photography-driven PDP, acetate vs metal material guide, frame dimension overlay on product image, color swatch with instant image swap |
| Warby Parker | warbyparker.com | Home Try-On program (5 frames free), virtual try-on, quiz-based frame recommendation, progressive lens explainer, insurance/FSA acceptance callout |

**Patterns to incorporate:**
- Virtual try-on with live camera or uploaded photo
- Face shape quiz/guide matching face types to frame shapes
- Frame dimension diagram (lens width, bridge width, temple length) overlaid on product
- Lens type comparison: clear, blue light, photochromic, polarized, progressive
- UV protection certification badge and coating details
- Color/material swatches with instant image swap
- Prescription readiness indicator and lens customization flow
- Home Try-On or free return program prominence

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Eyewear Detail**

1. **titlebar**
   Brand logo, nav links (Eyeglasses, Sunglasses, Computer Glasses, Contact Lenses, Accessories), search icon, virtual try-on icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5 slides -- front view, side profile, folded, on-model front, on-model side angle). Right column: **eyebrow** ("Wayfarer Classic"), **heading** (product name "Maverick Square Acetate"), **rating** (4.6 stars, 1,120 reviews), **paragraph** ("Timeless square frame in premium Italian acetate"), **badge** ("Trending"), color selector **button** components (Matte Black / Tortoise / Crystal Blue / Wine Red), **heading** (price "$129"), **button** ("Select Lenses & Buy"), **button** ("Virtual Try-On" outline with camera icon), **paragraph** ("Free shipping. 14-day returns. 1-year warranty.").

3. **layout-row (Feature: Frame Material & Shape)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Frame"), **heading** ("Hand-Polished Italian Acetate"), **paragraph** (bio-based acetate from Mazzucchelli, Italy, hand-polished for a smooth finish, spring-loaded hinges for flex fit, hypoallergenic material safe for sensitive skin), **icon** + **caption** pairs: "Bio-Acetate", "Spring Hinges", "Hand-Polished", "Hypoallergenic". Right column: **image** (frame material close-up showing grain pattern and hinge detail).

4. **layout-row (Feature: Lens Type & Coating)** -> `comp_0_components_3`
   **eyebrow** ("Lens Technology"), **heading** ("Choose Your Perfect Lens"), **columnsgrid** (4 columns) each with **icon** + **heading** + **paragraph** + **heading** (price add-on): "Clear Anti-Glare -- Multi-coated for screen comfort, reduces reflections -- +$0", "Blu-Cut Digital -- Filters 98% blue light from screens, reduces eye strain -- +$29", "Photochromic Transition -- Darkens in sunlight, clears indoors automatically -- +$59", "Polarized Sun -- Eliminates glare for driving and outdoors -- +$49". **badge** ("Most Popular") on Blu-Cut option. **button** ("Compare Lens Types") opening detail.

5. **layout-row (Feature: UV Protection)** -> `comp_0_components_4`
   Left column: **image** (UV protection diagram showing rays being blocked by lens). Right column: **eyebrow** ("Protection"), **heading** ("100% UV400 Protection"), **paragraph** (blocks UVA and UVB rays up to 400nm wavelength, meets AS/NZS 1067 and ANSI Z80.3 standards, anti-scratch hardcoat included on all lenses), **badge** ("UV400 Certified"), **icon** + **caption** pairs: "UVA Blocked", "UVB Blocked", "Anti-Scratch", "Impact Resistant".

6. **layout-row (Feature: Face Shape Guide)** -> `comp_0_components_5`
   **eyebrow** ("Fit Guide"), **heading** ("Find Your Perfect Frame Shape"), **columnsgrid** (4 columns) each with **image** (face shape illustration) + **heading** (shape name) + **paragraph** (recommended frames): "Oval Face -- Lucky you! Most frames work. Try bold shapes.", "Round Face -- Angular frames add definition. Square and rectangular styles.", "Square Face -- Round and oval frames soften angles. Aviators work well.", "Heart Face -- Bottom-heavy frames balance a broader forehead. Cat-eye and round.". **badge** ("Great Match" on the face shape this frame suits). **button** ("Take the Face Shape Quiz").

7. **layout-row (Feature: Colors)** -> `comp_0_components_6`
   **heading** ("Available Colors"), **columnsgrid** (4 columns) each with **image** (frame in color on white background), **heading** (color name), **caption** (material finish: "Glossy" / "Matte" / "Translucent"), **button** ("Select"). **badge** ("New Color") on latest addition.

8. **layout-row (Feature: Weight & Comfort)** -> `comp_0_components_7`
   Left column: **eyebrow** ("Comfort"), **heading** ("Featherlight at 22 Grams"), **paragraph** (balanced weight distribution, adjustable nose pads (on metal frames), temple tips designed for all-day wear without pressure marks, flex hinges accommodate wider faces), **counter-up**: "22g Total Weight". Right column: **image** (close-up of nose pad and temple tip comfort features). **icon** + **caption** pairs: "All-Day Comfort", "Adjustable Nose Pads", "Flex Hinges", "No Pressure Points".

9. **layout-row (Feature: Prescription Ready)** -> `comp_0_components_8`
   Left column: **image** (prescription lens being fitted into frame). Right column: **eyebrow** ("Prescription"), **heading** ("Your Prescription. Our Precision."), **paragraph** (accepts single vision, bifocal, and progressive prescriptions, digital free-form lenses for edge-to-edge clarity, 1.67 high-index available for strong prescriptions at no extra charge), **accordion** with items: "How to Upload Your Prescription", "Understanding Your Prescription Numbers", "Progressive Lens Options", "Prism Lens Availability". **button** ("Upload Prescription").

10. **layout-row (Feature: Brand Story)** -> `comp_0_components_9`
    Full-width **image** (Italian factory or design studio). Overlay: **eyebrow** ("Heritage"), **heading** ("Designed in Milan. Worn Worldwide."), **paragraph** (brand story -- founding, design philosophy, sustainability commitment), **button** ("Our Story").

11. **layout-row (Feature: Price)** -> `comp_0_components_10`
    **heading** ("Pricing"), **columnsgrid** (3 columns) each with **heading** (configuration) + **heading** (price) + list of included items using **paragraph**: "Frame Only -- $129 -- Frame, case, cleaning cloth", "Frame + Clear Lenses -- $129 -- Anti-glare coating included", "Frame + Blu-Cut Lenses -- $158 -- Blue light filter included". **badge** ("Best Value") on Blu-Cut option. **button** ("Select & Customize") under each. **paragraph** ("All prices include anti-scratch coating, UV400 protection, and hard case").

12. **layout-row (Feature: Virtual Try-On)** -> `comp_0_components_11`
    **eyebrow** ("Try Before You Buy"), **heading** ("Virtual Try-On"), **image** (screenshot of virtual try-on interface with frame overlaid on face). **paragraph** ("Use your camera or upload a photo to see how this frame looks on you. Powered by AI face mapping."), **button** ("Launch Virtual Try-On"), **paragraph** ("Or try our Home Trial -- 5 frames delivered free, keep what you love").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Customer Reviews"), **rating** (4.6 overall), **progress-bar** rows for star distribution, **tabs** with 3 tabs: "Most Helpful" / "With Photos" / "Prescription Users". Each tab: **accordion** with reviewer name, rating, face shape mentioned, review text, optional **image** (selfie wearing glasses).

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("You Might Also Like"), **columnsgrid** (4 columns) each with **image** (frame on white), **heading** (product name), **caption** (material + shape), **heading** (price), **button** ("Quick View").

15. **layout-row (Footer)** -> `comp_0_components_14`
    **columnsgrid** (4 columns): Shop categories, Customer Care (returns, warranty, prescription help), About, Newsletter **textbox** + **button**. **br** divider. **paragraph** (copyright).

---

## Variant B -- Product Launch / Landing Page

**Page: New Collection Launch**

1. **titlebar**
   Minimal logo, "New Collection" link, shop CTA.

2. **layout-row (Hero -- Fashion Campaign)**
   **video-background** (cinematic campaign video -- diverse models in urban/nature settings wearing the new collection). Overlay: **eyebrow** ("Spring/Summer 2026"), **heading** ("See the World Differently"), **paragraph** ("The new [Collection Name] -- where heritage meets edge"), **button** ("Shop the Collection").

3. **layout-row (Collection Story)**
   Split layout. Left: **image** (designer inspiration moodboard). Right: **heading** ("Inspired by [Theme]"), **paragraph** (design narrative -- color inspiration, shape philosophy, cultural references), **blockquote** ("Eyewear should frame your personality, not hide it." -- Creative Director).

4. **layout-row (Hero Styles)**
   **heading** ("3 Signature Shapes"), **columnsgrid** (3 columns) each with **image** (frame on model), **heading** (style name), **paragraph** (who it's for and key feature), **badge** ("New"), **button** ("Shop This Style").

5. **layout-row (Lens Innovation)**
   Dark background. **heading** ("New: Adaptive Shield Lenses"), **image** (lens technology animation -- indoor vs outdoor transition), **paragraph** (new photochromic coating transitions in 15 seconds, 20% faster than previous gen), **counter-up**: "15sec Transition", "UV400 Protection", "Anti-Fog Coating".

6. **layout-row (Face Shape Matcher)**
   **heading** ("Which One Is You?"), interactive **tabs** with 4 tabs (face shapes). Each tab: **image** (face shape + recommended frame) + **paragraph** (style advice) + **button** ("Shop for Your Face").

7. **layout-row (Influencer Gallery)**
   **ticker** scrolling influencer/celebrity images wearing the collection with **image** + **caption** (name and frame style).

8. **layout-row (Virtual Try-On CTA)**
   **heading** ("Try Them On. Right Now."), **image** (virtual try-on demo screenshot), **button** ("Launch Virtual Try-On"), **paragraph** ("Or order 5 frames for free Home Trial").

9. **layout-row (Launch Offer)**
   **heading** ("Launch Special"), **paragraph** ("Free premium case + cleaning kit with every order this week"), **button** ("Shop Now"), **countdown** (offer expiry).

10. **layout-row (Footer)**
    Newsletter, social, store locator, legal.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Eyewear Catalog**

1. **titlebar**
   Brand logo, category nav (Eyeglasses, Sunglasses, Computer Glasses, Reading Glasses, Kids), search, virtual try-on, cart.

2. **layout-row (Category Hero)**
   **image** (lifestyle banner -- various frames styled). **heading** ("Eyeglasses"), **paragraph** ("Frames that fit your face, style, and prescription"), **eyebrow** ("320+ styles").

3. **layout-row (Smart Filter Bar)**
   **layout-row** with **button** filters: Shape (Round, Square, Aviator, Cat-Eye, Rectangle), Material (Acetate, Metal, Titanium, TR90), Color, Face Shape, Price Range, Gender. **badge** (active filter count).

4. **layout-row (Face Shape Recommender)**
   **heading** ("Not Sure? Let Us Help"), **columnsgrid** (2 columns). Left: **image** (face scanning illustration). Right: **heading** ("AI Frame Finder"), **paragraph** ("Upload a photo and our AI will recommend frames based on your face shape, size, and features"), **button** ("Find My Frame"). Alternatively: **button** ("Take the Quiz").

5. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating) each card: **image** (frame on white), **button** ("Try On" overlay icon), **heading** (product name), **caption** (material + shape), **rating** (stars + count), **heading** (price + "onwards" if lens options), color dots using small **button** components, **badge** ("Trending" / "New" / "Bestseller"), **button** ("Select Lenses").

6. **layout-row (Lens Guide)**
   **heading** ("Lens Type Guide"), **tabs** with 5 tabs: "Anti-Glare" / "Blue Light" / "Photochromic" / "Progressive" / "Polarized". Each tab: **image** (lens demo) + **heading** (lens name) + **paragraph** (who needs it, how it works) + **heading** (starting price) + **button** ("Shop with This Lens").

7. **layout-row (Material Comparison)**
   **heading** ("Frame Materials Compared"), comparison **columnsgrid** (5 columns). Header: Feature / Acetate / Metal / Titanium / TR90. Rows: Weight, Durability, Hypoallergenic, Flexibility, Price Range -- using **paragraph** and **icon** components.

8. **layout-row (Bestsellers)**
   **heading** ("Customer Favorites"), **carousel** (6 slides) with product cards, **badge** ("Most Tried On"), **rating**.

9. **layout-row (Prescription Process)**
   **heading** ("How It Works"), **columnsgrid** (4 columns) with numbered steps: **counter-up** (step number) + **heading** + **paragraph**: "1. Choose Frame", "2. Select Lens Type", "3. Upload Prescription", "4. Delivered in 5-7 Days".

10. **layout-row (Footer)**
    Shop categories, customer care, store locator, insurance/FSA info, newsletter, social, copyright.
