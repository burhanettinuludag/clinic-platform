import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { routing } from './i18n/routing';

const intlMiddleware = createMiddleware(routing);

// ============================================
// LAUNCH MODE (production only):
// Sadece news sayfaları açık, diğerleri "Yakında"ya yönlendirilir
// Lokal geliştirmede tüm sayfalar açık kalır
// ============================================

const IS_PRODUCTION = process.env.NODE_ENV === 'production';
const ALLOWED_PREFIXES = ['/news', '/yakinda', '/coming-soon'];

function getPathWithoutLocale(pathname: string): string {
  const segments = pathname.split('/');
  if (segments.length > 1 && segments[1].length === 2) {
    return '/' + segments.slice(2).join('/');
  }
  return pathname;
}

export default function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Production'da launch mode: sadece izin verilen sayfalar açık
  if (IS_PRODUCTION) {
    const pathWithoutLocale = getPathWithoutLocale(pathname);
    const isAllowed = ALLOWED_PREFIXES.some(p => pathWithoutLocale.startsWith(p));
    const isRoot = pathWithoutLocale === '/' || pathWithoutLocale === '';

    if (!isAllowed && (isRoot || pathWithoutLocale.length > 1)) {
      const locale = pathname.split('/')[1] || 'tr';
      const validLocales = ['tr', 'en'];
      const loc = validLocales.includes(locale) ? locale : 'tr';
      return NextResponse.redirect(new URL(`/${loc}/yakinda`, request.url));
    }
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: [
    '/((?!api|_next|_vercel|.*\\..*).*)',
  ],
};
