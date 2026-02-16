# Test Case Template

**Version:** 1.0  
**Purpose:** This template provides a standardized format for documenting detailed test cases that validate specific functionality or requirements.  
**When to Use:** During Test Case Development (Phase 2), after requirements are understood and test planning is complete.

---

## Usage Guidance

### Who Should Use This Template?
- Test Engineers creating test cases
- Test Analysts designing test scenarios
- Automation Engineers documenting automated tests
- Business Analysts validating requirements coverage

### How to Use This Template
1. **Understand Requirements**: Thoroughly review the requirement or user story being tested
2. **Design Test Scenario**: Identify the specific condition or workflow to validate
3. **Document Steps**: Write clear, step-by-step instructions anyone can follow
4. **Define Expected Results**: Specify measurable, unambiguous expected outcomes
5. **Review**: Have test cases peer-reviewed before execution
6. **Maintain**: Update test cases when requirements or application behavior changes

### Tips for Writing Effective Test Cases
- **Be Specific**: Provide exact values, not "enter some text"
- **Be Atomic**: Test one thing at a time for easier debugging
- **Be Complete**: Include setup, execution, and cleanup steps
- **Be Clear**: Anyone should be able to execute without asking questions
- **Include Both Positive and Negative Scenarios**: Test both expected use and error conditions

---

## Test Case Information

**Field Explanations:**

| Field | Value | Purpose |
|-------|-------|---------|
| **Test Case ID** | TC-[Module]-[Number] | Unique identifier for tracking and reference (e.g., TC-LOGIN-001) |
| **Test Case Title** | [Descriptive title] | Clear summary of what is being tested |
| **Created By** | [Author name] | Original test case author |
| **Created Date** | [Date] | When test case was first created (YYYY-MM-DD) |
| **Last Modified By** | [Name] | Who made the most recent update |
| **Last Modified Date** | [Date] | Date of last modification |
| **Version** | [Version number] | Version tracking (e.g., 1.0, 1.1, 2.0) |

## Test Case Details

### Module/Feature
**What to include:** The specific module, feature, or functional area being tested.

*Example:* "User Authentication - Login Functionality" or "E-commerce - Shopping Cart"

[Name of the module or feature being tested]

### Test Objective
**What to include:** A brief, clear statement of what this test case aims to verify or validate.

*Example:* "Verify that users can successfully log in with valid credentials" or "Validate that users cannot proceed to checkout with an empty cart"

[Brief description of what this test case aims to verify]

### Priority
**Selection Guide:**
- **High**: Critical functionality, frequently used features, high-risk areas, must test before release
- **Medium**: Important features, moderate usage, should test in each cycle
- **Low**: Nice-to-have features, rarely used functionality, can defer if time constrained

- [ ] High
- [ ] Medium
- [ ] Low

### Test Type
**Selection Guide:** Choose all applicable types. A single test case can belong to multiple types.

- [ ] Functional - Validates feature meets functional requirements
- [ ] Integration - Tests interaction between components or systems
- [ ] Regression - Ensures existing functionality still works after changes
- [ ] Smoke - Quick validation of critical functionality
- [ ] Sanity - Focused check after specific changes
- [ ] Performance - Validates speed, scalability, or resource usage
- [ ] Security - Tests for vulnerabilities or access control
- [ ] Usability - Evaluates user experience and ease of use
- [ ] Other: [Specify]

### Test Method
**Selection Guide:**
- **Manual**: Best for exploratory, usability, visual validation, one-time tests
- **Automated**: Best for repetitive tests, regression suites, API testing, performance testing
- **Semi-Automated**: Combination of both (e.g., automated setup, manual validation)

- [ ] Manual
- [ ] Automated
- [ ] Semi-Automated

### Requirements Traceability
**Purpose:** Links test case to specific requirements for coverage tracking.

**What to include:** All requirement IDs that this test case validates. One test case can cover multiple requirements.

| Requirement ID | Requirement Description |
|----------------|-------------------------|
| REQ-[ID] | [Brief description of what requirement specifies] |

