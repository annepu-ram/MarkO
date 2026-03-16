# Musical Instruments — Product Pages

> Focus: Selling the sound and the dream through audio demos, material craftsmanship storytelling, brand heritage sections, and skill-level matching that helps musicians at every stage find their instrument.

## Real Website Examples & Key Insights

| Site | URL | Key Pattern |
|------|-----|-------------|
| Fender (Stratocaster) | fender.com/electric-guitars/stratocaster | Heritage hero with iconic silhouette; "Since 1954" brand story; pickup configuration selector; color/finish gallery with wood grain close-ups; artist signature series section; sound sample player per pickup position |
| Gibson (Les Paul) | gibson.com/les-paul | Craftsmanship-first hero (luthier workshop video); tone wood section (mahogany body, maple top); pickup comparison (P-90 vs PAF humbucker); custom shop callout; celebrity artist gallery; authenticity certificate section |
| Yamaha (Musical Instruments) | usa.yamaha.com/products/musical_instruments | Multi-instrument mega nav; skill-level filter (beginner, intermediate, advanced); technology explainer sections (CFX sampling, GrandTouch action); product comparison tool; artist endorsement grid; demo audio inline |
| Casio (Keyboards) | casio.com/keyboards | Budget-friendly positioning; lesson mode / learning feature section; sound library counter (700+ tones); key action comparison (weighted vs semi-weighted vs synth); size/portability comparison; USB-MIDI connectivity section |
| Roland | roland.com | Sound engine technology hero (SuperNATURAL, ZEN-Core); product series navigation (FP, RD, FANTOM); interactive sound demo player; stage vs studio vs home comparison; MIDI/DAW integration section; artist performance videos |

**Patterns to incorporate:**
- Audio demo player with sound samples (clean, distorted, acoustic, various presets)
- Material and tonewood section with close-up imagery (spruce, mahogany, rosewood)
- Craftsmanship gallery showing workshop/luthier process
- Brand heritage timeline ("Since 1946" / "Founded in Hamamatsu, Japan")
- Skill level indicator (beginner-friendly, intermediate, professional)
- Pickup/electronics configuration selector with tonal description
- Artist endorsement gallery with signature models
- Color/finish gallery with wood grain and hardware variations
- Size and weight comparison (especially for keyboards and acoustic guitars)
- Bundle deal (instrument + case + tuner + strap + picks)

---

## Variant A — Product Detail Page (Feature-Per-Section Trackable)

> Each feature section = separate layout-row = unique component ID = individually trackable

**Page: Guitar / Keyboard / Instrument Detail**

1. **titlebar** — Brand logo, nav links (Guitars, Keyboards, Drums, Accessories, Artists, Learn, Support), cart icon, search
2. **layout-row (Hero — Instrument Visual + Key Info)** → `comp_0_components_1`
   Left column: carousel (instrument front, back, headstock close-up, hardware detail, in-case, lifestyle/stage shot). Right column: eyebrow ("Electric Guitar — Made in Japan"), heading (instrument name + model), rating (4.8 stars, review count), paragraph (tagline: "Alder body. Rosewood fretboard. Three single-coil pickups. The sound that defined rock."), heading (price), badge ("Includes gig bag"), button ("Add to Cart"), button ("Buy Now"), caption ("Free shipping. 30-day return policy.").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Feature: Sound & Tone)** → `comp_0_components_2`
   Left column: heading ("The Sound That Changed Music") + paragraph (bright, articulate single-coil tone with bell-like cleans and punchy overdriven crunch, 5-way pickup selector for maximum tonal versatility). Accordion: Item 1 — "Position 1: Bridge Pickup" (bright, cutting, lead tones), Item 2 — "Position 2: Bridge + Middle" (funky, quacky, Hendrix-style), Item 3 — "Position 3: Middle Pickup" (warm, woody, clean rhythm), Item 4 — "Position 4: Middle + Neck" (glassy, smooth, R&B/jazz), Item 5 — "Position 5: Neck Pickup" (warm, full, blues and jazz). Right column: image (pickup close-up with magnetic pole pieces visible). Badge ("Audio Demos Available"). Caption ("Listen to sound samples for each pickup position.").
5. **layout-row (Feature: Material & Build)** → `comp_0_components_3`
   Heading ("Crafted from the Finest Tonewoods") + columnsgrid (3 columns): Column 1 — image (alder body wood close-up) + heading ("Alder Body") + paragraph ("Balanced tonal response with strong mids and good resonance. Lightweight and comfortable."). Column 2 — image (maple neck close-up) + heading ("Maple Neck") + paragraph ("Bright, snappy attack with excellent sustain. Bolt-on construction for easy adjustment."). Column 3 — image (rosewood fretboard) + heading ("Rosewood Fretboard") + paragraph ("Warm, smooth feel under the fingers. Rich overtones and natural oil finish."). Badge ("Premium Tonewoods").
