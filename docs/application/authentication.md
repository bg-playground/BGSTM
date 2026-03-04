# Authentication & RBAC

BGSTM uses **JWT Bearer token** authentication and a simple three-tier role-based access control (RBAC) model.

## Roles

| Role | Permissions |
|---|---|
| `admin` | Full access: user management, audit log access, all reviewer permissions |
| `reviewer` | Create/edit requirements, test cases, and links; review and generate suggestions |
| `viewer` | Read-only access to all resources |

Every registered user is assigned the `viewer` role by default. An `admin` can promote users via the Users API.

## Endpoints

### Register

```
POST /api/v1/auth/register
```

Create a new user account.

**Request body:**

```json
{
  "email": "alice@example.com",
  "password": "s3cr3t!",
  "full_name": "Alice Smith"
}
```

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"s3cr3t!","full_name":"Alice Smith"}'
```

**Example (httpie):**

```bash
http POST http://localhost:8000/api/v1/auth/register \
  email=alice@example.com password=s3cr3t! full_name="Alice Smith"
```

---

### Login

```
POST /api/v1/auth/login
```

Authenticate and receive a JWT access token.

**Request body (form data):**

```
username=alice@example.com&password=s3cr3t!
```

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=alice@example.com&password=s3cr3t!"
```

**Response:**

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Tokens are valid for **60 minutes** by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

---

### Current User Profile

```
GET /api/v1/auth/me
```

Returns the profile of the currently authenticated user.

**Example (curl):**

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <JWT>"
```

**Response:**

```json
{
  "id": 1,
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "role": "viewer",
  "is_active": true
}
```

## Using the Token

Include the token in the `Authorization` header for every protected request:

```
Authorization: Bearer <JWT>
```

**Example (curl):**

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=alice@example.com&password=s3cr3t!" | jq -r .access_token)

curl http://localhost:8000/api/v1/requirements \
  -H "Authorization: Bearer $TOKEN"
```

## Default Admin Account

On first startup, BGSTM seeds a default admin user:

| Field | Default value |
|---|---|
| Email | `admin@bgstm.local` |
| Password | `admin1234` |

!!! warning "Change the default password immediately in any non-development environment."
    Set the `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD` environment variables before the first run, or update the account via the Users API after login.
