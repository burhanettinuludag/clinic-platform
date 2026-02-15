'use client';

import { usePathname } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import { ChevronRight, Home } from 'lucide-react';

const LABELS: Record<string, string> = {
  patient: 'Hasta Paneli', doctor: 'Doktor Paneli', editor: 'Editor',
  dashboard: 'Dashboard', settings: 'Ayarlar', profile: 'Profil',
  medications: 'Ilaclar', symptoms: 'Semptomlar', tasks: 'Gorevler',
  migraine: 'Migren', epilepsy: 'Epilepsi', dementia: 'Demans',
  wellness: 'Wellness', rewards: 'Oduller', reminders: 'Hatirlaticilar',
  modules: 'Moduller', blog: 'Blog', news: 'Haberler', doctors: 'Doktorlar',
  education: 'Egitim', contact: 'Iletisim', author: 'Yazar Paneli',
  content: 'Icerik', alerts: 'Uyarilar', patients: 'Hastalar',
  analytics: 'Analitik', 'change-password': 'Sifre Degistir',
  'notification-settings': 'Bildirim Tercihleri',
};

export default function Breadcrumb() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  // Remove locale
  if (segments[0]?.length === 2) segments.shift();
  if (segments.length === 0) return null;

  const crumbs = segments.map((seg, i) => ({
    label: LABELS[seg] || seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' '),
    href: '/' + segments.slice(0, i + 1).join('/'),
    isLast: i === segments.length - 1,
  }));

  return (
    <nav className="flex items-center gap-1.5 text-xs text-gray-400 mb-4 overflow-x-auto">
      <Link href="/" className="hover:text-gray-600 flex-shrink-0"><Home className="h-3.5 w-3.5" /></Link>
      {crumbs.map(c => (
        <span key={c.href} className="flex items-center gap-1.5 flex-shrink-0">
          <ChevronRight className="h-3 w-3" />
          {c.isLast ? (
            <span className="text-gray-600 dark:text-gray-300 font-medium">{c.label}</span>
          ) : (
            <Link href={c.href} className="hover:text-gray-600 dark:hover:text-gray-300">{c.label}</Link>
          )}
        </span>
      ))}
    </nav>
  );
}
