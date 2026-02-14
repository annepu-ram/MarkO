# Page Settings Panel Plan

**Date:** 2025-10-10
**Objective:** Add a dedicated "Page" navigation item in the sidebar with comprehensive page-level settings including theme colors, SEO, and universal website options.

---

## Overview

Add a fourth panel to the sidebar navigation (alongside Components and Properties) that provides page-level configuration options. This centralizes all global settings that affect the entire website, including color themes, SEO metadata, fonts, and layout preferences.

---

## Sidebar Navigation Enhancement

### Current Sidebar Nav Items:
1. **Components** - Component library for insertion
2. **Properties** - Selected component properties editor

### New Addition:
3. **Page** (or "Settings") - Global page-level configuration

### Visual Structure:
```
┌────────────────────────────────┐
│ Sidebar    │   Main Canvas     │
├────────────┤                   │
│ [Nav]  │ P │                   │
│        │ a │                   │
│ [📦]   │ n │                   │
│ Comps  │ e │                   │
│        │ l │                   │
│ [⚙️]   │   │                   │
│ Props  │ C │                   │
│        │ o │                   │
│ [🌐]   │ n │  ← NEW PANEL!     │
│ Page   │ t │                   │
│        │ e │                   │
│        │ n │                   │
│        │ t │                   │
└────────┴───┴───────────────────┘
```

---

## Page Settings Categories

### 1. Theme Colors (Primary Feature)

**Purpose:** Allow users to quickly apply professional color schemes to their website with pre-curated palettes from multiple themes.

#### Theme Categories & Color Palettes

Each palette contains 4 colors:
- **Primary Color** - Main brand color (buttons, links, accents)
- **Secondary Color** - Supporting color (secondary buttons, highlights)
- **Accent Color** - Call-to-action color (CTAs, important elements)
- **Background/Neutral Color** - Page backgrounds, cards, surfaces

---

#### **Blue Themes** (Professional, Trust, Technology)

1. **Ocean Breeze**
   - Primary: `#4A90E2` (Sky Blue)
   - Secondary: `#7BA3CC` (Soft Blue)
   - Accent: `#2E5C8A` (Deep Blue)
   - Neutral: `#F0F4F8` (Light Blue-Gray)

2. **Corporate Navy**
   - Primary: `#1E3A8A` (Navy Blue)
   - Secondary: `#3B82F6` (Bright Blue)
   - Accent: `#60A5FA` (Light Blue)
   - Neutral: `#EFF6FF` (Ice Blue)

3. **Tech Modern**
   - Primary: `#0EA5E9` (Sky)
   - Secondary: `#06B6D4` (Cyan)
   - Accent: `#0284C7` (Deep Sky)
   - Neutral: `#F0F9FF` (Pale Cyan)

4. **Arctic Ice**
   - Primary: `#38BDF8` (Light Blue)
   - Secondary: `#BAE6FD` (Pale Blue)
   - Accent: `#0369A1` (Ocean Blue)
   - Neutral: `#F0FBFF` (Ice White)

5. **Midnight Blue**
   - Primary: `#1E40AF` (Royal Blue)
   - Secondary: `#3B82F6` (Medium Blue)
   - Accent: `#60A5FA` (Light Blue)
   - Neutral: `#DBEAFE` (Pale Blue)

6. **Navy Elegance**
   - Primary: `#1E293B` (Slate Navy)
   - Secondary: `#475569` (Cool Gray)
   - Accent: `#3B82F6` (Bright Blue)
   - Neutral: `#F1F5F9` (Light Slate)

7. **Sky Gradient**
   - Primary: `#0284C7` (Ocean Blue)
   - Secondary: `#0EA5E9` (Sky Blue)
   - Accent: `#38BDF8` (Light Sky)
   - Neutral: `#E0F2FE` (Pale Sky)

8. **Blue Steel**
   - Primary: `#334155` (Slate Blue)
   - Secondary: `#64748B` (Cool Slate)
   - Accent: `#0EA5E9` (Bright Sky)
   - Neutral: `#F8FAFC` (Off White)

9. **Aqua Marine**
   - Primary: `#0891B2` (Teal Blue)
   - Secondary: `#06B6D4` (Cyan)
   - Accent: `#67E8F9` (Light Cyan)
   - Neutral: `#ECFEFF` (Pale Cyan)

10. **Deep Ocean**
    - Primary: `#075985` (Deep Blue)
    - Secondary: `#0284C7` (Ocean Blue)
    - Accent: `#0EA5E9` (Sky Blue)
    - Neutral: `#F0F9FF` (Ice Blue)

---

#### **Orange Themes** (Energy, Creativity, Warmth)

1. **Sunset Glow**
   - Primary: `#F97316` (Orange)
   - Secondary: `#FB923C` (Light Orange)
   - Accent: `#EA580C` (Deep Orange)
   - Neutral: `#FFF7ED` (Cream)

2. **Autumn Harvest**
   - Primary: `#EA580C` (Burnt Orange)
   - Secondary: `#F59E0B` (Amber)
   - Accent: `#D97706` (Dark Amber)
   - Neutral: `#FFFBEB` (Light Cream)

3. **Tangerine Dream**
   - Primary: `#FB923C` (Tangerine)
   - Secondary: `#FDBA74` (Peach)
   - Accent: `#F97316` (Bright Orange)
   - Neutral: `#FFF7ED` (Off White)

4. **Coral Reef**
   - Primary: `#F97316` (Coral Orange)
   - Secondary: `#FDBA74` (Light Coral)
   - Accent: `#C2410C` (Deep Coral)
   - Neutral: `#FFF7ED` (Pale Peach)

