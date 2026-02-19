# Pet Supplies & Food -- Product Pages

> Focus: Ingredient transparency and nutritional breakdown, pet type/breed/age specificity, veterinarian endorsement, feeding guide clarity, and subscription convenience that build trust for the pet parent who treats their animal as family.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Pedigree | pedigree.com/dog-food | Ingredient-first hero with real meat callout, breed size selector (Small/Medium/Large), guaranteed analysis nutrition table, feeding chart by weight, "Complete & Balanced" badge |
| Royal Canin | royalcanin.com/us/dogs/products | Breed-specific product pages with breed photo, tailored nutrition story, kibble shape diagram, vet recommendation badge, precise feeding calculator by weight/activity |
| Heads Up For Tails | headsupfortails.com | Pet name customization on products, curated gift boxes, breed-specific browsing, free vet consultation callout, in-store and online experience |
| Supertails | supertails.com | Free vet advice integration, subscription with auto-delivery, pet profile-based recommendations, community pet photos, combo deal bundles |
| Chewy | chewy.com | Autoship subscription discount, vet diet section, pet pharmacy, customer Q&A alongside reviews, "Chewy Exclusive" badges, write-a-review with pet photo upload |

**Patterns to incorporate:**
- Ingredient list with real-meat-first callout and "no artificial" claims
- Pet type, breed, and life stage selector (Puppy/Adult/Senior, Small/Medium/Large)
- Guaranteed analysis nutrition table with protein/fat/fiber percentages
- Feeding guide chart by pet weight with scoop illustration
- Vet recommendation badge and expert endorsement
- Pack size selector with per-kg pricing
- Subscription/auto-delivery option with discount
- Customer pet photos in reviews
- Allergy/sensitivity information with alternative product suggestions

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Pet Food Detail**

1. **titlebar**
   Brand/store logo, nav links (Dog Food, Cat Food, Treats, Accessories, Health, Toys), search icon, pet profile icon, cart icon.

