# Project Overview

This project is a web-based visual website builder. It allows users to create and customize web pages using a YAML-based structure in a code editor, with a live preview that updates in real-time. The application is built with vanilla JavaScript, HTML, and CSS.

> **Update:** Headings now use a unified `heading` component with a `level` property instead of discrete `h1`/`h2`/`h3` entries. Additional text helpers (`eyebrow`, `caption`, `blockquote`) share the same typography/spacing token model.
> **Architecture:** Default typography/colors for text components now live entirely in `component_defaults.yaml`; runtime rendering just merges overrides so blockquote/eyebrow/caption styling is driven by YAML rather than hard-coded script or CSS.

## Key Features

- **Live Preview:** A real-time preview of the website as you type.
- **Component-Based:** Build your site using a YAML-based structure.
- **Visual Editing:** Click on components in the preview to edit their properties.
- **Export to HTML:** Export your creation as a single, clean HTML file.

# Project Structure

```
.
├── css/
│   ├── components.css      # Styles for rendered components
│   └── style.css           # Styles for the builder UI
├── js/
│   ├── core/
│   │   ├── app.js          # Core application initialization
│   │   ├── state.js        # State management
│   │   ├── templates.js    # Loading component templates and schemas
│   │   └── yaml.js         # YAML parsing and manipulation
│   ├── properties/
│   │   ├── customRenderers.js # Custom property editors
│   │   └── index.js        # Properties panel rendering
│   ├── render/
│   │   └── index.js        # Component rendering engine
│   ├── ui/
│   │   ├── actions.js      # UI actions
│   │   └── events.js       # Event listeners
│   ├── utils/
│   │   ├── object.js       # Object utility functions
│   │   ├── strings.js      # String utility functions
│   │   ├── styles.js       # Style utility functions
│   │   └── timing.js       # Timing utility functions
│   ├── component_interactions.js # Component-specific interactions
│   └── script.js           # Main entry point
├── index.html              # Main HTML file
├── component_defaults.yaml # Default properties for components
├── component_schemas.yaml  # Schema for component properties
├── schema_tokens.yaml      # Design tokens for property editors
├── README.md               # Project documentation
└── GEMINI.md               # This file
```

# Building and Running

This is a client-side application and does not require a build process. To run the application, simply open the `index.html` file in a web browser.

# Development Conventions

- **JavaScript:** The JavaScript code is organized into modules, each with a specific responsibility. The main entry point is `js/script.js`, which initializes the application. The core logic is in the `js/core` directory, the rendering engine is in `js/render`, the properties panel logic is in `js/properties`, UI actions and events are in `js/ui`, and utility functions are in `js/utils`.
- **CSS:** The application's UI is styled in `css/style.css`. The generated components are styled using `css/components.css` and inline styles for user-defined customizations.
- **HTML:** The main structure of the application is in `index.html`.

# Available Components

The following components are available for use in the editor:


Titlebar:  A navigation bar with a logo, title, and links.
```yaml
- name: h3
  properties:
    # ...
```

Heading 1: A top-level heading.
```yaml
- name: h3
  properties:
    # ...
```

Heading 2: A second-level heading.
```yaml
- name: h2
  properties:
    # ...
```

Heading 3: A third-level heading.
```yaml
- name: h3
  properties:
    # ...
```

Paragraph: A block of text.
```yaml
- name: paragraph
  properties:
    # ...
```

Image: An image.
```yaml
- name: image
  properties:
    src: 'https://example.com/image.jpg'
    alt: 'An example image'
    height: '400px' # Optional: specifies the height of the image
  components:
    # Optional: A list of components to be rendered on top of the image.
    # Supported components: h1, h2, h3, paragraph, br, button
    - name: h1
      properties:
        text: 'This is a heading on the image'
        color: '#ffffff'
```

Video: A video from YouTube.
```yaml
- name: video
  properties:
    src: 'https://www.youtube.com/watch?v=your_video_id'
```

GIF: A GIF image.
```yaml
- name: gif
  properties:
    # ...
```

Text Box: A single-line text input.
```yaml
- name: textbox
  properties:
    # ...
```

Text Area: A multi-line text input.
```yaml
- name: textarea
  properties:
    # ...
```

Label: A text label.
```yaml
- name: label
  properties:
    # ...
```

Button: A clickable button.
```yaml
- name: button
  properties:
    # ...
```

Dropdown: A dropdown menu.
```yaml
- name: dropdown
  properties:
    # ...
```

Calendar: A calendar display.
```yaml
- name: calendar
  properties:
    # ...
```

Checkbox: A checkbox.
```yaml
- name: checkbox
  properties:
    # ...
```

Radio Button: A radio button.
```yaml
- name: radio
  properties:
    # ...
```

Columns Grid: A grid of columns.
```yaml
- name: columnsgrid
  properties:
    columns:
    - components:
        # ...
    - components:
        # ...
```

Accordion: A collapsible content area.
```yaml
- name: accordion
  properties:
    content:
      components:
      # ...
```

Tabs: A set of tabs.
```yaml
- name: tabs
  properties:
    tabs:
      - title: 'About Us'
        components:
    # ...
```

Hamburger Menu: A hamburger menu.
```yaml
- name: hamburger
  properties:
    # ...
```

Line Break: A line break.
```yaml
- name: br
  properties:
    # ...
```
# How to Use

