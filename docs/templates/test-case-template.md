# Test Case Template

## Test Case Information

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-[Module]-[Number] |
| **Test Case Title** | [Descriptive title of the test case] |
| **Created By** | [Author name] |
| **Created Date** | [Date] |
| **Last Modified By** | [Name] |
| **Last Modified Date** | [Date] |
| **Version** | [Version number] |

## Test Case Details

### Module/Feature
[Name of the module or feature being tested]

### Test Objective
[Brief description of what this test case aims to verify]

### Priority
- [ ] High
- [ ] Medium
- [ ] Low

### Test Type
- [ ] Functional
- [ ] Integration
- [ ] Regression
- [ ] Smoke
- [ ] Sanity
- [ ] Performance
- [ ] Security
- [ ] Usability
- [ ] Other: [Specify]

### Test Method
- [ ] Manual
- [ ] Automated
- [ ] Semi-Automated

### Requirements Traceability
| Requirement ID | Requirement Description |
|----------------|-------------------------|
| REQ-[ID] | [Brief description] |

## Preconditions

[List all conditions that must be met before executing this test case]

1. [Precondition 1]
2. [Precondition 2]
3. [Precondition 3]

## Test Data

[Specify the test data required for this test case]

| Data Type | Value | Description |
|-----------|-------|-------------|
| [Field name] | [Test value] | [Purpose] |
| [Field name] | [Test value] | [Purpose] |

## Test Steps

| Step # | Action | Expected Result | Actual Result | Status | Comments |
|--------|--------|-----------------|---------------|--------|----------|
| 1 | [Action to perform] | [Expected outcome] | | | |
| 2 | [Action to perform] | [Expected outcome] | | | |
| 3 | [Action to perform] | [Expected outcome] | | | |
| 4 | [Action to perform] | [Expected outcome] | | | |

## Postconditions

[List conditions that should be true after test execution]

1. [Postcondition 1]
2. [Postcondition 2]

## Test Execution

### Execution Status
- [ ] Not Executed
- [ ] In Progress
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- [ ] Deferred

### Executed By
[Tester name]

### Execution Date
[Date]

### Test Environment
[Description of environment where test was executed]

### Browser/Platform
[If applicable: Browser version, OS, device type]

## Attachments

[List any attachments: screenshots, videos, logs]

1. [Attachment 1 name and description]
2. [Attachment 2 name and description]

## Defects

[Link to any defects found during execution of this test case]

| Defect ID | Defect Summary | Severity | Status |
|-----------|----------------|----------|--------|
| DEF-[ID] | [Brief description] | [Critical/High/Med/Low] | [Open/Fixed/Closed] |

## Notes and Comments

[Any additional information, observations, or comments]

---

## Instructions for Using This Template

1. **Test Case ID**: Use a consistent naming convention (e.g., TC-LOGIN-001)
2. **Test Case Title**: Should be clear and descriptive
3. **Test Objective**: Explain what you're validating
4. **Test Steps**: Be specific and detailed enough that anyone can execute
5. **Expected Results**: Should be clear and measurable
6. **Actual Results**: Document exactly what happened during execution
7. **Status**: Update after each execution
8. **Defects**: Link related defects for traceability

## Best Practices

- Keep test cases atomic (test one thing at a time)
- Make steps clear and unambiguous
- Include both positive and negative scenarios
- Review test cases before execution
- Update test cases when requirements change
- Version control your test cases
- Make test cases reusable across test cycles

---
**End of Test Case Template**
