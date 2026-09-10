from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_fixture(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _finding(
    finding_id: str,
    claim: str,
    reason: str,
    obligation_ids: list[str],
    evidence_refs: list[str],
    source_systems: list[str],
    source_object_ids: list[str],
    human_review_required: bool = False,
) -> dict[str, Any]:
    return {
        "finding_id": finding_id,
        "claim": claim,
        "status": "open",
        "reason": reason,
        "confidence": 1.0,
        "quality_obligation_ids": obligation_ids,
        "evidence_references": evidence_refs,
        "source_systems": source_systems,
        "source_object_ids": source_object_ids,
        "source_revisions_or_timestamps": evidence_refs,
        "human_review_required": human_review_required,
    }


def evaluate(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    release = fixture["release"]
    runs = fixture["runs"]
    environments = fixture["environments"]
    obligations = fixture["obligations"]

    # F-001: passing TC-005 is not sufficient when QO-003 requires explicit
    # proof of the no-order-created postcondition.
    qo3 = obligations["QO-003"]
    qualifying_tc5 = [
        run
        for run in runs
        if run["sha"] == release["candidate_sha"]
        and environments[run["environment_id"]]["definition_id"] == qo3["required_environment"]
        and run["results"].get("TC-005") == "pass"
    ]
    if qualifying_tc5 and not any(
        qo3["required_artifact"] in run.get("artifacts", {}).get("TC-005", []) for run in qualifying_tc5
    ):
        findings.append(
            _finding(
                "F-001",
                "QO-003 is insufficiently supported.",
                "TC-005 passed, but no qualifying evidence proves that no order was created.",
                ["QO-003"],
                [f"{run['id']}@{run['executed_at']}" for run in qualifying_tc5],
                [fixture["sources"]["executions"]],
                ["TC-005", *[run["id"] for run in qualifying_tc5]],
            )
        )

    # F-002: record the invalidation relationship even though RUN-003 later
    # restores current support for QO-004.
    change = fixture["changes"]["CHG-002"]
    stale_runs = [
        run
        for run in runs
        if run["results"].get("TC-007") == "pass" and _dt(run["executed_at"]) < _dt(change["occurred_at"])
    ]
    if stale_runs:
        findings.append(
            _finding(
                "F-002",
                "Historical TC-007 evidence was invalidated by CHG-002.",
                (
                    "A pricing-affecting change occurred after the historical execution; "
                    "that execution cannot by itself support QO-004."
                ),
                ["QO-004"],
                [f"{run['id']}@{run['executed_at']}" for run in stale_runs] + [f"CHG-002@{change['occurred_at']}"],
                [fixture["sources"]["requirements"], fixture["sources"]["executions"]],
                ["CHG-002", "TC-007", *[run["id"] for run in stale_runs]],
            )
        )

    # F-003: candidate PASS results on ENV-002 are explicitly non-qualifying.
    qo2 = obligations["QO-002"]
    mismatched = [
        run
        for run in runs
        if run["sha"] == release["candidate_sha"]
        and (run["results"].get("TC-003") == "pass" or run["results"].get("TC-004") == "pass")
        and environments[run["environment_id"]]["definition_id"] != qo2["required_environment"]
    ]
    if mismatched:
        findings.append(
            _finding(
                "F-003",
                "RUN-002 does not qualify as supported-browser release evidence.",
                "Candidate browser tests passed on an environment that does not satisfy ENVDEF-001.",
                ["QO-002"],
                [f"{run['id']}:{run['environment_id']}" for run in mismatched],
                [fixture["sources"]["executions"]],
                ["ENV-002", *[run["id"] for run in mismatched]],
            )
        )

    # F-004: closed/fixed BUG-001 lacks post-fix verification on a build
    # containing its fix SHA.
    bug = fixture["defects"]["BUG-001"]
    verification = [
        run
        for run in runs
        if run["results"].get(bug["verification_test_case_id"]) == "pass" and run["sha"] == bug["fix_sha"]
    ]
    if bug["status"] == "closed_fixed" and not verification:
        findings.append(
            _finding(
                "F-004",
                "BUG-001 lacks qualifying post-fix verification.",
                "No passing verification execution is recorded on the defect fix SHA.",
                ["QO-005"],
                [f"BUG-001:fix_sha={bug['fix_sha']}"],
                [fixture["sources"]["defects"], fixture["sources"]["executions"]],
                ["BUG-001", bug["verification_test_case_id"]],
            )
        )

    # F-005: TC-011 is explicitly outside all intent relationships and controls.
    mapped = {test_id for obligation in obligations.values() for test_id in obligation.get("test_case_ids", [])}
    executed = {test_id for run in runs for test_id in run["results"]}
    secondary = set(fixture["secondary_test_cases"])
    if "TC-011" in executed and "TC-011" not in mapped and "TC-011" not in secondary:
        findings.append(
            _finding(
                "F-005",
                "TC-011 is semantically orphaned.",
                (
                    "The executed test has no declared quality-intent relationship "
                    "and is not designated secondary evidence."
                ),
                [],
                [run["id"] for run in runs if "TC-011" in run["results"]],
                [fixture["sources"]["executions"]],
                ["TC-011"],
            )
        )

    # F-006: REQ-001 traceability was confirmed before CHG-001 changed the
    # requirement-relevant authentication behavior.
    chg1 = fixture["changes"]["CHG-001"]
    outdated = [
        relation
        for relation in fixture["traceability"]
        if relation["requirement_id"] == "REQ-001" and _dt(relation["confirmed_at"]) < _dt(chg1["occurred_at"])
    ]
    if outdated:
        findings.append(
            _finding(
                "F-006",
                "REQ-001 traceability requires revalidation.",
                "Authentication behavior changed after the validating relationships were last confirmed.",
                ["QO-001"],
                [f"{item['requirement_id']}->{item['test_case_id']}@{item['confirmed_at']}" for item in outdated]
                + [f"CHG-001@{chg1['occurred_at']}"],
                [fixture["sources"]["requirements"]],
                ["REQ-001", "CHG-001", *[item["test_case_id"] for item in outdated]],
            )
        )

    # F-007: contradictory qualifying observations remain unresolved.
    tc4_observations = []
    for run in runs:
        outcome = run["results"].get("TC-004")
        if (
            outcome in {"pass", "fail"}
            and run["sha"] == release["candidate_sha"]
            and environments[run["environment_id"]]["definition_id"] == "ENVDEF-001"
        ):
            tc4_observations.append((run, outcome))
    if {outcome for _, outcome in tc4_observations} == {"pass", "fail"}:
        findings.append(
            _finding(
                "F-007",
                "Qualifying TC-004 evidence is contradictory.",
                (
                    "Candidate observations on the approved environment contain both PASS and FAIL; "
                    "no reconciliation fact exists."
                ),
                ["QO-002", "QO-007"],
                [f"{run['id']}:{outcome}@{run['executed_at']}" for run, outcome in tc4_observations],
                [fixture["sources"]["executions"]],
                ["TC-004", *[run["id"] for run, _ in tc4_observations]],
                human_review_required=True,
            )
        )

    return findings


def evaluate_file(path: str | Path) -> list[dict[str, Any]]:
    return evaluate(load_fixture(path))
