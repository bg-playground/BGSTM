# BGSTM Evidence Spine Fixture Contract v0

**Status:** Frozen discovery fixture contract  
**Date:** 2026-09-10  
**Implements:** `quality-evidence-model-v0.md` experiment definition  
**Production implementation:** Not authorized by this document

## 1. Purpose

This document freezes the controlled dataset, expected findings, control cases, and acceptance assertions for the BGSTM Evidence Spine experiment before evaluator implementation begins.

The experiment must not redefine expected outcomes after results are observed.

The working question is:

> Can BGSTM reconstruct enough cross-tool quality context to identify meaningful evidence defects that are not obvious from simple artifact aggregation?

## 2. Source-system responsibilities

The first experiment uses four systems of record:

- **OpenProject** — requirements, risks, and declared changes;
- **Playwright** — test cases and executions;
- **GitHub Actions** — candidate commit/build identity and workflow evidence;
- **Bugzilla** — defect state and defect verification context.

BGSTM may normalize facts from these systems, but the source artifacts remain authoritative.

## 3. Candidate release

The frozen candidate release is:

```text
release_id: REL-001
name: Checkout Reliability Candidate 1
candidate_sha: sha-candidate-003
release_time: 2026-09-10T14:00:00Z
```

The fixture represents an intentionally imperfect checkout release containing both valid and invalid quality evidence.

## 4. Stable entity IDs

### 4.1 Requirements

```text
REQ-001 Authentication required before checkout
REQ-002 Supported browsers must complete checkout
REQ-003 Payment authorization failure must not create an order
REQ-004 Shipping option selection must persist through review
REQ-005 Order totals must remain consistent across checkout steps
REQ-006 Successful payment must produce one order confirmation
REQ-007 Checkout must retain cart contents during transient retry
REQ-008 Checkout audit events must contain release/build identity
```

### 4.2 Risks

```text
RISK-001 Unauthorized checkout completion
RISK-002 Browser-specific checkout failure
RISK-003 Duplicate or invalid order creation after payment failure
RISK-004 Incorrect order totals
RISK-005 Missing release auditability
```

### 4.3 Quality obligations

```text
QO-001 Authentication flow must be validated on the candidate build.
QO-002 Supported-browser checkout evidence must include Chromium and Firefox on the approved checkout environment.
QO-003 Payment failure handling must prove that no order is created.
QO-004 Order-total validation must execute after the pricing-rule change that affects totals.
QO-005 Closed checkout defects must have post-fix verification on a build containing the fix.
QO-006 Release audit evidence must identify the candidate SHA.
QO-007 Contradictory qualifying results must be reconciled before release confidence is considered high.
```

### 4.4 Test cases

```text
TC-001 authenticated checkout succeeds
TC-002 unauthenticated checkout is rejected
TC-003 Chromium checkout succeeds
TC-004 Firefox checkout succeeds
TC-005 payment-decline creates no order
TC-006 shipping selection persists
TC-007 totals remain stable through review
TC-008 order confirmation created exactly once
TC-009 cart retained after transient retry
TC-010 audit event contains build identity
TC-011 legacy coupon regression
TC-012 checkout smoke
```

### 4.5 Environment definitions and instances

```text
ENVDEF-001 approved-checkout
  required_browser_set: [chromium, firefox]
  identity_mode: production-equivalent
  payment_mode: sandbox

ENV-001 approved-checkout-instance
  definition: ENVDEF-001
  identity_mode: production-equivalent
  payment_mode: sandbox

ENV-002 developer-local
  definition: ad-hoc-local
  identity_mode: mock
  payment_mode: stub
```

### 4.6 Changes

```text
CHG-001 authentication middleware hardening
  introduced_sha: sha-change-001
  affected_requirement: REQ-001

CHG-002 pricing-rule update
  introduced_sha: sha-change-002
  affected_requirement: REQ-005

CHG-003 checkout audit metadata update
  introduced_sha: sha-candidate-003
  affected_requirement: REQ-008
```

### 4.7 Executions

```text
RUN-001
  sha: sha-before-change
  environment: ENV-001
  executed_at: 2026-09-08T10:00:00Z

RUN-002
  sha: sha-candidate-003
  environment: ENV-002
  executed_at: 2026-09-10T10:00:00Z

RUN-003
  sha: sha-candidate-003
  environment: ENV-001
  executed_at: 2026-09-10T12:00:00Z
```

### 4.8 Defects

```text
BUG-001 duplicate order after payment retry
  status: CLOSED FIXED
  fix_sha: sha-fix-bug-001

BUG-002 Firefox checkout submit failure
  status: CLOSED FIXED
  fix_sha: sha-candidate-003

BUG-003 incorrect shipping selection persistence
  status: OPEN

BUG-004 audit event missing candidate SHA
  status: CLOSED FIXED
  fix_sha: sha-candidate-003
```

