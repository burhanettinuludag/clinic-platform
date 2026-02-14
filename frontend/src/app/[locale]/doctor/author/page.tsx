'use client';

import { useState } from 'react';
import { FileText, Newspaper, BarChart3, Plus, Send, Archive, RotateCcw, Trash2, Eye, CheckCircle, Clock, AlertTriangle, Star, Shield, Loader2, Search, Filter, ChevronDown, Zap, BookOpen } from 'lucide-react';
import { useAuthorStats, useAuthorArticles, useAuthorNews, useArticleTransition, useNewsTransition, useDeleteArticle, useArticlePipeline } from '@/hooks/useAuthorData';
import type { AuthorArticle, AuthorNews } from '@/hooks/useAuthorData';

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.draft;
  return <span className={'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ' + cfg.color}>{cfg.label}</span>;
}

function formatDate(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
}

type TabId = 'stats' | 'articles' | 'news';

export default function AuthorPanelPage() {
  const [activeTab, setActiveTab] = useState<TabId>('stats');
  const tabs: { id: TabId; label: string }[] = [
    { id: 'stats', label: 'Genel Bakis' },
    { id: 'articles', label: 'Makaleler' },
    { id: 'news', label: 'Haberler' },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-indigo-600" />Yazar Paneli
        </h1>
        <p className="mt-1 text-sm text-gray-500">Makalelerinizi ve haberlerinizi yonetin.</p>
      </div>
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {tabs.map((tab) => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className={'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ' + (activeTab === tab.id ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {tab.label}
          </button>
        ))}
      </div>
      {activeTab === 'stats' && <StatsTab />}
      {activeTab === 'articles' && <ArticlesTab />}
      {activeTab === 'news' && <NewsTab />}
    </div>
  );
}

function StatsTab() {
  const { data: stats, isLoading, error } = useAuthorStats();
  if (isLoading) return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-indigo-400" /></div>;
  if (error || !stats) return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center"><p className="text-sm text-red-700">Istatistikler yuklenemedi. Yazar profiliniz olmayabilir.</p></div>;

  const { author, articles, news, recent_reviews } = stats;
  return (
    <div className="space-y-6">
      <div className="rounded-xl border bg-gradient-to-r from-indigo-50 to-purple-50 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{author.name}</h2>
            <p className="text-sm text-gray-600 mt-1">Seviye: <span className="font-medium text-indigo-700">{author.level_display}</span></p>
          </div>
          <div className="flex gap-2">
            {author.is_verified && <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700"><Shield className="h-3.5 w-3.5" />Dogrulanmis</span>}
            {author.can_auto_publish && <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-700"><Zap className="h-3.5 w-3.5" />Oto Yayin</span>}
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          {[['Toplam Makale', author.total_articles], ['Goruntulenme', author.total_views], ['Ort. Puan', author.average_rating.toFixed(1)], ['Seviye', author.level + ' / 4']].map(([label, val]) => (
            <div key={String(label)} className="rounded-lg bg-white/80 border p-3">
              <p className="text-xs text-gray-500">{label}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{val}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[{ title: 'Makaleler', d: articles }, { title: 'Haberler', d: news }].map(({ title, d }) => (
          <div key={title} className="rounded-xl border bg-white p-6">
            <h3 className="font-semibold text-gray-900 mb-3">{title}</h3>
            <p className="text-3xl font-bold text-gray-900 mb-4">{d.total}</p>
            <div className="space-y-2">
              {Object.entries(d.by_status).map(([st, count]) => (
                <div key={st} className="flex items-center justify-between"><StatusBadge status={st} /><span className="text-sm font-medium text-gray-700">{count}</span></div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {recent_reviews.length > 0 && (
        <div className="rounded-xl border bg-white p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><Star className="h-4 w-4 text-yellow-500" />Son Degerlendirmeler</h3>
          <div className="space-y-3">
            {recent_reviews.map((r) => (
              <div key={r.id} className="flex items-center justify-between rounded-lg border p-3">
                <span className="text-sm text-gray-600">{r.review_type_display} - {r.reviewer_name}</span>
                <div className="flex items-center gap-3">
                  <span className={'text-lg font-bold ' + (r.overall_score >= 70 ? 'text-green-600' : r.overall_score >= 50 ? 'text-yellow-600' : 'text-red-600')}>{r.overall_score}</span>
                  <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (r.decision === 'publish' ? 'bg-green-100 text-green-700' : r.decision === 'revise' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700')}>{r.decision_display}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ArticlesTab() {
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const { data: articles, isLoading } = useAuthorArticles({ status: statusFilter || undefined, search: searchQuery || undefined });
  const transitionMut = useArticleTransition();
  const deleteMut = useDeleteArticle();
  const pipelineMut = useArticlePipeline();

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex gap-2 items-center">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input type="text" placeholder="Makale ara..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-60" />
          </div>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-indigo-500 focus:outline-none bg-white">
            <option value="">Tum Durumlar</option>
            <option value="draft">Taslak</option>
            <option value="published">Yayinda</option>
            <option value="archived">Arsiv</option>
          </select>
        </div>
        <a href="content" className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
          <Plus className="h-4 w-4" />AI ile Icerik Uret
        </a>
      </div>
      {isLoading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-indigo-400" /></div>
       : !articles?.length ? <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center"><FileText className="h-10 w-10 text-gray-300 mx-auto mb-3" /><p className="text-sm text-gray-500">Henuz makaleniz yok.</p></div>
       : <div className="space-y-3">{articles.map((a) => (
          <div key={a.id} className="rounded-lg border bg-white p-4 hover:shadow-sm transition-shadow">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate">{a.title_tr || 'Basliksiz'}</h3>
                {a.excerpt_tr && <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{a.excerpt_tr}</p>}
                <div className="flex items-center gap-3 mt-2">
                  <StatusBadge status={a.status} />
                  {a.category_name && <span className="text-xs text-gray-400">{a.category_name}</span>}
                  <span className="text-xs text-gray-400">{formatDate(a.updated_at)}</span>
                </div>
              </div>
              <div className="flex gap-1">
                {a.status === 'draft' && <>
                  <button onClick={() => transitionMut.mutate({ id: a.id, action: 'submit_for_review' })} disabled={transitionMut.isPending}
                    className="rounded px-2 py-1 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100" title="Yayina Gonder"><Send className="h-3.5 w-3.5" /></button>
                  <button onClick={() => pipelineMut.mutate({ id: a.id, pipeline: 'seo_optimize' })}
                    className="rounded px-2 py-1 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100" title="SEO Optimize"><Zap className="h-3.5 w-3.5" /></button>
                  <button onClick={() => { if(confirm('Taslagi silmek istediginize emin misiniz?')) deleteMut.mutate(a.id); }}
                    className="rounded px-2 py-1 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100" title="Sil"><Trash2 className="h-3.5 w-3.5" /></button>
                </>}
                {a.status === 'published' && <button onClick={() => transitionMut.mutate({ id: a.id, action: 'archive' })} disabled={transitionMut.isPending}
                  className="rounded px-2 py-1 text-xs font-medium text-gray-700 bg-gray-50 hover:bg-gray-100" title="Arsivle"><Archive className="h-3.5 w-3.5" /></button>}
                {a.status === 'archived' && <button onClick={() => transitionMut.mutate({ id: a.id, action: 'revert_to_draft' })} disabled={transitionMut.isPending}
                  className="rounded px-2 py-1 text-xs font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100" title="Taslaga Al"><RotateCcw className="h-3.5 w-3.5" /></button>}
              </div>
            </div>
          </div>
        ))}</div>}
      {pipelineMut.isSuccess && pipelineMut.data && <div className="rounded-lg border border-green-200 bg-green-50 p-4"><p className="text-sm font-medium text-green-800">Pipeline tamamlandi: {pipelineMut.data.steps_completed.length} adim, {(pipelineMut.data.duration_ms / 1000).toFixed(1)}s</p></div>}
    </div>
  );
}

function NewsTab() {
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const { data: news, isLoading } = useAuthorNews({ status: statusFilter || undefined, search: searchQuery || undefined });
  const transitionMut = useNewsTransition();

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Haber ara..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 w-60" />
        </div>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:border-indigo-500 focus:outline-none bg-white">
          <option value="">Tum Durumlar</option>
          <option value="draft">Taslak</option>
          <option value="review">Incelemede</option>
          <option value="revision">Duzeltme</option>
          <option value="approved">Onaylandi</option>
          <option value="published">Yayinda</option>
          <option value="archived">Arsiv</option>
        </select>
      </div>
      {isLoading ? <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-indigo-400" /></div>
       : !news?.length ? <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center"><Newspaper className="h-10 w-10 text-gray-300 mx-auto mb-3" /><p className="text-sm text-gray-500">Henuz haberiniz yok.</p></div>
       : <div className="space-y-3">{news.map((n) => (
          <div key={n.id} className="rounded-lg border bg-white p-4 hover:shadow-sm transition-shadow">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-gray-900 truncate">{n.title_tr || 'Basliksiz'}</h3>
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  <StatusBadge status={n.status} />
                  <span className="text-xs text-gray-500">{n.category_display}</span>
                  <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (n.priority === 'urgent' ? 'bg-red-100 text-red-700' : n.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600')}>{n.priority_display}</span>
                  {n.is_auto_generated && <span className="text-xs text-purple-500">AI</span>}
                  <span className="text-xs text-gray-400">{formatDate(n.created_at)}</span>
                </div>
              </div>
              <div className="flex gap-1">
                {(n.status === 'draft' || n.status === 'revision') && <button onClick={() => transitionMut.mutate({ id: n.id, action: 'submit_for_review' })} disabled={transitionMut.isPending}
                  className="rounded px-2 py-1 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100" title="Incelemeye Gonder"><Send className="h-3.5 w-3.5" /></button>}
                {n.status === 'published' && <button onClick={() => transitionMut.mutate({ id: n.id, action: 'archive' })} disabled={transitionMut.isPending}
                  className="rounded px-2 py-1 text-xs font-medium text-gray-700 bg-gray-50 hover:bg-gray-100" title="Arsivle"><Archive className="h-3.5 w-3.5" /></button>}
                {n.status === 'archived' && <button onClick={() => transitionMut.mutate({ id: n.id, action: 'revert_to_draft' })} disabled={transitionMut.isPending}
                  className="rounded px-2 py-1 text-xs font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100" title="Taslaga Al"><RotateCcw className="h-3.5 w-3.5" /></button>}
                {(n.status === 'review' || n.status === 'approved') && <span className="text-xs text-gray-400 px-2 py-1">Onay bekleniyor</span>}
              </div>
            </div>
          </div>
        ))}</div>}
    </div>
  );
}
