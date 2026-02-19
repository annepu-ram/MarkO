# Plan: Ticker Component

## Context

The app needs a new interactive "ticker" component — a horizontally scrolling strip of child components (like a news ticker, logo carousel, or promotional banner). Users configure scroll direction, speed, pause-on-hover, and choose between continuous smooth scrolling or step-by-step scrolling with pauses. This follows the same interactive component pattern as carousel, tabs, and accordion.

**After plan approval, this will also be saved to `docs/plans_to_implement/TICKER_COMPONENT_PLAN.md`.**

---

## YAML Structure

```yaml
- name: ticker
  properties:
    behavior:
      direction: left           # left, right
      speed: 40                 # pixels per second (continuous mode)
      mode: continuous          # continuous, step
      pauseOnHover: true
      pauseDuration: 3000       # ms between items (step mode only)
    spacing:
      marginBlock: md
      marginInline: none
      gap: lg                   # gap between items
    appearance:
      background:
        color: '#ffffff'
        transparency: 0
  items:                        # component-level array (NOT inside properties)
    - name: image
      properties:
        source: { url: 'https://...', altText: 'Logo 1' }
    - name: image
      properties:
        source: { url: 'https://...', altText: 'Logo 2' }
```

---

## Part 1: Jinja2 Template

**CREATE: `ssr_python/templates/components/interactive/_ticker.html`**

```jinja2
{% macro render_ticker(component, tokens, path, component_id) %}
    {% set properties = component.properties | default({}) %}
    {% set items = component.items | default([]) %}
    {% set behavior = properties.behavior | default({}) %}
    {% set spacing = properties.spacing | default({}) %}
    {% set appearance = properties.appearance | default({}) %}

    {% set direction = behavior.direction | default('left') %}
    {% set speed = behavior.speed | default(40) %}
    {% set mode = behavior.mode | default('continuous') %}
    {% set pause_on_hover = behavior.pauseOnHover | default(true) %}
    {% set pause_duration = behavior.pauseDuration | default(3000) %}

    {% set gap_token = spacing.gap | default('lg') %}
    {% set gap_value = tokens.spacing[gap_token] if gap_token in tokens.spacing else '1rem' %}

    {% set styles = build_styles(component, tokens) %}

    {% if items | length == 0 %}
        <div class="ticker chrome-target"
             data-component-id="{{ component_id }}"
             style="{{ styles }} min-height: 60px; display: flex; align-items: center; justify-content: center; border: 2px dashed #ccc;">
            <span style="color: #6b7280;">Add items to the ticker</span>
        </div>
    {% else %}
        <div class="ticker chrome-target"
             data-component-id="{{ component_id }}"
             data-component-type="ticker"
             data-direction="{{ direction }}"
             data-speed="{{ speed }}"
             data-mode="{{ mode }}"
             data-pause-on-hover="{{ 'true' if pause_on_hover else 'false' }}"
             data-pause-duration="{{ pause_duration }}"
             data-ss-initialized="false"
             aria-label="Content ticker"
             style="{{ styles }} --ticker-gap: {{ gap_value }}; overflow: hidden; position: relative;">

            <div class="ticker-track" style="display: flex; gap: var(--ticker-gap); will-change: transform;">
                {# Render items #}
                {% for item in items %}
                    {% set item_path = path + ['items', loop.index0] %}
                    <div class="ticker-item">
                        {{ render_component(item, tokens, item_path) }}
                    </div>
                {% endfor %}

                {# Duplicate items for seamless infinite loop (continuous mode) #}
                {% if mode == 'continuous' %}
                    {% for item in items %}
                        {% set item_path = path + ['items', loop.index0] %}
                        <div class="ticker-item ticker-item-duplicate" aria-hidden="true">
                            {{ render_component(item, tokens, item_path) }}
                        </div>
                    {% endfor %}
                {% endif %}
            </div>
        </div>
    {% endif %}
{% endmacro %}
```

