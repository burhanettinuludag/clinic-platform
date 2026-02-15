'use client';

import RichTextEditor from '@/components/RichTextEditor';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Send, Archive, RotateCcw, Loader2, Eye, Calendar, Tag, AlertTriangle, CheckCircle, Star } from 'lucide-react';
import { useAuthorNewsDetail, useUpdateNews, useNewsTransition } from '@/hooks/useAuthorData';
import type { AuthorNewsDetail, ArticleReview } from '@/hooks/useAuthorData';

const STATUS_CFG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

const CATEGORIES = [
  { value: 'fda_approval', label: 'FDA Onayi' },
  { value: 'ema_approval', label: 'EMA Onayi' },
  { value: 'turkey_approval', label: 'Turkiye Ruhsat' },
  { value: 'clinical_trial', label: 'Klinik Calisma' },
  { value: 'new_device', label: 'Yeni Cihaz / Teknoloji' },
  { value: 'congress', label: 'Kongre Haberi' },
  { value: 'turkey_news', label: 'Turkiye Guncel' },
  { value: 'popular_science', label: 'Populer Bilim' },
  { value: 'drug_update', label: 'Ilac Guncellemesi' },
  { value: 'guideline_update', label: 'Kilavuz Guncellemesi' },
];

const PRIORITIES = [
  { value: 'urgent', label: 'Acil' },
  { value: 'high', label: 'Yuksek' },
  { value: 'medium', label: 'Orta' },
  { value: 'low', label: 'Dusuk' },
];