5. **Pumpkin Spice**
   - Primary: `#EA580C` (Pumpkin)
   - Secondary: `#FB923C` (Light Pumpkin)
   - Accent: `#C2410C` (Dark Pumpkin)
   - Neutral: `#FFF7ED` (Cream)

6. **Citrus Burst**
   - Primary: `#F59E0B` (Bright Amber)
   - Secondary: `#FCD34D` (Yellow)
   - Accent: `#EA580C` (Orange)
   - Neutral: `#FFFBEB` (Light Yellow)

7. **Terracotta**
   - Primary: `#DC2626` (Terracotta Red)
   - Secondary: `#F97316` (Orange)
   - Accent: `#EA580C` (Burnt Orange)
   - Neutral: `#FEF2F2` (Pale Rose)

8. **Peachy Keen**
   - Primary: `#FDBA74` (Peach)
   - Secondary: `#FED7AA` (Light Peach)
   - Accent: `#F97316` (Orange)
   - Neutral: `#FFEDD5` (Cream)

9. **Mango Tango**
   - Primary: `#F59E0B` (Mango)
   - Secondary: `#FCD34D` (Yellow Mango)
   - Accent: `#D97706` (Deep Mango)
   - Neutral: `#FEF3C7` (Pale Yellow)

10. **Flame Orange**
    - Primary: `#EA580C` (Flame)
    - Secondary: `#F97316` (Bright Flame)
    - Accent: `#C2410C` (Deep Flame)
    - Neutral: `#FFF7ED` (Cream)

---

#### **Green Themes** (Nature, Growth, Sustainability)

1. **Forest Canopy**
   - Primary: `#059669` (Emerald)
   - Secondary: `#10B981` (Green)
   - Accent: `#34D399` (Light Green)
   - Neutral: `#ECFDF5` (Mint Cream)

2. **Spring Meadow**
   - Primary: `#22C55E` (Grass Green)
   - Secondary: `#4ADE80` (Light Grass)
   - Accent: `#16A34A` (Deep Green)
   - Neutral: `#F0FDF4` (Pale Green)

3. **Mint Fresh**
   - Primary: `#10B981` (Mint)
   - Secondary: `#6EE7B7` (Light Mint)
   - Accent: `#059669` (Deep Mint)
   - Neutral: `#D1FAE5` (Pale Mint)

4. **Sage Garden**
   - Primary: `#84CC16` (Lime)
   - Secondary: `#A3E635` (Light Lime)
   - Accent: `#65A30D` (Olive)
   - Neutral: `#F7FEE7` (Pale Lime)

5. **Tropical Jungle**
   - Primary: `#059669` (Jungle Green)
   - Secondary: `#10B981` (Emerald)
   - Accent: `#047857` (Deep Forest)
   - Neutral: `#ECFDF5` (Pale Jade)

6. **Olive Grove**
   - Primary: `#65A30D` (Olive)
   - Secondary: `#84CC16` (Light Olive)
   - Accent: `#4D7C0F` (Dark Olive)
   - Neutral: `#F7FEE7` (Cream)

7. **Seafoam**
   - Primary: `#14B8A6` (Teal)
   - Secondary: `#5EEAD4` (Light Teal)
   - Accent: `#0D9488` (Deep Teal)
   - Neutral: `#F0FDFA` (Pale Teal)

8. **Mossy Stone**
   - Primary: `#16A34A` (Moss Green)
   - Secondary: `#22C55E` (Light Moss)
   - Accent: `#15803D` (Dark Moss)
   - Neutral: `#DCFCE7` (Pale Green)

9. **Eucalyptus**
   - Primary: `#10B981` (Eucalyptus)
   - Secondary: `#6EE7B7` (Light Eucalyptus)
   - Accent: `#059669` (Deep Green)
   - Neutral: `#ECFDF5` (Pale Mint)

10. **Pine Forest**
    - Primary: `#047857` (Pine Green)
    - Secondary: `#059669` (Forest Green)
    - Accent: `#10B981` (Light Green)
    - Neutral: `#D1FAE5` (Pale Forest)

---

#### **Red Themes** (Passion, Energy, Bold)

1. **Cherry Blossom**
   - Primary: `#EF4444` (Red)
   - Secondary: `#F87171` (Light Red)
   - Accent: `#DC2626` (Deep Red)
   - Neutral: `#FEF2F2` (Pale Pink)

2. **Crimson Sunset**
   - Primary: `#DC2626` (Crimson)
   - Secondary: `#EF4444` (Bright Red)
   - Accent: `#B91C1C` (Dark Red)
   - Neutral: `#FEE2E2` (Light Pink)

3. **Rose Garden**
   - Primary: `#F43F5E` (Rose)
   - Secondary: `#FB7185` (Light Rose)
   - Accent: `#E11D48` (Deep Rose)
   - Neutral: `#FFF1F2` (Pale Rose)

4. **Ruby Red**
   - Primary: `#DC2626` (Ruby)
   - Secondary: `#EF4444` (Light Ruby)
   - Accent: `#991B1B` (Deep Ruby)
   - Neutral: `#FEE2E2` (Pink Cream)

5. **Scarlet Flame**
   - Primary: `#EF4444` (Scarlet)
   - Secondary: `#FCA5A5` (Light Scarlet)
   - Accent: `#DC2626` (Deep Scarlet)
   - Neutral: `#FEF2F2` (Pale Red)

6. **Wine & Roses**
   - Primary: `#BE123C` (Wine)
   - Secondary: `#E11D48` (Rose)
   - Accent: `#9F1239` (Deep Wine)
   - Neutral: `#FFF1F2` (Pale Pink)

