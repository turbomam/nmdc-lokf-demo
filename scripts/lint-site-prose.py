#!/usr/bin/env python3
"""Check the built site for typography that should never reach a reader.

An em dash sat in the site footer, so on all 8 pages, plus one in the homepage
meta description and one in the graph page title. Vale runs against issue and
pull request bodies; nothing looked at the site, so the text most people read
was the only text nobody checked.

This lints `dist/`, meaning exactly what ships, rather than the sources that
produce it. That way code comments are out of scope for free (they are not
rendered), and anything arriving from the scaffold, from `knowledge/`, or from a
template update is caught the same way.

Usage:  python3 scripts/lint-site-prose.py [dist_dir]
Exit:   0 clean, 1 findings, 2 nothing to check
"""

import html
import pathlib
import re
import sys

# Character, name, what to use instead. Keep the reason in the message: the
# person who trips this is usually not the person who wrote the text.
BANNED = {
    "—": ("em dash", "comma, period, colon, or parentheses"),
    "–": ("en dash", '"to" for ranges, or a hyphen'),
}

STRIP = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
BODY = re.compile(r"<body\b[^>]*>(.*?)</body>", re.S | re.I)
META = re.compile(r"<meta\b[^>]*>", re.I)
ATTR = re.compile(r"""([a-zA-Z-]+)\s*=\s*("([^"]*)"|'([^']*)')""")


def body_text(markup: str) -> str:
    """Rendered text only.

    Scan the body element rather than the whole document. Running this over the
    full markup pulls in head content, so a title finding gets reported twice,
    once here and once by head_fields, and the duplicate is labelled with the
    wrong region.
    """
    m = BODY.search(markup)
    region = m.group(1) if m else markup
    return html.unescape(TAG.sub(" ", STRIP.sub(" ", region)))


def head_fields(markup: str) -> list[tuple[str, str]]:
    """Title and meta description: read by people, invisible to a body scan."""
    out = []
    if m := re.search(r"<title[^>]*>(.*?)</title>", markup, re.S | re.I):
        out.append(("<title>", html.unescape(TAG.sub("", m.group(1)))))
    # Match the tag, then read its attributes, rather than assuming name comes
    # before content. A build is free to emit them in either order, or to put
    # other attributes between them.
    for tag in META.findall(markup):
        attrs = {k.lower(): (v3 if v3 is not None else v4) for k, _, v3, v4 in ATTR.findall(tag)}
        if attrs.get("name", "").lower() == "description" and "content" in attrs:
            out.append(("meta description", html.unescape(attrs["content"])))
    return out


def context(text: str, index: int, width: int = 44) -> str:
    lo, hi = max(0, index - width), min(len(text), index + width)
    return " ".join(text[lo:hi].split())


def main(argv: list[str]) -> int:
    root = pathlib.Path(argv[1] if len(argv) > 1 else "dist")
    if not root.is_dir():
        print(f"{root} does not exist. Build the site first: just site", file=sys.stderr)
        return 2

    pages = sorted(root.rglob("*.html"))
    if not pages:
        print(f"No HTML under {root}. Build the site first: just site", file=sys.stderr)
        return 2

    findings = []
    for page in pages:
        markup = page.read_text(encoding="utf-8", errors="replace")
        regions = [("body", body_text(markup))] + head_fields(markup)
        for where, text in regions:
            for char, (name, instead) in BANNED.items():
                for m in re.finditer(re.escape(char), text):
                    findings.append((page, where, name, instead, context(text, m.start())))

    for page, where, name, instead, ctx in findings:
        print(f"{page}: {name} in {where}\n    ...{ctx}...\n    use {instead}")

    if findings:
        n = len(findings)
        pages_hit = len({f[0] for f in findings})
        print(
            f"\n{n} finding{'s' if n != 1 else ''} across {pages_hit} of {len(pages)} page(s).",
            file=sys.stderr,
        )
        print(
            "These come from string literals in src/ or prose in knowledge/, "
            "including text inherited from the lokf new scaffold.",
            file=sys.stderr,
        )
        return 1

    print(f"{len(pages)} page(s) checked, no banned typography.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
