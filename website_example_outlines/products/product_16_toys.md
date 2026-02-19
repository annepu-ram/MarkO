# Toys & Games -- Product Pages

> Focus: Age appropriateness, educational value demonstration, safety certifications, play experience visualization, and parent trust signals that satisfy both the child's excitement and the parent's due diligence.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| LEGO | lego.com/en-us/themes | Age filter prominently displayed, piece count as key stat, step count and build difficulty indicator, "Instructions Plus" app integration, community gallery of completed builds |
| Hamleys | hamleys.com | Age-based category navigation, in-store play demonstration videos, gift finder tool, trending toys carousel, "Hamleys Loves" staff pick badges |
| Fisher-Price | fisher-price.mattel.com | Developmental milestone mapping per toy, age-stage slider, safety-first messaging with certification logos, "Play Lab Tested" trust badge |
| Funskool | funskool.com | Player count and play duration on card, educational outcome tags (STEM, creativity, motor skills), family game night positioning, combo deal bundles |
| Melissa & Doug | melissaanddoug.com | Screen-free play messaging, developmental skill checklist, real wood material callout, age-graded buying guide, gift registry |

**Patterns to incorporate:**
- Age range prominently displayed with developmental milestone connection
- Educational value tags (STEM, creativity, motor skills, social skills)
- Safety certification badges (EN71, ASTM F963, CE mark, BIS, choking hazard warning)
- Play demonstration video showing children actually playing
- Player count, play duration, and setup time as quick specs
- "What's in the Box" flat-lay with piece count
- Parent review section emphasizing durability and replay value
- Gift finder tool by age, interest, and budget

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Toy/Game Detail**

1. **titlebar**
   Store/brand logo, nav links (Age Groups, Categories, Brands, Bestsellers, Gift Finder, Sale), search icon, wishlist icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5 slides -- product box front, product unboxed, child playing with it, detail close-up, all pieces laid out). Right column: **eyebrow** ("Ages 6-12 | STEM"), **heading** (product name "MechaBot Builder 500"), **rating** (4.7 stars, 890 reviews), **paragraph** ("Build and program your own robot with 500+ pieces and a free coding app"), **badge** ("Award Winner 2026"), **badge** ("STEM Certified"), **heading** (price "$49.99"), **button** ("Add to Cart"), **button** ("Add to Gift Registry" outline), **paragraph** ("In stock. Gift wrap available.").

3. **layout-row (Feature: Age Range)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Recommended Age"), **heading** ("Designed for Ages 6-12"), **paragraph** (complexity calibrated for developing fine motor skills and logical thinking, younger children can build with parent supervision, advanced builds challenge older kids), **progress-bar** (age range visualization: 3-5 Too Young | 6-8 Core | 9-12 Advanced | 13+ Nostalgic). Right column: **image** (children of target age group playing together). **caption** ("Choking hazard -- small parts. Not suitable for children under 3 years.").

4. **layout-row (Feature: Educational Value)** -> `comp_0_components_3`
   **eyebrow** ("Learning Through Play"), **heading** ("Skills Your Child Will Develop"), **columnsgrid** (4 columns) each with **icon** + **heading** + **paragraph**: "Engineering -- Follow instructions to build 10+ robot configurations", "Coding -- App-based block coding teaches programming logic", "Problem Solving -- Troubleshoot builds and debug code", "Creativity -- Free-build mode encourages original designs". **badge** ("Play Lab Tested") + **badge** ("STEM.org Authenticated").

5. **layout-row (Feature: Material & Safety)** -> `comp_0_components_4`
   Left column: **image** (close-up of pieces showing material quality, rounded edges). Right column: **eyebrow** ("Safety First"), **heading** ("Non-Toxic. Tested. Certified."), **paragraph** (ABS plastic, lead-free paint, rounded edges on all pieces, rigorously tested to exceed EN71, ASTM F963, and CPSIA standards), **columnsgrid** (3 columns) with **icon** + **caption**: "EN71 Certified", "ASTM F963 Compliant", "BPA/Lead Free". **paragraph** ("Every batch independently tested by SGS laboratories"). **badge** ("CE Marked").

6. **layout-row (Feature: Battery/Power)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Power"), **heading** ("Rechargeable via USB-C"), **paragraph** (built-in rechargeable battery lasts 4 hours of active play, USB-C charging cable included, full charge in 90 minutes, low-battery indicator LED), **counter-up** components: "4hrs Play Time", "90min Charge", "500+ Charge Cycles". Right column: **image** (USB-C charging port detail and battery compartment).