7. **Coral Sunset**
   - Primary: `#F43F5E` (Coral Red)
   - Secondary: `#FB7185` (Light Coral)
   - Accent: `#E11D48` (Deep Coral)
   - Neutral: `#FFE4E6` (Pale Coral)

8. **Brick & Mortar**
   - Primary: `#DC2626` (Brick Red)
   - Secondary: `#EF4444` (Light Brick)
   - Accent: `#B91C1C` (Deep Brick)
   - Neutral: `#FEE2E2` (Cream)

9. **Raspberry**
   - Primary: `#E11D48` (Raspberry)
   - Secondary: `#F43F5E` (Light Raspberry)
   - Accent: `#BE123C` (Deep Raspberry)
   - Neutral: `#FFF1F2` (Pink Cream)

10. **Fire Engine**
    - Primary: `#DC2626` (Fire Red)
    - Secondary: `#F87171` (Light Fire)
    - Accent: `#991B1B` (Deep Fire)
    - Neutral: `#FEE2E2` (Pale Red)

---

#### **Purple Themes** (Luxury, Creativity, Imagination)

1. **Royal Purple**
   - Primary: `#9333EA` (Purple)
   - Secondary: `#A855F7` (Light Purple)
   - Accent: `#7C3AED` (Deep Purple)
   - Neutral: `#FAF5FF` (Pale Lavender)

2. **Lavender Dream**
   - Primary: `#A855F7` (Lavender)
   - Secondary: `#C084FC` (Light Lavender)
   - Accent: `#9333EA` (Deep Lavender)
   - Neutral: `#F5F3FF` (Pale Purple)

3. **Violet Twilight**
   - Primary: `#7C3AED` (Violet)
   - Secondary: `#A78BFA` (Light Violet)
   - Accent: `#6D28D9` (Deep Violet)
   - Neutral: `#EDE9FE` (Pale Violet)

4. **Plum Elegance**
   - Primary: `#9333EA` (Plum)
   - Secondary: `#C084FC` (Light Plum)
   - Accent: `#7C3AED` (Deep Plum)
   - Neutral: `#FAF5FF` (Cream)

5. **Orchid Garden**
   - Primary: `#C026D3` (Orchid)
   - Secondary: `#D946EF` (Light Orchid)
   - Accent: `#A21CAF` (Deep Orchid)
   - Neutral: `#FAE8FF` (Pale Orchid)

6. **Amethyst**
   - Primary: `#9333EA` (Amethyst)
   - Secondary: `#A855F7` (Light Amethyst)
   - Accent: `#7C3AED` (Deep Amethyst)
   - Neutral: `#F3E8FF` (Pale Purple)

7. **Grape Soda**
   - Primary: `#7C3AED` (Grape)
   - Secondary: `#A78BFA` (Light Grape)
   - Accent: `#6D28D9` (Deep Grape)
   - Neutral: `#EDE9FE` (Pale Grape)

8. **Mauve Magic**
   - Primary: `#C084FC` (Mauve)
   - Secondary: `#D8B4FE` (Light Mauve)
   - Accent: `#A855F7` (Deep Mauve)
   - Neutral: `#F5F3FF` (Cream)

9. **Lilac Breeze**
   - Primary: `#A78BFA` (Lilac)
   - Secondary: `#C4B5FD` (Light Lilac)
   - Accent: `#8B5CF6` (Deep Lilac)
   - Neutral: `#EDE9FE` (Pale Lilac)

10. **Indigo Night**
    - Primary: `#6366F1` (Indigo)
    - Secondary: `#818CF8` (Light Indigo)
    - Accent: `#4F46E5` (Deep Indigo)
    - Neutral: `#E0E7FF` (Pale Indigo)

---

#### **Teal/Cyan Themes** (Modern, Fresh, Tech)

1. **Tropical Waters**
   - Primary: `#14B8A6` (Teal)
   - Secondary: `#2DD4BF` (Turquoise)
   - Accent: `#0D9488` (Deep Teal)
   - Neutral: `#F0FDFA` (Pale Teal)

2. **Mint Teal**
   - Primary: `#06B6D4` (Cyan)
   - Secondary: `#22D3EE` (Light Cyan)
   - Accent: `#0891B2` (Deep Cyan)
   - Neutral: `#ECFEFF` (Pale Cyan)

3. **Ocean Depth**
   - Primary: `#0891B2` (Ocean Teal)
   - Secondary: `#06B6D4` (Sky Cyan)
   - Accent: `#0E7490` (Deep Ocean)
   - Neutral: `#E0F2FE` (Pale Ocean)

4. **Seafoam Green**
   - Primary: `#14B8A6` (Seafoam)
   - Secondary: `#5EEAD4` (Light Seafoam)
   - Accent: `#0F766E` (Deep Seafoam)
   - Neutral: `#CCFBF1` (Pale Seafoam)

5. **Turquoise Bay**
   - Primary: `#06B6D4` (Turquoise)
   - Secondary: `#67E8F9` (Light Turquoise)
   - Accent: `#0891B2` (Deep Turquoise)
   - Neutral: `#CFFAFE` (Pale Turquoise)

6. **Aqua Fresh**
   - Primary: `#0EA5E9` (Aqua)
   - Secondary: `#38BDF8` (Light Aqua)
   - Accent: `#0284C7` (Deep Aqua)
   - Neutral: `#E0F2FE` (Pale Aqua)

7. **Caribbean Sea**
   - Primary: `#14B8A6` (Caribbean)
   - Secondary: `#2DD4BF` (Light Caribbean)
   - Accent: `#0D9488` (Deep Caribbean)
   - Neutral: `#F0FDFA` (Pale Blue-Green)

