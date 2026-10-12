"use strict";
// Phase 0 spike: load every page, report, close. No UI.
// Goal is to answer U1: do pages loaded this way stay available offline?
async function main() {
    const pages = figma.root.children.filter((page) => !page.isPageDivider);
    const start = Date.now();
    try {
        await figma.loadAllPagesAsync();
        const seconds = ((Date.now() - start) / 1000).toFixed(1);
        figma.notify(`All ${pages.length} pages loaded in ${seconds}s`, { timeout: 6000 });
    }
    catch (err) {
        figma.notify(`Failed to load pages: ${String(err)}`, { error: true, timeout: 10000 });
    }
    // Give the toast a moment before the plugin closes.
    setTimeout(() => figma.closePlugin(), 500);
}
main();
