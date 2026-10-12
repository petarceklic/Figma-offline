# Offline Prep

A Figma plugin that loads every page of a large file so it's all available offline (flights, commutes, patchy Wi-Fi).

**Status: Phase 1 (MVP), untested in Figma.** Pick pages (all by default), click **Prepare for offline**, watch per-page progress, get a summary with any errors, and tick through a pre-flight checklist. Test A hasn't been run yet, so it's still unconfirmed that plugin-loaded pages stay available offline. Research found nothing that confirms or rules it out (see `TEST_RESULTS.md`).

## Build

```bash
npm install
npm run build
```

`npm run watch` rebuilds on save. `npm run lint` checks for APIs that break under `dynamic-page`.

## Install in Figma (desktop app)

1. Open any Figma Design file in the **desktop app**.
2. Menu > Plugins > Development > **Import plugin from manifest...**
3. Pick `manifest.json` in this folder.
4. Run it: Plugins > Development > **Offline Prep**.

## Usage

1. Open the file while online and run Offline Prep.
2. Untick pages you don't need (useful if a huge file is slow or runs out of memory).
3. Click **Prepare for offline** and wait for the summary.
4. Go through the pre-flight checklist, then keep the tab open.

## Test A (the gate for Phase 1)

Use a **duplicate** of a real, large file (20+ pages, image-heavy).

1. Quit and relaunch Figma. Open the test file. Stay on page 1.
2. Run Offline Prep and click **Prepare for offline**. Wait for the summary. Don't click into any other page.
3. Turn Wi-Fi off.
4. Open every page. For each: does it render? Can you select, move and edit a layer? Edit text? Duplicate a local component?
5. Turn Wi-Fi on and confirm the edits sync.

Pass = every page opens and is editable offline. Record results in `TEST_RESULTS.md`.

It's worth running the baseline too (same steps without the plugin) so you can see that unvisited pages really are unavailable without it.

## Known limitations

- Keep the file's tab open: files can't be reopened offline.
- Library search/insert, plugin installs and unloaded fonts don't work offline. No plugin can fix these.
- High-res image availability offline is untested (Phase 2).
