'use client';

import { useState } from 'react';
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
} from 'lucide-react';

interface GenerateResult {
  success: boolean;
  article_id?: string;
  title?: string;
  seo_title?: string;
  legal_approved?: boolean;
  legal_score?: number;
  legal_issues?: string[];
  keywords?: string[];
  steps_completed?: string[];
  duration_ms?: number;
  error?: string;
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
  { value: 'blog', label: 'Blog Yazısı' },
  { value: 'education', label: 'Eğitim İçeriği' },
  { value: 'social', label: 'Sosyal Medya' },
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
  const [tone, setTone] = useState('friendly');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);

  const generateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/doctor/generate-content/', {
        topic,
        module,
        audience,
        content_type: contentType,
        tone,
      });
      return data as GenerateResult;
    },
    onSuccess: (data) => {
      setResult(data);
    },
    onError: (error: any) => {
      setResult({
        success: false,
        error: error.response?.data?.error || 'Bir hata oluştu',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setResult(null);
    generateMutation.mutate();
  };

  const stepLabels: Record<string, string> = {
    content_agent: 'İçerik Üretimi',
    seo_agent: 'SEO Optimizasyonu',
    legal_agent: 'Hukuki Kontrol',
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-purple-600" />
          İçerik Üret
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          AI destekli içerik üretimi. Üretilen içerik taslak olarak kaydedilir,
          yayınlamadan önce incelemeniz gerekir.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
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

        {/* Modül ve İçerik Tipi */}
        <div className="grid grid-cols-2 gap-4">
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              İçerik Tipi
            </label>
            <select
              value={contentType}
              onChange={(e) => setContentType(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {CONTENT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Gelişmiş Seçenekler */}
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

        {/* Üret Butonu */}
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

      {/* Sonuç */}
      {result && (
        <div className="mt-6 space-y-4">
          {/* Başarı / Hata */}
          {result.success ? (
            <div className="rounded-lg border border-green-200 bg-green-50 p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">
                  İçerik başarıyla üretildi!
                </span>
              </div>
              <p className="mt-1 text-sm text-green-700">
                Taslak olarak kaydedildi. Yayınlamadan önce incelemeniz gerekir.
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
              {/* Başlık ve SEO */}
              <div className="rounded-lg border bg-white p-4 space-y-3">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-blue-600" />
                  Üretilen İçerik
                </h3>
                <div>
                  <span className="text-xs font-medium text-gray-500">Başlık</span>
                  <p className="text-gray-900">{result.title}</p>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500">SEO Başlık</span>
                  <p className="text-gray-700">{result.seo_title}</p>
                </div>
                {result.keywords && result.keywords.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-500">Anahtar Kelimeler</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {result.keywords.map((kw, i) => (
                        <span
                          key={i}
                          className="inline-flex rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800"
                        >
                          {kw}
                        </span>
                      ))}
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
                      {i > 0 && <span className="text-gray-300">→</span>}
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
