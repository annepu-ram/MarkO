/** @jest-environment jsdom */

import { handleEditorKeyDown } from '../events.js';

describe('handleEditorKeyDown tab behavior', () => {
    const createEditor = (value, selectionStart, selectionEnd) => {
        const editor = document.createElement('textarea');
        editor.value = value;
        editor.selectionStart = selectionStart;
        editor.selectionEnd = selectionEnd;
        return editor;
    };

    const triggerTab = (editor, { shiftKey = false } = {}) => {
        const preventDefault = jest.fn();
        const event = {
            key: 'Tab',
            shiftKey,
            preventDefault,
        };
        const actions = {};
        let inputEventCount = 0;
        editor.addEventListener('input', () => {
            inputEventCount += 1;
        });
        handleEditorKeyDown(event, editor, actions);
        return { preventDefault, inputEventCount };
    };

    test('adds two leading spaces to every selected line when Tab is pressed', () => {
        const initialValue = 'first\nsecond\nthird';
        const editor = createEditor(initialValue, 0, initialValue.length);

        const { preventDefault, inputEventCount } = triggerTab(editor);

        expect(editor.value).toBe('  first\n  second\n  third');
        expect(editor.selectionStart).toBe(2);
        expect(editor.selectionEnd).toBe(editor.value.length);
        expect(preventDefault).toHaveBeenCalledTimes(1);
        expect(inputEventCount).toBe(1);
    });

    test('removes up to two leading spaces from every selected line when Shift+Tab is pressed', () => {
        const initialValue = '  alpha\n    beta\n  gamma';
        const editor = createEditor(initialValue, 0, initialValue.length);

        const { preventDefault, inputEventCount } = triggerTab(editor, { shiftKey: true });

        expect(editor.value).toBe('alpha\n  beta\ngamma');
        expect(editor.selectionStart).toBe(0);
        expect(editor.selectionEnd).toBe(editor.value.length);
        expect(preventDefault).toHaveBeenCalledTimes(1);
        expect(inputEventCount).toBe(1);
    });
});
