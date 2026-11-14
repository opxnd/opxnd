
import os
import json
import urllib.request
from pathlib import Path

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
            "User-Agent": "opxnd-profile",
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

        data = api(
            f"/repos/{OWNER}/{repo['name']}/languages"
        )

        languages.update(data.keys())

    page += 1

images = []

for language in sorted(languages):
    icon = ICONS.get(language)

    if icon:
        images.append(
            f'<img src="https://skillicons.dev/icons?i={icon}" '
            f'width="55" alt="{language}" />'
        )

content = (
    '<div align="center">\n\n'
    + "\n".join(images)
    + '\n\n</div>'
    if images else "No languages detected."
)

text = README.read_text(encoding="utf-8")

start = "<!-- LANGUAGES_START -->"
end = "<!-- LANGUAGES_END -->"

if text.count(start) != 1 or text.count(end) != 1:
    raise ValueError("Language markers missing or duplicated")

before, remainder = text.split(start, 1)
_, after = remainder.split(end, 1)

updated = before + start + "\n" + content + "\n" + end + after

README.write_text(updated, encoding="utf-8")
