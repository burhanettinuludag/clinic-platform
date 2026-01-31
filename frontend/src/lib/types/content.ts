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
  category: string | null;
  order: number;
  estimated_duration_minutes: number;
  progress: {
    progress_percent: number;
    completed_at: string | null;
  } | null;
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
