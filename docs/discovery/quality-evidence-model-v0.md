# BGSTM Quality Evidence Model v0 — Discovery Specification

**Status:** Discovery / validation only  
**Date:** 2026-09-10  
**Implementation status:** Not approved for production implementation  
**Canonical methodology:** BGSTM continues to contain exactly six phases.

## 1. Purpose

This document defines the smallest credible experiment for testing whether BGSTM can provide useful quality intelligence above heterogeneous software-delivery and testing tools.

It is intentionally a discovery specification, not a production architecture. Its purpose is to make the opportunity falsifiable before substantial product engineering begins.

The working thesis is:

> Keep the tools teams already use. BGSTM determines whether the quality evidence across them is complete, current, connected, and sufficient to support a quality or release claim.

A shorter expression of the hypothesis is:

> Existing tools tell teams what happened. BGSTM may be able to determine whether there is enough trustworthy evidence to believe the resulting quality claim.

## 2. Market constraint

Cross-tool test aggregation, traceability, dashboards, integrated test management, and graph-like relationships among requirements, tests, executions, defects, and releases already exist in commercial and open-source products.

Therefore this experiment must **not** treat any of the following as sufficient differentiation:

- collecting results from multiple tools;
- displaying requirements, tests, runs, and defects in one interface;
- representing quality artifacts as a graph;
- generating an AI summary of test results;
- duplicating functionality already available in an integrated ALM or test-management platform.

The hypothesis under test is narrower: a portable BGSTM semantic operating model may add value by representing both **observed evidence** and **expected quality obligations**, then evaluating whether the observed evidence sufficiently satisfies those obligations.

## 3. Architectural principle

> **BGSTM does not need to own every artifact. It needs to understand every artifact.**

External tools remain authoritative systems of record. BGSTM should preserve source identity and provenance rather than silently replacing source artifacts with BGSTM-owned copies.

## 4. Semantic model

The discovery model has three conceptual layers.

### 4.1 Quality Intent

Quality Intent describes why testing or validation is required.

Minimum entity types:

- Requirement
- Change
- Risk
- Test Objective
- Quality Obligation
- Acceptance / Exit Criterion

### 4.2 Quality Activity

Quality Activity describes what was designed, prepared, or performed.

Minimum entity types:

- Test Strategy / Plan
- Test Case / Scenario
- Test Data
- Environment Definition
- Environment Instance
- Build
- Deployment
- Execution / Test Run
- Analysis Activity
- Failure Investigation

### 4.3 Evidence and Decision

Evidence and Decision describes what was observed and what conclusions or decisions were made from those observations.

Minimum entity types:

- Evidence Artifact
- Observation
- Result
- Failure
- Defect
- Analysis Finding
- Risk Assessment
- Coverage Finding
- Waiver / Exception
- Approval
- Release Finding
- Release Decision
- Report

## 5. Quality Obligation

`Quality Obligation` is the key discovery entity connecting expected evidence to observed evidence.

A Quality Obligation describes evidence that should exist before a quality claim is considered supported.

Example:

```text
Requirement R-17
  INTRODUCES -> Risk RK-4

Risk RK-4
  REQUIRES -> Quality Obligation QO-23

QO-23:
  Authentication must be tested against supported browsers
  using production-equivalent identity configuration.
```

This distinction allows BGSTM to evaluate:

```text
EXPECTED EVIDENCE
        versus
OBSERVED EVIDENCE
```

rather than merely inventorying existing test artifacts.

## 6. Minimum provenance contract

Every normalized artifact must preserve enough provenance to identify its authoritative source and evaluate freshness and applicability.

Minimum fields, where applicable:

```text
canonical_id
artifact_type

source_system
source_tenant
source_project
source_object_type
source_object_id
source_url

created_at
modified_at
observed_at
ingested_at

source_revision
content_hash
connector_version
mapping_version

actor_or_producer
confidence
authoritativeness

valid_from
valid_until
superseded_by
```

The experiment may omit fields that a source cannot provide, but absence must remain explicit rather than fabricated.

## 7. Minimum typed relationships

The experiment should support at least the following semantic relationships:

```text
Requirement IS_AFFECTED_BY Change
Requirement INTRODUCES Risk
Requirement VERIFIED_BY TestObjective

Risk MITIGATED_BY QualityObligation

QualityObligation SATISFIED_BY TestCase
QualityObligation REQUIRES_ENVIRONMENT EnvironmentDefinition

TestCase EXECUTED_AS Execution

Execution RAN_ON Build
Execution USED_ENVIRONMENT EnvironmentInstance
Execution PRODUCED EvidenceArtifact
Execution OBSERVED Result

Result INDICATES Failure
Failure TRACKED_AS Defect

Defect RESOLVED_BY Change
Defect VERIFIED_BY Execution

Execution SUPPORTS AnalysisFinding
AnalysisFinding AFFECTS RiskAssessment
RiskAssessment SUPPORTS ReleaseFinding
ReleaseFinding SUPPORTS ReleaseDecision
ReleaseDecision REPORTED_IN Report
```

