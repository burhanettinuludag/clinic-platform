'use client';

import { useState, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import {
  Sparkles,
  FileText,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  ChevronDown,
  Eye,
  Copy,
  Check,
  Clock,
  BookOpen,
  MessageSquare,
  GraduationCap,
  Newspaper,
  Globe,
  ExternalLink,
} from 'lucide-react';

interface GenerateResult {
  success: boolean;
  article_id?: string;
  title?: string;
  body_tr?: string;
  excerpt_tr?: string;
  seo_title?: string;
  legal_approved?: boolean;
  legal_score?: number;
  legal_issues?: string[];
  keywords?: string[];
  steps_completed?: string[];
  duration_ms?: number;
  error?: string;
  content_type?: string;
}

const MODULE_OPTIONS = [
  { value: 'migraine', label: 'Migren' },
  { value: 'epilepsy', label: 'Epilepsi' },
  { value: 'dementia', label: 'Demans' },
  { value: 'wellness', label: 'Sağlıklı Yaşam' },
  { value: 'general', label: 'Genel Nöroloji' },
];

const AUDIENCE_OPTIONS = [
  { value: 'patient', label: 'Hastalar' },
  { value: 'public', label: 'Genel Halk' },
  { value: 'doctor', label: 'Hekimler' },
];

const CONTENT_TYPE_OPTIONS = [
  { value: 'blog', label: 'Blog Yazısı', icon: BookOpen, desc: 'Detaylı bilgilendirme yazısı' },
  { value: 'news', label: 'Haber', icon: Newspaper, desc: 'Güncel nöroloji haberi' },
  { value: 'education', label: 'Eğitim İçeriği', icon: GraduationCap, desc: 'Maddeler halinde eğitim materyali' },
  { value: 'social', label: 'Sosyal Medya', icon: MessageSquare, desc: 'Kısa sosyal medya postu' },
];

const LENGTH_OPTIONS = [
  { value: 'short', label: 'Kısa', desc: '2-3 dk okuma', words: '400-600 kelime' },
  { value: 'medium', label: 'Orta', desc: '~5 dk okuma', words: '800-1200 kelime' },
  { value: 'long', label: 'Uzun', desc: '8-10 dk okuma', words: '1500-2000 kelime' },
];

const TONE_OPTIONS = [
  { value: 'friendly', label: 'Samimi' },
  { value: 'formal', label: 'Resmi / Akademik' },
];

export default function GenerateContentPage() {
  const [topic, setTopic] = useState('');
  const [module, setModule] = useState('general');
  const [audience, setAudience] = useState('patient');
  const [contentType, setContentType] = useState('blog');
  const [contentLength, setContentLength] = useState('medium');
  const [tone, setTone] = useState('friendly');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [showPreview, setShowPreview] = useState(true);
  const [copied, setCopied] = useState(false);
  const previewRef = useRef<HTMLDivElement>(null);

  const generateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/doctor/generate-content/', {
        topic,
        module,
        audience,
        content_type: contentType,
        content_length: contentLength,
        tone,
      });
      return data as GenerateResult;
    },
    onSuccess: (data) => {
      setResult(data);
      setShowPreview(true);
      // Scroll to preview
      setTimeout(() => {
        previewRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 200);
    },
    onError: (error: any) => {
      setResult({
        success: false,
        error: error.response?.data?.error || 'Bir hata oluştu',
      });
    },
  });

  const [fetchResult, setFetchResult] = useState<any>(null);

  const fetchNewsMutation = useMutation({
    mutationFn: async (dryRun: boolean) => {
      const { data } = await api.post('/doctor/fetch-news/', {
        max_news: 3,
        dry_run: dryRun,
      });
      return data;
    },
    onSuccess: (data) => setFetchResult(data),
    onError: (error: any) => {
      setFetchResult({
        success: false,
        error: error.response?.data?.error || 'Kaynak tarama hatası',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setResult(null);
    generateMutation.mutate();
  };

  const handleCopyContent = async () => {
    if (result?.body_tr) {
      await navigator.clipboard.writeText(result.body_tr);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const stepLabels: Record<string, string> = {
    content_agent: 'İçerik Üretimi',
    news_agent: 'Haber Üretimi',
    seo_agent: 'SEO Optimizasyonu',
    legal_agent: 'Hukuki Kontrol',
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

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-purple-600" />
          İçerik Üret
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          AI destekli içerik üretimi. İçerik tipini ve uzunluğunu belirleyin,
          üretilen içeriği hemen önizleyin.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Konu */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Konu *
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Örn: Migren atağı sırasında ne yapmalı"
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            required
          />
        </div>

        {/* Modul */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Hastalık Modülü
          </label>
          <select
            value={module}
            onChange={(e) => setModule(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {MODULE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* Icerik Tipi - Kart secimi */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            İçerik Tipi
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {CONTENT_TYPE_OPTIONS.map((opt) => {
              const Icon = opt.icon;
              const isSelected = contentType === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setContentType(opt.value)}
                  className={`flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all ${
                    isSelected
                      ? 'border-purple-500 bg-purple-50 text-purple-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`h-6 w-6 ${isSelected ? 'text-purple-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-medium">{opt.label}</span>
                  <span className="text-xs opacity-70">{opt.desc}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Uzunluk - Kart secimi */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            İçerik Uzunluğu
          </label>
          <div className="grid grid-cols-3 gap-3">
            {LENGTH_OPTIONS.map((opt) => {
              const isSelected = contentLength === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setContentLength(opt.value)}
                  className={`flex flex-col items-center gap-1 rounded-xl border-2 p-4 transition-all ${
                    isSelected
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <Clock className={`h-5 w-5 mb-1 ${isSelected ? 'text-blue-600' : 'text-gray-400'}`} />
                  <span className="text-sm font-semibold">{opt.label}</span>
                  <span className="text-xs opacity-70">{opt.desc}</span>
                  <span className="text-[10px] opacity-50">{opt.words}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Gelismis Secenekler */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ChevronDown
            className={`h-4 w-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          />
          Gelişmiş Seçenekler
        </button>

        {showAdvanced && (
          <div className="grid grid-cols-2 gap-4 rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Hedef Kitle
              </label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
              >
                {AUDIENCE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ton
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
              >
                {TONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Uret Butonu */}
        <button
          type="submit"
          disabled={generateMutation.isPending || !topic.trim()}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-purple-600 px-6 py-3 text-white font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {generateMutation.isPending ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Üretiliyor... (10-15 saniye)
            </>
          ) : (
            <>
              <Sparkles className="h-5 w-5" />
              İçerik Üret
            </>
          )}
        </button>
      </form>

      {/* Kaynaklardan Haber Topla */}
      <div className="mt-8 rounded-xl border-2 border-dashed border-blue-200 bg-blue-50/50 p-6">
        <div className="flex items-start gap-3 mb-4">
          <Globe className="h-6 w-6 text-blue-600 mt-0.5" />
          <div>
            <h2 className="text-lg font-bold text-gray-900">Kaynaklardan Haber Topla</h2>
            <p className="text-sm text-gray-500 mt-1">
              PubMed, FDA, Medscape ve ScienceDaily gibi gerçek kaynaklardan güncel nöroloji haberlerini
              otomatik çeker ve AI ile Türkçe habere dönüştürür.
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => { setFetchResult(null); fetchNewsMutation.mutate(true); }}
            disabled={fetchNewsMutation.isPending}
            className="flex items-center gap-2 rounded-lg border border-blue-300 bg-white px-4 py-2.5 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-50 transition-colors"
          >
            {fetchNewsMutation.isPending && fetchNewsMutation.variables === true ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
            Kaynakları Önizle
          </button>
          <button
            type="button"
            onClick={() => { setFetchResult(null); fetchNewsMutation.mutate(false); }}
            disabled={fetchNewsMutation.isPending}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {fetchNewsMutation.isPending && fetchNewsMutation.variables === false ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Newspaper className="h-4 w-4" />
            )}
            Haberleri Üret (3 haber)
          </button>
        </div>

        {/* Fetch Sonuçları */}
        {fetchResult && (
          <div className="mt-4 space-y-2">
            {fetchResult.dry_run ? (
              <>
                <p className="text-sm font-medium text-blue-800">
                  {fetchResult.total_sources} kaynak bulundu:
                </p>
                <div className="max-h-60 overflow-y-auto space-y-1.5">
                  {fetchResult.items?.map((item: any, i: number) => (
                    <div key={i} className="flex items-start gap-2 rounded-lg bg-white p-2.5 text-sm border border-blue-100">
                      <ExternalLink className="h-3.5 w-3.5 text-blue-500 mt-0.5 shrink-0" />
                      <div>
                        <span className="text-gray-800 font-medium">{item.title}</span>
                        <div className="flex gap-2 mt-0.5 text-xs text-gray-400">
                          <span className="text-blue-600">{item.source}</span>
                          {item.diseases?.length > 0 && <span>{item.diseases.join(', ')}</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : fetchResult.success ? (
              <>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">
                    {fetchResult.succeeded} haber üretildi (taslak olarak kaydedildi)
                  </span>
                </div>
                <div className="space-y-1.5">
                  {fetchResult.results?.map((r: any, i: number) => (
                    <div key={i} className={`flex items-start gap-2 rounded-lg p-2.5 text-sm border ${r.success ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                      {r.success ? <CheckCircle className="h-3.5 w-3.5 text-green-500 mt-0.5" /> : <XCircle className="h-3.5 w-3.5 text-red-500 mt-0.5" />}
                      <div>
                        <span className={r.success ? 'text-green-800' : 'text-red-800'}>{r.title}</span>
                        <span className="text-xs text-gray-400 ml-2">[{r.source}]</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2 text-red-700 text-sm">
                <XCircle className="h-4 w-4" />
                {fetchResult.error}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pipeline Durumu */}
      {generateMutation.isPending && (
        <div className="mt-6 rounded-lg border border-purple-200 bg-purple-50 p-4">
          <p className="text-sm font-medium text-purple-800 mb-3">
            Pipeline çalışıyor...
          </p>
          <div className="space-y-2">
            {['content_agent', 'seo_agent', 'legal_agent'].map((step) => (
              <div key={step} className="flex items-center gap-2 text-sm text-purple-700">
                <Loader2 className="h-4 w-4 animate-spin" />
                {stepLabels[step]}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sonuc */}
      {result && (
        <div ref={previewRef} className="mt-6 space-y-4">
          {/* Basari / Hata */}
          {result.success ? (
            <div className="rounded-lg border border-green-200 bg-green-50 p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">
                  {result.content_type === 'news' ? 'Haber başarıyla üretildi!' : 'İçerik başarıyla üretildi!'}
                </span>
              </div>
              <p className="mt-1 text-sm text-green-700">
                Taslak olarak kaydedildi. Aşağıda önizleyebilir, {result.content_type === 'news' ? 'yazar panelinden haberi' : 'editörden'} düzenleyebilirsiniz.
              </p>
            </div>
          ) : (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4">
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-600" />
                <span className="font-medium text-red-800">Hata</span>
              </div>
              <p className="mt-1 text-sm text-red-700">{result.error}</p>
            </div>
          )}

          {/* Detaylar */}
          {result.success && (
            <>
              {/* Icerik Onizleme */}
              <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
                <div className="flex items-center justify-between border-b border-gray-200 px-5 py-3 bg-gray-50">
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    <Eye className="h-4 w-4 text-blue-600" />
                    İçerik Önizleme
                  </h3>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleCopyContent}
                      className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-md border border-gray-300 text-gray-600 hover:bg-gray-100 transition"
                    >
                      {copied ? (
                        <><Check className="h-3.5 w-3.5 text-green-600" /> Kopyalandı</>
                      ) : (
                        <><Copy className="h-3.5 w-3.5" /> Kopyala</>
                      )}
                    </button>
                    <button
                      onClick={() => setShowPreview(!showPreview)}
                      className="text-xs px-3 py-1.5 rounded-md border border-gray-300 text-gray-600 hover:bg-gray-100 transition"
                    >
                      {showPreview ? 'Gizle' : 'Göster'}
                    </button>
                  </div>
                </div>

                {showPreview && (
                  <div className="p-6">
                    {/* Baslik */}
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                      {result.title}
                    </h1>

                    {/* Ozet */}
                    {result.excerpt_tr && (
                      <p className="text-gray-500 italic text-sm mb-4 pb-4 border-b border-gray-100">
                        {result.excerpt_tr}
                      </p>
                    )}

                    {/* Anahtar Kelimeler */}
                    {result.keywords && result.keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {result.keywords.map((kw, i) => (
                          <span
                            key={i}
                            className="inline-flex rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Makale Icerik */}
                    {result.body_tr && (
                      <article
                        className="prose prose-gray max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-p:leading-relaxed prose-li:text-gray-700"
                        dangerouslySetInnerHTML={{
                          __html: `<p class="text-gray-700 leading-relaxed mb-3">${renderMarkdown(result.body_tr)}</p>`,
                        }}
                      />
                    )}

                    {/* SEO Bilgisi */}
                    <div className="mt-6 pt-4 border-t border-gray-100">
                      <div className="text-xs font-medium text-gray-400 mb-1">SEO Başlığı</div>
                      <p className="text-sm text-gray-600">{result.seo_title}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Hukuki Kontrol */}
              <div className="rounded-lg border bg-white p-4 space-y-3">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  {result.legal_approved ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                  )}
                  Hukuki Kontrol
                </h3>
                <div className="flex items-center gap-4">
                  <div>
                    <span className="text-xs font-medium text-gray-500">Puan</span>
                    <p
                      className={`text-2xl font-bold ${
                        (result.legal_score ?? 0) >= 70
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {result.legal_score}/100
                    </p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">Durum</span>
                    <p
                      className={`font-medium ${
                        result.legal_approved ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {result.legal_approved ? 'Onaylandı' : 'Reddedildi'}
                    </p>
                  </div>
                </div>
                {result.legal_issues && result.legal_issues.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-red-500">Sorunlar</span>
                    <ul className="mt-1 space-y-1">
                      {result.legal_issues.map((issue, i) => (
                        <li key={i} className="text-sm text-red-700 flex items-start gap-1">
                          <XCircle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                          {issue}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Pipeline Bilgisi */}
              <div className="rounded-lg border bg-white p-4">
                <h3 className="font-semibold text-gray-900 text-sm mb-2">Pipeline</h3>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  {result.steps_completed?.map((step, i) => (
                    <span key={step} className="flex items-center gap-1">
                      {i > 0 && <span className="text-gray-300">&rarr;</span>}
                      <CheckCircle className="h-3.5 w-3.5 text-green-500" />
                      {stepLabels[step] || step}
                    </span>
                  ))}
                  <span className="ml-auto text-xs text-gray-400">
                    {((result.duration_ms ?? 0) / 1000).toFixed(1)}s
                  </span>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
