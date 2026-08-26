# The BERIL atlas already has a schema. It is written in Python.

This is a note for BERIL colleagues. It does not require caring about LOKF.

The [atlas](https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/atlas) is
141 markdown pages across 16 types, and **all 141 carry the same 13 frontmatter keys**: `id`,
`title`, `type`, `status`, `summary`, `source_projects`, `source_docs`, `related_pages`,
`related_collections`, `confidence`, `generated_by`, `last_reviewed`, `order`. Type-specific
fields sit on top: `evidence` on 41 pages, `review_routes` on 20,
`opportunity_kind` / `readiness` / `impact` on 12.

That is a typed vocabulary with typed relations, provenance of the assertion itself
(`generated_by`), a confidence rating and a review date. It is a more developed knowledge model
than the six-concept bundle in this repository.

Its rules are enforced, as imperative Python. `ui/app/atlas_lint.py` holds
`REQUIRED_ATLAS_FIELDS`, `ATLAS_PAGE_TYPES`, `EVIDENCE_REQUIRED_TYPES`,
`DERIVED_PRODUCT_REQUIRED_FIELDS`, `CONFLICT_REQUIRED_FIELDS`, `OPPORTUNITY_REQUIRED_FIELDS`,
enums such as `{"unresolved", "partially_resolved", "resolved", "deprecated"}`, and referential
integrity checks against a collections snapshot. With `atlas_graph.py` (498 lines) and
`atlas_inventory.py` (323) that is 1,466 lines.

## So we tried translating a slice of it

Asserting "that could be a schema" is cheap. This is what happened when we wrote one.

[`examples/atlas-opportunity.linkml.yaml`](examples/atlas-opportunity.linkml.yaml) expresses the
`opportunity` type: the **11** fields in `REQUIRED_ATLAS_FIELDS`, the 10 in
`OPPORTUNITY_REQUIRED_FIELDS`, `evidence`, and all four `VALID_*` sets as enums. It parses as
LinkML: 3 classes, 26 slots, 4 enums.

Writing it forced two distinctions the prose above blurs. **Thirteen keys appear on every page;
eleven are required.** `related_pages` and `order` are universal by convention, not by rule. And
`evidence` is required for opportunity pages by a different mechanism than the others:
`opportunity` is in `EVIDENCE_REQUIRED_TYPES`, checked separately from the field set, so the
schema expresses it as `slot_usage` rather than a plain `required: true`. Neither distinction is
visible until something makes you write the rule down, which is the argument in miniature.

**The rules translated without resistance.** Every required-field set became `required: true`.
Every `VALID_*` set became an enum, one to one. Nothing in `atlas_lint.py`'s field and value
rules needed a workaround.

**One field is better typed than the linter can express.** All 24 `evidence` entries across the
12 opportunity pages are uniformly `{source, support}`. `atlas_lint` checks that `evidence` is
present; the committed schema declares an `Evidence` class with both slots required, so the
inner shape is typed too.

**And declaring a type found a real defect.** Validating the real pages against the schema
surfaced this in `atlas/opportunities/cf-formulation-reuse.md:37`:

```yaml
target_outputs:
  - Reuse decision: promote, revise, or deprecate the score product.
```

The unquoted colon makes YAML parse that item as a mapping, so `target_outputs` across the
corpus is 35 strings and one dict. `lint_atlas()` reports zero issues, correctly by its own
rules: it checks that the field is present, not what the items are. Reported at
https://github.com/kbaseincubator/BERIL-research-observatory/issues/405. Quoting the line fixes
it.

## The translation is easy but not semantics-preserving

This is the caveat worth knowing before anyone tries it, and it took validating real pages to
find.

`atlas_lint` reads "required" as **the key is present**. LinkML reads `required: true` on a
multivalued slot as **at least one item**. `cf-formulation-reuse.md` has:

```yaml
linked_conflicts: []
```

which `atlas_lint` accepts, correctly by its own rule, and which the generated JSON Schema
rejects:

```
[ERROR] 'linked_conflicts' is a required property in /
```

Isolated on a minimal document to be sure it is the empty list and not something else about the
page. Neither reading is wrong; they are different rules wearing the same word. A translation
that copies `REQUIRED_*` sets into `required: true` therefore **tightens** the rules without
anyone deciding to, and the atlas has at least one page that would newly fail.

Anyone doing this for real has to decide, per field, whether an empty list is acceptable. That
is a modelling conversation the current linter never had to have, and it is the actual cost of
the translation, more than the syntax.

## Where our test was wrong

The first pass also flagged `atlas/opportunities/index.md` as missing ten required fields. It is
`type: meta`, a section index. `atlas_lint` dispatches on `type` and correctly skips it; we had
validated every file in the directory. The linter is right and the test was wrong, and that is
worth saying as loudly as the finding.

## What this is not

**Not a proposal to adopt LOKF.** BERIL has four knowledge aggregations already, and one of them,
https://github.com/kbaseincubator/BERIL-research-observatory/pull/289, is an unmerged 372-file
pull request that **already carries LinkML schemas**. Schema-first is not a new idea there.

**Not a claim that the Python should be replaced.** Whether that is worth doing depends on
things this experiment cannot see: whether the compendium is meant to land, who maintains the
linter, and how often the rules change. The translation being easy is one input, not a
conclusion.

**The narrow claim only.** The rules in `atlas_lint.py` are a schema. Written declaratively,
the same file would also yield JSON Schema, SHACL, an OWL vocabulary, docs and typed bindings,
and would have caught a YAML colon slip that a presence check cannot see.
