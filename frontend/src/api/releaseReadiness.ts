import type { AxiosRequestConfig } from 'axios';

import { apiClient } from './client';
import type { WindowDays } from './qualityMetrics';

export type ReadinessStatus = 'pass' | 'fail' | 'warn' | 'na';
export type OverallStatus = 'go' | 'no_go' | 'caution';

export interface ReadinessCriterion {
  id: string;
  label: string;
  status: ReadinessStatus;
  value: string;
  threshold: string;
  category: string;
}

export interface RoleSignoff {
  role: string;
  signed_off: boolean;
  signed_off_by: string | null;
  signed_off_at: string | null;
  note: string | null;
}

export interface ReadinessSnapshot {
  overall_status: OverallStatus;
  generated_at: string;
  criteria: ReadinessCriterion[];
  signoffs: RoleSignoff[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    warning: number;
  };
}

export const releaseReadinessApi = {
  async getSnapshot(config?: AxiosRequestConfig): Promise<ReadinessSnapshot> {
    const response = await apiClient.get<ReadinessSnapshot>('/release-readiness/', config);
    return response.data;
  },

  async signoff(role: string, note?: string | null, config?: AxiosRequestConfig): Promise<ReadinessSnapshot> {
    const response = await apiClient.post<ReadinessSnapshot>('/release-readiness/signoff', { role, note: note ?? null }, config);
    return response.data;
  },

  async revoke(role: string, config?: AxiosRequestConfig): Promise<ReadinessSnapshot> {
    const response = await apiClient.delete<ReadinessSnapshot>(`/release-readiness/signoff/${role}`, config);
    return response.data;
  },

  async requestSignoff(role: string, note?: string | null, config?: AxiosRequestConfig): Promise<void> {
    await apiClient.post('/release-readiness/signoff/request', { role, note: note ?? null }, config);
  },

  async exportReport(
    format: 'md' | 'pdf',
    window?: WindowDays,
    config?: AxiosRequestConfig
  ): Promise<Blob> {
    const windowQuery = window ? `&window=${window}` : '';
    const response = await apiClient.get(`/release-readiness/export?format=${format}${windowQuery}`, {
      responseType: 'blob',
      ...config,
    });
    return response.data;
  },

  downloadExport(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
