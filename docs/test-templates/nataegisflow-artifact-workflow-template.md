# NATAegisFlow Artifact Workflow Checklist Template

**Version:** 1.0  
**Purpose:** This checklist helps teams validate NATAegisFlow-related artifacts before acceptance, release, or governance review.  
**When to Use:** Use for user stories, patches, or controlled artifact changes that rely on NATAegisFlow semantic validation evidence.

---

## Artifact and Story Details

| Field | Value |
|-------|-------|
| Artifact ID / Name | [Artifact identifier and name] |
| Related Story / Requirement | [Story, requirement, or change ID] |
| Artifact Type | [ETL mapping, rule set, validation output, patch, report, other] |
| NATAegisFlow Run ID | [Run identifier or link] |
| Owner | [Artifact owner] |
| Reviewer | [Semantic reviewer] |
| Approver | [Policy gate approver] |
| Target Release / Sprint | [Release, sprint, or gate] |

## Acceptance Criteria

- [ ] Artifact scope, source inputs, target outputs, and affected consumers are identified
- [ ] Semantic validation checkpoints are defined for glossary terms, lineage, transformation intent, and rule outcomes
- [ ] NATAegisFlow findings are reviewed and assigned a disposition: resolved, accepted, deferred, or false positive
- [ ] Critical and high semantic findings are resolved or have documented risk acceptance
- [ ] Patch validation is complete for all changed mappings, rules, evidence files, and downstream references
- [ ] Required evidence is attached and accessible from the story or artifact record

## Semantic Validation Checkpoints

| Checkpoint | Expected Evidence | Status | Notes |
|------------|-------------------|--------|-------|
| Business meaning preserved | NATAegisFlow semantic comparison, reviewer notes | [Pass/Fail/Blocked] | [Notes] |
| Lineage and source-to-target mapping verified | Lineage export, mapping spec, data contract reference | [Pass/Fail/Blocked] | [Notes] |
| Transformation rules match approved intent | Rule evaluation output, sample validation, business approval | [Pass/Fail/Blocked] | [Notes] |
| Findings dispositioned | Findings register with owner, severity, disposition, and rationale | [Pass/Fail/Blocked] | [Notes] |
| Residual risk assessed | Risk register entry or approval comment | [Pass/Fail/Blocked] | [Notes] |

## Policy Gate and Approval Workflow

- [ ] Policy gate criteria are documented for this artifact
- [ ] Required reviewers have completed semantic validation review
- [ ] Required approver has approved release, conditional release, or rework
- [ ] Exceptions include approver, rationale, compensating controls, and follow-up date
- [ ] Approval record links to NATAegisFlow run ID, artifact version, and evidence location

| Gate | Required Role | Decision | Date | Evidence / Approval Link |
|------|---------------|----------|------|--------------------------|
| Semantic Review | [Reviewer] | [Approved/Changes Required] | [Date] | [Link] |
| Policy Gate | [Approver] | [Approved/Conditional/Rejected] | [Date] | [Link] |
| Release / Handoff | [Owner] | [Complete/Blocked] | [Date] | [Link] |

## Evidence Package

- [ ] Evidence attached
- [ ] NATAegisFlow output files or report links attached
- [ ] Artifact version, patch ID, and source data versions recorded
- [ ] Reviewer notes and finding dispositions attached
- [ ] Approval record attached
- [ ] Evidence location meets access control and retention expectations

## Patch Validation

- [ ] Patch validation complete
- [ ] Changed artifacts are compared against the approved baseline
- [ ] Regression or replay validation confirms no unintended semantic drift
- [ ] Downstream consumers, reports, or operational handoffs are updated if affected
- [ ] Follow-up backlog items are created for accepted or deferred findings

## Related Documentation

- [Phase 7: ETL Semantic Validation](../phases/07-etl-semantic-validation.md)
- [Test Case Template](test-case-template.md)
- [Traceability Matrix Template](traceability-matrix-template.md)
- [NATAegisFlow Artifact Workflow Example](../examples/nataegisflow-artifact-workflow-example.md)

---

**End of NATAegisFlow Artifact Workflow Checklist Template**
