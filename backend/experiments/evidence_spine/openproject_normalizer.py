from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_snapshot(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_openproject(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Map the discovery snapshot into the frozen Evidence Spine fields.

    This adapter is intentionally fixture-level. It proves semantic mapping
    from source-shaped records without claiming to be a production connector.
    """
    requirements: dict[str, Any] = {}
    risks: dict[str, Any] = {}
    changes: dict[str, Any] = {}

    for item in snapshot["work_packages"]:
        fields = item["customFields"]
        canonical_id = fields["bgstm_id"]
        if item["type"] == "Requirement":
            requirements[canonical_id] = {
                "modified_at": item["updatedAt"],
                "risk_ids": fields["risk_ids"],
            }
        elif item["type"] == "Risk":
            risks[canonical_id] = {
                "severity": fields["severity"],
                "obligation_ids": fields["obligation_ids"],
            }
        elif item["type"] == "Change":
            changes[canonical_id] = {
                "affected_requirement": fields["affected_requirement"],
                "occurred_at": item["updatedAt"],
                "introduced_sha": fields["introduced_sha"],
            }

    traceability = [
        {
            "requirement_id": relation["from"]["bgstm_id"],
            "test_case_id": relation["to"]["bgstm_id"],
            "confirmed_at": relation["createdAt"],
        }
        for relation in snapshot["relations"]
        if relation["type"] == "verifies"
    ]

    return {
        "requirements": requirements,
        "risks": risks,
        "changes": changes,
        "traceability": traceability,
    }


def apply_openproject_snapshot(fixture: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    """Replace OpenProject-owned canonical sections while preserving other sources."""
    normalized = normalize_openproject(snapshot)
    result = deepcopy(fixture)
    for key, value in normalized.items():
        result[key] = value
    result["sources"]["requirements"] = snapshot["source_system"]
    return result
