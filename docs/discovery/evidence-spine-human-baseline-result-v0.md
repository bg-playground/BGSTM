# Evidence Spine Human Baseline Result v0

**Status:** Qualified baseline result  
**Date:** 2026-09-11  
**Baseline:** HB-001  
**Depends on:** `evidence-spine-human-baseline-v0.md`

## Result summary

HB-001 produced useful human-comparison evidence, but the participant packet omitted semantic facts available to the deterministic BGSTM evaluator. The result is therefore retained as a **qualified baseline**, not used to claim that BGSTM detected more material problems than the practitioner.

The participant was a QA lead / release-readiness reviewer with approximately 12 years of QA/testing experience and relevant experience with requirements/test management, automated test results, CI/build pipelines, and defect verification.

Recorded timing:

- start: 2026-09-10T17:50:00-04:00
- findings complete: 2026-09-10T18:22:00-04:00
- final explanation complete: 2026-09-10T18:34:00-04:00
- evidence assessment: **32 minutes**
- reporting after findings complete: **12 minutes**
- total assessment + reporting: **44 minutes**
- reported interruptions: none

The participant inspected all four source snapshots, used a text editor / JSON pretty-printing for readability, cross-referenced evidence manually, and reported no BGSTM evaluator or analysis script use.

## Frozen-finding comparison

| Frozen finding | Human result | Baseline treatment |
| --- | --- | --- |
| F-001 — payment-failure evidence insufficient | Detected | Comparable / detected |
| F-002 — pricing evidence invalidated by later change | Detected | Comparable / detected |
| F-003 — ENV-002 evidence cannot satisfy approved-environment semantics | Participant identified missing environment definitions but could not derive the frozen environment conclusion | **Not comparable** |
| F-004 — BUG-001 lacks qualifying post-fix verification | Detected | Comparable / detected |
| F-005 — TC-011 semantic orphan | Detected within broader traceability/orphan analysis | Comparable / detected |
| F-006 — REQ-001 traceability predates CHG-001 | Detected | Comparable / detected |
| F-007 — contradictory qualifying TC-004 observations | Detected | Comparable / detected |

### Comparable finding result

Of the six frozen findings for which the human packet exposed the semantic facts necessary for the comparison, the participant detected **6 of 6**.

F-003 is excluded from the human-vs-BGSTM completeness comparison. It must not be scored as a human false negative.

## Packet asymmetry

The participant packet contained the four source-shaped snapshots but omitted some semantic facts present in the canonical evaluator fixture. Most importantly, the participant could see `ENV-001` and `ENV-002` identifiers but not the environment definitions that distinguish the approved checkout environment from the developer-local/nonqualifying environment.

The participant independently called out this limitation rather than inventing environment semantics.

The packet also exposed Quality Obligation identifiers without the complete obligation definitions and test IDs without the complete canonical test-case descriptions. These omissions should be corrected in any future replication.

Because the deterministic evaluator had access to richer semantic facts, this run cannot support a claim that BGSTM found seven material problems while the human found six.

## Additional human observations

The participant recorded eight material findings rather than attempting to match an undisclosed expected count. In addition to the frozen conditions, the response raised professional concerns including:

- BUG-002 closure chronology relative to the later contradictory TC-004 evidence;
- BUG-003 remaining open at release declaration despite passing TC-006 observations;
- uncertainty about whether candidate composition contains relevant change/fix SHAs;
- broader traceability incompleteness beyond the frozen TC-011 orphan condition.

These observations are retained as discovery evidence. They are not retroactively added to the frozen oracle and are not automatically classified as BGSTM misses. Some overlap with frozen findings or represent human judgment under incomplete source semantics.

This behavior is commercially relevant: an experienced practitioner can generate useful judgment beyond deterministic rule output, while deterministic semantics may help distinguish confirmed evidence defects from broader concerns requiring human review.

## Release recommendation

The participant recommended **DO NOT RELEASE** with confidence **3/5**.

The response identified evidence supporting the candidate as well as evidence weakening release confidence. The participant's final rationale emphasized the unresolved TC-004 contradiction, defect-verification concerns, candidate-composition uncertainty, insufficient payment-failure evidence, stale pricing evidence, incomplete traceability, and undefined environment semantics.

## Commercial-support gate

### Additional-material-problems criterion

**Not satisfied / not claimable from HB-001.**

On mutually observable frozen conditions, the practitioner detected 6 of 6. F-003 is not comparable because the human packet did not contain the semantic facts required to derive it.

Accordingly, HB-001 does not support the claim that BGSTM detects at least two additional material evidence problems compared with this practitioner.

### Effort-reduction criterion

**Not yet evaluated.**

HB-001 establishes a usable human benchmark of:

- 32 minutes to complete evidence assessment;
- 44 minutes to complete assessment plus a defensible release-readiness explanation.

Automated evaluator/unit-test runtime is not a comparable BGSTM-assisted measurement and must not be used to claim the frozen 25% effort reduction.

The next measurement should determine how long it takes to turn BGSTM deterministic findings and provenance into a reviewable release assessment, including the human validation needed before a release decision is accepted.

For the 44-minute total benchmark, the frozen 25% threshold corresponds to **33 minutes or less** for comparable BGSTM-assisted assessment + reporting. For the 32-minute findings-only benchmark, it corresponds to **24 minutes or less** for comparable findings work. These thresholds must only be used when the measured work is genuinely equivalent.

## Classification

**QUALIFIED_BASELINE — COMMERCIAL GATE STILL OPEN**

This classification intentionally differs from treating the session as a failed or successful commercial proof. The run is sufficiently credible to establish a human effort benchmark and demonstrate strong expert performance, but its source asymmetry prevents a fair completeness comparison for all seven frozen findings.

The result therefore supports continued discovery without claiming superiority that the evidence does not establish.

## Product implication

HB-001 sharpens the value hypothesis:

> BGSTM should not depend on finding problems that an experienced QA lead is incapable of finding. Its value can come from continuously reconciling heterogeneous quality evidence so that an experienced reviewer can reach a defensible decision faster, more consistently, and with explicit provenance.

The participant manually performed the cross-system reconciliation that BGSTM is intended to systematize. The next proof should measure whether BGSTM materially reduces that expert reconciliation and reporting effort while preserving or improving the quality of the resulting decision.

## Future replication

A future independent participant is useful but is **not a blocker** for the next discovery step.

Before any replication, prepare a corrected participant packet that exposes the same source facts available to the evaluator, including:

- environment definitions and qualification properties;
- complete Quality Obligation definitions;
- complete test-case identities/descriptions;
- any other source fact consumed by deterministic rules but absent from the original human packet.

Do not change the frozen source conditions, expected F-001 through F-007 findings, evaluator rules, or commercial thresholds merely to improve a future result.

## Next decision

Proceed to a **BGSTM-assisted effort measurement** using the existing frozen Evidence Spine result and the 44-minute HB-001 benchmark.

The measurement must include the human review necessary to validate the deterministic findings and produce a defensible release-readiness explanation. If comparable BGSTM-assisted assessment + reporting is 33 minutes or less without degrading finding quality or materially increasing false positives, the frozen 25% effort-reduction criterion receives preliminary support.

After that measurement, make the commercial-support judgment and decide whether the evidence justifies proceeding to the Azure DevOps adversarial proof.