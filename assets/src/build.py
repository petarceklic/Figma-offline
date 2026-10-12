"""Builds listing images (icon, thumbnail, carousel) with headless Chrome.

Run from the project root:  python3 assets/src/build.py
The plugin panel shown in the images is the real ui.html, fed mock data.
"""
import json, os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'assets', 'src')
OUT = os.path.join(ROOT, 'assets')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

LIGHT = ":root{--figma-color-bg:#fff;--figma-color-bg-hover:#f5f5f5;--figma-color-bg-secondary:#eee;--figma-color-bg-brand:#0d99ff;--figma-color-bg-warning-tertiary:#fff1e3;--figma-color-text:#000000e6;--figma-color-text-secondary:#00000080;--figma-color-text-tertiary:#0000004d;--figma-color-text-brand:#007be5;--figma-color-text-onbrand:#fff;--figma-color-text-success:#14ae5c;--figma-color-text-warning:#b86200;--figma-color-text-danger:#dc3412;--figma-color-border:#e6e6e6}"

PAGES = ['Cover', '---', 'FLOWS', 'Onboarding', 'Home feed', 'Search', 'Checkout', 'Profile & settings',
         '---', 'SYSTEM', 'Components', 'Icons', 'Illustrations', '---', 'ARCHIVE', 'Explorations Q2']


def page_list():
    out = []
    for i, n in enumerate(PAGES):
        divider = n == '---' or (n.isupper() and len(n) > 3)
        out.append({'id': f'p{i}', 'name': n, 'isDivider': divider})
    return out


def panel_srcdoc(script):
    ui = open(os.path.join(ROOT, 'ui.html')).read()
    return f'<style>{LIGHT}</style>' + ui + f'<script>{script}</script>'


def panel_iframe(script, scale=1.0):
    doc = json.dumps(panel_srcdoc(script)).replace('</', '<\\/')
    return f'''<div class="panel" style="transform:scale({scale});transform-origin:top left">
  <div class="panel-bar"><span>Offline Prep</span><span>✕</span></div>
  <iframe id="f{abs(hash(script))}" style="width:360px;height:640px;border:0;display:block"></iframe>
  <script>document.currentScript.previousElementSibling.srcdoc = {doc};</script>
</div>'''


def init_msg(**extra):
    msg = {'type': 'init', 'fileName': 'Mobile app redesign', 'pages': page_list(), 'currentPageId': 'p0',
           'deselected': [], 'settings': {'imageMode': 'sweep', 'dwellMs': 1500}, 'prepared': []}
    msg.update(extra)
    return f'postMessage({{pluginMessage:{json.dumps(msg)}}},"*");'


NOW = 'Date.now()'
PREPARED = [{'name': 'Mobile app redesign', 'pages': 12, 'images': 'sweep'},
            {'name': 'Brand guidelines 2026', 'pages': 8, 'images': 'off'},
            {'name': 'Investor deck', 'pages': 21, 'images': 'fetch'}]


def prepared_js(ages_min=(0, 4, 11)):
    items = ','.join(
        f'{{name:{json.dumps(p["name"])},pages:{p["pages"]},images:"{p["images"]}",at:Date.now()-{m}*60000}}'
        for p, m in zip(PREPARED, ages_min))
    return f'[{items}]'


SCRIPT_PROGRESS = init_msg() + '''
document.getElementById('prepare').click();
postMessage({pluginMessage:{type:'progress',step:'sweep',done:17,total:38,label:'Checkout / Payment details'}},'*');
setTimeout(()=>{clearInterval(timer);document.getElementById('elapsed').textContent='41s';},50);
'''

SCRIPT_DONE = init_msg() + '''
setTimeout(()=>{postMessage({pluginMessage:{type:'done',loaded:12,total:12,pagesMs:9000,images:{mode:'sweep',count:38,ms:64000},failed:[],cancelled:false,ms:73000,prepared:%s}},'*');},10);
''' % prepared_js()

SCRIPT_CHECKLIST = init_msg() + '''
setTimeout(()=>{postMessage({pluginMessage:{type:'done',loaded:12,total:12,pagesMs:9000,images:null,failed:[],cancelled:false,ms:9000,prepared:%s}},'*');
const d=document.querySelectorAll('details'); d[0].open=true; d[1].open=true;
const cbs=document.querySelectorAll('.checklist input'); [0,1,2].forEach(i=>cbs[i].checked=true);
const f=document.querySelector('footer'); f.scrollTop=document.getElementById('prepared-box').offsetTop-f.offsetTop-10;},10);
''' % prepared_js()

