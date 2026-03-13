'use client';

import DiseaseNewsPage from '@/components/news/DiseaseNewsPage';

export default function MigraineNewsPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <DiseaseNewsPage
        disease="migraine"
        title_tr="Migren Haberleri"
        title_en="Migraine News"
      />
    </div>
  );
}
