# SwiftSites Style & Theme Reference

## Style: Modern Minimalist

Mood: clean, professional, functional, sleek, simple, trustworthy, corporate, minimal
Industries: SaaS, consulting, legal, healthcare, education, real estate, B2B, fintech, startup
Sections: hero, features, pricing, product, team, blog, contact, faq, stats, navigation

Themes:
1. Slate Professional — primary #1E3A5F, text #4B5563, secondary #C5D4E3, accent #0052CC, background #E8EDF2, fonts Inter/Inter
2. Warm Neutral — primary #2D3748, text #4A4540, secondary #E2D9CE, accent #D97706, background #FAF5EF, fonts Inter/Inter
3. Cool Sage — primary #1A3A2A, text #3D5040, secondary #D4E5D8, accent #16A34A, background #F0F7F2, fonts Inter/Inter
4. Ink & Paper — primary #1F2937, text #4B5563, secondary #D1D5DB, accent #4F46E5, background #FFFFFF, fonts Outfit/Inter

Properties:
- Container: radius sm, shadow soft, border none
- Card: radius sm, shadow soft, border width 1 color #e5e7eb
- Button: radius sm, shadow none, border none
- Heading: weight semibold, letterSpacing tight
- Body: weight regular
- Spacing: section paddingBlock xxxl, card paddingBlock xl paddingInline lg

Section style_notes:
- Hero: light bg, paddingBlock xxxl. paragraph *color-text. Split: wrap nowrap, both widthMode "50". Centered: single column horizontalAlign center
- Features: columnsgrid columns 3 gap lg. Cards radius sm shadow soft border 1px #e5e7eb. paragraph *color-text
- Pricing: columnsgrid columns 3. Popular card border *color-accent. paragraph *color-text
- Footer: inverted — bg *color-primary transparency 100, ALL text *color-background
- CTA: bg *color-accent transparency 100, text *color-background, paddingBlock xxl
- Dark sections: bg *color-primary transparency 100, ALL text *color-background

## Style: Glassmorphism

Mood: frosted, translucent, glass, layered, depth, futuristic, premium, blur, transparent
Industries: SaaS, fintech, tech startup, software, portfolio, luxury brand, hospitality, hotel, resort
Sections: hero, pricing, features, product, dashboard, testimonial, stats

Themes:
1. Glass Azure — primary #1A365D, text #334E68, secondary #B0D4E8, accent #3182CE, background #D6EBF5, fonts Inter/Inter
2. Frosted Lavender — primary #2D1B69, text #4A3870, secondary #D4C4F0, accent #7C3AED, background #EDE9FE, fonts Inter/Inter
3. Ice Crystal — primary #164E63, text #2E5A68, secondary #A5F3FC, accent #06B6D4, background #ECFEFF, fonts Inter/Inter
4. Ocean Mist — primary #1E3A3A, text #3A5858, secondary #B2DFDB, accent #009688, background #E0F2F1, fonts Inter/Inter

Properties:
- Page background: REQUIRED gradient (type gradient, direction to bottom right). Blur only visible on gradient parent
- Container: background color #ffffff, transparency 12, blur true, border width 1 color #ffffff, radius lg, shadow soft
- Card: background color #ffffff, transparency 15, blur true, border width 1 color #ffffff, radius lg, shadow soft
- Button: background color #ffffff, transparency 20, blur true, border width 1 color #ffffff, radius pill
- Heading: weight bold
- Body: weight regular
- Spacing: section paddingBlock xxxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: page MUST have gradient bg. Container blur true transparency 12. paragraph *color-text. Split: wrap nowrap widthMode "50"
- Features: columnsgrid columns 3 gap lg. Each card blur true transparency 15 radius lg border 1px #fff. paragraph *color-text
- Pricing: columnsgrid columns 3. Cards blur true transparency 15. Popular: transparency 25. paragraph *color-text
- Footer: bg *color-primary transparency 80, blur true, ALL text *color-background
- Dark sections: dark gradient bg, cards blur true transparency 15, ALL text *color-background

## Style: Retro Vintage

Mood: nostalgic, 70s, 80s, 90s, throwback, funky, groovy, vintage, bold, kitsch
Industries: entertainment, gaming, music, food, restaurant, bar, brewery, pizza, fashion, festival, event
Sections: hero, product, gallery, blog, team, ticker, countdown, cta

Themes:
1. Pop Art Yellow — primary #0D0D0D, text #2D2D00, secondary #FFD600, accent #FF0000, background #FFEB3B, fonts Bebas Neue/Merriweather
2. Disco Sunset — primary #1A0A2E, text #3A2040, secondary #FF6B6B, accent #FF2D87, background #FFB347, fonts Bebas Neue/Merriweather
3. Arcade Neon — primary #0D0D0D, text #B0B0C8, secondary #39FF14, accent #FF073A, background #1A1A2E, fonts Bebas Neue/Merriweather
4. Vinyl Brown — primary #2C1810, text #4A3828, secondary #D4A574, accent #E85D04, background #FDF0D5, fonts Bebas Neue/Merriweather

