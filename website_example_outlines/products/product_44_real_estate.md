# Real Estate Listings -- Product Pages

> Focus: Property-discovery storytelling with trackable sections for location, floor plans, amenities, pricing, and virtual tours that let builders and portals measure which listing details and interactive tools drive site visits, contact submissions, and booking conversions.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| 99acres Property Listing | 99acres.com/property-detail | Photo gallery hero with verified badge, price + EMI calculator sidebar, floor plan viewer, amenity icon grid, locality price trend graph, similar properties carousel, builder profile section |
| MagicBricks Listing | magicbricks.com/property-detail | Split-hero with gallery + key specs, price trend chart with area comparison, EMI calculator widget, neighborhood score radar chart, virtual tour embed, "Contact Builder" sticky CTA |
| Housing.com Project | housing.com/project | Full-width project hero with master plan, 3D walkthrough embed, configuration tabs (1BHK/2BHK/3BHK), amenity grid with categories, possession timeline progress bar, RERA details section |
| NoBroker Listing | nobroker.in/property | Owner-direct badge hero, detailed photo gallery with room labels, similar flats comparison, locality insights (schools, hospitals, transit), rent vs buy calculator, instant callback form |
| Lodha Group Project | lodhagroup.com/project | Luxury builder page with lifestyle video hero, master plan interactive map, specification accordion (flooring, fittings, electrical), payment plan timeline, site visit booking calendar, download brochure CTA |

**Patterns to incorporate:**
- Large photo gallery hero with room-by-room labeling and verified listing badge
- Price prominently displayed with EMI calculator and payment plan options
- Floor plan viewer with room dimensions and configuration options
- Amenity grid organized by category (fitness, leisure, convenience, security)
- Location map with nearby landmarks (schools, hospitals, metro, malls)
- Builder credentials with past project portfolio and RERA registration
- Possession timeline with construction progress indicators
- Virtual tour or 3D walkthrough embed
- Neighborhood insights with livability scores and price trends
- Site visit booking form or instant callback CTA

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Property Listing Detail (e.g., Lodha Bella Vita -- 3 BHK Apartment, Thane)**

1. **titlebar**
   Brand/portal logo, nav links (Projects, Localities, EMI Calculator, Blog, Contact), hamburger for mobile, "Schedule Visit" button.

