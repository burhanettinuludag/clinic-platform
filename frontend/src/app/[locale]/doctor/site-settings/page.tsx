'use client';

import { useDashboardStats, useFeatureFlags } from '@/hooks/useSiteAdmin';
import { Link } from '@/i18n/navigation';
import { Settings, ToggleLeft, Megaphone, Home, Share2, FileText, Users, TrendingUp, Bell, Flag, Link2Off, Bot, UserCheck } from 'lucide-react';

export default function SiteSettingsPage() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: flags } = useFeatureFlags();

  const activeFlags = flags?.filter(f => f.is_enabled).length ?? 0;
  const totalFlags = flags?.length ?? 0;

  const statCards = [
    { label: 'Toplam Kullanici', value: stats?.total_users ?? 0, sub: `Bugun +${stats?.new_users_today ?? 0}`, icon: Users, color: 'text-cyan-400' },
    { label: 'Yayinda Makale', value: `${stats?.published_articles ?? 0} / ${stats?.total_articles ?? 0}`, sub: 'Yayinda / Toplam', icon: FileText, color: 'text-purple-400' },
    { label: 'Onay Bekleyen', value: stats?.pending_review ?? 0, sub: 'Icerik incelemede', icon: TrendingUp, color: 'text-amber-400' },
    { label: 'Aktif Duyuru', value: stats?.active_announcements ?? 0, sub: 'Site bandinda', icon: Bell, color: 'text-rose-400' },
  ];

  const actionCards = [
    { href: '/doctor/site-settings/config', label: 'Site Ayarlari', sub: 'Site adi, iletisim, footer', icon: Settings, color: 'border-cyan-500/30 hover:border-cyan-500/60' },
    { href: '/doctor/site-settings/features', label: 'Ozellik Yonetimi', sub: `${activeFlags} aktif / ${totalFlags} toplam`, icon: ToggleLeft, color: 'border-green-500/30 hover:border-green-500/60' },
    { href: '/doctor/site-settings/announcements', label: 'Duyurular', sub: 'Site bandi duyurulari', icon: Megaphone, color: 'border-amber-500/30 hover:border-amber-500/60' },
    { href: '/doctor/site-settings/homepage', label: 'Anasayfa', sub: 'Hero, CTA butonlari', icon: Home, color: 'border-purple-500/30 hover:border-purple-500/60' },
    { href: '/doctor/site-settings/social', label: 'Sosyal Medya', sub: 'Twitter, LinkedIn, Instagram...', icon: Share2, color: 'border-blue-500/30 hover:border-blue-500/60' },
    { href: '/doctor/site-settings/broken-links', label: 'Kirik Linkler', sub: 'Kirik linkleri tara ve tamir et', icon: Link2Off, color: 'border-red-500/30 hover:border-red-500/60' },
    { href: '/doctor/site-settings/agents', label: 'Agent Yonetimi', sub: 'Agent lari izle ve tetikle', icon: Bot, color: 'border-indigo-500/30 hover:border-indigo-500/60' },
    { href: '/doctor/site-settings/doctor-approvals', label: 'Doktor Onaylari', sub: 'Doktor basvurularini onayla/reddet', icon: UserCheck, color: 'border-emerald-500/30 hover:border-emerald-500/60' },
    { href: '/doctor/editor', label: 'Icerik Yonetimi', sub: 'Makale ve haber onayi', icon: FileText, color: 'border-indigo-500/30 hover:border-indigo-500/60' },
  ];

  return (
    <div className="p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Site Yonetimi</h1>
        <p className="text-slate-500 mt-1">Platform ayarlari ve icerik yonetimi</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">{card.label}</p>
                  <p className="text-2xl font-bold text-slate-900 mt-1">
                    {isLoading ? '...' : card.value}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">{card.sub}</p>
                </div>
                <Icon className={`h-8 w-8 ${card.color}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Action Cards */}
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Hizli Aksiyonlar</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {actionCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link key={card.href} href={card.href}
                className={`block bg-white rounded-xl border-2 ${card.color} p-5 transition-all hover:shadow-lg`}>
                <div className="flex items-start gap-4">
                  <div className="rounded-lg bg-slate-100 p-3">
                    <Icon className="h-6 w-6 text-slate-700" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{card.label}</h3>
                    <p className="text-sm text-slate-500 mt-1">{card.sub}</p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
