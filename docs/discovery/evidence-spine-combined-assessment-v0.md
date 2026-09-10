# Evidence Spine Combined Assessment v0

**Status:** Discovery proof assessment  
**Date:** 2026-09-10  
**Oracle:** `quality-evidence-model-v0.md` and `evidence-spine-fixture-contract-v0.md`

## Decision

**Technical heterogeneous Evidence Spine proof: PASS, subject to CI confirmation of this assessment.**

This assessment combines the four frozen source-shaped discovery snapshots through their independent normalizers before running the deterministic evaluator:

- OpenProject — requirements, risks, changes, and traceability
- Playwright — executions and evidence artifacts
- GitHub Actions — candidate build identity, execution-to-build provenance, and build containment
- Bugzilla — defect lifecycle, fix identity, and verification-test metadata

The source systems remain authoritative for their respective facts. BGSTM normalizes and evaluates those facts; it does not replace the systems of record.

## Frozen acceptance assessment

| Assertion | Result | Evidence |
| --- | --- | --- |
| A-001 Detect at least 6 of F-001 through F-007 | PASS | Combined evaluator produces all 7 frozen findings. |
| A-002 No more than 2 material false positives | PASS for frozen controls | Combined evaluator produces exactly the 7 injected findings; existing control tests protect C-001 through C-005. |
| A-003 Every finding identifies source evidence and rule/reason | PASS | Combined assessment requires claim, reason, evidence references, source systems, and source object IDs for every finding. |
| A-004 At least one finding requires more than a missing-link check | PASS | Freshness invalidation, environment qualification, build containment, and contradiction are semantic checks. |
| A-005 F-003 depends on environment semantics | PASS | Candidate browser results on ENV-002 are rejected because it does not satisfy ENVDEF-001. |
| A-006 F-007 remains unresolved and requires human review | PASS | Contradictory qualifying TC-004 PASS/FAIL evidence is not automatically reconciled. |
| A-007 No LLM required | PASS | Evaluator and normalizers are deterministic Python. |
| A-008 No graph database required | PASS | Discovery implementation uses JSON-shaped facts and in-memory deterministic evaluation. |
| A-009 Four named systems remain systems of record | PASS | Combined fixture retains OpenProject, Playwright, GitHub Actions, and Bugzilla ownership. |
| A-010 No seventh BGSTM phase introduced | PASS | The experiment adds semantic evidence evaluation, not a lifecycle phase. |

## Frozen findings

The combined source-shaped proof must produce exactly:

1. F-001 — insufficient required postcondition evidence despite a passing test
2. F-002 — historical execution invalidated by a later relevant change
3. F-003 — candidate test outcome from a non-qualifying environment
4. F-004 — closed defect lacking verification on a build containing the fix
5. F-005 — executed test with no declared quality-intent relationship
6. F-006 — traceability requiring revalidation after requirement-affecting change
7. F-007 — contradictory qualifying evidence requiring human review

These findings demonstrate more than cross-tool aggregation. The evaluator distinguishes observed evidence from evidence that qualifies to satisfy a declared quality obligation.

## What this proves

The discovery implementation can reconstruct a coherent release-quality interpretation from heterogeneous source-shaped data while preserving source ownership and the frozen semantic conclusions. It can reject evidence because it is stale, from the wrong environment, attached to the wrong build context, insufficient for the obligation, semantically orphaned, or contradictory.

The strongest demonstrated distinction is therefore not that BGSTM can draw a cross-tool evidence graph. It is that BGSTM can apply explicit quality obligations to determine whether observed evidence is sufficient to support a quality claim.

## What this does not prove

This result does **not** establish production connector reliability, live API compatibility, enterprise-scale identity resolution, temporal reconciliation at production volume, commercial willingness to pay, or superiority to a competent QA practitioner. It also does not validate the Azure DevOps additive-semantics hypothesis.

The synthetic fixture is intentionally controlled. Passing it establishes technical feasibility against the frozen oracle, not market validation.

## Commercial threshold status

**Not yet evaluated.**

The frozen commercial support threshold requires either:

- at least 25% less assessment/reporting time than the human baseline; or
- at least 2 additional material evidence problems detected without a material false-positive increase.

No valid conclusion can be drawn on that threshold until the human baseline is executed and recorded.

## Next gate

After CI confirms this combined assessment, the next discovery activity should be the frozen **human baseline**, not another connector and not a commercial dashboard. A competent QA practitioner should inspect the same underlying source dataset without BGSTM assistance, with time, findings, false positives/negatives, inspected artifacts, release recommendation, confidence, and reporting time recorded using the fields already frozen in the fixture contract.

Only after that baseline should the project make a commercial-support judgment and decide whether to proceed to the Azure DevOps adversarial proof.