8. **Peacock**
   - Primary: `#0891B2` (Peacock Blue)
   - Secondary: `#06B6D4` (Light Peacock)
   - Accent: `#0E7490` (Deep Peacock)
   - Neutral: `#ECFEFF` (Pale Peacock)

9. **Jade Stone**
   - Primary: `#059669` (Jade)
   - Secondary: `#10B981` (Light Jade)
   - Accent: `#047857` (Deep Jade)
   - Neutral: `#D1FAE5` (Pale Jade)

10. **Cerulean Sky**
    - Primary: `#0EA5E9` (Cerulean)
    - Secondary: `#38BDF8` (Light Cerulean)
    - Accent: `#0284C7` (Deep Cerulean)
    - Neutral: `#F0F9FF` (Pale Cerulean)

---

#### **Earth/Neutral Themes** (Natural, Organic, Grounded)

1. **Warm Sand**
   - Primary: `#D97706` (Sand Brown)
   - Secondary: `#F59E0B` (Light Sand)
   - Accent: `#B45309` (Deep Brown)
   - Neutral: `#FEF3C7` (Cream)

2. **Desert Dune**
   - Primary: `#B45309` (Desert)
   - Secondary: `#D97706` (Light Desert)
   - Accent: `#92400E` (Deep Desert)
   - Neutral: `#FEF3C7` (Sand Cream)

3. **Clay & Stone**
   - Primary: `#78716C` (Clay)
   - Secondary: `#A8A29E` (Light Clay)
   - Accent: `#57534E` (Dark Clay)
   - Neutral: `#F5F5F4` (Stone White)

4. **Coffee Bean**
   - Primary: `#78350F` (Coffee)
   - Secondary: `#92400E` (Light Coffee)
   - Accent: `#451A03` (Dark Coffee)
   - Neutral: `#FEF3C7` (Cream)

5. **Terracotta Earth**
   - Primary: `#C2410C` (Terracotta)
   - Secondary: `#EA580C` (Light Terracotta)
   - Accent: `#9A3412` (Deep Terracotta)
   - Neutral: `#FFF7ED` (Clay Cream)

6. **Warm Gray**
   - Primary: `#78716C` (Warm Gray)
   - Secondary: `#A8A29E` (Light Gray)
   - Accent: `#44403C` (Dark Gray)
   - Neutral: `#FAFAF9` (Off White)

7. **Caramel Latte**
   - Primary: `#D97706` (Caramel)
   - Secondary: `#FBBF24` (Light Caramel)
   - Accent: `#B45309` (Deep Caramel)
   - Neutral: `#FFFBEB` (Cream)

8. **Chocolate Truffle**
   - Primary: `#78350F` (Chocolate)
   - Secondary: `#92400E` (Milk Chocolate)
   - Accent: `#451A03` (Dark Chocolate)
   - Neutral: `#FAFAF9` (Vanilla)

9. **Natural Linen**
   - Primary: `#A8A29E` (Linen)
   - Secondary: `#D6D3D1` (Light Linen)
   - Accent: `#78716C` (Dark Linen)
   - Neutral: `#FAFAF9` (Off White)

10. **Earthy Moss**
    - Primary: `#65A30D` (Moss)
    - Secondary: `#84CC16` (Light Moss)
    - Accent: `#4D7C0F` (Deep Moss)
    - Neutral: `#F7FEE7` (Pale Moss)

---

#### **Sky/Nature Themes** (Serene, Peaceful, Natural)

1. **Sunrise Horizon**
   - Primary: `#F59E0B` (Golden)
   - Secondary: `#FCD34D` (Light Gold)
   - Accent: `#F97316` (Orange)
   - Neutral: `#FFFBEB` (Pale Yellow)

2. **Clear Sky**
   - Primary: `#0EA5E9` (Sky Blue)
   - Secondary: `#7DD3FC` (Light Sky)
   - Accent: `#0284C7` (Deep Sky)
   - Neutral: `#F0F9FF` (Cloud White)

3. **Mountain Meadow**
   - Primary: `#10B981` (Meadow Green)
   - Secondary: `#6EE7B7` (Light Meadow)
   - Accent: `#0EA5E9` (Sky Blue)
   - Neutral: `#ECFDF5` (Pale Green)

4. **Sunset Beach**
   - Primary: `#F59E0B` (Sunset)
   - Secondary: `#FCD34D` (Light Sunset)
   - Accent: `#0EA5E9` (Ocean)
   - Neutral: `#FFFBEB` (Sand)

5. **Arctic Glacier**
   - Primary: `#06B6D4` (Ice Blue)
   - Secondary: `#A5F3FC` (Light Ice)
   - Accent: `#0891B2` (Deep Ice)
   - Neutral: `#F0FDFA` (Snow White)

6. **Rainforest**
   - Primary: `#059669` (Forest)
   - Secondary: `#10B981` (Foliage)
   - Accent: `#0284C7` (Sky Peek)
   - Neutral: `#ECFDF5` (Mist)

7. **Desert Oasis**
   - Primary: `#0891B2` (Oasis Blue)
   - Secondary: `#14B8A6` (Palm Green)
   - Accent: `#F59E0B` (Desert Sand)
   - Neutral: `#FEF3C7` (Cream)

8. **Coastal Breeze**
   - Primary: `#0EA5E9` (Ocean)
   - Secondary: `#14B8A6` (Teal)
   - Accent: `#F59E0B` (Sunset)
   - Neutral: `#F0F9FF` (Sky)

9. **Alpine Snow**
   - Primary: `#06B6D4` (Alpine Blue)
   - Secondary: `#22D3EE` (Ice Blue)
   - Accent: `#64748B` (Mountain Gray)
   - Neutral: `#F8FAFC` (Snow)

