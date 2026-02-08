// Post Types management
export interface PostType {
  id: string;
  name: string;
  key: string;
  description?: string;
  is_active: boolean;
  is_builtin: boolean;
  post_count: number;
  schema?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  content: string;
  content_type: 'html' | 'markdown' | 'json';
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  post_type: PostType;
  post_type_name: string;
  post_type_key: string;
  created_by: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  updated_by: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  published_at?: string;
  categories: Category[];
  tags: Tag[];
  template?: {
    id: string;
    name: string;
    key: string;
    template_role: string;
    template_type: string;
    theme_id: string;
  };
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parent?: Category;
  is_active: boolean;
  post_count: number;
  created_at: string;
  updated_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  post_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  post: string; // Post ID
  user?: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  parent?: string; // Parent comment ID
  content: string;
  is_approved: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface PostMeta {
  key: string;
  value: unknown;
}

// Form data types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface PostTypeCreateFormData {
  name: string;
  key: string;
  description?: string;
  is_active: boolean;
  store: string;
}

export interface PostCreateFormData {
  post_type: string;
  title: string;
  slug?: string;
  excerpt?: string;
  content: string;
  content_type: 'html' | 'markdown' | 'json';
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  categories: string[];
  store: string;
  meta?: Record<string, unknown>;
}

export interface PageCreateFormData {
  title: string;
  slug?: string;
  excerpt?: string;
  content: string;
  content_type: 'html' | 'markdown' | 'json';
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  categories: string[];
  store: string;
  meta?: Record<string, unknown>;
}

export interface CategoryCreateFormData {
  name: string;
  slug?: string;
  description?: string;
  parent?: string;
  is_active: boolean;
}

export interface CommentCreateFormData {
  post: string;
  user?: string;
  content: string;
  is_approved: boolean;
  is_public: boolean;
}

export interface TagCreateFormData {
  name: string;
  slug?: string;
  description?: string;
  is_active: boolean;
}

export interface TagUpdateFormData {
  name: string;
  slug?: string;
  description?: string;
  is_active: boolean;
}
