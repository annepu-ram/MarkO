# Media & Carousel Component Enhancements

## Implementation Document

This document details enhancements to the image, video, gif, and carousel components following Swift Sites SSR coding conventions.

---

## Current Architecture Summary

### Property Path Convention
```
Category → Subcategory → Property
```

| Category | Used For |
|----------|----------|
| `source` | URLs, alt text |
| `presentation` | Visual sizing (width, height, fit, aspectRatio) |
| `overlay` | Overlay settings |
| `effects` | **NEW** - Filters, shadows, hover effects |
| `caption` | **NEW** - Caption text and styling |
| `layout` | Width mode, alignment |
| `spacing` | Margins, padding |
| `appearance` | Background, border, radius |
| `behavior` | Interactive behavior |
| `playback` | Video controls |
| `navigation` | Carousel arrows/dots |
| `accessibility` | **NEW** - ARIA labels, pause button |

### Schema Field Convention
```yaml
- path: properties.category.subcategory.property
  type: select|text|number|checkbox|color|range
  label: "Display Label"
  tokens: tokenReferenceName  # from schema_tokens.yaml
```

### Token Naming Convention
- `tokens.yaml`: snake_case keys (`aspect_ratios`)
- `schema_tokens.yaml`: camelCase reference (`aspectRatios`)

---

## Phase 1: Image Component Enhancements

### 1.1 New Defaults (`component_defaults.yaml`)

```yaml
image:
  source:
    url: ''
    altText: 'Image'
  presentation:
    width: 100
    minHeight: 200
    fit: cover
    cornerStyle: none
    aspectRatio: auto           # NEW
    objectPosition: center      # NEW
  effects:                      # NEW section
    filter: none
    shadow: none
    hoverEffect: none
  caption:                      # NEW section
    text: ''
    position: below
    typography:
      size: sm
      color: '#666666'
      align: center
  loading:                      # NEW section
    lazy: true
  overlay:
    enabled: false
    color: 'rgba(0,0,0,0.5)'
    opacity: 50
  spacing:
    marginBlock: none
    marginInline: none
  layout:
    widthMode: stretch
```

### 1.2 New Schema Fields (`component_schemas.yaml`)

```yaml
image:
  groups:
    - id: source
      label: "Source"
      fields:
        - path: properties.source.url
          type: text
          label: "Image URL"
        - path: properties.source.altText
          type: text
          label: "Alt Text"

    - id: presentation
      label: "Presentation"
      fields:
        - path: properties.presentation.aspectRatio
          type: select
          label: "Aspect Ratio"
          tokens: aspectRatios
        - path: properties.presentation.objectPosition
          type: select
          label: "Focus Point"
          tokens: objectPositions
        - path: properties.presentation.fit
          type: select
          label: "Fit Mode"
          options:
            - { value: cover, label: Cover }
            - { value: contain, label: Contain }
            - { value: fill, label: Fill }
            - { value: none, label: None }
        - path: properties.presentation.cornerStyle
          type: select
          label: "Corner Style"
          tokens: borderRadiusScale
        - path: properties.presentation.minHeight
          type: number
          label: "Min Height (px)"
          min: 0
          max: 1000

    - id: effects
      label: "Effects"
      fields:
        - path: properties.effects.filter
          type: select
          label: "Filter"
          tokens: imageFilters
        - path: properties.effects.shadow
          type: select
          label: "Shadow"
          tokens: shadowScale
        - path: properties.effects.hoverEffect
          type: select
          label: "Hover Effect"
          tokens: hoverEffects

    - id: caption
      label: "Caption"
      fields:
        - path: properties.caption.text
          type: text
          label: "Caption Text"
        - path: properties.caption.position
          type: select
          label: "Position"
          options:
            - { value: above, label: Above }
            - { value: below, label: Below }
            - { value: overlay, label: Overlay }
          showWhen:
            field: properties.caption.text
            notEmpty: true
        - path: properties.caption.typography.size
          type: select
          label: "Caption Size"
          tokens: typographySizes
          showWhen:
            field: properties.caption.text
            notEmpty: true
        - path: properties.caption.typography.color
          type: color
          label: "Caption Color"
          showWhen:
            field: properties.caption.text
            notEmpty: true

    - id: loading
      label: "Loading"
      fields:
        - path: properties.loading.lazy
          type: checkbox
          label: "Lazy Load"

    # ... existing overlay, spacing, layout groups
```

