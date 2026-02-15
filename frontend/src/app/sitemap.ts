import { MetadataRoute } from 'next';

const SITE = process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchAll(endpoint: string) {
  try {
    const res = await fetch(`${API}${endpoint}`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [articles, news, doctors, education] = await Promise.all([
    fetchAll('/content/articles/?status=published'),
    fetchAll('/content/public-news/'),
    fetchAll('/content/doctors/'),
    fetchAll('/content/public-education/'),
  ]);

  const statics: MetadataRoute.Sitemap = [
    { url: SITE, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: `${SITE}/blog`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.8 },
    { url: `${SITE}/news`, lastModified: new Date(), changeFrequency: 'daily', priority: 0.8 },
    { url: `${SITE}/doctors`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.8 },
    { url: `${SITE}/education`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.7 },
    { url: `${SITE}/contact`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
    { url: `${SITE}/privacy-policy`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
    { url: `${SITE}/terms`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
    { url: `${SITE}/kvkk`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
  ];

  const blogPages = articles.flatMap((a: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/blog/${a.slug}`, lastModified: new Date(a.updated_at || a.created_at), changeFrequency: 'monthly' as const, priority: 0.7,
  })));

  const newsPages = news.flatMap((n: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/news/${n.slug}`, lastModified: new Date(n.updated_at || n.created_at), changeFrequency: 'weekly' as const, priority: 0.7,
  })));

  const doctorPages = doctors.map((d: any) => {
    const slug = `${(d.full_name || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}-${String(d.id).slice(0, 8)}`;
    return { url: `${SITE}/doctors/${slug}`, lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.7 };
  });

  const eduPages = education.map((e: any) => ({
    url: `${SITE}/education/${e.slug}`, lastModified: new Date(e.updated_at || e.created_at), changeFrequency: 'monthly' as const, priority: 0.6,
  }));

  return [...statics, ...blogPages, ...newsPages, ...doctorPages, ...eduPages];
}
