# NMDC LOKF demo

[Published site](https://turbomam.github.io/nmdc-lokf-demo/): concept pages, plus an
[interactive graph](https://turbomam.github.io/nmdc-lokf-demo/graph).

An exercise, not an NMDC product. Nothing here is authoritative about NMDC data, and
anything operational should be checked against the live catalog rather than this page.

This is a small [LOKF](https://lokf.nolan-nichols.com/) bundle built to answer one
question: what does it actually take to describe a set of data resources as linked data,
when the only thing you start with is prose?

## Why this content

Two reasons, and neither is a claim that anything is wrong with the resources described.

**It is the kind of content that exercises the format.** LOKF's value over plain OKF is
that it binds fields to schema.org, DCAT and PROV-O. `derivedFrom` becomes
`prov:wasDerivedFrom`; `dependsOn` becomes `dcterms:requires`. Only content with real
relationships between things exercises that. A flat glossary would have produced isolated
nodes and no edges, which demonstrates nothing. Provenance is relationships by definition,
so it was the obvious test.

**The findings were already public.** They come from the `nmdc_context_audit` project in
the BERIL Research Observatory, measured by the people who ran the audit. This bundle
re-expresses six of them in a different format. It does not measure anything, and it does
not make new claims about anyone's data.

## What the bundle shows

A BERDL database name carries the host tenant. Who produced the records is a separate,
independent fact. Both are worth knowing and a single string cannot hold both, so the
producer goes in the graph:

```
$ lokf query knowledge "$(cat queries/producer-and-host.rq)"

name                  hostTenant  producer               derivedFrom
kbase.nmdc_arkin      kbase       produced-by-arkin-lab  .../datasets/nmdc-metadata
kbase.nmdc_neon       kbase       produced-by-neon       None
nmdc.metadata         nmdc        produced-by-nmdc       None
nmdc.ncbi_biosamples  nmdc        produced-by-ncbi       None
```

Read down the two middle columns. The `kbase` tenant hosts data from two different
producers, and the `nmdc` tenant hosts data produced by NCBI as well as by NMDC. The host
is recoverable from the name, so the query derives it with `STRBEFORE`. The producer is
not, so it comes off the graph.

The tenant boundaries are deliberate: NMDC-derived products sit in the `kbase` tenant so
the `nmdc` tenant stays a clean surface the NMDC team curates. That is what makes the
hosting axis meaningful. This bundle adds the production axis alongside it.

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
    schema:about <.../explanations/provenance-is-not-in-the-name> ;
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

## Reproduce

```bash
uvx --from 'lokf[build]' lokf validate knowledge     # -> OK, 6 concepts
uvx --from lokf lokf convert knowledge --format ttl -o knowledge.ttl
uvx --from lokf lokf query knowledge "$(cat queries/producer-and-host.rq)"
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
