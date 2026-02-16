# Waterfall Phase Gate Checklist

## Overview
This comprehensive checklist provides phase gate criteria for testing activities in Waterfall methodology projects. Use this to ensure quality gates are met before proceeding from one phase to the next, maintaining rigorous quality standards throughout the project lifecycle.

## Requirements Phase Gate

### Requirements Validation
- [ ] All requirements documented and numbered
- [ ] Requirements are clear, complete, and unambiguous
- [ ] Requirements are testable and measurable
- [ ] Non-functional requirements specified
- [ ] Requirements prioritized (must-have, should-have, could-have)
- [ ] Requirements approved by stakeholders

### Test Plan Approval Criteria
- [ ] Master Test Plan document created
- [ ] Test strategy defined and documented
- [ ] Test levels identified (unit, integration, system, UAT)
- [ ] Test types specified (functional, performance, security)
- [ ] Test approach documented (manual/automated)
- [ ] Entry and exit criteria defined
- [ ] Test schedule with milestones created
- [ ] Resource requirements identified
- [ ] Risk assessment completed
- [ ] Master Test Plan reviewed by stakeholders
- [ ] Master Test Plan formally approved and signed off

### Requirements Traceability Setup
- [ ] Requirements Traceability Matrix (RTM) template created
- [ ] RTM structure defined (requirement ID, description, test case mapping)
- [ ] Process for maintaining RTM established
- [ ] Tool for RTM management selected
- [ ] Initial RTM populated with requirements
- [ ] RTM review process defined

### Test Environment Planning
- [ ] Test environment requirements identified
- [ ] Hardware specifications documented
- [ ] Software requirements listed
- [ ] Network configuration requirements defined
- [ ] Test data requirements identified
- [ ] Third-party system dependencies documented
- [ ] Environment procurement initiated
- [ ] Environment timeline established
- [ ] Environment responsibilities assigned

### Test Team Formation
- [ ] Test team roles and responsibilities defined
- [ ] Test lead assigned
- [ ] Test analysts/engineers identified
- [ ] Test automation engineers assigned
- [ ] Domain experts engaged
- [ ] Training needs assessed
- [ ] Team onboarding plan created

**Phase Gate Exit Criteria:**
- ✓ Master Test Plan approved
- ✓ Requirements are testable
- ✓ RTM framework established
- ✓ Test team formed
- ✓ Test environment plan approved
- ✓ Stakeholder sign-off obtained

**Common Pitfalls to Avoid:**
- ⚠️ Vague or untestable requirements approved
- ⚠️ Insufficient time allocated for test planning
- ⚠️ Test environment needs not identified early

## Design Phase Gate

### Design Review and Analysis
- [ ] System architecture reviewed from testing perspective
- [ ] Design documents reviewed for testability
- [ ] Integration points identified and documented
- [ ] Data flow diagrams reviewed
- [ ] Interface specifications analyzed
- [ ] Security design reviewed
- [ ] Performance requirements validated

### Test Case Design Completion
- [ ] Test design approach documented
- [ ] Test scenarios identified for all requirements
- [ ] Test case templates standardized
- [ ] Detailed test cases written
- [ ] Test cases map to requirements in RTM
- [ ] Test cases reviewed by peers
- [ ] Test cases reviewed by business analysts/SMEs
- [ ] Test case reviews documented
- [ ] Test case defects/issues resolved
- [ ] Test cases approved

### Test Case Coverage Verification
- [ ] All functional requirements have test cases
- [ ] Non-functional requirements covered
- [ ] Positive test scenarios created
- [ ] Negative test scenarios created
- [ ] Boundary value test cases included
- [ ] Error handling scenarios covered
- [ ] Integration test scenarios defined
- [ ] End-to-end workflow scenarios documented
- [ ] Test coverage gaps identified and addressed

### Test Data Preparation Planning
- [ ] Test data requirements analyzed
- [ ] Test data sources identified
- [ ] Data generation strategy defined
- [ ] Data privacy and security requirements addressed
- [ ] Test data creation approach documented
- [ ] Data refresh strategy planned
- [ ] Data masking requirements identified
- [ ] Test data validation criteria defined

