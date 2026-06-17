# Quality KPI Dashboard (v1)

The Quality KPI Dashboard adds a project-wide trend view at `/quality-dashboard` so teams can inspect the data behind release readiness decisions.

## Charts

### Defect Trend

- **Visualization:** stacked daily area chart by severity (`critical`, `high`, `medium`, `low`)
- **Data source:** failed `external_case_results` records in the selected 7/30/90 day window
- **Severity mapping:** derived from the linked `test_cases.priority` field, with linked requirement priority used as a fallback
- **How to read it:** rising totals or repeated critical/high spikes usually point to unstable areas that need focused remediation

### Pass Rate Over Time

- **Visualization:** daily line chart for `pass_rate_pct` with a faint execution-volume area
- **Data source:** all `external_case_results` outcomes in the selected window
- **How to read it:** use the pass-rate line alongside execution volume — a perfect pass rate with almost no executions is weaker evidence than a high pass rate on broad coverage

### Defects by Module

- **Visualization:** horizontal stacked bar chart for the top modules with the most failed executions
- **Data source:** failed `external_case_results`, grouped by `test_cases.module` first, then linked requirement module, tag, or external-id fallback
- **How to read it:** this highlights where failures concentrate so investigation and regression work can be prioritized by subsystem

### Automation Coverage

- **Visualization:** donut chart of `automated`, `manual`, and `in_progress`
- **Data source:** `test_cases.automation_status`
- **How to read it:** higher automated coverage means more of the suite is repeatable and CI-friendly, while a large manual or in-progress slice indicates remaining execution risk

## Summary tiles

The tile row surfaces:

- Defect Removal Efficiency
- MTTR
- Escape Rate
- Open Critical Defects
- Total Defects (30d)
- % Automation Coverage

When a metric cannot be derived from the current schema, the dashboard shows `—` and a short reason instead of failing.

## Null and synthetic states

- **Synthetic trend data** means BGSTM had to return zero-filled date buckets because there were no external execution results yet.
- **Null summary metrics** indicate the calculation needs data the current schema does not store yet (for example, production defect records or defect resolution timestamps).
- **Empty module charts** usually mean no failed executions were recorded in the selected window.

## See also

- [Release Readiness Dashboard](release-readiness-dashboard.md)
- [Phase 5: Test Results Analysis](../phases/05-test-results-analysis.md)
- [Phase 6: Test Results Reporting](../phases/06-test-results-reporting.md)
