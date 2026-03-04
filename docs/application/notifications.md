# Notifications

BGSTM includes an event-driven notification system that automatically alerts users when important events occur in the application.

## Notification Types

| Type | Trigger |
|---|---|
| `suggestions_generated` | AI suggestions were generated for a requirement |
| `suggestion_reviewed` | A suggestion was accepted or rejected |
| `coverage_drop` | Traceability coverage falls below a threshold |
| `requirement_created` | A new requirement was created |
| `test_case_created` | A new test case was created |

Notifications are scoped to the user who triggered the event or, in the case of coverage alerts, broadcast to all `reviewer` and `admin` users.

## API Endpoints

### List Notifications

```
GET /api/v1/notifications
```

Returns the authenticated user's notifications, newest first.

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `unread_only` | boolean | `false` | Return only unread notifications |
| `skip` | integer | `0` | Pagination offset |
| `limit` | integer | `20` | Page size (max 100) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/notifications?unread_only=true&limit=5" \
  -H "Authorization: Bearer <JWT>"
```

---

### Unread Count

```
GET /api/v1/notifications/unread-count
```

Returns the number of unread notifications for the current user. Used to display the notification badge in the frontend.

**Response:**

```json
{ "count": 3 }
```

---

### Mark as Read

```
PATCH /api/v1/notifications/{id}/read
```

Marks a single notification as read.

**Example:**

```bash
curl -X PATCH http://localhost:8000/api/v1/notifications/42/read \
  -H "Authorization: Bearer <JWT>"
```

---

### Mark All as Read

```
POST /api/v1/notifications/mark-all-read
```

Marks all of the current user's notifications as read in one request.

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/notifications/mark-all-read \
  -H "Authorization: Bearer <JWT>"
```

## Frontend Badge

The React frontend polls `GET /api/v1/notifications/unread-count` and displays a badge on the notification icon in the navigation bar. The count updates automatically after actions that generate notifications.
