#!/usr/bin/env python3
"""Generates the SVG assets used by the SHARUU-dev profile README.

Usage:
    python3 scripts/generate_assets.py [output_dir]

Standard library only. Genuine brand icons come from scripts/icons.json
(Simple Icons, CC0 - plus a few Material Design / Octicons glyphs), so every
SVG is self-contained: no fonts, images or scripts are loaded from outside.

All copy lives in the DATA section below - edit it, re-run, commit assets/.

telemetry.svg and snake-dark.svg are written here only as placeholders (and only
when missing). The GitHub Actions workflow replaces them with live data.
"""
import json
import math
import os
import sys
import textwrap
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import update_stats  # noqa: E402  (renders the telemetry placeholder)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args else os.path.join(os.path.dirname(HERE), "assets")
os.makedirs(OUT, exist_ok=True)

ICONS = json.load(open(os.path.join(HERE, "icons.json"), encoding="utf-8"))

# ================================================================== DATA ====
PROJECTS = [
    # slug, name, kind pill, description, tags
    ("bee-ai", "BEE AI", "AI DEVELOPMENT",
     "My AI development project.", []),
    ("bee-os", "BEE.OS", "DISCORD PLATFORM",
     "My Discord moderation and server management platform.",
     ["TypeScript", "AutoMod", "Tickets", "Logging", "Role panels", "Anti-Raid",
      "Levels & XP", "Giveaways", "Owner panel"]),
    ("sky", "SKY", "LOCAL AI ASSISTANT",
     "My independent local AI assistant project.", ["Local AI", "Independent"]),
    ("sentinel", "SENTINEL", "SECURITY",
     "My C++ security-focused project.", ["C++", "OOP", "File scanning"]),
]

# (title, [(group label, [chip, ...])])  chip = (label, icon ref or None)
# icon ref = ("simple"|"material", slug) -> drawn as a tool chip, None -> concept chip
S, M = "simple", "material"
STACK = [
    ("LANGUAGES", [
        ("code", [("C", (S, "c")), ("C++", (S, "cplusplus")), ("Python", (S, "python")),
                       ("Java", (S, "openjdk")), ("JavaScript", (S, "javascript")),
                       ("TypeScript", (S, "typescript")), ("Bash", (S, "gnubash")),
                       ("SQL", (M, "database"))]),
        ("core concepts", [("OOP", None), ("Data Structures & Algorithms", None),
                           ("Memory Management", None), ("File Handling", None), ("Debugging", None)]),
    ]),
    ("WEB", [
        ("frontend", [("HTML5", (S, "html5")), ("CSS", (S, "css")), ("React", (S, "react")),
                      ("Responsive Web", None)]),
        ("backend", [("Node.js", (S, "nodedotjs")), ("Express.js", (S, "express")),
                     ("Discord.js", (S, "discord")), ("JSON", (S, "json")), ("REST APIs", None)]),
    ]),
    ("AI & ML", [
        ("frameworks", [("PyTorch", (S, "pytorch"))]),
        ("concepts", [("Machine Learning", None), ("Neural Networks", None), ("NLP", None), ("LLMs", None),
                      ("Prompt Engineering", None), ("AI API Integration", None),
                      ("Speech-to-Text", None), ("Text-to-Speech", None)]),
    ]),
    ("DATABASES", [
        ("engines", [("MySQL", (S, "mysql")), ("PostgreSQL", (S, "postgresql")),
                     ("SQL Server", (M, "database-cog")), ("SQLite", (S, "sqlite")),
                     ("Redis", (S, "redis")), ("Supabase", (S, "supabase"))]),
        ("practice", [("Database Design", None), ("SQL Queries", None), ("pyodbc", None)]),
    ]),
    ("SECURITY & NETWORKS", [
        ("security", [("Cryptography", None), ("Hashing", None), ("Digital Signatures", None),
                      ("Firewalls", None), ("Security Monitoring", None), ("UEBA", None),
                      ("Ethical Hacking (basics)", None)]),
        ("networking", [("TCP/IP", None), ("Subnetting", None), ("VLAN", None), ("SSH", None),
                        ("Router-on-a-Stick", None), ("EtherChannel", None), ("HSRP", None)]),
    ]),
    ("SYSTEMS & TOOLS", [
        ("operating systems", [("Linux", (S, "linux")), ("Kali", (S, "kalilinux")),
                               ("Debian", (S, "debian")), ("Ubuntu", (S, "ubuntu")),
                               ("Windows", (M, "microsoft-windows")), ("Termux", (M, "console"))]),
        ("tooling", [("Git", (S, "git")), ("GitHub", (S, "github")),
                     ("VS Code", (M, "microsoft-visual-studio-code")), ("npm", (S, "npm")),
                     ("Docker (basics)", (S, "docker")), ("VirtualBox", (S, "virtualbox")),
                     ("PowerShell", (M, "powershell")), ("Arduino", (S, "arduino"))]),
    ]),
]

