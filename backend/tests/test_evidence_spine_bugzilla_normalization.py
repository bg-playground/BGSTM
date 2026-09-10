import json
from pathlib import Path

from experiments.evidence_spine.bugzilla_normalizer import apply_bugzilla_snapshot, normalize_bugzilla
from experiments.evidence_spine.evaluator import evaluate

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
SNAPSHOT = ROOT / "bugzilla_snapshot_v0.json"
EXPECTED_FINDINGS = {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_bugzilla_snapshot_normalizes_to_frozen_defects():
    frozen = _load(FIXTURE)
    normalized = normalize_bugzilla(_load(SNAPSHOT))

    assert normalized == frozen["defects"]


def test_source_shaped_bugzilla_data_preserves_semantic_conclusions():
    frozen = _load(FIXTURE)
    source_shaped = apply_bugzilla_snapshot(frozen, _load(SNAPSHOT))

    baseline = {finding["finding_id"] for finding in evaluate(frozen)}
    normalized = {finding["finding_id"] for finding in evaluate(source_shaped)}

    assert baseline == EXPECTED_FINDINGS
    assert normalized == EXPECTED_FINDINGS
    assert normalized == baseline


def test_closed_fixed_status_does_not_itself_prove_post_fix_verification():
    source_shaped = apply_bugzilla_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    findings = {finding["finding_id"]: finding for finding in evaluate(source_shaped)}

    assert source_shaped["defects"]["BUG-001"]["status"] == "closed_fixed"
    assert "F-004" in findings
    assert "BUG-001" in findings["F-004"]["source_object_ids"]


def test_known_good_closed_defects_are_not_reported_as_unverified():
    source_shaped = apply_bugzilla_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    finding = next(finding for finding in evaluate(source_shaped) if finding["finding_id"] == "F-004")

    assert "BUG-002" not in finding["source_object_ids"]
    assert "BUG-004" not in finding["source_object_ids"]


def test_open_bug_is_not_subject_to_closed_fixed_verification_rule():
    source_shaped = apply_bugzilla_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    finding = next(finding for finding in evaluate(source_shaped) if finding["finding_id"] == "F-004")

    assert source_shaped["defects"]["BUG-003"]["status"] == "open"
    assert "BUG-003" not in finding["source_object_ids"]


def test_bugzilla_remains_defect_system_of_record():
    source_shaped = apply_bugzilla_snapshot(_load(FIXTURE), _load(SNAPSHOT))
    findings = evaluate(source_shaped)

    assert source_shaped["sources"]["defects"] == "bugzilla"
    assert any("bugzilla" in finding["source_systems"] for finding in findings)
