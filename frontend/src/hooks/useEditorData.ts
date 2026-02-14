'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface ReviewQueueStats { total_pending: number; articles_pending: number; news_pending: number; approved_unpublished: number; }

export interface EditorArticle {
  id: string; slug: string; title_tr: string; title_en: string; excerpt_tr: string; status: string;
  author_name: string; category_name: string | null; published_at: string | null;
  created_at: string; updated_at: string; review_count: number;
}

export interface EditorNews {
  id: string; slug: string; title_tr: string; category: string; category_display: string;
  priority: string; priority_display: string; status: string; status_display: string;
  author_name: string; view_count: number; published_at: string | null; created_at: string; review_count: number;
}

export interface EditorAuthor {
  id: string; full_name: string; email: string; primary_specialty: string; specialty_display: string;
  author_level: number; level_display: string; total_articles: number; is_verified: boolean;
  verified_at: string | null; is_active: boolean;
}

export interface ReviewInput {
  medical_accuracy_score: number; language_quality_score: number; seo_score: number;
  style_compliance_score: number; ethics_score: number; decision: string; feedback: string;
}

export interface TransitionResult { detail: string; status: string; }

export function useReviewQueueStats() {
  return useQuery<ReviewQueueStats>({ queryKey: ['editor-review-stats'],
    queryFn: async () => { const { data } = await api.get('/doctor/editor/review-queue/stats/'); return data; },
  });
}

export function useEditorArticles(params?: { status?: string; search?: string }) {
  return useQuery<EditorArticle[]>({ queryKey: ['editor-articles', params],
    queryFn: async () => { const { data } = await api.get('/doctor/editor/articles/', { params }); return data; },
  });
}

export function useEditorNews(params?: { status?: string; search?: string }) {
  return useQuery<EditorNews[]>({ queryKey: ['editor-news', params],
    queryFn: async () => { const { data } = await api.get('/doctor/editor/news/', { params }); return data; },
  });
}

export function useEditorArticleTransition() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action, feedback }: { id: string; action: string; feedback?: string }) => {
      const { data } = await api.post('/doctor/editor/articles/' + id + '/transition/', { action, feedback });
      return data as TransitionResult;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['editor-articles'] });
      qc.invalidateQueries({ queryKey: ['editor-review-stats'] });
    },
  });
}

export function useEditorNewsTransition() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action, feedback }: { id: string; action: string; feedback?: string }) => {
      const { data } = await api.post('/doctor/editor/news/' + id + '/transition/', { action, feedback });
      return data as TransitionResult;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['editor-news'] });
      qc.invalidateQueries({ queryKey: ['editor-review-stats'] });
    },
  });
}

export function useEditorAuthors() {
  return useQuery<EditorAuthor[]>({ queryKey: ['editor-authors'],
    queryFn: async () => { const { data } = await api.get('/doctor/editor/authors/'); return data; },
  });
}

export function useVerifyAuthor() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, is_verified, author_level }: { id: string; is_verified?: boolean; author_level?: number }) => {
      const { data } = await api.post('/doctor/editor/authors/' + id + '/verify/', { is_verified, author_level });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['editor-authors'] }),
  });
}
