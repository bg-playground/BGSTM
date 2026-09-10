import { useCallback, useState } from 'react';

import { isRequestCanceled } from '../../api/client';
import { qualityDigestApi, type DigestCadence } from '../../api/qualityDigest';
import type { WindowDays } from '../../api/qualityMetrics';
import { useToast } from '../../context/ToastContext';
import { useEffectAsync } from '../../hooks/useEffectAsync';

export function QualityDigestSubscription({ dashboardWindow }: { dashboardWindow: WindowDays }) {
  const { showToast } = useToast();
  const [cadence, setCadence] = useState<DigestCadence>('off');
  const [windowDays, setWindowDays] = useState<WindowDays>(dashboardWindow);
  const [saving, setSaving] = useState(false);

  useEffectAsync(async (signal) => {
    try {
      const subscription = await qualityDigestApi.getSubscription(signal);
      if (signal.aborted || !subscription) return;
      setCadence(subscription.cadence);
      setWindowDays(subscription.window_days);
    } catch (error) {
      if (!isRequestCanceled(error)) showToast('Failed to load digest preference', 'error');
    }
  }, [showToast]);

  const save = useCallback(async () => {
    try {
      setSaving(true);
      const subscription = await qualityDigestApi.saveSubscription(cadence, windowDays);
      setCadence(subscription.cadence);
      setWindowDays(subscription.window_days);
      showToast(cadence === 'off' ? 'Quality digest disabled' : 'Quality digest preference saved', 'success');
    } catch {
      showToast('Failed to save digest preference', 'error');
    } finally {
      setSaving(false);
    }
  }, [cadence, showToast, windowDays]);

  return (
    <div data-testid="quality-digest-subscription" className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Quality KPI digest</h2>
          <p className="mt-1 text-sm text-slate-500">
            Receive a scheduled in-app summary using the same audited KPI semantics as this dashboard.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="text-sm text-slate-600">
            Cadence
            <select
              value={cadence}
              onChange={(event) => setCadence(event.target.value as DigestCadence)}
              className="ml-2 rounded-md border border-slate-300 px-2 py-2"
            >
              <option value="off">Off</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </label>
          <label className="text-sm text-slate-600">
            Reporting window
            <select
              value={windowDays}
              onChange={(event) => setWindowDays(Number(event.target.value) as WindowDays)}
              className="ml-2 rounded-md border border-slate-300 px-2 py-2"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </select>
          </label>
          <span className="rounded-md bg-slate-100 px-3 py-2 text-sm text-slate-600">Channel: In-app</span>
          <button
            type="button"
            disabled={saving}
            onClick={() => void save()}
            className="rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save digest'}
          </button>
        </div>
      </div>
    </div>
  );
}
