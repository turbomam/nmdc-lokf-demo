# Build, run and publish this

Everything here was run on macOS 15 with the versions listed. Nothing is theoretical.

## Prerequisites

| Tool | Version used | Needed for |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | 0.12.5 | Everything. `uvx` runs the `lokf` toolkit without installing it |
| [just](https://github.com/casey/just) | 1.58.0 | The task recipes. Optional; every recipe is a one-line command |
| Node | 24.15.0 | The website only. Not needed to work with the bundle |
| Python | 3.13 | Provided by `uv`; no separate install needed |

You do **not** need to install `lokf` or `linkml`. Every recipe fetches them through `uvx`,
pinned to the version the documentation was written against.

## Work with the bundle

```bash
git clone https://github.com/turbomam/nmdc-lokf-demo && cd nmdc-lokf-demo
just --list          # every recipe, with a one-line description each
```

| Recipe | What it does |
|---|---|
| `just check` | What CI runs. Validates the bundle and confirms `knowledge.ttl` matches the concepts. **Read-only**; never touches the working tree |
| `just ttl` | Regenerates `knowledge.ttl`. The one command that rewrites it |
| `just rdf` | Prints the bundle as Turtle to stdout |
| `just serve` | A local SPARQL endpoint and graph explorer, no Node required |
| `just tables` | Projects the bundle to CSV, one file per concept type plus an edge table |

By hand, without `just`:

```bash
uvx --from 'lokf[build]==0.5.0' lokf validate knowledge
uvx --from 'lokf==0.5.0'        lokf convert knowledge --format ttl -o knowledge.ttl
uvx --from 'lokf==0.5.0'        lokf query   knowledge "$(cat queries/producer-and-host.rq)"
```

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

1. Settings, then Pages, then set **Source** to **GitHub Actions**. There is no `gh-pages`
   branch and none is needed.
2. Push to `main`. `.github/workflows/pages.yml` builds the Astro site and deploys it.
3. If no build appears, dispatch it: `gh workflow run pages.yml --ref main`.

Current configuration of this repository, for comparison:

```
build_type: workflow
source:     branch main, path /
url:        https://turbomam.github.io/nmdc-lokf-demo/
```

**Set your own base IRI before publishing.** Concepts here are named at
`https://turbomam.github.io/nmdc-lokf-demo/` so that every subject IRI resolves to its own
page. A fork that keeps those names will publish a graph whose subjects point at this
repository. Change `base_iri` in `knowledge/index.md`, `site` and `base` in
`astro.config.mjs`, `BASE_IRI` in `src/lib/lokf.ts`, and the `id` on each concept. Scaffolding
fresh with `lokf new --base-iri <url>` sets all of these at once, which is the easier path;
see [lessons.md](lessons.md).

**One operational note.** During the GitHub Actions incident on 2026-08-26, push-triggered
workflow runs were silently dropped: merges to `main` did not fire `pages.yml` and it had to
be dispatched by hand. If a deploy seems to be missing, check
[githubstatus.com](https://www.githubstatus.com/) before debugging the workflow.

## What CI checks

`.github/workflows/check.yml` runs on every push and pull request. It validates the bundle
against the LOKF schema, then regenerates `knowledge.ttl` to a temporary file and fails if the
result differs from the committed one. A stale `knowledge.ttl` fails the build rather than
sitting unnoticed.

`.github/workflows/pages.yml` builds and deploys the site on pushes to `main`.