The experiment may add relationships when necessary, but additions should be justified by a concrete validation need rather than speculative completeness.

## 8. Relationship to the six BGSTM phases

The evidence model does not add methodology phases and should not reduce the methodology to six database containers.

The six phases define classes of quality questions and evidence obligations:

| BGSTM phase | Semantic question |
| --- | --- |
| 1. Test Planning | What must be proven, why, and at what risk? |
| 2. Test Case Development | What test design is intended to produce that proof? |
| 3. Test Environment Preparation | Under what conditions is the proof valid? |
| 4. Test Execution | What actually happened? |
| 5. Test Results Analysis | What does the observed evidence mean? |
| 6. Test Results Reporting | What claim or decision can responsibly be made from the evidence? |

## 9. Evidence Spine experiment

### 9.1 Toolchain

Use four heterogeneous systems for the first proof:

- **OpenProject** — requirements, work items, and risk/change context;
- **Playwright** — automated test execution and execution evidence;
- **GitHub Actions** — candidate build/commit identity, workflow execution, and persisted artifacts;
- **Bugzilla** — defects and defect lifecycle.

Cucumber, Jira, Jenkins, Azure DevOps, ServiceNow, NAT, and other systems are deliberately excluded from the first experiment. They remain candidates for later proofs if the minimum experiment succeeds.

### 9.2 Dataset scale

Target approximately:

- 8 requirements;
- 5 risks;
- 12 test cases;
- 2 environment definitions/instances;
- 3 test runs;
- 4 defects;
- 1 candidate release.

Exact counts may vary slightly when required to create a coherent test scenario.

### 9.3 Deliberately injected evidence failures

The dataset must contain seven known conditions:

1. **Uncovered risk** — a material risk has no qualifying evidence chain.
2. **Stale execution** — apparent test coverage exists, but the qualifying execution predates a relevant change.
3. **Environment mismatch** — an execution exists but occurred under conditions that do not satisfy the declared environment obligation.
4. **Unverified defect closure** — a defect is closed/fixed but lacks qualifying post-fix verification.
5. **Orphan test** — a test executes successfully but has no meaningful relationship to a requirement, risk, objective, or obligation.
6. **Outdated traceability** — a requirement or related artifact changed after the relationship/evidence on which the quality claim depends.
7. **Contradictory evidence** — two apparently valid observations support conflicting interpretations and require explicit reconciliation rather than silent selection.

The expected answer for each injected condition must be recorded before running the evaluator so the experiment cannot redefine success after seeing results.

## 10. Required evaluator questions

The proof must answer at least these questions from normalized evidence:

1. Which high-risk quality obligations are unsupported?
2. Which requirements appear covered but lack qualifying current execution?
3. Which quality evidence became potentially stale after a specified change?
4. Which fixed/closed defects lack qualifying post-fix verification?
5. Which tests or evidence artifacts are semantically orphaned?
6. Which evidence chains contain contradictory observations?
7. What evidence supports and contradicts a recommendation to release the candidate?

## 11. Output contract

A material finding should be capable of producing:

```text
claim
status
reason
confidence
quality_obligation_ids
evidence_references
source_systems
source_object_ids
source_revisions_or_timestamps
human_review_required
```

A finding must not assert source facts that cannot be traced to observed evidence.

## 12. AI boundary

AI is not required for the initial Evidence Spine proof.

Deterministic semantics should first establish:

- which obligations exist;
- which evidence may satisfy them;
- which required links are missing;
- which evidence is stale;
- which source facts conflict;
- which claims remain unsupported.

If AI is subsequently introduced, it may assist with interpretation, ranking, clustering, semantic matching, explanation, and report generation.

AI must not silently manufacture graph facts or replace source provenance.

A useful design constraint is:

> LLMs may propose interpretations. They do not become authoritative producers of source facts merely by producing plausible text.

## 13. Human-baseline comparison

Technical detection alone is insufficient to establish commercial value.

A competent QA practitioner should receive the same source dataset without the BGSTM evaluator and be asked to assess release readiness and identify evidence gaps.

Measure at minimum:

- time to identify evidence gaps;
- number of injected conditions correctly identified;
- false positives;
- false negatives;
- time to assemble a defensible release-readiness explanation;
- confidence in the resulting decision;
- number of source systems/artifacts manually inspected.

## 14. Success criteria

The experiment is technically successful only if all of the following are true:

1. The four source systems can remain systems of record; the proof does not require moving their primary artifacts into BGSTM.
2. A single normalized evidence spine can represent the relevant lifecycle without adding a seventh BGSTM phase.
3. At least **6 of the 7** deliberately injected evidence failures are detected correctly.
4. The evaluator produces no more than **2 material false-positive findings** in the controlled dataset.
5. Every material finding can identify the source evidence and reasoning that produced it.
6. At least one detected condition requires reasoning beyond a simple missing foreign-key/link check.
7. The result can support a release-readiness explanation without requiring an LLM to invent missing facts.