### 1.3 New Tokens (`schema_tokens.yaml`)

```yaml
aspectRatios:
  - { value: 'auto', label: 'Auto' }
  - { value: '16/9', label: '16:9 Widescreen' }
  - { value: '4/3', label: '4:3 Standard' }
  - { value: '1/1', label: '1:1 Square' }
  - { value: '3/2', label: '3:2 Photo' }
  - { value: '21/9', label: '21:9 Ultrawide' }
  - { value: '9/16', label: '9:16 Portrait' }

objectPositions:
  - { value: 'center', label: 'Center' }
  - { value: 'top', label: 'Top' }
  - { value: 'bottom', label: 'Bottom' }
  - { value: 'left', label: 'Left' }
  - { value: 'right', label: 'Right' }
  - { value: 'top left', label: 'Top Left' }
  - { value: 'top right', label: 'Top Right' }
  - { value: 'bottom left', label: 'Bottom Left' }
  - { value: 'bottom right', label: 'Bottom Right' }

imageFilters:
  - { value: 'none', label: 'None' }
  - { value: 'grayscale', label: 'Grayscale' }
  - { value: 'sepia', label: 'Sepia' }
  - { value: 'blur', label: 'Blur' }
  - { value: 'brighten', label: 'Brighten' }
  - { value: 'darken', label: 'Darken' }
  - { value: 'saturate', label: 'High Saturation' }

shadowScale:
  - { value: 'none', label: 'None' }
  - { value: 'sm', label: 'Small' }
  - { value: 'md', label: 'Medium' }
  - { value: 'lg', label: 'Large' }
  - { value: 'xl', label: 'Extra Large' }

hoverEffects:
  - { value: 'none', label: 'None' }
  - { value: 'zoom', label: 'Zoom In' }
  - { value: 'brighten', label: 'Brighten' }
  - { value: 'darken', label: 'Darken' }
  - { value: 'lift', label: 'Lift (Shadow)' }
```

### 1.4 Tokens Values (`tokens.yaml`)

```yaml
# Add to existing tokens.yaml
aspect_ratios:
  auto: 'auto'
  '16/9': '16 / 9'
  '4/3': '4 / 3'
  '1/1': '1 / 1'
  '3/2': '3 / 2'
  '21/9': '21 / 9'
  '9/16': '9 / 16'

object_positions:
  center: 'center'
  top: 'top'
  bottom: 'bottom'
  left: 'left'
  right: 'right'
  'top left': 'top left'
  'top right': 'top right'
  'bottom left': 'bottom left'
  'bottom right': 'bottom right'

image_filters:
  none: 'none'
  grayscale: 'grayscale(100%)'
  sepia: 'sepia(100%)'
  blur: 'blur(4px)'
  brighten: 'brightness(1.2)'
  darken: 'brightness(0.8)'
  saturate: 'saturate(1.5)'

shadows:
  none: 'none'
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)'
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
```

### 1.5 Jinja2 Macro Update (`_components.html`)

