import { loadMetadata } from './templates.js';
import { markMetadataLoaded, setSelection } from './state.js';
import { createActions } from '../ui/actions.js';
import { initializeEvents } from '../ui/events.js';

/**
 * @function getDomReferences
 * @description Gathers references to key DOM elements used throughout the application.
 * @returns {object} An object containing references to various DOM elements.
 * @calledBy {initializeApp}
 * @calls {document.getElementById|document.querySelectorAll}
 */
function getDomReferences() {
    const appContainer = document.getElementById('appContainer');
    return {
        appContainer,
        editor: document.getElementById('codeEditor'),
        preview: document.getElementById('preview'),
        propertiesPanel: document.getElementById('propertiesPanel'),
        propertiesContent: document.getElementById('propertiesContent'),
        fullscreenModal: document.getElementById('fullscreenModal'),
        fullscreenContent: document.getElementById('fullscreenContent'),
        helpPanel: document.getElementById('helpPanel'),
        exportButton: document.getElementById('exportBtn'),
        clearButton: document.getElementById('clearBtn'),
        fullscreenButton: document.getElementById('fullscreenBtn'),
        closeFullscreenButton: document.getElementById('closeFullscreenBtn'),
        helpButton: document.getElementById('helpBtn'),
        componentButtons: Array.from(document.querySelectorAll('.component-item')),
        resizer: document.getElementById('resizer'),
        sidebar: document.querySelector('.sidebar'),
        sidebarResizer: document.getElementById('sidebarResizer'),
    };
}

/**
 * @function initializeApp
 * @description Initializes the entire application, setting up DOM references, actions, event listeners, and loading metadata.
 * @returns {Promise<void>}
 * @calledBy {js/script.js}
 * @calls {getDomReferences|createActions|initializeEvents|loadMetadata|markMetadataLoaded|setSelection|actions.parseAndRender}
 */
export async function initializeApp() {
    const dom = getDomReferences();
    const actions = createActions(dom);

    initializeEvents(dom, actions);

    try {
        await loadMetadata();
        markMetadataLoaded();
    } catch (error) {
        console.error('Failed to load component metadata:', error);
    }

    const initialValue = dom.editor ? dom.editor.value : '';
    actions.parseAndRender(initialValue || '', { pushHistory: true });
    setSelection();
}
