'use client';

import { useState } from 'react';
import { ShieldCheck, Inbox, FileText, Newspaper, Users, CheckCircle, XCircle, Send, Archive, RotateCcw, AlertTriangle, Loader2, Search, Shield } from 'lucide-react';
import { useReviewQueueStats, useEditorArticles, useEditorNews, useEditorArticleTransition, useEditorNewsTransition, useEditorAuthors, useVerifyAuthor } from '@/hooks/useEditorData';
import type { EditorArticle, EditorNews, EditorAuthor } from '@/hooks/useEditorData';

const STATUS_CFG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

function SBadge({ status }: { status: string }) {
  const c = STATUS_CFG[status] || STATUS_CFG.draft;
  return <span className={'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ' + c.color}>{c.label}</span>;
}

function fmtD(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
}

type TabId = 'queue' | 'articles' | 'news' | 'authors';

export default function EditorPanelPage() {
  const [tab, setTab] = useState<TabId>('queue');
  const tabs: { id: TabId; label: string }[] = [
    { id: 'queue', label: 'Inceleme Kuyrugu' },
    { id: 'articles', label: 'Makaleler' },
    { id: 'news', label: 'Haberler' },
    { id: 'authors', label: 'Yazarlar' },
  ];
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><ShieldCheck className="h-6 w-6 text-emerald-600" />Editor Paneli</h1>
        <p className="mt-1 text-sm text-gray-500">Icerik onay, degerlendirme ve yazar yonetimi.</p>
      </div>
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {tabs.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === 'queue' && <QueueTab />}
      {tab === 'articles' && <ArticlesTab />}
      {tab === 'news' && <NewsTab />}
      {tab === 'authors' && <AuthorsTab />}
    </div>
  );
}

function QueueTab() {
  const { data: stats, isLoading } = useReviewQueueStats();
  const { data: articles } = useEditorArticles({ status: 'review' });
  const { data: news } = useEditorNews({ status: 'review' });
  const artT = useEditorArticleTransition();
  const newsT = useEditorNewsTransition();

  if (isLoading) return <Ld />;
  return (
    <div className="space-y-6">
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[['Toplam Bekleyen', stats.total_pending, 'text-yellow-600'], ['Makale', stats.articles_pending, 'text-blue-600'], ['Haber', stats.news_pending, 'text-purple-600'], ['Onaylandi (Yayinsiz)', stats.approved_unpublished, 'text-emerald-600']].map(([l, v, c]) => (
            <div key={String(l)} className="rounded-xl border bg-white p-4">
              <p className="text-xs text-gray-500">{l}</p>
              <p className={'text-3xl font-bold mt-1 ' + c}>{v}</p>
            </div>
          ))}
        </div>
      )}
      {articles && articles.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><FileText className="h-4 w-4" />Makale Incelemeleri</h3>
          <div className="space-y-2">{articles.map((a) => (
            <div key={a.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-900 truncate">{a.title_tr}</p>
                <p className="text-xs text-gray-500 mt-1">{a.author_name} - {fmtD(a.created_at)}</p>
              </div>
              <div className="flex gap-1">
                <button onClick={() => artT.mutate({ id: a.id, action: 'publish' })} disabled={artT.isPending} className="rounded px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100" title="Yayinla"><CheckCircle className="h-4 w-4" /></button>
                <button onClick={() => { const fb = prompt('Red sebebi:'); if (fb) artT.mutate({ id: a.id, action: 'archive', feedback: fb }); }} className="rounded px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100" title="Reddet"><XCircle className="h-4 w-4" /></button>
              </div>
            </div>
          ))}</div>
        </div>
      )}
      {news && news.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Newspaper className="h-4 w-4" />Haber Incelemeleri</h3>
          <div className="space-y-2">{news.map((n) => (
            <div key={n.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-900 truncate">{n.title_tr}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-500">{n.author_name}</span>
                  <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (n.priority === 'urgent' ? 'bg-red-100 text-red-700' : n.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600')}>{n.priority_display}</span>
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => newsT.mutate({ id: n.id, action: 'approve' })} disabled={newsT.isPending} className="rounded px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100" title="Onayla"><CheckCircle className="h-4 w-4" /></button>
                <button onClick={() => { const fb = prompt('Duzeltme notu:'); if (fb) newsT.mutate({ id: n.id, action: 'reject', feedback: fb }); }} className="rounded px-3 py-1.5 text-xs font-medium text-orange-700 bg-orange-50 hover:bg-orange-100" title="Duzeltme Iste"><AlertTriangle className="h-4 w-4" /></button>
              </div>
            </div>
          ))}</div>
        </div>
      )}
      {(!articles || articles.length === 0) && (!news || news.length === 0) && <Mt msg="Inceleme bekleyen icerik yok." />}
    </div>
  );
}

