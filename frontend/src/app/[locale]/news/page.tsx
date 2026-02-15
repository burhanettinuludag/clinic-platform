import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Noroloji Haberleri | Norosera',
  description: 'FDA onaylari, klinik calismalar, yeni tedaviler ve noroloji dunyasindan son haberler.',
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getNews() {
  try {
    const res = await fetch(`${API}/content/public-news/`, { next: { revalidate: 300, tags: ['news'] } });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

const CAT_BADGE: Record<string, string> = {
  fda_approval: 'bg-green-100 text-green-700', ema_approval: 'bg-blue-100 text-blue-700',
  clinical_trial: 'bg-purple-100 text-purple-700', congress: 'bg-amber-100 text-amber-700',
  new_device: 'bg-cyan-100 text-cyan-700', turkey_news: 'bg-red-100 text-red-700',
  popular_science: 'bg-pink-100 text-pink-700', drug_update: 'bg-orange-100 text-orange-700',
};
const CAT_LABEL: Record<string, string> = {
  fda_approval: 'FDA', ema_approval: 'EMA', turkey_approval: 'TR Ruhsat', clinical_trial: 'Klinik Calisma',
  new_device: 'Yeni Teknoloji', congress: 'Kongre', turkey_news: 'Turkiye', popular_science: 'Populer Bilim',
  drug_update: 'Ilac', guideline_update: 'Kilavuz',
};

export default async function NewsPage() {
  const news = await getNews();

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Noroloji Haberleri</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Son gelismeler ve guncel haberler</p>

      {news.length > 0 ? (
        <div className="space-y-4">
          {news.map((n: any) => (
            <Link key={n.slug} href={`/news/${n.slug}`}
              className="block rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-5 hover:shadow-md transition-shadow group">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={'rounded-full px-2 py-0.5 text-xs font-medium ' + (CAT_BADGE[n.category] || 'bg-gray-100 text-gray-600')}>
                      {CAT_LABEL[n.category] || n.category}
                    </span>
                    <span className="text-xs text-gray-400">{new Date(n.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                    {n.priority === 'urgent' && <span className="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded font-medium">Acil</span>}
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-cyan-600 transition-colors">{n.title_tr}</h2>
                  {n.excerpt_tr && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{n.excerpt_tr}</p>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">Henuz haber yok</div>
      )}
    </div>
  );
}
