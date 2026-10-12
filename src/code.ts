// Offline Prep: loads pages (and optionally warms up images) so a file stays
// usable when the connection drops.
// Read-only: never modifies the document. The only side effects are viewport
// and current-page navigation during the image sweep, which are restored.

type PageInfo = { id: string; name: string; isDivider: boolean };
type ImageMode = 'off' | 'sweep' | 'fetch';

type Settings = {
  imageMode: ImageMode;
  dwellMs: number;
};

type PreparedFile = {
  name: string;
  at: number;
  pages: number;
  images: ImageMode;
};

type UiMessage =
  | { type: 'prepare'; pageIds: string[]; imageMode: ImageMode; dwellMs: number }
  | { type: 'save-settings'; settings: Settings }
  | { type: 'cancel' }
  | { type: 'close' };

const SETTINGS_KEY = 'settings';
const DESELECTED_KEY = 'deselected';
const PREPARED_KEY = 'prepared';
const MAX_PREPARED = 10;
const MAX_REMEMBERED_FILES = 20;
const FETCH_CONCURRENCY = 4;

const DEFAULT_SETTINGS: Settings = { imageMode: 'off', dwellMs: 1500 };

// Node types worth bringing into view during the image sweep.
const SWEEP_TYPES = new Set<NodeType>(['FRAME', 'GROUP', 'COMPONENT', 'COMPONENT_SET', 'INSTANCE']);

let cancelRequested = false;
let closeRequested = false;
let running = false;

// ---------- helpers ----------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Sleeps in short slices so Cancel feels instant during long dwell times.
async function dwell(ms: number): Promise<void> {
  const end = Date.now() + ms;
  while (!cancelRequested && Date.now() < end) {
    await sleep(Math.min(100, end - Date.now()));
  }
}

