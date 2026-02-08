'use client';

import React, { useEffect } from 'react';
import { notFound, useRouter } from 'next/navigation';
import { useStore } from '@/hooks/stores';
import { useStoreContext } from '@/lib/store-context';

interface StoreClientLayoutProps {
  children: React.ReactNode;
  storeId: string;
}

export default function StoreClientLayout({ children, storeId }: StoreClientLayoutProps) {
  const { data: store, isLoading, error } = useStore(storeId);
  const { stores, currentStore, setCurrentStore } = useStoreContext();
  const router = useRouter();

  // Sync URL storeId with StoreContext
  useEffect(() => {
    if (store && stores.length > 0) {
      // Check if this store is in the user's accessible stores
      const accessibleStore = stores.find(s => s.id.toString() === storeId);
      if (accessibleStore && accessibleStore.id !== currentStore?.id) {
        // Update the current store in context
        setCurrentStore(accessibleStore);
      }
    }
  }, [store, stores, storeId, currentStore, setCurrentStore]);

  // Handle authentication errors
  const isAuthError = error && typeof error === 'object' && 'response' in error &&
      error.response && typeof error.response === 'object' &&
      'status' in error.response && error.response.status === 401;

  // Redirect to login on authentication error
  useEffect(() => {
    if (isAuthError) {
      const timer = setTimeout(() => {
        router.push('/auth/login');
      }, 1500); // Brief delay to show message

      return () => clearTimeout(timer);
    }
  }, [router, isAuthError]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (isAuthError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Authentication required. Redirecting to login...</p>
        </div>
      </div>
    );
  }

  if (error || !store) {
    notFound();
  }

  return (
    <div className="min-h-screen">
      {children}
    </div>
  );
}
