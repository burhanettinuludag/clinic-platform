'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Loader2, CheckCircle, Shield, Plus, X, User, BookOpen, GraduationCap, Building, Globe, Award } from 'lucide-react';
import { useAuthorProfile, useUpdateAuthorProfile, useCreateAuthorProfile } from '@/hooks/useAuthorData';

const SPECIALTIES = [
  { value: 'neurology', label: 'Noroloji' },
  { value: 'neurosurgery', label: 'Norosirurji' },
  { value: 'psychiatry', label: 'Psikiyatri' },
  { value: 'internal_medicine', label: 'Dahiliye' },
  { value: 'pediatrics', label: 'Pediatri' },
  { value: 'family_medicine', label: 'Aile Hekimligi' },
  { value: 'physical_therapy', label: 'FTR' },
  { value: 'general', label: 'Genel' },
];

type TabId = 'basic' | 'academic' | 'social';

export default function AuthorProfilePage() {
  const router = useRouter();
  const { data: profile, isLoading, error } = useAuthorProfile();
  const updateMut = useUpdateAuthorProfile();
  const createMut = useCreateAuthorProfile();
  const [tab, setTab] = useState<TabId>('basic');
  const [saved, setSaved] = useState(false);
  const isNew = !profile && !isLoading;

  const [form, setForm] = useState({
    primary_specialty: 'neurology',
    bio_tr: '', bio_en: '',
    headline_tr: '', headline_en: '',
    institution: '', department: '', city: '',
    orcid_id: '', google_scholar_url: '', pubmed_author_id: '',
    linkedin_url: '', website_url: '',
    memberships: [] as string[],
  });
  const [newMembership, setNewMembership] = useState('');

  useEffect(() => {
    if (profile) {
      setForm({
        primary_specialty: profile.primary_specialty || 'neurology',
        bio_tr: profile.bio_tr || '', bio_en: profile.bio_en || '',
        headline_tr: profile.headline_tr || '', headline_en: profile.headline_en || '',
        institution: profile.institution || '', department: profile.department || '', city: profile.city || '',
        orcid_id: profile.orcid_id || '', google_scholar_url: profile.google_scholar_url || '', pubmed_author_id: profile.pubmed_author_id || '',
        linkedin_url: profile.linkedin_url || '', website_url: profile.website_url || '',
        memberships: profile.memberships || [],
      });
    }
  }, [profile]);

  if (isLoading) return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-gray-400" /></div>;

  const handleSave = () => {
    const payload = { ...form };
    if (isNew) {
      createMut.mutate(payload, { onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000); } });
    } else {
      updateMut.mutate(payload, { onSuccess: () => { setSaved(true); setTimeout(() => setSaved(false), 2000); } });
    }
  };

  const isPending = updateMut.isPending || createMut.isPending;

  const addMembership = () => {
    if (newMembership.trim()) {
      setForm({ ...form, memberships: [...form.memberships, newMembership.trim()] });
      setNewMembership('');
    }
  };

  const removeMembership = (i: number) => {
    setForm({ ...form, memberships: form.memberships.filter((_, idx) => idx !== i) });
  };

  const tabs: { id: TabId; label: string; icon: typeof User }[] = [
    { id: 'basic', label: 'Temel Bilgiler', icon: User },
    { id: 'academic', label: 'Akademik', icon: GraduationCap },
    { id: 'social', label: 'Linkler & Uyelikler', icon: Globe },
  ];

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button onClick={() => router.push('/doctor/author')} className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4" />Geri
        </button>
        {profile && (
          <div className="flex items-center gap-2">
            {profile.is_verified && <span className="flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700"><Shield className="h-3 w-3" />Dogrulanmis</span>}
            <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">{profile.level_display}</span>
          </div>
        )}
      </div>

      <h1 className="text-xl font-bold text-gray-900 mb-1">{isNew ? 'Yazar Profili Olustur' : 'Yazar Profili Duzenle'}</h1>
      {profile && <p className="text-sm text-gray-500 mb-6">{profile.full_name} - {profile.email}</p>}

      {/* Tabs */}
      <div className="flex gap-1 border-b mb-6">
        {tabs.map(t => {
          const Icon = t.icon;
          return (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={'flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors ' + (tab === t.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
              <Icon className="h-4 w-4" />{t.label}
            </button>
          );
        })}
      </div>

      {/* Basic Tab */}
      {tab === 'basic' && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Uzmanlik Alani</label>
            <select value={form.primary_specialty} onChange={e => setForm({...form, primary_specialty: e.target.value})}
              className="w-full rounded-lg border px-3 py-2 text-sm bg-white">
              {SPECIALTIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Kurum</label>
              <input value={form.institution} onChange={e => setForm({...form, institution: e.target.value})} placeholder="Ege Universitesi" className="w-full rounded-lg border px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Bolum</label>
              <input value={form.department} onChange={e => setForm({...form, department: e.target.value})} placeholder="Noroloji ABD" className="w-full rounded-lg border px-3 py-2 text-sm" /></div>
            <div><label className="block text-xs font-medium text-gray-600 mb-1">Sehir</label>
              <input value={form.city} onChange={e => setForm({...form, city: e.target.value})} placeholder="Izmir" className="w-full rounded-lg border px-3 py-2 text-sm" /></div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (TR)</label>
            <input value={form.headline_tr} onChange={e => setForm({...form, headline_tr: e.target.value})} placeholder="Noroloji Uzmani, Klinik Norofizyoloji Yan Dal Uzmani" className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Baslik (EN)</label>
            <input value={form.headline_en} onChange={e => setForm({...form, headline_en: e.target.value})} placeholder="Neurologist, Clinical Neurophysiology Subspecialist" className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Biyografi (TR)</label>
            <textarea value={form.bio_tr} onChange={e => setForm({...form, bio_tr: e.target.value})} rows={4} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Biyografi (EN)</label>
            <textarea value={form.bio_en} onChange={e => setForm({...form, bio_en: e.target.value})} rows={4} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
        </div>
      )}

      {/* Academic Tab */}
      {tab === 'academic' && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">ORCID ID</label>
            <input value={form.orcid_id} onChange={e => setForm({...form, orcid_id: e.target.value})} placeholder="0000-0000-0000-0000" className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Google Scholar URL</label>
            <input value={form.google_scholar_url} onChange={e => setForm({...form, google_scholar_url: e.target.value})} placeholder="https://scholar.google.com/..." className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">PubMed Author ID</label>
            <input value={form.pubmed_author_id} onChange={e => setForm({...form, pubmed_author_id: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          {/* Stats (read-only) */}
          {profile && (
            <div className="border-t pt-4 mt-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Istatistikler</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[['Makale', profile.total_articles], ['Goruntulenme', profile.total_views], ['Ort. Puan', profile.average_rating], ['Seviye', profile.author_level + '/4']].map(([l, v]) => (
                  <div key={String(l)} className="rounded-lg border bg-gray-50 p-3 text-center">
                    <p className="text-[10px] text-gray-500">{l}</p>
                    <p className="text-lg font-bold text-gray-900">{v}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Social Tab */}
      {tab === 'social' && (
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">LinkedIn URL</label>
            <input value={form.linkedin_url} onChange={e => setForm({...form, linkedin_url: e.target.value})} placeholder="https://linkedin.com/in/..." className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Website URL</label>
            <input value={form.website_url} onChange={e => setForm({...form, website_url: e.target.value})} placeholder="https://..." className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Uyelikler</label>
            <div className="space-y-2">
              {form.memberships.map((m, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="flex-1 rounded-lg border bg-gray-50 px-3 py-2 text-sm">{m}</span>
                  <button onClick={() => removeMembership(i)} className="p-1 text-red-400 hover:text-red-600"><X className="h-4 w-4" /></button>
                </div>
              ))}
              <div className="flex gap-2">
                <input value={newMembership} onChange={e => setNewMembership(e.target.value)} onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addMembership())}
                  placeholder="Turk Noroloji Dernegi" className="flex-1 rounded-lg border px-3 py-2 text-sm" />
                <button onClick={addMembership} className="rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"><Plus className="h-4 w-4" /></button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save Button */}
      <div className="flex items-center gap-3 border-t pt-4 mt-6">
        <button onClick={handleSave} disabled={isPending} className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}{isNew ? 'Olustur' : 'Kaydet'}
        </button>
        {saved && <span className="flex items-center gap-1 text-sm text-green-600"><CheckCircle className="h-4 w-4" />Kaydedildi</span>}
      </div>
    </div>
  );
}
