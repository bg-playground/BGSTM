# Evidence Spine BGSTM-Assisted Effort Protocol v0

**Status:** Frozen measurement procedure  
**Date:** 2026-09-11  
**Measurement:** AE-001  
**Depends on:** `evidence-spine-human-baseline-result-v0.md`

## Purpose

Measure whether BGSTM materially reduces the expert effort required to turn heterogeneous quality evidence into a defensible release-readiness assessment.

HB-001 established the qualified human benchmark:

- evidence assessment: **32 minutes**;
- assessment + reporting: **44 minutes**.

The frozen commercial threshold is at least 25% less comparable effort. Therefore AE-001 passes the total-effort threshold at **33 minutes or less**, provided finding quality is not degraded and material false positives do not increase.

This is not a benchmark of evaluator CPU/runtime performance. The measured unit is expert review and decision effort after BGSTM has performed deterministic reconciliation.

## Product behavior under test

The product hypothesis is:

> BGSTM can continuously reconcile heterogeneous quality evidence and present deterministic, source-traceable findings so that an experienced reviewer can reach and document a defensible release decision faster than by manually reconciling the source systems.

AE-001 tests the smallest useful form of that workflow. It does not require a dashboard, graph database, LLM, production connector, or new scoring model.

## Measurement roles

### BGSTM deterministic layer

Before the timed human review, BGSTM may:

- normalize the four frozen source snapshots;
- evaluate the frozen deterministic rules;
- identify F-001 through F-007;
- assemble each finding's claim, reason, obligation references, evidence references, source systems, source object IDs, confidence, and human-review flag;
- provide canonical context already present in the frozen fixture, including test-case names, environment semantics, obligations, release identity, changes, defects, and traceability.

### Human reviewer

The timed reviewer must:

- validate that the presented findings are supported by the supplied evidence/context;
- identify any obvious material false positive or unsupported conclusion;
- recognize unresolved/contradictory evidence that requires judgment;
- decide release readiness;
- produce a concise defensible release-readiness explanation.

The human is not required to rediscover every relationship manually from the four raw snapshots. Avoiding that work is the capability being measured.

## Reviewer choice and contamination

AE-001 may be performed by a reviewer who already knows the frozen dataset, including the BGSTM implementer, **only as a product-workflow timing measurement**, not as an independent completeness replication.

Because prior exposure can reduce review time, record whether the reviewer previously knew the dataset and findings. A contaminated reviewer cannot establish a market-wide productivity claim by themselves.

If the reviewer is already familiar with F-001 through F-007, classify the result as `INTERNAL_ASSISTED_MEASUREMENT`. It may satisfy the project's preliminary discovery gate when the workflow and timing are fully recorded, but it must be described as directional evidence pending independent replication.

An independent future reviewer using the same protocol can strengthen or challenge the result.

## Frozen input

Use the combined four-source normalized Evidence Spine state from the merged technical proof. Do not change the frozen source conditions or expected findings for AE-001.

The reviewer receives a BGSTM-assisted review packet containing:

1. release identity and candidate build context;
2. the seven deterministic findings produced by the evaluator;
3. for each finding:
   - claim;
   - reason;
   - Quality Obligation references;
   - evidence references;
   - source systems;
   - source object IDs;
   - confidence;
   - human-review-required flag;
4. enough canonical semantic context to understand referenced tests, obligations, environments, changes, and defects;
5. a response section for validation, release recommendation, confidence, and final explanation.

The raw source snapshots remain available for drill-down when the reviewer wants to validate a finding. The reviewer does not need to inspect all four raw sources unless necessary.

## Important output-contract limitation

The current evaluator's `source_revisions_or_timestamps` field is not yet trustworthy as a distinct provenance field because it currently mirrors `evidence_references` rather than emitting independently normalized revisions/timestamps.

AE-001 must not present that field as stronger provenance than the implementation actually provides. Use the explicit evidence references and source object IDs for this experiment. Record the provenance-field weakness as follow-up rather than changing the frozen evaluator immediately before timing.

## Start condition

Before timing begins:

1. Generate the BGSTM-assisted review packet from the frozen combined state.
2. Confirm it contains exactly F-001 through F-007.
3. Confirm no finding was manually added, removed, or rewritten to improve the experiment outcome.
4. Confirm raw source snapshots are available for drill-down.
5. Record reviewer identity/role and whether they previously knew the dataset.
6. Place the completed packet in front of the reviewer but do not begin reviewing it yet.

Start the timer immediately before the reviewer begins reading the BGSTM-assisted packet.

Do **not** include packet-generation time in the human review measurement when generation is deterministic and would normally be automated by the product. If a human manually repairs, enriches, or reconciles the packet before review, record that time separately and include it in a secondary end-to-end measurement.

## Timed reviewer procedure

### Step 1 — orient to the release

Read the release identity and candidate context. Confirm which candidate is being assessed.

### Step 2 — review every BGSTM finding

For each finding, mark one:

