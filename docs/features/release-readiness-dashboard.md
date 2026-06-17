# Release Readiness Dashboard (v1)

The Release Readiness Dashboard provides a project-wide **Go / Caution / No-Go** view using existing BGSTM traceability data.

## Criteria and thresholds

### Coverage
- **Requirements with at least one linked test case**
  - Pass: `>= 95%`
  - Warn: `80-94%`
  - Fail: `< 80%`
- **Test cases with at least one linked requirement**
  - Pass: `>= 90%`
  - Warn: `70-89%`
  - Fail: `< 70%`

### Quality
- **Pending link suggestions awaiting review**
  - Pass: `0`
  - Warn: `1-10`
  - Fail: `> 10`
- **Test cases with no `last_run_status` (never executed)**
  - Pass: `<= 5%`
  - Warn: `6-20%`
  - Fail: `> 20%`
- **Test cases with `last_run_status == "failed"`**
  - Pass: `0`
  - Warn: `1-3`
  - Fail: `> 3`

### Process
- **All three roles signed off** (`qa_lead`, `product`, `eng_lead`)

If underlying data is empty or unavailable, criteria are marked `na` with value `data not available`.

## Overall status logic

- **Go**: no failing readiness checks and all roles signed off
- **Caution**: no failing checks, but one or more warnings or unsigned roles
- **No-Go**: failing checks present, or insufficient baseline data

## Sign-offs

Sign-offs are persisted in `release_signoffs`.

- Roles: `qa_lead`, `product`, `eng_lead`
- A new sign-off for a role automatically revokes the prior active sign-off for that role
- Active sign-offs can be explicitly revoked

## Exports

The dashboard supports export from the UI:
- Markdown (`.md`)
- PDF (`.pdf`)

## See also

- [Quality KPI Dashboard](quality-kpi-dashboard.md)
