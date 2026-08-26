# What LinkML actually does here

The rest of this repo shows markdown turning into RDF. That is LOKF's headline, but it is not
the part that is about LinkML. This page is.

Every figure below was counted or run on 2026-08-26 against LOKF 0.5.0. Nothing is estimated.

## One schema, six artifacts

`lokf.yaml` is the only hand-edited definition of the format: **1,624 lines, 29 classes, 76
slots, 5 enums, 3 subsets**. Six artifacts are derived from it.

**None of these files are in this repository.** They live in the upstream LOKF project,
https://github.com/nicholsn/lokf. The counts below were taken from that repository at the
`v0.5.0` tag. To check them, check that tag out rather than the default branch, which has moved
on:

```bash
git clone https://github.com/nicholsn/lokf && cd lokf && git checkout v0.5.0
wc -l lokf.yaml lokf.context.jsonld lokf.schema.json lokf.shacl.ttl \
      lokf.owl.ttl lokf.sql src/lokf/datamodel.py
```

| Derived artifact | Lines | Generator | Post-processed by `build.py`? | In the installed wheel? |
|---|---:|---|---|---|
| `lokf.context.jsonld` | 442 | `gen-jsonld-context` | **Yes, substantially** | Yes |
| `lokf.schema.json` | 5,502 | `gen-json-schema` | No | No, repo only |
| `lokf.shacl.ttl` | 3,271 | `gen-shacl` | No | No, repo only |
| `lokf.owl.ttl` | 1,994 | `gen-owl` | Yes, axioms appended | No, repo only |
| `lokf.sql` | 3,425 | `gen-sqltables` | No | No, repo only |
| `src/lokf/datamodel.py` | 2,014 | `gen-python` | Yes, one keyword fix | Yes |

**1,624 lines in, 16,648 lines out.** None of the 16,648 has to be written by hand, and that is
the argument. But two qualifications matter, and both are visible in `src/lokf/build.py`.

### The generators are not the whole story

Three of the six are post-processed after generation:

- **The JSON-LD context is rewritten**, and this is load-bearing. `build.py` adds the
  `type` → `@type` and `id` → `@id` keyword aliases, maps nine `ParameterType` values to their
  classes, and removes `@id` coercion from `author` so OKF actor strings stay literals. The
  first of those is what makes unmodified OKF frontmatter valid JSON-LD at all, which is LOKF's
  headline feature. A stock `gen-jsonld-context` run does not produce it.
- **OWL axioms are appended**, declaring the Parameter-kind classes and aligning
  `lokf:Verification` with `prov:Activity`, because LinkML materialises enum meanings as IRIs
  without emitting class axioms for them.
- **The Python bindings are patched** so a slot named `from` becomes `from_`; `gen-python`
  emits it verbatim, which is a `SyntaxError`.

So the honest claim is that LinkML does the bulk and the remainder is small, deliberate, and
documented in the build script. Adopting a LinkML schema alone would not reproduce these exact
files.

### Only two of the six derived artifacts ship in the package

`build.py` copies `lokf.yaml` and `lokf.context.jsonld` into `src/lokf/data`, and generates
`src/lokf/datamodel.py`. So three files ship, but one of them is `lokf.yaml`, the hand-edited
source rather than a derived artifact: of the six derived files, only the context and the
Python bindings are in the wheel. The JSON Schema, SHACL shapes, OWL ontology and SQL DDL stay
in the upstream repository. `lokf validate` reaches the JSON Schema by calling `linkml-validate`
against the packaged `lokf.yaml`, not by shipping the generated schema.

## The schema is enforced, not decorative

While authoring this bundle I invented a key. `seeAlso` looks like it should exist; it is not a
slot on `Concept`. The generated JSON Schema refused it:

```
[ERROR] [<temp bundle>/0] {'type': 'Dataset',
 'id': 'https://turbomam.github.io/nmdc-lokf-demo/datasets/broken-example',
 'title': 'Broken example', 'seeAlso': ['https://example.org/not-a-slot'], 'body': '# Body'}
 is not valid under any of the given schemas in /concepts/0
```

Committed at [`examples/validation-error.txt`](examples/validation-error.txt), with one path
elided: `lokf validate` assembles the bundle into a temp file, so the bracketed location differs
on every run and every machine. Everything after it is the schema's own message. Reproduce by
adding that key to any concept and running:

```bash
uvx --from 'lokf[build]==0.5.0' lokf validate knowledge
```

This is a real error caught by a schema rather than by review, which is worth more than the
assertion that a schema exists.

## The same bundle is a graph and a set of tables

`lokf convert` projects the bundle to RDF. `lokf tables` projects **the same concepts** to
relational form, one CSV per type plus an edge table:

```bash
uvx --from 'lokf[tables]==0.5.0' lokf tables knowledge --format csv --output build/tables
# -> Dataset.csv  Explanation.csv  GlossaryTerm.csv  relations.csv
```

[`examples/relations.csv`](examples/relations.csv), committed here, is the edge table:

```
source,predicate,target
.../datasets/kbase-nmdc-arkin,derivedFrom,.../datasets/nmdc-metadata
.../datasets/kbase-nmdc-arkin,dependsOn,.../glossary/berdl-tenant
```

Neither projection requires a separate table declaration, and that is the benefit. Two things
it is not.

**The columns are not schema-derived.** `to_frames` in `src/lokf/tables.py` consults the schema
at exactly one point, `vocabulary().relation_slots`, to decide which keys are edges. Every other
key in the document becomes a column as-is. An undeclared key therefore lands in the CSV:

```
$ # add `totally_invented_key: hello` to a concept, then
$ lokf tables <bundle> --format csv
$ head -1 GlossaryTerm.csv
type,id,title,definition,timestamp,status,totally_invented_key,body

$ lokf validate <bundle>
[ERROR] ... is not valid under any of the given schemas
```

The schema catches it; the table projection does not. Validation is a separate step, not a
property of the projection.

**They can drift.** RDF conversion reads the **committed** JSON-LD context while `lokf tables`
reads relation slots from the schema, so a schema change without a rebuilt context makes the two
disagree.

Note also what generates what. LinkML's `gen-sqltables` produces the relational **schema**
(`lokf.sql`). Projecting the **instances** to CSV or Parquet is LOKF's own code,
`src/lokf/tables.py`, 200 lines with no LinkML dependency. Adopting a LinkML schema gives you
the DDL, not `lokf tables`.

## What this would mean for a schema you already maintain

The pattern generalises past LOKF. If a body of documentation already has structure in its
frontmatter, a LinkML schema for that frontmatter gives validation, a JSON-LD context, SHACL
shapes, an OWL ontology and relational DDL without writing any of them. It does not give you
LOKF's CLI: the markdown parsing, the instance-to-table projection and the SPARQL server are
LOKF's own code.

`docs/landscape.md` works through a concrete case: the BERIL Research Observatory's atlas has
141 pages sharing 13 frontmatter keys across 16 types, and its structure is enforced by 1,466
lines of hand-written Python. That is the same job the 1,624-line schema above does
declaratively, minus the five other artifacts.

## What is not shown, and not claimed

Nothing here measures whether any of this improves retrieval, curation speed, or correctness.
This page shows what the conversion costs and what falls out of it, not what it buys.
