"""Builds listing images (icon, thumbnail, carousel) with headless Chrome.

Run from the project root:  python3 assets/src/build.py
Concept: you're on the plane. Cabin window, boarding pass, before/after, pre-flight card.
UI shown (page lists, toasts) are HTML mock-ups of the Figma UI.
"""
import base64, os, random, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets', 'src')
OUT = os.path.join(ROOT, 'assets')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

ICON_SVG = open(os.path.join(SRC, 'icon.svg')).read()
ICON_URI = 'data:image/svg+xml;base64,' + base64.b64encode(ICON_SVG.encode()).decode()

# ---------- palette ----------
NAVY = '#0E1A3A'
INK = '#1B2547'
CREAM = '#FBF6EE'
SUNSET = '#F2704A'
GOLD = '#FFC56E'
MINT = '#34D399'
MUTED = '#6B7390'

PLANE = ('<path d="M0 -15 C2 -15 3 -13 3 -10 L3 -3 L14 4 L14 7 L3 3.5 L3 9 L7 12 L7 14.5 L0 12.5 L-7 14.5 '
         'L-7 12 L-3 9 L-3 3.5 L-14 7 L-14 4 L-3 -3 L-3 -10 C-3 -13 -2 -15 0 -15 Z"/>')


def plane(size, color, rotate=90):
    return (f'<svg width="{size}" height="{size}" viewBox="-16 -16 32 32" style="display:block">'
            f'<g transform="rotate({rotate})" fill="{color}">{PLANE}</g></svg>')


def check(size=28, bg=MINT, fg='#06281B'):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" style="display:block;flex-shrink:0">'
            f'<circle cx="12" cy="12" r="12" fill="{bg}"/>'
            f'<path d="M7 12.5l3.2 3.2L17 9" fill="none" stroke="{fg}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def cloud_off(size=28, color='#8A8F9E'):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" style="display:block;flex-shrink:0">'
            f'<path d="M7 18h10a4 4 0 0 0 .7-7.94A6 6 0 0 0 6.2 9.1 4.5 4.5 0 0 0 7 18z"/>'
            f'<path d="M3 3l18 18"/></svg>')


def stars(n, w, h, seed, max_size=3, opacity=(0.3, 0.9)):
    rnd = random.Random(seed)
    dots = []
    for _ in range(n):
        x, y, s = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(1, max_size)
        o = rnd.uniform(*opacity)
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s / 2:.1f}" fill="#fff" opacity="{o:.2f}"/>')
    return f'<svg width="{w}" height="{h}" style="position:absolute;inset:0">{"".join(dots)}</svg>'


def clouds(seed, w, h, count=14, color='#fff', opacity=0.95, blur=6):
    rnd = random.Random(seed)
    puffs = []
    for _ in range(count):
        cw = rnd.uniform(0.25, 0.55) * w
        ch = cw * rnd.uniform(0.35, 0.55)
        x = rnd.uniform(-0.15, 0.95) * w
        y = h - ch * rnd.uniform(0.3, 0.9)
        puffs.append(f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{cw:.0f}px;height:{ch:.0f}px;'
                     f'border-radius:50%;background:{color};opacity:{opacity}"></div>')
    return (f'<div style="position:absolute;inset:0;filter:blur({blur}px)">{"".join(puffs)}</div>')


def barcode(seed, w, h, color=NAVY):
    rnd = random.Random(seed)
    x, bars = 0, []
    while x < w:
        bw = rnd.choice([2, 2, 3, 4, 6])
        if rnd.random() > 0.35:
            bars.append(f'<rect x="{x}" y="0" width="{bw}" height="{h}" fill="{color}"/>')
        x += bw + rnd.choice([2, 3, 4])
    return f'<svg width="{w}" height="{h}" style="display:block">{"".join(bars)}</svg>'


def flight_path(w, h, d, dash='2 14', color='rgba(255,255,255,.5)', width=3):
    return (f'<svg width="{w}" height="{h}" style="position:absolute;inset:0;overflow:visible">'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}" '
            f'stroke-linecap="round"/></svg>')


