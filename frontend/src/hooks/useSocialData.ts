'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// ==================== TYPES ====================

export interface SocialAccount {
  id: string;
  platform: string;
  platform_display: string;
  account_name: string;
  account_id: string;
  status: string;
  status_display: string;
  is_token_valid: boolean;
  token_expires_at: string | null;
  total_posts_published: number;
  followers_count: number;
  connected_by_name: string;
  last_used_at: string | null;
  created_at: string;
}

export interface SocialCampaignListItem {
  id: string;
  title: string;
  theme: string;
  status: string;
  status_display: string;
  platforms: string[];
  posts_per_platform: number;
  language: string;
  tone: string;
  target_audience: string;
  week_start: string | null;
  post_stats: Record<string, number>;
  total_tokens: number;
  total_cost_usd: string;
  created_by_name: string;
  created_at: string;
}

export interface SocialCampaignDetail extends SocialCampaignListItem {
  description: string;
  content_output: Record<string, unknown>;
  schedule_output: Record<string, unknown>;
  posts: SocialPostListItem[];
  updated_at: string;
}

export interface SocialPostListItem {
  id: string;
  platform: string;
  platform_display: string;
  post_format: string;
  format_display: string;
  caption_tr: string;
  final_caption: string;
  hashtags: string[];
  image_urls: string[];
  status: string;
  status_display: string;
  scheduled_at: string | null;
  published_at: string | null;
  platform_url: string;
  publish_error: string;
  campaign: string | null;
  campaign_title: string;
  ai_generated: boolean;
  created_at: string;
}

export interface SocialPostDetail extends SocialPostListItem {
  caption_en: string;
  edited_caption: string;
  final_caption_with_hashtags: string;
  image_prompt: string;
  visual_brief: Record<string, unknown>;
  social_account: string | null;
  social_account_name: string;
  platform_post_id: string;
  editor_notes: string;
  tokens_used: number;
  publish_logs: PublishLog[];
  updated_at: string;
}

export interface PublishLog {
  id: string;
  action: string;
  success: boolean;
  response_data: Record<string, unknown>;
  error_message: string;
  created_at: string;
}

export interface CalendarPost {
  id: string;
  platform: string;
  platform_display: string;
  caption_tr: string;
  status: string;
  status_display: string;
  scheduled_at: string | null;
  published_at: string | null;
  post_format: string;
  campaign: string | null;
}

export interface DashboardStats {
  total_accounts: number;
  active_accounts: number;
  expired_accounts: number;
  total_campaigns: number;
  active_campaigns: number;
  total_posts: number;
  published_posts: number;
  scheduled_posts: number;
  failed_posts: number;
  posts_by_platform: Record<string, number>;
  total_tokens_used: number;
}

export interface CreateCampaignPayload {
  title?: string;
  theme: string;
  platforms: string[];
  posts_per_platform?: number;
  language?: string;
  tone?: string;
  target_audience?: string;
  week_start?: string;
}

// ==================== DASHBOARD ====================

export function useSocialDashboard() {
  return useQuery<DashboardStats>({
    queryKey: ['social-dashboard'],
    queryFn: async () => {
      const { data } = await api.get('/social/dashboard/');
      return data;
    },
  });
}

// ==================== ACCOUNTS ====================

export function useSocialAccounts() {
  return useQuery<SocialAccount[]>({
    queryKey: ['social-accounts'],
    queryFn: async () => {
      const { data } = await api.get('/social/accounts/');
      return data.results ?? data;
    },
  });
}

export function useCreateSocialAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<SocialAccount>) => {
      const { data } = await api.post('/social/accounts/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['social-accounts'] }),
  });
}

export function useValidateToken() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/social/accounts/${id}/validate/`);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['social-accounts'] }),
  });
}

// ==================== CAMPAIGNS ====================

export function useSocialCampaigns(params?: { status?: string; search?: string }) {
  return useQuery<SocialCampaignListItem[]>({
    queryKey: ['social-campaigns', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.status) searchParams.set('status', params.status);
      if (params?.search) searchParams.set('search', params.search);
      const qs = searchParams.toString();
      const { data } = await api.get(`/social/campaigns/${qs ? `?${qs}` : ''}`);
      return data.results ?? data;
    },
  });
}

export function useSocialCampaignDetail(id: string) {
  return useQuery<SocialCampaignDetail>({
    queryKey: ['social-campaign', id],
    queryFn: async () => {
      const { data } = await api.get(`/social/campaigns/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateSocialCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateCampaignPayload) => {
      const { data } = await api.post('/social/campaigns/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['social-campaigns'] }),
  });
}

export function useRegenerateSocialCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/social/campaigns/${id}/regenerate/`);
      return data;
    },
    onSuccess: (_d, id) => {
      qc.invalidateQueries({ queryKey: ['social-campaign', id] });
      qc.invalidateQueries({ queryKey: ['social-campaigns'] });
    },
  });
}

export function useApproveAllPosts() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/social/campaigns/${id}/approve-all/`);
      return data;
    },
    onSuccess: (_d, id) => {
      qc.invalidateQueries({ queryKey: ['social-campaign', id] });
      qc.invalidateQueries({ queryKey: ['social-campaigns'] });
    },
  });
}

// ==================== POSTS ====================

export function useSocialPosts(params?: { campaign?: string; platform?: string; status?: string; search?: string }) {
  return useQuery<SocialPostListItem[]>({
    queryKey: ['social-posts', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params?.campaign) searchParams.set('campaign', params.campaign);
      if (params?.platform) searchParams.set('platform', params.platform);
      if (params?.status) searchParams.set('status', params.status);
      if (params?.search) searchParams.set('search', params.search);
      const qs = searchParams.toString();
      const { data } = await api.get(`/social/posts/${qs ? `?${qs}` : ''}`);
      return data.results ?? data;
    },
  });
}

export function useSocialPostDetail(id: string) {
  return useQuery<SocialPostDetail>({
    queryKey: ['social-post', id],
    queryFn: async () => {
      const { data } = await api.get(`/social/posts/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useApprovePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/social/posts/${id}/approve/`);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['social-posts'] });
      qc.invalidateQueries({ queryKey: ['social-campaigns'] });
    },
  });
}

export function useSchedulePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string; scheduled_at: string; social_account_id: string }) => {
      const { data } = await api.post(`/social/posts/${id}/schedule/`, payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['social-posts'] });
      qc.invalidateQueries({ queryKey: ['social-campaigns'] });
    },
  });
}

export function usePublishNow() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, social_account_id }: { id: string; social_account_id: string }) => {
      const { data } = await api.post(`/social/posts/${id}/publish-now/`, { social_account_id });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['social-posts'] });
      qc.invalidateQueries({ queryKey: ['social-dashboard'] });
    },
  });
}

export function useRetryPost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/social/posts/${id}/retry/`);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['social-posts'] }),
  });
}

export function useBulkPostAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { post_ids: string[]; action: string; scheduled_at?: string; social_account_id?: string }) => {
      const { data } = await api.post('/social/posts/bulk-action/', payload);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['social-posts'] });
      qc.invalidateQueries({ queryKey: ['social-campaigns'] });
    },
  });
}

// ==================== CALENDAR ====================

export function useSocialCalendar(month?: string, platform?: string) {
  return useQuery<{ year: number; month: number; posts: CalendarPost[] }>({
    queryKey: ['social-calendar', month, platform],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (month) searchParams.set('month', month);
      if (platform) searchParams.set('platform', platform);
      const qs = searchParams.toString();
      const { data } = await api.get(`/social/calendar/${qs ? `?${qs}` : ''}`);
      return data;
    },
  });
}
