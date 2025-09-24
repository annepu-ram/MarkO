# Project Overview

This project is a web-based visual website builder. It allows users to create and customize web pages using a YAML-based structure in a code editor, with a live preview that updates in real-time. The application is built with vanilla JavaScript, HTML, and CSS, and it utilizes the Mini.css framework for styling the generated components.

> **Update:** Headings now use a unified `heading` component with a `level` property instead of discrete `h1`/`h2`/`h3` entries. Additional text helpers (`eyebrow`, `caption`, `blockquote`) share the same typography/spacing token model.
> **Architecture:** Default typography/colors for text components now live entirely in `component_defaults.yaml`; runtime rendering just merges overrides so blockquote/eyebrow/caption styling is driven by YAML rather than hard-coded script or CSS.

## Key Features

- **Live Preview:** A real-time preview of the website as you type.
- **Component-Based:** Build your site using a YAML-based structure.
- **Visual Editing:** Click on components in the preview to edit their properties.
- **Export to HTML:** Export your creation as a single, clean HTML file.
- **Mini.css Integration:** Uses the lightweight Mini.css framework for a professional look.

# Project Structure

```
.
â”œâ”€â”€ css/
â”‚   â””â”€â”€ style.css         # Styles for the builder UI
â”œâ”€â”€ js/
â”‚   â””â”€â”€ script.js         # Core application logic
â”œâ”€â”€ index.html            # Main HTML file
â”œâ”€â”€ README.md             # Project documentation
â””â”€â”€ GEMINI.md             # This file
```

# Building and Running

This is a client-side application and does not require a build process. To run the application, simply open the `index.html` file in a web browser.

# Development Conventions

- **JavaScript:** The core logic is in `js/script.js`. The code is organized into sections for configuration, utility functions, the rendering engine, UI handling, and actions. The parsing logic has been updated to use a YAML-based structure, which inherently supports multiline component definitions.
- **CSS:** The application's UI is styled in `css/style.css`. The generated components are styled using a hybrid approach: Mini.css for structure and inline styles for user-defined customizations.
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

- `init()`: Initializes the application. It loads component templates, sets up event listeners, initializes component buttons, and the resizer. It's called when the DOM content is loaded.
- `loadComponentTemplates()`: Fetches and loads component templates from `component_defaults.yaml`. Called by `init()`.
- `debounce(func, delay)`: A utility function that delays the execution of a function until after a certain amount of time has passed without it being called.
- `initializeEventListeners()`: Sets up all the event listeners for the application, such as for the code editor, preview window, and various buttons. Called by `init()`.
- `registerComponentForInitialization(name, id)`: Registers a component to be initialized after rendering. Called by `renderCarousel` and `renderSimpleComponent`.
- `initializeAllComponents()`: Initializes all registered components. Called by `parseYamlComponents`.
- `handlePreviewClick(event)`: Handles click events on the preview window, including selecting and deleting components.
- `handleKeyDown(event)`: Handles keydown events in the code editor, such as Tab for indentation and Ctrl+Z/Y for undo/redo.
- `parseYamlContent(yamlText)`: Parses a YAML string into a JavaScript object.
- `generateYamlFromStructure(structure)`: Converts a JavaScript object into a YAML string.
- `getComponentByPath(structure, path)`: Retrieves a component from the YAML structure using its path.
- `updateComponentByPath(structure, path, newComponent)`: Updates a component in the YAML structure using its path.
- `deleteComponentByPath(structure, path)`: Deletes a component from the YAML structure using its path.
- `deleteComponent(componentId)`: Deletes a component by its ID.
- `insertYamlComponent(componentName)`: Inserts a new component into the YAML structure.
- `renderYamlStructure(structure, mode)`: Renders the entire YAML structure into HTML.
- `renderComponentsList(components, basePath, mode)`: Renders a list of components into HTML.
- `renderComponent(component, path, mode)`: Renders a single component into HTML.
- `renderCarousel(component, path, mode)`: Renders a carousel component.
- `renderGroupComponent(component, path, mode)`: Renders a group component.
- `renderPageComponent(component, path, mode)`: Renders the page component.
- `renderImageComponent(component, path, mode)`: Renders an image component.
- `renderSimpleComponent(component, path, mode)`: Renders a simple component.
- `renderColumnsGrid(component, path, mode)`: Renders a columns grid component.
- `renderAccordion(component, path, mode)`: Renders an accordion component.
- `renderTabs(component, path, mode)`: Renders a tabs component.
- `generateComponentInnerHTML(type, props, classes, styleAttr, mode)`: Generates the inner HTML for a component.
- `generateTitlebarHTML(props, classes, styleAttr, mode)`: Generates the HTML for a titlebar component.
- `generateMiniCssClasses(type, props)`: Generates Mini.css classes for a component.
- `generateRemainingStyles(props)`: Generates inline styles for a component.
- `renderPropertiesPanel(component, componentId, path)`: Renders the properties panel for a selected component.
- `generateCarouselImageEditor(images)`: Generates the HTML for the carousel image editor in the properties panel.
- `addCarouselImage()`: Adds a new image to a carousel component.
- `removeCarouselImage(index)`: Removes an image from a carousel component.
- `renderProperty(key, value)`: Renders a single property in the properties panel.
- `renderImageProperty(key, value)`: Renders an image property in the properties panel.
- `renderTextProperty(key, value)`: Renders a text property in the properties panel.
- `renderColorProperty(key, value)`: Renders a color property in the properties panel.
- `toggleColorFields(selectElement, key)`: Toggles the visibility of color fields in the properties panel.
- `renderSelectProperty(key, value, options)`: Renders a select property in the properties panel.
- `applyYamlComponentProperties(componentId, path)`: Applies the properties from the properties panel to the selected component.
- `toRem(value)`: Converts a pixel value to a rem value.
- `generateCalendarHTML(props)`: Generates the HTML for a calendar component.
- `getAlignmentClass(alignment)`: Gets the alignment class for a titlebar component.
- `generateTitlebarLinks(links, focusColor)`: Generates the HTML for the links in a titlebar component.
- `generateLinksEditor(links)`: Generates the HTML for the links editor in the properties panel.
- `addTitlebarLink()`: Adds a new link to a titlebar component.
- `removeTitlebarLink(index)`: Removes a link from a titlebar component.
- `initializeComponentButtons()`: Initializes the component buttons in the sidebar.
- `initializeResizer()`: Initializes the resizer for the code editor.
- `toggleHelpPanel()`: Toggles the visibility of the help panel.
- `openFullscreen()`: Opens the preview in fullscreen mode.
- `closeFullscreen()`: Closes the fullscreen preview.
- `clearCanvas()`: Clears the code editor and the preview.
- `exportCode()`: Exports the website as an HTML file.
- `parseYamlComponents(yamlText)`: Parses the YAML from the code editor and renders the preview.
- `generateCleanHTML(yamlText)`: Generates clean HTML for export.
- `logHtml()`: Logs the generated HTML to the console.


- heading: relies on its `level` plus typography settings from `component_defaults.yaml`; there are no heading variants (level 1 -> `xxxl`, level 2 -> `xxl`, level 3 -> `xl`, level 4 -> `lg`, level 5 -> `md`, level 6 -> `sm`).
- blockquote: default leaves the blockquote styling exactly as supplied by the component defaults and the shared CSS; pull is the customization that tweaks margins/typography.
- caption: default keeps the standard caption look (smaller type, neutral color). The muted variant swaps color/alignment.
- eyebrow: default uses the baseline uppercase styling and color; accent is the variant that swaps to the accent color.




