FONT_OPTIONS = [
    {'value': 'Inter', 'label': 'Inter', 'use': 'Clean SaaS and dashboards'},
    {'value': 'Manrope', 'label': 'Manrope', 'use': 'Modern marketing pages'},
    {'value': 'Plus Jakarta Sans', 'label': 'Plus Jakarta Sans', 'use': 'Polished startup brands'},
    {'value': 'DM Sans', 'label': 'DM Sans', 'use': 'Friendly product sites'},
    {'value': 'Space Grotesk', 'label': 'Space Grotesk', 'use': 'Bold tech and creative brands'},
    {'value': 'Sora', 'label': 'Sora', 'use': 'Sharp digital products'},
    {'value': 'Outfit', 'label': 'Outfit', 'use': 'Simple ecommerce and services'},
    {'value': 'Poppins', 'label': 'Poppins', 'use': 'Approachable consumer brands'},
    {'value': 'Montserrat', 'label': 'Montserrat', 'use': 'Professional broad-use brands'},
    {'value': 'IBM Plex Sans', 'label': 'IBM Plex Sans', 'use': 'Technical and editorial brands'},
    {'value': 'Playfair Display', 'label': 'Playfair Display', 'use': 'Luxury and editorial headlines'},
    {'value': 'Lora', 'label': 'Lora', 'use': 'Warm editorial and lifestyle brands'},
    {'value': 'Merriweather', 'label': 'Merriweather', 'use': 'Trustworthy long-form content'},
    {'value': 'Roboto Slab', 'label': 'Roboto Slab', 'use': 'Structured service brands'},
    {'value': 'Geist', 'label': 'Geist', 'use': 'Modern SaaS and product UI'},
    {'value': 'Instrument Sans', 'label': 'Instrument Sans', 'use': 'Contemporary brand systems'},
    {'value': 'Onest', 'label': 'Onest', 'use': 'Approachable digital products'},
    {'value': 'Public Sans', 'label': 'Public Sans', 'use': 'Civic, nonprofit, trustworthy organizations'},
    {'value': 'Source Sans 3', 'label': 'Source Sans 3', 'use': 'Readable broad-use content'},
    {'value': 'Work Sans', 'label': 'Work Sans', 'use': 'Startups, services, portfolios'},
    {'value': 'Mulish', 'label': 'Mulish', 'use': 'Soft SaaS and service brands'},
    {'value': 'Nunito Sans', 'label': 'Nunito Sans', 'use': 'Friendly consumer brands'},
    {'value': 'Rubik', 'label': 'Rubik', 'use': 'Modern ecommerce and apps'},
    {'value': 'Urbanist', 'label': 'Urbanist', 'use': 'Fashion, creator, modern lifestyle'},
    {'value': 'Archivo', 'label': 'Archivo', 'use': 'Strong editorial and product launches'},
    {'value': 'Fraunces', 'label': 'Fraunces', 'use': 'Expressive editorial and lifestyle headings'},
    {'value': 'Newsreader', 'label': 'Newsreader', 'use': 'Premium editorial content'},
    {'value': 'Libre Baskerville', 'label': 'Libre Baskerville', 'use': 'Trust, education, legal, heritage'},
]


THEME_CATEGORIES = [
    {
        'key': 'clean_professional',
        'label': 'Clean & Professional',
        'description': 'Structured, trustworthy styles for SaaS, services, fintech, civic, and technical brands.',
    },
    {
        'key': 'premium_editorial',
        'label': 'Premium & Editorial',
        'description': 'Refined, content-led styles for premium products, creators, courses, and publications.',
    },
    {
        'key': 'soft_wellness',
        'label': 'Soft & Wellness',
        'description': 'Warm, calm, natural styles for wellness, family, lifestyle, and care-oriented brands.',
    },
    {
        'key': 'bold_experimental',
        'label': 'Bold & Experimental',
        'description': 'High-energy, expressive styles for creative, entertainment, tech, and launch brands.',
    },
    {
        'key': 'commerce_conversion',
        'label': 'Commerce & Conversion',
        'description': 'Action-focused visual systems for retail, offers, launches, and conversion pages.',
    },
]


