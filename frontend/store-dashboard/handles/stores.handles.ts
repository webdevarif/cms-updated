import { apiMethods } from '@/lib/api-client';
import { ROUTES, buildUrlWithParams } from '@/lib/routes';
import { Store, StoreMembership, StoreRole, StoreAPIKey } from '@/types/stores.types';

// Store Action Handlers - Business logic for store operations

export const storeActionHandlers = {
  // Create store handler
  createStore: async (storeData: Omit<Store, 'id'>): Promise<Store> => {
    try {
      const response = await apiMethods.post<Store>(ROUTES.API.STORES.CREATE, storeData);
      return response;
    } catch (error) {
      console.error('Create store error:', error);
      throw error;
    }
  },

  // Update store handler
  updateStore: async (id: string | number, storeData: Partial<Store>): Promise<Store> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.UPDATE, { id });
      const response = await apiMethods.patch<Store>(url, storeData);
      return response;
    } catch (error) {
      console.error('Update store error:', error);
      throw error;
    }
  },

  // Delete store handler
  deleteStore: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete store error:', error);
      throw error;
    }
  },

  // Membership handlers
  createMembership: async (storeId: string | number, data: Omit<StoreMembership, 'id' | 'store' | 'joined_at'>): Promise<StoreMembership> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.CREATE, { id: storeId });
      const response = await apiMethods.post<StoreMembership>(url, data);
      return response;
    } catch (error) {
      console.error('Create membership error:', error);
      throw error;
    }
  },

  // Role handlers
  createRole: async (storeId: string | number, data: Omit<StoreRole, 'id' | 'store' | 'created_at' | 'updated_at'>): Promise<StoreRole> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.ROLES.CREATE, { id: storeId });
      const response = await apiMethods.post<StoreRole>(url, data);
      return response;
    } catch (error) {
      console.error('Create role error:', error);
      throw error;
    }
  },

  // API Key handlers
  createAPIKey: async (storeId: string | number, data: Omit<StoreAPIKey, 'id' | 'created' | 'last_used_at'>): Promise<StoreAPIKey> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.CREATE, { id: storeId });
      const response = await apiMethods.post<StoreAPIKey>(url, data);
      return response;
    } catch (error) {
      console.error('Create API key error:', error);
      throw error;
    }
  },

  revokeAPIKey: async (storeId: string | number, keyId: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.STORES.API_KEYS.REVOKE, { id: storeId, keyId });
      await apiMethods.post(url);
    } catch (error) {
      console.error('Revoke API key error:', error);
      throw error;
    }
  },

  // Form state handlers
  initializeCreateForm: (): Partial<Store> => ({
    name: '',
    slug: '',
    description: '',
    status: 'pending',
    owner: {
      id: '',
      username: '',
      email: '',
      first_name: '',
      last_name: '',
    },
    access_code: '',
    created_at: '',
    updated_at: '',
  }),

  resetCreateForm: (): Partial<Store> => ({
    name: '',
    slug: '',
    description: '',
    status: 'pending',
    owner: {
      id: '',
      username: '',
      email: '',
      first_name: '',
      last_name: '',
    },
    access_code: '',
    created_at: '',
    updated_at: '',
  }),

  validateStoreForm: (formData: Partial<Store>): string[] => {
    const errors: string[] = [];

    if (!formData.name || formData.name.trim().length === 0) {
      errors.push('Store name is required');
    }

    if (!formData.slug || formData.slug.trim().length === 0) {
      errors.push('Store slug is required');
    }

    if (formData.slug && !/^[a-z0-9-]+$/.test(formData.slug)) {
      errors.push('Store slug must contain only lowercase letters, numbers, and hyphens');
    }

    return errors;
  },

  prepareStoreData: (formData: Partial<Store>): Omit<Store, 'id'> => {
    return {
      name: formData.name || '',
      slug: formData.slug || '',
      description: formData.description || '',
      status: formData.status as 'active' | 'inactive' | 'pending' || 'pending',
      owner: formData.owner || {
        id: '',
        username: '',
        email: '',
        first_name: '',
        last_name: '',
      },
      access_code: formData.access_code || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as Omit<Store, 'id'>;
  },
};

// Store API Handles - Utilities for store-related API operations

