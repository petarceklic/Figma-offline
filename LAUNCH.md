# Launch checklist

## 1. Before anything goes public

- [ ] Run the image test (README > Known limitations). If images are still blurry, tell Claude before launching.
- [ ] Run it once on your biggest file to make sure it doesn't crash.

## 2. Publish on Figma Community

Full field-by-field copy is in `LISTING.md`.

- [ ] Turn on two-factor authentication on your Figma account.
- [ ] Figma desktop app: Plugins > Development > Offline Prep > ... > **Publish**.
- [ ] Paste the listing copy, upload `assets/icon.png`, `assets/thumbnail.png`, `assets/carousel-1.png`, `assets/carousel-2.png`. Set it to free.
- [ ] Submit for review and wait for approval (usually a few days, sometimes longer).
- [ ] After publishing, Figma writes a real `id` into `manifest.json`. Commit it.
- [ ] Put the Community link in `README.md` under Install (replace "listing coming soon").

## 3. Make the GitHub repo public (done)

Lets people check the code themselves, which builds trust for a plugin that touches every page.

- [x] Repo made public.
- [x] Description and topics set.

## 4. Record a short demo

A 10 to 15 second screen recording does far more on Twitter than a still image.

1. Open a big file. Start recording (Cmd+Shift+5 on Mac).
2. Run Offline Prep and let the progress toasts play through to "Ready for offline".
3. Turn Wi-Fi off (show the menu bar), then click through a few pages to show they open.
4. Trim to under 20 seconds.

## 5. Tweet

**Now (links to GitHub)**

> Heading to Vietnam, opened my Figma file mid-flight to get some work done. First page loaded. Every other page: "unavailable offline."
>
> Surprised there's no real fix for this, so I built one. Free plugin, one click before you fly, and it loads every page and image in your file.
>
> ✈️ github.com/petarceklic/Figma-offline

**Later, once the Community listing is live** (swap in the link). Use the demo video, or `assets/thumbnail.png` if you skip the video.

**Option A (short)**

> Figma only loads the page you're looking at. Go offline on a flight and the rest of your file is gone.
>
> I made a free plugin that fixes it in one click: it loads every page and every image before you lose Wi-Fi.
>
> Offline Prep: [Community link]

**Option B (story)**

> Opened my Figma file on a flight. Page 1 worked. Every other page: unavailable.
>
> So I built Offline Prep. Run it before you leave, it loads every page and image in the file, done. Free, no settings, never touches your design.
>
> [Community link]

**Option C (thread starter)**

> Tip for anyone who works in Figma while travelling 🧵
>
> Figma loads pages on demand now, so offline you only get the pages you've opened. Here's a free one-click fix 👇

Reply in the thread with the demo and the link, plus: "Keep the tab open. Figma can't reopen files offline."

Tag @figma; they sometimes share community plugins.
