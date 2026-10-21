"""Optional tool: regenerate this repository's light/dark hero banner (SVG). Every figure comes from the README."""
import html, pathlib

HEROES = {
    'whatsapp-agent-case-study': dict(eyebrow='ANONYMISED CASE STUDY · LIVE SINCE JUNE 2026', title='WhatsApp agent platform', tagline='A governed 15-agent WhatsApp and Telegram operations platform with a human in charge.', stats=[('460+', 'leads handled'), ('284', 'owner-approved follow-ups'), ('129', 'bugs closed with lessons')]),
}
T = {
    "light": dict(bg1="#ffffff", bg2="#f3f7fb", border="#d1d9e0", fg="#1f2328", dim="#59636e", accent="#0969da", tile="#f6f8fa", tileb="#d1d9e0", num="#1a7f37", glow="#0969da"),
    "dark": dict(bg1="#0d1117", bg2="#111a26", border="#30363d", fg="#e6edf3", dim="#9198a1", accent="#4493f8", tile="#161b22", tileb="#30363d", num="#3fb950", glow="#1f6feb"),
}
W, H = 1280, 300
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def wrap(text, n):
    out, line = [], ""
    for w in text.split():
        if len(line) + len(w) + 1 > n:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


def svg(h, theme):
    t = T[theme]
    e = html.escape
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(h["title"])}: {e(h["tagline"])}">',
        f'<title>{e(h["title"])}</title>',
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>'
        f'<radialGradient id="r" cx="0.92" cy="0.1" r="0.6"><stop offset="0" stop-color="{t["glow"]}" stop-opacity="0.18"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient></defs>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="url(#g)" stroke="{t["border"]}"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="url(#r)"/>',
        # mark: a plus in a rounded square (the org's sterile-field mark)
        f'<rect x="48" y="44" width="34" height="34" rx="8" fill="{t["accent"]}"/><path d="M65 51v20M55 61h20" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
        f'<text x="96" y="67" font-family="{FONT}" font-size="15" font-weight="600" letter-spacing="1.5" fill="{t["dim"]}">STERILE FIELD · {e(h["eyebrow"])}</text>',
        f'<text x="48" y="140" font-family="{FONT}" font-size="{50 if len(h["title"]) < 22 else 44}" font-weight="800" fill="{t["fg"]}">{e(h["title"])}</text>',
    ]
    for i, line in enumerate(wrap(h["tagline"], 52)):
        parts.append(f'<text x="48" y="{184 + i*28}" font-family="{FONT}" font-size="21" fill="{t["dim"]}">{e(line)}</text>')
    parts.append(f'<text x="48" y="262" font-family="{FONT}" font-size="15" fill="{t["accent"]}">▶ Live demo on invented data · runnable · tested · attested releases</text>')
    x0, tw, gap = 712, 172, 12
    for i, (num, label) in enumerate(h["stats"]):
        x = x0 + i * (tw + gap)
        parts.append(f'<rect x="{x}" y="96" width="{tw}" height="128" rx="10" fill="{t["tile"]}" stroke="{t["tileb"]}"/>')
        parts.append(f'<text x="{x + tw/2}" y="160" text-anchor="middle" font-family="{FONT}" font-size="{38 if len(num) < 6 else 32}" font-weight="800" fill="{t["num"]}">{e(num)}</text>')
        for j, ln in enumerate(wrap(label, 18)):
            parts.append(f'<text x="{x + tw/2}" y="{190 + j*18}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{t["dim"]}">{e(ln)}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parent.parent
    for theme in T:
        (root / "docs/img" / f"hero-{theme}.svg").write_text(svg(HEROES["whatsapp-agent-case-study"], theme), encoding="utf-8")
    print("hero banner written")
