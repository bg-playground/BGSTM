import { apiClient } from './client';
import type { Suggestion, SuggestionReview, GenerateSuggestionsResponse, SuggestionStatus, PaginatedResponse } from '../types/api';

export const suggestionsApi = {
  list: async (page = 1, pageSize = 50): Promise<PaginatedResponse<Suggestion>> => {
    const response = await apiClient.get<PaginatedResponse<Suggestion>>(
      `/suggestions?page=${page}&page_size=${pageSize}`
    );
    return response.data;
  },

  listPending: async (params?: {
    minScore?: number;
    maxScore?: number;
    algorithm?: string;
    sortBy?: string;
    sortOrder?: string;
    search?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Suggestion>> => {
    const searchParams = new URLSearchParams();
    if (params?.minScore !== undefined) searchParams.append('min_score', params.minScore.toString());
    if (params?.maxScore !== undefined) searchParams.append('max_score', params.maxScore.toString());
    if (params?.algorithm) searchParams.append('algorithm', params.algorithm);
    if (params?.sortBy) searchParams.append('sort_by', params.sortBy);
    if (params?.sortOrder) searchParams.append('sort_order', params.sortOrder);
    if (params?.search) searchParams.append('search', params.search);
    searchParams.append('page', (params?.page ?? 1).toString());
    searchParams.append('page_size', (params?.pageSize ?? 50).toString());
    
    const response = await apiClient.get<PaginatedResponse<Suggestion>>(`/suggestions/pending?${searchParams}`);
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

  exportCsv: async (params?: {
    status?: string;
    algorithm?: string;
    minScore?: number;
    maxScore?: number;
  }): Promise<Blob> => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append('status', params.status);
    if (params?.algorithm) searchParams.append('algorithm', params.algorithm);
    if (params?.minScore !== undefined) searchParams.append('min_score', params.minScore.toString());
    if (params?.maxScore !== undefined) searchParams.append('max_score', params.maxScore.toString());
    const query = searchParams.toString();
    const response = await apiClient.get(`/suggestions/export/csv${query ? `?${query}` : ''}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
