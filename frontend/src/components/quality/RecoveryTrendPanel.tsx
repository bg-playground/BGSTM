import { useMemo, useState } from 'react';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { isRequestCanceled } from '../../api/client';
import {
  qualityMetricsApi,
  type RecoveryGroupBy,
  type RecoveryTrendResponse,
  type WindowDays,
} from '../../api/qualityMetrics';
import { useEffectAsync } from '../../hooks/useEffectAsync';
import { LoadingSpinner } from '../LoadingSpinner';

const GROUP_OPTIONS: Array<{ value: RecoveryGroupBy; label: string }> = [
  { value: 'overall', label: 'Overall' },
  { value: 'module', label: 'Module' },
  { value: 'severity', label: 'Severity' },
];

export function RecoveryTrendPanel({ window }: { window: WindowDays }) {
  const [groupBy, setGroupBy] = useState<RecoveryGroupBy>('overall');
  const [data, setData] = useState<RecoveryTrendResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffectAsync(
    async (signal) => {
      try {
        setLoading(true);
        const nextData = await qualityMetricsApi.getRecoveryTrend(window, groupBy, { signal });
        if (signal.aborted) return;
        setData(nextData);
      } catch (error) {
        if (!isRequestCanceled(error)) {
          setData({
            window_days: window,
            group_by: groupBy,
            points: [],
            mean_recovery_hours: null,
            resolved_episodes: 0,
            open_episodes: 0,
            is_synthetic: false,
            reason: 'Failed to load recovery trend data.',
          });
        }
      } finally {
        setLoading(false);
      }
    },
    [groupBy, window]
  );

  const groups = useMemo(() => Array.from(new Set((data?.points ?? []).map((point) => point.group))), [data]);
  const chartData = useMemo(() => {
    const byDate = new Map<string, Record<string, string | number>>();
    for (const point of data?.points ?? []) {
      const row = byDate.get(point.date) ?? { date: point.date };
      row[point.group] = point.mean_recovery_hours;
      byDate.set(point.date, row);
    }
    return Array.from(byDate.values());
  }, [data]);

  return (
    <div data-testid="quality-dashboard-chart-recovery-trend" className="rounded-lg bg-white p-6 shadow">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Mean Time to Recovery</h2>
          <p className="mt-1 text-sm text-slate-500">
            Time from the first failed execution in an episode to its first subsequent pass. This is execution time-to-green, not defect repair time.
          </p>
          {data?.mean_recovery_hours !== null && data?.mean_recovery_hours !== undefined && (
            <p className="mt-2 text-sm font-medium text-slate-700">
              Window mean: {data.mean_recovery_hours.toFixed(1)}h · {data.resolved_episodes} resolved · {data.open_episodes} open
            </p>
          )}
        </div>
        <label className="text-sm text-slate-600">
          Group by
          <select
            aria-label="Recovery grouping"
            className="ml-2 rounded-md border border-slate-300 bg-white px-2 py-1"
            value={groupBy}
            onChange={(event) => setGroupBy(event.target.value as RecoveryGroupBy)}
          >
            {GROUP_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </label>
      </div>

      {loading && !data ? (
        <div className="flex h-72 items-center justify-center"><LoadingSpinner /></div>
      ) : !data || data.points.length === 0 ? (
        <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center">
          <p className="text-sm text-slate-500">{data?.reason ?? 'No resolved recovery episodes are available yet.'}</p>
        </div>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" />
              <YAxis unit="h" />
              <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}h`, 'Mean recovery']} />
              <Legend />
              {groups.map((group) => (
                <Line key={group} type="monotone" dataKey={group} name={group} stroke="#2563eb" strokeWidth={2} connectNulls />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
