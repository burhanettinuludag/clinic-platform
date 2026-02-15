import { ToastProvider } from '@/components/common/Toast';
import type { Metadata } from 'next';
import { NextIntlClientProvider, hasLocale } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { AuthProvider } from '@/context/AuthContext';
import { CartProvider } from '@/context/CartContext';
import QueryProvider from '@/components/providers/QueryProvider';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import DisclaimerBanner from '@/components/common/DisclaimerBanner';
import '../globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Norosera - Norolojik Hastaliklar Icin Dijital Platform',
    template: '%s | Norosera',
  },
  description: 'Migren, epilepsi ve diger kronik norolojik hastaliklar icin dijital takip, ev egitimi ve hekim paneli platformu.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com'),
  openGraph: {
    type: 'website',
    siteName: 'Norosera',
    title: 'Norosera - Norolojik Hastaliklar Icin Dijital Platform',
    description: 'Noroloji alaninda uzman doktorlar tarafindan desteklenen dijital saglik platformu.',
    locale: 'tr_TR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Norosera',
    description: 'Norolojik hastaliklar icin dijital platform.',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
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
    <html lang={locale}>
      <body className="min-h-screen flex flex-col bg-white text-gray-900">
        <NextIntlClientProvider messages={messages}>
          <QueryProvider>
            <AuthProvider>
              <CartProvider>
                <DisclaimerBanner />
                <Header />
                <main className="flex-1"><ToastProvider>{children}</ToastProvider></main>
                <Footer />
              </CartProvider>
            </AuthProvider>
          </QueryProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
