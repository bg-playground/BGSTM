import json
from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.openproject_normalizer import apply_openproject_snapshot, normalize_openproject

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
SNAPSHOT = ROOT / "openproject_snapshot_v0.json"
EXPECTED_FINDINGS = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_openproject_snapshot_normalizes_to_frozen_source_sections():
    frozen = _load(FIXTURE)
    normalized = normalize_openproject(_load(SNAPSHOT))

    assert normalized["requirements"] == frozen["requirements"]
    assert normalized["risks"] == frozen["risks"]
    assert normalized["changes"] == frozen["changes"]
    assert normalized["traceability"] == frozen["traceability"]


def test_source_shaped_openproject_data_preserves_semantic_conclusions():
    frozen = _load(FIXTURE)
    source_shaped = apply_openproject_snapshot(frozen, _load(SNAPSHOT))

    baseline = {finding["finding_id"] for finding in evaluate(frozen)}
    normalized = {finding["finding_id"] for finding in evaluate(source_shaped)}

    assert baseline == EXPECTED_FINDINGS
    assert normalized == EXPECTED_FINDINGS
    assert normalized == baseline


def test_normalization_preserves_external_system_as_system_of_record():
    source_shaped = apply_openproject_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    findings = evaluate(source_shaped)

    assert source_shaped["sources"]["requirements"] == "openproject"
    assert any("openproject" in finding["source_systems"] for finding in findings)
