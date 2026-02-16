'use client';

import { useState } from 'react';
import { useSocialPosts, useApprovePost, useRetryPost } from '@/hooks/useSocialData';
import { Link } from '@/i18n/navigation';
import { ArrowLeft, Search, Loader2, Instagram, Linkedin, Share2, CheckCircle, Clock, AlertTriangle, RefreshCw, ExternalLink } from 'lucide-react';

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
};

const PLATFORM_ICONS: Record<string, typeof Instagram> = {
  instagram: Instagram,
  linkedin: Linkedin,
};

export default function SocialPostsPage() {
  const [platform, setPlatform] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  const { data: posts, isLoading } = useSocialPosts({ platform, status: statusFilter, search });
  const approvePost = useApprovePost();
  const retryPost = useRetryPost();

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link href="/doctor/social" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Tum Postlar</h1>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Post ara..." value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border rounded-lg text-sm" />
        </div>
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Tum platformlar</option>
          <option value="instagram">Instagram</option>
          <option value="linkedin">LinkedIn</option>
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">Tum durumlar</option>
          {Object.entries(STATUS_CONFIG).map(([key, val]) => (
            <option key={key} value={key}>{val.label}</option>
          ))}
        </select>
      </div>

      {/* Posts */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-600" />
        </div>
      ) : posts && posts.length > 0 ? (
        <div className="space-y-3">
          {posts.map((post) => {
            const statusCfg = STATUS_CONFIG[post.status] || STATUS_CONFIG.draft;
            const Icon = PLATFORM_ICONS[post.platform] || Share2;
            return (
              <div key={post.id} className="bg-white rounded-xl border p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-gray-50 rounded-lg">
                    <Icon className="h-5 w-5 text-gray-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500 uppercase">{post.platform_display} / {post.format_display}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusCfg.color}`}>{statusCfg.label}</span>
                      {post.ai_generated && <span className="text-xs px-1.5 py-0.5 bg-purple-50 text-purple-600 rounded">AI</span>}
                    </div>
                    <p className="text-sm text-gray-900 line-clamp-2">{post.final_caption}</p>
                    {post.hashtags && post.hashtags.length > 0 && (
                      <p className="text-xs text-cyan-600 mt-1 truncate">{post.hashtags.join(' ')}</p>
                    )}
                    {post.publish_error && (
                      <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3" /> {post.publish_error}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      {post.campaign_title && <span>Kampanya: {post.campaign_title}</span>}
                      {post.scheduled_at && <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{new Date(post.scheduled_at).toLocaleString('tr')}</span>}
                      {post.published_at && <span className="flex items-center gap-1"><CheckCircle className="h-3 w-3 text-green-500" />{new Date(post.published_at).toLocaleString('tr')}</span>}
                    </div>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    {post.status === 'review' && (
                      <button onClick={() => approvePost.mutate(post.id)}
                        className="p-1.5 text-green-600 hover:bg-green-50 rounded" title="Onayla">
                        <CheckCircle className="h-4 w-4" />
                      </button>
                    )}
                    {post.status === 'failed' && (
                      <button onClick={() => retryPost.mutate(post.id)}
                        className="p-1.5 text-orange-600 hover:bg-orange-50 rounded" title="Tekrar Dene">
                        <RefreshCw className="h-4 w-4" />
                      </button>
                    )}
                    {post.platform_url && (
                      <a href={post.platform_url} target="_blank" rel="noopener noreferrer"
                        className="p-1.5 text-gray-400 hover:bg-gray-50 rounded" title="Platformda Gor">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">
          <Share2 className="h-16 w-16 mx-auto mb-4 opacity-20" />
          <p className="text-lg">Henuz post yok</p>
        </div>
      )}
    </div>
  );
}
