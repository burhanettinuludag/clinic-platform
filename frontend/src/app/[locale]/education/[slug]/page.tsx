import { Metadata } from 'next';
import { notFound } from 'next/navigation';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getItem(slug: string, locale: string) {
  try {
    const res = await fetch(`${API}/content/public-education/${slug}/`, {
      headers: { 'Accept-Language': locale },
      next: { revalidate: 600, tags: ['education', slug] },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string; locale: string }> }): Promise<Metadata> {
  const { slug, locale } = await params;
  const item = await getItem(slug, locale);
  const isTr = locale === 'tr';
  if (!item) return { title: isTr ? 'İçerik Bulunamadı' : 'Content Not Found' };
  const desc = item.body?.replace(/<[^>]*>/g, '').slice(0, 160) || '';
  return {
    title: `${item.title} | Norosera ${isTr ? 'Eğitim' : 'Education'}`,
    description: desc,
    openGraph: { title: item.title, ...(item.image && { images: [item.image] }) },
  };
}

export default async function EducationDetailPage({ params }: { params: Promise<{ slug: string; locale: string }> }) {
  const { slug, locale } = await params;
  const item = await getItem(slug, locale);
  if (!item) notFound();

  const isTr = locale === 'tr';

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item.title,
        "description": item.body?.replace(/<[^>]*>/g, '').slice(0, 160) || '',
        ...(item.image && { "image": item.image }),
        "publisher": { "@type": "Organization", "name": "Norosera" },
      }) }} />

      {item.image && <img src={item.image} alt={item.title} className="w-full h-56 object-cover rounded-xl mb-6" />}

      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">{item.title}</h1>

      <div className="flex items-center gap-3 mb-6 text-sm text-gray-500">
        <span className="capitalize">{item.content_type}</span>
        <span>·</span>
        <span>{item.estimated_duration_minutes} {isTr ? 'dk okuma' : 'min read'}</span>
      </div>

      {item.video_url && (
        <div className="mb-6 rounded-xl overflow-hidden aspect-video">
          <iframe src={item.video_url} className="w-full h-full" allowFullScreen />
        </div>
      )}

      {item.body && (
        <div className="prose prose-education dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: item.body }} />
      )}
    </div>
  );
}
