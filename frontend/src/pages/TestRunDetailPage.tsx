import React, { useCallback, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { externalResultsApi, type CaseOutcome, type CaseResult, type RunStatus, type TestSession } from '../api/externalResults';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import { useEffectAsync } from '../hooks/useEffectAsync';

const statusBadgeClass: Record<RunStatus, string> = {
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  started: 'bg-yellow-100 text-yellow-800',
  aborted: 'bg-gray-100 text-gray-700',
  skipped: 'bg-gray-100 text-gray-500',
};

const outcomeBadgeClass: Record<CaseOutcome, string> = {
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  flaky: 'bg-orange-100 text-orange-800',
  skipped: 'bg-gray-100 text-gray-500',
};

function formatDateTime(iso: string | null): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

function formatDurationMs(durationMs: number): string {
  if (durationMs >= 1000) return `${(durationMs / 1000).toFixed(1)}s`;
  return `${durationMs}ms`;
}

function formatSessionDuration(startedAt: string, finishedAt: string | null): string {
  if (!finishedAt) return '—';
  const ms = Math.max(0, new Date(finishedAt).getTime() - new Date(startedAt).getTime());
  return formatDurationMs(ms);
}

const TestRunDetailPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { showToast } = useToast();

  const [session, setSession] = useState<TestSession | null>(null);
  const [cases, setCases] = useState<CaseResult[]>([]);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    if (!sessionId) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const [sessionRes, casesRes] = await Promise.all([
        externalResultsApi.getSession(sessionId),
        externalResultsApi.listSessionCases(sessionId, { skip: 0, limit: 500 }),
      ]);
      setSession(sessionRes.data);
      setCases(casesRes.data.cases);
    } catch (error) {
      console.error('Failed to load test run details:', error);
      showToast('Failed to load test run details', 'error');
    } finally {
      setLoading(false);
    }
  }, [sessionId, showToast]);

  useEffectAsync(async () => {
    await loadData();
  }, [loadData]);

  const toggleExpand = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const progress = useMemo(() => {
    const total = session?.summary?.total ?? 0;
    const passed = session?.summary?.passed ?? 0;
    const failed = session?.summary?.failed ?? 0;
    const passedPct = total > 0 ? (passed / total) * 100 : 0;
    const failedPct = total > 0 ? (failed / total) * 100 : 0;
    const remainingPct = Math.max(0, 100 - passedPct - failedPct);
    return { passedPct, failedPct, remainingPct };
  }, [session]);

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!sessionId || !session) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Link to="/runs" className="text-primary-600 hover:underline text-sm">
          ← Back to Test Runs
        </Link>
        <div className="bg-gray-50 rounded-lg p-10 text-center mt-4">
          <p className="text-gray-500">Test run not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/runs" className="text-primary-600 hover:underline text-sm">
        ← Back to Test Runs
      </Link>

      <div className="bg-white rounded-lg shadow p-6 mt-4 mb-6">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Session {session.id.slice(0, 8)}</h1>
          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusBadgeClass[session.status]}`}>
            {session.status}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-gray-700">
          <div>
            <span className="font-semibold">Branch:</span> {session.git_branch ?? '—'}
          </div>
          <div>
            <span className="font-semibold">Commit:</span>{' '}
            <span className="font-mono">{session.git_sha ? session.git_sha.slice(0, 8) : '—'}</span>
          </div>
          <div>
            <span className="font-semibold">Runner:</span> {session.runner}
          </div>
          <div>
            <span className="font-semibold">Started:</span> {formatDateTime(session.started_at)}
          </div>
          <div>
            <span className="font-semibold">Finished:</span> {formatDateTime(session.finished_at)}
          </div>
          <div>
            <span className="font-semibold">Duration:</span> {formatSessionDuration(session.started_at, session.finished_at)}
          </div>
          <div className="md:col-span-2 lg:col-span-3">
            <span className="font-semibold">CI:</span>{' '}
            {session.ci_url ? (
              <a href={session.ci_url} target="_blank" rel="noreferrer" className="text-primary-600 hover:underline">
                {session.ci_url}
              </a>
            ) : (
              '—'
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
          <div className="bg-gray-50 rounded p-3 text-sm">
            <p className="text-gray-500">Total</p>
            <p className="text-xl font-semibold">{session.summary?.total ?? 0}</p>
          </div>
          <div className="bg-green-50 rounded p-3 text-sm">
            <p className="text-green-700">Passed</p>
            <p className="text-xl font-semibold text-green-800">{session.summary?.passed ?? 0}</p>
          </div>
          <div className="bg-red-50 rounded p-3 text-sm">
            <p className="text-red-700">Failed</p>
            <p className="text-xl font-semibold text-red-800">{session.summary?.failed ?? 0}</p>
          </div>
          <div className="bg-gray-50 rounded p-3 text-sm">
            <p className="text-gray-600">Skipped</p>
            <p className="text-xl font-semibold">{session.summary?.skipped ?? 0}</p>
          </div>
        </div>

        <div className="mt-5 w-full bg-gray-200 rounded-full h-3 overflow-hidden flex">
          <div className="bg-green-500" style={{ width: `${progress.passedPct}%` }} />
          <div className="bg-red-500" style={{ width: `${progress.failedPct}%` }} />
          <div className="bg-gray-400" style={{ width: `${progress.remainingPct}%` }} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Test Title', 'Outcome', 'Duration', 'Linked Requirements', 'Auto-registered', 'Error'].map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {cases.map((result) => (
              <React.Fragment key={result.id}>
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-800">{result.external_id ?? result.title}</td>
                  <td className="px-4 py-3 text-sm whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${outcomeBadgeClass[result.outcome]}`}>
                      {result.outcome}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">{formatDurationMs(result.duration_ms)}</td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs font-medium">
                      {result.requirement_ids.length} reqs
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {result.auto_registered ? (
                      <span className="px-2 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">auto</span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {result.error_message ? (
                      <button onClick={() => toggleExpand(result.id)} className="text-primary-600 hover:underline text-xs">
                        {expandedIds.has(result.id) ? '▲ collapse' : '▶ expand'}
                      </button>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                </tr>
                {expandedIds.has(result.id) && result.error_message ? (
                  <tr className="bg-gray-50">
                    <td colSpan={6} className="px-4 py-3">
                      <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-x-auto whitespace-pre-wrap">
                        {result.error_message}
                      </pre>
                    </td>
                  </tr>
                ) : null}
              </React.Fragment>
            ))}
            {cases.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-sm text-gray-500 text-center">
                  No case results recorded for this run.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TestRunDetailPage;
