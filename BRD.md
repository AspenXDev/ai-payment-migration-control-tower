# Business Requirements Document (BRD)

## AI-Assisted Payment Migration Control Tower

**Document status:** Draft baseline  
**Project type:** Public portfolio project  
**Data classification:** Public / synthetic only  
**Intended implementation:** MVP

---

## 1. Purpose

This Business Requirements Document defines the business problem, objectives, scope, stakeholders, capabilities, controls, and acceptance criteria for the **AI-Assisted Payment Migration Control Tower**.

The project models a fictional regional bank conducting a large corporate-treasury payment migration across Singapore, Japan, and other APAC markets.

It is designed as a public portfolio artefact demonstrating the ability to combine:

- banking and payment-workflow knowledge;
- PMO and migration governance;
- structured data management;
- deterministic validation;
- management reporting;
- evidence-aware AI assistance;
- Japanese stakeholder communication;
- responsible AI controls.

All data and communications must be synthetic.

---

## 2. Business problem

Large client migrations are rarely controlled through one clean system.

Programme status may be distributed across:

- client records;
- account and product data;
- implementation plans;
- technical message artefacts;
- documentation trackers;
- UAT results;
- dependencies;
- risk registers;
- correspondence;
- status acknowledgements;
- meeting actions;
- management reports.

This creates several control problems.

### 2.1 Status ambiguity

A client can be reported as "on track" while underlying evidence shows unresolved testing, documentation, dependency, or data-quality issues.

### 2.2 Evidence fragmentation

Reported status and supporting evidence may reside in different systems or documents.

### 2.3 Ownership gaps

Dependencies and actions can remain unresolved because no accountable owner is recorded.

### 2.4 Reporting latency

Executive reporting often requires repeated manual consolidation and rewriting.

### 2.5 Contradictory information

Different stakeholders may provide incompatible status updates.

### 2.6 AI governance risk

Generative AI can improve summarisation and drafting but can also produce unsupported statements, obscure contradictory evidence, or create false confidence if it is treated as authoritative.

### 2.7 Cross-language communication

Japanese stakeholder communication requires more than literal translation. Operational clarity, ownership, deadlines, escalation level, and technical terminology must survive the language transition.

---

## 3. Business objective

Create a synthetic control-tower demonstration that makes migration state, evidence, risk, ownership, and management attention visible while placing explicit limits on AI authority.

The target proposition is:

> **Banking workflow + PMO control + AI augmentation + data + Japanese communication + governance**

---

## 4. Business goals

### BG-01 — Demonstrate migration control

Show that a complex corporate migration programme can be represented through a coherent, auditable data model.

### BG-02 — Separate reported status from evidence-backed status

Enable reviewers to see whether a reported migration state is supported by current evidence.

### BG-03 — Surface management attention

Identify overdue actions, unresolved dependencies, ownership gaps, contradictions, and concentrated risk.

### BG-04 — Reduce manual reporting effort

Prepare repeatable datasets for a weekly executive brief and evidence-aware issue reports.

### BG-05 — Demonstrate responsible AI augmentation

Use AI for drafting and synthesis while keeping deterministic validation and decision authority outside the LLM.

### BG-06 — Demonstrate bilingual stakeholder capability

Provide realistic synthetic Japanese/English migration communications and explain material translation decisions.

### BG-07 — Protect confidentiality

Demonstrate the capabilities above without disclosing any real employer, bank, client, colleague, system, process, or confidential material.

---

## 5. Business scenario

A fictional regional bank must migrate **200 corporate customers** across APAC.

Customers differ by:

- jurisdiction;
- migration wave;
- payment-service profile;
- current and target payment format;
- bank account relationships;
- currencies;
- payment purpose;
- documentation status;
- testing status;
- migration dependencies;
- risk;
- ownership;
- target date;
- correspondence state;
- escalation state.

Synthetic source artefacts may include:

- MT101;
- legacy `pain.001.001.03`;
- current-state `pain.001.001.09` examples;
- selected payment status or acknowledgement data;
- selected downstream ISO 20022 messages;
- testing results;
- correspondence;
- reference data.

Public standards provide scenario context only. The project does not claim full scheme or network compliance.

---

## 6. Stakeholders

Because this is a portfolio project, stakeholders are modelled both as fictional business actors and real portfolio consumers.

### 6.1 Fictional programme stakeholders

