# Component Properties Matrix

Cross-tabulation showing which properties are available for each component. Use this to understand property commonality across components.

## Legend
- **Y** = Property supported
- **-** = Not supported
- Property groups are color-coded by category

---

## Property Groups by Component

### Layout Containers

| Property | page | layout-row | layout-column | columnsgrid | form |
|----------|------|------------|---------------|-------------|------|
| **LAYOUT** |||||
| layout.tag | - | Y | Y | - | - |
| layout.align | - | Y | Y | Y | - |
| layout.gap | - | Y | Y | Y | Y |
| layout.wrap | - | Y | Y | - | - |
| layout.direction | - | - | - | - | Y |
| layout.columns | - | - | - | Y | - |
| layout.padding.* | Y | - | - | - | - |
| layout.margin.* | Y | - | - | - | - |
| layout.width | - | Y | Y | - | - |
| layout.minWidth | - | Y | Y | - | - |
| layout.maxWidth | - | Y | Y | - | - |
| layout.minHeight | - | Y | Y | - | - |
| layout.maxHeight | - | Y | Y | - | - |
| **SPACING** |||||
| spacing.paddingBlock | - | Y | Y | - | - |
| spacing.paddingInline | - | Y | Y | - | - |
| spacing.marginBlock | - | Y | Y | - | - |
| spacing.marginInline | - | Y | Y | - | - |
| **BACKGROUND** |||||
| background.color | Y | Y | Y | - | - |
| background.transparency | Y | Y | Y | - | - |
| background.image | Y | Y | Y | - | - |
| **APPEARANCE** |||||
| appearance.border.width | - | Y | Y | - | - |
| appearance.border.style | - | Y | Y | - | - |
| appearance.border.color | - | Y | Y | - | - |
| appearance.radius | - | Y | Y | - | - |
| appearance.shadow | - | Y | Y | - | - |
| **RESPONSIVE** |||||
| responsive.breakpoints.md | - | - | - | Y | - |
| responsive.breakpoints.sm | - | - | - | Y | - |
| **SUBMIT** |||||
| submit.show | - | - | - | - | Y |
| submit.buttonText | - | - | - | - | Y |

---

### Text Components

| Property | heading | paragraph | eyebrow | caption | blockquote | link |
|----------|---------|-----------|---------|---------|------------|------|
| **CONTENT** ||||||
| text | Y | Y | Y | Y | - | Y |
| quote | - | - | - | - | Y | - |
| cite | - | - | - | - | Y | - |
| level | Y | - | - | - | - | - |
| href | - | - | - | - | - | Y |
| **TYPOGRAPHY** ||||||
| typography.size | Y | Y | Y | Y | Y | Y |
| typography.weight | Y | Y | Y | - | - | Y |
| typography.align | Y | Y | Y | Y | Y | - |
| typography.color | Y | Y | Y | Y | Y | - |
| typography.lineHeight | Y | - | - | Y | Y | - |
| typography.transform | Y | - | Y | Y | - | - |
| typography.letterSpacing | Y | Y | Y | - | - | - |
| **LAYOUT** ||||||
| layout.widthMode | Y | Y | Y | Y | Y | - |
| **APPEARANCE** ||||||
| appearance.background.color | Y | Y | Y | Y | Y | - |
| appearance.background.transparency | Y | Y | Y | Y | Y | - |
| appearance.radius | Y | Y | Y | Y | Y | - |
| appearance.padding.block | Y | Y | Y | Y | Y | - |
| appearance.padding.inline | Y | Y | Y | Y | Y | - |
| appearance.border.accentColor | - | - | - | - | Y | - |
| appearance.color | - | - | - | - | - | Y |
| appearance.underline | - | - | - | - | - | Y |
| appearance.showArrow | - | - | - | - | - | Y |
| **SPACING** ||||||
| spacing.marginBlock | Y | Y | Y | Y | Y | - |
| spacing.marginInline | Y | Y | Y | Y | Y | - |

---

### Media Components

| Property | image | video | gif |
|----------|-------|-------|-----|
| **SOURCE** |||
| source.url | Y | Y | Y |
| source.altText | Y | - | - |
| **PRESENTATION** |||
| presentation.height | Y | - | - |
| presentation.fit | Y | - | Y |
| presentation.cornerStyle | Y | - | - |
| **PLAYBACK** |||
| playback.controls | - | Y | - |
| playback.autoplay | - | Y | - |
| playback.muted | - | Y | - |
| **OVERLAY** |||
| overlay.enabled | Y | - | - |