# ---------- shared pieces ----------
BASE_CSS = f'''
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: Inter, system-ui, sans-serif; color: {NAVY}; -webkit-font-smoothing: antialiased; }}
.abs {{ position: absolute; }}
.mono {{ font-family: "JetBrains Mono", ui-monospace, monospace; letter-spacing: .04em; }}
.serif {{ font-family: "Instrument Serif", Georgia, serif; font-style: italic; font-weight: 400; letter-spacing: -0.01em; }}
.eyebrow {{ font-family: "JetBrains Mono", monospace; font-size: 22px; font-weight: 500; letter-spacing: .14em;
  text-transform: uppercase; display: flex; align-items: center; gap: 14px; }}
h1 {{ margin: 0; font-weight: 800; letter-spacing: -0.045em; line-height: .98; }}
.lead {{ line-height: 1.4; letter-spacing: -0.01em; }}
.chip {{ font-family: "JetBrains Mono", monospace; font-size: 20px; font-weight: 500; letter-spacing: .06em;
  padding: 12px 18px; border-radius: 999px; display: inline-flex; align-items: center; gap: 10px; }}
'''

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800'
         '&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">')


def page(body, w, h, bg='#fff'):
    return (f'<!doctype html><meta charset="utf-8">{FONTS}<style>{BASE_CSS} '
            f'body {{ width:{w}px; height:{h}px; overflow:hidden; position:relative; background:{bg}; }}</style>{body}')


def logo_lockup(color, size=64):
    return (f'<div style="display:flex;align-items:center;gap:18px">'
            f'<img src="{ICON_URI}" width="{size}" height="{size}" style="display:block;border-radius:{size * .22:.0f}px;'
            f'box-shadow:0 8px 24px rgba(10,30,80,.25)">'
            f'<div style="font-weight:700;font-size:{size * .44:.0f}px;letter-spacing:-0.02em;color:{color}">Offline Prep</div></div>')


PAGES = ['Cover', 'Onboarding', 'Home feed', 'Search', 'Checkout', 'Profile & settings', 'Components', 'Archive']


def pages_panel(width, mode, title='Pages', footer=True):
    """Figma-style dark page list. mode: 'ready' (all ticked) or 'before' (only first page available)."""
    rows = []
    for i, name in enumerate(PAGES):
        if mode == 'ready':
            icon, color, note = check(26), '#F2F2F2', ''
        elif i == 0:
            icon, color, note = check(26, '#3A3A3A', '#BDBDBD'), '#F2F2F2', ''
        else:
            icon, color, note = cloud_off(26, '#6E6E6E'), '#6E6E6E', '<span style="font-size:17px;color:#6E6E6E">Unavailable offline</span>'
        current = ' <span style="color:#8C8C8C;font-size:17px">(current)</span>' if i == 0 else ''
        rows.append(f'<div style="display:flex;align-items:center;gap:16px;padding:13px 26px">{icon}'
                    f'<span style="flex:1;color:{color};font-size:22px;font-weight:500">{name}{current}</span>{note}</div>')
    foot = ''
    if footer and mode == 'ready':
        foot = (f'<div style="margin:10px 16px 16px;padding:18px 20px;border-radius:14px;background:#0D99FF;color:#fff;'
                f'font-size:20px;font-weight:600;display:flex;align-items:center;gap:12px">'
                f'{plane(24, "#fff", 45)}Ready for offline · 44/44 pages · 212 images</div>')
    return (f'<div style="width:{width}px;background:#1E1E1E;border-radius:22px;overflow:hidden;'
            f'box-shadow:0 40px 90px rgba(8,14,40,.45),0 0 0 1px rgba(255,255,255,.06)">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:22px 26px 12px;'
            f'color:#fff;font-size:20px;font-weight:600">{title}<span style="color:#8C8C8C;font-weight:500">44</span></div>'
            f'{"".join(rows)}{foot}</div>')


