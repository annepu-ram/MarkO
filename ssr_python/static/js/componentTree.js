/**
 * Component Tree Module
 * Builds and renders a hierarchical tree view of components in the sidebar.
 * 
 * IMPORTANT: All sub-components MUST be at the component level, not under properties:
 * - component.components (for layout-row, layout-column, page, form)
 * - component.tabs[].components (for tabs)
 * - component.slides[].components (for carousel)
 * - component.columns[].components (for columnsgrid)
 * - component.columns[].components (for columnsgrid, ticker)
 * - component.items (for accordion - data items with title + components)
 */

/**
 * Map component names to their icon IDs in the SVG sprite
 * Icons must have 'icon-' prefix to match sprite symbol IDs
 * All icons are now available in the sprite after fixing the generation script
 */
const getComponentIcon = (componentName) => {
    const iconMap = {
        'page': 'icon-file-text',
        'layout-row': 'icon-layout-row',
        'layout-column': 'icon-layout-column',
        'columnsgrid': 'icon-layout-grid',
        'form': 'icon-clipboard-list',
        'heading': 'icon-heading-1',
        'paragraph': 'icon-pilcrow',
        'eyebrow': 'icon-type',
        'caption': 'icon-closed-captioning',
        'blockquote': 'icon-quote',
        'link': 'icon-link',
        'image': 'icon-image',
        'video': 'icon-video',
        'gif': 'icon-film',
        'button': 'icon-mouse-pointer-square',
        'titlebar': 'icon-credit-card',
        'tabs': 'icon-folder-tabs',
        'accordion': 'icon-chevrons-down-up',
        'carousel': 'icon-gallery-horizontal',
        'hamburger': 'icon-menu',
        'br': 'icon-wrap-text',
        'icon': 'icon-star',
        'badge': 'icon-tag',
        'rating': 'icon-star-filled',
        'progress-bar': 'icon-bar-chart',
        'counter-up': 'icon-hash',
        'countdown': 'icon-clock',
        'textbox': 'icon-type',
        'textarea': 'icon-file-text',
        'dropdown': 'icon-chevron-down',
        'checkbox': 'icon-check-square',
        'radio': 'icon-circle-dot',
        'calendar': 'icon-calendar',
        'ticker': 'icon-gallery-horizontal',
    };
    return iconMap[componentName] || 'icon-box'; // fallback to generic box icon
};

/**
 * Check if a component has nested children
 */
const hasChildren = (component) => {
    if (!component) return false;
    return !!(
        component.components?.length ||
        component.columns?.length ||
        component.tabs?.length ||
        component.slides?.length ||
        component.items?.length
    );
};

/**
 * Generate a component ID from path (matching server-side format)
 */
const generateComponentId = (path) => {
    if (!path || path.length === 0) {
        return 'comp_root';
    }
    return 'comp_' + path.join('_');
};

/**
 * Build tree data structure from YAML structure
 */
export const buildTreeFromStructure = (structure) => {
    if (!Array.isArray(structure) || structure.length === 0) {
        return [];
    }
    return buildTreeNodes(structure, []);
};

/**
 * Recursively build tree nodes from components array
 */
function buildTreeNodes(components, basePath) {
    const nodes = [];
    
    if (!Array.isArray(components)) {
        return nodes;
    }

    components.forEach((component, index) => {
        const currentPath = [...basePath, index];
        const componentId = generateComponentId(currentPath);

        const node = {
            id: componentId,
            name: component.name,
            path: currentPath,
            icon: getComponentIcon(component.name),
            children: [],
            isContainer: hasChildren(component),
            isExpanded: true,
            isVirtual: false
        };

        // Handle direct components array (layout-row, layout-column, page, form)
        if (component.components?.length) {
            node.children.push(...buildTreeNodes(
                component.components,
                [...currentPath, 'components']
            ));
        }

        // Handle columnsgrid columns
        if (component.columns?.length) {
            component.columns.forEach((column, colIndex) => {
                const colPath = [...currentPath, 'columns', colIndex];
                    const colNode = {
                        id: generateComponentId(colPath),
                        name: `Column ${colIndex + 1}`,
                        path: colPath,
                        icon: 'icon-layout-column',
                        children: [],
                        isContainer: true,
                        isExpanded: true,
                        isVirtual: true
                    };

                if (column.components?.length) {
                    colNode.children.push(...buildTreeNodes(
                        column.components,
                        [...colPath, 'components']
                    ));
                }

                node.children.push(colNode);
            });
        }

        // Handle tabs (component.tabs, NOT properties.tabs)
        if (component.tabs?.length) {
            component.tabs.forEach((tab, tabIndex) => {
                const tabPath = [...currentPath, 'tabs', tabIndex];
                    const tabNode = {
                        id: generateComponentId(tabPath),
                        name: tab.title || `Tab ${tabIndex + 1}`,
                        path: tabPath,
                        icon: 'icon-folder-tabs',
                        children: [],
                        isContainer: true,
                        isExpanded: true,
                        isVirtual: true
                    };

                if (tab.components?.length) {
                    tabNode.children.push(...buildTreeNodes(
                        tab.components,
                        [...tabPath, 'components']
                    ));
                }

                node.children.push(tabNode);
            });
        }

        // Handle carousel slides (component.slides, NOT properties.slides)
        if (component.slides?.length) {
            component.slides.forEach((slide, slideIndex) => {
                const slidePath = [...currentPath, 'slides', slideIndex];
                const slideNode = {
                    id: generateComponentId(slidePath),
                    name: `Slide ${slideIndex + 1}`,
                    path: slidePath,
                    icon: 'icon-layers',
                    children: [],
                    isContainer: true,
                    isExpanded: true,
                    isVirtual: true
                };

                if (slide.components?.length) {
                    slideNode.children.push(...buildTreeNodes(
                        slide.components,
                        [...slidePath, 'components']
                    ));
                }

                node.children.push(slideNode);
            });
        }

        // Handle items (accordion items have title + components)
        if (component.items?.length) {
            component.items.forEach((item, itemIndex) => {
                const itemPath = [...currentPath, 'items', itemIndex];
                const itemNode = {
                    id: generateComponentId(itemPath),
                    name: item.title || `Item ${itemIndex + 1}`,
                    path: itemPath,
                    icon: 'icon-chevrons-down-up',
                    children: [],
                    isContainer: false,
                    isExpanded: false,
                    isVirtual: true
                };
                node.children.push(itemNode);
            });
        }

        nodes.push(node);
    });

    return nodes;
}

