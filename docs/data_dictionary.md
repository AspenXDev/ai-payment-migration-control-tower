# Canonical data model

All records are fictional and classified as synthetic/public. The generator
writes one UTF-8 CSV per table, with one header row and ISO 8601 dates. Column
order, primary keys, and foreign keys are executable metadata in
`src/data_model.py`.

## Tables and grain

| Table | Grain | Primary key | Parent relationship |
|---|---|---|---|
| `clients` | One fictional corporate client | `client_id` | — |
| `client_addresses` | One client address | `address_id` | `client_id -> clients` |
| `accounts` | One synthetic bank account relationship | `account_id` | `client_id -> clients` |
| `payment_profiles` | One payment purpose/currency profile | `payment_profile_id` | `client_id -> clients` |
| `migration_cases` | One migration case per client | `case_id` | `client_id -> clients` |
| `milestones` | One planned case milestone | `milestone_id` | `case_id -> migration_cases` |
| `documentation_items` | One required or optional document | `document_item_id` | Case and optional evidence |
| `test_cycles` | One case test cycle | `test_id` | Case and optional evidence |
| `dependencies` | One case dependency | `dependency_id` | `case_id -> migration_cases` |
| `risks` | One transparent control-risk input | `risk_id` | `case_id -> migration_cases` |
| `evidence` | One observed assertion/source reference | `evidence_id` | `case_id -> migration_cases` |
| `correspondence` | One synthetic correspondence event | `correspondence_id` | Case and evidence |
| `message_artifacts` | One selected payment-message artefact | `message_artifact_id` | `case_id -> migration_cases` |
| `issues` | One evidence-aware issue claim | `issue_id` | `case_id -> migration_cases` |
| `issue_evidence` | One issue/evidence relationship | Composite | Issue and evidence |
| `audit_events` | One auditable system event | `audit_event_id` | Polymorphic entity reference |

`client_addresses` is the normalized extension needed for the SRS address
quality scenarios. `account_reference`, `prerequisite_status`, `mandatory`, and
`business_status` extend the SRS minimum fields so the specified anomalies are
machine-testable without overloading free text.

## Determinism and test-only controls

The default synthetic snapshot uses seed `20260829`, as-of date `2026-08-28`,
and a fixed synthetic generation timestamp. Attribute choices are derived from
SHA-256 using `(seed, namespace, client ordinal)`, so results do not depend on
iteration order or ambient random state.

The anomaly manifest is written to
`data/generated/_test_only/anomaly_manifest.json`. It records expected defects
for pytest only. Readiness derivation and relational validation operate solely
on the canonical tables and never load that manifest.