## Preconditions

**Purpose:** Lists conditions that must be satisfied before executing this test case.

**What to include:** 
- Required system state or configuration
- Required user accounts or permissions
- Required test data availability
- Prerequisite test cases that must pass first
- Required application state (e.g., user logged in, database seeded)

*Examples:*
- "User account 'testuser@example.com' exists in the system with active status"
- "Shopping cart contains at least one item"
- "Test database is reset to clean state"
- "User has 'Admin' role permissions"

[List all conditions that must be met before executing this test case]

1. [Precondition 1]
2. [Precondition 2]
3. [Precondition 3]

## Test Data

**Purpose:** Specifies exact data values needed for test execution.

**What to include:**
- Input values for fields
- Expected data states
- Test accounts and credentials
- Sample files or documents
- Configuration values

*Tip:* Be specific with actual values rather than placeholders. This ensures consistency across test executions.

[Specify the test data required for this test case]

| Data Type | Value | Description |
|-----------|-------|-------------|
| [Username] | [testuser@example.com] | [Valid test account] |
| [Password] | [Test@1234] | [Valid password for test account] |
| [Field name] | [Test value] | [Purpose/context] |

## Test Steps

**Purpose:** Provides step-by-step instructions for executing the test case.

**Instructions:**
- **Action**: What to do (e.g., "Click Login button", "Enter 'admin' in Username field")
- **Expected Result**: What should happen (e.g., "User is redirected to dashboard", "Error message displays")
- **Actual Result**: Leave blank until execution; document what actually happened
- **Status**: Mark as Pass/Fail/Blocked after execution
- **Comments**: Note any observations, deviations, or additional context

**Tips for Writing Steps:**
- Number steps sequentially
- Be explicit and detailed
- Use active voice
- Include specific values and locations
- One action per step when possible

