import { Metadata } from 'next';
import { getNews } from '@/lib/server-api';
import Link from 'next/link';
import { Calendar, User, Eye, Zap } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Saglik Haberleri - Norosera | Noroloji Haberleri',
  description: 'Noroloji alaninda en guncel saglik haberleri, FDA onaylari, klinik calismalar ve kongre haberleri.',
  openGraph: {
    title: 'Saglik Haberleri - Norosera',
    description: 'Noroloji alaninda guncel saglik haberleri.',
    type: 'website',
  },
};

const PRIORITY_BADGE: Record<string, string> = {
  urgent: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-gray-100 text-gray-600',
  low: 'bg-gray-50 text-gray-500',
};

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}

export default async function NewsPage({ params }: { params: { locale: string } }) {
  const news = await getNews(params.locale);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-2">
        <Zap className="h-7 w-7 text-orange-500" />
        <h1 className="text-3xl font-bold text-gray-900">Saglik Haberleri</h1>
      </div>
      <p className="text-gray-500 mb-8">Noroloji alaninda en guncel haberler ve gelismeler.</p>

      {news && news.length > 0 ? (
        <div className="space-y-4">
          {news.map((n: any) => (
            <Link key={n.id} href={`/${params.locale}/news/${n.slug}`}
              className="group flex gap-4 rounded-xl border bg-white p-4 hover:shadow-lg transition">
              {n.featured_image && (
                <div className="hidden sm:block w-40 h-28 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                  <img src={n.featured_image} alt={n.featured_image_alt || n.title_tr} className="w-full h-full object-cover group-hover:scale-105 transition" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-blue-600">{n.category_display}</span>
                  {n.priority && n.priority !== 'medium' && (
                    <span className={'text-xs font-medium px-2 py-0.5 rounded-full ' + (PRIORITY_BADGE[n.priority] || '')}>{n.priority_display}</span>
                  )}
                </div>
                <h2 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition mb-1 line-clamp-2">
                  {n.title_tr || n.title_en}
                </h2>
                {(n.excerpt_tr || n.excerpt_en) && (
                  <p className="text-sm text-gray-500 line-clamp-2 mb-2">{n.excerpt_tr || n.excerpt_en}</p>
                )}
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  {n.author_name && <span className="flex items-center gap-1"><User className="w-3 h-3" />{n.author_name}</span>}
                  {n.published_at && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />{fmtDate(n.published_at)}</span>}
                  {n.view_count > 0 && <span className="flex items-center gap-1"><Eye className="w-3 h-3" />{n.view_count}</span>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">Henuz haber bulunmuyor.</div>
      )}
    </div>
  );
}
