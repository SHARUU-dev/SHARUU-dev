#!/usr/bin/env python3
"""Generates the SVG assets used by the SHARUU-dev profile README.

Usage:
    python3 generate_assets.py [output_dir] [--preview]

--preview renders the typing animation fully revealed, for static renderers.
All text lives in the DATA sections below, so edits are one-line changes.
"""
import math
import os
import sys
import textwrap
from xml.sax.saxutils import escape

args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args else "assets"
PREVIEW = "--preview" in sys.argv
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------- palette
BG = "#0a0a0f"
PANEL = "#100f18"
LINE = "#2a2144"
PURPLE = "#8b5cf6"
LAV = "#c4b5fd"
TEXT = "#e7e5f2"
MUTED = "#8a86a3"
KEY = "#9b8fd0"
GREEN = "#34d399"
FONT = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CW = 0.6  # monospace character width in em


def esc(s):
    return escape(s, {'"': "&quot;"})


def hexpath(cx, cy, r):
    pts = [
        (cx + r * math.cos(math.radians(30 + 60 * k)),
         cy + r * math.sin(math.radians(30 + 60 * k)))
        for k in range(6)
    ]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


COMMON_DEFS = f"""
<linearGradient id="gWord" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ede9fe"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="#6d28d9"/>
</linearGradient>
<linearGradient id="gFade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{PURPLE}" stop-opacity=".9"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="gPulse" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".9"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/>
</linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
  <path d="M24 0H0V24" fill="none" stroke="{PURPLE}" stroke-opacity=".08"/>
</pattern>
"""


def svg(w, h, title, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}" '
        f'font-family="{FONT}">\n<title>{esc(title)}</title>\n'
        f"<defs>{COMMON_DEFS}{defs}</defs>\n{body}\n</svg>\n"
    )


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


def brackets(w, h, m=12, s=24, color=LAV, op=0.5):
    d = (
        f"M{m} {m+s} V{m} H{m+s} "
        f"M{w-m-s} {m} H{w-m} V{m+s} "
        f"M{w-m} {h-m-s} V{h-m} H{w-m-s} "
        f"M{m+s} {h-m} H{m} V{h-m-s}"
    )
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="1.5"/>'