```jinja2
{% macro render_image(component, tokens, path, component_id, parent_direction='row') %}
    {% set properties = component.properties | default({}) %}
    {% set source = properties.source | default({}) %}
    {% set presentation = properties.presentation | default({}) %}
    {% set effects = properties.effects | default({}) %}
    {% set caption_props = properties.caption | default({}) %}
    {% set loading = properties.loading | default({}) %}

    {# Build base styles #}
    {% set base_styles = build_styles(component, tokens, layout_direction=parent_direction) %}

    {# Aspect ratio #}
    {% set aspect_ratio = presentation.aspectRatio | default('auto') %}
    {% set aspect_style = '' %}
    {% if aspect_ratio != 'auto' %}
        {% set aspect_style = 'aspect-ratio: ' ~ aspect_ratio ~ ';' %}
    {% endif %}

    {# Object position #}
    {% set obj_position = presentation.objectPosition | default('center') %}
    {% set position_style = 'object-position: ' ~ obj_position ~ ';' %}

    {# Filter effect #}
    {% set filter_value = effects.filter | default('none') %}
    {% set filter_style = '' %}
    {% if filter_value != 'none' and tokens.image_filters and filter_value in tokens.image_filters %}
        {% set filter_style = 'filter: ' ~ tokens.image_filters[filter_value] ~ ';' %}
    {% endif %}

    {# Shadow #}
    {% set shadow_value = effects.shadow | default('none') %}
    {% set shadow_style = '' %}
    {% if shadow_value != 'none' and tokens.shadows and shadow_value in tokens.shadows %}
        {% set shadow_style = 'box-shadow: ' ~ tokens.shadows[shadow_value] ~ ';' %}
    {% endif %}

    {# Hover effect class #}
    {% set hover_class = '' %}
    {% set hover_effect = effects.hoverEffect | default('none') %}
    {% if hover_effect != 'none' %}
        {% set hover_class = 'image-hover-' ~ hover_effect %}
    {% endif %}

    {# Lazy loading #}
    {% set lazy_attr = 'lazy' if loading.lazy | default(true) else 'eager' %}

    {# Caption #}
    {% set caption_text = caption_props.text | default('') %}
    {% set caption_position = caption_props.position | default('below') %}

    <figure class="image-container chrome-target {{ hover_class }}"
            data-component-id="{{ component_id }}"
            style="{{ base_styles }} {{ shadow_style }} position: relative;">

        {# Caption above #}
        {% if caption_text and caption_position == 'above' %}
            {{ render_caption(caption_props, tokens) }}
        {% endif %}

        <div class="image-wrapper" style="{{ aspect_style }} overflow: hidden;">
            <img src="{{ source.url | default('') }}"
                 alt="{{ source.altText | default('Image') }}"
                 loading="{{ lazy_attr }}"
                 style="width: 100%; height: 100%; object-fit: {{ presentation.fit | default('cover') }}; {{ position_style }} {{ filter_style }}">
        </div>

        {# Caption below #}
        {% if caption_text and caption_position == 'below' %}
            {{ render_caption(caption_props, tokens) }}
        {% endif %}

        {# Caption overlay #}
        {% if caption_text and caption_position == 'overlay' %}
            <figcaption class="image-caption-overlay">
                {{ render_caption(caption_props, tokens) }}
            </figcaption>
        {% endif %}

        {# Existing overlay and nested content #}
        {% set overlay = properties.overlay | default({}) %}
        {% if overlay.enabled | default(false) %}
            <div class="image-overlay" style="..."></div>
        {% endif %}

        {% if component.components %}
            <div class="image-content">
                {% for child in component.components | default([]) %}
                    {% set child_path = path + ['components', loop.index0] %}
                    {{ render_component(child, tokens, child_path) }}
                {% endfor %}
            </div>
        {% endif %}
    </figure>
{% endmacro %}

{% macro render_caption(caption_props, tokens) %}
    {% set typo = caption_props.typography | default({}) %}
    {% set size = typo.size | default('sm') %}
    {% set color = typo.color | default('#666666') %}
    {% set align = typo.align | default('center') %}

    {% set size_value = tokens.typography_sizes[size] if tokens.typography_sizes and size in tokens.typography_sizes else '0.875rem' %}

    <figcaption class="image-caption"
                style="font-size: {{ size_value }}; color: {{ color }}; text-align: {{ align }}; padding: 0.5rem 0;">
        {{ caption_props.text }}
    </figcaption>
{% endmacro %}
```

### 1.6 CSS Additions (`components.css`)

```css
/* Image hover effects */
.image-hover-zoom img {
    transition: transform 0.3s ease;
}
.image-hover-zoom:hover img {
    transform: scale(1.05);
}

.image-hover-brighten img {
    transition: filter 0.3s ease;
}
.image-hover-brighten:hover img {
    filter: brightness(1.1);
}

.image-hover-darken img {
    transition: filter 0.3s ease;
}
.image-hover-darken:hover img {
    filter: brightness(0.9);
}

.image-hover-lift {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.image-hover-lift:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 20px -8px rgb(0 0 0 / 0.2);
}

/* Caption overlay positioning */
.image-caption-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.7));
    padding: 1rem;
}
.image-caption-overlay .image-caption {
    color: #ffffff;
}
```

