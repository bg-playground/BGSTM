import { apiClient } from './client';

export interface UserRecord {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: UserRecord[];
  total: number;
}

export interface UserUpdate {
  role?: 'admin' | 'reviewer' | 'viewer';
  is_active?: boolean;
  full_name?: string;
}

export const usersApi = {
  list: async (): Promise<UserListResponse> => {
    const response = await apiClient.get<UserListResponse>('/users');
    return response.data;
  },

  update: async (userId: string, data: UserUpdate): Promise<UserRecord> => {
    const response = await apiClient.patch<UserRecord>(`/users/${userId}`, data);
    return response.data;
  },
};
