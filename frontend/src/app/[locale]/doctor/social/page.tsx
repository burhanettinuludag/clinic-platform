'use client';

import { useSocialDashboard, useSocialAccounts } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { Share2, Users, FileText, Calendar, CheckCircle, Clock, AlertTriangle, TrendingUp, Instagram, Linkedin, Plus } from 'lucide-react';

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  expired: 'bg-red-100 text-red-700',
  disconnected: 'bg-gray-100 text-gray-700',
};

export default function SocialDashboardPage() {
  const { data: stats, isLoading } = useSocialDashboard();
  const { data: accounts } = useSocialAccounts();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-gray-200 rounded-xl" />)}
          </div>
        </div>
      </div>
    );
  }

  const statCards = [
    { label: 'Toplam Post', value: stats?.total_posts ?? 0, icon: FileText, color: 'text-blue-600 bg-blue-50' },
    { label: 'Yayinlanan', value: stats?.published_posts ?? 0, icon: CheckCircle, color: 'text-green-600 bg-green-50' },
    { label: 'Zamanlanmis', value: stats?.scheduled_posts ?? 0, icon: Clock, color: 'text-purple-600 bg-purple-50' },
    { label: 'Basarisiz', value: stats?.failed_posts ?? 0, icon: AlertTriangle, color: 'text-red-600 bg-red-50' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Share2 className="h-7 w-7 text-cyan-600" />
            Sosyal Medya Yonetimi
          </h1>
          <p className="text-sm text-gray-500 mt-1">Hesaplar, kampanyalar ve postlar</p>
        </div>
        <div className="flex gap-2">
          <Link href="/doctor/social/campaigns" className="px-4 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50">
            Kampanyalar
          </Link>
          <Link href="/doctor/social/posts" className="px-4 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50">
            Postlar
          </Link>
          <Link href="/doctor/social/calendar" className="px-4 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50">
            <Calendar className="h-4 w-4 inline mr-1" />
            Takvim
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-white rounded-xl border p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{card.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${card.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Campaign & Account Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Campaigns */}
        <div className="bg-white rounded-xl border p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Kampanyalar</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {stats?.active_campaigns ?? 0} aktif / {stats?.total_campaigns ?? 0} toplam
              </span>
              <Link href="/doctor/social/campaigns" className="text-cyan-600 text-sm hover:underline">
                Tumu
              </Link>
            </div>
          </div>
          <div className="text-center py-8 text-gray-400">
            <TrendingUp className="h-12 w-12 mx-auto mb-2 opacity-30" />
            <p className="text-sm">Kampanya olusturmak icin &quot;Kampanyalar&quot; sayfasina gidin</p>
          </div>
        </div>

        {/* Connected Accounts */}
        <div className="bg-white rounded-xl border p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Bagli Hesaplar</h2>
            <span className="text-sm text-gray-500">
              {stats?.active_accounts ?? 0} aktif / {stats?.total_accounts ?? 0} toplam
            </span>
          </div>
          {accounts && accounts.length > 0 ? (
            <div className="space-y-3">
              {accounts.map((acc) => {
                const Icon = PLATFORM_ICONS[acc.platform] || Share2;
                return (
                  <div key={acc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Icon className="h-5 w-5 text-gray-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{acc.account_name}</p>
                        <p className="text-xs text-gray-500">{acc.platform_display}</p>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[acc.status] || 'bg-gray-100'}`}>
                      {acc.status_display}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Users className="h-12 w-12 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Henuz bagli hesap yok</p>
            </div>
          )}
        </div>
      </div>

      {/* Platform Stats */}
      {stats?.posts_by_platform && (
        <div className="bg-white rounded-xl border p-5">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Platform Dagilimi</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.posts_by_platform).map(([platform, count]) => {
              const Icon = PLATFORM_ICONS[platform] || Share2;
              return (
                <div key={platform} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Icon className="h-6 w-6 text-gray-600" />
                  <div>
                    <p className="text-lg font-bold text-gray-900">{count as number}</p>
                    <p className="text-xs text-gray-500 capitalize">{platform}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Token Usage */}
      <div className="bg-white rounded-xl border p-5">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-gray-400" />
          <span className="text-sm text-gray-500">
            Toplam AI token kullanimi: <strong className="text-gray-900">{(stats?.total_tokens_used ?? 0).toLocaleString()}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
