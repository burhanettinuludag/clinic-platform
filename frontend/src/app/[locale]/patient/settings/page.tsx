'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useConsents, useGrantConsent } from '@/hooks/useDoctorData';
import { Bell, Shield, Mail, Cookie, Lock, User, Settings, ChevronRight } from 'lucide-react';

export default function PatientSettingsPage() {
  const t = useTranslations();
  const { data: consents, isLoading } = useConsents();
  const grantConsent = useGrantConsent();

  const [localConsents, setLocalConsents] = useState<Record<string, boolean>>({
    health_data: false, doctor_sharing: false, marketing: false, cookies: false,
  });

  useEffect(() => {
    if (consents && Array.isArray(consents)) {
      const map: Record<string, boolean> = {};
      consents.forEach((c: { consent_type: string; granted: boolean }) => { map[c.consent_type] = c.granted; });
      setLocalConsents(prev => ({ ...prev, ...map }));
    }
  }, [consents]);

  const handleToggle = (key: string) => {
    const next = !localConsents[key];
    setLocalConsents(prev => ({ ...prev, [key]: next }));
    grantConsent.mutate({ consent_type: key, granted: next, version: '1.0' });
  };

  const quickLinks = [
    { href: '/patient/profile', icon: User, label: 'Profil Duzenle', desc: 'Kisisel ve saglik bilgileri', color: 'text-blue-600 bg-blue-50' },
    { href: '/patient/change-password', icon: Lock, label: 'Sifre Degistir', desc: 'Hesap guvenlik ayarlari', color: 'text-red-500 bg-red-50' },
    { href: '/patient/notification-settings', icon: Bell, label: 'Bildirim Tercihleri', desc: 'Email, push ve sessiz saatler', color: 'text-purple-600 bg-purple-50' },
  ];

  const consentItems = [
    { key: 'health_data', label: 'Saglik Verisi Isleme', desc: 'Saglik verilerinizin takip amacli islenmesine izin verin.', icon: Shield, color: 'text-blue-600' },
    { key: 'doctor_sharing', label: 'Hekim ile Paylasim', desc: 'Verilerinizin hekiminizle paylasilmasina izin verin.', icon: User, color: 'text-green-600' },
    { key: 'marketing', label: 'Pazarlama Iletisimi', desc: 'Promosyon ve bilgilendirme e-postalari alin.', icon: Mail, color: 'text-purple-600' },
    { key: 'cookies', label: 'Cerez Kullanimi', desc: 'Analitik cerezlerin kullanimina izin verin.', icon: Cookie, color: 'text-amber-600' },
  ];

  if (isLoading) {
    return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" /></div>;
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="flex items-center gap-3 mb-6">
        <Settings className="h-6 w-6 text-blue-600" />
        <h1 className="text-xl font-bold text-gray-900">Ayarlar</h1>
      </div>

      {/* Quick Links */}
      <div className="space-y-2 mb-8">
        {quickLinks.map(item => (
          <Link key={item.href} href={item.href}
            className="flex items-center justify-between rounded-xl border bg-white p-4 hover:shadow-sm transition-shadow">
            <div className="flex items-center gap-3">
              <div className={'rounded-full p-2 ' + item.color}>
                <item.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{item.label}</p>
                <p className="text-xs text-gray-500">{item.desc}</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-gray-300" />
          </Link>
        ))}
      </div>

      {/* KVKK */}
      <div className="rounded-xl border bg-white p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-1">Onay ve KVKK Tercihleri</h2>
        <p className="text-xs text-gray-400 mb-4">Kisisel verilerinizin islenmesine iliskin tercihlerinizi yonetin.</p>
        <div className="divide-y">
          {consentItems.map(item => (
            <div key={item.key} className="flex items-center justify-between py-3">
              <div className="flex items-start gap-3">
                <item.icon className={'h-5 w-5 mt-0.5 ' + item.color} />
                <div>
                  <p className="text-sm font-medium text-gray-900">{item.label}</p>
                  <p className="text-xs text-gray-500">{item.desc}</p>
                </div>
              </div>
              <button type="button" onClick={() => handleToggle(item.key)}
                className={'relative w-11 h-6 rounded-full transition-colors ' + (localConsents[item.key] ? 'bg-blue-600' : 'bg-gray-200')}>
                <span className={'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ' + (localConsents[item.key] ? 'translate-x-5' : '')} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
