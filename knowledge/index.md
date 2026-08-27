---
lokf_version: "0.1"
okf_version: "0.1"
base_iri: https://turbomam.github.io/nmdc-lokf-demo/
context: https://raw.githubusercontent.com/nicholsn/lokf/main/lokf.context.jsonld
title: NMDC LOKF Demo
description: Six concepts recording who contributed which NMDC-derived resource, described as linked data to test what LOKF adds over prose.
license: https://www.gnu.org/licenses/agpl-3.0.html
---

# NMDC LOKF Demo

An exercise, not an NMDC product. Findings measured 2026-07-10 by the
`nmdc_context_audit` project in the BERIL Research Observatory and re-expressed here in
LOKF. Derived copies drift, so check the live catalog for anything operational.

Source and license:
https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/projects/nmdc_context_audit/knowledge

## The idea

* [Who built what on NMDC data](explanations/who-built-what-on-nmdc-data.md) - several
  groups across DOE BER and partners have built on NMDC data; recording who contributed
  what keeps that ecosystem legible.

## Glossary

* [BERDL tenant](glossary/berdl-tenant.md) - the top-level namespace of a database in the
  lakehouse catalog.

## Datasets

* [nmdc.metadata](datasets/nmdc-metadata.md) - produced by NMDC, and the source the derived
  work builds on.
* [kbase.nmdc_arkin](datasets/kbase-nmdc-arkin.md) - the Arkin Lab at LBNL added embeddings,
  traits and reconciled annotations to NMDC omics.
* [nmdc.ncbi_biosamples](datasets/nmdc-ncbi-biosamples.md) - NCBI records, hosted alongside
  NMDC's own.
* [kbase.nmdc_neon](datasets/kbase-nmdc-neon.md) - NSF NEON observations, processed with
  NMDC-style workflows.
