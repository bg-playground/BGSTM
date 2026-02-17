import { apiClient } from './client';
import type { 
  Suggestion, 
  SuggestionReview, 
  BatchSuggestionReview,
  BatchReviewResult,
  GenerateSuggestionsResponse,
  SuggestionFilters 
} from '../types/api';

export const suggestionsApi = {
  list: async (): Promise<Suggestion[]> => {
    const response = await apiClient.get<Suggestion[]>('/suggestions');
    return response.data;
  },

  listPending: async (filters?: SuggestionFilters): Promise<Suggestion[]> => {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.min_score !== undefined) params.append('min_score', filters.min_score.toString());
      if (filters.max_score !== undefined) params.append('max_score', filters.max_score.toString());
      if (filters.algorithm) params.append('algorithm', filters.algorithm);
      if (filters.created_after) params.append('created_after', filters.created_after);
      if (filters.created_before) params.append('created_before', filters.created_before);
      if (filters.search) params.append('search', filters.search);
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.sort_order) params.append('sort_order', filters.sort_order);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.offset) params.append('offset', filters.offset.toString());
    }
    
    const response = await apiClient.get<Suggestion[]>('/suggestions/pending', { params });
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

  batchReview: async (batchReview: BatchSuggestionReview): Promise<BatchReviewResult> => {
    const response = await apiClient.post<BatchReviewResult>('/suggestions/batch-review', batchReview);
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
