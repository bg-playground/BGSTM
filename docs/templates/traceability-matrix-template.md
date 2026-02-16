# Traceability Matrix Template

**Version:** 1.0  
**Purpose:** This template provides a structured format for tracking relationships between requirements, test cases, test execution, and defects. It ensures complete test coverage and enables impact analysis when requirements change.  
**When to Use:** During Test Case Development (Phase 2) to establish traceability, and continuously throughout Testing to track execution and defect status. Essential for audit, compliance, and coverage verification.

---

## Usage Guidance

### Who Should Use This Template?
- Test Analysts mapping requirements to test cases
- Test Leads verifying coverage completeness
- Test Managers reporting coverage status to stakeholders
- Business Analysts validating requirement validation
- Quality Auditors verifying traceability and compliance
- Project Managers assessing testing progress

### How to Use This Template
1. **Initialize**: List all requirements from requirements document or backlog
2. **Map Test Cases**: Link each requirement to one or more test cases
3. **Track Execution**: Update test execution status as tests are run
4. **Link Defects**: Associate defects with requirements and test cases
5. **Identify Gaps**: Find requirements without test coverage
6. **Update Regularly**: Keep matrix current as requirements or test cases change
7. **Report Coverage**: Generate coverage reports for stakeholders

### Tips for Effective Traceability
- **Start Early**: Begin mapping during test case development
- **Be Complete**: Every requirement should have test coverage
- **Be Specific**: Link to specific test case IDs, not general descriptions
- **Update Promptly**: Maintain matrix as changes occur
- **Verify Bidirectional**: Check both requirement→test and test→requirement links
- **Include All Test Types**: Map functional, integration, regression, etc.
- **Use Tools**: Leverage test management tools for automated traceability

### Benefits of Traceability Matrix
- **Coverage Verification:** Ensures all requirements are tested
- **Gap Identification:** Highlights untested or under-tested requirements
- **Impact Analysis:** Shows which tests need rerun when requirements change
- **Progress Tracking:** Visualizes testing completion status
- **Audit Support:** Demonstrates compliance and thoroughness
- **Defect Analysis:** Links defects back to requirements for root cause analysis

---

## Document Control

**Field Explanations:** This section tracks document metadata and currency.

| Field | Value | Instructions |
|-------|-------|--------------|
| **Project Name** | [Project Name] | Full name of the project or product |
| **Document Version** | [Version Number] | Version of this traceability matrix (e.g., 1.0, 1.1) |
| **Last Updated** | [Date] | Date of most recent update (YYYY-MM-DD format) |
| **Prepared By** | [Name] | Person responsible for maintaining this matrix |
| **Review Frequency** | [Daily/Weekly/Sprint] | How often this matrix should be reviewed and updated |
| **Status** | [Draft/Active/Archived] | Current state of the document |

### Revision History

| Version | Date | Author | Description of Changes |
|---------|------|--------|------------------------|
| 1.0 | | | Initial traceability matrix created |

---

## Coverage Summary

**Purpose:** High-level overview of test coverage status for quick stakeholder review.

### Overall Coverage Statistics

**Field Explanations:**

