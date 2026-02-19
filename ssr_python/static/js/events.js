import { debounce } from './utils/timing.js';

// Track current open panel (left sidebar)
let currentPanel = null;

// Track current open right panel
let currentRightPanel = null;

/**
 * Toggle a sidebar slide-out panel
 * @param {string} panelName - Name of the panel (layers, editor, settings)
 */
export function togglePanel(panelName) {
    const panel = document.getElementById(panelName + 'Panel');
    const btn = document.querySelector(`[data-panel="${panelName}"]`);

    if (!panel || !btn) return;

    // Close current panel if different
    if (currentPanel && currentPanel !== panelName) {
        const currentPanelEl = document.getElementById(currentPanel + 'Panel');
        const currentBtn = document.querySelector(`[data-panel="${currentPanel}"]`);
        if (currentPanelEl) currentPanelEl.classList.remove('open');
        if (currentBtn) currentBtn.classList.remove('active');
    }

    // Toggle clicked panel
    if (currentPanel === panelName) {
        panel.classList.remove('open');
        btn.classList.remove('active');
        currentPanel = null;
    } else {
        panel.classList.add('open');
        btn.classList.add('active');
        currentPanel = panelName;

        // Render panel content when opening
        if (panelName === 'themes' && window.renderThemesPanel) {
            window.renderThemesPanel();
        }
        if (panelName === 'images' && window.renderImagesPanel) {
            window.renderImagesPanel();
        }
    }
}

/**
 * Close the currently open panel
 */
export function closePanel() {
    if (currentPanel) {
        const panel = document.getElementById(currentPanel + 'Panel');
        const btn = document.querySelector(`[data-panel="${currentPanel}"]`);
        if (panel) panel.classList.remove('open');
        if (btn) btn.classList.remove('active');
        currentPanel = null;
    }
}

/**
 * Toggle a right-side slide-in panel
 * @param {string} panelName - Name of the panel (chat, prop)
 */
export function toggleRightPanel(panelName) {
    const panel = document.getElementById(panelName + 'Panel');
    const btn = document.querySelector(`[data-rpanel="${panelName}"]`);
    const sheet = document.getElementById('bottomSheet');

    if (!panel) return;

    // Close current right panel if different
    if (currentRightPanel && currentRightPanel !== panelName) {
        const curPanel = document.getElementById(currentRightPanel + 'Panel');
        const curBtn = document.querySelector(`[data-rpanel="${currentRightPanel}"]`);
        if (curPanel) curPanel.classList.remove('open');
        if (curBtn) curBtn.classList.remove('active');
    }

    // Toggle clicked panel
    if (currentRightPanel === panelName) {
        panel.classList.remove('open');
        if (btn) btn.classList.remove('active');
        if (sheet) sheet.classList.remove('open');
        currentRightPanel = null;
    } else {
        panel.classList.add('open');
        if (btn) btn.classList.add('active');
        if (sheet) sheet.classList.add('open');
        currentRightPanel = panelName;
    }

    // Update bottom sheet tab active states
    document.querySelectorAll('.bottom-sheet-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.rpanel === currentRightPanel);
    });
}

/**
 * Close the currently open right panel
 */
export function closeRightPanel() {
    if (currentRightPanel) {
        const panel = document.getElementById(currentRightPanel + 'Panel');
        const btn = document.querySelector(`[data-rpanel="${currentRightPanel}"]`);
        if (panel) panel.classList.remove('open');
        if (btn) btn.classList.remove('active');
        currentRightPanel = null;
    }
    // Close bottom sheet and clear tab states
    const sheet = document.getElementById('bottomSheet');
    if (sheet) sheet.classList.remove('open');
    document.querySelectorAll('.bottom-sheet-tab').forEach(tab => {
        tab.classList.remove('active');
    });
}

/**
 * Get the currently open right panel name
 */
export function getCurrentRightPanel() {
    return currentRightPanel;
}

/**
 * Set the viewport size (desktop, tablet, mobile)
 * @param {HTMLElement} btn - The clicked button
 * @param {string} size - Size mode (desktop, tablet, mobile)
 */
