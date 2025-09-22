# Titlebar Component Implementation Plan

## 1. Overview
This document outlines the implementation plan for adding a titlebar component to the existing website builder application. The titlebar will be a flexible header component with logo, title, navigation links, and responsive scroll behavior. navbar should first appear at the top. when scrolled down it should stick to the top and shrink to 50% of its original size. there should a property to set the logo to the left or right.

## 2. Component Definition

### 2.1 Component Template Addition
Add to `componentTemplates` object in `script.js`:


titlebar: 
    logo: 'https://via.placeholder.com/50x40', 
    title: 'Website Title',
    links: 
        { text: 'Home', value: '#home' },
        { text: 'About', value: '#about' },
        { text: 'Contact', value: '#contact' }
    
    borderColor: '#ddd',
    backgroundColor: '#ffffff',
    focusedButtonBackgroundColor: '#f0f0f0',
    alignment: 'left',
    height: 60,
    padding: 10,
    margin: 0
}
```

### 2.2 Properties Specification
- **logo** (string): URL to logo image
- **title** (string): Main title text
- **links** (array): Navigation menu items with `text` and `value` properties
- **borderColor** (string): Border color of the titlebar
- **backgroundColor** (string): Background color of the titlebar
- **focusedButtonBackgroundColor** (string): Hover/focus color for links
- **alignment** (string): Layout alignment - 'left', 'center', 'right'
- **height** (number): Titlebar height in pixels
- **padding** (number): Internal padding
- **margin** (number): External margin

## 3. Implementation Tasks

### 3.1 Core Rendering Logic

#### 3.1.1 Update `generateComponentInnerHTML()` function
Add titlebar case to the switch statement:

```javascript
case 'titlebar':
    return generateTitlebarHTML(props, classes, styleAttr, mode);
case 'paragraph':
    const text = props.text || 'This is a paragraph of text content.';
    return `<p ${finalAttrs}>${text.replace(/\n/g, '<br>')}</p>`;
```



#### 3.1.2 Create `generateTitlebarHTML()` function
```javascript
function generateTitlebarHTML(props, classes, styleAttr, mode) {
    const alignmentClass = getAlignmentClass(props.alignment);
    const logoHTML = props.logo ? `<img src="${props.logo}" alt="Logo" class="titlebar-logo" />` : '';
    const titleHTML = props.title ? `<h1 class="titlebar-title">${props.title}</h1>` : '';
    const linksHTML = generateTitlebarLinks(props.links, props.focusedButtonBackgroundColor);
    
    return `
        <nav class="titlebar ${alignmentClass} ${classes}" style="${styleAttr} height: ${toRem(props.height || 60)};" id="titlebar-${Date.now()}">
            <div class="titlebar-brand">
                ${logoHTML}
                ${titleHTML}
            </div>
            <button id="mobile-menu-button" class="mobile-menu-button">
                <span class="bar"></span>
                <span class="bar"></span>
                <span class="bar"></span>
            </button>
            <div class="titlebar-nav">
                ${linksHTML}
            </div>
        </nav>
    `;
}
```

#### 3.1.3 Helper Functions
```javascript
function getAlignmentClass(alignment) {
    switch(alignment) {
        case 'center': return 'titlebar-center';
        case 'right': return 'titlebar-right';
        default: return 'titlebar-left';
    }
}

function generateTitlebarLinks(links, focusColor) {
    if (!Array.isArray(links)) return '';
    
    return links.map(link => 
        `<a href="${link.value || '#'}" class="titlebar-link" style="--focus-bg: ${focusColor || '#f0f0f0'}">${link.text || 'Link'}</a>`
    ).join('');
}
```

### 3.2 CSS Styling

#### 3.2.1 Add to `style.css`
```css
/* --- Titlebar Component --- */
.titlebar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background-color: #fff;
    border-bottom: 1px solid #ddd;
    position: sticky;
    top: 0;
    z-index: 1000;
    transition: all 0.3s ease-in-out;
}

.titlebar-brand {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.titlebar-logo {
    height: 40px;
}

.titlebar-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0;
}

.titlebar-nav {
    display: flex;
    gap: 1rem;
}

.titlebar-link {
    color: #333;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background-color 0.3s ease;
}

.titlebar-link:hover {
    background-color: #f0f0f0;
}

.mobile-menu-button {
    display: none;
    flex-direction: column;
    gap: 4px;
    cursor: pointer;
}

.mobile-menu-button .bar {
    width: 25px;
    height: 3px;
    background-color: #333;
    border-radius: 3px;
    transition: all 0.3s ease-in-out;
}

.titlebar-left {
    justify-content: flex-start;
}

.titlebar-center {
    justify-content: center;
}

.titlebar-right {
    justify-content: flex-end;
}

