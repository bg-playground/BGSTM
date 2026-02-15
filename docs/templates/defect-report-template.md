# Defect Report Template

## Defect Information

| Field | Value |
|-------|-------|
| **Defect ID** | DEF-[ID] |
| **Reported Date** | [Date] |
| **Reported By** | [Reporter Name] |
| **Assigned To** | [Developer Name] |
| **Status** | [New/Assigned/In Progress/Fixed/Retest/Verified/Closed/Reopened] |
| **Last Updated** | [Date] |

## Defect Classification

### Severity
- [ ] **Critical** - System crash, data loss, security breach, complete feature failure
- [ ] **High** - Major functionality not working, significant impact on users
- [ ] **Medium** - Functionality partially working, workaround available
- [ ] **Low** - Minor issues, cosmetic problems, minor inconvenience

### Priority
- [ ] **High** - Must fix immediately, blocking release
- [ ] **Medium** - Should fix soon, fix in current sprint/cycle
- [ ] **Low** - Can be deferred to future release

### Type
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

### Summary
[Brief one-line description of the defect]

### Description
[Detailed description of the issue, including what went wrong]

### Environment
- **Application Version**: [Version/Build Number]
- **Operating System**: [OS and Version]
- **Browser** (if applicable): [Browser and Version]
- **Device** (if applicable): [Device Type/Model]
- **Test Environment**: [Dev/QA/Staging/Production]
- **Database**: [Database version if relevant]

## Reproduction

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]

### Preconditions
[Any setup or conditions required before reproducing]

### Test Data Used
[Specific data used to reproduce the issue]

## Results

### Expected Result
[What should happen]

### Actual Result
[What actually happened]

### Reproducibility
- [ ] Always (100%)
- [ ] Frequent (> 50%)
- [ ] Sometimes (< 50%)
- [ ] Rare (< 10%)
- [ ] Once (Cannot reproduce)

## Impact

### Affected Features/Modules
[List impacted features or modules]

### User Impact
[How does this affect end users?]

### Business Impact
[Business consequences of this defect]

### Workaround Available
- [ ] Yes - [Describe workaround]
- [ ] No

## Attachments

### Screenshots
1. [Screenshot 1 description]
2. [Screenshot 2 description]

### Videos
1. [Video 1 description]

### Logs
1. [Log file 1]
2. [Log file 2]

### Other Files
1. [Other relevant files]

## Related Items

### Related Test Case
- **Test Case ID**: [TC-ID]
- **Test Case Title**: [Title]

### Related Requirement
- **Requirement ID**: [REQ-ID]
- **Requirement Description**: [Brief description]

### Related Defects
| Defect ID | Relationship | Description |
|-----------|--------------|-------------|
| DEF-[ID] | Duplicate/Related/Caused by | [Brief description] |

## Root Cause Analysis

### Root Cause
[Technical explanation of why the defect occurred - filled by developer]

### Root Cause Category
- [ ] Coding Error
- [ ] Design Flaw
- [ ] Requirements Gap
- [ ] Environment Issue
- [ ] Configuration Error
- [ ] Integration Issue
- [ ] Data Issue
- [ ] Other: [Specify]

## Resolution

### Resolution Description
[How the defect was fixed - filled by developer]

### Changed Files
[List of files modified to fix the defect]

### Code Review
- **Reviewed By**: [Reviewer Name]
- **Review Date**: [Date]
- **Review Status**: [Approved/Changes Requested]

### Unit Tests Added/Updated
- [ ] Yes - [Describe tests]
- [ ] No - [Reason]

## Verification

### Verified By
[Tester Name]

### Verification Date
[Date]

### Verification Status
- [ ] Pass - Fix verified, working as expected
- [ ] Fail - Issue still exists
- [ ] Partial - Partially fixed
- [ ] Not Verified

### Verification Environment
[Where the fix was verified]

### Regression Impact
[Any side effects or regression issues found during verification]

## Comments and History

| Date | User | Comment |
|------|------|---------|
| [Date] | [User] | [Comment] |
| [Date] | [User] | [Comment] |

## Metrics

### Time Tracking
- **Time to Detect**: [Hours/Days from code commit to detection]
- **Time to Fix**: [Hours/Days from assignment to fix]
- **Time to Verify**: [Hours/Days from fix to verification]
- **Total Cycle Time**: [Total time from detection to closure]

### Effort
- **Development Effort**: [Hours]
- **Testing Effort**: [Hours]

## Lessons Learned

### Prevention
[How could this defect have been prevented?]

### Process Improvements
[What process changes could help avoid similar defects?]

---

## Instructions for Using This Template

### For Testers (Reporting)
1. Fill in all fields in the Defect Information and Classification sections
2. Provide clear, detailed steps to reproduce
3. Attach all relevant screenshots and logs
4. Set appropriate severity and priority
5. Link to related test cases and requirements
6. Submit for triage/assignment

### For Developers (Fixing)
1. Update status as you work on the defect
2. Add comments to communicate progress
3. Fill in Root Cause Analysis section
4. Document the fix in Resolution section
5. Add/update unit tests
6. Request code review
7. Move to "Ready for Retest" when complete

### For Testers (Verifying)
1. Review the fix description
2. Re-execute test cases
3. Check for regression issues
4. Fill in Verification section
5. Close if verified, or reopen with details if not fixed

## Best Practices

- **Be Specific**: Provide exact steps, not general descriptions
- **Be Objective**: State facts, not opinions
- **Be Complete**: Include all relevant information
- **Be Clear**: Use simple, unambiguous language
- **Be Professional**: Keep tone constructive and respectful
- **Attach Evidence**: Always include screenshots or logs
- **Update Promptly**: Keep status and comments current
- **Link Related Items**: Connect to test cases, requirements, other defects

---
**End of Defect Report Template**
