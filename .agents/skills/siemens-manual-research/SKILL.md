---
name: siemens-manual-research
description: Research Siemens STEP 7 or SINUMERIK manuals and reconcile their interface definitions with a project. Use for version-specific documentation, grounded source lookup and optional NotebookLM research without uploading project evidence.
---

# Siemens manual research

Identify the product family, software/basic-program version and exact question
before choosing sources. Use the version-matched primary Siemens manual. A
training handout or another controller generation can help locate a topic but
should not settle an address, alarm reaction, or machine-data definition.

If the user names an existing NotebookLM notebook, use a configured NotebookLM
connector or supported CLI. Check authentication with a read-only operation,
then identify the intended notebook and select only the relevant source
documents. Use an existing provider-specific skill if available. A notebook's
title does not establish its edition or controller coverage. If the
connection has expired or the needed source is missing, continue with
accessible official manuals and say what could not be checked.

For exact values and tables, open the original source passage, check section,
edition and page, and cross-check any generated answer against it. Cite the
source passage near the claim. For project-specific behavior, trace the
actual block call, settings, writers/readers, interface or matching archive.
Describe discrepancies instead of silently applying a manual default.

Do not copy account details, notebook identifiers or private project examples
into shared skill files. A request to consult an existing notebook does not
authorize creating sources, adding a notebook, or sending confidential data.
For any separately authorized ingestion, select only cleared material and
keep private source mapping and revision information local. NotebookLM does
not decode PLC archives or verify what is running on a machine.