function ArticlesTab() {
  const [sf, setSf] = useState('');
  const [sq, setSq] = useState('');
  const { data: articles, isLoading } = useEditorArticles({ status: sf || undefined, search: sq || undefined });
  const tr = useEditorArticleTransition();
  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Makale ara..." value={sq} onChange={(e) => setSq(e.target.value)} className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-emerald-500 focus:outline-none w-60" />
        </div>
        <select value={sf} onChange={(e) => setSf(e.target.value)} className="px-3 py-2 rounded-lg border border-gray-300 text-sm bg-white">
          <option value="">Tum Durumlar</option>
          <option value="draft">Taslak</option><option value="published">Yayinda</option><option value="archived">Arsiv</option>
        </select>
      </div>
      {isLoading ? <Ld /> : !articles?.length ? <Mt msg="Makale bulunamadi." />
       : <div className="space-y-2">{articles.map((a) => (
          <div key={a.id} className="rounded-lg border bg-white p-4 flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-gray-900 truncate">{a.title_tr || 'Basliksiz'}</p>
              <div className="flex items-center gap-3 mt-1"><SBadge status={a.status} /><span className="text-xs text-gray-500">{a.author_name}</span><span className="text-xs text-gray-400">{fmtD(a.updated_at)}</span></div>
            </div>
            <div className="flex gap-1">
              {a.status === 'draft' && <AB icon={Send} label="Yayinla" c="green" onClick={() => tr.mutate({ id: a.id, action: 'publish' })} d={tr.isPending} />}
              {a.status === 'published' && <AB icon={Archive} label="Arsivle" c="gray" onClick={() => tr.mutate({ id: a.id, action: 'archive' })} d={tr.isPending} />}
              {a.status === 'archived' && <AB icon={RotateCcw} label="Taslaga" c="indigo" onClick={() => tr.mutate({ id: a.id, action: 'revert_to_draft' })} d={tr.isPending} />}
            </div>
          </div>
        ))}</div>}
    </div>
  );
}

function NewsTab() {
  const [sf, setSf] = useState('');
  const [sq, setSq] = useState('');
  const { data: news, isLoading } = useEditorNews({ status: sf || undefined, search: sq || undefined });
  const tr = useEditorNewsTransition();
  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Haber ara..." value={sq} onChange={(e) => setSq(e.target.value)} className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-emerald-500 focus:outline-none w-60" />
        </div>
        <select value={sf} onChange={(e) => setSf(e.target.value)} className="px-3 py-2 rounded-lg border border-gray-300 text-sm bg-white">
          <option value="">Tum Durumlar</option>
          <option value="draft">Taslak</option><option value="review">Incelemede</option><option value="revision">Duzeltme</option>
          <option value="approved">Onaylandi</option><option value="published">Yayinda</option><option value="archived">Arsiv</option>
        </select>
      </div>
      {isLoading ? <Ld /> : !news?.length ? <Mt msg="Haber bulunamadi." />
       : <div className="space-y-2">{news.map((n) => (
          <div key={n.id} className="rounded-lg border bg-white p-4 flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-gray-900 truncate">{n.title_tr}</p>
              <div className="flex items-center gap-3 mt-1 flex-wrap">
                <SBadge status={n.status} /><span className="text-xs text-gray-500">{n.author_name}</span><span className="text-xs text-gray-500">{n.category_display}</span>
                <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (n.priority === 'urgent' ? 'bg-red-100 text-red-700' : n.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600')}>{n.priority_display}</span>
              </div>
            </div>
            <div className="flex gap-1">
              {n.status === 'review' && <><AB icon={CheckCircle} label="Onayla" c="blue" onClick={() => tr.mutate({ id: n.id, action: 'approve' })} d={tr.isPending} /><AB icon={XCircle} label="Reddet" c="red" onClick={() => { const fb = prompt('Red sebebi:'); if (fb) tr.mutate({ id: n.id, action: 'reject', feedback: fb }); }} d={tr.isPending} /></>}
              {n.status === 'approved' && <AB icon={Send} label="Yayinla" c="green" onClick={() => tr.mutate({ id: n.id, action: 'publish' })} d={tr.isPending} />}
              {n.status === 'published' && <AB icon={Archive} label="Arsivle" c="gray" onClick={() => tr.mutate({ id: n.id, action: 'archive' })} d={tr.isPending} />}
              {n.status === 'archived' && <AB icon={RotateCcw} label="Taslaga" c="indigo" onClick={() => tr.mutate({ id: n.id, action: 'revert_to_draft' })} d={tr.isPending} />}
            </div>
          </div>
        ))}</div>}
    </div>
  );
}

