# Evidence Spine Human Baseline v0

**Status:** Frozen comparison procedure  
**Date:** 2026-09-10  
**Depends on:** `quality-evidence-model-v0.md`, `evidence-spine-fixture-contract-v0.md`, and `evidence-spine-combined-assessment-v0.md`

## Purpose

The heterogeneous Evidence Spine technical proof has passed its frozen technical assertions. This baseline tests the remaining discovery question:

> Does BGSTM materially improve the completeness or effort of a release-quality evidence assessment compared with a competent QA practitioner working from the same source facts without the BGSTM evaluator?

This is a comparison experiment, not a usability test and not a test of whether a participant can guess the seven injected findings.

## Blinding rule

Before the session, the participant must **not** receive:

- the frozen F-001 through F-007 expected findings;
- evaluator output;
- the combined-assessment conclusions;
- the deterministic rules as named BGSTM findings;
- hints identifying which artifacts contain injected problems.

The participant may know that the exercise concerns release readiness and cross-tool quality evidence. They should work from source facts rather than the canonical evaluator fixture.

## Participant

Use a practitioner capable of independently assessing software release quality across requirements, automated tests, CI/build evidence, and defects.

Record the participant's role and relevant experience. The participant does not need prior BGSTM knowledge.

A BGSTM implementer who already knows the injected findings is not a valid blinded participant for the primary baseline.

## Source packet

Provide the source-shaped evidence representing the same frozen release candidate used by the evaluator:

1. `backend/experiments/evidence_spine/openproject_snapshot_v0.json`
2. `backend/experiments/evidence_spine/playwright_snapshot_v0.json`
3. `backend/experiments/evidence_spine/github_actions_snapshot_v0.json`
4. `backend/experiments/evidence_spine/bugzilla_snapshot_v0.json`

Do **not** provide `fixture_v0.json`, evaluator code, evaluator tests, or documents that reveal the expected findings.

The JSON files stand in for inspection of four systems of record. This baseline therefore measures reasoning and evidence-reconciliation effort, not UI navigation latency or production connector performance.

## Participant brief

Give the participant only the following task statement:

> You are reviewing release candidate REL-001 for checkout reliability. Using the supplied source-system evidence, assess whether the available quality evidence is sufficient to support release. Identify material evidence gaps, stale or invalid evidence, traceability concerns, defect-verification concerns, contradictions, or other conditions that would affect confidence in the release decision. For each material finding, identify the source evidence that led you to it. Finish with a release recommendation and confidence rating from 1 to 5.

Do not tell the participant how many findings exist.

## Questions to answer

The completed assessment must be sufficient to answer the seven questions frozen in the Quality Evidence Model v0 specification:

1. Which high-risk quality obligations are unsupported?
2. Which requirements appear covered but lack qualifying current execution?
3. Which quality evidence became potentially stale after a specified change?
4. Which fixed/closed defects lack qualifying post-fix verification?
5. Which tests or evidence artifacts are semantically orphaned?
6. Which evidence chains contain contradictory observations?
7. What evidence supports and contradicts a recommendation to release the candidate?

These questions are scoring dimensions for the facilitator. They should not be expanded into hints about the expected F-001 through F-007 conditions during the session.

## Timing procedure

1. Record `start_time` immediately before the participant receives the source packet.
2. The participant inspects the source facts and records findings in their own words.
3. The participant records the release recommendation and confidence rating.
4. Record the time at which evidence-gap identification is complete.
5. The participant then assembles the final defensible release-readiness explanation.
6. Record `end_time` when that explanation is complete.
7. Calculate `total_minutes` and `reporting_minutes` separately.

Do not pause the timer for ordinary source inspection, cross-referencing, or note taking. Record unusual interruptions separately rather than silently subtracting them.

## Baseline record

Create one completed record using this structure:

```yaml
baseline_id: HB-001
participant_role:
participant_experience_summary:
start_time:
findings_complete_time:
end_time:
total_minutes:
reporting_minutes:
source_artifacts_inspected: []
findings_identified:
  - participant_finding_id:
    claim:
    source_evidence: []
    release_impact:
release_recommendation:
confidence_1_to_5:
facilitator_notes:
```

Do not populate expected-finding matches until the participant has finished.

## Post-session scoring

After the session is complete, compare each participant finding with the frozen oracle. Record:

```yaml
correct_expected_findings: []
false_positives: []
false_negatives: []
expected_findings_detected_count:
material_false_positive_count:
material_false_negative_count:
```

A participant finding may use different terminology from BGSTM and still count as a correct detection if it identifies the same material evidence defect and its relevant source facts.

Do not award multiple detections for restating the same underlying condition.

A false positive is a material release-quality problem asserted by the participant that is contradicted by the frozen source facts or known-good controls. Stylistic recommendations and reasonable non-material observations are not false positives.

## Comparison calculation

Use the BGSTM-assisted result from the frozen combined technical proof and compare it with the completed human record.

For completeness:

```text
additional_material_problems =
    BGSTM correctly detected frozen findings
    - human correctly detected frozen findings
```

For effort, compare equivalent assessment/reporting work. Record the BGSTM-assisted elapsed measurement used and its measurement method before calculating a percentage.

```text
effort_reduction_percent =
    ((human_minutes - bgstm_assisted_minutes) / human_minutes) * 100
```

Do not claim an effort advantage if the BGSTM-assisted timing has not been measured on a comparable basis. Automated unit-test runtime alone is not a comparable human assessment/reporting measurement.

## Frozen commercial-support gate

The commercial hypothesis receives preliminary support if **either** condition is met:

1. BGSTM requires at least **25% less assessment/reporting time** on a comparable measurement basis; **or**
2. BGSTM identifies at least **2 additional material evidence problems** without a material increase in false positives.

The result should be classified as one of:

- `PRELIMINARY_SUPPORT`
- `NO_PRELIMINARY_SUPPORT`
- `INCONCLUSIVE`

Use `INCONCLUSIVE` when timing is not comparable, participant blinding was compromised, source facts changed during the exercise, or another validity problem prevents a defensible comparison.

## Interpretation constraints

One synthetic baseline session cannot establish a market-wide productivity claim. A passing result is evidence supporting continued discovery, not proof of commercial demand or an enterprise ROI guarantee.

Likewise, failure to beat one competent practitioner is meaningful evidence against the current value hypothesis and should not be hidden by changing the fixture or scoring after the session.

Record unexpected participant strategies. If the human reaches the same conclusion quickly by applying a simple existing-tool workflow, that is especially important evidence for the product decision.

## Next decision

After HB-001 is scored:

- if the result is `PRELIMINARY_SUPPORT`, document why the advantage occurred and proceed to the Azure DevOps adversarial proof;
- if `NO_PRELIMINARY_SUPPORT`, stop and reassess the Quality Intelligence differentiation before adding production connector scope;
- if `INCONCLUSIVE`, correct only the identified validity problem and rerun the baseline without changing the frozen source facts or expected findings.
