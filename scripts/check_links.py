#!/usr/bin/env python3
"""Fail if any page in dist/ links to a local file that does not exist.

Usage: python3 scripts/check_links.py   (run after scripts/build_site.py)
"""
import pathlib
import re
import sys
import urllib.parse

DIST = pathlib.Path(__file__).resolve().parent.parent / "dist"
REF = re.compile(r'(?:href|src)="(/[^"#]*)')


def exists(path):
    path = urllib.parse.unquote(path.split("?", 1)[0])
    target = DIST / path.lstrip("/")
    if path.endswith("/"):
        return (target / "index.html").exists()
    return target.exists() or (target / "index.html").exists()


def main():
    pages = sorted(DIST.rglob("*.html"))
    broken = {}
    for page in pages:
        for ref in set(REF.findall(page.read_text(encoding="utf-8"))):
            if not exists(ref):
                broken.setdefault(ref, []).append(str(page.relative_to(DIST)))
    if broken:
        for ref, where in sorted(broken.items()):
            print(f"broken: {ref}  (in {len(where)} pages, e.g. {where[0]})")
        sys.exit(1)
    print(f"OK: {len(pages)} pages, no broken local links")


if __name__ == "__main__":
    main()