function errorText(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

function post(msg: object): void {
  if (!closeRequested) figma.ui.postMessage(msg);
}

function contentPages(pageIds?: string[]): PageNode[] {
  const wanted = pageIds ? new Set(pageIds) : null;
  return figma.root.children.filter((page) => !page.isPageDivider && (!wanted || wanted.has(page.id)));
}

// ---------- storage ----------

async function getSettings(): Promise<Settings> {
  const stored = await figma.clientStorage.getAsync(SETTINGS_KEY);
  return { ...DEFAULT_SETTINGS, ...(stored || {}) };
}

// clientStorage is shared across all files, so page selections are keyed by file name.
async function getDeselected(): Promise<string[]> {
  const all: Record<string, string[]> = (await figma.clientStorage.getAsync(DESELECTED_KEY)) || {};
  return all[figma.root.name] || [];
}

async function saveDeselected(pageIds: string[]): Promise<void> {
  const selected = new Set(pageIds);
  const deselected = contentPages().filter((p) => !selected.has(p.id)).map((p) => p.id);
  const all: Record<string, string[]> = (await figma.clientStorage.getAsync(DESELECTED_KEY)) || {};
  delete all[figma.root.name];
  if (deselected.length) all[figma.root.name] = deselected;
  // Keep only the most recent files (object keys keep insertion order).
  const names = Object.keys(all);
  for (const name of names.slice(0, Math.max(0, names.length - MAX_REMEMBERED_FILES))) delete all[name];
  await figma.clientStorage.setAsync(DESELECTED_KEY, all);
}

async function getPrepared(): Promise<PreparedFile[]> {
  return (await figma.clientStorage.getAsync(PREPARED_KEY)) || [];
}

async function recordPrepared(pages: number, images: ImageMode): Promise<PreparedFile[]> {
  const list = (await getPrepared()).filter((f) => f.name !== figma.root.name);
  list.unshift({ name: figma.root.name, at: Date.now(), pages, images });
  const trimmed = list.slice(0, MAX_PREPARED);
  await figma.clientStorage.setAsync(PREPARED_KEY, trimmed);
  return trimmed;
}

// ---------- step 1: load pages ----------

async function loadPages(pages: PageNode[]): Promise<{ loaded: number; failed: { name: string; error: string }[] }> {
  const failed: { name: string; error: string }[] = [];
  let loaded = 0;
  for (let i = 0; i < pages.length; i++) {
    if (cancelRequested) break;
    const page = pages[i];
    post({ type: 'progress', step: 'pages', done: i, total: pages.length, label: page.name });
    try {
      await page.loadAsync();
      loaded++;
    } catch (err) {
      failed.push({ name: page.name, error: errorText(err) });
    }
  }
  return { loaded, failed };
}

// ---------- step 2a: image sweep ----------

// Top-level frames on a page. Sections are opened one level so each frame
// inside gets its own close-up rather than one zoomed-out view of the section.
function sweepTargets(page: PageNode): SceneNode[] {
  const targets: SceneNode[] = [];
  for (const node of page.children) {
    if (!node.visible) continue;
    if (node.type === 'SECTION') {
      const inner = node.children.filter((child) => child.visible && SWEEP_TYPES.has(child.type));
      if (inner.length) targets.push(...inner);
      else targets.push(node);
    } else if (SWEEP_TYPES.has(node.type)) {
      targets.push(node);
    }
  }
  return targets;
}

async function sweepImages(pages: PageNode[], dwellMs: number): Promise<{ visited: number; failed: { name: string; error: string }[] }> {
  const failed: { name: string; error: string }[] = [];
  const plan = pages.map((page) => {
    try {
      return { page, targets: sweepTargets(page) };
    } catch (err) {
      failed.push({ name: page.name, error: errorText(err) });
      return { page, targets: [] as SceneNode[] };
    }
  });
  const total = plan.reduce((sum, p) => sum + p.targets.length, 0);
  let visited = 0;

  const originalPage = figma.currentPage;
  const originalCenter = figma.viewport.center;
  const originalZoom = figma.viewport.zoom;

  try {
    for (const { page, targets } of plan) {
      if (cancelRequested || !targets.length) continue;
      try {
        await figma.setCurrentPageAsync(page);
      } catch (err) {
        failed.push({ name: page.name, error: errorText(err) });
        visited += targets.length;
        continue;
      }
      for (const node of targets) {
        if (cancelRequested) break;
        post({ type: 'progress', step: 'sweep', done: visited, total, label: `${page.name} / ${node.name}` });
        try {
          figma.viewport.scrollAndZoomIntoView([node]);
          await dwell(dwellMs);
        } catch (err) {
          failed.push({ name: `${page.name} / ${node.name}`, error: errorText(err) });
        }
        visited++;
      }
    }
  } finally {
    try {
      await figma.setCurrentPageAsync(originalPage);
      figma.viewport.center = originalCenter;
      figma.viewport.zoom = originalZoom;
    } catch (err) {
      failed.push({ name: 'Restoring your view', error: errorText(err) });
    }
  }
  return { visited, failed };
}

// ---------- step 2b: fetch image data ----------

function collectImageHashes(page: PageNode, into: Set<string>): void {
  const nodes = page.findAll((node) => 'fills' in node && Array.isArray(node.fills));
  for (const node of nodes) {
    for (const paint of (node as GeometryMixin).fills as readonly Paint[]) {
      if (paint.type === 'IMAGE' && paint.imageHash) into.add(paint.imageHash);
    }
  }
}

async function fetchImages(pages: PageNode[]): Promise<{ fetched: number; failed: { name: string; error: string }[] }> {
  const failed: { name: string; error: string }[] = [];
  const hashes = new Set<string>();
  figma.skipInvisibleInstanceChildren = true; // much faster findAll on big pages
  for (let i = 0; i < pages.length; i++) {
    if (cancelRequested) break;
    post({ type: 'progress', step: 'scan', done: i, total: pages.length, label: pages[i].name });
    try {
      collectImageHashes(pages[i], hashes);
    } catch (err) {
      failed.push({ name: pages[i].name, error: errorText(err) });
    }
    await sleep(0); // let the UI repaint between pages
  }

  const queue = Array.from(hashes);
  const total = queue.length;
  let done = 0;
  let fetched = 0;

  async function worker(): Promise<void> {
    while (queue.length && !cancelRequested) {
      const hash = queue.shift() as string;
      try {
        const image = figma.getImageByHash(hash);
        if (image) {
          await image.getBytesAsync(); // bytes are discarded; we only want Figma to fetch them
          fetched++;
        }
      } catch (err) {
        failed.push({ name: `Image ${hash.slice(0, 8)}`, error: errorText(err) });
      }
      done++;
      post({ type: 'progress', step: 'fetch', done, total, label: '' });
    }
  }

  post({ type: 'progress', step: 'fetch', done: 0, total, label: '' });
  await Promise.all(Array.from({ length: FETCH_CONCURRENCY }, worker));
  return { fetched, failed };
}

// ---------- orchestration ----------

async function prepare(pageIds: string[], imageMode: ImageMode, dwellMs: number): Promise<void> {
  if (running) return;
  running = true;
  cancelRequested = false;
  const start = Date.now();
  const pages = contentPages(pageIds);

  await saveDeselected(pageIds);
  await figma.clientStorage.setAsync(SETTINGS_KEY, { imageMode, dwellMs });

  const pageResult = await loadPages(pages);
  const pagesMs = Date.now() - start;

  let images: { mode: ImageMode; count: number; ms: number } | null = null;
  const imageFailures: { name: string; error: string }[] = [];
  if (imageMode !== 'off' && !cancelRequested) {
    const imgStart = Date.now();
    if (imageMode === 'sweep') {
      const r = await sweepImages(pages, dwellMs);
      images = { mode: imageMode, count: r.visited, ms: Date.now() - imgStart };
      imageFailures.push(...r.failed);
    } else {
      const r = await fetchImages(pages);
      images = { mode: imageMode, count: r.fetched, ms: Date.now() - imgStart };
      imageFailures.push(...r.failed);
    }
  }

  const cancelled = cancelRequested;
  // Pages count as prepared even if only the image step was cancelled.
  const pagesComplete = pageResult.loaded + pageResult.failed.length === pages.length;
  const prepared = pagesComplete
    ? await recordPrepared(pageResult.loaded, cancelled ? 'off' : imageMode)
    : await getPrepared();
  running = false;

  if (closeRequested) {
    figma.closePlugin();
    return;
  }

  post({
    type: 'done',
    loaded: pageResult.loaded,
    total: pages.length,
    pagesMs,
    images,
    failed: [...pageResult.failed, ...imageFailures],
    cancelled,
    ms: Date.now() - start,
    prepared,
  });
}

// Menu command: load every page with no UI. Handy when prepping several files.
async function quickPrepare(): Promise<void> {
  const pages = contentPages();
  const start = Date.now();
  figma.notify(`Loading ${pages.length} pages...`, { timeout: 2000 });
  const { loaded, failed } = await loadPages(pages);
  await recordPrepared(loaded, 'off');
  const seconds = ((Date.now() - start) / 1000).toFixed(1);
  if (failed.length) {
    figma.notify(`${loaded}/${pages.length} pages loaded in ${seconds}s. Failed: ${failed.map((f) => f.name).join(', ')}`, {
      error: true,
      timeout: 10000,
    });
  } else {
    figma.notify(`Ready for offline: ${loaded}/${pages.length} pages loaded in ${seconds}s. Keep this tab open.`, {
      timeout: 6000,
    });
  }
  setTimeout(() => figma.closePlugin(), 300);
}

async function openPanel(): Promise<void> {
  figma.showUI(__html__, { width: 360, height: 640, themeColors: true });

  figma.ui.onmessage = (msg: UiMessage) => {
    switch (msg.type) {
      case 'prepare':
        prepare(msg.pageIds, msg.imageMode, msg.dwellMs);
        break;
      case 'save-settings':
        figma.clientStorage.setAsync(SETTINGS_KEY, msg.settings);
        break;
      case 'cancel':
        cancelRequested = true;
        break;
      case 'close':
        // If a sweep is running, let it restore the user's view before closing.
        if (running) {
          closeRequested = true;
          cancelRequested = true;
        } else {
          figma.closePlugin();
        }
        break;
    }
  };

  const pages: PageInfo[] = figma.root.children.map((page) => ({
    id: page.id,
    name: page.name,
    isDivider: page.isPageDivider,
  }));

  post({
    type: 'init',
    fileName: figma.root.name,
    pages,
    currentPageId: figma.currentPage.id,
    deselected: await getDeselected(),
    settings: await getSettings(),
    prepared: await getPrepared(),
  });
}

if (figma.command === 'quick') {
  quickPrepare();
} else {
  openPanel();
}
