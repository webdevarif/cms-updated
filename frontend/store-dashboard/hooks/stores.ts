import { useState, useCallback } from 'react';
import useSWR from 'swr';
import { apiClient } from '@/lib/api-client';
import { buildUrlWithParams } from '@/lib/routes';
import { ROUTES } from '@/lib/routes';
import { Store, StoreMembership, StoreRole, StoreAPIKey, PaginatedResponse } from '@/types/stores.types';
import { StoreCreateFormData } from '@/schemas/stores.schemas';

// Custom fetcher for stores with proper typing
const storesFetcher = async (url: string): Promise<Store[]> => {
  console.log('Fetching stores from:', url);
  try {
    const res = await apiClient.get<PaginatedResponse<Store>>(url);
    console.log('Stores API response:', res);
    console.log('Stores data:', res.data);

    // Handle paginated response - extract results array
    const stores = res.data.results || res.data;
    console.log('Extracted stores array:', stores);
    return stores;
  } catch (error) {
    console.error('Stores fetch error:', error);
    // Don't throw error for 401 - let auth hooks handle it
    if (error && typeof error === 'object' && 'response' in error &&
        error.response && typeof error.response === 'object' &&
        'status' in error.response && error.response.status === 401) {
      console.log('Auth error in stores fetch, letting auth hooks handle it');
      return []; // Return empty array instead of throwing
    }
    throw error;
  }
};

const storeFetcher = async (url: string): Promise<Store> => {
  console.log('Fetching store from:', url);

  // Ensure fresh token before making the request
  const { ensureFreshToken } = await import('@/lib/auth');
  const accessToken = await ensureFreshToken();

  if (!accessToken) {
    throw new Error('Not authenticated');
  }

  try {
    const res = await apiClient.get<Store>(url);
    console.log('Store API response:', res);
    return res.data;
  } catch (error) {
    console.error('Store fetch error:', error);
    // Don't throw error for 401 - let auth hooks handle it
    if (error && typeof error === 'object' && 'response' in error &&
        error.response && typeof error.response === 'object' &&
        'status' in error.response && error.response.status === 401) {
      console.log('Auth error in store fetch, letting auth hooks handle it');
      throw error; // Let SWR handle the error for proper error state
    }
    throw error;
  }
};

export function useStores() {
  const { data, error, isLoading, mutate } = useSWR<Store[]>(ROUTES.API.STORES.LIST, storesFetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    shouldRetryOnError: false,
    dedupingInterval: 300000, // 5 minutes (increased from 1 minute)
    errorRetryCount: 0,
    refreshInterval: 0, // Disable automatic refresh
  });

  // Debug logging
  console.log('useStores hook state:', { data, error, isLoading });

  return { data, error, isLoading, mutate };
}

export function useStore(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Store>(url, storeFetcher, {
    revalidateOnFocus: false,
    shouldRetryOnError: false,
    dedupingInterval: 60000, // 1 minute
  });
  return { data, error, isLoading, mutate };
}

