# Software Requirements Specification (SRS)

## AI-Assisted Payment Migration Control Tower

**Document status:** Draft baseline  
**System type:** Synthetic-data analytical / portfolio system  
**Primary implementation:** Python + pandas + Power BI  
**Deployment:** Local development + public GitHub documentation  
**Runtime AI dependency:** Not required for MVP

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the functional, data, interface, validation, security, governance, and quality requirements for the **AI-Assisted Payment Migration Control Tower**.

The system supports a synthetic APAC corporate-payment migration programme containing 200 fictional customers.

It shall:

1. generate synthetic migration data;
2. ingest selected synthetic payment-message artefacts;
3. normalise data into a canonical model;
4. run deterministic validations;
5. derive programme-control indicators;
6. preserve evidence provenance;
7. produce Power BI-ready datasets;
8. produce evidence packages for reviewed AI-assisted reporting;
9. support public portfolio demonstration without confidential data.

---

## 2. Design principles

### DP-01 — Synthetic by construction

All data must be generated or manually authored as fictional test data.

### DP-02 — Deterministic before generative

If a condition can be checked by explicit logic, the check shall be performed by deterministic code rather than delegated to an LLM.

### DP-03 — Evidence before narrative

Narrative outputs shall be downstream of structured facts and evidence.

### DP-04 — Fact / inference / recommendation separation

The data model shall distinguish source evidence from derived conclusions and recommendations.

### DP-05 — Human authority

The system shall not automatically approve production readiness, risk acceptance, external communication, or regulatory interpretation.

### DP-06 — Portfolio-scale, not production-scale

Architecture shall optimise for clarity, reproducibility, testing, and demonstration rather than production throughput.

### DP-07 — Public-safe defaults

Generated names, IDs, correspondence, and account information shall be visibly fictional.

---

## 3. System context

```text
+-----------------------+
| Synthetic generators  |
+-----------+-----------+
            |
            v
+-----------------------+
| Raw synthetic inputs  |
| CSV / JSON / TXT/XML  |
+-----------+-----------+
            |
            v
+-----------------------+
| Parsers / normalisers |
+-----------+-----------+
            |
            v
+-----------------------+
| Canonical data model  |
+------+-----------+----+
       |           |
       v           v
+-----------+  +----------------+
| Validation|  | Evidence engine|
+-----+-----+  +-------+--------+
      |                |
      +--------+-------+
               |
               v
       +---------------+
       | Output tables |
       +------+--------+
              |
      +-------+---------+
      |                 |
      v                 v
+-------------+   +--------------+
| Power BI    |   | AI evidence  |
| dashboard   |   | packages     |
+-------------+   +--------------+
```

---

## 4. User classes

### UC-01 — Portfolio author

Can generate data, run validation, inspect results, update rules, and publish approved artefacts.

### UC-02 — Portfolio reviewer

Reads repository documentation, sample outputs, screenshots, and optionally runs the code locally.

### UC-03 — Dashboard consumer

Uses the Power BI report to explore programme state.

No production bank users are in scope.

---

## 5. Functional requirements

## 5.1 Synthetic-data generation

### FR-001 — Reproducible generation

The system shall generate the same base dataset when executed with the same configured random seed.

### FR-002 — Client volume

The default generator configuration shall create 200 fictional corporate clients.

### FR-003 — Client identifiers

Each client shall receive a unique synthetic identifier unrelated to any real client identifier.

### FR-004 — Fictional entity names

Generated company names shall be synthetic and shall not intentionally reproduce known real customer names.

### FR-005 — Jurisdictions

The generator shall assign clients across a configured set of APAC jurisdictions, including at minimum Singapore and Japan.

### FR-006 — Migration waves

Each client shall be assigned to one migration wave.

### FR-007 — Owners

Each migration case may have:

- treasury owner;
- IT owner;
- migration owner.

The anomaly generator shall be capable of deliberately omitting required ownership.

