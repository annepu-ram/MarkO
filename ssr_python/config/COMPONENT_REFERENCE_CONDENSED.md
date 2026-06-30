# SwiftSites YAML Reference

## Rules
1. `- name: X` then `properties:` — never inline. `components:` is sibling of `properties:`.
2. Array keys at COMPONENT level (not in properties): tabs→`tabs:`, accordion→`items:`, carousel→`slides:`, columnsgrid/ticker→`columns:`
3. Never use `typography.fontFamily` — fonts from site theme only.
4. `opacity`: 0=transparent, 100=opaque. Row/column bg default=0.
5. `layout.widthMode` is STRING ("50" not 50), only on direct children of layout-row. Never mix "stretch" with fixed widths.
6. Color defaults: heading→*color-primary, body→*color-text, eyebrow/link→*color-accent, caption→*color-secondary. Dark sections: ALL text→*color-background.
7. Omit default values. Only set what you change.

## Tokens
| Property | Values |
|----------|--------|
| spacing/margin/padding/gap | none, xxs, xs, sm, md, lg, xl, xxl, xxxl |
| typography.size | xxs, xs, sm, md, lg, xl, xxl, xxxl |
| weight | thin, extralight, light, regular, medium, semibold, bold, extrabold, black |
| radius/cornerStyle | none, xs, sm, md, lg, xl, xxl, pill |
| shadow | none, soft, medium, elevated, retro |
| textShadow | none, soft, strong |
| lineHeight | "1.2", "1.4", "1.5", "1.6" |
| transform | none, uppercase, lowercase, capitalize |
| letterSpacing | tighter, tight, normal, wide, wider, widest |
| align | left, center, right |
| verticalAlign | top, center, bottom, stretch, baseline, space-between, space-around, space-evenly |
| horizontalAlign | left, center, right, space-between, space-around, space-evenly |
| widthMode | "fit", "16", "25", "33", "50", "66", "75", "83", "stretch" |
| fit | cover, contain, fill, none |
| filter | none, grayscale, sepia, blur, brightness, contrast, saturate |
| hoverEffect | none, zoom, lift, brighten, darken |
| objectPosition | center, top, bottom, left, right |
| border.style | solid, dashed, dotted |
| br type | solid, dashed, dotted, wave, slant |
| badge variant | info, success, warning, danger |
| ticker widthMode | fit, 120, 200, 280, 360, 480 |

## Shared Property Groups
**typography** (heading, paragraph, eyebrow, caption, blockquote, link, button): size, weight, align, color, lineHeight, transform, letterSpacing, fontStyle(normal|italic), textDecoration(none|underline|line-through)
**typography-mini** (counter-up, countdown): size, weight, color, align
**spacing** (layout-row, layout-column, heading, paragraph, eyebrow, caption, blockquote, link, button, image, gif, video, carousel, accordion, tabs, ticker, panorama-display): marginBlock, marginInline, paddingBlock, paddingInline
**appearance-container** (layout-row, layout-column, form): background(color, opacity, image), border(width, style, color), radius, shadow, shadowColor, blur
**appearance-media** (image, gif): minHeight(rem), maxHeight(rem), fit, cornerStyle, objectPosition, filter, shadow, shadowColor, hoverEffect, lazy, overlay(enabled, color, opacity)

