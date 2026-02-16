# Defect Report Template

**Version:** 1.0  
**Purpose:** This template provides a standardized format for documenting and tracking defects discovered during testing, ensuring comprehensive defect information for efficient resolution and analysis.  
**When to Use:** During Test Execution (Phase 4), whenever a defect is discovered that deviates from expected behavior or requirements.

---

## Usage Guidance

### Who Should Use This Template?
- Testers discovering and reporting defects
- QA Engineers documenting issues
- Developers analyzing and fixing defects
- Test Leads managing defect triage
- Business Analysts validating defect fixes

### How to Use This Template
1. **Discover Defect**: Identify behavior that deviates from expected results during test execution
2. **Gather Information**: Collect all relevant details (steps, environment, screenshots)
3. **Classify**: Assign appropriate severity and priority based on impact
4. **Document**: Fill in all sections with clear, specific information
5. **Attach Evidence**: Include screenshots, logs, videos to support the report
6. **Submit**: Log defect in tracking system and notify relevant stakeholders
7. **Track**: Update status and add comments as defect progresses through workflow

### Tips for Effective Defect Reporting
- **Be Specific**: Provide exact steps to reproduce, not vague descriptions
- **Be Objective**: Report facts, not opinions or assumptions
- **Be Complete**: Include all relevant information in the initial report
- **Provide Context**: Explain the business impact and user experience
- **Include Evidence**: Always attach screenshots, logs, or videos
- **Test Reproducibility**: Verify you can reproduce the defect before reporting
- **Check for Duplicates**: Search existing defects to avoid duplicate reports

---

## Defect Information

**Field Explanations:** This section captures essential tracking and workflow information.

| Field | Value | Instructions |
|-------|-------|--------------|
| **Defect ID** | DEF-[ID] | Unique identifier following naming convention: DEF-[Module]-[Number] (e.g., DEF-LOGIN-001, DEF-CART-042) |
| **Reported Date** | [Date] | Date defect was discovered and reported (YYYY-MM-DD format) |
| **Reported By** | [Reporter Name] | Name of tester or person who discovered the defect |
| **Assigned To** | [Developer Name] | Developer or team member responsible for fixing the defect |
| **Status** | [New/Assigned/In Progress/Fixed/Retest/Verified/Closed/Reopened] | Current state in defect lifecycle workflow |
| **Last Updated** | [Date] | Date of most recent update or status change |

## Defect Classification

**Purpose:** Properly classifying defects helps prioritize fixes and allocate resources effectively.

### Severity

**What this means:** Severity measures the technical impact of the defect on the system or functionality.

**Selection Guide:**
- [ ] **Critical** - System crash, data loss, security breach, complete feature failure affecting all users
  - *Examples:* "Application crashes on login preventing all access", "Database corruption causing data loss", "Security vulnerability exposing user data", "Payment processing completely non-functional"
- [ ] **High** - Major functionality not working, significant impact on users, no reasonable workaround
  - *Examples:* "Shopping cart checkout fails for all payment methods", "Search returns no results", "Unable to upload files", "Critical business workflow broken"
- [ ] **Medium** - Functionality partially working, workaround available, moderate user impact
  - *Examples:* "Search returns incorrect results for special characters", "Report exports with formatting issues", "UI element misaligned on specific screen size", "Non-critical feature not working"
- [ ] **Low** - Minor issues, cosmetic problems, minimal user impact, suggestions for improvement
  - *Examples:* "Button alignment slightly off", "Typo in help text", "Color contrast could be improved", "Minor UI inconsistency"

**Note:** Severity is based on technical impact, not urgency. A low-severity defect can have high priority if it's visible to all users.

### Priority

**What this means:** Priority indicates the urgency of fixing the defect based on business impact and release plans.
**Selection Guide:**
- [ ] **High** - Must fix immediately, blocking release or critical functionality, affecting many users
  - *When to use:* Release blockers, security issues, data loss scenarios, critical business impact
- [ ] **Medium** - Should fix in current release/sprint, important but not blocking
  - *When to use:* Important features with workarounds, visible issues affecting user experience
- [ ] **Low** - Can be deferred to future releases, minimal business impact
  - *When to use:* Cosmetic issues, nice-to-have improvements, minor inconveniences

**Important:** Priority and severity can differ. Examples:
- *High Priority, Low Severity:* Typo on main login page (cosmetic but visible to all users)
- *Low Priority, High Severity:* Admin feature broken but only used once per month

