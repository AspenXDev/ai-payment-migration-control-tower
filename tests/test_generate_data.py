from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from xml.etree import ElementTree

import pytest

from src.data_model import TABLE_ORDER, TABLE_SPECS
from src.generate_data import (
    ALLOWED_PROFILE_CURRENCIES,
    ANOMALY_CATALOG,
    AS_OF_DATE,
    DEFAULT_CLIENT_COUNT,
    DEFAULT_SEED,
    EVIDENCE_FRESHNESS_DAYS,
    generate_to_directory,
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_tables(output_dir: Path) -> dict[str, list[dict[str, str]]]:
    return {name: _read_csv(output_dir / f"{name}.csv") for name in TABLE_ORDER}


def _by(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    }


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]]:
    output_dir = tmp_path_factory.mktemp("generated")
    generate_to_directory(output_dir)
    tables = _load_tables(output_dir)
    manifest = json.loads((output_dir / "_test_only" / "anomaly_manifest.json").read_text(encoding="utf-8"))
    return output_dir, tables, manifest


def test_default_generation_writes_all_normalized_tables(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    output_dir, tables, _ = generated

    assert len(tables["clients"]) == DEFAULT_CLIENT_COUNT
    assert len(tables["migration_cases"]) == DEFAULT_CLIENT_COUNT
    assert {path.name for path in output_dir.glob("*.csv")} == {
        f"{table_name}.csv" for table_name in TABLE_ORDER
    }
    for table_name, spec in TABLE_SPECS.items():
        with (output_dir / f"{table_name}.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            assert tuple(next(reader)) == spec.columns


def test_generation_is_byte_deterministic_for_a_fixed_seed(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    different = tmp_path / "different"

    generate_to_directory(first, seed=DEFAULT_SEED)
    generate_to_directory(second, seed=DEFAULT_SEED)
    generate_to_directory(different, seed=DEFAULT_SEED + 1)

    assert _tree_hashes(first) == _tree_hashes(second)
    assert _tree_hashes(first) != _tree_hashes(different)


def test_primary_keys_are_unique_and_foreign_keys_resolve(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    _, tables, _ = generated
    indexes: dict[str, set[tuple[str, ...]]] = {}

    for table_name, spec in TABLE_SPECS.items():
        keys = [tuple(row[column] for column in spec.primary_key) for row in tables[table_name]]
        assert all(all(value for value in key) for key in keys), table_name
        assert len(keys) == len(set(keys)), table_name
        indexes[table_name] = set(keys)

    for table_name, spec in TABLE_SPECS.items():
        for row in tables[table_name]:
            for foreign_key in spec.foreign_keys:
                value = tuple(row[column] for column in foreign_key.columns)
                if foreign_key.optional and not any(value):
                    continue
                assert all(value), (table_name, foreign_key.columns, row)
                assert value in indexes[foreign_key.referenced_table], (
                    table_name,
                    value,
                    foreign_key.referenced_table,
                )


def test_required_cardinalities_and_issue_lineage(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    _, tables, _ = generated
    client_ids = {row["client_id"] for row in tables["clients"]}
    case_client_ids = [row["client_id"] for row in tables["migration_cases"]]
    profile_client_ids = {row["client_id"] for row in tables["payment_profiles"]}

    assert len(case_client_ids) == len(set(case_client_ids)) == DEFAULT_CLIENT_COUNT
    assert set(case_client_ids) == client_ids
    assert profile_client_ids == client_ids

    evidence = _by(tables["evidence"], "evidence_id")
    links_by_issue: dict[str, list[dict[str, str]]] = defaultdict(list)
    for link in tables["issue_evidence"]:
        links_by_issue[link["issue_id"]].append(link)
    assert tables["issues"]
    for issue in tables["issues"]:
        links = links_by_issue[issue["issue_id"]]
        assert links
        assert all(evidence[link["evidence_id"]]["source_artifact_id"] for link in links)


def test_manifest_is_explicitly_test_only_and_covers_the_catalogue(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    output_dir, _, manifest = generated
    anomalies = manifest["anomalies"]

    assert output_dir.joinpath("_test_only", "anomaly_manifest.json").is_file()
    assert manifest["test_only"] is True
    assert manifest["classification"] == "SYNTHETIC_PUBLIC_TEST_ONLY"
    assert "must not read this file" in str(manifest["purpose"])
    assert manifest["seed"] == DEFAULT_SEED
    assert manifest["client_count"] == DEFAULT_CLIENT_COUNT
    assert len(anomalies) == len(ANOMALY_CATALOG) == 15
    assert {item["anomaly_type"] for item in anomalies} == {
        item["anomaly_type"] for item in ANOMALY_CATALOG
    }
    for item in anomalies:
        assert item["anomaly_id"]
        assert item["expected_validator"]
        assert item["expected_severity"] in {"MEDIUM", "HIGH", "CRITICAL"}
        assert item["affected_entity"]["entity_type"]
        assert item["affected_entity"]["entity_id"]


def _detect_anomalies(
    output_dir: Path, tables: dict[str, list[dict[str, str]]]
) -> dict[str, set[str]]:
    cases = _by(tables["migration_cases"], "case_id")
    clients = _by(tables["clients"], "client_id")
    detected: dict[str, set[str]] = {}

    detected["missing_treasury_owner"] = {
        row["case_id"] for row in tables["migration_cases"] if not row["treasury_owner"]
    }
    detected["missing_it_owner"] = {
        row["case_id"] for row in tables["migration_cases"] if not row["it_owner"]
    }
    detected["overdue_milestone"] = {
        row["milestone_id"]
        for row in tables["milestones"]
        if date.fromisoformat(row["planned_date"]) < AS_OF_DATE
        and not row["actual_date"]
        and row["status"] not in {"COMPLETED", "CANCELLED"}
    }

    failed_ready_cases: set[str] = set()
    for test in tables["test_cycles"]:
        case = cases[test["case_id"]]
        if (
            case["reported_readiness"] == "true"
            and test["mandatory"] == "true"
            and test["test_type"] == "USER_ACCEPTANCE_TEST"
            and test["status"] == "FAILED"
        ):
            failed_ready_cases.add(test["case_id"])
    detected["failed_mandatory_uat_marked_ready"] = failed_ready_cases

    missing_doc_cases: set[str] = set()
    for document in tables["documentation_items"]:
        case = cases[document["case_id"]]
        if (
            case["reported_readiness"] == "true"
            and document["required"] == "true"
            and document["status"] != "COMPLETE"
        ):
            missing_doc_cases.add(document["case_id"])
    detected["missing_mandatory_documentation_marked_ready"] = missing_doc_cases

    detected["unresolved_blocker_marked_ready"] = {
        dependency["case_id"]
        for dependency in tables["dependencies"]
        if cases[dependency["case_id"]]["reported_readiness"] == "true"
        and dependency["status"] == "OPEN"
        and dependency["severity"] == "BLOCKER"
    }
    detected["closed_dependency_with_incomplete_prerequisite"] = {
        dependency["dependency_id"]
        for dependency in tables["dependencies"]
        if dependency["status"] == "CLOSED"
        and dependency["prerequisite_status"] != "COMPLETE"
    }

    current_cutoff = AS_OF_DATE - timedelta(days=EVIDENCE_FRESHNESS_DAYS)
    readiness_correspondence: dict[str, list[dict[str, str]]] = defaultdict(list)
    current_states: dict[str, set[str]] = defaultdict(set)
    for item in tables["correspondence"]:
        sent_at = date.fromisoformat(item["sent_at"])
        if item["asserted_state"] == "READY":
            readiness_correspondence[item["case_id"]].append(item)
        if sent_at >= current_cutoff:
            current_states[item["case_id"]].add(item["asserted_state"])
    detected["stale_correspondence_as_sole_readiness_evidence"] = {
        case_id
        for case_id, rows in readiness_correspondence.items()
        if cases[case_id]["reported_readiness"] == "true"
        and rows
        and all(date.fromisoformat(row["sent_at"]) < current_cutoff for row in rows)
    }
    detected["contradictory_current_correspondence"] = {
        case_id for case_id, states in current_states.items() if {"READY", "NOT_READY"} <= states
    }

    malformed_messages: set[str] = set()
    for message in tables["message_artifacts"]:
        try:
            ElementTree.parse(output_dir / message["file_path"])
        except ElementTree.ParseError:
            malformed_messages.add(message["message_artifact_id"])
    detected["malformed_xml"] = malformed_messages

    detected["incomplete_postal_address"] = {
        row["address_id"]
        for row in tables["client_addresses"]
        if not all(row[field] for field in ("address_line_1", "city", "postal_code", "country_code"))
    }
    detected["structured_unstructured_address_conflict"] = {
        row["address_id"]
        for row in tables["client_addresses"]
        if row["country_code"] != row["unstructured_country_code"]
    }
    detected["unsupported_currency_payment_profile_combination"] = {
        row["payment_profile_id"]
        for row in tables["payment_profiles"]
        if row["transaction_currency"]
        not in ALLOWED_PROFILE_CURRENCIES[clients[row["client_id"]]["jurisdiction"]]
    }
    detected["message_status_contradicts_case_status"] = {
        row["case_id"]
        for row in tables["message_artifacts"]
        if cases[row["case_id"]]["reported_readiness"] == "true"
        and row["business_status"] == "REJECTED"
    }

    by_reference: dict[str, list[dict[str, str]]] = defaultdict(list)
    for account in tables["accounts"]:
        by_reference[account["account_reference"]].append(account)
    detected["duplicate_or_conflicting_account_reference_data"] = {
        reference
        for reference, accounts in by_reference.items()
        if len({account["currency"] for account in accounts}) > 1
    }
    return detected


def test_every_intended_anomaly_is_independently_detectable_and_isolated(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    output_dir, tables, manifest = generated
    detected = _detect_anomalies(output_dir, tables)
    manifest_by_type = {item["anomaly_type"]: item for item in manifest["anomalies"]}

    for anomaly_type, entity_ids in detected.items():
        assert entity_ids, anomaly_type
        if anomaly_type == "duplicate_or_conflicting_account_reference_data":
            entry = manifest_by_type[anomaly_type]
            assert entity_ids == {entry["details"]["account_reference"]}
            continue
        expected_id = manifest_by_type[anomaly_type]["affected_entity"]["entity_id"]
        assert entity_ids == {expected_id}, anomaly_type


def test_reported_readiness_is_distinct_from_evidence_readiness(
    generated: tuple[Path, dict[str, list[dict[str, str]]], dict[str, object]],
) -> None:
    _, tables, _ = generated
    cases = _by(tables["migration_cases"], "case_id")

    assert cases["MC-0004"]["reported_readiness"] == "true"
    assert cases["MC-0004"]["evidence_readiness"] == "false"
    assert cases["MC-0020"]["reported_readiness"] == "true"
    assert cases["MC-0020"]["evidence_readiness"] == "true"


def test_clean_generation_can_disable_anomaly_injection(tmp_path: Path) -> None:
    output_dir = tmp_path / "clean"
    dataset = generate_to_directory(output_dir, client_count=20, anomalies=False)
    manifest = json.loads((output_dir / "_test_only" / "anomaly_manifest.json").read_text(encoding="utf-8"))

    assert dataset.anomaly_manifest == []
    assert manifest["anomalies"] == []
    assert all(row["treasury_owner"] for row in dataset.tables["migration_cases"])
    assert all(row["it_owner"] for row in dataset.tables["migration_cases"])


def test_reusing_output_directory_removes_stale_message_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "reused"
    generate_to_directory(output_dir, client_count=200)
    smaller = generate_to_directory(output_dir, client_count=20, anomalies=False)

    expected_paths = {
        row["file_path"] for row in smaller.tables["message_artifacts"]
    }
    actual_paths = {
        path.relative_to(output_dir).as_posix()
        for path in (output_dir / "messages").glob("*.xml")
    }
    assert actual_paths == expected_paths
