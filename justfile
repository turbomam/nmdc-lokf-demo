# List recipes
default:
    @just --list

# Install the site's dependencies (once; commit package-lock.json)
setup:
    npm install

# Live-preview the site (concept pages + the /graph browser)
dev:
    npm run dev

# Build the static site (output: dist/)
site:
    npm run build

# Interactive SPARQL endpoint + graph explorer over the bundle
serve:
    uvx --from lokf lokf serve knowledge

# Project the bundle to RDF (Turtle) on stdout
rdf:
    uvx --from lokf lokf convert knowledge --format ttl

# Project the bundle to linked tables (CSV under build/tables)
tables:
    uvx --from 'lokf[tables]' lokf tables knowledge --format csv --output build/tables

# Regenerate the committed RDF (CI fails if this leaves a diff)
ttl:
    uvx --from lokf lokf convert knowledge --format ttl -o knowledge.ttl

# What CI checks: bundle validates and knowledge.ttl is current.
# Read-only: regenerates to a temp file so the working tree is never touched.
# Use `just ttl` when you actually want to rewrite knowledge.ttl.
check:
    #!/usr/bin/env bash
    set -euo pipefail
    uvx --from 'lokf[build]' lokf validate knowledge
    tmp="$(mktemp -t knowledge.XXXXXX.ttl)"
    trap 'rm -f "$tmp"' EXIT
    uvx --from lokf lokf convert knowledge --format ttl -o "$tmp"
    if ! diff -u knowledge.ttl "$tmp"; then
      echo "knowledge.ttl is out of date. Regenerate with: just ttl" >&2
      exit 1
    fi
    echo "knowledge.ttl is current."