Properties:
- Container: border width 3 style solid color #0D0D0D, radius none, shadow retro, shadowColor #0D0D0D
- Card: border width 3 style solid color #0D0D0D, radius none, shadow retro, shadowColor #0D0D0D
- Button: border width 3 style solid color #0D0D0D, radius none, shadow retro
- Heading: weight extrabold, letterSpacing wide, transform uppercase
- Body: weight regular
- Spacing: section paddingBlock xl paddingInline md, card paddingBlock md paddingInline md

Section style_notes:
- Hero: bold saturated bg. paragraph *color-text. Split: wrap nowrap widthMode "50". Heading transform uppercase weight extrabold
- Features: columnsgrid columns 3 gap lg. Cards border 3px #0D0D0D shadow retro radius none. paragraph *color-text
- Footer: bg *color-primary transparency 100, ALL text *color-background, border-top 3px
- CTA: bold accent bg, large heading uppercase, shadow retro on button
- Dark sections: bg *color-primary transparency 100, ALL text *color-secondary or *color-background

## Style: Neubrutalism

Mood: raw, bold, unapologetic, punk, edgy, brutalist, harsh, high-contrast, thick-border
Industries: creative agency, portfolio, indie brand, art gallery, fashion, design studio, startup, photography
Sections: hero, gallery, product, team, blog, cta, features, pricing

Themes:
1. Concrete Raw — primary #1A1A1A, text #3D3D3D, secondary #C8C4BB, accent #FF4D00, background #E5E2DD, fonts Space Grotesk/IBM Plex Sans
2. Highlighter Shock — primary #000000, text #333333, secondary #E8E8E8, accent #FFE500, background #FFFFFF, fonts Space Grotesk/IBM Plex Sans
3. Acid Green — primary #0D0D0D, text #2D2D2D, secondary #C1FF72, accent #FF3864, background #F0FFE0, fonts Space Grotesk/IBM Plex Sans
4. Hot Pink Brutal — primary #1A1A1A, text #3D3D3D, secondary #FFB4D2, accent #FF006E, background #FFF0F5, fonts Space Grotesk/IBM Plex Sans

Properties:
- Container: border width 4 style solid color #000000, radius none, shadow retro, shadowColor #000000
- Card: border width 4 style solid color #000000, radius none, shadow retro, shadowColor #000000
- Button: border width 4 style solid color #000000, radius none, shadow retro, shadowColor #000000
- Heading: weight extrabold, transform uppercase
- Body: weight medium
- Spacing: section paddingBlock xl paddingInline md, card paddingBlock md paddingInline md

Section style_notes:
- Hero: bg *color-background. Heading extrabold uppercase xxxl. paragraph *color-text. Button border 4px #000 shadow retro
- Features: columnsgrid columns 3 gap lg. Cards border 4px #000 shadow retro radius none. paragraph *color-text
- Pricing: columnsgrid columns 3. ALL cards border 4px #000. Popular bg *color-accent. paragraph *color-text
- Footer: bg *color-primary transparency 100, border-top 4px #000, ALL text *color-background
- CTA: bg *color-accent, border 4px #000, text *color-background, heading extrabold uppercase

## Style: Claymorphism

Mood: playful, bubbly, soft, friendly, 3D, cute, approachable, rounded, fun, colorful
Industries: education, kids, wellness, fitness, gym, food delivery, mobile app, casual gaming, childcare, toy
Sections: hero, features, pricing, product, stats, team, cta, faq

Themes:
1. Bubblegum — primary #4A1942, text #5A3058, secondary #F5B0D0, accent #FF1493, background #FFD6E6, fonts Poppins/Nunito Sans
2. Lavender Dream — primary #3B1F7E, text #4A3068, secondary #D4B8FF, accent #8B5CF6, background #F3EEFF, fonts Poppins/Nunito Sans
3. Mint Cream — primary #1A4A3A, text #3A5A4A, secondary #A7F3D0, accent #10B981, background #ECFDF5, fonts Poppins/Nunito Sans
4. Sunset Peach — primary #7C2D12, text #5A3828, secondary #FDBA74, accent #F97316, background #FFF7ED, fonts Poppins/Nunito Sans

Properties:
- Container: radius xxl, shadow elevated, border none
- Card: radius xxl, shadow elevated, border none
- Button: radius pill, shadow medium, border none
- Heading: weight bold
- Body: weight medium
- Spacing: section paddingBlock xl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: light pastel bg. Centered layout. Heading bold xxxl. paragraph *color-text. Button radius pill shadow medium
- Features: columnsgrid columns 3 gap lg. Cards radius xxl shadow elevated, soft pastel card bg. paragraph *color-text
- Pricing: columnsgrid columns 3. Cards radius xxl shadow elevated. Popular shadow elevated larger. paragraph *color-text
- Footer: bg *color-primary transparency 100, radius none, ALL text *color-background
- CTA: bg *color-accent transparency 100, radius xxl, text *color-background, button radius pill

## Style: Aurora Gradient

Mood: ethereal, futuristic, flowing, dreamy, gradient, liquid, cosmic, vibrant, aurora, northern-lights
Industries: AI product, SaaS, luxury ecommerce, travel, resort, wellness, creative agency, tech startup
Sections: hero, pricing, features, cta, stats, testimonial, dashboard

