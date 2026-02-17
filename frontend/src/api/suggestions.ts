import { apiClient } from './client';
import type { Suggestion, SuggestionReview, GenerateSuggestionsResponse } from '../types/api';

export const suggestionsApi = {
  list: async (): Promise<Suggestion[]> => {
    const response = await apiClient.get<Suggestion[]>('/suggestions');
    return response.data;
  },

  listPending: async (): Promise<Suggestion[]> => {
    const response = await apiClient.get<Suggestion[]>('/suggestions/pending');
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
