import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { routing } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

// Protected routes - auth required
// NOT: /patient gecici olarak auth gerektirmiyor (ucretsiz deneme modu)
const PROTECTED_PREFIXES = ['/doctor', '/editor', '/caregiver'];
// Role-based routes
const ROLE_ROUTES: Record<string, string[]> = {
  '/doctor/site-settings': ['admin'],
  '/doctor': ['doctor', 'admin'],
  '/editor': ['doctor', 'admin'],
  '/caregiver': ['caregiver', 'admin'],
  '/patient': ['patient', 'doctor', 'admin'],
};

function getPathWithoutLocale(pathname: string): string {
  const segments = pathname.split('/');
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

  return intlMiddleware(request);
}

export const config = {
  matcher: [
    '/((?!api|_next|_vercel|.*\\..*).*)',
  ],
};
