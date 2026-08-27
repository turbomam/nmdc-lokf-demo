---
type: Explanation
id: https://turbomam.github.io/nmdc-lokf-demo/explanations/who-built-what-on-nmdc-data
title: Who built what on NMDC data
genre: explanation
timestamp: 2026-08-26T00:00:00Z
description: Several groups across DOE BER and partners have built on NMDC data. Recording who contributed what keeps that ecosystem legible.
status: draft
tags: [attribution, reuse, berdl, modelling]
---
# Reuse is the point
NMDC publishes data so that other people can build on it, and several groups have. In the
BERDL lakehouse the Arkin Lab at LBNL has extended NMDC omics with vector embeddings,
organism trait assignments and a reconciled annotation layer. NEON observations are
processed through workflows of the kind NMDC uses. NCBI BioSample records are hosted
alongside NMDC records so the two can be queried together.

That is a working reuse ecosystem across DOE BER and partners, and it is what open data is
for. This bundle exists to record who contributed which piece of it.

# Attribution needs somewhere to live
Contribution is a fact about a resource, and it has to be written down somewhere to be
usable. A database name is not that place, and was never meant to be: a name carries where
a resource is hosted, which is a different and also useful fact.

Both facts matter, and neither is derivable from the other. The Arkin Lab's derived
products are hosted under the `kbase` tenant, which is a deliberate arrangement: keeping
NMDC-derived work in `kbase` leaves the `nmdc` tenant a clean surface the NMDC team
curates. Hosting and contribution are two axes, and a single string cannot carry both
without losing one.

So the contributions go in the graph, as `prov:wasDerivedFrom` edges and producer
attributions, where they can be queried, cited and corrected. That is all this bundle does.
