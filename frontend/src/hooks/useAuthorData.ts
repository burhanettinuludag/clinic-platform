'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface AuthorArticle {
  id: string; slug: string; title_tr: string; title_en: string; excerpt_tr: string;
  status: 'draft' | 'published' | 'archived'; is_featured: boolean;
  category: string | null; category_name: string | null;
  published_at: string | null; created_at: string; updated_at: string; review_count: number;
}

export interface AuthorNews {
  id: string; slug: string; title_tr: string; category: string; category_display: string;
  priority: string; priority_display: string; status: string; status_display: string;
  is_auto_generated: boolean; view_count: number; published_at: string | null;
  created_at: string; review_count: number;
}

export interface ArticleReview {
  id: string; review_type_display: string; reviewer_name: string;
  overall_score: number; decision: string; decision_display: string; created_at: string;
}

export interface AuthorStats {
  author: { name: string; level: number; level_display: string; total_articles: number;
    total_views: number; average_rating: number; can_auto_publish: boolean; is_verified: boolean; };
  articles: { total: number; by_status: Record<string, number> };
  news: { total: number; by_status: Record<string, number> };
  recent_reviews: ArticleReview[];
}

export interface TransitionResult { detail: string; status: string; article_id?: string; news_id?: string; auto_published?: boolean; }
export interface PipelineResult { success: boolean; pipeline: string; steps_completed: string[]; steps_failed: string[]; duration_ms: number; data: Record<string, any>; }

export function useAuthorStats() {
  return useQuery<AuthorStats>({ queryKey: ['author-stats'],
    queryFn: async () => { const { data } = await api.get('/doctor/author/stats/'); return data; },
  });
}

export function useAuthorArticles(params?: { status?: string; search?: string }) {
  return useQuery<AuthorArticle[]>({ queryKey: ['author-articles', params],
    queryFn: async () => { const { data } = await api.get('/doctor/author/articles/', { params }); return data; },
  });
}

export function useAuthorNews(params?: { status?: string; category?: string; search?: string }) {
  return useQuery<AuthorNews[]>({ queryKey: ['author-news', params],
    queryFn: async () => { const { data } = await api.get('/doctor/author/news/', { params }); return data; },
  });
}

export function useArticleTransition() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action, feedback }: { id: string; action: string; feedback?: string }) => {
      const { data } = await api.post('/doctor/author/articles/' + id + '/transition/', { action, feedback });
      return data as TransitionResult;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['author-articles'] }); qc.invalidateQueries({ queryKey: ['author-stats'] }); },
  });
}

export function useNewsTransition() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action, feedback }: { id: string; action: string; feedback?: string }) => {
      const { data } = await api.post('/doctor/author/news/' + id + '/transition/', { action, feedback });
      return data as TransitionResult;
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['author-news'] }); qc.invalidateQueries({ queryKey: ['author-stats'] }); },
  });
}

export function useDeleteArticle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => { await api.delete('/doctor/author/articles/' + id + '/'); },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['author-articles'] }),
  });
}

export function useArticlePipeline() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, pipeline }: { id: string; pipeline: string }) => {
      const { data } = await api.post('/doctor/author/articles/' + id + '/run-pipeline/', { pipeline });
      return data as PipelineResult;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['author-articles'] }),
  });
}