---

### Form Input Components

| Property | textbox | textarea | dropdown | checkbox | radio | calendar |
|----------|---------|----------|----------|----------|-------|----------|
| **LABEL** ||||||
| label.text | Y | Y | Y | Y | Y | - |
| label.show | Y | Y | Y | - | - | - |
| label.typography.size | Y | - | - | Y | Y | - |
| label.typography.weight | Y | - | - | Y | Y | - |
| label.typography.color | Y | - | - | Y | Y | - |
| **FIELD** ||||||
| field.placeholder | Y | Y | Y | - | - | - |
| field.initialValue | Y | - | - | - | - | - |
| field.helperText | Y | Y | - | - | - | - |
| field.required | Y | Y | - | Y | - | - |
| field.rows | - | Y | - | - | - | - |
| field.options | - | - | Y | - | - | - |
| field.selected | - | - | Y | - | - | - |
| field.text | - | - | - | Y | Y | - |
| field.checked | - | - | - | Y | Y | - |
| field.groupName | - | - | - | - | Y | - |
| field.value | - | - | - | - | Y | - |
| **DISPLAY** ||||||
| display.month | - | - | - | - | - | Y |
| display.year | - | - | - | - | - | Y |
| **APPEARANCE** ||||||
| appearance.border.width | Y | Y | Y | - | - | - |
| appearance.border.color | Y | Y | Y | - | - | - |
| appearance.background.color | Y | Y | Y | - | - | - |
| appearance.background.transparency | Y | Y | Y | - | - | - |
| appearance.radius | Y | Y | Y | - | - | - |
| appearance.color | - | - | - | Y | Y | - |
| appearance.showWeekNumbers | - | - | - | - | - | Y |
| **TYPOGRAPHY** ||||||
| typography.color | Y | Y | - | - | - | - |

---

### Interactive Components

| Property | accordion | tabs | carousel | hamburger |
|----------|-----------|------|----------|-----------|
| **CONTENT/ITEMS** ||||
| items (component-level) | Y | - | - | - |
| tabs (component-level) | - | Y | - | - |
| slides (component-level) | - | - | Y | - |
| label | - | - | - | Y |
| links | - | - | - | Y |
| **BEHAVIOR** ||||
| behavior.allowMultipleOpen | Y | - | - | - |
| behavior.autoplay | - | - | Y | - |
| behavior.delay | - | - | Y | - |
| behavior.loop | - | - | Y | - |
| **NAVIGATION** ||||
| navigation.showArrows | - | - | Y | - |
| navigation.showDots | - | - | Y | - |
| **LAYOUT** ||||
| layout.widthMode | Y | Y | - | - |
| layout.orientation | - | Y | - | - |
| **TYPOGRAPHY** ||||
| typography.title.size | Y | - | - | - |
| typography.title.weight | Y | - | - | - |
| typography.title.color | Y | - | - | - |
| typography.content.size | Y | - | - | - |
| typography.content.weight | Y | - | - | - |
| typography.content.color | Y | - | - | - |
| typography.label.size | - | Y | - | - |
| typography.label.weight | - | Y | - | - |
| typography.label.active.color | - | Y | - | - |
| typography.label.inactive.color | - | Y | - | - |
| **APPEARANCE** ||||
| appearance.titleBackground.color | Y | - | - | - |
| appearance.contentBackground.color | Y | - | - | - |
| appearance.contentBackground.transparency | Y | - | - | - |
| appearance.border.width | Y | - | - | - |
| appearance.border.style | Y | - | - | - |
| appearance.border.color | Y | - | - | - |
| appearance.border.position | Y | - | - | - |
| appearance.radius | Y | - | - | - |
| appearance.padding.block | Y | - | - | - |
| appearance.padding.inline | Y | - | - | - |
| appearance.tab.background.active | - | Y | - | - |
| appearance.tab.background.inactive | - | Y | - | - |
| appearance.tab.border.* | - | Y | - | - |
| appearance.content.background.* | - | Y | - | - |
| appearance.content.border.* | - | Y | - | - |
| appearance.content.padding.* | - | Y | - | - |
| **SPACING** ||||
| spacing.marginBlock | Y | Y | - | - |
| spacing.marginInline | Y | Y | - | - |

