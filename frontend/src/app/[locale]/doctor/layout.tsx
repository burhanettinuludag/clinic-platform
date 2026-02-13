'use client';

import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import { LayoutDashboard, Users, AlertTriangle, Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';

const sidebarItems = [
  { href: '/doctor/dashboard', icon: LayoutDashboard, labelKey: 'dashboard', fallback: 'Dashboard' },
  { href: '/doctor/patients', icon: Users, labelKey: 'patients', fallback: 'Hastalar' },
  { href: '/doctor/alerts', icon: AlertTriangle, labelKey: 'alerts', fallback: 'Uyarılar' },
  { href: '/doctor/content', icon: Sparkles, labelKey: 'content', fallback: 'İçerik Üret' },
];

export default function DoctorLayout({ children }: { children: ReactNode }) {
  const t = useTranslations('nav');
  const pathname = usePathname();

  const isActive = (href: string) => {
    const segments = pathname.split('/');
    const pathWithoutLocale = '/' + segments.slice(2).join('/');
    return pathWithoutLocale.startsWith(href);
  };

  const getLabel = (labelKey: string, fallback: string) => {
    try {
      const translated = t(labelKey);
      return translated === labelKey ? fallback : translated;
    } catch {
      return fallback;
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex md:w-64 md:flex-col md:border-r md:bg-white">
        <div className="flex h-16 items-center border-b px-6">
          <h2 className="text-lg font-semibold text-gray-800">Doctor Panel</h2>
        </div>
        <nav className="flex-1 space-y-1 p-4">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? item.href === '/doctor/content'
                      ? 'bg-purple-50 text-purple-700'
                      : 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon
                  className={`h-5 w-5 ${
                    active
                      ? item.href === '/doctor/content'
                        ? 'text-purple-700'
                        : 'text-blue-700'
                      : 'text-gray-400'
                  }`}
                />
                {getLabel(item.labelKey, item.fallback)}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-50 pb-20 md:pb-0">
        {children}
      </main>

      {/* Bottom Nav - Mobile */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t bg-white py-2 md:hidden">
        {sidebarItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-1 px-3 py-1 text-xs font-medium transition-colors ${
                active ? 'text-blue-700' : 'text-gray-500'
              }`}
            >
              <Icon className={`h-5 w-5 ${active ? 'text-blue-700' : 'text-gray-400'}`} />
              {getLabel(item.labelKey, item.fallback)}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
