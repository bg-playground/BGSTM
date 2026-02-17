import { apiClient } from './client';
import type { Requirement, RequirementCreate, RequirementUpdate } from '../types/api';

export const requirementsApi = {
  list: async (): Promise<Requirement[]> => {
    const response = await apiClient.get<Requirement[]>('/requirements');
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
