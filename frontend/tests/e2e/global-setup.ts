import { apiLogin, API_URL } from './helpers/api';

type PaginatedResponse<T> = {
  items: T[];
  total: number;
};

type SeededTestCase = {
  external_id: string | null;
  title: string;
};

const API_PREFIX = '/api/v1';
const REQUIRED_TEST_CASE_IDS = ['TC-001', 'TC-002', 'TC-003', 'TC-004', 'TC-005'] as const;

async function getPaginated<T>(path: string, token: string): Promise<PaginatedResponse<T>> {
  const response = await fetch(`${API_URL}${API_PREFIX}${path}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`[E2E seed smoke check] GET ${path} failed with ${response.status}: ${body}`);
  }

  return (await response.json()) as PaginatedResponse<T>;
}

export default async function globalSetup(): Promise<void> {
  const email = process.env.E2E_ADMIN_EMAIL || 'admin@test.com';
  const password = process.env.E2E_ADMIN_PASSWORD || 'password123';
  const token = await apiLogin(email, password);

  const [requirements, testCases, links] = await Promise.all([
    getPaginated('/requirements?page=1&page_size=200', token),
    getPaginated<SeededTestCase>('/test-cases?page=1&page_size=200', token),
    getPaginated('/links?page=1&page_size=200', token),
  ]);

  if (requirements.total < 5) {
    throw new Error(`[E2E seed smoke check] requirements seed incomplete: expected >= 5, found ${requirements.total}`);
  }

  if (testCases.total < 5) {
    throw new Error(`[E2E seed smoke check] test_cases seed incomplete: expected >= 5, found ${testCases.total}`);
  }

  if (links.total < 3) {
    throw new Error(
      `[E2E seed smoke check] requirement_test_case_links seed incomplete: expected >= 3, found ${links.total}`,
    );
  }

  const availableIds = new Set(
    testCases.items
      .map((testCase) => testCase.external_id)
      .filter((externalId): externalId is string => typeof externalId === 'string' && externalId.length > 0),
  );

  const missingSeededCases = REQUIRED_TEST_CASE_IDS.filter((requiredId) => !availableIds.has(requiredId));

  if (missingSeededCases.length > 0) {
    throw new Error(
      `[E2E seed smoke check] seeded test_cases missing external_id(s): ${missingSeededCases.join(', ')}`,
    );
  }
}