---

### UI Components

| Property | button | titlebar | br |
|----------|--------|----------|-----|
| **CONTENT** |||
| text | Y | - | - |
| size | - | - | Y |
| **BRANDING** |||
| branding.logoUrl | - | Y | - |
| branding.showLogo | - | Y | - |
| branding.title | - | Y | - |
| **NAVIGATION** |||
| navigation.links | - | Y | - |
| **ACTION** |||
| action.type | Y | - | - |
| action.value | Y | - | - |
| **LAYOUT** |||
| layout.alignment | - | Y | - |
| layout.height | - | Y | - |
| layout.shrinkPercent | - | Y | - |
| **APPEARANCE** |||
| appearance.background.color | Y | Y | - |
| appearance.background.transparency | Y | Y | - |
| appearance.border.width | Y | Y | - |
| appearance.border.style | Y | - | - |
| appearance.border.color | Y | Y | - |
| appearance.radius | Y | - | - |
| appearance.padding.block | Y | - | - |
| appearance.padding.inline | Y | - | - |
| appearance.iconPlacement | Y | - | - |
| appearance.focus.background | - | Y | - |
| appearance.focus.color | - | Y | - |
| **TYPOGRAPHY** |||
| typography.weight | Y | - | - |
| typography.color | Y | - | - |
| typography.title.size | - | Y | - |
| typography.title.weight | - | Y | - |
| typography.title.color | - | Y | - |
| typography.menu.size | - | Y | - |
| typography.menu.weight | - | Y | - |
| typography.menu.color | - | Y | - |
| **SPACING** |||
| spacing.marginBlock | Y | - | - |
| spacing.marginInline | Y | - | - |

---

## Common Properties Summary

### Most Common Properties (across all components)

| Property Category | # Components | Components |
|-------------------|--------------|------------|
| typography.size | 10 | heading, paragraph, eyebrow, caption, blockquote, link, textbox, checkbox, radio, tabs |
| typography.weight | 9 | heading, paragraph, eyebrow, link, button, textbox, checkbox, radio, tabs |
| typography.color | 8 | heading, paragraph, eyebrow, caption, blockquote, textbox, textarea, button |
| spacing.marginBlock | 9 | layout-row, layout-column, heading, paragraph, eyebrow, caption, blockquote, button, accordion, tabs |
| spacing.marginInline | 9 | layout-row, layout-column, heading, paragraph, eyebrow, caption, blockquote, button, accordion, tabs |
| appearance.background.color | 10 | page, layout-row, layout-column, heading, paragraph, eyebrow, caption, blockquote, button, titlebar |
| appearance.background.transparency | 10 | page, layout-row, layout-column, heading, paragraph, eyebrow, caption, blockquote, button, titlebar |
| layout.widthMode | 8 | heading, paragraph, eyebrow, caption, blockquote, accordion, tabs |
| layout.gap | 4 | layout-row, layout-column, columnsgrid, form |
| layout.align | 3 | layout-row, layout-column, columnsgrid |

### Unique Properties (single component only)

| Property | Component |
|----------|-----------|
| level | heading |
| quote, cite | blockquote |
| href | link |
| layout.columns | columnsgrid |
| layout.direction | form |
| submit.* | form |
| behavior.allowMultipleOpen | accordion |
| behavior.autoplay, behavior.delay, behavior.loop | carousel |
| navigation.showArrows, navigation.showDots | carousel |
| branding.*, layout.shrinkPercent | titlebar |
| field.rows | textarea |
| field.options, field.selected | dropdown |
| field.groupName, field.value | radio |
| display.month, display.year | calendar |

---

## Property Categories at a Glance

| Category | Description | Main Components |
|----------|-------------|-----------------|
| **layout** | Positioning, sizing, alignment | Containers, text components |
| **spacing** | Margins and padding | All except media, form inputs |
| **typography** | Font styling | Text, buttons, form labels |
| **appearance** | Visual styling (bg, border, radius) | Most components |
| **background** | Background color, image | Containers, text |
| **source** | Media URLs | image, video, gif |
| **presentation** | Media display options | image, gif |
| **field** | Form input configuration | Form inputs |
| **label** | Form input labels | Form inputs |
| **behavior** | Interactive behavior | accordion, carousel |
| **navigation** | Nav links, controls | titlebar, carousel |

---

**Last Updated:** January 2025
