import { escapeHtml } from '../strings.js';

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
});