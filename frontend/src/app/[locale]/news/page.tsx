import { Metadata } from 'next';
import NewsMagazineWrapper from './NewsMagazineWrapper';

export const metadata: Metadata = {
  title: 'Nöroloji Haberleri | Norosera',
  description: 'FDA onayları, klinik çalışmalar, yeni tedaviler ve nöroloji dünyasından son haberler.',
  openGraph: {
    title: 'Nöroloji Haberleri | Norosera',
    description: 'Nörolojik hastalıklar alanındaki en güncel gelişmeler',
    type: 'website',
  },
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getNews() {
  try {
    const res = await fetch(`${API}/content/public-news/`, {
      next: { revalidate: 300, tags: ['news'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch {
    return [];
  }
}

export default async function NewsPage() {
  const articles = await getNews();

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <NewsMagazineWrapper articles={articles} />
    </div>
  );
}
