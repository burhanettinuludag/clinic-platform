'use client';

import DiseaseNewsPage from '@/components/news/DiseaseNewsPage';

export default function DementiaNewsPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <DiseaseNewsPage
        disease="dementia"
        title_tr="Demans Haberleri"
        title_en="Dementia News"
      />
    </div>
  );
}
