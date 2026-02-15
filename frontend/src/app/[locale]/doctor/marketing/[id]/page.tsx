'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Megaphone, ArrowLeft, Loader2, CheckCircle, RotateCcw,
  Instagram, Linkedin, Twitter, Calendar, Eye, FileText,
  Palette, Clock, Edit2, Save, X, AlertTriangle, Sparkles,
  Image, Hash, Video, Send, Archive,
} from 'lucide-react';
import {
  useMarketingCampaignDetail,
  useUpdateCampaign,
  useApproveCampaign,
  useRegenerateCampaign,
} from '@/hooks/useMarketingData';
import { Link } from '@/i18n/navigation';

// ─── Status Config ───
const STATUS_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  generating: { label: 'AI Uretiyor...', color: 'text-blue-700', bgColor: 'bg-blue-50 border-blue-200' },
  review: { label: 'Inceleme Bekliyor', color: 'text-yellow-700', bgColor: 'bg-yellow-50 border-yellow-200' },
  approved: { label: 'Onaylandi', color: 'text-green-700', bgColor: 'bg-green-50 border-green-200' },
  scheduled: { label: 'Planlandi', color: 'text-purple-700', bgColor: 'bg-purple-50 border-purple-200' },
  published: { label: 'Yayinlandi', color: 'text-emerald-700', bgColor: 'bg-emerald-50 border-emerald-200' },
  archived: { label: 'Arsivlendi', color: 'text-gray-600', bgColor: 'bg-gray-50 border-gray-200' },
};

const PLATFORM_ICONS: Record<string, React.ElementType> = {
  instagram: Instagram,
  linkedin: Linkedin,
  twitter: Twitter,
};

const PLATFORM_COLORS: Record<string, string> = {
  instagram: 'from-pink-500 to-purple-500',
  linkedin: 'from-blue-600 to-blue-800',
  twitter: 'from-sky-400 to-sky-600',
};

type TabId = 'content' | 'visuals' | 'schedule';

// ─── Post Card ───
function PostCard({ post, platform }: { post: Record<string, unknown>; platform: string }) {
  const PIcon = PLATFORM_ICONS[platform] || FileText;
  const gradientClass = PLATFORM_COLORS[platform] || 'from-gray-400 to-gray-600';

  return (
    <div className="bg-white rounded-lg border p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-center gap-2 mb-3">
        <div className={`p-1.5 rounded-lg bg-gradient-to-br ${gradientClass}`}>
          <PIcon className="h-3.5 w-3.5 text-white" />
        </div>
        <span className="text-sm font-medium text-gray-700 capitalize">{platform}</span>
        {post.post_type && (
          <span className="text-xs bg-gray-100 text-gray-500 rounded-full px-2 py-0.5">
            {String(post.post_type)}
          </span>
        )}
      </div>

      {/* Content */}
      <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-line mb-3">
        {String(post.content || post.text || post.caption || '')}
      </p>

      {/* Hashtags */}
      {post.hashtags && Array.isArray(post.hashtags) && (
        <div className="flex flex-wrap gap-1 mb-2">
          {(post.hashtags as string[]).map((tag: string, i: number) => (
            <span key={i} className="text-xs text-blue-600 bg-blue-50 rounded px-1.5 py-0.5 flex items-center gap-0.5">
              <Hash className="h-2.5 w-2.5" />
              {tag.replace('#', '')}
            </span>
          ))}
        </div>
      )}

      {/* Video Script */}
      {post.video_script && (
        <div className="mt-2 p-2 bg-purple-50 rounded-lg border border-purple-100">
          <p className="text-xs font-medium text-purple-700 flex items-center gap-1 mb-1">
            <Video className="h-3 w-3" />
            Video Script
          </p>
          <p className="text-xs text-purple-600">{String(post.video_script)}</p>
        </div>
      )}
    </div>
  );
}

// ─── Visual Brief Card ───
function BriefCard({ brief }: { brief: Record<string, unknown> }) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center gap-2 mb-3">
        <Image className="h-4 w-4 text-pink-500" />
        <span className="text-sm font-medium text-gray-700">
          {String(brief.platform || 'Gorsel Brief')}
        </span>
      </div>

      {brief.layout && (
        <p className="text-xs text-gray-500 mb-2">
          <span className="font-medium">Layout:</span> {String(brief.layout)}
        </p>
      )}

      {brief.colors && Array.isArray(brief.colors) && (
        <div className="flex gap-1 mb-2">
          {(brief.colors as string[]).map((color: string, i: number) => (
            <div
              key={i}
              className="w-6 h-6 rounded-full border border-gray-200"
              style={{ backgroundColor: color }}
              title={color}
            />
          ))}
        </div>
      )}

      {brief.text_overlay && (
        <p className="text-xs text-gray-600 mb-1">
          <span className="font-medium">Metin:</span> {String(brief.text_overlay)}
        </p>
      )}

      {brief.style_notes && (
        <p className="text-xs text-gray-500 italic">{String(brief.style_notes)}</p>
      )}

      {brief.description && (
        <p className="text-xs text-gray-600 mt-1">{String(brief.description)}</p>
      )}
    </div>
  );
}

