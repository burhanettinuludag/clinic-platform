'use client';

import { useState } from 'react';
import { useLocale } from 'next-intl';
import { Mail, Phone, MapPin, Send, CheckCircle, Loader2, Code2, Handshake } from 'lucide-react';
import api from '@/lib/api';

export default function ContactPage() {
  const locale = useLocale();
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [honeypot, setHoneypot] = useState('');
  const [loadTime] = useState(Date.now());
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const t = locale === 'tr' ? {
    title: 'İletişim',
    subtitle: 'Sorularınız için bize ulaşın',
    email: 'E-posta',
    phone: 'Telefon',
    address: 'Adres',
    addressText: 'Ankara Caddesi No 243/2, Bornova, İzmir',
    name: 'Adınız',
    emailLabel: 'E-posta',
    subject: 'Konu',
    message: 'Mesajınız',
    send: 'Gönder',
    sendError: 'Gönderim başarısız. Lütfen tekrar deneyin.',
    sentTitle: 'Mesajınız Alındı',
    sentDesc: 'En kısa sürede dönüş yapacağız.',
    creatorTitle: 'Bu Projeyi Kim Geliştirdi?',
    creatorDesc: 'Norosera, nörolojik hastalıklar alanında hastaların yaşam kalitesini artırmak amacıyla Burhanettin Uludağ tarafından tasarlanmış ve geliştirilmiş bir dijital sağlık platformudur.',
    collab: 'İşbirliği & Geliştirme',
    collabDesc: 'Teknik işbirlikleri, entegrasyon talepleri veya proje hakkında detaylı bilgi almak için aşağıdaki adresten bize ulaşabilirsiniz.',
    collabEmail: 'İşbirliği E-postası',
  } : {
    title: 'Contact',
    subtitle: 'Get in touch with us',
    email: 'Email',
    phone: 'Phone',
    address: 'Address',
    addressText: 'Ankara Caddesi No 243/2, Bornova, Izmir, Turkey',
    name: 'Your Name',
    emailLabel: 'Email',
    subject: 'Subject',
    message: 'Your Message',
    send: 'Send',
    sendError: 'Failed to send. Please try again.',
    sentTitle: 'Message Received',
    sentDesc: 'We will get back to you as soon as possible.',
    creatorTitle: 'Who Built This Project?',
    creatorDesc: 'Norosera is a digital health platform designed and developed by Burhanettin Uludag to improve the quality of life for patients with neurological conditions.',
    collab: 'Collaboration & Development',
    collabDesc: 'For technical collaborations, integration requests, or detailed information about the project, you can reach us at the address below.',
    collabEmail: 'Collaboration Email',
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Bot protection: honeypot field must be empty
    if (honeypot) return;

    // Bot protection: form must take at least 3 seconds to fill
    if (Date.now() - loadTime < 3000) {
      setError(locale === 'tr' ? 'Lütfen biraz bekleyip tekrar deneyin.' : 'Please wait a moment and try again.');
      return;
    }

    setSending(true);
    setError('');
    try {
      await api.post('/common/contact/', form);
      setSent(true);
    } catch {
      setError(t.sendError);
    } finally {
      setSending(false);
    }
  };

  if (sent) return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{t.sentTitle}</h1>
        <p className="text-gray-500 dark:text-gray-400">{t.sentDesc}</p>
      </div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{t.title}</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">{t.subtitle}</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Info Cards */}
        <div className="space-y-4">
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <Mail className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">{t.email}</h3>
            <a href="mailto:info@norosera.com" className="text-sm text-gray-500 hover:text-cyan-600 transition-colors">
              info@norosera.com
            </a>
          </div>
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <Phone className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">{t.phone}</h3>
            <a href="tel:+905337231513" className="text-sm text-gray-500 hover:text-cyan-600 transition-colors">
              +90 533 723 15 13
            </a>
          </div>
          <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5">
            <MapPin className="h-6 w-6 text-cyan-500 mb-3" />
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">{t.address}</h3>
            <p className="text-sm text-gray-500">{t.addressText}</p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="lg:col-span-2 rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-6 space-y-4">
          {/* Honeypot - hidden from real users, bots fill it */}
          <div className="absolute -left-[9999px] opacity-0 h-0 overflow-hidden" aria-hidden="true">
            <label htmlFor="website">Website</label>
            <input
              type="text"
              id="website"
              name="website"
              tabIndex={-1}
              autoComplete="off"
              value={honeypot}
              onChange={e => setHoneypot(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">{t.name}</label>
              <input
                required
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">{t.emailLabel}</label>
              <input
                required
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">{t.subject}</label>
            <input
              required
              value={form.subject}
              onChange={e => setForm({ ...form, subject: e.target.value })}
              className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">{t.message}</label>
            <textarea
              required
              rows={5}
              value={form.message}
              onChange={e => setForm({ ...form, message: e.target.value })}
              className="w-full rounded-lg border dark:border-slate-600 px-3 py-2.5 text-sm dark:bg-slate-700 dark:text-white"
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={sending}
            className="flex items-center justify-center gap-2 w-full rounded-lg bg-cyan-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-cyan-700 disabled:opacity-50"
          >
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            {t.send}
          </button>
        </form>
      </div>

      {/* Creator & Collaboration Section */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Creator Credit */}
        <div className="rounded-xl border bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-slate-800 dark:to-slate-800 dark:border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-teal-100 dark:bg-teal-900/30">
              <Code2 className="h-5 w-5 text-teal-600 dark:text-teal-400" />
            </div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">{t.creatorTitle}</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
            {t.creatorDesc}
          </p>
        </div>

        {/* Collaboration */}
        <div className="rounded-xl border bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-slate-800 dark:to-slate-800 dark:border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
              <Handshake className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">{t.collab}</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-4">
            {t.collabDesc}
          </p>
          <div className="flex items-center gap-2 bg-white dark:bg-slate-700 rounded-lg px-4 py-3 border dark:border-slate-600">
            <Mail className="h-4 w-4 text-indigo-500 shrink-0" />
            <div>
              <p className="text-xs text-gray-400 dark:text-gray-500">{t.collabEmail}</p>
              <a
                href="mailto:info@norsera.com"
                className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                info@norsera.com
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
