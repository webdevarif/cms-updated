import { apiMethods } from '@/lib/api-client';
import { ROUTES, buildUrlWithParams } from '@/lib/routes';
import {
  PostType,
  Post,
  Category,
  Comment,
  PostTypeCreateFormData
} from '@/types/posts.types';

// Post Types Action Handlers
export const postTypeActionHandlers = {
  createPostType: async (postTypeData: PostTypeCreateFormData): Promise<PostType> => {
    try {
      const response = await apiMethods.post<PostType>(ROUTES.API.POSTS.POST_TYPES.CREATE, postTypeData);
      return response;
    } catch (error) {
      console.error('Create post type error:', error);
      throw error;
    }
  },

  updatePostType: async (id: string | number, postTypeData: Partial<PostType>): Promise<PostType> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POST_TYPES.UPDATE, { id });
      const response = await apiMethods.patch<PostType>(url, postTypeData);
      return response;
    } catch (error) {
      console.error('Update post type error:', error);
      throw error;
    }
  },

  deletePostType: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POST_TYPES.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete post type error:', error);
      throw error;
    }
  },
};

// Posts Action Handlers
export const postActionHandlers = {
  createPost: async (postData: Omit<Post, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by' | 'post_type_name' | 'post_type_key'>): Promise<Post> => {
    try {
      const response = await apiMethods.post<Post>(ROUTES.API.POSTS.POSTS.CREATE, postData);
      return response;
    } catch (error) {
      console.error('Create post error:', error);
      throw error;
    }
  },

  updatePost: async (id: string | number, postData: Partial<Post>): Promise<Post> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.UPDATE, { id });
      const response = await apiMethods.patch<Post>(url, postData);
      return response;
    } catch (error) {
      console.error('Update post error:', error);
      throw error;
    }
  },

  deletePost: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete post error:', error);
      throw error;
    }
  },

  // Post Meta operations
  getPostMeta: async (postId: string | number): Promise<Record<string, unknown>> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiMethods.get<Record<string, unknown>>(url);
      return response;
    } catch (error) {
      console.error('Get post meta error:', error);
      throw error;
    }
  },

  addPostMeta: async (postId: string | number, metaData: { key: string; value: unknown }): Promise<Record<string, unknown>> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiMethods.post<Record<string, unknown>>(url, metaData);
      return response;
    } catch (error) {
      console.error('Add post meta error:', error);
      throw error;
    }
  },

  updatePostMeta: async (postId: string | number, metaData: { key: string; value: unknown }): Promise<Record<string, unknown>> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiMethods.put<Record<string, unknown>>(url, metaData);
      return response;
    } catch (error) {
      console.error('Update post meta error:', error);
      throw error;
    }
  },

  deletePostMeta: async (postId: string | number, key: string): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      await apiMethods.delete(`${url}?key=${key}`);
    } catch (error) {
      console.error('Delete post meta error:', error);
      throw error;
    }
  },
};

// Pages Action Handlers (similar to posts but for page post type)
export const pageActionHandlers = {
  createPage: async (pageData: Omit<Post, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by' | 'post_type' | 'post_type_name' | 'post_type_key'>): Promise<Post> => {
    try {
      const response = await apiMethods.post<Post>(ROUTES.API.POSTS.PAGES.CREATE, pageData);
      return response;
    } catch (error) {
      console.error('Create page error:', error);
      throw error;
    }
  },

  updatePage: async (id: string | number, pageData: Partial<Post>): Promise<Post> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.PAGES.UPDATE, { id });
      const response = await apiMethods.patch<Post>(url, pageData);
      return response;
    } catch (error) {
      console.error('Update page error:', error);
      throw error;
    }
  },

  deletePage: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.PAGES.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete page error:', error);
      throw error;
    }
  },
};

// Categories Action Handlers
export const categoryActionHandlers = {
  createCategory: async (categoryData: Omit<Category, 'id' | 'created_at' | 'updated_at' | 'post_count'>): Promise<Category> => {
    try {
      const response = await apiMethods.post<Category>(ROUTES.API.POSTS.CATEGORIES.CREATE, categoryData);
      return response;
    } catch (error) {
      console.error('Create category error:', error);
      throw error;
    }
  },

  updateCategory: async (id: string | number, categoryData: Partial<Category>): Promise<Category> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.CATEGORIES.UPDATE, { id });
      const response = await apiMethods.patch<Category>(url, categoryData);
      return response;
    } catch (error) {
      console.error('Update category error:', error);
      throw error;
    }
  },

  deleteCategory: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.CATEGORIES.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete category error:', error);
      throw error;
    }
  },
};

// Comments Action Handlers
export const commentActionHandlers = {
  createComment: async (commentData: Omit<Comment, 'id' | 'created_at' | 'updated_at'>): Promise<Comment> => {
    try {
      const response = await apiMethods.post<Comment>(ROUTES.API.POSTS.COMMENTS.CREATE, commentData);
      return response;
    } catch (error) {
      console.error('Create comment error:', error);
      throw error;
    }
  },

  updateComment: async (id: string | number, commentData: Partial<Comment>): Promise<Comment> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.UPDATE, { id });
      const response = await apiMethods.patch<Comment>(url, commentData);
      return response;
    } catch (error) {
      console.error('Update comment error:', error);
      throw error;
    }
  },

  deleteComment: async (id: string | number): Promise<void> => {
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.DELETE, { id });
      await apiMethods.delete(url);
    } catch (error) {
      console.error('Delete comment error:', error);
      throw error;
    }
  },
};
