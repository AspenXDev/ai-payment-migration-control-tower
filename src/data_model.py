"""Canonical relational model for the synthetic migration control tower.

The model is intentionally represented as plain metadata so the generator and
tests share one definition of table names, column order, keys, and foreign-key
relationships without requiring a database or an ORM.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


DATA_MODEL_VERSION = "1.0.0"


@dataclass(frozen=True)
class ForeignKey:
    """A foreign-key relationship between two canonical CSV tables."""

    columns: tuple[str, ...]
    referenced_table: str
    referenced_columns: tuple[str, ...]
    optional: bool = False


@dataclass(frozen=True)
class TableSpec:
    """Column and key metadata for one normalized output table."""

    columns: tuple[str, ...]
    primary_key: tuple[str, ...]
    foreign_keys: tuple[ForeignKey, ...] = ()


TABLE_SPECS: dict[str, TableSpec] = {
    "clients": TableSpec(
        columns=(
            "client_id",
            "client_name",
            "jurisdiction",
            "segment",
            "migration_wave",
            "overall_reported_status",
            "target_date",
        ),
        primary_key=("client_id",),
    ),
    "client_addresses": TableSpec(
        columns=(
            "address_id",
            "client_id",
            "address_type",
            "address_line_1",
            "city",
            "postal_code",
            "country_code",
            "unstructured_address",
            "unstructured_country_code",
        ),
        primary_key=("address_id",),
        foreign_keys=(ForeignKey(("client_id",), "clients", ("client_id",)),),
    ),
    "accounts": TableSpec(
        columns=(
            "account_id",
            "client_id",
            "account_name",
            "booking_location",
            "currency",
            "in_scope",
            "account_reference",
        ),
        primary_key=("account_id",),
        foreign_keys=(ForeignKey(("client_id",), "clients", ("client_id",)),),
    ),
    "payment_profiles": TableSpec(
        columns=(
            "payment_profile_id",
            "client_id",
            "source_format",
            "target_format",
            "channel",
            "payment_purpose",
            "creditor_country",
            "transaction_currency",
            "volume_band",
        ),
        primary_key=("payment_profile_id",),
        foreign_keys=(ForeignKey(("client_id",), "clients", ("client_id",)),),
    ),
    "migration_cases": TableSpec(
        columns=(
            "case_id",
            "client_id",
            "wave",
            "lifecycle_stage",
            "reported_readiness",
            "evidence_readiness",
            "target_date",
            "treasury_owner",
            "it_owner",
            "migration_owner",
            "escalation_status",
        ),
        primary_key=("case_id",),
        foreign_keys=(ForeignKey(("client_id",), "clients", ("client_id",)),),
    ),
    "milestones": TableSpec(
        columns=(
            "milestone_id",
            "case_id",
            "milestone_type",
            "planned_date",
            "actual_date",
            "status",
        ),
        primary_key=("milestone_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "documentation_items": TableSpec(
        columns=(
            "document_item_id",
            "case_id",
            "document_type",
            "required",
            "status",
            "evidence_id",
        ),
        primary_key=("document_item_id",),
        foreign_keys=(
            ForeignKey(("case_id",), "migration_cases", ("case_id",)),
            ForeignKey(("evidence_id",), "evidence", ("evidence_id",), optional=True),
        ),
    ),
    "test_cycles": TableSpec(
        columns=(
            "test_id",
            "case_id",
            "test_type",
            "mandatory",
            "planned_date",
            "executed_date",
            "status",
            "defect_count",
            "evidence_id",
        ),
        primary_key=("test_id",),
        foreign_keys=(
            ForeignKey(("case_id",), "migration_cases", ("case_id",)),
            ForeignKey(("evidence_id",), "evidence", ("evidence_id",), optional=True),
        ),
    ),
    "dependencies": TableSpec(
        columns=(
            "dependency_id",
            "case_id",
            "dependency_type",
            "description",
            "owner",
            "opened_date",
            "due_date",
            "status",
            "severity",
            "prerequisite_status",
        ),
        primary_key=("dependency_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "risks": TableSpec(
        columns=(
            "risk_id",
            "case_id",
            "risk_type",
            "impact",
            "likelihood",
            "derived_score",
            "status",
            "owner",
        ),
        primary_key=("risk_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "evidence": TableSpec(
        columns=(
            "evidence_id",
            "case_id",
            "evidence_type",
            "source_artifact_id",
            "observed_at",
            "assertion",
            "structured_value",
            "freshness_status",
        ),
        primary_key=("evidence_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "correspondence": TableSpec(
        columns=(
            "correspondence_id",
            "case_id",
            "sent_at",
            "sender_role",
            "recipient_role",
            "language",
            "subject",
            "asserted_state",
            "evidence_id",
        ),
        primary_key=("correspondence_id",),
        foreign_keys=(
            ForeignKey(("case_id",), "migration_cases", ("case_id",)),
            ForeignKey(("evidence_id",), "evidence", ("evidence_id",)),
        ),
    ),
    "message_artifacts": TableSpec(
        columns=(
            "message_artifact_id",
            "case_id",
            "message_family",
            "message_version",
            "direction",
            "file_path",
            "parse_status",
            "validation_status",
            "business_status",
        ),
        primary_key=("message_artifact_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "issues": TableSpec(
        columns=(
            "issue_id",
            "case_id",
            "claim",
            "claim_type",
            "confidence",
            "recommended_action",
            "human_decision_required",
            "status",
        ),
        primary_key=("issue_id",),
        foreign_keys=(ForeignKey(("case_id",), "migration_cases", ("case_id",)),),
    ),
    "issue_evidence": TableSpec(
        columns=("issue_id", "evidence_id", "relationship", "weight_or_relevance"),
        primary_key=("issue_id", "evidence_id", "relationship"),
        foreign_keys=(
            ForeignKey(("issue_id",), "issues", ("issue_id",)),
            ForeignKey(("evidence_id",), "evidence", ("evidence_id",)),
        ),
    ),
    "audit_events": TableSpec(
        columns=(
            "audit_event_id",
            "event_timestamp",
            "event_type",
            "entity_type",
            "entity_id",
            "actor_type",
            "tool",
            "input_version",
            "output_version",
            "review_status",
        ),
        primary_key=("audit_event_id",),
    ),
}


TABLE_ORDER = tuple(TABLE_SPECS)


def validate_relations(tables: Mapping[str, Sequence[Mapping[str, object]]]) -> None:
    """Raise ``ValueError`` when canonical shape, keys, or joins are invalid."""

    errors: list[str] = []
    missing_tables = set(TABLE_SPECS) - set(tables)
    extra_tables = set(tables) - set(TABLE_SPECS)
    if missing_tables:
        errors.append(f"missing tables: {sorted(missing_tables)}")
    if extra_tables:
        errors.append(f"unexpected tables: {sorted(extra_tables)}")
    if errors:
        raise ValueError("; ".join(errors))

    indexes: dict[str, set[tuple[object, ...]]] = {}
    for table_name, spec in TABLE_SPECS.items():
        keys: set[tuple[object, ...]] = set()
        expected_columns = set(spec.columns)
        for row_number, row in enumerate(tables[table_name], start=2):
            if set(row) != expected_columns:
                errors.append(
                    f"{table_name} row {row_number} columns differ from canonical schema"
                )
                continue
            key = tuple(row[column] for column in spec.primary_key)
            if any(value in (None, "") for value in key):
                errors.append(f"{table_name} row {row_number} has a blank primary key")
            elif key in keys:
                errors.append(f"{table_name} has duplicate primary key {key!r}")
            keys.add(key)
        indexes[table_name] = keys

    for table_name, spec in TABLE_SPECS.items():
        for row_number, row in enumerate(tables[table_name], start=2):
            for foreign_key in spec.foreign_keys:
                key = tuple(row[column] for column in foreign_key.columns)
                if foreign_key.optional and all(value in (None, "") for value in key):
                    continue
                if any(value in (None, "") for value in key):
                    errors.append(
                        f"{table_name} row {row_number} has a partial blank foreign key {key!r}"
                    )
                elif key not in indexes[foreign_key.referenced_table]:
                    errors.append(
                        f"{table_name} row {row_number} foreign key {key!r} does not "
                        f"reference {foreign_key.referenced_table}"
                    )

    if errors:
        raise ValueError("; ".join(errors))