6. **layout-row (Feature: Size & Weight)** → `comp_0_components_4`
   Left column: heading ("Built to Play for Hours") + paragraph (3.5 kg, 25.5-inch scale length, 9.5-inch fretboard radius, 22 medium jumbo frets) + counter-up (3.5) + caption ("kg Weight"). Right column: image (dimensional diagram showing total length, body width, scale length). columnsgrid (2 columns): Column 1 — caption ("Scale Length: 25.5 inches (648 mm)"). Column 2 — caption ("Nut Width: 42 mm (1.650 inches)"). Caption ("Comfortable for players with medium to large hands.").
7. **layout-row (Feature: Skill Level)** → `comp_0_components_5`
   Heading ("Who Is This Guitar For?") + columnsgrid (3 columns): Column 1 — icon + heading ("Beginner") + paragraph ("Forgiving action, comfortable neck shape, versatile tones for learning any genre.") + rating (4 out of 5 suitability). Column 2 — icon + heading ("Intermediate") + badge ("Ideal Match") + paragraph ("Responsive dynamics, full pickup versatility, reliable tuning stability for gigging.") + rating (5 out of 5 suitability). Column 3 — icon + heading ("Professional") + paragraph ("Recording-quality tone, professional hardware, stage-ready electronics.") + rating (5 out of 5 suitability). Caption ("Versatile enough for any skill level. Grows with your playing.").
8. **layout-row (Feature: Accessories Included)** → `comp_0_components_6`
   Heading ("What's in the Box") + columnsgrid (2 columns): Column 1 — paragraph (list: instrument, gig bag/hard case, tremolo arm, allen wrenches, documentation, warranty card). Column 2 — image (open case with instrument and accessories). Heading below ("Complete Your Setup") + columnsgrid (4 columns): Each — image + heading (amp, cable, tuner, strap) + caption (price) + button ("Add").
9. **layout-row (Feature: Brand Heritage)** → `comp_0_components_7`
   Heading ("A Legacy of Innovation") + paragraph (brand founding story, key milestones, iconic users). Counter-up (1954) + caption ("Year Introduced"). Ticker (scrolling iconic artist names or photos who played this model). Blockquote from brand founder or legendary artist about the instrument. Image (vintage workshop photo or historical product shot).
10. **layout-row (Feature: Setup & Tuning)** → `comp_0_components_8`
   Heading ("Play-Ready Out of the Box") + columnsgrid (3 columns): Column 1 — icon + heading ("Factory Setup") + paragraph ("Action, intonation, and truss rod professionally adjusted before shipping"). Column 2 — icon + heading ("Tuning Stability") + paragraph ("Sealed die-cast tuners hold tune through hours of playing and bends"). Column 3 — icon + heading ("Setup Guide Included") + paragraph ("QR code links to video setup guide for personalized adjustments"). Caption ("First-time setup? Our step-by-step video walks you through action, intonation, and pickup height.").
11. **layout-row (Feature: Price & Bundles)** → `comp_0_components_9`
    Heading ("Choose Your Package") + columnsgrid (3 columns): Column 1 — image + heading ("Instrument Only") + paragraph (guitar + gig bag) + heading (price) + button ("Buy Instrument"). Column 2 — image + heading ("Starter Bundle") + badge ("Most Popular") + paragraph (guitar + amp + cable + tuner + strap + picks + gig bag) + heading (bundle price) + badge ("Save Rs 5,000") + button ("Buy Bundle"). Column 3 — image + heading ("Pro Bundle") + paragraph (guitar + premium amp + pedalboard + cable set + hard case + stand) + heading (pro price) + badge ("Best Value") + button ("Buy Pro Bundle").
12. **layout-row (Feature: Demo Audio / Video)** → `comp_0_components_10`
    Heading ("Hear It Before You Buy") + paragraph ("Listen to sound demos recorded with this exact model in our studio."). Video (embedded demo video showing clean and overdriven tones across all pickup positions). Caption ("Recorded direct and through a tube amplifier. No post-processing."). Badge ("Studio-Recorded Demos").
