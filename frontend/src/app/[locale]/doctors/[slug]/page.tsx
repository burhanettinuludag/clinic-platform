import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getDoctor(slug: string) {
  const uuid = slug.split('-').pop();
  try {
    const res = await fetch(`${API}/content/doctors/${uuid}/`, { next: { revalidate: 600, tags: ['doctor', slug] } });
    if (!res.ok) return null;
    return await res.json();
  } catch { return null; }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const doc = await getDoctor(params.slug);
  if (!doc) return { title: 'Doktor Bulunamadi' };
  return {
    title: `${doc.full_name} - ${doc.specialty_display} | Norosera`,
    description: doc.headline_tr || doc.bio_tr?.slice(0, 160),
    openGraph: { title: doc.full_name, description: doc.headline_tr, type: 'profile', ...(doc.profile_photo && { images: [doc.profile_photo] }) },
  };
}

export default async function DoctorDetailPage({ params }: { params: { slug: string } }) {
  const doc = await getDoctor(params.slug);
  if (!doc) notFound();

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      {doc.schema_markup && (
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(doc.schema_markup) }} />
      )}

      {/* Header */}
      <div className="flex items-start gap-6 mb-8">
        {doc.profile_photo ? (
          <img src={doc.profile_photo} alt={doc.full_name} className="h-24 w-24 rounded-full object-cover ring-4 ring-cyan-100" />
        ) : (
          <div className="h-24 w-24 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center text-white text-3xl font-bold ring-4 ring-cyan-100">
            {doc.full_name?.charAt(0)}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{doc.full_name}</h1>
          <p className="text-lg text-cyan-600">{doc.specialty_display}</p>
          {doc.headline_tr && <p className="text-gray-500 dark:text-gray-400 mt-1">{doc.headline_tr}</p>}
          <div className="flex items-center gap-3 mt-2">
            {doc.institution && <span className="text-sm text-gray-500">{doc.institution}{doc.department && `, ${doc.department}`}</span>}
            {doc.is_verified && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Dogrulanmis</span>}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{doc.article_count}</p>
          <p className="text-xs text-gray-500">Makale</p>
        </div>
        <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{doc.total_views}</p>
          <p className="text-xs text-gray-500">Goruntulenme</p>
        </div>
        <div className="rounded-xl border bg-white dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{doc.average_rating > 0 ? doc.average_rating : '-'}</p>
          <p className="text-xs text-gray-500">Puan</p>
        </div>
      </div>

      {/* Bio */}
      {doc.bio_tr && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Hakkinda</h2>
          <p className="text-gray-600 dark:text-gray-300 leading-relaxed whitespace-pre-line">{doc.bio_tr}</p>
        </div>
      )}

      {/* Education */}
      {doc.education?.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Egitim</h2>
          <div className="space-y-2">
            {doc.education.map((e: any, i: number) => (
              <div key={i} className="rounded-lg border dark:border-slate-700 bg-white dark:bg-slate-800 p-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{e.degree || e}</p>
                {e.institution && <p className="text-xs text-gray-500">{e.institution}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Memberships */}
      {doc.memberships?.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Uyelikler</h2>
          <div className="flex flex-wrap gap-2">
            {doc.memberships.map((m: any, i: number) => (
              <span key={i} className="rounded-full bg-cyan-50 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300 px-3 py-1 text-xs font-medium">{m.name || m}</span>
            ))}
          </div>
        </div>
      )}

      {/* Links */}
      <div className="flex flex-wrap gap-3">
        {doc.orcid_id && <a href={`https://orcid.org/${doc.orcid_id}`} target="_blank" rel="noopener" className="text-sm text-green-600 hover:underline">ORCID</a>}
        {doc.google_scholar_url && <a href={doc.google_scholar_url} target="_blank" rel="noopener" className="text-sm text-blue-600 hover:underline">Google Scholar</a>}
        {doc.linkedin_url && <a href={doc.linkedin_url} target="_blank" rel="noopener" className="text-sm text-blue-700 hover:underline">LinkedIn</a>}
        {doc.website_url && <a href={doc.website_url} target="_blank" rel="noopener" className="text-sm text-purple-600 hover:underline">Website</a>}
      </div>
    </div>
  );
}
