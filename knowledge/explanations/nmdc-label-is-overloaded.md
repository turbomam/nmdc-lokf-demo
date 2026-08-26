---
type: Explanation
id: https://w3id.org/turbomam/nmdc-lokf-demo/explanations/nmdc-label-is-overloaded
title: The NMDC label is overloaded
genre: explanation
timestamp: 2026-08-26T00:00:00Z
description: One "NMDC" label spans three BERDL tenants and six provenance classes, so the name alone does not tell you who produced the data.
status: draft
tags: [nmdc, berdl, provenance]
---
# Why this matters
Searching a lakehouse catalog for "nmdc" returns databases produced by NMDC, databases
harvested from elsewhere and re-hosted under the NMDC tenant, and databases about an
entirely different program that share the prefix. Choosing by name alone is unreliable.

Source: the `nmdc_context_audit` project in BERIL, measured 2026-07-10.
