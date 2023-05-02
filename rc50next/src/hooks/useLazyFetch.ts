import { useState } from "react";

declare global {
  interface MakeFetchProps {
    url: string;
    options?: any;
  }

  interface UseLazyFetchProps {
    onSuccess?: (data: any) => void;
    onError?: (err: any) => void;
  }
}

function useLazyFetch({ onSuccess, onError }: UseLazyFetchProps): any[] {
  const [error, setError] = useState<any>(null);
  const [loading, setLoading] = useState<boolean | null>(null);
  const [data, setData] = useState<any>(null);

  const reset = () => {
    setData(null);
    setError(null);
    setLoading(true);
  };

  const makeFetch = async ({ url, options = null }: MakeFetchProps) => {
    setData(null);
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(url, options);
      const parsed = await response.json();

      if (response.status !== 200) {
        throw parsed;
      }

      if (onSuccess) onSuccess(parsed);
      setData(parsed);
      return setLoading(false);
    } catch (err: any) {
      if (err.name === 'AbortError') return;

      if (onError) onError(err);

      setData(null);
      setError(err);
      return setLoading(false);
    }
  };

  return [makeFetch, { data, error, loading, reset }];
}

export default useLazyFetch;