# ---------- thumbnail: cabin window at sunset ----------
def porthole(w, h):
    frame = 44
    inner_w, inner_h = w - frame * 2, h - frame * 2
    sky = (f'linear-gradient(180deg,#141C4A 0%,#2B2F7A 30%,#7A4F9E 55%,{SUNSET} 78%,{GOLD} 100%)')
    return f'''
<div style="width:{w}px;height:{h}px;border-radius:{w / 2:.0f}px / {w / 2.1:.0f}px;
  background:linear-gradient(160deg,#FFFFFF 0%,#ECE6DC 45%,#D9D1C4 100%);
  box-shadow:0 50px 100px rgba(0,0,0,.5), inset 0 2px 0 rgba(255,255,255,.9), inset 0 -6px 18px rgba(80,60,30,.18);
  position:relative">
  <div style="position:absolute;left:{frame}px;top:{frame}px;width:{inner_w}px;height:{inner_h}px;
    border-radius:{inner_w / 2:.0f}px / {inner_w / 2.15:.0f}px;overflow:hidden;background:{sky};
    box-shadow:inset 0 12px 40px rgba(0,0,0,.45)">
    {stars(40, inner_w, inner_h * 0.45, 7, 3)}
    <div style="position:absolute;left:{inner_w * .62:.0f}px;top:{inner_h * .58:.0f}px;width:110px;height:110px;border-radius:50%;
      background:radial-gradient(circle,#FFE7B0 0%,#FFC56E 45%,rgba(255,197,110,0) 72%)"></div>
    <div style="position:absolute;left:0;right:0;bottom:{inner_h * .08:.0f}px;height:{inner_h * .40:.0f}px">{clouds(3, inner_w, inner_h * .40, 26, '#FFD9C2', .9, 9)}</div>
    <div style="position:absolute;left:0;right:0;bottom:0;height:{inner_h * .30:.0f}px">{clouds(11, inner_w, inner_h * .30, 24, '#FFF4EC', 1, 6)}</div>
    <div style="position:absolute;left:0;right:0;bottom:0;height:{inner_h * .14:.0f}px;background:#FFF4EC;filter:blur(4px)"></div>
    <div style="position:absolute;left:0;right:0;top:0;height:{inner_h * .16:.0f}px;
      background:linear-gradient(180deg,#F3EEE6,#E2DACD);box-shadow:0 6px 16px rgba(0,0,0,.25)">
      <div style="position:absolute;left:50%;bottom:10px;width:70px;height:10px;margin-left:-35px;border-radius:5px;background:#CFC6B7"></div>
    </div>
    <div style="position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.18) 0%,rgba(255,255,255,0) 38%)"></div>
  </div>
</div>'''


def night_sky(seed, path, glow_x='50%'):
    return (f'<div class="abs" style="inset:0;background:radial-gradient(1400px 800px at {glow_x} 115%,#4A3B8F 0%,#1B2357 45%,#0A1030 100%)"></div>'
            + stars(90, 1920, 600, seed, 3, (0.15, 0.7))
            + flight_path(1920, 1080, path, '2 16', 'rgba(255,255,255,.22)'))


THUMB = page(f'''
{night_sky(31, 'M -40 1010 C 300 960, 600 1040, 900 980 S 1400 1000, 1980 940', '70%')}

<div class="abs" style="left:1150px;top:96px">{porthole(620, 860)}</div>
<div class="abs" style="left:930px;top:470px">{pages_panel(540, 'ready')}</div>

<div class="abs" style="left:140px;top:0;bottom:0;width:780px;display:flex;flex-direction:column;justify-content:center">
  <div style="margin-bottom:64px">{logo_lockup('#fff', 72)}</div>
  <h1 style="font-size:108px;color:#fff">Your whole file,</h1>
  <div class="serif" style="font-size:132px;line-height:1;color:{GOLD};margin-top:4px">at 35,000 feet.</div>
  <p class="lead" style="font-size:34px;color:rgba(255,255,255,.7);margin:44px 0 52px;max-width:640px">
    One click before you board loads every page and image. No Wi-Fi needed.</p>
  <div style="display:flex;gap:14px">
    <span class="chip" style="background:{GOLD};color:{NAVY}">FREE</span>
    <span class="chip" style="background:rgba(255,255,255,.10);color:#fff">ONE CLICK</span>
    <span class="chip" style="background:rgba(255,255,255,.10);color:#fff">NEVER EDITS YOUR FILE</span>
  </div>
</div>
''', 1920, 1080)


# ---------- carousel 1: boarding pass ----------
def field(label, value, size=40, color=NAVY, mono=True):
    cls = 'mono' if mono else ''
    weight = 700 if mono else 600
    return (f'<div><div class="mono" style="font-size:16px;letter-spacing:.16em;color:{MUTED};margin-bottom:10px">{label}</div>'
            f'<div class="{cls}" style="font-size:{size}px;font-weight:{weight};color:{color};letter-spacing:{".02em" if mono else "-0.02em"}">{value}</div></div>')


