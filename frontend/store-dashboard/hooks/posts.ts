import { useState, useCallback } from 'react';
import useSWR from 'swr';
import { apiClient } from '@/lib/api-client';
import { buildUrlWithParams } from '@/lib/routes';
import { ROUTES } from '@/lib/routes';
import {
  PostType,
  Post,
  Category,
  Comment,
  Tag,
  PaginatedResponse,
  PostTypeCreateFormData,
  PostCreateFormData,
  PageCreateFormData,
  CategoryCreateFormData,
  CommentCreateFormData,
  TagCreateFormData,
  TagUpdateFormData
} from '@/types/posts.types';

// Type for paginated responses
interface PaginatedData<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// Post Types hooks
export function usePostTypes(storeId?: string) {
  const { data, error, isLoading, mutate } = useSWR<PostType[]>(
    ['postTypes', storeId],
    async ([, storeId]: [string, string?]) => {
      // Let the axios interceptor handle the Store header
      const res = await apiClient.get<PaginatedData<PostType> | PostType[]>(ROUTES.API.POSTS.POST_TYPES.LIST);
      // Handle paginated response - extract results array
      const postTypes = Array.isArray(res.data) ? res.data : res.data.results;
      return postTypes;
    }
  );
  return { data, error, isLoading, mutate };
}

