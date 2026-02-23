import { apiClient } from './client';

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  user_email: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  details: Record<string, unknown> | null;
}

export interface AuditLogParams {
  page?: number;
  page_size?: number;
  from_date?: string;
  to_date?: string;
  action?: string;
  user_email?: string;
  entity_type?: string;
}

export interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  pages: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export const adminApi = {
  getAuditLog: async (params: AuditLogParams = {}): Promise<AuditLogResponse> => {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    if (params.from_date) searchParams.append('from_date', params.from_date);
    if (params.to_date) searchParams.append('to_date', params.to_date);
    if (params.action) searchParams.append('action', params.action);
    if (params.user_email) searchParams.append('user_email', params.user_email);
    if (params.entity_type) searchParams.append('entity_type', params.entity_type);
    const response = await apiClient.get<AuditLogResponse>(`/audit-log?${searchParams}`);
    return response.data;
  },

  getUsers: async (): Promise<AdminUser[]> => {
    const response = await apiClient.get<AdminUser[]>('/users');
    return response.data;
  },

  updateUserRole: async (userId: string, role: AdminUser['role']): Promise<AdminUser> => {
    const response = await apiClient.put<AdminUser>(`/users/${userId}/role`, { role });
    return response.data;
  },

  deleteUser: async (userId: string): Promise<void> => {
    await apiClient.delete(`/users/${userId}`);
  },
};
