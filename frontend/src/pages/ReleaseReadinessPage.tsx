import { useCallback, useMemo, useRef, useState } from 'react';

import { isRequestCanceled } from '../api/client';
import { releaseReadinessApi, type ReadinessCriterion, type ReadinessSnapshot, type RoleSignoff } from '../api/releaseReadiness';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useEffectAsync } from '../hooks/useEffectAsync';

const roleLabel: Record<string, string> = {
  qa_lead: 'QA Lead',
  product: 'Product',
  eng_lead: 'Engineering Lead',
};

const statusPillClass: Record<string, string> = {
  pass: 'bg-green-100 text-green-800',
  warn: 'bg-amber-100 text-amber-800',
  fail: 'bg-red-100 text-red-800',
  na: 'bg-gray-100 text-gray-700',
};

const bannerClass: Record<string, string> = {
  go: 'bg-green-600 text-white',
  caution: 'bg-amber-500 text-white',
  no_go: 'bg-red-600 text-white',
};

function groupByCategory(criteria: ReadinessCriterion[]): Array<[string, ReadinessCriterion[]]> {
  const grouped = new Map<string, ReadinessCriterion[]>();
  criteria.forEach((criterion) => {
    const current = grouped.get(criterion.category) ?? [];
    current.push(criterion);
    grouped.set(criterion.category, current);
  });
  return Array.from(grouped.entries());
}

