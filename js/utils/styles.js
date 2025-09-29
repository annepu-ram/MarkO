export function toRem(value) {
    if (typeof value === 'number') {
        return `${value / 10}rem`;
    }
    if (typeof value === 'string') {
        return value
            .split(' ')
            .map(token => {
                const numeric = parseFloat(token);
                return Number.isNaN(numeric) ? token : `${numeric / 10}rem`;
            })
            .join(' ');
    }
    return value;
}

const SPACING_SCALE_MAP = {
    none: '0',
    xs: '0.4rem',
    sm: '0.8rem',
    md: '1.6rem',
    lg: '2.4rem',
    xl: '3.2rem',
};

export function resolveSpacingValue(value) {
    if (value === undefined || value === null || value === '') {
        return null;
    }
    if (SPACING_SCALE_MAP[value] !== undefined) {
        return SPACING_SCALE_MAP[value];
    }
    if (value === 'auto') {
        return 'auto';
    }
    if (typeof value === 'number') {
        return toRem(value);
    }
    const numeric = parseFloat(value);
    if (!Number.isNaN(numeric) && String(value).trim() === `${numeric}`) {
        return toRem(numeric);
    }
    return value;
}

const LETTER_SPACING_MAP = {
    normal: 'normal',
    tight: '-0.015em',
    wide: '0.1em',
    wider: '0.15em',
};

export function resolveLetterSpacing(value) {
    if (!value) {
        return null;
    }
    if (LETTER_SPACING_MAP[value] !== undefined) {
        return LETTER_SPACING_MAP[value];
    }
    return value;
}

const LINE_HEIGHT_MAP = {
    normal: 1.5,
    snug: 1.35,
    relaxed: 1.7,
    loose: 1.9,
};

export function resolveLineHeight(value) {
    if (!value) {
        return null;
    }
    if (LINE_HEIGHT_MAP[value] !== undefined) {
        return LINE_HEIGHT_MAP[value];
    }
    return value;
}
const TYPOGRAPHY_SIZE_MAP = {
    xxs: '1.0rem',
    xs: '1.2rem',
    sm: '1.4rem',
    md: '1.6rem',
    lg: '2.0rem',
    xl: '2.4rem',
    xxl: '3.2rem',
    xxxl: '3.6rem',
};
export function resolveTypographySize(value) {
    if (!value) {
        return null;
    }
    if (TYPOGRAPHY_SIZE_MAP[value] !== undefined) {
        return TYPOGRAPHY_SIZE_MAP[value];
    }
    if (typeof value === 'number') {
        return toRem(value);
    }
    return value;
}

const FONT_WEIGHT_MAP = {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
};

export function resolveFontWeight(value) {
    if (!value) {
        return null;
    }
    if (FONT_WEIGHT_MAP[value] !== undefined) {
        return FONT_WEIGHT_MAP[value];
    }
    return value;
}

