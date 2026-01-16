/**
 * @description Manages undo/redo history for YAML editor content.
 * Maintains two stacks: undoStack for previous states and redoStack for undone states.
 */

class HistoryManager {
    constructor(maxSize = 50) {
        this.undoStack = [];
        this.redoStack = [];
        this.maxSize = maxSize;
    }

    /**
     * Push a new state onto the history stack
     * @param {string} yamlContent - The YAML content to save
     */
    push(yamlContent) {
        // Don't push if it's the same as the last state
        if (this.undoStack.length > 0 && this.undoStack[this.undoStack.length - 1] === yamlContent) {
            return;
        }

        // Limit stack size
        if (this.undoStack.length >= this.maxSize) {
            this.undoStack.shift();
        }

        this.undoStack.push(yamlContent);
        // Clear redo stack whenever a new state is pushed
        this.redoStack = [];
    }

    /**
     * Check if undo is possible
     * @returns {boolean}
     */
    canUndo() {
        return this.undoStack.length > 1;
    }

    /**
     * Check if redo is possible
     * @returns {boolean}
     */
    canRedo() {
        return this.redoStack.length > 0;
    }

    /**
     * Undo to the previous state
     * @returns {string|null} The previous YAML content, or null if undo is not possible
     */
    undo() {
        if (this.undoStack.length > 1) {
            const currentState = this.undoStack.pop();
            this.redoStack.push(currentState);
            return this.undoStack[this.undoStack.length - 1];
        }
        return null;
    }

    /**
     * Redo to the next state
     * @returns {string|null} The next YAML content, or null if redo is not possible
     */
    redo() {
        if (this.redoStack.length > 0) {
            const nextState = this.redoStack.pop();
            this.undoStack.push(nextState);
            return nextState;
        }
        return null;
    }

    /**
     * Clear all history
     */
    clear() {
        this.undoStack = [];
        this.redoStack = [];
    }

    /**
     * Get the current state count (for debugging)
     */
    getStateCount() {
        return {
            undoCount: this.undoStack.length,
            redoCount: this.redoStack.length
        };
    }
}

export const historyManager = new HistoryManager();