10. **Cherry Blossom Spring**
    - Primary: `#F43F5E` (Cherry Blossom)
    - Secondary: `#FB7185` (Light Blossom)
    - Accent: `#10B981` (Spring Green)
    - Neutral: `#FFF1F2` (Petal Pink)

---

### Theme Color UI/UX

#### Color Picker Interface

**Visual Layout:**
```
┌────────────────────────────────────┐
│  Theme Colors                      │
├────────────────────────────────────┤
│  Category: [Blue ▼]                │
│                                    │
│  ┌──────────────────────────────┐ │
│  │ Ocean Breeze           ✓     │ │ ← Selected
│  │ ████ ████ ████ ████          │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ Corporate Navy               │ │
│  │ ████ ████ ████ ████          │ │
│  └──────────────────────────────┘ │
│  ┌──────────────────────────────┐ │
│  │ Tech Modern                  │ │
│  │ ████ ████ ████ ████          │ │
│  └──────────────────────────────┘ │
│                                    │
│  [Show More...]                    │
├────────────────────────────────────┤
│  Customize Selected Theme          │
│                                    │
│  Primary    ████ [#4A90E2] [🎨]   │
│  Secondary  ████ [#7BA3CC] [🎨]   │
│  Accent     ████ [#2E5C8A] [🎨]   │
│  Neutral    ████ [#F0F4F8] [🎨]   │
│                                    │
│  [Apply Theme]  [Reset to Default] │
└────────────────────────────────────┘
```

#### Features:
1. **Category Dropdown** - Filter by theme category (Blue, Orange, Green, etc.)
2. **Visual Palette Cards** - Show 4-color swatches with theme name
3. **Selected Indicator** - Checkmark on active theme
4. **Expand/Collapse** - "Show More" to see all 10 options per category
5. **Color Customization** - Click color picker icon to modify individual colors
6. **Live Preview** - Changes immediately reflect in canvas (with undo/redo support)
7. **Apply/Reset Buttons** - Confirm changes or revert to last saved state

---

### 2. SEO & Meta Settings

**Purpose:** Configure page-level SEO metadata that affects search engine rankings and social sharing.

#### Fields:

**Page Title**
- Label: "Page Title (SEO)"
- Description: "Title shown in browser tabs and search results (50-60 characters)"
- Type: Text input
- Character counter: Shows `45/60` (green when optimal, yellow when getting close, red when too long)
- Example: `"Swift Sites - Build Websites Fast | No Code Website Builder"`

**Meta Description**
- Label: "Meta Description"
- Description: "Brief summary shown in search results (150-160 characters)"
- Type: Textarea (3 rows)
- Character counter: Shows `148/160`
- Example: `"Create beautiful, responsive websites without code. Swift Sites offers drag-and-drop components, themes, and instant export."`

**Meta Keywords** (Optional - Less important in 2025 SEO)
- Label: "Meta Keywords"
- Description: "Comma-separated keywords (optional, less important than title/description)"
- Type: Text input
- Example: `"website builder, no code, landing page, responsive design"`

**Favicon**
- Label: "Favicon URL"
- Description: "Icon shown in browser tabs and bookmarks (.ico, .png, 16x16 or 32x32px)"
- Type: URL input with preview
- Example: `"https://example.com/favicon.ico"`
- Preview: Shows tiny icon next to input

**Open Graph Tags** (Social Sharing)
- **OG Title** - Title when shared on Facebook/LinkedIn (defaults to Page Title)
- **OG Description** - Description for social cards (defaults to Meta Description)
- **OG Image** - Image shown in social shares (recommended 1200x630px)
- **OG Type** - Type of content (website, article, product)

**Twitter Card Tags**
- **Twitter Card Type** - Summary, Summary Large Image, App, Player
- **Twitter Site** - Your Twitter handle (e.g., `@swiftsites`)
- **Twitter Creator** - Author's Twitter handle