function AuthorsTab() {
  const { data: authors, isLoading } = useEditorAuthors();
  const vm = useVerifyAuthor();
  if (isLoading) return <Ld />;
  if (!authors?.length) return <Mt msg="Yazar bulunamadi." />;
  const lvl: Record<number, string> = { 0: 'Yeni', 1: 'Onayli', 2: 'Aktif', 3: 'Kidemli', 4: 'Editor' };
  return (
    <div className="space-y-2">{authors.map((a) => (
      <div key={a.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-medium text-gray-900">{a.full_name}</p>
            {a.is_verified && <Shield className="h-4 w-4 text-green-500" />}
          </div>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs text-gray-500">{a.specialty_display}</span>
            <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (a.author_level >= 3 ? 'bg-purple-100 text-purple-700' : a.author_level >= 1 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600')}>{a.level_display}</span>
            <span className="text-xs text-gray-400">{a.total_articles} makale</span>
          </div>
        </div>
        <div className="flex gap-2 items-center">
          <select value={a.author_level} onChange={(e) => vm.mutate({ id: a.id, author_level: Number(e.target.value) })} className="text-xs px-2 py-1 rounded border border-gray-300 bg-white">
            {[0,1,2,3,4].map((l) => <option key={l} value={l}>{lvl[l]}</option>)}
          </select>
          <button onClick={() => vm.mutate({ id: a.id, is_verified: !a.is_verified })} disabled={vm.isPending}
            className={'rounded px-3 py-1.5 text-xs font-medium ' + (a.is_verified ? 'text-red-700 bg-red-50 hover:bg-red-100' : 'text-green-700 bg-green-50 hover:bg-green-100')}>
            {a.is_verified ? 'Kaldir' : 'Dogrula'}
          </button>
        </div>
      </div>
    ))}</div>
  );
}

const CM: Record<string, string> = { green: 'text-green-700 bg-green-50 hover:bg-green-100', red: 'text-red-700 bg-red-50 hover:bg-red-100', blue: 'text-blue-700 bg-blue-50 hover:bg-blue-100', gray: 'text-gray-700 bg-gray-50 hover:bg-gray-100', indigo: 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100' };

function AB({ icon: I, label, c, onClick, d }: { icon: typeof Send; label: string; c: string; onClick: () => void; d?: boolean }) {
  return <button onClick={onClick} disabled={d} className={'rounded px-2 py-1 text-xs font-medium flex items-center gap-1 ' + (CM[c] || CM.gray)} title={label}><I className="h-3.5 w-3.5" /><span className="hidden sm:inline">{label}</span></button>;
}

function Ld() { return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-emerald-400" /></div>; }
function Mt({ msg }: { msg: string }) { return <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center"><Inbox className="h-10 w-10 text-gray-300 mx-auto mb-3" /><p className="text-sm text-gray-500">{msg}</p></div>; }
PYEOFcd ~/clinic-platform && mkdir -p frontend/src/app/\[locale\]/doctor/editor && python3 -c "
import os
content = open('/dev/stdin').read()
path = 'frontend/src/app/[locale]/doctor/editor/page.tsx'
with open(path, 'w') as f:
    f.write(content)
print(f'Wrote {os.path.getsize(path)} bytes to {path}')
" << 'PYEOF'
'use client';

import { useState } from 'react';
import { ShieldCheck, Inbox, FileText, Newspaper, Users, CheckCircle, XCircle, Send, Archive, RotateCcw, AlertTriangle, Loader2, Search, Shield } from 'lucide-react';
import { useReviewQueueStats, useEditorArticles, useEditorNews, useEditorArticleTransition, useEditorNewsTransition, useEditorAuthors, useVerifyAuthor } from '@/hooks/useEditorData';
import type { EditorArticle, EditorNews, EditorAuthor } from '@/hooks/useEditorData';

const STATUS_CFG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

function SBadge({ status }: { status: string }) {
  const c = STATUS_CFG[status] || STATUS_CFG.draft;
  return <span className={'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ' + c.color}>{c.label}</span>;
}

function fmtD(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
}

type TabId = 'queue' | 'articles' | 'news' | 'authors';

export default function EditorPanelPage() {
  const [tab, setTab] = useState<TabId>('queue');
  const tabs: { id: TabId; label: string }[] = [
    { id: 'queue', label: 'Inceleme Kuyrugu' },
    { id: 'articles', label: 'Makaleler' },
    { id: 'news', label: 'Haberler' },
    { id: 'authors', label: 'Yazarlar' },
  ];
  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><ShieldCheck className="h-6 w-6 text-emerald-600" />Editor Paneli</h1>
        <p className="mt-1 text-sm text-gray-500">Icerik onay, degerlendirme ve yazar yonetimi.</p>
      </div>
      <div className="flex gap-1 border-b border-gray-200 mb-6">
        {tabs.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === 'queue' && <QueueTab />}
      {tab === 'articles' && <ArticlesTab />}
      {tab === 'news' && <NewsTab />}
      {tab === 'authors' && <AuthorsTab />}
    </div>
  );
}

function QueueTab() {
  const { data: stats, isLoading } = useReviewQueueStats();
  const { data: articles } = useEditorArticles({ status: 'review' });
  const { data: news } = useEditorNews({ status: 'review' });
  const artT = useEditorArticleTransition();
  const newsT = useEditorNewsTransition();

  if (isLoading) return <Ld />;
  return (
    <div className="space-y-6">
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[['Toplam Bekleyen', stats.total_pending, 'text-yellow-600'], ['Makale', stats.articles_pending, 'text-blue-600'], ['Haber', stats.news_pending, 'text-purple-600'], ['Onaylandi (Yayinsiz)', stats.approved_unpublished, 'text-emerald-600']].map(([l, v, c]) => (
            <div key={String(l)} className="rounded-xl border bg-white p-4">
              <p className="text-xs text-gray-500">{l}</p>
              <p className={'text-3xl font-bold mt-1 ' + c}>{v}</p>
            </div>
          ))}
        </div>
      )}
      {articles && articles.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><FileText className="h-4 w-4" />Makale Incelemeleri</h3>
          <div className="space-y-2">{articles.map((a) => (
            <div key={a.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-900 truncate">{a.title_tr}</p>
                <p className="text-xs text-gray-500 mt-1">{a.author_name} - {fmtD(a.created_at)}</p>
              </div>
              <div className="flex gap-1">
                <button onClick={() => artT.mutate({ id: a.id, action: 'publish' })} disabled={artT.isPending} className="rounded px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100" title="Yayinla"><CheckCircle className="h-4 w-4" /></button>
                <button onClick={() => { const fb = prompt('Red sebebi:'); if (fb) artT.mutate({ id: a.id, action: 'archive', feedback: fb }); }} className="rounded px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100" title="Reddet"><XCircle className="h-4 w-4" /></button>
              </div>
            </div>
          ))}</div>
        </div>
      )}
      {news && news.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2"><Newspaper className="h-4 w-4" />Haber Incelemeleri</h3>
          <div className="space-y-2">{news.map((n) => (
            <div key={n.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-900 truncate">{n.title_tr}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-500">{n.author_name}</span>
                  <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (n.priority === 'urgent' ? 'bg-red-100 text-red-700' : n.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600')}>{n.priority_display}</span>
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => newsT.mutate({ id: n.id, action: 'approve' })} disabled={newsT.isPending} className="rounded px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100" title="Onayla"><CheckCircle className="h-4 w-4" /></button>
                <button onClick={() => { const fb = prompt('Duzeltme notu:'); if (fb) newsT.mutate({ id: n.id, action: 'reject', feedback: fb }); }} className="rounded px-3 py-1.5 text-xs font-medium text-orange-700 bg-orange-50 hover:bg-orange-100" title="Duzeltme Iste"><AlertTriangle className="h-4 w-4" /></button>
              </div>
            </div>
          ))}</div>
        </div>
      )}
      {(!articles || articles.length === 0) && (!news || news.length === 0) && <Mt msg="Inceleme bekleyen icerik yok." />}
    </div>
  );
}

function ArticlesTab() {
  const [sf, setSf] = useState('');
  const [sq, setSq] = useState('');
  const { data: articles, isLoading } = useEditorArticles({ status: sf || undefined, search: sq || undefined });
  const tr = useEditorArticleTransition();
  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Makale ara..." value={sq} onChange={(e) => setSq(e.target.value)} className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-emerald-500 focus:outline-none w-60" />
        </div>
        <select value={sf} onChange={(e) => setSf(e.target.value)} className="px-3 py-2 rounded-lg border border-gray-300 text-sm bg-white">
          <option value="">Tum Durumlar</option>
          <option value="draft">Taslak</option><option value="published">Yayinda</option><option value="archived">Arsiv</option>
        </select>
      </div>
      {isLoading ? <Ld /> : !articles?.length ? <Mt msg="Makale bulunamadi." />
       : <div className="space-y-2">{articles.map((a) => (
          <div key={a.id} className="rounded-lg border bg-white p-4 flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-gray-900 truncate">{a.title_tr || 'Basliksiz'}</p>
              <div className="flex items-center gap-3 mt-1"><SBadge status={a.status} /><span className="text-xs text-gray-500">{a.author_name}</span><span className="text-xs text-gray-400">{fmtD(a.updated_at)}</span></div>
            </div>
            <div className="flex gap-1">
              {a.status === 'draft' && <AB icon={Send} label="Yayinla" c="green" onClick={() => tr.mutate({ id: a.id, action: 'publish' })} d={tr.isPending} />}
              {a.status === 'published' && <AB icon={Archive} label="Arsivle" c="gray" onClick={() => tr.mutate({ id: a.id, action: 'archive' })} d={tr.isPending} />}
              {a.status === 'archived' && <AB icon={RotateCcw} label="Taslaga" c="indigo" onClick={() => tr.mutate({ id: a.id, action: 'revert_to_draft' })} d={tr.isPending} />}
            </div>
          </div>
        ))}</div>}
    </div>
  );
}

