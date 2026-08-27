# What building this bundle taught us

Four things, each learned by getting it wrong first. They are written for someone about to do
the same thing, not as a record of what happened here.

Every claim below was measured on 2026-08-26 against LOKF 0.5.0.

## Name concepts where they resolve, or register the prefix first

This bundle originally minted every subject IRI under
`https://w3id.org/turbomam/nmdc-lokf-demo/`. Nobody had registered `turbomam` in
`perma-id/w3id.org`, so every subject 404'd:

```
https://w3id.org/turbomam/nmdc-lokf-demo/datasets/nmdc-metadata  -> 404
```

Six published subjects, all dead, while the site rendered perfectly and the RDF parsed. **A
graph does not complain about subjects that do not dereference.** Nothing in the toolchain
checks it, and no amount of validation would have.

The fix was to name concepts at the origin already serving them, so each subject resolves to
its own page. If a permanent identifier is wanted, register the prefix **first** and move the
IRIs afterwards, not the other way round.

Checking this takes one loop:

```bash
grep -oE '^<https://[^>]+>' knowledge.ttl | tr -d '<>' | sort -u | while read u; do
  echo "$(curl -sS -o /dev/null -w '%{http_code}' -L "$u") $u"
done
```

## Pass `--base-iri` to `lokf new`

It sets all four places that hold the base: `knowledge/index.md`, `astro.config.mjs`,
`BASE_IRI` in `src/lib/lokf.ts`, and the starter concept's cross-reference. Verified by
scaffolding with the flag and grepping for the placeholder: no matches.

Doing it by hand afterwards is where this goes wrong, because the failure is **silent**.
Concepts carrying an explicit absolute `id` never reach the `BASE_IRI` fallback, so the graph
looks correct until someone adds a concept without one. This repo published a page whose
canonical URL said `example.org` while its concept IRIs said something else, and a reviewer
caught it rather than any check. Reported upstream at
https://github.com/nicholsn/lokf/issues/36.

## Validation and projection are separate, and only one of them enforces the schema

`lokf validate` rejects an undeclared key. `lokf tables` puts it in a CSV column anyway:

```
$ # add `totally_invented_key: hello` to a concept
$ lokf tables <bundle> --format csv && head -1 GlossaryTerm.csv
type,id,title,definition,timestamp,status,totally_invented_key,body

$ lokf validate <bundle>
[ERROR] ... is not valid under any of the given schemas
```

`to_frames` consults the schema at one point, to decide which keys are edges. Everything else
becomes a column as-is. So a pipeline that projects without validating carries whatever the
author typed, and neither step tells you the other did not run.

## The mapping is the work, not the syntax

Converting an existing frontmatter convention to LOKF is not a relabelling. The source
documents here used `name` / `description` / `metadata` / `related`, and the conversion was
mostly deciding what the fields **meant**.

`metadata.provenance` was one string doing two jobs. It had to split into a producer tag and a
`derivedFrom` edge. `metadata.tenant` became a `dependsOn` edge to a glossary term. Tenant and
producer are different axes, and one field cannot carry both without losing information, which
was the whole finding the source documents existed to record.

That splitting is the cost, and it is where the value is. The syntax took minutes; deciding
that hosting and production are two axes took reading the source material properly.

A corollary seen elsewhere: **check what a rule actually does before copying it.** Porting a
presence check to `required: true` on a multivalued slot silently tightens the rules, because
`linkml-validate` rejects an empty list. Not because the two words mean different things: the
LinkML metamodel defines `required` as presence too, and the generated JSON Schema accepts the
empty list. `linkml-validate` normalises an empty collection, and a null, to absent before
validating, so the ordinary presence check fires on a document the schema itself would pass.

The exposure is narrower than "two tools disagree" and more useful to know: any slot that is
`multivalued`, `required`, and legitimately empty behaves differently depending on which
artifact a consumer validates against. See [atlas-as-linkml.md](atlas-as-linkml.md) for the
reduced case and the measurements.
