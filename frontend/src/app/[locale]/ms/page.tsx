'use client';

import { useState } from 'react';
import { useLocale } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  Dna, Brain, Stethoscope, Sparkles, HeartPulse, AlertCircle,
  Clock, Eye, ChevronRight, ChevronDown, ChevronUp, Search,
  BookOpen, Lightbulb, Star, ArrowRight,
} from 'lucide-react';
import {
  useMSCategories,
  useMSArticles,
  useFeaturedMSArticles,
  useMSTips,
  useMSFAQs,
} from '@/hooks/useMSData';
import type { MSArticle, MSFAQ } from '@/lib/types/ms';

const ICON_MAP: Record<string, React.ElementType> = {
  'alert-circle': AlertCircle,
  'sparkles': Sparkles,
  'stethoscope': Stethoscope,
  'heart-pulse': HeartPulse,
  'dna': Dna,
};

const ARTICLE_TYPE_LABELS: Record<string, { tr: string; en: string }> = {
  general: { tr: 'Genel Bilgi', en: 'General' },
  symptoms: { tr: 'Belirtiler', en: 'Symptoms' },
  treatment: { tr: 'Tedavi', en: 'Treatment' },
  diagnosis: { tr: 'Tani Yontemi', en: 'Diagnosis' },
  living_with: { tr: 'MS ile Yasamak', en: 'Living with MS' },
  tip: { tr: 'Oneri', en: 'Tip' },
};

