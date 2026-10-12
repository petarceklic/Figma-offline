"""Builds listing images (icon, thumbnail, carousel) with headless Chrome.

Run from the project root:  python3 assets/src/build.py
The toasts and plugin menu shown are HTML mock-ups of the Figma UI.
"""
import base64, os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets', 'src')
OUT = os.path.join(ROOT, 'assets')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

ICON_SVG = open(os.path.join(SRC, 'icon.svg')).read()


ICON_URI = 'data:image/svg+xml;base64,' + base64.b64encode(ICON_SVG.encode()).decode()


def icon(size):
    return f'<img src="{ICON_URI}" width="{size}" height="{size}" style="display:block">'


def toast(text, progress=None):
    bar = ''
    if progress is not None:
        bar = (f'<div style="height:6px;border-radius:3px;background:#444;margin-top:16px;overflow:hidden">'
               f'<div style="height:100%;width:{progress}%;background:#0d99ff"></div></div>')
    return (f'<div style="background:#2c2c2c;color:#fff;border-radius:14px;padding:22px 30px;width:620px;'
            f'font:500 26px/1.35 Inter,sans-serif;box-shadow:0 20px 60px rgba(0,0,0,.35)">{text}{bar}</div>')


def plugin_menu():
    return f'''<div style="width:620px;background:#2c2c2c;border-radius:16px;padding:18px;color:#fff;
  font:500 26px Inter,sans-serif;box-shadow:0 30px 80px rgba(0,0,0,.35)">
  <div style="background:#383838;border-radius:10px;padding:14px 18px;color:#999">Search</div>
  <div style="display:flex;align-items:center;gap:16px;background:#3a3a3a;border-radius:10px;padding:16px 18px;
    margin-top:14px;box-shadow:0 0 0 3px #0d99ff">
    <div style="width:44px;height:44px">{icon(44)}</div><div>Offline Prep</div>
  </div>
</div>'''


BASE_CSS = '''
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, -apple-system, system-ui, sans-serif; color: #0B1F33; }
.eyebrow { font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #0A6FD6; }
h1 { margin: 0; font-weight: 750; letter-spacing: -0.03em; line-height: 1.02; }
p.lead { color: #3D5266; line-height: 1.35; }
.pill { display: inline-flex; align-items: center; padding: 10px 18px; border-radius: 999px;
  background: #fff; box-shadow: 0 0 0 1px rgba(11,31,51,.1); font-weight: 600; color: #3D5266; }
'''


def page(body, w, h):
    return f'''<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;750&display=swap" rel="stylesheet">
<style>{BASE_CSS} body {{ width:{w}px; height:{h}px; overflow:hidden; }}</style>
{body}'''


DONE = 'Ready for offline: 44/44 pages and 212 images in 41s. Keep this tab open.'

THUMB = page(f'''
<div style="position:absolute;inset:0;background:linear-gradient(135deg,#EAF5FF 0%,#D6ECFF 55%,#BFE0FF 100%)"></div>
<div style="position:absolute;left:150px;top:0;bottom:0;width:990px;display:flex;flex-direction:column;justify-content:center">
  <div style="display:flex;align-items:center;gap:24px;margin-bottom:48px">
    <div style="width:96px;height:96px">{icon(96)}</div>
    <div class="eyebrow" style="font-size:28px">Offline Prep</div>
  </div>
  <h1 style="font-size:86px">Load every page<br>before you lose Wi-Fi.</h1>
  <p class="lead" style="font-size:36px;margin:40px 0 48px;max-width:800px">One click downloads every page and every image in a big Figma file, ready for your flight.</p>
  <div style="display:flex;gap:16px">
    <span class="pill" style="font-size:24px">One click</span>
    <span class="pill" style="font-size:24px">No network access</span>
    <span class="pill" style="font-size:24px">Never edits your file</span>
  </div>
</div>
<div style="position:absolute;left:1180px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:28px">
  {toast('Loading page 31 of 44: Checkout', 70)}
  {toast('Downloading image 96 of 212', 45)}
  {toast(DONE)}
</div>
''', 1920, 1080)

CAROUSEL_1 = page(f'''
<div style="position:absolute;inset:0;background:#F4F8FC"></div>
<div style="position:absolute;left:140px;top:0;bottom:0;width:820px;display:flex;flex-direction:column;justify-content:center">
  <div class="eyebrow" style="font-size:26px;margin-bottom:28px">How it works</div>
  <h1 style="font-size:96px">Run it once.<br>That's it.</h1>
  <p class="lead" style="font-size:34px;margin-top:36px;max-width:720px">Pick Offline Prep from your plugins. It loads every page, downloads every image, and tells you when you're ready.</p>
</div>
<div style="position:absolute;left:1160px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:40px">
  {plugin_menu()}
  {toast(DONE)}
</div>
''', 1920, 1080)

CAROUSEL_2 = page('''
<div style="position:absolute;inset:0;background:#0B1F33"></div>
<div style="position:absolute;left:140px;top:0;bottom:0;width:1300px;display:flex;flex-direction:column;justify-content:center;color:#fff">
  <div class="eyebrow" style="font-size:26px;margin-bottom:28px;color:#7CC4F8">Before you board</div>
  <h1 style="font-size:96px">Run it in every file<br>you're taking.</h1>
  <p class="lead" style="font-size:34px;margin-top:36px;max-width:1000px;color:#B8C7D6">Then keep those tabs open, because Figma can't reopen files offline. Check your fonts are installed and the library components you need are already in the file.</p>
</div>
''', 1920, 1080)

JOBS = [('icon.png', page(ICON_SVG, 128, 128), 128, 128), ('thumbnail.png', THUMB, 1920, 1080),
        ('carousel-1.png', CAROUSEL_1, 1920, 1080), ('carousel-2.png', CAROUSEL_2, 1920, 1080)]

with tempfile.TemporaryDirectory() as tmp:
    for name, html, w, h in JOBS:
        src = os.path.join(tmp, name + '.html')
        open(src, 'w').write(html)
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                        '--default-background-color=00000000', f'--window-size={w},{h}', '--virtual-time-budget=4000',
                        f'--screenshot={os.path.join(OUT, name)}', 'file://' + src],
                       check=True, capture_output=True)
        print('wrote', os.path.join('assets', name))