export function usePostType(id: string | number, storeId?: string) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.POST_TYPES.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<PostType>(url, async (url: string) => {
    const headers: Record<string, string> = {};
    if (storeId) {
      headers.Store = storeId;
    }
    const res = await apiClient.get<PostType>(url, { headers });
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreatePostType() {
  const [isLoading, setIsLoading] = useState(false);
  const createPostType = useCallback(async (postTypeData: PostTypeCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<PostType>(ROUTES.API.POSTS.POST_TYPES.CREATE, postTypeData, {
        headers: { Store: postTypeData.store }
      });
      return response.data;
    } catch (error) {
      console.error('Create post type error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createPostType, isLoading };
}

export function useUpdatePostType() {
  const [isLoading, setIsLoading] = useState(false);
  const updatePostType = useCallback(async (id: string | number, postTypeData: Partial<PostType>, storeId?: string) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POST_TYPES.UPDATE, { id });
      const headers: Record<string, string> = {};
      if (storeId) {
        headers.Store = storeId;
      }
      const response = await apiClient.patch<PostType>(url, postTypeData, { headers });
      return response.data;
    } catch (error) {
      console.error('Update post type error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updatePostType, isLoading };
}

export function useDeletePostType() {
  const [isLoading, setIsLoading] = useState(false);
  const deletePostType = useCallback(async (id: string | number, storeId?: string) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POST_TYPES.DELETE, { id });
      const headers: Record<string, string> = {};
      if (storeId) {
        headers.Store = storeId;
      }
      await apiClient.delete(url, { headers });
    } catch (error) {
      console.error('Delete post type error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deletePostType, isLoading };
}

// Posts hooks
export function usePosts(storeId?: string, searchParams?: URLSearchParams) {
  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse<Post>>(
    ['posts', storeId, searchParams?.toString()],
    async ([, storeId, searchQueryString]: [string, string?, string?]) => {
      // Let the axios interceptor handle the Store header
      const url = searchQueryString ? `${ROUTES.API.POSTS.POSTS.LIST}?${searchQueryString}` : ROUTES.API.POSTS.POSTS.LIST;
      const res = await apiClient.get<PaginatedResponse<Post>>(url);
      return res.data;
    }
  );
  return { data: data?.results, error, isLoading, mutate, pagination: data ? { count: data.count, next: data.next, previous: data.previous } : null };
}

export function usePost(id: string | number, storeId?: string) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Post>(url, async (url: string) => {
    const headers: Record<string, string> = {};
    if (storeId) {
      headers.Store = storeId;
    }
    const res = await apiClient.get<Post>(url, { headers });
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreatePost() {
  const [isLoading, setIsLoading] = useState(false);
  const createPost = useCallback(async (postData: PostCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Post>(ROUTES.API.POSTS.POSTS.CREATE, postData, {
        headers: { Store: postData.store }
      });
      return response.data;
    } catch (error) {
      console.error('Create post error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createPost, isLoading };
}

export function useUpdatePost() {
  const [isLoading, setIsLoading] = useState(false);
  const updatePost = useCallback(async (id: string | number, postData: Partial<Post>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.UPDATE, { id });
      const response = await apiClient.patch<Post>(url, postData);
      return response.data;
    } catch (error) {
      console.error('Update post error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updatePost, isLoading };
}

export function useDeletePost() {
  const [isLoading, setIsLoading] = useState(false);
  const deletePost = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.DELETE, { id });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete post error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deletePost, isLoading };
}

// Pages hooks
export function usePages(searchParams?: URLSearchParams) {
  const queryString = searchParams ? `?${searchParams.toString()}` : '';
  const url = `${ROUTES.API.POSTS.PAGES.LIST}${queryString}`;
  const { data, error, isLoading, mutate } = useSWR<PaginatedResponse<Post>>(
    url,
    async (url: string) => {
      const res = await apiClient.get<PaginatedResponse<Post>>(url);
      return res.data;
    }
  );
  return { data: data?.results, error, isLoading, mutate, pagination: data ? { count: data.count, next: data.next, previous: data.previous } : null };
}

export function usePage(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.PAGES.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Post>(url, async (url: string) => {
    const res = await apiClient.get<Post>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreatePage() {
  const [isLoading, setIsLoading] = useState(false);
  const createPage = useCallback(async (pageData: PageCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Post>(ROUTES.API.POSTS.PAGES.CREATE, pageData);
      return response.data;
    } catch (error) {
      console.error('Create page error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createPage, isLoading };
}

export function useUpdatePage() {
  const [isLoading, setIsLoading] = useState(false);
  const updatePage = useCallback(async (id: string | number, pageData: Partial<Post>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.PAGES.UPDATE, { id });
      const response = await apiClient.patch<Post>(url, pageData);
      return response.data;
    } catch (error) {
      console.error('Update page error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updatePage, isLoading };
}

export function useDeletePage() {
  const [isLoading, setIsLoading] = useState(false);
  const deletePage = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.PAGES.DELETE, { id });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete page error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deletePage, isLoading };
}

// Categories hooks
export function useCategories(searchParams?: URLSearchParams) {
  const queryString = searchParams ? `?${searchParams.toString()}` : '';
  const url = `${ROUTES.API.POSTS.CATEGORIES.LIST}${queryString}`;
  const { data, error, isLoading, mutate } = useSWR<Category[]>(
    url,
    async (url: string) => {
      const res = await apiClient.get<PaginatedData<Category> | Category[]>(url);
      // Handle paginated response - extract results array
      const categories = Array.isArray(res.data) ? res.data : res.data.results;
      return categories;
    }
  );
  return { data, error, isLoading, mutate };
}

export function useCategory(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.CATEGORIES.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Category>(url, async (url: string) => {
    const res = await apiClient.get<Category>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateCategory() {
  const [isLoading, setIsLoading] = useState(false);
  const createCategory = useCallback(async (categoryData: CategoryCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Category>(ROUTES.API.POSTS.CATEGORIES.CREATE, categoryData);
      return response.data;
    } catch (error) {
      console.error('Create category error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createCategory, isLoading };
}

export function useUpdateCategory() {
  const [isLoading, setIsLoading] = useState(false);
  const updateCategory = useCallback(async (id: string | number, categoryData: Partial<Category>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.CATEGORIES.UPDATE, { id });
      const response = await apiClient.patch<Category>(url, categoryData);
      return response.data;
    } catch (error) {
      console.error('Update category error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateCategory, isLoading };
}

export function useDeleteCategory() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteCategory = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.CATEGORIES.DELETE, { id });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete category error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteCategory, isLoading };
}

// Comments hooks
export function useComments(searchParams?: URLSearchParams) {
  const queryString = searchParams ? `?${searchParams.toString()}` : '';
  const url = `${ROUTES.API.POSTS.COMMENTS.LIST}${queryString}`;
  const { data, error, isLoading, mutate } = useSWR<Comment[]>(
    url,
    async (url: string) => {
      const res = await apiClient.get<PaginatedData<Comment> | Comment[]>(url);
      // Handle paginated response - extract results array
      const comments = Array.isArray(res.data) ? res.data : res.data.results;
      return comments;
    }
  );
  return { data, error, isLoading, mutate };
}

export function useCommentsByPost(postId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.BY_POST, { postId });
  const { data, error, isLoading, mutate } = useSWR<Comment[]>(
    url,
    async (url: string) => {
      const res = await apiClient.get<PaginatedData<Comment> | Comment[]>(url);
      // Handle paginated response - extract results array
      const comments = Array.isArray(res.data) ? res.data : res.data.results;
      return comments;
    }
  );
  return { data, error, isLoading, mutate };
}

export function useComment(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Comment>(url, async (url: string) => {
    const res = await apiClient.get<Comment>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateComment() {
  const [isLoading, setIsLoading] = useState(false);
  const createComment = useCallback(async (commentData: CommentCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Comment>(ROUTES.API.POSTS.COMMENTS.CREATE, commentData);
      return response.data;
    } catch (error) {
      console.error('Create comment error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createComment, isLoading };
}

export function useUpdateComment() {
  const [isLoading, setIsLoading] = useState(false);
  const updateComment = useCallback(async (id: string | number, commentData: Partial<Comment>) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.UPDATE, { id });
      const response = await apiClient.patch<Comment>(url, commentData);
      return response.data;
    } catch (error) {
      console.error('Update comment error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateComment, isLoading };
}

export function useDeleteComment() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteComment = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.COMMENTS.DELETE, { id });
      await apiClient.delete(url);
    } catch (error) {
      console.error('Delete comment error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteComment, isLoading };
}

// Post Metadata hooks
export function usePostMeta(postId: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
  const { data, error, isLoading, mutate } = useSWR<Record<string, unknown>>(
    url,
    async (url: string) => {
      const res = await apiClient.get<Record<string, unknown>>(url);
      return res.data;
    }
  );
  return { data, error, isLoading, mutate };
}

export function useAddPostMeta() {
  const [isLoading, setIsLoading] = useState(false);
  const addPostMeta = useCallback(async (postId: string | number, metaData: { key: string; value: unknown }) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiClient.post(url, metaData);
      return response.data;
    } catch (error) {
      console.error('Add post meta error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { addPostMeta, isLoading };
}

export function useUpdatePostMeta() {
  const [isLoading, setIsLoading] = useState(false);
  const updatePostMeta = useCallback(async (postId: string | number, metaData: { key: string; value: unknown }) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiClient.put(url, metaData);
      return response.data;
    } catch (error) {
      console.error('Update post meta error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updatePostMeta, isLoading };
}

export function useDeletePostMeta() {
  const [isLoading, setIsLoading] = useState(false);
  const deletePostMeta = useCallback(async (postId: string | number, key: string) => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.POSTS.POSTS.META, { id: postId });
      const response = await apiClient.delete(`${url}?key=${key}`);
      return response.data;
    } catch (error) {
      console.error('Delete post meta error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deletePostMeta, isLoading };
}

// Theme hooks
export function useThemes() {
  const { data, error, isLoading, mutate } = useSWR<{ id: string; name: string; key: string }[]>(
    '/api/themes', // TODO: Update with actual theme API endpoint
    async (url: string) => {
      const res = await apiClient.get<{ id: string; name: string; key: string }[]>(url);
      return res.data;
    }
  );
  return { data, error, isLoading, mutate };
}

// Template hooks
export function useTemplates() {
  const { data, error, isLoading, mutate } = useSWR<{ id: string; name: string; key: string; template_role: string; template_type: string }[]>(
    '/api/templates', // TODO: Update with actual template API endpoint
    async (url: string) => {
      const res = await apiClient.get<{ id: string; name: string; key: string; template_role: string; template_type: string }[]>(url);
      return res.data;
    }
  );
  return { data, error, isLoading, mutate };
}

// Tags hooks
export function useTags(searchParams?: URLSearchParams) {
  const queryString = searchParams ? `?${searchParams.toString()}` : '';
  const url = `${ROUTES.API.POSTS.TAGS.LIST}${queryString}`;
  const { data, error, isLoading, mutate } = useSWR<Tag[]>(
    url,
    async (url: string) => {
      const res = await apiClient.get<PaginatedData<Tag> | Tag[]>(url);
      // Handle paginated response - extract results array
      const tags = Array.isArray(res.data) ? res.data : res.data.results;
      return tags;
    }
  );
  return { data, error, isLoading, mutate };
}

export function useTag(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.POSTS.TAGS.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Tag>(url, async (url: string) => {
    const res = await apiClient.get<Tag>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateTag() {
  const [isLoading, setIsLoading] = useState(false);
  const createTag = useCallback(async (tagData: TagCreateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.post<Tag>(ROUTES.API.POSTS.TAGS.CREATE, tagData);
      return response.data;
    } catch (error) {
      console.error('Create tag error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createTag, isLoading };
}

export function useUpdateTag() {
  const [isLoading, setIsLoading] = useState(false);
  const updateTag = useCallback(async (id: string | number, tagData: TagUpdateFormData) => {
    setIsLoading(true);
    try {
      const response = await apiClient.patch<Tag>(`${ROUTES.API.POSTS.TAGS.DETAIL.replace(':id', String(id))}`, tagData);
      return response.data;
    } catch (error) {
      console.error('Update tag error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateTag, isLoading };
}

export function useDeleteTag() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteTag = useCallback(async (id: string | number) => {
    setIsLoading(true);
    try {
      await apiClient.delete(`${ROUTES.API.POSTS.TAGS.DETAIL.replace(':id', String(id))}`);
    } catch (error) {
      console.error('Delete tag error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteTag, isLoading };
}
