import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Doktorlarimiz | Norosera',
  description: 'Norosera platformunda yer alan uzman noroloji doktorlari.',
};

async function getDoctors() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/content/doctors/`, {
      next: { revalidate: 600, tags: ['doctors'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data;
  } catch { return []; }
}

export default async function DoctorsPage() {
  const doctors = await getDoctors();

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Doktorlarimiz</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Alaninda uzman noroloji hekimlerimiz</p>

      {doctors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map((doc: any) => (
            <Link key={doc.id} href={`/doctors/${doc.slug}`}
              className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-6 hover:shadow-lg transition-shadow group">
              <div className="flex items-center gap-4 mb-4">
                {doc.profile_photo ? (
                  <img src={doc.profile_photo} alt={doc.full_name} className="h-16 w-16 rounded-full object-cover" />
                ) : (
                  <div className="h-16 w-16 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
                    {doc.full_name?.charAt(0)}
                  </div>
                )}
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors">{doc.full_name}</h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{doc.specialty_display}</p>
                </div>
              </div>
              {doc.headline_tr && <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">{doc.headline_tr}</p>}
              <div className="flex items-center gap-4 text-xs text-gray-400">
                {doc.institution && <span>{doc.institution}</span>}
                {doc.is_verified && <span className="text-green-500 font-medium">✓ Dogrulanmis</span>}
              </div>
              <div className="flex gap-3 mt-3 pt-3 border-t dark:border-slate-700 text-xs text-gray-400">
                <span>{doc.article_count} makale</span>
                <span>{doc.total_views} goruntulenme</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-gray-400">Henuz doktor profili yok</div>
      )}
    </div>
  );
}