BRAND = {  # brand colours; very dark ones are lightened automatically
    "c": "#A8B9CC", "cplusplus": "#00599C", "python": "#3776AB", "openjdk": "#ED8B00",
    "javascript": "#F7DF1E", "typescript": "#3178C6", "gnubash": "#4EAA25", "html5": "#E34F26",
    "css": "#8A63D2", "react": "#61DAFB", "nodedotjs": "#5FA04E", "express": "#E7E5F2",
    "discord": "#5865F2", "json": "#E7E5F2", "mysql": "#6BA6D6", "postgresql": "#4169E1",
    "sqlite": "#0F80CC", "redis": "#FF4438", "supabase": "#3FCF8E", "pytorch": "#EE4C2C",
    "linux": "#FCC624", "kalilinux": "#6FA8DC", "debian": "#D70A53", "ubuntu": "#E95420",
    "git": "#F05032", "github": "#E7E5F2", "npm": "#CB3837", "docker": "#2496ED",
    "virtualbox": "#2F7BD6", "arduino": "#00979D", "instagram": "#E4405F", "youtube": "#FF0000",
    "database": "#C4B5FD", "database-cog": "#C4B5FD", "microsoft-windows": "#0078D4",
    "microsoft-visual-studio-code": "#2EA6F2", "powershell": "#5391FE", "console": "#34D399",
}

SERVICES = [  # name, price, delivery
    ("discord_bot()", "from ₹1,500", "1–3 days"),
    ("web_page()", "from ₹1,500", "2–4 days"),
    ("automation.py", "from ₹500", "1–2 days"),
    ("fix_bug()", "from ₹300", "same day"),
]

LINKS = [  # label, icon, handle, url or None
    ("GitHub", "github", "@SHARUU-dev", "https://github.com/SHARUU-dev"),
    ("YouTube", "youtube", "@SHARUUX-001", "https://www.youtube.com/@SHARUUX-001"),
    ("Instagram", "instagram", "@sha.ruux", "https://www.instagram.com/sha.ruux/"),
    ("Discord", "discord", "SHARUUX", None),
]

BIO = ("I'm a computer engineering student who learns by building. My work spans AI "
       "projects, backend services, security tooling and Discord platforms. I'd rather "
       "understand how something works than only call it.")

STATUS = [  # label, colour key, text
    ("BUILDING", "g", "Practical software, AI applications, automation systems and developer tools."),
    ("LEARNING", "l", "Computer engineering, systems, networking and cybersecurity."),
    ("EXPERIMENTING", "p", "AI assistants, automation and security tooling."),
    ("OPEN TO OPPORTUNITIES", "g", "Software, backend and AI application roles, plus freelance work."),
]

# ============================================================== PALETTE =====
BG, PANEL, PANEL2, LINE = "#0a0a0f", "#100f18", "#15112a", "#2a2144"
PURPLE, LAV, TEXT, MUTED, KEY, GREEN = "#8b5cf6", "#c4b5fd", "#e7e5f2", "#8a86a3", "#9b8fd0", "#34d399"
PD = "#6d28d9"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Inter,'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
CW = 0.62  # monospace advance in em, deliberately generous so text never overflows
W_FULL, W_CARD = 832, 408
COL = {"g": GREEN, "l": LAV, "p": PURPLE}

