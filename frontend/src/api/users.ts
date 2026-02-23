import { apiClient } from './client';

export interface ManagedUser {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: ManagedUser[];
  total: number;
}

export interface UserUpdate {
  role?: 'admin' | 'reviewer' | 'viewer';
  is_active?: boolean;
  full_name?: string;
}

export const usersApi = {
  list: (skip = 0, limit = 100) =>
    apiClient.get<UserListResponse>(`/users?skip=${skip}&limit=${limit}`),

  update: (id: string, updates: UserUpdate) =>
    apiClient.patch<ManagedUser>(`/users/${id}`, updates),
};
