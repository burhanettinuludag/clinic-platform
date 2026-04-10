import type { Metadata } from 'next';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const isTr = locale === 'tr';

  const title = isTr
    ? 'Uyku Sağlığı Rehberi | Norosera'
    : 'Sleep Health Guide | Norosera';

  const description = isTr
    ? 'Uyku bozuklukları, uyku hijyeni, uyku apnesi, insomni ve nörolojik hastalıklarda uyku sorunları hakkında kapsamlı bilgi rehberi. Uyku kalitesini artırmanın yolları.'
    : 'Comprehensive guide about sleep disorders, sleep hygiene, sleep apnea, insomnia and sleep problems in neurological diseases. Ways to improve sleep quality.';

  return {
    title,
    description,
    keywords: isTr
      ? 'uyku sağlığı, uyku bozuklukları, uyku hijyeni, insomni, uyku apnesi, nörolojik hastalıklarda uyku, uyku kalitesi'
      : 'sleep health, sleep disorders, sleep hygiene, insomnia, sleep apnea, sleep in neurological diseases, sleep quality',
    openGraph: {
      title,
      description,
      type: 'website',
      siteName: 'Norosera',
    },
  };
}

export default function SleepLayout({ children }: { children: React.ReactNode }) {
  return children;
}
