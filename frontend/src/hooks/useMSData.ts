'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import type { MSCategory, MSArticle, MSTip, MSFAQ } from '@/lib/types/ms';

export function useMSCategories() {
  return useQuery<MSCategory[]>({
    queryKey: ['ms', 'categories'],
    queryFn: async () => {
      const { data } = await api.get('/ms/categories/');
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useMSArticles(params?: {
  article_type?: string;
  category__slug?: string;
  is_featured?: boolean;
  search?: string;
}) {
  return useQuery<MSArticle[]>({
    queryKey: ['ms', 'articles', params],
    queryFn: async () => {
      const { data } = await api.get('/ms/articles/', { params });
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useMSArticle(slug: string) {
  return useQuery<MSArticle>({
    queryKey: ['ms', 'article', slug],
    queryFn: async () => {
      const { data } = await api.get(`/ms/articles/${slug}/`);
      return data;
    },
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFeaturedMSArticles() {
  return useQuery<MSArticle[]>({
    queryKey: ['ms', 'articles', 'featured'],
    queryFn: async () => {
      const { data } = await api.get('/ms/articles/featured/');
      return data.results ?? data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useMSTips() {
  return useQuery<MSTip[]>({
    queryKey: ['ms', 'tips'],
    queryFn: async () => {
      const { data } = await api.get('/ms/tips/');
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useMSFAQs(categorySlug?: string) {
  return useQuery<MSFAQ[]>({
    queryKey: ['ms', 'faqs', categorySlug],
    queryFn: async () => {
      const params = categorySlug ? { category__slug: categorySlug } : {};
      const { data } = await api.get('/ms/faqs/', { params });
      return data.results ?? data;
    },
    staleTime: 10 * 60 * 1000,
  });
}
