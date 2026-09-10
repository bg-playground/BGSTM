# Minimum Viable BGSTM Adoption Path

Use this page when you need to apply BGSTM to a real project quickly without first implementing every template, tool integration, training activity, or maturity practice in the broader [Getting Started guide](GETTING-STARTED.md).

> **This is a minimum adoption path, not a reduced methodology.** BGSTM still has exactly six core phases. The goal is to preserve the smallest credible evidence chain across all six while tailoring artifact depth to project risk, governance, and delivery context.

The FastAPI/React reference application is optional. You can follow this path with documents, spreadsheets, an existing test-management platform, issue tracking, automation tools, or another workflow that preserves the required evidence and traceability.

## The minimum credible evidence chain

| BGSTM phase | Minimum evidence to establish | Canonical support | Tailoring guidance |
|---|---|---|---|
| **1. Test Planning** | What is in scope, what matters most, major risks, test objectives, responsibilities, and the criteria for deciding when testing is sufficient | [Test Plan Template](test-templates/test-plan-template.md), [Risk Assessment Template](test-templates/risk-assessment-template.md) | A small or low-risk change may use a concise plan and risk list rather than a long formal document |
| **2. Test Case Development** | Tests that cover important requirements and risks, with clear expected outcomes and enough traceability to know what has and has not been tested | [Test Case Template](test-templates/test-case-template.md), [Traceability Matrix Template](test-templates/traceability-matrix-template.md) | Use the level of test-case detail needed for repeatability, review, automation, and auditability; do not create documentation merely for volume |
| **3. Test Environment Preparation** | Evidence that the build, environment, access, dependencies, test data, and required integrations are ready for the planned testing | [Phase 3 guidance](phases/03-test-environment-preparation.md), [Environment Setup Example](examples/environment-setup-example.md) | The readiness record can be a checklist or section of the test plan when a dedicated environment document would add little value |
| **4. Test Execution** | Actual results, build/environment context, retained evidence for material failures, and defects or blockers recorded so another person can understand what happened | [Test Execution Report Template](test-templates/test-execution-report-template.md), [Defect Report Template](test-templates/defect-report-template.md) | Manual, automated, exploratory, and mixed execution are all valid; preserve evidence appropriate to risk |
| **5. Test Results Analysis** | An assessment of coverage, failures, unresolved issues, evidence gaps, and residual risk—not just an aggregate pass rate | [Phase 5 guidance](phases/05-test-results-analysis.md), [Risk Assessment Template](test-templates/risk-assessment-template.md) | Use metrics only when their data and semantics are trustworthy. A failed execution is not automatically a unique defect |
| **6. Test Results Reporting** | A stakeholder-facing conclusion describing what was tested, what the evidence shows, what remains uncertain, and the release/readiness recommendation | [Test Summary Report Template](test-templates/test-summary-report-template.md) | Reporting can be lightweight or formal, but the decision, rationale, limitations, and residual risk should be explicit |

The evidence should connect across phases rather than exist as six isolated documents:

**scope and risk → requirements/tests → environment readiness → execution evidence → analysis → decision/report**

That chain is more important than the number of files or tools used to represent it.

## A practical first week

### Day 1 — Establish intent and risk

Start with Phase 1. Define the project or release scope, the most important business and technical risks, testing objectives, responsibilities, major dependencies, and the conditions that will support a release/readiness decision.

For a small project, a concise test plan and prioritized risk list are sufficient. For regulated, safety-critical, high-value, or otherwise high-risk work, use the fuller canonical templates and the governance your organization requires.

### Day 2 — Connect requirements and tests

Use Phase 2 to identify the requirements, workflows, and risks that require evidence. Create or select tests with explicit expected outcomes, then establish enough traceability to answer two questions:

1. What important requirement or risk does this test address?
2. Which important requirements or risks still lack sufficient test coverage?

The [Traceability Matrix Template](test-templates/traceability-matrix-template.md) is useful when the relationship is not already visible in your existing tooling.

### Day 3 — Prove readiness before trusting results

Use Phase 3 to verify the environment, build, data, accounts, permissions, dependencies, and integrations needed for execution. Record material differences from production or other limitations that could weaken confidence in the results.

Do not treat a test result as reliable evidence when the environment or data state needed to interpret it is unknown.

### Day 4 — Execute and retain evidence

Use Phase 4 to run the planned tests and record results consistently. Preserve enough evidence to reproduce or understand important failures, distinguish product problems from automation/environment/data failures, and log defects and blockers with traceability back to the affected test or requirement.

If time is constrained, prioritize execution using the risks established in Phase 1 and make omitted scope explicit.

### Day 5 — Analyze, report, and make residual risk visible

Use Phase 5 to interpret the results. Look at coverage, failure concentration, unresolved defects or blockers, retest/regression outcomes, and areas where evidence is still missing. Avoid treating a high pass rate as sufficient evidence when critical behavior is untested or failing.

Then complete Phase 6 with a concise stakeholder report or release recommendation that states:

- what scope was tested;
- what evidence supports the conclusion;
- critical unresolved issues;
- known limitations or evidence gaps;
- residual risk;
- the recommended decision and rationale.

## Minimum does not mean identical everywhere

BGSTM is methodology-agnostic. Agile, Scrum, Waterfall, continuous-delivery, and hybrid teams can use the same six phases while varying cadence, overlap, approval formality, and artifact weight.

Use more structure when the consequences of being wrong are high, when many teams depend on the evidence, when compliance or auditability matters, or when the work will be repeated by people who were not part of the original testing. Use lighter artifacts when the project is small, low-risk, short-lived, and the same information is already captured reliably elsewhere.

The following are **not required simply to claim BGSTM adoption**:

- a particular test-management platform;
- a specific automation framework;
- the BGSTM reference application;
- a prescribed percentage of automated tests;
- every optional template in the repository;
- a fixed number of test cases or metrics;
- a new phase for a specialized domain.

Specialized work such as ETL semantic validation still applies the same six phases. See the [ETL Semantic Validation Applied Example](examples/etl-semantic-validation-example.md) for one domain-specific application.

## See the complete lifecycle once

Before scaling BGSTM across a team, review the [Six-Phase Checkout Worked Example](examples/six-phase-checkout-worked-example.md). It shows one continuous evidence chain from planning and risk through test design, environment readiness, execution, analysis, and reporting.

For rollout planning, maturity assessment, tooling, training, and longer-term continuous improvement, continue with the full [Getting Started guide](GETTING-STARTED.md).