### Test Automation Strategy
- [ ] Automation feasibility assessed
- [ ] Automation tool selection completed
- [ ] Automation framework design documented
- [ ] Automation scope defined (which tests to automate)
- [ ] Automation priorities established
- [ ] Test automation resources assigned
- [ ] Automation development timeline created
- [ ] Automation standards and guidelines documented

### Environment Setup Validation
- [ ] Test environment specifications finalized
- [ ] Environment setup procedures documented
- [ ] Environment access requirements defined
- [ ] Environment monitoring approach defined
- [ ] Environment backup and recovery plan created
- [ ] Environment maintenance schedule established

**Phase Gate Exit Criteria:**
- ✓ All test cases designed and approved
- ✓ 100% requirements coverage in test cases
- ✓ Test data strategy approved
- ✓ Automation approach finalized
- ✓ Design reviews completed
- ✓ RTM updated with test cases
- ✓ Test lead sign-off obtained

**Common Pitfalls to Avoid:**
- ⚠️ Incomplete test case coverage
- ⚠️ Test cases too high-level and vague
- ⚠️ Not involving business users in test case review

## Development Phase Gate

### Unit Testing Completion
- [ ] Unit testing standards defined
- [ ] Developers completed unit testing
- [ ] Unit test coverage metrics collected
- [ ] Unit test coverage meets minimum threshold (e.g., 70%)
- [ ] Unit test results reviewed
- [ ] Critical unit test failures resolved
- [ ] Unit test reports archived
- [ ] Code coverage analysis completed

### Integration Test Readiness
- [ ] Integration test environment available
- [ ] Integration test data prepared
- [ ] Integration test cases ready for execution
- [ ] Integration points validated
- [ ] API documentation available
- [ ] Interface specifications confirmed
- [ ] Integration testing schedule finalized
- [ ] Integration test dependencies resolved

### Build and Deployment
- [ ] Code complete and checked in
- [ ] Build process documented
- [ ] Build deployed to test environment
- [ ] Smoke tests passed on deployed build
- [ ] Build version documented
- [ ] Deployment procedure documented
- [ ] Rollback procedure documented
- [ ] Build artifacts archived

### Test Environment Setup Completion
- [ ] Test environment fully configured
- [ ] All required software installed
- [ ] Database setup completed
- [ ] Test data loaded
- [ ] Network connectivity verified
- [ ] Third-party integrations configured
- [ ] Environment access provided to test team
- [ ] Environment validated against checklist
- [ ] Environment sign-off obtained

### Test Automation Development
- [ ] Automation framework implemented
- [ ] Automated test scripts developed
- [ ] Automation test data created
- [ ] Automated tests integrated with CI/CD (if applicable)
- [ ] Automated tests executed successfully
- [ ] Automation results reporting configured
- [ ] Automation maintenance documentation created
- [ ] Test team trained on automation framework

### Defect Tracking System Setup
- [ ] Defect tracking tool configured
- [ ] Defect workflow defined
- [ ] Defect fields and categories configured
- [ ] Severity and priority definitions documented
- [ ] Defect triage process established
- [ ] Defect reporting templates created
- [ ] Team trained on defect tracking tool
- [ ] Integration with test management tool completed
- [ ] Defect metrics and reporting configured

**Phase Gate Exit Criteria:**
- ✓ Unit testing completed with acceptable coverage
- ✓ Test environment ready and validated
- ✓ Build deployed and smoke tested
- ✓ Defect tracking system operational
- ✓ Test automation framework ready
- ✓ Integration test readiness confirmed
- ✓ Development lead sign-off

**Common Pitfalls to Avoid:**
- ⚠️ Low unit test coverage allowed to pass
- ⚠️ Test environment not properly validated
- ⚠️ Insufficient test data prepared

## Testing Phase Gate

### Test Execution Completion

