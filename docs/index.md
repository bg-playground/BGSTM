# BGSTM — Better Global Software Testing Methodology

!!! info "Welcome to BGSTM"
    A practical, methodology-agnostic software testing framework organized around exactly six core phases, adaptable to Agile, Scrum, Waterfall, and hybrid delivery models.

## 🎯 Overview

BGSTM provides a structured approach to software testing through **exactly six core phases**, with practical guidance for adapting testing work to different delivery models without redefining the methodology. It serves first as a testing methodology and knowledge base; the repository's reference application demonstrates how parts of BGSTM can be represented in software.

---

## 🚀 Quick Start

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __New to BGSTM?__

    ---

    Start with the practical getting started guide

    [:octicons-arrow-right-24: Getting Started](GETTING-STARTED.md)

-   :material-book-open-variant:{ .lg .middle } __Explore the Six Phases__

    ---

    Learn the canonical BGSTM testing lifecycle

    [:octicons-arrow-right-24: Testing Phases](phases/index.md)

-   :material-pencil:{ .lg .middle } __Use Templates__

    ---

    Adapt ready-to-use testing templates to your project

    [:octicons-arrow-right-24: Templates](test-templates/index.md)

-   :material-lightbulb:{ .lg .middle } __Adapt to Your Delivery Model__

    ---

    Apply BGSTM across Agile, Scrum, Waterfall, or hybrid delivery

    [:octicons-arrow-right-24: Methodologies](methodologies/index.md)

</div>

---

## 🔄 The Six BGSTM Testing Phases

BGSTM has exactly six core testing phases:

1. **[Test Planning](phases/01-test-planning.md)** - Define scope, strategy, resources, and timelines
2. **[Test Case Development](phases/02-test-case-development.md)** - Design and document test scenarios and cases
3. **[Test Environment Preparation](phases/03-test-environment-preparation.md)** - Set up infrastructure and tools
4. **[Test Execution](phases/04-test-execution.md)** - Execute tests and manage defects
5. **[Test Results Analysis](phases/05-test-results-analysis.md)** - Analyze outcomes and identify patterns
6. **[Test Results Reporting](phases/06-test-results-reporting.md)** - Communicate findings to stakeholders

Specialized domains apply these six phases; they do not add methodology phases.

---

## 🧭 ETL Semantic Validation Applied Example

ETL semantic validation is an application of the six-phase BGSTM methodology, not an additional methodology phase.

- **[ETL Semantic Validation Applied Example](examples/etl-semantic-validation-example.md)** - Shows how the six BGSTM phases can be applied to an ETL semantic-validation initiative using NATAegisFlow evidence
- **[NATAegisFlow Artifact Workflow Checklist Template](test-templates/nataegisflow-artifact-workflow-template.md)** - Story and artifact acceptance checklist with semantic validation, policy gate, approval, evidence, and patch validation checkpoints
- **[NATAegisFlow Artifact Workflow Example](examples/nataegisflow-artifact-workflow-example.md)** - Worked example showing a completed ETL artifact patch validation
- **[AegisFlow BGSTM Adoption Retrospective and Sign-off](examples/nataegisflow-bgstm-pilot-retrospective.md)** - Adoption record with process changes, rollout readiness, and process owner sign-off

---

## 🔧 Delivery-Model Adaptation

BGSTM is methodology-agnostic. Agile, Scrum, Waterfall, and hybrid approaches change how teams implement and pace the work; they do not change BGSTM's six-phase structure.

- **[Agile Testing](methodologies/agile.md)** - Continuous testing with rapid feedback
- **[Scrum Testing](methodologies/scrum.md)** - Sprint-based testing approach
- **[Waterfall Testing](methodologies/waterfall.md)** - Sequential delivery context
- **[Methodology Comparison](methodologies/comparison.md)** - Compare adaptation approaches

---

## ✨ Core Characteristics

<div class="grid cards" markdown>

-   :material-swap-horizontal:{ .lg .middle } __Methodology Agnostic__

    ---

    Adaptable to Agile, Scrum, Waterfall, and hybrid approaches

-   :material-book-check:{ .lg .middle } __Six-Phase Lifecycle__

    ---

    End-to-end testing work from planning through results reporting

-   :material-link-variant:{ .lg .middle } __Traceable__

    ---

    Connect requirements, tests, results, evidence, and decisions

-   :material-file-document:{ .lg .middle } __Practical__

    ---

    Ready-to-use templates and worked examples support adoption

-   :material-alert-decagram:{ .lg .middle } __Risk Aware__

    ---

    Scale testing rigor and effort according to project risk

-   :material-chart-line:{ .lg .middle } __Evidence Based__

    ---

    Use quality signals and test outcomes to support stakeholder decisions

</div>

---

## 💡 Who Should Use BGSTM?

### For Testing Teams
- Implement structured testing processes
- Improve test coverage and quality
- Standardize testing practices
- Connect testing evidence to quality decisions

### For Project Managers
- Plan testing activities and resources
- Track testing progress and metrics
- Manage testing risks
- Support evidence-based release decisions

### For Organizations
- Establish testing standards
- Train testing teams
- Improve testing maturity
- Adapt a common quality lifecycle across delivery models

### For Developers and Tool Builders
- Integrate testing into development workflows
- Automate testing processes where useful
- Build testing dashboards and reports
- Use the reference application as an implementation example without coupling BGSTM to a specific technology stack

---

## 🧪 Reference Application

BGSTM is first and foremost a **testing methodology and knowledge base**. This repository also contains an open-source FastAPI and React reference application demonstrating traceability, dashboards, reporting, notifications, and related testing-management workflows.

The application supports and demonstrates the methodology; it does **not** define BGSTM or add methodology phases.

[:octicons-arrow-right-24: Reference Application Documentation](application/index.md)

---

## 🤝 Contributing

Contributions are welcome for methodology guidance, documentation, examples, templates, application code, and integrations.

[:octicons-arrow-right-24: Contributing Guide](CONTRIBUTING.md)

---

## 📄 License

BGSTM is licensed under the MIT License. See the [license](LICENSE.md) for details.

---

## 📞 Get Involved

- [:fontawesome-brands-github: View on GitHub](https://github.com/bg-playground/BGSTM)
- [:material-bug: Report an Issue](https://github.com/bg-playground/BGSTM/issues)
- [:material-message: Start a Discussion](https://github.com/bg-playground/BGSTM/discussions)
