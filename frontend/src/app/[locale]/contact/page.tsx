'use client';

import { useState } from 'react';
import { Mail, Phone, MapPin, Send, CheckCircle, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true); setError('');
    try {
      await api.post('/common/contact/', form);
      setSent(true);
    } catch { setError('Gonderim basarisiz. Lutfen tekrar deneyin.'); }
    finally { setSending(false); }
  };

  if (sent) return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Mesajiniz Alindi</h1>
        <p className="text-gray-500 dark:text-gray-400">En kisa surede donus yapacagiz.</p>
      </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Iletisim</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Sorulariniz icin bize ulasin</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Info */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <Mail className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Email</h3>
            <p className="text-sm text-gray-500">info@norosera.com</p>
          </div>
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <Phone className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Telefon</h3>
            <p className="text-sm text-gray-500">+90 533 723 15 13</p>
          </div>
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <MapPin className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">Adres</h3>
            <p className="text-sm text-gray-500">Ankara Caddesi No 243/2, Bornova, Izmir</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Adiniz</label>
              <input required value={form.name} onChange={e => setForm({...form, name: e.target.value})}
                className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white" />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Email</label>
              <input required type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})}
                className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white" />
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Konu</label>
            <input required value={form.subject} onChange={e => setForm({...form, subject: e.target.value})}
              className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Mesajiniz</label>
            <textarea required rows={5} value={form.message} onChange={e => setForm({...form, message: e.target.value})}
              className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white" />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button type="submit" disabled={sending}
            className="flex items-center justify-center gap-2 w-full rounded-lg bg-cyan-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50">
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Gonder
          </button>
        </form>
      </div>
    </div>
  );
}
