# External Results API — v1 Specification

**Status:** Draft  
**Tracking:** [BGSTM#299](https://github.com/bg-playground/BGSTM/issues/299) (this spec) · [BGSTM#291](https://github.com/bg-playground/BGSTM/issues/291) (parent epic)  
**Pydantic schemas:** [`backend/app/schemas/external_results.py`](../../backend/app/schemas/external_results.py)

---

## a. Overview

The **External Results API** is the ingestion surface that external test runners use to push execution data into BGSTM. The initial target is [Playwright](https://playwright.dev/) (via the `@bgstm/playwright-core` reporter); Pytest and Cypress adapters follow in later milestones.

### Design goals

| Goal | Note |
|---|---|
| **Runner-agnostic** | Any test framework can POST results as long as it speaks JSON over HTTPS. |
| **Lightweight client** | Runners only need an HTTP client; no SDK is required. |
| **Idempotent** | Re-running a suite never creates phantom duplicates. |
| **Incrementally traceable** | Results link to existing BGSTM requirements via `requirement_ids`; unknown tests are auto-registered on demand. |

### Versioning model

All endpoints are under the `/api/v1/` prefix. Within v1, BGSTM commits to backward-compatible additions only (no field removals, no semantic changes to existing fields). A v2 path will be introduced if a breaking change is unavoidable.

### Reference implementation

The canonical reporter is being built in [bgstm-playwright-frameworks#3](https://github.com/bg-playground/bgstm-playwright-frameworks/issues/3). That repository's `@bgstm/playwright-core` package is the primary integration point and serves as the living reference for how a runner consumes this spec.

---

## b. Authentication

### Token shape

Every request to a state-changing endpoint must carry a runner token in the `Authorization` header:

```
Authorization: Bearer bgstm_runner_<opaque>
```

Where `<opaque>` is a cryptographically random, base-62-encoded string (minimum 32 characters). Tokens are:

- **Scoped** — each token declares which scopes it may exercise (see table below).
- **Revocable** — an admin can invalidate a token at any time without rotating other tokens.
- **Attributable** — every API call is logged under the token's identity for audit purposes.
- **Never logged** — tokens must never appear in application logs, error responses, or audit records. Log the token's `id` (UUID) instead.

Token issuance, revocation, and rotation are implemented in [BGSTM#296](https://github.com/bg-playground/BGSTM/issues/296).

### Scopes

| Scope | Grants |
|---|---|
| `external_results:write` | Create/update sessions, case results, and artifacts. |
| `external_results:read` | Read sessions, case results, and artifacts. |

Read-only endpoints also accept a standard user JWT (`Authorization: Bearer <jwt>`) issued by the regular auth flow.

### Error on auth failure

| HTTP status | `code` | Meaning |
|---|---|---|
| `401` | `runner_token.missing` | No `Authorization` header. |
| `401` | `runner_token.invalid` | Token not found or malformed. |
| `401` | `runner_token.expired` | Token has passed its expiry. |
| `403` | `runner_token.scope_denied` | Token lacks required scope. |
| `403` | `runner_token.project_denied` | Token is not authorized for the requested `project_id`. |

---

## c. Endpoints

### 1. Create session

```
POST /api/v1/external-results/session
```

**Auth scope:** `external_results:write`

Opens a new test-run session. Call this once at the beginning of the suite.

#### Request body

```json
{
  "runner": "@bgstm/playwright-core@0.1.0",
  "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "git_sha": "abc123def456",
  "git_branch": "main",
  "ci_url": "https://github.com/org/repo/actions/runs/123",
  "metadata": {
    "os": "ubuntu-22.04",
    "node": "20.11.0"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `runner` | `string` | ✅ | Runner name + version (e.g. `@bgstm/playwright-core@0.1.0`). |
| `project_id` | `UUID` | ✅ | BGSTM project this session belongs to. |
| `git_sha` | `string \| null` | — | Full or short commit SHA under test. |
| `git_branch` | `string \| null` | — | Branch name under test. |
| `ci_url` | `HttpUrl \| null` | — | URL of the CI job that triggered this run. |
| `metadata` | `object` | — | Arbitrary key/value runner metadata. Defaults to `{}`. |

#### Success response — `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "started_at": "2025-01-15T12:00:00Z",
  "finished_at": null,
  "runner": "@bgstm/playwright-core@0.1.0",
  "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "git_sha": "abc123def456",
  "git_branch": "main",
  "ci_url": "https://github.com/org/repo/actions/runs/123",
  "metadata": { "os": "ubuntu-22.04", "node": "20.11.0" }
}
```

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `400` | `session.project_not_found` | `project_id` does not exist. |
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `403` | `runner_token.scope_denied` | Token lacks `external_results:write`. |
| `422` | `validation_error` | Request body fails schema validation. |
| `500` | `internal_error` | Unexpected server error. |

---

### 2. Finish / update session

```
PATCH /api/v1/external-results/session/{session_id}
```

**Auth scope:** `external_results:write`

Sets the terminal status of a session. Only `passed`, `failed`, or `aborted` are accepted.

#### Request body

```json
{
  "status": "passed",
  "summary": {
    "total": 42,
    "passed": 40,
    "failed": 2,
    "skipped": 0
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | `"passed" \| "failed" \| "aborted"` | ✅ | Terminal status. `started` and `skipped` are rejected with `422`. |
| `summary` | `object` | — | Aggregate counters. Defaults to `{}`. |

#### Success response — `200 OK`

Returns the updated `SessionResponse` (same shape as `POST /session`).

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `400` | `session.already_finished` | Session is already in a terminal state. |
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `403` | `runner_token.scope_denied` | Token lacks `external_results:write`. |
| `404` | `session.not_found` | `session_id` does not exist. |
| `409` | `session.transition.invalid` | Status transition is not allowed (see §e). |
| `422` | `validation_error` | `status` is `started` or `skipped`. |
| `500` | `internal_error` | Unexpected server error. |

---

### 3. Get session

```
GET /api/v1/external-results/session/{session_id}
```

**Auth scope:** `external_results:read` OR a valid user JWT.

#### Success response — `200 OK`

Returns `SessionResponse`. Same shape as the `POST /session` response.

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `404` | `session.not_found` | `session_id` does not exist. |

---

### 4. Create case result

```
POST /api/v1/external-results/case
```

**Auth scope:** `external_results:write`

Records one test-case execution. Duplicate `external_id` within the same `session_id` collapses to the same row (idempotent — see §d).

#### Request body

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "test_case_id": null,
  "external_id": "suite > login > should redirect to dashboard",
  "title": "should redirect to dashboard",
  "outcome": "passed",
  "duration_ms": 1234,
  "error_message": null,
  "requirement_ids": [
    "c1234567-89ab-cdef-0123-456789abcdef"
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | `UUID` | ✅ | Session this result belongs to. |
| `test_case_id` | `UUID \| null` | ⚠️ | BGSTM test-case UUID, if known. At least one of `test_case_id` or `external_id` is required. |
| `external_id` | `string \| null` | ⚠️ | Runner-assigned unique test identifier. At least one of `test_case_id` or `external_id` is required. |
| `title` | `string` | ✅ | Human-readable test title. |
| `outcome` | `CaseOutcome` | ✅ | `passed`, `failed`, `skipped`, or `flaky`. |
| `duration_ms` | `integer ≥ 0` | ✅ | Wall-clock duration in milliseconds. |
| `error_message` | `string \| null` | — | First error line or assertion message. |
| `requirement_ids` | `UUID[]` | — | Requirement UUIDs to link. Duplicate insertions are no-ops. Defaults to `[]`. |

#### Success response — `201 Created`

```json
{
  "id": "7f000001-0000-0000-0000-000000000001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "test_case_id": null,
  "external_id": "suite > login > should redirect to dashboard",
  "title": "should redirect to dashboard",
  "outcome": "passed",
  "duration_ms": 1234,
  "error_message": null,
  "requirement_ids": ["c1234567-89ab-cdef-0123-456789abcdef"],
  "created_at": "2025-01-15T12:01:00Z",
  "auto_registered": false
}
```

`auto_registered: true` when BGSTM created a new test-case record from `external_id` (i.e. no `test_case_id` was supplied and the `external_id` had not been seen before in this project).

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `403` | `runner_token.scope_denied` | Token lacks `external_results:write`. |
| `404` | `session.not_found` | `session_id` does not exist. |
| `404` | `requirement.not_found` | One or more `requirement_ids` do not exist. |
| `409` | `session.already_finished` | Session is in a terminal state; no new results accepted. |
| `422` | `validation_error` | Both `test_case_id` and `external_id` are null, or `duration_ms < 0`. |
| `500` | `internal_error` | Unexpected server error. |

---

### 5. Update case result

```
PATCH /api/v1/external-results/case/{id}
```

**Auth scope:** `external_results:write`

Partial update: any combination of `outcome`, `duration_ms`, and `error_message`.

#### Request body

```json
{
  "outcome": "flaky",
  "duration_ms": 5000,
  "error_message": "Element not found after retry"
}
```

All fields are optional. Omitted fields are left unchanged.

#### Success response — `200 OK`

Returns the updated `CaseResultResponse`.

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `403` | `runner_token.scope_denied` | Token lacks `external_results:write`. |
| `404` | `case_result.not_found` | Case result `id` does not exist. |
| `409` | `case_result.transition.invalid` | Outcome transition is not allowed (see §e). |
| `422` | `validation_error` | `duration_ms < 0`. |
| `500` | `internal_error` | Unexpected server error. |

---

### 6. Get case result

```
GET /api/v1/external-results/case/{id}
```

**Auth scope:** `external_results:read` OR a valid user JWT.

#### Success response — `200 OK`

Returns `CaseResultResponse`.

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `404` | `case_result.not_found` | Case result `id` does not exist. |

---

### 7. Upload artifact

```
POST /api/v1/external-results/artifact
```

**Auth scope:** `external_results:write`

Multipart upload (`multipart/form-data`).  The four form fields below are locked — the reporter at `bgstm-playwright-frameworks` pinned SHA `ab5d7c1` sends exactly these names.

#### Request parts (multipart/form-data)

| Field name | Type | Required | Description |
|---|---|---|---|
| `case_result_id` | string (UUID) | ✓ | UUID of the owning `external_case_result`. |
| `kind` | string | ✓ | Artifact type: `screenshot`, `video`, `trace`, `log`, or `other`. |
| `filename` | string | ✓ | Original filename, including extension. |
| `file` | binary | ✓ | Raw artifact bytes.  The HTTP `Content-Type` header of this part is used as the artifact's MIME type. |

> **Note:** There is no separate `content_type` or `size_bytes` form field.  The `content_type` is read from the `file` part's `Content-Type` header and the `size_bytes` is counted while streaming the body.

#### Content-type allowlist

The following MIME types are accepted.  Requests with any other content-type are rejected with `415` **unless** `kind=other`, which bypasses the allowlist entirely.

```
image/png  image/jpeg  image/gif  image/webp
video/webm  video/mp4  video/mpeg
application/zip  application/x-zip-compressed  application/octet-stream
text/plain  application/json
```

#### Size enforcement

The server enforces `BGSTM_ARTIFACT_MAX_BYTES` (default 50 MiB) by reading the upload in 64 KiB chunks and accumulating a byte count.  Once the running total exceeds the limit, the server deletes its own temp copy and returns `413`.

> **Note on buffering:** FastAPI/Starlette parses the full multipart body via `python-multipart` before the handler runs, spooling to a temp file if the payload exceeds ~1 MiB.  The 413 check therefore operates on the spooled copy, not the live network stream.  For first-line DoS protection, configure your reverse proxy (e.g. nginx `client_max_body_size`, AWS ALB) to reject oversized bodies before they reach the application.  True in-stream early-abort (aborting mid-wire) is tracked as a follow-up improvement.

#### Success response — `201 Created`

```json
{
  "id": "af000001-0000-0000-0000-000000000001",
  "case_result_id": "7f000001-0000-0000-0000-000000000001",
  "kind": "screenshot",
  "filename": "failure-state.png",
  "content_type": "image/png",
  "size_bytes": 20480,
  "url": "https://storage.example.com/artifacts/failure-state.png",
  "created_at": "2025-01-15T12:02:00Z"
}
```

#### Error codes

| Status | `code` | Cause |
|---|---|---|
| `401` | `runner_token.invalid` | Missing or invalid token. |
| `403` | `runner_token.scope_denied` | Token lacks `external_results:write`. |
| `404` | `case_result.not_found` | `case_result_id` does not exist. |
| `413` | `artifact.too_large` | Artifact body exceeds the configured size limit. |
| `415` | `artifact.unsupported_type` | `content_type` is not in the allowed list. |
| `422` | `validation_error` | Payload fails schema validation (bad UUID, unknown kind, etc.). |
| `500` | `internal_error` | Unexpected server error. |

#### Audit log

Every successful upload writes an `external_results.artifact.upload` audit entry.  The `details` JSON always contains these five fields (the smoke workflow at PR #314 reconstructs case-result → artifact relationships from these fields):

```json
{
  "case_result_id": "<uuid>",
  "kind": "<artifact_kind>",
  "size_bytes": 20480,
  "filename": "failure-state.png",
  "content_type": "image/png"
}
```

---

## d. Idempotency rules

### Case results — deduplication by `external_id`

When a runner POSTs a case result with an `external_id` that already exists for the same `session_id`, BGSTM returns the **existing row** (`200 OK`) rather than creating a duplicate or returning `409`. This means re-running `POST /case` with identical input is safe.

### Traceability links — `requirement_ids`

Inserting a `(test_case_id, requirement_id)` link that already exists is a **no-op**. No error is raised.

### Artifacts — deduplication by SHA-256

If the body of a new artifact upload has the same SHA-256 as an artifact already attached to the same `case_result_id`, BGSTM returns the **existing artifact row** (`200 OK`) rather than creating a second copy. The `409` code in the error table above is the response shape, but the HTTP status is `200` (not an error condition — the caller's intent is fulfilled).

---

## e. Status transition rules

### Session status

| From | To | Allowed? |
|---|---|---|
| `started` | `passed` | ✅ |
| `started` | `failed` | ✅ |
| `started` | `aborted` | ✅ |
| `passed` / `failed` | any | ❌ → `409 session.transition.invalid` |
| `aborted` | any | ❌ → `409 session.transition.invalid` (terminal) |

### Case result outcome

| From | To | Allowed? |
|---|---|---|
| `passed` / `failed` / `skipped` | `flaky` | ✅ (re-classification after a retry) |
| `passed` / `failed` / `skipped` | any other | ❌ → `409 case_result.transition.invalid` |
| `flaky` | any | ❌ → `409 case_result.transition.invalid` (terminal) |

---

## f. Error model

All error responses share a single envelope:

```json
{
  "code": "runner_token.invalid",
  "message": "The provided runner token is invalid or has been revoked.",
  "details": {
    "token_prefix": "bgstm_runner_"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `code` | `string` | Machine-readable dotted-path code. |
| `message` | `string` | Human-readable explanation. |
| `details` | `object \| null` | Optional structured context (never contains the token itself). |

### Error code registry

| Code | Meaning |
|---|---|
| `runner_token.missing` | No `Authorization` header present. |
| `runner_token.invalid` | Token not found or malformed. |
| `runner_token.expired` | Token has passed its `expires_at`. |
| `runner_token.scope_denied` | Token lacks the required scope. |
| `runner_token.project_denied` | Token is not authorized for this project. |
| `session.not_found` | Session UUID does not exist. |
| `session.project_not_found` | `project_id` in `SessionCreate` does not exist. |
| `session.already_finished` | Session is already in a terminal state. |
| `session.transition.invalid` | Requested status transition is not allowed. |
| `case_result.not_found` | Case result UUID does not exist. |
| `case_result.transition.invalid` | Requested outcome transition is not allowed. |
| `requirement.not_found` | One or more `requirement_ids` do not exist. |
| `artifact.not_found` | Artifact UUID does not exist. |
| `artifact.too_large` | Artifact body exceeds size limit. |
| `artifact.unsupported_type` | `content_type` is not in the allowed list. |
| `artifact.duplicate` | Identical artifact already exists (see §d). |
| `validation_error` | Request body failed Pydantic schema validation. |
| `internal_error` | Unhandled server-side error. |

---

## g. Storage abstraction

Artifact binaries are stored via a pluggable `StorageBackend` abstraction (`backend/app/storage/`).

### Backend selection

Controlled by the `BGSTM_STORAGE_BACKEND` environment variable:

| Value | Backend | Notes |
|---|---|---|
| `local` | `LocalFsBackend` | Writes to `BGSTM_ARTIFACTS_DIR` (default `./artifacts`). Files are served by a dev-only static route mounted at `/artifacts`. **Do not use in production.** |
| `s3` | `S3Backend` | Stub only — raises `NotImplementedError` with a clear message. Set `BGSTM_STORAGE_BACKEND=local` for now. |

### Configuration

| Environment variable | Default | Description |
|---|---|---|
| `BGSTM_STORAGE_BACKEND` | `local` | Backend selector (`local` or `s3`). |
| `BGSTM_ARTIFACTS_DIR` | `./artifacts` | Root directory for `LocalFsBackend`. |
| `BGSTM_ARTIFACT_MAX_BYTES` | `52428800` (50 MiB) | Maximum artifact upload size. |
| `BGSTM_ARTIFACT_URL_PREFIX` | `http://localhost:8000/artifacts` | Base URL used by `LocalFsBackend` when constructing download URLs. |

### `StorageBackend` ABC

```python
class StorageBackend(ABC):
    def save(self, stream, *, key: str, content_type: str) -> StorageResult: ...
    def url_for(self, key: str) -> str: ...
```

`get_storage()` (in `backend/app/storage/__init__.py`) is a **function**, not a module-level singleton, so tests can swap settings without import-time side effects.

### Dev-only static route

When `BGSTM_STORAGE_BACKEND=local`, `main.py` mounts a `StaticFiles` route at `/artifacts` pointing at `BGSTM_ARTIFACTS_DIR`.  This route is **not** mounted for any other backend.

---

## h. Observability

### Audit log

Every state-changing call now writes an **audit log entry** recording actor identity, action, and affected resource (implemented in [BGSTM#297](https://github.com/bg-playground/BGSTM/issues/297)).

### Action taxonomy

| Action | Trigger |
|---|---|
| `external_results.session.start` | `POST /session` → `201` |
| `external_results.session.finish` | `PATCH /session/{id}` → `200` |
| `external_results.case.create` | `POST /case` → `201` |
| `external_results.case.update` | `PATCH /case/{id}` → `200` |
| `external_results.artifact.upload` | `POST /artifact` → `201` |

Each audit entry records:

- `actor_kind` — `user` or `runner_token`.
- `user_id` — UUID for user actors, nullable for runner-token actors.
- `actor_token_id` — UUID for runner-token actors, nullable for user actors (never the raw token string).
- `action` — one of the values above.
- `resource_type` — `external_session`, `case_result`, or `artifact`.
- `resource_id` — UUID of the created/updated resource.
- `project_id` — UUID of the project.
- `details` — JSON snapshot of the mutation (before/after where applicable).

Action taxonomy is enforced on the write paths: no state-changing External Results endpoint may skip audit emission.

---

## i. Reference implementation

The TypeScript reference reporter is being developed in [bgstm-playwright-frameworks](https://github.com/bg-playground/bgstm-playwright-frameworks) as part of [bgstm-playwright-frameworks#3](https://github.com/bg-playground/bgstm-playwright-frameworks/issues/3).

The reporter:

1. Calls `POST /session` at suite start.
2. Calls `POST /case` for each test result as it completes.
3. Calls `POST /artifact` for screenshots / traces on failure.
4. Calls `PATCH /session/{id}` with the terminal status at suite end.

A smoke-test that exercises the full lifecycle against a real BGSTM instance will live in BGSTM CI (tracked in [BGSTM#295](https://github.com/bg-playground/BGSTM/issues/295)).
