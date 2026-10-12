# Offline Prep

A Figma plugin that loads every page of a large file so it's all available offline (flights, commutes, patchy Wi-Fi). Figma Design files only.

**Status:** feature-complete, not yet tested inside real Figma. All logic has been tested against a simulated Figma API. See `TEST_RESULTS.md` for the test plan.

## Features

- **Prepare for offline:** loads every ticked page (all by default) with live progress, cancel, and a summary listing any pages that failed.
- **Images (experimental):**
  - *Skip:* fastest. Images may look blurry offline.
  - *Fetch image data:* asks Figma for every image's data. Doesn't move your view.
  - *Fly through every frame:* zooms to each top-level frame (and frames inside sections) for 1, 1.5 or 3 seconds so Figma loads sharp images. Your page and view are restored afterwards, even if you cancel or close the plugin.
- **Quick prepare:** Plugins > Offline Prep > Quick prepare loads all pages with no panel. Handy when you're prepping several files.
- **Prepared recently:** the panel lists the last 10 files you prepared and when.
- **Remembers:** image mode, time per frame, and the pages you unticked in each file.
- **Pre-flight checklist** for things a plugin can't fix.
- Read-only, no network access, light and dark theme.

## Build

```bash
npm install
npm run build
```

`npm run watch` rebuilds on save. `npm run lint` runs Figma's ESLint rules, which catch APIs that break under `dynamic-page`.

## Install in Figma (desktop app)

1. Open any Figma Design file in the **desktop app**.
2. Menu > Plugins > Development > **Import plugin from manifest...**
3. Pick `manifest.json` in this folder.
4. Run it: Plugins > Development > Offline Prep > **Open Offline Prep** (or **Quick prepare**).

## Usage

1. Open the file while online and run Offline Prep.
2. Untick pages you don't need (helps if a huge file is slow or runs out of memory).
3. Choose an image option, click **Prepare for offline**, and wait for the summary. During the fly-through, don't touch the canvas.
4. Repeat in every file you're taking. Keep all their tabs open.

## Project layout

```
manifest.json      plugin manifest (dynamic-page, no network, two menu commands)
src/code.ts        main thread: page loading, image warm-up, storage, messaging
ui.html            panel UI (inline CSS/JS, Figma theme variables)
dist/code.js       build output, referenced by the manifest
assets/            listing images; regenerate with `python3 assets/src/build.py` (needs Google Chrome)
LISTING.md         Community listing copy and data security answers
TEST_RESULTS.md    test plan and results log
```

## Known limitations

- Files can't be reopened offline, so keep each file's tab open.
- Library search/insert, plugin installs and fonts that aren't installed locally don't work offline. No plugin can fix these.
- Whether plugin-loaded pages and warmed-up images survive going offline is unconfirmed until tested (see `TEST_RESULTS.md`).
- Very large files may hit Figma's per-tab memory limit (about 2 GB). Untick pages if that happens.
- A plugin only runs in the open file, so multiple files need one run each.