# =================================================================== HERO
def hero():
    W, H = 640, 416
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
         '<defs><radialGradient id="glowP" cx="540" cy="90" r="280" gradientUnits="userSpaceOnUse">'
         f'<stop offset="0" stop-color="{PURPLE}" stop-opacity=".32"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="glowG" cx="40" cy="410" r="220" gradientUnits="userSpaceOnUse">'
         f'<stop offset="0" stop-color="{GREEN}" stop-opacity=".09"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#glowP)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glowG)"/>',
         # slow scanline
         f'<rect x="0" y="0" width="{W}" height="2" fill="url(#gPulse)" opacity=".35">'
         f'<animate attributeName="y" from="0" to="{H}" dur="7s" repeatCount="indefinite"/></rect>',
         brackets(W, H)]

    # honeycomb cluster
    r = 20
    dx, dy = r * math.sqrt(3), 1.5 * r
    x0, y0 = 492, 62
    cells = [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2)]
    pulse = {(0, 2): 0.0, (1, 1): 1.3, (1, 3): 2.2, (2, 2): 3.1}
    for row, col in cells:
        cx = x0 + col * dx + (dx / 2 if row % 2 else 0)
        cy = y0 + row * dy
        d = hexpath(cx, cy, r - 1.5)
        if (row, col) == (1, 2):
            b.append(f'<path d="{d}" fill="{GREEN}" fill-opacity=".14" stroke="{GREEN}" stroke-opacity=".85" stroke-width="1.3">'
                     f'<animate attributeName="fill-opacity" values=".08;.3;.08" dur="3.6s" repeatCount="indefinite"/></path>')
        elif (row, col) in pulse:
            b.append(f'<path d="{d}" fill="{PURPLE}" fill-opacity=".06" stroke="{PURPLE}" stroke-opacity=".6" stroke-width="1.2">'
                     f'<animate attributeName="fill-opacity" values=".06;.4;.06" dur="4s" begin="{pulse[(row, col)]}s" repeatCount="indefinite"/></path>')
        else:
            b.append(f'<path d="{d}" fill="{PURPLE}" fill-opacity=".05" stroke="{PURPLE}" stroke-opacity=".35" stroke-width="1.2"/>')

    b.append(f'<text x="40" y="48" font-size="13" fill="{MUTED}" letter-spacing="3">// SHARUU-dev</text>')
    b.append(f'<text x="40" y="130" font-size="80" font-weight="800" letter-spacing="4" fill="url(#gWord)">SHARUU'
             f'<tspan font-size="34" font-weight="700" letter-spacing="0" dx="6" fill="{GREEN}">.dev</tspan></text>')
    b.append(f'<text x="40" y="166" font-size="17" fill="{TEXT}">Computer engineering student · AI, systems &amp; backend</text>')

    # terminal panel
    b.append(f'<rect x="32" y="190" width="576" height="198" rx="6" fill="#07070c" stroke="{LINE}"/>')
    b.append(f'<text x="52" y="212" font-size="12" fill="{MUTED}" letter-spacing="2">~/identity</text>')

    lines = [
        ("whoami", "sharuu-dev"),
        ("focus", "ai · backend · security"),
        ("projects", "bee ai · bee.os · sentinel"),
        ("open_to", "freelance work"),
    ]
    fs = 19
    cw = fs * CW
    t = 0.6
    clips, texts = [], []
    for i, (k, v) in enumerate(lines):
        y = 248 + i * 30
        n = 2 + 10 + len(v)
        dur = n * 0.03
        if PREVIEW:
            rect = f'<rect x="52" y="{y-18}" width="{n*cw:.1f}" height="26"/>'
        else:
            vals = ";".join(f"{j*cw:.1f}" for j in range(n + 1))
            kts = ";".join(f"{j/n:.4f}" for j in range(n + 1))
            rect = (f'<rect x="52" y="{y-18}" width="0" height="26">'
                    f'<animate attributeName="width" values="{vals}" keyTimes="{kts}" calcMode="discrete" '
                    f'dur="{dur:.2f}s" begin="{t:.2f}s" fill="freeze"/></rect>')
        clips.append(f'<clipPath id="c{i}">{rect}</clipPath>')
        kpad = k.ljust(10).replace(" ", "&#160;")
        texts.append(
            f'<g clip-path="url(#c{i})"><text x="52" y="{y}" font-size="{fs}" xml:space="preserve">'
            f'<tspan fill="{GREEN}">&gt;</tspan><tspan>&#160;</tspan>'
            f'<tspan fill="{KEY}">{kpad}</tspan><tspan fill="{TEXT}">{esc(v)}</tspan></text></g>'
        )
        t += dur + 0.45
    b.append("<defs>" + "".join(clips) + "</defs>")
    b.extend(texts)

    # prompt + blinking cursor
    y = 248 + len(lines) * 30
    if PREVIEW:
        b.append(f'<text x="52" y="{y}" font-size="{fs}" fill="{GREEN}">&gt;</text>')
        b.append(f'<rect x="{52+2*cw:.1f}" y="{y-15}" width="{cw:.1f}" height="19" fill="{LAV}"/>')
    else:
        b.append(f'<text x="52" y="{y}" font-size="{fs}" fill="{GREEN}" opacity="0">&gt;'
                 f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/></text>')
        b.append(f'<rect x="{52+2*cw:.1f}" y="{y-15}" width="{cw:.1f}" height="19" fill="{LAV}" opacity="0">'
                 f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
                 f'<animate attributeName="opacity" values="1;0" dur="1.1s" begin="{t:.2f}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    write("hero.svg", svg(W, H, "SHARUU-dev: computer engineering student working on AI, systems and backend", "\n".join(b)))


# =================================================================== ABOUT
def about():
    W = 640
    bio = ("I'm a computer engineering student who learns by building. "
           "My work spans AI systems, backend services, security tooling and Discord bots. "
           "I'd rather understand how something works than only call it.")
    lines = textwrap.wrap(bio, 50)
    H = 84 + len(lines) * 28 + 52
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect width="3" height="{H}" fill="{PURPLE}"/>',
         f'<text x="40" y="40" font-size="13" fill="{MUTED}" letter-spacing="3">// about</text>']
    for i, ln in enumerate(lines):
        b.append(f'<text x="40" y="{84+i*28}" font-size="18" fill="{TEXT}">{esc(ln)}</text>')
    y = 84 + len(lines) * 28 + 16
    b.append(f'<path d="{hexpath(46, y+1, 7)}" fill="{GREEN}" fill-opacity=".25" stroke="{GREEN}" stroke-width="1.2"/>')
    b.append(f'<text x="64" y="{y+6}" font-size="16" fill="{LAV}" letter-spacing="1">build · break · debug · learn · improve</text>')
    write("about.svg", svg(W, H, "About SHARUU-dev", "\n".join(b)))


# =================================================================== SECTION HEADERS
def section(slug, num, title, meta):
    W, H = 640, 60
    b = [
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<path d="{hexpath(32, 30, 22)}" fill="{PURPLE}" fill-opacity=".12" stroke="{PURPLE}" stroke-width="1.5"/>',
        f'<text x="32" y="36" font-size="15" font-weight="700" fill="{LAV}" text-anchor="middle">{num}</text>',
        f'<text x="68" y="37" font-size="20" font-weight="700" fill="{TEXT}" letter-spacing="4">{esc(title)}</text>',
        f'<text x="632" y="36" font-size="13" fill="{MUTED}" text-anchor="end">{esc(meta)}</text>',
        f'<rect x="0" y="55" width="{W}" height="1.5" fill="url(#gFade)"/>',
        f'<rect x="0" y="54.5" width="90" height="2.5" fill="url(#gPulse)">'
        f'<animate attributeName="x" from="-90" to="{W}" dur="5s" repeatCount="indefinite"/></rect>',
    ]
    write(f"section-{slug}.svg", svg(W, H, f"Section {num}: {title.title()}", "\n".join(b)))


# =================================================================== MODULE CARDS
MODULES = [
    ("languages", "01", "LANGUAGES", [
        ("systems", ["C", "C++"]),
        ("scripting", ["Python", "Bash"]),
        ("web", ["JavaScript", "TypeScript"]),
        ("data & general", ["SQL", "Java"]),
    ]),
    ("web", "02", "WEB", [
        ("frontend", ["HTML5", "CSS3", "React"]),
        ("backend", ["Node.js", "Express.js", "REST APIs", "JSON"]),
    ]),
    ("ai", "03", "AI & ML", [
        ("core", ["Machine learning", "Neural networks", "PyTorch", "NLP", "LLMs"]),
        ("applied", ["Speech-to-text", "Text-to-speech", "Prompt engineering", "AI API integration"]),
    ]),
    ("data", "04", "DATABASES", [
        ("relational", ["MySQL", "PostgreSQL", "SQL Server", "SQLite"]),
        ("services", ["Redis", "Supabase"]),
    ]),
    ("security", "05", "SECURITY & NETWORKS", [
        ("security", ["Cryptography", "Linux security", "Firewalls", "Ethical hacking basics", "Behaviour analysis"]),
        ("networking", ["TCP/IP", "Subnetting", "VLAN", "SSH", "HSRP", "EtherChannel"]),
    ]),
    ("tools", "06", "SYSTEMS & TOOLS", [
        ("operating systems", ["Linux", "Kali", "Debian", "Windows", "Termux"]),
        ("tooling", ["Git", "GitHub", "VS Code", "Docker basics", "VirtualBox", "PowerShell"]),
    ]),
]
CARD_W = 440
PAD = 22


def layout_chips(groups):
    inner = CARD_W - 2 * PAD
    y = 72
    items = []
    for label, chips in groups:
        items.append(("label", label, PAD, y))
        y += 14
        x = PAD
        for c in chips:
            w = len(c) * 9 + 22
            if x + w > PAD + inner:
                x = PAD
                y += 36
            items.append(("chip", c, x, y, w))
            x += w + 8
        y += 36 + 14
    return items, y


def module_cards():
    laid = [(m, *layout_chips(m[3])) for m in MODULES]
    heights = {}
    for i in range(0, len(laid), 2):
        pair = laid[i:i + 2]
        h = max(p[2] for p in pair) + 4
        for p in pair:
            heights[p[0][0]] = h
    for (slug, num, title, _), items, _y in laid:
        H = heights[slug]
        b = [f'<rect width="{CARD_W}" height="{H}" fill="{BG}"/>',
             f'<rect x=".5" y=".5" width="{CARD_W-1}" height="{H-1}" rx="6" fill="{PANEL}" stroke="{LINE}"/>',
             f'<rect width="3" height="{H}" fill="{PURPLE}"/>',
             f'<path d="{hexpath(CARD_W-70, H-34, 46)}" fill="none" stroke="{PURPLE}" stroke-opacity=".07" stroke-width="2"/>',
             f'<text x="{PAD}" y="38" font-size="14" font-weight="700" fill="{GREEN}">{num}</text>',
             f'<text x="{PAD+32}" y="38" font-size="14" font-weight="700" fill="{LAV}" letter-spacing="3">{esc(title)}</text>',
             f'<circle cx="{CARD_W-24}" cy="33" r="3.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.25;1" dur="3s" repeatCount="indefinite"/></circle>',
             f'<rect x="{PAD}" y="52" width="{CARD_W-2*PAD}" height="1" fill="{LINE}"/>']
        for it in items:
            if it[0] == "label":
                b.append(f'<text x="{it[2]}" y="{it[3]+4}" font-size="12" fill="{MUTED}" letter-spacing="2">{esc(it[1].upper())}</text>')
            else:
                _, c, x, y, w = it
                b.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="4" fill="#1a1330" stroke="#3b2a66"/>')
                b.append(f'<text x="{x+11}" y="{y+19}" font-size="15" fill="#ddd6fe">{esc(c)}</text>')
        write(f"module-{slug}.svg", svg(CARD_W, H, f"{title.title()}: " + ", ".join(c for _, cs in MODULES[[m[0] for m in MODULES].index(slug)][3] for c in cs), "\n".join(b)))


# =================================================================== PROJECT CARDS
PROJECTS = [
    # slug, index, name, kind, badge (text, style), description
    ("bee-ai", "P/01", "BEE AI", "language model · python · pytorch", ("IN DEVELOPMENT", "live"),
     "A language-model project built from the ground up: tokenization, transformer architecture, training pipeline, voice interaction and Discord integration."),
    ("bee-os", "P/02", "BEE.OS", "system project", ("DETAILS SOON", "quiet"),
     "A system-level project in the Bee line. More details will be added to this profile soon."),
    ("sentinel", "P/03", "SENTINEL", "security project", ("DETAILS SOON", "quiet"),
     "A security-focused project exploring monitoring and behaviour analysis."),
    ("sky", "P/04", "SKY", "discord bot · javascript", ("VIEW REPO", "link"),
     "A Discord bot for server automation and community tools, written in JavaScript."),
]


def project_cards():
    wrapped = {p[0]: textwrap.wrap(p[5], 40) for p in PROJECTS}
    rows = [PROJECTS[0:2], PROJECTS[2:4]]
    for row in rows:
        H = max(150 + len(wrapped[p[0]]) * 24 + 26 for p in row)
        for slug, idx, name, kind, (btxt, bstyle), desc in row:
            b = [f'<rect width="{CARD_W}" height="{H}" fill="{BG}"/>',
                 f'<rect x=".5" y=".5" width="{CARD_W-1}" height="{H-1}" rx="6" fill="{PANEL}" stroke="{LINE}"/>',
                 f'<rect width="3" height="{H}" fill="{PURPLE}"/>',
                 f'<path d="{hexpath(CARD_W-66, H-60, 62)}" fill="{PURPLE}" fill-opacity=".04" stroke="{PURPLE}" stroke-opacity=".12" stroke-width="2"/>',
                 f'<text x="{PAD}" y="38" font-size="13" fill="{MUTED}" letter-spacing="2">{idx}</text>']
            bw = len(btxt) * 8.2 + 34
            bx = CARD_W - PAD - bw
            if bstyle == "live":
                b.append(f'<rect x="{bx:.1f}" y="20" width="{bw:.1f}" height="26" rx="13" fill="{GREEN}" fill-opacity=".08" stroke="{GREEN}" stroke-opacity=".6"/>')
                b.append(f'<circle cx="{bx+15:.1f}" cy="33" r="3.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="2.4s" repeatCount="indefinite"/></circle>')
                b.append(f'<text x="{bx+25:.1f}" y="37" font-size="11" font-weight="700" fill="{GREEN}" letter-spacing="1">{btxt}</text>')
            elif bstyle == "link":
                b.append(f'<rect x="{bx:.1f}" y="20" width="{bw:.1f}" height="26" rx="13" fill="{PURPLE}" fill-opacity=".12" stroke="{PURPLE}" stroke-opacity=".7"/>')
                b.append(f'<text x="{bx+bw/2:.1f}" y="37" font-size="11" font-weight="700" fill="{LAV}" letter-spacing="1" text-anchor="middle">{btxt} ↗</text>')
            else:
                b.append(f'<rect x="{bx:.1f}" y="20" width="{bw:.1f}" height="26" rx="13" fill="none" stroke="{LINE}"/>')
                b.append(f'<text x="{bx+bw/2:.1f}" y="37" font-size="11" fill="{MUTED}" letter-spacing="1" text-anchor="middle">{btxt}</text>')
            b.append(f'<text x="{PAD}" y="92" font-size="34" font-weight="800" letter-spacing="2" fill="url(#gWord)">{esc(name)}</text>')
            b.append(f'<text x="{PAD}" y="118" font-size="13" fill="{KEY}">{esc(kind)}</text>')
            b.append(f'<rect x="{PAD}" y="132" width="40" height="2" fill="{GREEN}" fill-opacity=".8"/>')
            for i, ln in enumerate(wrapped[slug]):
                b.append(f'<text x="{PAD}" y="{162+i*24}" font-size="15" fill="{TEXT}">{esc(ln)}</text>')
            write(f"project-{slug}.svg", svg(CARD_W, H, f"{name}: {desc}", "\n".join(b)))


# =================================================================== HIRE
def hire():
    W, H = 640, 336
    rows = [
        ("discord_bot()", "from ₹1,500", "1–3 days"),
        ("web_page()", "from ₹1,500", "2–4 days"),
        ("automation.py", "from ₹500", "1–2 days"),
        ("fix_bug()", "from ₹300", "same day"),
    ]
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect width="3" height="{H}" fill="{PURPLE}"/>',
         f'<circle cx="{W-34}" cy="36" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.25;1" dur="2.6s" repeatCount="indefinite"/></circle>',
         f'<text x="{W-46}" y="40" font-size="12" fill="{GREEN}" text-anchor="end" letter-spacing="2">OPEN FOR WORK</text>',
         f'<text x="40" y="40" font-size="13" fill="{MUTED}" letter-spacing="3">// services</text>',
         f'<text x="40" y="76" font-size="12" fill="{MUTED}" letter-spacing="2">BUILD</text>',
         f'<text x="320" y="76" font-size="12" fill="{MUTED}" letter-spacing="2">PRICE</text>',
         f'<text x="480" y="76" font-size="12" fill="{MUTED}" letter-spacing="2">DELIVERY</text>',
         f'<rect x="40" y="86" width="{W-80}" height="1" fill="{LINE}"/>']
    for i, (s, p, d) in enumerate(rows):
        y = 124 + i * 40
        b.append(f'<text x="40" y="{y}" font-size="21" fill="{TEXT}">{esc(s)}</text>')
        b.append(f'<text x="320" y="{y}" font-size="21" fill="{GREEN}">{esc(p)}</text>')
        b.append(f'<text x="480" y="{y}" font-size="19" fill="{KEY}">{esc(d)}</text>')
        b.append(f'<rect x="40" y="{y+14}" width="{W-80}" height="1" fill="{LINE}" fill-opacity=".6"/>')
    b.append(f'<text x="40" y="{H-38}" font-size="14" fill="{MUTED}">Fixed quote before I start · 50% upfront on bigger jobs</text>')
    b.append(f'<text x="40" y="{H-16}" font-size="14" fill="{MUTED}">Setup guide included, help if something breaks</text>')
    write("hire.svg", svg(W, H, "Services: Discord bots from 1,500 rupees, web pages from 1,500, Python automation from 500, bug fixes from 300", "\n".join(b)))


