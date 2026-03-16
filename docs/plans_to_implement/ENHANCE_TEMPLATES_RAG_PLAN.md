# Enhance Example Templates for RAG Retrievability

## Context

The RAG system chunks YAML templates at `- name:` component boundaries and extracts metadata from file header comments. Currently, most templates have minimal or no headers, making them poorly retrievable. When a user queries "create a bakery hero" or "restaurant pricing section", the system struggles to find the right template because:

1. Root-level full-page templates (bakery, restaurant, etc.) have **zero** header comments
2. Most category templates have only 2-3 line headers — missing "Perfect for:", "Visual style:", component lists
3. No templates describe which base components they use to build sections
4. Headers don't contain enough keywords to trigger the metadata extractor's industry, section_type, layout_pattern, and visual_style regex patterns

## How the RAG Chunker Consumes Headers

`ssr_python/rag/indexing/chunker.py` lines 78-130 — `_extract_file_comments()`:

```
Line 1           → title          (always first comment line)
"Perfect for:"   → use_cases      (checked FIRST for industry classification)
"Visual style:"  → visual_style   (fed to visual_style metadata)
First other line → description    (only ONE description line captured)
All other lines  → raw_lines      (in chunk content, helps BM25 + metadata regex)
```

`ssr_python/rag/indexing/metadata.py` — `extract_metadata()` scans full chunk content for:
- `component_types`: substring match ("button", "layout-row", etc.)
- `section_type`: regex ("hero|banner|splash", "pricing|plan|tier", etc.)
- `industry`: regex checked against use_cases FIRST then content
- `layout_pattern`: regex ("split|50.50|two.column", "full.screen|immersive", etc.)
- `visual_style`: regex ("glassmorphism", "dark.mode", "modern.minimal", etc.)

## Standard Header Format

Every template file should have this header before the YAML:

```yaml
# [Descriptive Title with Section Type Keywords]
# [Rich description: what this creates, layout structure, visual approach, what makes it unique]
# Base components: layout-row, layout-column, image, heading, paragraph, button
# Section type: hero
# Layout: split_screen
# Visual style: modern
# Perfect for: SaaS platforms, tech startups, software companies, B2B products
```

## Keyword Alignment Cheat Sheet

### Section Type Keywords (use in Title or Description)
| Target | Keywords that trigger match |
|--------|---------------------------|
| hero | hero, banner, splash, above fold, immersive |
| pricing | pricing, plan, tier |
| testimonial | testimonial, review, quote, social proof, praise |
| footer | footer, bottom, copyright |
| features | feature, benefit, highlight |
| cta | call to action, CTA, sign up, conversion |
| faq | faq, question, Q&A |
| contact | contact, get in touch, reach us |
| navigation | nav, menu, header, titlebar, mega menu, breadcrumb, sticky |
| product | product, catalog, shop, item, retail, bundle |
| team | team, staff, member, meet the |
| stats | stat, number, counter, metric, achievement |
| gallery | gallery, portfolio, showcase, masonry, hover overlay |
| blog | blog, article, post, story, editorial, listicle, podcast, newsletter |
| dashboard | dashboard, data card, stat snapshot, trend, activity feed |
| countdown | countdown, timer, flash sale, launch, event registration |
| ticker | ticker, scrolling, marquee, logo strip |

### Industry Keywords (use in "Perfect for:" line)
| Target | Keywords that trigger match |
|--------|---------------------------|
| saas | SaaS, software, app, platform, dashboard, fintech, B2B, startup, tech |
| restaurant | restaurant, food, menu, dining, bakery, cafe, coffee, pizza, gourmet |
| ecommerce | shop, store, product, cart, ecommerce, retail, flash sale |
| portfolio | portfolio, agency, freelance, creative, design, photography |
| health | health, medical, clinic, wellness, fitness, gym |
| education | education, school, course, learning, training |
| realestate | real estate, property, housing, apartment, interior design |
| logistics | logistics, shipping, delivery, transport |
| hospitality | hospitality, hotel, travel, tourism, resort, luxury brand |
| automotive | auto, car, vehicle, dealer, motor |
| entertainment | entertainment, gaming, music, event, conference, festival |
| legal | legal, law, attorney, consulting |

### Layout Keywords
| Target | Keywords that trigger match |
|--------|---------------------------|
| split_screen | split, 50/50, two column, side by side |
| fullscreen | full screen, full width, immersive |
| grid | grid, masonry, columnsgrid, card grid |
| centered | centered, center aligned, minimal |
| overlay | overlay, hover, tint, glass, blur |
| carousel_slider | carousel, slider, slideshow, swipe |

### Visual Style Keywords
| Target | Keywords that trigger match |
|--------|---------------------------|
| modern | modern, modern minimal |
| glassmorphism | glassmorphism, frosted, translucent |
| dark_mode | dark mode, dark theme, monochrome, noir |
| minimal | minimal, minimalist, clean design |
| retro | retro, vintage, nostalgic |
| neubrutalism | neubrutalism, brutalist, thick border |
| claymorphism | claymorphism, playful 3D, pastel rounded |
| aurora | aurora, liquid gradient, flowing gradient |
| monochrome | monochrome, dark sleek, neon on dark |
