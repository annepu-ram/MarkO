// YAML Editor Persistence using sessionStorage (tab-scoped)
// Survives tab refresh but NOT browser/tab close

const STORAGE_KEY = 'swift_sites_yaml_content';
const HISTORY_KEY = 'swift_sites_yaml_history';

export const yamlStorage = {
    // Save YAML content to sessionStorage
    save(yamlContent) {
        try {
            sessionStorage.setItem(STORAGE_KEY, yamlContent);
            return true;
        } catch (e) {
            console.warn('[YamlStorage] Failed to save:', e);
            return false;
        }
    },

    // Load YAML content from sessionStorage
    load() {
        try {
            return sessionStorage.getItem(STORAGE_KEY) || '';
        } catch (e) {
            console.warn('[YamlStorage] Failed to load:', e);
            return '';
        }
    },

    // Clear stored YAML (for "New" action)
    clear() {
        try {
            sessionStorage.removeItem(STORAGE_KEY);
            sessionStorage.removeItem(HISTORY_KEY);
            return true;
        } catch (e) {
            console.warn('[YamlStorage] Failed to clear:', e);
            return false;
        }
    },

    // Check if storage has content
    hasContent() {
        return !!sessionStorage.getItem(STORAGE_KEY);
    },

    // Save history state (for undo/redo persistence)
    saveHistory(undoStack, redoStack) {
        try {
            const historyData = JSON.stringify({ undoStack, redoStack });
            sessionStorage.setItem(HISTORY_KEY, historyData);
            return true;
        } catch (e) {
            console.warn('[YamlStorage] Failed to save history:', e);
            return false;
        }
    },

    // Load history state
    loadHistory() {
        try {
            const historyData = sessionStorage.getItem(HISTORY_KEY);
            if (historyData) {
                return JSON.parse(historyData);
            }
            return { undoStack: [], redoStack: [] };
        } catch (e) {
            console.warn('[YamlStorage] Failed to load history:', e);
            return { undoStack: [], redoStack: [] };
        }
    }
};
