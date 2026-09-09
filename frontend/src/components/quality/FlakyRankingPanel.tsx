import { useCallback, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { isRequestCanceled } from '../../api/client';
import {
  qualityMetricsApi,
  type FlakyTestEntry,
  type FlakyRankingResponse,
  type RecurringDefectEntry,
  type RecurringDefectsParetoResponse,
  type WindowDays,
} from '../../api/qualityMetrics';
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

const PARETO_BAR_COLOR = '#dc2626';
const PARETO_LINE_COLOR = '#2563eb';

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

function EmptyPanel({ title, reason }: { title: string; reason: string | null | undefined }) {
  return (
    <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center">
      <div className="space-y-2">
        <p className="text-sm font-semibold text-slate-700">{title}</p>
        <p className="text-sm text-slate-500">{reason ?? 'No data available for this chart yet.'}</p>
      </div>
    </div>
  );
}

function paretoEvidenceLink(entry: RecurringDefectEntry): string {
  const identity = entry.test_case_id ?? entry.external_id;
  const query = identity ? `?case=${encodeURIComponent(identity)}` : '';
  return `/runs/${entry.latest_failure_session_id}${query}`;
}

export function FlakyRankingPanel({ window }: { window: WindowDays }) {
  const navigate = useNavigate();
  const [flakyData, setFlakyData] = useState<FlakyRankingResponse | null>(null);
  const [paretoData, setParetoData] = useState<RecurringDefectsParetoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [sortKey, setSortKey] = useState<SortKey>('flip_rate');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffectAsync(
    async (signal) => {
      try {
        setLoading(true);
        const [nextFlaky, nextPareto] = await Promise.all([
          qualityMetricsApi.getFlakyRanking(window, 10, { signal }),
          qualityMetricsApi.getRecurringDefectsPareto(window, 10, { signal }),
        ]);
        if (signal.aborted) return;
        setFlakyData(nextFlaky);
        setParetoData(nextPareto);
      } catch (error) {
        if (!isRequestCanceled(error)) {
          setFlakyData({
            entries: [],
            is_synthetic: false,
            reason: 'Failed to load flaky ranking data.',
          });
          setParetoData({
            entries: [],
            total_recurring_failures: 0,
            is_synthetic: false,
            reason: 'Failed to load recurring defect data.',
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
    if (!flakyData) {
      return [];
    }
    return sortRows(flakyData.entries, sortKey, sortDirection);
  }, [flakyData, sortDirection, sortKey]);

  const paretoChartData = useMemo(
    () =>
      (paretoData?.entries ?? []).map((entry) => ({
        ...entry,
        label: entry.external_id ?? entry.display_name,
      })),
    [paretoData]
  );

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <div data-testid="quality-dashboard-chart-recurring-defects" className="rounded-lg bg-white p-6 shadow">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-slate-900">Recurring Defects Pareto</h2>
          <p className="mt-1 text-sm text-slate-500">
            Tests with two or more failures in the selected window. Bars are recurring failure counts; the line is cumulative share.
          </p>
        </div>
        {loading && !paretoData ? (
          <div className="flex h-72 items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : !paretoData || paretoData.entries.length === 0 ? (
          <EmptyPanel title="Recurring Defects Pareto" reason={paretoData?.reason} />
        ) : (
          <>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={paretoChartData} margin={{ top: 8, right: 16, left: 0, bottom: 48 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="label" interval={0} angle={-25} textAnchor="end" height={70} />
                  <YAxis yAxisId="count" allowDecimals={false} />
                  <YAxis yAxisId="pct" orientation="right" domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                  <Tooltip formatter={(value, name) => [name === 'cumulative_pct' ? `${value}%` : value, name === 'cumulative_pct' ? 'Cumulative %' : 'Recurring failures']} />
                  <Legend />
                  <Bar yAxisId="count" dataKey="failure_count" name="Recurring failures" fill={PARETO_BAR_COLOR}>
                    {paretoChartData.map((entry) => (
                      <Cell
                        key={`${entry.latest_failure_session_id}:${entry.label}`}
                        fill={PARETO_BAR_COLOR}
                        cursor="pointer"
                        onClick={() => navigate(paretoEvidenceLink(entry))}
                      />
                    ))}
                  </Bar>
                  <Line
                    yAxisId="pct"
                    type="monotone"
                    dataKey="cumulative_pct"
                    name="Cumulative %"
                    stroke={PARETO_LINE_COLOR}
                    strokeWidth={3}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 space-y-1 text-sm">
              {paretoData.entries.map((entry) => (
                <div key={`${entry.latest_failure_session_id}:${entry.test_case_id ?? entry.external_id ?? entry.display_name}`} className="flex items-center justify-between gap-3">
                  <span className="truncate text-slate-600">{entry.display_name} · {entry.module}</span>
                  <Link className="shrink-0 text-blue-600 hover:text-blue-800" to={paretoEvidenceLink(entry)}>
                    View latest failure
                  </Link>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      <div data-testid="quality-dashboard-chart-flaky-ranking" className="rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold text-slate-900">Flaky Test Ranking</h2>
        {loading && !flakyData ? (
          <div className="flex h-72 items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : !flakyData || flakyData.entries.length === 0 ? (
          <EmptyPanel title="Flaky Test Ranking" reason={flakyData?.reason} />
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
    </div>
  );
}
