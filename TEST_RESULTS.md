# Test results

| Test | Date | File (pages / size) | Result | Notes |
|------|------|---------------------|--------|-------|
| Baseline (no plugin) | | | | |
| A: pages | | | | |

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
