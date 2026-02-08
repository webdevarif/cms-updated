export interface Store {
  id: string;
  name: string;
  slug: string;
  description?: string;
  owner: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  status: 'active' | 'inactive' | 'pending';
  access_code: string;
  created_at: string;
  updated_at: string;
}

// Type for paginated API response
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface StoreMembership {
  id: string;
  store: Store;
  user: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  role: string;
  joined_at: string;
}

export interface StoreRole {
  id: string;
  store: Store;
  name: string;
  slug: string;
  description?: string;
  actions: string[];
  created_at: string;
  updated_at: string;
}

export interface StoreUserRole {
  id: string;
  user: {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
  };
  store: Store;
  role: StoreRole;
  assigned_at: string;
  assigned_by?: {
    id: string;
    username: string;
    email: string;
  };
}

export interface StoreAPIKey {
  id: string;
  store: Store;
  name: string;
  actions: string[];
  created_by?: {
    id: string;
    username: string;
    email: string;
  };
  last_used_at?: string;
  created: string;
  expires?: string;
  revoked: boolean;
}
