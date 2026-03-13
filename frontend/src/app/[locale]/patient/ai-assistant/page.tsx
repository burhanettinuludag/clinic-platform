'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Bot, Plus, MessageCircle, Trash2, Brain, Zap, Sparkles, Activity } from 'lucide-react';
import ChatBubble from '@/components/chat/ChatBubble';
import ChatInput from '@/components/chat/ChatInput';
import MessageList from '@/components/chat/MessageList';
import DisclaimerBanner from '@/components/chat/DisclaimerBanner';
import {
  useChatSessions,
  useChatMessages,
  useCreateChatSession,
  useAskQuestion,
  useDeleteChatSession,
} from '@/hooks/useChatData';
import type { ChatSession } from '@/lib/types/chat';

const MODULE_OPTIONS = [
  { value: 'general', label: 'Genel Saglik', icon: Activity, color: 'text-blue-600 bg-blue-50' },
  { value: 'migraine', label: 'Migren', icon: Brain, color: 'text-red-600 bg-red-50' },
  { value: 'epilepsy', label: 'Epilepsi', icon: Zap, color: 'text-amber-600 bg-amber-50' },
  { value: 'dementia', label: 'Demans', icon: Sparkles, color: 'text-purple-600 bg-purple-50' },
];

export default function AIAssistantPage() {
  const t = useTranslations('chat');
  const [selectedModule, setSelectedModule] = useState<string>('general');
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const { data: sessions = [], isLoading: sessionsLoading } = useChatSessions(selectedModule);
  const { data: sessionDetail } = useChatMessages(activeSessionId);
  const createSession = useCreateChatSession();
  const askQuestion = useAskQuestion();
  const deleteSession = useDeleteChatSession();

  const handleNewSession = async () => {
    try {
      const newSession = await createSession.mutateAsync(selectedModule);
      setActiveSessionId(newSession.id);
    } catch { /* handled by React Query */ }
  };

  const handleAskQuestion = async (question: string) => {
    if (!activeSessionId) {
      // Otomatik oturum olustur
      try {
        const newSession = await createSession.mutateAsync(selectedModule);
        setActiveSessionId(newSession.id);
        await askQuestion.mutateAsync({ sessionId: newSession.id, question });
      } catch { /* handled */ }
      return;
    }
    try {
      await askQuestion.mutateAsync({ sessionId: activeSessionId, question });
    } catch { /* handled */ }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await deleteSession.mutateAsync(sessionId);
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
      }
    } catch { /* handled */ }
  };

  const messages = sessionDetail?.messages || [];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
          <Bot className="w-5 h-5 text-purple-600" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {(() => { try { return t('aiTitle'); } catch { return 'AI Saglik Asistani'; } })()}
          </h1>
          <p className="text-sm text-gray-500">
            {(() => { try { return t('aiSubtitle'); } catch { return 'Sagliginizla ilgili sorular sorun'; } })()}
          </p>
        </div>
      </div>

      <DisclaimerBanner />

      {/* Module Selector */}
      <div className="flex gap-2 mt-4 mb-6 overflow-x-auto pb-1">
        {MODULE_OPTIONS.map((mod) => {
          const Icon = mod.icon;
          const isActive = selectedModule === mod.value;
          return (
            <button
              key={mod.value}
              onClick={() => { setSelectedModule(mod.value); setActiveSessionId(null); }}
              className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {mod.label}
            </button>
          );
        })}
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Session List */}
        <div className="md:col-span-1 bg-white rounded-xl border border-gray-200">
          <div className="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-800 text-sm">Sohbetler</h3>
            <button
              onClick={handleNewSession}
              disabled={createSession.isPending}
              className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="max-h-[500px] overflow-y-auto">
            {sessionsLoading ? (
              <div className="p-4 text-center text-gray-400 text-sm">Yukleniyor...</div>
            ) : sessions.length === 0 ? (
              <div className="p-6 text-center">
                <MessageCircle className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-400">Henuz sohbet yok</p>
                <p className="text-xs text-gray-300 mt-1">Soru sorarak baslayabilirsiniz</p>
              </div>
            ) : (
              sessions.map((session: ChatSession) => (
                <div
                  key={session.id}
                  className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition border-b border-gray-50 ${
                    activeSessionId === session.id
                      ? 'bg-blue-50 border-l-2 border-l-blue-500'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div
                    className="flex-1 min-w-0"
                    onClick={() => setActiveSessionId(session.id)}
                  >
                    <div className="text-sm font-medium text-gray-800 truncate">
                      {session.title || 'Yeni Sohbet'}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      {session.message_count} mesaj
                    </div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDeleteSession(session.id); }}
                    className="p-1 rounded text-gray-300 hover:text-red-500 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="md:col-span-2 bg-white rounded-xl border border-gray-200 flex flex-col h-[600px]">
          {activeSessionId ? (
            <>
              <MessageList
                isEmpty={messages.length === 0}
                isLoading={askQuestion.isPending}
                emptyMessage="Ilk sorunuzu sorun!"
              >
                {messages.map((msg) => (
                  <ChatBubble
                    key={msg.id}
                    role={msg.role}
                    content={msg.content}
                    timestamp={msg.created_at}
                    confidence={msg.role === 'assistant' ? msg.confidence : undefined}
                  />
                ))}
              </MessageList>
              <DisclaimerBanner variant="compact" />
              <ChatInput
                onSend={handleAskQuestion}
                isLoading={askQuestion.isPending}
                placeholder="Sağlığınızla ilgili sorunuzu yazın..."
              />
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <Bot className="w-16 h-16 text-gray-200 mb-4" />
              <p className="text-lg font-medium text-gray-500">Sorularınızı Sorun</p>
              <p className="text-sm text-gray-400 mt-1 text-center max-w-sm">
                Sol panelden bir sohbet seçin veya aşağıdaki alandan doğrudan soru sorun
              </p>
              <div className="mt-6 w-full max-w-md px-4">
                <ChatInput
                  onSend={handleAskQuestion}
                  isLoading={askQuestion.isPending || createSession.isPending}
                  placeholder="Soru sorarak baslayabilirsiniz..."
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
