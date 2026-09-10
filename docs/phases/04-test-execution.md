# Phase 4: Test Execution

## Overview
Test Execution is the phase where approved tests are run, observed behavior is compared with expected behavior, defects and blockers are documented, and evidence is collected for later analysis and reporting. Execution may be manual, automated, exploratory, or a combination of approaches defined during planning.

## Objectives
- Execute tests according to the approved plan and priorities
- Record reliable, reproducible results and supporting evidence
- Identify and document defects and blockers
- Verify fixes and perform appropriate regression testing
- Track progress, coverage, risks, and environment constraints
- Preserve traceability from requirements through tests to results

## Key Activities

### 1. Test Execution Preparation
- Confirm that Phase 3 readiness criteria are satisfied
- Review the planned scope, priorities, entry criteria, and approved test cases
- Verify test data, accounts, integrations, and required access
- Confirm the build/version and environment being tested
- Establish how results, evidence, defects, and blockers will be recorded

### 2. Test Case Execution

#### Manual Testing
- Follow the documented test intent and steps consistently
- Record actual results and final status
- Capture screenshots, logs, recordings, or other evidence when useful
- Record deviations, observations, and environmental conditions that affect interpretation
- Mark tests Pass, Fail, Blocked, or Not Executed using agreed definitions

#### Automated Testing
- Execute the appropriate automated suites against the intended build and environment
- Preserve run identifiers, logs, reports, screenshots, traces, or other diagnostic artifacts
- Distinguish product failures from automation, data, and environment failures before classifying results
- Investigate unexpected automation failures rather than automatically treating every failed script as a product defect
- Maintain automation when application behavior or intended test coverage changes

#### Exploratory and Session-Based Testing
- Define a charter, risk, or question to investigate
- Record meaningful paths explored, data used, observations, and defects
- Convert important repeatable discoveries into durable test cases when appropriate

### 3. Defect Management

#### Defect Identification
- Compare actual behavior with requirements, acceptance criteria, or other approved expectations
- Reproduce the problem when practical
- Check whether the issue is already known
- Separate product defects from environment, data, configuration, and test-automation problems
- Assign severity and priority using project-defined criteria

#### Defect Logging
A useful defect report normally includes:
- **Defect ID**: Unique identifier
- **Summary**: Concise description
- **Description**: Relevant context and impact
- **Steps to Reproduce**: Reproducible sequence or conditions
- **Expected Result**: Intended behavior
- **Actual Result**: Observed behavior
- **Severity and Priority**: Using agreed project definitions
- **Environment and Build**: Where the problem was observed
- **Evidence**: Screenshots, logs, recordings, traces, or payloads as appropriate
- **Traceability**: Related requirement, test case, run, or workflow

Severity and priority scales should be tailored to the organization. A common starting point is Critical/High/Medium/Low severity and High/Medium/Low priority, but teams should define the business and technical meaning of each level rather than rely on labels alone.

### 4. Defect Lifecycle Management
The exact workflow varies by organization. A representative lifecycle is:
1. **New**: Defect reported and awaiting triage
2. **Assigned**: Ownership established
3. **In Progress**: Investigation or remediation underway
4. **Fixed/Ready for Retest**: Candidate fix available
5. **Retest**: Tester verifies the reported behavior
6. **Verified/Closed**: Acceptance criteria for resolution are met
7. **Reopened**: The issue remains or recurs

Record lifecycle timestamps only when the organization intends to use them for defect-lifecycle metrics.

### 5. Retesting and Regression Testing

#### Retesting
- Reproduce the original failure conditions against the candidate fix
- Verify the expected behavior and relevant edge cases
- Record the build, environment, result, and evidence

#### Regression Testing
- Select regression scope according to change impact and risk
- Execute tests covering affected workflows, integrations, and critical unaffected behavior
- Expand scope when failures indicate broader impact
- Update regression suites as product risks and architecture evolve

### 6. Test Progress Tracking
- Maintain current execution status and blocker information
- Track planned versus executed scope and requirement/risk coverage
- Monitor failed, blocked, and not-executed tests separately
- Surface environment or data constraints that reduce confidence
- Communicate material changes to schedule, scope, or release risk promptly

### 7. Execution by Test Type
Execution may include smoke, sanity, functional, integration, end-to-end, performance, security, usability, accessibility, compatibility, and other test types selected during planning. Each type should use fit-for-purpose evidence and pass/fail criteria. BGSTM does not require every project to execute every test type.

## Test Execution Strategies

### Sequential Execution
Use sequential execution when tests depend on prior state, when isolation is difficult, or when ordered workflows are themselves part of the behavior under test.

### Parallel Execution
Use parallel execution when tests and data are sufficiently independent. Validate that parallelism does not introduce shared-state interference that can make results unreliable.

