# Food Festival / Culinary Event / Food Carnival

> Focus: Celebrating food culture through vendor showcases, tasting experiences, chef demos, and community gathering around cuisine

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Taste of London | tastefestivals.com/london | Hero video of sizzling dishes, chef lineup carousel, tiered ticket packages with session times |
| World Street Food Congress | wsfcongress.com | Bold street food photography, vendor map integration, countdown to event, cultural storytelling |
| Smorgasburg | smorgasburg.com | Grid-based vendor directory with food photography, location/date prominently displayed, minimal clean layout |
| Epcot Food & Wine Festival | disneyworld.disney.go.com/events-tours/epcot/epcot-international-food-and-wine-festival | Schedule accordion, marketplace listings, themed booth descriptions, badge-style dietary labels |
| The Big Feastival | thebigfeastival.com | Split hero with music + food branding, family-friendly imagery, tiered ticket comparison, chef bio cards |

**Patterns to incorporate:**
- Large hero imagery of vibrant, colorful food with event date/location overlay and countdown timer
- Vendor/chef lineup presented as visual card grids with cuisine type badges
- Tiered ticket pricing (general admission, VIP tasting pass, all-access) with clear benefit lists
- Interactive schedule organized by day/stage/cuisine type using tabs or accordion
- Map or venue layout section showing food zones, stages, and amenities
- Counter-up stats (vendors, cuisines represented, dishes available, past attendees)
- Prominent dietary/cuisine type badges (vegan, gluten-free, halal, street food, fine dining)
- Social proof through rating components, testimonial carousels, and past event photo galleries

---

## Variant A — Street Food Festival

**Page: Home (Single Page)**

1. **titlebar**
   - Festival logo/wordmark on left (e.g., "StreetBite Fest")
   - Navigation links: Vendors, Schedule, Tickets, Map, FAQ
   - **button** — "Get Tickets" in bold accent color (orange or red)
   - **hamburger** — mobile menu with same navigation items

2. **layout-row (Hero)**
   - Full-width background **image** of a bustling street food market at golden hour, vendors serving from stalls, steam rising
   - **eyebrow** — "AUGUST 15-17, 2026 | DOWNTOWN WATERFRONT PARK"
   - **heading** (h1) — "The Ultimate Street Food Experience"
   - **paragraph** — "Three days. 80+ vendors. Flavors from every corner of the globe. Come hungry, leave inspired."
   - **countdown** — counting down to festival opening day
   - **layout-row** with two **button** components — "Buy Tickets" (primary) and "See the Lineup" (outline/secondary)

3. **layout-row (Stats Bar)**
   - Dark background strip with **counter-up** components in a row
   - "80+" vendors, "25" cuisine types, "50,000+" expected attendees, "3" days of food

4. **layout-row (About the Festival)**
   - Two-column layout: **layout-column** with **image** (overhead shot of diverse food spread on a long communal table) and **layout-column** with text
   - **eyebrow** — "ABOUT THE FEST"
   - **heading** (h2) — "Where the World Eats Together"
   - **paragraph** — description of the festival's mission to bring global street food culture to one location, celebrating authenticity, craft, and community
   - **paragraph** — mention of cooking demos, eating competitions, live music stages, and kids' food zone
   - **button** — "Our Story"

5. **layout-row (Featured Vendors)**
   - **eyebrow** — "THE LINEUP"
   - **heading** (h2) — "Featured Vendors"
   - **paragraph** — "From Bangkok noodles to Mexican elote, meet the vendors bringing flavor to the festival."
   - **columnsgrid** — 3-column grid of vendor cards, each card is a **layout-column** containing:
     - **image** — signature dish photo from the vendor
     - **heading** (h4) — vendor name (e.g., "Bao Brothers", "Taco Madre", "Smoke & Fire BBQ")
     - **badge** — cuisine type tag (e.g., "Taiwanese", "Mexican", "Southern BBQ")
     - **paragraph** — one-line vendor description and must-try dish
   - **button** — "View All 80+ Vendors"

