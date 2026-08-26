# NMDC LOKF demo

Published site: https://turbomam.github.io/nmdc-lokf-demo/ (concept pages, plus an
interactive graph at https://turbomam.github.io/nmdc-lokf-demo/graph )

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

name                  producer               derivedFrom
kbase.nmdc_arkin      produced-by-arkin-lab  .../datasets/nmdc-metadata
kbase.nmdc_neon       produced-by-neon       None
nmdc.metadata         produced-by-nmdc       None
nmdc.ncbi_biosamples  produced-by-ncbi       None
```

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

The source documents did not use OKF frontmatter. They used `name` / `description` /
`metadata` / `related`, so converting them was a mapping exercise rather than a
relabelling. `metadata.provenance` had to be split: the producer became a tag plus a
`derivedFrom` link, and the tenant became a `dependsOn` link to a glossary term, because
tenant and producer are different things and one field cannot carry both.

Built with LOKF 0.5.0.