---

## Phase 2: Video Component Enhancements

### 2.1 New Defaults (`component_defaults.yaml`)

```yaml
video:
  source:
    url: 'https://www.youtube.com/embed/dQw4w9WgXcQ'
  presentation:
    aspectRatio: '16/9'         # NEW
    height: 400
  playback:
    controls: true
    autoplay: false
    muted: false
    loop: false                 # NEW
  poster:                       # NEW section
    url: ''
  caption:                      # NEW section
    text: ''
    position: below
    typography:
      size: sm
      color: '#666666'
      align: center
  spacing:
    marginBlock: md
    marginInline: none
```

### 2.2 New Schema Fields (`component_schemas.yaml`)

```yaml
video:
  groups:
    - id: source
      label: "Source"
      fields:
        - path: properties.source.url
          type: text
          label: "Video URL"

    - id: presentation
      label: "Presentation"
      fields:
        - path: properties.presentation.aspectRatio
          type: select
          label: "Aspect Ratio"
          tokens: aspectRatios
        - path: properties.presentation.height
          type: number
          label: "Height (px)"
          min: 100
          max: 1000

    - id: playback
      label: "Playback"
      fields:
        - path: properties.playback.controls
          type: checkbox
          label: "Show Controls"
        - path: properties.playback.autoplay
          type: checkbox
          label: "Autoplay"
        - path: properties.playback.muted
          type: checkbox
          label: "Start Muted"
        - path: properties.playback.loop
          type: checkbox
          label: "Loop Video"

    - id: poster
      label: "Poster"
      fields:
        - path: properties.poster.url
          type: text
          label: "Poster Image URL"

    - id: caption
      label: "Caption"
      fields:
        - path: properties.caption.text
          type: text
          label: "Caption Text"
        - path: properties.caption.position
          type: select
          label: "Position"
          options:
            - { value: above, label: Above }
            - { value: below, label: Below }
```

### 2.3 Jinja2 Macro Update

```jinja2
{% macro render_video(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set source = properties.source | default({}) %}
    {% set presentation = properties.presentation | default({}) %}
    {% set playback = properties.playback | default({}) %}
    {% set poster = properties.poster | default({}) %}
    {% set caption_props = properties.caption | default({}) %}

    {% set video_styles = build_styles(component, tokens) %}

    {# Aspect ratio #}
    {% set aspect_ratio = presentation.aspectRatio | default('16/9') %}
    {% set aspect_style = 'aspect-ratio: ' ~ aspect_ratio ~ ';' %}

    {# Caption #}
    {% set caption_text = caption_props.text | default('') %}
    {% set caption_position = caption_props.position | default('below') %}

    <figure class="video-container chrome-target"
            data-component-id="{{ component_id }}"
            style="{{ video_styles }}">

        {# Caption above #}
        {% if caption_text and caption_position == 'above' %}
            {{ render_caption(caption_props, tokens) }}
        {% endif %}

        <div class="video-wrapper" style="{{ aspect_style }}">
            <iframe src="{{ source.url }}"
                    style="width: 100%; height: 100%; border: none;"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                    {% if playback.loop | default(false) %}loop{% endif %}>
            </iframe>
        </div>

        {# Caption below #}
        {% if caption_text and caption_position == 'below' %}
            {{ render_caption(caption_props, tokens) }}
        {% endif %}
    </figure>
{% endmacro %}
```

---

## Phase 3: GIF Component Enhancements

### 3.1 New Defaults (`component_defaults.yaml`)

```yaml
gif:
  source:
    url: 'https://media.giphy.com/media/example/giphy.gif'
    altText: 'Animated GIF'
  presentation:
    fit: cover
    cornerStyle: none
    aspectRatio: auto           # NEW
    objectPosition: center      # NEW
  effects:                      # NEW section
    filter: none
    shadow: none
  caption:                      # NEW section
    text: ''
    position: below
    typography:
      size: sm
      color: '#666666'
      align: center
  spacing:
    marginBlock: none
    marginInline: none
  layout:
    widthMode: stretch
```