export function useCreateStore() {
  const [isLoading, setIsLoading] = useState(false);
  const createStore = useCallback(async (storeData: StoreCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Store>(ROUTES.API.STORES.CREATE, storeData);
      return response.data;
    } catch (error) {
      console.error('Create store error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createStore, isLoading };
}

export function useUpdateStore() {
  const [isLoading, setIsLoading] = useState(false);
  const updateStore = useCallback(async (id: string | number, storeData: Partial<Store>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.UPDATE, { id });
      const response = await apiClient.patch<Store>(url, storeData);
      return response.data;
    } catch (error) {
      console.error('Update store error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateStore, isLoading };
}

export function useDeleteStore() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteStore = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.DELETE, { id });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete store error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteStore, isLoading };
}

// Store Memberships hooks
export function useStoreMemberships(storeId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.LIST, { id: storeId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreMembership[]>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateStoreMembership() {
  const [isLoading, setIsLoading] = useState(false);
  const createStoreMembership = useCallback(async (storeId: string | number, membershipData: Omit<StoreMembership, 'id' | 'joined_at' | 'store'>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.CREATE, { id: storeId });
      const response = await apiClient.post(url, membershipData);
      return response.data as StoreMembership;
    } catch (error) {
      console.error('Create store membership error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createStoreMembership, isLoading };
}

// Store Roles hooks
export function useStoreRoles(storeId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.LIST, { id: storeId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreRole[]>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateStoreRole() {
  const [isLoading, setIsLoading] = useState(false);
  const createStoreRole = useCallback(async (storeId: string | number, roleData: Omit<StoreRole, 'id' | 'created_at' | 'updated_at'>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.CREATE, { id: storeId });
      const response = await apiClient.post(url, roleData);
      return response.data as StoreRole;
    } catch (error) {
      console.error('Create store role error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createStoreRole, isLoading };
}

// Store API Keys hooks
export function useStoreAPIKeys(storeId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.LIST, { id: storeId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreAPIKey[]>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateStoreAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const createStoreAPIKey = useCallback(async (storeId: string | number, keyData: Omit<StoreAPIKey, 'id' | 'created' | 'created_by'>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.CREATE, { id: storeId });
      const response = await apiClient.post(url, keyData);
      return response.data as StoreAPIKey;
    } catch (error) {
      console.error('Create store API key error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createStoreAPIKey, isLoading };
}

export function useRevokeStoreAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const revokeStoreAPIKey = useCallback(async (storeId: string | number, keyId: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.REVOKE, { id: storeId, keyId });
      await apiClient.post(url);
    } catch (error) {
      console.error('Revoke store API key error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { revokeStoreAPIKey, isLoading };
}

// Additional CRUD hooks for complete functionality

// Individual detail hooks
export function useStoreMembership(storeId: string | number, membershipId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.DETAIL, { id: storeId, membershipId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreMembership>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useStoreRole(storeId: string | number, roleId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.DETAIL, { id: storeId, roleId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreRole>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useStoreAPIKey(storeId: string | number, keyId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.DETAIL, { id: storeId, keyId });
  const { data, error, isLoading, mutate } = useSWR(url, async (url) => {
    const res = await apiClient.get<StoreAPIKey>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

// Store Membership update and delete
export function useUpdateStoreMembership() {
  const [isLoading, setIsLoading] = useState(false);
  const updateStoreMembership = useCallback(async (storeId: string | number, membershipId: string | number, membershipData: Partial<StoreMembership>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.UPDATE, { id: storeId, membershipId });
      const response = await apiClient.patch(url, membershipData);
      return response.data as StoreMembership;
    } catch (error) {
      console.error('Update store membership error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateStoreMembership, isLoading };
}

export function useDeleteStoreMembership() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteStoreMembership = useCallback(async (storeId: string | number, membershipId: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.DELETE, { id: storeId, membershipId });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete store membership error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteStoreMembership, isLoading };
}

// Store Role update and delete
export function useUpdateStoreRole() {
  const [isLoading, setIsLoading] = useState(false);
  const updateStoreRole = useCallback(async (storeId: string | number, roleId: string | number, roleData: Partial<StoreRole>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.UPDATE, { id: storeId, roleId });
      const response = await apiClient.patch(url, roleData);
      return response.data as StoreRole;
    } catch (error) {
      console.error('Update store role error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateStoreRole, isLoading };
}

export function useDeleteStoreRole() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteStoreRole = useCallback(async (storeId: string | number, roleId: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.DELETE, { id: storeId, roleId });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete store role error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteStoreRole, isLoading };
}

// Store API Key update and delete
export function useUpdateStoreAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const updateStoreAPIKey = useCallback(async (storeId: string | number, keyId: string | number, keyData: Partial<StoreAPIKey>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.DETAIL, { id: storeId, keyId });
      const response = await apiClient.patch(url, keyData);
      return response.data as StoreAPIKey;
    } catch (error) {
      console.error('Update store API key error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateStoreAPIKey, isLoading };
}

export function useDeleteStoreAPIKey() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteStoreAPIKey = useCallback(async (storeId: string | number, keyId: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.DETAIL, { id: storeId, keyId });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete store API key error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteStoreAPIKey, isLoading };
}
