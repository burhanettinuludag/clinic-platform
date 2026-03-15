import { ToastProvider } from '@/components/common/Toast';
import type { Metadata } from 'next';
import { NextIntlClientProvider, hasLocale } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { Inter } from 'next/font/google';
import { routing } from '@/i18n/routing';
import { AuthProvider } from '@/context/AuthContext';
import { CartProvider } from '@/context/CartContext';
import QueryProvider from '@/components/providers/QueryProvider';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import DisclaimerBanner from '@/components/common/DisclaimerBanner';
import AntiCopyProtection from '@/components/common/AntiCopyProtection';
import AnnouncementBanner from '@/components/common/AnnouncementBanner';
import '../globals.css';

const inter = Inter({
  subsets: ['latin', 'latin-ext'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: {
    default: 'Norosera - Nörolojik Hastalıklar İçin Dijital Platform',
    template: '%s | Norosera',
  },
  description: 'Migren, epilepsi ve diğer kronik nörolojik hastalıklar için dijital takip, ev eğitimi ve hekim paneli platformu.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com'),
  openGraph: {
    type: 'website',
    siteName: 'Norosera',
    title: 'Norosera - Nörolojik Hastalıklar İçin Dijital Platform',
    description: 'Nöroloji alanında uzman doktorlar tarafından desteklenen dijital sağlık platformu.',
    locale: 'tr_TR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Norosera',
    description: 'Nörolojik hastalıklar için dijital platform.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: '32x32' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    apple: '/icon.svg',
  },
  alternates: {
    languages: {
      'tr': 'https://norosera.com/tr',
      'en': 'https://norosera.com/en',
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION || '',
  },
};

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale} className={inter.variable}>
      <body className={`${inter.className} min-h-screen flex flex-col bg-white text-gray-900`}>
        <NextIntlClientProvider messages={messages}>
          <QueryProvider>
            <AuthProvider>
              <CartProvider>
                <AntiCopyProtection />
                <AnnouncementBanner />
                <DisclaimerBanner />
                <Header />
                <main className="flex-1 pt-16"><ToastProvider>{children}</ToastProvider></main>
                <Footer />
              </CartProvider>
            </AuthProvider>
          </QueryProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
