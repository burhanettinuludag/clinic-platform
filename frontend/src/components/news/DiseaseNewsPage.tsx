'use client';

import { useEffect, useState } from 'react';
import { useLocale } from 'next-intl';
import api from '@/lib/api';
import NewsMagazine from './NewsMagazine';
import type { NewsArticle } from '@/lib/types/content';
import { Loader2 } from 'lucide-react';

interface DiseaseNewsPageProps {
  disease: string;
  title_tr: string;
  title_en: string;
}

export default function DiseaseNewsPage({ disease, title_tr, title_en }: DiseaseNewsPageProps) {
  const locale = useLocale();
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get('/content/news/', { params: { disease } })
      .then((res) => {
        setArticles(res.data.results || res.data);
      })
      .catch(() => setArticles([]))
      .finally(() => setLoading(false));
  }, [disease]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-teal-600" />
      </div>
    );
  }

  return (
    <NewsMagazine
      articles={articles}
      diseaseFilter={disease}
      showDiseaseTabs={false}
      showHeader={true}
      title={locale === 'tr' ? title_tr : title_en}
    />
  );
}
