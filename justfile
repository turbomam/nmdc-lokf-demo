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

# Validates the bundle, then diffs knowledge.ttl against a temp regeneration.
# `just ttl` is the command that actually rewrites it.
# What CI checks, read-only: never touches the working tree
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

# Is a pull request safe to merge? Exits nonzero if not. See CONTRIBUTING.md.
ready pr:
    #!/usr/bin/env bash
    set -euo pipefail
    # Resolve one path and run that one. Prefer PATH; fall back to ~/bin.
    if gate="$(command -v pr-ready.sh 2>/dev/null)"; then
      :
    elif [ -x "$HOME/bin/pr-ready.sh" ]; then
      gate="$HOME/bin/pr-ready.sh"
    else
      gate=""
    fi
    if [ -n "$gate" ]; then
      "$gate" turbomam/nmdc-lokf-demo {{pr}}
    else
      echo "pr-ready.sh not installed. The check by hand:" >&2
      echo "  gh api repos/turbomam/nmdc-lokf-demo/pulls/{{pr}} --jq .head.sha" >&2
      echo "  gh api repos/turbomam/nmdc-lokf-demo/pulls/{{pr}}/reviews --jq '.[]|select(.user.login|test(\"copilot\"))|.submitted_at'" >&2
      echo "  gh api repos/turbomam/nmdc-lokf-demo/pulls/{{pr}}/reviews --jq '.[]|select(.body|test(\"Suppressed\"))|.body'" >&2
      echo "The review must be NEWER than the head commit and report nothing." >&2
      exit 1
    fi
