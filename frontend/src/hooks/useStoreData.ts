'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type { Product, ProductCategory, Order, License } from '@/lib/types/store';
import type { Article, ContentCategory, EducationItem, Notification } from '@/lib/types/content';

// ==================== STORE ====================

export function useProducts(params?: { category?: string; product_type?: string }) {
  return useQuery<Product[]>({
    queryKey: ['products', params],
    queryFn: async () => {
      const { data } = await api.get('/store/products/', { params });
      return data;
    },
  });
}

export function useProduct(slug: string) {
  return useQuery<Product>({
    queryKey: ['products', slug],
    queryFn: async () => {
      const { data } = await api.get(`/store/products/${slug}/`);
      return data;
    },
    enabled: !!slug,
  });
}

export function useFeaturedProducts() {
  return useQuery<Product[]>({
    queryKey: ['products', 'featured'],
    queryFn: async () => {
      const { data } = await api.get('/store/products/featured/');
      return data;
    },
  });
}

export function useProductCategories() {
  return useQuery<ProductCategory[]>({
    queryKey: ['product-categories'],
    queryFn: async () => {
      const { data } = await api.get('/store/categories/');
      return data;
    },
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (orderData: {
      items: { product_id: string; license_type: string; quantity?: number }[];
      billing_name: string;
      billing_address: string;
      billing_city: string;
      billing_zip_code?: string;
    }) => {
      const { data } = await api.post('/store/orders/', orderData);
      return data as Order;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
}

export function useOrders() {
  return useQuery<Order[]>({
    queryKey: ['orders'],
    queryFn: async () => {
      const { data } = await api.get('/store/orders/');
      return data;
    },
  });
}

export function useLicenses() {
  return useQuery<License[]>({
    queryKey: ['licenses'],
    queryFn: async () => {
      const { data } = await api.get('/store/licenses/');
      return data;
    },
  });
}

// ==================== CONTENT ====================

export function useArticles(params?: { category?: string; is_featured?: boolean }) {
  return useQuery<Article[]>({
    queryKey: ['articles', params],
    queryFn: async () => {
      const { data } = await api.get('/content/articles/', { params });
      return data;
    },
  });
}

export function useArticle(slug: string) {
  return useQuery<Article>({
    queryKey: ['articles', slug],
    queryFn: async () => {
      const { data } = await api.get(`/content/articles/${slug}/`);
      return data;
    },
    enabled: !!slug,
  });
}

export function useFeaturedArticles() {
  return useQuery<Article[]>({
    queryKey: ['articles', 'featured'],
    queryFn: async () => {
      const { data } = await api.get('/content/articles/featured/');
      return data;
    },
  });
}

export function useContentCategories() {
  return useQuery<ContentCategory[]>({
    queryKey: ['content-categories'],
    queryFn: async () => {
      const { data } = await api.get('/content/categories/');
      return data;
    },
  });
}

export function useEducationItems(params?: { disease_module?: string; content_type?: string }) {
  return useQuery<EducationItem[]>({
    queryKey: ['education-items', params],
    queryFn: async () => {
      const { data } = await api.get('/content/education/', { params });
      return data;
    },
  });
}

export function useEducationItem(slug: string) {
  return useQuery<EducationItem>({
    queryKey: ['education-items', slug],
    queryFn: async () => {
      const { data } = await api.get(`/content/education/${slug}/`);
      return data;
    },
    enabled: !!slug,
  });
}

// ==================== NOTIFICATIONS ====================

export function useNotifications() {
  return useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: async () => {
      const { data } = await api.get('/notifications/');
      return data;
    },
  });
}

export function useUnreadCount() {
  return useQuery<{ unread_count: number }>({
    queryKey: ['notifications', 'unread-count'],
    queryFn: async () => {
      const { data } = await api.get('/notifications/unread-count/');
      return data;
    },
    refetchInterval: 60000,
  });
}

export function useMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/notifications/${id}/read/`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.post('/notifications/read-all/');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}
