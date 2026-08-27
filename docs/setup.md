# Build, run and publish this

Everything here was run on macOS 15 with the versions listed. Nothing is theoretical.

## Prerequisites

| Tool | Version used | Needed for |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | 0.12.5 | The bundle recipes, and the Python that `just lint-site` runs on. `uvx` runs the `lokf` toolkit without installing it. Not needed for `setup`, `dev` or `site`, which call only npm |
| [just](https://github.com/casey/just) | 1.58.0 | The task recipes. Optional; most are a single command, and `just check` is a short bash script |
| Node | 24.15.0 | The website only. Not needed to work with the bundle |
| Python | 3.13 | Provided by `uv`; no separate install needed |

You do **not** need to install `lokf` or `linkml`. Every recipe fetches them through `uvx`,
pinned to `lokf==0.5.0`, which is the version this repository's documentation and committed
outputs were produced with. Bump it deliberately in the `justfile`, then re-run `just ttl` and
`just check`, rather than letting `uvx` drift to a new release silently.

## The stack

Two halves that do not depend on each other. The bundle is Python; the website is Node. You can
work on either without installing the other.

| Layer | What | Required? |
|---|---|---|
| Format | Markdown with YAML frontmatter. Not JSON-LD itself: `lokf convert` reads the frontmatter and emits JSON-LD using the generated context, and from there RDF | Yes. This is LOKF |
| Schema | [LinkML](https://linkml.io/), one schema (`lokf.yaml`) that generates the JSON-LD context, JSON Schema, SHACL, OWL and SQL DDL | Yes, but you never invoke it. The wheel ships `lokf.yaml`, the JSON-LD context and the Python bindings; the JSON Schema, SHACL, OWL and SQL stay upstream, and `lokf validate` reaches the JSON Schema by running `linkml-validate` against the packaged `lokf.yaml`. See [what-linkml-does.md](what-linkml-does.md) |
| Toolkit | `lokf` 0.5.0 (Python): `convert`, `validate`, `query`, `serve`, `tables`, `propose`, `vocab` | Yes |
| Graph | RDF via pyoxigraph; `lokf serve` gives a SPARQL endpoint and a graph explorer from stdlib `http.server` | Yes, for the query recipes |
| Website | Astro, TypeScript, Node, two remark plugins | **No.** Scaffold output. Deleting it costs only the published site |
| Tasks | `just` recipes wrapping the above | No. Every recipe is a command you can run yourself |

`lokf` declares no Node dependency. The website exists because `lokf new` scaffolds one and
GitHub Pages is a convenient place to resolve concept IRIs.

For the counts behind this table, and what the scaffold ships that this repository does not,
see [landscape.md](landscape.md).

## Work with the bundle

```bash
git clone https://github.com/turbomam/nmdc-lokf-demo && cd nmdc-lokf-demo
just --list          # every recipe, with a one-line description each
```

| Recipe | What it does |
|---|---|
| `just check` | What CI's `bundle` job runs. Validates the bundle and confirms `knowledge.ttl` matches the concepts. **Read-only**; never touches the working tree |
| `just lint-site` | What CI's `site-prose` job runs. Builds the site, then fails on em and en dashes in rendered body text, page titles and meta descriptions |
| `just lint-dist` | The same check without rebuilding. What the pages workflow runs before uploading the artifact |
| `just ttl` | Regenerates `knowledge.ttl`. The one command that rewrites it |
| `just rdf` | Prints the bundle as Turtle to stdout |
| `just serve` | A local SPARQL endpoint and graph explorer, no Node required |
| `just tables` | Projects the bundle to CSV, one file per concept type plus an edge table |

By hand, without `just`:

```bash
# just check   (validate, then confirm knowledge.ttl matches the concepts; read-only)
(
  set -euo pipefail
  uvx --from 'lokf[build]==0.5.0' lokf validate knowledge
  tmp=$(mktemp -t knowledge.XXXXXX.ttl)
  trap 'rm -f "$tmp"' EXIT
  uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl -o "$tmp"
  diff -u knowledge.ttl "$tmp" || { echo "knowledge.ttl is out of date. Regenerate with: just ttl" >&2; exit 1; }
  echo "knowledge.ttl is current."
)

# just ttl     (regenerate the committed Turtle in place)
uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl -o knowledge.ttl

# just rdf     (project to Turtle on stdout; does not write a file)
uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl

# just tables  (CSV projection of concepts and relations, under build/tables)
uvx --from 'lokf[tables]==0.5.0' lokf tables knowledge --format csv --output build/tables

# just serve   (SPARQL endpoint and graph explorer on localhost)
uvx --from 'lokf==0.5.0' lokf serve knowledge

# not a recipe, but the thing you probably want next
uvx --from 'lokf==0.5.0' lokf query knowledge "$(cat queries/producer-and-host.rq)"
```

The `check` block runs inside `( ... )` and uses `trap` rather than a trailing `rm`, both on
purpose. A trailing `rm` becomes the exit status of the whole sequence, so stale Turtle would exit
0 and pass in automation. The subshell keeps the `trap` and the `set -e` out of the shell you are
typing in, which is what the `just` recipe gets for free by being a script.

`just tables` writes to `build/tables`, which is untracked scratch space. The CSVs committed under
`docs/examples/` are documentation fixtures; copy them there deliberately when you mean to update
them, rather than pointing the recipe at that directory.

The website recipes (`setup`, `dev`, `site`) are plain npm; see
[Run the website locally](#run-the-website-locally) below.

The `[build]` extra on the first line is required. `lokf validate` fails without it in a
default install, reported upstream as https://github.com/nicholsn/lokf/issues/33

## Run the website locally

```bash
just setup     # npm ci, installs exactly what package-lock.json pins
just dev       # live preview at the URL it prints
just site      # static build into dist/
```

`just setup-update` runs `npm install` instead, for the deliberate case where the lockfile
should move. Updating dependencies is then an explicit act rather than a side effect of setup.

## Publish your own copy to GitHub Pages

The workflow is in the repository, but **Pages must be switched on by hand**. A fork gets the
workflow file and no site until you do this:

1. **Enable Actions.** A new fork has workflows disabled until you turn them on: open the
   **Actions** tab and confirm the prompt. Without this, nothing below runs, and the failure
   is silent rather than an error.
2. Settings, then Pages, then set **Source** to **GitHub Actions**. There is no `gh-pages`
   branch and none is needed.
3. Push to `main`. `.github/workflows/pages.yml` builds the Astro site and deploys it.
4. If no build appears, dispatch it from the **Actions** tab: select **pages**, then **Run
   workflow** on `main`. With the `gh` CLI, `gh workflow run pages.yml --ref main` does the
   same thing; the CLI is not a prerequisite.

Current configuration of this repository, for comparison:

```
build_type: workflow
url:        https://turbomam.github.io/nmdc-lokf-demo/
```

The API also reports a `source` of `branch main, path /`. That field is vestigial when
`build_type` is `workflow`; the deploy comes from the workflow, not from a branch, and there
is no branch to configure.

**Set your own base IRI before publishing.** Concepts here are named at
`https://turbomam.github.io/nmdc-lokf-demo/` so that every subject IRI resolves to its own
page. A fork that keeps those names will publish a graph whose subjects point at this
repository.

Listing the fields to edit is not enough, because the base appears inside concept bodies too:
`dependsOn`, `about` and `derivedFrom` all carry absolute IRIs under the old base, and
`astro.config.mjs` sets `base` **twice**, once for Astro and once for the `remarkLokfLinks`
plugin. As of this commit the string occurs 17 times across 8 files. Replace it everywhere
rather than field by field:

```bash
OLD=https://turbomam.github.io/nmdc-lokf-demo
NEW="https://YOURNAME.github.io/YOURREPO"   # quote it: bare <> are shell redirections
grep -rl "$OLD" knowledge/ src/ | xargs sed -i '' "s|$OLD|$NEW|g"   # macOS; drop the '' on GNU sed
sed -i '' "s|https://turbomam.github.io|https://YOURNAME.github.io|" astro.config.mjs  # site
sed -i '' "s|/nmdc-lokf-demo|/YOURREPO|g" astro.config.mjs                            # both base values
grep -rn "turbomam.github.io" knowledge/ src/ astro.config.mjs       # expect no output
just ttl        # concept IRIs changed, so the committed Turtle is now stale
just check      # only meaningful after the regeneration above
```

That sequence was run end to end against a copy of this repository before being documented:
15 triples move to the new base, 0 remain on the old one, and `just check` passes. Grep for
`turbomam.github.io` rather than `turbomam`, or you will get one hit from a comment in
`astro.config.mjs` about an unregistered `w3id.org/turbomam` prefix, which is history and not a
live IRI.

Three parts of that are easy to get wrong. `astro.config.mjs` sets `site` (the origin) separately
from `base` (the path), and `base` appears **twice**, once for Astro and once for the
`remarkLokfLinks` plugin, so a single substitution leaves canonical URLs pointing at the original
owner. And `just ttl` has to run **before** `just check`, not after: changing the concept IRIs
makes `knowledge.ttl` stale by definition, so `check` fails until it is regenerated.

The final `grep` is the part worth keeping: a fork that misses even one occurrence publishes a
graph whose subjects point at this repository, and nothing fails to build, so there is no error
to notice.

**Scaffolding fresh with `lokf new --base-iri <url>` avoids all of this** and is the easier
path; see [lessons.md](lessons.md). Fork only if you want this bundle's content.

**One operational note.** During the GitHub Actions incident on 2026-08-26, push-triggered
workflow runs were silently dropped: merges to `main` did not fire `pages.yml` and it had to
be dispatched by hand. If a deploy seems to be missing, check
[githubstatus.com](https://www.githubstatus.com/) before debugging the workflow.

## What CI checks

`.github/workflows/check.yml` runs on pushes to `main`, on every pull request, and on manual
dispatch. A push to a feature branch with no open pull request does not trigger it. Two jobs:

`bundle` validates the bundle against the LOKF schema, then regenerates `knowledge.ttl` to a
temporary file and fails if the result differs from the committed one. It also greps tracked
markdown for em and en dashes, which is a `git grep` rather than a linter: the site check needs a
script because it has to decide which parts of built HTML a reader sees, and a character in a
markdown file needs no such judgement. A stale `knowledge.ttl`
fails the build rather than sitting unnoticed. It runs `just check`, so the version pins live in
one place instead of being repeated here.

`site-prose` builds the site and runs `scripts/lint-site-prose.py` over `dist/`, failing on em
and en dashes in three regions: rendered body text, the page `<title>`, and the meta description.
Those are where all three shipped instances were. The report names the region, which is what tells
you where to fix a finding.

Attributes, inline scripts, client bundles and text assembled at runtime are **not** scanned. An
earlier version covered the first three, caught nothing real here across ten review rounds, and
introduced false positives on valid markup, so the scope was reduced to what has actually gone
wrong. https://github.com/turbomam/nmdc-lokf-demo/issues/56 lists every exclusion and what would
justify adding coverage back. It exists because an em
dash shipped in the footer of all 8 pages and nothing in this repository looked at published
text: Vale checks issue and pull request bodies, and the bundle checks say nothing about prose.
Linting `dist/` rather than the sources means code comments are out of scope for free, and text
inherited from the `lokf new` scaffold is caught the same as our own. The job invokes
`just lint-site`, so the recipe is the single definition and running it locally checks exactly
what CI checks.

`.github/workflows/pages.yml` builds and deploys the site on pushes to `main`, and runs the same
prose check between the build and the artifact upload. That is deliberate duplication: `check.yml`
runs on pull requests and `pages.yml` deploys on pushes, independently of each other, so a failing
check in one would not have stopped a deploy from the other. Both call `just lint-dist`, so there
is one definition of the check and two callers.
