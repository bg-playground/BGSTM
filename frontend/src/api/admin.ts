import { apiClient } from './client';

export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
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

export const adminApi = {
  fetchAuditLog: async (params?: {
    userId?: string;
    action?: string;
    resourceType?: string;
    dateFrom?: string;
    dateTo?: string;
    skip?: number;
    limit?: number;
  }): Promise<AuditLogListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.userId) searchParams.append('user_id', params.userId);
    if (params?.action) searchParams.append('action', params.action);
    if (params?.resourceType) searchParams.append('resource_type', params.resourceType);
    if (params?.dateFrom) searchParams.append('date_from', params.dateFrom);
    if (params?.dateTo) searchParams.append('date_to', params.dateTo);
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());
    const response = await apiClient.get<AuditLogListResponse>(
      `/audit-log${searchParams.toString() ? `?${searchParams}` : ''}`
    );
    return response.data;
  },

  fetchUsers: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<UserListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());
    const response = await apiClient.get<UserListResponse>(
      `/users${searchParams.toString() ? `?${searchParams}` : ''}`
    );
    return response.data;
  },

  updateUserRole: async (userId: string, role: 'admin' | 'reviewer' | 'viewer'): Promise<AdminUser> => {
    const response = await apiClient.patch<AdminUser>(`/users/${userId}`, { role });
    return response.data;
  },

  deactivateUser: async (userId: string): Promise<AdminUser> => {
    const response = await apiClient.delete<AdminUser>(`/users/${userId}`);
    return response.data;
  },
};