export function setViewport(btn, size) {
    document.querySelectorAll('.viewport-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const deviceFrame = document.getElementById('deviceFrame');
    if (deviceFrame) {
        deviceFrame.className = 'device-frame ' + size;
    }
}

/**
 * Toggle mobile sidebar and swap menu/close icon
 */
export function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('mobileMenuBtn');

    if (sidebar) {
        sidebar.classList.toggle('open');
    }

    const isOpen = sidebar?.classList.contains('open');

    // When closing sidebar, also close bottom sheet / right panel
    if (!isOpen) {
        closeRightPanel();
    }

    // Swap icon between menu and X
    if (menuBtn) {
        const useEl = menuBtn.querySelector('use');
        if (useEl) {
            useEl.setAttribute('href', isOpen ? '#icon-x' : '#icon-menu');
        }
    }
}

/**
 * Close mobile sidebar
 */
export function closeMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('mobileMenuBtn');

    if (sidebar) sidebar.classList.remove('open');

    // Reset icon to menu
    if (menuBtn) {
        const useEl = menuBtn.querySelector('use');
        if (useEl) useEl.setAttribute('href', '#icon-menu');
    }
}

// Make functions available globally for onclick handlers
window.togglePanel = togglePanel;
window.closePanel = closePanel;
window.toggleRightPanel = toggleRightPanel;
window.closeRightPanel = closeRightPanel;
window.getCurrentRightPanel = getCurrentRightPanel;
window.setViewport = setViewport;
window.toggleMobileSidebar = toggleMobileSidebar;
window.closeMobileSidebar = closeMobileSidebar;

export function initializeEvents(dom, actions) {
    const {
        editor,
        editorWrapper,
        preview,
        undoButton,
        redoButton,
        exportButton,
        clearButton,
        fullscreenButton,
        closeFullscreenButton,
        helpButton,
        componentButtons,
        resizer,
        sidebar,
        sidebarResizer,
        sidebarNavItems,
        sidebarPanels,
        propertiesPanel,
    } = dom;

    if (editor) {
        const debouncedParse = debounce(value => actions.handleEditorInput(value), 500);
        editor.addEventListener('input', () => {
            debouncedParse(editor.value);
        });
        editor.addEventListener('keydown', event => handleEditorKeyDown(event, editor, actions));
    }

    if (preview) {
        preview.addEventListener('click', actions.handlePreviewClick);
    }

    if (exportButton) {
        exportButton.addEventListener('click', actions.exportCode);
    }

    if (clearButton) {
        clearButton.addEventListener('click', actions.clearCanvas);
    }

    if (fullscreenButton) {
        fullscreenButton.addEventListener('click', actions.openFullscreen);
    }

    if (closeFullscreenButton) {
        closeFullscreenButton.addEventListener('click', actions.closeFullscreen);
    }

    if (undoButton) {
        undoButton.addEventListener('click', actions.undo);
    }

    if (redoButton) {
        redoButton.addEventListener('click', actions.redo);
    }

    // Escape key closes fullscreen modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            actions.closeFullscreen();
        }
    });

    if (helpButton) {
        helpButton.addEventListener('click', actions.toggleHelpPanel);
    }

    if (Array.isArray(componentButtons)) {
        componentButtons.forEach(button => {
            button.addEventListener('click', () => {
                const componentName = button.dataset.component;
                if (componentName) {
                    actions.insertComponent(componentName);
                }
            });
        });
    }

    // Setup viewport button handlers
    const viewportBtns = document.querySelectorAll('.viewport-btn[data-viewport]');
    viewportBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const size = btn.dataset.viewport;
            if (size) {
                setViewport(btn, size);
            }
        });
    });

    // Setup sidebar button click handlers (left panels)
    const sidebarBtns = document.querySelectorAll('.sidebar-btn[data-panel]');
    sidebarBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const panelName = btn.dataset.panel;
            if (panelName) {
                togglePanel(panelName);
            }
        });
    });

    // Setup command bar button click handlers (right panels)
    const commandBtns = document.querySelectorAll('.command-btn[data-rpanel]');
    commandBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const panelName = btn.dataset.rpanel;
            if (panelName) {
                toggleRightPanel(panelName);
            }
        });
    });

    // Setup panel close button handlers
    const closeBtns = document.querySelectorAll('.panel-close');
    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            closePanel();
        });
    });

    // Legacy sidebar nav items (for backwards compatibility)
    if (Array.isArray(sidebarNavItems) && sidebarNavItems.length > 0 && Array.isArray(sidebarPanels) && sidebarPanels.length > 0) {
        const activateNavItem = targetId => {
            sidebarNavItems.forEach(navItem => {
                const isActive = navItem.dataset.target === targetId;
                navItem.classList.toggle('active', isActive);
                navItem.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });

            sidebarPanels.forEach(panel => {
                const isActive = panel.id === targetId;
                panel.classList.toggle('active', isActive);
                panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
            });
        };

        sidebarNavItems.forEach(navItem => {
            navItem.addEventListener('click', () => {
                const targetId = navItem.dataset.target;
                if (targetId) {
                    activateNavItem(targetId);
                }
            });
        });
    }

    if (resizer && editorWrapper) {
        initializeResizer(resizer, editorWrapper);
    }

    if (sidebarResizer && sidebar) {
        initializeSidebarResizer(sidebarResizer, sidebar);
    }

    if (propertiesPanel) {
        propertiesPanel.addEventListener('click', event => {
            if (event.target.classList.contains('properties-apply-button')) {
                actions.applySelectedComponentProperties();
            }
        });
    }

    // Mobile menu button
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleMobileSidebar);
    }

    // Bottom sheet tab buttons (mobile)
    const sheetTabs = document.querySelectorAll('.bottom-sheet-tab[data-rpanel]');
    sheetTabs.forEach(btn => {
        btn.addEventListener('click', () => {
            const panelName = btn.dataset.rpanel;
            if (panelName) {
                toggleRightPanel(panelName);
            }
        });
    });
}

