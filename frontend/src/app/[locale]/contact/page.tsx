'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, CheckCircle, Mail, Phone, MapPin, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [sent, setSent] = useState(false);

  const mutation = useMutation({
    mutationFn: async (data: typeof form) => {
      const { data: res } = await api.post('/contact/', { ...data, recaptcha_token: '' });
      return res;
    },
    onSuccess: () => setSent(true),
  });

  const errors = (mutation.error as any)?.response?.data?.errors || {};

  if (sent) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
          <CheckCircle className="h-8 w-8 text-green-500" />
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Mesajiniz Alindi</h2>
        <p className="text-gray-500">En kisa surede donus yapacagiz. Tesekkurler!</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Iletisim</h1>
      <p className="text-gray-500 mb-8">Soru, oneri veya geri bildirimleriniz icin bize ulasin.</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Info */}
        <div className="space-y-6">
          <div className="flex items-start gap-3">
            <Mail className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Email</p>
              <a href="mailto:info@norosera.com" className="text-sm text-blue-600">info@norosera.com</a>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Phone className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Telefon</p>
              <a href="tel:+902321234567" className="text-sm text-blue-600">+90 232 123 45 67</a>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <MapPin className="h-5 w-5 text-blue-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">Adres</p>
              <p className="text-sm text-gray-500">Ege Universitesi Tip Fakultesi, Bornova, Izmir</p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="md:col-span-2">
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Adiniz</label>
                <input value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                  className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Ad Soyad" />
                {errors.name && <p className="text-xs text-red-500 mt-1">{errors.name}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Email</label>
                <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                  className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="ornek@email.com" />
                {errors.email && <p className="text-xs text-red-500 mt-1">{errors.email}</p>}
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Konu</label>
              <input value={form.subject} onChange={e => setForm({...form, subject: e.target.value})}
                className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Mesajinizin konusu" />
              {errors.subject && <p className="text-xs text-red-500 mt-1">{errors.subject}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Mesaj</label>
              <textarea value={form.message} onChange={e => setForm({...form, message: e.target.value})} rows={6}
                className="w-full rounded-lg border px-3 py-2 text-sm" placeholder="Mesajinizi yazin..." />
              {errors.message && <p className="text-xs text-red-500 mt-1">{errors.message}</p>}
              <p className="text-xs text-gray-400 mt-1">{form.message.length}/5000</p>
            </div>
            <button onClick={() => mutation.mutate(form)}
              disabled={mutation.isPending || !form.name || !form.email || !form.subject || !form.message}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              Gonder
            </button>
            {mutation.isError && !errors.name && <p className="text-sm text-red-500">Bir hata olustu. Tekrar deneyin.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
