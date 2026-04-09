import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Calendar, User, Tag, Shield } from 'lucide-react';

interface Props {
  params: Promise<{ slug: string; locale: string }>;
}

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getArticleBySlug(slug: string, locale: string) {
  try {
    const res = await fetch(`${API}/content/articles/${slug}/`, {
      headers: { 'Accept-Language': locale },
      next: { revalidate: 600, tags: ['article', slug] },
    });
    if (!res.ok) return null;
    return res.json();
  } catch { return null; }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug, locale } = await params;
  const article = await getArticleBySlug(slug, locale);
  if (!article) return { title: locale === 'tr' ? 'Makale Bulunamadı' : 'Article Not Found' };

  return {
    title: article.seo_title || article.title,
    description: (article.seo_description || article.excerpt || '').slice(0, 160),
    openGraph: {
      title: article.title,
      description: (article.seo_description || article.excerpt || '').slice(0, 160),
      type: 'article',
      publishedTime: article.published_at,
      authors: article.author_name ? [article.author_name] : [],
      images: article.featured_image ? [{ url: article.featured_image }] : [],
    },
    alternates: {
      canonical: `/${locale}/blog/${slug}`,
      languages: { tr: `/tr/blog/${slug}`, en: `/en/blog/${slug}` },
    },
  };
}

function JsonLd({ article }: { article: any }) {
  const schema = article.schema_markup || {
    '@context': 'https://schema.org',
    '@type': 'MedicalWebPage',
    headline: article.title,
    datePublished: article.published_at,
    dateModified: article.updated_at,
  };
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />;
}

function AuthorCard({ profile }: { profile: any }) {
  if (!profile) return null;
  return (
    <div className="flex items-start gap-4 rounded-xl border bg-gray-50 p-4 mt-8">
      {profile.profile_photo && (
        <img src={profile.profile_photo} alt="" className="h-14 w-14 rounded-full object-cover" />
      )}
      <div>
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-900">{profile.specialty}</span>
          {profile.is_verified && <Shield className="h-4 w-4 text-green-500" />}
        </div>
        <p className="text-sm text-gray-600 mt-0.5">{profile.institution}{profile.department ? ` - ${profile.department}` : ''}</p>
        {profile.bio && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{profile.bio}</p>}
        {profile.orcid_id && <p className="text-xs text-blue-500 mt-1">ORCID: {profile.orcid_id}</p>}
      </div>
    </div>
  );
}

function fmtDate(d: string, locale: string = 'tr') {
  return new Date(d).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default async function ArticlePage({ params }: Props) {
  const { slug, locale } = await params;
  const article = await getArticleBySlug(slug, locale);
  if (!article) notFound();

  return (
    <>
      <JsonLd article={article} />
      <article className="max-w-3xl mx-auto px-4 py-8">
        <Link href={`/${locale}/blog`} className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-6">
          <ArrowLeft className="w-4 h-4" /> {locale === 'tr' ? 'Geri' : 'Back'}
        </Link>

        {article.featured_image && (
          <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden mb-6">
            <img src={article.featured_image} alt={article.title} className="w-full h-full object-cover" />
          </div>
        )}

        <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
          {article.category_name && (
            <span className="flex items-center gap-1 text-blue-600"><Tag className="w-4 h-4" /> {article.category_name}</span>
          )}
          {article.author_name && (
            <span className="flex items-center gap-1"><User className="w-4 h-4" /> {article.author_name}</span>
          )}
          {article.published_at && (
            <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {fmtDate(article.published_at, locale)}</span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
        {article.excerpt && <p className="text-lg text-gray-600 mb-6">{article.excerpt}</p>}

        {article.body && (
          <div className="prose prose-gray max-w-none" dangerouslySetInnerHTML={{ __html: article.body }} />
        )}

        <AuthorCard profile={article.author_profile} />
      </article>
    </>
  );
}