**Key details:**
- `component.items` is component-level (like carousel's `component.slides`)
- Boolean data attributes use `{{ 'true' if value else 'false' }}` pattern
- Continuous mode duplicates items in DOM for seamless looping
- Duplicates have `aria-hidden="true"` for accessibility
- `--ticker-gap` CSS variable from gap token

---

## Part 2: Dispatcher & Assembly

**MODIFY: `ssr_python/templates/components/_dispatcher.html`** — Add after carousel (line 43):

```jinja2
    {% elif name == 'ticker' %}
        {{ render_ticker(component, tokens, path, component_id) }}
```

**MODIFY: `ssr_python/templates/components/_assembly.html`** — Add after carousel (line 18):

```jinja2
{% include "components/interactive/_ticker.html" %}
```

---

## Part 3: Component Defaults

**MODIFY: `ssr_python/config/component_defaults.yaml`** — Add after carousel section:

```yaml
ticker:
  behavior:
    direction: left
    speed: 40
    mode: continuous
    pauseOnHover: true
    pauseDuration: 3000
  spacing:
    marginBlock: md
    marginInline: none
    gap: lg
  appearance:
    background:
      color: '#ffffff'
      transparency: 0
  items:
  - name: heading
    properties:
      text: Ticker Item 1
      level: 4
      typography:
        size: md
        weight: semibold
  - name: heading
    properties:
      text: Ticker Item 2
      level: 4
      typography:
        size: md
        weight: semibold
  - name: heading
    properties:
      text: Ticker Item 3
      level: 4
      typography:
        size: md
        weight: semibold
```

---

## Part 4: Component Schema

**MODIFY: `ssr_python/config/component_schemas.yaml`** — Add after carousel section:

```yaml
ticker:
  groups:
  - id: items
    label: Items
    fields:
    - path: items
      type: custom
      renderer: tickerItems
      target: component
  - id: behavior
    label: Behavior
    fields:
    - path: behavior.direction
      type: select
      label: Scroll Direction
      options:
      - value: left
        label: Scroll Left
      - value: right
        label: Scroll Right
    - path: behavior.mode
      type: select
      label: Scroll Mode
      options:
      - value: continuous
        label: Continuous Smooth Scroll
      - value: step
        label: Step (Scroll-Pause-Scroll)
    - path: behavior.speed
      type: number
      label: Scroll Speed (px/sec)
      min: 10
      max: 200
      showWhen:
        field: behavior.mode
        value: continuous
    - path: behavior.pauseDuration
      type: number
      label: Pause Duration (ms)
      min: 1000
      max: 10000
      showWhen:
        field: behavior.mode
        value: step
    - path: behavior.pauseOnHover
      type: checkbox
      label: Pause on Hover
  - id: spacing
    label: Spacing
    fields:
    - path: spacing.marginBlock
      type: select
      label: Margin (Top+Bottom)
      tokens: spacingScale
    - path: spacing.marginInline
      type: select
      label: Margin (Left+Right)
      tokens: spacingScale
    - path: spacing.gap
      type: select
      label: Gap Between Items
      tokens: gapScale
  - id: appearance
    label: Appearance
    fields:
    - path: appearance.background.color
      type: color
      label: Background Color
    - path: appearance.background.transparency
      type: range
      label: Background Transparency
      min: 0
      max: 100
      unit: '%'
```

---

## Part 5: CSS Styles

**MODIFY: `ssr_python/static/css/components.css`** — Add after carousel styles:

```css
/* ===================================
   TICKER COMPONENT
   =================================== */

.ticker {
    width: 100%;
    position: relative;
    overflow: hidden;
}

.ticker-track {
    display: flex;
    align-items: center;
    width: max-content;
}

.ticker-item {
    flex-shrink: 0;
    display: flex;
    align-items: center;
}

/* Continuous mode: CSS animation for GPU-accelerated scrolling */
.ticker[data-mode="continuous"] .ticker-track {
    animation-name: ticker-scroll;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-play-state: running;
}

/* Direction: left = items scroll right-to-left (default) */
.ticker[data-direction="left"] .ticker-track {
    animation-direction: normal;
}

/* Direction: right = items scroll left-to-right */
.ticker[data-direction="right"] .ticker-track {
    animation-direction: reverse;
}

/* Pause on hover */
.ticker[data-pause-on-hover="true"]:hover .ticker-track {
    animation-play-state: paused;
}

/* Step mode: transitions controlled by JS */
.ticker[data-mode="step"] .ticker-track {
    transition: transform 0.6s ease-in-out;
}

@keyframes ticker-scroll {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
}

.ticker {
    user-select: none;
    -webkit-user-select: none;
}
```

**How it works:**
- Continuous mode: items are duplicated in DOM. `translateX(-50%)` scrolls exactly one full set, then the animation restarts seamlessly (the duplicate set is in the same visual position).
- Animation duration is set by JS: `(trackWidth / 2) / speed` seconds.
- Direction uses `animation-direction: reverse` — no separate keyframes needed.
- Pause on hover uses `animation-play-state: paused` — pure CSS, no JS.
- Step mode uses CSS `transition` for smooth item-to-item movement, controlled by JS intervals.

---

## Part 6: Runtime JavaScript

**MODIFY: `ssr_python/static/js/swift-sites-runtime.js`**

### 6A. Add to `init()` method (line 27):

```javascript
this.initTickers();
```

### 6B. Add to `reset()` method (line 730):

```javascript
this.cleanupTickers();
```

### 6C. Add ticker methods (after titlebar methods, before counter-up):

```javascript
initTickers: function() {
    document.querySelectorAll('.ticker').forEach(ticker => {
        this._initTicker(ticker);
    });
},

_tickerIntervals: [],

_initTicker: function(tickerElement) {
    if (!tickerElement || tickerElement.dataset.ssInitialized === 'true') return;
    tickerElement.dataset.ssInitialized = 'true';

    const track = tickerElement.querySelector('.ticker-track');
    const items = tickerElement.querySelectorAll('.ticker-item:not(.ticker-item-duplicate)');
    if (!track || items.length === 0) return;

    const speed = parseInt(tickerElement.dataset.speed, 10) || 40;
    const mode = tickerElement.dataset.mode || 'continuous';
    const direction = tickerElement.dataset.direction || 'left';
    const pauseDuration = parseInt(tickerElement.dataset.pauseDuration, 10) || 3000;

    if (mode === 'continuous') {
        this._initContinuousTicker(track, speed);
    } else {
        this._initStepTicker(tickerElement, track, items, pauseDuration, direction);
    }
},

_initContinuousTicker: function(track, speed) {
    // duration = (half of total track width) / speed in seconds
    function updateDuration() {
        var duration = (track.scrollWidth / 2) / speed;
        track.style.animationDuration = duration + 's';
    }
    updateDuration();

    var resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(updateDuration, 150);
    }, { passive: true });
},

_initStepTicker: function(tickerElement, track, items, pauseDuration, direction) {
    var currentIndex = 0;
    var totalItems = items.length;
    var gap = parseFloat(getComputedStyle(track).gap) || 0;
    var self = this;

    function getStepDistance() {
        return items[0].offsetWidth + gap;
    }

    function moveToNext() {
        currentIndex++;
        if (currentIndex >= totalItems) {
            // Instant reset
            track.style.transition = 'none';
            track.style.transform = 'translateX(0)';
            currentIndex = 0;
            setTimeout(function() {
                track.style.transition = 'transform 0.6s ease-in-out';
            }, 50);
        } else {
            var offset = getStepDistance() * currentIndex;
            var dir = (direction === 'left') ? -offset : offset;
            track.style.transform = 'translateX(' + dir + 'px)';
        }
    }

    var intervalId = setInterval(moveToNext, pauseDuration);
    this._tickerIntervals.push(intervalId);

    // Pause on hover for step mode
    if (tickerElement.dataset.pauseOnHover === 'true') {
        tickerElement.addEventListener('mouseenter', function() {
            clearInterval(intervalId);
        });
        tickerElement.addEventListener('mouseleave', function() {
            intervalId = setInterval(moveToNext, pauseDuration);
            self._tickerIntervals.push(intervalId);
        });
    }
},

cleanupTickers: function() {
    this._tickerIntervals.forEach(function(id) { clearInterval(id); });
    this._tickerIntervals = [];
},
```

---

## Part 7: Custom Renderer for Items Editor

**MODIFY: `ssr_python/static/js/customRenderers.js`** — Add `tickerItems` renderer following the pattern of `carouselSlides`:

```javascript
tickerItems: function(field, value, onChange, componentPath) {
    // Similar to carouselSlides renderer
    // Shows list of items with name labels
    // Add/Delete buttons for managing items
    // Default new item: heading with "Item N" text
}
```

(Follow exact pattern of existing `carouselSlides` or `accordionItems` renderer in that file.)

---

## Files Summary

| File | Action | Change |
|------|--------|--------|
| `templates/components/interactive/_ticker.html` | CREATE | Jinja2 macro with data attributes, item duplication for continuous mode |
| `templates/components/_dispatcher.html` | MODIFY | Add `ticker` route after carousel (line 43) |
| `templates/components/_assembly.html` | MODIFY | Add `_ticker.html` include after carousel (line 18) |
| `config/component_defaults.yaml` | MODIFY | Add ticker defaults with 3 example heading items |
| `config/component_schemas.yaml` | MODIFY | Add ticker schema with behavior/spacing/appearance groups |
| `static/css/components.css` | MODIFY | Add ticker CSS with `@keyframes ticker-scroll` animation |
| `static/js/swift-sites-runtime.js` | MODIFY | Add `initTickers()`, `_initTicker()`, continuous/step init, cleanup |
| `static/js/customRenderers.js` | MODIFY | Add `tickerItems` custom renderer |

## What Does NOT Change

- `renderer.py` — Template concatenation handles new file automatically
- `routes/` — No new endpoints needed
- `preview_bridge.js` — Not involved (runtime JS handles init)
- `preview_frame.html` — No changes
- Existing components — No modifications

## Verification

1. Start Flask, paste ticker YAML into editor
2. **Continuous left:** Items scroll smoothly right-to-left, seamless loop, no visible jump
3. **Continuous right:** Items scroll left-to-right
4. **Pause on hover:** Hovering stops animation, leaving resumes
5. **Speed:** Change speed value — faster/slower scroll
6. **Step mode:** Items scroll one at a time with pause between
7. **Step pauseDuration:** Longer/shorter waits between steps
8. **Properties panel:** All fields display, conditional visibility works (speed only for continuous, pauseDuration only for step)
9. **Component selection:** Clicking ticker in preview selects it
10. `python -m pytest tests/ -v` — all tests pass
