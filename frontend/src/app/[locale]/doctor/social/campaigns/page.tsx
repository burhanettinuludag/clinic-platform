'use client';

import { useState } from 'react';
import { useSocialCampaigns, useCreateSocialCampaign } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { Plus, Search, ArrowLeft, Loader2, Instagram, Linkedin, Share2 } from 'lucide-react';

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  generating: { label: 'AI Uretiyor', color: 'bg-yellow-100 text-yellow-700' },
  review: { label: 'Onay Bekliyor', color: 'bg-blue-100 text-blue-700' },
  partially_approved: { label: 'Kismen Onayli', color: 'bg-indigo-100 text-indigo-700' },
  approved: { label: 'Onayli', color: 'bg-green-100 text-green-700' },
  scheduled: { label: 'Zamanlandi', color: 'bg-purple-100 text-purple-700' },
  in_progress: { label: 'Yayinlaniyor', color: 'bg-orange-100 text-orange-700' },
  completed: { label: 'Tamamlandi', color: 'bg-emerald-100 text-emerald-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

export default function SocialCampaignsPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);

  const { data: campaigns, isLoading } = useSocialCampaigns({ status: statusFilter, search });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/doctor/social" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Kampanyalar</h1>
        </div>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 text-sm">
          <Plus className="h-4 w-4" /> Yeni Kampanya
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Ara..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border rounded-lg text-sm" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Tum durumlar</option>
          {Object.entries(STATUS_CONFIG).map(([key, val]) => (
            <option key={key} value={key}>{val.label}</option>
          ))}
        </select>
      </div>

      {/* Campaign List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-600" />
        </div>
      ) : campaigns && campaigns.length > 0 ? (
        <div className="grid gap-4">
          {campaigns.map((c) => {
            const statusCfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.draft;
            return (
              <Link key={c.id} href={`/doctor/social/campaigns/${c.id}`}
                className="bg-white rounded-xl border p-5 hover:shadow-md transition-shadow block">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-lg font-semibold text-gray-900">{c.title}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusCfg.color}`}>{statusCfg.label}</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">{c.theme}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <div className="flex items-center gap-1">
                        {c.platforms.map(p => {
                          const Icon = PLATFORM_ICONS[p] || Share2;
                          return <Icon key={p} className="h-4 w-4" />;
                        })}
                      </div>
                      {c.week_start && <span>Hafta: {c.week_start}</span>}
                      <span>{c.post_stats?.total ?? 0} post</span>
                      {c.total_tokens > 0 && <span>{c.total_tokens.toLocaleString()} token</span>}
                    </div>
                  </div>
                  <div className="text-right text-xs text-gray-400">
                    {new Date(c.created_at).toLocaleDateString('tr')}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">
          <Share2 className="h-16 w-16 mx-auto mb-4 opacity-20" />
          <p className="text-lg">Henuz kampanya yok</p>
          <p className="text-sm mt-1">Yeni bir kampanya olusturarak baslayabilirsiniz</p>
        </div>
      )}

      {/* Create Modal */}
      {showCreate && <CreateCampaignModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}

function CreateCampaignModal({ onClose }: { onClose: () => void }) {
  const createMutation = useCreateSocialCampaign();
  const [form, setForm] = useState({
    theme: '',
    title: '',
    platforms: ['instagram', 'linkedin'] as string[],
    posts_per_platform: 3,
    language: 'tr',
    tone: 'educational',
    target_audience: 'patients',
    week_start: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createMutation.mutateAsync(form);
    onClose();
  };

  const togglePlatform = (p: string) => {
    setForm(prev => ({
      ...prev,
      platforms: prev.platforms.includes(p) ? prev.platforms.filter(x => x !== p) : [...prev.platforms, p],
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl w-full max-w-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Yeni Kampanya</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tema *</label>
            <input type="text" value={form.theme} onChange={(e) => setForm({ ...form, theme: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Migren tetikleyicileri" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Baslik</label>
            <input type="text" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg text-sm" placeholder="Otomatik olusturulur" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Platformlar</label>
            <div className="flex gap-2">
              {['instagram', 'linkedin'].map(p => (
                <button key={p} type="button" onClick={() => togglePlatform(p)}
                  className={`px-3 py-1.5 rounded-lg text-sm border ${form.platforms.includes(p) ? 'bg-cyan-50 border-cyan-300 text-cyan-700' : 'bg-white text-gray-500'}`}>
                  {p === 'instagram' ? <Instagram className="h-4 w-4 inline mr-1" /> : <Linkedin className="h-4 w-4 inline mr-1" />}
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hafta Baslangici</label>
              <input type="date" value={form.week_start} onChange={(e) => setForm({ ...form, week_start: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Post/Platform</label>
              <input type="number" min="1" max="10" value={form.posts_per_platform}
                onChange={(e) => setForm({ ...form, posts_per_platform: parseInt(e.target.value) || 3 })}
                className="w-full px-3 py-2 border rounded-lg text-sm" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ton</label>
              <select value={form.tone} onChange={(e) => setForm({ ...form, tone: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm bg-white">
                <option value="educational">Egitici</option>
                <option value="motivational">Motivasyon</option>
                <option value="informational">Bilgilendirici</option>
                <option value="empathetic">Empatik</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hedef Kitle</label>
              <select value={form.target_audience} onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm bg-white">
                <option value="patients">Hastalar</option>
                <option value="caregivers">Bakim Verenler</option>
                <option value="general">Genel</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Dil</label>
              <select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg text-sm bg-white">
                <option value="tr">Turkce</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900">Iptal</button>
            <button type="submit" disabled={createMutation.isPending || !form.theme}
              className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm hover:bg-cyan-700 disabled:opacity-50 flex items-center gap-2">
              {createMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Olustur & AI Uret
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