### 3.2 Schema & Macro Updates

Follow same pattern as image component for:
- `presentation.aspectRatio`
- `presentation.objectPosition`
- `effects.filter`
- `effects.shadow`
- `caption.*`

---

## Phase 4: Carousel Component Enhancements

### 4.1 New Defaults (`component_defaults.yaml`)

```yaml
carousel:
  behavior:
    autoplay: true
    delay: 3000
    loop: true
    pauseOnHover: true          # NEW
  animation:                    # NEW section
    effect: slide
    duration: 300
  navigation:
    showArrows: true
    showDots: true
    arrowStyle: chevron         # NEW
    arrowPosition: inside       # NEW
  indicators:                   # NEW section
    style: dots
    position: bottom
  accessibility:                # NEW section
    showPauseButton: true
    ariaLabel: 'Image carousel'
  spacing:
    marginBlock: md
    marginInline: none
  slides: []
```

### 4.2 New Schema Fields (`component_schemas.yaml`)

```yaml
carousel:
  groups:
    - id: behavior
      label: "Behavior"
      fields:
        - path: properties.behavior.autoplay
          type: checkbox
          label: "Autoplay"
        - path: properties.behavior.delay
          type: number
          label: "Delay (ms)"
          min: 1000
          max: 10000
          showWhen:
            field: properties.behavior.autoplay
            value: true
        - path: properties.behavior.loop
          type: checkbox
          label: "Loop Slides"
        - path: properties.behavior.pauseOnHover
          type: checkbox
          label: "Pause on Hover"

    - id: animation
      label: "Animation"
      fields:
        - path: properties.animation.effect
          type: select
          label: "Transition Effect"
          options:
            - { value: slide, label: Slide }
            - { value: fade, label: Fade }
        - path: properties.animation.duration
          type: number
          label: "Duration (ms)"
          min: 100
          max: 1000

    - id: navigation
      label: "Navigation"
      fields:
        - path: properties.navigation.showArrows
          type: checkbox
          label: "Show Arrows"
        - path: properties.navigation.arrowStyle
          type: select
          label: "Arrow Style"
          options:
            - { value: chevron, label: Chevron (‹ ›) }
            - { value: arrow, label: Arrow (← →) }
            - { value: circle, label: Circle Buttons }
          showWhen:
            field: properties.navigation.showArrows
            value: true
        - path: properties.navigation.arrowPosition
          type: select
          label: "Arrow Position"
          options:
            - { value: inside, label: Inside }
            - { value: outside, label: Outside }
          showWhen:
            field: properties.navigation.showArrows
            value: true
        - path: properties.navigation.showDots
          type: checkbox
          label: "Show Indicators"

    - id: indicators
      label: "Indicators"
      fields:
        - path: properties.indicators.style
          type: select
          label: "Indicator Style"
          options:
            - { value: dots, label: Dots }
            - { value: numbers, label: Numbers }
            - { value: dashes, label: Dashes }
          showWhen:
            field: properties.navigation.showDots
            value: true
        - path: properties.indicators.position
          type: select
          label: "Position"
          options:
            - { value: bottom, label: Bottom }
            - { value: top, label: Top }
          showWhen:
            field: properties.navigation.showDots
            value: true

    - id: accessibility
      label: "Accessibility"
      fields:
        - path: properties.accessibility.showPauseButton
          type: checkbox
          label: "Show Pause Button (WCAG 2.2.2)"
        - path: properties.accessibility.ariaLabel
          type: text
          label: "ARIA Label"

    - id: slides
      label: "Slides"
      fields:
        - path: slides
          type: custom
          label: "Carousel Slides"
          renderer: carouselSlides
```

### 4.3 Jinja2 Macro Update

