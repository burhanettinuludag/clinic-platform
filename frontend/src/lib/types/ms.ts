export interface MSCategory {
  id: string;
  slug: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  description_tr: string;
  description_en: string;
  icon: string;
  order: number;
  article_count: number;
}

export type MSArticleType = 'definition' | 'diagnosis' | 'imaging' | 'biomarker' | 'treatment' | 'new_treatment' | 'general';

export interface MSArticle {
  id: string;
  slug: string;
  article_type: MSArticleType;
  title: string;
  subtitle: string;
  summary: string;
  content?: string;
  category_name?: string;
  category?: MSCategory;
  cover_image: string | null;
  cover_image_url: string;
  icon: string;
  reading_time_minutes: number;
  is_featured: boolean;
  view_count: number;
  references?: string;
  author_name: string;
  meta_title?: string;
  meta_description?: string;
  created_at: string;
  updated_at?: string;
}

export interface MSTip {
  id: string;
  title: string;
  content: string;
  icon: string;
  order: number;
}

export interface MSFAQ {
  id: string;
  question: string;
  answer: string;
  order: number;
}