// ─── Schedule Card ───
function ScheduleCard({ entry }: { entry: Record<string, unknown> }) {
  const PIcon = PLATFORM_ICONS[String(entry.platform || '')] || Calendar;

  return (
    <div className="flex items-center gap-3 bg-white rounded-lg border p-3">
      <div className="text-center min-w-[60px]">
        <p className="text-xs text-gray-400">{String(entry.day || entry.date || '')}</p>
        <p className="text-sm font-bold text-gray-900">{String(entry.time || '')}</p>
      </div>
      <div className="h-10 w-px bg-gray-200" />
      <PIcon className="h-4 w-4 text-gray-400" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-800 truncate">{String(entry.title || entry.content_summary || '')}</p>
        <p className="text-xs text-gray-400">{String(entry.platform || '')}</p>
      </div>
    </div>
  );
}

// ─── Main Detail Page ───
export default function MarketingCampaignDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [activeTab, setActiveTab] = useState<TabId>('content');
  const [editorNotes, setEditorNotes] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const { data: campaign, isLoading } = useMarketingCampaignDetail(id);
  const updateMutation = useUpdateCampaign();
  const approveMutation = useApproveCampaign();
  const regenerateMutation = useRegenerateCampaign();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="p-6 text-center">
        <AlertTriangle className="h-12 w-12 text-yellow-400 mx-auto mb-3" />
        <p className="text-gray-500">Kampanya bulunamadi.</p>
        <Link href="/doctor/marketing" className="mt-2 text-orange-600 hover:underline text-sm">
          Listeye don
        </Link>
      </div>
    );
  }

  const statusCfg = STATUS_CONFIG[campaign.status] || STATUS_CONFIG.generating;

  // Extract posts by platform from content_output
  const contentOutput = campaign.content_output || {};
  const platformPosts: Record<string, Record<string, unknown>[]> = {};
  for (const platform of ['instagram', 'linkedin', 'twitter']) {
    const key = `${platform}_posts`;
    if (contentOutput[key] && Array.isArray(contentOutput[key])) {
      platformPosts[platform] = contentOutput[key] as Record<string, unknown>[];
    }
  }
  // Also check for flat posts array
  if (contentOutput.posts && Array.isArray(contentOutput.posts)) {
    for (const post of contentOutput.posts as Record<string, unknown>[]) {
      const p = String(post.platform || 'other');
      if (!platformPosts[p]) platformPosts[p] = [];
      platformPosts[p].push(post);
    }
  }

  // Extract visual briefs
  const visualBriefs = campaign.visual_briefs || {};
  const briefsList: Record<string, unknown>[] = Array.isArray(visualBriefs)
    ? visualBriefs
    : (visualBriefs as Record<string, unknown>).briefs
      ? ((visualBriefs as Record<string, unknown>).briefs as Record<string, unknown>[])
      : [];

  // Extract schedule
  const scheduleData = campaign.schedule || {};
  const scheduleEntries: Record<string, unknown>[] = Array.isArray(scheduleData)
    ? scheduleData
    : (scheduleData as Record<string, unknown>).schedule
      ? ((scheduleData as Record<string, unknown>).schedule as Record<string, unknown>[])
      : (scheduleData as Record<string, unknown>).entries
        ? ((scheduleData as Record<string, unknown>).entries as Record<string, unknown>[])
        : [];

  const totalPosts = Object.values(platformPosts).reduce((sum, arr) => sum + arr.length, 0);

  const handleSaveNotes = () => {
    updateMutation.mutate(
      { id, editor_notes: editorNotes },
      { onSuccess: () => setIsEditing(false) },
    );
  };

  const tabs: { id: TabId; label: string; icon: React.ElementType; count?: number }[] = [
    { id: 'content', label: 'Icerikler', icon: FileText, count: totalPosts },
    { id: 'visuals', label: 'Gorsel Brief', icon: Palette, count: briefsList.length },
    { id: 'schedule', label: 'Yayin Plani', icon: Clock, count: scheduleEntries.length },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Back + Header */}
      <Link
        href="/doctor/marketing"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-orange-600 mb-4 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Kampanyalara Don
      </Link>

      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Megaphone className="h-6 w-6 text-orange-600" />
            {campaign.title}
          </h1>
          <p className="text-sm text-gray-500 mt-1">{campaign.theme}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              Hafta: {campaign.week_start}
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

        {/* Status + Actions */}
        <div className="flex flex-col items-end gap-2">
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium border ${statusCfg.bgColor} ${statusCfg.color}`}>
            {campaign.status === 'generating' && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            {statusCfg.label}
          </span>

          <div className="flex gap-2">
            {campaign.status === 'review' && (
              <button
                onClick={() => approveMutation.mutate(id)}
                disabled={approveMutation.isPending}
                className="flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {approveMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle className="h-4 w-4" />
                )}
                Onayla
              </button>
            )}
            {['review', 'approved'].includes(campaign.status) && (
              <button
                onClick={() => regenerateMutation.mutate(id)}
                disabled={regenerateMutation.isPending}
                className="flex items-center gap-1.5 rounded-lg border border-orange-300 px-3 py-2 text-sm font-medium text-orange-700 hover:bg-orange-50 disabled:opacity-50 transition-colors"
              >
                {regenerateMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RotateCcw className="h-4 w-4" />
                )}
                Yeniden Uret
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Generating Status Banner */}
      {campaign.status === 'generating' && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <div>
            <p className="text-sm font-medium text-blue-800">AI icerik uretiyor...</p>
            <p className="text-xs text-blue-600 mt-0.5">
              3 adimli pipeline calisiyor: Icerik &rarr; Gorsel Brief &rarr; Yayin Plani
            </p>
          </div>
        </div>
      )}

      {/* Editor Notes */}
      {(campaign.editor_notes || campaign.status === 'review') && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-amber-800 flex items-center gap-1.5">
              <Edit2 className="h-4 w-4" />
              Editor Notlari
            </h3>
            {!isEditing && campaign.status === 'review' && (
              <button
                onClick={() => { setEditorNotes(campaign.editor_notes || ''); setIsEditing(true); }}
                className="text-xs text-amber-600 hover:underline"
              >
                Duzenle
              </button>
            )}
          </div>
          {isEditing ? (
            <div>
              <textarea
                value={editorNotes}
                onChange={(e) => setEditorNotes(e.target.value)}
                rows={3}
                className="w-full rounded-lg border border-amber-300 px-3 py-2 text-sm focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
                placeholder="Notlarinizi yazin..."
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50"
                >
                  <X className="h-3 w-3" />
                  Iptal
                </button>
                <button
                  onClick={handleSaveNotes}
                  disabled={updateMutation.isPending}
                  className="flex items-center gap-1 rounded-lg bg-amber-600 px-3 py-1.5 text-xs text-white hover:bg-amber-700 disabled:opacity-50"
                >
                  <Save className="h-3 w-3" />
                  Kaydet
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-amber-700">
              {campaign.editor_notes || 'Henuz not eklenmedi.'}
            </p>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-orange-600 text-orange-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              {tab.count !== undefined && tab.count > 0 && (
                <span className="ml-1 text-xs bg-gray-100 text-gray-600 rounded-full px-1.5 py-0.5">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'content' && (
        <div>
          {totalPosts === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border">
              <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">
                {campaign.status === 'generating'
                  ? 'Icerikler uretiliyor...'
                  : 'Henuz icerik yok.'}
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(platformPosts).map(([platform, posts]) => (
                <div key={platform}>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2 capitalize">
                    {PLATFORM_ICONS[platform] && (() => {
                      const PIcon = PLATFORM_ICONS[platform];
                      return <PIcon className="h-4 w-4" />;
                    })()}
                    {platform} ({posts.length} post)
                  </h3>
                  <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {posts.map((post, idx) => (
                      <PostCard key={idx} post={post} platform={platform} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'visuals' && (
        <div>
          {briefsList.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border">
              <Palette className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">
                {campaign.status === 'generating'
                  ? 'Gorsel briefler olusturuluyor...'
                  : 'Gorsel brief bulunamadi.'}
              </p>
            </div>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {briefsList.map((brief, idx) => (
                <BriefCard key={idx} brief={brief} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'schedule' && (
        <div>
          {scheduleEntries.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border">
              <Clock className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500 text-sm">
                {campaign.status === 'generating'
                  ? 'Yayin plani olusturuluyor...'
                  : 'Yayin plani bulunamadi.'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {scheduleEntries.map((entry, idx) => (
                <ScheduleCard key={idx} entry={entry} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
