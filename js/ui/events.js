import { debounce } from '../utils/timing.js';
import { initializeAllComponents } from '../render/index.js';
import { componentInitializers } from '../component_interactions.js';

export function initializeEvents(dom, actions) {
    const {
        editor,
        preview,
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
        initializeAllComponents(componentInitializers);
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

    if (resizer && editor) {
        initializeResizer(resizer, editor);
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
    };

    sidebarResizer.addEventListener('mousedown', startResizing);
}

function initializeResizer(resizer, editor) {
    let initialEditorHeight = 0;
    let initialMouseY = 0;

    const handleMouseMove = event => {
        const deltaY = event.clientY - initialMouseY;
        const newHeight = initialEditorHeight + deltaY;
        if (newHeight > 120) {
            editor.style.height = `${newHeight}px`;
        }
    };

    const handleMouseUp = () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
    };

    resizer.addEventListener('mousedown', event => {
        event.preventDefault();
        initialEditorHeight = editor.clientHeight;
        initialMouseY = event.clientY;
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
    });
}

export { handleEditorKeyDown };
