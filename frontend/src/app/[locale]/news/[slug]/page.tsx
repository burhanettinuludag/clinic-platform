import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getNewsBySlug } from '@/lib/server-api';
import Link from 'next/link';
import { ArrowLeft, Calendar, User, Tag, Eye, Shield, ExternalLink } from 'lucide-react';

interface Props {
  params: { slug: string; locale: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const news = await getNewsBySlug(params.slug, params.locale);
  if (!news) return { title: 'Haber Bulunamadi' };

  const title = news.meta_title || news.title_tr || news.title_en;
  const desc = news.meta_description || news.excerpt_tr || '';

  return {
    title,
    description: desc.slice(0, 160),
    openGraph: {
      title,
      description: desc.slice(0, 160),
      type: 'article',
      publishedTime: news.published_at,
      images: news.featured_image ? [{ url: news.featured_image }] : [],
    },
    alternates: {
      canonical: `/${params.locale}/news/${params.slug}`,
      languages: { tr: `/tr/news/${params.slug}`, en: `/en/news/${params.slug}` },
    },
  };
}

function JsonLd({ news }: { news: any }) {
  const schema = news.schema_markup || {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: news.title_tr,
    datePublished: news.published_at,
    dateModified: news.updated_at,
  };
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />;
}

function AuthorCard({ profile }: { profile: any }) {
  if (!profile) return null;
  return (
    <div className="flex items-start gap-4 rounded-xl border bg-gray-50 p-4 mt-8">
      {profile.profile_photo && <img src={profile.profile_photo} alt="" className="h-14 w-14 rounded-full object-cover" />}
      <div>
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">{profile.specialty}</span>
          {profile.is_verified && <Shield className="h-4 w-4 text-green-500" />}
        </div>
        <p className="text-sm text-gray-600 mt-0.5">{profile.institution}{profile.department ? ` - ${profile.department}` : ''}</p>
        {profile.bio && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{profile.bio}</p>}
      </div>
    </div>
  );
}

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default async function NewsDetailPage({ params }: Props) {
  const news = await getNewsBySlug(params.slug, params.locale);
  if (!news) notFound();

  const title = params.locale === 'tr' ? news.title_tr : news.title_en || news.title_tr;
  const body = params.locale === 'tr' ? news.body_tr : news.body_en || news.body_tr;
  const excerpt = params.locale === 'tr' ? news.excerpt_tr : news.excerpt_en || news.excerpt_tr;

  return (
    <>
      <JsonLd news={news} />
      <article className="max-w-3xl mx-auto px-4 py-8">
        <Link href={`/${params.locale}/news`} className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-6">
          <ArrowLeft className="w-4 h-4" /> Haberlere Don
        </Link>

        {news.featured_image && (
          <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden mb-6">
            <img src={news.featured_image} alt={news.featured_image_alt || title} className="w-full h-full object-cover" />
          </div>
        )}

        <div className="flex items-center gap-4 text-sm text-gray-400 mb-4 flex-wrap">
          {news.category_display && (
            <span className="flex items-center gap-1 text-blue-600"><Tag className="w-4 h-4" /> {news.category_display}</span>
          )}
          {news.author_name && (
            <span className="flex items-center gap-1"><User className="w-4 h-4" /> {news.author_name}</span>
          )}
          {news.published_at && (
            <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {fmtDate(news.published_at)}</span>
          )}
          {news.view_count > 0 && (
            <span className="flex items-center gap-1"><Eye className="w-4 h-4" /> {news.view_count} goruntulenme</span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">{title}</h1>
        {excerpt && <p className="text-lg text-gray-600 mb-6">{excerpt}</p>}

        {body && <div className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: body }} />}

        {news.source_urls && news.source_urls.length > 0 && (
          <div className="mt-8 border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Kaynaklar</h3>
            {news.source_urls.map((url: string, i: number) => (
              <a key={i} href={url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 mb-1">
                <ExternalLink className="w-3 h-3" />{url}
              </a>
            ))}
          </div>
        )}

        <AuthorCard profile={news.author_profile} />
      </article>
    </>
  );
}
