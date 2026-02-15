/**
 * Server-side API fetch helper.
 * Next.js SSR/ISR icin kullanilir. Auth gerektirmeyen public endpoint'ler.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface FetchOptions {
  locale?: string;
  revalidate?: number;
  tags?: string[];
}

export async function serverFetch<T>(path: string, options: FetchOptions = {}): Promise<T | null> {
  const { locale = 'tr', revalidate = 300, tags } = options;
  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers: { 'Content-Type': 'application/json', 'Accept-Language': locale },
      next: { revalidate, ...(tags ? { tags } : {}) },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function getArticles(locale = 'tr') {
  return serverFetch<any[]>('/content/articles/', { locale, revalidate: 300, tags: ['articles'] });
}

export async function getArticleBySlug(slug: string, locale = 'tr') {
  return serverFetch<any>(`/content/articles/${slug}/`, { locale, revalidate: 600, tags: ['article', slug] });
}

export async function getCategories(locale = 'tr') {
  return serverFetch<any[]>('/content/categories/', { locale, revalidate: 3600, tags: ['categories'] });
}

export async function getNews(locale = 'tr') {
  return serverFetch<any[]>('/content/news/', { locale, revalidate: 300, tags: ['news'] });
}

export async function getNewsBySlug(slug: string, locale = 'tr') {
  return serverFetch<any>(\`/content/news/\${slug}/\`, { locale, revalidate: 600, tags: ['news', slug] });
}
