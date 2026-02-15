'use client';

import Breadcrumb from '@/components/common/Breadcrumb';

import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import {
  LayoutDashboard,
  ListTodo,
  Activity,
  Pill,
  Brain,
  Zap,
  Sparkles,
  BookOpen,
  Settings,
  Heart,
  Trophy,
  Bell,
  User,
  Clock,
} from 'lucide-react';
import type { ReactNode } from 'react';

const sidebarItems = [
  { href: '/patient/dashboard', icon: LayoutDashboard, labelKey: 'dashboard', fallback: 'Dashboard' },
  { href: '/patient/modules', icon: BookOpen, labelKey: 'modules', fallback: 'Moduller' },
  { href: '/patient/tasks', icon: ListTodo, labelKey: 'tasks', fallback: 'Gorevler' },
  { href: '/patient/symptoms', icon: Activity, labelKey: 'symptoms', fallback: 'Semptomlar' },
  { href: '/patient/medications', icon: Pill, labelKey: 'medications', fallback: 'Ilaclar' },
  { href: '/patient/migraine', icon: Brain, labelKey: 'migraine', fallback: 'Migren' },
  { href: '/patient/epilepsy', icon: Zap, labelKey: 'epilepsy', fallback: 'Epilepsi' },
  { href: '/patient/dementia', icon: Sparkles, labelKey: 'dementia', fallback: 'Demans' },
  { href: '/patient/wellness', icon: Heart, labelKey: 'wellness', fallback: 'Wellness' },
  { href: '/patient/rewards', icon: Trophy, labelKey: 'rewards', fallback: 'Oduller' },
  { href: '/patient/reminders', icon: Clock, labelKey: 'reminders', fallback: 'Hatirlaticilar' },
  { href: '/patient/profile', icon: User, labelKey: 'profile', fallback: 'Profil' },
  { href: '/patient/settings', icon: Settings, labelKey: 'settings', fallback: 'Ayarlar' },
];

export default function PatientLayout({ children }: { children: ReactNode }) {
  const t = useTranslations('nav');
  const pathname = usePathname();

  return (
    <div className="flex min-h-[calc(100vh-140px)]">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col bg-white border-r border-gray-200">
        <nav className="flex-1 p-4 space-y-1">
          {sidebarItems.map((item) => {
            const isActive = pathname.includes(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                {(() => { try { return t(item.labelKey); } catch { return (item as any).fallback || item.labelKey; } })()}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
        <div className="flex justify-around py-2">
          {sidebarItems.slice(0, 6).map((item) => {
            const isActive = pathname.includes(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-col items-center gap-0.5 px-2 py-1 text-xs ${
                  isActive ? 'text-blue-700' : 'text-gray-500'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{(() => { try { return t(item.labelKey); } catch { return (item as any).fallback || item.labelKey; } })()}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 p-4 md:p-6 bg-gray-50 pb-20 md:pb-6">
        <Breadcrumb />{children}
      </main>
    </div>
  );
}
