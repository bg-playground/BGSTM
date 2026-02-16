# Phase 4: Test Execution

## Overview
Test Execution is the phase where test cases are executed, defects are identified and logged, and actual results are compared against expected results. This is where the actual testing happens.

## Objectives
- Execute test cases according to test plan
- Identify and document defects
- Track test progress and coverage
- Verify bug fixes and perform retesting
- Conduct regression testing
- Collect evidence and test artifacts

## Key Activities

### 1. Test Execution Preparation
- Review test cases before execution
- Verify test environment readiness
- Ensure test data availability
- Confirm access to necessary tools
- Conduct test execution kickoff meeting

### 2. Test Case Execution

#### Manual Testing
- Follow test case steps precisely
- Record actual results for each step
- Take screenshots or videos as evidence
- Note any deviations from expected behavior
- Update test case status (Pass/Fail/Blocked)

#### Automated Testing
- Execute automated test scripts
- Monitor test execution progress
- Review test execution logs
- Analyze automation failures
- Maintain and update test scripts

### 3. Defect Management

#### Defect Identification
- Compare actual vs. expected results
- Verify defect is reproducible
- Check if defect is already reported
- Determine severity and priority

#### Defect Logging
Each defect report should include:
- **Defect ID**: Unique identifier
- **Summary**: Brief description
- **Description**: Detailed explanation
- **Steps to Reproduce**: How to replicate the defect
- **Expected Result**: What should happen
- **Actual Result**: What actually happened
- **Severity**: Critical/High/Medium/Low
- **Priority**: High/Medium/Low
- **Environment**: Where defect was found
- **Attachments**: Screenshots, logs, videos
- **Test Case Reference**: Related test case ID

#### Defect Severity Levels
- **Critical**: System crash, data loss, security breach
- **High**: Major feature not working, significant functionality impacted
- **Medium**: Feature partially working, workaround available
- **Low**: Minor issues, cosmetic problems, suggestions

#### Defect Priority Levels
- **High**: Must be fixed immediately
- **Medium**: Should be fixed soon
- **Low**: Can be fixed in future releases

### 4. Defect Lifecycle Management
1. **New**: Defect reported
2. **Assigned**: Assigned to developer
3. **In Progress**: Developer working on fix
4. **Fixed**: Developer has fixed the defect
5. **Retest**: Tester verifies the fix
6. **Verified**: Fix confirmed working
7. **Closed**: Defect resolved
8. **Reopened**: Fix didn't work, defect still exists

### 5. Retesting and Regression Testing

#### Retesting
- Verify that reported defects are fixed
- Execute failed test cases again
- Confirm fix doesn't introduce new issues

#### Regression Testing
- Execute existing test cases after changes
- Verify that fixes didn't break existing functionality
- Focus on areas impacted by changes
- Maintain regression test suite

### 6. Test Progress Tracking
- Update test execution status daily
- Track metrics: test cases passed/failed/blocked
- Monitor test coverage
- Identify bottlenecks and risks
- Report progress to stakeholders

### 7. Test Execution Activities by Type

#### Smoke Testing
- Quick validation of critical functionality
- Performed before detailed testing
- Determines if build is stable enough for further testing

#### Sanity Testing
- Focused testing of specific functionality
- Performed after minor changes
- Quick check that issue is resolved

#### Functional Testing
- Validate features against requirements
- Test user workflows and scenarios
- Verify business logic

#### Non-Functional Testing
- **Performance Testing**: Response time, throughput, scalability
- **Security Testing**: Vulnerabilities, access control, data protection
- **Usability Testing**: User experience, navigation, accessibility
- **Compatibility Testing**: Browsers, devices, operating systems

#### Integration Testing
- Test interaction between components
- Validate data flow across modules
- Verify API contracts

#### End-to-End Testing
- Test complete user workflows
- Validate system as a whole
- Simulate real-world scenarios

## Test Execution Strategies

### Sequential Execution
- Execute test cases one at a time
- Suitable for dependent test cases
- Easier to track and debug

### Parallel Execution
- Execute multiple test cases simultaneously
- Faster test execution
- Requires independent test cases
- Used primarily in automation

### Risk-Based Testing
- Prioritize high-risk areas
- Execute critical tests first
- Optimize test coverage

### Time-Boxed Testing
- Allocate fixed time for testing
- Focus on highest priority items
- Used when time is constrained

## Deliverables
Enumerate all key outputs produced in this phase:
- Test execution logs
- Completed test cases with results
- Defect reports
- Test metrics and KPIs
- Environment logs
- Screenshots/evidence

## Best Practices
Include tips, pitfalls to avoid, and recommendations:
- Execute tests in a consistent order
- Document all deviations from test cases
- Log defects immediately when found
- Maintain traceability between tests and requirements
- Communicate blockers quickly
- Follow the defect management workflow
- Keep test data organized and version-controlled

## Common Challenges and Solutions

### Challenge: Test Environment Issues
**Solution**: Have backup environments, implement quick recovery procedures

### Challenge: Test Data Problems
**Solution**: Automate data setup, maintain data repositories

### Challenge: Blocked Test Cases
**Solution**: Identify alternatives, escalate blockers, update test plan

### Challenge: Time Constraints
**Solution**: Prioritize testing, increase resources, extend timeline if needed

### Challenge: Frequent Builds
**Solution**: Implement smoke tests, automate regression suite

## Metrics to Track
- Test cases executed (count and percentage)
- Pass/Fail rate
- Defects found per test cycle
- Defect density (defects per module/feature)
- Test execution progress
- Test coverage percentage
- Average time to execute test suite
- Defect detection rate
- Defect resolution time

## Methodology-Specific Considerations
Explain how Agile, Scrum, Waterfall, etc. impact this phase:
- **Agile/Scrum**: Daily standup updates, sprint-based execution, continuous testing
- **Waterfall**: Formal test execution phase, gate criteria, comprehensive reporting
- **DevOps/Continuous**: Automated execution in CI/CD pipelines

## Tools and Technologies
- **Test Management**: TestRail, Zephyr, qTest
- **Defect Tracking**: Jira, Bugzilla, Azure DevOps
- **Test Automation**: Selenium, Cypress, Playwright, Appium
- **Performance Testing**: JMeter, LoadRunner, Gatling
- **Security Testing**: OWASP ZAP, Burp Suite
- **API Testing**: Postman, REST Assured, SoapUI

## Templates
- [Defect Report Template](../templates/defect-report-template.md)
- [Test Execution Report Template](../templates/test-execution-report-template.md)
- Test Results Summary Template

## Examples
- [Defect Report Example](../examples/defect-report-example.md) - Comprehensive defect report examples showing 10 realistic defects across all severity levels (Critical to Low). Includes complete defect lifecycle from identification through closure, with root cause analysis, reproduction steps, verification procedures, and best practices for defect documentation.

## Previous Phase
[Test Environment Preparation](03-test-environment-preparation.md)

## Next Phase
→ [Phase 5: Test Results Analysis](05-test-results-analysis.md)