7. **layout-row (Feature: Players)** -> `comp_0_components_6`
   **heading** ("Play Solo or Together"), **columnsgrid** (2 columns). Left: **icon** + **heading** ("Solo Play") + **paragraph** ("Build, code, and experiment at your own pace. Perfect for focused learning."). Right: **icon** + **heading** ("2-4 Players") + **paragraph** ("Competition mode -- build robots and race them. Collaborative build challenges."). **image** (children playing together with multiple robots).

8. **layout-row (Feature: Play Duration)** -> `comp_0_components_7`
   **eyebrow** ("Play Value"), **heading** ("Hours of Engagement"), **columnsgrid** (3 columns) with **counter-up** + **caption**: "3-5 hrs First Build", "10+ Configurations", "Unlimited Free-Build". **paragraph** ("Parents report an average of 15+ hours of engaged play before children explore all configurations"). **progress-bar** (replay value meter -- "High Replay Value").

9. **layout-row (Feature: Setup)** -> `comp_0_components_8`
   Left column: **eyebrow** ("Getting Started"), **heading** ("Unbox to Play in 10 Minutes"), **paragraph** (step-by-step illustrated instruction booklet, QR code links to video tutorials, app guides through first build with 3D rotating instructions), **accordion** with items: "Step 1: Sort Pieces by Color", "Step 2: Build the Base Frame", "Step 3: Attach Motors", "Step 4: Connect to App". Right column: **image** (instruction booklet spread and app screenshot).

10. **layout-row (Feature: Size & Package)** -> `comp_0_components_9`
    **heading** ("What's in the Box"), **image** (flat-lay of all 500+ pieces organized by category), **columnsgrid** (2 columns). Left: spec list using **paragraph** pairs -- Box Size: 40 x 30 x 12 cm, Product Weight: 1.2 kg, Piece Count: 512 pieces, Motors: 2 included, Sensors: 1 distance sensor. Right: **image** (completed robot next to common objects for scale -- next to a water bottle, book).

11. **layout-row (Feature: Price)** -> `comp_0_components_10`
    **heading** ("Value & Bundles"), **columnsgrid** (3 columns): "Standard Set -- $49.99 -- 512 pieces, 1 robot", "Expansion Pack -- $29.99 -- 200 extra pieces, 5 new builds", "Ultimate Bundle -- $69.99 -- Standard + Expansion, save $10". Each with **image** + **heading** (price) + **paragraph** (contents) + **badge** ("Best Value" on bundle) + **button** ("Add to Cart"). **paragraph** ("Gift wrapping available -- $4.99").

12. **layout-row (Feature: Parent Reviews)** -> `comp_0_components_11`
    **heading** ("What Parents Say"), **rating** (4.7 overall), **progress-bar** rows for star distribution, **tabs** with 3 tabs: "Most Helpful" / "Durability Focus" / "Educational Value". Each tab: **accordion** with parent name, child's age mentioned, rating, review text. Pull-out: **blockquote** ("My 8-year-old hasn't looked at a screen in days." -- Verified Parent).

13. **layout-row (Related Products)** -> `comp_0_components_12`
    **heading** ("Kids Also Love"), **columnsgrid** (4 columns) each with **image** (box), **heading** (product name), **caption** (age range), **rating**, **heading** (price), **button** ("Add to Cart").

14. **layout-row (Gift Finder CTA)** -> `comp_0_components_13`
    **heading** ("Not Sure What to Get?"), **paragraph** ("Our Gift Finder matches the perfect toy to the child's age, interests, and your budget"), **button** ("Launch Gift Finder").

15. **layout-row (Footer)** -> `comp_0_components_14`
    **columnsgrid** (4 columns): Shop by Age, Shop by Category, Customer Service, Newsletter **textbox** + **button**. **br** divider. **paragraph** (copyright + safety disclaimer).

---

## Variant B -- Product Launch / Landing Page

**Page: New Toy Launch**

1. **titlebar**
   Brand logo, "New Launch" badge, shop CTA.

2. **layout-row (Hero -- Excitement Builder)**
   **video-background** (children reacting with excitement as they unbox and play). Overlay: **eyebrow** ("Just Launched"), **heading** ("MechaBot Builder 500"), **paragraph** ("The toy that teaches coding without the screen"), **button** ("Shop Now"), **countdown** (limited launch bundle expiry).

