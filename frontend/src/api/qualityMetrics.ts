import type { AxiosRequestConfig } from 'axios';

import { apiClient } from './client';

export type WindowDays = 7 | 30 | 90;
export type RecoveryGroupBy = 'overall' | 'module' | 'severity';

export interface SeverityMix {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface DefectTrendPoint {
  date: string;
  total: number;
  by_severity: SeverityMix;
}

export interface DefectTrendResponse {
  points: DefectTrendPoint[];
  is_synthetic: boolean;
  reason: string | null;
}

export interface PassRateTrendPoint {
  date: string;
  pass_rate_pct: number;
  total_executed: number;
}

export interface PassRateTrendResponse {
  points: PassRateTrendPoint[];
  is_synthetic: boolean;
  reason: string | null;
}

export interface ModuleQualityBucket {
  module: string;
  count: number;
  severity_mix: SeverityMix;
}

export interface DefectsByModuleResponse {
  modules: ModuleQualityBucket[];
  is_synthetic: boolean;
  reason: string | null;
}

export interface ModuleCoverageFailurePoint {
  module: string;
  coverage_pct: number;
  failure_density_pct: number;
  total_requirements: number;
  covered_requirements: number;
  total_executions: number;
  total_failures: number;
}

export interface ModuleCoverageFailureResponse {
  points: ModuleCoverageFailurePoint[];
  median_coverage_pct: number | null;
  median_failure_density_pct: number | null;
  is_synthetic: boolean;
  reason: string | null;
}

export interface RecoveryTrendPoint {
  date: string;
  group: string;
  mean_recovery_hours: number;
  resolved_episodes: number;
}

export interface RecoveryTrendResponse {
  window_days: WindowDays;
  group_by: RecoveryGroupBy;
  points: RecoveryTrendPoint[];
  mean_recovery_hours: number | null;
  resolved_episodes: number;
  open_episodes: number;
  is_synthetic: boolean;
  reason: string | null;
}

export interface RecurringDefectEntry {
  test_case_id: string | null;
  external_id: string | null;
  display_name: string;
  module: string;
  failure_count: number;
  cumulative_pct: number;
  latest_failure_session_id: string;
  latest_failure_at: string;
}

export interface RecurringDefectsParetoResponse {
  entries: RecurringDefectEntry[];
  total_recurring_failures: number;
  is_synthetic: boolean;
  reason: string | null;
}

export interface FlakyTestEntry {
  test_case_id: string | null;
  external_id: string | null;
  display_name: string;
  runs: number;
  flaky_outcomes: number;
  transitions: number;
  flip_rate: number;
  last_outcome: string;
  last_seen_at: string;
}

export interface FlakyRankingResponse {
  entries: FlakyTestEntry[];
  is_synthetic: boolean;
  reason: string | null;
}

export interface AutomationCoverageResponse {
  total: number;
  automated: number;
  manual: number;
  in_progress: number;
  percent_automated: number;
  reason: string | null;
}

export interface SummaryStatsResponse {
  defect_removal_efficiency_pct: number | null;
  defect_removal_efficiency_reason: string | null;
  mean_time_to_repair_hours: number | null;
  mean_time_to_repair_hours_reason: string | null;
  escape_rate_pct: number | null;
  escape_rate_pct_reason: string | null;
  total_defects_30d: number;
  open_critical_defects: number;
}

export interface QualityDashboardSnapshot {
  generated_at: string;
  window_days: WindowDays;
  defect_trend: DefectTrendResponse;
  pass_rate_trend: PassRateTrendResponse;
  defects_by_module: DefectsByModuleResponse;
  automation_coverage: AutomationCoverageResponse;
  summary_stats: SummaryStatsResponse;
}

export const qualityMetricsApi = {
  async getSnapshot(config?: AxiosRequestConfig): Promise<QualityDashboardSnapshot> {
    const response = await apiClient.get<QualityDashboardSnapshot>('/quality-metrics/', config);
    return response.data;
  },

  async getDefectTrend(window: WindowDays, config?: AxiosRequestConfig): Promise<DefectTrendResponse> {
    const response = await apiClient.get<DefectTrendResponse>(`/quality-metrics/defect-trend?window=${window}`, config);
    return response.data;
  },

  async getPassRateTrend(window: WindowDays, config?: AxiosRequestConfig): Promise<PassRateTrendResponse> {
    const response = await apiClient.get<PassRateTrendResponse>(
      `/quality-metrics/pass-rate-trend?window=${window}`,
      config
    );
    return response.data;
  },

  async getDefectsByModule(
    window: WindowDays,
    topN = 10,
    config?: AxiosRequestConfig
  ): Promise<DefectsByModuleResponse> {
    const response = await apiClient.get<DefectsByModuleResponse>(
      `/quality-metrics/defects-by-module?window=${window}&top_n=${topN}`,
      config
    );
    return response.data;
  },

  async getCoverageVsDefects(
    window: WindowDays,
    config?: AxiosRequestConfig
  ): Promise<ModuleCoverageFailureResponse> {
    const response = await apiClient.get<ModuleCoverageFailureResponse>(
      `/quality-metrics/coverage-vs-defects?window=${window}`,
      config
    );
    return response.data;
  },

  async getRecoveryTrend(
    window: WindowDays,
    groupBy: RecoveryGroupBy = 'overall',
    config?: AxiosRequestConfig
  ): Promise<RecoveryTrendResponse> {
    const response = await apiClient.get<RecoveryTrendResponse>(
      `/quality-metrics/recovery-trend?window=${window}&group_by=${groupBy}`,
      config
    );
    return response.data;
  },

  async getRecurringDefectsPareto(
    window: WindowDays,
    topN = 10,
    config?: AxiosRequestConfig
  ): Promise<RecurringDefectsParetoResponse> {
    const response = await apiClient.get<RecurringDefectsParetoResponse>(
      `/quality-metrics/recurring-defects?window=${window}&top_n=${topN}`,
      config
    );
    return response.data;
  },

  async getFlakyRanking(
    window: WindowDays,
    topN = 10,
    config?: AxiosRequestConfig
  ): Promise<FlakyRankingResponse> {
    const response = await apiClient.get<FlakyRankingResponse>(
      `/quality-metrics/flaky-ranking?window=${window}&top_n=${topN}`,
      config
    );
    return response.data;
  },
};
