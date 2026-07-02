#!/usr/bin/env python3
"""Download section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

PEXELS: dict[str, tuple[str, str]] = {
    "hero.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "shared-bites.webp": (PEX.format(id="2338407"), "Pexels #2338407"),
    "sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "salads.webp": (PEX.format(id="1128678"), "Pexels #1128678"),
    "twelve-inch-pizzas.webp": (PEX.format(id="2147491"), "Pexels #2147491"),
    "sandwiches.webp": (PEX.format(id="1630757"), "Pexels #1630757"),
    "entrees.webp": (PEX.format(id="618785"), "Pexels #618785"),
    "pasta.webp": (PEX.format(id="2097090"), "Pexels #2097090"),
    "kids-menu.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "desserts.webp": (PEX.format(id="2089718"), "Pexels #2089718"),
    "signature-cocktails.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "classic-cocktails.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "mocktails.webp": (PEX.format(id="1267325"), "Pexels #1267325"),
    "beers.webp": (PEX.format(id="1304540"), "Pexels #1304540"),
    "white-wines.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "rose-wines.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "red-wines.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "prosecco-sparkling.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "champagne.webp": (PEX.format(id="1283219"), "Pexels #1283219"),
    "soft-drinks.webp": (PEX.format(id="1199957"), "Pexels #1199957"),
    "hot-drinks.webp": (PEX.format(id="302899"), "Pexels #302899"),
    "slideshow-burger.webp": (PEX.format(id="769289"), "Pexels #769289"),
    "slideshow-pizza.webp": (PEX.format(id="2147491"), "Pexels #2147491"),
    "slideshow-wings.webp": (PEX.format(id="2338407"), "Pexels #2338407"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "shared-bites": "shared-bites.webp",
    "sides": "sides.webp",
    "salads": "salads.webp",
    "twelve-inch-pizzas": "twelve-inch-pizzas.webp",
    "sandwiches": "sandwiches.webp",
    "entrees": "entrees.webp",
    "pasta": "pasta.webp",
    "kids-menu": "kids-menu.webp",
    "desserts": "desserts.webp",
    "signature-cocktails": "signature-cocktails.webp",
    "classic-cocktails": "classic-cocktails.webp",
    "mocktails": "mocktails.webp",
    "beers": "beers.webp",
    "white-wines": "white-wines.webp",
    "rose-wines": "rose-wines.webp",
    "red-wines": "red-wines.webp",
    "prosecco-sparkling": "prosecco-sparkling.webp",
    "champagne": "champagne.webp",
    "soft-drinks": "soft-drinks.webp",
    "hot-drinks": "hot-drinks.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>The Alley at East Gates — bowling, dining, and cocktails. "
            "Open daily 11AM–12 midnight.</p>"
        )
    text = (
        "---\n"
        'title: "The Alley at East Gates"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('twelve-inch-pizzas.webp')}\n"
        f"    - image: {img('shared-bites.webp')}\n"
        f"    - image: {img('signature-cocktails.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-burger.webp')}\n"
        f"    - image: {img('slideshow-pizza.webp')}\n"
        f"    - image: {img('slideshow-wings.webp')}\n"
        f"    - image: {img('signature-cocktails.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
