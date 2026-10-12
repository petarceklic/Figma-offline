# Test results

| Test | Date | File (pages / size) | Result | Notes |
|------|------|---------------------|--------|-------|
| Baseline (no plugin) | | | | |
| A: pages | | | | |
| B: images, fly-through | | | | |
| C: images, fetch data | | | | |
| D: 1 hour asleep offline | | | | |
| E: largest file | | | | |
| F: two files | | | | |

## Simulated tests (2026-10-12, fake Figma API, not real Figma)

All passed: page loading with progress; one failing page reported without stopping the rest; fly-through visits frames (and frames inside sections) and restores page and view; cancel and close mid-fly-through both restore the view; fetch mode finds and fetches unique images; settings and unticked pages remembered after reopening; quick prepare; prepared-recently list across two files; light and dark theme; panel layout with everything expanded.

## Real-Figma test plan

Use **duplicates** of real, large, image-heavy files, in the Figma desktop app. Restart Figma before each test.

- **A, pages:** open the file, stay on page 1, run Offline Prep with Images = Skip. Wi-Fi off. Open every page, move a layer, edit text. Wi-Fi on, check edits sync. *If this fails, image warm-up doesn't matter: the core idea doesn't work.*
- **B, fly-through:** run with Images = Fly through, 1.5s. Wi-Fi off. Zoom to 100% and 200% on image-heavy frames on several pages. Sharp, blurry or missing?
- **C, fetch data:** same as B with Images = Fetch image data.
- **D, endurance:** after preparing, Wi-Fi off, close the laptop for an hour, wake it, recheck pages and images.
- **E, scale:** run on your largest file. Note load time and whether Figma slows down or crashes.
- **F, two files:** prepare two files in two tabs (try Quick prepare on the second). Wi-Fi off, check both.

Whichever of B or C keeps images sharp stays; the other gets removed. If neither works, image warm-up is removed and the checklist says images may be blurry offline.

## Decisions

- 2026-10-12, U4: target files are Figma Design files, not Slides. `editorType` stays `["figma"]`.
- 2026-10-12: user chose to skip Test A for now and go ahead with Phase 1. Test A is still needed before publishing.

## Research (2026-10-12, no hands-on test)

Verdict: unclear, leaning towards "likely works" for page content. No source confirms or rules it out.

- Help center says offline you get "the current page and any other pages that were loaded during the session". It doesn't say whether a plugin load counts. https://help.figma.com/hc/en-us/articles/360040328553
- `loadAllPagesAsync` "loads all pages of the document into memory". It doesn't mention offline. https://developers.figma.com/docs/plugins/api/figma/#loadallpagesasync
- A forum thread suggested exactly this trick for commuters but nobody reported back. https://forum.figma.com/t/dynamically-loading-files-bad-for-commuters/74390
- No existing Community plugin claims to do this.
- Images: Figma fetches high-res images only for what's on screen, so images on pages you never looked at will probably be low-res offline (Phase 2 tries to fix this).
- Memory: each tab has roughly a 2 GB limit, so loading every page of a huge file could crash it. The page picker is the fallback.