6. **layout-row (Food Zones)**
   - **heading** (h2) — "Explore the Food Zones"
   - **tabs** — each tab represents a festival zone:
     - Tab 1: "Global Street" — description of international street food vendors, Asian, Latin, Middle Eastern, African
     - Tab 2: "Smoke Alley" — BBQ pits, smokers, grilled meats section
     - Tab 3: "Sweet Street" — desserts, pastries, ice cream, bubble tea vendors
     - Tab 4: "Craft Drinks" — local breweries, kombucha, fresh juices, cocktail bars
     - Tab 5: "Kids' Kitchen" — family-friendly food zone with interactive stations
   - Each tab panel contains **paragraph** text, an **image**, and relevant **badge** components for dietary options

7. **layout-row (Schedule)**
   - **eyebrow** — "WHAT'S HAPPENING"
   - **heading** (h2) — "Festival Schedule"
   - **tabs** — one tab per day (Friday, Saturday, Sunday)
   - Each tab contains an **accordion** with time-slot sections:
     - "11:00 AM — Gates Open & Welcome" with **paragraph** details
     - "12:00 PM — Chef Demo: Street Tacos with Chef Maria Santos" with **paragraph** and **badge** ("Live Demo")
     - "2:00 PM — Hot Wing Eating Competition" with **paragraph** and **badge** ("Competition")
     - "4:00 PM — DJ Set & Food Court Social Hour" with **paragraph**
     - "7:00 PM — Night Market Opens" with **paragraph** and **badge** ("After Dark")

8. **layout-row (Tickets)**
   - Gradient or dark background
   - **eyebrow** — "TICKETS"
   - **heading** (h2) — "Choose Your Pass"
   - **columnsgrid** — 3-column pricing layout:
     - **layout-column** — "Day Pass" at $25: **heading** (h3), **paragraph** (price), list via multiple **paragraph** lines (general admission, access to all zones, one drink token), **button** ("Buy Day Pass")
     - **layout-column** — "Weekend Pass" at $60 with **badge** ("Best Value"): **heading** (h3), **paragraph** (price), benefits including priority entry and three drink tokens, **button** ("Buy Weekend Pass") in highlighted style
     - **layout-column** — "VIP Tasting Pass" at $120: **heading** (h3), **paragraph** (price), benefits including VIP lounge, unlimited tastings from 10 premium vendors, chef meet-and-greet, **button** ("Buy VIP Pass")

9. **carousel (Past Festival Gallery)**
   - **heading** (h2) — "Scenes from Last Year"
   - Carousel of **image** slides showing past festival moments: crowds enjoying food, close-up of dishes, vendor interactions, night market lights, families eating together

10. **layout-row (Testimonials)**
    - **eyebrow** — "WHAT PEOPLE SAY"
    - **heading** (h2) — "Festival Reviews"
    - **columnsgrid** — 3-column grid of testimonial cards:
      - Each card: **rating** (4-5 stars), **blockquote** with attendee quote about the experience, **caption** with attendee name and year attended

11. **layout-row (Venue & Getting There)**
    - Two-column layout:
    - **layout-column** — **heading** (h3) "Find Us", **paragraph** with full venue address, **accordion** with "By Car" (parking info), "By Transit" (bus/train routes), "By Rideshare" (drop-off zone details)
    - **layout-column** — **image** of illustrated venue map showing food zones, stages, restrooms, and entry gates

12. **layout-row (Newsletter & Sponsors)**
    - **heading** (h3) — "Stay in the Loop"
    - **paragraph** — "Sign up for vendor announcements, early-bird tickets, and surprise menu reveals."
    - **form** with **textbox** (email), **button** ("Subscribe")
    - **br**
    - **heading** (h4) — "Proudly Sponsored By"
    - **ticker** — scrolling sponsor logos as **image** components