The commercial hypothesis receives preliminary support only if the BGSTM-assisted assessment also produces a meaningful improvement over the human baseline in either completeness or effort. A suggested initial signal is:

- at least **25% less assessment/reporting time**, **or**
- at least **2 additional material evidence problems detected** without a material increase in false positives.

These thresholds are discovery gates, not product SLAs.

## 15. Failure criteria

The experiment should be considered evidence **against** the product thesis if one or more of the following is observed:

- the normalized model mostly reproduces links already obvious in the source tools;
- detecting the seven conditions requires extensive custom configuration that effectively recreates a test-management system;
- provenance cannot be preserved reliably enough to explain findings;
- most useful findings reduce to dashboard aggregation;
- a competent QA practitioner reaches the same result with comparable effort using existing tools;
- the overlay requires teams to abandon or substantially alter their normal systems-of-record workflows;
- the model becomes useful only after introducing broad speculative AI inference;
- the complexity of maintaining cross-tool identity and freshness exceeds the value of the resulting findings.

A failed experiment is a valid discovery outcome and should stop or materially redirect product development.

## 16. Azure DevOps adversarial proof

If the Evidence Spine experiment succeeds, the next proof should use a capable integrated platform such as Azure DevOps/Test Plans.

The purpose is not to demonstrate that BGSTM can reproduce Azure traceability. The proof succeeds only if BGSTM can detect or explain useful quality conditions that native artifact linkage does not already make sufficiently apparent, for example:

- linked tests that do not satisfy the declared risk obligation;
- environment evidence that is insufficient for the quality claim;
- evidence invalidated by later changes;
- release findings unsupported by current execution evidence;
- policy/obligation conflicts within otherwise valid Azure artifacts.

If BGSTM merely redraws Azure DevOps relationships, this proof should be considered failed.

## 17. Product and repository boundary

The working layered model is:

```text
BGSTM
  public methodology + semantic concepts
        |
        v
Evidence/interchange contracts
        |
   +----+----------------+
   |                     |
   v                     v
External adapters     NAT / NATAegisFlow
observe evidence      generate, validate,
from systems          orchestrate evidence
   |                     |
   +----------+----------+
              v
Potential commercial quality-intelligence/control plane
```

NAT is not the BGSTM database and BGSTM is not the NAT user interface.

NAT may become a powerful producer and consumer of BGSTM-compatible evidence while retaining its independent automation, orchestration, validation, and adaptive-testing responsibilities.

## 18. Public/private discovery boundary

### Suitable for public BGSTM discussion

- the exactly-six-phase methodology;
- practitioner guidance and templates;
- generic traceability and evidence-based testing principles;
- worked examples;
- the principle that source tools may remain systems of record;
- basic, deliberately neutral interoperability contracts after review;
- simple reference integrations where disclosure creates adoption value without exposing proprietary mechanisms.

### Keep private pending deliberate IP and commercial review

Do not publish implementation detail for:

- production canonicalization and cross-tool identity resolution;
- connector mapping/reconciliation algorithms;
- temporal evidence reconciliation;
- evidence-completeness evaluation internals;
- automatic quality-obligation derivation;
- proprietary quality policy packs;
- risk propagation/scoring algorithms;
- change-impact inference;
- conflict-resolution algorithms;
- release-readiness scoring;
- proprietary AI reasoning/orchestration architecture;
- learned organizational quality intelligence, failure corpora, or benchmarks;
- NAT/NATAegisFlow proprietary or potentially patentable mechanisms.

The generic idea of connecting quality artifacts or representing them as a graph should not be treated as a proprietary novelty claim.

## 19. Explicit non-goals for v0

Do not build during this discovery step:

- a commercial dashboard;
- a graph database merely because the model is graph-shaped;
- production-grade connector infrastructure;
- enterprise RBAC/SSO/multi-tenancy;
- a chatbot;
- broad Jira/ServiceNow/Azure/Jenkins connector coverage;
- automated NAT orchestration over the model;
- a proprietary release-readiness score;
- a complete universal ontology for software engineering.

Use the simplest representation capable of testing the hypothesis. JSON documents, fixtures, and deterministic evaluation code are acceptable for the eventual experiment.

## 20. Decision gate

No large BGSTM Quality Intelligence product build should begin from this document alone.

The next implementation authorization should be limited to the Evidence Spine experiment and should occur only after review of:

1. the entity and relationship vocabulary;
2. the seven injected failure definitions;
3. the success/failure thresholds;
4. the public/private boundary;
5. any IP implications discovered before implementation.

The desired outcome is evidence about whether the opportunity deserves further investment—not confirmation of a predetermined product strategy.
