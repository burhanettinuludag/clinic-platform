'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Mail, Smartphone, Moon, Loader2, CheckCircle } from 'lucide-react';
import api from '@/lib/api';

interface Prefs {
  email_reminders: boolean;
  push_reminders: boolean;
  email_education: boolean;
  email_product_updates: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
}

function usePrefs() {
  return useQuery<Prefs>({
    queryKey: ['notification-prefs'],
    queryFn: async () => (await api.get('/notifications/settings/preferences/')).data,
  });
}

function Toggle({ label, desc, checked, onChange, icon: Icon }: { label: string; desc: string; checked: boolean; onChange: (v: boolean) => void; icon: any }) {
  return (
    <div className="flex items-center justify-between py-3">
      <div className="flex items-start gap-3">
        <Icon className="h-5 w-5 text-gray-400 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-gray-900">{label}</p>
          <p className="text-xs text-gray-500">{desc}</p>
        </div>
      </div>
      <button type="button" onClick={() => onChange(!checked)}
        className={'relative w-11 h-6 rounded-full transition-colors ' + (checked ? 'bg-blue-600' : 'bg-gray-200')}>
        <span className={'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ' + (checked ? 'translate-x-5' : '')} />
      </button>
    </div>
  );
}

export default function NotificationSettingsPage() {
  const { data: prefs, isLoading } = usePrefs();
  const [form, setForm] = useState<Prefs | null>(null);
  const [saved, setSaved] = useState(false);
  const qc = useQueryClient();

  useEffect(() => {
    if (prefs && !form) setForm(prefs);
  }, [prefs]);

  const mutation = useMutation({
    mutationFn: async (data: Partial<Prefs>) => {
      const { data: res } = await api.patch('/notifications/settings/preferences/', data);
      return res;
    },
    onSuccess: (data) => {
      qc.setQueryData(['notification-prefs'], data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  if (isLoading || !form) {
    return <div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>;
  }

  const update = (key: keyof Prefs, val: any) => {
    const next = { ...form, [key]: val };
    setForm(next);
    mutation.mutate({ [key]: val });
  };

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Bell className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">Bildirim Tercihleri</h1>
        </div>
        {saved && (
          <span className="flex items-center gap-1 text-xs text-green-600">
            <CheckCircle className="h-3.5 w-3.5" /> Kaydedildi
          </span>
        )}
      </div>

      <div className="rounded-xl border bg-white divide-y">
        <div className="px-4">
          <Toggle icon={Mail} label="Email Hatirlaticlari" desc="Ilac, gorev ve randevu hatirlatmalari email ile"
            checked={form.email_reminders} onChange={v => update('email_reminders', v)} />
        </div>
        <div className="px-4">
          <Toggle icon={Smartphone} label="Push Hatirlaticlari" desc="Anlik bildirimler (tarayici/mobil)"
            checked={form.push_reminders} onChange={v => update('push_reminders', v)} />
        </div>
        <div className="px-4">
          <Toggle icon={Mail} label="Egitim Icerik Bildirimleri" desc="Yeni egitim icerik ve makaleler email ile"
            checked={form.email_education} onChange={v => update('email_education', v)} />
        </div>
        <div className="px-4">
          <Toggle icon={Mail} label="Urun Guncellemeleri" desc="Platform guncellemeleri ve yeni ozellikler"
            checked={form.email_product_updates} onChange={v => update('email_product_updates', v)} />
        </div>
      </div>

      {/* Sessiz Saatler */}
      <div className="mt-6 rounded-xl border bg-white p-4">
        <div className="flex items-center gap-2 mb-3">
          <Moon className="h-5 w-5 text-gray-400" />
          <p className="text-sm font-medium text-gray-900">Sessiz Saatler</p>
        </div>
        <p className="text-xs text-gray-500 mb-3">Bu saatler arasinda bildirim gonderilmez.</p>
        <div className="flex items-center gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Baslangic</label>
            <input type="time" value={form.quiet_hours_start || ''} onChange={e => update('quiet_hours_start', e.target.value || null)}
              className="rounded-lg border px-3 py-1.5 text-sm" />
          </div>
          <span className="text-gray-300 mt-5">—</span>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Bitis</label>
            <input type="time" value={form.quiet_hours_end || ''} onChange={e => update('quiet_hours_end', e.target.value || null)}
              className="rounded-lg border px-3 py-1.5 text-sm" />
          </div>
        </div>
      </div>
    </div>
  );
}
