const lucide = require('lucide-static');

// Convert kebab-case to PascalCase
function toPascalCase(str) {
    return str
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join('');
}

// Test icon names - try both original and PascalCase
const iconsToTest = [
    'file-text', 
    'rows',
    'columns',
    'layout-grid',
    'clipboard-list',
    'heading-1',
    'heading',
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

console.log('Testing Lucide icons (PascalCase):\n');
const existing = [];
const missing = [];

iconsToTest.forEach(name => {
    const pascalName = toPascalCase(name);
    const exists = !!lucide[pascalName];
    if (exists) {
        existing.push({ original: name, pascal: pascalName });
        console.log(`✓ ${name} -> ${pascalName}`);
    } else {
        missing.push(name);
        console.log(`✗ ${name} -> ${pascalName} - NOT FOUND`);
    }
});

console.log(`\nSummary:`);
console.log(`Found: ${existing.length}`);
console.log(`Missing: ${missing.length}`);

// Show mapping
console.log(`\nIcon mapping:`);
existing.forEach(({ original, pascal }) => {
    console.log(`  '${original}' -> '${pascal}'`);
});