| Stakeholder | Interest |
|---|---|
| Migration Programme Lead | Overall delivery, risks, decisions |
| Treasury Owner | Client/business readiness |
| IT Owner | Technical readiness |
| Client Service / Implementation | Client coordination |
| Product / Payments SME | Product and format interpretation |
| Risk / Governance | Control effectiveness |
| Executive Sponsor | Exceptions, decisions, delivery confidence |
| Corporate Client Treasury | Business readiness |
| Corporate Client IT | File/message and connectivity readiness |

### 6.2 Portfolio stakeholders

| Stakeholder | Interest |
|---|---|
| Hiring manager | Evidence of relevant delivery capability |
| Recruiter | Clear market proposition |
| Technical interviewer | Data, Python, validation and design quality |
| Programme / PMO interviewer | Governance and control model |
| Banking/payments interviewer | Domain plausibility |
| Japanese-speaking stakeholder | Communication competence |

---

## 7. Scope

### 7.1 In scope

The MVP shall include:

1. reproducible generation of 200 synthetic migration cases;
2. synthetic accounts and payment profiles;
3. synthetic migration waves;
4. documentation and testing state;
5. dependencies, risks, owners, target dates, and escalation state;
6. selected synthetic payment-message artefacts;
7. deterministic validation;
8. evidence provenance;
9. contradiction detection based on defined rules;
10. Power BI-ready output tables;
11. migration-control dashboard;
12. weekly executive-brief dataset;
13. evidence-aware issue-report dataset;
14. selected Japanese stakeholder samples;
15. AI governance rules;
16. auditability of generated data and AI-assisted outputs.

### 7.2 Out of scope

The MVP shall not include:

- real bank or client data;
- production SWIFT connectivity;
- production API/H2H connectivity;
- payment execution;
- cryptographic signing;
- comprehensive message-standard implementation;
- comprehensive CBPR+ validation;
- regulatory certification;
- sanctions or AML screening;
- comprehensive domestic-clearing simulation;
- autonomous remediation;
- autonomous external communication;
- autonomous risk acceptance;
- full workflow-management software.

---

## 8. Business assumptions

### BA-01

The portfolio must be understandable without knowledge of any specific employer.

### BA-02

Synthetic data may deliberately contain realistic defects.

### BA-03

The dataset will support 200 clients, but only a limited number of message examples need to be richly modelled.

### BA-04

Power BI Desktop is the primary visual reporting tool.

### BA-05

Python and pandas are used for deterministic transformation and validation.

### BA-06

Generative AI is assistive. It is not the authoritative system of record.

### BA-07

The MVP can use manually invoked ChatGPT/Codex workflows rather than a production LLM API.

### BA-08

The portfolio must be publishable in a public GitHub repository.

---

## 9. Business requirements

### BR-01 — Synthetic client population

The solution shall generate 200 synthetic corporate client records with varied jurisdictions, waves, migration states, owners, risks, and target dates.

**Business value:** Creates a programme-scale dataset without confidentiality risk.

### BR-02 — Account and payment-profile modelling

The solution shall model one-to-many banking relationships for clients, including accounts, account names, branches or booking locations, currencies, creditor countries, and payment purposes.

**Business value:** Prevents the migration case from being reduced to one status field per client.

### BR-03 — Migration lifecycle

The solution shall represent a defined migration lifecycle, including at minimum:

- discovery / scope;
- documentation;
- build / configuration;
- testing;
- readiness;
- production / migrated;
- post-migration validation.

**Business value:** Provides consistent stage reporting.

### BR-04 — Milestone control

The solution shall record planned and actual milestone dates and identify overdue milestones.

### BR-05 — Dependency control

The solution shall record dependencies, accountable owners, due dates, status, and ageing.

### BR-06 — Ownership control

The solution shall identify material cases, dependencies, risks, or actions without a valid owner.

### BR-07 — Risk model

The solution shall provide transparent migration-risk inputs and an explainable derived risk indicator.

A derived risk indicator must not be represented as formal bank risk acceptance.

### BR-08 — Evidence model

Material migration claims shall be linkable to evidence.

Evidence may include:

- structured records;
- test results;
- message-validation results;
- correspondence;
- acknowledgements;
- manually generated synthetic artefacts.

### BR-09 — Evidence-backed readiness

The solution shall distinguish reported readiness from evidence-confirmed readiness according to documented rules.

### BR-10 — Contradiction identification

The solution shall identify defined contradictions, such as:

- client reported ready while UAT remains failed;
- dependency reported closed while prerequisite remains open;
- production-ready status while required documentation is missing;
- two current evidence items asserting incompatible states.

