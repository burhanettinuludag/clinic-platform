'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  Moon, Brain, Stethoscope, Sparkles, HeartPulse, AlertCircle,
  Clock, Eye, ChevronRight, ChevronDown, ChevronUp, Search,
  BookOpen, Lightbulb, Star, ClipboardList, ArrowRight,
} from 'lucide-react';
import {
  useSleepCategories,
  useSleepArticles,
  useFeaturedSleepArticles,
  useSleepTips,
  useSleepFAQs,
  useSleepScreeningTests,
} from '@/hooks/useSleepData';
import type { SleepArticle, SleepFAQ } from '@/lib/types/sleep';

const ICON_MAP: Record<string, React.ElementType> = {
  'alert-circle': AlertCircle,
  'sparkles': Sparkles,
  'stethoscope': Stethoscope,
  'heart-pulse': HeartPulse,
  'moon': Moon,
};

const ARTICLE_TYPE_LABELS: Record<string, { tr: string; en: string }> = {
  general: { tr: 'Genel Bilgi', en: 'General' },
  disorder: { tr: 'Uyku Bozuklugu', en: 'Sleep Disorder' },
  hygiene: { tr: 'Uyku Hijyeni', en: 'Sleep Hygiene' },
  diagnosis: { tr: 'Tani Yontemi', en: 'Diagnosis' },
  disease_sleep: { tr: 'Hastalikta Uyku', en: 'Sleep in Disease' },
  tip: { tr: 'Oneri', en: 'Tip' },
};

const DISEASE_LABELS: Record<string, { tr: string; en: string; color: string }> = {
  migraine: { tr: 'Migren', en: 'Migraine', color: 'bg-rose-100 text-rose-700' },
  alzheimer: { tr: 'Alzheimer', en: 'Alzheimer', color: 'bg-purple-100 text-purple-700' },
  parkinson: { tr: 'Parkinson', en: 'Parkinson', color: 'bg-blue-100 text-blue-700' },
  diabetes: { tr: 'Diyabet', en: 'Diabetes', color: 'bg-amber-100 text-amber-700' },
  adhd: { tr: 'ADHD', en: 'ADHD', color: 'bg-orange-100 text-orange-700' },
  epilepsy: { tr: 'Epilepsi', en: 'Epilepsy', color: 'bg-indigo-100 text-indigo-700' },
};

function FAQItem({ faq }: { faq: SleepFAQ }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="font-medium text-gray-900 pr-4">{faq.question}</span>
        {open ? <ChevronUp className="w-5 h-5 text-gray-400 shrink-0" /> : <ChevronDown className="w-5 h-5 text-gray-400 shrink-0" />}
      </button>
      {open && (
        <div className="px-4 pb-4 text-gray-600 text-sm leading-relaxed border-t border-gray-100 pt-3">
          {faq.answer}
        </div>
      )}
    </div>
  );
}

