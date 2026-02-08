'use client';

import React, { createContext, useContext, useState, useMemo } from 'react';
import { useStores } from '@/hooks/stores';
import { Store } from '@/types/stores.types';
import { setCurrentStoreId } from './current-store';

interface StoreContextType {
  stores: Store[];
  currentStore: Store | null;
  setCurrentStore: (store: Store) => void;
  isLoading: boolean;
  error: string | null;
}

const StoreContext = createContext<StoreContextType | null>(null);

const STORAGE_KEY = 'currentStoreId';

interface StoreProviderProps {
  children: React.ReactNode;
}

export function StoreProvider({ children }: StoreProviderProps) {
  const [currentStore, setCurrentStoreState] = useState<Store | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetch all stores user has access to
  const { data: stores = [], isLoading: storesLoading, error: storesError } = useStores();

  // Compute initial store when stores are loaded
  const initialStore = useMemo(() => {
    if (storesLoading || stores.length === 0) {
      return null;
    }

    // Check for stored preference
    let selectedStore: Store | null = null;

    if (typeof window !== 'undefined') {
      const storedId = localStorage.getItem(STORAGE_KEY);
      if (storedId) {
        // Find the stored store in the user's accessible stores
        selectedStore = stores.find(store => store.id.toString() === storedId) || null;
      }
    }

    // If no stored preference or stored store not accessible, use first store
    if (!selectedStore && stores.length > 0) {
      selectedStore = stores[0];
    }

    // Set current store ID immediately for axios interceptor
    if (selectedStore) {
      setCurrentStoreId(selectedStore.id);
    }

    return selectedStore;
  }, [stores, storesLoading]);

  // Set current store with persistence
  const setCurrentStore = React.useCallback((store: Store) => {
    setCurrentStoreState(store);
    setError(null);

    // Update the global current store ID for axios interceptor
    setCurrentStoreId(store.id);

    // Persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, store.id.toString());
    }
  }, []);

  // Set initial store when computed (avoid setState in effect)
  React.useEffect(() => {
    if (initialStore && currentStore !== initialStore) {
      setCurrentStoreState(initialStore);
    }
  }, [initialStore, currentStore]);

  // Handle errors (avoid setState in effect by using storesError directly)
  const contextError = React.useMemo(() => {
    return storesError ? (storesError.message || 'Failed to load stores') : null;
  }, [storesError]);

  const value: StoreContextType = React.useMemo(() => ({
    stores,
    currentStore,
    setCurrentStore,
    isLoading: storesLoading,
    error: error || contextError,
  }), [stores, currentStore, setCurrentStore, storesLoading, error, contextError]);

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStoreContext(): StoreContextType {
  const context = useContext(StoreContext);
  if (!context) {
    throw new Error('useStoreContext must be used within a StoreProvider');
  }
  return context;
}
