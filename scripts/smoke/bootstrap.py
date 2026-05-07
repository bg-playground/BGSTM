from __future__ import annotations

import json
import os
import uuid
from typing import Any

import httpx


def _api(client: httpx.Client, method: str, path: str, **kwargs) -> dict[str, Any]:
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Expected object response from {path}, got {type(data).__name__}")
    return data


def _get_or_generate_project_id(client: httpx.Client, headers: dict[str, str]) -> str:
    response = client.post("/api/v1/projects", headers=headers, json={"name": "smoke-project"})
    if response.status_code < 300:
        payload = response.json()
        project_id = payload.get("id")
        if isinstance(project_id, str) and project_id:
            return project_id
        raise RuntimeError("Project creation succeeded but no project id was returned.")
    if response.status_code == 404:
        print("Project creation endpoint not available; using generated project_id for external-results smoke run.")
        return str(uuid.uuid4())
    raise RuntimeError(f"Project creation failed: status={response.status_code}, body={response.text}")


def main() -> None:
    github_env = os.environ.get("GITHUB_ENV")
    if not github_env:
        raise RuntimeError("GITHUB_ENV is required")

    api_url = os.environ.get("BGSTM_API_URL", "http://localhost:8001")

    with httpx.Client(base_url=api_url, timeout=30.0) as client:
        login = _api(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"email": "admin@test.com", "password": "password123"},
        )
        admin_jwt = login["access_token"]
        headers = {"Authorization": f"Bearer {admin_jwt}"}

        project_id = _get_or_generate_project_id(client, headers)

        token_payload = {
            "label": "smoke",
            "scopes": ["external_results:write", "external_results:read"],
        }
        runner_token = _api(client, "POST", "/api/v1/auth/runner-tokens", headers=headers, json=token_payload)

    with open(github_env, "a", encoding="utf-8") as fh:
        fh.write(f"BGSTM_API_URL={api_url}\n")
        fh.write(f"BGSTM_API_TOKEN={runner_token['token']}\n")
        fh.write(f"BGSTM_PROJECT_ID={project_id}\n")
        fh.write(f"BGSTM_ADMIN_JWT={admin_jwt}\n")
        fh.write(f"BGSTM_RUNNER_TOKEN_ID={runner_token['id']}\n")

    print(json.dumps({"api_url": api_url, "project_id": project_id, "runner_token_id": runner_token["id"]}, indent=2))


if __name__ == "__main__":
    main()
