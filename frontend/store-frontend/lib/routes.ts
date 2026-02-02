// Route constants for the entire application
// Change these from one place and they'll update everywhere

export const ROUTES = {
  // Public routes (frontend)
  HOME: '/',
  CONTACT_US: '/contact-us',

  // Auth routes (for non-logged-in users)
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',

  // Protected routes (for logged-in users)
  DASHBOARD: '/dashboard',
  DASHBOARD_STORES: '/dashboard/stores',

  // API routes
  API_AUTH: '/api/auth',
} as const;

// Route groups for protection logic
export const ROUTE_GROUPS = {
  PUBLIC: [ROUTES.HOME, ROUTES.CONTACT_US],
  AUTH: [ROUTES.LOGIN, ROUTES.REGISTER],
  PROTECTED: [ROUTES.DASHBOARD, ROUTES.DASHBOARD_STORES],
} as const;

// Helper functions to check route types
export function isPublicRoute(pathname: string): boolean {
  return ROUTE_GROUPS.PUBLIC.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );
}

export function isAuthRoute(pathname: string): boolean {
  return ROUTE_GROUPS.AUTH.some(route =>
    pathname === route || pathname.startsWith(`${route}/`)
  );
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
  getLoginRedirect: (locale?: string) => routeHelpers.getLocalizedRoute(ROUTES.LOGIN, locale),

  // Get home redirect
  getHomeRedirect: (locale?: string) => routeHelpers.getLocalizedRoute(ROUTES.HOME, locale),
};
