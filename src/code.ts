// Offline Prep: one click loads every page and downloads every image, so the
// file stays usable when the connection drops.
// Read-only: never modifies the document, never moves the user's view.

const FETCH_CONCURRENCY = 4;

type Failure = { name: string; error: string };

let toast: NotificationHandler | null = null;

function show(message: string, options: NotificationOptions = { timeout: Infinity }): void {
  toast?.cancel();
  toast = figma.notify(message, options);
}

function errorText(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function plural(n: number, word: string): string {
  return `${n} ${word}${n === 1 ? '' : 's'}`;
}

async function loadPages(pages: PageNode[], failed: Failure[]): Promise<number> {
  let loaded = 0;
  for (let i = 0; i < pages.length; i++) {
    show(`Loading page ${i + 1} of ${pages.length}: ${pages[i].name}`);
    try {
      await pages[i].loadAsync();
      loaded++;
    } catch (err) {
      failed.push({ name: pages[i].name, error: errorText(err) });
    }
  }
  return loaded;
}

function collectImageHashes(pages: PageNode[], failed: Failure[]): Set<string> {
  const hashes = new Set<string>();
  for (const page of pages) {
    try {
      const nodes = page.findAll((node) => 'fills' in node && Array.isArray(node.fills));
      for (const node of nodes) {
        for (const paint of (node as GeometryMixin).fills as readonly Paint[]) {
          if (paint.type === 'IMAGE' && paint.imageHash) hashes.add(paint.imageHash);
        }
      }
    } catch (err) {
      failed.push({ name: page.name, error: errorText(err) });
    }
  }
  return hashes;
}

// Asks Figma for each image's full data, so the original (not the low-res
// preview) is downloaded while online. The bytes themselves are discarded.
async function fetchImages(hashes: Set<string>, failed: Failure[]): Promise<number> {
  const queue = Array.from(hashes);
  const total = queue.length;
  let done = 0;
  let fetched = 0;

  async function worker(): Promise<void> {
    while (queue.length) {
      const hash = queue.shift() as string;
      try {
        const image = figma.getImageByHash(hash);
        if (image) {
          await image.getBytesAsync();
          fetched++;
        }
      } catch (err) {
        failed.push({ name: `Image ${hash.slice(0, 8)}`, error: errorText(err) });
      }
      done++;
      show(`Downloading image ${done} of ${total}`);
    }
  }

  await Promise.all(Array.from({ length: FETCH_CONCURRENCY }, worker));
  return fetched;
}

async function main(): Promise<void> {
  const start = Date.now();
  const pages = figma.root.children.filter((page) => !page.isPageDivider);
  const failed: Failure[] = [];

  const loaded = await loadPages(pages, failed);

  show('Finding images...');
  await sleep(0); // let the toast render before the synchronous scan
  figma.skipInvisibleInstanceChildren = true; // much faster findAll on big pages
  const hashes = collectImageHashes(pages, failed);
  const images = await fetchImages(hashes, failed);

  const seconds = Math.round((Date.now() - start) / 1000);
  const summary = `${loaded}/${pages.length} pages and ${plural(images, 'image')} in ${seconds}s`;
  if (failed.length) {
    console.warn('Offline Prep failures:', failed);
    const names = failed.slice(0, 3).map((f) => f.name).join(', ');
    const more = failed.length > 3 ? ` and ${failed.length - 3} more` : '';
    show(`Done with problems: ${summary}. Failed: ${names}${more}`, {
      error: true,
      timeout: 15000,
    });
  } else {
    show(`Ready for offline: ${summary}. Keep this tab open.`, { timeout: 8000 });
  }
}

main()
  .catch((err) => show(`Offline Prep failed: ${errorText(err)}`, { error: true, timeout: 15000 }))
  .then(() => setTimeout(() => figma.closePlugin(), 300));