THEME_CATEGORY_BY_KEY = {
    'modern_minimalist': 'clean_professional',
    'corporate_professional': 'clean_professional',
    'scandinavian_clean': 'clean_professional',
    'clean_b2b_saas': 'clean_professional',
    'fintech_trust': 'clean_professional',
    'technical_docs': 'clean_professional',
    'nonprofit_civic': 'clean_professional',
    'local_service': 'clean_professional',
    'elegant_luxury': 'premium_editorial',
    'bold_editorial': 'premium_editorial',
    'art_deco_geometric': 'premium_editorial',
    'dark_academia': 'premium_editorial',
    'monochrome_dark': 'premium_editorial',
    'premium_ecommerce': 'premium_editorial',
    'creator_personal_brand': 'premium_editorial',
    'course_expert': 'premium_editorial',
    'high_contrast_editorial': 'premium_editorial',
    'organic_natural': 'soft_wellness',
    'pastel_soft': 'soft_wellness',
    'claymorphism': 'soft_wellness',
    'zen_japanese': 'soft_wellness',
    'bohemian_eclectic': 'soft_wellness',
    'health_wellness': 'soft_wellness',
    'playful_family': 'soft_wellness',
    'glassmorphism': 'bold_experimental',
    'retro_vintage': 'bold_experimental',
    'neubrutalism': 'bold_experimental',
    'cyberpunk_neon': 'bold_experimental',
    'memphis_design': 'bold_experimental',
    'industrial_grunge': 'bold_experimental',
    'y2k_retro_futurism': 'bold_experimental',
    'aurora_gradient': 'commerce_conversion',
    'tropical_vibrant': 'commerce_conversion',
    'conversion_landing_page': 'commerce_conversion',
    'marketplace_retail': 'commerce_conversion',
    'event_launch': 'commerce_conversion',
}


def _theme(value, label):
    return {
        'value': value,
        'label': label,
        'category': THEME_CATEGORY_BY_KEY[value],
    }


THEME_OPTIONS = [
    _theme('modern_minimalist', 'Modern Minimalist'),
    _theme('glassmorphism', 'Glassmorphism'),
    _theme('retro_vintage', 'Retro Vintage'),
    _theme('neubrutalism', 'Neubrutalism'),
    _theme('claymorphism', 'Claymorphism'),
    _theme('aurora_gradient', 'Aurora Gradient'),
    _theme('monochrome_dark', 'Monochrome Dark'),
    _theme('elegant_luxury', 'Elegant Luxury'),
    _theme('organic_natural', 'Organic Natural'),
    _theme('corporate_professional', 'Corporate Professional'),
    _theme('bold_editorial', 'Bold Editorial'),
    _theme('cyberpunk_neon', 'Cyberpunk Neon'),
    _theme('pastel_soft', 'Pastel Soft'),
    _theme('scandinavian_clean', 'Scandinavian Clean'),
    _theme('art_deco_geometric', 'Art Deco Geometric'),
    _theme('tropical_vibrant', 'Tropical Vibrant'),
    _theme('dark_academia', 'Dark Academia'),
    _theme('memphis_design', 'Memphis Design'),
    _theme('zen_japanese', 'Zen Japanese'),
    _theme('industrial_grunge', 'Industrial Grunge'),
    _theme('y2k_retro_futurism', 'Y2K Retro-futurism'),
    _theme('bohemian_eclectic', 'Bohemian Eclectic'),
    _theme('clean_b2b_saas', 'Clean B2B SaaS'),
    _theme('conversion_landing_page', 'Conversion Landing Page'),
    _theme('premium_ecommerce', 'Premium Ecommerce'),
    _theme('marketplace_retail', 'Marketplace Retail'),
    _theme('creator_personal_brand', 'Creator Personal Brand'),
    _theme('course_expert', 'Course Expert'),
    _theme('local_service', 'Local Service'),
    _theme('health_wellness', 'Health And Wellness'),
    _theme('fintech_trust', 'Fintech Trust'),
    _theme('nonprofit_civic', 'Nonprofit Civic'),
    _theme('event_launch', 'Event Launch'),
    _theme('high_contrast_editorial', 'High Contrast Editorial'),
    _theme('playful_family', 'Playful Family'),
    _theme('technical_docs', 'Technical Docs'),
]


