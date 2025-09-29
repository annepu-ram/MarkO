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

    if (resizer && editor) {
        initializeResizer(resizer, editor);
    }

    if (sidebarResizer && sidebar) {
        initializeSidebarResizer(sidebarResizer, sidebar);
    }

    const propertiesPanel = document.getElementById('propertiesPanel');
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
        if (start !== end) {
            const selectedText = editor.value.substring(start, end);
            const selectedLines = selectedText.split('');
            if (event.shiftKey) {
                const updatedLines = selectedLines.map(line => (line.startsWith('  ') ? line.substring(2) : line));
                const newText = updatedLines.join('');
                editor.value = editor.value.substring(0, start) + newText + editor.value.substring(end);
                editor.selectionStart = start;
                editor.selectionEnd = start + newText.length;
            } else {
                const updatedLines = selectedLines.map(line => '  ' + line);
                const newText = updatedLines.join('');
                editor.value = editor.value.substring(0, start) + newText + editor.value.substring(end);
                editor.selectionStart = start;
                editor.selectionEnd = start + newText.length;
            }
        } else {
            editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + 2;
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

    const minWidth = 150; // Minimum width for the sidebar
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