**Robots Meta Tag**
- Label: "Search Engine Indexing"
- Type: Dropdown
- Options:
  - `index, follow` (Allow search engines to index and crawl links)
  - `noindex, follow` (Don't index, but crawl links)
  - `index, nofollow` (Index page, but don't follow links)
  - `noindex, nofollow` (Don't index or follow links)
- Default: `index, follow`

**Canonical URL**
- Label: "Canonical URL"
- Description: "The preferred URL for this page (prevents duplicate content issues)"
- Type: URL input
- Example: `"https://example.com/about"`

---

### 3. Typography Settings

**Purpose:** Define global font styles that cascade throughout the website.

#### Global Font Family

**Heading Font**
- Label: "Heading Font"
- Type: Dropdown with preview
- Options:
  - **System Fonts** (Fast, no loading):
    - `Inter` (Modern, clean)
    - `Roboto` (Neutral, readable)
    - `Segoe UI` (Windows native)
    - `-apple-system` (Apple native)
    - `Arial` (Universal fallback)
  - **Google Fonts** (Popular, professional):
    - `Poppins` (Modern, geometric)
    - `Montserrat` (Elegant, versatile)
    - `Playfair Display` (Elegant, serif)
    - `Merriweather` (Readable, serif)
    - `Raleway` (Clean, sans-serif)
    - `Lora` (Friendly, serif)
- Default: `Inter`

**Body Font**
- Label: "Body Font"
- Type: Dropdown with preview
- Options: Same as Heading Font
- Default: `Inter`

**Font Size Scale**
- Label: "Base Font Size"
- Type: Range slider (12px - 20px)
- Default: `16px`
- Note: "All component font sizes scale from this base value"

---

### 4. Layout & Spacing

**Purpose:** Control global spacing, container widths, and layout behavior.

#### Container Width

**Max Container Width**
- Label: "Max Content Width"
- Type: Dropdown + Custom input
- Options:
  - `640px` (Small - blog posts, articles)
  - `768px` (Medium - mobile-first)
  - `1024px` (Large - standard websites)
  - `1280px` (Extra Large - wide layouts)
  - `1536px` (2XL - full width)
  - `100%` (Full width, no limit)
  - `Custom` (Enter custom value)
- Default: `1280px`

**Spacing Scale**
- Label: "Global Spacing Multiplier"
- Type: Range slider (0.5x - 2x)
- Default: `1x`
- Description: "Multiplier for all component spacing (padding, margins, gaps)"

---

### 5. Accessibility Settings

**Purpose:** Ensure website meets accessibility standards (WCAG compliance).

#### Options:

**High Contrast Mode**
- Label: "Enable High Contrast Mode"
- Type: Toggle switch
- Default: `Off`
- Description: "Increases color contrast for better readability (WCAG AAA)"

**Focus Indicators**
- Label: "Show Focus Outlines"
- Type: Toggle switch
- Default: `On`
- Description: "Visible outlines when navigating with keyboard (recommended)"

**Reduced Motion**
- Label: "Respect Reduced Motion Preference"
- Type: Toggle switch
- Default: `On`
- Description: "Disables animations for users with motion sensitivity"

**Alt Text Warnings**
- Label: "Warn for Missing Alt Text"
- Type: Toggle switch
- Default: `On`
- Description: "Show warnings when images don't have alt text"

---

### 6. Export Settings

**Purpose:** Configure how the website is exported.

#### Options:

**Export Format**
- Label: "Export Format"
- Type: Dropdown
- Options:
  - `Single HTML File` (All-in-one, easy sharing)
  - `HTML + Separate CSS` (Organized, cacheable)
  - `HTML + CSS + JS` (Full separation of concerns)
- Default: `Single HTML File`

**Minify Output**
- Label: "Minify HTML/CSS/JS"
- Type: Toggle switch
- Default: `Off`
- Description: "Remove whitespace and comments for smaller file size"

**Include Comments**
- Label: "Include HTML Comments"
- Type: Toggle switch
- Default: `On`
- Description: "Add comments in exported code for easier editing"

---

## Implementation Plan

### Phase 1: UI Structure (Week 1)

**1.1 Add Page Navigation Item**
- File: `index.html`
- Add fourth `.sidebar-nav-item` button with icon and "Page" label
- Use `#icon-settings` or `#icon-globe` for icon

**1.2 Create Page Panel HTML**
- File: `index.html`
- Add `<div id="pagePanel" class="sidebar-panel">` after `propertiesPanel`
- Structure with collapsible sections using `<details>` elements:
  ```html
  <div id="pagePanel" class="sidebar-panel">
      <h3>Page Settings</h3>

      <details open>
          <summary>Theme Colors</summary>
          <div class="setting-group">
              <!-- Theme color selector -->
          </div>
      </details>

      <details>
          <summary>SEO & Meta</summary>
          <div class="setting-group">
              <!-- SEO fields -->
          </div>
      </details>

      <details>
          <summary>Typography</summary>
          <div class="setting-group">
              <!-- Font settings -->
          </div>
      </details>

      <!-- More sections... -->
  </div>
  ```

**1.3 Update DOM References**
- File: `js/core/app.js`
- Add `pageNavBtn` and `pagePanel` to `getDomReferences()`

---

### Phase 2: Theme Color System (Week 2)

**2.1 Create Theme Data File**
- File: `theme_palettes.yaml` (new)
- Structure:
```yaml
blue:
  - name: "Ocean Breeze"
    primary: "#4A90E2"
    secondary: "#7BA3CC"
    accent: "#2E5C8A"
    neutral: "#F0F4F8"
  - name: "Corporate Navy"
    primary: "#1E3A8A"
    # ... etc

orange:
  - name: "Sunset Glow"
    # ... etc
```

**2.2 Theme Selector Component**
- File: `js/page/themePicker.js` (new)
- Functions:
  - `loadThemes()` - Load theme data from YAML
  - `renderThemeCategories()` - Render category dropdown
  - `renderThemePalettes(category)` - Render palette cards for category
  - `selectTheme(themeName)` - Apply selected theme
  - `customizeThemeColor(colorKey, hexValue)` - Modify individual color

**2.3 Apply Theme to Components**
- File: `js/render/index.js`
- Update `generateRemainingStyles()` to use theme colors:
  - Replace component color tokens with theme color variables
  - Add CSS custom properties: `--color-primary`, `--color-secondary`, `--color-accent`, `--color-neutral`
  - Components reference these variables instead of hardcoded colors

**2.4 Theme Preview**
- Real-time preview in canvas when hovering over theme
- Undo/redo support for theme changes
- "Apply" button to confirm, "Reset" to revert

---

### Phase 3: SEO & Meta Settings (Week 3)

**3.1 Page Meta State**
- File: `js/core/state.js`
- Add `pageSettings` to state:
```javascript
const pageSettings = {
    meta: {
        title: '',
        description: '',
        keywords: '',
        favicon: '',
        robots: 'index, follow',
        canonical: '',
        ogTitle: '',
        ogDescription: '',
        ogImage: '',
        ogType: 'website',
        twitterCard: 'summary',
        twitterSite: '',
        twitterCreator: '',
    },
    theme: {
        category: 'blue',
        selectedTheme: 'Ocean Breeze',
        customColors: null,
    },
    typography: {
        headingFont: 'Inter',
        bodyFont: 'Inter',
        baseFontSize: 16,
    },
    // ... etc
};
```

**3.2 Meta Form Component**
- File: `js/page/metaSettings.js` (new)
- Render form fields for all meta settings
- Character counters for title/description
- Validation for optimal lengths
- Live preview of meta tags

**3.3 Update Export with Meta Tags**
- File: `js/ui/actions.js` - Update `exportCode()`
- Generate full HTML document with meta tags:
```javascript
const documentHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${pageSettings.meta.title || 'Generated Website'}</title>
    <meta name="description" content="${pageSettings.meta.description}">
    <meta name="keywords" content="${pageSettings.meta.keywords}">
    <meta name="robots" content="${pageSettings.meta.robots}">
    ${pageSettings.meta.canonical ? `<link rel="canonical" href="${pageSettings.meta.canonical}">` : ''}
    <link rel="icon" href="${pageSettings.meta.favicon}">

    <!-- Open Graph -->
    <meta property="og:title" content="${pageSettings.meta.ogTitle || pageSettings.meta.title}">
    <meta property="og:description" content="${pageSettings.meta.ogDescription || pageSettings.meta.description}">
    <meta property="og:image" content="${pageSettings.meta.ogImage}">
    <meta property="og:type" content="${pageSettings.meta.ogType}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="${pageSettings.meta.twitterCard}">
    <meta name="twitter:site" content="${pageSettings.meta.twitterSite}">
    <meta name="twitter:creator" content="${pageSettings.meta.twitterCreator}">

    <style>
        /* Theme colors as CSS variables */
        :root {
            --color-primary: ${themeColors.primary};
            --color-secondary: ${themeColors.secondary};
            --color-accent: ${themeColors.accent};
            --color-neutral: ${themeColors.neutral};
        }
        /* ... rest of styles */
    </style>
</head>
<body>
    ${html}
</body>
</html>`;
```

---

### Phase 4: Typography & Layout Settings (Week 4)

**4.1 Typography Controls**
- File: `js/page/typography.js` (new)
- Font dropdown with preview
- Base font size slider
- Apply to page-level styles

**4.2 Layout Controls**
- Max container width selector
- Spacing scale multiplier
- Apply globally via CSS variables

---

### Phase 5: Testing & Polish (Week 5)

**5.1 Unit Tests**
- File: `js/page/__tests__/themePicker.test.js`
- Test theme selection
- Test color customization
- Test theme application

**5.2 Integration Tests**
- Test page panel switching
- Test settings persistence
- Test export with settings

**5.3 Manual QA**
- Test all theme categories (10 palettes × 8 categories = 80 themes)
- Test SEO meta tag generation
- Test typography settings
- Test export formats

---

## Data Model

### Page Settings Schema

```yaml
# component_schemas.yaml extension
page:
  groups:
    - name: "theme"
      label: "Theme Colors"
      fields:
        - name: "category"
          label: "Category"
          type: "select"
          options:
            - value: "blue"
              label: "Blue"
            - value: "orange"
              label: "Orange"
            - value: "green"
              label: "Green"
            - value: "red"
              label: "Red"
            - value: "purple"
              label: "Purple"
            - value: "teal"
              label: "Teal/Cyan"
            - value: "earth"
              label: "Earth/Neutral"
            - value: "sky"
              label: "Sky/Nature"

        - name: "selectedTheme"
          label: "Theme"
          type: "theme-picker"

        - name: "customPrimary"
          label: "Primary Color"
          type: "color"

        - name: "customSecondary"
          label: "Secondary Color"
          type: "color"

        - name: "customAccent"
          label: "Accent Color"
          type: "color"

        - name: "customNeutral"
          label: "Neutral Color"
          type: "color"

    - name: "seo"
      label: "SEO & Meta"
      fields:
        - name: "title"
          label: "Page Title"
          type: "text"
          maxLength: 60

        - name: "description"
          label: "Meta Description"
          type: "textarea"
          maxLength: 160

        - name: "keywords"
          label: "Meta Keywords"
          type: "text"

        - name: "favicon"
          label: "Favicon URL"
          type: "url"

        - name: "robots"
          label: "Search Engine Indexing"
          type: "select"
          options:
            - value: "index, follow"
              label: "Index & Follow Links"
            - value: "noindex, follow"
              label: "Don't Index, Follow Links"
            - value: "index, nofollow"
              label: "Index, Don't Follow Links"
            - value: "noindex, nofollow"
              label: "Don't Index, Don't Follow"
```

---

## UI/UX Considerations

### Visual Design

**Page Panel Appearance:**
- Same styling as Properties panel
- Collapsible sections with `<details>` elements
- Smooth animations on expand/collapse
- Clear section headers with icons
- Responsive layout (stacks on mobile)

**Theme Picker:**
- Large color swatches (20px × 20px each)
- Theme name clearly visible
- Hover state shows preview
- Selected state with checkmark
- "Show More" to reveal all 10 palettes per category

**Form Fields:**
- Consistent spacing (1.5rem between fields)
- Clear labels with descriptions
- Character counters for text inputs
- Inline validation (green checkmark when valid, red warning when invalid)
- Help tooltips with info icon

---

## Accessibility

**Keyboard Navigation:**
- All settings accessible via keyboard
- Tab order: Category dropdown → Theme cards → Color pickers → Apply button
- Arrow keys navigate between theme cards
- Enter/Space to select theme

**Screen Readers:**
- Clear ARIA labels on all controls
- `aria-live="polite"` on character counters
- Announce theme selection: "Ocean Breeze theme selected"
- Announce color changes: "Primary color changed to #4A90E2"

**Color Contrast:**
- All text meets WCAG AA standards (4.5:1 for normal text, 3:1 for large)
- Focus indicators clearly visible
- High contrast mode available

---

## Performance Considerations

**Theme Loading:**
- Lazy load theme data (only fetch when Page panel opened)
- Cache theme palettes in memory
- Debounce color picker changes (wait 300ms before applying)

**State Updates:**
- Batch theme color updates (apply all 4 colors at once)
- Use requestAnimationFrame for preview updates
- Throttle real-time preview (max 30fps)

**Export:**
- Minify CSS/JS only when user enables it (avoid blocking UI)
- Generate meta tags on-demand during export
- Stream large exports to avoid memory issues

---

## Shelved Features (For Later Implementation)

The following features are **explicitly shelved** to focus on core functionality first. They will be implemented in a future phase:

### Advanced Settings (Phase 6 - Future)

**Custom CSS Editor**
- Global custom CSS with syntax highlighting
- Code editor (CodeMirror or Monaco)
- Injected into exported HTML `<style>` tag
- Use case: Power users who want fine-grained control

**Custom JavaScript Editor**
- Global custom JavaScript with syntax highlighting
- Injected before closing `</body>` tag
- Use case: Custom interactions, animations, third-party integrations

**Analytics Integration**
- Google Analytics ID field (`G-XXXXXXXXXX`)
- Facebook Pixel ID field
- Custom tracking code textarea
- Auto-injection of tracking scripts in export
- Use case: Website owners who want to track visitor analytics

**Why Shelved:**
- Lower priority than theme colors and SEO
- Requires additional dependencies (code editor library)
- More complex UI (syntax highlighting, validation)
- Can be added later without breaking existing features
- Users can still add custom code manually to exported HTML

---

## Future Enhancements (Phase 7+)

Long-term feature ideas for continuous improvement:

1. **Custom Theme Creation** - Save user-created themes for reuse
2. **Theme Marketplace** - Import/export community themes
3. **Color Harmony Tools** - AI-suggested complementary colors
4. **A/B Testing** - Preview different themes side-by-side
5. **Dark Mode Toggle** - Auto-generate dark mode from light theme
6. **Gradient Support** - Linear/radial gradient backgrounds
7. **Animation Presets** - Page transition effects, scroll animations
8. **Responsive Breakpoints** - Configure custom mobile/tablet/desktop widths
9. **Multi-language Support** - Set page language, hreflang tags for SEO
10. **Performance Budgets** - Set max file size, image optimization warnings
11. **Version History** - Save/restore previous page settings
12. **Export Templates** - Pre-configured settings bundles (Blog, Portfolio, Business)

---

## Testing Strategy

### Unit Tests

**Theme Picker:**
- Test theme data loading
- Test category filtering
- Test theme selection
- Test color customization
- Test theme application to components

**Meta Settings:**
- Test meta tag generation
- Test character counting
- Test validation rules
- Test export with meta tags

**State Management:**
- Test page settings persistence
- Test undo/redo with page settings
- Test settings serialization/deserialization

### Integration Tests

**Page Panel:**
- Test panel switching (Components → Properties → Page)
- Test settings form submission
- Test live preview updates

**Export:**
- Test export with different theme colors
- Test export with all meta tags
- Test export formats (single file vs. separate files)

### Manual QA Checklist

- [ ] All 80 theme palettes load correctly (10 per category × 8 categories)
- [ ] Selecting a theme applies colors to all components
- [ ] Customizing individual colors updates preview instantly
- [ ] Theme changes support undo/redo
- [ ] Character counters work for title/description
- [ ] Meta tags appear correctly in exported HTML
- [ ] Font dropdowns render correctly
- [ ] All sections expand/collapse smoothly
- [ ] Keyboard navigation works throughout
- [ ] Screen reader announces changes correctly
- [ ] Mobile responsive layout works

---

## Success Metrics

**User Experience:**
- Time to apply a theme: < 5 seconds
- Theme selection satisfaction: > 90% (user survey)
- Settings panel discovery rate: > 70% of users find page panel

**Technical:**
- Page panel load time: < 200ms
- Theme application time: < 500ms
- Export with settings: < 2 seconds (average site)

**Adoption:**
- % of users who customize themes: Target 60%
- % of exports with SEO meta tags: Target 80%
- % of users using typography settings: Target 40%

---

## Open Questions for Stakeholder Review

1. **Theme Naming:** Should we keep descriptive names (Ocean Breeze) or simple names (Blue 1, Blue 2)?
2. **Color Customization:** Should customized themes be saveable for reuse?
3. **Default Theme:** Which theme should be the default on app load? (Suggest: Ocean Breeze or Clear Sky)
4. **SEO Priority:** Which meta tags are essential vs. optional for first release?
5. **Font Loading:** Should we support Google Fonts API or stick to system fonts for performance?
6. **Analytics:** Should we track which themes are most popular to inform future palette additions?
7. **Export Defaults:** Should "Minify Output" default to On for production-ready exports?

---

## Conclusion

This plan provides a comprehensive Page Settings panel that empowers users to:
1. **Quickly apply professional themes** (80 curated palettes across 8 categories)
2. **Customize colors** to match their brand
3. **Optimize for SEO** with meta tags and Open Graph
4. **Configure typography** with font families and sizing
5. **Control layout** with spacing and container width
6. **Export production-ready** HTML with all settings baked in

The implementation is phased to deliver value incrementally:
- **Week 1-2:** Theme colors (highest user value)
- **Week 3:** SEO settings (essential for launch)
- **Week 4:** Typography & layout settings
- **Week 5:** Testing & polish

**Note:** Advanced settings (Custom CSS/JS, Analytics) are **shelved for future implementation** to focus on core features first.

**Next Steps:**
1. Review plan with team
2. Approve theme palette selection
3. Begin Phase 1 implementation (UI structure)
4. Create `theme_palettes.yaml` data file
5. Implement theme picker component
