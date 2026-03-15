import { Metadata } from 'next';
import { Brain, Newspaper, Shield, Clock, Activity } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Yakinda | Norosera',
  description: 'Norosera platformu yayina hazirlaniyor. Noroloji haberlerini takip edin.',
};

export default function YakindaPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-indigo-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center py-20">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center shadow-lg shadow-teal-200">
            <Brain className="w-10 h-10 text-white" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4 tracking-tight">
          Norosera
        </h1>
        <p className="text-lg text-teal-600 font-medium mb-8">
          Norolojik Saglik Platformu
        </p>

        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-50 border border-amber-200 text-amber-700 mb-10">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-medium">Yayina hazirlaniyor</span>
        </div>

        {/* Description */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-100 p-8 mb-10 shadow-sm">
          <p className="text-gray-600 leading-relaxed mb-6">
            Norosera, migren, epilepsi ve demans gibi norolojik hastaliklarda
            hasta takibi, egitim ve hekim paneli sunan kapsamli bir saglik platformudur.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-teal-50/50">
              <Activity className="w-5 h-5 text-teal-600" />
              <span className="text-gray-700 font-medium">Hasta Takibi</span>
            </div>
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-indigo-50/50">
              <Shield className="w-5 h-5 text-indigo-600" />
              <span className="text-gray-700 font-medium">KVKK Uyumlu</span>
            </div>
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-rose-50/50">
              <Newspaper className="w-5 h-5 text-rose-600" />
              <span className="text-gray-700 font-medium">Noroloji Haberleri</span>
            </div>
          </div>
        </div>

        {/* CTA - News page */}
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            Su anda noroloji haberlerimize goz atabilirsiniz
          </p>
          <Link
            href="/news"
            className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 text-white font-semibold rounded-xl hover:bg-teal-700 transition-colors shadow-sm shadow-teal-200"
          >
            <Newspaper className="w-5 h-5" />
            Noroloji Haberleri
          </Link>
        </div>

        {/* Spacer */}
        <div className="mt-16" />
      </div>
    </div>
  );
}