Themes:
1. Holographic — primary #1A2035, text #384860, secondary #C8D8F0, accent #EC4899, background #E6F0FA, fonts Sora/Inter
2. Sunset Glow — primary #1A1A2E, text #3A3848, secondary #FED7AA, accent #F97316, background #FFF7ED, fonts Sora/Inter
3. Northern Lights — primary #0F172A, text #2A3A48, secondary #A5F3FC, accent #06B6D4, background #ECFEFF, fonts Sora/Inter
4. Deep Ocean — primary #0C1445, text #2A3860, secondary #818CF8, accent #6366F1, background #EEF2FF, fonts Sora/Inter

Properties:
- Page background: type gradient, gradient colorStart *color-accent colorEnd *color-secondary direction to bottom right
- Container: radius lg, shadow none, border none
- Card: background type gradient (subtle), radius lg, shadow none, border none
- Button: background type gradient, radius pill, shadow none, border none
- Heading: weight bold, letterSpacing tight
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: gradient bg (colorStart *color-accent, colorEnd *color-secondary, direction to bottom right). paragraph *color-text. Text *color-background if dark gradient
- Features: columnsgrid columns 3 gap lg. Cards subtle gradient bg radius lg. paragraph *color-text
- Pricing: columnsgrid columns 3. Popular card bold gradient bg. paragraph *color-text
- Footer: dark gradient bg, ALL text *color-background
- CTA: bold gradient bg *color-accent to *color-secondary, text *color-background, button gradient

## Style: Monochrome Dark

Mood: noir, cinematic, premium, sleek, dark, moody, high-contrast, sophisticated, nightlife
Industries: photography, luxury brand, automotive, car, fine dining, entertainment, portfolio, fashion, nightlife, music
Sections: hero, gallery, product, testimonial, team, pricing, stats, navigation, footer

Themes:
1. Cinema Noir — primary #F5F5F5, text #C8C8C8, secondary #1F1F1F, accent #DC143C, background #0F0F0F, fonts Space Grotesk/Inter
2. Midnight Blue — primary #E2E8F0, text #B0B8C8, secondary #1E293B, accent #3B82F6, background #0F172A, fonts Space Grotesk/Inter
3. Charcoal Silver — primary #F0F0F0, text #B8B8B8, secondary #2A2A2A, accent #A3A3A3, background #141414, fonts Space Grotesk/Inter
4. Obsidian Red — primary #FEE2E2, text #C8B0B0, secondary #1C1917, accent #EF4444, background #0C0A09, fonts Space Grotesk/Inter

Properties:
- Container: background color *color-secondary, transparency 100, border width 1 color #333333, radius xs, shadow soft, shadowColor #000000
- Card: background color *color-secondary, transparency 100, border width 1 color #333333, radius xs, shadow soft
- Button: border width 1 color #444444, radius xs, shadow none
- Heading: weight semibold, letterSpacing wide, color *color-primary
- Body: weight light, color *color-primary
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: dark bg *color-background transparency 100. ALL text *color-primary. Accent for CTA button only
- Features: columnsgrid columns 3 gap lg. Cards bg *color-secondary border 1px #333 radius xs
- Pricing: dark bg. ALL text *color-primary. Popular card border *color-accent
- Footer: bg *color-background, ALL text *color-primary, links *color-accent
- ALL sections: dark background, ALL text *color-primary (light on dark), accent ONLY for CTAs

## Style: Elegant Luxury

Mood: elegant, sophisticated, luxury, premium, upscale, refined, high-end, classy, opulent, exclusive
Industries: jewelry, hotel, fashion, interior design, real estate luxury, spa, fine dining, wedding, beauty
Sections: hero, features, gallery, testimonial, product, team, contact, cta

Themes:
1. Gold Standard — primary #1A1A1A, text #4A4A4A, secondary #D4AF37, accent #B8860B, background #FFFDF7, fonts Playfair Display/Inter
2. Champagne — primary #2C2C2C, text #4A4848, secondary #E8D5B7, accent #C9A96E, background #FAF6F0, fonts Playfair Display/Inter
3. Midnight Velvet — primary #F5F0E8, text #C8C0B8, secondary #2C1810, accent #9B7B4E, background #1A1A2E, fonts Playfair Display/Inter
4. Pearl & Onyx — primary #1C1C1C, text #4A4A48, secondary #E8E4DE, accent #8B7355, background #FAFAF8, fonts Cormorant Garamond/Inter

Properties:
- Container: radius none, shadow soft, border width 1 color *color-secondary
- Card: radius xs, shadow soft, border width 1 color *color-secondary
- Button: radius none, shadow none, border width 1 color *color-primary
- Heading: weight light, letterSpacing wider, transform uppercase, fontStyle normal
- Body: weight light, letterSpacing wide
- Spacing: section paddingBlock xxxl paddingInline xl, card paddingBlock xl paddingInline xl

Section style_notes:
- Hero: generous whitespace paddingBlock xxxl. paragraph *color-text. Split: wrap nowrap widthMode "50". Heading light uppercase letterSpacing wider
- Features: columnsgrid columns 3 gap xl. Cards radius xs shadow soft border 1px *color-secondary. paragraph *color-text
- Gallery: images with hoverEffect brighten. Minimal text, let visuals speak
- Footer: bg *color-primary transparency 100, ALL text *color-background, letterSpacing wider
- CTA: bg *color-primary transparency 100, text *color-background, button border 1px *color-background

