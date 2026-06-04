#!/usr/bin/env python3
"""Generate static SVG widgets for the GitHub profile README.

Why static: common README widget providers go down, get rate-limited, or disable
Vercel deployments. Local SVGs keep the profile clean and predictable.
"""

from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path
from textwrap import shorten
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "widgets"
OWNER = "ooodnakov"
SELECTED_REPOS = ["ooodnakov-config", "my_website", "telegram_meme_autoposter"]

LANG_COLORS = {
    "Python": "#3572A5",
    "Jupyter Notebook": "#DA5B0B",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Kotlin": "#A97BFF",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Dockerfile": "#384d54",
    "Ruby": "#701516",
    "Java": "#b07219",
    "C++": "#f34b7d",
}

REPO_DESCRIPTIONS = {
    "ooodnakov-config": "Configs, scripts and personal automation glue.",
    "my_website": "Personal website: dnakov.ooo.",
    "telegram_meme_autoposter": "Telegram automation experiments.",
}


def gh_json(args: list[str]) -> Any:
    raw = subprocess.check_output(["gh", *args], cwd=ROOT, text=True)
    return json.loads(raw)


def svg_card(width: int, height: int, body: str) -> str:
    return f"""<svg width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" role=\"img\" aria-labelledby=\"title desc\">
  <title id=\"title\">GitHub profile widget</title>
  <desc id=\"desc\">Static profile widget generated from public GitHub data.</desc>
  <style>
    .card {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .title {{ fill: #e6edf3; font: 600 16px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
    .text {{ fill: #c9d1d9; font: 400 13px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
    .muted {{ fill: #8b949e; font: 400 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
    .num {{ fill: #58a6ff; font: 700 24px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
    .accent {{ fill: #58a6ff; }}
  </style>
  <rect class=\"card\" x=\"0.5\" y=\"0.5\" width=\"{width - 1}\" height=\"{height - 1}\" rx=\"12\" />
{body}
</svg>
"""


def repo_card(repo: dict) -> str:
    name = repo["name"]
    desc = html.escape(shorten(REPO_DESCRIPTIONS.get(name) or repo.get("description") or "GitHub repository", width=58, placeholder="…"))
    lang = repo.get("primaryLanguage") or {}
    lang_name = html.escape(lang.get("name") or "Code")
    lang_color = lang.get("color") or LANG_COLORS.get(lang_name, "#8b949e")
    stars = repo.get("stargazerCount", 0)
    forks = repo.get("forkCount", 0)
    updated = (repo.get("updatedAt") or "")[:10]
    body = f"""
  <text class=\"title\" x=\"22\" y=\"32\">{html.escape(name)}</text>
  <text class=\"text\" x=\"22\" y=\"58\">{desc}</text>
  <circle cx=\"28\" cy=\"91\" r=\"5\" fill=\"{lang_color}\" />
  <text class=\"muted\" x=\"40\" y=\"95\">{lang_name}</text>
  <text class=\"muted\" x=\"155\" y=\"95\">★ {stars}</text>
  <text class=\"muted\" x=\"215\" y=\"95\">⑂ {forks}</text>
  <text class=\"muted\" x=\"290\" y=\"95\">updated {updated}</text>
"""
    return svg_card(410, 120, body)


def stats_card(user: dict, repos: list[dict]) -> str:
    public_repos = user.get("public_repos", len(repos))
    followers = user.get("followers", 0)
    total_stars = sum(r.get("stargazerCount", 0) for r in repos if not r.get("isFork"))
    active_repos = sum(1 for r in repos if not r.get("isArchived") and not r.get("isFork"))
    body = f"""
  <text class=\"title\" x=\"22\" y=\"34\">GitHub pulse</text>
  <text class=\"muted\" x=\"22\" y=\"56\">Public, local, no flaky third-party stats</text>

  <text class=\"num\" x=\"26\" y=\"98\">{public_repos}</text>
  <text class=\"muted\" x=\"26\" y=\"118\">public repos</text>

  <text class=\"num\" x=\"135\" y=\"98\">{total_stars}</text>
  <text class=\"muted\" x=\"135\" y=\"118\">stars</text>

  <text class=\"num\" x=\"238\" y=\"98\">{followers}</text>
  <text class=\"muted\" x=\"238\" y=\"118\">followers</text>

  <text class=\"num\" x=\"335\" y=\"98\">{active_repos}</text>
  <text class=\"muted\" x=\"312\" y=\"118\">active repos</text>
"""
    return svg_card(410, 150, body)


def top_languages_card(lang_totals: dict[str, int]) -> str:
    top = sorted(lang_totals.items(), key=lambda x: x[1], reverse=True)[:6]
    total = sum(v for _, v in top) or 1
    x = 22
    segments = []
    for name, value in top:
        w = max(8, round(366 * value / total))
        color = LANG_COLORS.get(name, "#8b949e")
        segments.append(f'<rect x=\"{x}\" y=\"60\" width=\"{w}\" height=\"10\" rx=\"5\" fill=\"{color}\" />')
        x += w
    lines = []
    y = 98
    for i, (name, value) in enumerate(top):
        pct = value / sum(lang_totals.values()) * 100 if sum(lang_totals.values()) else 0
        col_x = 22 if i < 3 else 215
        line_y = y + (i % 3) * 22
        color = LANG_COLORS.get(name, "#8b949e")
        lines.append(f'<circle cx=\"{col_x + 5}\" cy=\"{line_y - 4}\" r=\"5\" fill=\"{color}\" />')
        lines.append(f'<text class=\"text\" x=\"{col_x + 18}\" y=\"{line_y}\">{html.escape(name)} {pct:.1f}%</text>')
    body = """
  <text class=\"title\" x=\"22\" y=\"34\">Top languages</text>
  <text class=\"muted\" x=\"22\" y=\"52\">Aggregated from public non-fork repositories</text>
  {segments}
  {lines}
""".format(segments="\n  ".join(segments), lines="\n  ".join(lines))
    return svg_card(410, 150, body)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    user = gh_json(["api", f"users/{OWNER}"])
    repos = gh_json([
        "repo",
        "list",
        OWNER,
        "--visibility=public",
        "--limit=100",
        "--json=name,description,stargazerCount,forkCount,primaryLanguage,isFork,isArchived,updatedAt,url",
    ])
    repo_by_name = {repo["name"]: repo for repo in repos}

    lang_totals: dict[str, int] = {}
    for repo in repos:
        if repo.get("isFork") or repo.get("isArchived"):
            continue
        langs = gh_json(["api", f"repos/{OWNER}/{repo['name']}/languages"])
        for name, value in langs.items():
            lang_totals[name] = lang_totals.get(name, 0) + int(value)

    (OUT / "profile-stats.svg").write_text(stats_card(user, repos), encoding="utf-8")
    (OUT / "top-languages.svg").write_text(top_languages_card(lang_totals), encoding="utf-8")

    for name in SELECTED_REPOS:
        repo = repo_by_name.get(name)
        if not repo:
            continue
        safe = name.lower().replace("_", "-")
        (OUT / f"repo-{safe}.svg").write_text(repo_card(repo), encoding="utf-8")

    print(f"Generated widgets in {OUT}")


if __name__ == "__main__":
    main()
