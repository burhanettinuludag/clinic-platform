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
  title: 'Norosera - Norolojik Hastaliklar Icin Dijital Platform',
  description:
    'Migren, epilepsi ve diger kronik norolojik hastaliklar icin dijital takip, ev egitimi ve hekim paneli platformu.',
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
                <main className="flex-1">{children}</main>
                <Footer />
              </CartProvider>
            </AuthProvider>
          </QueryProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
