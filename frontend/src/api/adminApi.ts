import { apiClient } from './client';

export interface AuditLogEntry {
  id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface AuditLogListResponse {
  entries: AuditLogEntry[];
  total: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: AdminUser[];
  total: number;
}

export interface UserUpdatePayload {
  role?: 'admin' | 'reviewer' | 'viewer';
  is_active?: boolean;
  full_name?: string;
}

export interface AuditLogFilters {
  skip?: number;
  limit?: number;
  user_id?: string;
  action?: string;
  resource_type?: string;
  date_from?: string;
  date_to?: string;
}

export const adminApi = {
  getAuditLogs: (filters: AuditLogFilters = {}) =>
    apiClient.get<AuditLogListResponse>('/audit-log', { params: filters }),

  getUsers: (skip = 0, limit = 100) =>
    apiClient.get<UserListResponse>('/users', { params: { skip, limit } }),

  updateUser: (userId: string, payload: UserUpdatePayload) =>
    apiClient.patch<AdminUser>(`/users/${userId}`, payload),
};