2. **layout-row (Hero -- Product Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (5 slides -- bag front, bag back with nutrition info, kibble close-up, dog eating product, ingredient spread flat-lay). Right column: **eyebrow** ("Adult Dog | Medium Breed | Chicken"), **heading** (product name "NutriPrime Adult Chicken & Rice"), **rating** (4.7 stars, 3,450 reviews), **paragraph** ("Complete and balanced nutrition with real chicken as the #1 ingredient"), **badge** ("Vet Recommended"), **badge** ("#1 Ingredient: Real Chicken"), pack size selector using **button** components (2 kg / 5 kg / 10 kg / 15 kg), **heading** (price "$42.99 for 10 kg" + per-kg price), **button** ("Add to Cart"), **button** ("Subscribe & Save 15%" outline), **paragraph** ("Free delivery on orders over $35. Auto-delivery every 4/6/8 weeks.").

3. **layout-row (Feature: Ingredients & Nutrition)** -> `comp_0_components_2`
   Left column: **eyebrow** ("Ingredients"), **heading** ("Real Chicken. Real Ingredients. Real Nutrition."), **paragraph** (chicken is the #1 ingredient, whole grain rice for digestible energy, omega-3 and omega-6 fatty acids for healthy coat, no artificial colors, flavors, or preservatives), **accordion** with items: "Full Ingredient List", "Guaranteed Analysis (Protein 26%, Fat 16%, Fiber 3%)", "Calorie Content (3,680 kcal/kg)". Right column: **image** (ingredient spread -- raw chicken, rice, vegetables, fish oil arranged artistically). **columnsgrid** (3 columns) with **counter-up** + **caption**: "26% Protein", "16% Fat", "Real Chicken #1".

4. **layout-row (Feature: Pet Type & Breed)** -> `comp_0_components_3`
   **eyebrow** ("Tailored Nutrition"), **heading** ("Made for Medium Breed Adults"), **paragraph** (kibble size optimized for medium jaw and bite force, calorie density calibrated for 10-25 kg body weight, joint support nutrients for medium breed mobility needs), **columnsgrid** (3 columns) with **image** + **heading** + **paragraph**: "Small Breed (<10 kg) -- Smaller kibble, higher calorie density for fast metabolism", "Medium Breed (10-25 kg) -- Balanced kibble for moderate energy needs [THIS PRODUCT]", "Large Breed (25+ kg) -- Larger kibble, glucosamine for joint health". **badge** ("You're Viewing: Medium Breed"). **button** ("Find the Right Formula for Your Pet").

5. **layout-row (Feature: Age/Size)** -> `comp_0_components_4`
   **heading** ("Life Stage Nutrition"), **columnsgrid** (4 columns) each with **icon** + **heading** + **paragraph** + **button** ("Shop"): "Puppy (2-12m) -- DHA for brain development, calcium for growing bones", "Adult (1-7y) -- Balanced maintenance for peak health [CURRENT]", "Senior (7+) -- Reduced calories, joint support, easy-to-chew", "All Life Stages -- Formulated for any age". **badge** ("Viewing: Adult") on current product. **progress-bar** (life stage timeline visualization).

6. **layout-row (Feature: Flavors)** -> `comp_0_components_5`
   **heading** ("Available Flavors"), **columnsgrid** (4 columns) each with **image** (bag variant) + **heading** (flavor) + **paragraph** (key protein) + **button** ("Select"): "Chicken & Rice -- Real chicken, gentle on digestion", "Lamb & Vegetables -- Ideal for poultry-sensitive dogs", "Salmon & Sweet Potato -- Omega-rich for skin and coat", "Beef & Barley -- High-protein for active dogs". **badge** ("Bestseller") on most popular.

7. **layout-row (Feature: Pack Sizes)** -> `comp_0_components_6`
   **heading** ("Choose Your Size"), **columnsgrid** (4 columns) each with **image** (bag size visual) + **heading** (size) + **heading** (price) + **caption** (per-kg price) + **button** ("Select"): "2 kg -- $12.99 -- $6.50/kg -- Trial size", "5 kg -- $27.99 -- $5.60/kg", "10 kg -- $42.99 -- $4.30/kg -- Most Popular", "15 kg -- $57.99 -- $3.87/kg -- Best Value". **badge** ("Best Value") on largest. **badge** ("Most Popular") on 10 kg. **paragraph** ("Subscribe & Save: Additional 15% off any size with auto-delivery").

8. **layout-row (Feature: Vet Recommended)** -> `comp_0_components_7`
   Left column: **image** (veterinarian portrait in clinic). Right column: **eyebrow** ("Expert Endorsed"), **heading** ("Recommended by Veterinarians"), **blockquote** ("I recommend NutriPrime to my clients because every formula is backed by peer-reviewed nutritional research and uses high-quality, traceable ingredients." -- Dr. [Name], DVM, Board Certified Veterinary Nutritionist), **caption** (credentials), **badge** ("Vet Formulated"). **paragraph** ("Developed with a panel of 12 veterinary nutritionists").

9. **layout-row (Feature: Feeding Guide)** -> `comp_0_components_8`
   **eyebrow** ("Feeding Guide"), **heading** ("How Much to Feed"), **image** (feeding chart infographic with scoop sizes by dog weight). Table-like **columnsgrid** (4 columns) with headers: "Dog Weight" / "Daily Amount" / "Cups/Day" / "Bag Lasts": "5-10 kg / 100-170g / 1-1.5 cups / ~60 days", "10-20 kg / 170-280g / 1.5-2.5 cups / ~36 days", "20-30 kg / 280-380g / 2.5-3.5 cups / ~26 days", "30-40 kg / 380-470g / 3.5-4.5 cups / ~21 days". **paragraph** ("Adjust amounts based on your dog's activity level, age, and body condition. Always provide fresh water. Transition gradually over 7-10 days.").

10. **layout-row (Feature: Pet Photos)** -> `comp_0_components_9`
    **heading** ("#NutriPrimePets -- Real Pets, Real Results"), **columnsgrid** (4 columns) with customer-submitted **image** (pet photos) + **caption** (pet name, breed, age) + **rating** (owner's rating). **button** ("Share Your Pet's Photo"). **paragraph** ("Tag @NutriPrime on Instagram and your pet could be featured here").

11. **layout-row (Feature: Subscription)** -> `comp_0_components_10`
    **eyebrow** ("Never Run Out"), **heading** ("Subscribe & Save 15%"), **columnsgrid** (2 columns). Left: benefits list using **icon** + **paragraph**: "15% off every order", "Free shipping always", "Change, skip, or cancel anytime", "Automatic delivery every 4, 6, or 8 weeks". Right: **image** (subscription box arriving at door). **button** ("Start Subscription"), **paragraph** ("Delivery frequency selector available at checkout").

12. **layout-row (Feature: Allergy Info)** -> `comp_0_components_11`
    **eyebrow** ("Sensitivities"), **heading** ("Allergy & Sensitivity Information"), **paragraph** (this formula contains chicken and grains, may not be suitable for dogs with poultry or grain allergies), **columnsgrid** (2 columns). Left: "Contains" -- **badge** components: "Chicken", "Rice", "Corn", "Wheat Gluten". Right: "Free From" -- **badge** components (different color): "No Artificial Colors", "No Artificial Flavors", "No Soy", "No BHA/BHT". **heading** ("Need a Hypoallergenic Option?"), **button** ("Shop Limited Ingredient Diets").

13. **layout-row (Reviews & Ratings)** -> `comp_0_components_12`
    **heading** ("Pet Parent Reviews"), **rating** (4.7 overall from 3,450 reviews), **progress-bar** rows for star distribution, **tabs** with 3 tabs: "Most Helpful" / "Picky Eaters" / "With Pet Photos". Each tab: **accordion** with reviewer name, pet's name/breed/age, rating, review text, optional **image** (pet photo). Featured: **blockquote** ("My Golden Retriever's coat has never looked better. She devours every meal." -- Jake, Owner of Luna, 3yr Golden Retriever).

14. **layout-row (Related Products)** -> `comp_0_components_13`
    **heading** ("Complete Your Pet's Routine"), **columnsgrid** (4 columns) each with **image**, **heading** (name), **caption** (category), **heading** (price), **button** ("Add"): Dental Chews, Joint Supplement, Training Treats, Slow Feeder Bowl.

15. **layout-row (Footer)** -> `comp_0_components_14`
    **columnsgrid** (4 columns): Shop by Pet, Shop by Brand, Pet Health Resources, Newsletter **textbox** + **button**. **br** divider. **paragraph** (copyright + AAFCO statement).

---

## Variant B -- Product Launch / Landing Page

**Page: New Pet Food Launch**

1. **titlebar**
   Brand logo, "New Formula" badge, shop CTA.

2. **layout-row (Hero -- Emotional Bond)**
   **video-background** (montage of happy dogs running, eating, playing with owners, glossy coats, energetic movement). Overlay: **eyebrow** ("New Formula"), **heading** ("NutriPrime Fresh -- Real Cooked Meals Delivered"), **paragraph** ("Human-grade ingredients. Vet-formulated. Delivered to your door."), **button** ("Build Your Pet's Plan"), **countdown** (launch discount expiry).

3. **layout-row (Ingredient Transparency)**
   **heading** ("You Can See Every Ingredient"), **image** (flat-lay of all raw ingredients -- chicken breast, sweet potato, spinach, blueberries, fish oil), **paragraph** ("No powders. No mystery meals. Just real food you'd recognize from your own kitchen."), **counter-up**: "6 Whole Ingredients", "0 Artificial Additives", "Human-Grade Quality".

4. **layout-row (The Science)**
   **heading** ("Vet-Formulated. Research-Backed."), split layout: left **image** (veterinary nutritionist in lab), right **paragraph** (formulation process, clinical trials, AAFCO feeding trial completion), **badge** ("AAFCO Feeding Trial Approved").

5. **layout-row (Before & After Results)**
   **heading** ("Real Results in 30 Days"), **columnsgrid** (3 columns) each with **image** (pet before) + **image** (pet after) + **caption** (improvement noted: "Shinier coat", "More energy", "Better digestion"). **counter-up**: "93% of Pet Parents See Improvement in 4 Weeks".

6. **layout-row (How It Works)**
   **heading** ("3 Steps to Better Nutrition"), **columnsgrid** (3 columns) with **counter-up** (step number) + **icon** + **heading** + **paragraph**: "1. Tell Us About Your Pet -- Breed, age, weight, allergies, activity level", "2. Get a Custom Plan -- Vet-formulated portions shipped fresh", "3. Watch Them Thrive -- Track health improvements in our app".

7. **layout-row (Meal Options)**
   **heading** ("Choose a Recipe"), **columnsgrid** (4 columns) each with **image** (meal photo) + **heading** (recipe name) + **paragraph** (ingredients) + **button** ("Add to Plan"): "Chicken & Sweet Potato", "Beef & Brown Rice", "Turkey & Pumpkin", "Salmon & Quinoa".

8. **layout-row (Testimonials)**
   **carousel** (5 slides) each with **image** (pet photo) + **heading** (pet name and breed) + **blockquote** (owner testimonial) + **rating**.

9. **layout-row (Launch Offer)**
   **heading** ("50% Off Your First Box"), **paragraph** ("Try NutriPrime Fresh with zero commitment. Cancel anytime."), **heading** (original price crossed out + launch price), **button** ("Start My Plan -- 50% Off"), **countdown** (offer deadline).

10. **layout-row (Footer)**
    Newsletter, social, AAFCO info, vet resources, copyright.

---

## Variant C -- Product Catalog / Comparison Page

**Page: Pet Supplies Catalog**

1. **titlebar**
   Store logo, category nav (Dogs, Cats, Birds, Fish, Small Pets, Pharmacy), search, pet profile, cart.

2. **layout-row (Category Hero)**
   **image** (happy pets collage -- dogs, cats, birds). **heading** ("Pet Food & Supplies"), **paragraph** ("Everything your pet needs, recommended by vets"), **eyebrow** ("5,200+ products").

3. **layout-row (Pet Type Selector)**
   **heading** ("Shop by Pet"), **columnsgrid** (4 columns) each with **image** (pet type illustration) + **heading** (pet name) + **caption** (product count) + **button** ("Shop"): "Dogs -- 2,400+ products", "Cats -- 1,800+ products", "Birds -- 320+ products", "Small Pets -- 280+ products".

4. **layout-row (Breed-Specific Finder)**
   **heading** ("Find Food for Your Breed"), **layout-row** with **dropdown** ("Pet Type") + **dropdown** ("Breed") + **dropdown** ("Age") + **dropdown** ("Size") + **button** ("Find Food"). **paragraph** ("Get tailored nutrition recommendations based on your pet's specific needs").

5. **layout-row (Product Grid)**
   **columnsgrid** (3 columns, repeating) each card: **image** (product bag/can), **badge** ("Dog" / "Cat" / "Vet Diet"), **heading** (product name), **caption** (brand + flavor + size), **rating** (stars + count), **heading** (price + per-kg), **button** ("Add to Cart") + **button** ("Subscribe").

6. **layout-row (Brand Showcase)**
   **heading** ("Shop by Brand"), **ticker** scrolling brand logos with links: Royal Canin, Pedigree, Purina, Hills, Orijen, Acana, Farmina, Taste of the Wild. Each **image** (logo) + **caption** (brand name).

7. **layout-row (Diet & Health Needs)**
   **heading** ("Special Diets"), **columnsgrid** (4 columns) each with **icon** + **heading** + **caption** + **button** ("Shop"): "Weight Management -- Low-calorie formulas", "Grain-Free -- For grain sensitivities", "Vet Prescription -- Therapeutic diets", "Hypoallergenic -- Limited ingredient recipes".

8. **layout-row (Comparison Table)**
   **heading** ("Compare Popular Dog Foods"), comparison **columnsgrid** (4 columns): Header: Feature / Economy / Premium / Super-Premium. Rows for: Protein %, Primary Ingredient, Artificial Additives, Feeding Cost/Day, Vet Recommended -- using **paragraph** and **icon** components. **button** ("Select") under each.

9. **layout-row (Subscription Benefits)**
   **heading** ("Autoship & Save"), **columnsgrid** (3 columns) with **icon** + **heading** + **paragraph**: "Save 15% -- On every autoship order", "Free Shipping -- Always free on autoship", "Flexible Schedule -- Change, skip, or cancel anytime". **button** ("Start Autoship").

10. **layout-row (Vet Consultation)**
    **heading** ("Free Vet Advice"), **paragraph** ("Chat with a veterinarian about your pet's nutrition at no cost"), **image** (vet on video call with pet owner), **button** ("Book Free Consultation").

11. **layout-row (Footer)**
    Shop by pet, shop by brand, health resources, subscription FAQs, newsletter, social, copyright.