13. **layout-row (Feature: Warranty & Care)** → `comp_0_components_11`
    Heading ("Protected for Years") + columnsgrid (2 columns): Column 1 — counter-up (2) + heading ("Year Limited Warranty") + paragraph ("Covers manufacturing defects in materials and workmanship. Register online for seamless claims."). Column 2 — heading ("Care Tips") + accordion: Item 1 — "String changing frequency" (every 2-4 weeks for regular players), Item 2 — "Cleaning the fretboard" (lemon oil every 6 months for rosewood), Item 3 — "Storage recommendations" (case, humidity 45-55%, avoid temperature extremes), Item 4 — "When to get a professional setup" (annually or when changing string gauge).
14. **layout-row (Reviews & Artist Gallery)** → `comp_0_components_12`
    Left column: heading ("Player Reviews") + rating (4.8 stars) + counter-up (3,240 reviews) + progress-bar (star distribution). Right column: heading ("Artists Who Play This Model") + carousel of artist photos with name + genre + blockquote about the instrument.
15. **layout-row (Related Instruments)** → `comp_0_components_13`
    Heading ("Explore Similar Models") + columnsgrid (4 columns): Each — image + heading (model name) + paragraph (key difference: different pickups, different wood, different price point) + caption (price) + button ("View").
16. **layout-row (Footer)** → `comp_0_components_14`
    columnsgrid (4 columns): Column 1 — Brand heritage + paragraph. Column 2 — links (Guitars, Keyboards, Drums, Accessories, Artists). Column 3 — links (Support, Warranty, Service Centers, Authorized Dealers). Column 4 — paragraph (contact) + links (social media).

---

## Variant B — Product Launch / Landing Page

> Heritage-meets-innovation marketing page for a new instrument line or signature model launch

**Page: "The Phoenix Series — Reborn From Legend"**

1. **titlebar** — Brand logo, minimal nav (The Story, Sound, Specs), CTA button ("Pre-Order Now")
2. **layout-row (Hero — Cinematic Heritage)** → Video-background (craftsman shaping guitar body in workshop, slow motion). Centered overlay: eyebrow ("Handcrafted in Japan"), heading ("The Phoenix Series"), paragraph ("Vintage soul. Modern precision. Your next lifelong instrument."), button ("Pre-Order — From Rs 89,999"), badge ("Limited Edition — 500 Pieces").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Heritage Story)** → Heading ("Born From 70 Years of Craft") + paragraph (brand history, the inspiration behind Phoenix series, the luthier who designed it). Counter-up (1954) + caption ("Year the Legacy Began"). Image (vintage workshop photo + modern workshop comparison).
5. **layout-row (Sound Showcase)** → Heading ("Hear the Difference") + video (side-by-side sound comparison: standard model vs Phoenix Series). Paragraph ("New wound pickups designed for clarity at high gain without sacrificing vintage warmth.").
6. **layout-row (Material Deep Dive)** → Carousel: Slide 1 — Aged mahogany body (story + close-up). Slide 2 — Flame maple top (story + close-up). Slide 3 — Ebony fretboard (story + close-up). Slide 4 — Nitrocellulose lacquer finish (story + close-up). Slide 5 — Hand-wound pickups (story + close-up).
7. **layout-row (Artist Endorsement)** → Full-width image (iconic artist playing the Phoenix). Blockquote from artist. Caption (name, career highlight). Badge ("Artist Signature Approval").
8. **layout-row (Spec Highlights)** → columnsgrid (4 columns): counter-up (22) + caption ("Frets"), counter-up (2) + caption ("Custom Pickups"), counter-up (3.4) + caption ("kg Weight"), counter-up (500) + caption ("Limited Run"). Heading ("Every Detail Matters").
9. **layout-row (Finish & Color Gallery)** → Heading ("Choose Your Finish") + columnsgrid (4 columns): Each — image (guitar in that finish: Vintage Sunburst, Midnight Black, Natural, Heritage Cherry) + caption (finish name). Badge ("Limited Colors").
10. **layout-row (Bundle Options)** → columnsgrid (2 columns): Column 1 — heading ("Guitar Only") + heading (price) + paragraph (guitar + hardshell case + certificate) + button ("Pre-Order"). Column 2 — heading ("Collector's Bundle") + heading (price) + badge ("Exclusive") + paragraph (guitar + premium amp + cables + picks + signed certificate + framed photo) + button ("Pre-Order Bundle").
11. **layout-row (Countdown & Urgency)** → Heading ("Only 500 Will Be Made") + countdown (pre-order deadline). Counter-up showing remaining units. Paragraph ("Each guitar individually numbered. Certificate of authenticity included.").
12. **layout-row (Final CTA)** → Heading ("Own a Piece of History") + button ("Pre-Order Now") + caption ("Deliveries begin April 2026. Free worldwide shipping.").
13. **layout-row (Footer)** → Minimal footer with brand heritage line, contact, social, legal.

