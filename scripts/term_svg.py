#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Dr. Ravi Teja Thiriveedhi
"""term_svg: run a command and render its real output as an animated terminal SVG (light and dark).

Usage:
    python3 scripts/term_svg.py OUT_PREFIX "TITLE" -- COMMAND [ARGS...]

Writes OUT_PREFIX-light.svg and OUT_PREFIX-dark.svg. Lines appear one after another, then stay.
Standard library only. The output shown is exactly what the command printed (ANSI codes stripped); long lines wrap, as in a terminal.
"""
from __future__ import annotations

import html
import re
import subprocess
import sys

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
THEMES = {
    "light": {"bg": "#ffffff", "bar": "#eaeef2", "fg": "#1f2328", "dim": "#59636e", "ok": "#1a7f37", "bad": "#cf222e", "warn": "#9a6700", "border": "#d1d9e0"},
    "dark": {"bg": "#0d1117", "bar": "#161b22", "fg": "#e6edf3", "dim": "#9198a1", "ok": "#3fb950", "bad": "#f85149", "warn": "#d29922", "border": "#30363d"},
}
LINE_H, CHAR_W, PAD, BAR_H, MAX_COLS = 19, 7.8, 16, 30, 120


def colour(line: str, t: dict) -> str:
    s = line.strip()
    if s.startswith("$"):
        return t["dim"]
    if re.search(r"\b(PASS|SHIP|ALLOW|ACT|APPROVED|SENT|OK|done)\b|✔", line):
        return t["ok"]
    if re.search(r"\b(FAIL|STOP|BLOCK|DENIED|REJECTED|STOPPED|KILLED)\b|✖", line):
        return t["bad"]
    if re.search(r"\b(WAIT|PROPOSE|DEFER|HOLD|QUEUED|SPOOL)\b|⏸", line):
        return t["warn"]
    return t["fg"]


def render(lines: list[str], title: str, theme: str, step: float = 0.18) -> str:
    t = THEMES[theme]
    # Wrap long lines like a terminal does (nothing is cut off); colour follows the original line.
    wrapped = []
    for l in lines:
        c = colour(l, t)
        for k in range(0, max(len(l), 1), MAX_COLS):
            wrapped.append((l[k:k + MAX_COLS], c))
    lines = [w for w, _ in wrapped]
    width = int(PAD * 2 + CHAR_W * max(60, max((len(l) for l in lines), default=60)))
    height = BAR_H + PAD + LINE_H * len(lines) + PAD
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f"<title>{html.escape(title)}</title>",
        "<style>text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;white-space:pre}"
        ".l{opacity:0;animation:show .01s linear forwards}@keyframes show{to{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.l{animation:none;opacity:1}}</style>",
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="8" fill="{t["bg"]}" stroke="{t["border"]}"/>',
        f'<path d="M1 {BAR_H}h{width-2}" stroke="{t["border"]}"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{BAR_H-1}" rx="7" fill="{t["bar"]}"/>',
    ]
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{PAD + 6 + i*18}" cy="{BAR_H/2}" r="6" fill="{c}"/>')
    out.append(f'<text x="{width/2}" y="{BAR_H/2 + 4}" text-anchor="middle" fill="{t["dim"]}">{html.escape(title)}</text>')
    for i, line in enumerate(lines):
        y = BAR_H + PAD + LINE_H * (i + 0.8)
        out.append(
            f'<text class="l" style="animation-delay:{i*step:.2f}s" x="{PAD}" y="{y:.1f}" fill="{wrapped[i][1]}" xml:space="preserve">{html.escape(line)}</text>'
        )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    if "--" not in argv or len(argv) < 5:
        print(__doc__)
        return 2
    sep = argv.index("--")
    prefix, title, cmd = argv[1], argv[2], argv[sep + 1 :]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    body = ANSI.sub("", res.stdout).rstrip("\n").splitlines()
    shown = " ".join(c if " " not in c else repr(c) for c in cmd)
    lines = [f"$ {shown}"] + body
    for theme in THEMES:
        with open(f"{prefix}-{theme}.svg", "w", encoding="utf-8") as fh:
            fh.write(render(lines, title, theme))
    print(f"wrote {prefix}-light.svg and {prefix}-dark.svg ({len(lines)} lines, exit {res.returncode})")
    return res.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