function handleEditorKeyDown(event, editor, actions) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;

    if (event.key === 'Tab') {
        event.preventDefault();
        const value = editor.value;
        const indent = '  ';
        const hasSelection = start !== end;
        const blockStart = value.lastIndexOf('\n', Math.max(start - 1, 0)) + 1;
        const lastAffectedIndex = Math.max((hasSelection ? end - 1 : start), blockStart);
        const nextNewline = value.indexOf('\n', lastAffectedIndex);
        const blockEnd = nextNewline === -1 ? value.length : nextNewline;
        const before = value.slice(0, blockStart);
        const block = value.slice(blockStart, blockEnd);
        const after = value.slice(blockEnd);

        if (event.shiftKey) {
            const lines = block.split('\n');
            let removedFromFirstLine = 0;
            let totalRemoved = 0;
            const adjustedLines = lines.map((line, index) => {
                const leadingSpaces = (line.match(/^ */) || [''])[0].length;
                const removeCount = Math.min(indent.length, leadingSpaces);
                if (removeCount > 0) {
                    if (index === 0) {
                        removedFromFirstLine = removeCount;
                    }
                    totalRemoved += removeCount;
                    return line.slice(removeCount);
                }
                return line;
            });
            const updatedBlock = adjustedLines.join('\n');

            if (updatedBlock !== block) {
                editor.value = before + updatedBlock + after;
                const newStart = Math.max(blockStart, start - removedFromFirstLine);
                const newEnd = Math.max(newStart, end - totalRemoved);
                editor.selectionStart = newStart;
                editor.selectionEnd = newEnd;
                editor.dispatchEvent(new Event('input', { bubbles: true }));
            }
        } else {
            const lines = block.split('\n');
            const updatedLines = lines.map(line => indent + line);
            const updatedBlock = updatedLines.join('\n');
            editor.value = before + updatedBlock + after;
            const linesAffected = lines.length;
            const newStart = start + indent.length;
            const newEnd = end + indent.length * linesAffected;
            editor.selectionStart = newStart;
            editor.selectionEnd = newEnd;
            editor.dispatchEvent(new Event('input', { bubbles: true }));
        }
        return;
    }

    if (event.ctrlKey && (event.key === 'z' || event.key === 'Z')) {
        event.preventDefault();
        actions.undo();
        return;
    }

    if (event.ctrlKey && (event.key === 'y' || event.key === 'Y')) {
        event.preventDefault();
        actions.redo();
    }
}

