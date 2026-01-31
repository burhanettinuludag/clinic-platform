'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useArticles, useContentCategories } from '@/hooks/useStoreData';
import { Calendar, User, Tag } from 'lucide-react';
import { useState } from 'react';

export default function BlogPage() {
  const t = useTranslations();
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const { data: articles, isLoading } = useArticles(
    selectedCategory ? { category: selectedCategory } : undefined
  );
  const { data: categories } = useContentCategories();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('nav.blog')}</h1>
      <p className="text-gray-500 mb-8">Saglik hakkinda guncel icerikler ve bilgiler.</p>

      {/* Categories */}
      {categories && categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setSelectedCategory(undefined)}
            className={`px-4 py-2 rounded-full text-sm transition ${
              !selectedCategory ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {t('common.total')}
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm transition ${
                selectedCategory === cat.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {/* Articles Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>
      ) : articles && articles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <Link
              key={article.id}
              href={`/blog/${article.slug}`}
              className="group bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition"
            >
              {article.featured_image && (
                <div className="aspect-video bg-gray-100 overflow-hidden">
                  <img
                    src={article.featured_image}
                    alt={article.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                </div>
              )}
              <div className="p-5">
                {article.category_name && (
                  <span className="inline-flex items-center gap-1 text-xs text-blue-600 mb-2">
                    <Tag className="w-3 h-3" /> {article.category_name}
                  </span>
                )}
                <h2 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition mb-2">
                  {article.title}
                </h2>
                {article.excerpt && (
                  <p className="text-sm text-gray-500 line-clamp-2 mb-3">{article.excerpt}</p>
                )}
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  {article.author_name && (
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" /> {article.author_name}
                    </span>
                  )}
                  {article.published_at && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(article.published_at).toLocaleDateString('tr-TR')}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">{t('common.noResults')}</div>
      )}
    </div>
  );
}