13. **layout-row (Footer)**
    - **columnsgrid** — 4-column footer layout:
      - Column 1: Festival logo, **paragraph** with tagline and dates
      - Column 2: **heading** (h5) "Quick Links", **link** components (Vendors, Schedule, Tickets, FAQ, Contact)
      - Column 3: **heading** (h5) "Connect", **link** components (Instagram, TikTok, Facebook, Twitter)
      - Column 4: **heading** (h5) "Contact", **paragraph** (email and phone), **paragraph** (venue address)
    - **br**
    - **caption** — "2026 StreetBite Festival. All rights reserved."

---

## Variant B — Wine & Dine / Gourmet Experience

**Page: Home (Single Page)**

1. **titlebar**
   - Elegant serif logo on left (e.g., "Harvest & Vine")
   - Navigation links: Experience, Chefs, Tastings, Tickets, Gallery
   - **button** — "Reserve Your Seat" in deep burgundy or gold
   - **hamburger** — mobile menu

2. **layout-row (Hero)**
   - Full-width **image** background of an elegant outdoor long-table dinner at sunset, wine glasses catching light, candlelit ambiance
   - **eyebrow** — "SEPTEMBER 26-28, 2026 | NAPA VALLEY ESTATE GROUNDS"
   - **heading** (h1) — "An Evening of Extraordinary Taste"
   - **paragraph** — "A curated culinary journey pairing world-class wines with Michelin-starred cuisine under the stars."
   - **countdown** — elegant countdown timer to the opening night gala
   - **button** — "Secure Your Place" (gold accent)

3. **layout-row (Introduction)**
   - Centered text layout with generous white space
   - **eyebrow** — "THE EXPERIENCE"
   - **heading** (h2) — "Where Fine Wine Meets Fine Dining"
   - **paragraph** — detailed description of the three-day gourmet event featuring intimate tasting sessions, multi-course dinners prepared by acclaimed chefs, vineyard tours, sommelier-led masterclasses, and artisan food markets
   - **br**
   - **layout-row** with **counter-up** components — "12" Michelin Stars (combined), "40" Wineries, "8" Guest Chefs, "500" Exclusive Seats

4. **layout-row (Featured Chefs)**
   - **eyebrow** — "THE CULINARY ARTISTS"
   - **heading** (h2) — "Our Guest Chefs"
   - **columnsgrid** — 2x2 grid of chef profile cards, each **layout-column** containing:
     - **image** — professional portrait of the chef in their kitchen
     - **heading** (h3) — chef name (e.g., "Chef Elena Marchetti")
     - **badge** — accolade (e.g., "2 Michelin Stars", "James Beard Award Winner")
     - **caption** — restaurant name and location
     - **paragraph** — brief bio highlighting their culinary philosophy and what they'll be preparing at the event
   - **button** — "Meet All Chefs"

5. **layout-row (Tasting Experiences)**
   - **eyebrow** — "CURATED EXPERIENCES"
   - **heading** (h2) — "The Tastings"
   - **tabs** — each tab is a tasting category:
     - Tab 1: "Grand Wine Tasting" — **paragraph** describing open-floor tasting of 120+ wines from 40 vineyards, **image** of wine tasting hall, **badge** components ("Red", "White", "Rose", "Sparkling")
     - Tab 2: "Chef's Table Dinners" — **paragraph** about intimate 20-seat multi-course dinners, **image** of plated fine dining dish, **badge** ("Reservation Required")
     - Tab 3: "Masterclasses" — **paragraph** about sommelier and chef-led workshops (wine pairing, cheese making, pasta from scratch), **image** of hands-on class
     - Tab 4: "Artisan Market" — **paragraph** about curated marketplace with local cheesemakers, charcuterie, olive oils, chocolatiers, **image** of artisan stall

6. **layout-row (Schedule Overview)**
   - Elegant dark background (deep navy or charcoal)
   - **heading** (h2) — "Three Evenings, One Unforgettable Journey"
   - **columnsgrid** — 3-column layout, one per evening:
     - **layout-column** — **heading** (h3) "Night One: The Grand Opening", **eyebrow** "FRIDAY, SEPT 26", **paragraph** describing welcome champagne reception, grand tasting hall opens, live jazz ensemble, opening chef's table dinner
     - **layout-column** — **heading** (h3) "Night Two: The Masterclass", **eyebrow** "SATURDAY, SEPT 27", **paragraph** describing morning vineyard tour, afternoon masterclasses, evening multi-course pairing dinner under the stars
     - **layout-column** — **heading** (h3) "Night Three: The Farewell Feast", **eyebrow** "SUNDAY, SEPT 28", **paragraph** describing artisan market brunch, final grand dinner with all chefs collaborating, awards ceremony

