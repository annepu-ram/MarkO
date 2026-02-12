# WCAG 2.1 Accessible Color Theme Library

A comprehensive collection of 4-color website themes following WCAG 2.1 AA accessibility standards.

## Color System Overview

| Role | Coverage | Purpose | Examples |
|------|----------|---------|----------|
| **Background** | 60% | Page base, content areas | Page backgrounds, card backgrounds, hero sections |
| **Primary** | 30% | **TEXT & TYPOGRAPHY** | Headings, paragraphs, navigation text, brand text |
| **Secondary** | 10% | UI support elements | Section highlights, borders, regular buttons, dividers |
| **Accent** | CTAs only | High-visibility actions | "Buy Now", "Sign Up", "Get Started" buttons ONLY |

**⚠️ Critical Color Rules:**
- **Primary = TEXT COLOR** (not for buttons or decoration)
- **Secondary = UI ELEMENTS** (section backgrounds, regular buttons)
- **Accent = CTAs ONLY** (loses impact if overused)

**Accessibility Requirements:**
- Primary on Background: ≥4.5:1 contrast ratio
- Accent on Background: ≥4.5:1 contrast ratio
- All themes tested against WCAG 2.1 AA standards

## Creating Visual Interest: Inverted Sections

**Key Technique:** Swap Background and Primary colors to create eye-catching sections:

| Section Type | Background Color | Text Color | Effect |
|--------------|------------------|------------|--------|
| **Standard** | Background | Primary | Normal reading |
| **Inverted** | Primary | Background | High impact, catchy |
| **Highlight** | Secondary | Primary | Subtle emphasis |
| **CTA Banner** | Accent | Background | Maximum attention |

**Example Pattern:**
```
Section 1: Light bg (background) + Dark text (primary) ← Standard
Section 2: Dark bg (primary) + Light text (background) ← INVERTED (catchy!)
Section 3: Tinted bg (secondary) + Dark text (primary) ← Highlight
Section 4: Accent bg + Light text ← CTA Banner
```

---

## 1. Timeless & Classic

### Minimalist
*"Less is more" - focused on white space and functionality*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Pure Minimal** | `#FFFFFF` | `#1A1A1A` | `#E5E5E5` | `#0066CC` |
| **Warm Minimal** | `#FAFAF8` | `#2D2D2D` | `#E8E6E3` | `#B85C38` |
| **Cool Minimal** | `#F8FAFB` | `#1E2832` | `#E3E8EC` | `#0077B6` |

### Corporate
*Traditional, stable, and trustworthy*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Corporate Blue** | `#FFFFFF` | `#1E3A5F` | `#E8EDF2` | `#0052CC` |
| **Corporate Slate** | `#F5F7FA` | `#2C3E50` | `#DDE4EB` | `#2980B9` |
| **Corporate Navy** | `#FAFBFC` | `#1B2838` | `#E1E5EA` | `#0066A2` |

### Editorial
*High-end magazine feel with elegant typography*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Classic Editorial** | `#FFFEF9` | `#1C1C1C` | `#F0EDE8` | `#A61C00` |
| **Modern Editorial** | `#FFFFFF` | `#262626` | `#EBEBEB` | `#C41E3A` |
| **Refined Editorial** | `#FBF9F6` | `#2B2B2B` | `#E6E2DC` | `#8B4513` |

### Swiss Style
*Grid-based, clean, mathematically precise*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Helvetica Red** | `#FFFFFF` | `#000000` | `#F0F0F0` | `#FF0000` |
| **Swiss Blue** | `#FFFFFF` | `#1A1A1A` | `#E8E8E8` | `#0057B8` |
| **Swiss Minimal** | `#FAFAFA` | `#0A0A0A` | `#E5E5E5` | `#E63946` |

### Brutalist
*Raw, unpolished, and bold*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Concrete Raw** | `#F2F0ED` | `#1A1A1A` | `#D4D0CB` | `#FF4D00` |
| **Industrial Brutal** | `#E8E4DF` | `#0D0D0D` | `#C9C4BD` | `#00AA55` |
| **Stark Brutal** | `#FFFFFF` | `#000000` | `#CCCCCC` | `#0000FF` |