### FR-008 — Target dates

Each migration case shall contain one or more target dates generated within a configurable programme period.

### FR-009 — Status variation

The generator shall produce varied lifecycle states rather than uniform completion.

### FR-010 — Accounts

A client shall support zero-to-many synthetic bank accounts subject to configured rules.

### FR-011 — Account fields

Account records shall support at least:

- account ID;
- client ID;
- account name;
- booking jurisdiction or branch descriptor;
- account currency;
- active/in-scope flag.

No real account numbers shall be generated in a format intended for live use.

### FR-012 — Payment profile

A client shall support one-to-many payment-profile records containing:

- source format;
- target format;
- channel;
- currencies;
- creditor countries;
- payment purpose;
- volume band or synthetic transaction profile.

### FR-013 — Documentation

The system shall generate required-document records and completion states.

### FR-014 — Testing

The system shall generate test-cycle records including:

- test type;
- planned date;
- actual date;
- status;
- defect count;
- evidence reference.

### FR-015 — Dependencies

The system shall generate dependency records including:

- dependency ID;
- affected client;
- description;
- owner;
- opened date;
- due date;
- status;
- severity / blocker flag.

### FR-016 — Risks

The system shall generate risk records including explicit risk factors.

### FR-017 — Correspondence

The system shall generate synthetic correspondence metadata and selected synthetic content, including:

- date;
- sender role;
- recipient role;
- language;
- subject/category;
- asserted migration state;
- evidence ID.

### FR-018 — Controlled anomaly injection

The generator shall support configurable anomaly injection separate from base-data generation.

### FR-019 — Anomaly manifest

Each injected anomaly shall be recorded in a machine-readable manifest containing:

- anomaly ID;
- anomaly type;
- affected entity;
- expected validator;
- expected severity.

This manifest is for test verification and shall not be used by the operational validation logic to "cheat."

---

## 5.2 Message artefacts

### FR-020 — MT101 samples

The repository shall contain a small number of synthetic MT101-like samples sufficient for parsing and migration examples.

Samples shall be clearly marked synthetic and educational.

### FR-021 — Legacy pain.001 samples

The repository shall include selected synthetic `pain.001.001.03` source examples.

### FR-022 — Current-state pain.001 samples

The repository shall include selected synthetic `pain.001.001.09` target examples for the fictional FINplus relay scenario.

### FR-023 — Status samples

The repository shall include selected status / acknowledgement examples sufficient to demonstrate acceptance, rejection, or follow-up evidence.

### FR-024 — Downstream-flow samples

The repository may include a limited number of `pacs.008`, `pacs.002`, or relevant `camt` examples where necessary to explain end-to-end context.

The system shall not imply that `pain.001` is itself the FI-to-FI execution message.

### FR-025 — Message provenance

Every message artefact shall have metadata including:

- message artefact ID;
- client or case ID;
- synthetic creation timestamp;
- message type;
- version where applicable;
- direction / role in scenario;
- source path;
- expected validation outcome.

---

## 5.3 Parsing and normalisation

### FR-026 — Structured input ingestion

The system shall ingest generated CSV and/or JSON structured datasets.

### FR-027 — XML parsing

The system shall parse selected XML message artefacts using a safe XML-processing approach.

### FR-028 — MT parsing

The system shall extract a limited documented subset of fields from synthetic MT101 samples.

The parser need not implement the complete MT101 standard.

### FR-029 — Canonical mapping

Parsed message fields shall map into documented canonical structures.

### FR-030 — Parse errors

A malformed input shall produce a structured error record rather than silently failing.

### FR-031 — Source retention

Normalised data shall retain a reference to the source artefact used to create it.

---

## 5.4 Canonical data model

The implementation shall include logical equivalents of the following entities.

### Client

Minimum fields:

- `client_id`
- `client_name`
- `jurisdiction`
- `segment`
- `migration_wave`
- `overall_reported_status`
- `target_date`

