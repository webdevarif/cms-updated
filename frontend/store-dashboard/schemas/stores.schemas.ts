import { z } from 'zod';

// Store creation schema
export const storeCreateSchema = z.object({
  name: z.string().min(1, 'Store name is required').max(255, 'Store name too long'),
  slug: z.string().min(1, 'Store slug is required').max(255, 'Store slug too long'),
  description: z.string().optional(),
  status: z.enum(['active', 'inactive', 'pending']).default('pending'),
  access_code: z.string().optional(),
});

export type StoreCreateFormData = z.infer<typeof storeCreateSchema>;

// Store update schema
export const storeUpdateSchema = z.object({
  name: z.string().min(1, 'Store name is required').max(255, 'Store name too long'),
  slug: z.string().min(1, 'Store slug is required').max(255, 'Store slug too long'),
  description: z.string().optional(),
  status: z.enum(['active', 'inactive', 'pending']),
});

export type StoreUpdateFormData = z.infer<typeof storeUpdateSchema>;

// Store membership schema
export const storeMembershipSchema = z.object({
  user: z.object({
    id: z.string(),
    username: z.string(),
    email: z.string(),
    first_name: z.string().optional(),
    last_name: z.string().optional(),
  }),
  role: z.string().min(1, 'Role is required'),
});

export type StoreMembershipFormData = z.infer<typeof storeMembershipSchema>;

// Store role schema
export const storeRoleSchema = z.object({
  name: z.string().min(1, 'Role name is required').max(100, 'Role name too long'),
  slug: z.string().min(1, 'Role slug is required').max(100, 'Role slug too long'),
  description: z.string().optional(),
  actions: z.array(z.string()).default([]),
});

export type StoreRoleFormData = z.infer<typeof storeRoleSchema>;

// Store API key schema
export const storeApiKeySchema = z.object({
  name: z.string().min(1, 'API key name is required').max(100, 'API key name too long'),
  actions: z.array(z.string()).default([]),
});

export type StoreApiKeyFormData = z.infer<typeof storeApiKeySchema>;

// Store search/filter schema
export const storeFilterSchema = z.object({
  status: z.enum(['active', 'inactive', 'pending']).optional(),
  owner: z.string().optional(),
  search: z.string().optional(),
});

export type StoreFilterFormData = z.infer<typeof storeFilterSchema>;
