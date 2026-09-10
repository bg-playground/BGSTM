# Phase 5: Test Results Analysis

## Overview
Test Results Analysis converts execution evidence into an assessment of product quality, test completeness, and residual risk. The purpose is not to produce the largest possible collection of metrics; it is to explain what the evidence means and what decisions it supports.

## Objectives
- Consolidate and validate evidence from Test Execution
- Identify meaningful failure, defect, coverage, and risk patterns
- Assess confidence against the objectives and exit criteria established during planning
- Distinguish observed facts from interpretations and predictions
- Identify unresolved risks, evidence gaps, and recommended actions
- Prepare decision-ready conclusions for Phase 6 reporting

## Key Activities

### 1. Validate and Consolidate the Evidence
Before calculating metrics, confirm that the underlying data is interpretable:
- Identify the build, environment, test window, and scope represented
- Reconcile duplicate or retried executions where appropriate
- Separate product failures from automation, environment, configuration, and test-data failures
- Check for missing or blocked critical coverage
- Confirm that requirement, test, execution, and defect identifiers remain traceable
- Document material limitations in the available evidence

### 2. Analyze Test Execution Results
Evaluate:
- Planned versus executed tests
- Pass, fail, blocked, and not-executed counts
- Changes in results across builds, cycles, or iterations
- Concentrations of failures by feature, module, workflow, risk, platform, or environment
- Retest and regression outcomes
- Evidence that exit criteria have or have not been satisfied

A failed execution is not necessarily a unique defect. Multiple failures may represent one underlying defect, and a single defect may affect many tests.

### 3. Analyze Defects When Lifecycle Data Exists
Useful defect analysis can include:
- Distribution by severity, priority, module, type, or root cause
- Open versus closed trends
- Defect aging
- Reopen rate
- Defect density using a clearly defined denominator
- Time from defect creation to accepted resolution
- Escaped/post-release defects when a production defect source exists

Do not infer defect-lifecycle measures solely from test execution rows. If the system records only failed and later passing executions, describe that evidence as execution recovery/time-to-green rather than defect repair time.

### 4. Analyze Coverage

#### Requirements Coverage
- Percentage of in-scope requirements linked to tests
- Requirements without tests or without completed execution evidence
- Critical requirement validation status
- Traceability gaps that reduce confidence

#### Code Coverage, When Applicable
Statement, branch, condition, or other code-coverage measures can supplement test evidence, but high code coverage does not by itself demonstrate adequate behavioral or risk coverage.

#### Risk Coverage
Assess whether the highest-priority risks identified during planning received sufficient test depth and whether residual risk remains acceptable.

### 5. Assess Test Effectiveness
Consider questions such as:
- Did the test set expose meaningful product risks and failures?
- Are repeated failures concentrated in particular workflows or components?
- Are tests redundant, unstable, obsolete, or missing important scenarios?
- Are escaped defects revealing gaps in requirements, design, test coverage, or release controls?
- Is automation improving feedback without creating misleading confidence?

### 6. Perform Root Cause and Pattern Analysis
For material or recurring failures:
- Look for common technical, requirements, process, environment, or data causes
- Use evidence such as logs, traces, defect history, and change history
- Distinguish correlation from demonstrated causation
- Identify systemic improvements rather than only individual fixes

### 7. Reassess Release and Quality Risk
Update the Phase 1 risk view using current evidence:
- Unresolved critical/high-impact defects
- Missing or blocked critical coverage
- Known limitations and workarounds
- Environment or data limitations
- Performance, security, accessibility, reliability, or compatibility concerns
- Areas where evidence is insufficient to support a confident conclusion

Analysis should support a recommendation and its rationale; the final release authority remains with the organization-defined decision makers.

## Analysis Techniques
Use the simplest technique that answers the decision question reliably. Common techniques include:
- Trend analysis across runs, builds, sprints, or releases
- Pareto analysis to identify concentrated recurring problems
- Distribution and aging analysis for defect lifecycle data
- Coverage matrices and gap analysis
- Failure clustering by module, workflow, risk, platform, or root cause
- Statistical summaries where sample size and data quality justify them
- Visualizations that expose patterns without hiding raw counts or denominators

Predictive models can be useful when enough trustworthy historical data exists, but predictions should not be presented as observed quality evidence.

## Deliverables
Typical Phase 5 outputs include:
- Validated analysis dataset or evidence summary
- Test result and coverage analysis
- Failure and, where supported, defect trends
- Updated residual-risk assessment
- Root-cause or recurring-pattern findings
- Quality indicators with definitions and data limitations
- Release/readiness recommendation with supporting rationale
- Actionable recommendations for remediation, additional testing, or process improvement

These outputs are the analytical basis for Phase 6 reporting.

