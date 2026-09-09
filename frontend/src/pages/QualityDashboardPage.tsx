import { useCallback, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { isRequestCanceled } from '../api/client';
import {
  qualityMetricsApi,
  type AutomationCoverageResponse,
  type DefectTrendResponse,
  type DefectsByModuleResponse,
  type PassRateTrendResponse,
  type QualityDashboardSnapshot,
  type WindowDays,
} from '../api/qualityMetrics';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { FlakyRankingPanel } from '../components/quality/FlakyRankingPanel';
import { useToast } from '../context/ToastContext';
import { useEffectAsync } from '../hooks/useEffectAsync';

const WINDOW_OPTIONS: WindowDays[] = [7, 30, 90];
const STORAGE_KEY = 'bgstm-quality-dashboard-filters';
const DEFAULT_FILTERS = { window: 30 } as const satisfies QualityDashboardFilters;

const SEVERITY_COLORS = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#d97706',
  low: '#2563eb',
} as const;

const AUTOMATION_COLORS = ['#2563eb', '#64748b', '#f59e0b'];

type DeltaTone = 'up' | 'down' | 'flat';

interface QualityDashboardFilters {
  window: WindowDays;
}

interface DeltaIndicator {
  symbol: '▲' | '▼' | '●';
  label: string;
  tone: DeltaTone;
}

function formatPercent(value: number | null): string {
  return value === null ? '—' : `${value.toFixed(1)}%`;
}

function formatHours(value: number | null): string {
  return value === null ? '—' : `${value.toFixed(1)}h`;
}

function formatInteger(value: number): string {
  return value.toLocaleString();
}

function getDeltaClass(tone: DeltaTone): string {
  if (tone === 'up') return 'text-emerald-600';
  if (tone === 'down') return 'text-rose-600';
  return 'text-slate-500';
}

function isWindowDays(value: unknown): value is WindowDays {
  return typeof value === 'number' && WINDOW_OPTIONS.includes(value as WindowDays);
}

function parseWindowParam(value: string | null): WindowDays | null {
  if (value === '7') return 7;
  if (value === '30') return 30;
  if (value === '90') return 90;
  return null;
}

function readFromStorage(): Partial<QualityDashboardFilters> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as Partial<QualityDashboardFilters>;
  } catch {
    return {};
  }
}

function writeToStorage(filters: QualityDashboardFilters): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  } catch {
    // Ignore (e.g. private browsing)
  }
}

function clearStorage(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore (e.g. private browsing)
  }
}

function parseFiltersFromParams(
  params: URLSearchParams,
  stored: Partial<QualityDashboardFilters>
): QualityDashboardFilters {
  const parsedWindow = parseWindowParam(params.get('window'));

  return {
    window: isWindowDays(parsedWindow) ? parsedWindow : (isWindowDays(stored.window) ? stored.window : DEFAULT_FILTERS.window),
  };
}

function calculateHalfWindowDelta(
  values: number[],
  formatter: (value: number) => string
): DeltaIndicator | null {
  if (values.length < 2) {
    return null;
  }

  const midpoint = Math.floor(values.length / 2);
  const firstHalf = values.slice(0, midpoint);
  const secondHalf = values.slice(midpoint);
  const firstValue = firstHalf.reduce((sum, value) => sum + value, 0);
  const secondValue = secondHalf.reduce((sum, value) => sum + value, 0);
  const delta = Number((secondValue - firstValue).toFixed(1));

  if (delta === 0) {
    return { symbol: '●', label: 'stable', tone: 'flat' };
  }

  return {
    symbol: delta > 0 ? '▲' : '▼',
    label: formatter(Math.abs(delta)),
    tone: delta > 0 ? 'up' : 'down',
  };
}

function EmptyChartState({ title, reason }: { title: string; reason: string | null | undefined }) {
  return (
    <div className="flex h-72 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center">
      <div className="space-y-2">
        <p className="text-sm font-semibold text-slate-700">{title}</p>
        <p className="text-sm text-slate-500">{reason ?? 'No data available for this chart yet.'}</p>
      </div>
    </div>
  );
}

