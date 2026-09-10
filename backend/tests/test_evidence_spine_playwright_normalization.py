import json
from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.playwright_normalizer import apply_playwright_snapshot, normalize_playwright

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
SNAPSHOT = ROOT / "playwright_snapshot_v0.json"
EXPECTED_FINDINGS = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_playwright_snapshot_normalizes_to_frozen_runs():
    frozen = _load(FIXTURE)
    normalized = normalize_playwright(_load(SNAPSHOT))

    assert normalized == frozen["runs"]


def test_source_shaped_playwright_data_preserves_semantic_conclusions():
    frozen = _load(FIXTURE)
    source_shaped = apply_playwright_snapshot(frozen, _load(SNAPSHOT))

    baseline = {finding["finding_id"] for finding in evaluate(frozen)}
    normalized = {finding["finding_id"] for finding in evaluate(source_shaped)}

    assert baseline == EXPECTED_FINDINGS
    assert normalized == EXPECTED_FINDINGS
    assert normalized == baseline


def test_playwright_normalization_preserves_environment_and_candidate_context():
    runs = normalize_playwright(_load(SNAPSHOT))
    run_002 = next(run for run in runs if run["id"] == "RUN-002")
    run_003 = next(run for run in runs if run["id"] == "RUN-003")

    assert run_002["sha"] == "sha-candidate-003"
    assert run_002["environment_id"] == "ENV-002"
    assert run_003["sha"] == "sha-candidate-003"
    assert run_003["environment_id"] == "ENV-001"


def test_playwright_normalization_preserves_artifact_and_contradiction_evidence():
    source_shaped = apply_playwright_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    findings = {finding["finding_id"]: finding for finding in evaluate(source_shaped)}

    run_003 = next(run for run in source_shaped["runs"] if run["id"] == "RUN-003")
    assert run_003["artifacts"]["TC-010"] == ["candidate_sha_recorded"]
    assert findings["F-007"]["human_review_required"] is True
    assert "RUN-003" in findings["F-007"]["source_object_ids"]
    assert "RUN-003-OBS-2" in findings["F-007"]["source_object_ids"]


def test_playwright_remains_execution_system_of_record():
    source_shaped = apply_playwright_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    findings = evaluate(source_shaped)

    assert source_shaped["sources"]["executions"] == "playwright"
    assert any("playwright" in finding["source_systems"] for finding in findings)
