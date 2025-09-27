# Titlebar Component Implementation Plan

## 1. Overview
This document outlines the implementation plan for adding a titlebar component to the existing website builder application. The titlebar will be a flexible header component with logo, title, navigation links, and responsive scroll behavior. The navbar should first appear at the top. When scrolled down, it should stick to the top and shrink to 50% of its original size. There should be a property to set the logo to the left or right.

## 2. Component Definition

### 2.1 Component Defaults
Add to `component_defaults.yaml`:

```yaml
titlebar:
  branding:
    logoUrl: https://via.placeholder.com/50x40
    title: Website Title
  navigation:
    links:
      - label: Home
        href: '#home'
      - label: About
        href: '#about'
      - label: Contact
        href: '#contact'
  layout:
    alignment: left
    logoPlacement: left
    height: 60
  appearance:
    background:
      color: '#ffffff'
    border:
      width: 1
      style: solid
      color: '#dddddd'
    focus:
      background: '#f0f0f0'
  typography:
    title:
      size: 24
      weight: bold
    menu:
      size: 16
      weight: medium
```

### 2.2 Component Schema
Add to `component_schemas.yaml`:

```yaml
titlebar:
  groups:
    - id: branding
      label: Branding
      fields:
        - path: branding.logoUrl
          type: text
          label: Logo URL
        - path: branding.title
          type: text
          label: Title
    - id: navigation
      label: Navigation
      fields:
        - path: navigation.links
          type: custom
          renderer: linksEditor
    - id: layout
      label: Layout
      fields:
        - path: layout.alignment
          type: select
          label: Alignment
          options: [left, center, right]
        - path: layout.logoPlacement
          type: select
          label: Logo Placement
          options: [left, right]
        - path: layout.height
          type: number
          label: Height (px)
    - id: appearance
      label: Appearance
      fields:
        - path: appearance.background.color
          type: color
          label: Background Color
        - path: appearance.border.width
          type: number
          label: Border Width (px)
        - path: appearance.border.style
          type: select
          label: Border Style
          tokens: borderStyleOptions
        - path: appearance.border.color
          type: color
          label: Border Color
        - path: appearance.focus.background
          type: color
          label: Focus Background
    - id: typography
      label: Typography
      fields:
        - path: typography.title.size
          type: number
          label: Title Size (px)
        - path: typography.title.weight
          type: select
          label: Title Weight
          tokens: fontWeights
        - path: typography.menu.size
          type: number
          label: Menu Size (px)
        - path: typography.menu.weight
          type: select
          label: Menu Weight
          tokens: fontWeights
```

## 3. Implementation Tasks

### 3.1 Core Rendering Logic

#### 3.1.1 Update `js/render/index.js`
Update `generateTitlebarHTML` to use the new properties from the schema.

### 3.2 CSS Styling

#### 3.2.1 Add to `css/components.css`
Add the necessary CSS for the titlebar, including the scroll behavior and responsive styles.

### 3.3 Properties Panel Enhancement

#### 3.3.1 Update `js/properties/customRenderers.js`
Create a `linksEditor` custom renderer to handle the `navigation.links` property.

### 3.4 Scroll Behavior Implementation

#### 3.4.1 Update `js/component_interactions.js`
Add an `initializeTitlebar` function to handle the scroll behavior and mobile menu toggle.

## 4. Testing Strategy

### 4.1 Unit Testing
- Test the `linksEditor` custom renderer.
- Test the `initializeTitlebar` function.

### 4.2 Integration Testing
- Test titlebar rendering in preview mode.
- Test the properties panel for the titlebar component.
- Test the links editor functionality.
- Test the export functionality with the titlebar component.

### 4.3 Visual Testing
- Test the responsive behavior on mobile devices.
- Test the scroll shrinking animation.
- Test the different alignment and logo placement options.

## 5. Implementation Timeline

### Phase 1 (Day 1-2): Core Implementation
- Add component defaults and schema.
- Implement basic HTML generation in `js/render/index.js`.
- Add CSS styling for the titlebar.

### Phase 2 (Day 3-4): Properties Panel
- Implement the `linksEditor` custom renderer.
- Test properties application.

### Phase 3 (Day 5): Scroll Behavior
- Implement the `initializeTitlebar` function in `js/component_interactions.js`.
- Test the scroll behavior and mobile menu.

### Phase 4 (Day 6): Testing & Polish
- Comprehensive testing across all features.
- Bug fixes and refinements.
- Documentation updates.

## 6. Potential Issues & Solutions

### 6.1 Scroll Performance
**Issue**: Scroll event performance on complex pages.
**Solution**: Use `requestAnimationFrame` and passive event listeners in `js/component_interactions.js`.

### 6.2 Export Compatibility
**Issue**: Scroll behavior not working in exported HTML.
**Solution**: Include the necessary JavaScript in the exported HTML file.