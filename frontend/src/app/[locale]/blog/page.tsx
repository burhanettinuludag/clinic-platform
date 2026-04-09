import { Metadata } from 'next';
import Link from 'next/link';
import { Calendar, User, Tag } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Blog - Norosera | Nöroloji Sağlık Rehberi',
  description: 'Nöroloji alanında uzman doktorlar tarafından hazırlanan güncel sağlık içerikleri, makale ve rehberler.',
  openGraph: {
    title: 'Blog - Norosera',
    description: 'Nöroloji alanında güncel sağlık içerikleri ve rehberler.',
    type: 'website',
  },
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getArticles(locale: string) {
  try {
    const res = await fetch(`${API}/content/articles/`, {
      headers: { 'Accept-Language': locale },
      next: { revalidate: 300, tags: ['articles'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

async function getCategories(locale: string) {
  try {
    const res = await fetch(`${API}/content/categories/`, {
      headers: { 'Accept-Language': locale },
      next: { revalidate: 3600, tags: ['categories'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

function fmtDate(d: string, locale: string = 'tr') {
  return new Date(d).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US', { day: 'numeric', month: 'long', year: 'numeric' });
}

function JsonLd() {
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Norosera Blog',
    description: 'Nöroloji alanında uzman içerikleri',
    publisher: {
      '@type': 'Organization',
      name: 'Norosera',
      url: 'https://norosera.com',
    },
  };
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />;
}

export default async function BlogPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const [articles, categories] = await Promise.all([
    getArticles(locale),
    getCategories(locale),
  ]);

  const isTr = locale === 'tr';

  return (
    <>
      <JsonLd />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Blog</h1>
        <p className="text-gray-500 mb-8">{isTr ? 'Sağlık hakkında güncel içerikler ve bilgiler.' : 'Current health content and information.'}</p>

        {categories && categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-8">
            {categories.map((cat: any) => (
              <span key={cat.id} className="px-4 py-2 rounded-full text-sm bg-gray-100 text-gray-600">
                {cat.name}
              </span>
            ))}
          </div>
        )}

        {articles && articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article: any) => (
              <Link key={article.id} href={`/${locale}/blog/${article.slug}`}
                className="group bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition">
                {article.featured_image && (
                  <div className="aspect-video bg-gray-100 overflow-hidden">
                    <img src={article.featured_image} alt={article.title} className="w-full h-full object-cover group-hover:scale-105 transition" />
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
                      <span className="flex items-center gap-1"><User className="w-3 h-3" /> {article.author_name}</span>
                    )}
                    {article.published_at && (
                      <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {fmtDate(article.published_at, locale)}</span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">{isTr ? 'Henüz içerik bulunmuyor.' : 'No content available yet.'}</div>
        )}
      </div>
    </>
  );
}
