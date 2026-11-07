# scripts

| File | What it does |
|---|---|
| `generate_assets.py` | Builds every static SVG in `assets/` (hero, sections, stack, projects, services, links, footer). All copy is in the DATA block at the top. |
| `update_stats.py` | Builds `assets/telemetry.svg` from real GitHub API data. Run by the workflow; leaves the file untouched if the API is unreachable. |
| `check_readme.py` | Validates README image paths (case-exact), SVG validity/self-containment, alt text, orphan assets and banned text. |
| `icons.json` | Vendored icon paths: [Simple Icons](https://simpleicons.org) (CC0), plus a few Material Design Icons / Octicons glyphs. Brand logos remain trademarks of their owners. |

Regenerate after editing copy:

```bash
python3 scripts/generate_assets.py
python3 scripts/check_readme.py
```

`telemetry.svg` and `snake-dark.svg` are only written by `generate_assets.py` when missing (as placeholders),
so re-running it never overwrites live data.
