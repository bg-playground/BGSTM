from experiments.evidence_spine.assisted_review_packet import EXPECTED_FINDINGS, build_packet, render_markdown


def test_packet_preserves_exact_frozen_findings_in_order():
    packet = build_packet()
    assert [finding["finding_id"] for finding in packet["findings"]] == EXPECTED_FINDINGS


def test_packet_exposes_required_review_fields_without_bad_revision_field():
    required = {
        "finding_id",
        "claim",
        "reason",
        "quality_obligation_ids",
        "evidence_references",
        "source_systems",
        "source_object_ids",
        "confidence",
        "human_review_required",
    }
    for finding in build_packet()["findings"]:
        assert set(finding) == required
        assert "source_revisions_or_timestamps" not in finding


def test_packet_includes_semantic_context_needed_for_f003_and_other_findings():
    context = build_packet()["semantic_context"]
    assert context["environments"]["ENV-001"]["definition_id"] == "ENVDEF-001"
    assert context["environments"]["ENV-002"]["definition_id"] != "ENVDEF-001"
    assert context["obligations"]["QO-002"]["required_environment"] == "ENVDEF-001"
    assert context["test_cases"]["TC-004"]["name"] == "Firefox checkout succeeds"


def test_f007_remains_explicitly_human_review_required():
    findings = {finding["finding_id"]: finding for finding in build_packet()["findings"]}
    assert findings["F-007"]["human_review_required"] is True
    assert "PASS and FAIL" in findings["F-007"]["reason"]


def test_packet_preserves_four_systems_of_record_and_candidate_build_context():
    packet = build_packet()
    assert set(packet["semantic_context"]["sources"].values()) == {
        "openproject",
        "playwright",
        "github-actions",
        "bugzilla",
    }
    assert packet["candidate_build"]["id"] == "GHA-9003"
    assert packet["candidate_build"]["sha"] == packet["release"]["candidate_sha"]


def test_markdown_is_review_ready_without_adding_release_conclusion():
    text = render_markdown(build_packet())
    for finding_id in EXPECTED_FINDINGS:
        assert finding_id in text
    assert "Disposition:" in text
    assert "Final release-readiness explanation" in text
    assert "DO NOT RELEASE" not in text
    assert "RELEASE WITH CONDITIONS" not in text