### Type

**What this means:** Categorizes the nature of the defect to help with analysis and process improvement.
- [ ] Functional
- [ ] Performance
- [ ] Security
- [ ] Usability
- [ ] Compatibility
- [ ] Data
- [ ] UI/UX
- [ ] Documentation
- [ ] Other: [Specify]

## Defect Details

**Purpose:** Provides clear, detailed information about the defect for understanding and resolution.

### Summary

**What to include:** A concise, descriptive one-line summary that clearly identifies the issue.

**Best Practices:**
- Start with the affected area or feature (e.g., "Login:", "Shopping Cart:", "Dashboard:")
- Be specific about what's wrong, not just where
- Good: "Login: Application crashes when user enters special characters in username"
- Poor: "Login broken" or "Error in application"

[Brief one-line description of the defect]

### Description

**What to include:** Detailed explanation of the defect including:
- What functionality is affected
- What went wrong
- Under what conditions the defect occurs
- Any error messages displayed
- Business impact and user experience impact

**Tips:**
- Provide context and background information
- Explain what the user was trying to accomplish
- Include exact error messages (copy/paste, don't paraphrase)
- Describe the impact on user workflows or business processes

*Example:* "When users attempt to checkout with more than 10 items in their cart, the application displays error 'ERR_CART_LIMIT' and prevents checkout. This blocks users from completing large orders. The error occurs consistently across all browsers and appears to be a hard-coded limit not mentioned in requirements."
[Detailed description of the issue, including what went wrong]

### Environment

**Purpose:** Environment details are critical for reproducing and debugging defects. Different environments may exhibit different behaviors.

**What to include:** Specific versions and configurations where the defect was observed.
- **Application Version**: [Version/Build Number] - *Example: v2.5.1, Build #2024.02.15.3*
- **Operating System**: [OS and Version] - *Example: Windows 11 Pro 22H2, macOS Sonoma 14.2, Ubuntu 22.04 LTS*
- **Browser** (if applicable): [Browser and Version] - *Example: Chrome 121.0.6167.85, Firefox 122.0, Safari 17.2*
- **Device** (if applicable): [Device Type/Model] - *Example: iPhone 15 Pro, Samsung Galaxy S23, Desktop PC*
- **Test Environment**: [Dev/QA/Staging/Production] - *Specify which environment: QA-Environment-01, staging.example.com*
- **Database**: [Database version if relevant] - *Example: PostgreSQL 15.2, MongoDB 7.0*
- **Screen Resolution** (if UI issue): [Resolution] - *Example: 1920x1080, 1366x768*
- **Network Conditions** (if relevant): [Connection type/speed] - *Example: WiFi, 4G Mobile, VPN*

**Tip:** The more specific you are about the environment, the easier it is to reproduce and fix the defect.

## Reproduction

**Purpose:** Clear reproduction steps are the most critical part of a defect report. If developers cannot reproduce the issue, they cannot fix it.

### Steps to Reproduce

**How to write effective steps:**
- Number each step sequentially
- Be explicit and detailed (anyone should be able to follow)
- Include exact values, URLs, and navigation paths
- Start from a known state (e.g., "Starting from the login page...")
- Use active, imperative voice (Click, Enter, Select, etc.)
- One action per step when possible

**Good Example:**
1. Navigate to https://qa.example.com/login
2. Enter username: "testuser@example.com"
3. Enter password: "Test@1234"
4. Click the "Login" button
5. Navigate to Shopping Cart page by clicking cart icon
6. Click "Checkout" button
7. Observe error message

**Poor Example:**
1. Login to the app
2. Go to cart
3. Try to checkout
4. Error appears

[Detailed numbered steps to reproduce the defect]
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]

### Preconditions

**What to include:** Any setup, configuration, or data that must exist before the steps to reproduce.

**Examples:**
- "User account 'testuser@example.com' must exist in the system"
- "Database must have at least 10 products in the catalog"
- "User must have 'Admin' role permissions"
- "Shopping cart must contain items before starting these steps"

[Any setup or conditions required before reproducing]

### Test Data Used

**Purpose:** Specific data values used help developers reproduce exact conditions.

**What to include:**
- Exact input values used
- Test account credentials (for test environments only)
- File names and sample files
- Configuration values
- Any data that influenced the defect

*Example:*
- Username: testuser@example.com
- Password: Test@1234
- Product IDs: PRD-001, PRD-002, PRD-003
- Sample file: test_upload.pdf (2.5 MB)

