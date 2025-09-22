Project Summary: Website Builder
This document provides a comprehensive overview of the Website Builder application, detailing its core JavaScript functions and the integration of the Mini.css framework.

Tech or languages used - Javascript, CSS, HTML

1. Project Overview
The application is a browser-based, visual website builder. It allows users to create web page layouts by typing a custom, simplified @component syntax into a code editor. A live preview immediately renders the output. Users can click on components in the preview to edit their properties (like color, text, and size) through a dedicated UI panel. The final result can be exported as a complete, standalone HTML file.

2. JavaScript Functions Breakdown (script.js)
The JavaScript is structured into several key areas: Configuration, Utility Functions, Rendering Engine, UI Handling, and Actions.

Configuration & State
componentTemplates: An object that stores the default properties for every available component (e.g., @h1, @button). This is used to populate the properties panel and provide default values when a new component is inserted.

selectedComponentElement: A global variable that keeps track of the currently selected component in the preview window.

componentIdToLineMap: An object that maps the unique ID of a rendered component in the preview to its corresponding line number in the code editor. This is crucial for linking a visual element back to its source code for editing.

Utility Functions
toRem(value): A vital utility that converts numeric pixel values (e.g., fontSize: 16) into relative rem units (e.g., font-size: 1.6rem). This ensures the final output is scalable and accessible.

parseComponentLine(line): This function uses a regular expression to parse a single line of text from the editor (e.g., @h1{text: 'Hello'}). It extracts the component's type (h1) and its props ({text: 'Hello'}).

The Rendering Engine (Core Logic)
This is the heart of the application, responsible for turning the @component syntax into HTML.

renderComponentTree(options): This is the main recursive function. It iterates through the lines of code from the editor.

It identifies @component lines and determines if they are simple (like @h1) or complex containers (like @tabs or @columnsgrid).

It calls the appropriate sub-renderer (renderSimpleComponent or renderComplexComponent).

Crucially, it handles nested structures by calling itself to render the content inside containers. It passes down an absoluteLineOffset to ensure that even deeply nested components can be correctly mapped back to their original line number.

It operates in two modes: 'preview' (adds extra wrappers and labels for the editor UI) and 'export' (generates clean, final HTML).

renderSimpleComponent(...): Renders a single, non-container component. It generates the necessary classes and styles and wraps the final HTML in a special <div> with a unique ID for the preview mode.

renderComplexComponent(...): Renders container components. It contains the logic for parsing the structure between a start tag (e.g., @tabs) and an end tag (e.g., @endtabs). It finds the child components (like @tab or @column) and recursively calls renderComponentTree to render their inner content.

UI Event Handlers & Initialization
handlePreviewClick(event): Manages clicks within the preview area. It identifies the clicked component, highlights it, and calls renderPropertiesPanel to display its properties for editing.

renderPropertiesPanel(...): Dynamically builds the HTML for the "Properties" panel based on the selected component's properties.

applyComponentProperties(...): Takes the new values from the properties panel, reconstructs the @component{...} line, and updates the code editor, which in turn triggers a re-render of the preview.

initializeComponentButtons(), initializeTabKey(), initializeResizer(): These functions are called when the page loads. They attach all the necessary event listeners to the UI elements (component buttons, the editor for tab key handling, and the draggable resizer), keeping the HTML clean of inline onclick handlers.

Actions
exportCode(): Generates the final, standalone .html file by creating a complete HTML structure, adding the Mini.css CDN link, and injecting the clean HTML rendered in 'export' mode.

openFullscreen() / closeFullscreen(): Manages the fullscreen preview modal.

clearCanvas(): Clears the editor and preview.

3. Mini.css Integration
The project was refactored to use the Mini.css framework instead of a large set of custom CSS rules. This was done to make the output more professional, lightweight, and maintainable.

The "Hybrid" Strategy
A "hybrid" approach was adopted for styling:

Framework for Structure: Mini.css classes are used for structural and predefined component styling (e.g., buttons, grids, accordions). The generateMiniCssClasses() function is responsible for adding these classes.

Inline Styles for Customization: User-defined properties that Mini.css doesn't control (like color, backgroundColor, fontSize) are applied as inline styles. The generateRemainingStyles() function handles this.

This strategy provides the best of both worlds: the consistency of a framework and the dynamic flexibility required by a visual builder.

Implementation Steps
HTML Setup: The Mini.css stylesheet is loaded via a CDN link in index.html.

CSS Cleanup: All the old, custom .comp-* classes were removed from style.css. The stylesheet now only contains styles for the builder's UI itself, not the rendered output.

Custom Components: For components that Mini.css lacks, like Tabs, custom CSS was written and added to style.css. This ensures a consistent look and feel while filling the gaps in the framework.

JavaScript Refactor: The generateComponentInnerHTML function was updated to apply both the Mini.css classes and the inline styles to the final HTML elements.