'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// ==================== TYPES ====================

export interface DashboardStats {
  total_users: number;
  total_patients: number;
  total_doctors: number;
  new_users_today: number;
  new_users_this_week: number;
  total_articles: number;
  published_articles: number;
  pending_review: number;
  total_news: number;
  active_announcements: number;
  feature_flags_on: number;
  feature_flags_off: number;
}

export interface SiteConfig {
  id: string;
  key: string;
  label: string;
  value: string;
  value_type: 'string' | 'integer' | 'float' | 'boolean' | 'json';
  description: string;
  category: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface FeatureFlag {
  id: string;
  key: string;
  label: string;
  is_enabled: boolean;
  description: string;
  enabled_for_roles: string[];
  created_at: string;
  updated_at: string;
}

export interface Announcement {
  id: string;
  title_tr: string;
  title_en: string;
  message_tr: string;
  message_en: string;
  link_url: string;
  link_text_tr: string;
  link_text_en: string;
  bg_color: string;
  text_color: string;
  is_active: boolean;
  priority: number;
  starts_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface HomepageHero {
  id: string;
  title_tr: string;
  title_en: string;
  subtitle_tr: string;
  subtitle_en: string;
  cta_text_tr: string;
  cta_text_en: string;
  cta_url: string;
  secondary_cta_text_tr: string;
  secondary_cta_text_en: string;
  secondary_cta_url: string;
  background_image: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SocialLink {
  id: string;
  platform: string;
  platform_display: string;
  url: string;
  is_active: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

// ==================== DASHBOARD ====================

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['site-dashboard-stats'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/dashboard-stats/');
      return data;
    },
  });
}

// ==================== SITE CONFIG ====================

export function useSiteConfigs() {
  return useQuery<SiteConfig[]>({
    queryKey: ['site-configs'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/config/');
      return data;
    },
  });
}

export function useUpdateSiteConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string; value: string }) => {
      const { data } = await api.patch(`/site/admin/config/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-configs'] }),
  });
}

// ==================== FEATURE FLAGS ====================

export function useFeatureFlags() {
  return useQuery<FeatureFlag[]>({
    queryKey: ['site-feature-flags'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/feature-flags/');
      return data;
    },
  });
}

export function useToggleFeatureFlag() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, is_enabled }: { id: string; is_enabled: boolean }) => {
      const { data } = await api.patch(`/site/admin/feature-flags/${id}/`, { is_enabled });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-feature-flags'] }),
  });
}

// ==================== ANNOUNCEMENTS ====================

export function useAnnouncements() {
  return useQuery<Announcement[]>({
    queryKey: ['site-announcements'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/announcements/');
      return data;
    },
  });
}

export function useCreateAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<Announcement>) => {
      const { data } = await api.post('/site/admin/announcements/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-announcements'] }),
  });
}

export function useUpdateAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string } & Partial<Announcement>) => {
      const { data } = await api.patch(`/site/admin/announcements/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-announcements'] }),
  });
}

export function useDeleteAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/site/admin/announcements/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-announcements'] }),
  });
}

// ==================== HOMEPAGE HERO ====================

export function useHomepageHeroes() {
  return useQuery<HomepageHero[]>({
    queryKey: ['site-heroes'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/hero/');
      return data;
    },
  });
}

export function useUpdateHero() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string } & Partial<HomepageHero>) => {
      const { data } = await api.patch(`/site/admin/hero/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-heroes'] }),
  });
}

// ==================== SOCIAL LINKS ====================

export function useSocialLinks() {
  return useQuery<SocialLink[]>({
    queryKey: ['site-social-links'],
    queryFn: async () => {
      const { data } = await api.get('/site/admin/social-links/');
      return data;
    },
  });
}

export function useUpdateSocialLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string } & Partial<SocialLink>) => {
      const { data } = await api.patch(`/site/admin/social-links/${id}/`, payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['site-social-links'] }),
  });
}