function FAQItem({ faq }: { faq: MSFAQ }) {
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

function ArticleCard({ article, locale }: { article: MSArticle; locale: string }) {
  const typeLabel = ARTICLE_TYPE_LABELS[article.article_type]?.[locale as 'tr' | 'en'] || article.article_type;

  const imageUrl = article.cover_image_url || article.cover_image || '';

  return (
    <Link
      href={`/ms/${article.slug}`}
      className="group bg-white rounded-2xl border border-gray-100 hover:border-cyan-200 hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col"
    >
      {/* Cover Image */}
      {imageUrl && (
        <div className="relative w-full h-44 overflow-hidden bg-gray-100">
          <img
            src={imageUrl}
            alt={article.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
        </div>
      )}
      {/* Header */}
      <div className="p-5 flex-1">
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-cyan-50 text-cyan-700">
            {typeLabel}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-cyan-700 transition-colors mb-2 line-clamp-2">
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
        <ChevronRight className="w-4 h-4 text-cyan-500 group-hover:translate-x-1 transition-transform" />
      </div>
    </Link>
  );
}

export default function MSPage() {
  const locale = useLocale();

  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: categories = [] } = useMSCategories();
  const { data: featuredArticles = [] } = useFeaturedMSArticles();
  const { data: allArticles = [], isLoading: articlesLoading } = useMSArticles(
    activeCategory ? { category__slug: activeCategory } : undefined
  );
  const { data: tips = [] } = useMSTips();
  const { data: faqs = [] } = useMSFAQs();

  const filteredArticles = searchQuery
    ? allArticles.filter(a =>
        a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        a.summary?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allArticles;

  return (
    <div className="min-h-screen bg-gradient-to-b from-cyan-50/50 via-white to-white">
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-cyan-900 via-cyan-800 to-teal-900 text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-64 h-64 rounded-full bg-cyan-300 blur-3xl" />
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-teal-400 blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 mb-6">
              <Dna className="w-4 h-4 text-cyan-300" />
              <span className="text-sm font-medium">
                {locale === 'tr' ? 'Norosera MS Rehberi' : 'Norosera MS Guide'}
              </span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 tracking-tight">
              {locale === 'tr' ? 'Multipl Skleroz (MS) Rehberi' : 'Multiple Sclerosis (MS) Guide'}
            </h1>
            <p className="text-lg sm:text-xl text-cyan-200 max-w-2xl mx-auto mb-8">
              {locale === 'tr'
                ? 'MS hakkinda bilmeniz gereken her sey: belirtiler, tedavi secenekleri ve yasam kalitesini artirma yollari.'
                : 'Everything you need to know about MS: symptoms, treatment options, and ways to improve quality of life.'}
            </p>
            <div className="flex items-center justify-center gap-4 text-sm text-cyan-200">
              <span className="flex items-center gap-1.5">
                <BookOpen className="w-4 h-4" />
                {locale === 'tr' ? '7 Kategori' : '7 Categories'}
              </span>
              <span className="w-1 h-1 rounded-full bg-cyan-400" />
              <span className="flex items-center gap-1.5">
                <Star className="w-4 h-4" />
                {locale === 'tr' ? '18+ Makale' : '18+ Articles'}
              </span>
              <span className="w-1 h-1 rounded-full bg-cyan-400" />
              <span className="flex items-center gap-1.5">
                <Brain className="w-4 h-4" />
                {locale === 'tr' ? 'Ucretsiz' : 'Free'}
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
                <h2 className="text-2xl font-bold text-gray-900">
                  {locale === 'tr' ? 'One Cikan Yazilar' : 'Featured Articles'}
                </h2>
                <p className="text-sm text-gray-500">
                  {locale === 'tr' ? 'Editör secimi en populer icerikler' : 'Editor picks and most popular content'}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {featuredArticles.map(article => (
                <ArticleCard key={article.id} article={article} locale={locale} />
              ))}
            </div>
          </section>
        )}

        {/* Categories */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {locale === 'tr' ? 'Kategoriler' : 'Categories'}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {categories.map(cat => {
              const Icon = ICON_MAP[cat.icon] || Dna;
              const isActive = activeCategory === cat.slug;
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveCategory(isActive ? null : cat.slug)}
                  className={`p-4 rounded-xl border transition-all text-left ${
                    isActive
                      ? 'border-cyan-500 bg-cyan-50 shadow-sm'
                      : 'border-gray-200 bg-white hover:border-cyan-200 hover:shadow-sm'
                  }`}
                >
                  <Icon className={`w-6 h-6 mb-2 ${isActive ? 'text-cyan-600' : 'text-gray-400'}`} />
                  <h3 className={`font-semibold text-sm ${isActive ? 'text-cyan-800' : 'text-gray-900'}`}>
                    {cat.name}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {cat.article_count} {locale === 'tr' ? 'makale' : 'articles'}
                  </p>
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
              placeholder={locale === 'tr' ? 'Makale ara...' : 'Search articles...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
            />
          </div>
        </section>

        {/* All Articles */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {activeCategory
              ? categories.find(c => c.slug === activeCategory)?.name || (locale === 'tr' ? 'Tum Makaleler' : 'All Articles')
              : (locale === 'tr' ? 'Tum Makaleler' : 'All Articles')
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
              <Dna className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>{locale === 'tr' ? 'Henuz makale bulunamadi.' : 'No articles found yet.'}</p>
            </div>
          )}
        </section>

        {/* Tips Section */}
        {tips.length > 0 && (
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-cyan-100 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-cyan-600" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {locale === 'tr' ? 'Faydali Ipuclari' : 'Useful Tips'}
                </h2>
                <p className="text-sm text-gray-500">
                  {locale === 'tr' ? 'Gunluk yasaminizi kolaylastiracak oneriler' : 'Suggestions to make your daily life easier'}
                </p>
              </div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {tips.map(tip => (
                <div key={tip.id} className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl p-5 border border-cyan-100">
                  <Dna className="w-6 h-6 text-cyan-500 mb-3" />
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
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {locale === 'tr' ? 'Sikca Sorulan Sorular' : 'Frequently Asked Questions'}
            </h2>
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
            <strong>{locale === 'tr' ? 'Uyari:' : 'Disclaimer:'}</strong>{' '}
            {locale === 'tr'
              ? 'Bu sayfadaki icerikler yalnizca bilgilendirme amaclidir ve tibbi tani veya tedavi yerine gecmez. Saglik sorunlariniz icin mutlaka bir noroloji uzmani ile gorusun.'
              : 'The content on this page is for informational purposes only and does not replace medical diagnosis or treatment. Always consult a neurologist for your health concerns.'}
          </p>
        </section>
      </div>
    </div>
  );
}
