import { toRem, resolveSpacingValue, resolveLetterSpacing, resolveLineHeight, resolveTypographySize, resolveFontWeight } from '../styles.js';

describe('styles.js', () => {
  test('toRem should convert pixels to rem', () => {
    expect(toRem(16)).toBe('1.6rem');
    expect(toRem('20px')).toBe('2rem');
    expect(toRem('16px 20px')).toBe('1.6rem 2rem');
  });

  test('resolveSpacingValue should resolve spacing tokens', () => {
    expect(resolveSpacingValue('md')).toBe('1.6rem');
    expect(resolveSpacingValue(10)).toBe('1rem');
    expect(resolveSpacingValue('auto')).toBe('auto');
  });

  test('resolveLetterSpacing should resolve letter spacing tokens', () => {
    expect(resolveLetterSpacing('wide')).toBe('0.1em');
    expect(resolveLetterSpacing('2px')).toBe('2px');
  });

  test('resolveLineHeight should resolve line height tokens', () => {
    expect(resolveLineHeight('normal')).toBe(1.5);
    expect(resolveLineHeight(1.2)).toBe(1.2);
  });

  test('resolveTypographySize should resolve typography size tokens', () => {
    expect(resolveTypographySize('xl')).toBe('2.4rem');
    expect(resolveTypographySize(18)).toBe('1.8rem');
  });

  test('resolveFontWeight should resolve font weight tokens', () => {
    expect(resolveFontWeight('bold')).toBe(700);
    expect(resolveFontWeight(500)).toBe(500);
  });
});