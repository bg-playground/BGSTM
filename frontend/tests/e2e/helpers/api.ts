/**
 * Helpers for direct API calls used during test setup and cleanup.
 * These bypass the UI and interact with the backend REST API directly.
 */

const API_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const url = `${API_URL}${API_PREFIX}${path}`;
  return fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
    ...options,
  });
}

export async function apiLogin(email: string, password: string): Promise<string> {
  const resp = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    throw new Error(`Login failed: ${resp.status} ${await resp.text()}`);
  }
  const data = (await resp.json()) as { access_token: string };
  return data.access_token;
}

export async function apiCreateRequirement(
  token: string,
  payload: { title: string; description: string; type?: string; priority?: string; status?: string },
): Promise<{ id: string }> {
  const resp = await apiFetch('/requirements/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      type: 'functional',
      priority: 'medium',
      status: 'draft',
      ...payload,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Create requirement failed: ${resp.status} ${await resp.text()}`);
  }
  return resp.json() as Promise<{ id: string }>;
}

export async function apiDeleteRequirement(token: string, id: string): Promise<void> {
  await apiFetch(`/requirements/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function apiCreateTestCase(
  token: string,
  payload: { title: string; description: string; type?: string; priority?: string; status?: string },
): Promise<{ id: string }> {
  const resp = await apiFetch('/test-cases/', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      type: 'functional',
      priority: 'medium',
      status: 'draft',
      automated: false,
      ...payload,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Create test case failed: ${resp.status} ${await resp.text()}`);
  }
  return resp.json() as Promise<{ id: string }>;
}

export async function apiDeleteTestCase(token: string, id: string): Promise<void> {
  await apiFetch(`/test-cases/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export { API_URL };