- `ACCEPT` — evidence and reasoning support the finding;
- `REJECT` — finding is materially unsupported/incorrect;
- `NEEDS_REVIEW` — evidence is insufficient or contradictory and requires human judgment.

The reviewer may open raw source evidence whenever needed.

For each `REJECT` or `NEEDS_REVIEW`, record a short reason.

### Step 3 — check for obvious omissions

Ask: based on the presented context and any source evidence inspected during validation, is there an obvious material release concern that BGSTM failed to surface?

This is a sanity check, not a requirement to manually reconstruct the complete source graph.

### Step 4 — record findings-complete time

Record the timestamp when finding validation and the omission sanity check are complete.

### Step 5 — make the release decision

Record:

- `RELEASE`, `RELEASE WITH CONDITIONS`, `DO NOT RELEASE`, or equivalent;
- confidence from 1 to 5;
- the most important evidence supporting the decision;
- unresolved conditions or evidence needed to increase confidence.

### Step 6 — produce final explanation

Write a concise release-readiness explanation suitable for an engineering/release stakeholder. It must distinguish deterministic evidence defects from items requiring human review.

Record the end time when the explanation is complete.

## Measurement record

Complete:

```yaml
measurement_id: AE-001
reviewer_role:
reviewer_prior_dataset_exposure: none | partial | full
measurement_classification: INDEPENDENT_ASSISTED_MEASUREMENT | INTERNAL_ASSISTED_MEASUREMENT
start_time:
findings_complete_time:
end_time:
findings_review_minutes:
reporting_minutes:
total_minutes:
raw_sources_opened: []
finding_dispositions:
  F-001: ACCEPT | REJECT | NEEDS_REVIEW
  F-002: ACCEPT | REJECT | NEEDS_REVIEW
  F-003: ACCEPT | REJECT | NEEDS_REVIEW
  F-004: ACCEPT | REJECT | NEEDS_REVIEW
  F-005: ACCEPT | REJECT | NEEDS_REVIEW
  F-006: ACCEPT | REJECT | NEEDS_REVIEW
  F-007: ACCEPT | REJECT | NEEDS_REVIEW
rejected_or_review_notes: []
additional_material_concerns: []
release_recommendation:
confidence_1_to_5:
final_explanation:
interruptions_or_validity_notes:
```

## Quality guardrails

A fast review is not a pass if quality degrades materially.

AE-001 must record:

- whether all six mutually observable HB-001 frozen conditions remain represented and defensible;
- disposition of F-003 separately because HB-001 could not compare it fairly;
- number of evaluator findings rejected as material false positives;
- any obvious material concern the reviewer believes BGSTM omitted;
- whether F-007 remains unresolved and explicitly requires human review;
- whether the release recommendation is supported by cited evidence rather than generated from an unexplained score.

No LLM may invent source facts or silently resolve contradictory evidence.

## Primary effort calculation

Use total assessment + reporting time:

```text
effort_reduction_percent =
    ((44 - AE-001 total_minutes) / 44) * 100
```

Threshold:

```text
AE-001 total_minutes <= 33
```

For diagnostic comparison only, findings-review time may also be compared with the HB-001 32-minute findings benchmark:

```text
findings_effort_reduction_percent =
    ((32 - AE-001 findings_review_minutes) / 32) * 100
```

The corresponding findings-only threshold is 24 minutes or less.

## Decision rule

Classify the effort result:

### `PRELIMINARY_SUPPORT`

Use when:

- total comparable time is 33 minutes or less;
- the six mutually observable frozen conditions remain correctly represented;
- there is no material increase in false positives;
- F-007 remains explicitly unresolved/human-reviewed;
- the final release explanation is defensible and evidence-linked.

If the reviewer had prior exposure, report this as **directional preliminary support from an internal assisted measurement**, not independent validation.

### `NO_PRELIMINARY_SUPPORT`

Use when the comparable total exceeds 33 minutes or the apparent speed advantage requires degraded finding quality, hidden false positives, or unsupported automation.

### `INCONCLUSIVE`

Use when timing is interrupted/unreliable, the packet is manually altered during the run, the measured work is not comparable, or another validity problem prevents interpretation.

## What AE-001 does not prove

Even a passing result does not establish:

- enterprise ROI;
- production connector reliability;
- performance at enterprise scale;
- market willingness to pay;
- superiority over every experienced QA practitioner;
- independent replication when the reviewer has prior exposure;
- correctness of future AI-generated interpretations.

It answers a narrower question: whether the current deterministic BGSTM evidence workflow shows enough potential to reduce expert reconciliation effort to justify the next discovery investment.

## Execution sequence

After this protocol is merged:

1. implement the smallest deterministic **assisted review packet generator** from the existing combined fixture and evaluator output;
2. test that it preserves exactly F-001 through F-007 and exposes source/evidence references without adding conclusions;
3. generate the AE-001 packet;
4. conduct the timed review according to this document;
5. record the result without changing thresholds after seeing the time;
6. decide whether to proceed to the Azure DevOps adversarial proof.

Do not build a dashboard, production connector framework, graph database, AI summary layer, or release scoring engine merely to conduct AE-001.