import { useEffect } from 'react';

export function useEffectAsync(callback: () => Promise<void>, deps: React.DependencyList): void {
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      if (!cancelled) {
        await callback();
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}
