import React, { useCallback, useEffect, useRef, useState } from 'react';
import { notificationsApi } from '../api/notifications';
import type { Notification } from '../types/notification';

const POLL_INTERVAL_MS = 30_000;

const typeIcon: Record<Notification['type'], string> = {
  suggestions_generated: '🤖',
  coverage_drop: '📉',
  suggestion_reviewed: '✅',
  requirement_created: '📋',
  test_case_created: '🧪',
};

function relativeTime(dateStr: string): string {
  const diffMs = Date.now() - new Date(dateStr).getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.floor(diffHr / 24)}d ago`;
}

export const NotificationBell: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const fetchUnreadCount = useCallback(async () => {
    try {
      const count = await notificationsApi.getUnreadCount();
      setUnreadCount(count);
    } catch {
      // silent
    }
  }, []);

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await notificationsApi.list({ limit: 20 });
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch {
      // silent
    }
  }, []);

  // Poll for unread count every 30 seconds
  useEffect(() => {
    void fetchUnreadCount();
    const interval = setInterval(() => { void fetchUnreadCount(); }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Load notifications when dropdown opens
  useEffect(() => {
    if (open) {
      void fetchNotifications();
    }
  }, [open, fetchNotifications]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleMarkAsRead = useCallback(
    async (id: string) => {
      try {
        await notificationsApi.markAsRead(id);
        setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
        setUnreadCount((c) => Math.max(0, c - 1));
      } catch {
        // silent
      }
    },
    [],
  );

  const handleMarkAllAsRead = useCallback(async () => {
    try {
      await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
      setUnreadCount(0);
    } catch {
      // silent
    }
  }, []);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative p-2 rounded-md text-gray-200 hover:bg-primary-600 hover:text-white transition-colors"
        aria-label="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50 border border-gray-200 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
            <span className="font-semibold text-gray-800 text-sm">Notifications</span>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="text-xs text-primary-600 hover:text-primary-800 font-medium"
              >
                Mark all as read
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <p className="text-center text-gray-500 text-sm py-8">No notifications</p>
            ) : (
              notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => !n.read && handleMarkAsRead(n.id)}
                  className={`w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                    n.read ? 'opacity-50' : 'bg-white'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-lg flex-shrink-0">{typeIcon[n.type]}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{n.title}</p>
                      <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">{n.message}</p>
                      <p className="text-xs text-gray-400 mt-1">{relativeTime(n.created_at)}</p>
                    </div>
                    {!n.read && <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-1" />}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