The system shall not imply that all semantic contradictions can be discovered automatically.

### BR-11 — Message artefacts

The solution shall include selected synthetic message artefacts sufficient to demonstrate source-format and target-format migration concepts.

The portfolio shall clearly distinguish:

- legacy source formats;
- current target examples;
- customer-to-bank / forwarding-agent initiation concepts;
- downstream FI-to-FI execution concepts.

### BR-12 — Address-quality scenario

The solution shall contain synthetic postal-address migration scenarios, including structured, hybrid, incomplete, and conflicting address data.

### BR-13 — Deterministic validation

Fields and conditions that can be validated deterministically shall be evaluated in Python rather than delegated to an LLM.

### BR-14 — Dashboard

The solution shall provide a Power BI dashboard covering:

- completion;
- evidence-backed completion;
- overdue items;
- progress by country;
- progress by wave;
- risk concentration;
- unresolved dependencies;
- unowned dependencies;
- escalation population;
- data-quality exceptions.

### BR-15 — Executive reporting

The solution shall prepare a weekly reporting dataset capable of supporting:

- changes since last week;
- decisions required;
- top risks;
- recoveries;
- next milestones.

### BR-16 — Evidence-aware issue report

A material issue record shall be capable of presenting:

- claim;
- supporting evidence;
- contradicting evidence;
- confidence;
- missing evidence;
- recommended action;
- required human decision.

### BR-17 — Japanese stakeholder sample

The portfolio shall include at least:

1. one bilingual migration notice;
2. one bilingual clarification request;
3. one bilingual escalation example;
4. notes explaining selected translation decisions.

### BR-18 — AI authority boundaries

The project shall document actions that:

1. AI may perform;
2. AI may recommend subject to human approval;
3. AI must not decide.

### BR-19 — Human approval

Human approval shall remain mandatory for at least:

- production readiness;
- risk acceptance;
- target-date commitment;
- material escalation;
- regulatory interpretation;
- external communication.

### BR-20 — AI evidence discipline

Any AI-assisted material claim in a published sample shall either:

- cite its evidence;
- be labelled as an inference; or
- be identified as a recommendation.

### BR-21 — Audit trail

The solution shall maintain sufficient metadata to determine:

- when synthetic data was generated;
- which validation rules were applied;
- which evidence supported an issue;
- which output version was produced;
- whether an output was AI-assisted and reviewed.

### BR-22 — Data classification

Every dataset and artefact in the public repository shall be classified as synthetic/public.

### BR-23 — Confidentiality control

No implementation shall require or encourage copying employer data into the repository or into public AI contexts.

### BR-24 — Reproducibility

A reviewer shall be able to regenerate the principal synthetic structured datasets from documented code and a deterministic random seed.

### BR-25 — Explainability

Key dashboard and risk indicators shall have documented definitions.

### BR-26 — Portfolio usability

A reviewer shall be able to understand the business problem, architecture, outputs, controls, and limitations from the repository documentation without running the entire solution.

---

## 10. Dashboard business views

### View 1 — Executive Control Tower

Questions:

- How much of the programme is complete?
- How much is actually evidence-confirmed?
- Which waves or countries are at risk?
- What changed?
- Where is management attention needed?

### View 2 — Migration Operations

Questions:

- Which clients are blocked?
- Which milestones are late?
- What documentation or test evidence is missing?
- Which client/account/payment profiles are affected?

### View 3 — Risk and Dependencies

Questions:

- Where are risks concentrated?
- Which dependencies are ageing?
- Which dependencies have no owner?
- Which blockers affect multiple clients?

### View 4 — Evidence and Data Quality

Questions:

- Which reported statuses lack current evidence?
- Which sources contradict one another?
- Which payment/message records fail deterministic rules?
- Which address records are incomplete?

---

## 11. AI governance requirements

### 11.1 AI may

- draft prose from supplied evidence;
- summarise changes in structured data;
- suggest issue wording;
- identify candidate contradictions for human review;
- draft clarification questions;
- draft bilingual communications;
- assist development and testing.

### 11.2 AI may recommend but not approve

- escalation;
- revised target date;
- risk rating;
- client prioritisation;
- recovery action.

### 11.3 AI shall not be represented as deciding

- production readiness;
- risk acceptance;
- regulatory compliance;
- payment validity in production;
- external communication release;
- contractual commitment.

### 11.4 Hallucination control