## 5. Frozen semantic relationships

The fixture must include these minimum relationships:

```text
REQ-001 INTRODUCES RISK-001
REQ-002 INTRODUCES RISK-002
REQ-003 INTRODUCES RISK-003
REQ-005 INTRODUCES RISK-004
REQ-008 INTRODUCES RISK-005

RISK-001 MITIGATED_BY QO-001
RISK-002 MITIGATED_BY QO-002
RISK-003 MITIGATED_BY QO-003
RISK-004 MITIGATED_BY QO-004
RISK-005 MITIGATED_BY QO-006

QO-001 SATISFIED_BY TC-001
QO-001 SATISFIED_BY TC-002
QO-002 SATISFIED_BY TC-003
QO-002 SATISFIED_BY TC-004
QO-003 SATISFIED_BY TC-005
QO-004 SATISFIED_BY TC-007
QO-006 SATISFIED_BY TC-010
```

`QO-005` applies to defects marked fixed/closed. `QO-007` applies when two qualifying observations conflict.

## 6. Frozen execution facts

The implementation fixture must represent these facts without reinterpretation.

### RUN-001 — stale but otherwise valid historical run

- `TC-001`: PASS
- `TC-002`: PASS
- `TC-003`: PASS
- `TC-004`: PASS
- `TC-005`: PASS
- `TC-006`: PASS
- `TC-007`: PASS
- `TC-008`: PASS
- `TC-009`: PASS
- `TC-010`: PASS

`RUN-001` predates `CHG-001`, `CHG-002`, and the candidate SHA.

### RUN-002 — candidate run on non-qualifying local environment

- `TC-003`: PASS
- `TC-004`: PASS
- `TC-005`: PASS
- `TC-011`: PASS

Because `RUN-002` uses `ENV-002`, it cannot satisfy obligations that require `ENVDEF-001`.

### RUN-003 — candidate run on approved environment

- `TC-001`: PASS
- `TC-002`: PASS
- `TC-003`: PASS
- `TC-004`: FAIL
- `TC-005`: PASS
- `TC-006`: PASS
- `TC-007`: PASS
- `TC-008`: PASS
- `TC-009`: PASS
- `TC-010`: PASS
- `TC-012`: PASS

The fixture must also contain a second qualifying observation for `TC-004` on the same candidate and approved environment reporting `PASS`, creating an unresolved contradiction.

## 7. Seven injected evidence failures and expected findings

The following expected findings are frozen before evaluator implementation.

### F-001 — Uncovered risk

**Injected condition:** `RISK-003` is material, but the evidence chain proving the no-order side effect is intentionally incomplete. `TC-005` passes, but no qualifying evidence artifact records the required postcondition that no order was created.

**Expected finding:** BGSTM reports `QO-003` as unsupported or insufficiently supported rather than treating the test-case PASS alone as conclusive.

### F-002 — Stale execution

**Injected condition:** `TC-007` passed in `RUN-001`, but `CHG-002` changed pricing behavior afterward. The candidate execution evidence must be considered when deciding current support.

**Expected finding:** Any claim relying only on the pre-change `RUN-001` result is stale. The evaluator must identify the invalidation relationship, not merely report that a test exists.

### F-003 — Environment mismatch

**Injected condition:** `TC-003` and `TC-004` both pass in `RUN-002`, but `RUN-002` uses `ENV-002`, which does not satisfy `QO-002`.

**Expected finding:** `RUN-002` cannot qualify as supported-browser release evidence even though the tests passed.

### F-004 — Unverified defect closure

**Injected condition:** `BUG-001` is closed/fixed, but no execution on a build containing `sha-fix-bug-001` is linked as post-fix verification.

**Expected finding:** BGSTM reports missing qualifying post-fix verification for `BUG-001` under `QO-005`.

### F-005 — Orphan test

**Injected condition:** `TC-011` executes successfully but is intentionally not related to any requirement, risk, objective, obligation, or release criterion.

**Expected finding:** BGSTM reports `TC-011` as semantically orphaned. This is an evidence-model finding, not a test failure.

### F-006 — Outdated traceability

**Injected condition:** The stored relationship between `REQ-001` and its validating evidence was last confirmed before `CHG-001` modified the requirement-relevant authentication behavior.

**Expected finding:** BGSTM reports the traceability/evidence relationship as requiring revalidation because the source revision changed after the relationship was established.

### F-007 — Contradictory evidence

