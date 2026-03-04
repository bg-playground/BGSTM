# API Reference

All endpoints are prefixed with `/api/v1` and require a `Authorization: Bearer <JWT>` header unless noted otherwise.

Interactive documentation is available at:

- **Swagger UI** — `http://localhost:8000/docs`
- **ReDoc** — `http://localhost:8000/redoc`

---

## Auth

| Method | Path | Description | Required Role |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | Public |
| `POST` | `/auth/login` | Login and receive a JWT access token | Public |
| `GET` | `/auth/me` | Get the current user's profile | Any authenticated user |

---

## Requirements

| Method | Path | Description | Required Role |
|---|---|---|---|
| `POST` | `/requirements` | Create a requirement | `reviewer` or `admin` |
| `GET` | `/requirements` | List requirements (paginated) | Any authenticated user |
| `GET` | `/requirements/{id}` | Get a requirement by ID | Any authenticated user |
| `PUT` | `/requirements/{id}` | Update a requirement | `reviewer` or `admin` |
| `DELETE` | `/requirements/{id}` | Delete a requirement | `reviewer` or `admin` |

---

## Test Cases

| Method | Path | Description | Required Role |
|---|---|---|---|
| `POST` | `/test-cases` | Create a test case | `reviewer` or `admin` |
| `GET` | `/test-cases` | List test cases (paginated) | Any authenticated user |
| `GET` | `/test-cases/{id}` | Get a test case by ID | Any authenticated user |
| `PUT` | `/test-cases/{id}` | Update a test case | `reviewer` or `admin` |
| `DELETE` | `/test-cases/{id}` | Delete a test case | `reviewer` or `admin` |

---

## Links

| Method | Path | Description | Required Role |
|---|---|---|---|
| `POST` | `/links` | Create a manual requirement-to-test-case link | `reviewer` or `admin` |
| `GET` | `/links` | List all links (paginated) | Any authenticated user |
| `GET` | `/links/{id}` | Get a link by ID | Any authenticated user |
| `GET` | `/requirements/{id}/links` | List all links for a requirement | Any authenticated user |
| `GET` | `/test-cases/{id}/links` | List all links for a test case | Any authenticated user |
| `DELETE` | `/links/{id}` | Delete a link | `reviewer` or `admin` |

---

## Suggestions

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/suggestions` | List all suggestions | Any authenticated user |
| `GET` | `/suggestions/pending` | List pending (unreviewed) suggestions | Any authenticated user |
| `GET` | `/suggestions/{id}` | Get a specific suggestion | Any authenticated user |
| `POST` | `/suggestions/generate` | Trigger AI suggestion generation | `reviewer` or `admin` |
| `POST` | `/suggestions/{id}/review` | Accept or reject a suggestion | `reviewer` or `admin` |
| `POST` | `/suggestions/bulk-review` | Bulk accept or reject suggestions | `reviewer` or `admin` |

---

## Traceability

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/traceability-matrix` | Get traceability matrix with coverage analysis | Any authenticated user |
| `GET` | `/metrics` | Get coverage metrics and statistics | Any authenticated user |
| `GET` | `/traceability-matrix/export/csv` | Export traceability matrix as CSV | Any authenticated user |
| `GET` | `/traceability-matrix/export/pdf` | Export traceability matrix as PDF | Any authenticated user |

---

## Analytics

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/analytics/acceptance-rates` | Suggestion acceptance rates over time | Any authenticated user |
| `GET` | `/analytics/confidence-distribution` | Confidence score distribution | Any authenticated user |
| `GET` | `/analytics/generation-trends` | Suggestion generation trends | Any authenticated user |
| `GET` | `/analytics/metrics-csv` | Export analytics data as CSV | Any authenticated user |

---

## Notifications

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/notifications` | List notifications (supports `unread_only`, pagination) | Any authenticated user |
| `GET` | `/notifications/unread-count` | Get unread notification count | Any authenticated user |
| `PATCH` | `/notifications/{id}/read` | Mark a notification as read | Any authenticated user |
| `POST` | `/notifications/mark-all-read` | Mark all notifications as read | Any authenticated user |

---

## Audit Log

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/audit-log` | List audit log entries (filterable) | `admin` |

---

## Users

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/users` | List all users | `admin` |
| `GET` | `/users/{user_id}` | Get a user by ID | `admin` |
| `PUT` | `/users/{user_id}` | Update a user (role, active status) | `admin` |
| `DELETE` | `/users/{user_id}` | Deactivate a user | `admin` |

---

## Health Check

| Method | Path | Description | Required Role |
|---|---|---|---|
| `GET` | `/health` | Service health status | Public |