[Specific data used to reproduce the issue]

## Results

**Purpose:** Clearly contrast what should happen versus what actually happens.

### Expected Result

**What to include:** Clear, specific description of correct behavior based on requirements or specifications.

**Tips:**
- Reference requirements when possible (e.g., "Per requirement REQ-LOGIN-01...")
- Be specific and measurable
- Describe the complete expected outcome
- Good: "User should be redirected to dashboard (URL: /dashboard) within 2 seconds, with welcome message 'Welcome, Test User' displayed"
- Poor: "User should be logged in"

[What should happen according to requirements or expected behavior]

### Actual Result

**What to include:** Exact description of what actually occurred, including error messages.

**Tips:**
- Copy exact error messages (don't paraphrase)
- Describe what's visible to the user
- Include codes, stack traces, or technical details if available
- Note any side effects or secondary issues
- Good: "Application displays error dialog with message 'ERR_503: Service Unavailable' and remains on login page. Network tab shows 503 response from /api/auth endpoint"
- Poor: "Error appeared"
[What actually happened - be specific and include exact error messages]

### Reproducibility

**Purpose:** Indicates how consistently the defect occurs, which affects prioritization and debugging strategy.

**Selection Guide:**
- [ ] Always (100%) - Occurs every time steps are followed (easiest to fix)
- [ ] Frequent (> 50%) - Occurs more often than not (needs investigation into varying conditions)
- [ ] Sometimes (< 50%) - Occurs occasionally (may be timing or data dependent)
- [ ] Rare (< 10%) - Difficult to reproduce consistently (hardest to debug)
- [ ] Once (Cannot reproduce) - Occurred once, unable to reproduce (document thoroughly, may close if cannot reproduce)

**Tip:** If reproducibility is less than 100%, note any patterns (time of day, specific data, system load, etc.)

## Impact

**Purpose:** Helps stakeholders understand the business and user consequences of the defect.

### Affected Features/Modules

**What to include:** List all features, modules, or areas impacted by this defect.

*Examples:*
- "Login module - all authentication methods"
- "Shopping Cart and Checkout workflows"
- "Dashboard reporting widgets"
- "Mobile app - iOS version only"

[List impacted features or modules]

### User Impact

**What to include:** Describe how this defect affects end users' ability to accomplish their tasks.

**Be specific about:**
- How many users are affected (all users, specific roles, percentage)
- What user actions are blocked or impaired
- User frustration or confusion caused
- Any data loss or corruption risks

*Example:* "Affects all registered users attempting to make purchases. Users cannot complete checkout, leading to abandoned carts and lost sales. Approximately 200 daily transactions are impacted."
[How does this affect end users? Be specific about user experience and functionality impact]

### Business Impact

**What to include:** Financial, operational, or reputational consequences from a business perspective.

**Consider:**
- Revenue impact (lost sales, delayed revenue)
- Operational costs (support tickets, manual workarounds)
- Compliance or legal risks
- Brand reputation impact
- Customer satisfaction and retention

*Example:* "Estimated $10,000 daily revenue loss due to blocked checkout. May require customer support team to process orders manually. Risk of negative reviews and customer churn if not resolved quickly."

[Business consequences of this defect - revenue impact, compliance issues, reputation, etc.]

### Workaround Available

**Purpose:** Identifies if users can accomplish their goal through an alternative method while fix is pending.
- [ ] Yes - [Describe the workaround: What alternative steps can users take to accomplish their goal?]
  - *Example:* "Users can contact customer support to process order manually" or "Use desktop version instead of mobile"
- [ ] No - [No alternative method available]

**Note:** Existence of a workaround may affect priority but should not affect severity rating.

## Attachments

**Purpose:** Visual and technical evidence significantly improves defect understanding and speeds resolution.

**Best Practices:**
- Attach evidence at the time of reporting (not "will provide later")
- Use clear, descriptive file names (e.g., "DEF-LOGIN-001_error_screenshot.png")
- Annotate screenshots to highlight the issue (arrows, circles, boxes)
- Include console logs or network traces for technical defects
- Record videos for complex workflows or timing-related issues

### Screenshots

**What to capture:**
- The error or incorrect behavior
- Full screen context (not just the error message)
- Multiple screenshots showing the workflow if needed
- Annotated screenshots highlighting specific issues

[List screenshot files with brief descriptions]
1. [Screenshot 1 description] - *Example: "error_dialog_showing_ERR_503.png - Error dialog displayed to user"*
2. [Screenshot 2 description]

### Videos

**When to use videos:**
- Complex multi-step workflows
- Timing or animation issues
- Intermittent issues that are hard to capture in screenshots
- Demonstrating user interaction flows

**Tips:**
- Keep videos short and focused (under 2 minutes)
- Include audio narration if helpful
- Show cursor movements clearly
- Start recording from a known, stable state

[List video files with descriptions]
1. [Video 1 description] - *Example: "checkout_failure.mp4 - Complete checkout flow showing error at payment step"*

### Logs

**What to include:**
- Browser console logs (JavaScript errors, warnings)
- Application logs (server-side errors, stack traces)
- Network logs (failed API calls, error responses)
- Database query logs (if relevant)
- Mobile device logs (iOS Console, Android Logcat)

**Tips:**
- Include timestamps to correlate with reproduction steps
- Capture logs at time of defect occurrence
- Include several lines before and after the error for context
- Filter out noise but include relevant warnings

[List log files]
1. [Log file 1] - *Example: "console_errors.log - Browser console errors during checkout"*
2. [Log file 2]

### Other Files

**What to include:**
- Sample data files that trigger the issue
- Configuration files relevant to the defect
- Network traces (HAR files)
- Performance profiles
- Database dumps (sanitized)

[Other relevant files]
1. [Other file description]

## Related Items

**Purpose:** Links defects to test cases, requirements, and other defects for traceability and impact analysis.

### Related Test Case

**What to include:** Reference the test case that discovered this defect or that validates the fix.
- **Test Case ID**: [TC-ID] - *Example: TC-CHECKOUT-015*
- **Test Case Title**: [Title] - *Example: "Verify successful checkout with credit card payment"*

### Related Requirement

**What to include:** Link to the requirement that this defect violates or relates to.

**Why this matters:** Demonstrates requirement non-compliance and aids in traceability matrix updates.

- **Requirement ID**: [REQ-ID] - *Example: REQ-PAYMENT-003*
- **Requirement Description**: [Brief description] - *Example: "System shall support checkout with all major credit cards"*

### Related Defects

**Purpose:** Identifies relationships between defects for better analysis and resolution planning.

**Relationship Types:**
- **Duplicate:** Another report of the same issue
- **Related:** Similar issue in same area
- **Caused by:** This defect was introduced by fixing another defect
- **Blocks:** This defect prevents testing or fixing another defect
- **Depends on:** This defect can only be fixed after another is resolved

| Defect ID | Relationship | Description |
|-----------|--------------|-------------|
| DEF-[ID] | Duplicate/Related/Caused by/Blocks/Depends on | [Brief description] |

## Root Cause Analysis

**Purpose:** Understanding why the defect occurred helps prevent similar issues in the future. This section is typically filled by the developer who fixes the defect.

### Root Cause

**What to include:** Technical explanation of why the defect occurred, not just what was wrong.

**Good root cause analysis includes:**
- What code, logic, or configuration caused the issue
- Why the issue wasn't caught earlier (unit tests, code review, etc.)
- Environmental or timing factors if relevant
- Assumptions that proved incorrect

*Example:* "The checkout API had a hard-coded limit of 10 items that was not documented in requirements. This limit was added as a temporary measure in v1.5 and was never removed. The validation logic in OrderController.js line 234 throws an exception when cart.items.length > 10."
[Technical explanation of why the defect occurred - filled by developer]

### Root Cause Category

**Purpose:** Categorizing root causes helps identify patterns and process improvements.
- [ ] Coding Error
- [ ] Design Flaw
- [ ] Requirements Gap
- [ ] Environment Issue
- [ ] Configuration Error
- [ ] Integration Issue
- [ ] Data Issue
- [ ] Other: [Specify]

## Resolution

**Purpose:** Documents how the defect was fixed and what changed. This section is filled by the developer.

### Resolution Description

**What to include:**
- Summary of the fix implemented
- Technical approach taken
- Why this approach was chosen
- Any limitations or side effects of the fix
- Testing done by developer before marking as fixed

*Example:* "Removed the hard-coded 10-item limit from OrderController.js. Updated validation logic to allow up to 100 items per cart (new business requirement). Added unit tests to cover edge cases for large cart sizes. Tested manually with 1, 10, 50, 100, and 101 items to verify behavior."

[How the defect was fixed - filled by developer]

### Changed Files

**What to include:** List all files modified to implement the fix.

**Why this matters:** Helps with code review, regression testing, and understanding fix scope.

*Example:*
- src/controllers/OrderController.js (modified validation logic)
- src/config/limits.js (added MAX_CART_ITEMS constant)
- tests/unit/OrderController.test.js (added test cases)

[List of files modified to fix the defect]

### Code Review

**Purpose:** Ensures fix quality and knowledge sharing.
- **Reviewed By**: [Reviewer Name]
- **Review Date**: [Date]
- **Review Status**: [Approved/Changes Requested]
- **Review Comments**: [Any significant review feedback or concerns]

### Unit Tests Added/Updated

**Purpose:** Ensures the fix is covered by automated tests to prevent regression.
- [ ] Yes - [Describe tests: What scenarios are now covered?]
  - *Example:* "Added 5 unit tests covering cart sizes from 0 to 150 items. Added integration test for checkout with large cart."
- [ ] No - [Reason: Why weren't tests added?]
  - *Valid reasons:* UI-only change with manual test, test infrastructure not available, covered by existing tests

## Verification

**Purpose:** Confirms the fix resolves the defect without introducing new issues. This section is filled by the tester.

### Verified By

**What to include:** Name of the tester who verified the fix.

[Tester Name]

### Verification Date

[Date when verification testing was performed]

### Verification Status

**Selection Guide:**
- [ ] Pass - Fix verified, working as expected. Defect can be closed.
- [ ] Fail - Issue still exists or not completely fixed. Reopen defect with details.
- [ ] Partial - Partially fixed but some aspects remain. Document what works and what doesn't.
- [ ] Not Verified - Unable to verify due to blocker or environment issue.

**If status is Fail or Partial, provide details in Comments section.**

### Verification Environment

**What to include:** Specific environment where fix was verified (may differ from original defect environment).
*Example:* "QA Environment - Build #2024.02.20.1, Chrome 121 on Windows 11"

[Where the fix was verified - environment, build, browser]

### Regression Impact

**Purpose:** Identifies any side effects or new issues introduced by the fix.

**What to check:**
- Related functionality still works correctly
- No new errors or warnings introduced
- Performance hasn't degraded
- Other modules not unexpectedly affected

**What to document:**
- Any new issues discovered (file separate defects if found)
- Related test cases executed and their results
- Specific regression scenarios tested

*Example:* "Executed full checkout regression suite (15 test cases). All passed. No performance degradation observed. Verified cart functionality with 1, 10, 50, 100 items. No new issues found."

[Any side effects or regression issues found during verification. Note "None" if no issues.]

## Comments and History

**Purpose:** Provides audit trail and communication thread for the defect lifecycle.

**Best Practices:**
- Add comments whenever status changes
- Explain decisions (why priority changed, why closing without fix, etc.)
- Communicate blockers or delays promptly
- Keep comments professional and factual
- Include timestamps for time-sensitive information

| Date | User | Comment |
|------|------|---------|
| [Date] | [User] | [Comment - Example: "Defect confirmed. Assigning to development team. High priority due to production impact."] |
| [Date] | [User] | [Comment] |

## Metrics

**Purpose:** Tracking time metrics helps improve development and testing processes.

### Time Tracking

**What these metrics show:**
- **Time to Detect:** How quickly defects are found after code introduction (shorter is better - suggests effective testing)
- **Time to Fix:** Development efficiency and defect complexity
- **Time to Verify:** Testing efficiency
- **Total Cycle Time:** Overall defect resolution speed

[Hours/Days from key points in defect lifecycle]
- **Time to Detect**: [Hours/Days from code commit to detection] - *Example: "2 days (feature deployed Monday, defect found Wednesday)"*
- **Time to Fix**: [Hours/Days from assignment to fix] - *Example: "4 hours"*
- **Time to Verify**: [Hours/Days from fix to verification] - *Example: "1 day"*
- **Total Cycle Time**: [Total time from detection to closure] - *Example: "3.5 days"*

### Effort

**Purpose:** Tracks actual time invested for resource planning and estimation improvement.

- **Development Effort**: [Hours] - *Time spent analyzing, fixing, testing, and reviewing*
- **Testing Effort**: [Hours] - *Time spent reproducing, verifying, and regression testing*

## Lessons Learned

**Purpose:** Captures insights to prevent similar defects in the future. This section drives process improvement.

### Prevention

**What to include:** Specific actions that could have prevented this defect.

**Questions to consider:**
- Could this have been caught in code review?
- Should we add this to our testing checklist?
- Was there a gap in requirements or specifications?
- Do we need better validation or error handling?
- Should we add automated tests for this scenario?

*Example:* "This defect could have been prevented by: (1) Adding input validation unit tests for edge cases, (2) Documenting all business rules in requirements, (3) Including large dataset scenarios in test plan"

[How could this defect have been prevented? Be specific.]

### Process Improvements

**What to include:** Changes to development, testing, or communication processes to reduce similar defects.

**Consider improvements to:**
- Code review checklists
- Testing strategies and coverage
- Requirements documentation standards
- Development coding standards
- CI/CD pipeline checks
- Knowledge sharing practices

*Example:* "Process improvements: (1) Add 'boundary value testing' to test case development checklist, (2) Require unit tests for all input validation logic, (3) Create coding standard for documenting business rule constants"

[What process changes could help avoid similar defects?]

---

## Best Practices for Defect Reporting

### For Testers

**Do:**
- ✅ Report defects as soon as discovered
- ✅ Verify reproducibility before reporting (try at least 2-3 times)
- ✅ Check for duplicate defects before creating new reports
- ✅ Provide complete information in initial report
- ✅ Include specific reproduction rate if less than 100%
- ✅ Attach screenshots, logs, and videos
- ✅ Be objective and professional in descriptions
- ✅ Include both positive and negative test results
- ✅ Link to related test cases and requirements

**Don't:**
- ❌ Report multiple defects in one report (create separate reports)
- ❌ Use vague terms like "doesn't work" or "broken"
- ❌ Assume information is obvious (be explicit)
- ❌ Report without attaching evidence
- ❌ Over-estimate or under-estimate severity/priority
- ❌ Include personal opinions or blame
- ❌ Leave sections incomplete (fill all applicable fields)

### For Developers

**Do:**
- ✅ Update status promptly as you work on the defect
- ✅ Add comments to communicate progress and blockers
- ✅ Ask clarifying questions if reproduction steps are unclear
- ✅ Document root cause and resolution thoroughly
- ✅ Add or update unit tests with the fix
- ✅ Request code review before marking as fixed
- ✅ Verify fix locally before moving to "Retest"
- ✅ Check for similar defects that might need the same fix

**Don't:**
- ❌ Close defects without proper verification
- ❌ Mark as "Cannot Reproduce" without thorough investigation
- ❌ Fix defects without understanding root cause
- ❌ Introduce changes without test coverage
- ❌ Ignore severity/priority ratings
- ❌ Skip documentation of the fix

### Severity vs. Priority Guidelines

**Understanding the Difference:**
- **Severity:** Technical impact on the system (what breaks)
- **Priority:** Business urgency of the fix (when to fix)

**Common Combinations:**

| Scenario | Severity | Priority | Example |
|----------|----------|----------|---------|
| Critical feature broken, blocking release | Critical | High | Payment processing completely fails |
| Major feature broken, workaround exists | High | Medium | Report export fails but data accessible another way |
| Visible cosmetic issue | Low | High | Typo on main landing page seen by all users |
| Minor issue in rarely used feature | Low | Low | Formatting issue in admin-only legacy report |
| Performance degradation | Medium | High | Page load time increased 300% |
| Security vulnerability | Critical | High | SQL injection vulnerability discovered |

### Communication Tips

1. **Be Clear and Concise**
   - Use simple language, avoid jargon unless necessary
   - One defect per report
   - Use bullet points for clarity

2. **Be Constructive**
   - Focus on the problem, not blame
   - Suggest potential causes if you have insights
   - Offer to help with investigation if needed

3. **Be Responsive**
   - Answer questions promptly
   - Provide additional information when requested
   - Update status when situation changes

4. **Be Thorough**
   - Anticipate questions and answer them preemptively
   - Provide complete environment details
   - Include all relevant evidence

---

## Related Templates and Documents

**Related Templates:**
- [Test Case Template](test-case-template.md) - For creating test cases that may discover defects
- [Test Execution Report Template](test-execution-report-template.md) - For reporting defect statistics and trends
- [Test Summary Report Template](test-summary-report-template.md) - For executive-level defect reporting

**Related Phase Documentation:**
- [Phase 4: Test Execution](../phases/04-test-execution.md) - Guidance on defect discovery during test execution
- [Phase 5: Test Results Analysis](../phases/05-test-results-analysis.md) - Analyzing defect patterns and trends

---

**End of Defect Report Template**