// Store operations
export const storeHandles = {
  // Get store with additional metadata
  getStoreWithDetails: async (storeId: string | number): Promise<Store> => {
    const url = buildUrlWithParams(ROUTES.API.STORES.DETAIL, { id: storeId });
    return apiMethods.get<Store>(url);
  },

  // Check if user can access store
  canAccessStore: async (storeId: string | number): Promise<boolean> => {
    try {
      const store = await storeHandles.getStoreWithDetails(storeId);
      return !!store;
    } catch {
      return false;
    }
  },

  // Generate store access code
  generateAccessCode: (): string => {
    return Math.random().toString(36).substring(2, 8).toUpperCase();
  },

  // Validate store slug
  validateSlug: (slug: string): boolean => {
    return /^[a-z0-9-]+$/.test(slug) && slug.length >= 3 && slug.length <= 50;
  },

  // Get store statistics
  getStoreStats: async (storeId: string | number) => {
    const [memberships, roles, apiKeys] = await Promise.all([
      apiMethods.get<StoreMembership[]>(buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.LIST, { id: storeId })),
      apiMethods.get<StoreRole[]>(buildUrlWithParams(ROUTES.API.STORES.ROLES.LIST, { id: storeId })),
      apiMethods.get<StoreAPIKey[]>(buildUrlWithParams(ROUTES.API.STORES.API_KEYS.LIST, { id: storeId })),
    ]);

    return {
      memberCount: memberships.length,
      roleCount: roles.length,
      apiKeyCount: apiKeys.length,
      activeApiKeys: apiKeys.filter(key => !key.revoked).length,
    };
  },
};

// Membership operations
export const membershipHandles = {
  // Check if user has specific role in store
  hasRole: async (storeId: string | number, userId: string, roleName: string): Promise<boolean> => {
    try {
      const memberships = await apiMethods.get<StoreMembership[]>(
        buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.LIST, { id: storeId })
      );
      return memberships.some(membership =>
        membership.user.id === userId && membership.role === roleName
      );
    } catch {
      return false;
    }
  },

  // Get user role in store
  getUserRole: async (storeId: string | number, userId: string): Promise<string | null> => {
    try {
      const memberships = await apiMethods.get<StoreMembership[]>(
        buildUrlWithParams(ROUTES.API.STORES.MEMBERSHIPS.LIST, { id: storeId })
      );
      const membership = memberships.find(m => m.user.id === userId);
      return membership?.role || null;
    } catch {
      return null;
    }
  },
};

// Role operations
export const roleHandles = {
  // Check if role has specific action permission
  hasPermission: (role: StoreRole, action: string): boolean => {
    return role.actions.includes(action) || role.actions.includes('*');
  },

  // Get all unique actions from roles
  getAllActions: (roles: StoreRole[]): string[] => {
    const actions = new Set<string>();
    roles.forEach(role => {
      role.actions.forEach(action => actions.add(action));
    });
    return Array.from(actions);
  },

  // Validate role actions
  validateActions: (actions: string[]): boolean => {
    const validActions = [
      'read', 'write', 'delete', 'manage_members', 'manage_roles',
      'manage_api_keys', 'view_analytics', 'export_data'
    ];
    return actions.every(action => validActions.includes(action) || action === '*');
  },
};

// API Key operations
export const apiKeyHandles = {
  // Check if API key has permission for action
  hasPermission: (apiKey: StoreAPIKey, action: string): boolean => {
    return apiKey.actions.includes(action) || apiKey.actions.includes('*');
  },

  // Get API key usage statistics
  getUsageStats: (apiKeys: StoreAPIKey[]) => {
    const now = new Date();
    const last24h = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const last7d = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    return {
      total: apiKeys.length,
      active: apiKeys.filter(key => !key.revoked).length,
      revoked: apiKeys.filter(key => key.revoked).length,
      usedRecently: apiKeys.filter(key =>
        key.last_used_at && new Date(key.last_used_at) > last24h
      ).length,
      usedThisWeek: apiKeys.filter(key =>
        key.last_used_at && new Date(key.last_used_at) > last7d
      ).length,
    };
  },

  // Check if API key is expired
  isExpired: (apiKey: StoreAPIKey): boolean => {
    if (!apiKey.expires) return false;
    return new Date(apiKey.expires) < new Date();
  },
};
