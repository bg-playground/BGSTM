from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate_file

FIXTURE = Path(__file__).parents[1] / "experiments" / "evidence_spine" / "fixture_v0.json"


def _by_id():
    return {finding["finding_id"]: finding for finding in evaluate_file(FIXTURE)}


def test_detects_all_frozen_injected_failures():
    findings = _by_id()
    assert set(findings) == {"F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007"}


def test_every_finding_has_required_explainability_fields():
    required = {
        "finding_id",
        "claim",
        "status",
        "reason",
        "confidence",
        "quality_obligation_ids",
        "evidence_references",
        "source_systems",
        "source_object_ids",
        "source_revisions_or_timestamps",
        "human_review_required",
    }
    for finding in evaluate_file(FIXTURE):
        assert required <= set(finding)
        assert finding["confidence"] == 1.0
        assert finding["evidence_references"]
        assert finding["source_systems"]
        assert finding["source_object_ids"]


def test_environment_mismatch_depends_on_environment_semantics():
    finding = _by_id()["F-003"]
    assert "ENV-002" in finding["source_object_ids"]
    assert "ENVDEF-001" in finding["reason"]


def test_contradiction_requires_human_review():
    finding = _by_id()["F-007"]
    assert finding["human_review_required"] is True
    assert "PASS and FAIL" in finding["reason"]


def test_current_controls_are_not_misreported():
    findings = _by_id()
    text = " ".join(
        " ".join([finding["claim"], finding["reason"], *finding["source_object_ids"]]) for finding in findings.values()
    )
    assert "BUG-002 lacks" not in text
    assert "BUG-004 lacks" not in text
    for test_id in ("TC-006", "TC-008", "TC-009", "TC-012"):
        assert f"{test_id} is semantically orphaned" not in text


def test_freshness_finding_records_invalidation_without_rejecting_current_run():
    finding = _by_id()["F-002"]
    assert "RUN-001" in finding["source_object_ids"]
    assert "CHG-002" in finding["source_object_ids"]
    assert "RUN-003" not in finding["source_object_ids"]


def test_evidence_sufficiency_goes_beyond_missing_link_check():
    finding = _by_id()["F-001"]
    assert "TC-005" in finding["source_object_ids"]
    assert "passed" in finding["reason"].lower()
    assert "no order was created" in finding["reason"].lower()


def test_four_systems_of_record_are_preserved():
    systems = {system for finding in evaluate_file(FIXTURE) for system in finding["source_systems"]}
    assert "openproject" in systems
    assert "playwright" in systems
    assert "bugzilla" in systems

    # GitHub Actions is source provenance for the candidate build even when no
    # standalone finding is emitted solely because the build exists.
    import json

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert fixture["sources"]["build"] == "github-actions"
