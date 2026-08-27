#!/usr/bin/env python3
"""Check the built site for typography that should never reach a reader.

An em dash sat in the site footer, so on all 8 pages, plus one in the homepage
meta description and one in the graph page title. Vale runs against issue and
pull request bodies; nothing looked at the site, so the text most people read
was the only text nobody checked.

Scope is deliberately the three regions those instances were in: rendered body
text, the page title, and the meta description. An earlier version of this file
also scanned attributes, inline scripts and client bundles. That coverage caught
nothing real in this repository, cost 250 lines, and introduced its own defects,
including false positives on valid markup and a path traversal out of the scan
root. Widening it again is worth doing against a real instance, not against a
hypothetical one. See issue 56 for what is not covered.

Lints `dist/`, meaning exactly what ships. Code comments are out of scope for
free because they are not rendered, and text inherited from the `lokf new`
scaffold is caught the same as our own, which matters because all three
instances came from scaffold.

Parsing goes through `html.parser` rather than regular expressions. Four bugs in
the earlier version came from matching markup with patterns.

Usage:  python3 scripts/lint-site-prose.py [dist_dir]
Exit:   0 clean, 1 findings, 2 nothing to check
"""

import pathlib
import re
import sys
from html.parser import HTMLParser

# Character, name, what to use instead. Keep the reason in the message: the
# person who trips this is usually not the person who wrote the text.
BANNED = {
    "—": ("em dash", "comma, period, colon, or parentheses"),
    "–": ("en dash", '"to" for ranges, or a hyphen'),
}


class PageReader(HTMLParser):
    """Body text, title and meta description, as a reader meets them."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.regions: list[tuple[str, str]] = []
        self._body: list[str] = []
        self._title = ""
        self._in_body = 0
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body":
            self._in_body += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("script", "style"):
            self._skip += 1
        elif tag == "meta":
            a = {k.lower(): (v or "") for k, v in attrs}
            if a.get("name", "").lower() == "description":
                self.regions.append(("meta description", a.get("content", "")))

    def handle_endtag(self, tag: str) -> None:
        if tag == "body":
            self._in_body = max(0, self._in_body - 1)
        elif tag == "title":
            self._in_title = False
        elif tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title += data
        elif self._in_body and not self._skip:
            self._body.append(data)

    def result(self) -> list[tuple[str, str]]:
        out = [("body", " ".join(self._body))]
        if self._title.strip():
            out.append(("<title>", self._title))
        return out + self.regions


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1] if len(argv) > 1 else "dist")
    pages = sorted(root.rglob("*.html")) if root.is_dir() else []
    if not pages:
        print(f"No HTML under {root}. Build the site first: just site", file=sys.stderr)
        return 2

    findings = []
    for page in pages:
        reader = PageReader()
        reader.feed(page.read_text(encoding="utf-8", errors="replace"))
        reader.close()
        for where, text in reader.result():
            for char, (name, instead) in BANNED.items():
                for m in re.finditer(re.escape(char), text):
                    lo, hi = max(0, m.start() - 44), m.start() + 44
                    ctx = " ".join(text[lo:hi].split())
                    findings.append(f"{page}: {name} in {where}\n    ...{ctx}...\n    use {instead}")

    for f in findings:
        print(f)
    if findings:
        print(f"\n{len(findings)} finding(s). These come from string literals in src/ or prose "
              "in knowledge/, including text inherited from the lokf new scaffold.", file=sys.stderr)
        return 1
    print(f"{len(pages)} page(s) checked, no banned typography.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
