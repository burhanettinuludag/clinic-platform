export interface SleepCategory {
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

export type SleepArticleType = 'general' | 'disorder' | 'hygiene' | 'diagnosis' | 'disease_sleep' | 'tip';

export interface SleepArticle {
  id: string;
  slug: string;
  article_type: SleepArticleType;
  title: string;
  subtitle: string;
  summary: string;
  content?: string;
  category_name?: string;
  category?: SleepCategory;
  related_disease: string;
  cover_image: string | null;
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

export interface SleepTip {
  id: string;
  title: string;
  content: string;
  icon: string;
  order: number;
}

export interface SleepFAQ {
  id: string;
  question: string;
  answer: string;
  order: number;
}

// ── Screening Tests ───────────────────────────────────────────────────

export interface SleepScreeningOption {
  id: string;
  text: string;
  score: number;
  order: number;
}

export interface SleepScreeningQuestion {
  id: string;
  question: string;
  help_text: string;
  order: number;
  options: SleepScreeningOption[];
}

export type ScreeningResultLevel = 'low' | 'moderate' | 'high' | 'severe';

export interface SleepScreeningResultRange {
  id: string;
  level: ScreeningResultLevel;
  min_score: number;
  max_score: number;
  title: string;
  description: string;
  recommendation: string;
  color: string;
}

export interface SleepScreeningTest {
  id: string;
  slug: string;
  title: string;
  description: string;
  instructions?: string;
  icon: string;
  duration_minutes: number;
  question_count?: number;
  order: number;
  questions?: SleepScreeningQuestion[];
  result_ranges?: SleepScreeningResultRange[];
}
