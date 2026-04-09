import { Metadata } from 'next';
import Link from 'next/link';
import { Lock, ArrowRight, GraduationCap } from 'lucide-react';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const isTr = locale === 'tr';
  return {
    title: isTr ? 'Eğitim İçerikleri | Norosera' : 'Educational Content | Norosera',
    description: isTr
      ? 'Nörolojik hastalıklar hakkında uzman doktorlar tarafından hazırlanan eğitim içerikleri.'
      : 'Educational content about neurological diseases prepared by expert doctors.',
  };
}

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function getEducation(locale: string) {
  try {
    const res = await fetch(`${API}/content/public-education/`, {
      headers: { 'Accept-Language': locale },
      next: { revalidate: 600, tags: ['education'] },
    });
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
const TYPE_LABEL: Record<string, { tr: string; en: string }> = {
  video: { tr: 'Video', en: 'Video' },
  text: { tr: 'Makale', en: 'Article' },
  infographic: { tr: 'İnfografik', en: 'Infographic' },
  interactive: { tr: 'İnteraktif', en: 'Interactive' },
};

export default async function EducationPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const items = await getEducation(locale);
  const isTr = locale === 'tr';

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{isTr ? 'Eğitim İçerikleri' : 'Educational Content'}</h1>
      <p className="text-gray-500 mb-8">{isTr ? 'Nörolojik hastalıklar hakkında uzman bilgileri' : 'Expert information about neurological diseases'}</p>

      {items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item: any) => (
            <Link key={item.slug} href={`/education/${item.slug}`}
              className="rounded-xl border bg-white overflow-hidden hover:shadow-lg transition-shadow group">
              {item.image && (
                <div className="h-40 overflow-hidden">
                  <img src={item.image} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                </div>
              )}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={'rounded-full px-2 py-0.5 text-xs font-medium ' + (TYPE_BADGE[item.content_type] || TYPE_BADGE.text)}>
                    {TYPE_LABEL[item.content_type]?.[isTr ? 'tr' : 'en'] || item.content_type}
                  </span>
                  <span className="text-xs text-gray-400">{item.estimated_duration_minutes} {isTr ? 'dk' : 'min'}</span>
                </div>
                <h2 className="text-lg font-semibold text-gray-900 group-hover:text-cyan-600 transition-colors line-clamp-2">{item.title}</h2>
                {item.body && <p className="text-sm text-gray-500 mt-2 line-clamp-3">{item.body.replace(/<[^>]*>/g, '').slice(0, 150)}...</p>}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="max-w-lg mx-auto text-center py-16">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-teal-50 mb-6">
            <GraduationCap className="w-10 h-10 text-teal-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-3">{isTr ? 'Eğitim İçerikleri Üyelere Özeldir' : 'Educational Content is Members-Only'}</h2>
          <p className="text-gray-500 mb-2">
            {isTr ? 'Uzman doktorlar tarafından hazırlanan eğitim içeriklerine erişmek için üye olmanız gerekmektedir.' : 'You need to register to access educational content prepared by expert doctors.'}
          </p>
          <p className="text-gray-400 text-sm mb-8">
            {isTr ? 'Kayıt olduktan sonra hastalık modülünüze özel eğitim materyallerine, videolara ve interaktif içeriklere erişebilirsiniz.' : 'After registering, you can access disease module-specific educational materials, videos, and interactive content.'}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-teal-600 text-white rounded-xl text-sm font-semibold hover:bg-teal-700 transition-all shadow-sm"
            >
              {isTr ? 'Ücretsiz Kayıt Ol' : 'Register for Free'}
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/auth/login"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-gray-700 rounded-xl text-sm font-semibold border border-gray-200 hover:border-teal-300 hover:text-teal-700 transition-all"
            >
              <Lock className="w-4 h-4" />
              {isTr ? 'Giriş Yap' : 'Login'}
            </Link>
          </div>

          <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
            {(isTr ? [
              { icon: '🧠', title: 'Hastalık Bilgileri', desc: 'Migren, epilepsi ve demans hakkında kapsamlı eğitimler' },
              { icon: '🎥', title: 'Video İçerikler', desc: 'Uzman doktorların hazırladığı eğitici videolar' },
              { icon: '📊', title: 'İnteraktif Materyaller', desc: 'Bilginizi pekiştiren interaktif içerikler' },
            ] : [
              { icon: '🧠', title: 'Disease Information', desc: 'Comprehensive education on migraine, epilepsy, and dementia' },
              { icon: '🎥', title: 'Video Content', desc: 'Educational videos prepared by expert doctors' },
              { icon: '📊', title: 'Interactive Materials', desc: 'Interactive content to reinforce your knowledge' },
            ]).map((feat) => (
              <div key={feat.title} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
                <span className="text-2xl mb-2 block">{feat.icon}</span>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">{feat.title}</h3>
                <p className="text-gray-500 text-xs">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