| Step # | Action | Expected Result | Actual Result | Status | Comments |
|--------|--------|-----------------|---------------|--------|----------|
| 1 | [Navigate to login page at https://app.example.com/login] | [Login page displays with username, password fields and login button] | | | |
| 2 | [Enter 'testuser@example.com' in Username field] | [Text appears in username field] | | | |
| 3 | [Enter 'Test@1234' in Password field] | [Password is masked with dots] | | | |
| 4 | [Click 'Login' button] | [User is redirected to dashboard, welcome message displays] | | | |

## Postconditions

**Purpose:** Describes the expected system state after successful test execution.

**What to include:**
- Data changes that should persist
- System state changes
- Cleanup requirements
- Side effects of the test

*Examples:*
- "User session is established and remains active"
- "Transaction record is created in database"
- "Test data should be cleaned up after execution"
- "User remains logged in"

[List conditions that should be true after test execution]

1. [Postcondition 1]
2. [Postcondition 2]

## Test Execution

**Purpose:** Track execution history and results.

### Execution Status
**Status Definitions:**
- **Not Executed**: Test case has not been run yet
- **In Progress**: Currently being executed
- **Pass**: All steps passed, expected results matched actual results
- **Fail**: One or more steps failed, defect should be logged
- **Blocked**: Cannot execute due to blocker (environment issue, prerequisite failure, missing data)
- **Deferred**: Postponed to future cycle

- [ ] Not Executed
- [ ] In Progress
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- [ ] Deferred

### Executed By
**What to include:** Name of the tester who executed this test case

[Tester name]

### Execution Date
**What to include:** Date when this test case was executed (YYYY-MM-DD format)

[Date]

### Test Environment
**What to include:** Specific environment details where test was executed

*Examples:*
- "QA Environment - qa.example.com"
- "Staging Environment - Build #2024.01.15"
- "UAT Environment - Release 2.0 RC1"

[Description of environment where test was executed]

### Browser/Platform
**What to include:** Technical details relevant to test execution (if applicable)

*Examples:*
- "Chrome 120.0 on Windows 11"
- "Safari 17.2 on macOS Sonoma"
- "Mobile - iPhone 14, iOS 17.2"
- "Android - Samsung Galaxy S23, Android 14"

[If applicable: Browser version, OS, device type]

## Attachments

**Purpose:** Reference supporting evidence or documentation.

**What to include:**
- Screenshots showing test execution or defects
- Video recordings of test execution
- Log files or error messages
- Test output files
- Network traces or performance data

*Naming Convention:* Use descriptive names like "TC-LOGIN-001_failure_screenshot.png" or "TC-CART-005_video.mp4"

[List any attachments: screenshots, videos, logs]

1. [Attachment 1 name and description]
2. [Attachment 2 name and description]

## Defects

**Purpose:** Link to defects discovered during test execution for traceability.

**What to include:** Reference defect reports logged during test case execution. Update this section as defects are found and resolved.

[Link to any defects found during execution of this test case]

| Defect ID | Defect Summary | Severity | Status | Notes |
|-----------|----------------|----------|--------|-------|
| DEF-[ID] | [Brief description] | [Critical/High/Med/Low] | [Open/Fixed/Closed] | [Additional context] |

## Notes and Comments

**Purpose:** Capture additional observations, context, or information not covered elsewhere.

**What to include:**
- Observations during execution
- Suggestions for improvement
- Known issues or limitations
- Special instructions or warnings
- Historical context

*Examples:*
- "This test case is sensitive to network latency"
- "May need to clear browser cache before execution"
- "Feature behavior changed in v2.0 - test case updated accordingly"

[Any additional information, observations, or comments]

---

## Instructions for Using This Template

### Creating a New Test Case
1. **Test Case ID**: Use a consistent naming convention (e.g., TC-[MODULE]-[###])
   - TC-LOGIN-001, TC-LOGIN-002 for login module
   - TC-CART-001, TC-CART-002 for shopping cart
2. **Test Case Title**: Should be clear and descriptive
   - Good: "Verify successful login with valid credentials"
   - Poor: "Login test"
3. **Test Objective**: Explain what you're validating in one sentence
4. **Test Steps**: Be specific and detailed enough that anyone can execute
5. **Expected Results**: Should be clear and measurable, not vague
   - Good: "User is redirected to dashboard page (URL: /dashboard)"
   - Poor: "User is redirected"

### Executing a Test Case
1. Review preconditions and ensure they are met
2. Gather required test data
3. Follow test steps exactly as written
4. Document actual results for each step
5. Mark status (Pass/Fail/Blocked)
6. Take screenshots or evidence
7. Log defects for any failures
8. Update defects section with defect references

### Maintaining Test Cases
1. Review and update when requirements change
2. Update after application changes that affect the test
3. Refine based on feedback from test execution
4. Archive or remove obsolete test cases
5. Version control test case updates
6. Document significant changes in Notes section

## Best Practices

### Writing Test Cases
- **Keep test cases atomic**: Test one thing at a time for easier debugging
- **Make steps clear and unambiguous**: Anyone should understand without explanation
- **Include both positive and negative scenarios**: Test expected use and error conditions
- **Be specific with data**: Use actual values, not "enter some text"
- **Consider edge cases**: Boundary values, null values, special characters
- **Make test cases reusable**: Design for multiple test cycles

### Reviewing Test Cases
- Verify test cases before execution
- Check for completeness and clarity
- Ensure traceability to requirements
- Validate expected results are measurable
- Confirm test data is realistic

### Managing Test Cases
- Update test cases when requirements change
- Maintain version history
- Use consistent naming conventions
- Organize test cases logically (by module, feature, priority)
- Regular cleanup of obsolete test cases
- Keep test case repository current

---

## Related Templates and Documents

**Related Templates:**
- [Test Plan Template](test-plan-template.md) - Overall testing strategy and approach
- [Defect Report Template](defect-report-template.md) - For logging defects found during execution
- [Traceability Matrix Template](traceability-matrix-template.md) - For tracking requirements coverage

**Related Phase Documentation:**
- [Phase 2: Test Case Development](../phases/02-test-case-development.md) - Detailed guidance on creating test cases

---
**End of Test Case Template**
