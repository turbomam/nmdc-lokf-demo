# What building this bundle taught us

Six things, each learned by getting it wrong first. They are written for someone about to do
the same thing, not as a record of what happened here.

Everything here was measured against LOKF 0.5.0, and against linkml 1.11.1 where a section names
it. The first four were measured on 2026-08-26, while building the bundle. The two about
dereferencing and about the context IRI were measured on 2026-08-27, against the deployed site,
and say so where the figures appear.

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

## Resolving is not the same as dereferencing to the graph

The lesson above is that subject IRIs must resolve. It stops short of the next question, which
is what a machine gets when it follows one. Measured against the live site on 2026-08-27:

```
$ curl -sL -H "Accept: text/turtle"         .../datasets/kbase-nmdc-arkin  -> 200 text/html
$ curl -sL -H "Accept: application/ld+json" .../datasets/kbase-nmdc-arkin  -> 200 text/html
$ curl -sL -H "Accept: application/rdf+xml" .../datasets/kbase-nmdc-arkin  -> 200 text/html
```

**GitHub Pages cannot do content negotiation.** Every `Accept` header gets HTML. That is a
hosting limit rather than anything about LOKF or LinkML, and it is worth separating the two,
because a reader evaluating the pattern may otherwise assume the demo is showing what the format
can do.

The HTML does carry machine-readable data, but less than the name suggests. Each page embeds a
`<script type="application/ld+json">` block, and on a concept page it contains exactly this:

```json
{"@context": "https://schema.org", "@type": "Dataset", "@id": "...", "name": "...", "description": "..."}
```

That is search-engine markup. **The typed relations are not in it.** `derivedFrom`, `dependsOn`,
`about` and the producer `tags`, which are the entire point of the bundle, appear only in the
whole-graph document at `/graph.jsonld`. So a consumer that dereferences a single concept IRI
gets a name and, if the concept has one, a description. A consumer that fetches the whole graph
gets the edges.

`description` really is conditional, and the glossary term shows why it is worth saying. Its
frontmatter carries `definition` rather than `description`, and the embed only emits
`description`, so that page dereferences to a bare name:

```json
{"@context": "https://schema.org", "@type": "GlossaryTerm", "@id": "...", "name": "BERDL tenant"}
```

The definition, which is the whole content of a glossary term, is not in the machine-readable
output at all.

Whether that matters depends on the consumer, and it is a reasonable thing for a static site to
do. It is not a reasonable thing to leave undocumented in a demo whose claim is that the markdown
*is* a queryable graph.

What is published, in full:

| Path | Status | Content type | Carries the relations |
|---|---|---|---|
| a concept IRI | 200 | `text/html` | no. schema.org `name`, plus `description` when the concept has one |
| `/graph.jsonld` | 200 | `application/ld+json` | yes, all 6 concepts and 9 edges |
| `/graph.json` | 200 | `application/json` | yes, as cytoscape elements |
| `/knowledge.ttl` | 404 | | not published, though it is committed |

When negotiation is unavailable, the usual way to advertise a machine-readable representation is
`<link rel="alternate">`. There was none on any page. There is now: every page carries

```html
<link rel="alternate" type="application/ld+json" href="/nmdc-lokf-demo/graph.jsonld" />
```

That points at the whole graph rather than at a per-concept document, because no per-concept RDF
file is published. It is an honest pointer to where the relations actually live, not a claim that
the concept itself has an alternate serialisation.

## Pin the context, not just the tools

The published graph declares its `@context` as a URL on a moving branch:

```
https://raw.githubusercontent.com/nicholsn/lokf/main/lokf.context.jsonld
```

Two consequences. The meaning of every term in this graph is defined by whatever that file
contains at the moment a consumer resolves it, so an upstream edit changes this graph's semantics
with no commit here. And `raw.githubusercontent.com` serves it as `text/plain`, from a host that
makes no availability promise for this use.

This is the scaffold default: `lokf new` writes that line into `knowledge/index.md`, and the
installed template carries it verbatim, so every LOKF bundle inherits it.

Worth noticing next to what this repository does elsewhere. Every `uvx` invocation here is
version-pinned, the 18 `lokf` ones to `0.5.0`, precisely so a new release cannot change behaviour
silently. The *semantics* of
the published graph were left pointing at a branch. Pinning the tools and not the vocabulary is a
gap that is easy to miss, because tooling drift breaks a build and vocabulary drift does not
break anything at all.

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
empty list. LinkML's **JSON loader** normalises empty collections and nulls to absent before validating, so
the ordinary presence check fires on a document the schema itself would pass. The YAML loader
does not, which means the same instance validates clean as YAML and fails as JSON. `lokf
validate` gets the JSON behaviour because it writes a temporary `.bundle.json`.

The exposure is narrower than "two tools disagree" and more useful to know: any slot that is
`multivalued`, `required`, and legitimately empty behaves differently depending on which
artifact a consumer validates against and which format it is loaded from. See [atlas-as-linkml.md](atlas-as-linkml.md) for the
reduced case and the measurements.
