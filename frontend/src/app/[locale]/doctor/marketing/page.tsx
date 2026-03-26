'use client';

import { Megaphone, ArrowLeft } from 'lucide-react';
import { Link } from '@/i18n/navigation';

export default function MarketingPage() {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl border-2 border-orange-100 p-10 text-center">
        <div className="w-16 h-16 bg-orange-100 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <Megaphone className="w-8 h-8 text-orange-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Marketing Kampanyaları
        </h1>
        <p className="text-gray-500 mb-1">
          AI destekli sosyal medya içerik üretimi ve yönetimi
        </p>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-50 border border-orange-200 rounded-full text-orange-700 text-sm font-medium mt-4 mb-6">
          <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
          Yakında Yayında
        </div>
        <p className="text-sm text-gray-400 max-w-md mx-auto mb-6">
          Bu özellik üzerinde çalışıyoruz. Çok yakında AI destekli kampanya oluşturma,
          sosyal medya planlaması ve otomatik içerik üretimi hizmetinizde olacak.
        </p>
        <Link
          href="/doctor/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Dashboard'a Dön
        </Link>
      </div>
    </div>
  );
}