## Best Practices
- Start with the decision or risk question, then select the metric
- Preserve raw counts and denominators alongside percentages
- Define metric windows, populations, and status semantics
- Separate execution failures from unique defects
- State when data is insufficient rather than manufacturing a precise-looking metric
- Compare actual evidence with planned scope, exit criteria, and risk priorities
- Explain important trends and exceptions, not just dashboard values
- Keep conclusions traceable to the evidence that supports them
- Record assumptions and known data-quality limitations

## Common Challenges and Responses

### Too Many Metrics Without Purpose
Retain measures that inform quality, risk, capacity, or a concrete decision. Remove vanity metrics and duplicated indicators.

### Data Quality and Consistency Problems
Establish stable identifiers, agreed status definitions, reliable timestamps, and validation rules. Document unresolved gaps before interpreting the data.

### Analysis Paralysis
Begin with release objectives, critical risks, exit criteria, and major failures. Add deeper analysis only where it can change understanding or action.

### Limited Historical Data
Use current evidence as a documented baseline. Avoid presenting external benchmarks as direct proof that the product meets its own quality goals.

### Stakeholder Disagreement
Make definitions, assumptions, raw counts, and evidence accessible so disagreement can focus on risk tolerance and decision criteria rather than hidden calculations.

## Metric Semantics
Metric names must match the evidence actually available.

### Execution Metrics
Examples include execution volume, pass/fail/blocked rates, requirement coverage, automation coverage, recurring failed-test patterns, and **execution Mean Time to Recovery (time-to-green)**. Execution recovery measures the interval from the opening failed execution in a failure episode to a subsequent passing execution for the same stable test identity. It is useful operational evidence, but it is **not defect MTTR**.

### Defect-Lifecycle Metrics
Metrics such as defect age, mean time to repair/resolution, reopen rate, and defect closure rate require a defect system with meaningful lifecycle states and timestamps. A true defect MTTR should be calculated from the organization's defined defect-open and accepted-resolution events, not reconstructed from unrelated execution records.

### Post-Release Metrics
Defect Removal Efficiency, escape rate, and similar measures require a trustworthy source for production/post-release defects and a defined attribution window. If that source does not exist, report the metric as unsupported rather than treating zero as evidence of no escaped defects.

### Reliability and Business Metrics
Measures such as MTBF or customer satisfaction require operational or customer data beyond normal test execution evidence. Use them only when the relevant source and definition are available.

## Methodology-Specific Considerations
BGSTM keeps the same six phases across delivery models; the cadence of analysis changes.

- **Agile/Scrum**: Analyze continuously within the iteration and use findings for story acceptance, release decisions, retrospectives, and backlog refinement.
- **Waterfall**: Consolidate analysis around formal test cycles and phase gates, with documented exit-criteria and residual-risk review.
- **DevOps/Continuous Delivery**: Automate trustworthy evidence collection and trend analysis where practical, while retaining human review for ambiguous failures and risk decisions.
- **Hybrid**: Combine the cadence and governance appropriate to the project without changing Phase 5's purpose or evidence standards.

## Decision-Making Framework
A release/readiness assessment should consider:
- Critical and high-impact unresolved failures or defects
- Planned versus achieved requirement and risk coverage
- Blocked or omitted critical testing
- Performance, security, reliability, accessibility, and compatibility objectives where applicable
- Known limitations and workarounds
- Evidence quality and confidence
- Explicit acceptance of residual risk by the appropriate stakeholders

Avoid universal numerical thresholds unless the project established them during planning. A 95% pass rate, for example, may be unacceptable if the remaining 5% covers critical behavior.

## Tools and Technologies
BGSTM is tool-agnostic. Analysis can be performed in test-management and defect systems, observability platforms, BI tools, spreadsheets, statistical environments, or purpose-built dashboards. Select tools that preserve definitions, provenance, and traceability of the evidence.

## Related Templates

### Primary Templates
- **[Test Summary Report Template](../test-templates/test-summary-report-template.md)** - Decision-ready quality assessment, residual risk, and recommendation
- **[Risk Assessment Template](../test-templates/risk-assessment-template.md)** - Update residual risks using current evidence

### Supporting Templates
- **[Test Execution Report Template](../test-templates/test-execution-report-template.md)** - Execution evidence and interim metrics
- **[Traceability Matrix Template](../test-templates/traceability-matrix-template.md)** - Requirement coverage and gap analysis
- **[Defect Report Template](../test-templates/defect-report-template.md)** - Defect lifecycle evidence when applicable

## Examples
- [Risk Assessment Matrix Example](../examples/risk-assessment-matrix-example.md) - Demonstrates structured risk scoring and mitigation.
- [Six-Phase Checkout Worked Example](../examples/six-phase-checkout-worked-example.md) - Shows how execution evidence, a duplicate-order defect, coverage, and residual risk are analyzed before reporting.

## Previous Phase
[Test Execution](04-test-execution.md)

## Next Phase
Proceed to [Phase 6: Test Results Reporting](06-test-results-reporting.md) when the analysis is sufficiently stable to communicate decisions, evidence, and residual risk. In iterative delivery, reporting and analysis may occur repeatedly within the same delivery cycle.