export default function ReleaseReadinessPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [snapshot, setSnapshot] = useState<ReadinessSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyRole, setBusyRole] = useState<string | null>(null);
  const refreshControllerRef = useRef<AbortController | null>(null);
  const actionControllerRef = useRef<AbortController | null>(null);

  const beginAction = useCallback((): AbortSignal => {
    actionControllerRef.current?.abort();
    const controller = new AbortController();
    actionControllerRef.current = controller;
    return controller.signal;
  }, []);

  const loadSnapshot = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoading(true);
      const data = await releaseReadinessApi.getSnapshot({ signal });
      setSnapshot(data);
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to load release readiness', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffectAsync(async (signal) => {
    await loadSnapshot(signal);
  }, [loadSnapshot]);

  const handleRefresh = useCallback(() => {
    refreshControllerRef.current?.abort();
    const controller = new AbortController();
    refreshControllerRef.current = controller;
    void loadSnapshot(controller.signal);
  }, [loadSnapshot]);

  const handleExport = useCallback(async (format: 'md' | 'pdf') => {
    try {
      const signal = beginAction();
      const blob = await releaseReadinessApi.exportReport(format, { signal });
      const filename = format === 'md' ? 'release_readiness_report.md' : 'release_readiness_report.pdf';
      releaseReadinessApi.downloadExport(blob, filename);
      showToast(`Exported ${format.toUpperCase()} report`, 'success');
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast(`Failed to export ${format.toUpperCase()} report`, 'error');
    }
  }, [beginAction, showToast]);

  const handleSignoff = useCallback(async (role: string) => {
    try {
      setBusyRole(role);
      const signal = beginAction();
      const updated = await releaseReadinessApi.signoff(role, null, { signal });
      setSnapshot(updated);
      showToast(`Signed off as ${roleLabel[role] ?? role}`, 'success');
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to sign off', 'error');
    } finally {
      setBusyRole(null);
    }
  }, [beginAction, showToast]);

  const handleRevoke = useCallback(async (role: string) => {
    try {
      setBusyRole(role);
      const signal = beginAction();
      const updated = await releaseReadinessApi.revoke(role, { signal });
      setSnapshot(updated);
      showToast(`Revoked ${roleLabel[role] ?? role} sign-off`, 'success');
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to revoke sign-off', 'error');
    } finally {
      setBusyRole(null);
    }
  }, [beginAction, showToast]);

  const handleRequestSignoff = useCallback(async (role: string) => {
    try {
      setBusyRole(role);
      const signal = beginAction();
      await releaseReadinessApi.requestSignoff(role, null, { signal });
      showToast(`Sign-off requested for ${roleLabel[role] ?? role}`, 'success');
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to request sign-off', 'error');
    } finally {
      setBusyRole(null);
    }
  }, [beginAction, showToast]);

  const groupedCriteria = useMemo(() => groupByCategory(snapshot?.criteria ?? []), [snapshot?.criteria]);
  const isAdmin = user?.role === 'admin';

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No release readiness data available</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Release Readiness Dashboard</h1>
          <a
            href="https://github.com/bg-playground/BGSTM/blob/main/docs/features/release-readiness-dashboard.md"
            target="_blank"
            rel="noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            What is this?
          </a>
        </div>
        <div className="flex items-center gap-2">
          <details className="relative">
            <summary className="list-none cursor-pointer px-3 py-2 text-sm bg-slate-700 text-white rounded hover:bg-slate-800">
              Export
            </summary>
            <div className="absolute right-0 mt-2 bg-white border border-gray-200 rounded shadow-lg z-10 min-w-48">
              <button
                onClick={() => handleExport('md')}
                data-testid="release-readiness-export-md"
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
              >
                Markdown
              </button>
              <button
                onClick={() => handleExport('pdf')}
                data-testid="release-readiness-export-pdf"
                className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
              >
                PDF
              </button>
            </div>
          </details>
          <button
            onClick={handleRefresh}
            className="px-3 py-2 text-sm bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
          >
            Refresh
          </button>
        </div>
      </div>

      <div
        data-testid="release-readiness-status-banner"
        className={`rounded-lg px-6 py-5 ${bannerClass[snapshot.overall_status]}`}
      >
        <p className="text-xs uppercase tracking-wider">Overall status</p>
        <p className="text-3xl font-bold">{snapshot.overall_status.replace('_', ' ').toUpperCase()}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4"><p className="text-sm text-gray-500">Passed</p><p className="text-2xl font-bold text-green-600">{snapshot.summary.passed}</p></div>
        <div className="bg-white rounded-lg shadow p-4"><p className="text-sm text-gray-500">Warning</p><p className="text-2xl font-bold text-amber-600">{snapshot.summary.warning}</p></div>
        <div className="bg-white rounded-lg shadow p-4"><p className="text-sm text-gray-500">Failed</p><p className="text-2xl font-bold text-red-600">{snapshot.summary.failed}</p></div>
        <div className="bg-white rounded-lg shadow p-4"><p className="text-sm text-gray-500">Total</p><p className="text-2xl font-bold text-gray-800">{snapshot.summary.total}</p></div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100"><h2 className="text-xl font-semibold text-gray-900">Criteria</h2></div>
        {groupedCriteria.map(([category, items]) => (
          <div key={category}>
            <div className="px-6 py-2 bg-gray-50 text-sm font-semibold text-gray-700">{category}</div>
            <table className="min-w-full divide-y divide-gray-100">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase">Criterion</th>
                  <th className="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                  <th className="px-6 py-2 text-left text-xs font-medium text-gray-500 uppercase">Threshold</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((criterion) => (
                  <tr key={criterion.id} data-testid="release-readiness-criterion-row">
                    <td className="px-6 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusPillClass[criterion.status]}`}>
                        {criterion.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-800">{criterion.label}</td>
                    <td className="px-6 py-3 text-sm text-gray-700">{criterion.value}</td>
                    <td className="px-6 py-3 text-xs text-gray-500">{criterion.threshold}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Role Sign-offs</h2>
        <div className="space-y-3">
          {snapshot.signoffs.map((signoff: RoleSignoff) => (
            <div
              key={signoff.role}
              data-testid={`release-readiness-signoff-${signoff.role}`}
              className="border border-gray-200 rounded-lg p-4 flex items-center justify-between"
            >
              <div>
                <p className="font-semibold text-gray-900">{roleLabel[signoff.role] ?? signoff.role}</p>
                <p className="text-sm text-gray-600">
                  {signoff.signed_off
                    ? `Signed off by ${signoff.signed_off_by ?? 'unknown'}${signoff.signed_off_at ? ` on ${new Date(signoff.signed_off_at).toLocaleString()}` : ''}`
                    : 'Not signed off'}
                </p>
                {signoff.note && <p className="text-xs text-gray-500 mt-1">Note: {signoff.note}</p>}
              </div>
              <div>
                {isAdmin ? (
                  signoff.signed_off ? (
                    <button
                      onClick={() => handleRevoke(signoff.role)}
                      disabled={busyRole === signoff.role}
                      className="px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                    >
                      Revoke
                    </button>
                  ) : (
                    <button
                      onClick={() => handleSignoff(signoff.role)}
                      disabled={busyRole === signoff.role}
                      className="px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      Sign off
                    </button>
                  )
                ) : !signoff.signed_off ? (
                  <button
                    onClick={() => handleRequestSignoff(signoff.role)}
                    disabled={busyRole === signoff.role}
                    className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    Request sign-off
                  </button>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