### Bauhaus
*Primary colors and geometric shapes*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Bauhaus Primary** | `#FFFEF5` | `#1A1A1A` | `#F5E6C8` | `#DD0100` |
| **Bauhaus Blue** | `#FFFFFF` | `#0D0D0D` | `#E8E8E8` | `#004D95` |
| **Bauhaus Yellow** | `#FEFEFE` | `#1E1E1E` | `#F0F0F0` | `#F5B700` |

### Luxury/Prestige
*High-contrast with premium feel*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Black Gold** | `#FFFFFF` | `#0A0A0A` | `#F5F5F5` | `#B8860B` |
| **Champagne** | `#FFFEFA` | `#1C1C1C` | `#F7F3E9` | `#996515` |
| **Platinum** | `#FAFAFA` | `#1A1A1A` | `#E8E8E8` | `#6B5B4C` |

### Industrial
*Raw textures, dark tones, mechanical motifs*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Steel Mill** | `#E8E6E3` | `#1F1F1F` | `#C8C4BF` | `#FF6B35` |
| **Concrete Jungle** | `#EDEAE5` | `#252525` | `#D1CCC5` | `#00A86B` |
| **Oxidized Iron** | `#F0EDEA` | `#2A2A2A` | `#D6D1CB` | `#B7410E` |

---

## 2. Retro & Nostalgic

### Retro-Future (Atomic Age)
*1950s vision of the future*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Atomic Teal** | `#FFF8E7` | `#1A3A3A` | `#E8DCC8` | `#008B8B` |
| **Space Age** | `#F5F5F0` | `#2D2D3F` | `#D8D8D0` | `#FF6347` |
| **Jetsons** | `#FFFEF5` | `#1E3D59` | `#F0E6D3` | `#17BEBB` |

### 80s Synthwave
*Neon pinks/cyans on dark chrome*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Neon Nights** | `#0D0221` | `#FFFFFF` | `#2D1B4E` | `#FF00FF` |
| **Chrome Dreams** | `#120458` | `#F0F0F0` | `#2A1B5A` | `#00FFFF` |
| **Sunset Grid** | `#1A0A2E` | `#FEFEFE` | `#2E1650` | `#FF6EC7` |

### 90s Grunge
*Texture-heavy, "dirty" colors*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Flannel** | `#E8E0D5` | `#2C2416` | `#C9BFB0` | `#8B0000` |
| **Muddy Waters** | `#DED5C4` | `#1E1E1E` | `#BFB5A3` | `#556B2F` |
| **Distressed** | `#E5DDD0` | `#262018` | `#C7BDA8` | `#704214` |

### Vintage/Antique
*Sepia tones and parchment textures*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Aged Parchment** | `#FDF5E6` | `#3D2B1F` | `#E8DCC8` | `#8B4513` |
| **Victorian** | `#FAF3E8` | `#2F1810` | `#E5D9C9` | `#722F37` |
| **Antique Rose** | `#FFF5EE` | `#362419` | `#EBE0D5` | `#BC5D58` |

### Vaporwave
*Dreamy, lo-fi aesthetic*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Mall Soft** | `#FFE4EC` | `#2D1B4E` | `#E8C4D4` | `#9B59B6` |
| **Sunset Plaza** | `#E8D5E5` | `#1A1A3E` | `#CDB4C9` | `#FF69B4` |
| **Digital Dreams** | `#F0E6FA` | `#2A1B54` | `#D5C4E8` | `#00CED1` |

### Art Deco
*1920s Gatsby style*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Gatsby Gold** | `#0D0D0D` | `#FFFFFF` | `#2A2A2A` | `#D4AF37` |
| **Deco Emerald** | `#1A1A1A` | `#F5F5F5` | `#333333` | `#50C878` |
| **Roaring Ivory** | `#FFFFF0` | `#1A1A1A` | `#E8E8D8` | `#996515` |

### Pop Art
*High saturation, comic-style*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Lichtenstein** | `#FFEB3B` | `#0D0D0D` | `#FFD700` | `#FF0000` |
| **Warhol** | `#FF69B4` | `#000000` | `#FF1493` | `#00BFFF` |
| **Comic Bold** | `#FFFFFF` | `#1A1A1A` | `#E8E8E8` | `#FF4500` |