BASE_CSS = '''
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, -apple-system, system-ui, sans-serif; color: #0B1F33; }
.panel { background: #fff; border-radius: 12px; overflow: hidden; width: 360px;
  box-shadow: 0 30px 80px rgba(11,31,51,.25), 0 0 0 1px rgba(11,31,51,.08); }
.panel-bar { display: flex; justify-content: space-between; padding: 10px 14px; font: 600 12px Inter, sans-serif;
  border-bottom: 1px solid #e6e6e6; background: #fff; color: #333; }
.eyebrow { font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #0A6FD6; }
h1 { margin: 0; font-weight: 750; letter-spacing: -0.03em; line-height: 1.02; }
p.lead { color: #3D5266; line-height: 1.35; }
.pill { display: inline-flex; gap: 10px; align-items: center; padding: 10px 18px; border-radius: 999px;
  background: #fff; box-shadow: 0 0 0 1px rgba(11,31,51,.1); font-weight: 600; color: #3D5266; }
'''

ICON_SVG = open(os.path.join(SRC, 'icon.svg')).read()


def page(body, w, h, extra_css=''):
    return f'''<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;750&display=swap" rel="stylesheet">
<style>{BASE_CSS} body {{ width:{w}px; height:{h}px; overflow:hidden; }} {extra_css}</style>
{body}'''


THUMB = page(f'''
<div style="position:absolute;inset:0;background:linear-gradient(135deg,#EAF5FF 0%,#D6ECFF 55%,#BFE0FF 100%)"></div>
<div style="position:absolute;left:150px;top:0;bottom:0;width:990px;display:flex;flex-direction:column;justify-content:center">
  <div style="display:flex;align-items:center;gap:24px;margin-bottom:48px">
    <div style="width:96px;height:96px">{ICON_SVG.replace('width="128" height="128"', 'width="96" height="96"')}</div>
    <div class="eyebrow" style="font-size:28px">Offline Prep</div>
  </div>
  <h1 style="font-size:86px">Load every page<br>before you lose Wi-Fi.</h1>
  <p class="lead" style="font-size:36px;margin:40px 0 48px;max-width:760px">One click gets a big, multi-page file ready for your flight. No more blank pages mid-air.</p>
  <div style="display:flex;gap:16px">
    <span class="pill" style="font-size:24px">No network access</span>
    <span class="pill" style="font-size:24px">Never edits your file</span>
  </div>
</div>
<div style="position:absolute;left:1180px;top:110px">{panel_iframe(SCRIPT_PROGRESS, 1.3)}</div>
''', 1920, 1080)

CAROUSEL_1 = page(f'''
<div style="position:absolute;inset:0;background:#F4F8FC"></div>
<div style="position:absolute;left:140px;top:0;bottom:0;width:820px;display:flex;flex-direction:column;justify-content:center">
  <div class="eyebrow" style="font-size:26px;margin-bottom:28px">Step 1</div>
  <h1 style="font-size:96px">Pick pages.<br>Click once.</h1>
  <p class="lead" style="font-size:34px;margin-top:36px;max-width:720px">Offline Prep loads every page you tick, then can fly through each frame so images stay sharp. Errors on one page never stop the rest.</p>
</div>
<div style="position:absolute;left:1180px;top:110px">{panel_iframe(SCRIPT_DONE, 1.3)}</div>
''', 1920, 1080)

CAROUSEL_2 = page(f'''
<div style="position:absolute;inset:0;background:#0B1F33"></div>
<div style="position:absolute;left:140px;top:0;bottom:0;width:820px;display:flex;flex-direction:column;justify-content:center;color:#fff">
  <div class="eyebrow" style="font-size:26px;margin-bottom:28px;color:#7CC4F8">Step 2</div>
  <h1 style="font-size:96px">Prep every file<br>for the trip.</h1>
  <p class="lead" style="font-size:34px;margin-top:36px;max-width:720px;color:#B8C7D6">See which files you've prepared, and run through a pre-flight checklist for the things no plugin can fix: open tabs, fonts and libraries.</p>
</div>
<div style="position:absolute;left:1180px;top:110px">{panel_iframe(SCRIPT_CHECKLIST, 1.3)}</div>
''', 1920, 1080)

ICON = page(ICON_SVG, 128, 128)

JOBS = [('icon.png', ICON, 128, 128), ('thumbnail.png', THUMB, 1920, 1080),
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