/**
 * @function initializeSidebarResizer
 * @description Initializes the functionality for resizing the left sidebar horizontally.
 * @param {HTMLElement} sidebarResizer - The draggable resizer element.
 * @param {HTMLElement} sidebar - The sidebar element to be resized.
 * @calledBy {initializeEvents}
 * @calls {localStorage.setItem|localStorage.getItem}
 */
function initializeSidebarResizer(sidebarResizer, sidebar) {
    let isResizing = false;
    let initialX;
    let initialWidth;

    const minWidth = 250; // Minimum width for the sidebar
    const maxWidth = 500;  // Maximum width for the sidebar

    const appContainer = document.getElementById('appContainer');

    const storedWidth = localStorage.getItem('sidebarWidth');
    if (storedWidth) {
        appContainer.style.setProperty('--sidebar-width', `${storedWidth}px`);
    }

    const startResizing = (e) => {
        isResizing = true;
        initialX = e.clientX;
        initialWidth = sidebar.offsetWidth;
        document.addEventListener('mousemove', resize);
        document.addEventListener('mouseup', stopResizing);
        document.body.style.cursor = 'ew-resize'; // Change cursor globally
        sidebar.style.userSelect = 'none'; // Prevent text selection during resize
        sidebar.style.pointerEvents = 'none'; // Prevent interaction with sidebar content

        // Block iframe pointer events to prevent mouse getting trapped during resize
        const iframe = document.getElementById('preview-frame');
        if (iframe) iframe.style.pointerEvents = 'none';
    };

    const resize = (e) => {
        if (!isResizing) return;
        const dx = e.clientX - initialX;
        let newWidth = initialWidth + dx;

        if (newWidth < minWidth) {
            newWidth = minWidth;
        } else if (newWidth > maxWidth) {
            newWidth = maxWidth;
        }

        appContainer.style.setProperty('--sidebar-width', `${newWidth}px`);
    };

    const stopResizing = () => {
        isResizing = false;
        document.removeEventListener('mousemove', resize);
        document.removeEventListener('mouseup', stopResizing);
        document.body.style.cursor = ''; // Reset cursor
        sidebar.style.userSelect = ''; // Restore user select
        sidebar.style.pointerEvents = ''; // Restore pointer events
        localStorage.setItem('sidebarWidth', sidebar.offsetWidth);

        // Restore iframe pointer events
        const iframe = document.getElementById('preview-frame');
        if (iframe) iframe.style.pointerEvents = '';
    };

    sidebarResizer.addEventListener('mousedown', startResizing);
}

function initializeResizer(resizer, editorWrapper) {
    let initialEditorHeight = 0;
    let initialMouseY = 0;

    const handleMouseMove = event => {
        const deltaY = event.clientY - initialMouseY;
        const newHeight = initialEditorHeight + deltaY;
        if (newHeight > 120) {
            editorWrapper.style.height = `${newHeight}px`;
        }
    };

    const handleMouseUp = () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);

        // Restore iframe pointer events
        const iframe = document.getElementById('preview-frame');
        if (iframe) iframe.style.pointerEvents = '';
    };

    resizer.addEventListener('mousedown', event => {
        event.preventDefault();
        initialEditorHeight = editorWrapper.clientHeight;
        initialMouseY = event.clientY;
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);

        // Block iframe pointer events during resize
        const iframe = document.getElementById('preview-frame');
        if (iframe) iframe.style.pointerEvents = 'none';
    });
}

export { handleEditorKeyDown };
