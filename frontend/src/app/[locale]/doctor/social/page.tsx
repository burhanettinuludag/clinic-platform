'use client';

import { useState } from 'react';
import { useSocialDashboard, useSocialAccounts, useCreateSocialAccount, useValidateToken } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { Share2, Users, FileText, Calendar, CheckCircle, Clock, AlertTriangle, TrendingUp, Instagram, Linkedin, Plus, X, Loader2, RefreshCw, Trash2 } from 'lucide-react';
import api from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

const STATUS_COLORS: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  expired: 'bg-red-100 text-red-700',
  disconnected: 'bg-gray-100 text-gray-700',
  pending_review: 'bg-yellow-100 text-yellow-700',
};

const PLATFORM_OPTIONS = [
  { value: 'instagram', label: 'Instagram', icon: Instagram },
  { value: 'linkedin', label: 'LinkedIn', icon: Linkedin },
];

export default function SocialDashboardPage() {
  const { data: stats, isLoading } = useSocialDashboard();
  const { data: accounts } = useSocialAccounts();
  const createAccount = useCreateSocialAccount();
  const validateToken = useValidateToken();
  const queryClient = useQueryClient();

  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    platform: 'instagram',
    account_name: '',
    account_id: '',
    access_token: '',
    page_id: '',
    organization_urn: '',
  });

  const deleteAccount = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/social/accounts/${id}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-accounts'] });
      queryClient.invalidateQueries({ queryKey: ['social-dashboard'] });
    },
  });

  const handleAddAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createAccount.mutateAsync(formData);
      setShowAddModal(false);
      setFormData({ platform: 'instagram', account_name: '', account_id: '', access_token: '', page_id: '', organization_urn: '' });
      queryClient.invalidateQueries({ queryKey: ['social-dashboard'] });
    } catch {
      // Error handled by React Query
    }
  };

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
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">
                {stats?.active_accounts ?? 0} aktif / {stats?.total_accounts ?? 0} toplam
              </span>
              <button
                onClick={() => setShowAddModal(true)}
                className="flex items-center gap-1 px-3 py-1.5 bg-cyan-600 text-white text-sm rounded-lg hover:bg-cyan-700 transition"
              >
                <Plus className="h-4 w-4" />
                Hesap Ekle
              </button>
            </div>
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
                        <p className="text-xs text-gray-500">{acc.platform_display} - {acc.account_id}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-1 rounded-full ${STATUS_COLORS[acc.status] || 'bg-gray-100'}`}>
                        {acc.status_display}
                      </span>
                      <button
                        onClick={() => validateToken.mutate(acc.id)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 rounded transition"
                        title="Token Dogrula"
                      >
                        <RefreshCw className={`h-4 w-4 ${validateToken.isPending ? 'animate-spin' : ''}`} />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Bu hesabi silmek istediginize emin misiniz?')) {
                            deleteAccount.mutate(acc.id);
                          }
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-600 rounded transition"
                        title="Hesabi Sil"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <Users className="h-12 w-12 mx-auto mb-2 opacity-30" />
              <p className="text-sm mb-3">Henuz bagli hesap yok</p>
              <button
                onClick={() => setShowAddModal(true)}
                className="inline-flex items-center gap-1 px-4 py-2 bg-cyan-600 text-white text-sm rounded-lg hover:bg-cyan-700 transition"
              >
                <Plus className="h-4 w-4" />
                Hesap Ekle
              </button>
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

      {/* Hesap Ekle Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Sosyal Medya Hesabi Ekle</h2>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleAddAccount} className="p-6 space-y-4">
              {/* Platform Secimi */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                <div className="grid grid-cols-2 gap-3">
                  {PLATFORM_OPTIONS.map((opt) => {
                    const Icon = opt.icon;
                    const isSelected = formData.platform === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, platform: opt.value })}
                        className={`flex items-center gap-3 p-3 rounded-xl border-2 transition ${
                          isSelected
                            ? 'border-cyan-500 bg-cyan-50 text-cyan-700'
                            : 'border-gray-200 text-gray-600 hover:border-gray-300'
                        }`}
                      >
                        <Icon className={`h-6 w-6 ${isSelected ? 'text-cyan-600' : 'text-gray-400'}`} />
                        <span className="font-medium">{opt.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Hesap Adi */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Hesap Adi *</label>
                <input
                  type="text"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                  placeholder="Orn: @norosera"
                  className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  required
                />
              </div>

              {/* Hesap ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Platform Hesap ID *</label>
                <input
                  type="text"
                  value={formData.account_id}
                  onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
                  placeholder={formData.platform === 'instagram' ? 'Instagram Business Account ID' : 'LinkedIn Organization ID'}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  required
                />
              </div>

              {/* Access Token */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Access Token *</label>
                <textarea
                  value={formData.access_token}
                  onChange={(e) => setFormData({ ...formData, access_token: e.target.value })}
                  placeholder="Platform API access token"
                  rows={2}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 font-mono text-xs"
                  required
                />
              </div>

              {/* Platform-specific fields */}
              {formData.platform === 'instagram' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Facebook Page ID
                    <span className="text-gray-400 font-normal ml-1">(opsiyonel)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.page_id}
                    onChange={(e) => setFormData({ ...formData, page_id: e.target.value })}
                    placeholder="Facebook sayfa ID (Instagram Business icin)"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
              )}
              {formData.platform === 'linkedin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Organization URN
                    <span className="text-gray-400 font-normal ml-1">(opsiyonel)</span>
                  </label>
                  <input
                    type="text"
                    value={formData.organization_urn}
                    onChange={(e) => setFormData({ ...formData, organization_urn: e.target.value })}
                    placeholder="urn:li:organization:123456"
                    className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  />
                </div>
              )}

              {/* Hata mesaji */}
              {createAccount.isError && (
                <div className="text-sm text-red-600 bg-red-50 rounded-lg p-3">
                  Hesap eklenirken bir hata olustu. Bilgileri kontrol edip tekrar deneyin.
                </div>
              )}

              {/* Butonlar */}
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                  Iptal
                </button>
                <button
                  type="submit"
                  disabled={createAccount.isPending}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 disabled:opacity-50 transition"
                >
                  {createAccount.isPending ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> Ekleniyor...</>
                  ) : (
                    <><Plus className="h-4 w-4" /> Hesap Ekle</>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
