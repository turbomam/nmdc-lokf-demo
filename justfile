# Every lokf invocation is pinned to 0.5.0, the version this repo's docs and
# committed outputs were produced with. Bump deliberately, then re-run `just ttl`
# and `just check`, rather than letting uvx drift to a new release silently.

# List recipes
default:
    @just --list

# Install the site's dependencies exactly as pinned by package-lock.json
setup:
    npm ci

# Update the lockfile deliberately (then commit it)
setup-update:
    npm install

# Live-preview the site (concept pages + the /graph browser)
dev:
    npm run dev

# Build the static site (output: dist/)
site:
    npm run build

# Interactive SPARQL endpoint + graph explorer over the bundle
serve:
    uvx --from 'lokf==0.5.0' lokf serve knowledge

# Project the bundle to RDF (Turtle) on stdout
rdf:
    uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl

# Project the bundle to linked tables (CSV under build/tables)
tables:
    uvx --from 'lokf[tables]==0.5.0' lokf tables knowledge --format csv --output build/tables

# Regenerate the committed RDF (CI fails if this leaves a diff)
ttl:
    uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl -o knowledge.ttl

# Check the built site for typography that should never reach a reader.
# Lints dist/, meaning exactly what ships, so code comments are out of scope and
# text inherited from the lokf new scaffold is caught the same as our own.
lint-site: site
    python3 scripts/lint-site-prose.py dist

# What CI's `bundle` job runs: the bundle validates and knowledge.ttl is
# current. Not the whole suite; `site-prose` runs `just lint-site` separately.
# Read-only: regenerates to a temp file so the working tree is never touched.
# Use `just ttl` when you actually want to rewrite knowledge.ttl.
check:
    #!/usr/bin/env bash
    set -euo pipefail
    uvx --from 'lokf[build]==0.5.0' lokf validate knowledge
    tmp="$(mktemp -t knowledge.XXXXXX.ttl)"
    trap 'rm -f "$tmp"' EXIT
    uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl -o "$tmp"
    if ! diff -u knowledge.ttl "$tmp"; then
      echo "knowledge.ttl is out of date. Regenerate with: just ttl" >&2
      exit 1
    fi
    echo "knowledge.ttl is current."
