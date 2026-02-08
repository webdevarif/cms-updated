import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { routing } from './i18n/routing';
import { ROUTES, isAuthRoute, isProtectedRoute, isPublicRoute } from './lib/routes';
import { tokenUtils } from './handles/auth.handles';
import { SUPPORTED_LOCALES } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

export default async function middleware(request: NextRequest) {
  // Skip auth logic for API routes, static files, and Next.js internals
  if (
    request.nextUrl.pathname.startsWith('/api/') ||
    request.nextUrl.pathname.startsWith('/_next/') ||
    request.nextUrl.pathname.startsWith('/static/') ||
    request.nextUrl.pathname.includes('.')
  ) {
    return intlMiddleware(request);
  }

  // Get the potentially rewritten pathname
  const pathname = request.nextUrl.pathname;
  const segments = pathname.split('/');

  // Check if the first segment is a valid locale
  const firstSegment = segments[1];
  const hasLocale = (SUPPORTED_LOCALES as unknown as string[]).includes(firstSegment);

  // If path already has locale, just run internationalization middleware
  if (hasLocale) {
    return intlMiddleware(request);
  }

  // For paths without locale, handle auth logic
  const locale = 'en'; // default locale
  const pathnameWithoutLocale = pathname;

  // Skip auth for public routes
  if (isPublicRoute(pathnameWithoutLocale)) {
    return intlMiddleware(request);
  }

  // Get auth status - check for valid token in cookies
  const token = tokenUtils.getTokenFromCookie(request);
  const isAuth = !!token && !tokenUtils.isTokenExpired(token);

  // Check if the path is an auth route (login, register, etc.)
  const isAuthPath = isAuthRoute(pathnameWithoutLocale);

  // Check if the path is a protected route (dashboard, etc.)
  const isProtectedPath = isProtectedRoute(pathnameWithoutLocale);

  // Redirect logic
  // Handle invalid /auth/dashboard URL - redirect to /dashboard
  if (pathnameWithoutLocale === '/auth/dashboard') {
    const dashboardUrl = new URL(`/${locale}${ROUTES.DASHBOARD}`, request.url);
    return NextResponse.redirect(dashboardUrl);
  }

  if (isAuth && isAuthPath) {
    // If user is authenticated and trying to access auth pages, redirect to dashboard
    const dashboardUrl = new URL(`/${locale}${ROUTES.DASHBOARD}`, request.url);
    return NextResponse.redirect(dashboardUrl);
  } else if (!isAuth && isProtectedPath) {
    // If user is not authenticated and trying to access protected pages, redirect to login
    const loginUrl = new URL(`/${locale}${ROUTES.AUTH.LOGIN}`, request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Finally run internationalization middleware
  return intlMiddleware(request);
}

export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/trpc`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  // - … next-auth API routes
  matcher: '/((?!api|trpc|_next|_vercel|.*\\..*).*)'
};
