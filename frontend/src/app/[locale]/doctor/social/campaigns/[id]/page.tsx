'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useSocialCampaignDetail, useRegenerateSocialCampaign, useApproveAllPosts, useApprovePost } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { ArrowLeft, Loader2, CheckCircle, RefreshCw, Instagram, Linkedin, Share2, Clock, FileText, Eye, AlertTriangle } from 'lucide-react';

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  generating: { label: 'AI Uretiyor', color: 'bg-yellow-100 text-yellow-700' },
  review: { label: 'Onay Bekliyor', color: 'bg-blue-100 text-blue-700' },
  approved: { label: 'Onaylandi', color: 'bg-green-100 text-green-700' },
  scheduled: { label: 'Zamanlandi', color: 'bg-purple-100 text-purple-700' },
  publishing: { label: 'Yayinlaniyor', color: 'bg-orange-100 text-orange-700' },
  published: { label: 'Yayinlandi', color: 'bg-emerald-100 text-emerald-700' },
  failed: { label: 'Basarisiz', color: 'bg-red-100 text-red-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
  partially_approved: { label: 'Kismen Onayli', color: 'bg-indigo-100 text-indigo-700' },
  in_progress: { label: 'Yayinlaniyor', color: 'bg-orange-100 text-orange-700' },
  completed: { label: 'Tamamlandi', color: 'bg-emerald-100 text-emerald-700' },
};

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

