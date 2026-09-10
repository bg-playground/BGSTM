import { apiClient } from './client';
import type { WindowDays } from './qualityMetrics';

export type DigestCadence = 'off' | 'daily' | 'weekly';
export type DigestChannel = 'in_app';

export interface DigestSubscription {
  id: string;
  user_id: string;
  channel: DigestChannel;
  cadence: DigestCadence;
  window_days: WindowDays;
  last_delivered_at: string | null;
  next_delivery_at: string | null;
  created_at: string;
  updated_at: string;
}

export const qualityDigestApi = {
  getSubscription: async (signal?: AbortSignal): Promise<DigestSubscription | null> => {
    const response = await apiClient.get<DigestSubscription | null>('/quality-digest/subscription', { signal });
    return response.data;
  },
  saveSubscription: async (
    cadence: DigestCadence,
    windowDays: WindowDays,
  ): Promise<DigestSubscription> => {
    const response = await apiClient.put<DigestSubscription>('/quality-digest/subscription', {
      cadence,
      window_days: windowDays,
      channel: 'in_app',
    });
    return response.data;
  },
};