.titlebar.scrolled {
    padding: 0.5rem 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .titlebar-nav {
        display: none;
        flex-direction: column;
        position: absolute;
        top: 60px;
        left: 0;
        width: 100%;
        background-color: #fff;
        border-top: 1px solid #ddd;
        padding: 1rem;
    }

    .titlebar-nav.active {
        display: flex;
    }

    .mobile-menu-button {
        display: flex;
    }
}
```

### 3.3 Properties Panel Enhancement

#### 3.3.1 Update `renderPropertiesPanel()` function
Add special handling for titlebar component:

```javascript
// In renderPropertiesPanel function, add after existing logic:
if (component.type === 'titlebar') {
    let links = finalProps.links || [];
    if (typeof links === 'string') {
        try {
            links = JSON.parse(links.replace(/'/g, '"'));
        } catch (e) {
            links = [];
        }
    }
    propertiesHTML += generateLinksEditor(links);
}
```

#### 3.3.2 Create Links Editor Function
```javascript
function generateLinksEditor(links) {
    let html = '<div class="links-editor"><h4>Navigation Links</h4>';
    
    links.forEach((link, index) => {
        html += `
            <div class="link-item" data-index="${index}">
                <label>Link ${index + 1}</label>
                <input type="text" placeholder="Link Text" value="${link.text || ''}" data-prop="links.${index}.text">
                <input type="text" placeholder="Link URL" value="${link.value || ''}" data-prop="links.${index}.value">
                <button type="button" class="btn-remove-link" onclick="removeTitlebarLink(${index})">Remove</button>
            </div>
        `;
    });
    
    html += '<button type="button" class="btn-add-link" onclick="addTitlebarLink()">Add Link</button></div>';
    return html;
}
```

#### 3.3.3 Link Management Functions
```javascript
function addTitlebarLink() {
    const componentId = selectedComponentElement?.dataset.componentId;
    if (!componentId) return;

    const lineIndex = componentIdToLineMap[componentId];
    const editor = document.getElementById('codeEditor');
    const lines = editor.value.split('\n');
    const component = parseComponentLine(lines[lineIndex]);

    const links = component.props.links || [];
    const newLinks = [...links, { text: 'New Link', value: '#' }];
    component.props.links = newLinks;

    renderPropertiesPanel(component, componentId);
}

function removeTitlebarLink(index) {
    const componentId = selectedComponentElement?.dataset.componentId;
    if (!componentId) return;

    const lineIndex = componentIdToLineMap[componentId];
    const editor = document.getElementById('codeEditor');
    const lines = editor.value.split('\n');
    const component = parseComponentLine(lines[lineIndex]);

    const links = component.props.links || [];
    const newLinks = links.filter((_, i) => i !== index);
    component.props.links = newLinks;

    renderPropertiesPanel(component, componentId);
}
```

### 3.4 Scroll Behavior Implementation

#### 3.4.1 Add Scroll Listener
```javascript
// Add to DOMContentLoaded event listener
function initializeTitlebar() {
    const navbar = document.querySelector('.titlebar');
    if (!navbar) return;

    const mobileMenuButton = navbar.querySelector('.mobile-menu-button');
    const navLinks = navbar.querySelector('.titlebar-nav');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    window.addEventListener('scroll', function() {
        const titlebars = document.querySelectorAll('.titlebar');
        const scrolled = window.scrollY > 50;

        titlebars.forEach(titlebar => {
            if (scrolled) {
                titlebar.classList.add('scrolled');
            } else {
                titlebar.classList.remove('scrolled');
            }
        });
    });
}
```

### 3.5 Component Button Addition

#### 3.5.1 Update `index.html`
Add titlebar button to the components section:

```html
<button class="component-item" data-component="@titlebar" title="Syntax: @titlebar{logo: '...', title: '...', links: [...]}">
    <span>📋</span> Title Bar
</button>
```

## 4. Testing Strategy

### 4.1 Unit Testing
- Test `parsePropsString()` with links array property
- Test `generateTitlebarHTML()` with various property combinations
- Test alignment classes generation
- Test scroll behavior toggle

### 4.2 Integration Testing
- Test titlebar rendering in preview mode
- Test properties panel for titlebar component
- Test links addition/removal functionality
- Test export functionality with titlebar component

### 4.3 Visual Testing
- Test responsive behavior on mobile devices
- Test scroll shrinking animation
- Test different alignment options
- Test logo auto-resizing with various image dimensions

## 5. Implementation Timeline

### Phase 1 (Day 1-2): Core Implementation
- Add component template definition
- Implement basic HTML generation
- Add CSS styling for navbar

### Phase 2 (Day 3-4): Properties Panel
- Implement links editor in properties panel
- Add link addition/removal functionality
- Test properties application

### Phase 3 (Day 5): Scroll Behavior
- Implement scroll detection and shrinking animation
- Test smooth transitions
- Fine-tune responsive behavior

### Phase 4 (Day 6): Testing & Polish
- Comprehensive testing across all features
- Bug fixes and refinements
- Documentation updates

## 6. Potential Issues & Solutions

### 6.1 Links Array Parsing
**Issue**: Complex array parsing in `parsePropsString()`
**Solution**: Enhance regex to handle nested array structures properly

### 6.2 Scroll Performance
**Issue**: Scroll event performance on complex pages
**Solution**: Implement throttling and use `requestAnimationFrame`

### 6.3 Mobile Responsiveness
**Issue**: Navbar overflow on small screens
**Solution**: Implement hamburger menu collapse for mobile

### 6.4 Export Compatibility
**Issue**: Scroll behavior not working in exported HTML
**Solution**: Include necessary JavaScript in export template

## 7. Future Enhancements

- Sticky navbar option
- Dropdown menus for navigation items
- Search functionality integration
- Social media links section
- Custom logo upload functionality