AI outputs shall be reviewed for unsupported:

- dates;
- client states;
- causes;
- commitments;
- owners;
- technical requirements;
- regulatory claims.

---

## 12. Business rules

The following initial rules are illustrative and shall be refined during implementation.

### RULE-001 — Ready requires successful testing

A case shall not be evidence-confirmed as ready if mandatory testing remains failed or incomplete.

### RULE-002 — Ready requires required documentation

A case shall not be evidence-confirmed as ready if mandatory documentation remains incomplete.

### RULE-003 — Material open blocker prevents evidence-confirmed readiness

A case with an unresolved blocker-level dependency shall not be evidence-confirmed as ready.

### RULE-004 — Ownership exception

An open material dependency without an accountable owner shall be surfaced as a governance exception.

### RULE-005 — Stale evidence

A reported status supported only by evidence older than a configurable threshold shall be flagged as stale rather than automatically treated as false.

### RULE-006 — Contradictory current evidence

Where two current evidence items assert incompatible states, the case shall be marked for human review.

### RULE-007 — Inference is not fact

Derived or AI-generated conclusions shall be stored separately from source evidence.

---

## 13. Non-functional business expectations

### NBE-01 — Public-safe

The repository must be suitable for public viewing.

### NBE-02 — Understandable

A hiring manager should understand the principal value proposition within several minutes of reading the README.

### NBE-03 — Demonstrable

The project must produce screenshots, sample outputs, and traceable examples even if a reviewer does not have Power BI installed.

### NBE-04 — Maintainable

The code and rules should be modular enough to extend without redesigning the whole project.

### NBE-05 — Honest limitations

Documentation must clearly distinguish demonstration logic from production banking compliance.

---

## 14. Success measures

The MVP shall be considered complete when:

1. 200 synthetic migration cases can be reproduced;
2. at least 10 controlled exception types are injected;
3. deterministic validations produce traceable results;
4. a Power BI-ready model is generated;
5. the dashboard exposes the agreed management views;
6. reported vs evidence-backed readiness is visible;
7. at least one evidence-aware issue can be traced from claim to source;
8. one weekly executive brief can be generated from a dated snapshot comparison;
9. the Japanese sample pack is published;
10. AI governance and human approval boundaries are documented;
11. all public data is demonstrably synthetic;
12. the project can be explained without reference to a specific employer.

---

## 15. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Scope expands into building a bank | Maintain explicit MVP and out-of-scope list |
| Portfolio recreates daily operational labour | Automate synthetic generation and implementation; focus human effort on judgement |
| Technical standards become inaccurate | Cite public standards and label demonstrative assumptions |
| AI outputs appear authoritative | Evidence links, labels, confidence and human approval |
| Synthetic data looks unrealistically clean | Inject controlled contradictions and defects |
| Synthetic data accidentally resembles real clients | Use fictional names, deterministic generators and review |
| Confidential process knowledge leaks into design | Use generic control patterns and public standards only |
| Dashboard becomes cosmetic | Tie each visual to a defined business question |
| Code becomes main story | Keep business-control narrative primary |
| AI assistance obscures authorship | Publish concise AI-assisted development disclosure |

---

## 16. Dependencies

- Python environment;
- pandas;
- pytest;
- XML parsing library from the Python standard library or a documented dependency;
- Power BI Desktop for PBIX authoring;
- GitHub repository;
- optional GitHub Pages deployment;
- AI tooling for development assistance and reviewed drafting.

---

## 17. Standards context

The portfolio may reference public materials including:

- ISO 20022 archive for `pain.001.001.03`;
- Swift Payment Initiation Relay documentation;
- Swift FINplus `pain.001.001.09` training material;
- current Swift CBPR+ message-version references.

These sources inform the fictional architecture; they do not turn the portfolio into a certified implementation.

### References

- https://www.iso20022.org/catalogue-messages/iso-20022-messages-archive
- https://www.swift.com/sites/default/files/files/rulebook-for-payment-initiation-relay_10032025.pdf
- https://www.swift.com/myswift/services/training/swift-training-catalogue/browse-swift-training-catalogue/finplus-customer-credit-transfer-initiation-iso-20022-pain001
- https://www.swift.com/de/node/309830

---

## 18. Approval principle

For this personal portfolio project, approval means the author has reviewed the requirements for:

- portfolio relevance;
- technical plausibility;
- public confidentiality;
- explainability;
- manageable scope.

No employer approval or endorsement is implied.
