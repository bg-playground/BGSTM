# Risk Assessment Template

**Version:** 1.0  
**Purpose:** This template provides a structured approach to identifying, analyzing, and managing risks that could impact testing activities and project quality. It helps teams proactively plan mitigation strategies.  
**When to Use:** During Test Planning (Phase 1) and continuously throughout Test Execution (Phase 4) and Test Results Analysis (Phase 5). Update as new risks emerge or existing risks change.

---

## Usage Guidance

### Who Should Use This Template?
- Test Managers identifying and managing testing risks
- Test Leads planning risk mitigation strategies
- Project Managers assessing overall project risk
- Quality Assurance teams evaluating quality risks
- Stakeholders reviewing risk exposure and mitigation plans

### How to Use This Template
1. **Identify Risks**: Brainstorm potential risks through team discussions, lessons learned, historical data
2. **Analyze**: Assess probability and impact for each risk
3. **Calculate Risk Score**: Use Risk Score = Probability × Impact to prioritize
4. **Plan Mitigation**: Develop strategies to prevent or minimize each risk
5. **Assign Owners**: Designate who is responsible for monitoring and mitigating each risk
6. **Monitor**: Regularly review risks and update status
7. **Update**: Add new risks as discovered, close risks that are no longer relevant

### Tips for Effective Risk Assessment
- **Be Proactive**: Identify risks early before they become issues
- **Be Realistic**: Assess probability and impact honestly
- **Be Comprehensive**: Consider technical, resource, schedule, and external risks
- **Be Specific**: Vague risks lead to vague mitigation plans
- **Review Regularly**: Risks change as projects progress
- **Learn from History**: Review past projects for common risks
- **Engage the Team**: Multiple perspectives identify more risks

---

## Document Control

**Field Explanations:** This section tracks document metadata and approval workflow.

| Field | Value | Instructions |
|-------|-------|--------------|
| **Project Name** | [Project Name] | Full name of the project being assessed |
| **Document Version** | [Version Number] | Version of this risk assessment (e.g., 1.0, 1.1, 2.0) |
| **Assessment Date** | [Date] | Date of current assessment (YYYY-MM-DD format) |
| **Prepared By** | [Name] | Person who prepared this risk assessment |
| **Reviewed By** | [Name(s)] | Person(s) who reviewed the assessment |
| **Next Review Date** | [Date] | When this assessment should be reviewed next |
| **Status** | [Draft/Active/Archived] | Current state of the document |

### Revision History

| Version | Date | Author | Description of Changes |
|---------|------|--------|------------------------|
| 1.0 | | | Initial risk assessment |

---

## Risk Rating Scale

**Purpose:** Defines how to rate probability and impact consistently across all risks.

### Probability Ratings

**Definition:** Likelihood that the risk will occur during the project.

| Rating | Range | Description | When to Use |
|--------|-------|-------------|-------------|
| **High** | > 60% | Very likely to occur | Strong indicators present, happened in similar projects |
| **Medium** | 30-60% | May occur | Some indicators present, possible but not certain |
| **Low** | < 30% | Unlikely to occur | Few indicators, rarely happens |

### Impact Ratings

**Definition:** Consequence if the risk occurs, measured by effect on schedule, quality, or resources.

| Rating | Schedule Impact | Quality Impact | Resource Impact |
|--------|----------------|----------------|-----------------|
| **High** | > 2 weeks delay | Critical quality issues, release blocker | > 25% resource loss or addition needed |
| **Medium** | 3 days - 2 weeks delay | Moderate quality issues, workarounds available | 10-25% resource impact |
| **Low** | < 3 days delay | Minor quality issues, minimal impact | < 10% resource impact |

**Note:** Rate based on the highest impact category. A risk with high schedule impact but low quality impact is still "High Impact."

### Risk Score Calculation

**Formula:** Risk Score = Probability Weight × Impact Weight

**Weight Values:**
- High = 3
- Medium = 2  
- Low = 1

**Risk Score Interpretation:**