---

## Variant C — Product Catalog / Comparison Page

> Multi-instrument browsing with skill-level filtering, brand comparison, and bundle discovery

**Page: "Musical Instruments — Guitars, Keyboards, Drums & More"**

1. **titlebar** — Brand logo (music store), nav (Guitars, Keyboards, Drums, Wind, Strings, Accessories, Learn, Deals), search, cart
2. **layout-row (Category Hero)** → Full-width music store/performance image. Heading ("Musical Instruments for Every Musician") + paragraph ("From first lesson to the big stage. Find your sound.") + eyebrow ("Free shipping on orders over Rs 4,999").
3. **br (divider)**
   Visual separator between hero and content sections.

4. **layout-row (Shop by Instrument)** → columnsgrid or ticker (horizontal): Electric Guitars, Acoustic Guitars, Bass, Keyboards/Pianos, Drums, Ukulele, Violin, Flute, Saxophone — each with icon + label + "from Rs X".
5. **layout-row (Shop by Skill Level)** → columnsgrid (3 columns): Column 1 — icon + heading ("Beginner") + paragraph ("Easy-to-play instruments with learning resources. Perfect for starting out.") + button ("Shop Beginner"). Column 2 — icon + heading ("Intermediate") + paragraph ("Quality craftsmanship and versatile features for developing players.") + button ("Shop Intermediate"). Column 3 — icon + heading ("Professional") + paragraph ("Premium materials, elite electronics, stage-ready performance.") + button ("Shop Professional").
6. **layout-row (Brand Comparison — Guitars)** → Heading ("Compare Top Guitar Brands") + columnsgrid (5 columns): Column 1 (labels: Origin, Price Range, Best For, Signature Sound, Warranty), Columns 2-5 (Fender, Gibson, Yamaha, Ibanez). Badges on "Best Value", "Best Tone", "Best for Beginners".
7. **layout-row (Bestsellers)** → Heading ("Bestsellers") + columnsgrid (4 columns): Each — image, badge ("Bestseller" / "Editor's Pick"), heading (instrument name), rating, paragraph (type + skill level + key feature), heading (price), button ("View Details").
8. **layout-row (Starter Bundles)** → Heading ("Starter Bundles — Everything to Begin Playing") + columnsgrid (3 columns): Guitar Starter (guitar + amp + cable + tuner + picks + strap + bag), Keyboard Starter (keyboard + stand + bench + headphones + pedal), Drum Starter (kit + sticks + throne + practice pad). Each with image, contents, bundle price, savings badge, button.
9. **layout-row (Demo Audio Section)** → Heading ("Hear the Instruments") + tabs: Tab 1 ("Electric Guitars" — audio player with sample clips per model), Tab 2 ("Acoustic Guitars" — audio samples), Tab 3 ("Keyboards" — tone samples), Tab 4 ("Drums" — beat samples). Each with instrument image, play button, brief description.
10. **layout-row (Buying Guide)** → Heading ("Instrument Buying Guide") + accordion: Item 1 ("Which guitar type is right for me?"), Item 2 ("Acoustic vs Digital piano — pros and cons"), Item 3 ("How to choose the right keyboard for beginners"), Item 4 ("Electric vs acoustic drums — which is better at home?"), Item 5 ("What size guitar for my child?"), Item 6 ("How much should I spend on my first instrument?").
11. **layout-row (Pre-Owned / Trade-In)** → Heading ("Trade In Your Old Instrument") + paragraph ("Get up to 40% of your old instrument's value toward a new purchase.") + columnsgrid (2 columns): Column 1 — heading ("How It Works") + paragraph (3-step process: submit, appraise, credit). Column 2 — button ("Get Trade-In Value") + caption ("Online valuation in 2 minutes").
12. **layout-row (Customer Reviews)** → Heading ("Musician Reviews") + carousel of review cards with instrument type, skill level, rating, blockquote.
13. **layout-row (Learn to Play Section)** → Heading ("Start Your Musical Journey") + columnsgrid (3 columns): Column 1 — link ("Free Online Lessons") + image (lesson screenshot). Column 2 — link ("Local Teachers") + image (teacher + student). Column 3 — link ("Sheet Music Library") + image (sheet music). Paragraph ("Every purchase includes 3 months of free online lessons.").
14. **layout-row (Newsletter)** → Left column: heading ("Music News, Tips & Deals") + form (textbox + button "Subscribe"). Right column: heading ("Need Help Choosing?") + paragraph + button ("Talk to a Musician").
15. **layout-row (Footer)** → columnsgrid (4 columns): Store info + history, instrument categories, brands, support + contact + social.
