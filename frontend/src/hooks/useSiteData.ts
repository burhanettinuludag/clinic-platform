'use client';

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useLocale } from 'next-intl';

const publicApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
});

// ==================== TYPES ====================

export interface PublicSiteConfig {
  key: string;
  label: string;
  value: string;
  typed_value: string | number | boolean | object;
  value_type: string;
  category: string;
}

export interface ActiveAnnouncement {
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
  priority: number;
}

export interface ActiveHero {
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
}

export interface PublicSocialLink {
  platform: string;
  platform_display: string;
  url: string;
  order: number;
}

export interface PublicFeatureFlag {
  key: string;
  label: string;
  is_enabled: boolean;
}

// ==================== HOOKS ====================

export function usePublicSiteConfigs() {
  return useQuery<PublicSiteConfig[]>({
    queryKey: ['public-site-configs'],
    queryFn: async () => {
      const { data } = await publicApi.get('/site/config/public/');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 min cache
  });
}

export function useSiteConfig(key: string): string | undefined {
  const { data } = usePublicSiteConfigs();
  return data?.find(c => c.key === key)?.value;
}

export function useActiveAnnouncements() {
  return useQuery<ActiveAnnouncement[]>({
    queryKey: ['public-announcements'],
    queryFn: async () => {
      const { data } = await publicApi.get('/site/announcements/active/');
      return data;
    },
    staleTime: 2 * 60 * 1000, // 2 min cache
  });
}

export function useActiveHero() {
  return useQuery<ActiveHero | null>({
    queryKey: ['public-hero'],
    queryFn: async () => {
      const { data } = await publicApi.get('/site/hero/active/');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function usePublicSocialLinks() {
  return useQuery<PublicSocialLink[]>({
    queryKey: ['public-social-links'],
    queryFn: async () => {
      const { data } = await publicApi.get('/site/social-links/');
      return data;
    },
    staleTime: 10 * 60 * 1000, // 10 min cache
  });
}

export function usePublicFeatureFlags() {
  return useQuery<PublicFeatureFlag[]>({
    queryKey: ['public-feature-flags'],
    queryFn: async () => {
      const { data } = await publicApi.get('/site/feature-flags/');
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useFeatureFlag(key: string): boolean {
  const { data } = usePublicFeatureFlags();
  return data?.find(f => f.key === key)?.is_enabled ?? false;
}

// ==================== LOCALE HELPERS ====================

export function useLocalizedField<T extends Record<string, unknown>>(
  item: T | null | undefined,
  field: string
): string {
  const locale = useLocale();
  if (!item) return '';
  const key = `${field}_${locale}` as keyof T;
  const fallbackKey = `${field}_tr` as keyof T;
  return (item[key] as string) || (item[fallbackKey] as string) || '';
}
