import useSWR from 'swr';
import { useCallback, useState } from 'react';
import { apiClient, externalApiClient } from '@/lib/api-client';

// Generic API hooks for other resources
export function useApiGet<T>(url: string | null, options?: { withAuth?: boolean; swrConfig?: Record<string, unknown> }) {
  const { withAuth = true, swrConfig } = options || {};

  const { data, error, isLoading, mutate } = useSWR<T>(
    url,
    (url: string) => {
      if (withAuth) {
        return apiClient.get(url).then(res => res.data);
      } else {
        return externalApiClient.get(url).then(res => res.data);
      }
    },
    {
      revalidateOnFocus: false,
      shouldRetryOnError: false,
      ...swrConfig,
    }
  );

  return {
    data,
    error,
    isLoading,
    mutate,
  };
}

export function useApiPost<T = unknown>() {
  const [isLoading, setIsLoading] = useState(false);

  const post = useCallback(async (url: string, data: T) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post(url, data);
      return response.data;
    } catch (error) {
      console.error('API POST error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { post, isLoading };
}

export function useApiPut<T = unknown>() {
  const [isLoading, setIsLoading] = useState(false);

  const put = useCallback(async (url: string, data: T) => {
    setIsLoading(true);
    try {
      const response = await apiClient.put(url, data);
      return response.data;
    } catch (error) {
      console.error('API PUT error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { put, isLoading };
}

export function useApiDelete() {
  const [isLoading, setIsLoading] = useState(false);

  const remove = useCallback(async (url: string) => {
    setIsLoading(true);
    try {
      const response = await apiClient.delete(url);
      return response.data;
    } catch (error) {
      console.error('API DELETE error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { remove, isLoading };
}
