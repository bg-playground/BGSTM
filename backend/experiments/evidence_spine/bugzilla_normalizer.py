from __future__ import annotations

from copy import deepcopy
from typing import Any


def _canonical_status(bug: dict[str, Any]) -> str:
    if bug["status"].upper() == "CLOSED" and bug.get("resolution", "").upper() == "FIXED":
        return "closed_fixed"
    return "open"


def normalize_bugzilla(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map a Bugzilla-shaped discovery snapshot into frozen defect semantics."""
    defects: dict[str, dict[str, Any]] = {}
    for bug in snapshot["bugs"]:
        aliases = bug.get("alias", [])
        if len(aliases) != 1:
            raise ValueError(f"Bugzilla bug {bug['id']} must have exactly one BGSTM alias")
        defect_id = aliases[0]
        defects[defect_id] = {
            "status": _canonical_status(bug),
            "fix_sha": bug.get("cf_fix_sha"),
            "verification_test_case_id": bug["cf_verification_test_case"],
        }
    return defects


def apply_bugzilla_snapshot(fixture: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    """Replace Bugzilla-owned defect facts while preserving other source systems."""
    result = deepcopy(fixture)
    result["defects"] = normalize_bugzilla(snapshot)
    result["sources"]["defects"] = snapshot["source_system"]
    return result
