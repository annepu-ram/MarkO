/**
 * Creates an HTML element with the given tag, class, and text content.
 * @param {string} tag The HTML tag.
 * @param {string} className The CSS class name.
 * @param {string} textContent The text content.
 * @returns {HTMLElement} The created element.
 */
const createElement = (tag, className, textContent) => {
    const el = document.createElement(tag);
    if (className) {
        el.className = className;
    }
    if (textContent !== undefined) {
        el.textContent = textContent;
    }
    return el;
};

/**
 * Creates an input element.
 * @param {object} options The options for the input.
 * @returns {HTMLInputElement} The created input element.
 */
const createInput = ({ type = 'text', value = '', placeholder = '', dataset = {} }) => {
    const input = document.createElement('input');
    input.type = type;
    input.value = value ?? '';
    if (placeholder) {
        input.placeholder = placeholder;
    }
    Object.entries(dataset).forEach(([key, dataValue]) => {
        input.dataset[key] = dataValue;
    });
    return input;
};

/**
 * Creates a textarea element.
 * @param {object} options The options for the textarea.
 * @returns {HTMLTextAreaElement} The created textarea element.
 */
const createTextarea = ({ value = '', placeholder = '', rows = 3, dataset = {} }) => {
    const textarea = document.createElement('textarea');
    textarea.value = value ?? '';
    textarea.rows = rows;
    if (placeholder) {
        textarea.placeholder = placeholder;
    }
    Object.entries(dataset).forEach(([key, dataValue]) => {
        textarea.dataset[key] = dataValue;
    });
    return textarea;
};

/**
 * Creates an icon button element.
 * @param {object} options The options for the button.
 * @returns {HTMLButtonElement} The created button element.
 */
const createIconButton = ({ label, onClick, dataset = {}, className = 'btn btn-icon' }) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = className;
    button.textContent = label;
    Object.entries(dataset).forEach(([key, dataValue]) => {
        button.dataset[key] = dataValue;
    });
    button.addEventListener('click', onClick);
    return button;
};

/**
 * Renders a custom editor for a list of links.
 * @param {object} options The options for the editor.
 * @returns {{element: HTMLElement, serialize: function}} The editor element and a function to serialize its value.
 */
const renderLinksEditor = ({ value = [] } = {}) => {
    const container = createElement('div', 'custom-editor links-editor');
    const list = createElement('div', 'links-editor-list');
    container.appendChild(list);

    const addRow = (link = { label: '', href: '' }) => {
        const row = createElement('div', 'links-editor-row');
        const labelInput = createInput({ type: 'text', value: link.label || '', placeholder: 'Label', dataset: { field: 'label' } });
        const hrefInput = createInput({ type: 'text', value: link.href || '', placeholder: 'URL', dataset: { field: 'href' } });
        const removeButton = createIconButton({
            label: 'Remove',
            onClick: () => {
                row.remove();
            },
            className: 'btn btn-small btn-danger'
        });
        row.appendChild(labelInput);
        row.appendChild(hrefInput);
        row.appendChild(removeButton);
        list.appendChild(row);
    };

    (value || []).forEach(link => addRow(link));
    if (list.children.length === 0) {
        addRow();
    }

    const addButton = createIconButton({
        label: 'Add Link',
        onClick: () => addRow(),
        className: 'btn btn-small btn-secondary'
    });
    container.appendChild(addButton);

    return {
        element: container,
        serialize: () => Array.from(list.children).map(row => {
            const label = row.querySelector('[data-field="label"]').value.trim();
            const href = row.querySelector('[data-field="href"]').value.trim();
            return { label, href };
        }).filter(link => link.label || link.href),
    };
};

/**
 * Renders a custom editor for a simple list.
 * @param {object} options The options for the editor.
 * @returns {{element: HTMLElement, serialize: function}} The editor element and a function to serialize its value.
 */
const renderSimpleListEditor = ({
    value = [],
    fields,
    addLabel,
    placeholders = {},
    textareaFields = {},
}) => {
    const container = createElement('div', 'custom-editor list-editor');
    const list = createElement('div', 'list-editor-items');
    container.appendChild(list);

    const addRow = (item = {}) => {
        const row = createElement('div', 'list-editor-row');
        fields.forEach(fieldName => {
            const fieldValue = item[fieldName] ?? '';
            const placeholder = placeholders[fieldName] || '';
            if (textareaFields[fieldName]) {
                const textarea = createTextarea({
                    value: fieldValue,
                    placeholder,
                    rows: textareaFields[fieldName],
                    dataset: { field: fieldName },
                });
                row.appendChild(textarea);
            } else {
                const input = createInput({
                    type: 'text',
                    value: fieldValue,
                    placeholder,
                    dataset: { field: fieldName },
                });
                row.appendChild(input);
            }
        });
        const removeButton = createIconButton({
            label: 'Remove',
            onClick: () => row.remove(),
            className: 'btn btn-small btn-danger'
        });
        row.appendChild(removeButton);
        list.appendChild(row);
    };

    (value || []).forEach(item => addRow(item));
    if (list.children.length === 0) {
        addRow();
    }

    const addButton = createIconButton({
        label: addLabel,
        onClick: () => addRow(),
        className: 'btn btn-small btn-secondary'
    });
    container.appendChild(addButton);

    return {
        element: container,
        serialize: () => Array.from(list.children).map(row => {
            const output = {};
            fields.forEach(fieldName => {
                const fieldEl = row.querySelector(`[data-field="${fieldName}"]`);
                if (fieldEl) {
                    output[fieldName] = fieldEl.value.trim();
                }
            });
            return output;
        }).filter(item => Object.values(item).some(value => value !== '')),
    };
};

