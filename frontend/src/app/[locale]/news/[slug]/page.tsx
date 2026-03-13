import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Calendar, Eye, Tag } from 'lucide-react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getNewsItem(slug: string) {
  try {
    const res = await fetch(`${API}/content/public-news/${slug}/`, {
      next: { revalidate: 600, tags: ['news', slug] },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const item = await getNewsItem(slug);
  if (!item) return { title: 'Haber Bulunamadı' };
  return {
    title: `${item.title_tr} | Norosera`,
    description: item.excerpt_tr || item.body_tr?.replace(/<[^>]*>/g, '').slice(0, 160),
    openGraph: { title: item.title_tr, description: item.excerpt_tr, type: 'article' },
  };
}

const CATEGORY_LABELS: Record<string, { tr: string; en: string; color: string }> = {
  fda_approval: { tr: 'FDA Onayı', en: 'FDA Approval', color: 'bg-blue-100 text-blue-700' },
  ema_approval: { tr: 'EMA Onayı', en: 'EMA Approval', color: 'bg-indigo-100 text-indigo-700' },
  clinical_trial: { tr: 'Klinik Araştırma', en: 'Clinical Trial', color: 'bg-purple-100 text-purple-700' },
  guideline_update: { tr: 'Kılavuz Güncellemesi', en: 'Guideline Update', color: 'bg-teal-100 text-teal-700' },
  congress: { tr: 'Kongre', en: 'Congress', color: 'bg-amber-100 text-amber-700' },
  turkey_news: { tr: 'Türkiye Haberi', en: 'Turkey News', color: 'bg-red-100 text-red-700' },
  turkey_approval: { tr: 'Türkiye Onayı', en: 'Turkey Approval', color: 'bg-rose-100 text-rose-700' },
  new_device: { tr: 'Yeni Cihaz', en: 'New Device', color: 'bg-cyan-100 text-cyan-700' },
  popular_science: { tr: 'Popüler Bilim', en: 'Popular Science', color: 'bg-green-100 text-green-700' },
  research: { tr: 'Araştırma', en: 'Research', color: 'bg-violet-100 text-violet-700' },
};

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  const item = await getNewsItem(slug);
  if (!item) notFound();

  const isTr = locale === 'tr';
  const title = isTr ? item.title_tr : (item.title_en || item.title_tr);
  const excerpt = isTr ? item.excerpt_tr : (item.excerpt_en || item.excerpt_tr);
  const body = isTr ? item.body_tr : (item.body_en || item.body_tr);
  const categoryInfo = CATEGORY_LABELS[item.category];
  const categoryLabel = categoryInfo
    ? (isTr ? categoryInfo.tr : categoryInfo.en)
    : item.category?.replace(/_/g, ' ');
  const categoryColor = categoryInfo?.color || 'bg-gray-100 text-gray-700';

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'NewsArticle',
            headline: title,
            description: excerpt,
            datePublished: item.published_at || item.created_at,
            dateModified: item.updated_at,
            publisher: { '@type': 'Organization', name: 'Norosera' },
            ...(item.author_name && { author: { '@type': 'Person', name: item.author_name } }),
          }),
        }}
      />

      {/* Back link */}
      <Link
        href={`/${locale}/news`}
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-teal-600 transition-colors mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        {isTr ? 'Tüm Haberler' : 'All News'}
      </Link>

      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3 mb-4 text-sm">
          {item.category && (
            <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${categoryColor}`}>
              <Tag className="h-3 w-3" />
              {categoryLabel}
            </span>
          )}
          <span className="flex items-center gap-1 text-gray-400">
            <Calendar className="h-3.5 w-3.5" />
            {new Date(item.published_at || item.created_at).toLocaleDateString(isTr ? 'tr-TR' : 'en-US', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </span>
          {item.view_count > 0 && (
            <span className="flex items-center gap-1 text-gray-400">
              <Eye className="h-3.5 w-3.5" />
              {item.view_count.toLocaleString(isTr ? 'tr-TR' : 'en-US')}
            </span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
          {title}
        </h1>

        {excerpt && (
          <p className="text-lg text-gray-500 dark:text-gray-400 leading-relaxed">
            {excerpt}
          </p>
        )}

        {item.author_name && (
          <p className="mt-4 text-sm text-gray-500">
            {isTr ? 'Yazar:' : 'Author:'}{' '}
            <span className="font-medium text-gray-700">{item.author_name}</span>
          </p>
        )}
      </div>

      {/* Featured Image */}
      {item.featured_image && (
        <div className="mb-8 rounded-xl overflow-hidden">
          <img
            src={item.featured_image}
            alt={item.featured_image_alt || title}
            className="w-full h-auto max-h-[400px] object-cover"
          />
          {item.featured_image_alt && (
            <p className="text-xs text-gray-400 mt-2 italic">{item.featured_image_alt}</p>
          )}
        </div>
      )}

      {/* Divider */}
      <div className="border-t border-gray-200 dark:border-gray-700 mb-8" />

      {/* Body */}
      <div
        className="prose prose-education dark:prose-invert max-w-none"
        dangerouslySetInnerHTML={{ __html: body }}
      />

      {/* Source */}
      {item.original_source && (
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-400">
            {isTr ? 'Kaynak:' : 'Source:'}{' '}
            <span className="text-gray-600">{item.original_source}</span>
          </p>
        </div>
      )}

      {/* Related diseases */}
      {item.related_diseases && item.related_diseases.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {item.related_diseases.map((d: string) => (
            <Link
              key={d}
              href={`/${locale}/patient/${d}/news`}
              className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700 hover:bg-teal-100 transition-colors"
            >
              {d === 'migraine' ? (isTr ? 'Migren Haberleri' : 'Migraine News')
                : d === 'epilepsy' ? (isTr ? 'Epilepsi Haberleri' : 'Epilepsy News')
                : d === 'dementia' ? (isTr ? 'Demans Haberleri' : 'Dementia News')
                : d}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
