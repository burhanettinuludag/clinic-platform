'use client';

import RichTextEditor from '@/components/RichTextEditor';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Send, Archive, RotateCcw, Loader2, Eye, Calendar, Tag, CheckCircle, Sparkles } from 'lucide-react';
import { useAuthorArticle, useUpdateArticle, useArticleTransition, useArticlePipeline } from '@/hooks/useAuthorData';
import type { ArticleReview } from '@/hooks/useAuthorData';

const STATUS_CFG: Record<string, { label: string; color: string }> = {
  draft: { label: 'Taslak', color: 'bg-gray-100 text-gray-700' },
  review: { label: 'Incelemede', color: 'bg-yellow-100 text-yellow-700' },
  revision: { label: 'Duzeltme', color: 'bg-orange-100 text-orange-700' },
  approved: { label: 'Onaylandi', color: 'bg-blue-100 text-blue-700' },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-700' },
  archived: { label: 'Arsiv', color: 'bg-gray-100 text-gray-500' },
};

function fmtDate(d: string | null) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

type TabId = 'edit' | 'preview' | 'reviews';

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: article, isLoading } = useAuthorArticle(id);
  const updateMut = useUpdateArticle();
  const transMut = useArticleTransition();
  const pipeMut = useArticlePipeline();
  const [tab, setTab] = useState<TabId>('edit');
  const [form, setForm] = useState({
    title_tr: '', title_en: '', excerpt_tr: '', excerpt_en: '',
    body_tr: '', body_en: '',
    seo_title_tr: '', seo_title_en: '',
    seo_description_tr: '', seo_description_en: '',
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (article) {
      setForm({
        title_tr: article.title_tr || '', title_en: article.title_en || '',
        excerpt_tr: article.excerpt_tr || '', excerpt_en: article.excerpt_en || '',
        body_tr: article.body_tr || '', body_en: article.body_en || '',
        seo_title_tr: article.seo_title_tr || '', seo_title_en: article.seo_title_en || '',
        seo_description_tr: article.seo_description_tr || '', seo_description_en: article.seo_description_en || '',
      });
    }
  }, [article]);

  if (isLoading) return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-gray-400" /></div>;
  if (!article) return <div className="p-6 text-center text-gray-500">Makale bulunamadi.</div>;

  const canEdit = ['draft', 'revision'].includes(article.status);
  const sc = STATUS_CFG[article.status] || STATUS_CFG.draft;

  const handleSave = () => {
    updateMut.mutate({ id, ...form }, { onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000); } });
  };

  const handleTransition = (action: string) => {
    transMut.mutate({ id, action }, { onSuccess: () => router.push('/doctor/author') });
  };

  const handlePipeline = (pipeline: string) => {
    pipeMut.mutate({ id, pipeline });
  };

  const tabs: { id: TabId; label: string }[] = [
    { id: 'edit', label: 'Duzenle' },
    { id: 'preview', label: 'Onizleme' },
    { id: 'reviews', label: 'Degerlendirmeler (' + (article.reviews?.length || 0) + ')' },
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
          {article.is_featured && <span className="rounded-full px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-700">One Cikan</span>}
          <span className="text-xs text-gray-400">{fmtDate(article.created_at)}</span>
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
              <label className="block text-xs font-medium text-gray-600 mb-1">Ozet (TR)</label>
              <textarea value={form.excerpt_tr} onChange={e => setForm({...form, excerpt_tr: e.target.value})} disabled={!canEdit}
                rows={2} className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Ozet (EN)</label>
              <textarea value={form.excerpt_en} onChange={e => setForm({...form, excerpt_en: e.target.value})} disabled={!canEdit}
                rows={2} className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (TR)</label>
              <RichTextEditor content={form.body_tr} onChange={(html) => setForm({...form, body_tr: html})} placeholder="Icerik (Turkce)" disabled={false} />

          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Icerik (EN)</label>
              <RichTextEditor content={form.body_en} onChange={(html) => setForm({...form, body_en: html})} placeholder="Content (English)" disabled={false} />

          </div>
          {/* SEO */}
          <div className="border-t pt-4 mt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">SEO</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">SEO Title (TR)</label>
                <input value={form.seo_title_tr} onChange={e => setForm({...form, seo_title_tr: e.target.value})} disabled={!canEdit} maxLength={70}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.seo_title_tr.length}/70</span>
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">SEO Title (EN)</label>
                <input value={form.seo_title_en} onChange={e => setForm({...form, seo_title_en: e.target.value})} disabled={!canEdit} maxLength={70}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.seo_title_en.length}/70</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Meta Description (TR)</label>
                <textarea value={form.seo_description_tr} onChange={e => setForm({...form, seo_description_tr: e.target.value})} disabled={!canEdit} maxLength={160} rows={2}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.seo_description_tr.length}/160</span>
              </div>
              <div><label className="block text-xs font-medium text-gray-600 mb-1">Meta Description (EN)</label>
                <textarea value={form.seo_description_en} onChange={e => setForm({...form, seo_description_en: e.target.value})} disabled={!canEdit} maxLength={160} rows={2}
                  className="w-full rounded-lg border px-3 py-2 text-sm disabled:bg-gray-50" />
                <span className="text-[10px] text-gray-400">{form.seo_description_en.length}/160</span>
              </div>
            </div>
          </div>
          {/* Actions */}
          <div className="flex items-center justify-between border-t pt-4 mt-4">
            <div className="flex gap-2">
              {canEdit && <button onClick={handleSave} disabled={updateMut.isPending} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
                {updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}Kaydet
              </button>}
              {canEdit && <button onClick={() => handlePipeline('seo_optimize')} disabled={pipeMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50">
                {pipeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}SEO Optimize
              </button>}
              {saved && <span className="flex items-center gap-1 text-sm text-green-600"><CheckCircle className="h-4 w-4" />Kaydedildi</span>}
              {pipeMut.isSuccess && <span className="flex items-center gap-1 text-sm text-purple-600"><CheckCircle className="h-4 w-4" />SEO tamamlandi</span>}
            </div>
            <div className="flex gap-2">
              {article.status === 'draft' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Incelemeye Gonder</button>}
              {article.status === 'revision' && <button onClick={() => handleTransition('submit_for_review')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"><Send className="h-4 w-4" />Tekrar Gonder</button>}
              {article.status === 'published' && <button onClick={() => handleTransition('archive')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-gray-600 px-3 py-2 text-sm font-medium text-white hover:bg-gray-700"><Archive className="h-4 w-4" />Arsivle</button>}
              {article.status === 'archived' && <button onClick={() => handleTransition('revert_to_draft')} disabled={transMut.isPending}
                className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700"><RotateCcw className="h-4 w-4" />Taslaga Al</button>}
            </div>
          </div>
        </div>
      )}

      {/* Preview Tab */}
      {tab === 'preview' && (
        <div className="rounded-xl border bg-white p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{form.title_tr || 'Basliksiz'}</h1>
          {form.excerpt_tr && <p className="text-gray-600 italic mb-4">{form.excerpt_tr}</p>}
          <div className="flex items-center gap-3 mb-6 text-xs text-gray-400">
            <span className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5" />{fmtDate(article.published_at || article.created_at)}</span>
            {article.category_name && <span className="flex items-center gap-1"><Tag className="h-3.5 w-3.5" />{article.category_name}</span>}
          </div>
          <div className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: form.body_tr }} />
        </div>
      )}

      {/* Reviews Tab */}
      {tab === 'reviews' && (
        <div className="space-y-3">
          {!article.reviews?.length ? (
            <div className="rounded-lg border border-dashed p-8 text-center text-sm text-gray-400">Henuz degerlendirme yok.</div>
          ) : article.reviews.map((r: ArticleReview) => (
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
