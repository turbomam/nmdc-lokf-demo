# NMDC LOKF demo

[Published site](https://turbomam.github.io/nmdc-lokf-demo/): concept pages, plus an
[interactive graph](https://turbomam.github.io/nmdc-lokf-demo/graph).

An exercise, not an NMDC product. Nothing here is authoritative about NMDC data, and
anything operational should be checked against the live catalog rather than this page.

This is a small [LOKF](https://lokf.nolan-nichols.com/) bundle built to answer one
question: what does it actually take to describe a set of data resources as linked data,
when the only thing you start with is prose?

## Why this content

**Because people are building on NMDC data, and that is worth recording.** In the BERDL
lakehouse the Arkin Lab at LBNL has extended NMDC omics with vector embeddings, organism
trait assignments and a reconciled annotation layer. NEON observations run through
workflows of the kind NMDC uses. NCBI BioSample records sit alongside NMDC's own so the two
can be queried together. That is a working reuse ecosystem across DOE BER and partners, and
it is what publishing open data is for.

An ecosystem like that stays legible only if contribution is written down somewhere it can
be queried, cited and corrected. This bundle does that for four datasets, alongside a glossary
term and an explanation that give them context.

**It also happens to exercise the format.** LOKF's value over plain OKF is that it binds
fields to schema.org, DCAT and PROV-O: `derivedFrom` becomes `prov:wasDerivedFrom`,
`dependsOn` becomes `dcterms:requires`. Attribution is relationships by definition, so it
was the obvious content to test with. A flat glossary would have produced isolated nodes
and no edges.

**The findings were already public.** They come from the `nmdc_context_audit` project in
the BERIL Research Observatory, measured by the people who ran the audit. This bundle
re-expresses six of them in a different format. It does not measure anything, and it does
not make new claims about anyone's data.

## What the bundle shows

Who contributed each resource, and what it was built from:

```
$ lokf query knowledge "$(cat queries/producer-and-host.rq)"

name                  hostTenant  producer               derivedFrom
kbase.nmdc_arkin      kbase       produced-by-arkin-lab  .../datasets/nmdc-metadata
kbase.nmdc_neon       kbase       produced-by-neon       None
nmdc.metadata         nmdc        produced-by-nmdc       None
nmdc.ncbi_biosamples  nmdc        produced-by-ncbi       None
```

Four groups contributed these four resources, and one of them builds directly on another:
`kbase.nmdc_arkin` carries a `prov:wasDerivedFrom` edge to `nmdc.metadata`.

The two middle columns are separate facts. Hosting is recoverable from the name, so the
query derives it with `STRBEFORE`; the tenant boundaries are a deliberate arrangement that
keeps NMDC-derived work in `kbase` and leaves the `nmdc` tenant a clean surface the NMDC
team curates. Contribution is not recoverable from a name and was never meant to be, so it
comes off the graph. Both are worth having, which is why they are two columns.

## Currency

The findings were measured **2026-07-10**. Derived copies drift from their sources; as one
example, on 2026-07-31 `kbase.nmdc_neon.study_sample` held 5,917 samples where the NEON soil
study had 6,489. Treat everything here as a dated snapshot used to test a format, not as a
current description of the lakehouse.

## What LOKF is doing here

Each file in `knowledge/` is ordinary markdown with YAML frontmatter. Attaching the
LinkML-generated JSON-LD context makes the same file valid JSON-LD, so it expands to RDF
with no separate file:

```
<.../datasets/kbase-nmdc-arkin> a schema:Dataset ;
    prov:wasDerivedFrom <.../datasets/nmdc-metadata> ;
    dcterms:requires <.../glossary/berdl-tenant> ;
    schema:about <.../explanations/who-built-what-on-nmdc-data> ;
    schema:name "kbase.nmdc_arkin" .
```

The whole format is defined in one LinkML schema, and the JSON-LD context, JSON Schema,
SHACL shapes, OWL ontology and SQL DDL are generated from it.

## What LinkML actually does here

[docs/what-linkml-does.md](docs/what-linkml-does.md): 1,624 lines of LinkML schema yield 16,648
lines of JSON-LD context, JSON Schema, SHACL, OWL, SQL DDL and Python bindings, with a note on
which three are post-processed afterwards and which two of them ship in the installed package;
the generated schema rejecting a real authoring mistake; and where LinkML stops and LOKF's own
code starts.

## What exercising it turned up

Building against a real LinkML-defined format surfaced something neither the format nor the data
shows on its own: **`linkml-validate` gives different verdicts for the same data depending on the
serialisation it is loaded from.**

```
$ linkml-validate -s s.yaml -C T <file>          # linkml 1.11.1

  empty.yaml   tags: []          No issues found
  empty.json   {"tags": []}      [ERROR] 'tags' is a required property in /
  null.yaml    tags: null        [ERROR] None is not of type 'array' in /tags
  null.json    {"tags": null}    [ERROR] 'tags' is a required property in /
```

Same schema, same required multivalued slot, same version. As YAML the empty list is accepted;
as JSON it is reported missing. LinkML's JSON loader runs `json_clean`, which strips empty
collections and nulls, while the YAML loader passes `yaml.safe_load_all` output through
unchanged. The presence check then fires on a document that no longer contains the key.

`lokf validate` inherits the JSON behaviour, because it writes a temporary `.bundle.json` and
validates that. So a bundle author meets this without ever writing JSON. Any slot that is
`multivalued`, `required` and legitimately empty is exposed.

The four files reproduce it: [docs/examples/loader-normalization/](docs/examples/loader-normalization/).
Fuller treatment, including what it means for translating an existing validator to a schema, in
[docs/lessons.md](docs/lessons.md) and [docs/atlas-as-linkml.md](docs/atlas-as-linkml.md).

Not reported upstream by this work. Seven searches of the `linkml/linkml` tracker returned no
matching issue, which is not proof there is none.

## For BERIL colleagues

[docs/atlas-as-linkml.md](docs/atlas-as-linkml.md): a slice of the atlas's 1,466 lines of Python
validation, one type of sixteen, expressed as a LinkML schema. What translated cleanly, one real
defect it found, and the tooling inconsistency that makes the translation a modelling decision
rather than a port.

## What this taught us

[docs/lessons.md](docs/lessons.md): four things learned by getting them wrong first, written for
someone about to build their own bundle. Dead subject IRIs that nothing checks, the silent
half-migration when `--base-iri` is skipped, projection not enforcing what validation enforces,
and why the frontmatter mapping is the real work.

## What it's built on, and what else exists

[docs/landscape.md](docs/landscape.md) covers the stack (Python required, Astro optional) and how this compares
to the four knowledge aggregations already in the BERIL Research Observatory.

## Build, run and publish

[docs/setup.md](docs/setup.md): prerequisites and versions, every `just` recipe, running the
site locally, **switching GitHub Pages on** (a fork gets the workflow but no site until you
do), and what CI checks.

[docs/what-changed.md](docs/what-changed.md): how this differs from a fresh `lokf new`, who
maintains which part, and the four related repositories with what each owns.

## Reproduce

```bash
uvx --from 'lokf[build]==0.5.0' lokf validate knowledge     # -> OK, 6 concepts
uvx --from 'lokf==0.5.0' lokf convert knowledge --format ttl -o knowledge.ttl
uvx --from 'lokf==0.5.0' lokf query knowledge "$(cat queries/producer-and-host.rq)"
```

The `[build]` extra on the first line is required: `lokf validate` alone fails in a default
install. Reported as https://github.com/nicholsn/lokf/issues/33

## Source and license

The findings are not mine. They come from the `nmdc_context_audit` project in the BERIL
Research Observatory, measured 2026-07-10:
https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/projects/nmdc_context_audit/knowledge

That repository is public and licensed AGPL-3.0, and this bundle is a derivative of those
documents, so it carries the same license. See `LICENSE`. For anything that matters, read
the source.

## Notes for anyone doing the same thing

Moved to [docs/lessons.md](docs/lessons.md), which covers the frontmatter mapping this
section used to summarise, plus three other things worth knowing before starting.

Built with LOKF 0.5.0.