```jinja2
{% macro render_carousel(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set slides = component.slides | default([]) %}
    {% set behavior = properties.behavior | default({}) %}
    {% set animation = properties.animation | default({}) %}
    {% set navigation = properties.navigation | default({}) %}
    {% set indicators = properties.indicators | default({}) %}
    {% set a11y = properties.accessibility | default({}) %}

    {% set carousel_styles = build_styles(component, tokens) %}

    {# Animation class #}
    {% set anim_effect = animation.effect | default('slide') %}
    {% set anim_class = 'carousel-' ~ anim_effect %}

    {# Arrow style #}
    {% set arrow_style = navigation.arrowStyle | default('chevron') %}
    {% set prev_symbol = '‹' if arrow_style == 'chevron' else '←' %}
    {% set next_symbol = '›' if arrow_style == 'chevron' else '→' %}

    <div class="carousel chrome-target {{ anim_class }}"
         data-component-id="{{ component_id }}"
         data-component-type="carousel"
         data-autoplay="{{ 'true' if behavior.autoplay else 'false' }}"
         data-delay="{{ behavior.delay | default(3000) }}"
         data-loop="{{ 'true' if behavior.loop | default(true) else 'false' }}"
         data-pause-on-hover="{{ 'true' if behavior.pauseOnHover | default(true) else 'false' }}"
         data-animation-duration="{{ animation.duration | default(300) }}"
         aria-label="{{ a11y.ariaLabel | default('Image carousel') }}"
         aria-roledescription="carousel"
         style="{{ carousel_styles }}">

        {# Pause button for accessibility (WCAG 2.2.2) #}
        {% if a11y.showPauseButton | default(true) and behavior.autoplay | default(true) %}
            <button class="carousel-pause"
                    aria-label="Pause carousel"
                    data-playing="true">
                <span class="pause-icon">❚❚</span>
                <span class="play-icon" style="display:none;">▶</span>
            </button>
        {% endif %}

        <div class="carousel-slides">
            {% for slide in slides %}
                <div class="carousel-slide {% if loop.first %}active{% endif %}"
                     role="group"
                     aria-roledescription="slide"
                     aria-label="Slide {{ loop.index }} of {{ slides | length }}">
                    {% for child in slide.components | default([]) %}
                        {% set child_path = path + ['slides', loop.index0, 'components', loop.index0] %}
                        {{ render_component(child, tokens, child_path) }}
                    {% endfor %}
                </div>
            {% endfor %}
        </div>

        {# Navigation arrows #}
        {% if navigation.showArrows | default(true) %}
            {% set arrow_pos_class = 'carousel-arrows-' ~ (navigation.arrowPosition | default('inside')) %}
            <div class="carousel-navigation {{ arrow_pos_class }}">
                <button class="carousel-prev {% if arrow_style == 'circle' %}carousel-arrow-circle{% endif %}"
                        aria-label="Previous slide">{{ prev_symbol }}</button>
                <button class="carousel-next {% if arrow_style == 'circle' %}carousel-arrow-circle{% endif %}"
                        aria-label="Next slide">{{ next_symbol }}</button>
            </div>
        {% endif %}

        {# Indicators #}
        {% if navigation.showDots | default(true) %}
            {% set indicator_style = indicators.style | default('dots') %}
            {% set indicator_pos = indicators.position | default('bottom') %}
            <div class="carousel-indicators carousel-indicators-{{ indicator_pos }} carousel-indicators-{{ indicator_style }}"
                 role="tablist"
                 aria-label="Slide indicators">
                {% for slide in slides %}
                    <button class="carousel-indicator {% if loop.first %}active{% endif %}"
                            role="tab"
                            aria-selected="{{ 'true' if loop.first else 'false' }}"
                            aria-label="Go to slide {{ loop.index }}">
                        {% if indicator_style == 'numbers' %}{{ loop.index }}{% endif %}
                    </button>
                {% endfor %}
            </div>
        {% endif %}
    </div>
{% endmacro %}
```

### 4.4 CSS Additions (`components.css`)