3. **layout-row (The Problem & Solution)**
   **columnsgrid** (2 columns). Left: **heading** ("Too Much Screen Time?"), **paragraph** (statistics on children's screen time, need for hands-on STEM learning). Right: **heading** ("Build. Code. Play. Offline."), **paragraph** (how this toy combines physical building with app-guided coding), **image** (child building vs child on tablet -- contrast).

4. **layout-row (How It Works)**
   **heading** ("3 Steps to Your First Robot"), **columnsgrid** (3 columns) with **counter-up** (step number) + **image** (step photo) + **heading** (action) + **paragraph** (description): "1. Build -- 512 pieces, 10 configurations", "2. Code -- Block-based coding app", "3. Play -- Race, dance, navigate obstacles".

5. **layout-row (Educational Endorsement)**
   **blockquote** ("This is exactly the kind of hands-on STEM tool we recommend for children aged 6-12." -- Dr. [Name], Child Development Specialist), **image** (expert photo), **caption** (credentials). **badge** ("Educator Recommended").

6. **layout-row (Awards & Recognition)**
   **heading** ("Award-Winning Design"), **ticker** scrolling award badges: **image** (award seal) + **caption** (award name and year).

7. **layout-row (Play Montage)**
   **carousel** (6 slides) -- children building, coding, racing robots, collaborating, showing completed builds, proud moments with parents.

8. **layout-row (Safety Promise)**
   **heading** ("Safe for Little Hands"), **columnsgrid** (4 columns) with certification badges and **caption** explanations. **paragraph** ("Every toy tested to exceed the strictest global safety standards").

9. **layout-row (Launch Bundle)**
   **heading** ("Launch Special -- Save 20%"), **image** (bundle contents), **heading** (crossed-out price + sale price), **button** ("Get the Launch Bundle"), **countdown** (offer expiry).

10. **layout-row (Footer)**
    Newsletter, social, safety info, copyright.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Toys & Games Catalog**

1. **titlebar**
   Store logo, category nav (0-2 Years, 3-5 Years, 6-8 Years, 9-12 Years, Teens, Family Games), search, gift finder, cart.

2. **layout-row (Category Hero)**
   **image** (colorful toy collage). **heading** ("Toys & Games"), **paragraph** ("Play, learn, and grow together"), **eyebrow** ("2,400+ toys").

3. **layout-row (Age Selector)**
   **heading** ("Shop by Age"), **columnsgrid** (5 columns) each with **image** (age-appropriate toy illustration) + **heading** (age range) + **caption** (toy count) + **button** ("Shop"): "0-2 Years", "3-5 Years", "6-8 Years", "9-12 Years", "Teens & Adults".

4. **layout-row (Category Browser)**
   **heading** ("Shop by Interest"), **columnsgrid** (4 columns, 2 rows) each with **icon** + **heading** + **caption**: "STEM & Science", "Arts & Crafts", "Building & Construction", "Board Games", "Action Figures", "Dolls & Playsets", "Outdoor Play", "Musical Instruments". Each is a clickable **button**.

5. **layout-row (Trending Now)**
   **heading** ("Trending This Week"), **carousel** (8 slides) with **image** (product), **badge** ("Hot"), **heading** (name), **caption** (age range), **rating**, **heading** (price), **button** ("Quick Add").

6. **layout-row (Product Grid)**
   **columnsgrid** (4 columns, repeating) each card: **image** (product/box), **badge** ("Age 6+" / "STEM" / "New"), **heading** (product name), **caption** (brand + age range), **rating** (stars + count), **heading** (price), **button** ("Add to Cart").

7. **layout-row (Gift Finder)**
   **heading** ("Gift Finder"), **paragraph** ("Answer 3 questions and we'll find the perfect toy"), **columnsgrid** (3 columns): **dropdown** ("Child's Age"), **dropdown** ("Interest Area"), **dropdown** ("Budget"). **button** ("Find Toys").

8. **layout-row (Safety Guide)**
   **heading** ("Safety Information"), **accordion** with sections: "Age Rating Explained", "Choking Hazard Warnings", "Battery Safety", "Material Standards (EN71, ASTM)", "How We Test Our Toys".

9. **layout-row (Bestsellers by Age)**
   **tabs** with 4 tabs by age group. Each tab: **columnsgrid** (4 columns) with top-selling products for that age -- **image** + **heading** + **rating** + **heading** (price) + **button** ("Add").

10. **layout-row (Footer)**
    Shop by age, shop by brand, customer service, safety policies, newsletter, social, copyright.
