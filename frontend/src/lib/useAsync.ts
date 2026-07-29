import { useCallback, useEffect, useState } from "react";
import { ApiError } from "@/api/client";

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function describeError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return String(err);
}

/** Runs `fetcher` on mount (and whenever `deps` change), tracking
 * loading/error/data state. Returns a `refetch` you can call after
 * mutations to re-sync the list/detail view.
 */
export function useAsync<T>(fetcher: () => Promise<T>, deps: unknown[] = []): AsyncState<T> & { refetch: () => void } {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null });
  const [tick, setTick] = useState(0);

  const load = useCallback(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (!cancelled) setState({ data: null, loading: false, error: describeError(err) });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  useEffect(() => load(), [load]);

  return { ...state, refetch: () => setTick((t) => t + 1) };
}

export { describeError };
