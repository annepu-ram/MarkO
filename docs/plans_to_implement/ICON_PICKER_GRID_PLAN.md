# Plan: Searchable Icon Picker with All Material Icons (IMPLEMENTED)

## Status: Complete

## What Changed

Replaced the static 24-icon grid with a **searchable picker** that loads all ~2235 Google Material Icons from a JSON file. Users can type a keyword (e.g., "cart", "fire", "cloud") to filter icons instantly.

## Files Modified

| File | Change |
|------|--------|
| `static/data/material-icons.json` | **NEW** — JSON array of ~2235 icon names (34KB) |
| `static/js/propertiesPanel.js` | Async `renderIconGrid()` with search input, debounced filtering, max 60 visible |
| `static/css/style.css` | `.icon-picker-wrapper`, `.icon-picker-search`, scrollable grid, `.icon-picker-more` |
| `config/component_schemas.yaml` | Removed hardcoded icon options — picker loads dynamically |
| `templates/index.html` | Font link: Material Icons |
| `templates/preview_frame.html` | Font link: Material Icons |
| `templates/components/marketing/_icon.html` | Class: `material-icons` |
| `LLM_COMPONENT_GUIDE.md` | Updated icon docs |

## How It Works

1. When user clicks an icon component, the properties panel renders a search input + scrollable grid
2. `loadMaterialIcons()` fetches `/static/data/material-icons.json` (cached after first load)
3. Typing in the search box filters icons with 200ms debounce
4. Max 60 icons shown at once; "X more — refine search" indicator when truncated
5. Clicking an icon highlights it; value is collected via `.active[data-value]` selector
6. Icons render via Google Material Icons font ligatures (`<span class="material-icons">icon_name</span>`)