#### Test Cycle Tracking
- [ ] Test execution started as per schedule
- [ ] Daily test execution status tracked
- [ ] Test case execution status updated in test management tool
- [ ] All planned test cases executed
- [ ] Test execution results documented
- [ ] Failed test cases analyzed
- [ ] Blocked test cases resolved or documented
- [ ] Test execution evidence collected (screenshots, logs)

#### Test Types Completion
- [ ] Integration testing completed
- [ ] System testing completed
- [ ] Functional testing completed
- [ ] Non-functional testing completed (performance, security, usability)
- [ ] Regression testing completed
- [ ] User Acceptance Testing (UAT) completed
- [ ] End-to-end testing completed
- [ ] Cross-browser/platform testing completed (if applicable)

### Defect Resolution Status

#### Defect Metrics
- [ ] All critical defects resolved and verified
- [ ] All high priority defects resolved and verified
- [ ] Medium defects reviewed and resolved/deferred
- [ ] Low defects reviewed and resolved/deferred
- [ ] Defect aging analyzed
- [ ] Defect density calculated
- [ ] Defect removal efficiency measured
- [ ] Root cause analysis completed for critical defects

#### Defect Closure
- [ ] Fixed defects retested and verified
- [ ] Regression testing performed for defect fixes
- [ ] Deferred defects documented and approved
- [ ] Known issues list created
- [ ] Workarounds documented for known issues
- [ ] Defect trends analyzed
- [ ] Final defect triage meeting conducted
- [ ] Defect summary report created

### Test Coverage Metrics

#### Requirements Coverage
- [ ] All requirements traced to test cases
- [ ] All test cases executed
- [ ] Requirements Traceability Matrix updated
- [ ] 100% requirements coverage verified
- [ ] Gaps in coverage analyzed and addressed
- [ ] Coverage report generated
- [ ] Coverage reviewed with stakeholders

#### Code Coverage (if applicable)
- [ ] Code coverage analysis performed
- [ ] Coverage percentage meets target (e.g., 70-80%)
- [ ] Uncovered code reviewed and justified
- [ ] Critical paths fully covered
- [ ] Code coverage trends analyzed

#### Functional Coverage
- [ ] All functional areas tested
- [ ] All user workflows validated
- [ ] All business rules verified
- [ ] All integration points tested
- [ ] All error conditions tested

### Exit Criteria Validation

#### Quality Criteria
- [ ] Test pass rate ≥ 95% (or defined threshold)
- [ ] No open critical or high severity defects
- [ ] Medium/low defects at acceptable levels
- [ ] Performance benchmarks met
- [ ] Security requirements validated
- [ ] Usability criteria met
- [ ] Compatibility requirements verified
- [ ] Regression test suite passes

#### Documentation Criteria
- [ ] Test execution report completed
- [ ] Test results summary prepared
- [ ] Test metrics report created
- [ ] Defect summary report finalized
- [ ] Known issues documented
- [ ] Test coverage report generated
- [ ] Lessons learned documented
- [ ] Test artifacts archived

#### Sign-off Criteria
- [ ] Test lead approval obtained
- [ ] QA manager approval obtained
- [ ] Product owner/business sign-off obtained
- [ ] Project manager approval obtained
- [ ] UAT sign-off received
- [ ] Go/No-go decision documented

### Test Summary Report
- [ ] Executive summary written
- [ ] Test objectives and scope documented
- [ ] Test approach summarized
- [ ] Test environment details included
- [ ] Test execution summary provided
- [ ] Defect analysis included
- [ ] Test coverage analysis presented
- [ ] Quality metrics reported
- [ ] Risks and issues documented
- [ ] Recommendations provided
- [ ] Formal report review completed
- [ ] Report distributed to stakeholders

**Phase Gate Exit Criteria:**
- ✓ All planned tests executed
- ✓ Test pass rate meets threshold
- ✓ Critical/high defects resolved
- ✓ Test coverage meets requirements
- ✓ Exit criteria validated
- ✓ Test summary report approved
- ✓ Stakeholder sign-offs obtained
- ✓ Go-live approval granted

