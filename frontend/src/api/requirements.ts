import { apiClient } from './client';
import type { Requirement, RequirementCreate, RequirementUpdate, PaginatedResponse } from '../types/api';

export const requirementsApi = {
  list: async (page = 1, pageSize = 50): Promise<PaginatedResponse<Requirement>> => {
    const response = await apiClient.get<PaginatedResponse<Requirement>>(
      `/requirements?page=${page}&page_size=${pageSize}`
    );
    return response.data;
  },

  get: async (id: string): Promise<Requirement> => {
    const response = await apiClient.get<Requirement>(`/requirements/${id}`);
    return response.data;
  },

  create: async (data: RequirementCreate): Promise<Requirement> => {
    const response = await apiClient.post<Requirement>('/requirements', data);
    return response.data;
  },

  update: async (id: string, data: RequirementUpdate): Promise<Requirement> => {
    const response = await apiClient.put<Requirement>(`/requirements/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/requirements/${id}`);
  },
};
