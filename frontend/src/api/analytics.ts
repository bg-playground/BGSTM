import { apiClient } from './client';

export interface AcceptanceRates {
  overall: {
    total: number;
    accepted: number;
    rejected: number;
    pending: number;
    rate: number;
  };
  by_algorithm: Record<string, {
    total: number;
    accepted: number;
    rejected: number;
    pending: number;
    rate: number;
  }>;
}

export interface ConfidenceDistribution {
  buckets: Record<string, {
    accepted: number;
    rejected: number;
    pending: number;
  }>;
}

export interface GenerationTrend {
  date: string;
  total: number;
  by_algorithm: Record<string, number>;
}

export interface ReviewVelocity {
  avg_time_to_review_hours: number;
  daily_review_rate: number;
  pending_backlog: number;
}

export interface AlgorithmComparison {
  algorithm: string;
  total_suggestions: number;
  acceptance_rate: number;
  avg_confidence: number;
  accepted: number;
  rejected: number;
  pending: number;
}

export const analyticsApi = {
  getAcceptanceRates: async (days?: number): Promise<AcceptanceRates> => {
    const params = days ? `?days=${days}` : '';
    const response = await apiClient.get<AcceptanceRates>(`/analytics/acceptance-rates${params}`);
    return response.data;
  },

  getConfidenceDistribution: async (algorithm?: string): Promise<ConfidenceDistribution> => {
    const params = algorithm ? `?algorithm=${algorithm}` : '';
    const response = await apiClient.get<ConfidenceDistribution>(`/analytics/confidence-distribution${params}`);
    return response.data;
  },

  getGenerationTrends: async (days: number = 30): Promise<GenerationTrend[]> => {
    const response = await apiClient.get<GenerationTrend[]>(`/analytics/generation-trends?days=${days}`);
    return response.data;
  },

  getReviewVelocity: async (days: number = 30): Promise<ReviewVelocity> => {
    const response = await apiClient.get<ReviewVelocity>(`/analytics/review-velocity?days=${days}`);
    return response.data;
  },

  getAlgorithmComparison: async (): Promise<AlgorithmComparison[]> => {
    const response = await apiClient.get<AlgorithmComparison[]>('/analytics/algorithm-comparison');
    return response.data;
  },
};
