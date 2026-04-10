import { MetadataRoute } from 'next';

const SITE = process.env.NEXT_PUBLIC_SITE_URL || 'https://norosera.com';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function safeDate(value: any): Date {
  if (!value) return new Date();
  const d = new Date(value);
  return isNaN(d.getTime()) ? new Date() : d;
}

async function fetchAll(endpoint: string) {
  try {
    const res = await fetch(`${API}${endpoint}`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [articles, news, doctors, education, sleepArticles, msArticles] = await Promise.all([
    fetchAll('/content/articles/?status=published'),
    fetchAll('/content/public-news/'),
    fetchAll('/content/doctors/'),
    fetchAll('/content/public-education/'),
    fetchAll('/sleep/articles/'),
    fetchAll('/ms/articles/'),
  ]);

  // Static pages with language alternates
  const staticPaths = [
    { path: '', changeFrequency: 'weekly' as const, priority: 1 },
    { path: '/blog', changeFrequency: 'daily' as const, priority: 0.8 },
    { path: '/news', changeFrequency: 'daily' as const, priority: 0.8 },
    { path: '/doctors', changeFrequency: 'weekly' as const, priority: 0.8 },
    { path: '/education', changeFrequency: 'weekly' as const, priority: 0.7 },
    { path: '/sleep', changeFrequency: 'weekly' as const, priority: 0.7 },
    { path: '/ms', changeFrequency: 'weekly' as const, priority: 0.7 },
    { path: '/contact', changeFrequency: 'monthly' as const, priority: 0.5 },
    { path: '/privacy-policy', changeFrequency: 'yearly' as const, priority: 0.3 },
    { path: '/terms', changeFrequency: 'yearly' as const, priority: 0.3 },
    { path: '/kvkk', changeFrequency: 'yearly' as const, priority: 0.3 },
  ];

  const statics: MetadataRoute.Sitemap = staticPaths.flatMap(({ path, changeFrequency, priority }) => [
    {
      url: `${SITE}/tr${path}`,
      lastModified: new Date(),
      changeFrequency,
      priority,
      alternates: {
        languages: {
          tr: `${SITE}/tr${path}`,
          en: `${SITE}/en${path}`,
        },
      },
    },
    {
      url: `${SITE}/en${path}`,
      lastModified: new Date(),
      changeFrequency,
      priority: priority > 0.3 ? priority - 0.1 : priority,
      alternates: {
        languages: {
          tr: `${SITE}/tr${path}`,
          en: `${SITE}/en${path}`,
        },
      },
    },
  ]);

  const blogPages = articles.flatMap((a: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/blog/${a.slug}`,
    lastModified: safeDate(a.updated_at || a.created_at),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
    alternates: {
      languages: {
        tr: `${SITE}/tr/blog/${a.slug}`,
        en: `${SITE}/en/blog/${a.slug}`,
      },
    },
  })));

  const newsPages = news.flatMap((n: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/news/${n.slug}`,
    lastModified: safeDate(n.updated_at || n.created_at),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
    alternates: {
      languages: {
        tr: `${SITE}/tr/news/${n.slug}`,
        en: `${SITE}/en/news/${n.slug}`,
      },
    },
  })));

  const doctorPages = doctors.map((d: any) => {
    const slug = `${(d.full_name || '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}-${String(d.id).slice(0, 8)}`;
    return {
      url: `${SITE}/doctors/${slug}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    };
  });

  const eduPages = education.map((e: any) => ({
    url: `${SITE}/education/${e.slug}`,
    lastModified: safeDate(e.updated_at || e.created_at),
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }));

  const sleepPages = sleepArticles.flatMap((a: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/sleep/${a.slug}`,
    lastModified: safeDate(a.updated_at || a.created_at),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
    alternates: {
      languages: {
        tr: `${SITE}/tr/sleep/${a.slug}`,
        en: `${SITE}/en/sleep/${a.slug}`,
      },
    },
  })));

  const msPages = msArticles.flatMap((a: any) => ['tr', 'en'].map(l => ({
    url: `${SITE}/${l}/ms/${a.slug}`,
    lastModified: safeDate(a.updated_at || a.created_at),
    changeFrequency: 'monthly' as const,
    priority: 0.7,
    alternates: {
      languages: {
        tr: `${SITE}/tr/ms/${a.slug}`,
        en: `${SITE}/en/ms/${a.slug}`,
      },
    },
  })));

  return [...statics, ...blogPages, ...newsPages, ...doctorPages, ...eduPages, ...sleepPages, ...msPages];
}