BUSINESS_THEME_ALIASES = {
    'modern_minimalist': ('clean_b2b_saas', 'technical_docs'),
    'corporate_professional': ('clean_b2b_saas', 'fintech_trust', 'nonprofit_civic', 'local_service'),
    'scandinavian_clean': ('technical_docs', 'local_service'),
    'elegant_luxury': ('premium_ecommerce',),
    'bold_editorial': ('creator_personal_brand', 'course_expert', 'high_contrast_editorial'),
    'art_deco_geometric': ('premium_ecommerce', 'event_launch'),
    'dark_academia': ('course_expert',),
    'monochrome_dark': ('creator_personal_brand', 'high_contrast_editorial'),
    'organic_natural': ('health_wellness', 'local_service'),
    'pastel_soft': ('health_wellness', 'playful_family'),
    'claymorphism': ('playful_family',),
    'zen_japanese': ('health_wellness',),
    'bohemian_eclectic': ('health_wellness',),
    'aurora_gradient': ('conversion_landing_page', 'marketplace_retail', 'event_launch'),
    'tropical_vibrant': ('marketplace_retail', 'event_launch'),
}


CATEGORY_TONE_TAGS = {
    'clean_professional': ('professional', 'trustworthy', 'confident', 'technical', 'calm'),
    'premium_editorial': ('premium', 'aspirational', 'confident', 'authoritative'),
    'soft_wellness': ('warm', 'empathetic', 'friendly', 'calm', 'educational'),
    'bold_experimental': ('bold', 'energetic', 'playful', 'witty', 'aspirational'),
    'commerce_conversion': ('energetic', 'confident', 'aspirational', 'friendly', 'bold'),
}


STYLE_TONE_TAGS = {
    'modern_minimalist': ('professional', 'trustworthy', 'minimal', 'calm'),
    'glassmorphism': ('premium', 'confident', 'aspirational'),
    'retro_vintage': ('playful', 'energetic', 'witty'),
    'neubrutalism': ('bold', 'energetic', 'confident'),
    'claymorphism': ('friendly', 'playful', 'warm'),
    'aurora_gradient': ('aspirational', 'energetic', 'premium'),
    'monochrome_dark': ('premium', 'confident', 'authoritative'),
    'elegant_luxury': ('premium', 'aspirational', 'calm'),
    'organic_natural': ('warm', 'empathetic', 'calm'),
    'corporate_professional': ('professional', 'trustworthy', 'confident'),
    'bold_editorial': ('authoritative', 'confident', 'premium'),
    'cyberpunk_neon': ('technical', 'bold', 'energetic'),
    'pastel_soft': ('warm', 'friendly', 'calm'),
    'scandinavian_clean': ('calm', 'professional', 'trustworthy'),
    'art_deco_geometric': ('premium', 'aspirational', 'confident'),
    'tropical_vibrant': ('energetic', 'friendly', 'playful'),
    'dark_academia': ('authoritative', 'educational', 'premium'),
    'memphis_design': ('playful', 'bold', 'energetic'),
    'zen_japanese': ('calm', 'empathetic', 'warm'),
    'industrial_grunge': ('bold', 'confident', 'energetic'),
    'y2k_retro_futurism': ('playful', 'energetic', 'aspirational'),
    'bohemian_eclectic': ('warm', 'friendly', 'aspirational'),
}


