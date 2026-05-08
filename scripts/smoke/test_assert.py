from __future__ import annotations

import sys
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

_MODULE_PATH = Path(__file__).with_name("assert.py")
_SPEC = spec_from_file_location("smoke_assert", _MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load scripts/smoke/assert.py")
_MODULE = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
validate_snapshot = _MODULE.validate_snapshot


PROJECT_ID = "00000000-0000-0000-0000-000000000111"
TOKEN_ID = "00000000-0000-0000-0000-000000000222"
SESSION_ID = "00000000-0000-0000-0000-000000000333"
FAILED_CASE_ID = "00000000-0000-0000-0000-000000000444"


def _snapshot() -> dict[str, Any]:
    return {
        "sessions": [
            {
                "id": SESSION_ID,
                "project_id": PROJECT_ID,
                "status": "failed",
                "runner": "@bgstm/playwright-core@0.1.0",
            }
        ],
        "case_results": [
            {
                "id": "case-pass",
                "session_id": SESSION_ID,
                "external_id": "suite > passes — homepage loads",
                "outcome": "passed",
                "requirement_ids": ["req-1"],
            },
            {
                "id": FAILED_CASE_ID,
                "session_id": SESSION_ID,
                "external_id": "suite > fails — intentional assertion failure to exercise artifact upload",
                "outcome": "failed",
                "requirement_ids": [],
            },
            {
                "id": "case-skip",
                "session_id": SESSION_ID,
                "external_id": "suite > skipped — exercises skip path",
                "outcome": "skipped",
                "requirement_ids": [],
            },
        ],
        "artifacts": [
            {
                "id": "art-1",
                "case_result_id": FAILED_CASE_ID,
                "kind": "screenshot",
                "filename": "failure-state.png",
                "content_type": "image/png",
                "size_bytes": 20480,
            }
        ],
        "audit_entries": [
            {"actor_kind": "runner_token", "actor_token_id": TOKEN_ID, "action": "external_results.session.start"},
            {"actor_kind": "runner_token", "actor_token_id": TOKEN_ID, "action": "external_results.case.create"},
            {"actor_kind": "runner_token", "actor_token_id": TOKEN_ID, "action": "external_results.case.create"},
            {"actor_kind": "runner_token", "actor_token_id": TOKEN_ID, "action": "external_results.case.create"},
            {"actor_kind": "runner_token", "actor_token_id": TOKEN_ID, "action": "external_results.session.finish"},
        ],
    }


def test_validate_snapshot_passes_for_expected_payload() -> None:
    checks = validate_snapshot(_snapshot(), PROJECT_ID, TOKEN_ID)
    assert all(check.passed for check in checks)


def test_validate_snapshot_fails_for_wrong_session_count() -> None:
    payload = _snapshot()
    payload["sessions"].append(deepcopy(payload["sessions"][0]))
    checks = validate_snapshot(payload, PROJECT_ID, TOKEN_ID)
    assert any((check.name == "single session for project" and not check.passed) for check in checks)


def test_validate_snapshot_fails_for_wrong_case_outcome() -> None:
    payload = _snapshot()
    payload["case_results"][2]["outcome"] = "passed"
    checks = validate_snapshot(payload, PROJECT_ID, TOKEN_ID)
    assert any((check.name == "case outcomes 1/1/1" and not check.passed) for check in checks)


def test_validate_snapshot_fails_for_missing_failed_artifact() -> None:
    payload = _snapshot()
    payload["artifacts"] = []
    checks = validate_snapshot(payload, PROJECT_ID, TOKEN_ID)
    assert any((check.name == "failed case has artifact" and not check.passed) for check in checks)
    assert any((check.name == "artifact has filename" and not check.passed) for check in checks)


def test_validate_snapshot_fails_for_missing_audit_action() -> None:
    payload = _snapshot()
    payload["audit_entries"] = payload["audit_entries"][:-1]
    checks = validate_snapshot(payload, PROJECT_ID, TOKEN_ID)
    assert any((check.name == "audit action counts" and not check.passed) for check in checks)
