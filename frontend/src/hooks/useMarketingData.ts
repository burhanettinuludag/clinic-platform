'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

// ==================== TYPES ====================

export interface MarketingCampaignListItem {
  id: string;
  title: string;
  theme: string;
  week_start: string;
  status: string;
  status_display: string;
  platforms: string[];
  language: string;
  total_tokens: number;
  total_cost_usd: string;
  created_at: string;
  updated_at: string;
}

export interface MarketingCampaignDetail {
  id: string;
  title: string;
  theme: string;
  week_start: string;
  status: string;
  status_display: string;
  platforms: string[];
  language: string;
  tone: string;
  target_audience: string;
  content_output: Record<string, unknown>;
  visual_briefs: Record<string, unknown>;
  schedule: Record<string, unknown>;
  edited_content: Record<string, unknown>;
  editor_notes: string;
  created_by_email: string;
  approved_at: string | null;
  total_tokens: number;
  total_cost_usd: string;
  pipeline_task_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateCampaignPayload {
  theme: string;
  week_start: string;
  platforms?: string[];
  language?: string;
  tone?: string;
  target_audience?: string;
}

export interface UpdateCampaignPayload {
  edited_content?: Record<string, unknown>;
  editor_notes?: string;
  status?: string;
}

// ==================== LIST & CREATE ====================

export function useMarketingCampaigns(params?: { status?: string }) {
  return useQuery<MarketingCampaignListItem[]>({
    queryKey: ['marketing-campaigns', params?.status],
    queryFn: async () => {
      const queryParams = params?.status ? `?status=${params.status}` : '';
      const { data } = await api.get(`/doctor/marketing/${queryParams}`);
      return data;
    },
  });
}

export function useCreateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateCampaignPayload) => {
      const { data } = await api.post('/doctor/marketing/', payload);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['marketing-campaigns'] }),
  });
}

// ==================== DETAIL & UPDATE ====================

export function useMarketingCampaignDetail(id: string) {
  return useQuery<MarketingCampaignDetail>({
    queryKey: ['marketing-campaign', id],
    queryFn: async () => {
      const { data } = await api.get(`/doctor/marketing/${id}/`);
      return data;
    },
    enabled: !!id,
  });
}

export function useUpdateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...payload }: { id: string } & UpdateCampaignPayload) => {
      const { data } = await api.patch(`/doctor/marketing/${id}/`, payload);
      return data;
    },
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ['marketing-campaign', variables.id] });
      qc.invalidateQueries({ queryKey: ['marketing-campaigns'] });
    },
  });
}

// ==================== APPROVE & REGENERATE ====================

export function useApproveCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/doctor/marketing/${id}/approve/`);
      return data;
    },
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['marketing-campaign', id] });
      qc.invalidateQueries({ queryKey: ['marketing-campaigns'] });
    },
  });
}

export function useRegenerateCampaign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await api.post(`/doctor/marketing/${id}/regenerate/`);
      return data;
    },
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['marketing-campaign', id] });
      qc.invalidateQueries({ queryKey: ['marketing-campaigns'] });
    },
  });
}
