Project Summary: Website Builder
This document provides a comprehensive overview of the Website Builder application, detailing its core JavaScript modules.

Tech or languages used - Javascript, CSS, HTML

1. Project Overview
The application is a browser-based, visual website builder. It allows users to create web page layouts by typing a YAML structure into a code editor. A live preview immediately renders the output. Users can click on components in the preview to edit their properties (like color, text, and size) through a dedicated UI panel. The final result can be exported as a complete, standalone HTML file.

2. JavaScript Modules Breakdown
The JavaScript is structured into several key modules:

*   **`js/core`**: This directory contains the core application logic.
    *   `app.js`: Initializes the application, gets DOM references, and wires up events and actions.
    *   `state.js`: Manages the application's state, including the YAML structure, component templates, schemas, selection, and history.
    *   `templates.js`: Loads component defaults, schemas, and tokens from YAML files.
    *   `yaml.js`: Provides functions for parsing and generating YAML, as well as for manipulating the YAML structure.
*   **`js/properties`**: This directory handles the rendering of the properties panel.
    *   `index.js`: Renders the properties panel for the selected component based on its schema. It uses helper functions to render different types of properties (text, select, color, etc.).
    *   `customRenderers.js`: Provides custom UI for editing complex properties, like a list of links or accordion items.
*   **`js/render`**: This directory is responsible for rendering the HTML preview from the YAML structure.
    *   `index.js`: The main rendering engine. It traverses the YAML structure and calls specific rendering functions for each component type. It handles both preview and export modes.
*   **`js/ui`**: This directory contains the UI-related logic.
    *   `actions.js`: Defines the actions that can be performed in the UI, such as parsing and rendering the YAML, inserting and deleting components, and applying properties.
    *   `events.js`: Initializes all the event listeners for the application, such as for the code editor, preview window, and buttons.
*   **`js/utils`**: This directory contains utility functions used throughout the application.
    *   `object.js`: Provides utility functions for working with objects, such as deep cloning, merging, and getting/setting nested values.
    *   `strings.js`: Contains string utility functions, like `escapeHtml`.
    *   `styles.js`: Provides functions for converting units (e.g., `toRem`) and resolving style values from design tokens.
    *   `timing.js`: Contains timing-related utility functions, like `debounce`.
*   **`js/component_interactions.js`**: This file contains the logic for initializing and handling interactions with complex components like carousels and title bars.
*   **`js/script.js`**: This is the main entry point of the application, which calls `initializeApp`.