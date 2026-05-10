import { useEffect } from 'react';

export function useEffectAsync(
  callback: (signal: AbortSignal) => Promise<void>,
  deps: React.DependencyList
): void {
  useEffect(() => {
    const controller = new AbortController();
    void callback(controller.signal);
    return () => controller.abort();
    // callback dependencies are intentionally provided by the caller through `deps`
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
