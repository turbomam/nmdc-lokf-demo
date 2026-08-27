---
type: Explanation
id: https://turbomam.github.io/nmdc-lokf-demo/explanations/who-built-what-on-nmdc-data
title: Who built what on NMDC data
genre: explanation
timestamp: 2026-08-26T00:00:00Z
description: "Work across DOE BER and partners sits alongside NMDC data in several different ways: derived from it, processed like it, hosted with it. Recording which is which keeps that ecosystem legible."
status: draft
tags: [attribution, reuse, berdl, modelling]
---
# Reuse is the point
NMDC publishes data so that other people can build on it. In the BERDL lakehouse the Arkin
Lab at LBNL has done exactly that, extending NMDC omics with vector embeddings, organism
trait assignments and a reconciled annotation layer.

Two other things sit nearby without being that. NEON observations are not NMDC data; they
are processed through workflows of the kind NMDC uses. NCBI BioSample records are not NMDC
data either; they are hosted alongside NMDC records so the two can be queried together.

Three different relationships, then: derived from, processed like, hosted with. All three are
what a shared lakehouse is for, and all three are worth having. But they are not the same
relationship, and a single phrase like "built on NMDC data" covers all three while
distinguishing none of them. This bundle exists to record which is which.

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
