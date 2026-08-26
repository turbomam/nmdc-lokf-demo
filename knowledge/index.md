---
lokf_version: "0.1"
okf_version: "0.1"
base_iri: https://w3id.org/turbomam/nmdc-lokf-demo/
context: https://raw.githubusercontent.com/nicholsn/lokf/main/lokf.context.jsonld
title: NMDC LOKF Demo
description: Six data resources described as linked data, to test what LOKF adds over prose.
license: https://www.gnu.org/licenses/agpl-3.0.html
---

# NMDC LOKF Demo

An exercise, not an NMDC product. Findings measured 2026-07-10 by the
`nmdc_context_audit` project in the BERIL Research Observatory and re-expressed here in
LOKF. Derived copies drift, so check the live catalog for anything operational.

Source and license:
https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/projects/nmdc_context_audit/knowledge

## The idea

* [Provenance is not in the name](explanations/provenance-is-not-in-the-name.md) - a
  database name carries the host tenant; who produced the records is a second, independent
  axis.

## Glossary

* [BERDL tenant](glossary/berdl-tenant.md) - the top-level namespace of a database in the
  lakehouse catalog.

## Datasets

* [nmdc.metadata](datasets/nmdc-metadata.md) - produced by NMDC.
* [kbase.nmdc_arkin](datasets/kbase-nmdc-arkin.md) - produced by the Arkin Lab at LBNL,
  derived from NMDC omics.
* [nmdc.ncbi_biosamples](datasets/nmdc-ncbi-biosamples.md) - produced by NCBI.
* [kbase.nmdc_neon](datasets/kbase-nmdc-neon.md) - produced by the NSF NEON program.
