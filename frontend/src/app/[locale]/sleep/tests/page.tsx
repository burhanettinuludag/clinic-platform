'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ClipboardList, Moon, Sun, AlertCircle, Wind,
  Clock, ArrowRight, ChevronLeft, ShieldCheck,
} from 'lucide-react';
import { useSleepScreeningTests } from '@/hooks/useSleepData';

const ICON_MAP: Record<string, React.ElementType> = {
  'clipboard-list': ClipboardList,
  'moon': Moon,
  'sun': Sun,
  'alert-circle': AlertCircle,
  'wind': Wind,
};

const GRADIENT_MAP: Record<string, string> = {
  'moon': 'from-indigo-500 to-purple-600',
  'sun': 'from-amber-400 to-orange-500',
  'alert-circle': 'from-rose-400 to-pink-600',
  'wind': 'from-cyan-400 to-blue-600',
};

export default function SleepTestsPage() {
  const t = useTranslations('sleep');
  const params = useParams();
  const locale = (params?.locale as string) || 'tr';

  const { data: tests = [], isLoading } = useSleepScreeningTests();

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 rounded-full bg-yellow-300 blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-blue-400 blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 py-16 sm:py-20">
          <Link
            href={`/${locale}/sleep`}
            className="inline-flex items-center gap-2 text-indigo-300 hover:text-white transition-colors mb-6"
          >
            <ChevronLeft className="w-4 h-4" />
            {t('tests.backToSleep')}
          </Link>
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
              <ClipboardList className="w-4 h-4 text-yellow-300" />
              <span className="text-sm font-medium">{t('tests.badge')}</span>
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold mb-4 tracking-tight">
              {t('tests.hero.title')}
            </h1>
            <p className="text-lg sm:text-xl text-indigo-200 max-w-2xl mx-auto mb-6">
              {t('tests.hero.subtitle')}
            </p>
            <div className="flex items-center justify-center gap-4 text-sm text-indigo-200">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                {t('tests.hero.anonymous')}
              </span>
              <span className="w-1 h-1 rounded-full bg-indigo-400" />
              <span className="flex items-center gap-1.5">
                <ClipboardList className="w-4 h-4" />
                {tests.length} {t('tests.hero.tests')}
              </span>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Test Cards */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-2xl border border-gray-100 p-6 animate-pulse">
                <div className="w-14 h-14 bg-gray-200 rounded-xl mb-4" />
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-2" />
                <div className="h-4 bg-gray-100 rounded w-full mb-1" />
                <div className="h-4 bg-gray-100 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tests.map(test => {
              const Icon = ICON_MAP[test.icon] || ClipboardList;
              const gradient = GRADIENT_MAP[test.icon] || 'from-indigo-500 to-purple-600';
              return (
                <Link
                  key={test.id}
                  href={`/${locale}/sleep/tests/${test.slug}`}
                  className="group bg-white rounded-2xl border border-gray-100 hover:border-indigo-200 hover:shadow-xl transition-all duration-300 p-6 flex flex-col"
                >
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 group-hover:text-indigo-700 transition-colors mb-2">
                    {test.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4 flex-1 line-clamp-3">
                    {test.description}
                  </p>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-3 text-gray-400">
                      <span className="flex items-center gap-1">
                        <ClipboardList className="w-4 h-4" />
                        {test.question_count} {t('tests.questions')}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        ~{test.duration_minutes} {t('tests.minutes')}
                      </span>
                    </div>
                    <ArrowRight className="w-5 h-5 text-indigo-500 group-hover:translate-x-1 transition-transform" />
                  </div>
                </Link>
              );
            })}
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-12 bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
          <p className="text-sm text-amber-800">
            <strong>{t('tests.disclaimer.title')}</strong>{' '}
            {t('tests.disclaimer.text')}
          </p>
        </div>
      </div>
    </div>
  );
}
