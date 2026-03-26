'use client';

import { Megaphone, ArrowLeft } from 'lucide-react';
import { Link } from '@/i18n/navigation';

export default function MarketingCampaignDetailPage() {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <Link
        href="/doctor/marketing"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-orange-600 mb-4 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Geri Dön
      </Link>
      <div className="bg-white rounded-2xl border-2 border-orange-100 p-10 text-center">
        <div className="w-16 h-16 bg-orange-100 rounded-2xl flex items-center justify-center mx-auto mb-5">
          <Megaphone className="w-8 h-8 text-orange-600" />
        </div>
        <h1 className="text-xl font-bold text-gray-900 mb-2">
          Kampanya Detayı
        </h1>
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-50 border border-orange-200 rounded-full text-orange-700 text-sm font-medium mt-2">
          <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
          Yakında Yayında
        </div>
      </div>
    </div>
  );
}