### Account

- `account_id`
- `client_id`
- `account_name`
- `booking_location`
- `currency`
- `in_scope`

### PaymentProfile

- `payment_profile_id`
- `client_id`
- `source_format`
- `target_format`
- `channel`
- `payment_purpose`
- `creditor_country`
- `transaction_currency`

### MigrationCase

- `case_id`
- `client_id`
- `wave`
- `lifecycle_stage`
- `reported_readiness`
- `evidence_readiness`
- `target_date`
- `treasury_owner`
- `it_owner`
- `escalation_status`

### Milestone

- `milestone_id`
- `case_id`
- `milestone_type`
- `planned_date`
- `actual_date`
- `status`

### DocumentationItem

- `document_item_id`
- `case_id`
- `document_type`
- `required`
- `status`
- `evidence_id`

### TestCycle

- `test_id`
- `case_id`
- `test_type`
- `planned_date`
- `executed_date`
- `status`
- `defect_count`
- `evidence_id`

### Dependency

- `dependency_id`
- `case_id`
- `dependency_type`
- `description`
- `owner`
- `opened_date`
- `due_date`
- `status`
- `severity`

### Risk

- `risk_id`
- `case_id`
- `risk_type`
- `impact`
- `likelihood`
- `derived_score`
- `status`
- `owner`

### Evidence

- `evidence_id`
- `case_id`
- `evidence_type`
- `source_artifact_id`
- `observed_at`
- `assertion`
- `structured_value`
- `freshness_status`

### Correspondence

- `correspondence_id`
- `case_id`
- `sent_at`
- `sender_role`
- `recipient_role`
- `language`
- `subject`
- `asserted_state`
- `evidence_id`

### MessageArtifact

- `message_artifact_id`
- `case_id`
- `message_family`
- `message_version`
- `direction`
- `file_path`
- `parse_status`
- `validation_status`

### Issue

- `issue_id`
- `case_id`
- `claim`
- `claim_type`
- `confidence`
- `recommended_action`
- `human_decision_required`
- `status`

### IssueEvidence

- `issue_id`
- `evidence_id`
- `relationship` (`SUPPORTS`, `CONTRADICTS`, `CONTEXT`)
- `weight_or_relevance`

### AuditEvent

- `audit_event_id`
- `event_timestamp`
- `event_type`
- `entity_type`
- `entity_id`
- `actor_type`
- `tool`
- `input_version`
- `output_version`
- `review_status`

---

## 5.5 Deterministic validation

### FR-032 — Validation framework

Validators shall return structured results with:

- rule ID;
- entity type;
- entity ID;
- severity;
- pass/fail status;
- observed value;
- explanatory message;
- evidence reference where relevant.

### FR-033 — Required fields

The system shall validate configured mandatory fields.

### FR-034 — Date logic

The system shall detect impossible or inconsistent date sequences.

Examples:

- completion before start;
- target date before mandatory prerequisite;
- executed test before test preparation where configured.

### FR-035 — Ownership

The system shall flag open material items without an owner.

### FR-036 — Testing readiness

Evidence-confirmed readiness shall fail if mandatory testing is incomplete or failed.

### FR-037 — Documentation readiness

Evidence-confirmed readiness shall fail if mandatory documentation is incomplete.

### FR-038 — Blocking dependencies

Evidence-confirmed readiness shall fail if a configured blocker dependency remains open.

### FR-039 — Stale evidence

Evidence older than a configurable freshness threshold shall be marked stale.

Stale evidence shall not automatically be marked incorrect.

### FR-040 — Contradictory structured state

The system shall identify defined contradictory combinations.

### FR-041 — Address validation

Synthetic address validation shall support checks for:

- missing country;
- missing town/city where required by scenario;
- presence of address lines;
- structured vs hybrid classification;
- contradictory structured and unstructured fields.

