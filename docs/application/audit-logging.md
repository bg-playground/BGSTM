# Audit Logging

BGSTM maintains an immutable audit trail of all write operations performed through the API. This makes it possible to answer "who changed what, and when?" for every resource in the system.

## What Is Logged

Audit log entries are created automatically for:

| Resource | Logged Actions |
|---|---|
| Requirements | `create`, `update`, `delete` |
| Test Cases | `create`, `update`, `delete` |
| Links | `create`, `delete` |
| Suggestions | `review` (accept/reject), `generate` |
| Users | `create`, `update`, `delete` |

## Audit Log Entry Fields

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique entry identifier |
| `user_id` | integer | ID of the user who performed the action |
| `action` | string | Action performed (e.g. `create`, `update`, `delete`) |
| `resource_type` | string | Type of resource (e.g. `requirement`, `test_case`) |
| `resource_id` | integer | ID of the affected resource |
| `details` | object | Additional context (e.g. changed fields, old/new values) |
| `timestamp` | datetime | UTC timestamp of the action |

## Querying the Audit Log

```
GET /api/v1/audit-log
```

!!! note "Admin only"
    This endpoint requires the `admin` role.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | integer | Filter by the user who performed the action |
| `action` | string | Filter by action type (e.g. `create`, `delete`) |
| `resource_type` | string | Filter by resource type (e.g. `requirement`) |
| `start_date` | datetime | Include entries on or after this timestamp (ISO 8601) |
| `end_date` | datetime | Include entries on or before this timestamp (ISO 8601) |
| `skip` | integer | Pagination offset (default `0`) |
| `limit` | integer | Page size (default `50`, max `200`) |

**Example — all deletions in the last 7 days:**

```bash
curl "http://localhost:8000/api/v1/audit-log?action=delete&start_date=2025-01-01T00:00:00Z" \
  -H "Authorization: Bearer <admin-JWT>"
```

**Example — all actions by a specific user:**

```bash
curl "http://localhost:8000/api/v1/audit-log?user_id=5" \
  -H "Authorization: Bearer <admin-JWT>"
```

**Response:**

```json
[
  {
    "id": 101,
    "user_id": 5,
    "action": "delete",
    "resource_type": "requirement",
    "resource_id": 12,
    "details": {},
    "timestamp": "2025-06-15T10:32:00Z"
  }
]
```