```css
/* Carousel fade transition */
.carousel-fade .carousel-slide {
    opacity: 0;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    transition: opacity var(--carousel-duration, 300ms) ease;
}
.carousel-fade .carousel-slide.active {
    opacity: 1;
    position: relative;
}

/* Pause button */
.carousel-pause {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 10;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem;
    cursor: pointer;
    font-size: 0.75rem;
}
.carousel-pause:hover {
    background: rgba(0, 0, 0, 0.7);
}

/* Arrow positions */
.carousel-arrows-outside .carousel-prev {
    left: -3rem;
}
.carousel-arrows-outside .carousel-next {
    right: -3rem;
}

/* Circle arrow style */
.carousel-arrow-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid #ccc;
}

/* Indicator styles */
.carousel-indicators-dashes .carousel-indicator {
    width: 24px;
    height: 4px;
    border-radius: 2px;
}

.carousel-indicators-numbers .carousel-indicator {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    font-size: 12px;
}

.carousel-indicators-top {
    top: 1rem;
    bottom: auto;
}
```

### 4.5 JavaScript Update (`component_interactions.js`)

```javascript
function initCarousel(carouselElement) {
    const autoplay = carouselElement.dataset.autoplay === 'true';
    const delay = parseInt(carouselElement.dataset.delay) || 3000;
    const loop = carouselElement.dataset.loop === 'true';
    const pauseOnHover = carouselElement.dataset.pauseOnHover === 'true';
    const animDuration = parseInt(carouselElement.dataset.animationDuration) || 300;

    // Set CSS variable for animation duration
    carouselElement.style.setProperty('--carousel-duration', `${animDuration}ms`);

    let isPaused = false;
    let intervalId = null;

    // Pause button functionality
    const pauseBtn = carouselElement.querySelector('.carousel-pause');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            isPaused = !isPaused;
            pauseBtn.dataset.playing = !isPaused;
            pauseBtn.querySelector('.pause-icon').style.display = isPaused ? 'none' : 'inline';
            pauseBtn.querySelector('.play-icon').style.display = isPaused ? 'inline' : 'none';
            pauseBtn.setAttribute('aria-label', isPaused ? 'Play carousel' : 'Pause carousel');

            if (isPaused) {
                clearInterval(intervalId);
            } else if (autoplay) {
                startAutoplay();
            }
        });
    }

    // Pause on hover
    if (pauseOnHover && autoplay) {
        carouselElement.addEventListener('mouseenter', () => {
            if (!isPaused) clearInterval(intervalId);
        });
        carouselElement.addEventListener('mouseleave', () => {
            if (!isPaused && autoplay) startAutoplay();
        });
    }

    function startAutoplay() {
        intervalId = setInterval(() => {
            if (!isPaused) goToNext();
        }, delay);
    }

    // ... rest of carousel logic
}
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `component_defaults.yaml` | Add new default properties for all 4 components |
| `component_schemas.yaml` | Add new schema fields with proper groups |
| `schema_tokens.yaml` | Add `aspectRatios`, `objectPositions`, `imageFilters`, `shadowScale`, `hoverEffects` |
| `tokens.yaml` | Add token values for new properties |
| `ssr_python/templates/macros/_components.html` | Update `render_image`, `render_video`, `render_gif`, `render_carousel` macros |
| `ssr_python/static/css/components.css` | Add CSS for hover effects, caption overlay, carousel enhancements |
| `ssr_python/static/js/component_interactions.js` | Update carousel initialization for new features |

---

## Implementation Order

1. **Tokens first** - Add all new tokens to `tokens.yaml` and `schema_tokens.yaml`
2. **Defaults second** - Add new defaults to `component_defaults.yaml`
3. **Schemas third** - Add schema fields to `component_schemas.yaml`
4. **Macros fourth** - Update Jinja2 macros in `_components.html`
5. **CSS fifth** - Add CSS to `components.css`
6. **JavaScript last** - Update carousel runtime

---

## Verification

1. **Start Flask server:** `cd ssr_python && python app.py`
2. **Test each component in properties panel:**
   - New fields appear in correct groups
   - Token dropdowns show all options
   - Conditional fields show/hide correctly
3. **Test visual rendering:**
   - Image aspect ratios maintain shape
   - Filters apply correctly
   - Hover effects animate
   - Captions display in correct positions
4. **Test carousel accessibility:**
   - Pause button toggles autoplay
   - Keyboard navigation works
   - ARIA labels read correctly
