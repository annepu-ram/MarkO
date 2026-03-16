## Enhance Templates: Image-as-Container + Carousel Integration
### Context
### Two underused features need showcasing in example templates:

Image as container — the image component supports components: for overlay content (text, buttons over background images). Only 3 hero templates use it (01, 06, 16). Many more hero and non-hero sections would benefit from this pattern.
Carousel component — only 5 templates use carousel (hero 11/22, testimonial 10, team 03, portfolio 04). Many section types naturally suit carousels (testimonials, products, portfolios, features).
Image Component Container Pattern

- name: image
  properties:
    source: { url: '...', altText: '...' }
    appearance: { minHeight: 30, fit: cover, overlay: { enabled: true, color: '#000', opacity: 50 } }
    layout: { widthMode: stretch }
  components:                    # Children render as overlay on top of image
    - name: layout-column
      components:
        - name: heading
          properties: { text: 'Title', typography: { color: '#fff' } }
        - name: button
          properties: { text: 'CTA' }

## Part A: Convert Hero Templates to Image-as-Container

Current state
Already use image-as-container: 01_fullscreen_immersive, 06_storytelling, 16_services_card
Already use carousel: 11_video_background, 22_story_starter
Typography-only (no bg image): 05_bold, 09_card, 21_centered, 26_navigation — skip
Use video-background: 18_immersive_motion, 23_search — skip (different component)
Use form/calendar focus: 19_lead_gen, 24_product_launch — skip

### Templates to convert (8 hero templates)
Template	Current Pattern	New Pattern
03_dark_mode	layout-column + image below content	Image-as-container with product screenshot as bg, content overlay
04_gradient_glassmorphism	layout-column + images below	Image-as-container hero bg with glassmorphic overlay cards
08_tiles_hero_magazine	layout-row with image columns	Main tile image uses image-as-container with headline overlay
10_asymmetric_creative	layout-row with image column	Feature image uses image-as-container with project info overlay
13_zen_wellness	split layout-row, image on right	Right-side image becomes image-as-container with floating badge
15_portfolio_creative	image grid with text below	Portfolio images use image-as-container with title overlay
17_standard_split	split layout-row, plain image right	Right-side image becomes image-as-container with subtle overlay text
25_social_proof	centered text, logo bar below	Add a hero background image-as-container wrapping the entire content

### Non-hero templates to add image-as-container
Category	Template	Use Case
features_benefits	02_alternating_image_text	Feature images with label/icon overlay
portfolio_showcase_cards	01_hover_overlay	Portfolio images with project title overlay
portfolio_showcase_cards	03_masonry_style	Masonry images with caption overlay
product_cards	04_limited_drop	Product image with "Limited" badge overlay
story_blog_cards	01_editorial_card	Blog featured image with category/title overlay
cta_banners	02_split_image_cta	CTA image side with text overlay

## Part B: Add Carousel to Templates
New carousel templates to create
Category	Template	Description
hero	08_tiles_hero_magazine	Convert static tile grid → auto-playing carousel of editorial stories
product_cards	01_retail_classic	Add product image carousel (3 slides showing different angles)
review_testimonial_cards	03_grid_wall	Convert static grid → testimonial carousel with slide transition
review_testimonial_cards	04_social_post	Social post carousel (Instagram-like swipe)
portfolio_showcase_cards	08_interactive_gallery	Convert tabbed gallery → project carousel
features_benefits	05_tabbed_feature_categories	Convert tabs → feature carousel with auto-advance
story_blog_cards	01_editorial_card	Convert static blog cards → blog carousel
Carousel configuration patterns to use
Testimonial carousel (fade, slow):

```yaml
behavior: { autoplay: true, delay: 6000, loop: true, pauseOnHover: true }
animation: { effect: fade, duration: 700 }
navigation: { showArrows: true, arrowStyle: chevron, showDots: true }
Product gallery (slide, manual):
```

``` yaml
behavior: { autoplay: false, loop: true, swipeEnabled: true }
animation: { effect: slide, duration: 300 }
navigation: { showArrows: true, arrowStyle: circle, showDots: true }
Hero slider (fade, cinematic):
```

``` yaml
behavior: { autoplay: true, delay: 5000, loop: true, pauseOnHover: true }
animation: { effect: fade, duration: 500 }
navigation: { showArrows: true, showDots: true }
```

### Files to Modify

#### Hero templates (image-as-container conversion)
example_templates/hero/03_dark_mode.yaml
example_templates/hero/04_gradient_glassmorphism.yaml
example_templates/hero/08_tiles_hero_magazine.yaml
example_templates/hero/10_asymmetric_creative.yaml
example_templates/hero/13_zen_wellness.yaml
example_templates/hero/15_portfolio_creative.yaml
example_templates/hero/17_standard_split.yaml
example_templates/hero/25_social_proof.yaml
#### Non-hero templates (image-as-container)
example_templates/features_benefits/02_alternating_image_text.yaml
example_templates/portfolio_showcase_cards/01_hover_overlay.yaml
example_templates/portfolio_showcase_cards/03_masonry_style.yaml
example_templates/product_cards/04_limited_drop.yaml
example_templates/story_blog_cards/01_editorial_card.yaml
example_templates/cta_banners/02_split_image_cta.yaml
#### Templates to add carousel
example_templates/product_cards/01_retail_classic.yaml
example_templates/review_testimonial_cards/03_grid_wall.yaml
example_templates/review_testimonial_cards/04_social_post.yaml
example_templates/portfolio_showcase_cards/08_interactive_gallery.yaml
example_templates/features_benefits/05_tabbed_feature_categories.yaml
example_templates/story_blog_cards/01_editorial_card.yaml
example_templates/hero/08_tiles_hero_magazine.yaml (carousel + image-as-container)

### Implementation Order
Hero templates — image-as-container conversions (8 files)
Non-hero templates — image-as-container additions (6 files)
Carousel integrations (7 files, some overlap with step 2)
Rebuild RAG index: cd ssr_python && python -m rag.scripts.build_index --force
### Verification
cd ssr_python && python app.py
Load each modified template in the preview — verify image overlay content renders correctly
Check carousel templates — slides navigate, autoplay works, dots/arrows functional
python -m pytest tests/ -v — all tests pass
Rebuild RAG index and verify chunk count increased