export default function SocialCampaignDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [activeTab, setActiveTab] = useState<'posts' | 'schedule' | 'output'>('posts');

  const { data: campaign, isLoading } = useSocialCampaignDetail(id);
  const regenerate = useRegenerateSocialCampaign();
  const approveAll = useApproveAllPosts();
  const approvePost = useApprovePost();

  if (isLoading || !campaign) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-48" />
          <div className="h-64 bg-gray-200 rounded-xl" />
        </div>
      </div>
    );
  }

  const statusCfg = STATUS_CONFIG[campaign.status] || STATUS_CONFIG.draft;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Link href="/doctor/social/campaigns" className="text-gray-400 hover:text-gray-600">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-gray-900">{campaign.title}</h1>
              <span className={`text-xs px-2 py-0.5 rounded-full ${statusCfg.color}`}>{statusCfg.label}</span>
            </div>
            <p className="text-sm text-gray-500 mt-0.5">{campaign.theme}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {campaign.status !== 'generating' && (
            <button onClick={() => regenerate.mutate(id)} disabled={regenerate.isPending}
              className="flex items-center gap-1 px-3 py-2 bg-white border rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50">
              {regenerate.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Yeniden Uret
            </button>
          )}
          {campaign.status === 'review' && (
            <button onClick={() => approveAll.mutate(id)} disabled={approveAll.isPending}
              className="flex items-center gap-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 disabled:opacity-50">
              {approveAll.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
              Tumunu Onayla
            </button>
          )}
        </div>
      </div>

      {/* Generating Banner */}
      {campaign.status === 'generating' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-yellow-600" />
          <span className="text-sm text-yellow-700">AI icerik uretiyor, lutfen bekleyiniz...</span>
        </div>
      )}

      {/* Campaign Meta */}
      <div className="bg-white rounded-xl border p-5">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Platformlar</p>
            <div className="flex items-center gap-1 mt-1">
              {campaign.platforms.map(p => {
                const Icon = PLATFORM_ICONS[p] || Share2;
                return <Icon key={p} className="h-5 w-5 text-gray-700" />;
              })}
            </div>
          </div>
          <div>
            <p className="text-gray-500">Post/Platform</p>
            <p className="font-medium text-gray-900 mt-1">{campaign.posts_per_platform}</p>
          </div>
          <div>
            <p className="text-gray-500">Hafta</p>
            <p className="font-medium text-gray-900 mt-1">{campaign.week_start || '-'}</p>
          </div>
          <div>
            <p className="text-gray-500">Ton</p>
            <p className="font-medium text-gray-900 mt-1 capitalize">{campaign.tone}</p>
          </div>
          <div>
            <p className="text-gray-500">Token</p>
            <p className="font-medium text-gray-900 mt-1">{campaign.total_tokens.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Post Stats */}
      {campaign.post_stats && (
        <div className="grid grid-cols-3 md:grid-cols-7 gap-2">
          {Object.entries(campaign.post_stats).map(([key, val]) => (
            <div key={key} className="bg-white rounded-lg border p-3 text-center">
              <p className="text-xl font-bold text-gray-900">{val as number}</p>
              <p className="text-xs text-gray-500 capitalize">{key}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
        {[
          { key: 'posts' as const, label: 'Postlar', icon: FileText },
          { key: 'schedule' as const, label: 'Zamanlama', icon: Clock },
          { key: 'output' as const, label: 'AI Ciktisi', icon: Eye },
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition ${activeTab === tab.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
              <Icon className="h-4 w-4" /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'posts' && (
        <div className="space-y-3">
          {campaign.posts && campaign.posts.length > 0 ? (
            campaign.posts.map((post) => {
              const postStatus = STATUS_CONFIG[post.status] || STATUS_CONFIG.draft;
              const Icon = PLATFORM_ICONS[post.platform] || Share2;
              return (
                <div key={post.id} className="bg-white rounded-xl border p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <Icon className="h-5 w-5 text-gray-400 mt-0.5" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-gray-500 uppercase">{post.platform} / {post.format_display}</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${postStatus.color}`}>{postStatus.label}</span>
                        </div>
                        <p className="text-sm text-gray-900">{post.final_caption?.substring(0, 200)}{(post.final_caption?.length ?? 0) > 200 ? '...' : ''}</p>
                        {post.hashtags && post.hashtags.length > 0 && (
                          <p className="text-xs text-cyan-600 mt-1">{post.hashtags.join(' ')}</p>
                        )}
                        {post.publish_error && (
                          <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" /> {post.publish_error}
                          </p>
                        )}
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                          {post.scheduled_at && <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{new Date(post.scheduled_at).toLocaleString('tr')}</span>}
                          {post.published_at && <span className="flex items-center gap-1"><CheckCircle className="h-3 w-3 text-green-500" />{new Date(post.published_at).toLocaleString('tr')}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      {post.status === 'review' && (
                        <button onClick={() => approvePost.mutate(post.id)}
                          className="px-2 py-1 text-xs bg-green-50 text-green-700 rounded hover:bg-green-100">
                          Onayla
                        </button>
                      )}
                      {post.platform_url && (
                        <a href={post.platform_url} target="_blank" rel="noopener noreferrer"
                          className="px-2 py-1 text-xs bg-gray-50 text-gray-600 rounded hover:bg-gray-100">
                          Gor
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-12 text-gray-400">
              <FileText className="h-12 w-12 mx-auto mb-2 opacity-20" />
              <p className="text-sm">Henuz post olusturulmamis</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'schedule' && (
        <div className="bg-white rounded-xl border p-5">
          {campaign.schedule_output && Object.keys(campaign.schedule_output).length > 0 ? (
            <pre className="text-xs text-gray-700 overflow-auto max-h-96 whitespace-pre-wrap">
              {JSON.stringify(campaign.schedule_output, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-gray-400 text-center py-8">Zamanlama verisi henuz mevcut degil</p>
          )}
        </div>
      )}

      {activeTab === 'output' && (
        <div className="bg-white rounded-xl border p-5">
          {campaign.content_output && Object.keys(campaign.content_output).length > 0 ? (
            <pre className="text-xs text-gray-700 overflow-auto max-h-96 whitespace-pre-wrap">
              {JSON.stringify(campaign.content_output, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-gray-400 text-center py-8">AI ciktisi henuz mevcut degil</p>
          )}
        </div>
      )}
    </div>
  );
}
