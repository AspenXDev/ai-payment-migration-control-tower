# AI-Assisted Payment Migration Control Tower

> **Portfolio project:** a synthetic APAC corporate-treasury migration programme demonstrating banking workflow knowledge, PMO control, data engineering, AI augmentation, Japanese stakeholder communication, and AI governance.

## Overview

A fictional regional bank is migrating **200 synthetic corporate customers** across Singapore, Japan, and other APAC markets from legacy payment-initiation arrangements toward ISO 20022-aligned target states.

The project models the operational control problem around that migration:

- Which clients are ready?
- Which milestones are overdue?
- Which dependencies are unowned?
- Where is risk concentrated?
- What evidence supports a reported status?
- What changed since the previous reporting period?
- Which matters require a human decision?
- How should migration communications be drafted for Japanese stakeholders?
- What may AI assist with, and what must remain under human approval?

The project is intentionally a **migration control tower**, not a payment-processing platform.

## Why this project exists

Migration programmes often combine fragmented operational data, technical message evidence, correspondence, testing results, dependencies, risk judgements, and management reporting.

This project demonstrates a reusable approach to turning that information into an evidence-aware control system.

The portfolio proposition is:

> **Banking workflow + PMO control + AI augmentation + data + Japanese communication + governance**

## Important disclaimer

This repository is a **personal portfolio project built entirely with synthetic data**.

It does **not** contain:

- employer or client data;
- proprietary bank documents;
- production payment instructions;
- internal schemas, procedures, screenshots, or correspondence;
- credentials, endpoints, network information, or production connectivity;
- claims of full SWIFT, ISO 20022, regulatory, sanctions, AML, or scheme compliance.

Public standards are used only to make the fictional scenario technically plausible. The implementation is educational and demonstrative, not a production banking system.

## Scenario

The fictional programme covers 200 corporate customers across APAC. Each migration case can include:

- migration wave;
- jurisdiction;
- treasury product / payment-service profile;
- documentation status;
- testing status;
- dependencies;
- risk rating;
- treasury owner;
- IT owner;
- target date;
- banking relationships and branches;
- account names;
- transaction currencies;
- creditor countries;
- payment purposes such as payroll and vendor payments;
- latest correspondence;
- escalation status;
- original state / target state;
- evidence supporting reported readiness.

Synthetic payment artefacts include a limited selection of:

- legacy MT101 examples;
- legacy `pain.001.001.03` XML examples;
- current-state `pain.001.001.09` examples for a FINplus payment-initiation-relay scenario;
- selected status / acknowledgement evidence;
- selected downstream ISO 20022 MX examples where useful to explain the migration flow.

`pain.001.001.03` is deliberately treated as a **legacy source format** rather than a current CBPR+ target. ISO 20022 lists Payments Initiation V03 in its archive, while current Swift CBPR+ materials identify `pain.001.001.09` for CustomerCreditTransferInitiation.

## Target outputs

### 1. Migration dashboard

Power BI Desktop provides an operational and executive view of:

- overall completion;
- evidence-backed completion;
- overdue items;
- risk concentration;
- progress by country and migration wave;
- documentation and testing status;
- dependency ageing;
- unowned dependencies;
- escalated cases;
- data-quality exceptions.

A key distinction is:

> **reported readiness vs evidence-confirmed readiness**

### 2. Weekly executive brief

A generated reporting pack summarises:

- changes since the previous reporting date;
- decisions required;
- top risks;
- recoveries;
- overdue commitments;
- next milestones;
- exceptions requiring management attention.

The underlying facts are prepared deterministically from structured data. Any LLM-assisted narrative must remain traceable to the evidence package.

### 3. Evidence-aware issue report

Each material issue can record:

| Field | Purpose |
|---|---|
| Claim | What the issue asserts |
| Evidence for | Sources supporting the claim |
| Evidence against | Sources weakening or contradicting it |
| Contradiction | Inconsistency between sources |
| Confidence | Bounded assessment based on available evidence |
| Missing evidence | Information still required |
| Recommended action | Proposed next step |
| Human decision | Decision that cannot be delegated to AI |

