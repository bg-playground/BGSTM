from __future__ import annotations

from copy import deepcopy
from typing import Any


_STATUS = {"passed": "pass", "failed": "fail"}


def normalize_playwright(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Map a Playwright-shaped discovery snapshot into frozen run semantics."""
    runs: list[dict[str, Any]] = []
    for source_run in snapshot["runs"]:
        metadata = source_run["metadata"]
        results: dict[str, str] = {}
        artifacts: dict[str, list[str]] = {}
        for test in source_run["tests"]:
            results[test["id"]] = _STATUS[test["status"]]
            attachments = [attachment["name"] for attachment in test.get("attachments", [])]
            if attachments:
                artifacts[test["id"]] = attachments

        runs.append(
            {
                "id": metadata["run_id"],
                "sha": metadata["commit_sha"],
                "environment_id": metadata["environment_id"],
                "executed_at": metadata["finished_at"],
                "results": results,
                "artifacts": artifacts,
            }
        )
    return runs


def apply_playwright_snapshot(fixture: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    """Replace Playwright-owned canonical runs while preserving other sources."""
    result = deepcopy(fixture)
    result["runs"] = normalize_playwright(snapshot)
    result["sources"]["executions"] = snapshot["source_system"]
    return result
