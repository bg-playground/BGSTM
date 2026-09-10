import json
from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.openproject_normalizer import normalize_openproject

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
OPENPROJECT = ROOT / "openproject_snapshot_v0.json"
EXPECTED_REQUIREMENTS = {f"REQ-{number:03d}" for number in range(1, 9)}
EXPECTED_TEST_CASES = {f"TC-{number:03d}" for number in range(1, 13)}
EXPECTED_FINDINGS = {f"F-{number:03d}" for number in range(1, 8)}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fixture_contains_complete_frozen_entity_inventory():
    fixture = _load(FIXTURE)

    assert set(fixture["requirements"]) == EXPECTED_REQUIREMENTS
    assert set(fixture["test_cases"]) == EXPECTED_TEST_CASES
    assert set(fixture["risks"]) == {f"RISK-{number:03d}" for number in range(1, 6)}
    assert set(fixture["obligations"]) == {f"QO-{number:03d}" for number in range(1, 8)}
    assert set(fixture["changes"]) == {f"CHG-{number:03d}" for number in range(1, 4)}
    assert set(fixture["defects"]) == {f"BUG-{number:03d}" for number in range(1, 5)}


def test_openproject_source_contains_all_frozen_requirements():
    normalized = normalize_openproject(_load(OPENPROJECT))

    assert set(normalized["requirements"]) == EXPECTED_REQUIREMENTS


def test_every_executed_test_is_a_declared_frozen_test_case():
    fixture = _load(FIXTURE)
    executed = {test_id for run in fixture["runs"] for test_id in run["results"]}

    assert executed <= set(fixture["test_cases"])
    assert executed == EXPECTED_TEST_CASES


def test_orphan_condition_is_semantic_not_missing_inventory():
    fixture = _load(FIXTURE)
    mapped = {
        test_id
        for obligation in fixture["obligations"].values()
        for test_id in obligation.get("test_case_ids", [])
    }

    assert "TC-011" in fixture["test_cases"]
    assert "TC-011" not in mapped
    assert "TC-011" not in fixture["secondary_test_cases"]


def test_reconciliation_does_not_move_frozen_findings():
    finding_ids = {finding["finding_id"] for finding in evaluate(_load(FIXTURE))}

    assert finding_ids == EXPECTED_FINDINGS
