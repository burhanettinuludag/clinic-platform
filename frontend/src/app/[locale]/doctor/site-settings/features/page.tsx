'use client';

import { useState } from 'react';
import { useFeatureFlags, useToggleFeatureFlag } from '@/hooks/useSiteAdmin';
import { ArrowLeft, Shield } from 'lucide-react';
import { Link } from '@/i18n/navigation';

const DANGEROUS_FLAGS = ['payment_module', 'maintenance_mode', 'store_module'];

export default function FeaturesPage() {
  const { data: flags, isLoading } = useFeatureFlags();
  const toggleFlag = useToggleFeatureFlag();
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const handleToggle = (id: string, key: string, currentState: boolean) => {
    if (DANGEROUS_FLAGS.includes(key)) {
      setConfirmId(id);
      return;
    }
    toggleFlag.mutate({ id, is_enabled: !currentState });
  };

  const confirmToggle = () => {
    if (!confirmId || !flags) return;
    const flag = flags.find(f => f.id === confirmId);
    if (flag) toggleFlag.mutate({ id: confirmId, is_enabled: !flag.is_enabled });
    setConfirmId(null);
  };

  if (isLoading) return <div className="p-6"><div className="animate-pulse space-y-4">{[1,2,3,4].map(i => <div key={i} className="h-24 bg-slate-200 rounded-xl" />)}</div></div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/doctor/site-settings" className="text-slate-400 hover:text-slate-600"><ArrowLeft className="h-5 w-5" /></Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Ozellik Yonetimi</h1>
          <p className="text-slate-500 text-sm">Modul ve ozellik bayraklari</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {flags?.map(flag => {
          const isDangerous = DANGEROUS_FLAGS.includes(flag.key);
          return (
            <div key={flag.id}
              className={`bg-white rounded-xl border p-5 ${flag.is_enabled ? 'border-green-200' : 'border-slate-200'}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-slate-900">{flag.label}</h3>
                    {isDangerous && <Shield className="h-4 w-4 text-amber-500" />}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">{flag.key}</p>
                  {flag.description && <p className="text-sm text-slate-500 mt-2">{flag.description}</p>}
                </div>
                <button
                  onClick={() => handleToggle(flag.id, flag.key, flag.is_enabled)}
                  disabled={toggleFlag.isPending}
                  className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors ${flag.is_enabled ? 'bg-green-500' : 'bg-slate-300'}`}>
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${flag.is_enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Confirm dialog */}
      {confirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl p-6 max-w-sm mx-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">Emin misiniz?</h3>
            <p className="text-sm text-slate-500 mt-2">Bu kritik bir ozellik bayragi. Degistirmek siteyi etkileyebilir.</p>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setConfirmId(null)}
                className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Iptal</button>
              <button onClick={confirmToggle}
                className="flex-1 rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-white hover:bg-amber-600">Onayla</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
