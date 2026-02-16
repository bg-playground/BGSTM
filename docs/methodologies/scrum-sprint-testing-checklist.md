# Scrum Sprint Testing Checklist

## Overview
This checklist provides a comprehensive guide for testing activities throughout a Scrum sprint. Use this to ensure all critical testing tasks are completed and nothing is overlooked during your sprint cycle.

## Pre-Sprint Planning

### User Story Review
- [ ] Review all user stories planned for the sprint
- [ ] Verify each story has clear acceptance criteria
- [ ] Ensure acceptance criteria are testable and measurable
- [ ] Identify stories with unclear requirements for clarification
- [ ] Check that stories follow Given-When-Then or similar format

### Test Planning
- [ ] Identify all testable items for the sprint
- [ ] List dependencies between user stories and tests
- [ ] Determine which stories need automated tests
- [ ] Plan exploratory testing sessions
- [ ] Identify non-functional testing needs (performance, security)

### Estimation
- [ ] Estimate testing effort for each user story
- [ ] Account for automation development time
- [ ] Include time for regression testing
- [ ] Reserve time for defect retesting
- [ ] Factor in test environment setup time
- [ ] Consider time for exploratory testing sessions

### Test Environment
- [ ] Verify test environment availability for sprint
- [ ] Confirm environment matches production configuration
- [ ] Check test data availability and quality
- [ ] Validate access credentials are current
- [ ] Ensure necessary test tools are accessible
- [ ] Test CI/CD pipeline is functioning

### Definition of Done Review
- [ ] Review and confirm Definition of Done with team
- [ ] Ensure all team members understand testing criteria
- [ ] Verify Definition of Done includes testing requirements
- [ ] Confirm acceptance criteria alignment with DoD

**Common Pitfalls to Avoid:**
- ⚠️ Not clarifying vague acceptance criteria early
- ⚠️ Underestimating testing effort
- ⚠️ Assuming test environment will "just work"

## During Sprint

### Daily Testing Activities

#### Daily Stand-up Participation
- [ ] Share yesterday's testing accomplishments
- [ ] Communicate today's testing plan
- [ ] Raise any blockers or impediments
- [ ] Flag test environment issues
- [ ] Report critical defects found
- [ ] Request clarifications from team members

#### Continuous Integration Testing
- [ ] Monitor CI/CD pipeline for build failures
- [ ] Investigate and report failed automated tests
- [ ] Verify automated smoke tests pass on each commit
- [ ] Review test coverage metrics from CI reports
- [ ] Ensure regression tests run successfully

#### Story Acceptance Testing
- [ ] Test completed stories as soon as they're ready
- [ ] Execute test cases based on acceptance criteria
- [ ] Perform exploratory testing on new features
- [ ] Validate business logic and workflows
- [ ] Test edge cases and error conditions
- [ ] Verify integration with existing functionality
- [ ] Confirm responsive design on different devices/browsers

#### Defect Management
- [ ] Log defects with clear reproduction steps
- [ ] Attach screenshots or videos to defect reports
- [ ] Tag defects with appropriate severity and priority
- [ ] Link defects to affected user stories
- [ ] Participate in daily defect triage
- [ ] Retest fixed defects promptly
- [ ] Verify defect fixes don't introduce regressions

#### Test Automation Activities
- [ ] Write automated tests for new functionality
- [ ] Update existing tests affected by changes
- [ ] Refactor flaky or unreliable tests
- [ ] Add tests to regression suite
- [ ] Review and optimize test execution time
- [ ] Document automation progress

#### Collaboration
- [ ] Pair test with developers when needed
- [ ] Clarify requirements with Product Owner
- [ ] Share testing insights in team discussions
- [ ] Help team members with testing questions
- [ ] Review code from testing perspective

**Common Pitfalls to Avoid:**
- ⚠️ Waiting until sprint end to start testing
- ⚠️ Not retesting defect fixes promptly
- ⚠️ Ignoring flaky automated tests

## Sprint Review / Retrospective

### Sprint Review Preparation
- [ ] Complete all planned test execution
- [ ] Verify all acceptance criteria met
- [ ] Document known issues and limitations
- [ ] Prepare demo environment
- [ ] Create test summary report
- [ ] Gather quality metrics

### Demo and Presentation
- [ ] Demonstrate tested features to stakeholders
- [ ] Present test results and coverage metrics
- [ ] Show passing automated test suites
- [ ] Explain any known issues or workarounds
- [ ] Gather feedback from stakeholders
- [ ] Document questions and concerns raised

### Test Coverage Review
- [ ] Calculate percentage of stories fully tested
- [ ] Review test automation coverage
- [ ] Identify gaps in test coverage
- [ ] Document areas needing additional testing
- [ ] Assess regression test suite effectiveness

