const fs = require('fs');
const path = require('path');
const lucide = require('lucide-static');

/**
 * Convert kebab-case to PascalCase
 */
function toPascalCase(str) {
    return str
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join('');
}

/**
 * Icon name mapping: kebab-case (used in code) -> PascalCase (used in lucide-static)
 * For missing icons, map to alternatives
 */
const ICON_MAPPING = {
    'file-text': 'FileText',
    'rows': 'Rows',
    'columns': 'Columns',
    'layout-grid': 'LayoutGrid',
    'clipboard-list': 'ClipboardList',
    'heading-1': 'Heading1',
    'pilcrow': 'Pilcrow',
    'type': 'Type',
    'closed-captioning': 'Subtitles', // Alternative: ClosedCaptioning doesn't exist
    'quote': 'Quote',
    'link': 'Link',
    'image': 'Image',
    'video': 'Video',
    'film': 'Film',
    'mouse-pointer-square': 'MousePointer', // Alternative: MousePointerSquare doesn't exist
    'credit-card': 'CreditCard',
    'folder-tabs': 'Folder', // Alternative: FolderTabs doesn't exist
    'chevrons-down-up': 'ChevronsUpDown',
    'gallery-horizontal': 'GalleryHorizontal',
    'menu': 'Menu',
    'wrap-text': 'WrapText',
    'chevron-down': 'ChevronDown',
    'check-square': 'CheckSquare',
    'circle-dot': 'CircleDot',
    'calendar': 'Calendar',
    'layout': 'Layout',
    'settings': 'Settings',
    'square': 'Square',
    'layers': 'Layers',
    'sliders': 'Sliders',
    'edit-2': 'Edit2',
    'file-plus': 'FilePlus',
    'edit': 'Edit',
    'box': 'Box',
    'maximize': 'Maximize',
    'download': 'Download',
    'help-circle': 'HelpCircle',
    'trash-2': 'Trash2',
    'chevrons-down': 'ChevronsDown',
    'circle': 'Circle',
    'grid': 'Grid',
    'clear-canvas': 'XCircle', // Alternative for clear-canvas
};

// This list contains kebab-case icon names (as used in the codebase)
const LUCIDE_ICONS = Object.keys(ICON_MAPPING);

