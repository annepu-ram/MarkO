# Solar & Green Tech -- Product Pages

> Focus: Savings-driven technical storytelling with trackable sections for panel efficiency, system sizing, ROI calculators, and installation processes that let solar companies measure which financial projections and environmental impact details convert browsers into site survey bookings and system purchases.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Tesla Solar | tesla.com/energy/design | Interactive system designer hero with address-based solar estimate, roof tile visualization, Powerwall battery pairing, monthly savings counter, utility bill offset percentage, order flow with deposit CTA |
| Tata Power Solar | tatapowersolar.com/residential | Savings calculator hero with electricity bill input, panel efficiency comparison chart, step-by-step installation timeline, government subsidy information, EMI options, customer testimonial video grid |
| Luminous Solar | luminoussolar.com/rooftop | ROI calculator with payback period visualization, panel wattage selector, inverter pairing guide, warranty comparison table, "Book Free Site Survey" prominent CTA, dealer locator map |
| Havells Solar | havells.com/solar-rooftop | Product range hero with panel efficiency badges, system size recommendation based on bill amount, net metering explanation, installation process steps, 25-year performance warranty, download datasheet CTA |
| SunPower Maxeon | sunpower.com/solar-panels | Industry-leading efficiency hero (22.8%), degradation rate comparison, shade performance advantage, complete home solar system packages, monitoring app showcase, financing options breakdown |

**Patterns to incorporate:**
- Savings calculator hero where users input their electricity bill to see estimated savings
- Panel efficiency and wattage specifications with competitive comparison
- System size recommendation based on consumption and roof area
- Monthly/annual savings projection with payback period counter
- Step-by-step installation process timeline with duration estimates
- Battery storage options with backup duration calculator
- Government subsidy and incentive information by region
- Warranty details emphasizing 25-year performance guarantees
- ROI timeline visualization showing cumulative savings over decades
- Monitoring app showcase with real-time generation data
- Environmental impact counter (CO2 offset, trees equivalent)
- "Book Free Site Survey" or "Get Custom Quote" conversion CTA

---

## Variant A -- Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Solar System Product Detail (e.g., Tata Power Solar -- 5kW Rooftop Solar System)**

1. **titlebar**
   Brand logo, nav links (Residential, Commercial, Products, Calculator, About, Contact), hamburger for mobile, "Get Free Quote" button.

2. **layout-row (Hero -- System Overview + Key Info)** -> `comp_0_components_1`
   Left column: **carousel** (6 shots -- installed rooftop system aerial view, panel close-up showing cell pattern, inverter wall mount, monitoring app screenshot, installation team at work, happy homeowner with panels on roof). Right column: **eyebrow** ("Residential | Grid-Tied"), **heading** ("5kW Rooftop Solar System"), **paragraph** ("Power your home with clean, free energy from the sun. A 5kW system covers the average 3-4 BHK household's electricity needs and pays for itself within 4-5 years."), **badge** ("BIS Certified"), **badge** ("Govt. Subsidy Eligible"), **rating** (4.6 stars, "2,100 Reviews"), **heading** ("INR 2,85,000*"), **caption** ("*Before government subsidy. After subsidy: ~INR 2,07,000"), **button** ("Get Free Site Survey"), **button** ("Calculate Your Savings"), **link** ("Download Datasheet").

3. **layout-row (Feature 1: Panel Efficiency & Wattage)** -> `comp_0_components_2`
   Left column: **image** (solar panel close-up showing monocrystalline PERC cell structure with half-cut technology visible). Right column: **eyebrow** ("Panel Technology"), **heading** ("High-Efficiency Mono PERC Panels"), **paragraph** ("Each panel in your 5kW system uses monocrystalline PERC (Passivated Emitter and Rear Cell) technology with half-cut cell design. This delivers up to 21.5% conversion efficiency -- extracting more energy from every square meter of roof space."). **columnsgrid** (3 columns) each with **counter-up** + **caption**: "21.5" / "% Panel Efficiency", "545" / "W Per Panel", "10" / "Panels in 5kW System". **accordion** with items: "Cell Technology (Mono PERC Half-Cut, 144 cells per panel)", "Panel Dimensions (2278 x 1134 x 35mm, 27.5 kg each)", "Temperature Coefficient (-0.34%/C -- minimal heat loss)", "Low-Light Performance (Generates power even on cloudy days)". **badge** ("Tier-1 Manufacturer").