2. **layout-row (Hero -- Property Gallery + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (8 shots -- building exterior, living room, master bedroom, kitchen, bathroom, balcony view, lobby/reception, amenity area). Right column: **eyebrow** ("3 BHK Apartment | Ready to Move"), **heading** ("Lodha Bella Vita"), **paragraph** ("Premium 3 BHK residences in Thane West with panoramic creek views, world-class amenities, and direct metro connectivity."), **badge** ("RERA Registered"), **badge** ("Ready to Move"), **rating** (4.4 stars, "185 Reviews"), **heading** ("INR 1.85 Cr*"), **caption** ("Carpet Area: 950 sq.ft. | All-inclusive price"), **button** ("Schedule Site Visit"), **button** ("Download Brochure"), **link** ("View on Map").

3. **layout-row (Feature 1: Location & Map)** -> `comp_0_components_2`
   Left column: **image** (locality map showing the property location with key landmarks marked -- metro station, highway, schools, hospitals, malls). Right column: **eyebrow** ("Location"), **heading** ("Thane West -- Ghodbunder Road"), **paragraph** ("Strategically located on Ghodbunder Road with direct access to the Eastern Express Highway and the upcoming Thane Metro Line 4. 5 minutes from Viviana Mall, 10 minutes from Jupiter Hospital."). **columnsgrid** (3 columns) each with **icon** + **counter-up** + **caption**: "Metro" + "500" / "m to Thane Metro (upcoming)", "Highway" + "2" / "km to Eastern Express Highway", "Airport" + "35" / "min to Mumbai Airport". **accordion** with items: "Schools Nearby (DAV, Podar, Ryan International -- all within 3 km)", "Hospitals (Jupiter, Bethany, Hiranandani -- within 5 km)", "Shopping (Viviana Mall, Korum Mall -- within 5 min)", "IT Parks (Wagle Estate, Airoli -- within 20 min)".

4. **layout-row (Feature 2: Floor Plan & Layout)** -> `comp_0_components_3`
   **eyebrow** ("Floor Plans"), **heading** ("Thoughtfully Designed Layouts"). **tabs** with tab per configuration: "2 BHK (780 sq.ft.)", "3 BHK (950 sq.ft.)", "3 BHK Large (1,150 sq.ft.)". Each tab: **image** (detailed floor plan with room dimensions annotated), **columnsgrid** (2 columns) with room-by-room dimensions: Left -- **paragraph** ("Living + Dining: 18' x 12'"), **paragraph** ("Master Bedroom: 14' x 12'"), **paragraph** ("Bedroom 2: 12' x 10'"); Right -- **paragraph** ("Kitchen: 10' x 8'"), **paragraph** ("Bathroom 1: 8' x 5'"), **paragraph** ("Balcony: 10' x 4'"). **caption** ("All dimensions are carpet area. Actual layout may vary slightly."). **button** ("Download Floor Plan PDF").

5. **layout-row (Feature 3: Amenities & Features)** -> `comp_0_components_4`
   **eyebrow** ("Amenities"), **heading** ("World-Class Living"). **tabs** with tab per category: "Fitness" (**columnsgrid** 3 columns with **icon** + **caption** each: "Gymnasium", "Swimming Pool", "Jogging Track", "Yoga Lawn", "Tennis Court", "Badminton Court"), "Leisure" (**columnsgrid** 3 columns: "Clubhouse", "Mini Theater", "Library", "Kids Play Area", "Party Hall", "BBQ Zone"), "Convenience" (**columnsgrid** 3 columns: "Covered Parking", "EV Charging", "Power Backup", "Rainwater Harvesting", "STP Plant", "High-Speed Elevators"), "Security" (**columnsgrid** 3 columns: "24/7 CCTV", "Gated Entry", "Intercom", "Fire Safety System", "Earthquake Resistant", "Security Guards"). **counter-up** stats: "40+" / "Premium Amenities", "3" / "Acres of Open Space", "80" / "% Green Coverage".

6. **layout-row (Feature 4: Price & EMI Calculator)** -> `comp_0_components_5`
   Left column: **eyebrow** ("Pricing"), **heading** ("Investment Overview"), **columnsgrid** (1 column, stacked): **layout-row** with **heading** ("2 BHK") + **caption** ("From INR 1.35 Cr | 780 sq.ft."), **layout-row** with **heading** ("3 BHK") + **caption** ("From INR 1.85 Cr | 950 sq.ft.") + **badge** ("Most Popular"), **layout-row** with **heading** ("3 BHK Large") + **caption** ("From INR 2.25 Cr | 1,150 sq.ft."). **caption** ("*Prices are all-inclusive. GST applicable on under-construction units. Stamp duty and registration extra."). Right column: **eyebrow** ("EMI Calculator"), **heading** ("Plan Your Investment"). **form** with **textbox** (Loan Amount -- pre-filled INR 1.48 Cr for 80% of 3BHK), **dropdown** (Interest Rate: 8.5% / 9% / 9.5%), **dropdown** (Tenure: 10 / 15 / 20 / 25 / 30 years), **button** ("Calculate EMI"). **heading** ("Estimated EMI: INR 1,14,000/month"), **caption** ("Based on 80% financing at 8.5% for 20 years"). **button** ("Check Bank Offers").

7. **layout-row (Feature 5: Builder Credentials)** -> `comp_0_components_6`
   Left column: **image** (Lodha Group corporate image -- completed landmark project or HQ). Right column: **eyebrow** ("The Builder"), **heading** ("Lodha Group"), **paragraph** ("One of India's largest real estate developers with 40+ years of experience. Macrotech Developers (Lodha) is listed on BSE and NSE with a market cap of INR 80,000+ Cr. Known for landmark projects across Mumbai, Thane, and Pune."). **columnsgrid** (4 columns) with **counter-up** + **caption**: "40" / "Years Experience", "100" / "Million sq.ft. Delivered", "35000" / "Happy Families", "30" / "Ongoing Projects". **link** ("View All Lodha Projects"). **badge** ("CRISIL A+ Rated").

8. **layout-row (Feature 6: Possession Timeline)** -> `comp_0_components_7`
   **eyebrow** ("Construction"), **heading** ("Project Status"). **progress-bar** labeled "Construction Progress" at 100% (for Ready to Move). **columnsgrid** (4 columns) each with **badge** (status) + **caption** (milestone): "Completed" / "Foundation & Structure", "Completed" / "Internal Finishing", "Completed" / "Amenity Handover", "Completed" / "OC Received". **paragraph** ("Occupancy Certificate received. Ready for immediate possession. Society formation in progress."). **caption** ("RERA Registration: P51700028765"). **badge** ("Ready to Move").

9. **layout-row (Feature 7: Virtual Tour)** -> `comp_0_components_8`
   **eyebrow** ("Experience"), **heading** ("Take a Virtual Tour"). **video** (360-degree walkthrough video of the sample flat -- living room, bedrooms, kitchen, bathrooms, balcony). **paragraph** ("Can't visit in person? Explore the 3 BHK sample flat from the comfort of your home. Our virtual tour covers every room with realistic rendering."). **button** ("Launch Full 360 Tour"). **button** ("Schedule Video Call with Sales Team").

10. **layout-row (Feature 8: Neighborhood Info)** -> `comp_0_components_9`
    **eyebrow** ("Neighborhood"), **heading** ("Life in Thane West"). **columnsgrid** (2 columns): Left -- **heading** ("Livability Score") + **progress-bar** bars: "Connectivity" at 85%, "Social Infrastructure" at 80%, "Safety" at 75%, "Green Spaces" at 90%, "Civic Amenities" at 70%; Right -- **heading** ("Price Trends") + **paragraph** ("Average price in Ghodbunder Road: INR 12,500/sq.ft. 5-year appreciation: 38%.") + **counter-up** + **caption**: "38" / "% 5-Year Price Growth", "12500" / "INR Avg. Price/sq.ft.". **paragraph** ("Thane West is one of the fastest-growing residential corridors in the Mumbai Metropolitan Region, driven by metro connectivity, IT park proximity, and premium civic infrastructure."). **link** ("View Detailed Locality Report").

11. **layout-row (Feature 9: RERA Compliance)** -> `comp_0_components_10`
    Left column: **eyebrow** ("Legal"), **heading** ("RERA Registered & Compliant"), **paragraph** ("This project is registered under the Real Estate (Regulation and Development) Act, 2016 with MahaRERA. All project details, approvals, and financial statements are publicly available on the RERA portal."). Right column: **columnsgrid** (1 column) with **icon** + **heading** + **caption** for each: "RERA Number" / "P51700028765" / "Verify on maharera.mahaonline.gov.in", "Commencement Certificate" / "Issued" / "Mumbai Municipal Corporation", "Environment Clearance" / "Approved" / "MoEFCC", "Fire NOC" / "Obtained" / "Thane Fire Department". **link** ("Verify on MahaRERA Portal"). **button** ("Download Legal Documents").

12. **layout-row (Feature 10: Visit / Contact CTA)** -> `comp_0_components_11`
    **video-background** (aerial drone footage of the project and surrounding area). Overlay: **heading** ("See It. Feel It. Own It."), **paragraph** ("Schedule a site visit and experience Lodha Bella Vita in person. Our sales team will arrange pickup from the nearest metro station."). **form** with **textbox** (Full Name), **textbox** (Phone Number), **textbox** (Email), **dropdown** (Configuration: 2 BHK / 3 BHK / 3 BHK Large), **dropdown** (Purpose: Self-Use / Investment), **calendar** (Preferred Visit Date), **dropdown** (Preferred Time Slot: 10 AM / 12 PM / 2 PM / 4 PM), **button** ("Schedule Visit"). **caption** ("Complimentary pickup from Thane Metro Station. Or call: 1800-XXX-XXXX").

13. **layout-row (Reviews)** -> `comp_0_components_12`
    **eyebrow** ("Resident Reviews"), **heading** ("What Residents Say"). **rating** (4.4 overall, "185 reviews"). **columnsgrid** (3 columns) each with **rating**, **blockquote** (review), **caption** (reviewer + configuration + "Verified Resident"). **button** ("Read All Reviews").

14. **layout-row (Similar Properties)** -> `comp_0_components_13`
    **heading** ("Similar Properties Nearby"). **columnsgrid** (3 columns) each with **image** (project exterior), **heading** (project name), **caption** (builder + configuration + price range), **badge** ("Under Construction" / "Ready" / "New Launch"), **button** ("View Details").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Popular Localities (Thane, Powai, Andheri, Navi Mumbai), Explore (New Projects, Ready to Move, Under Construction, Resale), Tools (EMI Calculator, Home Loan, Legal Check, Vastu Guide), Connect (Contact, Blog, Careers, Advertise). **br** (divider). **caption** (copyright, RERA disclaimer, legal text).

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new real estate project launch

**Page: New Project Launch (e.g., "Godrej Reserve -- Bandra East")**

1. **titlebar** -- Builder logo, minimal nav (Overview, Masterplan, Amenities, Pricing, Location), "Register Interest" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic aerial drone footage of the Bandra skyline transitioning to architectural rendering of the project). Overlay: **eyebrow** ("A Godrej Properties Address"), **heading** ("Godrej Reserve"), **paragraph** ("Ultra-luxury residences in the heart of Bandra East"), **badge** ("Pre-Launch"), **heading** ("Starting INR 5 Cr*"), **button** ("Register Interest"), **countdown** (to official launch date).

