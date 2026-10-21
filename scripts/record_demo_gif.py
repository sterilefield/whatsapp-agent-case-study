"""Optional dev tool (needs Playwright and Pillow; not part of the checks).
Record each showcase's live demo page (site/index.html) as an animated GIF, from real interactions.
Frames are real screenshots of the page after each scripted step; nothing is drawn by hand."""
import io, sys, pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent  # this repository
SET_SELECT = "(id,v)=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}))}"
STEPS = {
    "agent-governance-kit": [
        ("", "main", 1600),
        ("document.getElementById('level').value='L3';document.getElementById('level').dispatchEvent(new Event('change'))", "main", 1400),
        ("document.getElementById('action').value='read';document.getElementById('action').dispatchEvent(new Event('change'))", "main", 1200),
        ("document.getElementById('action').value='delete_records';document.getElementById('action').dispatchEvent(new Event('change'))", "main", 1400),
        ("document.getElementById('kill').checked=true;document.getElementById('kill').dispatchEvent(new Event('change'))", "main", 1600),
        ("document.getElementById('kill').checked=false;document.getElementById('kill').dispatchEvent(new Event('change'));document.getElementById('play').click()", "#play", 300, 14),
        ("", "#log", 2400),
    ],
    "llm-token-economics": [
        ("", "main", 1600),
        ("(()=>{const i=document.querySelectorAll('#fleet tbody tr')[0].querySelectorAll('input')[4];i.value=120;i.dispatchEvent(new Event('input'))})()", "main", 1300),
        ("(()=>{const i=document.querySelectorAll('#fleet tbody tr')[1].querySelectorAll('input')[4];i.value=360;i.dispatchEvent(new Event('input'))})()", "main", 1300),
        ("(()=>{const i=document.querySelectorAll('#fleet tbody tr')[3].querySelectorAll('input')[4];i.value=1440;i.dispatchEvent(new Event('input'))})()", "main", 1300),
        ("(()=>{const i=document.getElementById('price');i.value=2.5;i.dispatchEvent(new Event('input'))})()", "main", 1500),
        ("document.getElementById('reset').click()", "#whatif", 1200),
        ("(()=>{const i=document.getElementById('wInt');i.value=30;i.dispatchEvent(new Event('input'))})()", "#whatif", 1800),
    ],
    "whatsapp-agent-case-study": [
        ("", "main", 1600),
        ("document.querySelector('[data-ok]').click()", "main", 1300),
        ("(()=>{const c=document.getElementById('clock');c.value=22;c.dispatchEvent(new Event('input'))})()", "main", 1200),
        ("document.querySelector('[data-ok]').click()", "main", 1400),
        ("(()=>{const c=document.getElementById('clock');c.value=9;c.dispatchEvent(new Event('input'))})()", "main", 1400),
        ("document.querySelector('[data-take]').click()", "main", 1300),
        ("document.getElementById('dup').click()", "#log", 1400),
        ("document.getElementById('busy').click()", "#log", 400, 4),
        ("", "#log", 2200),
    ],
    "empire-os-reference-architecture": [
        ("", "main", 1600),
        ("document.querySelectorAll('[data-s]')[5].click()", "main", 1500),
        ("document.querySelectorAll('[data-s]')[5].click()", "main", 1200),
        ("document.getElementById('addBatch').click()", "main", 1100),
        ("document.getElementById('addBatch').click()", "main", 1300),
        ("document.getElementById('finish').click()", "main", 1400),
        ("document.getElementById('kill').click()", "#klog", 1300),
        ("document.getElementById('act').click()", "#klog", 1200),
        ("document.getElementById('restoreAgent').click()", "#klog", 1200),
        ("document.getElementById('restoreOwner').click();document.getElementById('act').click()", "#klog", 2000),
    ],
}


def record(repo, width=1100, height=760, out_w=880):
    frames, durations = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height}, color_scheme="light", device_scale_factor=1)
        pg.goto(f"file://{ROOT}/site/index.html")
        pg.add_style_tag(content="*{transition:none!important;animation:none!important}")
        pg.wait_for_timeout(500)
        for step in STEPS[repo]:
            js, anchor, hold = step[:3]
            repeat = step[3] if len(step) > 3 else 1
            if js:
                pg.evaluate(js)
            if anchor != "main":
                pg.evaluate(f"document.querySelector('{anchor}').scrollIntoView({{block:'center'}})")
            else:
                pg.evaluate("window.scrollTo(0,0)")
            for _ in range(repeat):
                pg.wait_for_timeout(260)
                img = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
                img = img.resize((out_w, int(img.height * out_w / img.width)), Image.LANCZOS)
                frames.append(img)
                durations.append(hold)
        b.close()
    pal = frames[0].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    out = ROOT / "docs/img/demo.gif"
    q[0].save(out, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=False, disposal=2)
    print(repo, len(frames), "frames", out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    record("whatsapp-agent-case-study")
