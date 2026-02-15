'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Stethoscope, Loader2, CheckCircle, Save, UserCheck } from 'lucide-react';
import api from '@/lib/api';

interface UserInfo { first_name: string; last_name: string; email: string; phone: string; }
interface DoctorProfile { specialty: string; license_number: string; bio: string; is_accepting_patients: boolean; }

function useUserInfo() {
  return useQuery<UserInfo>({ queryKey: ['user-info'], queryFn: async () => (await api.get('/users/me/')).data });
}
function useDoctorProfile() {
  return useQuery<DoctorProfile>({ queryKey: ['doctor-profile'], queryFn: async () => (await api.get('/users/me/doctor-profile/')).data });
}

const SPECIALTIES = [
  { value: '', label: 'Seciniz' },
  { value: 'neurology', label: 'Noroloji' },
  { value: 'neurosurgery', label: 'Beyin ve Sinir Cerrahisi' },
  { value: 'psychiatry', label: 'Psikiyatri' },
  { value: 'ftr', label: 'Fiziksel Tip ve Rehabilitasyon' },
  { value: 'physiology', label: 'Fizyoloji' },
  { value: 'geriatrics', label: 'Geriatri' },
  { value: 'sleep_medicine', label: 'Uyku Bozukluklari' },
  { value: 'other', label: 'Diger' },
];

export default function DoctorProfilePage() {
  const { data: user, isLoading: loadU } = useUserInfo();
  const { data: profile, isLoading: loadP } = useDoctorProfile();
  const [userForm, setUserForm] = useState<UserInfo | null>(null);
  const [profForm, setProfForm] = useState<DoctorProfile | null>(null);
  const [saved, setSaved] = useState(false);
  const qc = useQueryClient();

  useEffect(() => { if (user && !userForm) setUserForm(user); }, [user]);
  useEffect(() => { if (profile && !profForm) setProfForm(profile); }, [profile]);

  const userMut = useMutation({
    mutationFn: async (data: Partial<UserInfo>) => (await api.patch('/users/me/', data)).data,
    onSuccess: (data) => { qc.setQueryData(['user-info'], data); setSaved(true); setTimeout(() => setSaved(false), 2000); },
  });
  const profMut = useMutation({
    mutationFn: async (data: Partial<DoctorProfile>) => (await api.patch('/users/me/doctor-profile/', data)).data,
    onSuccess: (data) => { qc.setQueryData(['doctor-profile'], data); setSaved(true); setTimeout(() => setSaved(false), 2000); },
  });

  const handleSave = () => {
    if (userForm) userMut.mutate({ first_name: userForm.first_name, last_name: userForm.last_name, phone: userForm.phone });
    if (profForm) profMut.mutate(profForm);
  };

  if (loadU || loadP || !userForm || !profForm) {
    return <div className="flex justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-blue-500" /></div>;
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Stethoscope className="h-6 w-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">Doktor Profili</h1>
        </div>
        {saved && <span className="flex items-center gap-1 text-xs text-green-600"><CheckCircle className="h-3.5 w-3.5" /> Kaydedildi</span>}
      </div>

      <div className="rounded-xl border bg-white p-4 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Kisisel Bilgiler</h2>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Ad</label>
            <input value={userForm.first_name} onChange={e => setUserForm({...userForm, first_name: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Soyad</label>
            <input value={userForm.last_name} onChange={e => setUserForm({...userForm, last_name: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="mt-3">
          <label className="block text-xs text-gray-500 mb-1">Email</label>
          <input value={userForm.email} disabled className="w-full rounded-lg border px-3 py-2 text-sm bg-gray-50 text-gray-400" />
        </div>
        <div className="mt-3">
          <label className="block text-xs text-gray-500 mb-1">Telefon</label>
          <input value={userForm.phone || ''} onChange={e => setUserForm({...userForm, phone: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="+90 5XX XXX XX XX" />
        </div>
      </div>

      <div className="rounded-xl border bg-white p-4 mb-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Mesleki Bilgiler</h2>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Uzmanlik</label>
            <select value={profForm.specialty} onChange={e => setProfForm({...profForm, specialty: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm bg-white">
              {SPECIALTIES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Lisans No</label>
            <input value={profForm.license_number} onChange={e => setProfForm({...profForm, license_number: e.target.value})} className="w-full rounded-lg border px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="mt-3">
          <label className="block text-xs text-gray-500 mb-1">Biyografi</label>
          <textarea value={profForm.bio} onChange={e => setProfForm({...profForm, bio: e.target.value})} rows={4} className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Uzmanlik alanlari, deneyim..." />
        </div>
      </div>

      <div className="rounded-xl border bg-white p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-start gap-3">
            <UserCheck className="h-5 w-5 text-gray-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Hasta Kabul</p>
              <p className="text-xs text-gray-500">Yeni hasta kabul durumu</p>
            </div>
          </div>
          <button type="button" onClick={() => setProfForm({...profForm, is_accepting_patients: !profForm.is_accepting_patients})}
            className={'relative w-11 h-6 rounded-full transition-colors ' + (profForm.is_accepting_patients ? 'bg-green-500' : 'bg-gray-200')}>
            <span className={'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ' + (profForm.is_accepting_patients ? 'translate-x-5' : '')} />
          </button>
        </div>
      </div>

      <button onClick={handleSave} disabled={userMut.isPending || profMut.isPending}
        className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
        {(userMut.isPending || profMut.isPending) ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        Kaydet
      </button>
    </div>
  );
}
