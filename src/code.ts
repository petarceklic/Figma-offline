// Offline Prep: loads pages so they stay available when the connection drops.
// Read-only: never modifies the document and never changes the current page.

type PageInfo = { id: string; name: string; isDivider: boolean };

type UiMessage =
  | { type: 'load-pages'; pageIds: string[] }
  | { type: 'cancel' }
  | { type: 'close' };

let cancelRequested = false;
let running = false;

figma.showUI(__html__, { width: 360, height: 600, themeColors: true });

function pageList(): PageInfo[] {
  return figma.root.children.map((page) => ({
    id: page.id,
    name: page.name,
    isDivider: page.isPageDivider,
  }));
}

function sendInit(): void {
  figma.ui.postMessage({
    type: 'init',
    pages: pageList(),
    currentPageId: figma.currentPage.id,
  });
}

async function loadPages(pageIds: string[]): Promise<void> {
  if (running) return;
  running = true;
  cancelRequested = false;

  const wanted = new Set(pageIds);
  const pages = figma.root.children.filter((page) => !page.isPageDivider && wanted.has(page.id));
  const total = pages.length;
  const failed: { name: string; error: string }[] = [];
  const start = Date.now();
  let loaded = 0;

  for (let i = 0; i < pages.length; i++) {
    if (cancelRequested) break;
    const page = pages[i];
    figma.ui.postMessage({ type: 'progress', done: i, total, pageName: page.name });
    try {
      await page.loadAsync();
      loaded++;
    } catch (err) {
      failed.push({ name: page.name, error: err instanceof Error ? err.message : String(err) });
    }
  }
  if (!cancelRequested) figma.ui.postMessage({ type: 'progress', done: total, total, pageName: '' });

  running = false;
  figma.ui.postMessage({
    type: 'pages-done',
    loaded,
    total,
    failed,
    cancelled: cancelRequested,
    ms: Date.now() - start,
  });
}

figma.ui.onmessage = (msg: UiMessage) => {
  switch (msg.type) {
    case 'load-pages':
      loadPages(msg.pageIds);
      break;
    case 'cancel':
      cancelRequested = true;
      break;
    case 'close':
      figma.closePlugin();
      break;
  }
};

sendInit();
