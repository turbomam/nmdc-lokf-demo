---
type: Explanation
id: https://w3id.org/turbomam/nmdc-lokf-demo/explanations/provenance-is-not-in-the-name
title: Provenance is not in the name
genre: explanation
timestamp: 2026-08-26T00:00:00Z
description: A database name carries one axis, where the data is hosted. Who produced the data is a second, independent axis, and no naming scheme carries both at once.
status: draft
tags: [provenance, berdl, modelling]
---
# The two axes
A BERDL database name gives you a tenant and a short label. The tenant says who hosts and
curates the database. It does not say who produced the records inside it, and it was never
meant to.

Those two facts vary independently. A tenant can host data it did not produce, and data a
group produced can be hosted by someone else. Two independent axes cannot both be encoded in
one string without losing information, so a reader who infers a producer from a name is
inferring something the name does not carry.

# Why this is the right shape for a graph
Hosting and production are separate properties of the same resource, which is exactly what a
graph represents well and a naming convention does not. `prov:wasDerivedFrom` states the
production lineage; the tenant stays where it belongs, in the name and the catalog.

The tenant boundaries here are deliberate. NMDC-derived products were placed in the `kbase`
tenant so that the `nmdc` tenant stays a clean, authoritative surface that the NMDC team
curates. That separation is what makes the hosting axis meaningful. This bundle adds the
production axis alongside it rather than in place of it.
