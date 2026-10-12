# Test results

| Test | Date | File (pages / size) | Result | Notes |
|------|------|---------------------|--------|-------|
| Baseline (no plugin) | | | | |
| A: pages | 2026-10-12 | Real file, 44 pages | **Pass** | Quick prepare, 44/44 loaded in 8.8s. Offline: every page opened, editing worked. Images on unvisited pages were blurry/pixelated offline (low-res versions only); vector content and text sharp. So page loading alone doesn't fetch high-res images. Sync after reconnecting not yet reported. |
| B: images (one-click version) | | | | |
| D: 1 hour asleep offline | | | | |
| E: largest file | | | | |
| F: two files | | | | |

## Simulated tests (2026-10-12, fake Figma API, not real Figma)

All passed: page loading with progress; one failing page reported without stopping the rest; fly-through visits frames (and frames inside sections) and restores page and view; cancel and close mid-fly-through both restore the view; fetch mode finds and fetches unique images; settings and unticked pages remembered after reopening; quick prepare; prepared-recently list across two files; light and dark theme; panel layout with everything expanded.

## Real-Figma test plan (one-click version)

Restart Figma before each test. Use duplicates of real, image-heavy files in the desktop app.

- **B, images:** open the file, stay on page 1, run Offline Prep, wait for "Ready for offline". Wi-Fi off. On pages you haven't opened, zoom into images at 100% and 200%. Sharp or blurry? (Test A showed they're blurry with pages-only loading.) *If still blurry, bring back the fly-through approach from git history, which zooms to each frame.*
- **D, endurance:** after preparing, Wi-Fi off, close the laptop for an hour, wake it, recheck pages and images.
- **E, scale:** run on your largest file. Note time and whether Figma slows down or crashes.
- **F, two files:** prepare two files in two tabs. Wi-Fi off, check both.