This is intended to distinguish **fact, evidence, inference, recommendation, and decision authority**.

### 4. Japanese stakeholder samples

The repository will include synthetic bilingual examples such as:

- migration notice;
- clarification request;
- escalation wording;
- explanation of translation decisions and operational ambiguity.

The objective is not literal translation. It is to demonstrate how language choices affect accountability, clarity, urgency, and technical meaning.

### 5. Governance documentation

The project will document:

- permitted AI assistance;
- human approval gates;
- data-classification rules;
- hallucination / unsupported-claim checks;
- evidence provenance;
- audit trail;
- failure scenarios;
- confidentiality boundaries.

## Architecture

```text
Synthetic source artefacts
        |
        +-- Client / account reference data
        +-- MT101 samples
        +-- pain.001 XML samples
        +-- Status / acknowledgement evidence
        +-- Testing results
        +-- Dependencies / risks
        +-- Synthetic correspondence
        |
        v
Python ingestion + deterministic validation
        |
        v
Canonical migration data model
        |
        +-------------------> Power BI
        |                       |
        |                       +-- Control Tower
        |                       +-- Operations
        |                       +-- Risk & Dependencies
        |                       +-- Evidence / Data Quality
        |
        +-------------------> Evidence packages
                                |
                                +-- Weekly executive brief
                                +-- Evidence-aware issue report
                                +-- Draft stakeholder communication
                                +-- Human review / approval
```

## Technology

- **Python**
- **pandas**
- **pytest**
- **XML / XSD-aware parsing**
- **Power BI Desktop**
- **Git / GitHub**
- **GitHub Pages**
- **ChatGPT / Codex** for development assistance, review, drafting, and code generation

The MVP does **not** require an autonomous LLM service or production API integration.

## Generate the canonical synthetic dataset

The implementation uses only the Python standard library at runtime. The
default command writes 16 normalized CSV tables for 200 fictional cases,
selected educational XML artefacts, and a clearly separated test-only anomaly
manifest:

```bash
python -m src.generate_data --seed 20260829 --clients 200
```

Run the verification suite with:

```bash
python -m pip install -r requirements.txt
pytest
```

The canonical grains and relationships are documented in
[`docs/data_dictionary.md`](docs/data_dictionary.md). Controlled anomaly
injection is a separate step after clean base-data generation, and operational
readiness derivation does not read the anomaly manifest.

## Proposed repository structure

```text
ai-payment-migration-control-tower/
|
+-- README.md
+-- BRD.md
+-- SRS.md
+-- requirements.txt
+-- LICENSE
|
+-- data/
|   +-- synthetic/
|   +-- messages/
|   |   +-- mt101/
|   |   +-- pain001_v03/
|   |   +-- pain001_v09/
|   |   +-- status/
|   +-- generated/
|
+-- src/
|   +-- generate_data.py
|   +-- parse_mt101.py
|   +-- parse_xml.py
|   +-- validate_messages.py
|   +-- validate_migrations.py
|   +-- evidence_engine.py
|   +-- reporting.py
|
+-- tests/
|
+-- powerbi/
|   +-- screenshots/
|   +-- model_documentation.md
|
+-- samples/
|   +-- executive_brief/
|   +-- issue_reports/
|   +-- japanese_stakeholder_pack/
|
+-- governance/
|   +-- ai_authority_matrix.md
|   +-- data_classification.md
|   +-- hallucination_controls.md
|   +-- failure_scenarios.md
|   +-- audit_model.md
|
+-- docs/
|   +-- architecture.md
|   +-- data_dictionary.md
|   +-- migration_scenario.md
|   +-- design_decisions.md
|
+-- site/
```

## MVP scope

The first release should remain intentionally small in functionality even though the synthetic programme contains 200 clients.

### In scope

