'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Code, FileSearch, Loader2, Copy, CheckCircle, Terminal, Sparkles } from 'lucide-react';
import api from '@/lib/api';

const TASK_TYPES = [
  { value: 'create_model', label: 'Model Olustur', hint: 'Django model + migration' },
  { value: 'create_view', label: 'View Olustur', hint: 'DRF endpoint' },
  { value: 'create_serializer', label: 'Serializer Olustur', hint: 'DRF serializer' },
  { value: 'create_test', label: 'Test Olustur', hint: 'unittest + mock' },
  { value: 'create_page', label: 'Sayfa Olustur', hint: 'Next.js page' },
  { value: 'refactor', label: 'Refactor', hint: 'Kod iyilestirme' },
  { value: 'analyze', label: 'Analiz', hint: 'Kod analizi' },
];

const APPS = ['content', 'accounts', 'patient', 'doctor_panel', 'notifications', 'common'];

type TabId = 'generate' | 'review';

interface FileResult {
  path: string;
  action: string;
  content: string;
  description: string;
}

export default function DevOpsPage() {
  const [tab, setTab] = useState<TabId>('generate');
  const [task, setTask] = useState('');
  const [taskType, setTaskType] = useState('create_model');
  const [targetApp, setTargetApp] = useState('content');
  const [context, setContext] = useState('');
  const [reviewCode, setReviewCode] = useState('');
  const [copied, setCopied] = useState<string | null>(null);

  const generateMut = useMutation({
    mutationFn: async (input: { task: string; task_type: string; context: string; target_app: string }) => {
      const { data } = await api.post('/doctor/devops/generate/', input);
      return data;
    },
  });

  const reviewMut = useMutation({
    mutationFn: async (input: { file_content: string; task: string }) => {
      const { data } = await api.post('/doctor/devops/review/', input);
      return data;
    },
  });

  const handleGenerate = () => {
    if (!task.trim()) return;
    generateMut.mutate({ task, task_type: taskType, context, target_app: targetApp });
  };

  const handleReview = () => {
    if (!reviewCode.trim()) return;
    reviewMut.mutate({ file_content: reviewCode, task: 'Kodu incele ve kalite raporu olustur' });
  };

  const copyCode = (content: string, id: string) => {
    navigator.clipboard.writeText(content);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const genResult = generateMut.data?.result;
  const revResult = reviewMut.data?.result;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Terminal className="h-6 w-6 text-cyan-600" />
        <h1 className="text-xl font-bold text-gray-900">DevOps Agent</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b mb-6">
        {[{ id: 'generate' as TabId, label: 'Kod Uret', icon: Sparkles }, { id: 'review' as TabId, label: 'Kod Review', icon: FileSearch }].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={'flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-cyan-600 text-cyan-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            <t.icon className="h-4 w-4" />{t.label}
          </button>
        ))}
      </div>

      {/* Generate Tab */}
      {tab === 'generate' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Gorev Tipi</label>
              <select value={taskType} onChange={e => setTaskType(e.target.value)} className="w-full rounded-lg border px-3 py-2 text-sm bg-white">
                {TASK_TYPES.map(t => <option key={t.value} value={t.value}>{t.label} - {t.hint}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Hedef App</label>
              <select value={targetApp} onChange={e => setTargetApp(e.target.value)} className="w-full rounded-lg border px-3 py-2 text-sm bg-white">
                {APPS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Gorev Aciklamasi</label>
            <textarea value={task} onChange={e => setTask(e.target.value)} rows={3} placeholder="Ornek: FAQ modeli olustur - soru, cevap, kategori, siralama, aktif/pasif alanlari olsun"
              className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Ek Baglam (opsiyonel)</label>
            <textarea value={context} onChange={e => setContext(e.target.value)} rows={3} placeholder="Mevcut model yapisi, ozel gereksinimler..."
              className="w-full rounded-lg border px-3 py-2 text-sm font-mono" />
          </div>
          <button onClick={handleGenerate} disabled={generateMut.isPending || !task.trim()}
            className="flex items-center gap-2 rounded-lg bg-cyan-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50">
            {generateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Code className="h-4 w-4" />}Kod Uret
          </button>

          {/* Results */}
          {genResult && !genResult.error && (
            <div className="mt-6 space-y-4">
              {genResult.migration_needed && (
                <div className="rounded-lg bg-amber-50 border border-amber-200 px-4 py-2 text-sm text-amber-700">Migration gerekli: python manage.py makemigrations</div>
              )}
              {genResult.notes && <div className="rounded-lg bg-blue-50 border border-blue-200 px-4 py-2 text-sm text-blue-700">{genResult.notes}</div>}
              {(genResult.files || []).map((f: FileResult, i: number) => (
                <div key={i} className="rounded-xl border bg-white overflow-hidden">
                  <div className="flex items-center justify-between bg-gray-50 px-4 py-2 border-b">
                    <div>
                      <span className="text-sm font-medium text-gray-900">{f.path}</span>
                      <span className="ml-2 text-xs text-gray-500">[{f.action}]</span>
                    </div>
                    <button onClick={() => copyCode(f.content, String(i))} className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
                      {copied === String(i) ? <><CheckCircle className="h-3.5 w-3.5 text-green-500" />Kopyalandi</> : <><Copy className="h-3.5 w-3.5" />Kopyala</>}
                    </button>
                  </div>
                  {f.description && <p className="px-4 py-2 text-xs text-gray-500 bg-gray-50 border-b">{f.description}</p>}
                  <pre className="p-4 text-xs font-mono text-gray-800 overflow-x-auto max-h-96 overflow-y-auto">{f.content}</pre>
                </div>
              ))}
            </div>
          )}
          {genResult?.error && <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{genResult.error}</div>}
        </div>
      )}

      {/* Review Tab */}
      {tab === 'review' && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Kod (yapistir)</label>
            <textarea value={reviewCode} onChange={e => setReviewCode(e.target.value)} rows={14} placeholder="Python veya TypeScript kodunu yapistirin..."
              className="w-full rounded-lg border px-3 py-2 text-sm font-mono" />
          </div>
          <button onClick={handleReview} disabled={reviewMut.isPending || !reviewCode.trim()}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
            {reviewMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileSearch className="h-4 w-4" />}Review Baslat
          </button>

          {/* Review Results */}
          {revResult && !revResult.error && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center gap-4">
                <div className={'rounded-full h-16 w-16 flex items-center justify-center text-xl font-bold text-white ' + (revResult.score >= 80 ? 'bg-green-500' : revResult.score >= 60 ? 'bg-yellow-500' : 'bg-red-500')}>
                  {revResult.score}
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Kalite Skoru</p>
                  <p className="text-xs text-gray-500">{revResult.summary}</p>
                </div>
              </div>
              {(revResult.issues || []).map((issue: { severity: string; line: number; message: string; suggestion: string }, i: number) => (
                <div key={i} className={'rounded-lg border px-4 py-3 ' + (issue.severity === 'critical' ? 'bg-red-50 border-red-200' : issue.severity === 'warning' ? 'bg-yellow-50 border-yellow-200' : 'bg-blue-50 border-blue-200')}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (issue.severity === 'critical' ? 'bg-red-100 text-red-700' : issue.severity === 'warning' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700')}>{issue.severity}</span>
                    {issue.line > 0 && <span className="text-xs text-gray-400">Satir {issue.line}</span>}
                  </div>
                  <p className="text-sm text-gray-800">{issue.message}</p>
                  {issue.suggestion && <p className="text-xs text-gray-500 mt-1">Oneri: {issue.suggestion}</p>}
                </div>
              ))}
            </div>
          )}
          {revResult?.error && <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{revResult.error}</div>}
        </div>
      )}
    </div>
  );
}
