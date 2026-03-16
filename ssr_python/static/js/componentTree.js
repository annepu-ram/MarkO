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

// ============================================================================
// Clipboard State (persists across page switches within session)
// ============================================================================

let _clipboard = null; // { component: {...}, name: 'heading' }

export function getClipboard() { return _clipboard; }
export function setClipboard(data) { _clipboard = data; }
export function clearClipboard() { _clipboard = null; }

/**
 * Map component names to their icon IDs in the SVG sprite
 * Icons must have 'icon-' prefix to match sprite symbol IDs
 * All icons are now available in the sprite after fixing the generation script
 */
const getComponentIcon = (componentName) => {
    const iconMap = {
        'site': 'icon-globe',
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
        'ticker': 'icon-chevrons-left-right-ellipsis',
        'panorama-display': 'icon-panorama-display',
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
 * Build tree data structure from YAML structure.
 * Site wrapper is always expected — tree shows pages directly.
 */
export const buildTreeFromStructure = (structure) => {
    if (!Array.isArray(structure) || structure.length === 0) {
        return [];
    }
    const site = structure[0];

    // Pages
    return buildTreeNodes(site.components || [], [0, 'components']);
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
                    isContainer: true,
                    isExpanded: true,
                    isVirtual: true
                };

                if (item.components?.length) {
                    itemNode.children.push(...buildTreeNodes(
                        item.components,
                        [...itemPath, 'components']
                    ));
                }

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

    treeData.forEach((node, index) => {
        const nodeEl = renderTreeNode(node, 0, treeData.length, index);
        container.appendChild(nodeEl);
    });
};

/**
 * Determine which action buttons should appear for a tree node
 */
function getNodeActions(node, siblingCount, siblingIndex) {
    const isPage = node.name === 'page';
    const isVirtual = node.isVirtual;
    const isContainer = node.isContainer || isPage;
    const hasClipboard = !!_clipboard;

    if (isPage) {
        return { moveUp: false, moveDown: false, copy: false, paste: hasClipboard, addChild: true, addAfter: false, remove: false };
    }

    if (isVirtual) {
        return { moveUp: false, moveDown: false, copy: false, paste: hasClipboard, addChild: true, addAfter: false, remove: false };
    }

    return {
        moveUp: siblingIndex > 0,
        moveDown: siblingIndex < siblingCount - 1,
        copy: true,
        paste: hasClipboard,
        addChild: isContainer,
        addAfter: true,
        remove: true
    };
}

/**
 * Create an SVG icon element for action buttons
 */
function createActionIcon(iconId) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '13');
    svg.setAttribute('height', '13');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'round');
    svg.setAttribute('stroke-linejoin', 'round');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', `#${iconId}`);
    svg.appendChild(use);
    return svg;
}

/**
 * Render a single tree node
 */
