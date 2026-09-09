# Scrum Sprint Testing Checklist

## Overview

This checklist adapts the **six BGSTM phases** to a Scrum sprint. The phases are iterative rather than sequential: planning, test design, environment preparation, execution, analysis, and reporting can all recur during a sprint.

For ETL or data-pipeline stories, NATAegisFlow semantic-validation activities can be incorporated into the same six phases using the specialized applied example and checklist linked below.

## Pre-Sprint / Sprint Planning

### Phase 1 — Test Planning
- [ ] Review planned user stories and acceptance criteria
- [ ] Identify testing scope, dependencies, risks, and non-functional needs
- [ ] Estimate testing and automation effort
- [ ] Confirm Definition of Done includes appropriate quality criteria
- [ ] For NATAegisFlow artifact stories, define semantic-validation acceptance criteria, required evidence, and policy-gate expectations

### Phase 2 — Test Case Development
- [ ] Define test scenarios for each story
- [ ] Cover positive, negative, edge, integration, and regression scenarios
- [ ] Identify automation candidates
- [ ] Establish or update requirements-to-test traceability

### Phase 3 — Test Environment Preparation
- [ ] Confirm test environments are available and production-representative where practical
- [ ] Prepare test data and access
- [ ] Validate required tools, services, integrations, and CI/CD pipelines
- [ ] Confirm NATAegisFlow run inputs and evidence locations when applicable

## During the Sprint

### Phase 4 — Test Execution
- [ ] Test completed stories as soon as they are ready
- [ ] Execute acceptance, exploratory, integration, regression, and non-functional tests as appropriate
- [ ] Log defects with clear reproduction steps and evidence
- [ ] Retest resolved defects and check for regressions
- [ ] Maintain automated tests for new and changed functionality
- [ ] Review and disposition NATAegisFlow semantic findings for applicable stories
- [ ] Confirm required evidence is attached and patch validation is complete before acceptance

### Daily Quality Coordination
- [ ] Communicate testing progress and blockers during stand-up
- [ ] Monitor CI/CD and automated-test health
- [ ] Raise critical defects, environment issues, and requirement ambiguities promptly
- [ ] Coordinate with developers and Product Owner on quality decisions

## Sprint Review and Closeout

### Phase 5 — Test Results Analysis
- [ ] Review pass/fail status, coverage, defect trends, and open risks
- [ ] Identify gaps in planned versus completed testing
- [ ] Evaluate regression and automation effectiveness
- [ ] Assess residual risk and release readiness
- [ ] For applicable ETL work, confirm semantic findings have owners, dispositions, target dates, and gate impacts

### Phase 6 — Test Results Reporting
- [ ] Prepare a concise sprint test summary
- [ ] Report coverage, defects, risks, known limitations, and release recommendation
- [ ] Confirm Definition of Done and acceptance criteria status
- [ ] Record policy-gate approval or documented exceptions when applicable
- [ ] Archive relevant execution and approval evidence

## Sprint Retrospective

- [ ] Review what worked well and what slowed testing
- [ ] Identify recurring defect patterns or quality risks
- [ ] Assess test automation and environment reliability
- [ ] Capture actionable process improvements with owners
- [ ] Feed improvements into the next sprint's Phase 1 planning

## Key Metrics

- Test cases or scenarios executed versus planned
- Pass/fail/blocked rate
- Requirement or story coverage
- Defects by severity and status
- Escaped defects
- Automation coverage and stability
- Regression execution time
- Residual-risk status

## Related Resources

### Templates
- [Test Plan Template](../test-templates/test-plan-template.md)
- [Test Case Template](../test-templates/test-case-template.md)
- [Defect Report Template](../test-templates/defect-report-template.md)
- [Test Execution Report Template](../test-templates/test-execution-report-template.md)
- [NATAegisFlow Artifact Workflow Checklist](../test-templates/nataegisflow-artifact-workflow-template.md)

### BGSTM Phase Guidance
- [Phase 1: Test Planning](../phases/01-test-planning.md)
- [Phase 2: Test Case Development](../phases/02-test-case-development.md)
- [Phase 3: Test Environment Preparation](../phases/03-test-environment-preparation.md)
- [Phase 4: Test Execution](../phases/04-test-execution.md)
- [Phase 5: Test Results Analysis](../phases/05-test-results-analysis.md)
- [Phase 6: Test Results Reporting](../phases/06-test-results-reporting.md)

### Applied Examples
- [ETL Semantic Validation Applied Example](../examples/etl-semantic-validation-example.md)
- [NATAegisFlow Artifact Workflow Example](../examples/nataegisflow-artifact-workflow-example.md)

### Methodology Guides
- [Scrum Testing](scrum.md)
- [Agile Testing](agile.md)
- [Methodology Comparison](comparison.md)

---

*This checklist is part of BGSTM. BGSTM has exactly six core methodology phases.*
