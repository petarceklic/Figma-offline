# Community listing (ready to paste)

Everything you need for Figma's publish screen. Nothing has been published: you submit it.

## Basics

- **Name:** Offline Prep
- **Tagline:** Load every page before you lose Wi-Fi
- **Category:** Design tools
- **Price:** Free (once paid it can't go free again, so keep it free)
- **Icon:** `assets/icon.png` (128 x 128)
- **Thumbnail:** `assets/thumbnail.png` (1920 x 1080)
- **Carousel:** `assets/carousel-1.png` (boarding pass), `assets/carousel-2.png` (before/after), `assets/carousel-3.png` (pre-flight checklist)
- **Demo video/GIF (optional):** a 10 second screen recording of you running it on a real file.

## Description

You're on the plane, laptop open, three hours to finally get through that redesign. Page one loads. Page two: unavailable offline. And the images you can see are blurry smudges.

Figma only loads the page you're looking at, and only downloads full-quality images for what's on screen. Everything else stays in the cloud.

Offline Prep fixes that in one click. Run it while you're still online: it loads every page and downloads every image in the file, then tells you when you're ready.

**One click, no settings.** Run it from the plugins menu and watch the progress.

**Taking several files?** Run it in each one and keep the tabs open.

**Safe by design**
- Never edits your file or moves your view.
- No network access, no data collected, nothing stored.

**Good to know**
- Keep each prepared file's tab open. Figma can't reopen files offline.
- Library search, plugin installs and fonts you haven't installed won't work offline. That's a Figma limit.

## Data security disclosure

| Question | Answer |
|---|---|
| Does the plugin access the network? | No. The manifest declares `networkAccess: none`. |
| Does it collect, store or transmit user data? | No. It stores nothing at all. |
| Does it modify file content? | No. It only loads pages and requests image data that Figma already holds for the file. |
| Third-party services or analytics? | None. |
| Authentication? | None. |

## Before you submit

1. Turn on two-factor authentication on your Figma account (required to publish).
2. In the Figma desktop app: Plugins > Development > Offline Prep > ... > **Publish**. Figma gives the plugin a real `id` and writes it into `manifest.json`; commit that change.
3. Fill in the fields above, upload the images, submit for review.