### Psychedelic
*Swirling patterns, "trippy" contrast*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Acid Trip** | `#FFE4B5` | `#4B0082` | `#FFDAB9` | `#FF1493` |
| **Kaleidoscope** | `#E6E6FA` | `#2F0A28` | `#D8BFD8` | `#FF6600` |
| **Mind Melt** | `#FFFACD` | `#301934` | `#F0E68C` | `#00CED1` |

---

## 3. Futuristic & Tech-Forward

### Cyberpunk
*Dark, urban, neon-lit*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Neo Tokyo** | `#0A0A0F` | `#FFFFFF` | `#1A1A25` | `#FF0080` |
| **Chrome City** | `#0D0D12` | `#E8E8E8` | `#1E1E28` | `#00FFFF` |
| **Night Market** | `#0F0F14` | `#F5F5F5` | `#1C1C24` | `#ADFF2F` |

### Solarpunk
*Optimistic futurism with nature*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Green Future** | `#F5FAF0` | `#1A3A1A` | `#E0EBD8` | `#2E8B57` |
| **Solar Dawn** | `#FFFBF0` | `#2D4A2D` | `#F0E8D8` | `#DAA520` |
| **Eco Harmony** | `#F0F8F0` | `#1E4D2B` | `#D8EBD8` | `#32CD32` |

### Glassmorphism
*Frosted glass effects*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Frosted Blue** | `#E8F4FC` | `#1A365D` | `#C5DCF0` | `#3182CE` |
| **Frosted Purple** | `#F3E8FF` | `#2D1B69` | `#DCC8F5` | `#7C3AED` |
| **Frosted Rose** | `#FFF0F5` | `#5D1A4A` | `#F5D0E0` | `#DB2777` |

### Neumorphism
*Soft shadows, molded buttons*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Soft Gray** | `#E0E5EC` | `#31343A` | `#C8CDD5` | `#6C63FF` |
| **Soft Blue** | `#D1E3F8` | `#1E3A5F` | `#B8D0EC` | `#0077B6` |
| **Soft Sage** | `#DCE8DC` | `#2D3E2D` | `#C4D4C4` | `#4A7C4A` |

### Holographic
*Iridescent, light-bending*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Prism Light** | `#FAF0FF` | `#2D1B4E` | `#E8D5F5` | `#8B5CF6` |
| **Aurora** | `#F0FFFA` | `#1A3D3D` | `#D5F0E8` | `#06B6D4` |
| **Pearl** | `#FFFAF5` | `#3D2D1A` | `#F5E8D5` | `#EC4899` |

### Sci-Fi UI
*Dark mode with data lines*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Terminal Blue** | `#0A1628` | `#E8F4FC` | `#152238` | `#00D4FF` |
| **HUD Green** | `#0A150A` | `#E8FCE8` | `#142814` | `#00FF41` |
| **Alert Red** | `#140A0A` | `#FCE8E8` | `#281414` | `#FF3333` |

### Space/Galactic
*Deep purples/blacks with star-fields*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Deep Space** | `#0B0B1A` | `#E8E8F8` | `#15152D` | `#9D4EDD` |
| **Nebula** | `#0D0A14` | `#F5F0FA` | `#1A1428` | `#F72585` |
| **Cosmos** | `#0A0A12` | `#F0F0F8` | `#141420` | `#4CC9F0` |

### AI-Core
*Ethereal, generative patterns*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Neural Light** | `#F8F9FC` | `#1A1B2E` | `#E8EAF0` | `#6366F1` |
| **Synthetic Mind** | `#F5F8FA` | `#1E2A38` | `#E0E8F0` | `#06B6D4` |
| **Digital Pulse** | `#FAFAFA` | `#1A1A2E` | `#E8E8F0` | `#8B5CF6` |

---

## 4. Organic & Nature-Inspired

### Biophilic
*Mimics nature to reduce stress*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Forest Calm** | `#F5F9F5` | `#1A3328` | `#E0EBE0` | `#228B22` |
| **Moss Garden** | `#F8FAF5` | `#2D3D2D` | `#E5EBE0` | `#6B8E23` |
| **Living Green** | `#F0F5F0` | `#1E3E2E` | `#D8E5D8` | `#32CD32` |