**Injected condition:** Two qualifying candidate observations for `TC-004` on the approved environment disagree: one PASS and one FAIL.

**Expected finding:** BGSTM reports an unresolved contradiction and requires human review. It must not silently choose the latest, best, passing, or failing result unless a deterministic policy explicitly authorizes that resolution.

## 8. Control cases that must not be reported as failures

The evaluator must avoid obvious false positives.

```text
C-001 TC-001 and TC-002 in RUN-003 are current and on ENV-001; QO-001 is supported.
C-002 TC-007 in RUN-003 is current after CHG-002; QO-004 is supported by candidate evidence.
C-003 BUG-002 is closed and has candidate-build verification; do not report missing post-fix verification.
C-004 BUG-004 is closed and TC-010 in RUN-003 verifies candidate-SHA audit identity; do not report missing verification.
C-005 TC-006, TC-008, TC-009, and TC-012 may be useful evidence even though they are not among the seven primary obligation mappings; do not classify them as failures solely because they are secondary evidence.
```

## 9. Deterministic evaluation rules

The first evaluator may use simple explicit rules. It must not require an LLM.

Minimum rules:

1. **Freshness rule** — evidence that predates an affecting change cannot by itself satisfy an obligation requiring current behavior.
2. **Candidate identity rule** — release evidence must resolve to the candidate SHA when the obligation is release-specific.
3. **Environment qualification rule** — executions on environments that do not satisfy declared environment properties do not satisfy those obligations.
4. **Defect verification rule** — a closed/fixed defect requiring verification must have a qualifying execution on a build containing the fix.
5. **Semantic orphan rule** — a test/evidence artifact with no meaningful intent relationship may be reported as orphaned.
6. **Contradiction rule** — conflicting qualifying observations remain contradictory until an explicit reconciliation fact or rule resolves them.
7. **Evidence sufficiency rule** — a PASS result does not satisfy an obligation when the obligation requires evidence not represented by that result alone.

## 10. Required evaluator output

Each material finding must include:

```text
finding_id
claim
status
reason
confidence
quality_obligation_ids
evidence_references
source_systems
source_object_ids
source_revisions_or_timestamps
human_review_required
```

For this controlled deterministic fixture, `confidence` should normally be `1.0` for rule-based findings unless the evaluator intentionally models uncertainty.

## 11. Acceptance assertions

The implementation increment that follows this contract must demonstrate all of the following:

```text
A-001 Detect at least 6 of F-001 through F-007.
A-002 Produce no more than 2 material false positives against C-001 through C-005 and other clearly valid fixture evidence.
A-003 Every finding identifies source evidence and the rule/reason that produced it.
A-004 At least one finding requires reasoning beyond a missing-link check.
A-005 F-003 must depend on environment semantics, not merely test outcome.
A-006 F-007 must remain unresolved and require human review.
A-007 The evaluator must run without an LLM.
A-008 The evaluator must not require a graph database.
A-009 The four named systems remain represented as systems of record.
A-010 The experiment must not introduce a seventh BGSTM phase.
```

## 12. Human-baseline procedure

The comparison participant receives the same source facts without evaluator findings.

Record:

```text
participant_role
start_time
end_time
total_minutes
findings_identified
false_positives
false_negatives
source_artifacts_inspected
release_recommendation
confidence_1_to_5
reporting_minutes
```

The participant should answer the same seven evaluator questions defined in the Quality Evidence Model v0 specification.

The BGSTM-assisted result receives preliminary commercial support if it achieves either:

- at least 25% less assessment/reporting time; or
- at least 2 additional material evidence problems detected without a material increase in false positives.

## 13. Implementation boundary for the next increment

After this contract is merged, the next implementation may include only the smallest local proof necessary to exercise the frozen assertions, such as:

- JSON fixtures representing normalized source facts;
- a deterministic evaluator;
- machine-readable findings;
- automated tests for F-001 through F-007 and C-001 through C-005;
- a CLI or test entry point only if useful for repeatability.

The next increment must not introduce:

- production connector infrastructure;
- a commercial dashboard;
- a graph database by default;
- enterprise authentication or tenancy;
- NAT orchestration;
- AI/LLM interpretation;
- proprietary release-readiness scoring;
- broad connector coverage.

## 14. Change control

Once merged, this document is the frozen v0 experiment oracle.

If implementation exposes an ambiguity or invalid assumption, the contract may be amended only through a separate reviewed change that:

1. identifies the ambiguity;
2. explains why the original expectation is invalid or incomplete;
3. preserves the distinction between fixing the experiment and moving the goalposts;
4. updates affected acceptance assertions explicitly.

A failed experiment remains an acceptable discovery result.