4. **layout-row (Feature 2: System Size & Coverage)** -> `comp_0_components_3`
   Left column: **eyebrow** ("System Sizing"), **heading** ("Right-Sized for Your Home"), **paragraph** ("A 5kW system generates approximately 20-25 units (kWh) of electricity per day, enough to offset the complete electricity consumption of a typical 3-4 BHK household with AC, refrigerator, washing machine, and standard appliances."). Right column: **columnsgrid** (2 columns): Column 1 -- **heading** ("Daily Generation") + **counter-up** ("22") + **caption** ("kWh average daily output") + **paragraph** ("Based on 4.5 peak sun hours/day in most Indian metros"); Column 2 -- **heading** ("Monthly Generation") + **counter-up** ("660") + **caption** ("kWh average monthly output") + **paragraph** ("Equivalent to INR 5,000-6,000 electricity bill offset"). **paragraph** ("Roof area required: approximately 350 sq.ft. of shadow-free space. East-West or South-facing roofs preferred."). **image** (roof area illustration showing panel placement on a typical terrace).

5. **layout-row (Feature 3: Savings Calculator)** -> `comp_0_components_4`
   **eyebrow** ("Your Savings"), **heading** ("Calculate How Much You'll Save"). **form** with **textbox** (Monthly Electricity Bill in INR -- placeholder "e.g., 5000"), **dropdown** (City: Mumbai / Delhi / Bangalore / Chennai / Hyderabad / Pune / Kolkata / Other), **dropdown** (Roof Type: RCC Flat / Sloped Tile / Metal Sheet), **button** ("Calculate Savings"). **columnsgrid** (3 columns) with **counter-up** + **caption** (example output): "5200" / "INR Monthly Savings*", "6.24" / "Lakh Savings Over 25 Years*", "4.5" / "Years Payback Period*". **paragraph** ("*Estimates based on average solar irradiance for your city, current electricity tariff, and 0.5% annual panel degradation. Actual results may vary."). **progress-bar** labeled "Bill Offset" at 90%.

6. **layout-row (Feature 4: Installation Process)** -> `comp_0_components_5`
   **eyebrow** ("Installation"), **heading** ("From Survey to Switch-On in 7 Days"). **columnsgrid** (4 columns) each with **counter-up** (day number) + **heading** (step name) + **caption** (description): "Day 1" / "Free Site Survey" / "Our engineer visits your home to assess roof structure, shadow analysis, and electrical capacity", "Day 2-3" / "Design & Approvals" / "Custom system design, net metering application, and DISCOM approval submission", "Day 4-6" / "Installation" / "Panel mounting, inverter installation, wiring, and earthing by certified technicians", "Day 7" / "Commissioning" / "System testing, net meter installation, monitoring app setup, and handover". **video** (timelapse of a rooftop installation from bare roof to operational system). **paragraph** ("All installations performed by MNRE-certified technicians with zero roof penetration mounting systems. No structural damage to your terrace."). **badge** ("7-Day Installation Guarantee").

7. **layout-row (Feature 5: Battery Storage)** -> `comp_0_components_6`
   Left column: **image** (wall-mounted lithium battery storage unit in a home utility room). Right column: **eyebrow** ("Battery Backup"), **heading** ("Add Energy Storage"), **paragraph** ("Pair your solar system with a lithium-ion battery bank to store excess daytime generation for evening and nighttime use. Essential for areas with frequent power cuts or for maximizing self-consumption."). **columnsgrid** (3 columns) each with **heading** + **caption**: "5 kWh Battery" / "INR 1,80,000 -- 4-6 hours backup for essentials (lights, fans, WiFi, fridge)" + **button** ("Add"), "10 kWh Battery" / "INR 3,20,000 -- 8-10 hours backup including AC and heavy loads" + **button** ("Add"), "No Battery" / "INR 0 -- Grid-tied only, use net metering credits for night consumption" + **button** ("Selected"). **paragraph** ("Battery adds 3-5 years to the payback period but provides energy independence during outages."). **badge** ("10-Year Battery Warranty").

