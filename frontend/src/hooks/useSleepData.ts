'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import type { SleepCategory, SleepArticle, SleepTip, SleepFAQ, SleepScreeningTest } from '@/lib/types/sleep';

export function useSleepCategories() {
  return useQuery<SleepCategory[]>({
    queryKey: ['sleep', 'categories'],
    queryFn: async () => {
      const { data } = await api.get('/sleep/categories/');
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSleepArticles(params?: {
  article_type?: string;
  category__slug?: string;
  related_disease?: string;
  is_featured?: boolean;
  search?: string;
}) {
  return useQuery<SleepArticle[]>({
    queryKey: ['sleep', 'articles', params],
    queryFn: async () => {
      const { data } = await api.get('/sleep/articles/', { params });
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSleepArticle(slug: string) {
  return useQuery<SleepArticle>({
    queryKey: ['sleep', 'article', slug],
    queryFn: async () => {
      const { data } = await api.get(`/sleep/articles/${slug}/`);
      return data;
    },
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFeaturedSleepArticles() {
  return useQuery<SleepArticle[]>({
    queryKey: ['sleep', 'articles', 'featured'],
    queryFn: async () => {
      const { data } = await api.get('/sleep/articles/featured/');
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSleepArticlesByDisease(disease: string) {
  return useQuery<SleepArticle[]>({
    queryKey: ['sleep', 'articles', 'disease', disease],
    queryFn: async () => {
      const { data } = await api.get(`/sleep/articles/by-disease/${disease}/`);
      return data.results ?? data;
    },
    enabled: !!disease,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSleepTips() {
  return useQuery<SleepTip[]>({
    queryKey: ['sleep', 'tips'],
    queryFn: async () => {
      const { data } = await api.get('/sleep/tips/');
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useSleepFAQs(categorySlug?: string) {
  return useQuery<SleepFAQ[]>({
    queryKey: ['sleep', 'faqs', categorySlug],
    queryFn: async () => {
      const params = categorySlug ? { category__slug: categorySlug } : {};
      const { data } = await api.get('/sleep/faqs/', { params });
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

// ── Screening Tests ───────────────────────────────────────────────────

export function useSleepScreeningTests() {
  return useQuery<SleepScreeningTest[]>({
    queryKey: ['sleep', 'tests'],
    queryFn: async () => {
      const { data } = await api.get('/sleep/tests/');
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useSleepScreeningTest(slug: string) {
  return useQuery<SleepScreeningTest>({
    queryKey: ['sleep', 'test', slug],
    queryFn: async () => {
      const { data } = await api.get(`/sleep/tests/${slug}/`);
      return data;
    },
    enabled: !!slug,
    staleTime: 10 * 60 * 1000,
  });
}
