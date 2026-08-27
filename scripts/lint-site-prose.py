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
# Attributes a reader or a screen reader is shown. Stripping tags throws these
# away, so a banned character in a placeholder or an aria-label used to pass.
READER_ATTRS = ("placeholder", "title", "alt", "aria-label", "aria-description", "aria-placeholder")
ANY_TAG = re.compile(r"<[a-zA-Z][^>]*>")
SCRIPT_SRC = re.compile(r'<script[^>]*\bsrc=["\']([^"\']+)["\']', re.I)
INLINE_SCRIPT = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S | re.I)
JS_ESCAPE = re.compile(
    r"(\\*)\\(?:u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2}))"
)
TAG = re.compile(r"<[^>]+>")
BODY = re.compile(r"<body\b[^>]*>(.*?)</body>", re.S | re.I)
META = re.compile(r"<meta\b[^>]*>", re.I)
# One alternation per quote style. re.findall returns "" rather than None for an
# unmatched group, so the two value groups cannot be told apart by an is-None
# test. Callers take `dq or sq`, whichever is non-empty.
ATTR = re.compile(r"""([a-zA-Z-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')""")


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
        attrs = {k.lower(): (dq or sq) for k, dq, sq in ATTR.findall(tag)}
        if attrs.get("name", "").lower() == "description" and "content" in attrs:
            out.append(("meta description", html.unescape(attrs["content"])))
    return out


def reader_attributes(markup: str) -> list[tuple[str, str]]:
    """Text shown to a reader or a screen reader but held in an attribute."""
    out = []
    for tag in ANY_TAG.findall(markup):
        attrs = {k.lower(): (dq or sq) for k, dq, sq in ATTR.findall(tag)}
        for name in READER_ATTRS:
            if value := attrs.get(name):
                out.append((f"@{name}", html.unescape(value)))
    return out


def decode_js_escapes(text: str) -> str:
    """Turn active \\uXXXX and \\xXX escapes into the characters they denote.

    This build emits non-ASCII literally, measured end to end: an em dash placed
    in a src/ string arrives in the bundle as the character, not as an escape.
    Other bundlers, and this one under a different target or minifier setting,
    emit ASCII-only output. Decoding first means the check does not quietly stop
    working if that changes, which is the failure mode worth guarding: it would
    report clean rather than error.

    Only escapes preceded by an even number of backslashes are active. Where the
    backslash is itself escaped, the text is literal and stays literal.

    Widths are exact, and getting that wrong is silent. An unbraced ``\\u`` takes
    exactly four hex digits, so JavaScript reads ``"\\u2014and"`` as an em dash
    followed by ``and``. A pattern allowing up to six consumed ``2014a`` as one
    code point, produced a different character, and missed the dash entirely.
    Braced ``\\u{...}`` takes one to six; ``\\x`` takes exactly two.
    """

    def sub(m: re.Match[str]) -> str:
        prefix = m.group(1)
        if len(prefix) % 2:
            return m.group(0)
        digits = m.group(2) or m.group(3) or m.group(4)
        return prefix + chr(int(digits, 16))

    return JS_ESCAPE.sub(sub, text)


def script_text(root: pathlib.Path, markup: str) -> list[tuple[str, str]]:
    """Strings a script writes into the DOM.

    Astro emits client scripts as separate bundles under `_astro/`, so text a
    script renders never appears in the HTML and no amount of tag stripping will
    find it.

    These bundles are scanned as raw text rather than by extracting string
    literals. Pairing quotes with a regex is not reliable on minified output:
    scanning left to right, one unbalanced quote earlier in the file shifts
    every pair after it, and a real string silently stops being visible. That
    was happening here, and it produced a linter that reported clean on a bundle
    with a banned character in it. Minified output carries no comments, so a
    banned character in one of these files is in a string, and searching the
    text directly has no pairing problem to get wrong.
    """
    out = []
    for block in INLINE_SCRIPT.findall(markup):
        out.append(("inline script", decode_js_escapes(block)))
    for src in SCRIPT_SRC.findall(markup):
        name = src.split("/")[-1]
        for candidate in root.rglob(name):
            if candidate.is_file():
                raw = candidate.read_text(encoding="utf-8", errors="replace")
                out.append((f"script {candidate.name}", decode_js_escapes(raw)))
                break
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
        regions = (
            [("body", body_text(markup))]
            + head_fields(markup)
            + reader_attributes(markup)
            + script_text(root, markup)
        )
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