8. **layout-row (Feature 6: Warranty & Lifespan)** -> `comp_0_components_7`
   Left column: **eyebrow** ("Warranty"), **heading** ("Built to Last 25+ Years"), **paragraph** ("Your Tata Power Solar system comes with one of the most comprehensive warranty packages in the industry, protecting your investment for decades."). Right column: **columnsgrid** (3 columns) each with **counter-up** + **caption**: "25" / "Year Panel Performance Warranty (min 80% output at year 25)", "10" / "Year Inverter Warranty", "5" / "Year Workmanship & Installation Warranty". **accordion** with items: "Panel Performance Guarantee (Linear degradation: max 0.5%/year, min 80% at year 25)", "Inverter Coverage (Free replacement or repair for 10 years)", "Mounting Structure (10-year corrosion and structural warranty)", "Annual Maintenance Contract (Optional AMC: INR 5,000/year for cleaning and inspection)". **progress-bar** labeled "Expected Lifespan" at 100% (representing 25+ years). **caption** ("Most panels continue generating at 70%+ capacity beyond 30 years.").

9. **layout-row (Feature 7: Government Subsidies)** -> `comp_0_components_8`
   Left column: **image** (PM Surya Ghar scheme logo / government solar promotion visual). Right column: **eyebrow** ("Subsidies"), **heading** ("Government Incentives"), **paragraph** ("The PM Surya Ghar Muft Bijli Yojana provides a direct subsidy of up to INR 78,000 for residential rooftop solar installations up to 3kW, and INR 78,000 + INR 15,000/kW for 3-10kW systems."). **columnsgrid** (2 columns): Column 1 -- **heading** ("Your 5kW System") + **paragraph** ("System Cost: INR 2,85,000") + **paragraph** ("Central Subsidy: -INR 78,000") + **br** + **heading** ("Net Cost: INR 2,07,000") + **badge** ("27% Subsidy"); Column 2 -- **heading** ("Additional Benefits") + **accordion** with items: "Accelerated Depreciation (For commercial: 40% in year 1)", "Net Metering (Sell excess power back to the grid)", "Tax Benefits (No GST on residential solar systems up to 5kW)", "State-Level Incentives (Vary by state -- check eligibility)". **button** ("Check Your Subsidy Eligibility"). **caption** ("Subsidy amount and eligibility subject to government policy. We handle all paperwork.").

10. **layout-row (Feature 8: ROI Timeline)** -> `comp_0_components_9`
    **eyebrow** ("Return on Investment"), **heading** ("Your 25-Year Solar Journey"). **columnsgrid** (1 column, stacked timeline): **layout-row** with **badge** ("Year 0") + **paragraph** ("Investment: INR 2,07,000 (after subsidy). System goes live. Savings begin immediately."), **layout-row** with **badge** ("Year 1-4") + **paragraph** ("Cumulative savings: INR 2,08,000. System pays for itself by end of year 4.") + **progress-bar** at 40%, **layout-row** with **badge** ("Year 5-10") + **paragraph** ("Cumulative savings: INR 5,20,000. Pure profit from year 5 onward. System generating free electricity.") + **progress-bar** at 70%, **layout-row** with **badge** ("Year 11-25") + **paragraph** ("Cumulative savings: INR 15,60,000+. Over 7x return on investment. Panel still at 85%+ efficiency.") + **progress-bar** at 100%. **counter-up** + **caption**: "750" / "% Total ROI Over 25 Years". **paragraph** ("Savings increase annually as electricity tariffs rise 3-5% per year while solar generation cost remains zero.").

11. **layout-row (Feature 9: Monitoring App)** -> `comp_0_components_10`
    Left column: **image** (smartphone showing the Tata Power Solar monitoring app with real-time generation dashboard -- daily graph, lifetime generation counter, CO2 offset). Right column: **eyebrow** ("Smart Monitoring"), **heading** ("Track Every Watt"), **paragraph** ("The Tata Power Solar app gives you real-time visibility into your system's performance. Monitor daily, monthly, and lifetime generation, track savings, receive maintenance alerts, and share your environmental impact."). **columnsgrid** (3 columns) with **icon** + **caption**: "Real-Time Dashboard" / "Live generation and consumption data", "Performance Alerts" / "Notifications if system underperforms", "Savings Tracker" / "Cumulative INR and kWh savings". **paragraph** ("Available on iOS and Android. WiFi-enabled inverter connects automatically."). **button** ("View App Demo").

