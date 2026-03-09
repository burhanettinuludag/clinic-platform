import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import type {
  ChatSession, ChatSessionDetail, AskQuestionResponse,
  Conversation, ConversationDetail, DirectMessage,
  DoctorForChat, DoctorChatStats,
} from '@/lib/types/chat';

// ─── AI Chat Hooks ───

export function useChatSessions(module?: string) {
  return useQuery<ChatSession[]>({
    queryKey: ['chatSessions', module],
    queryFn: async () => {
      const params = module ? { module } : {};
      const { data } = await api.get('/chat/sessions/', { params });
      return data.results || data;
    },
  });
}

export function useChatMessages(sessionId: string | null) {
  return useQuery<ChatSessionDetail>({
    queryKey: ['chatMessages', sessionId],
    queryFn: async () => {
      const { data } = await api.get(`/chat/sessions/${sessionId}/`);
      return data;
    },
    enabled: !!sessionId,
  });
}

export function useCreateChatSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (module: string) => {
      const { data } = await api.post('/chat/sessions/', { module });
      return data as ChatSession;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatSessions'] });
    },
  });
}

export function useAskQuestion() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ sessionId, question }: { sessionId: string; question: string }) => {
      const { data } = await api.post(`/chat/sessions/${sessionId}/ask/`, { question });
      return data as AskQuestionResponse;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['chatMessages', variables.sessionId] });
      queryClient.invalidateQueries({ queryKey: ['chatSessions'] });
    },
  });
}

export function useDeleteChatSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (sessionId: string) => {
      await api.delete(`/chat/sessions/${sessionId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chatSessions'] });
    },
  });
}

// ─── Doctor List Hook ───

export function useDoctorsList(params?: { specialty?: string; search?: string }) {
  return useQuery<DoctorForChat[]>({
    queryKey: ['chatDoctors', params],
    queryFn: async () => {
      const { data } = await api.get('/chat/doctors/', { params });
      return data;
    },
  });
}

// ─── Patient Messaging Hooks ───

export function useConversations() {
  return useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: async () => {
      const { data } = await api.get('/chat/conversations/');
      return data.results || data;
    },
  });
}

export function useConversationDetail(conversationId: string | null) {
  return useQuery<ConversationDetail>({
    queryKey: ['conversationDetail', conversationId],
    queryFn: async () => {
      const { data } = await api.get(`/chat/conversations/${conversationId}/`);
      return data;
    },
    enabled: !!conversationId,
    refetchInterval: 15000,
  });
}

export function useStartConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { doctor_id: string; subject: string; initial_message: string }) => {
      const { data } = await api.post('/chat/conversations/', payload);
      return data as ConversationDetail;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ conversationId, content }: { conversationId: string; content: string }) => {
      const { data } = await api.post(`/chat/conversations/${conversationId}/send/`, { content });
      return data as DirectMessage;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversationDetail', variables.conversationId] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
}

export function useMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (conversationId: string) => {
      await api.post(`/chat/conversations/${conversationId}/mark-read/`);
    },
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: ['conversationDetail', conversationId] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
}

export function useCloseConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (conversationId: string) => {
      await api.post(`/chat/conversations/${conversationId}/close/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
}

// ─── Doctor Side Messaging Hooks ───

export function useDoctorConversations() {
  return useQuery<Conversation[]>({
    queryKey: ['doctorConversations'],
    queryFn: async () => {
      const { data } = await api.get('/chat/doctor/conversations/');
      return data.results || data;
    },
  });
}

export function useDoctorConversationDetail(conversationId: string | null) {
  return useQuery<ConversationDetail>({
    queryKey: ['doctorConversationDetail', conversationId],
    queryFn: async () => {
      const { data } = await api.get(`/chat/doctor/conversations/${conversationId}/`);
      return data;
    },
    enabled: !!conversationId,
    refetchInterval: 15000,
  });
}

export function useDoctorSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ conversationId, content }: { conversationId: string; content: string }) => {
      const { data } = await api.post(`/chat/doctor/conversations/${conversationId}/send/`, { content });
      return data as DirectMessage;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['doctorConversationDetail', variables.conversationId] });
      queryClient.invalidateQueries({ queryKey: ['doctorConversations'] });
      queryClient.invalidateQueries({ queryKey: ['doctorChatStats'] });
    },
  });
}

export function useDoctorMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (conversationId: string) => {
      await api.post(`/chat/doctor/conversations/${conversationId}/mark-read/`);
    },
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: ['doctorConversationDetail', conversationId] });
      queryClient.invalidateQueries({ queryKey: ['doctorConversations'] });
      queryClient.invalidateQueries({ queryKey: ['doctorChatStats'] });
    },
  });
}

export function useDoctorCloseConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (conversationId: string) => {
      await api.post(`/chat/doctor/conversations/${conversationId}/close/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['doctorConversations'] });
    },
  });
}

export function useDoctorChatStats() {
  return useQuery<DoctorChatStats>({
    queryKey: ['doctorChatStats'],
    queryFn: async () => {
      const { data } = await api.get('/chat/doctor/stats/');
      return data;
    },
  });
}
