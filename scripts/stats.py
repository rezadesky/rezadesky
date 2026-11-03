"""Generate maroon gothic stats cards (assets/stats.svg, assets/langs.svg) from the GitHub API."""
import json, os, urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "rezadesky")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
BG, DEEP, MAROON, BLOOD, BONE, ASH = "#120406", "#2a0a0f", "#6e1423", "#9b2335", "#e9dfcf", "#8a7f74"
SERIF = "'Cormorant Garamond','Garamond','Georgia','Times New Roman',serif"
W, H = 420, 200


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": USER,
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def frame(title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">',
            f'<rect width="{W}" height="{H}" fill="{BG}"/>',
            f'<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="none" stroke="{MAROON}" stroke-width="1.5"/>',
            f'<rect x="11" y="11" width="{W-22}" height="{H-22}" fill="none" stroke="{BONE}" stroke-width=".6" opacity=".4"/>',
            f'<text x="{W/2}" y="40" text-anchor="middle" font-family="{SERIF}" font-size="15" letter-spacing="5" fill="{BLOOD}">{title}</text>',
            f'<line x1="40" y1="52" x2="{W-40}" y2="52" stroke="{MAROON}" stroke-width="1"/>']


def stats_svg(rows):
    s = frame("RECORDS")
    for i, (label, value) in enumerate(rows):
        y = 82 + i * 24
        s.append(f'<text x="48" y="{y}" font-family="{SERIF}" font-size="14" letter-spacing="2" fill="{ASH}">{label}</text>')
        s.append(f'<line x1="200" y1="{y-4}" x2="320" y2="{y-4}" stroke="{DEEP}" stroke-width="1" stroke-dasharray="2 4"/>')
        s.append(f'<text x="{W-48}" y="{y}" text-anchor="end" font-family="{SERIF}" font-size="16" fill="{BONE}">{value:,}</text>')
    return "\n".join(s + ["</svg>"])


def langs_svg(langs):
    s = frame("TONGUES")
    total = sum(b for _, b in langs) or 1
    shades = [BLOOD, MAROON, "#b5475a", "#4a0d17", "#c9a9a0", ASH]
    x = 48
    for (name, b), c in zip(langs, shades):  # stacked bar
        w = (W - 96) * b / total
        s.append(f'<rect x="{x:.1f}" y="66" width="{w:.1f}" height="8" fill="{c}"/>')
        x += w
    for i, ((name, b), c) in enumerate(zip(langs, shades)):
        col, row = i % 2, i // 2
        cx, cy = 52 + col * 170, 104 + row * 28
        s.append(f'<rect x="{cx-4}" y="{cy-9}" width="8" height="8" fill="{c}" transform="rotate(45 {cx} {cy-5})"/>')
        s.append(f'<text x="{cx+12}" y="{cy}" font-family="{SERIF}" font-size="14" fill="{BONE}">{escape(name)}</text>')
        s.append(f'<text x="{cx+150}" y="{cy}" text-anchor="end" font-family="{SERIF}" font-size="13" fill="{ASH}">{100*b/total:.1f}%</text>')
    return "\n".join(s + ["</svg>"])


def main():
    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
    langs = {}
    for r in repos:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    count = lambda q: api(f"/search/{q}")["total_count"]
    rows = [("STARS EARNED", sum(r["stargazers_count"] for r in repos)),
            ("COMMITS", count(f"commits?q=author:{USER}")),
            ("PULL REQUESTS", count(f"issues?q=author:{USER}+type:pr")),
            ("ISSUES", count(f"issues?q=author:{USER}+type:issue")),
            ("REPOSITORIES", len(repos))]
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    open(os.path.join(out, "stats.svg"), "w", encoding="utf-8").write(stats_svg(rows))
    open(os.path.join(out, "langs.svg"), "w", encoding="utf-8").write(langs_svg(top))
    print(rows, top)


if __name__ == "__main__":
    main()