**Common Pitfalls to Avoid:**
- ⚠️ Rushing testing phase to meet deadlines
- ⚠️ Accepting too many open defects
- ⚠️ Inadequate regression testing
- ⚠️ Incomplete documentation

## Deployment Phase Gate

### Production Readiness Testing

#### Pre-Deployment Validation
- [ ] Final smoke test on release candidate passed
- [ ] Production deployment checklist prepared
- [ ] Production environment validated
- [ ] Production data migration tested (if applicable)
- [ ] Database scripts validated
- [ ] Configuration files reviewed
- [ ] Deployment procedures verified
- [ ] Rollback procedures tested
- [ ] Backup procedures validated
- [ ] Production access verified

#### Release Package Validation
- [ ] Release package contents verified
- [ ] Version numbers validated
- [ ] Release notes reviewed and approved
- [ ] Installation guide available
- [ ] User documentation completed
- [ ] Training materials prepared
- [ ] Support documentation ready
- [ ] Known issues list included

### Production Deployment Activities
- [ ] Production deployment window scheduled
- [ ] Stakeholders notified of deployment
- [ ] Deployment team briefed
- [ ] Deployment executed per checklist
- [ ] Deployment logs captured
- [ ] Post-deployment smoke tests executed
- [ ] Critical functionality verified
- [ ] Integration points validated
- [ ] Performance monitoring active
- [ ] Error logs monitored

### User Acceptance Sign-off

#### UAT Completion
- [ ] UAT test cases executed
- [ ] UAT results documented
- [ ] UAT defects resolved or accepted
- [ ] Business scenarios validated
- [ ] User workflows verified
- [ ] Business users trained
- [ ] UAT sign-off document prepared
- [ ] Formal UAT sign-off obtained

#### Business Readiness
- [ ] Business processes updated
- [ ] User training completed
- [ ] Help desk briefed
- [ ] Support procedures in place
- [ ] Communication plan executed
- [ ] Change management activities completed
- [ ] Business stakeholders ready

### Post-Deployment Validation

#### Production Verification
- [ ] Production smoke tests passed
- [ ] Critical business workflows working
- [ ] Integration with external systems verified
- [ ] Performance benchmarks validated
- [ ] Security checks performed
- [ ] Data integrity verified
- [ ] User access validated
- [ ] Monitoring dashboards operational

#### Hypercare Period Setup
- [ ] War room established (if applicable)
- [ ] Support team on standby
- [ ] Issue escalation process active
- [ ] Enhanced monitoring enabled
- [ ] Issue tracking active
- [ ] Communication channels open
- [ ] Quick response team ready

#### Production Monitoring
- [ ] Application monitoring active
- [ ] Performance monitoring enabled
- [ ] Error tracking operational
- [ ] User activity monitoring active
- [ ] Security monitoring enabled
- [ ] Alert thresholds configured
- [ ] Dashboard reporting functional
- [ ] Log aggregation working

### Project Closure Activities

#### Final Documentation
- [ ] Final test report completed
- [ ] Project lessons learned documented
- [ ] Test metrics finalized
- [ ] Test artifacts archived
- [ ] Knowledge transfer completed
- [ ] Process improvements identified
- [ ] Best practices documented
- [ ] Project closure report prepared

#### Transition to Support
- [ ] Support team trained
- [ ] Support documentation handed over
- [ ] Known issues transferred
- [ ] Monitoring handed over
- [ ] Support processes established
- [ ] Escalation procedures documented
- [ ] Transition sign-off obtained

#### Project Sign-off
- [ ] Project completion criteria met
- [ ] Final stakeholder approval obtained
- [ ] Project formally closed
- [ ] Team recognition completed
- [ ] Post-implementation review scheduled

**Phase Gate Exit Criteria:**
- ✓ Production deployment successful
- ✓ Post-deployment validation passed
- ✓ UAT sign-off obtained
- ✓ Production monitoring active
- ✓ Support transition completed
- ✓ Project closure activities completed
- ✓ Final sign-offs obtained