3. **layout-row (Key Numbers)** -- Dark background. **columnsgrid** (4 columns) with **counter-up** + **caption**: "3" / "Towers", "45" / "Floors", "4" / "Configurations (2-4 BHK)", "70" / "% Open Spaces". **paragraph** ("RERA Pre-Registration Applied. Expected Registration: Q2 2026.").

4. **layout-row (Masterplan)** -- **heading** ("The Masterplan"), **image** (interactive-style masterplan rendering showing towers, gardens, amenities). **paragraph** ("Spread across 5 acres with 70% open and green spaces. Designed by internationally acclaimed architects.").

5. **layout-row (Signature Amenities)** -- **heading** ("The Godrej Reserve Lifestyle"), **carousel** (amenity renders -- infinity pool, rooftop lounge, wellness spa, children's world, business center). **columnsgrid** (3 columns) with **icon** + **caption**: "Infinity Pool with Bay View", "Private Residents' Lounge", "10,000 sq.ft. Clubhouse".

6. **layout-row (Location Advantage)** -- **heading** ("Bandra East -- The Address That Needs No Introduction"), **image** (map with key landmarks), **ticker** scrolling distances: "Bandra Station: 5 min", "BKC: 8 min", "Airport: 20 min", "Linking Road: 10 min".

7. **layout-row (Builder Trust)** -- **heading** ("Godrej Properties -- 125 Years of Trust"), **columnsgrid** (3 columns) with **counter-up** + **caption**: "125" / "Years Godrej Legacy", "200" / "Million sq.ft. Delivered", "12" / "Cities Across India". **image** (completed landmark Godrej project).

8. **layout-row (Registration CTA)** -- **heading** ("Register for Priority Allotment"), **paragraph** ("Get early access to pricing, floor plans, and preferred unit selection"), **form** with **textbox** (Name), **textbox** (Phone), **textbox** (Email), **dropdown** (Budget Range), **button** ("Register Interest"). **caption** ("Your information is kept strictly confidential.").

9. **layout-row (Footer)** -- Minimal footer with builder info, RERA disclaimer, legal text, privacy policy.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-property browsing layout for a real estate portal

**Page: Property Search Results (e.g., "99acres -- Flats in Thane West")**

1. **titlebar** -- Portal logo, nav (Buy, Rent, Projects, Agents, Home Loans, Post Property), search bar, "Post Free Ad" button.

2. **layout-row (Hero)** -- **heading** ("Flats for Sale in Thane West"), **paragraph** ("2,450 properties found | Starting from INR 45 Lakh"), **layout-row** with **counter-up** + **caption**: "2450" / "Properties", "85" / "Projects", "40" / "Builders".

3. **layout-row (Filter Bar)** -- **layout-row** with filters: **dropdown** (BHK: 1 / 2 / 3 / 4+), **dropdown** (Budget: Under 50L / 50L-1Cr / 1-2Cr / 2-3Cr / 3Cr+), **dropdown** (Status: Ready / Under Construction / New Launch), **dropdown** (Area: 500-750 / 750-1000 / 1000-1500 / 1500+ sq.ft.), **dropdown** (Sort By: Price Low-High / Price High-Low / Newest / Relevance), **button** ("Search").

4. **layout-row (Featured Projects)** -- **eyebrow** ("Featured"), **heading** ("Premium Projects in Thane West"). **columnsgrid** (3 columns) each card: **image** (project render), **badge** ("Featured" / "RERA Verified" / "Ready to Move"), **heading** (project name), **caption** (builder name), **paragraph** (configuration range + price range), **rating** (livability score), **button** ("View Details"), **button** ("Get Quote").

5. **layout-row (Resale Properties)** -- **eyebrow** ("Resale"), **heading** ("Owner-Listed Properties"). Same card pattern but with owner listing details: **image** (flat photos), **heading** (description -- "3 BHK in Hiranandani Estate"), **caption** (area + floor + age), **heading** (price), **badge** ("Owner" / "Broker"), **button** ("Contact"), **button** ("View Photos").

6. **layout-row (Under Construction)** -- **eyebrow** ("Upcoming"), **heading** ("Under-Construction Projects"). Same card pattern with possession date and **progress-bar** (construction progress).

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Properties"). **columnsgrid** (3 columns) each with **dropdown** (select property). Comparison rows: Price, Carpet Area, Configuration, Floor, Possession, Builder Rating, Amenities Count, Locality Score.

8. **layout-row (Price Trend)** -- **heading** ("Thane West Price Trends"), **paragraph** ("Average price: INR 12,500/sq.ft. | 5-year growth: 38%"), **image** (price trend chart placeholder), **counter-up** + **caption**: "12500" / "INR Avg. Price/sq.ft.", "38" / "% 5-Year Growth".

9. **layout-row (Home Loan CTA)** -- **heading** ("Get Pre-Approved for a Home Loan"), **paragraph** ("Compare rates from 15+ banks"), **form** with **textbox** (Loan Amount), **dropdown** (Employment Type), **button** ("Check Eligibility"). **ticker** scrolling bank logos and rates.

10. **layout-row (Footer)** -- Full footer with popular searches, localities, tools (EMI, stamp duty, legal), company info, social links, legal disclaimers, RERA compliance notice.