The validator is demonstrative and shall not claim complete CBPR+ compliance.

### FR-042 — XML well-formedness

XML artefacts shall be checked for well-formedness.

### FR-043 — Schema validation

Where an appropriate public XSD is legally and practically distributable or referenced, the project may validate selected samples against it.

If schema validation is not implemented, the documentation shall not imply that it is.

### FR-044 — Message business rules

Selected message fields shall be checked against documented portfolio business rules.

### FR-045 — Validation independence

Validators shall not read the anomaly manifest when determining pass/fail results.

---

## 5.6 Evidence engine

### FR-046 — Evidence linkage

Issues and readiness calculations shall preserve links to supporting evidence.

### FR-047 — Supporting / contradicting relationship

An evidence item may be classified as supporting, contradicting, or contextual relative to a claim.

### FR-048 — Confidence representation

The system may derive a bounded confidence category such as:

- High;
- Medium;
- Low;
- Insufficient evidence.

The derivation method shall be documented and shall not be presented as statistical probability unless it actually is one.

### FR-049 — Missing evidence

The system shall be able to record explicitly required but absent evidence.

### FR-050 — Human decision field

Issue outputs shall contain a field indicating whether a human decision is required and, where appropriate, the fictional role responsible.

### FR-051 — No hidden narrative facts

A generated narrative package shall not contain factual fields that are absent from its input evidence package.

---

## 5.7 Snapshot and change reporting

### FR-052 — Reporting date

Generated programme snapshots shall contain an as-of date.

### FR-053 — Prior snapshot comparison

The system shall support comparison between current and prior snapshots.

### FR-054 — Change categories

The comparison shall be able to identify at least:

- newly completed;
- newly overdue;
- newly blocked;
- recovered;
- newly escalated;
- risk increased;
- risk decreased;
- owner added / removed;
- milestone changed.

### FR-055 — Weekly brief dataset

The system shall output structured data sufficient to draft:

- changes since last week;
- top risks;
- decisions required;
- recoveries;
- next milestones.

---

## 5.8 Power BI outputs

### FR-056 — Tabular export

The system shall export Power BI-ready CSV files or equivalent flat tables.

### FR-057 — Stable keys

Exported tables shall contain stable unique keys and documented relationships.

### FR-058 — Star-schema preference

Analytical outputs should support a documented dimensional or star-like reporting model where practical.

### FR-059 — Executive KPIs

The dataset shall support calculation of:

- total clients;
- migrated clients;
- reported-ready clients;
- evidence-confirmed-ready clients;
- overdue clients;
- blocked clients;
- escalated clients;
- unowned material dependencies.

### FR-060 — Country and wave analysis

The dataset shall support filtering and aggregation by:

- country / jurisdiction;
- wave;
- migration stage;
- risk band;
- owner;
- target period.

### FR-061 — Drill-through identity

A reviewer shall be able to trace a dashboard exception to the relevant synthetic case and supporting records.

### FR-062 — Screenshot support

The repository shall include static screenshots for reviewers without Power BI.

---

## 5.9 AI evidence packages

### FR-063 — Runtime independence

The MVP shall not require an LLM API to generate the canonical data, validation results, or dashboard.

### FR-064 — Evidence package generation

The system shall produce machine-readable and/or Markdown evidence packages for selected reporting scenarios.

### FR-065 — Prompt-ready context

Evidence packages may include concise context suitable for submission to ChatGPT or another LLM.

### FR-066 — AI-output metadata

Where AI-assisted sample outputs are committed, metadata shall record:

- output ID;
- source evidence-package version;
- generation/review date;
- AI-assisted flag;
- human-review status.

### FR-067 — Unsupported-claim review

AI-assisted sample outputs shall be checked against their evidence package before publication.

### FR-068 — Review status

AI-assisted output shall have a review state such as:

- `UNREVIEWED`
- `REVIEWED`
- `APPROVED_FOR_PORTFOLIO`
- `REJECTED`

