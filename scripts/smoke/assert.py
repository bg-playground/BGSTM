from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def validate_snapshot(snapshot: dict[str, Any], project_id: str, actor_token_id: str) -> list[Check]:
    checks: list[Check] = []

    sessions = [s for s in snapshot["sessions"] if s.get("project_id") == project_id]
    checks.append(Check("single session for project", len(sessions) == 1, f"found={len(sessions)}"))

    session = sessions[0] if sessions else {}
    checks.append(Check("session status failed", session.get("status") == "failed", f"status={session.get('status')}"))
    checks.append(
        Check(
            "session runner prefix",
            str(session.get("runner", "")).startswith("@bgstm/playwright-core@"),
            f"runner={session.get('runner')}",
        )
    )

    session_id = session.get("id")
    case_rows = [c for c in snapshot["case_results"] if c.get("session_id") == session_id]
    checks.append(Check("three case results", len(case_rows) == 3, f"found={len(case_rows)}"))

    outcome_counts = Counter(c.get("outcome") for c in case_rows)
    checks.append(
        Check(
            "case outcomes 1/1/1",
            outcome_counts == Counter({"passed": 1, "failed": 1, "skipped": 1}),
            f"counts={dict(outcome_counts)}",
        )
    )

    def _find_case(suffix: str) -> dict[str, Any] | None:
        for case in case_rows:
            if str(case.get("external_id", "")).endswith(suffix):
                return case
        return None

    passed_case = _find_case("passes — homepage loads")
    failed_case = _find_case("fails — intentional assertion failure to exercise artifact upload")
    skipped_case = _find_case("skipped — exercises skip path")

    checks.append(Check("passed case exists", passed_case is not None, "expected suffix=passes — homepage loads"))
    checks.append(
        Check(
            "passed case has requirement links",
            bool((passed_case or {}).get("requirement_ids")),
            f"requirement_ids={(passed_case or {}).get('requirement_ids', [])}",
        )
    )
    checks.append(
        Check(
            "failed case exists",
            failed_case is not None,
            "expected suffix=fails — intentional assertion failure to exercise artifact upload",
        )
    )
    checks.append(Check("skipped case exists", skipped_case is not None, "expected suffix=skipped — exercises skip path"))

    failed_case_id = (failed_case or {}).get("id")
    failed_case_artifacts = [a for a in snapshot["artifacts"] if a.get("case_result_id") == failed_case_id]
    checks.append(
        Check("failed case has artifact", len(failed_case_artifacts) >= 1, f"artifact_count={len(failed_case_artifacts)}")
    )
    checks.append(
        Check(
            "failed case has screenshot artifact",
            any(a.get("kind") == "screenshot" for a in failed_case_artifacts),
            f"kinds={[a.get('kind') for a in failed_case_artifacts]}",
        )
    )

    audit_entries = [
        entry
        for entry in snapshot["audit_entries"]
        if entry.get("actor_kind") == "runner_token" and entry.get("actor_token_id") == actor_token_id
    ]
    action_counts = Counter(entry.get("action") for entry in audit_entries)
    checks.append(Check("audit total >= 5", len(audit_entries) >= 5, f"total={len(audit_entries)}"))
    checks.append(
        Check(
            "audit action counts",
            action_counts.get("external_results.session.start", 0) == 1
            and action_counts.get("external_results.case.create", 0) == 3
            and action_counts.get("external_results.session.finish", 0) == 1,
            f"counts={dict(action_counts)}",
        )
    )

    return checks


def _fetch_snapshot(api_url: str, admin_jwt: str, project_id: str, actor_token_id: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {admin_jwt}"}

    with httpx.Client(base_url=api_url, headers=headers, timeout=30.0) as client:
        def _get_json(path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
            response = client.get(path, params=params)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(f"Request failed for {path}: {exc.response.status_code} {exc.response.text}") from exc
            payload = response.json()
            if not isinstance(payload, dict):
                raise RuntimeError(f"Unexpected response shape from {path}: {type(payload).__name__}")
            return payload

        audit_entries = _get_json(
            "/api/v1/audit-log",
            params={"actor_kind": "runner_token", "actor_token_id": actor_token_id, "limit": 500},
        ).get("entries", [])

        session_ids = {
            entry.get("resource_id")
            for entry in audit_entries
            if entry.get("action") == "external_results.session.start"
            and (entry.get("details") or {}).get("project_id") == project_id
        }

        sessions: list[dict[str, Any]] = []
        for session_id in sorted(str(sid) for sid in session_ids if sid):
            sessions.append(_get_json(f"/api/v1/external-results/session/{session_id}"))

        case_ids = {
            entry.get("resource_id")
            for entry in audit_entries
            if entry.get("action") == "external_results.case.create"
        }

        case_results: list[dict[str, Any]] = []
        for case_id in sorted(str(cid) for cid in case_ids if cid):
            case_results.append(_get_json(f"/api/v1/external-results/case/{case_id}"))

        artifacts: list[dict[str, Any]] = []
        for entry in audit_entries:
            if entry.get("action") != "external_results.artifact.upload":
                continue
            details = entry.get("details") or {}
            artifacts.append(
                {
                    "id": entry.get("resource_id"),
                    "case_result_id": details.get("case_result_id"),
                    "kind": details.get("kind"),
                }
            )

    return {
        "sessions": sessions,
        "case_results": case_results,
        "artifacts": artifacts,
        "audit_entries": audit_entries,
    }


def _print_results(checks: list[Check]) -> None:
    print("| Check | Result | Detail |")
    print("|---|---|---|")
    for check in checks:
        icon = "✅" if check.passed else "❌"
        print(f"| {check.name} | {icon} | {check.detail} |")


def main() -> None:
    api_url = os.environ["BGSTM_API_URL"]
    admin_jwt = os.environ["BGSTM_ADMIN_JWT"]
    project_id = os.environ["BGSTM_PROJECT_ID"]
    actor_token_id = os.environ["BGSTM_RUNNER_TOKEN_ID"]

    snapshot = _fetch_snapshot(api_url, admin_jwt, project_id, actor_token_id)
    checks = validate_snapshot(snapshot, project_id, actor_token_id)
    _print_results(checks)

    failed = [check for check in checks if not check.passed]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
