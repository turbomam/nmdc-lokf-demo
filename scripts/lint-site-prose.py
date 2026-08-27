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

Parsing goes through `html.parser`, not regular expressions. Four separate bugs
in this file came from matching markup with patterns: a body scan that reached
into the head and double-counted the title, a meta matcher that assumed
attribute order, a value group that could not distinguish quote styles, and a
tag matcher that stopped at the first `>` even inside a quoted value, so
`title="A > B"` with a banned character before the `>` reported clean. A parser
does not have those failure modes and they were not going to stop arriving.

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

# Attributes a reader or a screen reader is shown. Tag stripping throws these
# away, so a banned character in a placeholder or an aria-label used to pass.
READER_ATTRS = (
    "placeholder",
    "title",
    "alt",
    "aria-label",
    "aria-description",
    "aria-placeholder",
)

# `<script>` types whose contents are not scanned as code. Kept deliberately
# narrow: excluding a type that client code reads and renders would let a
# reader-visible character through, which is the expensive direction.
DATA_SCRIPT_TYPES = {
    # Duplicated on this site: the JSON-LD block holds the concept's name and
    # description, both already scanned as body text and as the meta
    # description, so scanning it reports the same character two or three times.
    # This exclusion is specific to that arrangement and would need revisiting
    # on a site whose JSON-LD carried prose appearing nowhere else.
    "application/ld+json",
    # URLs and configuration. Cannot carry prose a reader will see.
    "importmap",
    "speculationrules",
}
# Deliberately NOT excluded: application/json, text/template and
# text/x-template. Client code routinely reads those and inserts the result into
# the page, and nothing guarantees that text appears in another scanned region,
# so skipping them would let a reader-visible dash through.

JS_ESCAPE = re.compile(
    r"(\\*)\\(?:u\{([0-9a-fA-F]{1,6})\}|u([0-9a-fA-F]{4})|x([0-9a-fA-F]{2}))"
)


class PageReader(HTMLParser):
    """Collect the regions of a built page that a reader can meet."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body: list[str] = []
        self.title = ""
        self.meta_descriptions: list[str] = []
        self.attributes: list[tuple[str, str]] = []
        self.inline_scripts: list[str] = []
        self.script_srcs: list[str] = []
        self._depth_body = 0
        self._in_title = False
        self._skip = 0
        self._script_is_code = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "body":
            self._depth_body += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("name", "").lower() == "description":
            self.meta_descriptions.append(a.get("content", ""))
        elif tag == "script":
            if src := a.get("src"):
                self.script_srcs.append(src)
                self._script_is_code = False
            else:
                self._script_is_code = a.get("type", "").lower() not in DATA_SCRIPT_TYPES
            self._skip += 1
        elif tag == "style":
            self._skip += 1
        for name in READER_ATTRS:
            if value := a.get(name):
                self.attributes.append((f"@{name}", value))

    def handle_endtag(self, tag: str) -> None:
        if tag == "body":
            self._depth_body = max(0, self._depth_body - 1)
        elif tag == "title":
            self._in_title = False
        elif tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
            self._script_is_code = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif self._skip:
            if self._script_is_code:
                self.inline_scripts.append(data)
        elif self._depth_body:
            self.body.append(data)


def decode_js_escapes(text: str) -> str:
    r"""Turn active \uXXXX and \xXX escapes into the characters they denote.

    This build emits non-ASCII literally, measured end to end: an em dash placed
    in a src/ string arrives in the bundle as the character, not as an escape.
    Other bundlers, and this one under a different target or minifier setting,
    emit ASCII-only output. Decoding first means the check does not quietly stop
    working if that changes, which is the failure mode worth guarding: it would
    report clean rather than error.

    Only escapes preceded by an even number of backslashes are active. Where the
    backslash is itself escaped, the text is literal and stays literal.

    Widths are exact, and getting that wrong is silent. An unbraced ``\u`` takes
    exactly four hex digits, so JavaScript reads ``"—and"`` as an em dash
    followed by ``and``. A pattern allowing up to six consumed ``2014a`` as one
    code point, produced a different character, and missed the dash entirely.
    Braced ``\u{...}`` takes one to six; ``\x`` takes exactly two.
    """

    def sub(m: "re.Match[str]") -> str:
        prefix = m.group(1)
        if len(prefix) % 2:
            return m.group(0)
        digits = m.group(2) or m.group(3) or m.group(4)
        return prefix + chr(int(digits, 16))

    return JS_ESCAPE.sub(sub, text)


def bundle_text(root: pathlib.Path, srcs: list[str]) -> list[tuple[str, str]]:
    """Raw text of the client bundles a page references.

    Astro emits client scripts as separate files under `_astro/`, so text a
    script renders never appears in the HTML and no amount of tag stripping will
    find it.

    These are scanned as raw text rather than by extracting string literals.
    Pairing quotes with a regex is not reliable on minified output: scanning left
    to right, one unbalanced quote earlier in the file shifts every pair after it
    and a real string silently stops being visible. That was happening here, and
    it produced a linter that reported clean on a bundle with a banned character
    in it. Minified output carries no comments, so a banned character in one of
    these files is in a string, and searching the text directly has no pairing
    problem to get wrong.
    """
    out = []
    for src in srcs:
        # A query string or fragment is part of the URL, not of the filename.
        # Leaving it on turns app.js?v=1 into a name nothing matches, and the
        # bundle is then skipped without a word.
        name = src.split("#")[0].split("?")[0].split("/")[-1]
        if not name:
            continue
        for candidate in root.rglob(name):
            if candidate.is_file():
                raw = candidate.read_text(encoding="utf-8", errors="replace")
                out.append((f"script {candidate.name}", decode_js_escapes(raw)))
                break
    return out


def regions(root: pathlib.Path, markup: str) -> list[tuple[str, str]]:
    reader = PageReader()
    reader.feed(markup)
    reader.close()
    out: list[tuple[str, str]] = [("body", " ".join(reader.body))]
    if reader.title.strip():
        out.append(("<title>", reader.title))
    out += [("meta description", d) for d in reader.meta_descriptions]
    # Values arrive already resolved: convert_charrefs=True handles attributes too.
    # Unescaping again turns a deliberately literal title="Write &amp;mdash;", which
    # a reader sees as &mdash;, into an actual em dash and fails on it.
    out += list(reader.attributes)
    out += [("inline script", decode_js_escapes(s)) for s in reader.inline_scripts]
    out += bundle_text(root, reader.script_srcs)
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
        for where, text in regions(root, markup):
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