---

## 5.10 Japanese stakeholder samples

### FR-069 — Bilingual pairing

Japanese samples shall include the corresponding English source or intended meaning.

### FR-070 — Communication types

Samples shall include:

- migration notice;
- clarification request;
- escalation.

### FR-071 — Translation notes

Each sample shall document selected translation decisions affecting:

- ownership;
- urgency;
- deadline;
- technical terminology;
- ambiguity;
- politeness / escalation level.

### FR-072 — Synthetic identities

All names, organisations, dates, accounts, and transaction details in samples shall be fictional.

---

## 5.11 Audit trail

### FR-073 — Data-generation event

Each generated dataset shall record:

- generator version;
- seed;
- generation timestamp;
- configuration version.

### FR-074 — Validation run

Each validation run shall record:

- rule-set version;
- input dataset version;
- run timestamp;
- result location.

### FR-075 — Report generation

Generated evidence packages and reports shall record their source snapshot versions.

### FR-076 — AI assistance

Published AI-assisted artefacts shall indicate AI assistance without exposing private internal work-allocation details.

---

## 6. Data-quality requirements

### DQ-01 — Uniqueness

Primary identifiers shall be unique within each entity.

### DQ-02 — Referential integrity

Foreign keys shall reference valid parent entities unless a deliberately injected anomaly explicitly tests referential-integrity handling.

### DQ-03 — Controlled nulls

Null values shall either be:

- permitted by schema;
- deliberately injected;
- or reported as validation failures.

### DQ-04 — Enumerations

Core statuses shall use controlled enumerations.

### DQ-05 — Date format

Machine-readable outputs shall use ISO 8601-compatible dates.

### DQ-06 — Currency

Currency codes should use ISO 4217-style three-letter values for synthetic scenarios.

### DQ-07 — Country

Country values should use documented canonical country codes or names consistently.

### DQ-08 — Data lineage

Derived fields shall document their source fields and calculation logic.

---

## 7. Initial controlled anomaly catalogue

The MVP shall support at least 10 anomaly classes. Recommended initial set:

1. missing treasury owner;
2. missing IT owner;
3. overdue milestone;
4. failed mandatory UAT marked ready;
5. missing mandatory documentation marked ready;
6. unresolved blocker marked ready;
7. closed dependency with incomplete prerequisite;
8. stale correspondence used as sole readiness evidence;
9. contradictory current correspondence;
10. malformed XML;
11. incomplete postal address;
12. structured/unstructured address conflict;
13. unsupported currency/payment-profile combination according to fictional rules;
14. message status contradicting case status;
15. duplicate or conflicting account reference data.

---

## 8. Derived indicators

### 8.1 Reported readiness

The explicitly recorded programme status.

### 8.2 Evidence-confirmed readiness

A deterministic derived indicator.

Illustrative logic:

```text
evidence_ready =
    reported_ready
    AND mandatory_documentation_complete
    AND mandatory_testing_passed
    AND no_open_blocker
    AND required_evidence_present
    AND no_unresolved_critical_contradiction
```

The exact rules shall be version-controlled.

### 8.3 Dependency ageing

```text
age_days = as_of_date - opened_date
```

for open dependencies.

### 8.4 Overdue milestone

```text
planned_date < as_of_date
AND actual_date is null
AND status not in completed/cancelled states
```

### 8.5 Risk indicator

Any risk score shall be derived from documented inputs and shall be labelled a **portfolio control indicator**, not a formal bank credit/operational risk model.

---

## 9. External-interface requirements

## 9.1 File interfaces

Supported MVP inputs/outputs may include:

- `.csv`
- `.json`
- `.xml`
- `.txt`
- `.md`

### IR-001

Paths shall be relative to the repository root where practical.

### IR-002

Generated output directories shall be documented.

### IR-003

Generated artefacts shall not overwrite hand-authored source examples without explicit configuration.