/**
 * Render tree to DOM
 */
export const renderTree = (treeData, container) => {
    if (!container) return;
    container.innerHTML = '';

    if (!treeData || treeData.length === 0) {
        container.innerHTML = '<p class="tree-empty">No components</p>';
        return;
    }

    treeData.forEach(node => {
        const nodeEl = renderTreeNode(node, 0);
        container.appendChild(nodeEl);
    });
};

/**
 * Render a single tree node
 */
function renderTreeNode(node, depth) {
    const item = document.createElement('div');
    item.className = 'tree-item';
    if (node.isVirtual) item.classList.add('tree-item-virtual');
    item.dataset.componentId = node.id;
    item.dataset.path = JSON.stringify(node.path);

    const content = document.createElement('div');
    content.className = 'tree-item-content';
    content.style.paddingLeft = `${depth * 8 + 8}px`;

    // Toggle arrow for containers
    const toggle = document.createElement('span');
    toggle.className = node.children?.length ? 'tree-toggle' : 'tree-toggle tree-toggle-leaf';
    toggle.textContent = node.children?.length ? (node.isExpanded ? '▼' : '▶') : '';
    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleNode(item, node);
    });

    // Icon
    const icon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    icon.classList.add('tree-icon');
    icon.setAttribute('aria-hidden', 'true');
    icon.setAttribute('width', '16');
    icon.setAttribute('height', '16');
    icon.setAttribute('viewBox', '0 0 24 24'); // Most Lucide icons use this viewBox
    icon.setAttribute('fill', 'none');
    icon.setAttribute('stroke', 'currentColor');
    icon.setAttribute('stroke-width', '2');
    icon.setAttribute('stroke-linecap', 'round');
    icon.setAttribute('stroke-linejoin', 'round');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    // Use modern href attribute instead of deprecated xlink:href
    use.setAttribute('href', `#${node.icon}`);
    icon.appendChild(use);

    // Label
    const label = document.createElement('span');
    label.className = 'tree-label';
    label.textContent = node.name;

    content.appendChild(toggle);
    content.appendChild(icon);
    content.appendChild(label);
    item.appendChild(content);

    // Click to select
    content.addEventListener('click', () => {
        // Will be handled by the main module
        const event = new CustomEvent('tree-item-selected', {
            detail: { componentId: node.id, path: node.path },
            bubbles: true
        });
        item.dispatchEvent(event);
    });

    // Render children
    if (node.children?.length && node.isExpanded) {
        const childContainer = document.createElement('div');
        childContainer.className = 'tree-children';
        node.children.forEach(child => {
            childContainer.appendChild(renderTreeNode(child, depth + 1));
        });
        item.appendChild(childContainer);
    }

    return item;
}

/**
 * Toggle node expand/collapse
 */
function toggleNode(itemEl, node) {
    node.isExpanded = !node.isExpanded;
    const toggle = itemEl.querySelector('.tree-toggle');
    const childContainer = itemEl.querySelector('.tree-children');

    if (node.isExpanded) {
        toggle.textContent = '▼';
        if (!childContainer && node.children?.length) {
            const newContainer = document.createElement('div');
            newContainer.className = 'tree-children';
            node.children.forEach(child => {
                newContainer.appendChild(renderTreeNode(child, 0));
            });
            itemEl.appendChild(newContainer);
        } else if (childContainer) {
            childContainer.style.display = 'block';
        }
    } else {
        toggle.textContent = '▶';
        if (childContainer) {
            childContainer.style.display = 'none';
        }
    }
}

/**
 * Highlight a tree item by component ID
 */
export const highlightTreeItem = (componentId) => {
    // Clear existing selection
    document.querySelectorAll('.tree-item.selected').forEach(el => {
        el.classList.remove('selected');
    });

    if (!componentId) return;

    // Find and highlight the item
    const item = document.querySelector(`.tree-item[data-component-id="${componentId}"]`);
    if (item) {
        item.classList.add('selected');
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
};

/**
 * Clear tree selection
 */
export const clearTreeSelection = () => {
    document.querySelectorAll('.tree-item.selected').forEach(el => {
        el.classList.remove('selected');
    });
};

/**
 * Initialize tree event listeners
 */
export const initComponentTree = (container, onSelect) => {
    if (!container) return;

    container.addEventListener('tree-item-selected', (e) => {
        const { componentId, path } = e.detail;
        if (onSelect) {
            onSelect(componentId, path);
        }
    });
};

