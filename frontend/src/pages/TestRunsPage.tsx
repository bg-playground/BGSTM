import React, { useCallback, useMemo, useState } from 'react';
import { isRequestCanceled } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { externalResultsApi, type RunStatus, type TestSession } from '../api/externalResults';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';
import { useEffectAsync } from '../hooks/useEffectAsync';

const PAGE_SIZE = 25;

type StatusFilter = 'all' | 'running' | 'passed' | 'failed' | 'aborted';

const statusBadgeClass: Record<RunStatus, string> = {
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  started: 'bg-yellow-100 text-yellow-800',
  aborted: 'bg-gray-100 text-gray-700',
  skipped: 'bg-gray-100 text-gray-500',
};

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString();
}

function formatDuration(startedAt: string, finishedAt: string | null): string {
  if (!finishedAt) return '—';
  const ms = Math.max(0, new Date(finishedAt).getTime() - new Date(startedAt).getTime());
  if (ms >= 1000) return `${(ms / 1000).toFixed(1)}s`;
  return `${ms}ms`;
}

function toStatusParam(filter: StatusFilter): RunStatus | undefined {
  switch (filter) {
    case 'running':
      return 'started';
    case 'passed':
      return 'passed';
    case 'failed':
      return 'failed';
    case 'aborted':
      return 'aborted';
    default:
      return undefined;
  }
}

export const TestRunsPage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [sessions, setSessions] = useState<TestSession[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [loading, setLoading] = useState(true);

  const pages = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  const loadSessions = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      const skip = (page - 1) * PAGE_SIZE;
      const res = await externalResultsApi.listSessions({
        skip,
        limit: PAGE_SIZE,
        status: toStatusParam(statusFilter),
      }, { signal });
      setSessions(res.data.sessions);
      setTotal(res.data.total);
    } catch (error) {
      if (isRequestCanceled(error)) return;
      console.error('Failed to load test runs:', error);
      showToast('Failed to load test runs', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, showToast, statusFilter]);

  useEffectAsync(async (signal) => {
    await loadSessions(signal);
  }, [loadSessions]);

  const handleStatusFilterChange = useCallback((event: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(event.target.value as StatusFilter);
    setPage(1);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Test Runs</h1>
        <select
          value={statusFilter}
          onChange={handleStatusFilterChange}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="all">All</option>
          <option value="running">Running</option>
          <option value="passed">Passed</option>
          <option value="failed">Failed</option>
          <option value="aborted">Aborted</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : sessions.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-10 text-center">
          <p className="text-gray-500">
            No test runs yet. Connect the BGSTM Playwright reporter to start recording results.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Started', 'Status', 'Branch', 'Commit', 'Runner', 'Total / Passed / Failed', 'Duration', 'CI'].map(
                  (col) => (
                    <th
                      key={col}
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                    >
                      {col}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sessions.map((session) => {
                const totalCount = session.summary?.total ?? 0;
                const passedCount = session.summary?.passed ?? 0;
                const failedCount = session.summary?.failed ?? 0;
                return (
                  <tr
                    key={session.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/runs/${session.id}`)}
                  >
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">{formatDateTime(session.started_at)}</td>
                    <td className="px-4 py-3 text-sm whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusBadgeClass[session.status]}`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">{session.git_branch ?? '—'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 font-mono whitespace-nowrap">
                      {session.git_sha ? session.git_sha.slice(0, 8) : '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">{session.runner}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                      {`${totalCount} / ${passedCount} / ${failedCount}`}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                      {formatDuration(session.started_at, session.finished_at)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                      {session.ci_url ? (
                        <a
                          href={session.ci_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-primary-600 hover:text-primary-800"
                          onClick={(e) => e.stopPropagation()}
                          aria-label="Open CI run"
                        >
                          ↗
                        </a>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
    </div>
  );
};
