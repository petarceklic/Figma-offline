# Test results

| Test | Date | File (pages / size) | Result | Notes |
|------|------|---------------------|--------|-------|
| A: pages | 2026-10-12 | Real file, 44 pages | **Pass** | Earlier pages-only build, 44/44 loaded in 8.8s. Offline: every page opened, editing worked. Images on unvisited pages were blurry/pixelated offline (low-res versions only); vector content and text sharp. So page loading alone doesn't fetch high-res images. Sync after reconnecting not yet reported. |
| B: images | | | | |
| C: 1 hour asleep offline | | | | |
| D: largest file | | | | |
| E: two files | | | | |

## Simulated tests (fake Figma API, not real Figma)

One-click version, all passed: loads every non-divider page; one failing page is reported without stopping the rest; finds image fills in nested layers and downloads each unique image once; never opens a panel; always closes when done.

## Real-Figma test plan

Restart Figma before each test. Use duplicates of real, image-heavy files in the desktop app.

- **B, images:** open the file, stay on page 1, run Offline Prep, wait for "Ready for offline". Wi-Fi off. On pages you haven't opened, zoom into images at 100% and 200%. Sharp or blurry? (Test A showed they're blurry with pages-only loading.) *If still blurry, bring back the fly-through approach from git history, which zooms to each frame.*
- **C, endurance:** after preparing, Wi-Fi off, close the laptop for an hour, wake it, recheck pages and images.
- **D, scale:** run on your largest file. Note time and whether Figma slows down or crashes.
- **E, two files:** prepare two files in two tabs. Wi-Fi off, check both.
