import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { routing } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

// Protected routes - auth required
const PROTECTED_PREFIXES = ['/patient', '/doctor', '/editor'];
// Role-based routes
const ROLE_ROUTES: Record<string, string[]> = {
  '/doctor': ['doctor', 'admin'],
  '/editor': ['doctor', 'admin'],
  '/patient': ['patient', 'doctor', 'admin'],
};
// Public routes (no auth needed)
const PUBLIC_PREFIXES = ['/blog', '/news', '/doctors', '/education', '/contact', '/auth'];

function getPathWithoutLocale(pathname: string): string {
  const segments = pathname.split('/');
  // Remove locale segment (e.g., /tr/patient -> /patient)
  if (segments.length > 1 && segments[1].length === 2) {
    return '/' + segments.slice(2).join('/');
  }
  return pathname;
}

export default function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const pathWithoutLocale = getPathWithoutLocale(pathname);

  // Check if protected route
  const isProtected = PROTECTED_PREFIXES.some(p => pathWithoutLocale.startsWith(p));

  if (isProtected) {
    // Check for auth token in cookies
    const token = request.cookies.get('access_token')?.value
      || request.cookies.get('token')?.value;

    if (!token) {
      // Redirect to login with return URL
      const locale = pathname.split('/')[1] || 'tr';
      const loginUrl = new URL(`/${locale}/auth/login`, request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Role check via cookie (set at login)
    const userRole = request.cookies.get('user_role')?.value;
    if (userRole) {
      for (const [prefix, roles] of Object.entries(ROLE_ROUTES)) {
        if (pathWithoutLocale.startsWith(prefix) && !roles.includes(userRole)) {
          const locale = pathname.split('/')[1] || 'tr';
          return NextResponse.redirect(new URL(`/${locale}`, request.url));
        }
      }
    }
  }

  // Run intl middleware for all requests
  return intlMiddleware(request);
}

export const config = {
  matcher: [
    '/((?!api|_next|_vercel|.*\\..*).*)',
  ],
};