12. **layout-row (Feature 10: Environmental Impact)** -> `comp_0_components_11`
    **eyebrow** ("Your Impact"), **heading** ("Power the Planet"). **columnsgrid** (4 columns) with **counter-up** + **caption**: "165" / "Tonnes CO2 Offset Over 25 Years", "2700" / "Trees Equivalent Planted", "16500" / "kWh Clean Energy Per Year", "25" / "Years of Zero-Emission Power". **paragraph** ("By switching to solar, your household eliminates the equivalent carbon emissions of driving a car 400,000 km. You're not just saving money -- you're protecting the future."). **image** (aerial of green forest transitioning to solar farm -- environmental impact visualization). **badge** ("Carbon Neutral Home").

13. **layout-row (Reviews & Case Studies)** -> `comp_0_components_12`
    **eyebrow** ("Customer Stories"), **heading** ("Real Homes, Real Savings"). **columnsgrid** (3 columns) each with **image** (customer's home with panels), **blockquote** (testimonial with savings mentioned), **rating** (stars), **caption** (customer name + city + system size + "Verified Installation"). **counter-up** + **caption**: "50000" / "Happy Solar Homes". **button** ("Read All Stories").

14. **layout-row (Related Systems)** -> `comp_0_components_13`
    **heading** ("Other System Sizes"). **columnsgrid** (4 columns) each with **image** (system), **heading** (system size), **caption** (ideal for + price), **button** ("View Details"): "3kW System" / "1-2 BHK, INR 1,89,000*", "5kW System" / "3-4 BHK, INR 2,85,000*" + **badge** ("Popular"), "8kW System" / "Bungalow/Villa, INR 4,10,000*", "10kW System" / "Large Home + EV, INR 5,00,000*". **caption** ("*Prices before subsidy. Subsidy reduces cost by up to 40%.").

15. **layout-row (Footer)**
    **columnsgrid** (4 columns): Solutions (Residential, Commercial, Industrial, Off-Grid), Resources (Savings Calculator, Subsidy Guide, Installation FAQ, Blog), Company (About Tata Power Solar, Careers, Investor Relations, CSR), Support (Warranty Claims, AMC Plans, Monitoring Help, Contact). **br** (divider). **caption** (copyright, "India's most trusted solar brand. BIS certified. MNRE approved.").

---

## Variant B -- Product Launch / Landing Page

> Marketing-focused single-page layout for a new solar product or campaign launch

**Page: Product Launch (e.g., "Tesla Solar Roof -- Now Available in India")**

1. **titlebar** -- Brand logo, minimal nav (Solar Roof, How It Works, Savings, Order), "Order Now" button.

2. **layout-row (Hero)** -- Full-width **video-background** (cinematic drone footage zooming from a sun-drenched neighborhood to a single home with Tesla Solar Roof tiles -- indistinguishable from premium roofing, then pulling back to show the entire street going solar). Overlay: **eyebrow** ("The Invisible Solar Solution"), **heading** ("Tesla Solar Roof"), **paragraph** ("Every tile generates clean energy. No panels. No compromise."), **button** ("Design Your Solar Roof"), **button** ("Calculate Savings").

3. **layout-row (The Technology)** -- Dark background. **heading** ("Solar, Reimagined"). **columnsgrid** (3 columns) with **counter-up** + **caption**: "72" / "W Per Tile", "25" / "Year Warranty", "3x" / "Stronger Than Standard Roofing". **paragraph** ("Tempered glass solar tiles replace your existing roof, generating electricity while providing superior weather protection."). **image** (close-up of solar tile showing the texture that makes it look like a traditional roof tile).

4. **layout-row (Savings Promise)** -- **heading** ("Lower Your Bills. Raise Your Home Value."), **columnsgrid** (2 columns): Left -- **counter-up** stats: "60" / "% Average Bill Reduction", "30" / "Year Expected Lifespan"; Right -- **image** (home value appreciation chart showing solar premium). **paragraph** ("Homes with solar sell for 4-6% more than comparable non-solar homes.").

5. **layout-row (Powerwall Integration)** -- **heading** ("Add Powerwall for Full Independence"), **image** (Powerwall unit mounted in garage), **paragraph** ("Store solar energy for nighttime use and power outage protection."), **columnsgrid** (2 columns) with **counter-up** + **caption**: "13.5" / "kWh Storage Per Powerwall", "7" / "Days Backup (Essential Loads)".

6. **layout-row (Installation)** -- **heading** ("Professional Installation"), **columnsgrid** (4 columns) timeline steps with **icon** + **heading** + **caption**: "Design" / "Custom roof design using satellite imagery", "Permits" / "We handle all local permits and approvals", "Install" / "1-2 week installation by Tesla-certified crew", "Power On" / "System activation and app monitoring setup".

7. **layout-row (Order CTA)** -- **heading** ("Design Your Solar Roof"), **paragraph** ("Enter your address to get a custom design and savings estimate"), **form** with **textbox** (Address), **button** ("Get Started"). **caption** ("USD 100 fully refundable deposit to reserve your order.").

8. **layout-row (Footer)** -- Minimal footer with Tesla Energy links, legal disclaimers, privacy policy.

---

## Variant C -- Product Catalog / Comparison Page

> Multi-product browsing layout for a solar brand's full product range

**Page: Product Range (e.g., "Luminous Solar -- All Products")**

1. **titlebar** -- Brand logo, nav (Rooftop Solar, Panels, Inverters, Batteries, Accessories, Calculator), search, "Find Dealer" button.

2. **layout-row (Hero)** -- **heading** ("Solar Solutions for Every Need"), **paragraph** ("From residential rooftops to commercial installations, find the right solar system for your energy goals"), **image** (range of products -- panels, inverters, batteries arranged together). **button** ("Use Savings Calculator").

3. **layout-row (Category Selector)** -- **tabs** (By Application: "Home Rooftop", "Commercial", "Off-Grid", "Solar Water Heater") each filtering the product grid.

4. **layout-row (Category: Rooftop Systems)** -- **eyebrow** ("Complete Systems"), **heading** ("Rooftop Solar Packages"). **columnsgrid** (3 columns) each card: **image** (system on roof), **badge** ("Bestseller" / "Subsidy Eligible" / "New"), **heading** (system size), **caption** (ideal for + monthly savings estimate), **paragraph** (key specs -- panel count, inverter, warranty), **counter-up** + **caption** (monthly savings), **button** ("Get Quote"), **button** ("Compare").

5. **layout-row (Category: Solar Panels)** -- Same card pattern. **eyebrow** ("Panels"), **heading** ("High-Efficiency Solar Panels"). Cards show wattage, efficiency, dimensions.

6. **layout-row (Category: Inverters & Batteries)** -- Same card pattern. **eyebrow** ("Power Electronics"), **heading** ("Inverters & Storage").

7. **layout-row (Comparison Tool)** -- **heading** ("Compare Systems Side by Side"). **columnsgrid** (3 columns) each with **dropdown** (select system). Comparison rows: System Size, Panel Count, Panel Efficiency, Inverter Type, Battery Option, Monthly Savings, Payback Period, Warranty, Price Before Subsidy, Price After Subsidy.

8. **layout-row (Subsidy Guide)** -- **heading** ("Government Subsidy Guide"), **paragraph** ("Check your eligibility and estimated subsidy amount"), **columnsgrid** (3 columns) with system size tiers and subsidy amounts, **button** ("Check Eligibility"). **link** ("Read Complete Subsidy FAQ").

9. **layout-row (Free Survey CTA)** -- **heading** ("Get a Free Site Survey"), **paragraph** ("Our solar engineers will assess your roof, design your system, and provide a detailed savings report -- absolutely free"), **form** with **textbox** (Name), **textbox** (Phone), **textbox** (Pincode), **dropdown** (Monthly Bill Range), **button** ("Book Free Survey"). **counter-up** + **caption**: "100000" / "Free Surveys Completed".

10. **layout-row (Footer)** -- Full footer with product categories, resources (calculator, subsidy guide, FAQ, blog), company info, dealer network, social links, legal. **caption** ("BIS Certified | MNRE Channel Partner | 25-Year Performance Warranty").
