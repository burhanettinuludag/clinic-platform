'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Plus, Clock, Trash2, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface Reminder { id: string; reminder_type: string; title: string; time_of_day: string; days_of_week: number[]; is_enabled: boolean; }

const TYPES = [{ value: 'medication', label: 'Ilac' }, { value: 'exercise', label: 'Egzersiz' }, { value: 'sleep', label: 'Uyku' }, { value: 'diary', label: 'Gunluk' }, { value: 'general', label: 'Genel' }];
const DAYS = ['Pzt', 'Sal', 'Car', 'Per', 'Cum', 'Cmt', 'Paz'];
const TYPE_COLORS: Record<string, string> = { medication: 'bg-blue-100 text-blue-700', exercise: 'bg-green-100 text-green-700', sleep: 'bg-purple-100 text-purple-700', diary: 'bg-yellow-100 text-yellow-700', general: 'bg-gray-100 text-gray-700' };

export default function RemindersPage() {
  const { data: reminders, isLoading } = useQuery<Reminder[]>({ queryKey: ['reminders'], queryFn: async () => { const { data } = await api.get('/tracking/reminders/'); return data.results || data; } });
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ reminder_type: 'general', title: '', time_of_day: '08:00', days_of_week: [0,1,2,3,4,5,6] });
  const qc = useQueryClient();

  const createMut = useMutation({ mutationFn: async (d: any) => (await api.post('/tracking/reminders/', d)).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ['reminders'] }); setShowForm(false); } });
  const deleteMut = useMutation({ mutationFn: async (id: string) => { await api.delete('/tracking/reminders/' + id + '/'); }, onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }) });
  const toggleMut = useMutation({ mutationFn: async ({ id, enabled }: { id: string; enabled: boolean }) => (await api.patch('/tracking/reminders/' + id + '/', { is_enabled: enabled })).data, onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }) });

  const toggleDay = (day: number) => { setForm({ ...form, days_of_week: form.days_of_week.includes(day) ? form.days_of_week.filter(x => x !== day) : [...form.days_of_week, day] }); };

  if (isLoading) return <div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>;

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3"><Bell className="h-6 w-6 text-blue-600" /><h1 className="text-xl font-bold text-gray-900">Hatirlaticilar</h1></div>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 rounded-lg bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"><Plus className="h-4 w-4" /> Yeni</button>
      </div>

      {showForm && (
        <div className="rounded-xl border bg-white p-4 mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs text-gray-500 mb-1">Tur</label><select value={form.reminder_type} onChange={e => setForm({...form, reminder_type: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm bg-white">{TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}</select></div>
            <div><label className="block text-xs text-gray-500 mb-1">Saat</label><input type="time" value={form.time_of_day} onChange={e => setForm({...form, time_of_day: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" /></div>
          </div>
          <div><label className="block text-xs text-gray-500 mb-1">Baslik</label><input value={form.title} onChange={e => setForm({...form, title: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Hatirlat: ..." /></div>
          <div>
            <label className="block text-xs text-gray-500 mb-2">Gunler</label>
            <div className="flex gap-1">{DAYS.map((d, i) => (<button key={i} type="button" onClick={() => toggleDay(i)} className={'flex-1 py-1.5 rounded text-xs font-medium transition-colors ' + (form.days_of_week.includes(i) ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500')}>{d}</button>))}</div>
          </div>
          <button onClick={() => createMut.mutate(form)} disabled={!form.title || createMut.isPending} className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">{createMut.isPending ? 'Kaydediliyor...' : 'Olustur'}</button>
        </div>
      )}

      {(reminders || []).length > 0 ? (
        <div className="space-y-2">{(reminders || []).map(r => (
          <div key={r.id} className="rounded-lg border bg-white p-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => toggleMut.mutate({ id: r.id, enabled: !r.is_enabled })} className={'relative w-10 h-5 rounded-full transition-colors ' + (r.is_enabled ? 'bg-blue-600' : 'bg-gray-200')}><span className={'absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ' + (r.is_enabled ? 'translate-x-5' : '')} /></button>
              <div>
                <p className={'text-sm font-medium ' + (r.is_enabled ? 'text-gray-900' : 'text-gray-400')}>{r.title}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className={'rounded px-1.5 py-0.5 text-xs ' + (TYPE_COLORS[r.reminder_type] || TYPE_COLORS.general)}>{TYPES.find(t => t.value === r.reminder_type)?.label}</span>
                  <span className="flex items-center gap-1 text-xs text-gray-400"><Clock className="h-3 w-3" />{r.time_of_day?.slice(0,5)}</span>
                </div>
              </div>
            </div>
            <button onClick={() => deleteMut.mutate(r.id)} className="p-1.5 text-gray-300 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
          </div>
        ))}</div>
      ) : (<div className="text-center py-8 text-gray-400 text-sm">Henuz hatirlaticiniz yok</div>)}
    </div>
  );
}
