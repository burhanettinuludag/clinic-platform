import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Egitim Icerikleri | Norosera',
  description: 'Norolojik hastaliklar hakkinda uzman doktorlar tarafindan hazirlanan egitim icerikleri.',
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getEducation() {
  try {
    const res = await fetch(`${API}/content/public-education/`, { next: { revalidate: 600, tags: ['education'] } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

const TYPE_BADGE: Record<string, string> = {
  video: 'bg-red-100 text-red-700',
  text: 'bg-blue-100 text-blue-700',
  infographic: 'bg-green-100 text-green-700',
  interactive: 'bg-purple-100 text-purple-700',
};
const TYPE_LABEL: Record<string, string> = { video: 'Video', text: 'Makale', infographic: 'Infografik', interactive: 'Interaktif' };

export default async function EducationPage() {
  const items = await getEducation();

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Egitim Icerikleri</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Norolojik hastaliklar hakkinda uzman bilgileri</p>

      {items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item: any) => (
            <Link key={item.slug} href={`/education/${item.slug}`}
              className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 overflow-hidden hover:shadow-lg transition-shadow group">
              {item.image && (
                <div className="h-40 overflow-hidden">
                  <img src={item.image} alt={item.title_tr} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                </div>
              )}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={'rounded-full px-2 py-0.5 text-xs font-medium ' + (TYPE_BADGE[item.content_type] || TYPE_BADGE.text)}>
                    {TYPE_LABEL[item.content_type] || item.content_type}
                  </span>
                  <span className="text-xs text-gray-400">{item.estimated_duration_minutes} dk</span>
                </div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-cyan-600 transition-colors line-clamp-2">{item.title_tr}</h2>
                {item.body_tr && <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 line-clamp-3">{item.body_tr.replace(/<[^>]*>/g, '').slice(0, 150)}...</p>}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">Henuz egitim icerigi yok</div>
      )}
    </div>
  );
}
