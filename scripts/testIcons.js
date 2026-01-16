const lucide = require('lucide-static');

// Test all the icon names we're trying to use
const iconsToTest = [
    'file-text', 
    'rows',
    'columns',
    'layout-grid',
    'clipboard-list',
    'heading-1',
    'pilcrow',
    'type',
    'closed-captioning',
    'quote',
    'link',
    'image',
    'video',
    'film',
    'mouse-pointer-square',
    'credit-card',
    'folder-tabs',
    'chevrons-up-down',
    'gallery-horizontal',
    'menu',
    'wrap-text',
    'chevron-down',
    'check-square',
    'circle-dot',
    'calendar',
    'layout',
    'settings',
    'square',
    'layers',
    'sliders',
    'pen',
    'edit-2',
    'file-plus',
    'edit',
    'box',
    'maximize',
    'download',
    'help-circle',
    'trash-2',
    'chevrons-down',
    'circle',
    'grid',
];

console.log('Testing Lucide icons:\n');
const existing = [];
const missing = [];

iconsToTest.forEach(name => {
    const exists = !!lucide[name];
    if (exists) {
        existing.push(name);
        console.log(`✓ ${name}`);
    } else {
        missing.push(name);
        console.log(`✗ ${name} - NOT FOUND`);
    }
});

console.log(`\nSummary:`);
console.log(`Found: ${existing.length}`);
console.log(`Missing: ${missing.length}`);

// Try to find alternatives for missing icons
console.log(`\nTrying alternative names for missing icons:`);
const alternatives = {
    'rows': ['rows-3', 'layout'],
    'columns': ['columns-3', 'layout'],
    'heading-1': ['heading', 'type'],
    'closed-captioning': ['subtitles'],
    'mouse-pointer-square': ['mouse-pointer', 'square'],
    'folder-tabs': ['folder', 'tabs'],
    'chevrons-up-down': ['chevrons-up-down', 'chevrons-up-down'],
    'gallery-horizontal': ['gallery', 'images'],
    'wrap-text': ['text'],
    'circle-dot': ['circle', 'dot'],
    'edit-2': ['pen', 'pencil'],
    'trash-2': ['trash', 'trash-can'],
    'chevrons-down': ['chevron-down'],
    'clear-canvas': ['x', 'x-circle'],
};

missing.forEach(name => {
    if (alternatives[name]) {
        alternatives[name].forEach(alt => {
            if (lucide[alt]) {
                console.log(`  ${name} -> ${alt} (EXISTS)`);
            }
        });
    }
});

