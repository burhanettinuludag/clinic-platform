'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import {
  useEditorArticleDetail,
  useEditorArticleUpdate,
  useEditorArticleTransition,
} from '@/hooks/useEditorData';
import {
  ArrowLeft,
  FileText,
  Eye,
  Edit3,
  Save,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Loader2,
  Send,
  Archive,
  RotateCcw,
  Star,
} from 'lucide-react';

const STATUS_LABELS: Record<string, { label: string; color: string; icon: typeof Clock }> = {
  draft: { label: 'Taslak', color: 'bg-yellow-100 text-yellow-800', icon: Edit3 },
  published: { label: 'Yayinda', color: 'bg-green-100 text-green-800', icon: CheckCircle },
  archived: { label: 'Arsivlendi', color: 'bg-gray-100 text-gray-700', icon: Archive },
};

export default function EditorArticleDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: article, isLoading, error } = useEditorArticleDetail(id);
  const updateArticle = useEditorArticleUpdate();
  const transition = useEditorArticleTransition();

  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    title_tr: '',
    body_tr: '',
    excerpt_tr: '',
    seo_title_tr: '',
    seo_description_tr: '',
  });
  const [showTransitionFeedback, setShowTransitionFeedback] = useState<string | null>(null);
  const [transitionFeedback, setTransitionFeedback] = useState('');

  const startEditing = () => {
    if (!article) return;
    setEditData({
      title_tr: article.title_tr || '',
      body_tr: article.body_tr || '',
      excerpt_tr: article.excerpt_tr || '',
      seo_title_tr: article.seo_title_tr || '',
      seo_description_tr: article.seo_description_tr || '',
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    await updateArticle.mutateAsync({ id, ...editData });
    setIsEditing(false);
  };

  const handleTransition = async (action: string) => {
    await transition.mutateAsync({ id, action, feedback: transitionFeedback });
    setShowTransitionFeedback(null);
    setTransitionFeedback('');
  };

  // Simple markdown to HTML renderer
  const renderMarkdown = (md: string) => {
    if (!md) return '';
    return md
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-900 mt-6 mb-3">$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>')
      .replace(/^(\d+)\. (.*$)/gm, '<li class="ml-4 list-decimal text-gray-700">$2</li>')
      .replace(/\n\n/g, '</p><p class="text-gray-700 leading-relaxed mb-3">')
      .replace(/\n/g, '<br/>')
      ;
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="p-6">
        <div className="text-center py-16">
          <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Makale Bulunamadi</h2>
          <Link href="/doctor/editor" className="text-blue-600 hover:underline">
            Editore Don
          </Link>
        </div>
      </div>
    );
  }

  const statusInfo = STATUS_LABELS[article.status] || STATUS_LABELS.draft;
  const StatusIcon = statusInfo.icon;

  const allowedActions: Record<string, Array<{ action: string; label: string; icon: typeof Send; color: string }>> = {
    draft: [
      { action: 'publish', label: 'Yayinla', icon: Send, color: 'bg-green-600 hover:bg-green-700 text-white' },
      { action: 'archive', label: 'Arsivle', icon: Archive, color: 'bg-gray-600 hover:bg-gray-700 text-white' },
    ],
    published: [
      { action: 'archive', label: 'Arsivle', icon: Archive, color: 'bg-gray-600 hover:bg-gray-700 text-white' },
    ],
    archived: [
      { action: 'revert_to_draft', label: 'Taslaga Cevir', icon: RotateCcw, color: 'bg-blue-600 hover:bg-blue-700 text-white' },
    ],
  };

  const actions = allowedActions[article.status] || [];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Link href="/doctor/editor" className="p-2 rounded-lg hover:bg-gray-100 transition">
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-gray-900">Makale Detay</h1>
            <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full ${statusInfo.color}`}>
              <StatusIcon className="h-3 w-3" />
              {statusInfo.label}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5">
            Olusturulma: {new Date(article.created_at).toLocaleDateString('tr-TR')}
            {article.category_name && ` - Kategori: ${article.category_name}`}
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button
              onClick={startEditing}
              className="flex items-center gap-1.5 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition"
            >
              <Edit3 className="h-4 w-4" />
              Duzenle
            </button>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition"
              >
                Iptal
              </button>
              <button
                onClick={handleSave}
                disabled={updateArticle.isPending}
                className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {updateArticle.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                Kaydet
              </button>
            </>
          )}

          {!isEditing && actions.map((act) => {
            const Icon = act.icon;
            return (
              <button
                key={act.action}
                onClick={() => setShowTransitionFeedback(act.action)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm transition ${act.color}`}
              >
                <Icon className="h-4 w-4" />
                {act.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Transition Feedback Modal */}
      {showTransitionFeedback && (
        <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4">
          <p className="text-sm font-medium text-blue-800 mb-2">
            Bu islemi onaylıyor musunuz? (Opsiyonel not ekleyebilirsiniz)
          </p>
          <textarea
            value={transitionFeedback}
            onChange={(e) => setTransitionFeedback(e.target.value)}
            placeholder="Editorden not (opsiyonel)..."
            rows={2}
            className="w-full rounded-lg border border-blue-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-1 focus:ring-blue-500 mb-3"
          />
          <div className="flex gap-2">
            <button
              onClick={() => setShowTransitionFeedback(null)}
              className="px-4 py-1.5 border border-gray-300 rounded-lg text-sm hover:bg-white transition"
            >
              Iptal
            </button>
            <button
              onClick={() => handleTransition(showTransitionFeedback)}
              disabled={transition.isPending}
              className="flex items-center gap-1 px-4 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {transition.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Onayla
            </button>
          </div>
          {transition.isError && (
            <p className="text-sm text-red-600 mt-2">Islem sirasinda bir hata olustu.</p>
          )}
          {transition.isSuccess && (
            <p className="text-sm text-green-600 mt-2">Islem basariyla tamamlandi.</p>
          )}
        </div>
      )}

      {/* Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-4">
          {/* Title */}
          <div className="bg-white rounded-xl border p-5">
            <label className="block text-xs font-medium text-gray-500 mb-1">Baslik</label>
            {isEditing ? (
              <input
                type="text"
                value={editData.title_tr}
                onChange={(e) => setEditData({ ...editData, title_tr: e.target.value })}
                className="w-full text-xl font-bold text-gray-900 border border-gray-300 rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            ) : (
              <h2 className="text-xl font-bold text-gray-900">{article.title_tr}</h2>
            )}
          </div>

          {/* Excerpt */}
          <div className="bg-white rounded-xl border p-5">
            <label className="block text-xs font-medium text-gray-500 mb-1">Ozet</label>
            {isEditing ? (
              <textarea
                value={editData.excerpt_tr}
                onChange={(e) => setEditData({ ...editData, excerpt_tr: e.target.value })}
                rows={3}
                className="w-full text-gray-700 border border-gray-300 rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            ) : (
              <p className="text-gray-700 italic">{article.excerpt_tr || 'Ozet yok'}</p>
            )}
          </div>

          {/* Body */}
          <div className="bg-white rounded-xl border p-5">
            <div className="flex items-center justify-between mb-3">
              <label className="text-xs font-medium text-gray-500 flex items-center gap-1">
                <FileText className="h-3.5 w-3.5" />
                Icerik
              </label>
              {!isEditing && (
                <span className="text-xs text-gray-400">
                  ~{Math.ceil((article.body_tr?.split(/\s+/).length || 0) / 200)} dk okuma
                </span>
              )}
            </div>
            {isEditing ? (
              <textarea
                value={editData.body_tr}
                onChange={(e) => setEditData({ ...editData, body_tr: e.target.value })}
                rows={20}
                className="w-full text-gray-800 border border-gray-300 rounded-lg px-3 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono text-sm leading-relaxed"
              />
            ) : (
              <article
                className="prose prose-gray max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-p:leading-relaxed prose-li:text-gray-700"
                dangerouslySetInnerHTML={{
                  __html: `<p class="text-gray-700 leading-relaxed mb-3">${renderMarkdown(article.body_tr || '')}</p>`,
                }}
              />
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* SEO */}
          <div className="bg-white rounded-xl border p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-1.5">
              <Eye className="h-4 w-4 text-blue-600" />
              SEO Bilgileri
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-500">SEO Basligi</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.seo_title_tr}
                    onChange={(e) => setEditData({ ...editData, seo_title_tr: e.target.value })}
                    className="w-full text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none mt-1"
                  />
                ) : (
                  <p className="text-sm text-gray-700 mt-0.5">{article.seo_title_tr || '-'}</p>
                )}
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500">Meta Aciklama</label>
                {isEditing ? (
                  <textarea
                    value={editData.seo_description_tr}
                    onChange={(e) => setEditData({ ...editData, seo_description_tr: e.target.value })}
                    rows={3}
                    className="w-full text-sm border border-gray-300 rounded-lg px-2.5 py-1.5 focus:border-blue-500 focus:outline-none mt-1"
                  />
                ) : (
                  <p className="text-sm text-gray-600 mt-0.5">{article.seo_description_tr || '-'}</p>
                )}
              </div>
            </div>
          </div>

          {/* Meta Info */}
          <div className="bg-white rounded-xl border p-5">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Detaylar</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Durum</span>
                <span className={`px-2 py-0.5 rounded-full text-xs ${statusInfo.color}`}>{statusInfo.label}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Kategori</span>
                <span className="text-gray-900">{article.category_name || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Olusturulma</span>
                <span className="text-gray-900">{new Date(article.created_at).toLocaleDateString('tr-TR')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Guncelleme</span>
                <span className="text-gray-900">{new Date(article.updated_at).toLocaleDateString('tr-TR')}</span>
              </div>
              {article.published_at && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Yayin Tarihi</span>
                  <span className="text-gray-900">{new Date(article.published_at).toLocaleDateString('tr-TR')}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-500">Kelime</span>
                <span className="text-gray-900">{article.body_tr?.split(/\s+/).length || 0}</span>
              </div>
            </div>
          </div>

          {/* Reviews */}
          {article.reviews && article.reviews.length > 0 && (
            <div className="bg-white rounded-xl border p-5">
              <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-1.5">
                <Star className="h-4 w-4 text-yellow-500" />
                Degerlendirmeler ({article.reviews.length})
              </h3>
              <div className="space-y-3">
                {article.reviews.map((review) => (
                  <div key={review.id} className="border-l-2 border-gray-200 pl-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-700">{review.reviewer_name}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        review.decision === 'approve' ? 'bg-green-100 text-green-700' :
                        review.decision === 'reject' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {review.decision === 'approve' ? 'Onay' :
                         review.decision === 'reject' ? 'Red' : 'Revizyon'}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      Puan: {review.overall_score}/100 - {new Date(review.created_at).toLocaleDateString('tr-TR')}
                    </div>
                    {review.feedback && (
                      <p className="text-xs text-gray-600 mt-1">{review.feedback}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
