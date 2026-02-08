// Route constants for the entire application
// Change these from one place and they'll update everywhere

export const ROUTES = {
  // Public routes (frontend)
  HOME: '/',
  CONTACT_US: '/contact-us',

  // Auth routes (for non-logged-in users)
  AUTH: {
    ME: '/auth/me',
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGET_PASSWORD: '/auth/forget-password',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },

  // Protected routes (for logged-in users)
  DASHBOARD: '/dashboard',
  DASHBOARD_STORES: '/dashboard/stores',

  // API routes
  API: {
    // Base URLs for different API sources
    BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

    // Authentication endpoints
    AUTH: {
      LOGIN: '/auth/jwt/create/',
      REGISTER: '/auth/users/',
      REFRESH: '/auth/jwt/refresh/',
      ME: '/auth/users/me/',
      FORGET_PASSWORD: '/auth/users/reset_password/',
      RESET_PASSWORD: '/auth/users/reset_password/',
      RESET_PASSWORD_CONFIRM: '/auth/users/reset_password_confirm/',
      LOGOUT: '/auth/logout', // Frontend route for logout
    },

    // OAuth endpoints
    OAUTH: {
      GOOGLE: '/v2/api/accounts/public/oauth/google/',
      FACEBOOK: '/v2/api/accounts/public/oauth/facebook/',
      GITHUB: '/v2/api/accounts/public/oauth/github/',
      CALLBACK: '/v2/api/accounts/public/oauth/{provider}/callback/',
    },

    // Stores endpoints
    STORES: {
      LIST: '/stores/',
      DETAIL: '/stores/{id}/',
      CREATE: '/stores/',
      UPDATE: '/stores/{id}/',
      DELETE: '/stores/{id}/',
      // Nested endpoints
      MEMBERSHIPS: {
        LIST: '/stores/{id}/memberships/',
        CREATE: '/stores/{id}/memberships/',
        DETAIL: '/stores/{id}/memberships/{membershipId}/',
        UPDATE: '/stores/{id}/memberships/{membershipId}/',
        DELETE: '/stores/{id}/memberships/{membershipId}/',
      },
      ROLES: {
        LIST: '/stores/{id}/roles/',
        CREATE: '/stores/{id}/roles/',
        DETAIL: '/stores/{id}/roles/{roleId}/',
        UPDATE: '/stores/{id}/roles/{roleId}/',
        DELETE: '/stores/{id}/roles/{roleId}/',
      },
      API_KEYS: {
        LIST: '/stores/{id}/api-keys/',
        CREATE: '/stores/{id}/api-keys/',
        DETAIL: '/stores/{id}/api-keys/{keyId}/',
        REVOKE: '/stores/{id}/api-keys/{keyId}/revoke/',
      },
    },

    // Posts endpoints
    POSTS: {
      // Post Types
      POST_TYPES: {
        LIST: '/posts/post-types/',
        DETAIL: '/posts/post-types/{id}/',
        CREATE: '/posts/post-types/',
        UPDATE: '/posts/post-types/{id}/',
        DELETE: '/posts/post-types/{id}/',
      },
      // Posts (generic)
      POSTS: {
        LIST: '/posts/posts/',
        DETAIL: '/posts/posts/{id}/',
        CREATE: '/posts/posts/',
        UPDATE: '/posts/posts/{id}/',
        DELETE: '/posts/posts/{id}/',
        META: '/posts/posts/{id}/meta/',
      },
      // Pages (scoped to page post type)
      PAGES: {
        LIST: '/posts/pages/',
        DETAIL: '/posts/pages/{id}/',
        CREATE: '/posts/pages/',
        UPDATE: '/posts/pages/{id}/',
        DELETE: '/posts/pages/{id}/',
        PUBLISHED: '/posts/pages/published/',
      },
      // Categories
      CATEGORIES: {
        LIST: '/posts/categories/',
        DETAIL: '/posts/categories/{id}/',
        CREATE: '/posts/categories/',
        UPDATE: '/posts/categories/{id}/',
        DELETE: '/posts/categories/{id}/',
        POSTS: '/posts/categories/{id}/posts/',
      },
      // Comments
      COMMENTS: {
        LIST: '/posts/comments/',
        DETAIL: '/posts/comments/{id}/',
        CREATE: '/posts/comments/',
        UPDATE: '/posts/comments/{id}/',
        DELETE: '/posts/comments/{id}/',
        BY_POST: '/posts/comments/by_post/?post={postId}',
      },
      // Tags
      TAGS: {
        LIST: '/posts/tags/',
        DETAIL: '/posts/tags/{id}/',
        CREATE: '/posts/tags/',
        UPDATE: '/posts/tags/{id}/',
        DELETE: '/posts/tags/{id}/',
      },
    },

    // Themes endpoints (nested under stores: /stores/{store_pk}/themes/)
    THEMES: {
      LIST: '/stores/{store}/themes/',
      DETAIL: '/stores/{store}/themes/{id}/',
      CREATE: '/stores/{store}/themes/',
      UPDATE: '/stores/{store}/themes/{id}/',
      DELETE: '/stores/{store}/themes/{id}/',
      COLOR_SCHEMES: {
        LIST: '/stores/{store}/themes/color-schemes/',
        DETAIL: '/stores/{store}/themes/color-schemes/{id}/',
        CREATE: '/stores/{store}/themes/color-schemes/',
        UPDATE: '/stores/{store}/themes/color-schemes/{id}/',
        DELETE: '/stores/{store}/themes/color-schemes/{id}/',
      },
      LAYOUTS: {
        LIST: '/stores/{store}/themes/layouts/',
        DETAIL: '/stores/{store}/themes/layouts/{id}/',
        CREATE: '/stores/{store}/themes/layouts/',
        UPDATE: '/stores/{store}/themes/layouts/{id}/',
        DELETE: '/stores/{store}/themes/layouts/{id}/',
      },
      STYLE_CLASSES: {
        LIST: '/stores/{store}/themes/style-classes/',
        DETAIL: '/stores/{store}/themes/style-classes/{id}/',
        CREATE: '/stores/{store}/themes/style-classes/',
        UPDATE: '/stores/{store}/themes/style-classes/{id}/',
        DELETE: '/stores/{store}/themes/style-classes/{id}/',
      },
      TEMPLATES: {
        LIST: '/stores/{store}/themes/templates/',
        DETAIL: '/stores/{store}/themes/templates/{id}/',
        CREATE: '/stores/{store}/themes/templates/',
        UPDATE: '/stores/{store}/themes/templates/{id}/',
        DELETE: '/stores/{store}/themes/templates/{id}/',
      },
    },
  }
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (apiPath: string, baseUrl?: string): string => {
  const base = baseUrl || ROUTES.API.BASE_URL;
  return `${base}${apiPath}`;
};

// Helper function to build URLs with parameters
export const buildUrlWithParams = (urlTemplate: string, params: Record<string, string | number>): string => {
  return urlTemplate.replace(/\{(\w+)\}/g, (match, key) => {
    return params[key]?.toString() || match;
  });
};

// Route groups for protection logic
export const ROUTE_GROUPS = {
  PUBLIC: [ROUTES.HOME, ROUTES.CONTACT_US],
  AUTH: [ROUTES.AUTH.LOGIN, ROUTES.AUTH.REGISTER, '/login', '/register'],
  PROTECTED: [ROUTES.DASHBOARD, ROUTES.DASHBOARD_STORES],
} as const;

// Helper functions to check route types
export function isPublicRoute(pathname: string): boolean {
  return ROUTE_GROUPS.PUBLIC.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );
}

export function isAuthRoute(pathname: string): boolean {
  // Only check for exact auth routes, not paths starting with /auth/
  return ROUTE_GROUPS.AUTH.some(route => pathname === route);
}

export function isProtectedRoute(pathname: string): boolean {
  return ROUTE_GROUPS.PROTECTED.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );
}

// Route helpers for navigation
export const routeHelpers = {
  // Get localized route (to be used with next-intl Link)
  getLocalizedRoute: (route: string, locale?: string) => {
    const normalizedRoute = route.startsWith('/') ? route : `/${route}`;
    return locale ? `/${locale}${normalizedRoute}` : normalizedRoute;
  },

  // Get dashboard redirect after login
  getDashboardRedirect: (locale?: string) => routeHelpers.getLocalizedRoute(ROUTES.DASHBOARD, locale),

  // Get login redirect for unauthenticated users
  getLoginRedirect: (locale?: string) => routeHelpers.getLocalizedRoute(ROUTES.AUTH.LOGIN, locale),

  // Get home redirect
  getHomeRedirect: (locale?: string) => routeHelpers.getLocalizedRoute(ROUTES.HOME, locale),
};
