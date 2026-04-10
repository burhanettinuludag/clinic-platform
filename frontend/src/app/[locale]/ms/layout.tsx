import type { Metadata } from 'next';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const isTr = locale === 'tr';

  const title = isTr
    ? 'Multipl Skleroz (MS) Rehberi | Norosera'
    : 'Multiple Sclerosis (MS) Guide | Norosera';

  const description = isTr
    ? 'Multipl Skleroz (MS) hakkında kapsamlı bilgi rehberi. MS tanımı, tanı kriterleri (McDonald 2017), MR bulguları, biyobelirteçler, DMT tedavileri, BTK inhibitörleri ve yeni tedavi seçenekleri.'
    : 'Comprehensive information guide about Multiple Sclerosis (MS). MS definition, diagnostic criteria (McDonald 2017), MRI findings, biomarkers, DMT treatments, BTK inhibitors and new treatment options.';

  return {
    title,
    description,
    keywords: isTr
      ? 'multipl skleroz, MS, demiyelinizan hastalık, McDonald tanı kriterleri, DMT tedavi, BTK inhibitörleri, remyelinizasyon, nörofilament, MR bulguları, oligoklonal band'
      : 'multiple sclerosis, MS, demyelinating disease, McDonald diagnostic criteria, DMT treatment, BTK inhibitors, remyelination, neurofilament, MRI findings, oligoclonal band',
    openGraph: {
      title,
      description,
      type: 'website',
      siteName: 'Norosera',
    },
  };
}

export default function MSLayout({ children }: { children: React.ReactNode }) {
  return children;
}