def boarding_pass():
    notch = 'radial-gradient(circle at 0 0, transparent 0, transparent 0)'
    return f'''
<div style="display:flex;filter:drop-shadow(0 50px 80px rgba(0,0,0,.45))">
  <div style="width:1040px;height:520px;background:{CREAM};border-radius:32px 0 0 32px;position:relative;padding:48px 56px;
    -webkit-mask:radial-gradient(circle 26px at 100% 0,transparent 98%,#000) top/100% 51% no-repeat,
                 radial-gradient(circle 26px at 100% 100%,transparent 98%,#000) bottom/100% 51% no-repeat">
    <div style="display:flex;justify-content:space-between;align-items:center">
      {logo_lockup(NAVY, 52)}
      <div class="mono" style="font-size:18px;letter-spacing:.2em;color:{MUTED}">BOARDING PASS</div>
    </div>
    <div style="display:flex;align-items:center;gap:40px;margin:44px 0 40px">
      <div><div class="mono" style="font-size:16px;letter-spacing:.16em;color:{MUTED}">FROM</div>
        <div style="font-size:112px;font-weight:800;letter-spacing:-0.05em;line-height:1">ON</div>
        <div style="font-size:20px;color:{MUTED};margin-top:6px">Online</div></div>
      <div style="flex:1;display:flex;align-items:center;gap:16px">
        <div style="flex:1;border-top:3px dashed rgba(14,26,58,.25)"></div>{plane(56, SUNSET, 90)}
        <div style="flex:1;border-top:3px dashed rgba(14,26,58,.25)"></div></div>
      <div style="text-align:right"><div class="mono" style="font-size:16px;letter-spacing:.16em;color:{MUTED}">TO</div>
        <div style="font-size:112px;font-weight:800;letter-spacing:-0.05em;line-height:1">OFF</div>
        <div style="font-size:20px;color:{MUTED};margin-top:6px">Offline</div></div>
    </div>
    <div style="display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr;gap:28px;border-top:2px solid rgba(14,26,58,.08);padding-top:32px">
      {field('PASSENGER', 'Mobile app redesign', 34, NAVY, False)}
      {field('PAGES', '44/44')}
      {field('IMAGES', '212')}
      {field('WI-FI', 'NONE', 40, SUNSET)}
    </div>
  </div>
  <div style="width:3px;background:repeating-linear-gradient(180deg,rgba(14,26,58,.25) 0 10px,transparent 10px 20px);
    background-color:{CREAM};margin:26px 0"></div>
  <div style="width:300px;height:520px;background:{CREAM};border-radius:0 32px 32px 0;padding:48px 40px;
    display:flex;flex-direction:column;justify-content:space-between;
    -webkit-mask:radial-gradient(circle 26px at 0 0,transparent 98%,#000) top/100% 51% no-repeat,
                 radial-gradient(circle 26px at 0 100%,transparent 98%,#000) bottom/100% 51% no-repeat">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px">
      {field('SEAT', '14A', 36)}{field('GATE', 'PLUGINS', 24)}
      {field('BOARDS', 'NOW', 36, SUNSET)}{field('CLASS', 'FREE', 24)}
    </div>
    <div>{barcode(5, 220, 90)}</div>
  </div>
</div>'''


CAROUSEL_1 = page(f'''
{night_sky(21, 'M -40 980 C 400 900, 700 1000, 1100 860 S 1700 700, 1980 760')}
<div class="abs" style="left:0;right:0;top:110px;text-align:center;color:#fff">
  <div class="eyebrow" style="justify-content:center;color:{GOLD}">{plane(26, GOLD, 90)}How it works</div>
  <h1 style="font-size:88px;margin-top:26px">Your file’s <span class="serif" style="font-size:104px;color:{GOLD}">boarding pass.</span></h1>
  <p class="lead" style="font-size:30px;color:rgba(255,255,255,.7);margin:22px auto 0;max-width:1300px">
    Run Offline Prep once while you’re online. Every page and image comes with you.</p>
</div>
<div class="abs" style="left:270px;top:430px">{boarding_pass()}</div>
''', 1920, 1080)


# ---------- carousel 2: before / after ----------
def label(text, bg, fg):
    return (f'<div class="mono" style="display:inline-block;font-size:18px;font-weight:700;letter-spacing:.16em;'
            f'padding:10px 16px;border-radius:10px;background:{bg};color:{fg};margin-bottom:22px">{text}</div>')


CAROUSEL_2 = page(f'''
{night_sky(42, 'M -40 1020 C 500 960, 800 1060, 1200 990 S 1700 960, 1980 1000')}
<div class="abs" style="left:0;right:0;top:96px;text-align:center;color:#fff">
  <h1 style="font-size:92px">No more <span class="serif" style="font-size:108px;color:{GOLD}">“unavailable offline.”</span></h1>
  <p class="lead" style="font-size:30px;color:rgba(255,255,255,.7);margin:20px auto 0;max-width:1100px">
    Figma only loads the page you’re on. Offline Prep loads the rest.</p>
</div>
<div class="abs" style="left:250px;top:370px">
  {label('WITHOUT', 'rgba(255,255,255,.10)', 'rgba(255,255,255,.7)')}
  <div style="opacity:.85">{pages_panel(620, 'before', footer=False)}</div>
</div>
<div class="abs" style="left:928px;top:600px;width:64px;height:64px;border-radius:50%;background:{GOLD};
  display:flex;align-items:center;justify-content:center;box-shadow:0 14px 30px rgba(0,0,0,.4)">
  <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{NAVY}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
</div>
<div class="abs" style="left:1050px;top:370px">
  {label('WITH OFFLINE PREP', GOLD, NAVY)}
  {pages_panel(620, 'ready', footer=True)}
</div>
''', 1920, 1080)


