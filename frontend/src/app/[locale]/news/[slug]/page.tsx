import { Metadata } from 'next';
import { notFound } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getNewsItem(slug: string) {
  try {
    const res = await fetch(`${API}/content/public-news/${slug}/`, { next: { revalidate: 600, tags: ['news', slug] } });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const item = await getNewsItem(params.slug);
  if (!item) return { title: 'Haber Bulunamadi' };
  return {
    title: `${item.title_tr} | Norosera`,
    description: item.excerpt_tr || item.body_tr?.replace(/<[^>]*>/g, '').slice(0, 160),
    openGraph: { title: item.title_tr, description: item.excerpt_tr, type: 'article' },
  };
}

export default async function NewsDetailPage({ params }: { params: { slug: string } }) {
  const item = await getNewsItem(params.slug);
  if (!item) notFound();

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": item.title_tr, "description": item.excerpt_tr,
        "datePublished": item.created_at, "publisher": { "@type": "Organization", "name": "Norosera" },
      }) }} />

      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3 text-sm text-gray-500">
          <span className="capitalize">{item.category?.replace(/_/g, ' ')}</span>
          <span>·</span>
          <span>{new Date(item.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">{item.title_tr}</h1>
        {item.excerpt_tr && <p className="text-lg text-gray-500 dark:text-gray-400">{item.excerpt_tr}</p>}
      </div>

      <div className="prose prose-education dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: item.body_tr }} />
    </div>
  );
}