## Style: Organic Natural

Mood: organic, natural, earthy, warm, eco, sustainable, handcrafted, rustic, wholesome, farm-to-table
Industries: bakery, farm, wellness, organic food, eco brand, spa, herbal, craft, florist, garden center
Sections: hero, features, product, testimonial, team, contact, gallery, about

Themes:
1. Forest Floor — primary #1A3A1A, text #3A5A3A, secondary #E0EBD8, accent #2E8B57, background #F5FAF0, fonts Playfair Display/Inter
2. Desert Sand — primary #5C4033, text #6A5040, secondary #E8D5B7, accent #C2703E, background #FDF6EC, fonts Lora/Inter
3. Herb Garden — primary #2D4A2D, text #4A5A40, secondary #D4E2C8, accent #6B8F3C, background #F4F9EE, fonts Playfair Display/Inter
4. Terra Cotta — primary #6B3A2A, text #6A4A38, secondary #E8C4A8, accent #C1582A, background #FFF5EB, fonts Lora/Inter

Properties:
- Container: radius lg, shadow soft, border none
- Card: radius lg, shadow soft, border none
- Button: radius lg, shadow none, border none
- Heading: weight semibold, fontStyle italic for eyebrow
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: warm light bg. paragraph *color-text. Split: wrap nowrap widthMode "50". Image with cornerStyle lg hoverEffect brighten
- Features: columnsgrid columns 3 gap lg. Cards radius lg shadow soft, warm card bg. paragraph *color-text
- Product: columnsgrid columns 3. Image fit cover cornerStyle lg. Warm earth tones. paragraph *color-text
- Footer: bg *color-primary transparency 100, ALL text *color-background, radius none
- CTA: bg *color-accent transparency 100, text *color-background, radius lg

## Style: Corporate Professional

Mood: corporate, enterprise, reliable, structured, business, formal, institutional, trustworthy, stable
Industries: bank, insurance, law firm, consulting, enterprise SaaS, government, accounting, HR, logistics
Sections: hero, features, stats, pricing, team, contact, faq, testimonial, blog

Themes:
1. Trust Blue — primary #1E3A5F, text #4B5563, secondary #E2E8F0, accent #2563EB, background #F8FAFC, fonts Inter/Inter
2. Executive Grey — primary #374151, text #4B5563, secondary #E5E7EB, accent #4F46E5, background #F9FAFB, fonts Inter/Inter
3. Legal Navy — primary #1E293B, text #475569, secondary #CBD5E1, accent #0EA5E9, background #F0F4F8, fonts Inter/Inter
4. Finance Green — primary #14532D, text #3A5A40, secondary #D1FAE5, accent #059669, background #F0FDF4, fonts Inter/Inter

Properties:
- Container: radius sm, shadow none, border width 1 color #e5e7eb
- Card: radius sm, shadow soft, border width 1 color #e5e7eb
- Button: radius sm, shadow none, border none
- Heading: weight semibold, letterSpacing normal
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline xl, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: light bg, structured layout. paragraph *color-text. Split: wrap nowrap widthMode "50". Conservative heading weight semibold
- Features: columnsgrid columns 3 gap lg. Cards radius sm shadow soft border 1px #e5e7eb. paragraph *color-text
- Stats: layout-row wrap wrap. counter-up components. bg *color-primary transparency 100 ALL text *color-background
- Footer: bg *color-primary transparency 100, structured 3-column, ALL text *color-background
- CTA: bg *color-accent transparency 100, text *color-background, professional tone

## Style: Bold Editorial

Mood: editorial, magazine, dramatic, newspaper, typographic, bold, striking, media, headline-driven
Industries: media, news, magazine, blog, publishing, content platform, journal, literary
Sections: hero, blog, features, gallery, team, newsletter, cta

Themes:
1. Print Classic — primary #1A1A1A, text #374151, secondary #F5F5F0, accent #DC2626, background #FFFFFF, fonts Playfair Display/Inter
2. Red Masthead — primary #1C1917, text #3D3830, secondary #FEE2E2, accent #B91C1C, background #FFFBEB, fonts Playfair Display/Inter
3. Newsroom Grey — primary #111827, text #374151, secondary #E5E7EB, accent #2563EB, background #F3F4F6, fonts Sora/Inter
4. Broadsheet — primary #292524, text #44403C, secondary #D6D3D1, accent #EA580C, background #FAFAF9, fonts Cormorant Garamond/Inter

Properties:
- Container: radius none, shadow none, border none
- Card: radius none, shadow none, border width 1 color #e5e7eb bottom only
- Button: radius none, shadow none, border width 2 color *color-primary
- Heading: weight black, size xxxl for hero, letterSpacing tighter
- Body: weight regular, lineHeight "1.7"
- Spacing: section paddingBlock xxl paddingInline xl, card paddingBlock lg

Section style_notes:
- Hero: dramatic oversized heading weight black size xxxl letterSpacing tighter. paragraph *color-text. Minimal elements. paddingBlock xxxl
- Blog: asymmetric grid — columnsgrid columns 3. First article large. Clean card with bottom border only. paragraph *color-text
- Features: columnsgrid columns 2 gap xl. Bold heading for each, descriptive paragraph *color-text
- Footer: bg *color-primary transparency 100, ALL text *color-background, minimal links
- CTA: bg *color-accent transparency 100, large heading, text *color-background

