import { useState } from 'react';
import {
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { isRequestCanceled } from '../../api/client';
import {
  qualityMetricsApi,
  type ModuleCoverageFailurePoint,
  type ModuleCoverageFailureResponse,
  type WindowDays,
} from '../../api/qualityMetrics';
import { useEffectAsync } from '../../hooks/useEffectAsync';
import { LoadingSpinner } from '../LoadingSpinner';

function ModuleRiskTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload?: unknown }> }) {
  if (!active || !payload?.length) return null;
  const point = payload[0]?.payload as ModuleCoverageFailurePoint | undefined;
  if (!point) return null;

  return (
    <div className="rounded-md border border-slate-200 bg-white p-3 text-xs shadow-lg">
      <p className="mb-2 font-semibold text-slate-900">{point.module}</p>
      <p>Requirement coverage: {point.coverage_pct.toFixed(1)}%</p>
      <p>Failure density: {point.failure_density_pct.toFixed(1)}%</p>
      <p>Covered requirements: {point.covered_requirements}/{point.total_requirements}</p>
      <p>Failed executions: {point.total_failures}/{point.total_executions}</p>
    </div>
  );
}

export function CoverageFailureDensityPanel({ window }: { window: WindowDays }) {
  const [data, setData] = useState<ModuleCoverageFailureResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffectAsync(async (signal) => {
    try {
      setLoading(true);
      setError(null);
      const response = await qualityMetricsApi.getCoverageVsDefects(window, { signal });
      if (signal.aborted) return;
      setData(response);
    } catch (requestError) {
      if (isRequestCanceled(requestError)) return;
      setError('Unable to load module coverage and failure-density data.');
    } finally {
      setLoading(false);
    }
  }, [window]);

  return (
    <section data-testid="quality-dashboard-chart-coverage-vs-defects" className="rounded-lg bg-white p-6 shadow">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-slate-900">Coverage vs Failure Density</h2>
        <p className="mt-1 text-sm text-slate-500">
          Requirement traceability coverage versus failed executions as a percentage of executions in the selected window.
          The upper-left quadrant is the relative investigation priority.
        </p>
      </div>

      {loading ? (
        <div className="flex h-80 items-center justify-center"><LoadingSpinner /></div>
      ) : error ? (
        <div className="flex h-80 items-center justify-center text-sm text-rose-600">{error}</div>
      ) : !data || data.points.length === 0 ? (
        <div className="flex h-80 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 px-6 text-center">
          <div className="space-y-2">
            <p className="text-sm font-semibold text-slate-700">Coverage vs Failure Density</p>
            <p className="text-sm text-slate-500">{data?.reason ?? 'Add requirements with module assignments to populate this analysis.'}</p>
          </div>
        </div>
      ) : (
        <>
          {data.reason ? <p className="mb-3 text-xs text-slate-500">{data.reason}</p> : null}
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis
                  type="number"
                  dataKey="coverage_pct"
                  name="Requirement coverage"
                  unit="%"
                  domain={[0, 100]}
                  label={{ value: 'Requirement coverage %', position: 'insideBottom', offset: -10 }}
                />
                <YAxis
                  type="number"
                  dataKey="failure_density_pct"
                  name="Failure density"
                  unit="%"
                  domain={[0, 100]}
                  label={{ value: 'Failure density %', angle: -90, position: 'insideLeft' }}
                />
                {data.median_coverage_pct !== null ? (
                  <ReferenceLine x={data.median_coverage_pct} stroke="#64748b" strokeDasharray="5 5" />
                ) : null}
                {data.median_failure_density_pct !== null ? (
                  <ReferenceLine y={data.median_failure_density_pct} stroke="#64748b" strokeDasharray="5 5" />
                ) : null}
                <Tooltip content={<ModuleRiskTooltip />} />
                <Scatter name="Modules" data={data.points} fill="#2563eb" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            Dashed guides are medians for the modules shown; they support relative prioritization and are not release thresholds.
          </p>
        </>
      )}
    </section>
  );
}
