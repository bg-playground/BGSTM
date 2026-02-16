# Waterfall Testing Checklist

**Purpose:** Comprehensive checklist for testing activities at each Waterfall phase gate.  
**When to Use:** Reference at phase transitions to ensure all testing criteria are met before proceeding to next phase.

---

## Requirements Phase

### Requirements Review
- [ ] Review requirements documentation for testability
- [ ] Identify ambiguous or incomplete requirements
- [ ] Define acceptance criteria for each requirement
- [ ] Validate requirements with stakeholders
- [ ] Document non-functional requirements

### Test Planning Preparation
- [ ] Identify testing scope and objectives
- [ ] Define test strategy approach
- [ ] Estimate testing effort and resources
- [ ] Identify testing risks
- [ ] Plan test environment requirements

---

## Design Phase

### Design Review for Testability
- [ ] Review system architecture for testability
- [ ] Identify integration test points
- [ ] Validate design against requirements
- [ ] Document test approach for design
- [ ] Identify performance testing needs

### Test Planning
- [ ] Create comprehensive test plan
- [ ] Define test levels (unit, integration, system, UAT)
- [ ] Allocate testing resources
- [ ] Create test schedule with milestones
- [ ] Establish entry and exit criteria for each level
- [ ] Plan test environment and tools
- [ ] Document risk mitigation strategies

---

## Development/Implementation Phase

### Test Case Development
- [ ] Develop test cases for all requirements
- [ ] Create traceability matrix
- [ ] Design test data sets
- [ ] Prepare test scripts (manual and automated)
- [ ] Review test cases with stakeholders
- [ ] Obtain test case approval

### Test Environment Preparation
- [ ] Set up test environments (integration, system, UAT)
- [ ] Configure test tools and infrastructure
- [ ] Load test data
- [ ] Validate environment readiness
- [ ] Document environment configuration
- [ ] Establish change control procedures

### Early Testing
- [ ] Review unit test results from development
- [ ] Participate in code reviews
- [ ] Conduct early integration testing if possible
- [ ] Validate builds before formal testing

---

## Testing Phase

### Integration Testing
- [ ] Execute integration test cases
- [ ] Validate component interactions
- [ ] Test data flow between modules
- [ ] Verify API integrations
- [ ] Document integration test results
- [ ] Log integration defects

### System Testing
- [ ] Execute system test cases
- [ ] Perform end-to-end testing
- [ ] Validate functional requirements
- [ ] Conduct non-functional testing (performance, security, usability)
- [ ] Execute regression test suite
- [ ] Document system test results

### Defect Management
- [ ] Log all defects with severity and priority
- [ ] Track defect resolution progress
- [ ] Retest fixed defects
- [ ] Perform regression testing after fixes
- [ ] Escalate critical defects
- [ ] Maintain defect metrics

### Test Progress Tracking
- [ ] Update test execution status daily
- [ ] Track test coverage metrics
- [ ] Monitor defect trends
- [ ] Report progress to stakeholders
- [ ] Identify and mitigate testing risks
- [ ] Document deviations from test plan

---

## User Acceptance Testing (UAT) Phase

### UAT Preparation
- [ ] Prepare UAT environment
- [ ] Create UAT test scenarios with business users
- [ ] Train users on UAT process
- [ ] Provide UAT documentation and support
- [ ] Set up UAT defect tracking

### UAT Execution
- [ ] Support users during UAT execution
- [ ] Monitor UAT progress
- [ ] Triage UAT defects
- [ ] Coordinate defect fixes
- [ ] Obtain UAT sign-off

---

## Pre-Deployment Phase

### Release Readiness
- [ ] Verify all exit criteria met
- [ ] Confirm all critical defects resolved
- [ ] Execute final regression testing
- [ ] Validate deployment package
- [ ] Review test summary report
- [ ] Obtain stakeholder approval for release

### Documentation
- [ ] Finalize test summary report
- [ ] Document known issues and workarounds
- [ ] Prepare release notes
- [ ] Archive test artifacts
- [ ] Create handover documentation for support team

### Deployment Support
- [ ] Participate in deployment planning
- [ ] Prepare rollback procedures
- [ ] Plan post-deployment validation
- [ ] Define production monitoring approach

---

## Post-Deployment Phase

### Production Validation
- [ ] Execute smoke tests in production
- [ ] Monitor production issues
- [ ] Validate critical business processes
- [ ] Document production defects
- [ ] Support incident resolution

### Closure Activities
- [ ] Conduct project retrospective
- [ ] Document lessons learned
- [ ] Archive all test documentation
- [ ] Update test process based on learnings
- [ ] Celebrate successes and recognize team

---

## Phase Gate Criteria

### Gate Review Checklist
- [ ] All planned test cases executed
- [ ] Test coverage goals achieved
- [ ] Exit criteria met
- [ ] Critical defects resolved
- [ ] Test documentation complete
- [ ] Risks assessed and mitigated
- [ ] Stakeholder approval obtained
- [ ] Lessons learned documented

---

## Related Resources
- [Waterfall Testing Guide](waterfall.md) - Complete Waterfall testing methodology
- [Methodology Comparison](comparison.md) - Compare with other methodologies
- [Test Plan Template](../templates/test-plan-template.md)
- [Test Case Template](../templates/test-case-template.md)
- [Test Summary Report Template](../templates/test-summary-report-template.md)
- [Risk Assessment Template](../templates/risk-assessment-template.md)
