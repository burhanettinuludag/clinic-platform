'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Lock, Eye, EyeOff, CheckCircle, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function ChangePasswordPage() {
  const [form, setForm] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [success, setSuccess] = useState(false);

  const mutation = useMutation({
    mutationFn: async (data: typeof form) => {
      const { data: res } = await api.post('/auth/password/change/', {
        old_password: data.old_password,
        new_password: data.new_password,
      });
      return res;
    },
    onSuccess: () => {
      setSuccess(true);
      setForm({ old_password: '', new_password: '', confirm_password: '' });
    },
  });

  const errors = (mutation.error as any)?.response?.data || {};
  const passwordMismatch = form.confirm_password && form.new_password !== form.confirm_password;
  const tooShort = form.new_password && form.new_password.length < 8;
  const canSubmit = form.old_password && form.new_password && form.confirm_password && !passwordMismatch && !tooShort && !mutation.isPending;

  if (success) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
          <CheckCircle className="h-8 w-8 text-green-500" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Sifreniz Degistirildi</h2>
        <p className="text-gray-500">Yeni sifreniz aktif edildi.</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 py-12">
      <div className="flex items-center gap-3 mb-6">
        <Lock className="h-6 w-6 text-blue-600" />
        <h1 className="text-xl font-bold text-gray-900">Sifre Degistir</h1>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Mevcut Sifre</label>
          <div className="relative">
            <input type={showOld ? 'text' : 'password'} value={form.old_password}
              onChange={e => setForm({...form, old_password: e.target.value})}
              className="w-full rounded-lg border px-3 py-2 text-sm pr-10" />
            <button type="button" onClick={() => setShowOld(!showOld)}
              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
              {showOld ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.old_password && <p className="text-xs text-red-500 mt-1">{errors.old_password}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Yeni Sifre</label>
          <div className="relative">
            <input type={showNew ? 'text' : 'password'} value={form.new_password}
              onChange={e => setForm({...form, new_password: e.target.value})}
              className="w-full rounded-lg border px-3 py-2 text-sm pr-10" />
            <button type="button" onClick={() => setShowNew(!showNew)}
              className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600">
              {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {tooShort && <p className="text-xs text-orange-500 mt-1">Sifre en az 8 karakter olmali</p>}
          {errors.new_password && <p className="text-xs text-red-500 mt-1">{errors.new_password}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Yeni Sifre (Tekrar)</label>
          <input type="password" value={form.confirm_password}
            onChange={e => setForm({...form, confirm_password: e.target.value})}
            className="w-full rounded-lg border px-3 py-2 text-sm" />
          {passwordMismatch && <p className="text-xs text-red-500 mt-1">Sifreler eslesmiyor</p>}
        </div>

        <button onClick={() => mutation.mutate(form)} disabled={!canSubmit}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Lock className="h-4 w-4" />}
          Sifreyi Degistir
        </button>

        {mutation.isError && !errors.old_password && !errors.new_password && (
          <p className="text-sm text-red-500 text-center">Bir hata olustu. Tekrar deneyin.</p>
        )}
      </div>
    </div>
  );
}
