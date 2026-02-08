import { z } from 'zod';

// Post Type schemas
export const postTypeCreateSchema = z.object({
  name: z.string().min(1, 'Post type name is required').max(255, 'Post type name too long'),
  key: z.string().min(1, 'Post type key is required').max(255, 'Post type key too long'),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
  store: z.string().min(1, 'Store is required'),
});

export type PostTypeCreateFormData = z.infer<typeof postTypeCreateSchema>;

export const postTypeUpdateSchema = z.object({
  name: z.string().min(1, 'Post type name is required').max(255, 'Post type name too long'),
  key: z.string().min(1, 'Post type key is required').max(255, 'Post type key too long'),
  description: z.string().optional(),
  is_active: z.boolean(),
});

export type PostTypeUpdateFormData = z.infer<typeof postTypeUpdateSchema>;

// Post schemas
export const postCreateSchema = z.object({
  post_type: z.string().min(1, 'Post type is required'),
  title: z.string().min(1, 'Title is required'),
  slug: z.string().optional(),
  excerpt: z.string().optional(),
  content: z.string().min(1, 'Content is required'),
  content_type: z.enum(['html', 'markdown', 'json']).default('html'),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
  is_featured: z.boolean().default(false),
  categories: z.array(z.string()).default([]), // Category IDs
  store: z.string().min(1, 'Store is required'), // Store ID
  meta: z.record(z.string(), z.any()).optional(),
});

export type PostCreateFormData = z.infer<typeof postCreateSchema>;

export const postUpdateSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  slug: z.string().optional(),
  excerpt: z.string().optional(),
  content: z.string().min(1, 'Content is required'),
  content_type: z.enum(['html', 'markdown', 'json']),
  status: z.enum(['draft', 'published', 'archived']),
  is_featured: z.boolean(),
  categories: z.array(z.string()), // Category IDs
  meta: z.record(z.string(), z.any()).optional(),
});

export type PostUpdateFormData = z.infer<typeof postUpdateSchema>;

// Page schemas (similar to post but for page post type)
export const pageCreateSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  slug: z.string().optional(),
  excerpt: z.string().optional(),
  content: z.string().min(1, 'Content is required'),
  content_type: z.enum(['html', 'markdown', 'json']).default('html'),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
  is_featured: z.boolean().default(false),
  categories: z.array(z.string()).default([]), // Category IDs (optional for pages)
  store: z.string().min(1, 'Store is required'), // Store ID
  meta: z.record(z.string(), z.any()).optional(),
});

export type PageCreateFormData = z.infer<typeof pageCreateSchema>;

// Category schemas
export const categoryCreateSchema = z.object({
  name: z.string().min(1, 'Category name is required').max(255, 'Category name too long'),
  slug: z.string().optional(),
  description: z.string().optional(),
  parent: z.string().optional(), // Parent category ID
  is_active: z.boolean().default(true),
});

export type CategoryCreateFormData = z.infer<typeof categoryCreateSchema>;

export const categoryUpdateSchema = z.object({
  name: z.string().min(1, 'Category name is required').max(255, 'Category name too long'),
  slug: z.string().optional(),
  description: z.string().optional(),
  parent: z.string().optional(), // Parent category ID
  is_active: z.boolean(),
});

export type CategoryUpdateFormData = z.infer<typeof categoryUpdateSchema>;

// Tag schemas
export const tagCreateSchema = z.object({
  name: z.string().min(1, 'Tag name is required').max(255, 'Tag name too long'),
  slug: z.string().optional(),
  description: z.string().optional(),
  is_active: z.boolean().default(true),
});

export type TagCreateFormData = z.infer<typeof tagCreateSchema>;

export const tagUpdateSchema = z.object({
  name: z.string().min(1, 'Tag name is required').max(255, 'Tag name too long'),
  slug: z.string().optional(),
  description: z.string().optional(),
  is_active: z.boolean(),
});

export type TagUpdateFormData = z.infer<typeof tagUpdateSchema>;

// Comment schemas
export const commentCreateSchema = z.object({
  post: z.string().min(1, 'Post ID is required'),
  parent: z.string().optional(), // Parent comment ID
  content: z.string().min(1, 'Comment content is required'),
  is_approved: z.boolean().default(false),
  is_public: z.boolean().default(true),
});

export type CommentCreateFormData = z.infer<typeof commentCreateSchema>;

export const commentUpdateSchema = z.object({
  content: z.string().min(1, 'Comment content is required'),
  is_approved: z.boolean(),
  is_public: z.boolean(),
});

export type CommentUpdateFormData = z.infer<typeof commentUpdateSchema>;

// Post Meta schemas
export const postMetaCreateSchema = z.object({
  key: z.string().min(1, 'Meta key is required'),
  value: z.any(), // JSON value
});

export type PostMetaCreateFormData = z.infer<typeof postMetaCreateSchema>;

export const postMetaUpdateSchema = z.object({
  value: z.any(), // JSON value
});

export type PostMetaUpdateFormData = z.infer<typeof postMetaUpdateSchema>;

// Filter schemas
export const postFilterSchema = z.object({
  post_type: z.string().optional(),
  post_type_key: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']).optional(),
  is_featured: z.boolean().optional(),
  content_type: z.enum(['html', 'markdown', 'json']).optional(),
  search: z.string().optional(),
  ordering: z.string().optional(),
});

export type PostFilterFormData = z.infer<typeof postFilterSchema>;

export const postTypeFilterSchema = z.object({
  is_active: z.boolean().optional(),
  is_builtin: z.boolean().optional(),
  search: z.string().optional(),
});

export type PostTypeFilterFormData = z.infer<typeof postTypeFilterSchema>;

export const categoryFilterSchema = z.object({
  is_active: z.boolean().optional(),
  parent: z.string().optional(),
  search: z.string().optional(),
});

export type CategoryFilterFormData = z.infer<typeof categoryFilterSchema>;

export const tagFilterSchema = z.object({
  is_active: z.boolean().optional(),
  search: z.string().optional(),
});

export type TagFilterFormData = z.infer<typeof tagFilterSchema>;

export const commentFilterSchema = z.object({
  post: z.string().optional(),
  user: z.string().optional(),
  parent: z.string().optional(),
  is_approved: z.boolean().optional(),
  is_public: z.boolean().optional(),
  search: z.string().optional(),
});

export type CommentFilterFormData = z.infer<typeof commentFilterSchema>;