### Sprint Retrospective

#### What Went Well
- [ ] Identify successful testing practices
- [ ] Note effective collaboration moments
- [ ] Recognize helpful tools or techniques
- [ ] Document time-saving automation wins

#### What Needs Improvement
- [ ] List testing challenges encountered
- [ ] Identify bottlenecks in testing process
- [ ] Note environment or tool issues
- [ ] Document communication gaps

#### Lessons Learned
- [ ] Record key insights about testing approach
- [ ] Document new techniques or tools tried
- [ ] Note effective defect prevention strategies
- [ ] Capture knowledge for future sprints

#### Action Items
- [ ] Create specific, actionable improvements
- [ ] Assign owners to action items
- [ ] Set deadlines for improvements
- [ ] Plan to review action items next sprint

**Common Pitfalls to Avoid:**
- ⚠️ Rushing through retrospective discussion
- ⚠️ Not following up on action items from previous sprints
- ⚠️ Focusing only on problems, not celebrating successes

## Sprint Closeout

### Final Verification
- [ ] Run full regression test suite
- [ ] Verify all critical and high priority defects resolved
- [ ] Confirm all Definition of Done criteria met
- [ ] Validate integration with existing features
- [ ] Check that no new regressions introduced

### Documentation Updates
- [ ] Update test case repository
- [ ] Document new test scenarios
- [ ] Update automated test documentation
- [ ] Record sprint metrics and trends
- [ ] Archive test execution results

### Preparation for Next Sprint
- [ ] Identify carry-over testing tasks
- [ ] Update test environment for next sprint
- [ ] Plan automation improvements
- [ ] Review and groom test backlog
- [ ] Prepare for upcoming sprint planning

## Key Metrics to Track

### Test Execution Metrics
- [ ] Number of test cases executed
- [ ] Pass/fail rate
- [ ] Test automation coverage percentage
- [ ] Regression test suite execution time

### Defect Metrics
- [ ] Total defects found
- [ ] Defects by severity
- [ ] Defect fix rate
- [ ] Escaped defects (if any)

### Sprint Velocity and Quality
- [ ] Story points completed vs. planned
- [ ] Stories meeting Definition of Done
- [ ] Test coverage per story point
- [ ] Technical debt created or resolved

## Related Resources

### Templates
- [Test Plan Template](../templates/test-plan-template.md) - For sprint test planning
- [Test Case Template](../templates/test-case-template.md) - For detailed test scenarios
- [Defect Report Template](../templates/defect-report-template.md) - For logging defects
- [Test Execution Report Template](../templates/test-execution-report-template.md) - For sprint review

### Phase Guidance
- [Test Planning Phase](../phases/01-test-planning.md) - Detailed planning guidance
- [Test Case Development](../phases/02-test-case-development.md) - Creating test cases
- [Test Environment Preparation](../phases/03-test-environment-preparation.md) - Environment setup
- [Test Execution Phase](../phases/04-test-execution.md) - Execution best practices
- [Test Results Analysis](../phases/05-test-results-analysis.md) - Analyzing results
- [Test Results Reporting](../phases/06-test-results-reporting.md) - Sprint reporting

### Examples
- [Examples Directory](../examples/README.md) - Practical examples (coming soon)

### Related Methodology Docs
- [Scrum Testing Methodology](scrum.md) - Comprehensive Scrum testing guide
- [Agile Testing Methodology](agile.md) - General Agile testing practices
- [Methodology Comparison](comparison.md) - Compare different approaches

## Tips for Success

### For New Scrum Teams
1. Start with a simple Definition of Done and evolve it
2. Focus on automation from sprint one
3. Don't over-commit on testing in early sprints
4. Build time for learning and improvement

### For Experienced Teams
1. Continuously refactor and improve test automation
2. Experiment with new testing techniques
3. Mentor team members on testing practices
4. Challenge yourselves to increase velocity without compromising quality

### General Best Practices
- Test early and test often throughout the sprint
- Collaborate closely with developers
- Automate repetitive tests
- Keep test documentation lightweight but sufficient
- Celebrate quality wins, learn from defects
- Maintain sustainable testing pace

## Checklist Usage Guidelines

**How to Use This Checklist:**
1. Review at sprint planning to prepare for the sprint
2. Reference daily during sprint execution
3. Use during sprint review to ensure completeness
4. Customize based on your team's specific needs
5. Print or pin for easy team access

**Customization Tips:**
- Add team-specific items relevant to your context
- Remove items that don't apply to your project
- Adjust frequency of activities based on sprint length
- Modify to align with your Definition of Done

---

*This checklist is part of the BGSTM (BG Software Testing Methodology) framework. For more information, see the [main documentation](../README.md).*
