#!/usr/bin/env python3
"""Builds assets/telemetry.svg from REAL GitHub data (no third-party stats service).

Run by .github/workflows/profile.yml with the workflow's GITHUB_TOKEN:

    GITHUB_TOKEN=... python3 scripts/update_stats.py --user SHARUU-dev --out assets/telemetry.svg

Data sources: REST /users, /users/{u}/repos, /repos/{r}/languages and the GraphQL
contribution calendar. Forks are excluded from language and star totals.
If the REST calls fail the existing file is left untouched (exit code 1).
If only GraphQL fails, the card renders with the contribution panel marked unavailable.

Standard library only. `render(data)` is pure, so it can be tested offline.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

API = "https://api.github.com"
BG, PANEL, LINE = "#0a0a0f", "#100f18", "#2a2144"
PURPLE, LAV, TEXT, MUTED, KEY, GREEN = "#8b5cf6", "#c4b5fd", "#e7e5f2", "#8a86a3", "#9b8fd0", "#34d399"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "Inter,'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
LANG_COLORS = [PURPLE, GREEN, LAV, "#6d28d9", "#a78bfa", "#4b3f72"]
CW = 0.62


# ---------------------------------------------------------------- fetching --
def _req(url, token, body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "sharuu-profile-stats",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(user, token):
    u = _req(f"{API}/users/{user}", token)
    repos, page = [], 1
    while True:
        chunk = _req(f"{API}/users/{user}/repos?per_page=100&type=owner&page={page}", token)
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    langs = {}
    for r in own:
        try:
            for name, n in _req(f"{API}/repos/{r['full_name']}/languages", token).items():
                langs[name] = langs.get(name, 0) + n
        except urllib.error.URLError as e:
            print("warn: languages for", r["full_name"], e, file=sys.stderr)
    data = {
        "repos": u["public_repos"], "followers": u["followers"], "following": u["following"],
        "stars": sum(r["stargazers_count"] for r in own),
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
        "total": None, "cur": None, "longest": None, "weekly": None,
        "synced": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    q = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
           totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    try:
        res = _req(f"{API}/graphql", token, {"query": q, "variables": {"login": user}})
        cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]
        days = [c for w in weeks for c in w]
        data.update(total=cal["totalContributions"], weekly=[sum(w) for w in weeks])
        data["cur"], data["longest"] = streaks(days)
    except Exception as e:  # noqa: BLE001 - keep the REST data even if GraphQL is unavailable
        print("warn: contribution calendar unavailable:", e, file=sys.stderr)
    return data


def streaks(days):
    """days: daily contribution counts, oldest first. Today may still be empty."""
    longest = run = 0
    for c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    ds = list(days)
    if ds and ds[-1] == 0:
        ds.pop()
    cur = 0
    for c in reversed(ds):
        if c > 0:
            cur += 1
        else:
            break
    return cur, longest


def placeholder_data():
    """Shown only until the first workflow run. Counts verified on github.com/SHARUU-dev on 2026-11-04."""
    return {"repos": 6, "followers": 2, "following": 4, "stars": None, "langs": None,
            "total": None, "cur": None, "longest": None, "weekly": None, "synced": None}


# --------------------------------------------------------------- rendering --
def _e(s):
    return escape(str(s), {'"': "&quot;"})


def _n(v):
    return "—" if v is None else f"{v:,}"


def _icon(d, x, y, size, color):
    return f'<path transform="translate({x} {y}) scale({size/24:.4f})" d="{d}" fill="{color}"/>'


def render(data):
    here = os.path.dirname(os.path.abspath(__file__))
    icons = json.load(open(os.path.join(here, "icons.json"), encoding="utf-8"))["octicons"]
    W, H = 832, 392
    synced = data.get("synced")
    stamp = f"synced {synced}" if synced else "awaiting first sync"
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{LINE}"/>',
         f'<rect x="0" y="8" width="3" height="{H-16}" fill="{PURPLE}"/>',
         f'<text x="28" y="36" font-size="13" fill="{MUTED}" letter-spacing="3">// github telemetry</text>',
         f'<circle cx="{W-24-len(stamp)*12*CW-12:.1f}" cy="32" r="4" fill="{GREEN if synced else MUTED}"><animate attributeName="opacity" values="1;.25;1" dur="2.6s" repeatCount="indefinite"/></circle>',
         f'<text x="{W-24}" y="36" font-size="12" fill="{MUTED}" text-anchor="end">{_e(stamp)}</text>']
    # KPI tiles
    kpis = [("REPOSITORIES", data["repos"], "repo-24"), ("FOLLOWERS", data["followers"], "people-24"),
            ("FOLLOWING", data["following"], "person-24"), ("STARS EARNED", data["stars"], "star-24")]
    tw_, gap, x0 = 188, 12, 22
    for i, (label, val, ic) in enumerate(kpis):
        x = x0 + i * (tw_ + gap)
        b.append(f'<rect x="{x}" y="56" width="{tw_}" height="76" rx="8" fill="#15112a" stroke="#2f2352"/>')
        b.append(_icon(icons[ic], x + tw_ - 36, 70, 18, LAV))
        b.append(f'<text x="{x+16}" y="102" font-family="{SANS}" font-size="34" font-weight="800" fill="{TEXT}">{_n(val)}</text>')
        b.append(f'<text x="{x+16}" y="122" font-size="11" fill="{MUTED}" letter-spacing="2">{label}</text>')
    # contributions panel
    px, py, pw, ph = 22, 146, 500, 216
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="#15112a" stroke="#2f2352"/>')
    b.append(f'<text x="{px+16}" y="{py+26}" font-size="11" fill="{MUTED}" letter-spacing="2">CONTRIBUTIONS · LAST 12 MONTHS</text>')
    b.append(f'<text x="{px+16}" y="{py+68}" font-family="{SANS}" font-size="38" font-weight="800" fill="{TEXT}">{_n(data["total"])}</text>')
    for j, (lab, v) in enumerate([("CURRENT STREAK", data["cur"]), ("LONGEST STREAK", data["longest"])]):
        sx = px + 190 + j * 150
        b.append(f'<text x="{sx}" y="{py+48}" font-size="11" fill="{MUTED}" letter-spacing="1.5">{lab}</text>')
        b.append(f'<text x="{sx}" y="{py+70}" font-family="{SANS}" font-size="22" font-weight="700" fill="{GREEN}">{_n(v)}<tspan font-size="12" fill="{KEY}" font-weight="400"> days</tspan></text>')
    cx0, cy0, cw, ch = px + 16, py + 90, pw - 32, 94
    weekly = data.get("weekly")
    if weekly:
        mx = max(weekly) or 1
        n = len(weekly)
        step = cw / n
        for i, v in enumerate(weekly):
            h = max(2, (v / mx) * ch) if v else 2
            hi = i >= n - 4
            b.append(f'<rect x="{cx0+i*step:.1f}" y="{cy0+ch-h:.1f}" width="{step-2.5:.1f}" height="{h:.1f}" rx="1.5" '
                     f'fill="{GREEN if hi else PURPLE}" fill-opacity="{.95 if hi else (.35 + .6 * v / mx):.2f}"/>')
        b.append(f'<text x="{cx0}" y="{py+ph-8}" font-size="11" fill="{MUTED}">52 weeks ago</text>')
        b.append(f'<text x="{cx0+cw}" y="{py+ph-8}" font-size="11" fill="{MUTED}" text-anchor="end">this week</text>')
    else:
        b.append(f'<rect x="{cx0}" y="{cy0+ch-2}" width="{cw}" height="2" fill="{LINE}"/>')
        b.append(f'<text x="{cx0+cw/2}" y="{cy0+ch/2}" font-size="12" fill="{MUTED}" text-anchor="middle">weekly activity appears after the first sync</text>')
    # languages panel
    lx, lw = px + pw + 12, W - 22 - (px + pw + 12)
    b.append(f'<rect x="{lx}" y="{py}" width="{lw}" height="{ph}" rx="8" fill="#15112a" stroke="#2f2352"/>')
    b.append(f'<text x="{lx+16}" y="{py+26}" font-size="11" fill="{MUTED}" letter-spacing="2">TOP LANGUAGES</text>')
    langs = data.get("langs")
    if langs:
        total = sum(v for _, v in langs) or 1
        top = langs[:5]
        rest = total - sum(v for _, v in top)
        items = [(n, v) for n, v in top] + ([("Other", rest)] if rest > 0 else [])
        bx, bw = lx + 16, lw - 32
        b.append(f'<clipPath id="lb"><rect x="{bx}" y="{py+40}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lb)">')
        cur = bx
        for i, (n, v) in enumerate(items):
            w = bw * v / total
            b.append(f'<rect x="{cur:.1f}" y="{py+40}" width="{w:.1f}" height="10" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
            cur += w
        b.append('</g>')
        for i, (n, v) in enumerate(items):
            yy = py + 78 + i * 24
            b.append(f'<circle cx="{lx+22}" cy="{yy-4}" r="4.5" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
            b.append(f'<text x="{lx+36}" y="{yy}" font-size="13" fill="{TEXT}">{_e(n)}</text>')
            b.append(f'<text x="{lx+lw-16}" y="{yy}" font-size="13" fill="{LAV}" text-anchor="end">{100*v/total:.1f}%</text>')
    else:
        b.append(f'<text x="{lx+lw/2}" y="{py+ph/2}" font-size="12" fill="{MUTED}" text-anchor="middle">language mix appears</text>')
        b.append(f'<text x="{lx+lw/2}" y="{py+ph/2+18}" font-size="12" fill="{MUTED}" text-anchor="middle">after the first sync</text>')
    b.append(f'<text x="28" y="{H-8}" font-size="10.5" fill="{MUTED}">source: GitHub API · forks excluded from languages and stars · refreshed by GitHub Actions</text>')
    title = (f"GitHub telemetry: {_n(data['repos'])} repositories, {_n(data['followers'])} followers, "
             f"{_n(data['following'])} following, {_n(data['stars'])} stars earned. "
             f"Contributions in the last 12 months: {_n(data['total'])}; current streak {_n(data['cur'])} days; "
             f"longest streak {_n(data['longest'])} days.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{_e(title)}" font-family="{MONO}">\n<title>{_e(title)}</title>\n'
            f'<style>@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>\n'
            + "\n".join(b) + "\n</svg>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("PROFILE_USER", "SHARUU-dev"))
    ap.add_argument("--out", default="assets/telemetry.svg")
    ap.add_argument("--from-json", help="render from a saved data file instead of calling the API (testing)")
    a = ap.parse_args()
    try:
        data = json.load(open(a.from_json)) if a.from_json else fetch(a.user, os.environ.get("GITHUB_TOKEN"))
    except Exception as e:  # noqa: BLE001
        print("error: could not fetch GitHub data, leaving", a.out, "unchanged:", e, file=sys.stderr)
        return 1
    svg = render(data)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
