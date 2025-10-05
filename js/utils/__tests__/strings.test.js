import { escapeHtml, escapeHtmlWithLineBreaks } from '../strings.js';

describe('strings.js', () => {
  test('escapeHtml should escape HTML characters', () => {
    const html = '<p>Hello & World!</p>';
    const escapedHtml = escapeHtml(html);
    expect(escapedHtml).toBe('&lt;p&gt;Hello &amp; World!&lt;/p&gt;');
  });

  test('escapeHtml should return non-string values as is', () => {
    expect(escapeHtml(123)).toBe(123);
    expect(escapeHtml(null)).toBe(null);
    expect(escapeHtml(undefined)).toBe(undefined);
  });

  test('escapeHtmlWithLineBreaks converts newlines to <br> while escaping HTML', () => {
    const value = 'Hello\n<World>';
    const result = escapeHtmlWithLineBreaks(value);
    expect(result).toBe('Hello<br>&lt;World&gt;');
  });

  test('escapeHtmlWithLineBreaks returns non-string values unchanged', () => {
    expect(escapeHtmlWithLineBreaks(null)).toBeNull();
    expect(escapeHtmlWithLineBreaks(42)).toBe(42);
  });
});
