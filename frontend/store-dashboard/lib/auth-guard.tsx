import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { ROUTES, isAuthRoute, isProtectedRoute } from '@/lib/routes';

// Authentication helper functions
export async function getSession() {
  return await getServerSession(authOptions);
}

export async function getCurrentUser() {
  const session = await getSession();
  return session?.user;
}

export async function isAuthenticated() {
  const session = await getSession();
  return !!session;
}

// Route protection functions
export async function requireAuth() {
  const authenticated = await isAuthenticated();

  if (!authenticated) {
    redirect(ROUTES.LOGIN);
  }
}

export async function requireGuest() {
  const authenticated = await isAuthenticated();

  if (authenticated) {
    redirect(ROUTES.DASHBOARD);
  }
}

export async function requireAuthOrRedirect(pathname: string) {
  const authenticated = await isAuthenticated();

  // If accessing protected routes without auth, redirect to login
  if (isProtectedRoute(pathname) && !authenticated) {
    redirect(ROUTES.LOGIN);
  }

  // If accessing auth routes while authenticated, redirect to dashboard
  if (isAuthRoute(pathname) && authenticated) {
    redirect(ROUTES.DASHBOARD);
  }
}

// Higher-order component for protecting pages
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: { requireAuth?: boolean; requireGuest?: boolean } = {}
) {
  return async function ProtectedComponent(props: P) {
    if (options.requireAuth) {
      await requireAuth();
    }

    if (options.requireGuest) {
      await requireGuest();
    }

    return <Component {...props} />;
  };
}

// Client-side auth check hook (for components that need auth state)
export function useAuth() {
  // This would typically use SWR or similar for client-side auth state
  // For now, we'll implement a basic version
  return {
    user: null, // Would be populated from session
    isAuthenticated: false, // Would be populated from session
    isLoading: false,
  };
}
