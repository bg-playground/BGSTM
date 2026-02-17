import { apiClient } from './client';
import type { TestCase, TestCaseCreate, TestCaseUpdate } from '../types/api';

export const testCasesApi = {
  list: async (): Promise<TestCase[]> => {
    const response = await apiClient.get<TestCase[]>('/test-cases');
    return response.data;
  },

  get: async (id: string): Promise<TestCase> => {
    const response = await apiClient.get<TestCase>(`/test-cases/${id}`);
    return response.data;
  },

  create: async (data: TestCaseCreate): Promise<TestCase> => {
    const response = await apiClient.post<TestCase>('/test-cases', data);
    return response.data;
  },

  update: async (id: string, data: TestCaseUpdate): Promise<TestCase> => {
    const response = await apiClient.put<TestCase>(`/test-cases/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/test-cases/${id}`);
  },
};