STYLE_THEME_PALETTES = [
    ('modern_minimalist', 'Modern Minimalist', (
        ('Slate Professional', '#1E3A5F', '#4B5563', '#C5D4E3', '#0052CC', '#E8EDF2', 'Inter', 'Inter'),
        ('Warm Neutral', '#2D3748', '#4A4540', '#E2D9CE', '#D97706', '#FAF5EF', 'Inter', 'Inter'),
        ('Cool Sage', '#1A3A2A', '#3D5040', '#D4E5D8', '#16A34A', '#F0F7F2', 'Inter', 'Inter'),
        ('Ink & Paper', '#1F2937', '#4B5563', '#D1D5DB', '#4F46E5', '#FFFFFF', 'Outfit', 'Inter'),
    )),
    ('glassmorphism', 'Glassmorphism', (
        ('Glass Azure', '#1A365D', '#334E68', '#B0D4E8', '#3182CE', '#D6EBF5', 'Inter', 'Inter'),
        ('Frosted Lavender', '#2D1B69', '#4A3870', '#D4C4F0', '#7C3AED', '#EDE9FE', 'Inter', 'Inter'),
        ('Ice Crystal', '#164E63', '#2E5A68', '#A5F3FC', '#06B6D4', '#ECFEFF', 'Inter', 'Inter'),
        ('Ocean Mist', '#1E3A3A', '#3A5858', '#B2DFDB', '#009688', '#E0F2F1', 'Inter', 'Inter'),
    )),
    ('retro_vintage', 'Retro Vintage', (
        ('Pop Art Yellow', '#0D0D0D', '#2D2D00', '#FFD600', '#FF0000', '#FFEB3B', 'Bebas Neue', 'Merriweather'),
        ('Disco Sunset', '#1A0A2E', '#3A2040', '#FF6B6B', '#FF2D87', '#FFB347', 'Bebas Neue', 'Merriweather'),
        ('Arcade Neon', '#0D0D0D', '#B0B0C8', '#39FF14', '#FF073A', '#1A1A2E', 'Bebas Neue', 'Merriweather'),
        ('Vinyl Brown', '#2C1810', '#4A3828', '#D4A574', '#E85D04', '#FDF0D5', 'Bebas Neue', 'Merriweather'),
    )),
    ('neubrutalism', 'Neubrutalism', (
        ('Concrete Raw', '#1A1A1A', '#3D3D3D', '#C8C4BB', '#FF4D00', '#E5E2DD', 'Space Grotesk', 'IBM Plex Sans'),
        ('Highlighter Shock', '#000000', '#333333', '#E8E8E8', '#FFE500', '#FFFFFF', 'Space Grotesk', 'IBM Plex Sans'),
        ('Acid Green', '#0D0D0D', '#2D2D2D', '#C1FF72', '#FF3864', '#F0FFE0', 'Space Grotesk', 'IBM Plex Sans'),
        ('Hot Pink Brutal', '#1A1A1A', '#3D3D3D', '#FFB4D2', '#FF006E', '#FFF0F5', 'Space Grotesk', 'IBM Plex Sans'),
    )),
    ('claymorphism', 'Claymorphism', (
        ('Bubblegum', '#4A1942', '#5A3058', '#F5B0D0', '#FF1493', '#FFD6E6', 'Poppins', 'Nunito Sans'),
        ('Lavender Dream', '#3B1F7E', '#4A3068', '#D4B8FF', '#8B5CF6', '#F3EEFF', 'Poppins', 'Nunito Sans'),
        ('Mint Cream', '#1A4A3A', '#3A5A4A', '#A7F3D0', '#10B981', '#ECFDF5', 'Poppins', 'Nunito Sans'),
        ('Sunset Peach', '#7C2D12', '#5A3828', '#FDBA74', '#F97316', '#FFF7ED', 'Poppins', 'Nunito Sans'),
    )),
    ('aurora_gradient', 'Aurora Gradient', (
        ('Holographic', '#1A2035', '#384860', '#C8D8F0', '#EC4899', '#E6F0FA', 'Sora', 'Inter'),
        ('Sunset Glow', '#1A1A2E', '#3A3848', '#FED7AA', '#F97316', '#FFF7ED', 'Sora', 'Inter'),
        ('Northern Lights', '#0F172A', '#2A3A48', '#A5F3FC', '#06B6D4', '#ECFEFF', 'Sora', 'Inter'),
        ('Deep Ocean', '#0C1445', '#2A3860', '#818CF8', '#6366F1', '#EEF2FF', 'Sora', 'Inter'),
    )),
    ('monochrome_dark', 'Monochrome Dark', (
        ('Cinema Noir', '#F5F5F5', '#C8C8C8', '#1F1F1F', '#DC143C', '#0F0F0F', 'Space Grotesk', 'Inter'),
        ('Midnight Blue', '#E2E8F0', '#B0B8C8', '#1E293B', '#3B82F6', '#0F172A', 'Space Grotesk', 'Inter'),
        ('Charcoal Silver', '#F0F0F0', '#B8B8B8', '#2A2A2A', '#A3A3A3', '#141414', 'Space Grotesk', 'Inter'),
        ('Obsidian Red', '#FEE2E2', '#C8B0B0', '#1C1917', '#EF4444', '#0C0A09', 'Space Grotesk', 'Inter'),
    )),
    ('elegant_luxury', 'Elegant Luxury', (
        ('Gold Standard', '#1A1A1A', '#4A4A4A', '#D4AF37', '#B8860B', '#FFFDF7', 'Playfair Display', 'Inter'),
        ('Champagne', '#2C2C2C', '#4A4848', '#E8D5B7', '#C9A96E', '#FAF6F0', 'Playfair Display', 'Inter'),
        ('Midnight Velvet', '#F5F0E8', '#C8C0B8', '#2C1810', '#9B7B4E', '#1A1A2E', 'Playfair Display', 'Inter'),
        ('Pearl & Onyx', '#1C1C1C', '#4A4A48', '#E8E4DE', '#8B7355', '#FAFAF8', 'Cormorant Garamond', 'Inter'),
    )),
    ('organic_natural', 'Organic Natural', (
        ('Forest Floor', '#1A3A1A', '#3A5A3A', '#E0EBD8', '#2E8B57', '#F5FAF0', 'Playfair Display', 'Inter'),
        ('Desert Sand', '#5C4033', '#6A5040', '#E8D5B7', '#C2703E', '#FDF6EC', 'Lora', 'Inter'),
        ('Herb Garden', '#2D4A2D', '#4A5A40', '#D4E2C8', '#6B8F3C', '#F4F9EE', 'Playfair Display', 'Inter'),
        ('Terra Cotta', '#6B3A2A', '#6A4A38', '#E8C4A8', '#C1582A', '#FFF5EB', 'Lora', 'Inter'),
    )),
    ('corporate_professional', 'Corporate Professional', (
        ('Trust Blue', '#1E3A5F', '#4B5563', '#E2E8F0', '#2563EB', '#F8FAFC', 'Inter', 'Inter'),
        ('Executive Grey', '#374151', '#4B5563', '#E5E7EB', '#4F46E5', '#F9FAFB', 'Inter', 'Inter'),
        ('Legal Navy', '#1E293B', '#475569', '#CBD5E1', '#0EA5E9', '#F0F4F8', 'Inter', 'Inter'),
        ('Finance Green', '#14532D', '#3A5A40', '#D1FAE5', '#059669', '#F0FDF4', 'Inter', 'Inter'),
    )),
    ('bold_editorial', 'Bold Editorial', (
        ('Print Classic', '#1A1A1A', '#374151', '#F5F5F0', '#DC2626', '#FFFFFF', 'Playfair Display', 'Inter'),
        ('Red Masthead', '#1C1917', '#3D3830', '#FEE2E2', '#B91C1C', '#FFFBEB', 'Playfair Display', 'Inter'),
        ('Newsroom Grey', '#111827', '#374151', '#E5E7EB', '#2563EB', '#F3F4F6', 'Sora', 'Inter'),
        ('Broadsheet', '#292524', '#44403C', '#D6D3D1', '#EA580C', '#FAFAF9', 'Cormorant Garamond', 'Inter'),
    )),
    ('cyberpunk_neon', 'Cyberpunk Neon', (
        ('Electric Purple', '#E0E7FF', '#B0B8D8', '#1E1B4B', '#A855F7', '#0F0B1A', 'Space Grotesk', 'Inter'),
        ('Neon Matrix', '#D1FAE5', '#A0C8B0', '#064E3B', '#10B981', '#022C22', 'Space Grotesk', 'Inter'),
        ('Chrome Pink', '#FCE7F3', '#C8B0C0', '#4A1942', '#EC4899', '#0F0A15', 'Space Grotesk', 'Inter'),
        ('Cyber Teal', '#CCFBF1', '#A0C8C0', '#134E4A', '#14B8A6', '#042F2E', 'Space Grotesk', 'Inter'),
    )),
    ('pastel_soft', 'Pastel Soft', (
        ('Cotton Candy', '#6B2D5B', '#5A3858', '#FBCFE8', '#EC4899', '#FDF2F8', 'Poppins', 'Nunito Sans'),
        ('Sky Breeze', '#1E3A5F', '#3A5068', '#BAE6FD', '#0EA5E9', '#F0F9FF', 'Poppins', 'Nunito Sans'),
        ('Lavender Fields', '#4C1D95', '#4A3068', '#DDD6FE', '#8B5CF6', '#F5F3FF', 'Poppins', 'Nunito Sans'),
        ('Peach Blossom', '#7C2D12', '#5A3828', '#FED7AA', '#F97316', '#FFF7ED', 'Poppins', 'Nunito Sans'),
    )),
    ('scandinavian_clean', 'Scandinavian Clean', (
        ('Fjord Grey', '#374151', '#6B7280', '#E5E7EB', '#6B7280', '#FFFFFF', 'Inter', 'Inter'),
        ('Birch Wood', '#44403C', '#57534E', '#E7E5E4', '#A8A29E', '#FAFAF9', 'Inter', 'Inter'),
        ('Winter White', '#1F2937', '#4B5563', '#F3F4F6', '#3B82F6', '#FFFFFF', 'Inter', 'Inter'),
        ('Copenhagen Blue', '#1E3A5F', '#4B5563', '#DBEAFE', '#2563EB', '#F8FAFF', 'Inter', 'Inter'),
    )),
    ('art_deco_geometric', 'Art Deco Geometric', (
        ('Gatsby Gold', '#0D0D0D', '#C8C8B8', '#D4AF37', '#B8860B', '#1A1A2E', 'Playfair Display', 'Inter'),
        ('Emerald Ballroom', '#F5F0E8', '#C8C0B0', '#065F46', '#D4AF37', '#064E3B', 'Playfair Display', 'Inter'),
        ('Onyx & Brass', '#F5F5F0', '#C8C8C0', '#D4AF37', '#B45309', '#1C1917', 'Cormorant Garamond', 'Inter'),
        ('Ruby Theater', '#FEE2E2', '#C8A8A8', '#991B1B', '#D4AF37', '#450A0A', 'Playfair Display', 'Inter'),
    )),
    ('tropical_vibrant', 'Tropical Vibrant', (
        ('Island Sunset', '#1C1917', '#3D3830', '#FDBA74', '#F97316', '#FFF7ED', 'Poppins', 'Nunito Sans'),
        ('Jungle Canopy', '#14532D', '#3A5A3A', '#BBF7D0', '#22C55E', '#F0FDF4', 'Poppins', 'Nunito Sans'),
        ('Coral Reef', '#9F1239', '#6A2838', '#FDA4AF', '#F43F5E', '#FFF1F2', 'Poppins', 'Nunito Sans'),
        ('Mango Splash', '#713F12', '#5A4828', '#FEF08A', '#EAB308', '#FEFCE8', 'Poppins', 'Nunito Sans'),
    )),
    ('dark_academia', 'Dark Academia', (
        ('Oxford Library', '#F5E6D3', '#C8B8A0', '#3C2415', '#8B6914', '#2C1810', 'Cormorant Garamond', 'Inter'),
        ('Sepia Study', '#E8D5B7', '#B8A890', '#4A3728', '#C2703E', '#352A21', 'Playfair Display', 'Inter'),
        ('Midnight Scholar', '#E2E8F0', '#B0B8C8', '#1E293B', '#9B7B4E', '#0F172A', 'Cormorant Garamond', 'Inter'),
        ('Parchment Ink', '#44403C', '#57534E', '#E7E5E4', '#92400E', '#FEFCE8', 'Playfair Display', 'Inter'),
    )),
    ('memphis_design', 'Memphis Design', (
        ('Primary Shapes', '#1A1A1A', '#2D2D2D', '#FFD700', '#FF3366', '#00BFFF', 'Space Grotesk', 'IBM Plex Sans'),
        ('Squiggle Pink', '#1A1A1A', '#3D3D3D', '#FF69B4', '#39FF14', '#FFE4E1', 'Space Grotesk', 'IBM Plex Sans'),
        ('Confetti', '#1A1A1A', '#3D3D3D', '#FF6B35', '#7B2FF7', '#FFFACD', 'Space Grotesk', 'IBM Plex Sans'),
        ('Electric Grid', '#FFFFFF', '#C8C8C8', '#FF1493', '#00FF7F', '#1A1A2E', 'Space Grotesk', 'IBM Plex Sans'),
    )),
    ('zen_japanese', 'Zen Japanese', (
        ('Bamboo Garden', '#374151', '#57534E', '#D1D5C0', '#6B7F4E', '#F5F5F0', 'Inter', 'Inter'),
        ('Stone Temple', '#44403C', '#57534E', '#D6D3D1', '#A8A29E', '#FAFAF9', 'Inter', 'Inter'),
        ('Cherry Blossom', '#4C1D3A', '#5A3050', '#FBCFE8', '#DB2777', '#FDF2F8', 'Inter', 'Inter'),
        ('Ink Wash', '#1F2937', '#4B5563', '#E5E7EB', '#6B7280', '#FFFFFF', 'Inter', 'Inter'),
    )),
    ('industrial_grunge', 'Industrial Grunge', (
        ('Iron Forge', '#E5E5E5', '#B0B0B0', '#2D2D2D', '#D97706', '#1A1A1A', 'Space Grotesk', 'Inter'),
        ('Rust & Concrete', '#F5E6D3', '#C0B0A0', '#44403C', '#B45309', '#292524', 'Space Grotesk', 'Inter'),
        ('Smoke Stack', '#D1D5DB', '#A0A8B0', '#374151', '#EF4444', '#111827', 'Space Grotesk', 'Inter'),
        ('Warehouse Grey', '#1F2937', '#4B5563', '#D1D5DB', '#F59E0B', '#F3F4F6', 'Space Grotesk', 'Inter'),
    )),
    ('y2k_retro_futurism', 'Y2K Retro-futurism', (
        ('Cyber Chrome', '#1A1A2E', '#3A3A50', '#C0C0C0', '#7B68EE', '#E8E8FF', 'Sora', 'Inter'),
        ('Bubblegum Tech', '#4A1942', '#5A3050', '#FFB6C1', '#FF69B4', '#FFF0F5', 'Sora', 'Inter'),
        ('Hologram', '#0F172A', '#2A3848', '#A5F3FC', '#06B6D4', '#F0FDFF', 'Sora', 'Inter'),
        ('Digital Lavender', '#2E1065', '#4A3868', '#C4B5FD', '#8B5CF6', '#F5F3FF', 'Sora', 'Inter'),
    )),
    ('bohemian_eclectic', 'Bohemian Eclectic', (
        ('Moroccan Sunset', '#5C2018', '#5A3828', '#F4A261', '#E76F51', '#FFF5EB', 'Lora', 'Inter'),
        ('Gypsy Rose', '#4A1942', '#5A3050', '#E8A0BF', '#C74B7A', '#FFF0F5', 'Lora', 'Inter'),
        ('Artisan Clay', '#6B3A2A', '#5A4838', '#D4A574', '#B8621B', '#FAF0E6', 'Playfair Display', 'Inter'),
        ('Festival Nights', '#F5E6D3', '#C8B8A0', '#6B2D5B', '#D4AF37', '#1A1A2E', 'Lora', 'Inter'),
    )),
]