# =================================================================== CONTACT
def contact():
    W, H = 640, 266
    rows = [
        ("discord", "SHARUUX"),
        ("instagram", "@sha.ruux"),
        ("youtube", "@SHARUUX-001"),
        ("portfolio", "sharuux-2007.github.io"),
    ]
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="{PANEL}" fill-opacity=".85" stroke="{LINE}"/>',
         f'<rect width="3" height="{H}" fill="{PURPLE}"/>',
         brackets(W, H, m=10, s=18, op=0.35),
         f'<text x="40" y="44" font-size="13" fill="{MUTED}" letter-spacing="3">// reach me</text>']
    for i, (k, v) in enumerate(rows):
        y = 92 + i * 36
        b.append(f'<text x="40" y="{y}" font-size="20" xml:space="preserve"><tspan fill="{GREEN}">&gt;</tspan><tspan>&#160;</tspan>'
                 f'<tspan fill="{KEY}">{k.ljust(11).replace(" ", "&#160;")}</tspan><tspan fill="{TEXT}">{esc(v)}</tspan></text>')
    b.append(f'<text x="40" y="{H-26}" font-size="14" fill="{MUTED}">Tell me what you want built. A rough idea is enough.</text>')
    write("contact.svg", svg(W, H, "Contact: Discord SHARUUX, Instagram sha.ruux, YouTube SHARUUX-001", "\n".join(b)))