function renderTreeNode(node, depth, siblingCount, siblingIndex) {
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
    icon.setAttribute('viewBox', '0 0 24 24');
    icon.setAttribute('fill', 'none');
    icon.setAttribute('stroke', 'currentColor');
    icon.setAttribute('stroke-width', '2');
    icon.setAttribute('stroke-linecap', 'round');
    icon.setAttribute('stroke-linejoin', 'round');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', `#${node.icon}`);
    icon.appendChild(use);

    // Label
    const label = document.createElement('span');
    label.className = 'tree-label';
    label.textContent = node.name;

    content.appendChild(toggle);
    content.appendChild(icon);
    content.appendChild(label);

    // Action buttons (hover-reveal)
    const actions = getNodeActions(node, siblingCount || 1, siblingIndex || 0);
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'tree-actions';

    const nodeData = {
        nodeId: node.id,
        path: node.path,
        name: node.name,
        isVirtual: node.isVirtual,
        isContainer: node.isContainer
    };

    if (actions.moveUp) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'move-up';
        btn.title = 'Move up';
        btn.appendChild(createActionIcon('icon-chevron-up'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'move-up', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.moveDown) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'move-down';
        btn.title = 'Move down';
        btn.appendChild(createActionIcon('icon-chevron-down'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'move-down', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.copy) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'copy';
        btn.title = 'Copy component';
        btn.appendChild(createActionIcon('icon-copy'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'copy', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.paste) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'paste';
        btn.title = _clipboard ? `Paste ${_clipboard.name}` : 'Paste component';
        btn.appendChild(createActionIcon('icon-clipboard-paste'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'paste', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.addChild) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'add-child';
        btn.title = 'Add child component';
        btn.appendChild(createActionIcon('icon-list-plus'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'add-child', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.addAfter) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'add-after';
        btn.title = 'Add component after';
        btn.appendChild(createActionIcon('icon-list-end'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'add-after', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    if (actions.remove) {
        const btn = document.createElement('button');
        btn.className = 'tree-action-btn';
        btn.dataset.action = 'delete';
        btn.title = 'Delete component';
        btn.appendChild(createActionIcon('icon-trash-2'));
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.dispatchEvent(new CustomEvent('tree-action', {
                detail: { action: 'delete', ...nodeData, sourceElement: btn },
                bubbles: true
            }));
        });
        actionsContainer.appendChild(btn);
    }

    content.appendChild(actionsContainer);
    item.appendChild(content);

    // Click to select
    content.addEventListener('click', () => {
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
        node.children.forEach((child, childIndex) => {
            childContainer.appendChild(renderTreeNode(child, depth + 1, node.children.length, childIndex));
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
 * Component type categories for the picker popover
 */
const COMPONENT_CATEGORIES = [
    { label: 'Layout', items: ['layout-row', 'layout-column', 'columnsgrid', 'form'] },
    { label: 'Text', items: ['heading', 'paragraph', 'eyebrow', 'caption', 'blockquote', 'link'] },
    { label: 'Media', items: ['image', 'video', 'gif', 'video-background', 'panorama-display'] },
    { label: 'Interactive', items: ['tabs', 'accordion', 'carousel', 'hamburger', 'ticker'] },
    { label: 'UI', items: ['button', 'titlebar', 'br'] },
    { label: 'Marketing', items: ['icon', 'badge', 'rating', 'progress-bar', 'counter-up', 'countdown'] },
    { label: 'Forms', items: ['textbox', 'textarea', 'dropdown', 'checkbox', 'radio', 'calendar'] }
];

/** Currently open picker element */
let activePicker = null;

/**
 * Show a component type picker as a side panel next to the layers panel.
 * @param {HTMLElement} anchorEl - The button that triggered the picker
 * @param {Function} callback - Called with the selected component name
 */
export function showComponentPicker(anchorEl, callback) {
    // Dismiss any existing picker
    dismissPicker();

    // On mobile, close the properties bottom sheet
    if (window.innerWidth <= 1024 && window.closeRightPanel) {
        window.closeRightPanel();
    }

    const picker = document.createElement('div');
    picker.className = 'tree-component-picker';

    // Header with title and close button
    const header = document.createElement('div');
    header.className = 'tree-picker-header';

    const title = document.createElement('span');
    title.className = 'tree-picker-title';
    title.textContent = 'Add Component';
    header.appendChild(title);

    const closeBtn = document.createElement('button');
    closeBtn.className = 'tree-picker-close';
    closeBtn.type = 'button';
    const closeIcon = createActionIcon('icon-x');
    closeIcon.setAttribute('width', '14');
    closeIcon.setAttribute('height', '14');
    closeBtn.appendChild(closeIcon);
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dismissPicker();
    });
    header.appendChild(closeBtn);

    picker.appendChild(header);

    // Scrollable body with categories
    const body = document.createElement('div');
    body.className = 'tree-picker-body';

    for (const category of COMPONENT_CATEGORIES) {
        const catLabel = document.createElement('div');
        catLabel.className = 'tree-picker-category-label';
        catLabel.textContent = category.label;
        body.appendChild(catLabel);

        for (const compName of category.items) {
            const item = document.createElement('button');
            item.className = 'tree-picker-item';
            item.type = 'button';

            const iconSvg = createActionIcon(getComponentIcon(compName));
            iconSvg.setAttribute('width', '14');
            iconSvg.setAttribute('height', '14');
            item.appendChild(iconSvg);

            const nameSpan = document.createElement('span');
            nameSpan.textContent = compName;
            item.appendChild(nameSpan);

            item.addEventListener('click', (e) => {
                e.stopPropagation();
                dismissPicker();
                callback(compName);
            });

            body.appendChild(item);
        }
    }

    picker.appendChild(body);

    document.body.appendChild(picker);
    activePicker = picker;

    // Dismiss on click-outside or Escape
    const onClickOutside = (e) => {
        if (!picker.contains(e.target) && e.target !== anchorEl) {
            dismissPicker();
        }
    };
    const onEscape = (e) => {
        if (e.key === 'Escape') dismissPicker();
    };

    setTimeout(() => {
        document.addEventListener('click', onClickOutside);
        document.addEventListener('keydown', onEscape);
    }, 0);

    picker._cleanup = () => {
        document.removeEventListener('click', onClickOutside);
        document.removeEventListener('keydown', onEscape);
    };
}

/**
 * Dismiss the currently open picker
 */
function dismissPicker() {
    if (activePicker) {
        if (activePicker._cleanup) activePicker._cleanup();
        activePicker.remove();
        activePicker = null;
    }
}

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

/**
 * Initialize tree action button listeners
 * @param {HTMLElement} container - The component tree container element
 * @param {Function} onAction - Callback: (action, nodeData) => void
 */
export const initTreeActions = (container, onAction) => {
    if (!container) return;

    container.addEventListener('tree-action', (e) => {
        const { action, ...nodeData } = e.detail;
        if (onAction) {
            onAction(action, nodeData);
        }
    });
};

