'use client';

import { useState } from 'react';
import { Link } from '@/i18n/navigation';
import {
  Megaphone, Plus, Search, Calendar, Loader2, Eye,
  Instagram, Linkedin, Twitter, ChevronRight, Sparkles,
  RotateCcw, CheckCircle, Clock, Archive, Send,
} from 'lucide-react';
import {
  useMarketingCampaigns,
  useCreateCampaign,
  type CreateCampaignPayload,
} from '@/hooks/useMarketingData';

// ─── Status Config ───
const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  generating: { label: 'Uretiyor', color: 'bg-blue-100 text-blue-700', icon: Loader2 },
  review: { label: 'Inceleme', color: 'bg-yellow-100 text-yellow-700', icon: Eye },
  approved: { label: 'Onaylandi', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  scheduled: { label: 'Planlandi', color: 'bg-purple-100 text-purple-700', icon: Clock },
  published: { label: 'Yayinlandi', color: 'bg-emerald-100 text-emerald-700', icon: Send },
  archived: { label: 'Arsivlendi', color: 'bg-gray-100 text-gray-600', icon: Archive },
};

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  instagram: Instagram,
  linkedin: Linkedin,
  twitter: Twitter,
};

// ─── Create Campaign Modal ───
function CreateCampaignModal({
  onClose,
  onCreate,
  isPending,
}: {
  onClose: () => void;
  onCreate: (payload: CreateCampaignPayload) => void;
  isPending: boolean;
}) {
  const [form, setForm] = useState<CreateCampaignPayload>({
    theme: '',
    week_start: new Date().toISOString().split('T')[0],
    platforms: ['instagram', 'linkedin', 'twitter'],
    language: 'tr',
    tone: 'educational',
    target_audience: 'patients',
  });

  const togglePlatform = (p: string) => {
    setForm((prev) => ({
      ...prev,
      platforms: prev.platforms?.includes(p)
        ? prev.platforms.filter((x) => x !== p)
        : [...(prev.platforms || []), p],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 overflow-y-auto py-8">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4 shadow-2xl">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-orange-500" />
          Yeni Kampanya Olustur
        </h3>

        {/* Theme */}
        <label className="block text-sm font-medium text-gray-700 mb-1">Tema *</label>
        <input
          type="text"
          placeholder="ornek: Migren Farkindalik Haftasi"
          value={form.theme}
          onChange={(e) => setForm({ ...form, theme: e.target.value })}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm mb-4 focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        />

        {/* Week Start */}
        <label className="block text-sm font-medium text-gray-700 mb-1">Hafta Baslangici *</label>
        <input
          type="date"
          value={form.week_start}
          onChange={(e) => setForm({ ...form, week_start: e.target.value })}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm mb-4 focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        />

        {/* Platforms */}
        <label className="block text-sm font-medium text-gray-700 mb-2">Platformlar</label>
        <div className="flex gap-2 mb-4">
          {['instagram', 'linkedin', 'twitter'].map((p) => {
            const Icon = PLATFORM_ICONS[p];
            const active = form.platforms?.includes(p);
            return (
              <button
                key={p}
                type="button"
                onClick={() => togglePlatform(p)}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? 'bg-orange-100 text-orange-700 border border-orange-300'
                    : 'bg-gray-100 text-gray-500 border border-gray-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            );
          })}
        </div>

        {/* Tone & Audience */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ton</label>
            <select
              value={form.tone}
              onChange={(e) => setForm({ ...form, tone: e.target.value })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
            >
              <option value="educational">Egitici</option>
              <option value="motivational">Motive Edici</option>
              <option value="empathetic">Empatik</option>
              <option value="professional">Profesyonel</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Hedef Kitle</label>
            <select
              value={form.target_audience}
              onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
            >
              <option value="patients">Hastalar</option>
              <option value="caregivers">Bakicilar</option>
              <option value="professionals">Saglik Profes.</option>
              <option value="general">Genel</option>
            </select>
          </div>
        </div>

        {/* Language */}
        <label className="block text-sm font-medium text-gray-700 mb-1">Dil</label>
        <select
          value={form.language}
          onChange={(e) => setForm({ ...form, language: e.target.value })}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm mb-6 focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        >
          <option value="tr">Turkce</option>
          <option value="en">English</option>
        </select>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Iptal
          </button>
          <button
            onClick={() => onCreate(form)}
            disabled={!form.theme.trim() || isPending}
            className="flex-1 rounded-lg bg-orange-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-orange-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Olusturuluyor...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                AI ile Olustur
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ───
export default function MarketingPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showModal, setShowModal] = useState(false);

  const { data: campaigns, isLoading } = useMarketingCampaigns(
    statusFilter ? { status: statusFilter } : undefined,
  );
  const createMutation = useCreateCampaign();

  const filteredCampaigns = (campaigns || []).filter((c) =>
    !searchQuery || c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.theme.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const handleCreate = (payload: CreateCampaignPayload) => {
    createMutation.mutate(payload, {
      onSuccess: () => setShowModal(false),
    });
  };

  // Stats
  const stats = {
    total: campaigns?.length || 0,
    generating: campaigns?.filter((c) => c.status === 'generating').length || 0,
    review: campaigns?.filter((c) => c.status === 'review').length || 0,
    approved: campaigns?.filter((c) => c.status === 'approved').length || 0,
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Megaphone className="h-6 w-6 text-orange-600" />
            Marketing Kampanyalari
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            AI destekli sosyal medya icerik uretimi ve yonetimi
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 rounded-lg bg-orange-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-orange-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Yeni Kampanya
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Toplam', value: stats.total, icon: Megaphone, color: 'text-orange-500' },
          { label: 'Uretiyor', value: stats.generating, icon: Loader2, color: 'text-blue-500' },
          { label: 'Inceleme', value: stats.review, icon: Eye, color: 'text-yellow-500' },
          { label: 'Onaylandi', value: stats.approved, icon: CheckCircle, color: 'text-green-500' },
        ].map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="bg-white rounded-xl border p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{s.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{s.value}</p>
                </div>
                <Icon className={`h-8 w-8 ${s.color}`} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Kampanya ara..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        >
          <option value="">Tum Durumlar</option>
          <option value="generating">Uretiyor</option>
          <option value="review">Inceleme</option>
          <option value="approved">Onaylandi</option>
          <option value="scheduled">Planlandi</option>
          <option value="published">Yayinlandi</option>
          <option value="archived">Arsivlendi</option>
        </select>
      </div>

      {/* Campaign List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
        </div>
      ) : filteredCampaigns.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-xl border">
          <Megaphone className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 text-sm">Henuz kampanya yok.</p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-3 text-orange-600 text-sm font-medium hover:underline"
          >
            Ilk kampanyanizi olusturun
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredCampaigns.map((campaign) => {
            const statusCfg = STATUS_CONFIG[campaign.status] || STATUS_CONFIG.generating;
            const StatusIcon = statusCfg.icon;
            return (
              <Link
                key={campaign.id}
                href={`/doctor/marketing/${campaign.id}`}
                className="block bg-white rounded-xl border p-4 hover:border-orange-300 hover:shadow-sm transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {campaign.title}
                      </h3>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusCfg.color}`}>
                        <StatusIcon className={`h-3 w-3 ${campaign.status === 'generating' ? 'animate-spin' : ''}`} />
                        {statusCfg.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 truncate mb-2">{campaign.theme}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        {campaign.week_start}
                      </span>
                      <div className="flex items-center gap-1">
                        {(campaign.platforms || []).map((p) => {
                          const PIcon = PLATFORM_ICONS[p];
                          return PIcon ? <PIcon key={p} className="h-3.5 w-3.5" /> : null;
                        })}
                      </div>
                      {campaign.total_tokens > 0 && (
                        <span>{campaign.total_tokens.toLocaleString()} token</span>
                      )}
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-orange-500 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <CreateCampaignModal
          onClose={() => setShowModal(false)}
          onCreate={handleCreate}
          isPending={createMutation.isPending}
        />
      )}
    </div>
  );
}
