from __future__ import annotations

from copy import deepcopy
from typing import Any


def normalize_github_actions(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Map GitHub Actions-shaped workflow evidence into build provenance."""
    builds: dict[str, Any] = {}
    execution_builds: dict[str, str] = {}
    release: dict[str, Any] | None = None

    for workflow in snapshot["workflow_runs"]:
        build_id = f"GHA-{workflow['id']}"
        builds[build_id] = {
            "sha": workflow["head_sha"],
            "workflow_name": workflow["name"],
            "status": workflow["status"],
            "conclusion": workflow["conclusion"],
            "observed_at": workflow["updated_at"],
        }
        for artifact in workflow.get("artifacts", []):
            execution_builds[artifact["execution_run_id"]] = build_id

        release_data = workflow.get("release")
        if release_data and release_data.get("candidate"):
            release = {
                "id": release_data["id"],
                "candidate_sha": workflow["head_sha"],
                "release_time": release_data["declared_at"],
            }

    if release is None:
        raise ValueError("GitHub Actions snapshot has no declared release candidate workflow")

    return {"release": release, "builds": builds, "execution_builds": execution_builds}


def apply_github_actions_snapshot(fixture: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    """Apply candidate/build provenance without changing execution source facts."""
    normalized = normalize_github_actions(snapshot)
    result = deepcopy(fixture)
    result["release"] = normalized["release"]
    result["builds"] = normalized["builds"]
    result["execution_builds"] = normalized["execution_builds"]
    result["sources"]["build"] = snapshot["source_system"]
    return result