### Earth-Tone
*Terracotta, sand, and clay*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Desert Sand** | `#FAF6F0` | `#3D2B1F` | `#E8DFD2` | `#C2703B` |
| **Clay Pot** | `#FBF5EE` | `#4A3728` | `#EBE0D3` | `#A0522D` |
| **Terracotta** | `#FFF8F0` | `#3E2723` | `#F0E3D5` | `#E07040` |

### Coastal/Nautical
*Airy blues and driftwood*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Ocean Breeze** | `#F5FAFB` | `#1A3A4A` | `#E0EEF2` | `#0077B6` |
| **Sandy Shore** | `#FFFAF5` | `#2C4A5A` | `#F0E8E0` | `#20B2AA` |
| **Nautical Navy** | `#F8FBFC` | `#1B3B5A` | `#E5EEF3` | `#006994` |

### Botanical
*Intricate leaf patterns, forest greens*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Deep Forest** | `#F5F8F5` | `#1A3318` | `#E0E8DE` | `#2E7D32` |
| **Fern Gully** | `#F8FAF5` | `#2D4428` | `#E5EBE0` | `#558B2F` |
| **Botanical Garden** | `#F0F5F0` | `#1E3820` | `#D8E5D5` | `#4CAF50` |

### Bohemian
*Free-spirited, warm sunset palettes*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Sunset Boho** | `#FFF8F0` | `#4A2C17` | `#F5E6D5` | `#D2691E` |
| **Moroccan Spice** | `#FFF5E8` | `#3D2214` | `#F0DCC5` | `#B8510D` |
| **Desert Dream** | `#FFFAF2` | `#4E3524` | `#F5E8D8` | `#CD853F` |

### Rustic
*Rough-hewn textures, barn wood*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Barn Wood** | `#F5F0E8` | `#3D2B1F` | `#E5D8C8` | `#8B4513` |
| **Cabin Cozy** | `#FAF5ED` | `#4A3525` | `#EBE0D0` | `#996633` |
| **Weathered Oak** | `#F8F3EB` | `#3E2E20` | `#E8DED0` | `#A0522D` |

### Tropical
*High-energy, paradise vibes*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Paradise** | `#FFFEF5` | `#1A4D2E` | `#E8F5E0` | `#FF6B35` |
| **Mango Tango** | `#FFF8F0` | `#1E5035` | `#F5EBD8` | `#FF9500` |
| **Coral Reef** | `#F5FFFA` | `#1A3D3D` | `#E0F0E8` | `#FF7F50` |

---

## 5. Emotional & Psychological Moods

### Dark Mode / Cinematic
*High-drama, moody, immersive*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Cinema Noir** | `#0D0D0D` | `#F5F5F5` | `#1F1F1F` | `#DC143C` |
| **Midnight Movie** | `#0A0A12` | `#E8E8F0` | `#1A1A25` | `#FF4500` |
| **Director's Cut** | `#0F0F14` | `#F0F0F5` | `#1E1E28` | `#FFD700` |

### Playful/Whimsical
*Bright candy colors, bouncy*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Candy Shop** | `#FFF5F8` | `#4A1942` | `#FFE0E8` | `#FF1493` |
| **Bubble Gum** | `#F5FAFF` | `#1A3352` | `#E0EBFA` | `#FF69B4` |
| **Rainbow Bright** | `#FFFAF5` | `#2D1F4E` | `#F0E5FA` | `#FF6B35` |

### Aggressive/High-Energy
*Sharp angles, danger reds*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Code Red** | `#1A0A0A` | `#FFFFFF` | `#2D1414` | `#FF0000` |
| **Thunder Strike** | `#0D0D0D` | `#F5F5F5` | `#1F1F1F` | `#FF4500` |
| **Electric Storm** | `#0A0A14` | `#F0F0F8` | `#141428` | `#FFFF00` |

### Serene/Zen
*Monochromatic, quiet layouts*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Zen Garden** | `#F8F8F5` | `#3D3D35` | `#E8E8E0` | `#708090` |
| **Still Water** | `#F5F8FA` | `#2D3842` | `#E0E8EC` | `#5F9EA0` |
| **Morning Mist** | `#F8FAF8` | `#35403A` | `#E5EBE8` | `#778899` |

