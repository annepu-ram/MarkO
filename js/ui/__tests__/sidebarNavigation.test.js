/**
 * @jest-environment jsdom
 */

describe('sidebar navigation switching', () => {
    let dom;
    let activateNavItem;

    beforeEach(() => {
        document.body.innerHTML = `
            <div class="sidebar">
                <nav class="sidebar-nav">
                    <button id="componentsNavBtn" class="sidebar-nav-item active"
                            data-target="componentsPanel" aria-selected="true"></button>
                    <button id="propertiesNavBtn" class="sidebar-nav-item"
                            data-target="propertiesPanel" aria-selected="false"></button>
                </nav>
                <div class="sidebar-panels-container">
                    <div id="componentsPanel" class="sidebar-panel active" aria-hidden="false"></div>
                    <div id="propertiesPanel" class="sidebar-panel" aria-hidden="true"></div>
                </div>
            </div>
        `;

        const sidebarNavItems = Array.from(document.querySelectorAll('.sidebar-nav-item'));
        const sidebarPanels = Array.from(document.querySelectorAll('.sidebar-panel'));

        activateNavItem = targetId => {
            sidebarNavItems.forEach(navItem => {
                const isActive = navItem.dataset.target === targetId;
                navItem.classList.toggle('active', isActive);
                navItem.setAttribute('aria-selected', isActive ? 'true' : 'false');
            });

            sidebarPanels.forEach(panel => {
                const isActive = panel.id === targetId;
                panel.classList.toggle('active', isActive);
                panel.setAttribute('aria-hidden', isActive ? 'false' : 'true');
            });
        };

        sidebarNavItems.forEach(navItem => {
            navItem.addEventListener('click', () => {
                const targetId = navItem.dataset.target;
                if (targetId) {
                    activateNavItem(targetId);
                }
            });
        });
    });

    test('clicking the Properties nav item activates the properties panel', () => {
        const propertiesNavBtn = document.getElementById('propertiesNavBtn');
        const propertiesPanel = document.getElementById('propertiesPanel');
        const componentsPanel = document.getElementById('componentsPanel');

        propertiesNavBtn.click();

        expect(propertiesNavBtn.classList.contains('active')).toBe(true);
        expect(propertiesNavBtn.getAttribute('aria-selected')).toBe('true');
        expect(propertiesPanel.classList.contains('active')).toBe(true);
        expect(propertiesPanel.getAttribute('aria-hidden')).toBe('false');
        expect(componentsPanel.classList.contains('active')).toBe(false);
    });

    test('clicking back on Components restores the components panel', () => {
        const componentsNavBtn = document.getElementById('componentsNavBtn');
        const propertiesNavBtn = document.getElementById('propertiesNavBtn');
        const componentsPanel = document.getElementById('componentsPanel');
        const propertiesPanel = document.getElementById('propertiesPanel');

        propertiesNavBtn.click();
        componentsNavBtn.click();

        expect(componentsNavBtn.classList.contains('active')).toBe(true);
        expect(componentsPanel.classList.contains('active')).toBe(true);
        expect(propertiesNavBtn.classList.contains('active')).toBe(false);
        expect(propertiesPanel.classList.contains('active')).toBe(false);
    });
});
