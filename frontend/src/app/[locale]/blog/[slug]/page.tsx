'use client';

import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useArticle } from '@/hooks/useStoreData';
import { ArrowLeft, Calendar, User, Tag } from 'lucide-react';

export default function ArticleDetailPage() {
  const t = useTranslations();
  const params = useParams();
  const slug = params.slug as string;
  const { data: article, isLoading } = useArticle(slug);

  if (isLoading) {
    return <div className="max-w-3xl mx-auto px-4 py-12 text-center text-gray-500">{t('common.loading')}</div>;
  }

  if (!article) {
    return <div className="max-w-3xl mx-auto px-4 py-12 text-center text-gray-500">{t('common.noResults')}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <Link href="/blog" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-6">
        <ArrowLeft className="w-4 h-4" /> {t('common.back')}
      </Link>

      {article.featured_image && (
        <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden mb-6">
          <img src={article.featured_image} alt={article.title} className="w-full h-full object-cover" />
        </div>
      )}

      <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
        {article.category_name && (
          <span className="flex items-center gap-1 text-blue-600">
            <Tag className="w-4 h-4" /> {article.category_name}
          </span>
        )}
        {article.author_name && (
          <span className="flex items-center gap-1">
            <User className="w-4 h-4" /> {article.author_name}
          </span>
        )}
        {article.published_at && (
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {new Date(article.published_at).toLocaleDateString('tr-TR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </span>
        )}
      </div>

      <h1 className="text-3xl font-bold text-gray-900 mb-6">{article.title}</h1>

      {/* E-E-A-T: Yazar Profili */}
      {article.author_profile && (
        <div className="flex items-center gap-4 rounded-lg border bg-blue-50 p-4 mb-6">
          {article.author_profile.profile_photo && (
            <img src={article.author_profile.profile_photo} alt={article.author_name} className="w-14 h-14 rounded-full object-cover border-2 border-white shadow" />
          )}
          <div>
            <p className="font-semibold text-gray-900">{article.author_name}</p>
            <p className="text-sm text-gray-600">{article.author_profile.specialty}{article.author_profile.institution ? ' - ' + article.author_profile.institution : ''}</p>
            {article.author_profile.is_verified && (
              <span className="inline-flex items-center gap-1 mt-1 text-xs text-green-700 bg-green-100 rounded-full px-2 py-0.5">Dogrulanmis Hekim</span>
            )}
          </div>
        </div>
      )}

      {article.body && (
        <div
          className="prose prose-gray max-w-none"
          dangerouslySetInnerHTML={{ __html: article.body }}
        />
      )}

      {/* E-E-A-T: JSON-LD Schema */}
      {article.schema_markup && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(article.schema_markup) }}
        />
      )}
    </div>
  );
}
