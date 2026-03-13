'use client';

import { useState, useMemo } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import type { NewsArticle } from '@/lib/types/content';
import {
  Newspaper,
  Clock,
  Eye,
  ArrowRight,
  Tag,
  Search,
  ChevronRight,
  AlertTriangle,
  Flame,
  Brain,
  Zap,
  Activity,
} from 'lucide-react';

// ==================== CONFIG ====================

const DISEASE_TABS = [
  { key: 'all', label_tr: 'Tüm Haberler', label_en: 'All News', icon: Newspaper },
  { key: 'migraine', label_tr: 'Migren', label_en: 'Migraine', icon: Brain },
  { key: 'epilepsy', label_tr: 'Epilepsi', label_en: 'Epilepsy', icon: Zap },
  { key: 'dementia', label_tr: 'Demans', label_en: 'Dementia', icon: Activity },
];

const CATEGORY_COLORS: Record<string, string> = {
  fda_approval: 'bg-blue-100 text-blue-700',
  ema_approval: 'bg-indigo-100 text-indigo-700',
  turkey_approval: 'bg-red-100 text-red-700',
  clinical_trial: 'bg-purple-100 text-purple-700',
  new_device: 'bg-cyan-100 text-cyan-700',
  congress: 'bg-amber-100 text-amber-700',
  turkey_news: 'bg-rose-100 text-rose-700',
  popular_science: 'bg-green-100 text-green-700',
  drug_update: 'bg-teal-100 text-teal-700',
  guideline_update: 'bg-orange-100 text-orange-700',
};

const PRIORITY_ICONS: Record<string, React.ReactNode> = {
  urgent: <AlertTriangle className="h-3 w-3 text-red-500" />,
  high: <Flame className="h-3 w-3 text-orange-500" />,
};

interface NewsMagazineProps {
  articles: NewsArticle[];
  diseaseFilter?: string;
  showDiseaseTabs?: boolean;
  showHeader?: boolean;
  maxItems?: number;
  compact?: boolean;
  title?: string;
}

