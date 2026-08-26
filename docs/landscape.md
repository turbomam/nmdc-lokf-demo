# What this is built on, and how it relates to what BERIL already has

Two questions this repo would otherwise leave a reader guessing about: what do I have to
install, and does this duplicate something that already exists?

All figures below were read from the installed `lokf` 0.5.0 package, this repo's tracked
files, and the public BERIL Research Observatory repository on 2026-08-26. Nothing here is
estimated.

## Do I have to learn Astro?

No. The website is optional scaffolding.

**Required.** The format is markdown with YAML frontmatter plus a LinkML-generated JSON-LD
context. The toolkit is Python: `lokf convert`, `validate`, `query`, `serve`, `tables`,
`propose`, `vocab`. `lokf serve` gives you a SPARQL endpoint and an interactive graph explorer
from stdlib `http.server`, pyoxigraph, and one bundled `cytoscape.min.js`. No Node involved.

**Optional.** Astro (4 `.astro` files), TypeScript (4 `.ts`), three `.mjs` ES modules
including two remark plugins, `package.json`, `tsconfig.json`, a `justfile`, and a GitHub
Pages workflow. In the `lokf` package these exist only under `src/lokf/templates/kb/`, which
is scaffold output, and the Python package declares no Node dependency at all. Deleting every
one of them from this repo would cost only the published website.

So the LOKF value chain is markdown, to JSON-LD, to RDF, in Python. `lokf new` adds a web
front end on top because GitHub Pages is convenient.

### One thing the scaffold ships that this repo does not

`lokf new` also writes six Claude agent skills into `.claude/skills/`: `author-concept`,
`build-knowledge-base`, `enrich-relations`, `publish-graph`, `query-knowledge-base`, and
`scaffold-knowledge-base`, 616 lines in total.

They were removed here. They are byte-identical copies of the skills inside the `lokf`
package, and they reference `examples/acme-knowledge` thirteen times across three files. That
is upstream's example bundle and it does not exist in this repo, so an agent following them
here would run commands against a missing directory.

Their content is otherwise unobjectionable: no destructive commands, no credential handling,
no network calls beyond the `lokf` CLI itself, and the only mutating operation is
`lokf propose --apply`, which rewrites frontmatter in the bundle after a review step.

Run `lokf skills install` to get them, or read them in the `lokf` package under
`src/lokf/skills/`.

## How this relates to BERIL's knowledge aggregations

BERIL has four. This demo is smaller than three of them and overlaps none of them cleanly.

| | What it is | Scale | Where its structure lives |
|---|---|---|---|
| **OpenViking** | Retrieval. Embeds and searches text. | `knowledge/openviking/`, `observatory_context/openviking_client.py` | Not applicable; it indexes content |
| **The atlas** | Curated research knowledge base | **141 pages, 16 types** | **Python** (`ui/app/atlas_lint.py`, 645 lines) |
| **The compendium** | Statement-card KG synthesis wiki | **48,865 lines, 372 files** | **LinkML**, and **not released** |
| **Project `knowledge/` bundles** | Per-project context documents | 15 files in `nmdc_context_audit` | Nowhere |

### The atlas

Every one of its 141 pages carries the same 13 frontmatter keys: `id`, `title`, `type`,
`status`, `summary`, `source_projects`, `source_docs`, `related_pages`,
`related_collections`, `confidence`, `generated_by`, `last_reviewed`, `order`. Type-specific
fields sit on top of that (`evidence` on 41 pages, `review_routes` on 20,
`opportunity_kind` / `readiness` / `impact` on 12).

Sixteen types: `data_collection` (48), `meta`, `opportunity`, `data_type`, `topic`,
`hypothesis`, `derived_product`, `claim`, `method`, `direction`, `conflict`, `data_tenant`,
`person`, `data_gap`, `join_recipe`, `atlas`.

That is a typed concept vocabulary with typed relations, provenance of the assertion itself,
a confidence rating, and a review date. It is a more developed knowledge model than this demo
and than LOKF's own example bundle.

Its structure is enforced, but as imperative Python. `ui/app/atlas_lint.py` holds
`REQUIRED_ATLAS_FIELDS`, `ATLAS_PAGE_TYPES`, `EVIDENCE_REQUIRED_TYPES`,
`DERIVED_PRODUCT_REQUIRED_FIELDS`, `CONFLICT_REQUIRED_FIELDS`,
`OPPORTUNITY_REQUIRED_FIELDS`, status enums such as
`{"unresolved", "partially_resolved", "resolved", "deprecated"}`, and referential integrity
checks against a collections snapshot. With `atlas_graph.py` (498 lines) and
`atlas_inventory.py` (323) that is 1,466 lines expressing what a schema language declares.

### The compendium

https://github.com/kbaseincubator/BERIL-research-observatory/pull/289
("feat(compendium): statement-card KG synthesis wiki") is open, 48,865 added lines across 372
files, last updated 2026-06-23. `compendium/` is not on `main`. It already carries LinkML
schemas at `compendium/schema/compendium.yaml` and `synthesis_wiki.yaml`.

This matters for honesty about novelty: **BERIL already took the LinkML route for its
knowledge layer.** Anyone presenting a schema-first approach there is not introducing the idea.

## What this demo does claim, and what it does not

**It does not claim that BERIL should adopt LOKF.** BERIL has four knowledge structures
already and one is a large unmerged pull request. A fifth format is not help.

**It does claim something narrower.** The atlas has a genuine schema that currently exists
only as Python. A format like LOKF shows what a declarative schema yields instead: from one
LinkML file you get a JSON-LD context, JSON Schema, SHACL shapes, an OWL ontology, SQL DDL,
and Python bindings, none of which have to be written or kept in sync by hand.

**The one thing LOKF does that the alternatives here do not** is make a directory of markdown
files simultaneously human-readable and valid JSON-LD, with no separate RDF artifact to
maintain. The atlas is structured but not linked data. The compendium is linked data but is
not merged. OpenViking retrieves but does not model.

**Unmeasured.** Nothing here shows that any of this improves retrieval, curation speed, or
correctness. This demo shows what the conversion costs, not what it buys.
