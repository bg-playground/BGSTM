import json
from copy import deepcopy
from pathlib import Path

from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.github_actions_normalizer import apply_github_actions_snapshot

ROOT = Path(__file__).parents[1] / "experiments" / "evidence_spine"
FIXTURE = ROOT / "fixture_v0.json"
GITHUB_ACTIONS = ROOT / "github_actions_snapshot_v0.json"
EXPECTED_FINDINGS = {f"F-{number:03d}" for number in range(1, 8)}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _with_build_provenance():
    return apply_github_actions_snapshot(_load(FIXTURE), _load(GITHUB_ACTIONS))


def test_build_provenance_preserves_frozen_findings():
    finding_ids = {finding["finding_id"] for finding in evaluate(_with_build_provenance())}

    assert finding_ids == EXPECTED_FINDINGS


def test_candidate_qualification_uses_linked_build_not_run_claimed_sha():
    fixture = _with_build_provenance()
    run = next(run for run in fixture["runs"] if run["id"] == "RUN-002")
    run["sha"] = "sha-untrusted-run-metadata"

    findings = {finding["finding_id"] for finding in evaluate(fixture)}

    assert "F-003" in findings


def test_non_candidate_linked_build_overrides_run_claimed_candidate_sha():
    fixture = _with_build_provenance()
    fixture["builds"]["GHA-9002"]["sha"] = "sha-not-candidate"

    finding = next(finding for finding in evaluate(fixture) if finding["finding_id"] == "F-003")

    assert "RUN-002" not in finding["source_object_ids"]


def test_later_build_containing_fix_satisfies_post_fix_verification():
    fixture = _with_build_provenance()
    candidate_build = fixture["builds"]["GHA-9003"]
    candidate_build["contains_shas"] = [*candidate_build["contains_shas"], "sha-fix-bug-001"]

    findings = {finding["finding_id"] for finding in evaluate(fixture)}

    assert "F-004" not in findings


def test_same_head_sha_does_not_imply_build_contains_fix():
    fixture = _with_build_provenance()
    mutated = deepcopy(fixture)
    mutated["defects"]["BUG-001"]["fix_sha"] = mutated["release"]["candidate_sha"]
    for build in mutated["builds"].values():
        build["contains_shas"] = [sha for sha in build["contains_shas"] if sha != mutated["release"]["candidate_sha"]]

    findings = {finding["finding_id"] for finding in evaluate(mutated)}

    assert "F-004" in findings