CSS = """
@keyframes pulse{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}
@keyframes sweep{from{transform:translateX(-140px)}to{transform:translateX(840px)}}
@keyframes scan{from{transform:translateY(-4px)}to{transform:translateY(420px)}}
@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes bars{0%,100%{transform:scaleY(.4)}50%{transform:scaleY(1)}}
@keyframes flip{0%,45%{opacity:.25}55%,100%{opacity:1}}
.pulse{animation:pulse 2.8s ease-in-out infinite}
.spin{animation:spin 6s linear infinite;transform-box:view-box}
.float{animation:float 5s ease-in-out infinite}
.sweep{animation:sweep 5s linear infinite}
.scan{animation:scan 8s linear infinite}
.tag{animation:type 2.2s steps(31,end) .5s both}
.rise{animation:rise .8s ease-out both}
.bar{transform-box:fill-box;transform-origin:center;animation:bars 1.8s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def esc(s):
    return escape(s, {'"': "&quot;"})


def svg_doc(w, h, title, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}" font-family="{MONO}">\n<title>{esc(title)}</title>\n'
            f'<defs>{COMMON_DEFS}{defs}<style>{CSS}</style></defs>\n{body}\n</svg>\n')


COMMON_DEFS = f"""
<linearGradient id="gWord" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ede9fe"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="{PD}"/></linearGradient>
<linearGradient id="gFade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".9"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
<linearGradient id="gPulse" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".9"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{PURPLE}" stroke-opacity=".08"/></pattern>
"""


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


def write_if_missing(name, content):
    if not os.path.exists(os.path.join(OUT, name)):
        write(name, content)


# ============================================================== HELPERS =====
def hexpath(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * math.sin(math.radians(30 + 60 * k)))
           for k in range(6)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def brackets(w, h, m=12, s=22, color=LAV, op=0.45):
    d = (f"M{m} {m+s} V{m} H{m+s} M{w-m-s} {m} H{w-m} V{m+s} "
         f"M{w-m} {h-m-s} V{h-m} H{w-m-s} M{m+s} {h-m} H{m} V{h-m-s}")
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{op}" stroke-width="1.5"/>'


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def readable(hexc, floor=0.22):
    """Lighten a brand colour until it reads on the dark panels."""
    c = hexc
    for _ in range(12):
        if lum(c) >= floor:
            break
        r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
        c = "#%02x%02x%02x" % tuple(int(v + (255 - v) * .18) for v in (r, g, b))
    return c


def icon(ref, x, y, size, color=None):
    fam, slug = ref
    d = ICONS[fam][slug]
    col = color or readable(BRAND.get(slug, LAV))
    return f'<path transform="translate({x:.1f} {y:.1f}) scale({size/24:.4f})" d="{d}" fill="{col}"/>'


def tw(text, fs, ls=0.0):
    return len(text) * (fs * CW + ls)


def panel(w, h, accent=True, rx=8, fill=PANEL):
    s = (f'<rect width="{w}" height="{h}" fill="{BG}"/>'
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="{fill}" stroke="{LINE}"/>')
    if accent:
        s += f'<path d="M0.5 {rx} A{rx-.5} {rx-.5} 0 0 1 {rx} .5 V{h-.5} H{rx} A{rx-.5} {rx-.5} 0 0 1 .5 {h-rx} Z" fill="none"/>'
        s += f'<rect x="0" y="{rx}" width="3" height="{h-2*rx}" fill="{PURPLE}"/>'
    return s


def chip(x, y, label, ref=None, h=30):
    fs = 13
    iw = 16 + 7 if ref else 0
    w = 12 + iw + tw(label, fs) + 12
    if ref:
        s = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="6" fill="#1a1330" stroke="#3b2a66"/>'
             + icon(ref, x + 10, y + (h - 16) / 2, 16)
             + f'<text x="{x+10+iw:.1f}" y="{y+h/2+4.5}" font-size="{fs}" fill="#ddd6fe">{esc(label)}</text>')
    else:
        s = (f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{PURPLE}" fill-opacity=".07" '
             f'stroke="{PURPLE}" stroke-opacity=".45"/>'
             f'<text x="{x+12:.1f}" y="{y+h/2+4.5}" font-size="{fs}" fill="{LAV}">{esc(label)}</text>')
    return s, w


def flow(items, x0, y0, max_w, gap=8, row_h=38, h=30):
    """Lay chips out in wrapping rows. Returns (svg, y after last row)."""
    x, y, out = x0, y0, []
    for label, ref in items:
        _, w = chip(0, 0, label, ref, h)
        if x + w > x0 + max_w and x > x0:
            x, y = x0, y + row_h
        s, w = chip(x, y, label, ref, h)
        out.append(s)
        x += w + gap
    return "".join(out), y + row_h


def wrap(text, fs, width):
    return textwrap.wrap(text, max(8, int(width / (fs * CW))))


# ================================================================= HERO =====
def hero():
    W, H = W_FULL, 360
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
         f'<defs><radialGradient id="glowP" cx="700" cy="110" r="330" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".30"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="glowG" cx="30" cy="360" r="260" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{GREEN}" stop-opacity=".10"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#glowP)"/><rect width="{W}" height="{H}" fill="url(#glowG)"/>',
         f'<rect class="scan" x="0" y="0" width="{W}" height="2" fill="url(#gPulse)" opacity=".35"/>',
         brackets(W, H)]
    # honeycomb cluster (the Bee motif), right side
    r = 22
    dx, dy = r * math.sqrt(3), 1.5 * r
    x0, y0 = 584, 70
    cells = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 3), (2, 4), (3, 2), (3, 3)]
    pulse = {(0, 2): 0.0, (1, 1): 1.1, (1, 3): 2.0, (2, 4): 2.9, (3, 2): 0.6, (2, 2): 1.7}
    for row, col in cells:
        cx = x0 + col * dx + (dx / 2 if row % 2 else 0)
        cy = y0 + row * dy
        d = hexpath(cx, cy, r - 1.6)
        if (row, col) == (1, 3):
            b.append(f'<path class="pulse" style="animation-duration:3.6s" d="{d}" fill="{GREEN}" fill-opacity=".16" stroke="{GREEN}" stroke-opacity=".9" stroke-width="1.3"/>')
        elif (row, col) in pulse:
            b.append(f'<path d="{d}" fill="{PURPLE}" fill-opacity=".10" stroke="{PURPLE}" stroke-opacity=".7" stroke-width="1.2" class="pulse" style="animation-delay:{pulse[(row, col)]}s;animation-duration:4s"/>')
        else:
            b.append(f'<path d="{d}" fill="{PURPLE}" fill-opacity=".04" stroke="{PURPLE}" stroke-opacity=".32" stroke-width="1.2"/>')
    b.append(f'<text x="44" y="54" font-size="13" fill="{MUTED}" letter-spacing="3">// SHARUU-dev</text>')
    b.append(f'<text x="44" y="152" font-family="{SANS}" font-size="104" font-weight="800" letter-spacing="-2" fill="url(#gWord)">SHARUU<tspan fill="{GREEN}">!</tspan></text>')
    b.append(f'<text class="tag" x="46" y="198" font-family="{SANS}" font-size="27" fill="{TEXT}">Building ideas into technology.</text>')
    b.append(f'<text x="46" y="232" font-size="15" fill="{KEY}">Computer Engineering  ·  Software Development</text>')
    x = 46
    for label in ["Backend", "AI Applications", "Automation", "Cybersecurity", "Systems"]:
        s, w = chip(x, 250, label, None, 28)
        b.append(s)
        x += w + 8
    # status strip
    segs = [("BUILDING", GREEN), ("LEARNING", LAV), ("EXPERIMENTING", PURPLE), ("OPEN TO OPPORTUNITIES", GREEN)]
    fs, ls, pad = 12, 1.6, 16
    base = [26 + tw(t, fs, ls) + pad for t, _ in segs]
    sw, sx0, sy = W - 88, 44, 292
    extra = (sw - sum(base)) / len(segs)
    b.append(f'<rect x="{sx0}" y="{sy}" width="{sw}" height="44" rx="8" fill="{PANEL}" stroke="{LINE}"/>')
    x = sx0
    for i, ((t, c), bw) in enumerate(zip(segs, base)):
        w = bw + extra
        if i:
            b.append(f'<rect x="{x:.1f}" y="{sy+11}" width="1" height="22" fill="{LINE}"/>')
        b.append(f'<circle class="pulse" style="animation-delay:{i*.7:.1f}s" cx="{x+pad+4:.1f}" cy="{sy+22}" r="4" fill="{c}"/>')
        b.append(f'<text x="{x+pad+18:.1f}" y="{sy+26.5}" font-size="{fs}" font-weight="700" letter-spacing="{ls}" fill="{TEXT}">{t}</text>')
        x += w
    write("hero.svg", svg_doc(W, H, "SHARUU! Building ideas into technology. Computer engineering and software development. "
                                    "Status: building, learning, experimenting, open to opportunities.", "\n".join(b)))


# ============================================================ SECTIONS ======
def section(slug, num, title, meta, total=5):
    W, H = W_FULL, 72
    b = [f'<g transform="translate(0 16)">',
         f'<path d="{hexpath(30, 28, 21)}" fill="{PURPLE}" fill-opacity=".12" stroke="{PURPLE}" stroke-width="1.5"/>',
         f'<text x="30" y="34" font-size="15" font-weight="700" fill="{LAV}" text-anchor="middle">{num:02d}</text>',
         f'<text x="64" y="35" font-family="{SANS}" font-size="20" font-weight="700" fill="{TEXT}" letter-spacing="4">{esc(title)}</text>']
    px = W - 8 - total * 17
    for i in range(total):
        on = i < num
        b.append(f'<path d="{hexpath(px + i*17 + 8, 24, 6.5)}" fill="{PURPLE if on else "none"}" fill-opacity="{1 if i == num-1 else .35}" '
                 f'stroke="{PURPLE}" stroke-opacity="{.9 if on else .35}" stroke-width="1.2"/>')
    b.append(f'<text x="{px-14}" y="29" font-size="13" fill="{MUTED}" text-anchor="end">{esc(meta)}</text>')
    b.append(f'<rect x="0" y="51" width="{W}" height="1.5" fill="url(#gFade)"/>')
    b.append(f'<rect class="sweep" x="0" y="50.5" width="110" height="2.5" fill="url(#gPulse)"/></g>')
    write(f"section-{slug}.svg", svg_doc(W, H, f"Section {num}: {title.title()}", "\n".join(b)))


# =============================================================== OVERVIEW ===
def overview():
    """Two cards (about / status) so they sit side by side on desktop and stack on phones."""
    W = W_CARD
    bio = wrap(BIO, 17, W - 52)
    kv = [("name", "SHARUU!"), ("github", "SHARUU-dev"), ("field", "Computer Engineering"),
          ("focus", "Backend · AI apps · Automation"), ("also", "Cybersecurity · Systems")]
    left_h = 52 + len(bio) * 29 + 4 + 28 + len(kv) * 22 + 74
    rows = [(l, c, wrap(t, 13, W - 52)) for l, c, t in STATUS]
    right_h = 58 + sum(34 + len(ls) * 20 + 14 for _, _, ls in rows)
    H = max(left_h, right_h)
    # about
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="8" width="3" height="{H-16}" fill="{PURPLE}"/>',
         f'<text x="28" y="36" font-size="13" fill="{MUTED}" letter-spacing="3">// about</text>']
    for i, ln in enumerate(bio):
        b.append(f'<text x="28" y="{80+i*29}" font-size="17" fill="{TEXT}">{esc(ln)}</text>')
    y = 80 + len(bio) * 29 + 4
    b.append(f'<rect x="28" y="{y}" width="{W-56}" height="1" fill="{LINE}"/>')
    for i, (k, v) in enumerate(kv):
        b.append(f'<text x="28" y="{y+28+i*22}" font-size="14" xml:space="preserve"><tspan fill="{GREEN}">&gt;</tspan>'
                 f'<tspan fill="{KEY}"> {k.ljust(7).replace(" ", chr(160))}</tspan><tspan fill="{TEXT}">{esc(v)}</tspan></text>')
    b.append(f'<path d="{hexpath(W-40, H-30, 9)}" fill="{GREEN}" fill-opacity=".22" stroke="{GREEN}" stroke-width="1.2"/>')
    b.append(f'<text x="{W-58}" y="{H-25}" font-size="12" fill="{LAV}" text-anchor="end" letter-spacing="1">build · break · debug · learn</text>')
    write("overview-about.svg", svg_doc(W, H, "About: " + BIO, "\n".join(b)))
    # status
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="8" width="3" height="{H-16}" fill="{GREEN}"/>',
         f'<text x="28" y="36" font-size="13" fill="{MUTED}" letter-spacing="3">// status</text>',
         f'<circle class="pulse" cx="{W-26}" cy="31" r="4" fill="{GREEN}"/>']
    y = 58
    for i, (lab, ck, lines) in enumerate(rows):
        c = COL[ck]
        if i:
            b.append(f'<rect x="28" y="{y-8}" width="{W-56}" height="1" fill="{LINE}"/>')
        pw = tw(lab, 11, 1.6) + 28
        b.append(f'<rect x="28" y="{y+4}" width="{pw:.1f}" height="22" rx="11" fill="{c}" fill-opacity=".10" stroke="{c}" stroke-opacity=".7"/>')
        b.append(f'<circle cx="41" cy="{y+15}" r="3" fill="{c}"/>')
        b.append(f'<text x="51" y="{y+19}" font-size="11" font-weight="700" letter-spacing="1.6" fill="{c}">{lab}</text>')
        for j, ln in enumerate(lines):
            b.append(f'<text x="28" y="{y+46+j*20}" font-size="13" fill="{TEXT}">{esc(ln)}</text>')
        y += 34 + len(lines) * 20 + 14
    write("overview-status.svg", svg_doc(W, H, "Status: " + "; ".join(f"{l.lower()}: {t}" for l, _, t in STATUS), "\n".join(b)))


# ================================================================ STACK =====
def stack_cards():
    PAD = 22
    inner = W_CARD - 2 * PAD
    laid = []
    for title, groups in STACK:
        y, parts, count = 74, [], 0
        for glabel, items in groups:
            parts.append(f'<text x="{PAD}" y="{y}" font-size="11" fill="{MUTED}" letter-spacing="2">{esc(glabel.upper())}</text>')
            s, y2 = flow(items, PAD, y + 10, inner)
            parts.append(s)
            y = y2 + 12
            count += len(items)
        laid.append((title, parts, y, count))
    for i in range(0, len(laid), 2):
        pair = laid[i:i + 2]
        H = max(p[2] for p in pair) + 2
        for k, (title, parts, _, count) in enumerate(pair):
            idx = i + k + 1
            b = [f'<rect width="{W_CARD}" height="{H}" fill="{BG}"/>',
                 f'<rect x=".5" y=".5" width="{W_CARD-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
                 f'<rect x="0" y="8" width="3" height="{H-16}" fill="{PURPLE}"/>',
                 f'<path d="{hexpath(W_CARD-62, H-46, 52)}" fill="none" stroke="{PURPLE}" stroke-opacity=".06" stroke-width="2"/>',
                 f'<text x="{PAD}" y="38" font-size="13" font-weight="700" fill="{GREEN}">{idx:02d}</text>',
                 f'<text x="{PAD+30}" y="38" font-size="13" font-weight="700" fill="{LAV}" letter-spacing="3">{esc(title)}</text>',
                 f'<text x="{W_CARD-PAD-14}" y="38" font-size="12" fill="{MUTED}" text-anchor="end">{count} items</text>',
                 f'<circle class="pulse" style="animation-delay:{idx*.4:.1f}s" cx="{W_CARD-PAD-3}" cy="34" r="3.5" fill="{GREEN}"/>',
                 f'<rect x="{PAD}" y="50" width="{inner}" height="1" fill="{LINE}"/>'] + parts
            names = ", ".join(lbl for _, its in [g for t, g in STACK if t == title][0] for lbl, _ in its)
            slug = ["languages", "web", "ai", "data", "security", "tools"][idx - 1]
            write(f"stack-{slug}.svg", svg_doc(W_CARD, H, f"{title.title()}: {names}", "\n".join(b)))


# ============================================================== PROJECTS ====
def art_bee_ai(w, h):
    cx, cy = w / 2, h / 2
    layers = [3, 4, 5, 4, 3]
    gx = (w - 120) / (len(layers) - 1)
    gy = min(30, (h - 40) / 4)
    pts = []
    for li, n in enumerate(layers):
        x = 60 + li * gx
        pts.append([(x, cy + (k - (n - 1) / 2) * gy) for k in range(n)])
    out = [f'<path d="{hexpath(cx, cy, min(h/2-6, 92))}" fill="{PURPLE}" fill-opacity=".05" stroke="{PURPLE}" stroke-opacity=".35" stroke-width="1.4"/>']
    n = 0
    for a, bb in zip(pts, pts[1:]):
        for (x1, y1) in a:
            for (x2, y2) in bb:
                n += 1
                out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PURPLE}" stroke-opacity=".28" stroke-width="1"/>')
    k = 0
    for li, layer in enumerate(pts):
        for (x, y) in layer:
            k += 1
            hot = (li + k) % 5 == 0
            col = GREEN if hot else LAV
            out.append(f'<circle class="pulse" style="animation-delay:{(k*.37)%3:.2f}s" cx="{x:.1f}" cy="{y:.1f}" r="{6 if hot else 4.5}" fill="{col}" fill-opacity=".9"/>')
    return "".join(out)


def art_bee_os(w, h):
    x0, y0, pw, ph = 58, 24, w - 116, h - 48
    out = [f'<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="10" fill="{PANEL2}" stroke="{LINE}"/>',
           f'<rect x="{x0}" y="{y0}" width="{pw}" height="22" rx="10" fill="#0d0a1c"/>',
           f'<rect x="{x0}" y="{y0+12}" width="{pw}" height="10" fill="#0d0a1c"/>']
    for i, c in enumerate([PD, PURPLE, GREEN]):
        out.append(f'<circle cx="{x0+16+i*14}" cy="{y0+11}" r="3.5" fill="{c}"/>')
    side = 58
    out.append(f'<rect x="{x0+side}" y="{y0+22}" width="1" height="{ph-22}" fill="{LINE}"/>')
    for i in range(min(6, int((ph - 40) / 20))):
        yy = y0 + 36 + i * 20
        out.append(f'<rect x="{x0+12}" y="{yy}" width="{side-24}" height="8" rx="4" fill="{PURPLE}" fill-opacity="{.5 if i == 1 else .16}"/>')
    rows = min(5, int((ph - 40) / 26))
    for i in range(rows):
        yy = y0 + 34 + i * 26
        rw = pw - side - 28
        out.append(f'<rect x="{x0+side+14}" y="{yy}" width="{rw}" height="20" rx="6" fill="#1a1330" stroke="#2f2352"/>')
        out.append(f'<rect x="{x0+side+26}" y="{yy+7}" width="{[90,130,70,110,100][i]}" height="6" rx="3" fill="{LAV}" fill-opacity=".4"/>')
        on = i in (0, 2)
        tx = x0 + side + 14 + rw - 40
        out.append(f'<rect x="{tx}" y="{yy+4}" width="28" height="12" rx="6" fill="{GREEN if on else LINE}" fill-opacity="{.85 if on else 1}"/>')
        out.append(f'<circle cx="{tx+(21 if on else 7)}" cy="{yy+10}" r="4.5" fill="{TEXT}"/>')
    out.append(f'<circle class="pulse" cx="{x0+pw-16}" cy="{y0+11}" r="3.5" fill="{GREEN}"/>')
    return "".join(out)


def art_sky(w, h):
    cx, cy = w / 2, h - 34
    out = [f'<defs><radialGradient id="orb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ecfdf5"/><stop offset=".45" stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient></defs>']
    for i, (x, y) in enumerate([(52, 30), (110, 64), (332, 36), (362, 82), (250, 22), (170, 28), (300, 70)]):
        if y < cy - 10:
            out.append(f'<circle class="pulse" style="animation-delay:{i*.5:.1f}s" cx="{x}" cy="{y}" r="1.8" fill="{LAV}"/>')
    for r in (40, 72, 108):
        out.append(f'<path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}" fill="none" stroke="{GREEN}" stroke-opacity="{.5 - r/300:.2f}" stroke-dasharray="3 6"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#orb)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="{GREEN}"/>')
    out.append(f'<rect x="40" y="{cy}" width="{w-80}" height="1.5" fill="{GREEN}" fill-opacity=".6"/>')
    for i in range(1, 5):
        yy = cy + i * 7 + i * i
        if yy < h - 4:
            out.append(f'<rect x="{40 - i*8}" y="{yy:.1f}" width="{w-80+i*16}" height="1" fill="{PURPLE}" fill-opacity="{.5 - i*.09:.2f}"/>')
    for i, bh in enumerate([10, 18, 26, 18, 10]):
        out.append(f'<rect class="bar" style="animation-delay:{i*.15:.2f}s" x="{cx+66+i*8}" y="{cy-bh/2-22:.1f}" width="4" height="{bh}" rx="2" fill="{LAV}" fill-opacity=".7"/>')
    return "".join(out)


def art_sentinel(w, h):
    cx, cy = w / 2, h / 2
    R = min(h / 2 - 8, 92)
    out = []
    for r in (R, R * .66, R * .33):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="{PURPLE}" stroke-opacity=".45"/>')
    out.append(f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="{LINE}"/><line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" stroke="{LINE}"/>')
    ex, ey = cx + R * math.cos(math.radians(-40)), cy + R * math.sin(math.radians(-40))
    out.append(f'<g class="spin" style="transform-origin:{cx}px {cy}px"><path d="M {cx} {cy} L {cx+R:.1f} {cy} A {R:.1f} {R:.1f} 0 0 0 {ex:.1f} {ey:.1f} Z" fill="{GREEN}" fill-opacity=".20"/>'
               f'<line x1="{cx}" y1="{cy}" x2="{cx+R:.1f}" y2="{cy}" stroke="{GREEN}" stroke-width="2"/></g>')
    for i, (dx, dy) in enumerate([(.5, -.4), (-.6, .25), (.25, .62), (-.35, -.58)]):
        out.append(f'<circle class="pulse" style="animation-delay:{i*.7:.1f}s" cx="{cx+dx*R:.1f}" cy="{cy+dy*R:.1f}" r="3.2" fill="{GREEN}"/>')
    s = 22
    out.append(f'<path d="M {cx} {cy-s} L {cx+s*.8:.1f} {cy-s*.6:.1f} V {cy+s*.1:.1f} C {cx+s*.8:.1f} {cy+s*.6:.1f} {cx+s*.25:.1f} {cy+s*.95:.1f} {cx} {cy+s*1.1:.1f} '
               f'C {cx-s*.25:.1f} {cy+s*.95:.1f} {cx-s*.8:.1f} {cy+s*.6:.1f} {cx-s*.8:.1f} {cy+s*.1:.1f} V {cy-s*.6:.1f} Z" fill="{PANEL}" stroke="{PURPLE}" stroke-width="2"/>')
    out.append(f'<text x="{cx}" y="{cy+5}" font-size="11" font-weight="700" fill="{LAV}" text-anchor="middle">C++</text>')
    return "".join(out)


ARTS = {"bee-ai": art_bee_ai, "bee-os": art_bee_os, "sky": art_sky, "sentinel": art_sentinel}


def project_cards():
    PAD, MIN_ART = 22, 170
    inner = W_CARD - 2 * PAD
    info = {}
    for slug, name, kind, desc, tags in PROJECTS:
        dl = wrap(desc, 15, inner)
        tag_svg, ty = flow([(t, None) for t in tags], PAD, 0, inner, row_h=36, h=28) if tags else ("", 0)
        text_h = 62 + 22 + len(dl) * 24 + (14 + ty if tags else 0) + 18
        info[slug] = (dl, tags, text_h)
    num = {p[0]: i + 1 for i, p in enumerate(PROJECTS)}
    for i in range(0, len(PROJECTS), 2):
        pair = PROJECTS[i:i + 2]
        text_h = max(info[p[0]][2] for p in pair)
        H = MIN_ART + text_h
        for slug, name, kind, desc, tags in pair:
            dl, _, own_h = info[slug]
            art_h = H - own_h
            b = [f'<rect width="{W_CARD}" height="{H}" fill="{BG}"/>',
                 f'<rect x=".5" y=".5" width="{W_CARD-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
                 f'<clipPath id="art"><rect x="1" y="1" width="{W_CARD-2}" height="{art_h}" rx="7"/></clipPath>',
                 f'<g clip-path="url(#art)"><rect x="1" y="1" width="{W_CARD-2}" height="{art_h}" fill="#0c0a16"/>'
                 f'<rect x="1" y="1" width="{W_CARD-2}" height="{art_h}" fill="url(#grid)"/>'
                 f'<rect class="sweep" x="0" y="1" width="140" height="{art_h}" fill="{PURPLE}" fill-opacity=".05"/>'
                 f'<g class="float">{ARTS[slug](W_CARD, art_h)}</g></g>',
                 f'<rect x="1" y="{art_h}" width="{W_CARD-2}" height="1" fill="{LINE}"/>',
                 f'<text x="{PAD}" y="30" font-size="13" fill="{MUTED}" letter-spacing="2">P/{num[slug]:02d}</text>']
            kw = tw(kind, 11, 1.5) + 24
            kx = W_CARD - PAD - kw
            b.append(f'<rect x="{kx:.1f}" y="14" width="{kw:.1f}" height="24" rx="12" fill="{PANEL}" fill-opacity=".9" stroke="{PURPLE}" stroke-opacity=".7"/>')
            b.append(f'<text x="{kx+kw/2:.1f}" y="30" font-size="11" font-weight="700" letter-spacing="1.5" fill="{LAV}" text-anchor="middle">{kind}</text>')
            y = art_h + 56
            b.append(f'<text x="{PAD}" y="{y}" font-family="{SANS}" font-size="34" font-weight="800" letter-spacing="1" fill="url(#gWord)">{esc(name)}</text>')
            b.append(f'<rect x="{PAD}" y="{y+14}" width="36" height="2" fill="{GREEN}" fill-opacity=".85"/>')
            for j, ln in enumerate(dl):
                b.append(f'<text x="{PAD}" y="{y+42+j*24}" font-size="15" fill="{TEXT}">{esc(ln)}</text>')
            if tags:
                ty0 = y + 42 + len(dl) * 24 - 6
                s, _ = flow([(t, None) for t in tags], PAD, ty0, inner, row_h=36, h=28)
                b.append(s)
            write(f"project-{slug}.svg", svg_doc(W_CARD, H, f"{name}: {desc}" + (f" Tags: {', '.join(tags)}." if tags else ""), "\n".join(b)))


# ============================================================== SERVICES ====
def service_cards():
    W, H = W_CARD, 104
    for i, (name, price, delivery) in enumerate(SERVICES):
        b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
             f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
             f'<rect x="0" y="8" width="3" height="{H-16}" fill="{PURPLE}"/>',
             f'<text x="24" y="38" font-size="12" fill="{MUTED}" letter-spacing="2">0{i+1} / BUILD</text>',
             f'<text x="24" y="72" font-size="22" font-weight="700" fill="{TEXT}">{esc(name)}</text>',
             f'<text x="{W-24}" y="46" font-size="20" font-weight="700" fill="{GREEN}" text-anchor="end">{esc(price)}</text>',
             f'<text x="{W-24}" y="72" font-size="14" fill="{KEY}" text-anchor="end">{esc(delivery)}</text>',
             f'<rect x="24" y="84" width="40" height="2" fill="{GREEN}" fill-opacity=".7"/>']
        write(f"service-{i+1}.svg", svg_doc(W, H, f"{name}: {price}, delivery {delivery}", "\n".join(b)))


# =============================================================== CONNECT ====
def link_cards():
    W, H = W_CARD, 76
    for label, ic, handle, url in LINKS:
        col = readable(BRAND[ic])
        b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
             f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{PANEL}" stroke="{PURPLE if url else LINE}" stroke-opacity="{.65 if url else 1}"/>',
             f'<circle cx="-4" cy="38" r="70" fill="{col}" fill-opacity=".05"/>',
             f'<rect x="16" y="16" width="44" height="44" rx="12" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".5"/>',
             icon(("simple", ic), 26, 26, 24, col),
             f'<text x="76" y="35" font-family="{SANS}" font-size="18" font-weight="700" fill="{TEXT}">{label}</text>',
             f'<text x="76" y="56" font-size="14" fill="{LAV}">{esc(handle)}</text>']
        b.append(f'<text x="{W-26}" y="45" font-family="{SANS}" font-size="20" fill="{GREEN}" text-anchor="end">↗</text>' if url else
                 f'<text x="{W-22}" y="44" font-size="11" fill="{MUTED}" text-anchor="end" letter-spacing="1.5">USERNAME</text>')
        write(f"link-{label.lower()}.svg", svg_doc(W, H, f"{label}: {handle}", "\n".join(b)))


# ================================================================ FOOTER ====
def footer():
    W, H = W_FULL, 84
    msg = "idea → code → error → debug → learn → build → repeat"
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<defs><clipPath id="sw"><rect class="sweep" x="0" y="0" width="140" height="{H}"/></clipPath></defs>',
         f'<path d="{hexpath(30, 34, 12)}" fill="none" stroke="{PURPLE}" stroke-opacity=".6" stroke-width="1.4"/>',
         f'<path d="{hexpath(W-30, 34, 12)}" fill="none" stroke="{PURPLE}" stroke-opacity=".6" stroke-width="1.4"/>',
         f'<rect x="56" y="33.5" width="40" height="1" fill="{LINE}"/><rect x="{W-96}" y="33.5" width="40" height="1" fill="{LINE}"/>',
         f'<text x="{W/2}" y="40" font-size="17" letter-spacing="1" text-anchor="middle" fill="{MUTED}">{msg}</text>',
         f'<g clip-path="url(#sw)"><text x="{W/2}" y="40" font-size="17" letter-spacing="1" text-anchor="middle" fill="{LAV}">{msg}</text></g>',
         f'<text x="{W/2}" y="68" font-family="{SANS}" font-size="13" fill="{MUTED}" text-anchor="middle" letter-spacing="2">SHARUU! · BUILDING IDEAS INTO TECHNOLOGY</text>']
    write("footer.svg", svg_doc(W, H, "idea, code, error, debug, learn, build, repeat. SHARUU! Building ideas into technology.", "\n".join(b)))


# ======================================================= PLACEHOLDERS =======
def snake_placeholder():
    W, H = W_FULL, 176
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>']
    cols, size, gap = 53, 12, 3
    x0 = (W - cols * (size + gap)) / 2 + 2
    for c in range(cols):
        for r in range(7):
            b.append(f'<rect x="{x0+c*(size+gap):.1f}" y="{26+r*(size+gap)}" width="{size}" height="{size}" rx="2" fill="#1a1330"/>')
    b.append(f'<text x="{W/2}" y="158" font-size="12" fill="{MUTED}" text-anchor="middle" letter-spacing="1">contribution snake · generated by GitHub Actions on the first workflow run</text>')
    return svg_doc(W, H, "Contribution snake. Generated by GitHub Actions; this placeholder is replaced on the first run.", "\n".join(b))


if __name__ == "__main__":
    hero()
    section("overview", 1, "OVERVIEW", "who · what · status")
    section("stack", 2, "STACK", "six areas, no duplicates")
    section("projects", 3, "PROJECTS", "four independent builds")
    section("telemetry", 4, "TELEMETRY", "live from GitHub")
    section("contact", 5, "WORK WITH ME", "freelance · contact")
    overview()
    stack_cards()
    project_cards()
    service_cards()
    link_cards()
    footer()
    write_if_missing("telemetry.svg", update_stats.render(update_stats.placeholder_data()))
    write_if_missing("snake-dark.svg", snake_placeholder())
    print("generated", len([f for f in os.listdir(OUT) if f.endswith(".svg")]), "svg files in", OUT)