---

## 9.2 Power BI interface

Power BI shall consume generated analytical tables.

The Python layer shall not require Power BI to run validations.

---

## 9.3 GitHub interface

The project shall be compatible with normal Git source control.

Generated large/redundant files should be excluded through `.gitignore` where practical.

Sensitive data shall never be required for repository operation.

---

## 9.4 AI interface

For MVP, AI interaction may be manual.

A typical flow is:

1. Python generates an evidence package.
2. Author submits the package to an LLM using an approved prompt.
3. LLM drafts a brief or issue summary.
4. Author reviews the draft against evidence.
5. Approved sample is saved with metadata.

Future API integration may be added but is not required.

---

## 10. Non-functional requirements

## 10.1 Security and confidentiality

### NFR-SEC-001

No secrets shall be committed to the repository.

### NFR-SEC-002

The repository shall not contain real customer, employee, counterparty, or account data.

### NFR-SEC-003

Synthetic data shall be obviously fictional.

### NFR-SEC-004

Environment variables shall be used if future integrations require tokens or keys.

### NFR-SEC-005

A `.env` file shall be gitignored if introduced.

---

## 10.2 Reproducibility

### NFR-REP-001

A documented command shall regenerate the principal synthetic datasets.

### NFR-REP-002

Randomness shall use a configurable seed.

### NFR-REP-003

Dependencies shall be pinned or bounded sufficiently to support repeatable local execution.

---

## 10.3 Testability

### NFR-TST-001

Deterministic validation functions shall be unit-testable.

### NFR-TST-002

Tests shall confirm that controlled anomalies are detected by the expected rule.

### NFR-TST-003

Tests shall include negative cases to demonstrate that clean records are not indiscriminately flagged.

### NFR-TST-004

The test suite shall not require Power BI.

---

## 10.4 Maintainability

### NFR-MNT-001

Generation, parsing, validation, evidence logic, and reporting shall be separated into modules.

### NFR-MNT-002

Business-rule identifiers shall remain stable where possible.

### NFR-MNT-003

Rules shall have human-readable descriptions.

### NFR-MNT-004

Code shall contain type hints where they materially improve readability.

---

## 10.5 Performance

Production-scale performance is not required.

### NFR-PERF-001

The system shall comfortably process the default 200-client synthetic dataset on a normal personal computer.

### NFR-PERF-002

No distributed-computing framework is required.

---

## 10.6 Explainability

### NFR-EXP-001

Every failed deterministic rule shall provide a reason.

### NFR-EXP-002

Every published derived KPI shall have a documented definition.

### NFR-EXP-003

Confidence labels shall describe their derivation.

### NFR-EXP-004

AI-generated prose shall not be the sole location of a material fact.

---

## 10.7 Accessibility and reviewability

### NFR-ACC-001

Core portfolio conclusions shall be available through Markdown and screenshots, not solely through an interactive PBIX file.

### NFR-ACC-002

Charts shall use clear titles and avoid relying exclusively on colour to encode critical meaning where practical.

---

## 11. Error handling

### ER-001

Invalid input files shall produce a logged structured error.

### ER-002

One malformed message shall not terminate processing of unrelated cases unless configured as fatal.

### ER-003

Unknown enumeration values shall be reported.

### ER-004

Missing files shall produce a clear error message.

### ER-005

AI-output generation failure shall not affect canonical validation or dashboard generation.

---

## 12. Logging

The MVP shall use human-readable logs sufficient to diagnose:

- generation failures;
- parse failures;
- validation errors;
- export failures.

Logs shall not contain secrets or real personal data.

---

## 13. Testing strategy

### 13.1 Unit tests

Test:

- generators;
- parsers;
- date rules;
- ownership rules;
- readiness rules;
- address rules;
- evidence relationships;
- snapshot comparison.

### 13.2 Integration tests

Test:

- generate -> normalise -> validate -> export;
- message -> parse -> evidence -> issue;
- prior/current snapshots -> weekly-change output.

### 13.3 Golden samples

A small number of fixed synthetic cases may be committed as expected-output examples.

### 13.4 Anomaly tests

For each anomaly type:

1. inject anomaly;
2. run relevant validator;
3. assert expected rule fails;
4. assert severity;
5. assert affected entity;
6. confirm unrelated clean case remains valid.

---

## 14. Acceptance criteria

### AC-001

Running the documented generator with the default seed produces 200 clients.

### AC-002

The output contains all required principal entities.

### AC-003

At least 10 anomaly classes are injected.

### AC-004

The test suite verifies detection of those anomalies.

### AC-005

A client marked reported-ready but with failed mandatory UAT is not evidence-confirmed-ready.

### AC-006

An open blocker without an owner appears in governance exceptions.

### AC-007

A selected issue can be traced from issue -> evidence -> source artefact.

### AC-008

Current and prior snapshots produce a deterministic change dataset.

### AC-009

Power BI-ready tables support the required KPIs.

### AC-010

At least one dashboard screenshot shows reported vs evidence-confirmed readiness.

### AC-011

At least one weekly executive brief sample is traceable to an evidence package.

### AC-012

At least one evidence-aware issue sample contains supporting and contradicting evidence.

### AC-013

Bilingual migration notice, clarification, and escalation samples are available.

### AC-014

AI-authority documentation states explicit human approval gates.

### AC-015

No real employer/client data is required to run or understand the repository.

---

## 15. Suggested command-line interface

The exact CLI may change, but the following target is recommended:

```bash
python -m src.generate_data --seed 20260829 --clients 200
python -m src.validate_migrations
python -m src.validate_messages
python -m src.reporting --as-of 2026-08-28
pytest
```

A later implementation may replace this with a task runner or Makefile.

---

## 16. Suggested configuration

Example conceptual configuration:

```yaml
programme:
  client_count: 200
  seed: 20260829
  primary_markets:
    - SG
    - JP

evidence:
  freshness_days: 14

readiness:
  require_documentation: true
  require_testing: true
  block_on_open_blocker: true
  block_on_critical_contradiction: true

anomalies:
  enabled: true
```

The actual implementation format may be YAML, JSON, TOML, or Python configuration.

---

## 17. Public standards context

For the fictional scenario:

- `pain.001.001.03` is treated as a legacy source XML version. ISO 20022 lists Payments Initiation V03 in its archive.
- Swift current CBPR+ materials identify `pain.001.001.09` for CustomerCreditTransferInitiation.
- Swift's Payment Initiation Relay documentation describes `pain.001` relay and `pain.002` status flows, with downstream FI-to-FI execution using messages such as `pacs.008`.

This SRS does not claim complete implementation of those standards.

### References

- ISO 20022 archive:  
  https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive
- Swift Payment Initiation Relay Rulebook:  
  https://www.swift.com/sites/default/files/files/rulebook-for-payment-initiation-relay_10032025.pdf
- Swift FINplus pain.001 training:  
  https://www.swift.com/myswift/services/training/swift-training-catalogue/browse-swift-training-catalogue/finplus-customer-credit-transfer-initiation-iso-20022-pain001
- Swift CBPR+ message versions:  
  https://www.swift.com/de/node/309830

---

## 18. Future enhancements

Potential later enhancements, not MVP commitments:

- richer XML schema validation;
- additional status and reporting messages;
- richer Japanese correspondence scenarios;
- interactive evidence drill-through;
- automated Markdown executive-report generation;
- CI test execution through GitHub Actions;
- GitHub Pages portfolio site;
- optional local or hosted LLM integration;
- rule-version comparison;
- scenario simulator for slippage / recovery;
- data-quality scorecard.

Enhancements should be added only if they strengthen the portfolio proposition without turning the project into an unnecessary simulation of a production bank.