function NewsTab() {
  const [sf, setSf] = useState('');
  const [sq, setSq] = useState('');
  const { data: news, isLoading } = useEditorNews({ status: sf || undefined, search: sq || undefined });
  const tr = useEditorNewsTransition();
  return (
    <div className="space-y-4">
      <div className="flex gap-2 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" placeholder="Haber ara..." value={sq} onChange={(e) => setSq(e.target.value)} className="pl-9 pr-4 py-2 rounded-lg border border-gray-300 text-sm focus:border-emerald-500 focus:outline-none w-60" />
        </div>
        <select value={sf} onChange={(e) => setSf(e.target.value)} className="px-3 py-2 rounded-lg border border-gray-300 text-sm bg-white">
          <option value="">Tum Durumlar</option>
          <option value="draft">Taslak</option><option value="review">Incelemede</option><option value="revision">Duzeltme</option>
          <option value="approved">Onaylandi</option><option value="published">Yayinda</option><option value="archived">Arsiv</option>
        </select>
      </div>
      {isLoading ? <Ld /> : !news?.length ? <Mt msg="Haber bulunamadi." />
       : <div className="space-y-2">{news.map((n) => (
          <div key={n.id} className="rounded-lg border bg-white p-4 flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-gray-900 truncate">{n.title_tr}</p>
              <div className="flex items-center gap-3 mt-1 flex-wrap">
                <SBadge status={n.status} /><span className="text-xs text-gray-500">{n.author_name}</span><span className="text-xs text-gray-500">{n.category_display}</span>
                <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (n.priority === 'urgent' ? 'bg-red-100 text-red-700' : n.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600')}>{n.priority_display}</span>
              </div>
            </div>
            <div className="flex gap-1">
              {n.status === 'review' && <><AB icon={CheckCircle} label="Onayla" c="blue" onClick={() => tr.mutate({ id: n.id, action: 'approve' })} d={tr.isPending} /><AB icon={XCircle} label="Reddet" c="red" onClick={() => { const fb = prompt('Red sebebi:'); if (fb) tr.mutate({ id: n.id, action: 'reject', feedback: fb }); }} d={tr.isPending} /></>}
              {n.status === 'approved' && <AB icon={Send} label="Yayinla" c="green" onClick={() => tr.mutate({ id: n.id, action: 'publish' })} d={tr.isPending} />}
              {n.status === 'published' && <AB icon={Archive} label="Arsivle" c="gray" onClick={() => tr.mutate({ id: n.id, action: 'archive' })} d={tr.isPending} />}
              {n.status === 'archived' && <AB icon={RotateCcw} label="Taslaga" c="indigo" onClick={() => tr.mutate({ id: n.id, action: 'revert_to_draft' })} d={tr.isPending} />}
            </div>
          </div>
        ))}</div>}
    </div>
  );
}

function AuthorsTab() {
  const { data: authors, isLoading } = useEditorAuthors();
  const vm = useVerifyAuthor();
  if (isLoading) return <Ld />;
  if (!authors?.length) return <Mt msg="Yazar bulunamadi." />;
  const lvl: Record<number, string> = { 0: 'Yeni', 1: 'Onayli', 2: 'Aktif', 3: 'Kidemli', 4: 'Editor' };
  return (
    <div className="space-y-2">{authors.map((a) => (
      <div key={a.id} className="rounded-lg border bg-white p-4 flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <p className="font-medium text-gray-900">{a.full_name}</p>
            {a.is_verified && <Shield className="h-4 w-4 text-green-500" />}
          </div>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs text-gray-500">{a.specialty_display}</span>
            <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (a.author_level >= 3 ? 'bg-purple-100 text-purple-700' : a.author_level >= 1 ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600')}>{a.level_display}</span>
            <span className="text-xs text-gray-400">{a.total_articles} makale</span>
          </div>
        </div>
        <div className="flex gap-2 items-center">
          <select value={a.author_level} onChange={(e) => vm.mutate({ id: a.id, author_level: Number(e.target.value) })} className="text-xs px-2 py-1 rounded border border-gray-300 bg-white">
            {[0,1,2,3,4].map((l) => <option key={l} value={l}>{lvl[l]}</option>)}
          </select>
          <button onClick={() => vm.mutate({ id: a.id, is_verified: !a.is_verified })} disabled={vm.isPending}
            className={'rounded px-3 py-1.5 text-xs font-medium ' + (a.is_verified ? 'text-red-700 bg-red-50 hover:bg-red-100' : 'text-green-700 bg-green-50 hover:bg-green-100')}>
            {a.is_verified ? 'Kaldir' : 'Dogrula'}
          </button>
        </div>
      </div>
    ))}</div>
  );
}

const CM: Record<string, string> = { green: 'text-green-700 bg-green-50 hover:bg-green-100', red: 'text-red-700 bg-red-50 hover:bg-red-100', blue: 'text-blue-700 bg-blue-50 hover:bg-blue-100', gray: 'text-gray-700 bg-gray-50 hover:bg-gray-100', indigo: 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100' };

function AB({ icon: I, label, c, onClick, d }: { icon: typeof Send; label: string; c: string; onClick: () => void; d?: boolean }) {
  return <button onClick={onClick} disabled={d} className={'rounded px-2 py-1 text-xs font-medium flex items-center gap-1 ' + (CM[c] || CM.gray)} title={label}><I className="h-3.5 w-3.5" /><span className="hidden sm:inline">{label}</span></button>;
}

function Ld() { return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-emerald-400" /></div>; }
function Mt({ msg }: { msg: string }) { return <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center"><Inbox className="h-10 w-10 text-gray-300 mx-auto mb-3" /><p className="text-sm text-gray-500">{msg}</p></div>; }
