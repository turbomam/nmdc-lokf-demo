# NMDC LOKF demo

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

`nmdc.ncbi_biosamples` is a harvested NCBI mirror re-hosted under the nmdc tenant.
`kbase.nmdc_neon` is NEON, a different program entirely. Only `nmdc.metadata` is
canonical NMDC.

The underlying findings come from the `nmdc_context_audit` project in BERIL, measured
2026-07-10. This bundle re-expresses six of them in LOKF; it does not re-measure them.

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
