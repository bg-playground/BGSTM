import { apiClient } from './client';

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: UserResponse[];
  total: number;
}

export interface UserUpdate {
  role?: 'admin' | 'reviewer' | 'viewer';
  is_active?: boolean;
  full_name?: string;
}

export const usersApi = {
  list: async (skip = 0, limit = 100): Promise<UserListResponse> => {
    const response = await apiClient.get<UserListResponse>('/users', { params: { skip, limit } });
    return response.data;
  },

  update: async (userId: string, updates: UserUpdate): Promise<UserResponse> => {
    const response = await apiClient.patch<UserResponse>(`/users/${userId}`, updates);
    return response.data;
  },

  deactivate: async (userId: string): Promise<UserResponse> => {
    const response = await apiClient.delete<UserResponse>(`/users/${userId}`);
    return response.data;
  },
};
