import { renderHook } from '@testing-library/react';
import { useEffectAsync } from './useEffectAsync';

describe('useEffectAsync', () => {
  it('invokes the async callback on mount', async () => {
    const callback = vi.fn().mockImplementation(async (signal: AbortSignal) => {
      expect(signal).toBeInstanceOf(AbortSignal);
    });

    renderHook(() => useEffectAsync(callback, []));

    await vi.waitFor(() => {
      expect(callback).toHaveBeenCalledTimes(1);
    });

    const [signal] = callback.mock.calls[0] as [AbortSignal];
    expect(signal.aborted).toBe(false);
  });

  it('aborts the callback signal on unmount cleanup', async () => {
    let capturedSignal: AbortSignal | undefined;
    const callback = vi.fn().mockImplementation(async (signal: AbortSignal) => {
      capturedSignal = signal;
    });
    const { unmount } = renderHook(() => useEffectAsync(callback, []));

    await vi.waitFor(() => {
      expect(callback).toHaveBeenCalledTimes(1);
    });

    unmount();
    expect(capturedSignal?.aborted).toBe(true);
  });

  it('cleans up (cancels) the previous effect and re-invokes callback when deps change', async () => {
    const signals: AbortSignal[] = [];
    const callback1 = vi.fn().mockImplementation(async (signal: AbortSignal) => {
      signals.push(signal);
    });
    const callback2 = vi.fn().mockImplementation(async (signal: AbortSignal) => {
      signals.push(signal);
    });

    let cb = callback1;
    const { rerender } = renderHook(() => useEffectAsync(cb, [cb]));

    await vi.waitFor(() => {
      expect(callback1).toHaveBeenCalledTimes(1);
    });

    cb = callback2;
    rerender();

    await vi.waitFor(() => {
      expect(callback2).toHaveBeenCalledTimes(1);
    });

    expect(signals[0].aborted).toBe(true);
    expect(signals[1].aborted).toBe(false);
    expect(callback1).toHaveBeenCalledTimes(1);
  });

  it('calls AbortController.abort during cleanup', async () => {
    const abortSpy = vi.spyOn(AbortController.prototype, 'abort');
    const callback = vi.fn().mockImplementation(async (signal: AbortSignal) => {
      expect(signal).toBeInstanceOf(AbortSignal);
    });
    const { unmount } = renderHook(() => useEffectAsync(callback, []));

    await vi.waitFor(() => {
      expect(callback).toHaveBeenCalledTimes(1);
    });

    unmount();
    expect(abortSpy).toHaveBeenCalledTimes(1);

    abortSpy.mockRestore();
  });
});
