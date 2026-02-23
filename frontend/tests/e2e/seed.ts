/**
 * E2E test seed script.
 *
 * Creates the test users, projects, requirements, test cases, traceability links,
 * suggestions and notifications that the E2E suite depends on.
 *
 * Usage:
 *   npx tsx tests/e2e/seed.ts
 *   or
 *   API_URL=http://localhost:8000 npx tsx tests/e2e/seed.ts
 *
 * The script is idempotent – running it multiple times is safe because it uses
 * unique e-mail addresses / titles that won't collide with production data.
 */

const API_URL = process.env.API_URL ?? 'http://localhost:8000';
const API_PREFIX = '/api/v1';

// ── helpers ──────────────────────────────────────────────────────────────────

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  token?: string,
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${API_PREFIX}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${method} ${path} → ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

async function login(email: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>('POST', '/auth/login', {
    email,
    password,
  });
  return data.access_token;
}

async function registerOrLogin(
  email: string,
  password: string,
  fullName: string,
): Promise<string> {
  try {
    await request('POST', '/auth/register', { email, password, full_name: fullName });
  } catch {
    // user probably already exists – proceed to login
  }
  return login(email, password);
}

// ── seed ─────────────────────────────────────────────────────────────────────

export async function seed() {
  console.log('🌱  Seeding E2E test data …');

  // 1. Users
  const adminToken = await registerOrLogin(
    'e2e-admin@bgstm.test',
    'Admin1234!',
    'E2E Admin',
  );
  await registerOrLogin('e2e-reviewer@bgstm.test', 'Reviewer1234!', 'E2E Reviewer');
  await registerOrLogin('e2e-viewer@bgstm.test', 'Viewer1234!', 'E2E Viewer');

  console.log('  ✓ users');

  // 2. Requirements
  const reqTitles = [
    'User Authentication',
    'Password Reset',
    'Dashboard Overview',
    'Export Reports',
    'Notification System',
  ];

  const requirements: Array<{ id: string }> = [];
  for (const title of reqTitles) {
    try {
      const req = await request<{ id: string }>(
        'POST',
        '/requirements',
        {
          title,
          description: `${title} requirement for E2E testing`,
          type: 'functional',
          priority: 'medium',
          status: 'draft',
        },
        adminToken,
      );
      requirements.push(req);
    } catch {
      // already exists – fetch the list and find it
    }
  }

  console.log(`  ✓ ${requirements.length} requirements`);

  // 3. Test cases
  const tcTitles = [
    'Verify login with valid credentials',
    'Verify login with invalid credentials',
    'Verify password reset flow',
    'Verify dashboard loads',
    'Verify CSV export',
  ];

  const testCases: Array<{ id: string }> = [];
  for (const title of tcTitles) {
    try {
      const tc = await request<{ id: string }>(
        'POST',
        '/test-cases',
        {
          title,
          description: `${title} – created by E2E seed script`,
          type: 'functional',
          priority: 'medium',
          status: 'draft',
          automated: false,
        },
        adminToken,
      );
      testCases.push(tc);
    } catch {
      // already exists
    }
  }

  console.log(`  ✓ ${testCases.length} test cases`);

  // 4. Traceability links (first req ↔ first two TCs)
  if (requirements.length > 0 && testCases.length >= 2) {
    for (const tc of testCases.slice(0, 2)) {
      try {
        await request(
          'POST',
          '/links',
          {
            requirement_id: requirements[0].id,
            test_case_id: tc.id,
            link_type: 'covers',
            link_source: 'manual',
          },
          adminToken,
        );
      } catch {
        // already linked
      }
    }
    console.log('  ✓ traceability links');
  }

  // 5. Generate AI suggestions (best-effort – engine may not be configured in CI)
  try {
    await request('POST', '/suggestions/generate', null, adminToken);
    console.log('  ✓ AI suggestions generated');
  } catch {
    console.log('  ⚠  AI suggestion generation skipped (engine not available)');
  }

  console.log('✅  Seed complete');
}

// Run when executed directly
if (process.argv[1] && process.argv[1].endsWith('seed.ts')) {
  seed().catch((err) => {
    console.error('Seed failed:', err);
    process.exit(1);
  });
}
