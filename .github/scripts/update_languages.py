
import os
import json
import urllib.request
from pathlib import Path
from html import escape

TOKEN = os.environ["PROFILE_STATS_TOKEN"]
OWNER = "opxnd"
README = Path("README.md")

ICONS = {
    "TypeScript": "ts",
    "JavaScript": "js",
    "HTML": "html",
    "CSS": "css",
    "Python": "py",
    "Java": "java",
    "C": "c",
    "C++": "cpp",
    "C#": "cs",
    "Go": "go",
    "Rust": "rust",
    "PHP": "php",
    "Ruby": "ruby",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Dart": "dart",
    "Shell": "bash",
}

def api(path):
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "opxnd-profile-stats",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)

languages = set()
page = 1

while True:
    repos = api(
        f"/user/repos?type=owner&per_page=100&page={page}"
    )
    if not repos:
        break

    for repo in repos:
        if repo["owner"]["login"].lower() != OWNER:
            continue
        if repo["name"] == OWNER:
            continue

        repo_languages = api(
            f"/repos/{OWNER}/{repo['name']}/languages"
        )
        languages.update(repo_languages.keys())

    page += 1

cells = []
for language in sorted(languages):
    name = escape(language)
    icon = ICONS.get(language)

    if icon:
        content = (
            f'<img src="https://skillicons.dev/icons?i={icon}" '
            f'width="55" alt="{name}" /><br />'
            f'<sub>{name}</sub>'
        )
    else:
        content = f'<strong>{name}</strong>'

    cells.append(f'<td align="center">{content}</td>')

rows = [
    "<tr>" + "".join(cells[i:i+5]) + "</tr>"
    for i in range(0, len(cells), 5)
]

table = (
    '<div align="center">\n<table>\n'
    + "\n".join(rows)
    + '\n</table>\n</div>'
    if rows else "No languages detected."
)

original = README.read_text(encoding="utf-8")
start = "<!-- LANGUAGES_START -->"
end = "<!-- LANGUAGES_END -->"

if original.count(start) != 1 or original.count(end) != 1:
    raise ValueError("README language markers missing or duplicated")

before, remainder = original.split(start, 1)
_, after = remainder.split(end, 1)

updated = before + start + "\n" + table + "\n" + end + after
README.write_text(updated, encoding="utf-8")