## Style: Cyberpunk Neon

Mood: cyberpunk, neon, futuristic, high-tech, digital, sci-fi, hacker, electric, matrix, dystopian
Industries: gaming, tech, AI, VR, crypto, software, digital agency, esports, music electronic
Sections: hero, features, product, pricing, stats, gallery, cta, countdown

Themes:
1. Electric Purple — primary #E0E7FF, text #B0B8D8, secondary #1E1B4B, accent #A855F7, background #0F0B1A, fonts Space Grotesk/Inter
2. Neon Matrix — primary #D1FAE5, text #A0C8B0, secondary #064E3B, accent #10B981, background #022C22, fonts Space Grotesk/Inter
3. Chrome Pink — primary #FCE7F3, text #C8B0C0, secondary #4A1942, accent #EC4899, background #0F0A15, fonts Space Grotesk/Inter
4. Cyber Teal — primary #CCFBF1, text #A0C8C0, secondary #134E4A, accent #14B8A6, background #042F2E, fonts Space Grotesk/Inter

Properties:
- Container: background color *color-secondary, transparency 100, border width 1 color *color-accent, radius xs, shadow soft, shadowColor *color-accent
- Card: background color *color-secondary, transparency 100, border width 1 color *color-accent, radius xs, shadow soft
- Button: border width 2 color *color-accent, radius xs, shadow soft, shadowColor *color-accent
- Heading: weight bold, transform uppercase, letterSpacing wide
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: very dark bg *color-background. Heading uppercase bold. Neon accent border on elements. ALL text *color-primary
- Features: columnsgrid columns 3 gap lg. Cards dark bg border 1px *color-accent shadow soft shadowColor *color-accent
- Pricing: dark bg. Cards border *color-accent. Popular glow effect stronger shadowColor
- Footer: bg *color-background, border-top 1px *color-accent, ALL text *color-primary
- ALL sections: dark background, text *color-primary, neon borders *color-accent, shadow glow with shadowColor *color-accent

## Style: Pastel Soft

Mood: pastel, gentle, calm, soothing, light, airy, delicate, feminine, sweet, dreamy
Industries: beauty, skincare, baby, wedding, bakery, cafe, florist, stationery, photography, lifestyle
Sections: hero, features, product, testimonial, gallery, contact, about, team

Themes:
1. Cotton Candy — primary #6B2D5B, text #5A3858, secondary #FBCFE8, accent #EC4899, background #FDF2F8, fonts Poppins/Nunito Sans
2. Sky Breeze — primary #1E3A5F, text #3A5068, secondary #BAE6FD, accent #0EA5E9, background #F0F9FF, fonts Poppins/Nunito Sans
3. Lavender Fields — primary #4C1D95, text #4A3068, secondary #DDD6FE, accent #8B5CF6, background #F5F3FF, fonts Poppins/Nunito Sans
4. Peach Blossom — primary #7C2D12, text #5A3828, secondary #FED7AA, accent #F97316, background #FFF7ED, fonts Poppins/Nunito Sans

Properties:
- Container: radius lg, shadow soft, border none
- Card: radius lg, shadow soft, border none
- Button: radius pill, shadow soft, border none
- Heading: weight semibold
- Body: weight light
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: soft pastel bg. Centered layout. Heading semibold. paragraph *color-text. Gentle paddingBlock xxl
- Features: columnsgrid columns 3 gap lg. Cards radius lg shadow soft, pastel card bg. paragraph *color-text
- Product: columnsgrid columns 3. Images cornerStyle lg. Soft shadow on cards. paragraph *color-text
- Footer: bg *color-primary transparency 100, ALL text *color-background
- CTA: bg *color-accent transparency 100, text *color-background, button radius pill

## Style: Scandinavian Clean

Mood: scandinavian, nordic, hygge, cozy, balanced, understated, calm, white-space, functional, warm-minimal
Industries: furniture, home decor, architecture, interior design, lifestyle, wellness, craft, sustainable brand
Sections: hero, features, product, gallery, about, contact, testimonial, blog

Themes:
1. Fjord Grey — primary #374151, text #6B7280, secondary #E5E7EB, accent #6B7280, background #FFFFFF, fonts Inter/Inter
2. Birch Wood — primary #44403C, text #57534E, secondary #E7E5E4, accent #A8A29E, background #FAFAF9, fonts Inter/Inter
3. Winter White — primary #1F2937, text #4B5563, secondary #F3F4F6, accent #3B82F6, background #FFFFFF, fonts Inter/Inter
4. Copenhagen Blue — primary #1E3A5F, text #4B5563, secondary #DBEAFE, accent #2563EB, background #F8FAFF, fonts Inter/Inter

Properties:
- Container: radius md, shadow none, border none
- Card: radius md, shadow none, border width 1 color #f0f0f0
- Button: radius sm, shadow none, border width 1 color *color-primary
- Heading: weight medium, letterSpacing normal
- Body: weight light
- Spacing: section paddingBlock xxxl paddingInline xl, card paddingBlock xl paddingInline xl

