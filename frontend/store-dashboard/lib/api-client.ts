import axios, { InternalAxiosRequestConfig, AxiosError } from 'axios';
import { tokenUtils } from '@/handles/auth.handles';
import { ROUTES, buildApiUrl } from '@/lib/routes';
import { getCurrentStoreId } from './current-store';

// Extend InternalAxiosRequestConfig to include retry flag
interface ExtendedAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// API Client Configuration Types
export interface ApiClientConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  withAuth?: boolean;
}

// Default configuration
const defaultConfig: ApiClientConfig = {
  baseURL: ROUTES.API.BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withAuth: true,
};

// Create flexible axios instance factory
export function createApiClient(config: Partial<ApiClientConfig> = {}) {
  const finalConfig = { ...defaultConfig, ...config };

  const client = axios.create({
    baseURL: finalConfig.baseURL,
    timeout: finalConfig.timeout,
    headers: finalConfig.headers,
  });

  // Add auth interceptor for token injection only
  if (finalConfig.withAuth) {
    client.interceptors.request.use(
      (requestConfig: InternalAxiosRequestConfig) => {
        // Add authorization header
        const token = tokenUtils.getTokens().token;
        if (token && !requestConfig.headers.Authorization) {
          requestConfig.headers.Authorization = `Bearer ${token}`;
        }

        // Add Store header for all requests (since all APIs are store-scoped)
        const storeId = getCurrentStoreId();
        if (!requestConfig.headers.Store && storeId != null) {
          requestConfig.headers.Store = storeId.toString();
        }

        return requestConfig;
      },
      (error: AxiosError) => Promise.reject(error)
    );
  }

// API Error Response type
interface ApiErrorResponse {
  detail?: string;
  store?: string | string[];
  [key: string]: unknown;
}

// Add response interceptor for error handling and token refresh
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig;

    // Handle 401 errors - try to refresh token
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const { ensureFreshToken } = await import('./auth');
        const newToken = await ensureFreshToken();

        if (newToken) {
          // Update the authorization header and retry the request
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Let the auth hooks handle the redirect
        return Promise.reject(error);
      }
    }

    // Handle store-related errors
    if (error.response?.status === 400) {
      const data = error.response.data as ApiErrorResponse;
      // Check if it's a store validation error
      if (data?.store || data?.detail?.includes('store')) {
        console.error('Store validation error:', data);
        // Could redirect to store selection or show error
        // For now, just log the error
      }
    } else if (error.response?.status === 403) {
      const data = error.response.data as ApiErrorResponse;
      // Check if it's a store access error
      if (data?.detail?.includes('permission') || data?.detail?.includes('access')) {
        console.error('Store access denied:', data);
        // Could redirect to accessible stores list
        // For now, just log the error
      }
    }

    return Promise.reject(error);
  }
);

  return client;
}

// Default API client (with auth)
export const apiClient = createApiClient();

// External API client (without auth)
export const externalApiClient = createApiClient({ withAuth: false });

// API Methods
export const apiMethods = {
  // GET request
  get: <T = unknown>(url: string, config?: Partial<ApiClientConfig>) => {
    const client = config?.withAuth === false ? externalApiClient : apiClient;
    return client.get<T>(url).then(res => res.data);
  },

  // POST request
  post: <T = unknown>(url: string, data?: unknown, config?: Partial<ApiClientConfig>) => {
    const client = config?.withAuth === false ? externalApiClient : apiClient;
    return client.post<T>(url, data).then(res => res.data);
  },

  // PUT request
  put: <T = unknown>(url: string, data?: unknown, config?: Partial<ApiClientConfig>) => {
    const client = config?.withAuth === false ? externalApiClient : apiClient;
    return client.put<T>(url, data).then(res => res.data);
  },

  // PATCH request
  patch: <T = unknown>(url: string, data?: unknown, config?: Partial<ApiClientConfig>) => {
    const client = config?.withAuth === false ? externalApiClient : apiClient;
    return client.patch<T>(url, data).then(res => res.data);
  },

  // DELETE request
  delete: <T = unknown>(url: string, config?: Partial<ApiClientConfig>) => {
    const client = config?.withAuth === false ? externalApiClient : apiClient;
    return client.delete<T>(url).then(res => res.data);
  },
};

// SWR Fetcher Functions
export const swrFetchers = {
  // Default fetcher for SWR (uses auth)
  fetcher: (url: string) => apiMethods.get(url),

  // External fetcher (no auth)
  externalFetcher: (url: string) => apiMethods.get(url, { withAuth: false }),

  // Custom fetcher with config
  customFetcher: (config: Partial<ApiClientConfig>) => (url: string) =>
    apiMethods.get(url, config),
};

// Helper functions for common API patterns
export const apiHelpers = {
  // Build URL with parameters
  buildUrl: buildApiUrl,

  // Handle API errors consistently
  handleError: (error: unknown) => {
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { data?: unknown } };
      return axiosError.response?.data || { message: 'An error occurred' };
    }
    if (error && typeof error === 'object' && 'message' in error) {
      return { message: (error as { message: string }).message };
    }
    return { message: 'An unexpected error occurred' };
  },

  // Check if error is authentication error
  isAuthError: (error: unknown) => {
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { status?: number } };
      return axiosError.response?.status === 401 || axiosError.response?.status === 403;
    }
    return false;
  },

  // Check if error is network error
  isNetworkError: (error: unknown) => {
    if (error && typeof error === 'object' && 'code' in error) {
      return (error as { code: string }).code === 'NETWORK_ERROR' && !('response' in error);
    }
    return false;
  },
};

export default apiClient;
