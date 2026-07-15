import { useCallback, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { isRequestCanceled } from '../../api/client';
import { qualityMetricsApi, type FlakyTestEntry, type FlakyRankingResponse, type WindowDays } from '../../api/qualityMetrics';
import { LoadingSpinner } from '../LoadingSpinner';
import { useEffectAsync } from '../../hooks/useEffectAsync';

const outcomeBadgeClass: Record<string, string> = {
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  flaky: 'bg-orange-100 text-orange-800',
  skipped: 'bg-gray-100 text-gray-500',
  started: 'bg-yellow-100 text-yellow-800',
  aborted: 'bg-gray-100 text-gray-700',
};

type SortKey = 'display_name' | 'runs' | 'transitions' | 'flip_rate' | 'last_outcome' | 'last_seen_at';
type SortDirection = 'asc' | 'desc';

function formatFlipRate(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function sortRows(entries: FlakyTestEntry[], key: SortKey, direction: SortDirection): FlakyTestEntry[] {
  const multiplier = direction === 'asc' ? 1 : -1;
  return [...entries].sort((a, b) => {
    if (key === 'display_name' || key === 'last_outcome') {
      return multiplier * a[key].localeCompare(b[key]);
    }
    if (key === 'last_seen_at') {
      return multiplier * (new Date(a.last_seen_at).getTime() - new Date(b.last_seen_at).getTime());
    }
    return multiplier * ((a[key] as number) - (b[key] as number));
  });
}

export function FlakyRankingPanel({ window }: { window: WindowDays }) {
  const [data, setData] = useState<FlakyRankingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>('flip_rate');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffectAsync(
    async (signal) => {
      try {
        setLoading(true);
        const next = await qualityMetricsApi.getFlakyRanking(window, 10, { signal });
        setData(next);
      } catch (error) {
        if (!isRequestCanceled(error)) {
          setData({
            entries: [],
            is_synthetic: false,
            reason: 'Failed to load flaky ranking data.',
          });
        }
      } finally {
        setLoading(false);
      }
    },
    [window]
  );

  const onSort = useCallback((nextKey: SortKey) => {
    setSortKey((currentKey) => {
      if (currentKey === nextKey) {
        setSortDirection((currentDirection) => (currentDirection === 'desc' ? 'asc' : 'desc'));
        return currentKey;
      }
      setSortDirection('desc');
      return nextKey;
    });
  }, []);

  const sortedEntries = useMemo(() => {
    if (!data) {
      return [];
    }
    return sortRows(data.entries, sortKey, sortDirection);
  }, [data, sortDirection, sortKey]);

  return (
    <div data-testid="quality-dashboard-chart-flaky-ranking" className="rounded-lg bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold text-slate-900">Flaky Test Ranking</h2>
      {loading && !data ? (
        <div className="flex h-72 items-center justify-center">
          <LoadingSpinner />
        </div>
      ) : !data || data.entries.length === 0 ? (
        <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center">
          <div className="space-y-2">
            <p className="text-sm font-semibold text-slate-700">Flaky Test Ranking</p>
            <p className="text-sm text-slate-500">{data?.reason ?? 'No data available for this chart yet.'}</p>
          </div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left font-semibold text-slate-700">
                  <button onClick={() => onSort('display_name')}>Test</button>
                </th>
                <th className="px-3 py-2 text-right font-semibold text-slate-700">
                  <button onClick={() => onSort('runs')}>Runs</button>
                </th>
                <th className="px-3 py-2 text-right font-semibold text-slate-700">
                  <button onClick={() => onSort('transitions')}>Flips</button>
                </th>
                <th className="px-3 py-2 text-right font-semibold text-slate-700">
                  <button onClick={() => onSort('flip_rate')}>Flip rate</button>
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-700">
                  <button onClick={() => onSort('last_outcome')}>Last outcome</button>
                </th>
                <th className="px-3 py-2 text-left font-semibold text-slate-700">
                  <button onClick={() => onSort('last_seen_at')}>Last seen</button>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedEntries.map((entry) => {
                const searchValue = entry.test_case_id ?? entry.external_id ?? entry.display_name;
                return (
                  <tr key={`${entry.test_case_id ?? 'ext'}:${entry.external_id ?? entry.display_name}`}>
                    <td className="px-3 py-2 text-slate-800">
                      <Link className="text-blue-600 hover:text-blue-800" to={`/test-cases?search=${encodeURIComponent(searchValue)}`}>
                        {entry.display_name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-right text-slate-700">{entry.runs}</td>
                    <td className="px-3 py-2 text-right text-slate-700">{entry.transitions}</td>
                    <td className="px-3 py-2 text-right text-slate-700">{formatFlipRate(entry.flip_rate)}</td>
                    <td className="px-3 py-2">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                          outcomeBadgeClass[entry.last_outcome] ?? 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {entry.last_outcome}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-slate-700">{new Date(entry.last_seen_at).toLocaleString()}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
