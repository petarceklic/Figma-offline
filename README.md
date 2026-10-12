# Offline Prep

A Figma plugin that loads every page of a large file so it's all available offline (flights, commutes, patchy Wi-Fi).

**Status: Phase 0 spike.** Right now it only loads all pages, shows a toast, and closes. No UI yet. The goal is to confirm that pages loaded by a plugin stay available offline (Test A) before building more.

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

## Test A (the gate for Phase 1)

Use a **duplicate** of a real, large file (20+ pages, image-heavy).

1. Quit and relaunch Figma. Open the test file. Stay on page 1.
2. Run Offline Prep. Wait for the "All N pages loaded" toast. Don't click into any other page.
3. Turn Wi-Fi off.
4. Open every page. For each: does it render? Can you select, move and edit a layer? Edit text? Duplicate a local component?
5. Turn Wi-Fi on and confirm the edits sync.

Pass = every page opens and is editable offline. Record results in `TEST_RESULTS.md`.

It's worth running the baseline too (same steps without the plugin) so you can see that unvisited pages really are unavailable without it.

## Known limitations

- Keep the file's tab open: files can't be reopened offline.
- Library search/insert, plugin installs and unloaded fonts don't work offline. No plugin can fix these.
- High-res image availability offline is untested (Phase 2).
