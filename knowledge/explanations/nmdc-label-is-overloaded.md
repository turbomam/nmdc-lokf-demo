---
type: Explanation
id: https://w3id.org/turbomam/nmdc-lokf-demo/explanations/nmdc-label-is-overloaded
title: The NMDC label is overloaded
genre: explanation
timestamp: 2026-08-26T00:00:00Z
description: Databases whose names contain nmdc sit in three different tenants and were produced by six different groups, so matching on the name tells you nothing about who made the data.
status: draft
tags: [nmdc, berdl, provenance]
---
# Why this matters
Searching a lakehouse catalog for "nmdc" returns databases produced by NMDC, databases
harvested from elsewhere and re-hosted under the NMDC tenant, and databases about an
entirely different program that share the prefix. Choosing by name alone is unreliable.

Source: the `nmdc_context_audit` project in BERIL, measured 2026-07-10.
