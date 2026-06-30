let activePrompt = null;

function ensurePromptStyles() {
    if (document.getElementById('appPromptModalStyles')) return;
    const style = document.createElement('style');
    style.id = 'appPromptModalStyles';
    style.textContent = `
        .app-prompt-overlay {
            position: fixed;
            inset: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background: rgba(15, 23, 42, 0.48);
        }
        .app-prompt-modal {
            width: min(460px, 100%);
            border: 1px solid rgba(148, 163, 184, 0.32);
            border-radius: 12px;
            background: #ffffff;
            color: #111827;
            box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
            padding: 18px;
        }
        .app-prompt-title {
            margin: 0 0 8px;
            font-size: 16px;
            font-weight: 700;
        }
        .app-prompt-message {
            margin: 0 0 12px;
            color: #64748b;
            font-size: 13px;
            line-height: 1.45;
        }
        .app-prompt-input {
            width: 100%;
            min-height: 40px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 9px 10px;
            font: inherit;
            color: inherit;
            background: #ffffff;
            box-sizing: border-box;
        }
        textarea.app-prompt-input {
            min-height: 96px;
            resize: vertical;
        }
        .app-prompt-error {
            display: none;
            margin: 8px 0 0;
            color: #dc2626;
            font-size: 13px;
        }
        .app-prompt-actions {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 16px;
        }
        .app-prompt-button {
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            background: #ffffff;
            color: #334155;
            padding: 8px 12px;
            font: inherit;
            cursor: pointer;
        }
        .app-prompt-button-primary {
            border-color: #2563eb;
            background: #2563eb;
            color: #ffffff;
        }
        .app-prompt-button-danger {
            border-color: #dc2626;
            background: #dc2626;
            color: #ffffff;
        }
        .app-prompt-button:focus,
        .app-prompt-input:focus {
            outline: 2px solid rgba(37, 99, 235, 0.35);
            outline-offset: 2px;
        }
    `;
    document.head.appendChild(style);
}

export function showTextPrompt({
    title = 'Enter value',
    message = '',
    value = '',
    placeholder = '',
    confirmText = 'Save',
    cancelText = 'Cancel',
    multiline = false,
    required = true,
} = {}) {
    ensurePromptStyles();
    if (activePrompt) activePrompt.remove();

    return new Promise(resolve => {
        const overlay = document.createElement('div');
        overlay.className = 'app-prompt-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');

        const modal = document.createElement('div');
        modal.className = 'app-prompt-modal';

        const heading = document.createElement('h2');
        heading.className = 'app-prompt-title';
        heading.textContent = title;

        const description = document.createElement('p');
        description.className = 'app-prompt-message';
        description.textContent = message;

        const input = document.createElement(multiline ? 'textarea' : 'input');
        input.className = 'app-prompt-input';
        if (!multiline) input.type = 'text';
        input.value = value;
        input.placeholder = placeholder;

        const error = document.createElement('p');
        error.className = 'app-prompt-error';
        error.textContent = 'This field is required.';

        const actions = document.createElement('div');
        actions.className = 'app-prompt-actions';

        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.className = 'app-prompt-button';
        cancel.textContent = cancelText;

        const confirm = document.createElement('button');
        confirm.type = 'button';
        confirm.className = 'app-prompt-button app-prompt-button-primary';
        confirm.textContent = confirmText;

        actions.append(cancel, confirm);
        modal.append(heading);
        if (message) modal.append(description);
        modal.append(input, error, actions);
        overlay.append(modal);
        document.body.appendChild(overlay);
        activePrompt = overlay;

        const close = result => {
            overlay.remove();
            if (activePrompt === overlay) activePrompt = null;
            resolve(result);
        };

        const submit = () => {
            const result = input.value.trim();
            if (required && !result) {
                error.style.display = 'block';
                input.focus();
                return;
            }
            close(result);
        };

        cancel.addEventListener('click', () => close(null));
        confirm.addEventListener('click', submit);
        overlay.addEventListener('click', event => {
            if (event.target === overlay) close(null);
        });
        input.addEventListener('input', () => {
            error.style.display = 'none';
        });
        input.addEventListener('keydown', event => {
            if (event.key === 'Escape') {
                event.preventDefault();
                close(null);
            }
            if (event.key === 'Enter' && (!multiline || event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                submit();
            }
        });

        requestAnimationFrame(() => {
            input.focus();
            input.select();
        });
    });
}

function showDialogModal({
    title = 'Confirm',
    message = '',
    confirmText = 'OK',
    cancelText = 'Cancel',
    showCancel = true,
    danger = false,
} = {}) {
    ensurePromptStyles();
    if (activePrompt) activePrompt.remove();

    return new Promise(resolve => {
        const overlay = document.createElement('div');
        overlay.className = 'app-prompt-overlay';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');

        const modal = document.createElement('div');
        modal.className = 'app-prompt-modal';

        const heading = document.createElement('h2');
        heading.className = 'app-prompt-title';
        heading.textContent = title;

        const description = document.createElement('p');
        description.className = 'app-prompt-message';
        description.textContent = message;

        const actions = document.createElement('div');
        actions.className = 'app-prompt-actions';

        const close = result => {
            overlay.remove();
            if (activePrompt === overlay) activePrompt = null;
            resolve(result);
        };

        if (showCancel) {
            const cancel = document.createElement('button');
            cancel.type = 'button';
            cancel.className = 'app-prompt-button';
            cancel.textContent = cancelText;
            cancel.addEventListener('click', () => close(false));
            actions.append(cancel);
        }

        const confirm = document.createElement('button');
        confirm.type = 'button';
        confirm.className = `app-prompt-button ${danger ? 'app-prompt-button-danger' : 'app-prompt-button-primary'}`;
        confirm.textContent = confirmText;
        confirm.addEventListener('click', () => close(true));
        actions.append(confirm);

        modal.append(heading);
        if (message) modal.append(description);
        modal.append(actions);
        overlay.append(modal);
        document.body.appendChild(overlay);
        activePrompt = overlay;

        overlay.addEventListener('click', event => {
            if (event.target === overlay) close(false);
        });
        overlay.addEventListener('keydown', event => {
            if (event.key === 'Escape') {
                event.preventDefault();
                close(false);
            }
            if (event.key === 'Enter') {
                event.preventDefault();
                close(true);
            }
        });

        requestAnimationFrame(() => {
            confirm.focus();
        });
    });
}

export function showConfirmModal(options = {}) {
    return showDialogModal({
        title: 'Confirm action',
        confirmText: 'Confirm',
        ...options,
        showCancel: true,
    });
}

export function showMessageModal(options = {}) {
    return showDialogModal({
        title: 'Notice',
        confirmText: 'OK',
        ...options,
        showCancel: false,
    });
}
