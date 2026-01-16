/** @jest-environment jsdom */

import { loadSvgSprite } from '../../utils/sprite.js';

describe('loadSvgSprite', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="svgSpriteRoot" hidden></div>';
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                text: () => Promise.resolve('<svg><symbol id="icon-test"></symbol></svg>'),
            }),
        );
    });

    afterEach(() => {
        jest.resetAllMocks();
        delete global.fetch;
    });

    test('injects sprite markup into the mount point', async () => {
        await loadSvgSprite();

        const mount = document.getElementById('svgSpriteRoot');
        expect(global.fetch).toHaveBeenCalledWith('assets/icon-sprite.svg', expect.any(Object));
        expect(mount.innerHTML).toContain('<svg');
        expect(mount.dataset.spriteLoaded).toBe('true');
    });

    test('skips loading when the mount point is absent', async () => {
        document.body.innerHTML = '';

        await loadSvgSprite();

        expect(global.fetch).not.toHaveBeenCalled();
    });

    test('does not refetch when sprite is already loaded', async () => {
        await loadSvgSprite();
        await loadSvgSprite();

        expect(global.fetch).toHaveBeenCalledTimes(1);
    });
});
