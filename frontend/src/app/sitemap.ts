import { MetadataRoute } from 'next';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchPublished(endpoint: string) {
  try {
    const res = await fetch(`${API}${endpoint}`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [articles, news, doctors] = await Promise.all([
    fetchPublished('/content/articles/?status=published'),
    fetchPublished('/content/news/?status=published'),
    fetchPublished('/content/doctors/'),
  ]);

  const staticPages = [
    { url: SITE_URL, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 1 },
    { url: `${SITE_URL}/tr`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${SITE_URL}/en`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.9 },
    { url: `${SITE_URL}/blog`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.8 },
    { url: `${SITE_URL}/news`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.8 },
    { url: `${SITE_URL}/doctors`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.8 },
    { url: `${SITE_URL}/contact`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.5 },
    { url: `${SITE_URL}/education`, lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.6 },
  ];

  const articlePages = articles.flatMap((a: any) => [
    { url: `${SITE_URL}/tr/blog/${a.slug}`, lastModified: new Date(a.updated_at || a.published_at), changeFrequency: 'monthly' as const, priority: 0.7 },
    { url: `${SITE_URL}/en/blog/${a.slug}`, lastModified: new Date(a.updated_at || a.published_at), changeFrequency: 'monthly' as const, priority: 0.6 },
  ]);

  const newsPages = news.flatMap((n: any) => [
    { url: `${SITE_URL}/tr/news/${n.slug}`, lastModified: new Date(n.updated_at || n.published_at), changeFrequency: 'weekly' as const, priority: 0.7 },
    { url: `${SITE_URL}/en/news/${n.slug}`, lastModified: new Date(n.updated_at || n.published_at), changeFrequency: 'weekly' as const, priority: 0.6 },
  ]);

  const doctorPages = doctors.map((d: any) => {
    const name = (d.full_name || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    const slug = `${name}-${String(d.id).slice(0, 8)}`;
    return { url: `${SITE_URL}/doctors/${slug}`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.7 };
  });

  return [...staticPages, ...articlePages, ...newsPages, ...doctorPages];
}
