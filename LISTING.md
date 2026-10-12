# Community listing (ready to paste)

Everything you need to fill in on Figma's publish screen. Claude didn't publish anything: you submit it.

## Basics

- **Name:** Offline Prep
- **Tagline:** Load every page before you lose Wi-Fi
- **Category:** Design tools
- **Price:** Free (can't be changed to paid later without approved-creator status, so keep it free)
- **Icon:** `assets/icon.png` (128 x 128)
- **Thumbnail:** `assets/thumbnail.png` (1920 x 1080)
- **Carousel:** `assets/carousel-1.png`, `assets/carousel-2.png`
- **Demo GIF/video:** not made yet. Record a 10 to 20 second screen capture of the plugin running on a real file (needs Figma, so it's yours to do).

## Description

Figma only loads the page you're looking at. Go offline on a flight or a train and every page you haven't opened is unavailable.

Offline Prep fixes that in one click. Run it while you're still online and it loads every page in the file, so they're there when the Wi-Fi drops.

**What it does**
- Loads every page, or just the ones you tick, with live progress.
- Optional image warm-up: flies through every frame so Figma fetches sharp images, or asks Figma to download image data directly. (Experimental.)
- Lists the files you've prepared recently, handy when you're taking several files on a trip.
- Quick prepare: a menu command that loads every page with no panel.
- Pre-flight checklist for the things no plugin can fix: keep the tab open, install fonts, place library components.

**What it doesn't do**
- It never edits your file.
- It has no network access and collects no data.
- It can't reopen a closed file offline or search libraries offline. Those are Figma limits.

**Tips**
- Keep each prepared file's tab open. Files can't be reopened offline.
- Turn Wi-Fi off for a moment to check before you leave.

## Data security disclosure

Answers for Figma's optional data security form:

| Question | Answer |
|---|---|
| Does the plugin access the network? | No. The manifest declares `networkAccess: none`. |
| Does it collect, store or transmit user data? | No. It stores only its own settings (image mode, time per frame, which pages you unticked per file name, and a list of the last 10 prepared file names) locally via `figma.clientStorage`, on your computer. Nothing leaves the device. |
| Does it modify file content? | No. It only loads pages, and during the optional fly-through it moves the viewport and current page, then restores them. |
| Third-party services or analytics? | None. |
| Authentication? | None. |

## Before you submit

1. Turn on two-factor authentication on your Figma account (required to publish).
2. In the Figma desktop app: Plugins > Development > right-click Offline Prep > Publish. Figma replaces the `id` in `manifest.json` with a real one; commit that change.
3. Fill in the fields above, upload the images, submit for review.
