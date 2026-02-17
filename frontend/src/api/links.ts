import { apiClient } from './client';
import type { Link, LinkCreate } from '../types/api';

export const linksApi = {
  list: async (): Promise<Link[]> => {
    const response = await apiClient.get<Link[]>('/links');
    return response.data;
  },

  get: async (id: string): Promise<Link> => {
    const response = await apiClient.get<Link>(`/links/${id}`);
    return response.data;
  },

  create: async (data: LinkCreate): Promise<Link> => {
    const response = await apiClient.post<Link>('/links', data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/links/${id}`);
  },

  getByRequirement: async (requirementId: string): Promise<Link[]> => {
    const response = await apiClient.get<Link[]>(`/requirements/${requirementId}/links`);
    return response.data;
  },

  getByTestCase: async (testCaseId: string): Promise<Link[]> => {
    const response = await apiClient.get<Link[]>(`/test-cases/${testCaseId}/links`);
    return response.data;
  },
};