function ArticleCard({ article, locale }: { article: SleepArticle; locale: string }) {
  const typeLabel = ARTICLE_TYPE_LABELS[article.article_type]?.[locale as 'tr' | 'en'] || article.article_type;
  const diseaseInfo = article.related_disease ? DISEASE_LABELS[article.related_disease] : null;

  return (
    <Link
      href={`/${locale}/sleep/${article.slug}`}
      className="group bg-white rounded-2xl border border-gray-100 hover:border-teal-200 hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col"
    >
      {/* Header */}
      <div className="p-5 flex-1">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-teal-50 text-teal-700">
            {typeLabel}
          </span>
          {diseaseInfo && (
            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${diseaseInfo.color}`}>
              {diseaseInfo[locale as 'tr' | 'en']}
            </span>
          )}
        </div>

        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-teal-700 transition-colors mb-2 line-clamp-2">
          {article.title}
        </h3>

        {article.subtitle && (
          <p className="text-sm text-gray-500 mb-3 line-clamp-2">{article.subtitle}</p>
        )}

        {article.summary && (
          <p className="text-sm text-gray-600 line-clamp-3">{article.summary}</p>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 pb-4 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {article.reading_time_minutes} dk
          </span>
          <span className="flex items-center gap-1">
            <Eye className="w-3.5 h-3.5" />
            {article.view_count}
          </span>
        </div>
        <ChevronRight className="w-4 h-4 text-teal-500 group-hover:translate-x-1 transition-transform" />
      </div>
    </Link>
  );
}

export default function SleepPage() {
  const t = useTranslations('sleep');
  const params = useParams();
  const locale = (params?.locale as string) || 'tr';

  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: categories = [] } = useSleepCategories();
  const { data: featuredArticles = [] } = useFeaturedSleepArticles();
  const { data: allArticles = [], isLoading: articlesLoading } = useSleepArticles(
    activeCategory ? { category__slug: activeCategory } : undefined
  );
  const { data: tips = [] } = useSleepTips();
  const { data: screeningTests = [] } = useSleepScreeningTests();
  const { data: faqs = [] } = useSleepFAQs();

  const filteredArticles = searchQuery
    ? allArticles.filter(a =>
        a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.summary?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allArticles;

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-50/50 via-white to-white">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 rounded-full bg-yellow-300 blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-blue-400 blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
              <Moon className="w-4 h-4 text-yellow-300" />
              <span className="text-sm font-medium">{t('badge')}</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 tracking-tight">
              {t('hero.title')}
            </h1>
            <p className="text-lg sm:text-xl text-indigo-200 max-w-2xl mx-auto mb-8">
              {t('hero.subtitle')}
            </p>
            <div className="flex items-center justify-center gap-4 text-sm text-indigo-200">
              <span className="flex items-center gap-1.5">
                <BookOpen className="w-4 h-4" />
                {allArticles.length} {t('hero.articles')}
              </span>
              <span className="w-1 h-1 rounded-full bg-indigo-400" />
              <span className="flex items-center gap-1.5">
                <Star className="w-4 h-4" />
                {t('hero.free')}
              </span>
              <span className="w-1 h-1 rounded-full bg-indigo-400" />
              <span className="flex items-center gap-1.5">
                <Brain className="w-4 h-4" />
                {t('hero.evidence')}
              </span>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Featured Articles */}
        {featuredArticles.length > 0 && (
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                <Star className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{t('featured.title')}</h2>
                <p className="text-sm text-gray-500">{t('featured.subtitle')}</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {featuredArticles.map(article => (
                <ArticleCard key={article.id} article={article} locale={locale} />
              ))}
            </div>
          </section>
        )}

        {/* Screening Tests CTA */}
        {screeningTests.length > 0 && (
          <section className="mb-16">
            <div className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 rounded-3xl p-8 md:p-10 text-white relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 rounded-full bg-white/5 -translate-y-1/2 translate-x-1/2" />
              <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full bg-white/5 translate-y-1/2 -translate-x-1/2" />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center">
                    <ClipboardList className="w-6 h-6 text-yellow-300" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">{t('tests.badge')}</h2>
                    <p className="text-sm text-indigo-200">{screeningTests.length} {locale === 'tr' ? 'ücretsiz test' : 'free tests'}</p>
                  </div>
                </div>
                <p className="text-indigo-100 mb-6 max-w-xl">
                  {locale === 'tr'
                    ? 'Uyku kalitenizi, gündüz uykululuğunuzu, uykusuzluk ve uyku apnesi riskinizi değerlendirin. Tamamen anonim, kayıt gerektirmez.'
                    : 'Evaluate your sleep quality, daytime sleepiness, insomnia and sleep apnea risk. Completely anonymous, no registration required.'}
                </p>
                <div className="flex flex-wrap gap-3">
                  {screeningTests.slice(0, 4).map(test => (
                    <Link
                      key={test.id}
                      href={`/${locale}/sleep/tests/${test.slug}`}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-xl text-sm font-medium transition-colors"
                    >
                      {test.title}
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  ))}
                </div>
                <Link
                  href={`/${locale}/sleep/tests`}
                  className="mt-4 inline-flex items-center gap-2 text-sm text-yellow-300 hover:text-yellow-200 transition-colors font-medium"
                >
                  {locale === 'tr' ? 'Tüm testleri gör' : 'See all tests'}
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* Categories */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('categories.title')}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {categories.map(cat => {
              const Icon = ICON_MAP[cat.icon] || Moon;
              const isActive = activeCategory === cat.slug;
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(isActive ? null : cat.slug)}
                  className={`p-4 rounded-xl border transition-all text-left ${
                    isActive
                      ? 'border-teal-500 bg-teal-50 shadow-sm'
                      : 'border-gray-200 bg-white hover:border-teal-200 hover:shadow-sm'
                  }`}
                >
                  <Icon className={`w-6 h-6 mb-2 ${isActive ? 'text-teal-600' : 'text-gray-400'}`} />
                  <h3 className={`font-semibold text-sm ${isActive ? 'text-teal-800' : 'text-gray-900'}`}>
                    {cat.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">{cat.article_count} {t('categories.articleCount')}</p>
                </button>
              );
            })}
          </div>
        </section>

        {/* Search */}
        <section className="mb-8">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder={t('search.placeholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            />
          </div>
        </section>

        {/* All Articles */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {activeCategory
              ? categories.find(c => c.slug === activeCategory)?.name || t('articles.title')
              : t('articles.title')
            }
          </h2>
          {articlesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-20 mb-3" />
                  <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
                  <div className="h-4 bg-gray-100 rounded w-full mb-1" />
                  <div className="h-4 bg-gray-100 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : filteredArticles.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredArticles.map(article => (
                <ArticleCard key={article.id} article={article} locale={locale} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <Moon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>{t('articles.empty')}</p>
            </div>
          )}
        </section>

        {/* Tips Section */}
        {tips.length > 0 && (
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{t('tips.title')}</h2>
                <p className="text-sm text-gray-500">{t('tips.subtitle')}</p>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {tips.map(tip => (
                <div key={tip.id} className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-5 border border-indigo-100">
                  <Moon className="w-6 h-6 text-indigo-500 mb-3" />
                  <h3 className="font-semibold text-gray-900 text-sm mb-2">{tip.title}</h3>
                  <p className="text-xs text-gray-600 leading-relaxed">{tip.content}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* FAQ Section */}
        {faqs.length > 0 && (
          <section className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('faq.title')}</h2>
            <div className="max-w-2xl space-y-3">
              {faqs.map(faq => (
                <FAQItem key={faq.id} faq={faq} />
              ))}
            </div>
          </section>
        )}

        {/* Disclaimer */}
        <section className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-center">
          <p className="text-sm text-amber-800">
            <strong>{t('disclaimer.title')}</strong>{' '}
            {t('disclaimer.text')}
          </p>
        </section>
      </div>
    </div>
  );
}
