import { apiClient } from './client';
import type { Notification, NotificationListResponse } from '../types/notification';

type NotificationListParams = {
  unread_only?: boolean;
  limit?: number;
  offset?: number;
};

type NotificationRequestConfig = {
  signal?: AbortSignal;
};

export const notificationsApi = {
  list: async (
    params?: NotificationListParams,
    config?: NotificationRequestConfig,
  ): Promise<NotificationListResponse> => {
    const response = await apiClient.get<NotificationListResponse>('/notifications', {
      ...config,
      params,
    });
    return response.data;
  },

  getUnreadCount: async (config?: NotificationRequestConfig): Promise<number> => {
    const response = await apiClient.get<{ unread_count: number }>('/notifications/unread-count', config);
    return response.data.unread_count;
  },

  markAsRead: async (id: string): Promise<Notification> => {
    const response = await apiClient.patch<Notification>(`/notifications/${id}/read`);
    return response.data;
  },

  markAllAsRead: async (): Promise<number> => {
    const response = await apiClient.post<{ marked_read: number }>('/notifications/mark-all-read');
    return response.data.marked_read;
  },
};