# ---------- carousel 3: pre-flight safety card ----------
def step(n, title, body, icon_svg):
    return f'''
<div style="background:{CREAM};border-radius:28px;padding:40px 36px;box-shadow:0 30px 60px rgba(0,0,0,.35);
  display:flex;flex-direction:column;gap:22px;height:100%">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <div style="width:84px;height:84px;border-radius:22px;background:rgba(242,112,74,.12);display:flex;align-items:center;justify-content:center">{icon_svg}</div>
    <div class="mono" style="font-size:44px;font-weight:700;color:rgba(14,26,58,.12)">0{n}</div>
  </div>
  <div style="font-size:34px;font-weight:700;letter-spacing:-0.025em;line-height:1.1">{title}</div>
  <div style="font-size:23px;line-height:1.45;color:{MUTED}">{body}</div>
</div>'''


def line_icon(paths):
    return (f'<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="{SUNSET}" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg>')


ICON_PLAY = line_icon('<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 19h16"/>')
ICON_TABS = line_icon('<rect x="3" y="5" width="18" height="15" rx="2"/><path d="M3 9h18M7 5v4M12 5v4"/>')
ICON_FONT = line_icon('<path d="M5 19L11 5h2l6 14M8 14h8"/>')
ICON_COMP = line_icon('<path d="M12 3l4 4-4 4-4-4zM12 13l4 4-4 4-4-4zM7 8l4 4-4 4-4-4zM17 8l4 4-4 4-4-4z"/>')

CAROUSEL_3 = page(f'''
{night_sky(53, 'M -40 960 C 400 1040, 800 940, 1200 1010 S 1700 1050, 1980 980')}
<div class="abs" style="left:140px;right:140px;top:200px;display:flex;justify-content:space-between;align-items:flex-end;color:#fff">
  <div>
    <div class="eyebrow" style="color:{GOLD}">{plane(26, GOLD, 90)}Before you board</div>
    <h1 style="font-size:96px;margin-top:24px">Pre-flight <span class="serif" style="font-size:112px;color:{GOLD}">checklist.</span></h1>
  </div>
  <div class="mono" style="font-size:18px;letter-spacing:.16em;color:rgba(255,255,255,.5);text-align:right;line-height:1.7">
    SAFETY CARD<br>OFFLINE PREP · FIGMA</div>
</div>
<div class="abs" style="left:140px;right:140px;top:530px;height:350px;display:grid;grid-template-columns:repeat(4,1fr);gap:28px">
  {step(1, 'Run it in every file', 'One click per file while you’re still online. Pages and images load in seconds.', ICON_PLAY)}
  {step(2, 'Keep the tabs open', 'Figma can’t reopen a closed file offline. Leave each prepared tab open.', ICON_TABS)}
  {step(3, 'Fonts on board', 'Make sure the fonts your file uses are installed on this computer.', ICON_FONT)}
  {step(4, 'Pack components', 'Library search needs Wi-Fi, so place any components you’ll need first.', ICON_COMP)}
</div>
''', 1920, 1080)


# ---------- icon ----------
ICON = page(ICON_SVG, 128, 128, 'transparent')

JOBS = [('icon.png', ICON, 128, 128), ('thumbnail.png', THUMB, 1920, 1080),
        ('carousel-1.png', CAROUSEL_1, 1920, 1080), ('carousel-2.png', CAROUSEL_2, 1920, 1080),
        ('carousel-3.png', CAROUSEL_3, 1920, 1080)]

if __name__ == '__main__':
    import sys
    only = set(sys.argv[1:])
    with tempfile.TemporaryDirectory() as tmp:
        for name, html, w, h in JOBS:
            if only and name not in only:
                continue
            src = os.path.join(tmp, name + '.html')
            open(src, 'w').write(html)
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            '--default-background-color=00000000', f'--window-size={w},{h}', '--virtual-time-budget=5000',
                            f'--screenshot={os.path.join(OUT, name)}', 'file://' + src],
                           check=True, capture_output=True)
            print('wrote', os.path.join('assets', name))