export default function NewsMagazine({
  articles,
  diseaseFilter,
  showDiseaseTabs = true,
  showHeader = true,
  maxItems,
  compact = false,
  title,
}: NewsMagazineProps) {
  const locale = useLocale();
  const [activeDisease, setActiveDisease] = useState(diseaseFilter || 'all');
  const [searchQuery, setSearchQuery] = useState('');

  const t = (tr: string, en: string) => (locale === 'tr' ? tr : en);
  const getTitle = (a: NewsArticle) => (locale === 'tr' ? a.title_tr : a.title_en) || a.title_tr;
  const getExcerpt = (a: NewsArticle) => (locale === 'tr' ? a.excerpt_tr : a.excerpt_en) || a.excerpt_tr;

  // Filtrele
  const filtered = useMemo(() => {
    let result = articles;

    if (activeDisease && activeDisease !== 'all') {
      result = result.filter((a) => a.related_diseases?.includes(activeDisease));
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (a) =>
          getTitle(a).toLowerCase().includes(q) ||
          getExcerpt(a).toLowerCase().includes(q)
      );
    }

    if (maxItems) {
      result = result.slice(0, maxItems);
    }

    return result;
  }, [articles, activeDisease, searchQuery, maxItems]);

  const featured = filtered[0];
  const rest = filtered.slice(1);

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      {showHeader && (
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Newspaper className="h-7 w-7 text-teal-600" />
              {title || t('Noroloji Haberleri', 'Neurology News')}
            </h2>
            <p className="text-gray-500 text-sm mt-1">
              {t(
                'Nörolojik hastalıklar alanındaki en güncel gelişmeler',
                'Latest developments in neurological diseases'
              )}
            </p>
          </div>
          {!compact && (
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder={t('Haberlerde ara...', 'Search news...')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm w-64 focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          )}
        </div>
      )}

      {/* Disease Tabs */}
      {showDiseaseTabs && !diseaseFilter && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {DISEASE_TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeDisease === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveDisease(tab.key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-teal-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                {locale === 'tr' ? tab.label_tr : tab.label_en}
              </button>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {filtered.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl">
          <Newspaper className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">
            {t('Bu kategoride haber bulunamadı.', 'No news found in this category.')}
          </p>
        </div>
      )}

      {/* Featured Article - Hero */}
      {featured && !compact && (
        <Link href={`/news/${featured.slug}`} className="block group">
          <div className="relative bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl overflow-hidden">
            {featured.featured_image && (
              <div className="absolute inset-0">
                <img
                  src={featured.featured_image}
                  alt={featured.featured_image_alt || getTitle(featured)}
                  className="w-full h-full object-cover opacity-30 group-hover:opacity-40 transition-opacity"
                />
              </div>
            )}
            <div className="relative p-8 md:p-12">
              <div className="flex items-center gap-2 mb-4">
                {PRIORITY_ICONS[featured.priority] && (
                  <span className="px-2 py-0.5 bg-red-500/20 text-red-300 rounded text-xs font-medium flex items-center gap-1">
                    {PRIORITY_ICONS[featured.priority]}
                    {featured.priority_display || featured.priority}
                  </span>
                )}
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${CATEGORY_COLORS[featured.category] || 'bg-gray-100 text-gray-600'}`}>
                  {featured.category_display}
                </span>
                {featured.related_diseases?.map((d) => (
                  <span key={d} className="px-2 py-0.5 bg-white/10 text-white/80 rounded text-xs">
                    {d}
                  </span>
                ))}
              </div>
              <h3 className="text-2xl md:text-3xl font-bold text-white mb-3 group-hover:text-teal-300 transition-colors line-clamp-2">
                {getTitle(featured)}
              </h3>
              <p className="text-white/70 text-base md:text-lg max-w-3xl line-clamp-3 mb-4">
                {getExcerpt(featured)}
              </p>
              <div className="flex items-center gap-4 text-white/50 text-sm">
                {featured.author_name && <span>{featured.author_name}</span>}
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {formatDate(featured.published_at)}
                </span>
                <span className="flex items-center gap-1">
                  <Eye className="h-3 w-3" />
                  {featured.view_count}
                </span>
              </div>
            </div>
          </div>
        </Link>
      )}

      {/* News Grid */}
      {(compact ? filtered : rest).length > 0 && (
        <div className={`grid gap-4 ${compact ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}>
          {(compact ? filtered : rest).map((article) => (
            <NewsCard
              key={article.id}
              article={article}
              locale={locale}
              compact={compact}
              getTitle={getTitle}
              getExcerpt={getExcerpt}
              formatDate={formatDate}
            />
          ))}
        </div>
      )}

      {/* View All Link */}
      {maxItems && filtered.length >= maxItems && (
        <div className="text-center">
          <Link
            href="/news"
            className="inline-flex items-center gap-2 text-teal-600 hover:text-teal-700 font-medium text-sm"
          >
            {t('Tüm Haberleri Gör', 'View All News')}
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      )}
    </div>
  );
}

// ==================== NEWS CARD ====================

function NewsCard({
  article,
  locale,
  compact,
  getTitle,
  getExcerpt,
  formatDate,
}: {
  article: NewsArticle;
  locale: string;
  compact: boolean;
  getTitle: (a: NewsArticle) => string;
  getExcerpt: (a: NewsArticle) => string;
  formatDate: (d: string) => string;
}) {
  return (
    <Link href={`/news/${article.slug}`} className="group block">
      <div className={`bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-lg transition-all hover:border-teal-200 ${compact ? 'flex gap-4 p-3' : ''}`}>
        {/* Image */}
        {!compact && (
          <div className="aspect-[16/9] overflow-hidden bg-gray-100">
            {article.featured_image ? (
              <img
                src={article.featured_image}
                alt={article.featured_image_alt || getTitle(article)}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-teal-50 to-blue-50">
                <Newspaper className="h-12 w-12 text-teal-300" />
              </div>
            )}
          </div>
        )}
        {compact && (
          <div className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
            {article.featured_image ? (
              <img
                src={article.featured_image}
                alt={article.featured_image_alt || getTitle(article)}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-teal-50 to-blue-50">
                <Newspaper className="h-6 w-6 text-teal-300" />
              </div>
            )}
          </div>
        )}

        {/* Content */}
        <div className={compact ? 'flex-1 min-w-0' : 'p-4'}>
          {/* Tags */}
          <div className="flex items-center gap-1.5 mb-2 flex-wrap">
            {PRIORITY_ICONS[article.priority] && PRIORITY_ICONS[article.priority]}
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${CATEGORY_COLORS[article.category] || 'bg-gray-100 text-gray-600'}`}>
              {article.category_display}
            </span>
            {!compact && article.related_diseases?.map((d) => (
              <span key={d} className="px-1.5 py-0.5 bg-teal-50 text-teal-700 rounded text-[10px]">
                {d}
              </span>
            ))}
          </div>

          {/* Title */}
          <h3 className={`font-semibold text-gray-900 group-hover:text-teal-600 transition-colors ${compact ? 'text-sm line-clamp-2' : 'text-base line-clamp-2 mb-2'}`}>
            {getTitle(article)}
          </h3>

          {/* Excerpt */}
          {!compact && (
            <p className="text-sm text-gray-500 line-clamp-2 mb-3">
              {getExcerpt(article)}
            </p>
          )}

          {/* Meta */}
          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDate(article.published_at)}
            </span>
            {!compact && (
              <span className="flex items-center gap-1">
                <Eye className="h-3 w-3" />
                {article.view_count}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
