# What LinkML actually does here

The rest of this repo shows markdown turning into RDF. That is LOKF's headline, but it is not
the part that is about LinkML. This page is.

Every figure below was counted or run on 2026-08-26 against LOKF 0.5.0. Nothing is estimated.

## One schema, six artifacts

`lokf.yaml` is the only hand-edited definition of the format: **1,624 lines, 29 classes, 76
slots, 5 enums, 3 subsets**. Everything else is generated from it by stock LinkML generators.

**None of these files are in this repository.** They live in the upstream LOKF project,
https://github.com/nicholsn/lokf, and ship inside the installed `lokf` package. This bundle
consumes the generated JSON-LD context rather than regenerating it. The counts below were taken
from that repository at version 0.5.0; to check them, clone it and count.

| Generated artifact | Lines | Made by | What it buys |
|---|---:|---|---|
| `lokf.context.jsonld` | 442 | `gen-jsonld-context` | Makes the frontmatter valid JSON-LD, so markdown expands to RDF with no separate file |
| `lokf.schema.json` | 5,502 | `gen-json-schema` | Validates frontmatter, closed-world, which is what rejects the mistake below |
| `lokf.shacl.ttl` | 3,271 | `gen-shacl` | Validates the RDF graph rather than the source documents |
| `lokf.owl.ttl` | 1,994 | `gen-owl` | Reasoning and alignment against schema.org, DCAT and PROV-O |
| `lokf.sql` | 3,425 | SQL DDL generator | One table per type, foreign keys for typed relations |
| `src/lokf/datamodel.py` | 2,014 | `gen-python` | Typed Python bindings, `from lokf.datamodel import Dataset` |

**1,624 lines in, 16,648 lines out.** None of the 16,648 has to be written, reviewed, or kept in
sync by hand. That is the whole argument, and it is why the format can be changed in one place.

## The schema is enforced, not decorative

While authoring this bundle I invented a key. `seeAlso` looks like it should exist; it is not a
slot on `Concept`. The generated JSON Schema refused it:

```
[ERROR] [<temp bundle>/0] {'type': 'Dataset', 'id': '.../datasets/broken-example',
 'title': 'Broken example', 'seeAlso': ['https://example.org/not-a-slot'], 'body': '# Body'}
 is not valid under any of the given schemas in /concepts/0
```

Committed at [`examples/validation-error.txt`](examples/validation-error.txt), with one path
elided: `lokf validate` assembles the bundle into a temp file, so the bracketed location differs
on every run and every machine. Everything after it is the schema's own message. Reproduce by
adding that key to any concept and running:

```bash
uvx --from 'lokf[build]' lokf validate knowledge
```

This is a real error caught by a schema rather than by review, which is worth more than the
assertion that a schema exists.

## The same bundle is a graph and a set of tables

`lokf convert` projects the bundle to RDF. `lokf tables` projects **the same concepts** to
relational form, one CSV per type plus an edge table:

```bash
uvx --from 'lokf[tables]' lokf tables knowledge --format csv --output build/tables
# -> Dataset.csv  Explanation.csv  GlossaryTerm.csv  relations.csv
```

[`examples/relations.csv`](examples/relations.csv), committed here, is the edge table:

```
source,predicate,target
.../datasets/kbase-nmdc-arkin,derivedFrom,.../datasets/nmdc-metadata
.../datasets/kbase-nmdc-arkin,dependsOn,.../glossary/berdl-tenant
```

Both projections come from the same 76 slot definitions. Nothing declares the tables separately,
and nothing can drift between the two, because there is only one source.

## What this would mean for a schema you already maintain

The pattern generalises past LOKF. If a body of documentation already has structure in its
frontmatter, a LinkML schema for that frontmatter gives validation, a JSON-LD context, SHACL,
OWL and a relational projection without writing any of them.

`docs/landscape.md` works through a concrete case: the BERIL Research Observatory's atlas has
141 pages sharing 13 frontmatter keys across 16 types, and its structure is enforced by 1,466
lines of hand-written Python. That is the same job the 1,624-line schema above does
declaratively, minus the five other artifacts.

## What is not shown, and not claimed

Nothing here measures whether any of this improves retrieval, curation speed, or correctness.
This page shows what the conversion costs and what falls out of it, not what it buys.