def _palette_key(style_key, label):
    label_key = ''.join(ch if ch.isalnum() else '_' for ch in label.lower()).strip('_')
    while '__' in label_key:
        label_key = label_key.replace('__', '_')
    return f'{style_key}_{label_key}'


def _palette(style_key, label, primary, text, secondary, accent, background, heading_font, body_font):
    category = THEME_CATEGORY_BY_KEY[style_key]
    tone_tags = []
    for tone in STYLE_TONE_TAGS.get(style_key, ()) + CATEGORY_TONE_TAGS.get(category, ()):
        if tone not in tone_tags:
            tone_tags.append(tone)
    theme_keys = [style_key, *BUSINESS_THEME_ALIASES.get(style_key, ())]
    return {
        'key': _palette_key(style_key, label),
        'label': label,
        'category': category,
        'theme_keys': theme_keys,
        'tone_tags': tone_tags,
        'colors': {
            'primary': primary,
            'text': text,
            'secondary': secondary,
            'accent': accent,
            'background': background,
        },
        'fonts': {
            'heading': heading_font,
            'body': body_font,
        },
        'source': 'style_theme_reference',
    }


COLOR_PALETTE_OPTIONS = [
    _palette(style_key, *palette)
    for style_key, _style_label, palettes in STYLE_THEME_PALETTES
    for palette in palettes
]