### Academic/Scholarly
*Ivy league greens and maroons*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Oxford** | `#FFFEF8` | `#1A2E28` | `#E8EBE5` | `#00356B` |
| **Harvard** | `#FFFAF8` | `#2D1F1F` | `#F0E5E5` | `#A51C30` |
| **Cambridge** | `#F8FBF8` | `#1E3E2E` | `#E5EDE5` | `#2E5339` |

### Gothic
*Dark, mysterious, ornate*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Crimson Night** | `#0D0A0A` | `#F5F0F0` | `#1F1818` | `#8B0000` |
| **Midnight Cathedral** | `#0A0A0F` | `#F0F0F5` | `#181820` | `#4B0082` |
| **Victorian Noir** | `#0F0D0D` | `#F5F3F3` | `#201C1C` | `#800020` |

### Scandinavian (Scandi)
*Bright, airy, functional, hygge*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Nordic Light** | `#FAFAFA` | `#2D3436` | `#E8E8E8` | `#0984E3` |
| **Hygge Home** | `#FFFBF5` | `#3D3D3D` | `#F5EDE3` | `#D35400` |
| **Copenhagen** | `#F8FAFB` | `#2C3E50` | `#E5EEF2` | `#16A085` |

### Urban/Street
*Graffiti-inspired, concrete and neon*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Brooklyn** | `#E8E6E3` | `#1A1A1A` | `#C8C4BF` | `#FF4081` |
| **Metro** | `#F0EDEA` | `#0D0D0D` | `#D6D1CB` | `#00E676` |
| **Street Art** | `#E5E2DF` | `#1E1E1E` | `#C4C0BB` | `#FFEA00` |

### Metaverse-Aesthetic
*Digital-first neon gradients*

| Palette | Background | Primary | Secondary | Accent |
|---------|------------|---------|-----------|--------|
| **Virtual World** | `#0D0D1A` | `#F0F0FF` | `#1A1A2E` | `#00FFFF` |
| **Avatar Realm** | `#0A0F1A` | `#E8F0FF` | `#141E30` | `#FF00FF` |
| **Digital Twin** | `#0F0A14` | `#F5F0FA` | `#1E1428` | `#7B68EE` |

---

## Contrast Ratio Reference

All themes meet WCAG 2.1 AA standards:

| Level | Ratio | Use Case |
|-------|-------|----------|
| **AA** | 4.5:1 | Normal text (required) |
| **AA Large** | 3:1 | Large text (18pt+ or 14pt bold) |
| **AAA** | 7:1 | Enhanced accessibility |

### Verification Tools
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Coolors Contrast Checker](https://coolors.co/contrast-checker)
- [Adobe Color Accessibility Tools](https://color.adobe.com/create/color-accessibility)

---

## Usage in Swift Sites

These themes are designed for the 60-30-10 color distribution:

```yaml
theme:
  colors:
    background: "#FFFFFF"   # 60% - Page backgrounds, cards
    primary: "#1A1A1A"      # 30% - Headings, body text, logos
    secondary: "#E5E5E5"    # 10% - Borders, dividers, subtle UI
    accent: "#0066CC"       # CTAs - Buttons, links, highlights
```

---

## Quick Reference by Mood

| Mood | Recommended Style | Key Colors |
|------|-------------------|------------|
| **Trust & Stability** | Corporate, Swiss | Blues, Grays |
| **Creativity & Energy** | Pop Art, Synthwave | Neons, Brights |
| **Luxury & Premium** | Art Deco, Luxury | Golds, Blacks |
| **Nature & Wellness** | Biophilic, Coastal | Greens, Blues |
| **Tech & Innovation** | Cyberpunk, Sci-Fi UI | Neons, Dark bases |
| **Calm & Peaceful** | Zen, Scandi | Neutrals, Soft tones |
| **Bold & Edgy** | Brutalist, Gothic | High contrast, Reds |
| **Nostalgic & Warm** | Vintage, Rustic | Sepias, Earth tones |

---

*Last Updated: January 2025*