### Risk-Based Execution
Execute the highest business, technical, safety, security, or change-impact risks first when early feedback is valuable or time is constrained.

### Time-Boxed and Exploratory Execution
Use a defined time box and charter to investigate uncertain or rapidly changing areas. Preserve observations and evidence so findings can be analyzed with the rest of the execution record.

## Deliverables
The exact artifact set should be proportional to project risk and governance needs. Typical Phase 4 outputs include:
- Completed test cases or automated run records with actual results and status
- Test execution logs and supporting evidence
- Defect reports linked to relevant tests, requirements, and runs
- Blocker and environment-impact records
- Updated traceability and execution coverage
- Progress metrics and interim execution reports
- Retest and regression results

These outputs become the primary evidence base for Phase 5 analysis.

## Best Practices
- Record the build, environment, data context, and execution time needed to interpret a result
- Preserve evidence proportionate to risk; do not collect artifacts that nobody can use
- Keep requirement → test → execution → defect/result traceability intact
- Investigate automation failures before classifying them as product defects
- Communicate blockers and critical failures quickly rather than waiting for a reporting cycle
- Avoid changing expected results simply to make observed behavior pass; route expectation changes through the appropriate requirement/change process
- Keep test data controlled and reproducible where practical
- Reassess regression scope when new failures reveal previously unknown impact

## Common Challenges and Responses

### Test Environment Issues
Record the affected tests and confidence impact, coordinate recovery, and use alternate or isolated environments only when they remain representative of the intended test conditions.

### Test Data Problems
Use repeatable setup/reset mechanisms where possible and distinguish invalid data setup from product behavior before logging defects.

### Blocked Test Cases
Record the blocker and affected scope, execute independent tests when possible, and escalate blockers that threaten exit criteria or critical coverage.

### Time Constraints
Use the risk model from Phase 1 to prioritize execution. Make omitted scope and residual risk explicit rather than presenting a partial run as complete coverage.

### Frequent Builds
Define which changes require smoke, targeted regression, or broader regression. Automation can shorten feedback cycles, but the selected scope should still be risk-driven.

## Metrics to Track
Select metrics because they answer a decision question, not because they are easy to count. Useful execution measures may include:
- Tests planned, executed, passed, failed, blocked, and not executed
- Execution completion percentage
- Requirement or risk coverage achieved
- Failure counts and trends by feature/module
- Environment-related blocked time
- Retest and regression outcomes
- Execution duration or suite runtime where it informs capacity or feedback speed
- Defect counts by severity/status when backed by a defect lifecycle source

A failed execution is evidence of an unsuccessful test observation; it is not automatically equivalent to a unique defect.

## Methodology-Specific Considerations
BGSTM retains the same six phases across delivery models; the cadence and formality of execution change.

- **Agile/Scrum**: Execution occurs continuously within short iterations, with rapid feedback, story/acceptance-criteria traceability, and frequent targeted regression.
- **Waterfall**: Execution is commonly organized into a formally controlled test stage with explicit entry/exit criteria, approved baselines, and comprehensive evidence.
- **DevOps/Continuous Delivery**: Automated suites may execute on every change or deployment while manual, exploratory, performance, security, and other testing is triggered according to risk and pipeline policy.
- **Hybrid**: Use the governance and cadence appropriate to the project while preserving the same Phase 4 outputs and traceability into analysis.

## Tools and Technologies
BGSTM is tool-agnostic. Teams may use test-management, defect-tracking, automation, API, performance, security, observability, and CI/CD tools that fit their environment. Tool choice should support the required evidence and traceability rather than define the methodology.

## Related Templates

### Primary Templates
- **[Test Execution Report Template](../test-templates/test-execution-report-template.md)** - Periodic execution progress, evidence, metrics, risks, and blockers
- **[Defect Report Template](../test-templates/defect-report-template.md)** - Reproducible defect documentation and lifecycle tracking

### Supporting Templates
- **[Test Case Template](../test-templates/test-case-template.md)** - Expected/actual results and execution status
- **[Traceability Matrix Template](../test-templates/traceability-matrix-template.md)** - Requirement-to-test coverage and execution status

## Examples
- [Defect Report Example](../examples/defect-report-example.md) - Realistic defect documentation across multiple severity levels, including reproduction, evidence, resolution, and verification.
- [Six-Phase Checkout Worked Example](../examples/six-phase-checkout-worked-example.md) - Shows how Phase 4 execution evidence flows into analysis and reporting in one end-to-end scenario.

## Previous Phase
[Test Environment Preparation](03-test-environment-preparation.md)

## Next Phase
Proceed to [Phase 5: Test Results Analysis](05-test-results-analysis.md) when sufficient execution evidence exists to assess quality, coverage, and residual risk. In iterative delivery, Phase 5 analysis can occur continuously while additional Phase 4 execution continues.
