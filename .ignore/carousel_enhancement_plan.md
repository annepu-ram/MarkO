# Carousel Component Enhancement Plan

## 1. Overview

This document outlines the plan to redesign the `carousel` component from the ground up to address existing bugs and enhance its functionality. The new design will be based on the structure of the `columnsgrid` component, making it a complex, nestable component.

## 2. New Carousel Design

The carousel component will be redesigned to function similarly to the `columnsgrid` component, making it a complex, nested component. This allows for greater flexibility in the content of each slide.

### 2.1. YAML Structure

The new structure for the carousel will be as follows:

```yaml
- name: carousel
  properties:
    images_count: 3 # Determines the number of slides
    # Other carousel-specific properties like:
    # transition_type: 'slide'
    # autoplay: true
    # delay: 3000
  slides:
    - components:
        - name: image
          properties:
            src: 'https://example.com/image1.jpg'
            alt: 'Image 1'
        - name: h3
          properties:
            text: 'First Slide'
    - components:
        - name: image
          properties:
            src: 'https://example.com/image2.jpg'
            alt: 'Image 2'
        - name: paragraph
          properties:
            text: 'Second slide with some text.'
    - components:
        - name: image
          properties:
            src: 'https://example.com/image3.jpg'
            alt: 'Image 3'
```

### 2.2. Key Changes

*   **`images_count` property:** This integer property will control the number of slides in the carousel.
*   **`slides` property:** This will be an array of objects, where each object represents a slide.
*   **Nested Components:** Each slide will contain a `components` array, allowing any other component (like `image`, `h3`, `paragraph`, `button`, etc.) to be placed within a slide. This is the same pattern used by the `columnsgrid` component.

## 3. Implementation Details

The implementation will need to be updated to support this new structure.

### 3.1. `js/script.js`

1.  **`renderCarousel` function:** This function will be significantly modified.
    *   It will read the `images_count` property.
    *   It will iterate through the `slides` array.
    *   For each slide, it will call `renderComponentsList` to render the components within that slide. This reuses the existing rendering logic.
2.  **Properties Panel:** The properties panel for the carousel will be updated.
    *   It will have a field to edit `images_count`. Changing this value will dynamically add or remove slide objects from the `slides` array in the YAML.
    *   Instead of an "Add Image" button, the user will interact with the nested components within the preview. Clicking on an element inside a slide will open the properties panel for that specific element (e.g., the `image` or `h3`).

This new design makes the carousel a much more powerful and flexible component, aligning it with the existing `columnsgrid` component for a more consistent development experience.

## 4. Testing

After implementing the new component, it should be tested to ensure that:

*   The carousel displays correctly with nested components.
*   The `images_count` property correctly controls the number of slides.
*   All carousel-specific properties (like transitions, autoplay) can be customized.
*   Editing components within a slide works as expected.
*   The overall functionality is stable and free of the bugs that prompted the redesign.