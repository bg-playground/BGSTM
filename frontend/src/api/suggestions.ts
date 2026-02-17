import { apiClient } from './client';
import type { Suggestion, SuggestionReview, GenerateSuggestionsResponse, SuggestionStatus } from '../types/api';

export const suggestionsApi = {
  list: async (): Promise<Suggestion[]> => {
    const response = await apiClient.get<Suggestion[]>('/suggestions');
    return response.data;
  },

  listPending: async (params?: {
    minScore?: number;
    maxScore?: number;
    algorithm?: string;
    sortBy?: string;
    sortOrder?: string;
  }): Promise<Suggestion[]> => {
    const searchParams = new URLSearchParams();
    if (params?.minScore !== undefined) searchParams.append('min_score', params.minScore.toString());
    if (params?.maxScore !== undefined) searchParams.append('max_score', params.maxScore.toString());
    if (params?.algorithm) searchParams.append('algorithm', params.algorithm);
    if (params?.sortBy) searchParams.append('sort_by', params.sortBy);
    if (params?.sortOrder) searchParams.append('sort_order', params.sortOrder);
    
    const response = await apiClient.get<Suggestion[]>(`/suggestions/pending?${searchParams}`);
    return response.data;
  },

  get: async (id: string): Promise<Suggestion> => {
    const response = await apiClient.get<Suggestion>(`/suggestions/${id}`);
    return response.data;
  },

  review: async (id: string, review: SuggestionReview): Promise<Suggestion> => {
    const response = await apiClient.post<Suggestion>(`/suggestions/${id}/review`, review);
    return response.data;
  },

  bulkReview: async (ids: string[], status: SuggestionStatus, feedback?: string): Promise<{ message: string; count: number; status: SuggestionStatus }> => {
    const response = await apiClient.post<{ message: string; count: number; status: SuggestionStatus }>('/suggestions/bulk-review', {
      suggestion_ids: ids,
      status,
      feedback
    });
    return response.data;
  },

  generate: async (algorithm?: string, threshold?: number): Promise<GenerateSuggestionsResponse> => {
    const params = new URLSearchParams();
    if (algorithm) params.append('algorithm', algorithm);
    if (threshold !== undefined) params.append('threshold', threshold.toString());
    
    const response = await apiClient.post<GenerateSuggestionsResponse>(
      '/suggestions/generate',
      null,
      { params }
    );
    return response.data;
  },
};
