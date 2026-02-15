'use client';

import { useState, useEffect } from 'react';
import { useHomepageHeroes, useUpdateHero } from '@/hooks/useSiteAdmin';
import type { HomepageHero } from '@/hooks/useSiteAdmin';
import { ArrowLeft, Save, Eye } from 'lucide-react';
import { Link } from '@/i18n/navigation';

export default function HomepagePage() {
  const { data: heroes, isLoading } = useHomepageHeroes();
  const updateHero = useUpdateHero();
  const [form, setForm] = useState<Partial<HomepageHero> | null>(null);
  const [activeHeroId, setActiveHeroId] = useState<string | null>(null);

  useEffect(() => {
    if (heroes?.length && !form) {
      const active = heroes.find(h => h.is_active) || heroes[0];
      setForm({ ...active });
      setActiveHeroId(active.id);
    }
  }, [heroes, form]);

  const updateField = (key: string, value: unknown) => setForm(prev => prev ? { ...prev, [key]: value } : null);

  const handleSave = () => {
    if (!form || !activeHeroId) return;
    updateHero.mutate({ id: activeHeroId, ...form });
  };

  if (isLoading) return <div className="p-6"><div className="animate-pulse space-y-4">{[1,2,3].map(i => <div key={i} className="h-24 bg-slate-200 rounded-xl" />)}</div></div>;

  if (!form) return <div className="p-6 text-slate-400">Henuz hero verisi yok. Django admin panelinden olusturun.</div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/doctor/site-settings" className="text-slate-400 hover:text-slate-600"><ArrowLeft className="h-5 w-5" /></Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Anasayfa Yonetimi</h1>
            <p className="text-slate-500 text-sm">Hero section ayarlari</p>
          </div>
        </div>
        <button onClick={handleSave} disabled={updateHero.isPending}
          className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600 disabled:opacity-50">
          <Save className="h-4 w-4" /> Kaydet
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Baslik (TR)</label>
              <input value={form.title_tr || ''} onChange={e => updateField('title_tr', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Baslik (EN)</label>
              <input value={form.title_en || ''} onChange={e => updateField('title_en', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Alt Baslik (TR)</label>
              <textarea value={form.subtitle_tr || ''} onChange={e => updateField('subtitle_tr', e.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Alt Baslik (EN)</label>
              <textarea value={form.subtitle_en || ''} onChange={e => updateField('subtitle_en', e.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Ana CTA Text (TR)</label>
              <input value={form.cta_text_tr || ''} onChange={e => updateField('cta_text_tr', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Ana CTA URL</label>
              <input value={form.cta_url || ''} onChange={e => updateField('cta_url', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Ikincil CTA Text (TR)</label>
              <input value={form.secondary_cta_text_tr || ''} onChange={e => updateField('secondary_cta_text_tr', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-slate-500 mb-1">Ikincil CTA URL</label>
              <input value={form.secondary_cta_url || ''} onChange={e => updateField('secondary_cta_url', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_active || false} onChange={e => updateField('is_active', e.target.checked)} className="h-4 w-4 rounded" />
            <span className="text-sm text-slate-700">Aktif</span>
          </label>
        </div>

        {/* Preview */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-1 text-xs font-medium text-slate-500 mb-3"><Eye className="h-3 w-3" /> Onizleme</div>
          <div className="bg-gradient-to-b from-slate-900 to-cyan-900 rounded-lg p-8 text-center text-white">
            <h2 className="text-xl font-bold">{form.title_tr || 'Baslik'}</h2>
            <p className="text-sm text-slate-300 mt-2">{form.subtitle_tr || 'Alt baslik'}</p>
            <div className="flex gap-3 justify-center mt-4">
              <span className="bg-cyan-500 px-4 py-2 rounded-lg text-sm font-medium">{form.cta_text_tr || 'CTA'}</span>
              {form.secondary_cta_text_tr && (
                <span className="border border-white/30 px-4 py-2 rounded-lg text-sm font-medium">{form.secondary_cta_text_tr}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
