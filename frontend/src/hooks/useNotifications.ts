'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface Notification {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  read_at: string | null;
  action_url: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export function useUnreadCount() {
  return useQuery<{ unread_count: number }>({
    queryKey: ['notifications-unread'],
    queryFn: async () => { const { data } = await api.get('/notifications/unread-count/'); return data; },
    refetchInterval: 30000,
  });
}

export function useNotifications(limit = 10) {
  return useQuery<Notification[]>({
    queryKey: ['notifications', limit],
    queryFn: async () => { const { data } = await api.get('/notifications/', { params: { page_size: limit } }); return data.results || data; },
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => { const { data } = await api.post('/notifications/' + id + '/read/'); return data; },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['notifications'] }); qc.invalidateQueries({ queryKey: ['notifications-unread'] }); },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () => { const { data } = await api.post('/notifications/read-all/'); return data; },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['notifications'] }); qc.invalidateQueries({ queryKey: ['notifications-unread'] }); },
  });
}