function fmtDate(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

type TabId = 'edit' | 'preview' | 'reviews';

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: news, isLoading } = useAuthorNewsDetail(id);
  const updateMut = useUpdateNews();
  const transMut = useNewsTransition();
  const [tab, setTab] = useState<TabId>('edit');
  const [form, setForm] = useState({
    title_tr: '', title_en: '', excerpt_tr: '', excerpt_en: '',
    body_tr: '', body_en: '', category: '', priority: 'medium',
    source_urls: '', original_source: '',
    meta_title: '', meta_description: '', keywords: '',
    featured_image_alt: '',
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (news) {
      setForm({
        title_tr: news.title_tr || '', title_en: news.title_en || '',
        excerpt_tr: news.excerpt_tr || '', excerpt_en: news.excerpt_en || '',
        body_tr: news.body_tr || '', body_en: news.body_en || '',
        category: news.category || '', priority: news.priority || 'medium',
        source_urls: (news.source_urls || []).join('\n'),
        original_source: news.original_source || '',
        meta_title: news.meta_title || '', meta_description: news.meta_description || '',
        keywords: (news.keywords || []).join(', '),
        featured_image_alt: news.featured_image_alt || '',
      });
    }
  }, [news]);

  if (isLoading) return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-gray-400" /></div>;
  if (!news) return <div className="p-6 text-center text-gray-500">Haber bulunamadi.</div>;

  const canEdit = ['draft', 'revision'].includes(news.status);
  const sc = STATUS_CFG[news.status] || STATUS_CFG.draft;

  const handleSave = () => {
    const payload: Record<string, any> = { ...form, id };
    payload.source_urls = form.source_urls.split('\n').map(s => s.trim()).filter(Boolean);
    payload.keywords = form.keywords.split(',').map(s => s.trim()).filter(Boolean);
    updateMut.mutate(payload, { onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000); } });
  };

  const handleTransition = (action: string) => {
    transMut.mutate({ id, action }, { onSuccess: () => router.push('/doctor/author') });
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: 'edit', label: 'Duzenle' },
    { id: 'preview', label: 'Onizleme' },
    { id: 'reviews', label: 'Degerlendirmeler (' + (news.reviews?.length || 0) + ')' },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button onClick={() => router.push('/doctor/author')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" />Geri
        </button>
        <div className="flex items-center gap-2">
          <span className={'rounded-full px-3 py-1 text-xs font-medium ' + sc.color}>{sc.label}</span>
          {news.view_count > 0 && <span className="flex items-center gap-1 text-xs text-gray-400"><Eye className="h-3.5 w-3.5" />{news.view_count}</span>}
          <span className="text-xs text-gray-400">{fmtDate(news.created_at)}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b mb-6">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={'px-4 py-2 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Edit Tab */}
      {tab === 'edit' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (TR)</label>
              <input value={form.title_tr} onChange={e => setForm({...form, title_tr: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (EN)</label>
              <input value={form.title_en} onChange={e => setForm({...form, title_en: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Kategori</label>
              <select value={form.category} onChange={e => setForm({...form, category: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm bg-white disabled:bg-gray-50">
                <option value="">Sec...</option>
                {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Oncelik</label>
              <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm bg-white disabled:bg-gray-50">
                {PRIORITIES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Ozet (TR)</label>
            <textarea value={form.excerpt_tr} onChange={e => setForm({...form, excerpt_tr: e.target.value})} disabled={!canEdit}
              rows={2} className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (TR)</label>
              <RichTextEditor content={form.body_tr} onChange={(html) => setForm({...form, body_tr: html})} placeholder="Icerik (Turkce)" disabled={!canEdit} />

          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (EN)</label>
              <RichTextEditor content={form.body_en} onChange={(html) => setForm({...form, body_en: html})} placeholder="Content (English)" disabled={!canEdit} />

          </div>
          {/* SEO */}
          <div className="border-t pt-4 mt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">SEO & Meta</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Meta Title</label>
                <input value={form.meta_title} onChange={e => setForm({...form, meta_title: e.target.value})} disabled={!canEdit} maxLength={70}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.meta_title.length}/70</span>
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Anahtar Kelimeler</label>
                <input value={form.keywords} onChange={e => setForm({...form, keywords: e.target.value})} disabled={!canEdit} placeholder="virgul ile ayir"
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              </div>
            </div>
            <div className="mt-3"><label className="block text-xs font-medium text-gray-600 mb-1">Meta Description</label>
              <textarea value={form.meta_description} onChange={e => setForm({...form, meta_description: e.target.value})} disabled={!canEdit} maxLength={160} rows={2}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              <span className="text-[10px] text-gray-400">{form.meta_description.length}/160</span>
            </div>
          </div>
          {/* Sources */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Kaynaklar</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Orijinal Kaynak</label>
                <input value={form.original_source} onChange={e => setForm({...form, original_source: e.target.value})} disabled={!canEdit}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Kaynak URL (satir satir)</label>
                <textarea value={form.source_urls} onChange={e => setForm({...form, source_urls: e.target.value})} disabled={!canEdit} rows={3}
                  className="w-full rounded-lg border px-3 py-2 text-sm font-mono disabled:bg-gray-50" />
              </div>
            </div>
          </div>
          {/* Actions */}
          <div className="flex items-center justify-between border-t pt-4 mt-4">
            <div className="flex gap-2">
              {canEdit && <button onClick={handleSave} disabled={updateMut.isPending} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}Kaydet
              </button>}
              {saved && <span className="flex items-center gap-1 text-sm text-green-600"><CheckCircle className="h-4 w-4" />Kaydedildi</span>}
            </div>
            <div className="flex gap-2">
              {news.status === 'draft' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Incelemeye Gonder</button>}
              {news.status === 'revision' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Tekrar Gonder</button>}
            </div>
          </div>
        </div>
      )}

      {/* Preview Tab */}
      {tab === 'preview' && (
        <div className="rounded-xl border bg-white p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{form.title_tr || 'Basliksiz'}</h1>
          {form.excerpt_tr && <p className="text-gray-600 mb-4">{form.excerpt_tr}</p>}
          <div className="flex items-center gap-3 mb-6 text-xs text-gray-400">
            <span className="flex items-center gap-1"><Tag className="h-3.5 w-3.5" />{CATEGORIES.find(c => c.value === form.category)?.label || form.category}</span>
            <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" />{fmtDate(news.published_at || news.created_at)}</span>
          </div>
          <div className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: form.body_tr }} />
          {form.source_urls && (
            <div className="mt-6 border-t pt-4">
              <h4 className="text-xs font-semibold text-gray-500 mb-2">Kaynaklar</h4>
              {form.source_urls.split('\n').filter(Boolean).map((u, i) => (
                <p key={i} className="text-xs text-blue-600 truncate">{u}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Reviews Tab */}
      {tab === 'reviews' && (
        <div className="space-y-3">
          {!news.reviews?.length ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-gray-400">Henuz degerlendirme yok.</div>
          ) : news.reviews.map((r: ArticleReview) => (
            <div key={r.id} className="rounded-lg border bg-white p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900">{r.reviewer_name || r.review_type_display}</span>
                <span className={'rounded-full px-2.5 py-0.5 text-xs font-medium ' + (r.decision === 'publish' ? 'bg-green-100 text-green-700' : r.decision === 'revise' ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700')}>{r.decision_display}</span>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-3">
                {[['Tibbi', r.medical_accuracy_score], ['Dil', r.language_quality_score], ['SEO', r.seo_score], ['Stil', r.style_compliance_score], ['Etik', r.ethics_score], ['Genel', r.overall_score]].map(([label, score]) => (
                  <div key={String(label)} className="text-center">
                    <p className="text-[10px] text-gray-400">{label}</p>
                    <p className={'text-sm font-bold ' + (Number(score) >= 70 ? 'text-green-600' : Number(score) >= 50 ? 'text-orange-600' : 'text-red-600')}>{score}</p>
                  </div>
                ))}
              </div>
              {r.feedback && <p className="text-sm text-gray-600 bg-gray-50 rounded p-3">{r.feedback}</p>}
              <p className="text-[10px] text-gray-400 mt-2">{fmtDate(r.created_at)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
PYEOFcd ~/clinic-platform && mkdir -p frontend/src/app/\[locale\]/doctor/author/news/\[id\] && python3 -c "
import os
c = open('/dev/stdin').read()
p = 'frontend/src/app/[locale]/doctor/author/news/[id]/page.tsx'
with open(p,'w') as f: f.write(c)
print(f'Wrote {os.path.getsize(p)} bytes')
" << 'PYEOF'
'use client';

import RichTextEditor from '@/components/RichTextEditor';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Send, Archive, RotateCcw, Loader2, Eye, Calendar, Tag, AlertTriangle, CheckCircle, Star } from 'lucide-react';
import { useAuthorNewsDetail, useUpdateNews, useNewsTransition } from '@/hooks/useAuthorData';
import type { AuthorNewsDetail, ArticleReview } from '@/hooks/useAuthorData';

const STATUS_CFG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

const CATEGORIES = [
  { value: 'fda_approval', label: 'FDA Onayi' },
  { value: 'ema_approval', label: 'EMA Onayi' },
  { value: 'turkey_approval', label: 'Turkiye Ruhsat' },
  { value: 'clinical_trial', label: 'Klinik Calisma' },
  { value: 'new_device', label: 'Yeni Cihaz / Teknoloji' },
  { value: 'congress', label: 'Kongre Haberi' },
  { value: 'turkey_news', label: 'Turkiye Guncel' },
  { value: 'popular_science', label: 'Populer Bilim' },
  { value: 'drug_update', label: 'Ilac Guncellemesi' },
  { value: 'guideline_update', label: 'Kilavuz Guncellemesi' },
];

const PRIORITIES = [
  { value: 'urgent', label: 'Acil' },
  { value: 'high', label: 'Yuksek' },
  { value: 'medium', label: 'Orta' },
  { value: 'low', label: 'Dusuk' },
];

function fmtDate(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

type TabId = 'edit' | 'preview' | 'reviews';

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: news, isLoading } = useAuthorNewsDetail(id);
  const updateMut = useUpdateNews();
  const transMut = useNewsTransition();
  const [tab, setTab] = useState<TabId>('edit');
  const [form, setForm] = useState({
    title_tr: '', title_en: '', excerpt_tr: '', excerpt_en: '',
    body_tr: '', body_en: '', category: '', priority: 'medium',
    source_urls: '', original_source: '',
    meta_title: '', meta_description: '', keywords: '',
    featured_image_alt: '',
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (news) {
      setForm({
        title_tr: news.title_tr || '', title_en: news.title_en || '',
        excerpt_tr: news.excerpt_tr || '', excerpt_en: news.excerpt_en || '',
        body_tr: news.body_tr || '', body_en: news.body_en || '',
        category: news.category || '', priority: news.priority || 'medium',
        source_urls: (news.source_urls || []).join('\n'),
        original_source: news.original_source || '',
        meta_title: news.meta_title || '', meta_description: news.meta_description || '',
        keywords: (news.keywords || []).join(', '),
        featured_image_alt: news.featured_image_alt || '',
      });
    }
  }, [news]);

  if (isLoading) return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-gray-400" /></div>;
  if (!news) return <div className="p-6 text-center text-gray-500">Haber bulunamadi.</div>;

  const canEdit = ['draft', 'revision'].includes(news.status);
  const sc = STATUS_CFG[news.status] || STATUS_CFG.draft;

  const handleSave = () => {
    const payload: Record<string, any> = { ...form, id };
    payload.source_urls = form.source_urls.split('\n').map(s => s.trim()).filter(Boolean);
    payload.keywords = form.keywords.split(',').map(s => s.trim()).filter(Boolean);
    updateMut.mutate(payload, { onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000); } });
  };

  const handleTransition = (action: string) => {
    transMut.mutate({ id, action }, { onSuccess: () => router.push('/doctor/author') });
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: 'edit', label: 'Duzenle' },
    { id: 'preview', label: 'Onizleme' },
    { id: 'reviews', label: 'Degerlendirmeler (' + (news.reviews?.length || 0) + ')' },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button onClick={() => router.push('/doctor/author')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" />Geri
        </button>
        <div className="flex items-center gap-2">
          <span className={'rounded-full px-3 py-1 text-xs font-medium ' + sc.color}>{sc.label}</span>
          {news.view_count > 0 && <span className="flex items-center gap-1 text-xs text-gray-400"><Eye className="h-3.5 w-3.5" />{news.view_count}</span>}
          <span className="text-xs text-gray-400">{fmtDate(news.created_at)}</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b mb-6">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={'px-4 py-2 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Edit Tab */}
      {tab === 'edit' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (TR)</label>
              <input value={form.title_tr} onChange={e => setForm({...form, title_tr: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (EN)</label>
              <input value={form.title_en} onChange={e => setForm({...form, title_en: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Kategori</label>
              <select value={form.category} onChange={e => setForm({...form, category: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm bg-white disabled:bg-gray-50">
                <option value="">Sec...</option>
                {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Oncelik</label>
              <select value={form.priority} onChange={e => setForm({...form, priority: e.target.value})} disabled={!canEdit}
                className="w-full rounded-lg border px-3 py-2 text-sm bg-white disabled:bg-gray-50">
                {PRIORITIES.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Ozet (TR)</label>
            <textarea value={form.excerpt_tr} onChange={e => setForm({...form, excerpt_tr: e.target.value})} disabled={!canEdit}
              rows={2} className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (TR)</label>
              <RichTextEditor content={form.body_tr} onChange={(html) => setForm({...form, body_tr: html})} placeholder="Icerik (Turkce)" disabled={!canEdit} />

          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (EN)</label>
              <RichTextEditor content={form.body_en} onChange={(html) => setForm({...form, body_en: html})} placeholder="Content (English)" disabled={!canEdit} />

          </div>
          {/* SEO */}
          <div className="border-t pt-4 mt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">SEO & Meta</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Meta Title</label>
                <input value={form.meta_title} onChange={e => setForm({...form, meta_title: e.target.value})} disabled={!canEdit} maxLength={70}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.meta_title.length}/70</span>
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Anahtar Kelimeler</label>
                <input value={form.keywords} onChange={e => setForm({...form, keywords: e.target.value})} disabled={!canEdit} placeholder="virgul ile ayir"
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              </div>
            </div>
            <div className="mt-3"><label className="block text-xs font-medium text-gray-600 mb-1">Meta Description</label>
              <textarea value={form.meta_description} onChange={e => setForm({...form, meta_description: e.target.value})} disabled={!canEdit} maxLength={160} rows={2}
                className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              <span className="text-[10px] text-gray-400">{form.meta_description.length}/160</span>
            </div>
          </div>
          {/* Sources */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Kaynaklar</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Orijinal Kaynak</label>
                <input value={form.original_source} onChange={e => setForm({...form, original_source: e.target.value})} disabled={!canEdit}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Kaynak URL (satir satir)</label>
                <textarea value={form.source_urls} onChange={e => setForm({...form, source_urls: e.target.value})} disabled={!canEdit} rows={3}
                  className="w-full rounded-lg border px-3 py-2 text-sm font-mono disabled:bg-gray-50" />
              </div>
            </div>
          </div>
          {/* Actions */}
          <div className="flex items-center justify-between border-t pt-4 mt-4">
            <div className="flex gap-2">
              {canEdit && <button onClick={handleSave} disabled={updateMut.isPending} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}Kaydet
              </button>}
              {saved && <span className="flex items-center gap-1 text-sm text-green-600"><CheckCircle className="h-4 w-4" />Kaydedildi</span>}
            </div>
            <div className="flex gap-2">
              {news.status === 'draft' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Incelemeye Gonder</button>}
              {news.status === 'revision' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Tekrar Gonder</button>}
            </div>
          </div>
        </div>
      )}

      {/* Preview Tab */}
      {tab === 'preview' && (
        <div className="rounded-xl border bg-white p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{form.title_tr || 'Basliksiz'}</h1>
          {form.excerpt_tr && <p className="text-gray-600 mb-4">{form.excerpt_tr}</p>}
          <div className="flex items-center gap-3 mb-6 text-xs text-gray-400">
            <span className="flex items-center gap-1"><Tag className="h-3.5 w-3.5" />{CATEGORIES.find(c => c.value === form.category)?.label || form.category}</span>
            <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" />{fmtDate(news.published_at || news.created_at)}</span>
          </div>
          <div className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: form.body_tr }} />
          {form.source_urls && (
            <div className="mt-6 border-t pt-4">
              <h4 className="text-xs font-semibold text-gray-500 mb-2">Kaynaklar</h4>
              {form.source_urls.split('\n').filter(Boolean).map((u, i) => (
                <p key={i} className="text-xs text-blue-600 truncate">{u}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Reviews Tab */}
      {tab === 'reviews' && (
        <div className="space-y-3">
          {!news.reviews?.length ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-gray-400">Henuz degerlendirme yok.</div>
          ) : news.reviews.map((r: ArticleReview) => (
            <div key={r.id} className="rounded-lg border bg-white p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-900">{r.reviewer_name || r.review_type_display}</span>
                <span className={'rounded-full px-2.5 py-0.5 text-xs font-medium ' + (r.decision === 'publish' ? 'bg-green-100 text-green-700' : r.decision === 'revise' ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700')}>{r.decision_display}</span>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-3">
                {[['Tibbi', r.medical_accuracy_score], ['Dil', r.language_quality_score], ['SEO', r.seo_score], ['Stil', r.style_compliance_score], ['Etik', r.ethics_score], ['Genel', r.overall_score]].map(([label, score]) => (
                  <div key={String(label)} className="text-center">
                    <p className="text-[10px] text-gray-400">{label}</p>
                    <p className={'text-sm font-bold ' + (Number(score) >= 70 ? 'text-green-600' : Number(score) >= 50 ? 'text-orange-600' : 'text-red-600')}>{score}</p>
                  </div>
                ))}
              </div>
              {r.feedback && <p className="text-sm text-gray-600 bg-gray-50 rounded p-3">{r.feedback}</p>}
              <p className="text-[10px] text-gray-400 mt-2">{fmtDate(r.created_at)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
