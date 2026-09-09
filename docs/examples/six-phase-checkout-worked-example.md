# BGSTM End-to-End Worked Example: Guest Checkout

This example shows how one realistic software change moves through the **six core BGSTM testing phases** from planning through final reporting. It is intended as the shortest practical path for readers who understand the phase definitions but want to see how the methodology works as a connected system.

> **BGSTM has exactly six core testing phases.** The activities below may overlap or iterate in Agile, Scrum, Waterfall, or hybrid delivery, but they remain the same six phases.

## Scenario

ShopFlow is adding **guest checkout** to its e-commerce checkout flow. A customer must be able to purchase without creating an account, enter shipping and payment information, review the order, submit it once, and receive confirmation.

For this worked example, assume these requirements:

| Requirement | Expected behavior | Risk |
|---|---|---|
| REQ-GC-01 | A guest can begin checkout without registering | High |
| REQ-GC-02 | Required shipping fields are validated | High |
| REQ-GC-03 | A valid payment can create exactly one order | Critical |
| REQ-GC-04 | Failed payment does not create an order | Critical |
| REQ-GC-05 | Successful checkout displays and sends confirmation | High |
| REQ-GC-06 | The critical guest flow works on supported desktop and mobile browsers | High |

The purpose is not to prescribe a particular test-management or automation product. The same BGSTM reasoning applies whether evidence is recorded manually, in a test-management platform, in CI, or through an automation framework.

## Phase 1 — Test Planning

### Question

**What are we testing, why does it matter, and what evidence will be sufficient to make a release decision?**

### Activities

The QA lead reviews the guest-checkout requirements with product, development, security, and operations. The team identifies payment and duplicate-order behavior as the highest risks and decides that the critical path requires functional, API/integration, negative, browser/mobile, and regression coverage.

The plan establishes:

- in-scope and out-of-scope behavior;
- risk and priority for each requirement;
- test levels and test types;
- environment, data, tooling, and staffing needs;
- entry, suspension, resumption, and exit criteria;
- expected test evidence and reporting cadence.

### Example decisions

- REQ-GC-03 and REQ-GC-04 receive the deepest negative and integration coverage because payment/order integrity is release-critical.
- Smoke tests run on every candidate build; the critical regression suite runs in CI.
- Release exit requires all critical/high tests executed, no unresolved critical/high defects, and explicit disposition of residual risk.

### Outputs

- [Test Plan Template](../test-templates/test-plan-template.md)
- [Risk Assessment Template](../test-templates/risk-assessment-template.md)
- [ShopFlow Test Plan Example](test-plan-example.md)
- [Risk Assessment Example](risk-assessment-matrix-example.md)

**Traceability checkpoint:** every in-scope requirement has a risk classification and a planned validation approach.

---

## Phase 2 — Test Case Development

### Question

**What specific observations will prove or disprove the expected behavior?**

### Activities

The team turns requirements and risks into test conditions, test cases, data, and automation candidates. Positive-path coverage alone is insufficient for a payment flow, so cases include validation boundaries, failures, retries, navigation, session behavior, and integration responses.

### Representative test cases

| Test case | Requirement(s) | Expected result | Automation candidate |
|---|---|---|---|
| TC-GC-001 Successful guest checkout | 01, 02, 03, 05 | One order is created and confirmation is produced | Yes |
| TC-GC-002 Missing required shipping field | 02 | User cannot continue; field-level validation is shown | Yes |
| TC-GC-003 Declined payment | 03, 04 | Payment failure is shown and no order is created | Yes |
| TC-GC-004 Double-submit protection | 03 | Repeated submission creates only one order | Yes |
| TC-GC-005 Confirmation email | 05 | Email contains the correct order and shipping details | Partial |
| TC-GC-006 Mobile critical path | 06 | Checkout remains usable and completes on target device/browser | Yes |

The traceability matrix is updated before execution so uncovered requirements are visible rather than discovered at the end.

### Outputs

- [Test Case Template](../test-templates/test-case-template.md)
- [Traceability Matrix Template](../test-templates/traceability-matrix-template.md)
- [ShopFlow Test Case Suite Example](test-case-suite-example.md)
- [Traceability Matrix Example](traceability-matrix-example.md)

**Traceability checkpoint:** each requirement maps to one or more test cases, and each critical risk has explicit positive and negative coverage.

---

## Phase 3 — Test Environment Preparation

### Question

**Can the planned tests run in a controlled environment whose results we can trust?**

### Activities

QA and DevOps prepare a production-representative QA environment. The payment provider runs in sandbox mode; email is routed to a test mailbox; test products and guest identities are seeded; supported browsers are available; logging is enabled so UI results can be correlated with API and order records.

Before formal execution, the team verifies:

- the intended application build is deployed;
- database schema and seed data match the test baseline;
- payment, shipping, and email integrations are reachable or deliberately mocked;
- test credentials and permissions work;
- automation runners and browser versions are known;
- logs and diagnostic evidence can be retrieved;
- a smoke test proves the environment is testable.

A failed environment-readiness check is treated as an environment problem, not a product test failure.

### Outputs

- [Environment Setup Example](environment-setup-example.md)
- environment/version record;
- test-data baseline;
- smoke-test evidence;
- dependency status and known limitations.

**Traceability checkpoint:** the execution record can identify the build, environment, data baseline, and dependency configuration that produced a result.

---

## Phase 4 — Test Execution

### Question

**What actually happens when the planned tests are run?**

### Activities

The team executes risk-prioritized smoke, functional, integration, negative, regression, and browser/mobile tests. Each result records enough evidence to reproduce and assess the outcome.