| Risk Score | Priority | Action Required |
|------------|----------|-----------------|
| **9 (High × High)** | Critical | Immediate mitigation required, escalate to management |
| **6 (High × Medium or Medium × High)** | High | Develop detailed mitigation plan, monitor closely |
| **4 (Medium × Medium or High × Low)** | Medium | Plan mitigation, review regularly |
| **2-3 (Low/Medium × Low)** | Low | Monitor, document contingency |
| **1 (Low × Low)** | Very Low | Accept risk, minimal monitoring |

---

## Risk Register

**Purpose:** Complete list of all identified risks with assessment and mitigation details.

### Risk Entry Template

For each risk, complete all fields below. Add one section per risk.

---

#### Risk #[1]: [Risk Title]

**Risk Description:**
**What to include:** Clear, specific description of what could go wrong.

*Example:* "Key test engineer with domain expertise may leave the project mid-cycle due to planned resignation, creating knowledge gap and potential delays."

[Detailed description of the risk]

**Risk Category:**
**Selection Guide:** Choose primary category that best fits the risk.

- [ ] Technical - Technology, tools, architecture, complexity
- [ ] Resource - People availability, skills, turnover
- [ ] Schedule - Timeline, dependencies, deadlines
- [ ] Requirements - Unclear, changing, or missing requirements
- [ ] Environment - Test environment availability, stability, configuration
- [ ] External - Third-party dependencies, vendor issues, regulatory
- [ ] Organizational - Process, communication, decision-making
- [ ] Quality - Defect rates, test coverage, code quality

**Probability:** [High / Medium / Low]

**Impact:** [High / Medium / Low]

**Risk Score:** [Calculate: Probability Weight × Impact Weight]

*Example: High (3) × Medium (2) = 6 (High Priority)*

**Impact Details:**
**What to include:** Specific consequences if this risk occurs.

*Example:*
- Schedule: 2-3 week delay in test execution
- Quality: 30% reduction in test coverage for complex features
- Resources: Need to hire contractor at additional cost
- Business: Potential delay in release affecting market window

- Schedule Impact: [Specific timeline impact]
- Quality Impact: [Specific quality consequences]
- Resource Impact: [Specific resource needs or losses]
- Business Impact: [Business consequences]

**Triggers/Warning Signs:**
**What to include:** Early indicators that this risk is materializing.

*Example:*
- Test engineer submits resignation
- Test engineer mentions job dissatisfaction
- Test engineer reduces documentation of work
- Knowledge transfer sessions stop

[List observable signs that indicate risk is occurring]
1. [Trigger 1]
2. [Trigger 2]
3. [Trigger 3]

**Mitigation Strategy:**
**What to include:** Specific actions to prevent the risk or reduce its probability/impact.

**Prevention Actions** (reduce probability):
*Example:*
- Conduct knowledge transfer sessions weekly
- Document all critical test scenarios and domain knowledge
- Cross-train two additional team members on complex features
- Improve retention through recognition and engagement

[Actions to prevent risk from occurring]
1. [Prevention action 1]
2. [Prevention action 2]

**Mitigation Actions** (reduce impact if risk occurs):
*Example:*
- Maintain documentation of all test cases and procedures
- Identify backup resources (contractor list with required skills)
- Create contingency schedule with extended timelines
- Prioritize testing to ensure critical features are covered first

[Actions to minimize impact if risk occurs]
1. [Mitigation action 1]
2. [Mitigation action 2]

**Contingency Plan:**
**What to include:** Detailed plan to execute if risk materializes.

*Example:* "If test engineer leaves: (1) Immediately engage contractor from pre-approved list within 3 days, (2) Assign backup team member as interim lead, (3) Extend test schedule by 2 weeks, (4) Prioritize critical path testing, (5) Delay low-priority test scenarios"

[Detailed plan to execute if risk occurs]

**Risk Owner:** [Name]
**Responsibilities:** Monitor triggers, implement mitigation, escalate if needed