function SummaryTile({
  testId,
  label,
  value,
  reason,
  delta,
}: {
  testId: string;
  label: string;
  value: string;
  reason?: string | null;
  delta?: DeltaIndicator | null;
}) {
  return (
    <div data-testid={testId} className="rounded-lg bg-white p-4 shadow">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
      {reason ? (
        <p className="mt-2 text-xs text-slate-500">{reason}</p>
      ) : delta ? (
        <p className={`mt-2 text-xs font-medium ${getDeltaClass(delta.tone)}`}>
          {delta.symbol} {delta.label}
        </p>
      ) : (
        <p className="mt-2 text-xs text-slate-400">Delta unavailable</p>
      )}
    </div>
  );
}

export default function QualityDashboardPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { showToast } = useToast();
  const [snapshot, setSnapshot] = useState<QualityDashboardSnapshot | null>(null);
  const [filters, setFilters] = useState<QualityDashboardFilters>(() =>
    parseFiltersFromParams(searchParams, readFromStorage())
  );
  const [defectTrend, setDefectTrend] = useState<DefectTrendResponse | null>(null);
  const [passRateTrend, setPassRateTrend] = useState<PassRateTrendResponse | null>(null);
  const [defectsByModule, setDefectsByModule] = useState<DefectsByModuleResponse | null>(null);
  const [automationCoverage, setAutomationCoverage] = useState<AutomationCoverageResponse | null>(null);
  const [loadingSnapshot, setLoadingSnapshot] = useState(true);
  const [loadingCharts, setLoadingCharts] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const refreshControllerRef = useRef<AbortController | null>(null);

  const syncFiltersToUrl = useCallback(
    (nextFilters: QualityDashboardFilters) => {
      const params = new URLSearchParams();
      if (nextFilters.window !== DEFAULT_FILTERS.window) {
        params.set('window', nextFilters.window.toString());
      }
      setSearchParams(params, { replace: true });
    },
    [setSearchParams]
  );

  const handleFiltersChange = useCallback(
    (nextFilters: QualityDashboardFilters) => {
      setFilters(nextFilters);
      clearStorage();
      writeToStorage(nextFilters);
      syncFiltersToUrl(nextFilters);
    },
    [syncFiltersToUrl]
  );

  const handleWindowChange = useCallback(
    (window: WindowDays) => {
      handleFiltersChange({ ...filters, window });
    },
    [filters, handleFiltersChange]
  );

  const loadSnapshot = useCallback(async (signal?: AbortSignal) => {
    try {
      setLoadingSnapshot(true);
      const data = await qualityMetricsApi.getSnapshot({ signal });
      setSnapshot(data);
      setAutomationCoverage(data.automation_coverage);
      setUpdatedAt(new Date().toISOString());
      if (filters.window === 30) {
        setDefectTrend(data.defect_trend);
        setPassRateTrend(data.pass_rate_trend);
        setDefectsByModule(data.defects_by_module);
      }
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to load quality dashboard', 'error');
    } finally {
      setLoadingSnapshot(false);
    }
  }, [filters.window, showToast]);

  useEffectAsync(async (signal) => {
    await loadSnapshot(signal);
  }, [loadSnapshot]);

  useEffectAsync(async (signal) => {
    if (!snapshot) {
      return;
    }

    if (filters.window === 30) {
      setDefectTrend(snapshot.defect_trend);
      setPassRateTrend(snapshot.pass_rate_trend);
      setDefectsByModule(snapshot.defects_by_module);
      return;
    }

    try {
      setLoadingCharts(true);
      const [nextDefectTrend, nextPassRateTrend, nextDefectsByModule] = await Promise.all([
        qualityMetricsApi.getDefectTrend(filters.window, { signal }),
        qualityMetricsApi.getPassRateTrend(filters.window, { signal }),
        qualityMetricsApi.getDefectsByModule(filters.window, 10, { signal }),
      ]);
      if (signal.aborted) return;
      setDefectTrend(nextDefectTrend);
      setPassRateTrend(nextPassRateTrend);
      setDefectsByModule(nextDefectsByModule);
      setUpdatedAt(new Date().toISOString());
    } catch (error) {
      if (isRequestCanceled(error)) return;
      showToast('Failed to load chart data', 'error');
    } finally {
      setLoadingCharts(false);
    }
  }, [filters.window, snapshot, showToast]);

  const handleRefresh = useCallback(() => {
    refreshControllerRef.current?.abort();
    const controller = new AbortController();
    refreshControllerRef.current = controller;
    void loadSnapshot(controller.signal);
  }, [loadSnapshot]);

  const defectTrendChartData = useMemo(
    () =>
      (defectTrend?.points ?? []).map((point) => ({
        date: point.date,
        total: point.total,
        critical: point.by_severity.critical,
        high: point.by_severity.high,
        medium: point.by_severity.medium,
        low: point.by_severity.low,
      })),
    [defectTrend]
  );

  const passRateChartData = useMemo(
    () =>
      (passRateTrend?.points ?? []).map((point) => ({
        date: point.date,
        pass_rate_pct: point.pass_rate_pct,
        total_executed: point.total_executed,
      })),
    [passRateTrend]
  );

  const defectsByModuleChartData = useMemo(
    () =>
      (defectsByModule?.modules ?? []).map((bucket) => ({
        module: bucket.module,
        critical: bucket.severity_mix.critical,
        high: bucket.severity_mix.high,
        medium: bucket.severity_mix.medium,
        low: bucket.severity_mix.low,
      })),
    [defectsByModule]
  );

  const automationCoverageChartData = useMemo(
    () =>
      automationCoverage
        ? [
            { name: 'Automated', value: automationCoverage.automated },
            { name: 'Manual', value: automationCoverage.manual },
            { name: 'In Progress', value: automationCoverage.in_progress },
          ]
        : [],
    [automationCoverage]
  );

  const tileDeltas = useMemo(() => {
    const defectValues = (snapshot?.defect_trend.points ?? []).map((point) => point.total);
    const criticalValues = (snapshot?.defect_trend.points ?? []).map((point) => point.by_severity.critical);

    return {
      totalDefects: calculateHalfWindowDelta(defectValues, (value) => formatInteger(Math.round(value))),
      openCritical: calculateHalfWindowDelta(criticalValues, (value) => formatInteger(Math.round(value))),
    };
  }, [snapshot]);

  if (loadingSnapshot && !snapshot) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!snapshot || !automationCoverage) {
    return (
      <div className="py-12 text-center">
        <p className="text-slate-500">No quality dashboard data available.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 px-4 py-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-slate-900">Quality KPI Dashboard</h1>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <Link to="/release-readiness" className="text-blue-600 hover:text-blue-800">
              ← Back to Release Readiness
            </Link>
            <a
              href="https://github.com/bg-playground/BGSTM/blob/main/docs/features/quality-kpi-dashboard.md"
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 hover:text-blue-800"
            >
              What is this?
            </a>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
            {WINDOW_OPTIONS.map((windowOption) => (
              <button
                key={windowOption}
                data-testid={`quality-dashboard-window-${windowOption}`}
                onClick={() => handleWindowChange(windowOption)}
                className={`rounded-md px-3 py-2 text-sm font-medium ${
                  filters.window === windowOption
                    ? 'bg-slate-900 text-white'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                {windowOption}d
              </button>
            ))}
          </div>
          <button
            onClick={handleRefresh}
            className="rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Refresh
          </button>
          <p className="text-sm text-slate-500">
            Last updated:{' '}
            {updatedAt ? new Date(updatedAt).toLocaleString() : new Date(snapshot.generated_at).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <SummaryTile
          testId="quality-dashboard-tile-defect_removal_efficiency"
          label="Defect Removal Efficiency"
          value={formatPercent(snapshot.summary_stats.defect_removal_efficiency_pct)}
          reason={snapshot.summary_stats.defect_removal_efficiency_reason}
        />
        <SummaryTile
          testId="quality-dashboard-tile-mttr"
          label="MTTR"
          value={formatHours(snapshot.summary_stats.mean_time_to_repair_hours)}
          reason={snapshot.summary_stats.mean_time_to_repair_hours_reason}
        />
        <SummaryTile
          testId="quality-dashboard-tile-escape_rate"
          label="Escape Rate"
          value={formatPercent(snapshot.summary_stats.escape_rate_pct)}
          reason={snapshot.summary_stats.escape_rate_pct_reason}
        />
        <SummaryTile
          testId="quality-dashboard-tile-open_critical_defects"
          label="Open Critical Defects"
          value={formatInteger(snapshot.summary_stats.open_critical_defects)}
          delta={tileDeltas.openCritical}
        />
        <SummaryTile
          testId="quality-dashboard-tile-total_defects_30d"
          label="Total Defects (30d)"
          value={formatInteger(snapshot.summary_stats.total_defects_30d)}
          delta={tileDeltas.totalDefects}
        />
        <SummaryTile
          testId="quality-dashboard-tile-automation_coverage"
          label="% Automation Coverage"
          value={formatPercent(automationCoverage.percent_automated)}
          reason={automationCoverage.reason}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div data-testid="quality-dashboard-chart-defect-trend" className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">Defect Trend</h2>
          {loadingCharts && filters.window !== 30 ? (
            <div className="flex h-72 items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : defectTrend?.is_synthetic ? (
            <EmptyChartState title="Defect Trend" reason={defectTrend.reason} />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={defectTrendChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Area type="monotone" dataKey="critical" stackId="1" stroke={SEVERITY_COLORS.critical} fill={SEVERITY_COLORS.critical} />
                  <Area type="monotone" dataKey="high" stackId="1" stroke={SEVERITY_COLORS.high} fill={SEVERITY_COLORS.high} />
                  <Area type="monotone" dataKey="medium" stackId="1" stroke={SEVERITY_COLORS.medium} fill={SEVERITY_COLORS.medium} />
                  <Area type="monotone" dataKey="low" stackId="1" stroke={SEVERITY_COLORS.low} fill={SEVERITY_COLORS.low} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div data-testid="quality-dashboard-chart-pass-rate" className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">Pass Rate Over Time</h2>
          {loadingCharts && filters.window !== 30 ? (
            <div className="flex h-72 items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : passRateTrend?.is_synthetic ? (
            <EmptyChartState title="Pass Rate Over Time" reason={passRateTrend.reason} />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={passRateChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" domain={[0, 100]} />
                  <YAxis yAxisId="right" orientation="right" allowDecimals={false} />
                  <Tooltip />
                  <Legend />
                  <Area yAxisId="right" type="monotone" dataKey="total_executed" fill="#cbd5e1" stroke="#94a3b8" fillOpacity={0.35} />
                  <Line yAxisId="left" type="monotone" dataKey="pass_rate_pct" stroke="#2563eb" strokeWidth={3} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div data-testid="quality-dashboard-chart-defects-by-module" className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">Defects by Module</h2>
          {loadingCharts && filters.window !== 30 ? (
            <div className="flex h-72 items-center justify-center">
              <LoadingSpinner />
            </div>
          ) : !defectsByModule || defectsByModule.modules.length === 0 ? (
            <EmptyChartState title="Defects by Module" reason={defectsByModule?.reason} />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={defectsByModuleChartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="module" width={110} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="critical" stackId="severity" fill={SEVERITY_COLORS.critical} />
                  <Bar dataKey="high" stackId="severity" fill={SEVERITY_COLORS.high} />
                  <Bar dataKey="medium" stackId="severity" fill={SEVERITY_COLORS.medium} />
                  <Bar dataKey="low" stackId="severity" fill={SEVERITY_COLORS.low} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div data-testid="quality-dashboard-chart-automation-coverage" className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold text-slate-900">Automation Coverage</h2>
          {automationCoverage.total === 0 ? (
            <EmptyChartState title="Automation Coverage" reason={automationCoverage.reason} />
          ) : (
            <div className="relative h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={automationCoverageChartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={2}
                  >
                    {automationCoverageChartData.map((entry, index) => (
                      <Cell key={entry.name} fill={AUTOMATION_COLORS[index % AUTOMATION_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <p className="text-3xl font-bold text-slate-900">{automationCoverage.percent_automated.toFixed(1)}%</p>
                <p className="text-sm text-slate-500">automated</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <FlakyRankingPanel window={filters.window} />
    </div>
  );
}