Section style_notes:
- Hero: white bg, generous whitespace paddingBlock xxxl. paragraph *color-text. Split: wrap nowrap widthMode "50". Understated heading weight medium
- Features: columnsgrid columns 3 gap xl. Minimal cards, subtle border only. Generous spacing. paragraph *color-text
- Product: columnsgrid columns 2-3. Large images, minimal text. cornerStyle md. paragraph *color-text
- Footer: light bg, subtle text, minimal elements. NO dark bg for scandi style
- CTA: simple centered layout, outline button border 1px *color-primary, paddingBlock xxl

## Style: Art Deco Geometric

Mood: art deco, geometric, gatsby, glamorous, 1920s, ornamental, grand, opulent, jazz-age, theatrical
Industries: hotel, event venue, cocktail bar, theater, luxury brand, jewelry, ballroom, heritage, museum
Sections: hero, features, gallery, testimonial, pricing, cta, about, contact

Themes:
1. Gatsby Gold — primary #0D0D0D, text #C8C8B8, secondary #D4AF37, accent #B8860B, background #1A1A2E, fonts Playfair Display/Inter
2. Emerald Ballroom — primary #F5F0E8, text #C8C0B0, secondary #065F46, accent #D4AF37, background #064E3B, fonts Playfair Display/Inter
3. Onyx & Brass — primary #F5F5F0, text #C8C8C0, secondary #D4AF37, accent #B45309, background #1C1917, fonts Cormorant Garamond/Inter
4. Ruby Theater — primary #FEE2E2, text #C8A8A8, secondary #991B1B, accent #D4AF37, background #450A0A, fonts Playfair Display/Inter

Properties:
- Container: radius none, shadow medium, border width 2 color *color-secondary
- Card: radius none, shadow medium, border width 2 color *color-secondary
- Button: radius none, shadow none, border width 2 color *color-secondary
- Heading: weight bold, transform uppercase, letterSpacing widest
- Body: weight regular, letterSpacing wide
- Spacing: section paddingBlock xxxl paddingInline xl, card paddingBlock xl paddingInline xl

Section style_notes:
- Hero: dark bg. Heading uppercase bold letterSpacing widest. Gold accent border. ALL text light color
- Features: columnsgrid columns 3 gap lg. Cards border 2px *color-secondary shadow medium. Dark card bg
- Pricing: dark bg. Cards border 2px gold. Popular highlighted with *color-accent bg
- Footer: bg *color-background, border-top 2px *color-secondary, ALL text light
- ALL sections: dark backgrounds, gold/brass accents, uppercase headings, geometric borders

## Style: Tropical Vibrant

Mood: tropical, vibrant, beach, summer, paradise, island, colorful, lively, festive, caribbean
Industries: resort, travel, beach club, surf shop, tropical food, juice bar, tourism, outdoor adventure
Sections: hero, features, product, gallery, testimonial, cta, about, contact

Themes:
1. Island Sunset — primary #1C1917, text #3D3830, secondary #FDBA74, accent #F97316, background #FFF7ED, fonts Poppins/Nunito Sans
2. Jungle Canopy — primary #14532D, text #3A5A3A, secondary #BBF7D0, accent #22C55E, background #F0FDF4, fonts Poppins/Nunito Sans
3. Coral Reef — primary #9F1239, text #6A2838, secondary #FDA4AF, accent #F43F5E, background #FFF1F2, fonts Poppins/Nunito Sans
4. Mango Splash — primary #713F12, text #5A4828, secondary #FEF08A, accent #EAB308, background #FEFCE8, fonts Poppins/Nunito Sans

Properties:
- Container: radius lg, shadow none, border none
- Card: radius lg, shadow soft, border none
- Button: radius pill, shadow none, border none
- Heading: weight bold
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: vibrant bg or bold image overlay. Heading bold. paragraph *color-text. Button radius pill. paddingBlock xxl
- Features: columnsgrid columns 3 gap lg. Cards radius lg shadow soft, bright accent colors. paragraph *color-text
- Gallery: images fit cover cornerStyle lg. Bright, saturated images
- Footer: bg *color-primary transparency 100, ALL text *color-background
- CTA: bg *color-accent transparency 100, text *color-background, energetic heading

## Style: Dark Academia

Mood: academic, scholarly, literary, classical, bookish, vintage-intellectual, library, warm-dark, studious
Industries: bookstore, university, library, museum, literary magazine, antique, vintage clothing, education
Sections: hero, features, blog, gallery, about, testimonial, faq, contact

Themes:
1. Oxford Library — primary #F5E6D3, text #C8B8A0, secondary #3C2415, accent #8B6914, background #2C1810, fonts Cormorant Garamond/Inter
2. Sepia Study — primary #E8D5B7, text #B8A890, secondary #4A3728, accent #C2703E, background #352A21, fonts Playfair Display/Inter
3. Midnight Scholar — primary #E2E8F0, text #B0B8C8, secondary #1E293B, accent #9B7B4E, background #0F172A, fonts Cormorant Garamond/Inter
4. Parchment Ink — primary #44403C, text #57534E, secondary #E7E5E4, accent #92400E, background #FEFCE8, fonts Playfair Display/Inter

