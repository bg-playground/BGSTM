from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from experiments.evidence_spine.bugzilla_normalizer import apply_bugzilla_snapshot
from experiments.evidence_spine.evaluator import evaluate
from experiments.evidence_spine.github_actions_normalizer import apply_github_actions_snapshot
from experiments.evidence_spine.openproject_normalizer import apply_openproject_snapshot
from experiments.evidence_spine.playwright_normalizer import apply_playwright_snapshot

ROOT = Path(__file__).parent
EXPECTED_FINDINGS = [f"F-{number:03d}" for number in range(1, 8)]


def _load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def combined_fixture() -> dict[str, Any]:
    fixture = _load("fixture_v0.json")
    fixture = apply_openproject_snapshot(fixture, _load("openproject_snapshot_v0.json"))
    fixture = apply_playwright_snapshot(fixture, _load("playwright_snapshot_v0.json"))
    fixture = apply_github_actions_snapshot(fixture, _load("github_actions_snapshot_v0.json"))
    return apply_bugzilla_snapshot(fixture, _load("bugzilla_snapshot_v0.json"))


def build_packet() -> dict[str, Any]:
    fixture = combined_fixture()
    findings = evaluate(fixture)

    ids = [finding["finding_id"] for finding in findings]
    if ids != EXPECTED_FINDINGS:
        raise ValueError(f"Frozen finding set changed: {ids!r}")

    safe_findings = []
    for finding in findings:
        safe_findings.append(
            {
                "finding_id": finding["finding_id"],
                "claim": finding["claim"],
                "reason": finding["reason"],
                "quality_obligation_ids": deepcopy(finding["quality_obligation_ids"]),
                "evidence_references": deepcopy(finding["evidence_references"]),
                "source_systems": deepcopy(finding["source_systems"]),
                "source_object_ids": deepcopy(finding["source_object_ids"]),
                "confidence": finding["confidence"],
                "human_review_required": finding["human_review_required"],
            }
        )

    return {
        "measurement_id": "AE-001",
        "release": deepcopy(fixture["release"]),
        "candidate_build": deepcopy(fixture.get("builds", {}).get(fixture.get("execution_builds", {}).get("RUN-003"))),
        "findings": safe_findings,
        "semantic_context": {
            "test_cases": deepcopy(fixture["test_cases"]),
            "obligations": deepcopy(fixture["obligations"]),
            "environments": deepcopy(fixture["environments"]),
            "changes": deepcopy(fixture["changes"]),
            "defects": deepcopy(fixture["defects"]),
            "traceability": deepcopy(fixture["traceability"]),
            "sources": deepcopy(fixture["sources"]),
        },
        "review_response": {
            "reviewer_role": "",
            "reviewer_prior_dataset_exposure": "",
            "measurement_classification": "",
            "start_time": "",
            "findings_complete_time": "",
            "end_time": "",
            "findings_review_minutes": None,
            "reporting_minutes": None,
            "total_minutes": None,
            "raw_sources_opened": [],
            "finding_dispositions": {finding_id: "" for finding_id in EXPECTED_FINDINGS},
            "rejected_or_review_notes": [],
            "additional_material_concerns": [],
            "release_recommendation": "",
            "confidence_1_to_5": None,
            "final_explanation": "",
            "interruptions_or_validity_notes": "",
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    release = packet["release"]
    build = packet["candidate_build"] or {}
    lines = [
        "# AE-001 BGSTM-Assisted Review Packet",
        "",
        "## Release context",
        "",
        f"- Release: `{release['id']}`",
        f"- Candidate SHA: `{release['candidate_sha']}`",
        f"- Release time: `{release['release_time']}`",
        f"- Candidate build: `{build.get('id', 'not-recorded')}`",
        "",
        "Review each deterministic finding as `ACCEPT`, `REJECT`, or `NEEDS_REVIEW`. Open raw source snapshots only when needed to validate the evidence.",
        "",
        "## Deterministic findings",
        "",
    ]

    for finding in packet["findings"]:
        lines.extend(
            [
                f"### {finding['finding_id']} — {finding['claim']}",
                "",
                f"**Reason:** {finding['reason']}",
                "",
                f"**Quality obligations:** {', '.join(finding['quality_obligation_ids']) or 'None'}",
                "",
                f"**Evidence references:** {', '.join(finding['evidence_references'])}",
                "",
                f"**Source systems:** {', '.join(finding['source_systems'])}",
                "",
                f"**Source object IDs:** {', '.join(finding['source_object_ids'])}",
                "",
                f"**Confidence:** {finding['confidence']}",
                "",
                f"**Human review required:** {'YES' if finding['human_review_required'] else 'NO'}",
                "",
                "**Disposition:** ____________________",
                "",
                "**Reviewer note (required for REJECT/NEEDS_REVIEW):**",
                "",
                "",
            ]
        )

    context = packet["semantic_context"]
    lines.extend(["## Canonical semantic context", "", "### Test cases", ""])
    for test_id, test in context["test_cases"].items():
        lines.append(f"- `{test_id}` — {test['name']}")

    lines.extend(["", "### Environments", ""])
    for environment_id, environment in context["environments"].items():
        lines.append(f"- `{environment_id}` — `{json.dumps(environment, sort_keys=True)}`")

    lines.extend(["", "### Quality obligations", ""])
    for obligation_id, obligation in context["obligations"].items():
        lines.append(f"- `{obligation_id}` — `{json.dumps(obligation, sort_keys=True)}`")

    lines.extend(
        [
            "",
            "## Timed review record",
            "",
            "- Reviewer role:",
            "- Prior dataset exposure: none / partial / full",
            "- Measurement classification: INDEPENDENT_ASSISTED_MEASUREMENT / INTERNAL_ASSISTED_MEASUREMENT",
            "- Start time:",
            "- Findings complete time:",
            "- End time:",
            "- Findings review minutes:",
            "- Reporting minutes:",
            "- Total minutes:",
            "- Raw sources opened:",
            "- Additional material concerns:",
            "- Release recommendation:",
            "- Confidence (1-5):",
            "- Interruptions or validity notes:",
            "",
            "## Final release-readiness explanation",
            "",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the frozen AE-001 assisted review packet.")
    parser.add_argument("--out", type=Path, required=True, help="Output Markdown path")
    parser.add_argument("--json-out", type=Path, help="Optional machine-readable packet path")
    args = parser.parse_args()

    packet = build_packet()
    args.out.write_text(render_markdown(packet), encoding="utf-8")
    if args.json_out:
        args.json_out.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
