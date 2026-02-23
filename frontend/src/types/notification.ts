export interface Notification {
  id: string;
  user_id: string;
  type: 'suggestions_generated' | 'coverage_drop' | 'suggestion_reviewed' | 'requirement_created' | 'test_case_created';
  title: string;
  message: string;
  read: boolean;
  metadata_: Record<string, unknown> | null;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  unread_count: number;
  total: number;
}
