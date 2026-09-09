import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { notificationsApi } from '../api/notifications';
import { NotificationBell } from './NotificationBell';

vi.mock('../api/notifications', async () => {
  const actual = await vi.importActual<typeof import('../api/notifications')>('../api/notifications');
  return {
    ...actual,
    notificationsApi: {
      ...actual.notificationsApi,
      getUnreadCount: vi.fn(),
      list: vi.fn(),
      markAsRead: vi.fn(),
      markAllAsRead: vi.fn(),
    },
  };
});

describe('NotificationBell request cancellation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('aborts the unread-count request when the component unmounts', async () => {
    let signal: AbortSignal | undefined;
    vi.mocked(notificationsApi.getUnreadCount).mockImplementation(async (config) => {
      signal = config?.signal;
      return await new Promise<number>(() => undefined);
    });

    const { unmount } = render(<NotificationBell />);

    await waitFor(() => expect(notificationsApi.getUnreadCount).toHaveBeenCalledTimes(1));
    expect(signal).toBeDefined();
    expect(signal?.aborted).toBe(false);

    unmount();

    expect(signal?.aborted).toBe(true);
  });

  it('aborts the dropdown loader when the dropdown closes', async () => {
    let signal: AbortSignal | undefined;
    vi.mocked(notificationsApi.getUnreadCount).mockResolvedValue(0);
    vi.mocked(notificationsApi.list).mockImplementation(async (_params, config) => {
      signal = config?.signal;
      return await new Promise(() => undefined);
    });

    render(<NotificationBell />);

    const bell = screen.getByRole('button', { name: 'Notifications' });
    fireEvent.click(bell);

    await waitFor(() => expect(notificationsApi.list).toHaveBeenCalledTimes(1));
    expect(notificationsApi.list).toHaveBeenCalledWith({ limit: 20 }, { signal: expect.any(AbortSignal) });
    expect(signal?.aborted).toBe(false);

    fireEvent.click(bell);

    await waitFor(() => expect(signal?.aborted).toBe(true));
  });

  it('passes an AbortSignal to unread-count polling', async () => {
    vi.mocked(notificationsApi.getUnreadCount).mockResolvedValue(3);

    render(<NotificationBell />);

    await waitFor(() => expect(notificationsApi.getUnreadCount).toHaveBeenCalledTimes(1));
    expect(notificationsApi.getUnreadCount).toHaveBeenCalledWith({ signal: expect.any(AbortSignal) });
    expect(await screen.findByText('3')).toBeInTheDocument();
  });
});