/**
 * Renders a custom editor for accordion items.
 * @param {object} options The options for the editor.
 * @returns {{element: HTMLElement, serialize: function}} The editor element and a function to serialize its value.
 */
const renderAccordionItems = ({ value = [] } = {}) => renderSimpleListEditor({
    value,
    fields: ['title', 'content'],
    addLabel: 'Add Item',
    placeholders: { title: 'Item title', content: 'Item content' },
    textareaFields: { content: 4 },
});

/**
 * Renders an advanced editor for tabs (titles only, components edited in YAML).
 * @param {object} options The options for the editor.
 * @returns {{element: HTMLElement, serialize: function}} The editor element and a function to serialize its value.
 */
const renderTabsEditor = ({ value = [] } = {}) => {
    const container = createElement('div', 'custom-editor tabs-editor');
    const list = createElement('div', 'tabs-editor-list');
    container.appendChild(list);

    const addRow = (tab = { title: '', components: [] }, index = -1) => {
        const row = createElement('div', 'tabs-editor-row');
        row.style.cssText = 'display: flex; gap: 0.8rem; align-items: center; margin-bottom: 0.8rem;';

        const titleInput = createInput({
            type: 'text',
            value: tab.title || '',
            placeholder: 'Tab title',
            dataset: { field: 'title' }
        });
        titleInput.style.cssText = 'flex: 1;';

        const componentCount = createElement('span', 'component-count',
            `${(tab.components || []).length} component${(tab.components || []).length !== 1 ? 's' : ''}`);
        componentCount.style.cssText = 'color: #6b7280; font-size: 1.4rem; white-space: nowrap;';

        const removeButton = createElement('button', 'btn btn-small', '×');
        removeButton.type = 'button';
        removeButton.title = 'Remove tab';
        removeButton.style.cssText = 'color: #dc2626; padding: 0.4rem 0.8rem;';
        removeButton.onclick = () => row.remove();

        row.appendChild(titleInput);
        row.appendChild(componentCount);
        row.appendChild(removeButton);

        // Store original components array
        row.dataset.components = JSON.stringify(tab.components || []);

        if (index >= 0 && index < list.children.length) {
            list.insertBefore(row, list.children[index]);
        } else {
            list.appendChild(row);
        }
    };

    // Initialize with existing tabs
    (value || []).forEach(tab => addRow(tab));
    if (list.children.length === 0) {
        addRow();
    }

    const addButton = createElement('button', 'btn btn-small btn-secondary', '+ Add Tab');
    addButton.type = 'button';
    addButton.onclick = () => addRow();
    addButton.style.cssText = 'margin-top: 0.8rem;';
    container.appendChild(addButton);

    const notice = createElement('p', 'helper-text',
        'Note: Edit components within each tab directly in YAML.');
    notice.style.cssText = 'margin-top: 1.2rem; color: #6b7280; font-size: 1.3rem; font-style: italic;';
    container.appendChild(notice);

    return {
        element: container,
        serialize: () => Array.from(list.children).map(row => {
            const title = row.querySelector('[data-field="title"]').value.trim();
            const components = JSON.parse(row.dataset.components || '[]');
            return { title, components };
        }),
    };
};

/**
 * Renders a placeholder for the carousel slides editor.
 * @param {object} options The options for the editor.
 * @returns {{element: HTMLElement, serialize: function}} The editor element and a function to serialize its value.
 */
const renderCarouselSlides = ({ value = [] } = {}) => {
    const container = createElement('div', 'custom-editor carousel-placeholder');
    const notice = createElement('p', 'helper-text', 'Slide editing is not yet available in the properties panel. Update slides directly in YAML.');
    container.appendChild(notice);
    const count = createElement('p', 'helper-text-muted', `Slides: ${Array.isArray(value) ? value.length : 0}`);
    container.appendChild(count);
    return {
        element: container,
        serialize: () => value,
    };
};

export const customRenderers = {
    linksEditor: {
        render: renderLinksEditor,
    },
    accordionItems: {
        render: renderAccordionItems,
    },
    tabsEditor: {
        render: renderTabsEditor,
    },
    carouselSlides: {
        render: renderCarouselSlides,
    },
};