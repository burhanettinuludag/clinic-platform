'use client';

import { useState } from 'react';
import { useAnnouncements, useCreateAnnouncement, useUpdateAnnouncement, useDeleteAnnouncement } from '@/hooks/useSiteAdmin';
import type { Announcement } from '@/hooks/useSiteAdmin';
import { ArrowLeft, Plus, Trash2, Edit2, X, Eye } from 'lucide-react';
import { Link } from '@/i18n/navigation';

const emptyForm: Partial<Announcement> = {
  title_tr: '', title_en: '', message_tr: '', message_en: '',
  link_url: '', link_text_tr: '', link_text_en: '',
  bg_color: '#1B4F72', text_color: '#FFFFFF', is_active: false,
  priority: 0, starts_at: null, expires_at: null,
};

export default function AnnouncementsPage() {
  const { data: announcements, isLoading } = useAnnouncements();
  const createAnnouncement = useCreateAnnouncement();
  const updateAnnouncement = useUpdateAnnouncement();
  const deleteAnnouncement = useDeleteAnnouncement();
  const [form, setForm] = useState<Partial<Announcement> | null>(null);
  const [editId, setEditId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const openNew = () => { setForm({ ...emptyForm }); setEditId(null); };
  const openEdit = (a: Announcement) => { setForm({ ...a }); setEditId(a.id); };
  const close = () => { setForm(null); setEditId(null); };

  const handleSave = () => {
    if (!form) return;
    if (editId) {
      updateAnnouncement.mutate({ id: editId, ...form }, { onSuccess: close });
    } else {
      createAnnouncement.mutate(form, { onSuccess: close });
    }
  };

  const handleDelete = () => {
    if (deleteId) {
      deleteAnnouncement.mutate(deleteId, { onSuccess: () => setDeleteId(null) });
    }
  };

  const updateField = (key: string, value: unknown) => setForm(prev => prev ? { ...prev, [key]: value } : null);

  if (isLoading) return <div className="p-6"><div className="animate-pulse space-y-4">{[1,2,3].map(i => <div key={i} className="h-24 bg-slate-200 rounded-xl" />)}</div></div>;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/doctor/site-settings" className="text-slate-400 hover:text-slate-600"><ArrowLeft className="h-5 w-5" /></Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Duyurular</h1>
            <p className="text-slate-500 text-sm">Site bandi duyurulari</p>
          </div>
        </div>
        <button onClick={openNew} className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600">
          <Plus className="h-4 w-4" /> Yeni Duyuru
        </button>
      </div>

      {/* List */}
      <div className="space-y-3">
        {announcements?.map(a => (
          <div key={a.id} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`h-3 w-3 rounded-full ${a.is_active ? 'bg-green-500' : 'bg-slate-300'}`} />
                <div>
                  <p className="font-medium text-slate-900">{a.title_tr}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{a.message_tr.slice(0, 80)}...</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Oncelik: {a.priority}</span>
                <button onClick={() => openEdit(a)} className="p-1.5 text-slate-400 hover:text-cyan-500"><Edit2 className="h-4 w-4" /></button>
                <button onClick={() => setDeleteId(a.id)} className="p-1.5 text-slate-400 hover:text-red-500"><Trash2 className="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        ))}
        {announcements?.length === 0 && <p className="text-center text-slate-400 py-8">Henuz duyuru yok.</p>}
      </div>

      {/* Form Modal */}
      {form && (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 overflow-y-auto py-8">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4 shadow-2xl">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-slate-900">{editId ? 'Duyuru Duzenle' : 'Yeni Duyuru'}</h3>
              <button onClick={close} className="text-slate-400 hover:text-slate-600"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Baslik (TR)</label>
                  <input value={form.title_tr || ''} onChange={e => updateField('title_tr', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Baslik (EN)</label>
                  <input value={form.title_en || ''} onChange={e => updateField('title_en', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Mesaj (TR)</label>
                  <textarea value={form.message_tr || ''} onChange={e => updateField('message_tr', e.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Mesaj (EN)</label>
                  <textarea value={form.message_en || ''} onChange={e => updateField('message_en', e.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Link URL</label>
                  <input value={form.link_url || ''} onChange={e => updateField('link_url', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Link Text (TR)</label>
                  <input value={form.link_text_tr || ''} onChange={e => updateField('link_text_tr', e.target.value)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Oncelik</label>
                  <input type="number" value={form.priority ?? 0} onChange={e => updateField('priority', parseInt(e.target.value) || 0)} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /></div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Arka Plan</label>
                  <input type="color" value={form.bg_color || '#1B4F72'} onChange={e => updateField('bg_color', e.target.value)} className="h-10 w-full rounded-lg border border-slate-300" /></div>
                <div><label className="block text-xs font-medium text-slate-500 mb-1">Yazi Rengi</label>
                  <input type="color" value={form.text_color || '#FFFFFF'} onChange={e => updateField('text_color', e.target.value)} className="h-10 w-full rounded-lg border border-slate-300" /></div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.is_active || false} onChange={e => updateField('is_active', e.target.checked)} className="h-4 w-4 rounded" />
                    <span className="text-sm text-slate-700">Aktif</span>
                  </label>
                </div>
              </div>

              {/* Preview */}
              <div>
                <label className="flex items-center gap-1 text-xs font-medium text-slate-500 mb-1"><Eye className="h-3 w-3" /> Onizleme</label>
                <div className="rounded-lg px-4 py-3 text-center text-sm" style={{ backgroundColor: form.bg_color || '#1B4F72', color: form.text_color || '#FFFFFF' }}>
                  <strong>{form.title_tr || 'Baslik'}</strong> &mdash; {form.message_tr || 'Mesaj icerigi'}
                  {form.link_url && <span className="underline ml-2">{form.link_text_tr || 'Detay'}</span>}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={close} className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Iptal</button>
              <button onClick={handleSave} disabled={createAnnouncement.isPending || updateAnnouncement.isPending}
                className="flex-1 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-medium text-white hover:bg-cyan-600 disabled:opacity-50">Kaydet</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete confirm */}
      {deleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl p-6 max-w-sm mx-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-900">Duyuruyu Sil</h3>
            <p className="text-sm text-slate-500 mt-2">Bu islem geri alinamaz.</p>
            <div className="flex gap-3 mt-5">
              <button onClick={() => setDeleteId(null)} className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Iptal</button>
              <button onClick={handleDelete} className="flex-1 rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600">Sil</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