- reproducible generation of 200 synthetic client migration cases;
- controlled injection of realistic data-quality and migration exceptions;
- canonical migration tables;
- a small set of synthetic payment-message samples;
- deterministic validation rules;
- evidence provenance;
- Power BI-ready outputs;
- one operational dashboard;
- weekly executive reporting dataset;
- evidence-aware issue output;
- selected Japanese stakeholder examples;
- governance controls and human approval boundaries.

### Out of scope

- real SWIFT connectivity;
- production payment processing;
- cryptographic signing;
- payment execution;
- comprehensive ISO 20022 implementation;
- comprehensive CBPR+ validation;
- sanctions / AML screening;
- regulatory compliance certification;
- full APAC clearing-system simulation;
- autonomous production agents;
- storage or processing of confidential employer information.

## Example controlled anomalies

The generator should deliberately create realistic failures such as:

- missing treasury or IT owner;
- overdue testing;
- contradictory migration statuses;
- stale correspondence;
- target date preceding prerequisite completion;
- unresolved dependency marked as closed;
- malformed or incomplete postal address;
- conflicting account / currency reference data;
- message schema or field validation failure;
- status evidence inconsistent with dashboard status;
- Japanese / English entity-name variation;
- unsupported claims in a draft narrative.

The objective is to test controls, not to generate a perfectly clean dataset.

## AI operating principle

AI is an **assistive layer**, not the source of truth.

### AI may assist with

- drafting summaries;
- grouping evidence;
- highlighting possible contradictions;
- drafting clarification questions;
- drafting bilingual communications;
- proposing issue wording;
- explaining code and tests.

### Human approval is required for

- changing an official migration status;
- accepting risk;
- confirming production readiness;
- changing a committed target date;
- interpreting regulatory obligations;
- escalating to senior stakeholders;
- sending external communication.

All material claims in AI-assisted reports should be traceable to structured evidence or explicitly labelled as inference.

## Development approach

1. Define canonical data model.
2. Define synthetic-data generation rules.
3. Define injected exceptions.
4. Generate reproducible data.
5. Build deterministic validators.
6. Produce Power BI-ready tables.
7. Build the dashboard.
8. Produce evidence packages and sample AI-assisted outputs.
9. Add Japanese stakeholder examples.
10. Document governance and failure handling.
11. Publish selected screenshots and explanations through GitHub Pages.

## Success criteria

The project is successful if a reviewer can understand, without access to any employer information:

1. the operational migration problem;
2. the data model used to control it;
3. how evidence changes reported readiness;
4. how Python catches deterministic errors;
5. how Power BI exposes programme risk;
6. how AI assists without being treated as authoritative;
7. how Japanese stakeholder communication is handled;
8. where human judgement remains mandatory.

## Standards context and references

The repository uses public standards only as background for a fictional scenario.

- ISO 20022 archive — Payments Initiation V03 / `pain.001.001.03`  
  https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive
- Swift — FINplus Customer Credit Transfer Initiation with ISO 20022 (`pain.001.001.09`)  
  https://www.swift.com/myswift/services/training/swift-training-catalogue/browse-swift-training-catalogue/finplus-customer-credit-transfer-initiation-iso-20022-pain001
- Swift — Rulebook for Payment Initiation Relay  
  https://www.swift.com/sites/default/files/files/rulebook-for-payment-initiation-relay_10032025.pdf
- Swift — CBPR+ self-attestation message versions  
  https://www.swift.com/de/node/309830

## AI-assisted development disclosure

This portfolio is designed and reviewed by its author with development assistance from AI tools including ChatGPT and Codex. AI may be used for code generation, testing support, documentation drafts, language review, and implementation assistance.

The author remains responsible for:

- project scope and acceptance criteria;
- domain interpretation;
- design decisions;
- review of generated code and outputs;
- accuracy of public claims;
- confidentiality controls;
- final published content.

## Status

**Phase:** Initial specification / MVP design.
