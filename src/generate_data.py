"""Generate deterministic synthetic APAC corporate migration data.

The default command creates 200 fictional client cases, writes the normalized
canonical tables as CSV, emits selected synthetic message files, and places the
anomaly manifest in an explicitly test-only directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping, Sequence

from src.data_model import DATA_MODEL_VERSION, TABLE_ORDER, TABLE_SPECS, validate_relations


DEFAULT_SEED = 20260829
DEFAULT_CLIENT_COUNT = 200
GENERATOR_VERSION = "1.0.0"
CONFIG_VERSION = "1.0.0"
AS_OF_DATE = date(2026, 8, 28)
GENERATION_TIMESTAMP = datetime(2026, 8, 29, tzinfo=timezone(timedelta(hours=8)))
EVIDENCE_FRESHNESS_DAYS = 14

TRUE = "true"
FALSE = "false"

JURISDICTIONS = ("SG", "JP", "HK", "AU", "MY", "TH", "ID", "PH", "KR", "NZ")
ALLOWED_PROFILE_CURRENCIES: dict[str, tuple[str, ...]] = {
    "SG": ("SGD", "USD"),
    "JP": ("JPY", "USD"),
    "HK": ("HKD", "USD"),
    "AU": ("AUD", "USD"),
    "MY": ("MYR", "USD"),
    "TH": ("THB", "USD"),
    "ID": ("IDR", "USD"),
    "PH": ("PHP", "USD"),
    "KR": ("KRW", "USD"),
    "NZ": ("NZD", "USD"),
}

CITY_BY_JURISDICTION = {
    "SG": "Singapore",
    "JP": "Yokohama",
    "HK": "Kowloon",
    "AU": "Melbourne",
    "MY": "Johor Bahru",
    "TH": "Chiang Mai",
    "ID": "Surabaya",
    "PH": "Cebu City",
    "KR": "Busan",
    "NZ": "Wellington",
}

LEGAL_SUFFIX = {
    "SG": "Pte. Ltd.",
    "JP": "Kabushiki Kaisha",
    "HK": "Limited",
    "AU": "Pty Ltd",
    "MY": "Sdn. Bhd.",
    "TH": "Company Limited",
    "ID": "Perseroan Terbatas",
    "PH": "Corporation",
    "KR": "Jusik Hoesa",
    "NZ": "Limited",
}

ANOMALY_CATALOG: tuple[dict[str, str], ...] = (
    {
        "anomaly_id": "ANOM-001",
        "anomaly_type": "missing_treasury_owner",
        "expected_validator": "OWN-001",
        "expected_severity": "HIGH",
        "description": "A migration case has no treasury owner.",
    },
    {
        "anomaly_id": "ANOM-002",
        "anomaly_type": "missing_it_owner",
        "expected_validator": "OWN-002",
        "expected_severity": "HIGH",
        "description": "A migration case has no IT owner.",
    },
    {
        "anomaly_id": "ANOM-003",
        "anomaly_type": "overdue_milestone",
        "expected_validator": "DATE-001",
        "expected_severity": "HIGH",
        "description": "An incomplete milestone is planned before the as-of date.",
    },
    {
        "anomaly_id": "ANOM-004",
        "anomaly_type": "failed_mandatory_uat_marked_ready",
        "expected_validator": "READY-001",
        "expected_severity": "CRITICAL",
        "description": "A reported-ready case has failed mandatory UAT.",
    },
    {
        "anomaly_id": "ANOM-005",
        "anomaly_type": "missing_mandatory_documentation_marked_ready",
        "expected_validator": "READY-002",
        "expected_severity": "CRITICAL",
        "description": "A reported-ready case is missing required documentation.",
    },
    {
        "anomaly_id": "ANOM-006",
        "anomaly_type": "unresolved_blocker_marked_ready",
        "expected_validator": "READY-003",
        "expected_severity": "CRITICAL",
        "description": "A reported-ready case retains an open blocker.",
    },
    {
        "anomaly_id": "ANOM-007",
        "anomaly_type": "closed_dependency_with_incomplete_prerequisite",
        "expected_validator": "DEP-001",
        "expected_severity": "HIGH",
        "description": "A dependency is closed while its prerequisite remains incomplete.",
    },
    {
        "anomaly_id": "ANOM-008",
        "anomaly_type": "stale_correspondence_as_sole_readiness_evidence",
        "expected_validator": "EVID-001",
        "expected_severity": "HIGH",
        "description": "Only stale correspondence supports reported readiness.",
    },
    {
        "anomaly_id": "ANOM-009",
        "anomaly_type": "contradictory_current_correspondence",
        "expected_validator": "EVID-002",
        "expected_severity": "CRITICAL",
        "description": "Current correspondence asserts incompatible readiness states.",
    },
    {
        "anomaly_id": "ANOM-010",
        "anomaly_type": "malformed_xml",
        "expected_validator": "MSG-001",
        "expected_severity": "HIGH",
        "description": "A selected synthetic XML message is not well formed.",
    },
    {
        "anomaly_id": "ANOM-011",
        "anomaly_type": "incomplete_postal_address",
        "expected_validator": "ADDR-001",
        "expected_severity": "MEDIUM",
        "description": "A postal address omits required locality fields.",
    },
    {
        "anomaly_id": "ANOM-012",
        "anomaly_type": "structured_unstructured_address_conflict",
        "expected_validator": "ADDR-002",
        "expected_severity": "HIGH",
        "description": "Structured and unstructured address countries conflict.",
    },
    {
        "anomaly_id": "ANOM-013",
        "anomaly_type": "unsupported_currency_payment_profile_combination",
        "expected_validator": "PROFILE-001",
        "expected_severity": "HIGH",
        "description": "A payment-profile currency is outside the fictional market rules.",
    },
    {
        "anomaly_id": "ANOM-014",
        "anomaly_type": "message_status_contradicts_case_status",
        "expected_validator": "MSG-002",
        "expected_severity": "CRITICAL",
        "description": "A rejected message contradicts a reported-ready case.",
    },
    {
        "anomaly_id": "ANOM-015",
        "anomaly_type": "duplicate_or_conflicting_account_reference_data",
        "expected_validator": "ACCOUNT-001",
        "expected_severity": "HIGH",
        "description": "One account reference is assigned conflicting currencies.",
    },
)


class StableValues:
    """Order-independent, cross-run deterministic values derived with SHA-256."""

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def integer(self, namespace: str, ordinal: int, lower: int, upper: int) -> int:
        if lower > upper:
            raise ValueError("lower bound cannot exceed upper bound")
        material = f"{self.seed}|{namespace}|{ordinal}".encode("utf-8")
        value = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
        return lower + value % (upper - lower + 1)

    def choice(self, namespace: str, ordinal: int, values: Sequence[str]) -> str:
        return values[self.integer(namespace, ordinal, 0, len(values) - 1)]


@dataclass
class GeneratedDataset:
    tables: dict[str, list[dict[str, object]]]
    anomaly_manifest: list[dict[str, object]]
    seed: int
    client_count: int


def _iso(value: date) -> str:
    return value.isoformat()


def _id(prefix: str, ordinal: int) -> str:
    return f"{prefix}-{ordinal:04d}"


def _case_id(ordinal: int) -> str:
    return _id("MC", ordinal)


def _find(
    rows: Iterable[MutableMapping[str, object]], field: str, value: object
) -> MutableMapping[str, object]:
    for row in rows:
        if row[field] == value:
            return row
    raise KeyError(f"no row where {field}={value!r}")


def _rows_for(
    rows: Iterable[MutableMapping[str, object]], field: str, value: object
) -> list[MutableMapping[str, object]]:
    return [row for row in rows if row[field] == value]


def _empty_tables() -> dict[str, list[dict[str, object]]]:
    return {table_name: [] for table_name in TABLE_ORDER}


def build_base_dataset(seed: int, client_count: int) -> dict[str, list[dict[str, object]]]:
    """Build a clean base dataset before controlled anomaly injection."""

    if client_count < 1:
        raise ValueError("client_count must be at least 1")

    stable = StableValues(seed)
    tables = _empty_tables()
    adjectives = ("Azure", "Cedar", "Lumen", "Mosaic", "Nimbus", "Sakura", "Tidal", "Verdant")
    industries = ("Components", "Logistics", "Foods", "Textiles", "Robotics", "Trading", "Packaging")
    segments = ("MID_MARKET", "LARGE_CORPORATE", "REGIONAL_TREASURY")
    source_formats = ("MT101", "PAIN.001.001.03", "PROPRIETARY_CSV")
    channels = ("HOST_TO_HOST", "FILE_UPLOAD", "SFTP_BATCH")
    purposes = ("PAYROLL", "VENDOR_PAYMENT", "INTERCOMPANY", "TAX_PAYMENT")
    risk_types = ("SCHEDULE", "CLIENT_READINESS", "TECHNICAL", "DOCUMENTATION")

    for ordinal in range(1, client_count + 1):
        client_id = _id("CL", ordinal)
        case_id = _case_id(ordinal)
        jurisdiction = stable.choice("jurisdiction", ordinal, JURISDICTIONS)
        wave = f"W{stable.integer('wave', ordinal, 1, 4)}"
        reported_ready = ordinal % 5 == 0
        target_date = AS_OF_DATE + timedelta(days=stable.integer("target", ordinal, 35, 190))
        lifecycle_stage = (
            "READINESS"
            if reported_ready
            else stable.choice(
                "lifecycle",
                ordinal,
                ("DISCOVERY", "DOCUMENTATION", "BUILD_CONFIGURATION", "TESTING"),
            )
        )
        overall_status = (
            "READY"
            if reported_ready
            else stable.choice("overall_status", ordinal, ("IN_PROGRESS", "AT_RISK", "NOT_READY"))
        )
        client_name = (
            f"Fictional {stable.choice('adjective', ordinal, adjectives)} "
            f"{stable.choice('industry', ordinal, industries)} {ordinal:04d} "
            f"{LEGAL_SUFFIX[jurisdiction]}"
        )

        tables["clients"].append(
            {
                "client_id": client_id,
                "client_name": client_name,
                "jurisdiction": jurisdiction,
                "segment": stable.choice("segment", ordinal, segments),
                "migration_wave": wave,
                "overall_reported_status": overall_status,
                "target_date": _iso(target_date),
            }
        )
        city = CITY_BY_JURISDICTION[jurisdiction]
        tables["client_addresses"].append(
            {
                "address_id": _id("ADDR", ordinal),
                "client_id": client_id,
                "address_type": "REGISTERED",
                "address_line_1": f"{100 + ordinal} Fictional Commerce Avenue",
                "city": city,
                "postal_code": f"SYN{ordinal:05d}",
                "country_code": jurisdiction,
                "unstructured_address": (
                    f"{100 + ordinal} Fictional Commerce Avenue, {city}, "
                    f"SYN{ordinal:05d}, {jurisdiction}"
                ),
                "unstructured_country_code": jurisdiction,
            }
        )
        tables["migration_cases"].append(
            {
                "case_id": case_id,
                "client_id": client_id,
                "wave": wave,
                "lifecycle_stage": lifecycle_stage,
                "reported_readiness": TRUE if reported_ready else FALSE,
                "evidence_readiness": TRUE if reported_ready else FALSE,
                "target_date": _iso(target_date),
                "treasury_owner": f"Synthetic Treasury Owner {((ordinal - 1) % 12) + 1:02d}",
                "it_owner": f"Synthetic IT Owner {((ordinal - 1) % 10) + 1:02d}",
                "migration_owner": f"Synthetic Migration Owner {((ordinal - 1) % 8) + 1:02d}",
                "escalation_status": "NONE" if ordinal % 7 else "MONITOR",
            }
        )

        account_count = stable.integer("account_count", ordinal, 0, 3)
        allowed_currencies = ALLOWED_PROFILE_CURRENCIES[jurisdiction]
        for account_number in range(1, account_count + 1):
            currency = allowed_currencies[(account_number - 1) % len(allowed_currencies)]
            tables["accounts"].append(
                {
                    "account_id": f"AC-{ordinal:04d}-{account_number:02d}",
                    "client_id": client_id,
                    "account_name": f"{client_name} Synthetic {currency} Account",
                    "booking_location": f"Fictional {city} Branch",
                    "currency": currency,
                    "in_scope": TRUE if account_number <= 2 else FALSE,
                    "account_reference": f"SYN-REF-{ordinal:04d}-{account_number:02d}",
                }
            )

        profile_count = stable.integer("profile_count", ordinal, 1, 2)
        for profile_number in range(1, profile_count + 1):
            transaction_currency = allowed_currencies[(profile_number - 1) % len(allowed_currencies)]
            creditor_country = JURISDICTIONS[(ordinal + profile_number) % len(JURISDICTIONS)]
            tables["payment_profiles"].append(
                {
                    "payment_profile_id": f"PP-{ordinal:04d}-{profile_number:02d}",
                    "client_id": client_id,
                    "source_format": stable.choice(
                        f"source_format_{profile_number}", ordinal, source_formats
                    ),
                    "target_format": "PAIN.001.001.09",
                    "channel": stable.choice(f"channel_{profile_number}", ordinal, channels),
                    "payment_purpose": stable.choice(
                        f"purpose_{profile_number}", ordinal, purposes
                    ),
                    "creditor_country": creditor_country,
                    "transaction_currency": transaction_currency,
                    "volume_band": stable.choice(
                        f"volume_{profile_number}", ordinal, ("LOW", "MEDIUM", "HIGH")
                    ),
                }
            )

        document_evidence_ids: list[str] = []
        for document_number, document_type in enumerate(
            ("MIGRATION_ENROLMENT", "AUTHORIZED_CONTACT_LIST"), start=1
        ):
            evidence_id = f"EV-{ordinal:04d}-DOC-{document_number:02d}"
            document_evidence_ids.append(evidence_id)
            tables["evidence"].append(
                {
                    "evidence_id": evidence_id,
                    "case_id": case_id,
                    "evidence_type": "DOCUMENT",
                    "source_artifact_id": f"SYN-DOC-{ordinal:04d}-{document_number:02d}",
                    "observed_at": _iso(AS_OF_DATE - timedelta(days=8 + document_number)),
                    "assertion": "DOCUMENT_COMPLETE",
                    "structured_value": document_type,
                    "freshness_status": "CURRENT",
                }
            )
            tables["documentation_items"].append(
                {
                    "document_item_id": f"DOC-{ordinal:04d}-{document_number:02d}",
                    "case_id": case_id,
                    "document_type": document_type,
                    "required": TRUE,
                    "status": "COMPLETE",
                    "evidence_id": evidence_id,
                }
            )

        uat_evidence_id = f"EV-{ordinal:04d}-UAT"
        uat_status = "PASSED" if reported_ready else "PLANNED"
        tables["evidence"].append(
            {
                "evidence_id": uat_evidence_id,
                "case_id": case_id,
                "evidence_type": "TEST_RESULT",
                "source_artifact_id": f"SYN-UAT-{ordinal:04d}",
                "observed_at": _iso(AS_OF_DATE - timedelta(days=3)),
                "assertion": uat_status,
                "structured_value": "defect_count=0",
                "freshness_status": "CURRENT",
            }
        )
        tables["test_cycles"].append(
            {
                "test_id": f"TEST-{ordinal:04d}-UAT",
                "case_id": case_id,
                "test_type": "USER_ACCEPTANCE_TEST",
                "mandatory": TRUE,
                "planned_date": _iso(AS_OF_DATE - timedelta(days=12) if reported_ready else AS_OF_DATE + timedelta(days=12)),
                "executed_date": _iso(AS_OF_DATE - timedelta(days=3)) if reported_ready else "",
                "status": uat_status,
                "defect_count": 0,
                "evidence_id": uat_evidence_id,
            }
        )

        milestone_rows = (
            (
                "DOCUMENTATION",
                AS_OF_DATE - timedelta(days=30),
                AS_OF_DATE - timedelta(days=25),
                "COMPLETED",
            ),
            (
                "UAT",
                AS_OF_DATE - timedelta(days=12) if reported_ready else AS_OF_DATE + timedelta(days=12),
                AS_OF_DATE - timedelta(days=3) if reported_ready else None,
                "COMPLETED" if reported_ready else "PLANNED",
            ),
            ("CUTOVER", target_date, None, "PLANNED"),
        )
        for milestone_type, planned_date, actual_date, status in milestone_rows:
            tables["milestones"].append(
                {
                    "milestone_id": f"MS-{ordinal:04d}-{milestone_type}",
                    "case_id": case_id,
                    "milestone_type": milestone_type,
                    "planned_date": _iso(planned_date),
                    "actual_date": _iso(actual_date) if actual_date else "",
                    "status": status,
                }
            )

        if ordinal % 4 == 0:
            tables["dependencies"].append(
                {
                    "dependency_id": f"DEP-{ordinal:04d}-01",
                    "case_id": case_id,
                    "dependency_type": "CONNECTIVITY_COORDINATION",
                    "description": "Synthetic coordination dependency for demonstration.",
                    "owner": f"Synthetic Dependency Owner {((ordinal - 1) % 9) + 1:02d}",
                    "opened_date": _iso(AS_OF_DATE - timedelta(days=10)),
                    "due_date": _iso(AS_OF_DATE + timedelta(days=20)),
                    "status": "OPEN",
                    "severity": "MEDIUM",
                    "prerequisite_status": "IN_PROGRESS",
                }
            )

        impact = stable.integer("risk_impact", ordinal, 1, 5)
        likelihood = stable.integer("risk_likelihood", ordinal, 1, 5)
        tables["risks"].append(
            {
                "risk_id": _id("RISK", ordinal),
                "case_id": case_id,
                "risk_type": stable.choice("risk_type", ordinal, risk_types),
                "impact": impact,
                "likelihood": likelihood,
                "derived_score": impact * likelihood,
                "status": "OPEN" if impact * likelihood >= 9 else "MONITOR",
                "owner": f"Synthetic Risk Owner {((ordinal - 1) % 7) + 1:02d}",
            }
        )

        correspondence_id = _id("CORR", ordinal)
        correspondence_evidence_id = f"EV-{ordinal:04d}-CORR"
        asserted_state = "READY" if reported_ready else "IN_PROGRESS"
        sent_date = AS_OF_DATE - timedelta(days=stable.integer("correspondence_age", ordinal, 1, 10))
        tables["evidence"].append(
            {
                "evidence_id": correspondence_evidence_id,
                "case_id": case_id,
                "evidence_type": "CORRESPONDENCE",
                "source_artifact_id": correspondence_id,
                "observed_at": _iso(sent_date),
                "assertion": asserted_state,
                "structured_value": f"asserted_state={asserted_state}",
                "freshness_status": "CURRENT",
            }
        )
        tables["correspondence"].append(
            {
                "correspondence_id": correspondence_id,
                "case_id": case_id,
                "sent_at": _iso(sent_date),
                "sender_role": "CLIENT_TREASURY",
                "recipient_role": "MIGRATION_OWNER",
                "language": "JA" if jurisdiction == "JP" else "EN",
                "subject": "Synthetic migration readiness update",
                "asserted_state": asserted_state,
                "evidence_id": correspondence_evidence_id,
            }
        )

        if ordinal in (10, 14) or ordinal % 20 == 0:
            tables["message_artifacts"].append(
                {
                    "message_artifact_id": _id("MSG", ordinal),
                    "case_id": case_id,
                    "message_family": "PAIN001",
                    "message_version": "pain.001.001.09",
                    "direction": "OUTBOUND",
                    "file_path": f"messages/msg-{ordinal:04d}.xml",
                    "parse_status": "PARSED",
                    "validation_status": "VALID",
                    "business_status": "ACCEPTED" if reported_ready else "PENDING",
                }
            )

        if ordinal % 40 == 0:
            issue_id = _id("ISSUE", ordinal)
            tables["issues"].append(
                {
                    "issue_id": issue_id,
                    "case_id": case_id,
                    "claim": "A fictional coordination item requires human review.",
                    "claim_type": "COORDINATION",
                    "confidence": "MEDIUM",
                    "recommended_action": "Confirm the next synthetic coordination checkpoint.",
                    "human_decision_required": TRUE,
                    "status": "OPEN",
                }
            )
            tables["issue_evidence"].append(
                {
                    "issue_id": issue_id,
                    "evidence_id": correspondence_evidence_id,
                    "relationship": "SUPPORTS",
                    "weight_or_relevance": "PRIMARY",
                }
            )

    tables["audit_events"].append(
        {
            "audit_event_id": "AUDIT-GENERATION-0001",
            "event_timestamp": GENERATION_TIMESTAMP.isoformat(),
            "event_type": "SYNTHETIC_DATA_GENERATED",
            "entity_type": "DATASET",
            "entity_id": "APAC-MIGRATION-SYNTHETIC",
            "actor_type": "SYSTEM",
            "tool": "src.generate_data",
            "input_version": f"seed={seed};clients={client_count};config={CONFIG_VERSION}",
            "output_version": f"canonical-model={DATA_MODEL_VERSION};generator={GENERATOR_VERSION}",
            "review_status": "NOT_REQUIRED_SYNTHETIC",
        }
    )
    return tables


def _set_reported_ready(tables: dict[str, list[dict[str, object]]], ordinal: int) -> None:
    case_id = _case_id(ordinal)
    case = _find(tables["migration_cases"], "case_id", case_id)
    client = _find(tables["clients"], "client_id", _id("CL", ordinal))
    case["reported_readiness"] = TRUE
    case["lifecycle_stage"] = "READINESS"
    client["overall_reported_status"] = "READY"

    test = _find(tables["test_cycles"], "test_id", f"TEST-{ordinal:04d}-UAT")
    test["planned_date"] = _iso(AS_OF_DATE - timedelta(days=12))
    test["executed_date"] = _iso(AS_OF_DATE - timedelta(days=3))
    test["status"] = "PASSED"
    test["defect_count"] = 0
    evidence = _find(tables["evidence"], "evidence_id", f"EV-{ordinal:04d}-UAT")
    evidence["assertion"] = "PASSED"
    evidence["structured_value"] = "defect_count=0"

    uat_milestone = _find(tables["milestones"], "milestone_id", f"MS-{ordinal:04d}-UAT")
    uat_milestone["planned_date"] = _iso(AS_OF_DATE - timedelta(days=12))
    uat_milestone["actual_date"] = _iso(AS_OF_DATE - timedelta(days=3))
    uat_milestone["status"] = "COMPLETED"

    correspondence = _find(tables["correspondence"], "correspondence_id", _id("CORR", ordinal))
    correspondence["asserted_state"] = "READY"
    corr_evidence = _find(tables["evidence"], "evidence_id", f"EV-{ordinal:04d}-CORR")
    corr_evidence["assertion"] = "READY"
    corr_evidence["structured_value"] = "asserted_state=READY"


def _manifest_entry(
    catalog_index: int,
    entity_type: str,
    entity_id: str,
    **details: object,
) -> dict[str, object]:
    entry: dict[str, object] = dict(ANOMALY_CATALOG[catalog_index])
    entry["affected_entity"] = {"entity_type": entity_type, "entity_id": entity_id}
    if details:
        entry["details"] = details
    return entry


def inject_controlled_anomalies(
    tables: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    """Inject each catalogue anomaly into a distinct, predictable case."""

    if len(tables["clients"]) < len(ANOMALY_CATALOG):
        raise ValueError(
            f"anomaly injection requires at least {len(ANOMALY_CATALOG)} clients"
        )

    manifest: list[dict[str, object]] = []

    case = _find(tables["migration_cases"], "case_id", _case_id(1))
    case["treasury_owner"] = ""
    manifest.append(_manifest_entry(0, "MigrationCase", _case_id(1)))

    case = _find(tables["migration_cases"], "case_id", _case_id(2))
    case["it_owner"] = ""
    manifest.append(_manifest_entry(1, "MigrationCase", _case_id(2)))

    milestone_id = "MS-0003-UAT"
    milestone = _find(tables["milestones"], "milestone_id", milestone_id)
    milestone["planned_date"] = _iso(AS_OF_DATE - timedelta(days=10))
    milestone["actual_date"] = ""
    milestone["status"] = "IN_PROGRESS"
    manifest.append(_manifest_entry(2, "Milestone", milestone_id))

    _set_reported_ready(tables, 4)
    failed_test = _find(tables["test_cycles"], "test_id", "TEST-0004-UAT")
    failed_test["status"] = "FAILED"
    failed_test["defect_count"] = 3
    failed_evidence = _find(tables["evidence"], "evidence_id", "EV-0004-UAT")
    failed_evidence["assertion"] = "FAILED"
    failed_evidence["structured_value"] = "defect_count=3"
    manifest.append(
        _manifest_entry(3, "MigrationCase", _case_id(4), related_test_id="TEST-0004-UAT")
    )

    _set_reported_ready(tables, 5)
    missing_document = _find(
        tables["documentation_items"], "document_item_id", "DOC-0005-01"
    )
    missing_document["status"] = "MISSING"
    missing_document["evidence_id"] = ""
    manifest.append(
        _manifest_entry(
            4,
            "MigrationCase",
            _case_id(5),
            related_document_item_id="DOC-0005-01",
        )
    )

    _set_reported_ready(tables, 6)
    blocker_id = "DEP-0006-ANOM"
    tables["dependencies"].append(
        {
            "dependency_id": blocker_id,
            "case_id": _case_id(6),
            "dependency_type": "MANDATORY_CONNECTIVITY",
            "description": "Synthetic unresolved blocker deliberately injected for testing.",
            "owner": "Synthetic Dependency Owner 06",
            "opened_date": _iso(AS_OF_DATE - timedelta(days=25)),
            "due_date": _iso(AS_OF_DATE - timedelta(days=2)),
            "status": "OPEN",
            "severity": "BLOCKER",
            "prerequisite_status": "INCOMPLETE",
        }
    )
    manifest.append(
        _manifest_entry(5, "MigrationCase", _case_id(6), related_dependency_id=blocker_id)
    )

    dependency_id = "DEP-0007-ANOM"
    tables["dependencies"].append(
        {
            "dependency_id": dependency_id,
            "case_id": _case_id(7),
            "dependency_type": "CLIENT_CONFIGURATION",
            "description": "Synthetic dependency closed before its prerequisite completed.",
            "owner": "Synthetic Dependency Owner 07",
            "opened_date": _iso(AS_OF_DATE - timedelta(days=30)),
            "due_date": _iso(AS_OF_DATE - timedelta(days=5)),
            "status": "CLOSED",
            "severity": "HIGH",
            "prerequisite_status": "INCOMPLETE",
        }
    )
    manifest.append(_manifest_entry(6, "Dependency", dependency_id))

    _set_reported_ready(tables, 8)
    stale_date = AS_OF_DATE - timedelta(days=45)
    correspondence = _find(tables["correspondence"], "correspondence_id", "CORR-0008")
    correspondence["sent_at"] = _iso(stale_date)
    evidence = _find(tables["evidence"], "evidence_id", "EV-0008-CORR")
    evidence["observed_at"] = _iso(stale_date)
    evidence["freshness_status"] = "STALE"
    manifest.append(
        _manifest_entry(7, "MigrationCase", _case_id(8), readiness_evidence_id="EV-0008-CORR")
    )

    _set_reported_ready(tables, 9)
    contradictory_evidence_id = "EV-0009-CORR-B"
    contradictory_correspondence_id = "CORR-0009-B"
    current_date = AS_OF_DATE - timedelta(days=2)
    tables["evidence"].append(
        {
            "evidence_id": contradictory_evidence_id,
            "case_id": _case_id(9),
            "evidence_type": "CORRESPONDENCE",
            "source_artifact_id": contradictory_correspondence_id,
            "observed_at": _iso(current_date),
            "assertion": "NOT_READY",
            "structured_value": "asserted_state=NOT_READY",
            "freshness_status": "CURRENT",
        }
    )
    tables["correspondence"].append(
        {
            "correspondence_id": contradictory_correspondence_id,
            "case_id": _case_id(9),
            "sent_at": _iso(current_date),
            "sender_role": "CLIENT_IT",
            "recipient_role": "MIGRATION_OWNER",
            "language": "EN",
            "subject": "Synthetic conflicting readiness update",
            "asserted_state": "NOT_READY",
            "evidence_id": contradictory_evidence_id,
        }
    )
    manifest.append(
        _manifest_entry(
            8,
            "MigrationCase",
            _case_id(9),
            correspondence_ids=["CORR-0009", contradictory_correspondence_id],
        )
    )

    malformed_message = _find(tables["message_artifacts"], "message_artifact_id", "MSG-0010")
    malformed_message["parse_status"] = "ERROR"
    malformed_message["validation_status"] = "INVALID"
    manifest.append(_manifest_entry(9, "MessageArtifact", "MSG-0010"))

    address = _find(tables["client_addresses"], "address_id", "ADDR-0011")
    address["city"] = ""
    address["postal_code"] = ""
    manifest.append(_manifest_entry(10, "ClientAddress", "ADDR-0011"))

    address = _find(tables["client_addresses"], "address_id", "ADDR-0012")
    conflicting_country = "AU" if address["country_code"] != "AU" else "JP"
    address["unstructured_country_code"] = conflicting_country
    address["unstructured_address"] = (
        f"{address['address_line_1']}, {address['city']}, {address['postal_code']}, "
        f"{conflicting_country}"
    )
    manifest.append(_manifest_entry(11, "ClientAddress", "ADDR-0012"))

    profile = _find(tables["payment_profiles"], "payment_profile_id", "PP-0013-01")
    profile["transaction_currency"] = "EUR"
    manifest.append(_manifest_entry(12, "PaymentProfile", "PP-0013-01"))

    _set_reported_ready(tables, 14)
    message = _find(tables["message_artifacts"], "message_artifact_id", "MSG-0014")
    message["business_status"] = "REJECTED"
    manifest.append(
        _manifest_entry(13, "MigrationCase", _case_id(14), related_message_id="MSG-0014")
    )

    client_id = _id("CL", 15)
    client = _find(tables["clients"], "client_id", client_id)
    client_accounts = _rows_for(tables["accounts"], "client_id", client_id)
    if client_accounts:
        first_account = client_accounts[0]
        first_account["account_id"] = "AC-0015-01"
    else:
        first_account = {
            "account_id": "AC-0015-01",
            "client_id": client_id,
            "account_name": f"{client['client_name']} Synthetic Primary Account",
            "booking_location": "Fictional APAC Branch",
            "currency": "USD",
            "in_scope": TRUE,
            "account_reference": "SYN-REF-0015-01",
        }
        tables["accounts"].append(first_account)
    conflict_reference = "SYN-REF-CONFLICT-0015"
    first_account["account_reference"] = conflict_reference
    first_currency = str(first_account["currency"])
    second_currency = "JPY" if first_currency != "JPY" else "SGD"
    conflicting_account_id = "AC-0015-99"
    tables["accounts"].append(
        {
            "account_id": conflicting_account_id,
            "client_id": client_id,
            "account_name": f"{client['client_name']} Synthetic Conflicting Account",
            "booking_location": "Fictional APAC Branch",
            "currency": second_currency,
            "in_scope": TRUE,
            "account_reference": conflict_reference,
        }
    )
    manifest.append(
        _manifest_entry(
            14,
            "Account",
            "AC-0015-01",
            conflicting_entity_ids=["AC-0015-01", conflicting_account_id],
            account_reference=conflict_reference,
        )
    )

    return manifest


def derive_evidence_readiness(tables: dict[str, list[dict[str, object]]]) -> None:
    """Recalculate readiness from canonical evidence, never from the manifest."""

    for case in tables["migration_cases"]:
        case_id = str(case["case_id"])
        reported_ready = case["reported_readiness"] == TRUE
        documents = _rows_for(tables["documentation_items"], "case_id", case_id)
        tests = _rows_for(tables["test_cycles"], "case_id", case_id)
        dependencies = _rows_for(tables["dependencies"], "case_id", case_id)
        correspondence = _rows_for(tables["correspondence"], "case_id", case_id)
        messages = _rows_for(tables["message_artifacts"], "case_id", case_id)

        documents_complete = all(
            item["required"] != TRUE or item["status"] == "COMPLETE" for item in documents
        )
        mandatory_uat_passed = any(
            test["test_type"] == "USER_ACCEPTANCE_TEST"
            and test["mandatory"] == TRUE
            and test["status"] == "PASSED"
            for test in tests
        )
        no_open_blocker = not any(
            item["status"] == "OPEN" and item["severity"] == "BLOCKER"
            for item in dependencies
        )
        current_cutoff = AS_OF_DATE - timedelta(days=EVIDENCE_FRESHNESS_DAYS)
        current_assertions = {
            str(item["asserted_state"])
            for item in correspondence
            if date.fromisoformat(str(item["sent_at"])) >= current_cutoff
        }
        current_ready_evidence = "READY" in current_assertions
        no_current_contradiction = not (
            "READY" in current_assertions and "NOT_READY" in current_assertions
        )
        no_rejected_message = not any(
            message["business_status"] == "REJECTED" for message in messages
        )

        case["evidence_readiness"] = (
            TRUE
            if reported_ready
            and documents_complete
            and mandatory_uat_passed
            and no_open_blocker
            and current_ready_evidence
            and no_current_contradiction
            and no_rejected_message
            else FALSE
        )


def generate_dataset(
    *, seed: int = DEFAULT_SEED, client_count: int = DEFAULT_CLIENT_COUNT, anomalies: bool = True
) -> GeneratedDataset:
    """Create the in-memory canonical dataset and validate all relations."""

    tables = build_base_dataset(seed, client_count)
    manifest = inject_controlled_anomalies(tables) if anomalies else []
    derive_evidence_readiness(tables)
    validate_relations(tables)
    return GeneratedDataset(tables, manifest, seed, client_count)


def _serialize(value: object) -> object:
    if value is None:
        return ""
    return value


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _serialize(row[column]) for column in columns})


def _write_message_files(output_dir: Path, rows: Sequence[Mapping[str, object]]) -> None:
    message_dir = output_dir / "messages"
    message_dir.mkdir(parents=True, exist_ok=True)
    for stale_file in message_dir.glob("*.xml"):
        stale_file.unlink()

    for row in rows:
        path = output_dir / str(row["file_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        if row["parse_status"] == "ERROR":
            content = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<Document xmlns="urn:synthetic:payment:migration">\n'
                "  <Synthetic>true</Synthetic>\n"
                f"  <MessageId>{row['message_artifact_id']}</MessageId>\n"
                "  <PaymentStatus>REJECTED\n"
            )
        else:
            content = (
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<Document xmlns="urn:synthetic:payment:migration">\n'
                "  <Synthetic>true</Synthetic>\n"
                f"  <MessageId>{row['message_artifact_id']}</MessageId>\n"
                f"  <CaseId>{row['case_id']}</CaseId>\n"
                f"  <PaymentStatus>{row['business_status']}</PaymentStatus>\n"
                "</Document>\n"
            )
        path.write_text(content, encoding="utf-8", newline="\n")


def write_dataset(dataset: GeneratedDataset, output_dir: Path) -> None:
    """Write normalized CSVs, message samples, and the test-only manifest."""

    output_dir.mkdir(parents=True, exist_ok=True)
    for table_name in TABLE_ORDER:
        _write_csv(
            output_dir / f"{table_name}.csv",
            TABLE_SPECS[table_name].columns,
            dataset.tables[table_name],
        )
    _write_message_files(output_dir, dataset.tables["message_artifacts"])

    test_only_dir = output_dir / "_test_only"
    test_only_dir.mkdir(parents=True, exist_ok=True)
    manifest_payload = {
        "test_only": True,
        "classification": "SYNTHETIC_PUBLIC_TEST_ONLY",
        "purpose": (
            "Expected injected defects for automated tests only; operational "
            "readiness logic must not read this file."
        ),
        "generator_version": GENERATOR_VERSION,
        "data_model_version": DATA_MODEL_VERSION,
        "seed": dataset.seed,
        "client_count": dataset.client_count,
        "as_of_date": _iso(AS_OF_DATE),
        "anomalies": dataset.anomaly_manifest,
    }
    (test_only_dir / "anomaly_manifest.json").write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def generate_to_directory(
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
    client_count: int = DEFAULT_CLIENT_COUNT,
    anomalies: bool = True,
) -> GeneratedDataset:
    dataset = generate_dataset(seed=seed, client_count=client_count, anomalies=anomalies)
    write_dataset(dataset, output_dir)
    return dataset


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--clients", type=int, default=DEFAULT_CLIENT_COUNT)
    parser.add_argument("--output", type=Path, default=Path("data/generated"))
    parser.add_argument(
        "--no-anomalies",
        action="store_true",
        help="Generate clean base data without controlled anomaly injection.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    dataset = generate_to_directory(
        args.output,
        seed=args.seed,
        client_count=args.clients,
        anomalies=not args.no_anomalies,
    )
    print(
        f"Generated {dataset.client_count} synthetic clients, "
        f"{len(dataset.anomaly_manifest)} controlled anomalies, and "
        f"{len(TABLE_ORDER)} normalized CSV tables in {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
