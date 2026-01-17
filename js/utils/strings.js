export function escapeHtml(value) {
    if (typeof value !== 'string') {
        return value;
    }
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

export function escapeHtmlWithLineBreaks(value) {
    if (typeof value !== 'string') {
        return value;
    }
    const escaped = escapeHtml(value);
    return escaped.replace(/\r\n|\r|\n/g, '<br>');
}