const CUSTOM_ICONS = {
  'layout-row': {
    viewBox: '0 0 512 512',
    content: `<g fill="currentColor" fill-rule="nonzero">
    <g>
            <rect x="30" y="100" width="460" height="280" stroke="currentcolor" stroke-width="30" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    
    		<rect x="70" y="160" width="100" height="160" stroke="currentcolor" stroke-width="8" fill="currentcolor" stroke-linecap="round" stroke-linejoin="round"/>
    
    		<rect x="210.857" y="160" width="100" height="160" stroke="currentcolor" stroke-width="8" fill="currentcolor" stroke-linecap="round" stroke-linejoin="round"/>
    
    		<rect x="350.714" y="160" width="100" height="160" stroke="currentcolor" stroke-width="8" fill="currentcolor" stroke-linecap="round" stroke-linejoin="round"/>
    </g></g>`
  },
  'layout-column': {
    viewBox: '0 0 35 35',
    content: `<g fill="currentColor" fill-rule="nonzero">
    <g>
           <g>
            <rect x="1" y="3" width="33" height="30" stroke-width="2" fill="none" stoke="currentcolor" stroke-linecap="round" stroke-linejoin="round"/>
    		<rect x="5" y="20" width="25" height="8" stroke-linecap="round" stroke-linejoin="round"/>
    		<rect x="5" y="7" width="25" height="8" stroke-linecap="round" stroke-linejoin="round"/>
            
    </g>
    </g></g>`
  },
  'swift-sites': {
    viewBox: '0 0 24 24',
    content: `
      <path fill="none" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" d="m22.999 10c0 4.397-1.021 7.169-1.063 7.285-.104.275-.324.492-.602.591-.122.043-2.895 1.005-8.335 1.113v2.011h3.001c.553 0 1 .447 1 1s-.447 1-1 1h-8c-.553 0-1-.447-1-1s.447-1 1-1h3v-2.011c-5.44-.108-8.214-1.07-8.336-1.113-.277-.099-.498-.315-.602-.591-.043-.116-1.063-2.888-1.063-7.285s1.021-7.169 1.063-7.285c.104-.275.324.492.602-.591.129-.046 3.232-1.124 9.335-1.124.724 0 1.405.015 2.043.042.552.023.98.489.957 1.041s-.484.997-1.041.957c-.612-.025-1.265-.04-1.959-.04-4.427 0-7.18.6-8.209.875-.263.904-.791 3.101-.791 6.125s.528 5.219.792 6.125c1.026.274 3.78.875 8.208.875s7.18-.6 8.209-.875c.263-.904.791-3.101.791-6.125 0-.553.447-1 1-1s1 .447 1 1zm-9.238-3.958c.554-.552 1.092-1.069 1.598-1.541.973-.901 1.978-1.777 3.073-2.678.924-.755 2.174-1.431 3.671.065 1.547 1.547.771 2.844.054 3.686-.572.697-1.509 1.804-2.647 3.035-.475.51-1.006 1.067-1.559 1.623.099 1.081-.378 2.161-1.474 3.256-1.269 1.269-3.514 1.508-5.021 1.508-.771 0-1.348-.062-1.506-.081-.458-.056-.818-.416-.874-.874-.056-.466-.49-4.61 1.427-6.527 1.097-1.097 2.177-1.573 3.259-1.473zm1.302 2.887c-1.234-1.234-1.912-1.234-3.146 0-.828.828-.951 2.807-.911 4.061 1.416.053 3.288-.145 4.058-.914 1.235-1.235 1.235-1.911 0-3.146zm.695-2.045c.239.183.479.391.719.631.241.241.449.48.632.719.327-.339.644-.672.936-.985 1.104-1.193 2.013-2.269 2.58-2.959.366-.43.376-.579.376-.578.025-.255-.423-.748-.709-.712.004 0-.149.009-.591.37-1.062.873-2.038 1.724-2.979 2.596-.309.288-.633.597-.963.918z" />
    `
  },
};

function toSymbol(kebabName) {
  // Convert kebab-case to PascalCase using mapping
  const pascalName = ICON_MAPPING[kebabName] || toPascalCase(kebabName);
  const svgString = lucide[pascalName];
  
  if (!svgString || typeof svgString !== 'string') {
    // Fallback for any icons not in lucide-static
    console.warn(`Warning: Icon "${kebabName}" (${pascalName}) not found in lucide-static`);
    return `<!-- Icon "${kebabName}" (${pascalName}) not found -->`;
  }
  
  // Extract viewBox from SVG string
  const viewBoxMatch = svgString.match(/viewBox=["']([^"']+)["']/);
  const viewBox = viewBoxMatch ? viewBoxMatch[1] : '0 0 24 24';
  
  // Extract inner content (everything between <svg> and </svg> tags)
  const innerMatch = svgString.match(/<svg[^>]*>([\s\S]*)<\/svg>/);
  const inner = innerMatch ? innerMatch[1].trim() : '';

  // Use kebab-case for the symbol ID (as used in the codebase)
  return `<symbol id="icon-${kebabName}" viewBox="${viewBox}">${inner}</symbol>`;
}

function buildCustomSymbol(name, definition) {
  const { viewBox, content } = definition;
  return `<symbol id="icon-${name}" viewBox="${viewBox}">${content.trim()}</symbol>`;
}

function buildSprite() {
  const lucideSymbols = LUCIDE_ICONS.map(toSymbol).join('\n');
  const customSymbols = Object.entries(CUSTOM_ICONS)
    .map(([name, definition]) => buildCustomSymbol(name, definition))
    .join('\n');
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden;">
${lucideSymbols}
${customSymbols}
</svg>
`;
}

function writeSprite(outputPath) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, buildSprite(), 'utf8');
  console.log(`SVG sprite generated at ${outputPath}`);
}

// Write to both assets and ssr_python static assets
writeSprite(path.resolve(__dirname, '..', 'assets', 'icon-sprite.svg'));
writeSprite(path.resolve(__dirname, '..', 'ssr_python', 'static', 'icon-sprite.svg'));