# =================================================================== FOOTER
def footer():
    W, H = 640, 72
    msg = "idea → code → error → debug → learn → build → repeat"
    sweep = ('<rect x="40" y="0" width="110" height="72"/>' if PREVIEW else
             '<rect x="-110" y="0" width="110" height="72">'
             '<animate attributeName="x" from="-110" to="640" dur="5s" repeatCount="indefinite"/></rect>')
    b = [
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<defs><clipPath id="sweep">{sweep}</clipPath></defs>',
        f'<path d="{hexpath(26, 36, 12)}" fill="none" stroke="{PURPLE}" stroke-opacity=".6" stroke-width="1.4"/>',
        f'<path d="{hexpath(W-26, 36, 12)}" fill="none" stroke="{PURPLE}" stroke-opacity=".6" stroke-width="1.4"/>',
        f'<rect x="50" y="35.5" width="30" height="1" fill="{LINE}"/>',
        f'<rect x="{W-80}" y="35.5" width="30" height="1" fill="{LINE}"/>',
        f'<text x="{W/2}" y="41" font-size="16" letter-spacing="1" text-anchor="middle" fill="{MUTED}">{msg}</text>',
        f'<g clip-path="url(#sweep)"><text x="{W/2}" y="41" font-size="16" letter-spacing="1" text-anchor="middle" fill="{LAV}">{msg}</text></g>',
    ]
    write("footer.svg", svg(W, H, "idea, code, error, debug, learn, build, repeat", "\n".join(b)))


if __name__ == "__main__":
    hero()
    about()
    section("modules", "01", "MODULES", "what I work with")
    section("projects", "02", "PROJECTS", "what I'm building")
    section("hire", "03", "HIRE", "freelance work")
    section("contact", "04", "CONTACT", "let's talk")
    module_cards()
    project_cards()
    hire()
    contact()
    footer()
    print("generated", len(os.listdir(OUT)), "files in", OUT)