## Components
**site** — theme.fonts{heading: &font-heading, content: &font-content}, theme.colors{primary: &color-primary, text: &color-text, secondary: &color-secondary, accent: &color-accent, background: &color-background}. Children: page.
**page** — slug, title (component-level). spacing(paddingBlock, paddingInline), appearance.background(color, opacity, image).
**layout-row** — layout: tag(section|div|main|article), horizontalAlign, verticalAlign, wrap(wrap|nowrap), gap. +spacing +appearance-container. Children MUST have widthMode.
**layout-column** — layout: tag, horizontalAlign, verticalAlign, wrap, gap, widthMode. +spacing +appearance-container.
**columnsgrid** — layout.columns(number), layout.gap, layout.verticalAlign. responsive.breakpoints{md, sm}. appearance: shadow, columnBackground, columnOpacity, columnRadius, columnBorder(width, color), columnBlur. +spacing. Array:`columns:`→{components}
**form** — layout.style(vertical|inline|horizontal), submit(buttonText, show). +appearance-container +spacing.
**heading** — text(supports |), level(1-6). +typography(def: size=xl, weight=bold, lineHeight="1.2") +spacing +appearance(background, radius, textShadow) +widthMode.
**paragraph** — text(supports |). +typography(def: size=md, color=*color-text, lineHeight="1.6") +spacing +appearance(background, radius, textShadow) +widthMode.
**eyebrow** — text. +typography(def: size=xs, weight=semibold, color=*color-accent, transform=uppercase, letterSpacing=wide) +spacing +widthMode.
**caption** — text. +typography(def: size=sm, color=*color-secondary, align=center) +spacing +widthMode.
**blockquote** — quote(not text!), cite. +typography(def: size=xl, fontStyle=italic). appearance.border.accentColor. +spacing +widthMode.
**link** — text, href, appearance(underline, showArrow). +typography(def: color=*color-accent) +spacing +widthMode.
**image** — source(url, altText), layout(horizontalAlign, widthMode=stretch). +appearance-media +spacing. Can have `components:` for overlay.
**gif** — same as image.
**video** — source.url, appearance(aspectRatio, height(px)), playback(controls, autoplay, muted, loop), poster.url. +spacing +widthMode.
**video-background** — source(url, poster), appearance(aspectRatio, minHeight, fit, objectPosition, overlay), playback(autoplay, loop, muted, playsinline), content(verticalAlign, horizontalAlign, padding). Has `components:` for overlay.
**button** — text, action(type: link|inlineScript|submit, value). appearance: background(color, opacity), border(width, style, color), radius, shadow, iconPlacement(none|left|right). +typography(def: weight=semibold, color=*color-background) +spacing +widthMode.
**titlebar** — branding(showLogo, logoUrl, title), navigation.links[]{label, href}, layout(alignment, height(px)), scroll.shrinkPercentage, appearance(background, border, focus), typography(title: size/weight/color, menu: size/weight/color).
**hamburger** — label, links[]{label, href}.
**br** — size, type, orientation(horizontal|vertical), thickness(px), color, invert(bool), mirror(bool).
**tabs** — layout(orientation: horizontal|vertical, widthMode), typography.label(size, weight, active.color, inactive.color), appearance.tab(background, border), appearance.content(background, border, padding). +spacing. Array:`tabs:`→{title, components}
**accordion** — behavior.allowMultipleOpen. typography(title, content: size/weight/color). appearance(titleBackground, contentBackground, border+position, radius). +spacing +widthMode. Array:`items:`→{title, components}
**carousel** — behavior(autoplay, delay, loop, pauseOnHover, swipeEnabled, swipeThreshold, keyboardNavigation), animation(effect: slide|fade, duration), navigation(showArrows, showDots, arrowStyle, arrowPosition), indicators(style: dots|bars|numbers, position), accessibility(showPauseButton, ariaLabel). +spacing. Array:`slides:`→{components}
**ticker** — behavior(direction: left|right, speed, mode: continuous|step, pauseOnHover, pauseDuration), layout(widthMode, gap), appearance(columnBackground, columnOpacity, columnRadius, columnBorder). +spacing. Array:`columns:`→{components}
**panorama-display** — source(url, altText), behavior(autoScroll, autoScrollSpeed, stepDistance, pauseOnHover, initialPosition: left|center|right), appearance(border, radius, shadow). +spacing.
**icon** — name(kebab-case), size(STRING px), strokeWidth(STRING), color.
**badge** — text, variant(info|success|warning|danger), pill(bool), typography(size, color).
**rating** — value(0-5, half ok), iconType(star|heart), showCount, color, typography(size, color).
**progress-bar** — percent(0-100), thickness(small|medium|large), color, trackColor, colorGradient(bool), appearance.radius.
**counter-up** — endValue, duration(ms), prefix, suffix. +typography-mini.
**countdown** — targetDate(ISO 8601), format(DD:HH:MM:SS|HH:MM:SS|MM:SS), expiredText. +typography-mini.
**Form fields (textbox, textarea, dropdown, checkbox, radio, calendar)** — All: label(text, show, typography.weight/color), field(name, helperText, required), appearance(size: sm|md|lg, accentColor). textbox: placeholder, initialValue, validation(none|email|phone|zipCode|url|password|creditCard|lettersOnly|alphanumeric). textarea: placeholder, rows. dropdown/checkbox/radio: options(newline-separated STRING). calendar: value, min, max.

## Container Keys
| Component | Key | Entry |
|-----------|-----|-------|
| layout-row/column/form | components: | {- name: ...} |
| tabs | tabs: | {title, components} |
| accordion | items: | {title, components} |
| carousel | slides: | {components} |
| columnsgrid/ticker | columns: | {components} |
