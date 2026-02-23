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
  list: async (filters: AuditLogFilters = {}): Promise<AuditLogListResponse> => {
    const params: Record<string, string | number> = {};
    if (filters.user_id) params.user_id = filters.user_id;
    if (filters.action) params.action = filters.action;
    if (filters.resource_type) params.resource_type = filters.resource_type;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    if (filters.skip !== undefined) params.skip = filters.skip;
    if (filters.limit !== undefined) params.limit = filters.limit;
    const response = await apiClient.get<AuditLogListResponse>('/audit-log', { params });
    return response.data;
  },
};
