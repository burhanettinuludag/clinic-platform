import { MetadataRoute } from 'next';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchPublished(endpoint: string) {
  try {
    const res = await fetch(`${API_URL}${endpoint}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [articles, news] = await Promise.all([
    fetchPublished('/content/articles/'),
    fetchPublished('/content/news/'),
  ]);

  const staticPages = [
    { url: SITE_URL, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 1.0 },
    { url: `${SITE_URL}/tr`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 1.0 },
    { url: `${SITE_URL}/en`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 1.0 },
    { url: `${SITE_URL}/tr/blog`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.9 },
    { url: `${SITE_URL}/en/blog`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.9 },
    { url: `${SITE_URL}/tr/news`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.9 },
    { url: `${SITE_URL}/en/news`, lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.9 },
  ];

  const articlePages = articles.flatMap((a: any) => [
    {
      url: `${SITE_URL}/tr/blog/${a.slug}`,
      lastModified: new Date(a.updated_at || a.published_at),
      changeFrequency: 'weekly' as const,
      priority: 0.8,
    },
    {
      url: `${SITE_URL}/en/blog/${a.slug}`,
      lastModified: new Date(a.updated_at || a.published_at),
      changeFrequency: 'weekly' as const,
      priority: 0.7,
    },
  ]);

  const newsPages = news.flatMap((n: any) => [
    {
      url: `${SITE_URL}/tr/news/${n.slug}`,
      lastModified: new Date(n.updated_at || n.published_at),
      changeFrequency: 'daily' as const,
      priority: 0.8,
    },
    {
      url: `${SITE_URL}/en/news/${n.slug}`,
      lastModified: new Date(n.updated_at || n.published_at),
      changeFrequency: 'daily' as const,
      priority: 0.7,
    },
  ]);

  return [...staticPages, ...articlePages, ...newsPages];
}
