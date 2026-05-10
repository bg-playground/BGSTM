import { apiClient } from './client';

export type RunStatus = 'started' | 'passed' | 'failed' | 'skipped' | 'aborted';
export type CaseOutcome = 'passed' | 'failed' | 'skipped' | 'flaky';

export interface TestSessionSummary {
  total?: number;
  passed?: number;
  failed?: number;
  skipped?: number;
}

export interface TestSession {
  id: string;
  status: RunStatus;
  started_at: string;
  finished_at: string | null;
  runner: string;
  project_id: string;
  git_sha: string | null;
  git_branch: string | null;
  ci_url: string | null;
  metadata: Record<string, unknown>;
  summary?: TestSessionSummary;
}

export interface CaseResult {
  id: string;
  session_id: string;
  test_case_id: string | null;
  external_id: string | null;
  title: string;
  outcome: CaseOutcome;
  duration_ms: number;
  error_message: string | null;
  requirement_ids: string[];
  created_at: string;
  auto_registered: boolean;
}

export interface SessionListResponse {
  sessions: TestSession[];
  total: number;
  skip: number;
  limit: number;
}

export interface CaseResultListResponse {
  cases: CaseResult[];
  total: number;
  skip: number;
  limit: number;
}

export const externalResultsApi = {
  listSessions: (params: { skip?: number; limit?: number; status?: RunStatus } = {}) => {
    const p = new URLSearchParams();
    if (params.skip !== undefined) p.set('skip', String(params.skip));
    if (params.limit !== undefined) p.set('limit', String(params.limit));
    if (params.status) p.set('status', params.status);
    return apiClient.get<SessionListResponse>(`/external-results/sessions?${p.toString()}`);
  },
  getSession: (sessionId: string) => apiClient.get<TestSession>(`/external-results/session/${sessionId}`),
  listSessionCases: (sessionId: string, params: { skip?: number; limit?: number } = {}) => {
    const p = new URLSearchParams();
    if (params.skip !== undefined) p.set('skip', String(params.skip));
    if (params.limit !== undefined) p.set('limit', String(params.limit));
    return apiClient.get<CaseResultListResponse>(`/external-results/session/${sessionId}/cases?${p.toString()}`);
  },
};
