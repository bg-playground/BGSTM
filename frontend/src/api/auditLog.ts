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

export interface AuditLogFilters {
  user_id?: string;
  action?: string;
  resource_type?: string;
  date_from?: string;
  date_to?: string;
  skip?: number;
  limit?: number;
}

export const auditLogApi = {
  list: (filters: AuditLogFilters = {}) => {
    const params = new URLSearchParams();
    if (filters.user_id) params.set('user_id', filters.user_id);
    if (filters.action) params.set('action', filters.action);
    if (filters.resource_type) params.set('resource_type', filters.resource_type);
    if (filters.date_from) params.set('date_from', filters.date_from);
    if (filters.date_to) params.set('date_to', filters.date_to);
    params.set('skip', String(filters.skip ?? 0));
    params.set('limit', String(filters.limit ?? 25));
    return apiClient.get<AuditLogListResponse>(`/audit-log?${params.toString()}`);
  },
};
