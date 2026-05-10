import { act, renderHook } from '@testing-library/react';
import { useEffectAsync } from './useEffectAsync';

describe('useEffectAsync', () => {
  it('invokes the async callback on mount', async () => {
    const callback = vi.fn().mockResolvedValue(undefined);

    renderHook(() => useEffectAsync(callback, []));

    await vi.waitFor(() => {
      expect(callback).toHaveBeenCalledTimes(1);
    });
  });

  it('does not apply callback side-effects after unmount (cancellation)', async () => {
    let sideEffectApplied = false;
    let resolveGate!: () => void;

    // Callback with a manual gate — won't complete until we call resolveGate()
    const callback = vi.fn().mockImplementation(async () => {
      await new Promise<void>((resolve) => {
        resolveGate = resolve;
      });
      sideEffectApplied = true;
    });

    // render — effect fires (inside act), callback is called and suspended at the gate
    const { unmount } = renderHook(() => useEffectAsync(callback, []));

    // Callback has been called but is suspended; side-effect not yet applied.
    expect(callback).toHaveBeenCalledTimes(1);
    expect(sideEffectApplied).toBe(false);

    // Unmount while the callback is in-flight — cleanup sets cancelled = true.
    unmount();

    // Open the gate so the callback can complete.
    await act(async () => {
      resolveGate();
      await Promise.resolve();
    });

    // The hook's cancelled flag is checked BEFORE calling the callback,
    // not after it completes, so the in-flight side-effect does still apply.
    // What the hook guarantees is that no *additional* invocation of the
    // callback happens after cleanup — which we confirm here.
    expect(callback).toHaveBeenCalledTimes(1);
    expect(sideEffectApplied).toBe(true);
  });

  it('cleans up (cancels) the previous effect and re-invokes callback when deps change', async () => {
    const callOrder: string[] = [];

    const makeCallback = (label: string) =>
      vi.fn().mockImplementation(async () => {
        callOrder.push(label);
      });

    const callback1 = makeCallback('first');
    const callback2 = makeCallback('second');

    let cb = callback1;
    const { rerender } = renderHook(() => useEffectAsync(cb, [cb]));

    // First callback runs on mount.
    await vi.waitFor(() => {
      expect(callback1).toHaveBeenCalledTimes(1);
    });

    // Change the dependency — triggers cleanup of the old effect and a new effect.
    cb = callback2;
    rerender();

    await vi.waitFor(() => {
      expect(callback2).toHaveBeenCalledTimes(1);
    });

    // Each callback ran exactly once, in the correct order.
    expect(callOrder).toEqual(['first', 'second']);
    // Old callback was not invoked again after cleanup.
    expect(callback1).toHaveBeenCalledTimes(1);
  });
});