Properties:
- Container: radius xs, shadow soft, border width 1 color *color-secondary
- Card: radius xs, shadow soft, border width 1 color *color-secondary
- Button: radius xs, shadow none, border width 1 color *color-primary
- Heading: weight semibold, fontStyle italic for eyebrow, letterSpacing wide
- Body: weight regular, lineHeight "1.7"
- Spacing: section paddingBlock xxl paddingInline xl, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: warm dark bg (themes 1-3) or warm light bg (theme 4). Serif heading italic eyebrow. paragraph *color-text on light bg. paddingBlock xxl
- Blog: columnsgrid columns 2-3. Cards radius xs border 1px. Long-form friendly lineHeight "1.7". paragraph *color-text on light bg
- Features: columnsgrid columns 3 gap lg. Warm tones, serif headings, scholarly feel. paragraph *color-text on light bg
- Footer: bg darker than page, ALL text light if dark theme, border-top 1px
- Dark themes (1-3): ALL text *color-primary (light), warm borders. Theme 4: standard light bg

## Style: Memphis Design

Mood: memphis, 80s geometric, abstract, pop, playful-shapes, colorful, postmodern, bold-pattern, retro-fun
Industries: design studio, toy brand, kids education, creative agency, pop-up shop, youth brand, party
Sections: hero, features, product, gallery, team, cta, pricing, about

Themes:
1. Primary Shapes — primary #1A1A1A, text #2D2D2D, secondary #FFD700, accent #FF3366, background #00BFFF, fonts Space Grotesk/IBM Plex Sans
2. Squiggle Pink — primary #1A1A1A, text #3D3D3D, secondary #FF69B4, accent #39FF14, background #FFE4E1, fonts Space Grotesk/IBM Plex Sans
3. Confetti — primary #1A1A1A, text #3D3D3D, secondary #FF6B35, accent #7B2FF7, background #FFFACD, fonts Space Grotesk/IBM Plex Sans
4. Electric Grid — primary #FFFFFF, text #C8C8C8, secondary #FF1493, accent #00FF7F, background #1A1A2E, fonts Space Grotesk/IBM Plex Sans

Properties:
- Container: radius none, shadow retro, shadowColor #000000, border width 3 color #000000
- Card: mix of radius none and radius pill on alternating cards, shadow retro, border width 3 color #000000
- Button: radius pill, shadow retro, shadowColor #000000, border width 3 color #000000
- Heading: weight extrabold, transform uppercase
- Body: weight medium
- Spacing: section paddingBlock xl paddingInline md, card paddingBlock md paddingInline md

Section style_notes:
- Hero: bold contrasting bg. Heading extrabold uppercase xxxl. paragraph *color-text on light bg. Mix of shapes and bold colors
- Features: columnsgrid columns 3 gap lg. Cards alternating radius (none/pill). Bold border 3px shadow retro. paragraph *color-text on light bg
- Pricing: columnsgrid columns 3. Each card different accent bg color. Bold borders. paragraph *color-text on light bg
- Footer: bg *color-primary transparency 100, ALL text *color-background, playful icon accents
- CTA: vivid accent bg, large heading uppercase, button pill shadow retro

## Style: Zen Japanese

Mood: zen, japanese, wabi-sabi, tranquil, serene, minimalist, peaceful, contemplative, nature, balance
Industries: spa, meditation, tea house, garden center, yoga studio, wellness retreat, Japanese restaurant
Sections: hero, features, about, gallery, testimonial, contact, faq

Themes:
1. Bamboo Garden — primary #374151, text #57534E, secondary #D1D5C0, accent #6B7F4E, background #F5F5F0, fonts Inter/Inter
2. Stone Temple — primary #44403C, text #57534E, secondary #D6D3D1, accent #A8A29E, background #FAFAF9, fonts Inter/Inter
3. Cherry Blossom — primary #4C1D3A, text #5A3050, secondary #FBCFE8, accent #DB2777, background #FDF2F8, fonts Inter/Inter
4. Ink Wash — primary #1F2937, text #4B5563, secondary #E5E7EB, accent #6B7280, background #FFFFFF, fonts Inter/Inter

Properties:
- Container: radius sm, shadow none, border none
- Card: radius sm, shadow none, border width 1 color #e8e8e8
- Button: radius sm, shadow none, border width 1 color *color-primary
- Heading: weight light, letterSpacing wider
- Body: weight light, lineHeight "1.8"
- Spacing: section paddingBlock xxxl paddingInline xl, card paddingBlock xl paddingInline xl

Section style_notes:
- Hero: white or very light bg. Extreme whitespace paddingBlock xxxl. paragraph *color-text. Heading light weight wider letterSpacing. Minimal elements
- Features: columnsgrid columns 3 gap xl. Very minimal cards, thin border. Maximum whitespace. paragraph *color-text
- Gallery: images full width or large. cornerStyle sm. Generous spacing between
- Footer: light bg, minimal text, understated. Heading light weight
- ALL sections: maximum whitespace, minimal elements, restraint over decoration, light heading weights

## Style: Industrial Grunge

Mood: industrial, grunge, warehouse, raw, urban, loft, rugged, gritty, exposed, underground
Industries: brewery, motorcycle, construction, workshop, music venue, tattoo, urban fashion, gym, CrossFit
Sections: hero, features, product, gallery, about, team, cta, contact

