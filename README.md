# NMDC LOKF demo

Published site: https://turbomam.github.io/nmdc-lokf-demo/ (concept pages, plus an interactive graph at https://turbomam.github.io/nmdc-lokf-demo/graph )

An exercise, not an NMDC product. Nothing here is authoritative about NMDC data.

This is a small [LOKF](https://lokf.nolan-nichols.com/) bundle built to answer one
question: what does it actually take to describe a set of data resources as linked
data, when the only thing you start with is prose?

## The question the bundle answers

Four databases in the BERDL lakehouse carry an "NMDC" name. They have four different
producers. The name does not tell you which is which, and that has repeatedly cost
people time. The bundle records the difference as typed relations, so a query answers
it instead of a person:

```
$ lokf query knowledge "$(cat queries/not-nmdc-produced.rq)"

name                  tag                 derivedFrom
nmdc.metadata         canonical           None
kbase.nmdc_arkin      derived             .../datasets/nmdc-metadata
nmdc.ncbi_biosamples  harvested           None
kbase.nmdc_neon       namesake-collision  None
```

`nmdc.ncbi_biosamples` holds records copied from NCBI, stored under the nmdc tenant.
`kbase.nmdc_neon` holds NSF NEON observations. Of the four, only `nmdc.metadata` is
produced by NMDC.

## Source and license

The findings are not mine. They come from the `nmdc_context_audit` project in the
BERIL Research Observatory, measured 2026-07-10:
https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/projects/nmdc_context_audit/knowledge

That repository is public and licensed AGPL-3.0, and this bundle is a derivative of
those documents, so it carries the same license. See `LICENSE`. This bundle
re-expresses six of the findings in LOKF; it does not re-measure them, and it is not
authoritative about NMDC data. For anything that matters, read the source.

## What LOKF is doing here

Each file in `knowledge/` is ordinary markdown with YAML frontmatter. Attaching the
LinkML-generated JSON-LD context makes the same file valid JSON-LD, so it expands to
RDF with no separate file:

```
<.../datasets/kbase-nmdc-arkin> a schema:Dataset ;
    prov:wasDerivedFrom <.../datasets/nmdc-metadata> ;
    dcterms:requires <.../glossary/berdl-tenant> ;
    schema:about <.../explanations/nmdc-label-is-overloaded> ;
    schema:name "kbase.nmdc_arkin" .
```

`derivedFrom` became `prov:wasDerivedFrom`, `dependsOn` became `dcterms:requires`.
The whole format is defined in one LinkML schema, and the JSON-LD context, JSON Schema,
SHACL shapes, OWL ontology and SQL DDL are generated from it.

## Reproduce

```bash
uvx --from 'lokf[build]' lokf validate knowledge     # -> OK, 6 concepts
uvx --from lokf lokf convert knowledge --format ttl -o knowledge.ttl
uvx --from lokf lokf query knowledge "$(cat queries/not-nmdc-produced.rq)"
```

The `[build]` extra on the first line is required: `lokf validate` alone fails in a
default install. Reported as https://github.com/nicholsn/lokf/issues/33

## Notes for anyone doing the same thing

The source documents did not use OKF frontmatter. They used `name` / `description` /
`metadata` / `related`, so converting them was a mapping exercise rather than a
relabelling. `metadata.provenance` had to be split: the producer became a `tag` plus a
`derivedFrom` link, and the tenant became a `dependsOn` link to a glossary term, because
tenant and producer are different things and conflating them is the original problem.

Built with LOKF 0.5.0.