**Common Pitfalls to Avoid:**
- ⚠️ Insufficient production validation
- ⚠️ Inadequate rollback planning
- ⚠️ Poor transition to support team
- ⚠️ Skipping lessons learned documentation

## Continuous Tracking and Metrics

### Phase Metrics to Track

#### Requirements Phase
- [ ] Requirements review completion rate
- [ ] Requirements defect density
- [ ] Testability assessment score

#### Design Phase
- [ ] Test case development progress
- [ ] Test case review completion
- [ ] Requirements coverage percentage

#### Development Phase
- [ ] Unit test coverage
- [ ] Code review completion
- [ ] Build stability rate

#### Testing Phase
- [ ] Test execution progress
- [ ] Defect detection rate
- [ ] Defect resolution time
- [ ] Test pass rate
- [ ] Requirements coverage

#### Deployment Phase
- [ ] Deployment success rate
- [ ] Post-deployment defects
- [ ] Production stability

### Quality Gates Dashboard
- [ ] Define KPIs for each phase gate
- [ ] Create dashboard for tracking
- [ ] Review metrics weekly
- [ ] Report to stakeholders monthly
- [ ] Use metrics for process improvement

## Related Resources

### Templates
- [Test Plan Template](../templates/test-plan-template.md) - Master test plan creation
- [Test Case Template](../templates/test-case-template.md) - Detailed test case documentation
- [Defect Report Template](../templates/defect-report-template.md) - Comprehensive defect reporting
- [Test Execution Report Template](../templates/test-execution-report-template.md) - Test cycle reporting

### Phase Guidance
- [Test Planning Phase](../phases/01-test-planning.md) - Detailed planning guidance
- [Test Case Development](../phases/02-test-case-development.md) - Test case design principles
- [Test Environment Preparation](../phases/03-test-environment-preparation.md) - Environment setup
- [Test Execution Phase](../phases/04-test-execution.md) - Execution strategies
- [Test Results Analysis](../phases/05-test-results-analysis.md) - Results analysis
- [Test Results Reporting](../phases/06-test-results-reporting.md) - Reporting best practices

### Examples
- [Examples Directory](../examples/README.md) - Practical examples (coming soon)

### Related Methodology Docs
- [Waterfall Testing Methodology](waterfall.md) - Complete Waterfall methodology
- [Agile Testing Methodology](agile.md) - Agile practices
- [Methodology Comparison](comparison.md) - Compare different approaches

## Best Practices for Phase Gate Success

### For Project Managers
1. Enforce phase gate discipline rigorously
2. Don't skip gate reviews to save time
3. Ensure adequate resources for each phase
4. Plan for contingency in schedule
5. Maintain clear documentation

### For Test Leads
1. Prepare thoroughly for each gate review
2. Maintain comprehensive documentation
3. Track metrics consistently
4. Communicate risks early
5. Ensure team readiness for each phase

### For Test Team
1. Complete assigned tasks on time
2. Maintain quality in deliverables
3. Follow established processes
4. Document thoroughly
5. Communicate issues promptly

### General Best Practices
- Plan thoroughly before each phase
- Review and validate all deliverables
- Maintain traceability throughout
- Document everything formally
- Obtain proper approvals at each gate
- Learn from each phase
- Apply lessons to future phases

## Checklist Usage Guidelines

**How to Use This Checklist:**
1. Review before starting each project phase
2. Use during phase to track progress
3. Validate completion before phase gate review
4. Customize based on project needs
5. Archive completed checklists for audit

**Customization Tips:**
- Adjust criteria based on project size
- Add industry-specific requirements
- Scale based on project complexity
- Align with organizational standards
- Include regulatory requirements

**Integration with Project Management:**
- Align with project milestones
- Include in project schedule
- Track in project management tools
- Report in status meetings
- Use for risk management

---

*This checklist is part of the BGSTM (BG Software Testing Methodology) framework. For more information, see the [main documentation](../README.md).*
