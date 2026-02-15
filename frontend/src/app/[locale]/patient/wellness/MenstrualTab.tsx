'use client';

import { useState, useEffect } from 'react';
import { Calendar, Plus, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface MenstrualLog {
  id: number;
  date: string;
  is_period_day: boolean;
  flow_intensity: string;
  has_cramps: boolean;
  cramp_intensity: number | null;
  has_headache: boolean;
  has_mood_changes: boolean;
  has_bloating: boolean;
  has_fatigue: boolean;
  notes: string;
}

const FLOW_LABELS: Record<string, string> = { spotting: 'Lekelenme', light: 'Hafif', medium: 'Orta', heavy: 'Yogun' };
const FLOW_COLORS: Record<string, string> = { spotting: 'bg-pink-100 text-pink-600', light: 'bg-pink-200 text-pink-700', medium: 'bg-red-200 text-red-700', heavy: 'bg-red-300 text-red-800' };

function today() { return new Date().toISOString().split('T')[0]; }

export default function MenstrualTab() {
  const [logs, setLogs] = useState<MenstrualLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    date: today(), is_period_day: true, flow_intensity: 'medium',
    has_cramps: false, cramp_intensity: 5,
    has_headache: false, has_mood_changes: false, has_bloating: false, has_fatigue: false, notes: '',
  });
  const [saving, setSaving] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.get('/wellness/menstrual/');
      setLogs(res.data.results || res.data);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchLogs(); }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.post('/wellness/menstrual/', form);
      setShowForm(false);
      setForm({ ...form, date: today(), notes: '', has_cramps: false, has_headache: false, has_mood_changes: false, has_bloating: false, has_fatigue: false });
      fetchLogs();
    } catch {} finally { setSaving(false); }
  };

  const symptoms = (log: MenstrualLog) => {
    const s = [];
    if (log.has_cramps) s.push('Kramp');
    if (log.has_headache) s.push('Bas agrisi');
    if (log.has_mood_changes) s.push('Ruh hali');
    if (log.has_bloating) s.push('Sisman.');
    if (log.has_fatigue) s.push('Yorgunluk');
    return s;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Dongu Takibi</h3>
        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 rounded-lg bg-pink-500 px-3 py-1.5 text-sm text-white hover:bg-pink-600">
          <Plus className="h-4 w-4" /> Kayit Ekle
        </button>
      </div>

      {showForm && (
        <div className="rounded-xl border bg-white p-4 mb-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Tarih</label>
              <input type="date" value={form.date} onChange={e => setForm({...form, date: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Akis Yogunlugu</label>
              <select value={form.flow_intensity} onChange={e => setForm({...form, flow_intensity: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm bg-white">
                <option value="spotting">Lekelenme</option>
                <option value="light">Hafif</option>
                <option value="medium">Orta</option>
                <option value="heavy">Yogun</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-2">Belirtiler</label>
            <div className="flex flex-wrap gap-2">
              {[
                { key: 'has_cramps', label: 'Kramp' },
                { key: 'has_headache', label: 'Bas Agrisi' },
                { key: 'has_mood_changes', label: 'Ruh Hali Degisimi' },
                { key: 'has_bloating', label: 'Siskinlik' },
                { key: 'has_fatigue', label: 'Yorgunluk' },
              ].map(s => (
                <button key={s.key} type="button"
                  onClick={() => setForm({...form, [s.key]: !(form as any)[s.key]})}
                  className={'rounded-full px-3 py-1 text-xs font-medium border transition-colors ' +
                    ((form as any)[s.key] ? 'bg-pink-100 border-pink-300 text-pink-700' : 'bg-gray-50 border-gray-200 text-gray-500')}>
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {form.has_cramps && (
            <div>
              <label className="block text-xs text-gray-500 mb-1">Kramp Siddeti: {form.cramp_intensity}/10</label>
              <input type="range" min={1} max={10} value={form.cramp_intensity} onChange={e => setForm({...form, cramp_intensity: +e.target.value})} className="w-full" />
            </div>
          )}

          <div>
            <label className="block text-xs text-gray-500 mb-1">Notlar</label>
            <input value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Ek notlar..." />
          </div>

          <button onClick={handleSave} disabled={saving} className="w-full rounded-lg bg-pink-500 py-2 text-sm font-medium text-white hover:bg-pink-600 disabled:opacity-50">
            {saving ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-pink-500" /></div>
      ) : logs.length > 0 ? (
        <div className="space-y-2">
          {logs.slice(0, 30).map(log => (
            <div key={log.id} className="rounded-lg border bg-white p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 text-sm text-gray-600">
                  <Calendar className="h-4 w-4" />
                  {new Date(log.date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                </div>
                <span className={'rounded-full px-2 py-0.5 text-xs font-medium ' + (FLOW_COLORS[log.flow_intensity] || 'bg-gray-100')}>
                  {FLOW_LABELS[log.flow_intensity] || log.flow_intensity}
                </span>
              </div>
              <div className="flex gap-1">
                {symptoms(log).map(s => (
                  <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">{s}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400 text-sm">Henuz kayit yok</div>
      )}
    </div>
  );
}
