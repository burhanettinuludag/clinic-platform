'use client';

import DiseaseNewsPage from '@/components/news/DiseaseNewsPage';

export default function EpilepsyNewsPage() {
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <DiseaseNewsPage
        disease="epilepsy"
        title_tr="Epilepsi Haberleri"
        title_en="Epilepsy News"
      />
    </div>
  );
}