| Metric | Value | Formula | Target |
|--------|-------|---------|--------|
| **Total Requirements** | [#] | Count of all requirements in scope | - |
| **Requirements Covered** | [#] | Requirements with at least one test case | - |
| **Requirements Not Covered** | [#] | Requirements with zero test cases | 0 |
| **Coverage Percentage** | [%] | (Requirements Covered / Total) × 100 | 100% |
| **Total Test Cases** | [#] | Count of all test cases mapped to requirements | - |
| **Test Cases Executed** | [#] | Test cases that have been run | - |
| **Execution Percentage** | [%] | (Executed / Total Test Cases) × 100 | 100% |
| **Test Cases Passed** | [#] | Test cases with Pass status | - |
| **Pass Rate** | [%] | (Passed / Executed) × 100 | 95%+ |
| **Total Defects Logged** | [#] | Defects linked to requirements | - |
| **Open Defects** | [#] | Defects not yet closed | 0 |

### Coverage by Priority

**Purpose:** Shows coverage distribution ensuring high-priority requirements are well-tested.

**What to analyze:**
- High-priority requirements should have 100% coverage
- Higher priority requirements typically need more test cases
- Low pass rates on high-priority requirements are critical concerns

| Priority | Total Requirements | Covered | Not Covered | Coverage % | Avg Tests per Req |
|----------|-------------------|---------|-------------|------------|-------------------|
| **High** | [#] | [#] | [#] | [%] | [#] |
| **Medium** | [#] | [#] | [#] | [%] | [#] |
| **Low** | [#] | [#] | [#] | [%] | [#] |
| **Total** | **[#]** | **[#]** | **[#]** | **[%]** | **[#]** |

### Coverage by Module/Feature

**Purpose:** Identifies which application areas have adequate test coverage.

| Module/Feature | Total Requirements | Covered | Coverage % | Test Cases | Executed | Pass Rate |
|----------------|-------------------|---------|------------|------------|----------|-----------|
| [Module 1] | [#] | [#] | [%] | [#] | [#] | [%] |
| [Module 2] | [#] | [#] | [%] | [#] | [#] | [%] |
| [Module 3] | [#] | [#] | [%] | [#] | [#] | [%] |
| **Total** | **[#]** | **[#]** | **[%]** | **[#]** | **[#]** | **[%]** |

---

## Traceability Matrix

**Purpose:** Detailed mapping showing relationships between requirements, test cases, execution status, and defects.

### Matrix Format Instructions

**Column Explanations:**

- **Requirement ID:** Unique identifier from requirements document (e.g., REQ-001, US-125)
- **Requirement Description:** Brief description of what the requirement specifies
- **Priority:** Importance level (High/Medium/Low or P0/P1/P2/P3)
- **Module/Feature:** Application area this requirement belongs to
- **Test Case IDs:** All test cases that validate this requirement (comma-separated)
- **Coverage Status:** Whether requirement has adequate test coverage
  - ✅ Covered: Has one or more test cases
  - ⚠️ Partial: Has test cases but coverage may be insufficient
  - ❌ Not Covered: No test cases exist
- **Test Execution Status:** Overall execution status for linked test cases
  - Pass: All test cases passed
  - Fail: One or more test cases failed
  - Blocked: One or more test cases blocked
  - Not Run: Test cases not yet executed
  - In Progress: Test execution ongoing
- **Pass Rate:** (Passed Tests / Executed Tests) × 100 for this requirement
- **Defect IDs:** Defects found during testing of this requirement (comma-separated)
- **Comments:** Notes, issues, or additional context

### Requirements-to-Test Cases Matrix

| Req ID | Requirement Description | Priority | Module | Test Case IDs | Coverage Status | Execution Status | Pass Rate | Defect IDs | Comments |
|--------|------------------------|----------|--------|---------------|-----------------|------------------|-----------|------------|----------|
| REQ-001 | [Description] | High | [Module] | TC-001, TC-002, TC-003 | ✅ Covered | Pass | 100% | - | All scenarios validated |
| REQ-002 | [Description] | High | [Module] | TC-004, TC-005 | ✅ Covered | Fail | 50% | DEF-012 | 1 test failed, defect logged |
| REQ-003 | [Description] | Medium | [Module] | TC-006 | ⚠️ Partial | Pass | 100% | - | May need more test cases |
| REQ-004 | [Description] | Medium | [Module] | - | ❌ Not Covered | - | - | - | Test case development pending |
| REQ-005 | [Description] | Low | [Module] | TC-007 | ✅ Covered | Not Run | - | - | Scheduled for next sprint |

### Test Cases-to-Requirements Matrix

**Purpose:** Reverse view showing which requirements each test case validates. Identifies orphan test cases not linked to requirements.

| Test Case ID | Test Case Title | Requirement IDs | Test Type | Priority | Execution Status | Pass/Fail | Defect IDs | Comments |
|--------------|-----------------|-----------------|-----------|----------|------------------|-----------|------------|----------|
| TC-001 | [Title] | REQ-001 | Functional | High | Pass | Pass | - | Validates positive scenario |
| TC-002 | [Title] | REQ-001 | Functional | High | Pass | Pass | - | Validates negative scenario |
| TC-003 | [Title] | REQ-001 | Regression | Medium | Pass | Pass | - | Regression check |
| TC-004 | [Title] | REQ-002 | Functional | High | Fail | Fail | DEF-012 | Checkout validation failed |
| TC-005 | [Title] | REQ-002 | Integration | High | Pass | Pass | - | API integration validated |
| TC-006 | [Title] | REQ-003 | Functional | Medium | Pass | Pass | - | |
| TC-007 | [Title] | REQ-005 | Functional | Low | Not Run | - | - | Deferred to next cycle |
| TC-999 | [Title] | None | Exploratory | Low | Pass | Pass | - | ⚠️ Orphan - no requirement link |

**Note:** Test cases with "None" in Requirement IDs column are orphan tests that should be reviewed - either link to requirements or remove if obsolete.

---

## Gap Analysis

**Purpose:** Identifies requirements without adequate test coverage that need attention.

### Requirements Without Coverage

**Priority:** These requirements have no test cases and need immediate attention.

| Req ID | Description | Priority | Module | Reason for Gap | Action Plan | Target Date | Owner |
|--------|-------------|----------|--------|----------------|-------------|-------------|-------|
| REQ-004 | [Description] | Medium | [Module] | Test case development delayed | Create TC-008 and TC-009 | [Date] | [Name] |
| REQ-015 | [Description] | Low | [Module] | Requirement added late | Create test case next sprint | [Date] | [Name] |

### Requirements with Insufficient Coverage

**Priority:** These requirements have test cases but coverage may be inadequate (e.g., only positive scenarios tested, no edge cases).

| Req ID | Description | Current Test Cases | Missing Scenarios | Action Plan | Target Date | Owner |
|--------|-------------|-------------------|-------------------|-------------|-------------|-------|
| REQ-003 | [Description] | TC-006 (positive only) | Negative scenario, edge cases | Add TC-010, TC-011 | [Date] | [Name] |
| REQ-018 | [Description] | TC-045 (basic test) | Performance, security testing | Add performance test | [Date] | [Name] |

### Orphan Test Cases

**Priority:** Test cases not linked to any requirement should be reviewed.

| Test Case ID | Title | Test Type | Reason | Recommendation |
|--------------|-------|-----------|--------|----------------|
| TC-999 | [Title] | Exploratory | No requirement link | Link to REQ-XXX or remove if obsolete |
| TC-888 | [Title] | Regression | Old requirement removed | Archive test case |

---

## Defect Impact Analysis

**Purpose:** Shows which requirements are affected by defects and their impact on coverage validation.

### Requirements with Open Defects

| Req ID | Description | Priority | Test Case IDs | Defect IDs | Defect Severity | Impact | Status |
|--------|-------------|----------|---------------|------------|-----------------|--------|--------|
| REQ-002 | [Description] | High | TC-004 | DEF-012 | High | Requirement not validated, blocking release | Open |
| REQ-008 | [Description] | Medium | TC-023 | DEF-045 | Medium | Partial validation, workaround exists | In Progress |
| REQ-012 | [Description] | High | TC-034 | DEF-067 | Critical | Complete failure, cannot validate | Open |

**Key Actions:**
- Requirements with Critical/High defects affecting High-priority requirements are release blockers
- Track defect resolution progress to unblock requirement validation
- May need to rerun test cases after defect fixes

### Defect-to-Requirement Mapping

**Purpose:** Links each defect back to the requirement(s) it affects for root cause analysis.

| Defect ID | Summary | Severity | Status | Related Requirements | Related Test Cases | Impact |
|-----------|---------|----------|--------|---------------------|-------------------|--------|
| DEF-012 | [Summary] | High | Open | REQ-002 | TC-004 | Cannot validate checkout flow |
| DEF-045 | [Summary] | Medium | In Progress | REQ-008, REQ-009 | TC-023, TC-024 | Partial functionality affected |
| DEF-067 | [Summary] | Critical | Open | REQ-012 | TC-034, TC-035 | Complete feature failure |

---

## Change Impact Analysis

**Purpose:** When requirements change, identifies which test cases need review or rerun.

### Recent Requirement Changes

**Track requirement modifications and their testing impact:**

| Req ID | Description | Change Date | Type of Change | Impacted Test Cases | Action Required | Status |
|--------|-------------|-------------|----------------|--------------------|--------------------|--------|
| REQ-007 | [Description] | [Date] | Modified | TC-018, TC-019, TC-020 | Review and update test cases | In Progress |
| REQ-021 | [Description] | [Date] | New | None | Create new test cases | Pending |
| REQ-033 | [Description] | [Date] | Deleted | TC-077, TC-078 | Archive test cases | Complete |

**Change Types:**
- **New:** Requirement added - need new test cases
- **Modified:** Requirement changed - review/update existing test cases
- **Deleted:** Requirement removed - archive related test cases
- **Clarified:** Requirement clarified - verify test cases still valid

---

## Test Coverage Heat Map

**Purpose:** Visual representation of coverage quality across requirements.

### Coverage Quality Indicators

**Legend:**
- 🟢 **Excellent:** High-priority requirement with multiple test cases, all passed
- 🟡 **Good:** Requirement covered, tests passed or minor issues
- 🟠 **Needs Attention:** Requirement covered but tests failed or coverage gaps
- 🔴 **Critical:** High-priority requirement not covered or critical defects

### Coverage by Module

| Module | Total Requirements | 🟢 Excellent | 🟡 Good | 🟠 Needs Attention | 🔴 Critical | Overall Status |
|--------|-------------------|-------------|---------|-------------------|--------------|----------------|
| Authentication | 15 | 10 | 3 | 2 | 0 | 🟢 Healthy |
| Shopping Cart | 22 | 12 | 6 | 3 | 1 | 🟠 Needs Work |
| Checkout | 18 | 8 | 5 | 2 | 3 | 🔴 Critical |
| Reporting | 10 | 7 | 3 | 0 | 0 | 🟢 Healthy |

**Actions Required:**
- **Checkout Module:** 3 critical gaps need immediate attention
- **Shopping Cart:** Address 1 critical gap and 3 needs attention items
- **All other modules:** Monitor good/needs attention items

---

## Best Practices for Traceability Management

### Creating the Matrix

**Do:**
- ✅ Start traceability mapping early in test case development
- ✅ Use unique, consistent IDs for requirements and test cases
- ✅ Link every test case to at least one requirement
- ✅ Link every requirement to at least one test case
- ✅ Include all test types (functional, integration, regression, performance, etc.)
- ✅ Document the rationale for test case counts per requirement
- ✅ Leverage test management tools for automated traceability

**Don't:**
- ❌ Wait until end of testing to create traceability matrix
- ❌ Use vague descriptions instead of specific IDs
- ❌ Leave requirements or test cases unmapped
- ❌ Forget to update matrix when requirements or tests change
- ❌ Create traceability only for compliance without using it actively
- ❌ Maintain traceability manually when tools can automate it

### Maintaining the Matrix

**Regular Updates:**
- Update immediately when requirements change
- Update when test cases are added, modified, or removed
- Update test execution status after each test run
- Link defects to requirements and test cases when logged
- Review and update during test planning for each cycle

**Quality Checks:**
- Verify no requirements are unmapped
- Check for orphan test cases
- Validate that high-priority requirements have adequate coverage
- Review pass rates for each requirement
- Ensure defects are properly linked

### Using the Matrix

**Coverage Analysis:**
- Identify requirements without test coverage before test execution
- Verify adequate coverage for high-priority requirements
- Find areas needing additional test scenarios
- Balance test case distribution across modules

**Impact Analysis:**
- When requirement changes, identify affected test cases
- Determine which tests need rerun after defect fixes
- Assess testing impact of feature additions or removals
- Prioritize regression testing based on requirement criticality

**Progress Tracking:**
- Monitor test execution completion by requirement
- Track requirement validation status
- Report coverage metrics to stakeholders
- Identify testing bottlenecks or delays

**Defect Analysis:**
- Link defects back to requirements for root cause analysis
- Identify requirements with high defect counts (quality concerns)
- Track defect resolution impact on requirement validation
- Support product quality assessment for release decisions

### Tool Integration

**Test Management Tools:**
- Jira (with Zephyr, Xray, or other test management plugins)
- TestRail
- Azure DevOps Test Plans
- qTest
- HP ALM/Quality Center

**Benefits of Tool-Based Traceability:**
- Automated linkage between requirements, tests, and defects
- Real-time coverage and execution reporting
- Bi-directional traceability maintained automatically
- Impact analysis with change tracking
- Visual coverage dashboards and reports
- Integration with CI/CD pipelines

---

## Related Templates and Documents

**Related Templates:**
- [Test Plan Template](test-plan-template.md) - References traceability approach and coverage targets
- [Test Case Template](test-case-template.md) - Individual test cases linked in this matrix
- [Test Execution Report Template](test-execution-report-template.md) - Reports coverage metrics from this matrix
- [Test Summary Report Template](test-summary-report-template.md) - Summarizes coverage achievements
- [Defect Report Template](defect-report-template.md) - Defects linked to requirements in this matrix

**Related Phase Documentation:**
- [Phase 2: Test Case Development](../phases/02-test-case-development.md) - Establishing traceability during test design
- [Phase 6: Test Results Reporting](../phases/06-test-results-reporting.md) - Reporting coverage results

---

**End of Traceability Matrix Template**