**Target Closure Date:** [Date or Milestone]
**When to close:** When probability is reduced to Low or risk is no longer relevant

**Status:** [Open / In Progress / Mitigated / Closed / Occurred]

**Status Definitions:**
- **Open:** Identified but mitigation not yet started
- **In Progress:** Actively implementing mitigation strategies
- **Mitigated:** Mitigation complete, risk reduced to acceptable level
- **Closed:** Risk no longer relevant or probability reduced to very low
- **Occurred:** Risk materialized, executing contingency plan

**Current Status Notes:**
[Update as status changes - track mitigation progress, trigger observations, status changes]

**Date Last Reviewed:** [Date]

---

### Additional Risk Template

Copy the above template for each additional risk identified. Number risks sequentially (Risk #1, Risk #2, etc.).

---

## Risk Summary Dashboard

**Purpose:** Quick reference of all risks by priority for stakeholder review.

### Critical Priority Risks (Score 9)

| Risk ID | Risk Title | Probability | Impact | Score | Owner | Status |
|---------|------------|-------------|--------|-------|-------|--------|
| [#] | [Title] | High | High | 9 | [Name] | [Status] |

### High Priority Risks (Score 6)

| Risk ID | Risk Title | Probability | Impact | Score | Owner | Status |
|---------|------------|-------------|--------|-------|-------|--------|
| [#] | [Title] | [H/M] | [H/M] | 6 | [Name] | [Status] |

### Medium Priority Risks (Score 3-4)

| Risk ID | Risk Title | Probability | Impact | Score | Owner | Status |
|---------|------------|-------------|--------|-------|-------|--------|
| [#] | [Title] | [M/L] | [M/L] | 3-4 | [Name] | [Status] |

### Low Priority Risks (Score 1-2)

| Risk ID | Risk Title | Probability | Impact | Score | Owner | Status |
|---------|------------|-------------|--------|-------|-------|--------|
| [#] | [Title] | Low | Low | 1-2 | [Name] | [Status] |

---

## Risk Trends and Analysis

**Purpose:** Tracks how risk exposure changes over time.

### Risk Trend Analysis

**Track over time:**
- Total number of risks identified
- Number of risks by priority (Critical/High/Medium/Low)
- Number of risks closed or mitigated
- Number of new risks identified
- Number of risks that occurred

**Period:** [Week/Sprint/Month]

| Period | Total Risks | Critical | High | Medium | Low | Closed | New | Occurred |
|--------|-------------|----------|------|--------|-----|--------|-----|----------|
| [Date] | [#] | [#] | [#] | [#] | [#] | [#] | [#] | [#] |

**Trend Interpretation:**
- Increasing risk count may indicate project complexity or issues
- Decreasing high-priority risks shows effective mitigation
- Many occurred risks suggests inadequate mitigation or unrealistic assessment

### Lessons Learned from Occurred Risks

**Purpose:** Captures insights when risks materialize to improve future risk management.

| Risk ID | What Happened | Impact | What Worked | What Didn't Work | Prevention for Future |
|---------|---------------|--------|-------------|------------------|----------------------|
| [#] | [Description] | [Actual impact] | [Effective actions] | [Ineffective actions] | [How to prevent next time] |

---

## Common Testing Risks Reference

**Purpose:** Examples of typical risks to consider during risk identification.

### Technical Risks
- Complex technology or architecture requiring specialized skills
- Integration challenges with third-party systems
- Legacy system dependencies with limited documentation
- Performance issues under load not discovered until late testing
- Insufficient test automation coverage
- Technical debt impacting testability

### Resource Risks
- Key personnel unavailability or departure
- Insufficient test team size or skills
- Lack of domain knowledge on test team
- Competing priorities reducing test team availability
- Training needs not addressed
- Contractor dependencies

### Schedule Risks
- Compressed testing timeline
- Late delivery of test environment
- Development delays pushing testing schedule
- Insufficient time for regression testing
- Dependencies on external teams or vendors
- Holiday or vacation impacts on availability

### Requirements Risks
- Unclear or ambiguous requirements
- Frequent requirement changes during testing
- Missing acceptance criteria
- Incomplete or outdated requirements documentation
- Requirements not testable as written
- Conflicting requirements from different stakeholders

### Environment Risks
- Test environment instability or frequent downtime
- Environment not matching production configuration
- Insufficient test environments (conflicts between teams)
- Environment setup delays
- Data management issues (test data availability, privacy)
- Infrastructure dependencies (network, database, services)

### External Risks
- Third-party API unavailability or changes
- Vendor delays in providing necessary components
- Regulatory or compliance requirement changes
- External security audits required
- Client unavailability for UAT or feedback
- Production environment access restrictions

### Quality Risks
- Higher than expected defect rates
- Critical defects discovered late in cycle
- Defect fix rate slower than discovery rate
- High defect reopen rate indicating fix quality issues
- Insufficient code review or unit testing by development
- Poor code quality or maintainability

---

## Best Practices for Risk Assessment

### Identifying Risks

**Techniques:**
- **Brainstorming:** Team sessions to identify risks collaboratively
- **Historical Analysis:** Review past projects for recurring risks
- **Checklist:** Use common risks reference as starting point
- **Expert Judgment:** Consult experienced team members
- **SWOT Analysis:** Identify threats from weakness and external factors
- **Assumption Analysis:** Question project assumptions for hidden risks

**Do:**
- ✅ Involve entire team in risk identification
- ✅ Consider risks across all categories (technical, resource, schedule, etc.)
- ✅ Be specific about what could go wrong
- ✅ Document even low-probability risks
- ✅ Look for patterns from past projects
- ✅ Review risks at regular intervals

**Don't:**
- ❌ Rely on single person's perspective
- ❌ Use vague descriptions like "things might go wrong"
- ❌ Dismiss risks because they seem unlikely
- ❌ Forget to update risk register as project progresses
- ❌ Ignore "soft" risks like communication or morale issues

### Assessing Risks

**Be Objective:**
- Base probability on evidence, not gut feel
- Use historical data when available
- Consider multiple factors (schedule, quality, resources)
- Get input from subject matter experts
- Review assessments with stakeholders

**Avoid Common Biases:**
- **Optimism Bias:** Don't underestimate probability or impact
- **Anchoring:** Don't over-rely on first assessment
- **Groupthink:** Encourage dissenting views
- **Recency Bias:** Don't over-weight recent events

### Managing Risks

**Prioritization:**
- Focus mitigation efforts on high-risk score items first
- Don't ignore medium risks - they can escalate
- Review priorities regularly as risks change
- Balance risk reduction with resource constraints

**Mitigation Strategies:**
1. **Avoid:** Change plans to eliminate the risk (e.g., remove risky feature)
2. **Reduce:** Take actions to lower probability or impact
3. **Transfer:** Shift risk to third party (e.g., insurance, vendor warranty)
4. **Accept:** Acknowledge and monitor risk, prepare contingency

**Monitoring:**
- Assign clear ownership for each risk
- Set regular review schedule (weekly, sprint, monthly)
- Watch for trigger indicators
- Update status promptly when risks change
- Escalate critical risks to management immediately

### Communication

**Regular Reporting:**
- Include risk summary in status reports
- Highlight new or escalating risks
- Report on mitigation progress
- Celebrate risks successfully mitigated or closed

**Stakeholder Engagement:**
- Present risk assessment to stakeholders for buy-in
- Seek input on mitigation strategies
- Escalate high-impact risks requiring management decisions
- Keep stakeholders informed of risk status changes

---

## Related Documentation

### Phase Documentation
- [Phase 1: Test Planning](../phases/01-test-planning.md) - Incorporate risk assessment into test planning

### Related Templates
- [Test Plan Template](test-plan-template.md) - Reference risks in the overall test plan

### Methodology Guides
- [Methodology Comparison](../methodologies/comparison.md) - Risk considerations by methodology

---

**End of Risk Assessment Template**
