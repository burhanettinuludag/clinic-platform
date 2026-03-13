export interface ContentCategory {
  id: string;
  slug: string;
  name: string;
  name_tr: string;
  name_en: string;
  parent: string | null;
  order: number;
  children: ContentCategory[];
}

export interface Article {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  body?: string;
  featured_image: string;
  category: string | null;
  category_name: string | null;
  author_name: string | null;
  is_featured: boolean;
  published_at: string;
  seo_title?: string;
  seo_description?: string;
}

export interface EducationItem {
  id: string;
  slug: string;
  title: string;
  body: string;
  content_type: 'video' | 'text' | 'infographic' | 'interactive';
  video_url: string;
  image: string;
  disease_module: string | null;
  disease_module_slug: string | null;
  category: string | null;
  category_slug: string | null;
  category_name: string | null;
  order: number;
  estimated_duration_minutes: number;
  progress: {
    id: string;
    progress_percent: number;
    completed_at: string | null;
  } | null;
}

export interface QuizOption {
  text: string;
  is_correct?: boolean;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
  explanation: string;
  order: number;
}

export interface QuizBestAttempt {
  score: number;
  total_questions: number;
  passed: boolean;
  completed_at: string;
}

export interface EducationQuiz {
  id: string;
  slug: string;
  title: string;
  description: string;
  disease_module: string | null;
  category: string | null;
  category_slug: string | null;
  passing_score_percent: number;
  points_reward: number;
  question_count: number;
  questions: QuizQuestion[];
  best_attempt: QuizBestAttempt | null;
  order: number;
}

export interface EducationQuizListItem {
  id: string;
  slug: string;
  title: string;
  description: string;
  disease_module: string | null;
  category: string | null;
  category_slug: string | null;
  passing_score_percent: number;
  points_reward: number;
  question_count: number;
  best_attempt: QuizBestAttempt | null;
  order: number;
}

export interface QuizAttemptAnswer {
  question_id: string;
  selected_option_index: number;
  is_correct?: boolean;
}

export interface QuizAttempt {
  id: string;
  quiz: string;
  score: number;
  total_questions: number;
  passed: boolean;
  duration_seconds: number | null;
  answers: QuizAttemptAnswer[];
  completed_at: string;
  created_at: string;
}

// ==================== NEWS ====================

export type NewsCategory =
  | 'fda_approval' | 'ema_approval' | 'turkey_approval'
  | 'clinical_trial' | 'new_device' | 'congress'
  | 'turkey_news' | 'popular_science' | 'drug_update' | 'guideline_update';

export type NewsPriority = 'urgent' | 'high' | 'medium' | 'low';

export interface NewsArticle {
  id: string;
  slug: string;
  title_tr: string;
  title_en: string;
  excerpt_tr: string;
  excerpt_en: string;
  body_tr?: string;
  body_en?: string;
  category: NewsCategory;
  category_display: string;
  priority: NewsPriority;
  priority_display?: string;
  featured_image: string | null;
  featured_image_alt: string;
  author_name: string | null;
  author_profile?: {
    specialty: string;
    institution: string;
    department: string;
    bio: string;
    is_verified: boolean;
    orcid_id: string;
    profile_photo: string | null;
  } | null;
  related_diseases: string[]; // ['migraine', 'epilepsy', ...]
  source_urls?: string[];
  original_source?: string;
  meta_title?: string;
  meta_description?: string;
  keywords?: string;
  published_at: string;
  updated_at?: string;
  view_count: number;
}

export interface Notification {
  id: string;
  notification_type: 'reminder' | 'alert' | 'info' | 'system';
  title: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  action_url: string;
  metadata: Record<string, unknown>;
  created_at: string;
}
