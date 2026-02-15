'use client';

import { useState } from 'react';
import { useSiteConfigs, useUpdateSiteConfig } from '@/hooks/useSiteAdmin';
import type { SiteConfig } from '@/hooks/useSiteAdmin';
import { Save, ArrowLeft } from 'lucide-react';
import { Link } from '@/i18n/navigation';

function ConfigInput({ config, onSave }: { config: SiteConfig; onSave: (id: string, value: string) => void }) {
  const [value, setValue] = useState(config.value);
  const changed = value !== config.value;

  if (config.value_type === 'boolean') {
    return (
      <div className="flex items-center gap-3">
        <button
          onClick={() => {
            const newVal = value === 'true' ? 'false' : 'true';
            setValue(newVal);
            onSave(config.id, newVal);
          }}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${value === 'true' ? 'bg-cyan-500' : 'bg-slate-300'}`}>
          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${value === 'true' ? 'translate-x-6' : 'translate-x-1'}`} />
        </button>
        <span className="text-sm text-slate-500">{value === 'true' ? 'Aktif' : 'Pasif'}</span>
      </div>
    );
  }

  if (config.value_type === 'json') {
    return (
      <div className="space-y-2">
        <textarea value={value} onChange={(e) => setValue(e.target.value)}
          rows={4} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm font-mono" />
        {changed && (
          <button onClick={() => onSave(config.id, value)}
            className="inline-flex items-center gap-1 rounded-lg bg-cyan-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-600">
            <Save className="h-3 w-3" /> Kaydet
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <input
        type={config.value_type === 'integer' || config.value_type === 'float' ? 'number' : 'text'}
        value={value} onChange={(e) => setValue(e.target.value)}
        className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm" />
      {changed && (
        <button onClick={() => onSave(config.id, value)}
          className="inline-flex items-center gap-1 rounded-lg bg-cyan-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-600">
          <Save className="h-3 w-3" /> Kaydet
        </button>
      )}
    </div>
  );
}

export default function SiteConfigPage() {
  const { data: configs, isLoading } = useSiteConfigs();
  const updateConfig = useUpdateSiteConfig();

  const handleSave = (id: string, value: string) => {
    updateConfig.mutate({ id, value });
  };

  const categories = configs ? [...new Set(configs.map(c => c.category))].sort() : [];

  if (isLoading) return <div className="p-6"><div className="animate-pulse space-y-4">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-200 rounded-xl" />)}</div></div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/doctor/site-settings" className="text-slate-400 hover:text-slate-600"><ArrowLeft className="h-5 w-5" /></Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Site Ayarlari</h1>
          <p className="text-slate-500 text-sm">Genel site yapilandirmasi</p>
        </div>
      </div>

      {categories.map(cat => (
        <div key={cat} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="bg-slate-50 px-5 py-3 border-b border-slate-200">
            <h2 className="font-semibold text-slate-700 capitalize">{cat}</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {configs?.filter(c => c.category === cat).map(config => (
              <div key={config.id} className="px-5 py-4">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <div>
                    <p className="font-medium text-slate-900">{config.label}</p>
                    {config.description && <p className="text-xs text-slate-400 mt-0.5">{config.description}</p>}
                  </div>
                  <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded">{config.value_type}</span>
                </div>
                <ConfigInput config={config} onSave={handleSave} />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
