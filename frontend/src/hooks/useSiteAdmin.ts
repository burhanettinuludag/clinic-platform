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

// ==================== BROKEN LINKS ====================

export interface BrokenLinkItem {
  id: string;
  broken_url: string;
  http_status: number | null;
  error_message: string;
  link_type: string;
  link_type_display: string;
  source_type: string;
  source_type_display: string;
  source_id: string;
  source_title: string;
  source_field: string;
  source_language: string;
  status: string;
  status_display: string;
  suggested_url: string;
  fix_notes: string;
  fixed_at: string | null;
  check_count: number;
  last_checked: string;
  created_at: string;
}

export interface BrokenLinkScanItem {
  id: string;
  status: string;
  status_display: string;
  total_links_checked: number;
  broken_links_found: number;
  auto_fixed_count: number;
  duration_seconds: number;
  error_message: string;
  details: Record<string, number>;
  created_at: string;
}

export interface BrokenLinkStats {
  total: number;
  detected: number;
  auto_fixed: number;
  manually_fixed: number;
  ai_suggested: number;
  ignored: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  last_scan: BrokenLinkScanItem | null;
}

export function useBrokenLinks(params?: { status?: string; link_type?: string; source_type?: string; search?: string }) {
  return useQuery<BrokenLinkItem[]>({
    queryKey: ['broken-links', params],
    queryFn: async () => {
      const { data } = await api.get('/doctor/broken-links/', { params });
      return data;
    },
  });
}

export function useBrokenLinkStats() {
  return useQuery<BrokenLinkStats>({
    queryKey: ['broken-links-stats'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/broken-links/stats/');
      return data;
    },
  });
}

export function useBrokenLinkScans() {
  return useQuery<BrokenLinkScanItem[]>({
    queryKey: ['broken-link-scans'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/broken-links/scans/');
      return data;
    },
  });
}

export function useTriggerScan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/doctor/broken-links/scan/');
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['broken-links'] });
      qc.invalidateQueries({ queryKey: ['broken-links-stats'] });
      qc.invalidateQueries({ queryKey: ['broken-link-scans'] });
    },
  });
}

export function useFixBrokenLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, new_url }: { id: string; new_url: string }) => {
      const { data } = await api.post(`/doctor/broken-links/${id}/fix/`, { new_url });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['broken-links'] });
      qc.invalidateQueries({ queryKey: ['broken-links-stats'] });
    },
  });
}

export function useRecheckBrokenLink() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/doctor/broken-links/${id}/recheck/`);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['broken-links'] });
      qc.invalidateQueries({ queryKey: ['broken-links-stats'] });
    },
  });
}

export function useBulkBrokenLinkAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { ids: string[]; action: 'ignore' | 'recheck' }) => {
      const { data } = await api.post('/doctor/broken-links/bulk/', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['broken-links'] });
      qc.invalidateQueries({ queryKey: ['broken-links-stats'] });
    },
  });
}

// ==================== AGENT MANAGEMENT ====================

export interface AgentLastRun {
  status: string | null;
  created_at: string | null;
  duration_ms: number | null;
  tokens_used: number | null;
}

export interface AgentItem {
  key: string;
  name_tr: string;
  name_en: string;
  description_tr: string;
  description_en: string;
  category: string;
  risk_level: 'low' | 'medium' | 'high';
  cooldown_minutes: number;
  cooldown_remaining_seconds: number;
  schedule_info: string;
  last_run: AgentLastRun | null;
}

export interface AgentListResponse {
  agents: AgentItem[];
  daily_triggers_used: number;
  daily_trigger_limit: number;
}

export interface AgentTriggerHistoryItem {
  id: string;
  task_key: string;
  task_name: string;
  user_email: string;
  ip_address: string;
  celery_task_id: string;
  created_at: string;
}

export interface AgentWeeklyStats {
  weekly: {
    total: number;
    completed: number;
    failed: number;
    running: number;
    total_tokens: number;
  };
  by_task: Array<{
    task_type: string;
    count: number;
    success: number;
    fail: number;
    tokens: number;
  }>;
}

export function useAgentList() {
  return useQuery<AgentListResponse>({
    queryKey: ['agents-list'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/agents/');
      return data;
    },
    refetchInterval: 30000, // Her 30 saniyede cooldown guncelle
  });
}

export function useTriggerAgent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (task_key: string) => {
      const { data } = await api.post('/doctor/agents/trigger/', { task_key });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['agents-list'] });
      qc.invalidateQueries({ queryKey: ['agents-history'] });
    },
  });
}

export function useAgentTriggerHistory() {
  return useQuery<{ history: AgentTriggerHistoryItem[] }>({
    queryKey: ['agents-history'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/agents/history/');
      return data;
    },
  });
}

export function useAgentStats() {
  return useQuery<AgentWeeklyStats>({
    queryKey: ['agents-stats'],
    queryFn: async () => {
      const { data } = await api.get('/doctor/agents/stats/');
      return data;
    },
  });
}
