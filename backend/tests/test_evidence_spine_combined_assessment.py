import json
from pathlib import Path

from experiments.evidence_spine.bugzilla_normalizer import apply_bugzilla_snapshot
from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.github_actions_normalizer import apply_github_actions_snapshot
from experiments.evidence_spine.openproject_normalizer import apply_openproject_snapshot
from experiments.evidence_spine.playwright_normalizer import apply_playwright_snapshot

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
EXPECTED_FINDINGS = {f"F-{number:03d}" for number in range(1, 8)}
EXPECTED_SOURCES = {"openproject", "playwright", "github-actions", "bugzilla"}


def _load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _combined_fixture():
    fixture = _load("fixture_v0.json")
    fixture = apply_openproject_snapshot(fixture, _load("openproject_snapshot_v0.json"))
    fixture = apply_playwright_snapshot(fixture, _load("playwright_snapshot_v0.json"))
    fixture = apply_github_actions_snapshot(fixture, _load("github_actions_snapshot_v0.json"))
    return apply_bugzilla_snapshot(fixture, _load("bugzilla_snapshot_v0.json"))


def test_all_four_source_snapshots_preserve_frozen_findings():
    findings = evaluate(_combined_fixture())

    assert {finding["finding_id"] for finding in findings} == EXPECTED_FINDINGS
    assert len(findings) == 7


def test_combined_fixture_preserves_source_systems_of_record():
    fixture = _combined_fixture()

    assert set(fixture["sources"].values()) == EXPECTED_SOURCES
    assert fixture["sources"] == {
        "requirements": "openproject",
        "executions": "playwright",
        "build": "github-actions",
        "defects": "bugzilla",
    }


def test_every_material_finding_is_explainable_and_traceable():
    for finding in evaluate(_combined_fixture()):
        assert finding["claim"]
        assert finding["reason"]
        assert finding["evidence_references"]
        assert finding["source_systems"]
        assert finding["source_object_ids"]
        assert set(finding["source_systems"]) <= EXPECTED_SOURCES


def test_combined_proof_includes_non_missing_link_semantics():
    findings = {finding["finding_id"]: finding for finding in evaluate(_combined_fixture())}

    assert "invalidated" in findings["F-002"]["claim"].lower()
    assert "environment" in findings["F-003"]["reason"].lower()
    assert "containing the defect fix sha" in findings["F-004"]["reason"].lower()
    assert "contradictory" in findings["F-007"]["claim"].lower()


def test_contradiction_remains_unresolved_and_requires_human_review():
    finding = next(finding for finding in evaluate(_combined_fixture()) if finding["finding_id"] == "F-007")

    assert finding["human_review_required"] is True
    assert "PASS and FAIL" in finding["reason"]


def test_combined_release_identity_comes_from_github_actions():
    fixture = _combined_fixture()

    assert fixture["sources"]["build"] == "github-actions"
    assert fixture["execution_builds"]["RUN-003"] == "GHA-9003"
    assert fixture["builds"]["GHA-9003"]["sha"] == fixture["release"]["candidate_sha"]
