import json
from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.github_actions_normalizer import apply_github_actions_snapshot, normalize_github_actions

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
SNAPSHOT = ROOT / "github_actions_snapshot_v0.json"
EXPECTED_FINDINGS = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_github_actions_snapshot_derives_frozen_candidate_release_identity():
    frozen = _load(FIXTURE)
    normalized = normalize_github_actions(_load(SNAPSHOT))

    assert normalized["release"] == frozen["release"]


def test_github_actions_provenance_links_execution_runs_to_observed_builds():
    normalized = normalize_github_actions(_load(SNAPSHOT))

    assert normalized["execution_builds"] == {
        "RUN-001": "GHA-9001",
        "RUN-002": "GHA-9002",
        "RUN-003": "GHA-9003",
        "RUN-003-OBS-2": "GHA-9003",
    }
    assert normalized["builds"]["GHA-9003"]["sha"] == "sha-candidate-003"
    assert normalized["builds"]["GHA-9003"]["conclusion"] == "success"


def test_source_shaped_github_actions_data_preserves_semantic_conclusions():
    frozen = _load(FIXTURE)
    source_shaped = apply_github_actions_snapshot(frozen, _load(SNAPSHOT))

    baseline = {finding["finding_id"] for finding in evaluate(frozen)}
    normalized = {finding["finding_id"] for finding in evaluate(source_shaped)}

    assert baseline == EXPECTED_FINDINGS
    assert normalized == EXPECTED_FINDINGS
    assert normalized == baseline


def test_candidate_identity_is_derived_from_workflow_not_playwright_run():
    frozen = _load(FIXTURE)
    snapshot = _load(SNAPSHOT)
    source_shaped = apply_github_actions_snapshot(frozen, snapshot)

    candidate_workflow = next(
        workflow for workflow in snapshot["workflow_runs"] if workflow.get("release", {}).get("candidate")
    )
    assert source_shaped["release"]["candidate_sha"] == candidate_workflow["head_sha"]
    assert source_shaped["execution_builds"]["RUN-003"] == "GHA-9003"


def test_github_actions_remains_build_system_of_record():
    source_shaped = apply_github_actions_snapshot(_load(FIXTURE), _load(SNAPSHOT))

    assert source_shaped["sources"]["build"] == "github-actions"
    assert source_shaped["builds"]["GHA-9003"]["workflow_name"] == "Release Candidate CI"