Example execution snapshot:

| Test case | Result | Evidence / observation |
|---|---|---|
| TC-GC-001 | Pass | One payment and one order recorded; confirmation page displayed |
| TC-GC-002 | Pass | Required address validation blocks progression |
| TC-GC-003 | Pass | Decline displayed; order count unchanged |
| TC-GC-004 | **Fail** | Rapid second submit produces a second order |
| TC-GC-005 | Pass | Test mailbox receives correct confirmation |
| TC-GC-006 | Pass | Critical path completes on target mobile browser |

TC-GC-004 produces `DEF-GC-001 — Duplicate order created when Place Order is submitted twice`. The defect is linked back to REQ-GC-03 and the failing test, with build, environment, steps, expected/actual behavior, logs, and severity.

After a fix is deployed, TC-GC-004 is rerun and the relevant regression subset is executed before the defect is closed.

### Outputs

- [Test Execution Report Template](../test-templates/test-execution-report-template.md)
- [Defect Report Template](../test-templates/defect-report-template.md)
- [Defect Report Examples](defect-report-example.md)
- execution logs, screenshots, API responses, CI results, or equivalent evidence.

**Traceability checkpoint:** every executed result can be traced to its test case and requirement; every defect can be traced to the evidence that exposed it.

---

## Phase 5 — Test Results Analysis

### Question

**What do the accumulated results mean for product quality and release risk?**

### Activities

BGSTM analysis is more than counting passes and failures. The team examines coverage, defect severity and concentration, repeated failure patterns, blocked/not-run tests, regression results, and the relationship between defects and business risk.

For the guest-checkout example, the first execution cycle shows 5/6 representative tests passing but the failed test covers the critical order-integrity requirement. A raw 83% pass rate therefore does **not** justify release. The severity and requirement affected matter more than the aggregate percentage.

After the duplicate-order fix:

- TC-GC-004 passes on retest;
- the critical checkout regression subset remains green;
- no other open defect affects a critical/high requirement;
- all six example requirements retain executed coverage;
- no environment limitation invalidates the evidence.

The team records any accepted residual risks rather than allowing them to disappear behind a green percentage.

### Outputs

- coverage and traceability assessment;
- pass/fail/block/not-run analysis;
- defect severity, clustering, and trend analysis;
- regression impact assessment;
- residual-risk statement;
- release recommendation input.

**Traceability checkpoint:** release risk is explained in terms of requirements, test evidence, and defects—not only test counts.

---

## Phase 6 — Test Results Reporting

### Question

**What should stakeholders know, and what decision does the evidence support?**

### Activities

The test lead converts the analysis into a concise, auditable report for the people making the release decision. The report distinguishes facts, unresolved risk, and recommendation.

### Example final summary

> Guest Checkout Release Candidate 3.5.0-RC2 completed planned critical/high validation. All six in-scope example requirements have executed coverage. The critical duplicate-order defect found during TC-GC-004 was fixed, retested successfully, and followed by a passing critical checkout regression run. No critical or high defects remain open. Known low-risk cosmetic issues are documented and accepted. QA recommends release from the tested scope, environment, and build represented by this evidence.

The recommendation does not claim that testing proves the absence of defects. It states what was tested, what was observed, what risk remains, and why the evidence supports the decision.

### Outputs

- [Test Summary Report Template](../test-templates/test-summary-report-template.md)
- final traceability status;
- defect disposition;
- residual risks and exceptions;
- release recommendation and stakeholder sign-off where required.

**Traceability checkpoint:** a stakeholder can move backward from the release recommendation to analysis, execution evidence, test cases, requirements, and the original plan.

---

## The Evidence Chain

The six phases form a connected evidence chain:

```text
Risk and requirements
        ↓
Phase 1: Test Planning
        ↓
Phase 2: Test Case Development
        ↓
Phase 3: Test Environment Preparation
        ↓
Phase 4: Test Execution
        ↓
Phase 5: Test Results Analysis
        ↓
Phase 6: Test Results Reporting
        ↓
Evidence-based quality / release decision
```

Iteration does not change the model. A defect may send the team back to refine a test case, prepare new data, or repeat execution and analysis. In an Agile sprint, several phases may operate continuously or in parallel. In a Waterfall project, the same phases may be separated by formal gates. BGSTM provides the testing structure while the delivery methodology determines cadence and governance.

## One-Page Artifact Map

| BGSTM phase | Primary artifact/evidence | What it answers |
|---|---|---|
| 1. Test Planning | Test plan + risk assessment | What and why will we test? |
| 2. Test Case Development | Test cases + traceability matrix | How will we verify it? |
| 3. Test Environment Preparation | Environment/data readiness evidence | Can we trust the test conditions? |
| 4. Test Execution | Results + defects + raw evidence | What happened? |
| 5. Test Results Analysis | Coverage/defect/risk analysis | What do the results mean? |
| 6. Test Results Reporting | Test summary + recommendation | What should stakeholders decide? |

## Continue From Here

- Read the [six phase definitions](../phases/index.md) for detailed guidance.
- Use the [canonical BGSTM templates](../test-templates/index.md) to create your own artifacts.
- Explore the [full ShopFlow examples](index.md) for larger sample documents.
- See [ETL Semantic Validation](etl-semantic-validation-example.md) for a specialized domain applying the same six phases.

This worked example is intentionally technology-agnostic. BGSTM can use manual testing, automation, AI-assisted testing, CI/CD integrations, or specialized platforms as implementation mechanisms without making any of them an additional methodology phase.