7. **layout-row (Wine Partners)**
   - **eyebrow** — "FEATURED VINEYARDS"
   - **heading** (h2) — "Our Wine Partners"
   - **ticker** — scrolling vineyard/winery logos as **image** components
   - **paragraph** — "Featuring selections from over 40 renowned vineyards across Napa, Sonoma, Bordeaux, and Tuscany."

8. **layout-row (Tickets & Packages)**
   - **eyebrow** — "RESERVATIONS"
   - **heading** (h2) — "Select Your Experience"
   - **columnsgrid** — 3-column pricing:
     - **layout-column** — "Tasting Pass" at $175: **heading** (h3), **paragraph** (price), benefits (access to grand tasting, artisan market, one masterclass), **button** ("Reserve Tasting Pass")
     - **layout-column** — "Gourmet Package" at $450 with **badge** ("Most Popular"): **heading** (h3), **paragraph** (price), benefits (all tasting pass perks plus two chef's table dinners, vineyard tour, sommelier session), **button** ("Reserve Gourmet Package")
     - **layout-column** — "Connoisseur Experience" at $850: **heading** (h3), **paragraph** (price), benefits (full three-day access, all dinners, private vineyard tour, signed cookbook, concierge service), **button** ("Reserve Connoisseur")

9. **carousel (Ambiance Gallery)**
   - **heading** (h2) — "A Glimpse of the Evening"
   - Carousel of **image** slides: long table dinner setup at dusk, wine being poured, plated courses, vineyard landscape, guests mingling, chef plating in open kitchen

10. **layout-row (Testimonials)**
    - Soft cream or warm background
    - **eyebrow** — "GUEST REFLECTIONS"
    - **heading** (h2) — "What Our Guests Say"
    - **columnsgrid** — 2-column layout of testimonial cards:
      - Each card: **blockquote** with eloquent guest quote about the experience, **rating** (5 stars), **caption** with guest name and year, **badge** ("Returning Guest" on some)

11. **layout-row (Venue Details)**
    - Two-column layout:
    - **layout-column** — **image** of the estate venue, sprawling grounds with vineyard backdrop
    - **layout-column** — **heading** (h3) "The Venue", **paragraph** describing the private estate location with capacity, outdoor dining terrace, barrel room, garden areas, **accordion** with "Accommodation" (partner hotel info), "Dress Code" (smart casual to evening attire), "Dietary Requirements" (customization form available), "Transportation" (shuttle service from nearby hotels)

12. **layout-row (RSVP / Contact)**
    - **heading** (h3) — "Join Our Private List"
    - **paragraph** — "Be the first to receive invitations, menu previews, and exclusive early booking access."
    - **form** with **textbox** (full name), **textbox** (email), **dropdown** (preferred experience: Tasting Pass / Gourmet / Connoisseur), **button** ("Request Invitation")

13. **layout-row (Footer)**
    - **columnsgrid** — 3-column footer:
      - Column 1: Event logo, **paragraph** with dates and venue, **caption** with tagline "Taste the extraordinary"
      - Column 2: **heading** (h5) "Navigate", **link** components (Experience, Chefs, Tastings, Tickets, Contact, Privacy Policy)
      - Column 3: **heading** (h5) "Follow the Journey", **link** components (Instagram, Facebook, Pinterest), **paragraph** with email contact
    - **br**
    - **caption** — "2026 Harvest & Vine Culinary Experience. All rights reserved."

---

## Variant C — Cooking Competition / MasterChef Event

**Page: Home (Single Page)**

1. **titlebar**
   - Bold, energetic logo (e.g., "Iron Spatula Championship")
   - Navigation links: Competition, Judges, Register, Schedule, Watch Live
   - **button** — "Register to Compete" in fiery red/orange
   - **hamburger** — mobile menu

2. **layout-row (Hero)**
   - High-energy **image** background of a cooking competition in action — flames, chefs plating under time pressure, dramatic lighting
   - **eyebrow** — "NOVEMBER 14-15, 2026 | CONVENTION CENTER MAIN STAGE"
   - **heading** (h1) — "Do You Have What It Takes?"
   - **paragraph** — "The ultimate amateur cooking showdown. 64 competitors. 5 rounds. One champion. $25,000 grand prize."
   - **countdown** — bold countdown to registration deadline
   - **layout-row** with two **button** components — "Register Now" (primary, bold) and "Watch Last Year's Final" (secondary with play icon reference)

3. **layout-row (Competition Stats)**
   - Dark background with bold typography
   - **counter-up** components in a row — "64" Competitors, "5" Rounds, "$25,000" Grand Prize, "10,000+" Live Audience, "3" Celebrity Judges

4. **layout-row (How It Works)**
   - **eyebrow** — "THE FORMAT"
   - **heading** (h2) — "How the Competition Works"
   - **columnsgrid** — 5-column process steps:
     - Each **layout-column** contains **icon** (numbered or themed), **heading** (h4) with step name, **paragraph** with description:
     - Step 1: "Apply" — submit your application with a signature dish description and 60-second video
     - Step 2: "Qualify" — top 64 selected by judges panel from applications
     - Step 3: "Compete" — head-to-head elimination rounds with mystery ingredients and time limits
     - Step 4: "Survive" — semi-finals with themed challenges (dessert, fusion, street food)
     - Step 5: "Win" — grand finale: 3-course meal in 90 minutes judged on taste, presentation, creativity

5. **layout-row (Meet the Judges)**
   - **eyebrow** — "THE PANEL"
   - **heading** (h2) — "Meet Your Judges"
   - **columnsgrid** — 3-column judge profiles:
     - Each **layout-column**: **image** (professional headshot of judge), **heading** (h3) — judge name (e.g., "Chef Marcus Thompson"), **badge** components for credentials ("Michelin Star", "TV Host", "Cookbook Author"), **paragraph** — bio describing their culinary background, restaurant empire, and what they look for in a competitor
   - **blockquote** — a pull quote from the head judge about what makes a champion

6. **layout-row (Competition Categories)**
   - **heading** (h2) — "Competition Divisions"
   - **tabs** — one tab per division:
     - Tab 1: "Open Division" — **paragraph** describing the main 64-person bracket, ages 18+, any cuisine style, **badge** ("$25,000 Prize")
     - Tab 2: "Junior Chef (Ages 13-17)" — **paragraph** about the youth bracket, 16 competitors, adapted time limits, **badge** ("$5,000 Prize")
     - Tab 3: "Team Battle (Pairs)" — **paragraph** about 2-person team format, 16 teams, collaborative cooking challenge, **badge** ("$10,000 Prize")
     - Tab 4: "Bake-Off Special" — **paragraph** about dedicated baking/pastry competition, separate judging criteria, **badge** ("$10,000 Prize")

7. **layout-row (Schedule)**
   - **eyebrow** — "EVENT SCHEDULE"
   - **heading** (h2) — "Two Days of Culinary Combat"
   - **tabs** — Day 1 and Day 2:
   - Each tab contains **accordion** sections:
     - Day 1: "9:00 AM — Doors Open & Competitor Check-In", "10:00 AM — Opening Ceremony & Rules Briefing", "11:00 AM — Round 1: The Mystery Box (64 to 32)", "2:00 PM — Round 2: The Speed Challenge (32 to 16)", "5:00 PM — Junior Chef Finals", "7:00 PM — Evening Food Market & Live Entertainment"
     - Day 2: "10:00 AM — Round 3: Fusion Frenzy (16 to 8)", "1:00 PM — Semi-Finals: The Pressure Test (8 to 3)", "3:00 PM — Team Battle Grand Final", "5:00 PM — Bake-Off Showdown", "7:00 PM — Grand Finale: The Championship Round", "9:00 PM — Awards Ceremony & Champion Crowned"
   - Each accordion item has **paragraph** with details and **badge** for round type

8. **layout-row (Registration)**
   - Bold background color or gradient
   - **eyebrow** — "ENTER THE ARENA"
   - **heading** (h2) — "Register to Compete"
   - **paragraph** — "Applications close October 15, 2026. Submit your details and a description of your signature dish. Top 64 applicants will be notified by October 25."
   - **form** containing:
     - **textbox** — Full Name
     - **textbox** — Email Address
     - **textbox** — Phone Number
     - **dropdown** — Division (Open / Junior Chef / Team Battle / Bake-Off)
     - **textarea** — "Describe your signature dish and why you should compete (200 words max)"
     - **textbox** — Link to 60-second cooking video (YouTube/Instagram)
     - **checkbox** — "I agree to the competition rules and terms"
     - **button** — "Submit Application"

9. **layout-row (Prizes)**
   - **eyebrow** — "WHAT'S AT STAKE"
   - **heading** (h2) — "The Prizes"
   - **columnsgrid** — 3-column prize tier layout:
     - **layout-column** — **heading** (h3) "Grand Champion", **heading** (h2, large) "$25,000", **badge** ("Open Division"), list via **paragraph** lines: cash prize, trophy, feature in Food Magazine, guest spot on cooking show, professional knife set
     - **layout-column** — **heading** (h3) "Runner-Up", **heading** (h2, large) "$10,000", list via **paragraph** lines: cash prize, silver medal, cookbook deal opportunity, kitchen equipment package
     - **layout-column** — **heading** (h3) "Third Place", **heading** (h2, large) "$5,000", list via **paragraph** lines: cash prize, bronze medal, culinary school scholarship, artisan ingredient hamper

10. **carousel (Past Competitions)**
    - **heading** (h2) — "Last Year's Highlights"
    - Carousel of **image** slides: intense cooking moments, judges tasting, champion holding trophy, crowd reactions, beautifully plated finalist dishes, behind-the-scenes prep

11. **layout-row (Spectator Info)**
    - Two-column layout:
    - **layout-column** — **heading** (h3) "Watch Live", **paragraph** about spectator tickets to watch the competition live on the main stage, food market access, meet the judges, **button** ("Buy Spectator Tickets — $35")
    - **layout-column** — **heading** (h3) "Stream Online", **paragraph** about free livestream of semi-finals and grand finale on YouTube and Twitch, sign up for stream reminders, **button** ("Set a Reminder")

12. **layout-row (Testimonials from Past Competitors)**
    - **eyebrow** — "FROM THE KITCHEN"
    - **heading** (h2) — "Past Competitor Stories"
    - **columnsgrid** — 3-column testimonials:
      - Each card: **image** (competitor photo), **blockquote** with their experience quote about the adrenaline, growth, and community, **caption** with name and year, **badge** ("2025 Finalist" or "2024 Champion")

13. **layout-row (Sponsors & Partners)**
    - **heading** (h3) — "Our Partners"
    - **ticker** — scrolling sponsor and partner logos as **image** components (kitchenware brands, food networks, culinary schools)
    - **br**

14. **layout-row (Footer)**
    - **columnsgrid** — 4-column footer:
      - Column 1: Competition logo, **paragraph** with event dates and venue, **caption** — "Where home cooks become champions"
      - Column 2: **heading** (h5) "Competition", **link** components (Rules, Format, Prizes, Past Winners, FAQ)
      - Column 3: **heading** (h5) "Attend", **link** components (Spectator Tickets, Livestream, Venue Map, Accommodation, Contact)
      - Column 4: **heading** (h5) "Follow Us", **link** components (YouTube, Instagram, TikTok, Twitter/X), **paragraph** with contact email
    - **br**
    - **caption** — "2026 Iron Spatula Championship. All rights reserved."