Themes:
1. Iron Forge — primary #E5E5E5, text #B0B0B0, secondary #2D2D2D, accent #D97706, background #1A1A1A, fonts Space Grotesk/Inter
2. Rust & Concrete — primary #F5E6D3, text #C0B0A0, secondary #44403C, accent #B45309, background #292524, fonts Space Grotesk/Inter
3. Smoke Stack — primary #D1D5DB, text #A0A8B0, secondary #374151, accent #EF4444, background #111827, fonts Space Grotesk/Inter
4. Warehouse Grey — primary #1F2937, text #4B5563, secondary #D1D5DB, accent #F59E0B, background #F3F4F6, fonts Space Grotesk/Inter

Properties:
- Container: radius none, shadow none, border width 1 color #444444
- Card: radius none, shadow none, border width 1 color #444444
- Button: radius none, shadow none, border width 2 color *color-accent
- Heading: weight bold, transform uppercase, letterSpacing wide
- Body: weight regular
- Spacing: section paddingBlock xl paddingInline md, card paddingBlock md paddingInline md

Section style_notes:
- Hero: dark bg (themes 1-3) or grey bg (theme 4). Heading uppercase bold. paragraph *color-text on light bg. Raw industrial feel
- Features: columnsgrid columns 3 gap lg. Cards radius none border 1px #444. No shadow. paragraph *color-text on light bg
- Gallery: images full width, no cornerStyle. Raw edges
- Footer: bg darker, border-top 1px #444, ALL text light if dark bg
- Dark themes (1-3): ALL text *color-primary (light), accent for CTAs only. Theme 4: standard colors

## Style: Y2K Retro-futurism

Mood: y2k, 2000s, chrome, iridescent, digital-nostalgia, retro-future, techno, bubble, shiny, metallic
Industries: fashion, music, digital agency, gaming, pop culture, tech startup, NFT, social media
Sections: hero, features, product, gallery, pricing, cta, about

Themes:
1. Cyber Chrome — primary #1A1A2E, text #3A3A50, secondary #C0C0C0, accent #7B68EE, background #E8E8FF, fonts Sora/Inter
2. Bubblegum Tech — primary #4A1942, text #5A3050, secondary #FFB6C1, accent #FF69B4, background #FFF0F5, fonts Sora/Inter
3. Hologram — primary #0F172A, text #2A3848, secondary #A5F3FC, accent #06B6D4, background #F0FDFF, fonts Sora/Inter
4. Digital Lavender — primary #2E1065, text #4A3868, secondary #C4B5FD, accent #8B5CF6, background #F5F3FF, fonts Sora/Inter

Properties:
- Container: radius xl, shadow soft, border none
- Card: radius xl, shadow soft, border none, background type gradient (subtle shimmer)
- Button: radius pill, shadow soft, border none, background type gradient
- Heading: weight bold
- Body: weight regular
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: light gradient bg or iridescent feel. paragraph *color-text. Button gradient bg radius pill. Heading bold
- Features: columnsgrid columns 3 gap lg. Cards radius xl gradient bg subtle. Soft shadow. paragraph *color-text
- Pricing: columnsgrid columns 3. Gradient cards. Popular card stronger gradient. paragraph *color-text
- Footer: bg *color-primary transparency 100, ALL text *color-background
- CTA: gradient bg *color-accent to *color-secondary, text *color-background, button pill gradient

## Style: Bohemian Eclectic

Mood: bohemian, boho, eclectic, artisan, handmade, free-spirited, creative, warm, textured, organic-mixed
Industries: craft market, artisan shop, yoga studio, vintage store, boutique hotel, art school, pottery
Sections: hero, features, product, gallery, about, testimonial, contact, team

Themes:
1. Moroccan Sunset — primary #5C2018, text #5A3828, secondary #F4A261, accent #E76F51, background #FFF5EB, fonts Lora/Inter
2. Gypsy Rose — primary #4A1942, text #5A3050, secondary #E8A0BF, accent #C74B7A, background #FFF0F5, fonts Lora/Inter
3. Artisan Clay — primary #6B3A2A, text #5A4838, secondary #D4A574, accent #B8621B, background #FAF0E6, fonts Playfair Display/Inter
4. Festival Nights — primary #F5E6D3, text #C8B8A0, secondary #6B2D5B, accent #D4AF37, background #1A1A2E, fonts Lora/Inter

Properties:
- Container: radius md, shadow soft, border none
- Card: radius lg, shadow soft, border none
- Button: radius lg, shadow none, border none
- Heading: weight semibold, fontStyle italic for eyebrow
- Body: weight regular, lineHeight "1.6"
- Spacing: section paddingBlock xxl paddingInline lg, card paddingBlock lg paddingInline lg

Section style_notes:
- Hero: warm bg. paragraph *color-text. Split: wrap nowrap widthMode "50". Serif italic eyebrow. Rich warm colors
- Features: columnsgrid columns 3 gap lg. Cards radius lg shadow soft. Warm palette. paragraph *color-text
- Gallery: images cornerStyle lg. Mix of sizes if possible. Warm filter
- Footer: bg *color-primary transparency 100, ALL text *color-background, warm accent links
- Dark theme (theme 4): ALL text *color-primary (light), warm golden accents
