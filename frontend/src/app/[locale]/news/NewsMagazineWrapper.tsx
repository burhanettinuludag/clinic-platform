'use client';

import NewsMagazine from '@/components/news/NewsMagazine';
import type { NewsArticle } from '@/lib/types/content';

export default function NewsMagazineWrapper({ articles }: { articles: NewsArticle[] }) {
  return (
    <NewsMagazine
      articles={articles}
      showDiseaseTabs={true}
      showHeader={true}
    />
  );
}
