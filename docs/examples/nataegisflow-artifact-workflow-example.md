# NATAegisFlow Artifact Workflow Example

This worked example shows how to complete the
[NATAegisFlow Artifact Workflow Checklist Template](../test-templates/nataegisflow-artifact-workflow-template.md)
for an ETL patch that changes customer risk segmentation logic.

## Artifact and Story Details

| Field | Value |
|-------|-------|
| Artifact ID / Name | ETL-RISK-SEG-042 / Customer Risk Segment Mapping |
| Related Story / Requirement | US-RISK-218: Update premium customer risk segment calculation |
| Artifact Type | ETL mapping patch and semantic validation report |
| NATAegisFlow Run ID | NAF-2026-07-23-018 |
| Owner | Data Engineering Lead |
| Reviewer | QA Semantic Reviewer |
| Approver | Risk Data Product Owner |
| Target Release / Sprint | Sprint 24.7 |

## Completed Acceptance Criteria

- [x] Artifact scope, source inputs, target outputs, and affected consumers are identified
- [x] Semantic validation checkpoints are defined for glossary terms, lineage, transformation intent, and rule outcomes
- [x] NATAegisFlow findings are reviewed and assigned a disposition: resolved, accepted, deferred, or false positive
- [x] Critical and high semantic findings are resolved or have documented risk acceptance
- [x] Patch validation is complete for all changed mappings, rules, evidence files, and downstream references
- [x] Required evidence is attached and accessible from the story or artifact record

## Semantic Validation Checkpoints

| Checkpoint | Expected Evidence | Status | Notes |
|------------|-------------------|--------|-------|
| Business meaning preserved | NATAegisFlow semantic comparison, reviewer notes | Pass | Premium customer definition matches approved glossary update BG-117. |
| Lineage and source-to-target mapping verified | Lineage export, mapping spec, data contract reference | Pass | Source fields `customer_value_score` and `tenure_months` map to approved target fields. |
| Transformation rules match approved intent | Rule evaluation output, sample validation, business approval | Pass | Sample replay matched expected risk bands for 250 representative records. |
| Findings dispositioned | Findings register with owner, severity, disposition, and rationale | Pass | One medium finding resolved by updating the null-handling rule. |
| Residual risk assessed | Risk register entry or approval comment | Pass | No critical or high residual semantic risk remains. |

## Policy Gate and Approval Workflow

- [x] Policy gate criteria are documented for this artifact
- [x] Required reviewers have completed semantic validation review
- [x] Required approver has approved release, conditional release, or rework
- [x] Exceptions include approver, rationale, compensating controls, and follow-up date
- [x] Approval record links to NATAegisFlow run ID, artifact version, and evidence location

| Gate | Required Role | Decision | Date | Evidence / Approval Link |
|------|---------------|----------|------|--------------------------|
| Semantic Review | QA Semantic Reviewer | Approved | 2026-07-23 | Story attachment: `semantic-review-NAF-2026-07-23-018.md` |
| Policy Gate | Risk Data Product Owner | Approved | 2026-07-23 | Story approval comment: `POLICY-GATE-RISK-218` |
| Release / Handoff | Data Engineering Lead | Complete | 2026-07-23 | Release checklist: `REL-24.7-risk-segmentation` |

## Evidence Package

- [x] Evidence attached
- [x] NATAegisFlow output files or report links attached
- [x] Artifact version, patch ID, and source data versions recorded
- [x] Reviewer notes and finding dispositions attached
- [x] Approval record attached
- [x] Evidence location meets access control and retention expectations

**Evidence attached:**
- `NAF-2026-07-23-018-summary.json`
- `risk-segment-lineage-export.csv`
- `US-RISK-218-patch-validation.md`
- `POLICY-GATE-RISK-218-approval.txt`

## Patch Validation

- [x] Patch validation complete
- [x] Changed artifacts are compared against the approved baseline
- [x] Regression or replay validation confirms no unintended semantic drift
- [x] Downstream consumers, reports, or operational handoffs are updated if affected
- [x] Follow-up backlog items are created for accepted or deferred findings

**Patch validation result:** Complete. Replay validation confirmed the patch only changes the approved premium customer
segment boundary, and no downstream report columns changed.