1.  **Open `index.html` in a web browser.**
2.  **Write YAML structure in the code editor.** For example, to create a heading, type:
```yaml
components:
  - name: h1
    properties:
      text: 'Hello, World!'
```
3.  **See the live preview update.**
4.  **Click on a component in the preview** to open the properties panel.
5.  **Edit the properties** in the panel and click "Apply Changes".
6.  **Export your work** by clicking the "Export HTML" button.
7.  **Example of complex nested components.** 
```yaml
page:
  properties:
    backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    backgroundImage: 'https://www.toptal.com/designers/subtlepatterns/uploads/moroccan-flower.png'
    padding: 0

components:
  - name: titlebar
    properties:
      title: 'My Company'
      logo: 'https://via.placeholder.com/50x40/4f46e5/ffffff?text=LOGO'
      backgroundColor: '#ffffff'
      links:
        - text: 'Home'
          value: '#home'
        - text: 'Services' 
          value: '#services'
        - text: 'Contact'
          value: '#contact'

  - name: columnsgrid
    properties:
      count: 3
      padding: 40
      margin: 20
    columns:
      - components:
          - name: paragraph
            properties:
              text: 'Beautiful, responsive websites that engage your audience.'
              textAlign: 'center'
          - name: button
            properties:
              text: 'Learn More'
              variant: 'primary'
              
      - components:
          - name: paragraph
            properties:
              text: 'Full-stack development with modern technologies.'
              textAlign: 'center'
          - name: button
            properties:
              text: 'View Projects'
              variant: 'secondary'
              
      - components:
          - name: paragraph
            properties:
              text: '24/7 support and maintenance for your peace of mind.'
              textAlign: 'center'

  - name: tabs
    properties:
      margin: 40
    tabs:
      - title: 'About Us'
        components:
          - name: h2
            properties:
              text: 'Our Story'
              fontSize: 28
          - name: paragraph
            properties:
              text: 'Founded in 2020, we have been creating digital experiences that matter. Our team of designers and developers work together to bring your vision to life.'
              fontSize: 16
              lineHeight: 1.6
          - name: image
            properties:
              src: 'https://via.placeholder.com/600x300/4f46e5/ffffff?text=Our+Team'
              alt: 'Our team working together'
              
      - title: 'Our Process'
        components:
          - name: accordion
            properties:
              title: 'Discovery Phase'
            content:
              components:
                - name: paragraph
                  properties:
                    text: 'We start by understanding your business goals, target audience, and project requirements through detailed consultation.'
          - name: accordion
            properties:
              title: 'Design Phase'
            content:
              components:
                - name: paragraph
                  properties:
                    text: 'Our designers create wireframes and mockups, ensuring every element serves a purpose and enhances user experience.'
          - name: accordion
            properties:
              title: 'Development Phase'
            content:
              components:
                - name: paragraph
                  properties:
                    text: 'Clean, efficient code brings the designs to life with responsive layouts and smooth interactions.'
```

# Functions

## core

- `initializeApp()`: Initializes the application.
- `loadMetadata()`: Fetches and loads component templates, schemas, and tokens.
- `setSelection()`: Sets the selected component.
- `getState()`: Returns the current application state.
- `setYamlStructure()`: Sets the YAML structure in the state.
- `getYamlStructure()`: Gets the YAML structure from the state.
- `getComponentByPath()`: Retrieves a component from the YAML structure using its path.
- `updateComponentByPath()`: Updates a component in the YAML structure using its path.
- `deleteComponentByPath()`: Deletes a component from the YAML structure using its path.
- `parseYamlContent()`: Parses a YAML string into a JavaScript object.
- `generateYamlFromStructure()`: Converts a JavaScript object into a YAML string.

## properties

- `renderPropertiesPanel()`: Renders the properties panel for a selected component.
- `applyPropertiesForComponent()`: Applies the properties from the properties panel to the selected component.
- `clearPropertiesPanel()`: Clears the properties panel.

## render

- `renderYamlStructure()`: Renders the entire YAML structure into HTML.
- `renderComponentsList()`: Renders a list of components into HTML.
- `renderComponent()`: Renders a single component into HTML.
- `initializeAllComponents()`: Initializes all registered components.

## ui

- `createActions()`: Creates the UI actions.
- `initializeEvents()`: Initializes the event listeners.

## utils

- `debounce()`: A utility function that delays the execution of a function.
- `toRem()`: Converts a pixel value to a rem value.
- `deepClone()`: Creates a complete, independent copy of a JavaScript object or array. This is crucial for state immutability, ensuring that the original state is not accidentally modified.
- `deepMerge()`: Recursively merges the properties of one or more source objects into a target object. This is used to combine default component properties with user-defined properties.

- heading: relies on its `level` plus typography settings from `component_defaults.yaml`; there are no heading variants (level 1 -> `xxxl`, level 2 -> `xxl`, level 3 -> `xl`, level 4 -> `lg`, level 5 -> `md`, level 6 -> `sm`).
- blockquote: default leaves the blockquote styling exactly as supplied by the component defaults and the shared CSS; pull is the customization that tweaks margins/typography.
- caption: default keeps the standard caption look (smaller type, neutral color). The muted variant swaps color/alignment.
- eyebrow: default uses the baseline uppercase styling and color; accent is the variant that swaps to the accent color.