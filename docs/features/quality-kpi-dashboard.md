# Quality KPI Dashboard

The Quality KPI Dashboard is part of the **optional BGSTM reference application**. It provides a project-wide evidence view at `/quality-dashboard` so teams can inspect trends, concentrations, recovery patterns, coverage, and supporting data behind release-readiness decisions.

The dashboard does not redefine the BGSTM methodology. It is one software implementation of selected Phase 5 analysis and Phase 6 reporting practices within BGSTM's six-phase lifecycle.

## Time-window semantics

The dashboard supports **7-, 30-, and 90-day windows**. The selected window drives the execution-based trend, failure, recurrence, recovery, and release-readiness evidence displayed by the reference application.

The selected window is represented in the page URL so a view can be shared or reloaded. The reference application also persists the user's saved/default dashboard view locally. When both exist, explicit URL state takes precedence over the saved local preference.

## Core dashboard evidence

### Failed executions over time

- **Visualization:** daily stacked area chart by severity (`critical`, `high`, `medium`, `low`)
- **Evidence source:** failed `external_case_results` records in the selected window
- **Severity mapping:** derived from linked test-case priority, with linked requirement priority used as a fallback
- **Interpretation:** rising totals or repeated critical/high spikes identify periods and areas that warrant investigation

These values are **failed executions**, not necessarily unique defects. Multiple failing tests can be caused by one underlying defect, and one defect can affect multiple executions.

### Pass rate over time

- **Visualization:** daily line chart for pass rate with execution volume context
- **Evidence source:** execution outcomes in the selected window
- **Interpretation:** pass rate should be read together with execution volume and coverage; a high pass rate on very little evidence is weaker than a comparable rate across broad, relevant coverage

### Failures by module

- **Visualization:** horizontal stacked bars for modules with the most failed executions
- **Evidence source:** failed execution records grouped by module context
- **Interpretation:** highlights where failures are concentrated so investigation and regression effort can be prioritized

This view answers **where failures occur**. It is distinct from the recurring-failure Pareto analysis below, which answers **which stable test identities fail repeatedly**.

### Automation coverage

- **Visualization:** distribution of `automated`, `manual`, and `in_progress` test cases
- **Evidence source:** `test_cases.automation_status`
- **Interpretation:** describes the current execution-mode mix; it should not be treated as a universal quality target or release gate

BGSTM does not prescribe a fixed automation percentage. Appropriate automation depth depends on risk, economics, system characteristics, and the type of evidence required.

## Recurring-failure Pareto

The dashboard includes a **Recurring Defects Pareto** panel in the reference application. Despite the historical UI label, the underlying evidence is based on recurring failed test executions rather than confirmed unique defect records.

A recurring entry represents a stable test identity with **two or more failed executions in the selected window**. The bars show recurring failure counts, and the cumulative line shows how much of the recurring-failure population is explained by the ranked entries.

The panel supports prioritization by showing which tests or workflows account for the greatest repeated failure burden. It also links to the latest failing execution evidence for investigation.

## Coverage vs. failure density

The dashboard includes a module-level **coverage-vs-failure-density** scatter view.

- **X-axis:** requirement traceability coverage percentage
- **Y-axis:** failed executions divided by total executions for the module
- **Supporting evidence:** raw failure and execution counts remain visible alongside percentages
- **Population:** modules with at least one requirement

Median guide lines divide the chart into relative quadrants. Modules with comparatively lower traceability coverage and higher failure density deserve attention, but the quadrants are **diagnostic signals, not release gates**.

A module with requirements but no execution evidence is represented as having zero executions and zero calculated failure density; that does not imply proven quality. It indicates lack of execution evidence and should be interpreted accordingly.

## Execution Mean Time to Recovery

The dashboard reports **execution Mean Time to Recovery (time-to-green)** rather than true defect MTTR.

For a stable test identity, a recovery episode begins with the first failed execution and ends with the first subsequent passing execution. Repeated failures do not reset the episode. Open episodes are counted as unresolved but are excluded from the mean until a passing execution closes them.

The recovery view can be grouped overall, by module, or by severity.

This metric describes **execution recovery evidence**. It must not be interpreted as the time required to repair a defect unless the underlying system separately records a real defect lifecycle with defined open and accepted-resolution timestamps.

## Summary metrics and unavailable defect metrics

The reference application can surface decision-relevant summary evidence such as:

- execution volume and pass rate
- failed executions
- current open critical failure evidence
- automation coverage
- execution recovery/time-to-green
- module failure concentrations

Some traditional quality metrics require data the reference application does not currently possess.

### Defect Removal Efficiency and Escape Rate

DRE, escape rate, and similar post-release measures require a trustworthy source of production/post-release defects plus a defined attribution window. If that source does not exist, the application must not interpret missing data as zero escaped defects.

### True defect MTTR

True defect mean time to repair/resolution requires a defect lifecycle with meaningful open/resolved timestamps and agreed resolution semantics. Execution failure and later pass records alone do not provide that lifecycle.

Where the required source data is unavailable, the dashboard should show the metric as unavailable or unsupported rather than manufacture a value.

## Shareable and saved views

The selected dashboard window is synchronized to the URL, making the current view reloadable and shareable. The reference application also stores a preferred/default view locally for convenience.

This is presentation state only; sharing a dashboard URL does not change project data or create a separate BGSTM artifact.

## Release-readiness export integration

When a release-readiness export is initiated from the Quality KPI Dashboard, the selected 7/30/90-day window is passed into the release-readiness export.

The formal export intentionally includes a bounded evidence set rather than every diagnostic visualization. Current KPI evidence includes execution volume/pass rate, failed executions, open critical failure evidence, automation coverage, execution recovery/time-to-green, and leading failure concentrations.

Recurring Pareto, scatter diagnostics, and other exploratory views remain dashboard analysis aids rather than automatically becoming formal release-report content.

## Scheduled KPI digest foundation

The reference application includes a **scheduled in-app KPI digest foundation**. A user can configure the digest cadence as off, daily, or weekly for the supported in-app channel.

The dispatcher is designed as a one-shot process that can be invoked by an external scheduler. This avoids coupling scheduling semantics to a particular web-server process topology.

Email and Slack delivery are not part of the current implementation. Outbound providers should be treated as a separate integration concern with explicit delivery, retry, idempotency, and operational behavior.

## Null, empty, and synthetic states

- **Synthetic/zero-filled trend buckets** preserve a continuous time axis when no execution result exists for a date.
- **Unavailable metrics** mean the required source data or lifecycle semantics are not present; unavailable is not equivalent to zero.
- **Empty module or recurring-failure views** mean no qualifying execution evidence exists in the selected window.
- **No-execution modules** in the coverage-vs-failure-density view indicate missing execution evidence, not demonstrated absence of risk.

## Interpreting the dashboard within BGSTM

Use the dashboard as supporting evidence for Phase 5 analysis and Phase 6 reporting. The methodology still requires human interpretation of scope, risk, evidence quality, known limitations, and residual risk.

No single percentage, chart quadrant, failure count, or automation ratio should be treated as a universal release criterion unless the project established that criterion during planning.

## See also

- [Phase 5: Test Results Analysis](../phases/05-test-results-analysis.md)
- [Phase 6: Test Results Reporting](../phases/06-test-results-reporting.md)
- [Release Readiness Dashboard](release-readiness-dashboard.md)
- [Minimum Viable BGSTM Adoption](../minimum-viable-adoption.md)
