'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { MessageSquare, User, Clock, Inbox } from 'lucide-react';
import ChatBubble from '@/components/chat/ChatBubble';
import ChatInput from '@/components/chat/ChatInput';
import MessageList from '@/components/chat/MessageList';
import {
  useDoctorConversations,
  useDoctorConversationDetail,
  useDoctorSendMessage,
  useDoctorMarkRead,
  useDoctorCloseConversation,
  useDoctorChatStats,
} from '@/hooks/useChatData';
import type { Conversation } from '@/lib/types/chat';

export default function DoctorMessagesPage() {
  const t = useTranslations('messages');
  const [activeConvId, setActiveConvId] = useState<string | null>(null);

  const { data: conversations = [], isLoading } = useDoctorConversations();
  const { data: convDetail } = useDoctorConversationDetail(activeConvId);
  const { data: stats } = useDoctorChatStats();
  const sendMessage = useDoctorSendMessage();
  const markReadMutation = useDoctorMarkRead();
  const closeConversation = useDoctorCloseConversation();

  // Okundu isaretle
  useEffect(() => {
    if (activeConvId && convDetail && convDetail.doctor_unread_count > 0) {
      markReadMutation.mutate(activeConvId);
    }
  }, [activeConvId, convDetail?.doctor_unread_count]);

  const handleSend = async (content: string) => {
    if (!activeConvId) return;
    try {
      await sendMessage.mutateAsync({ conversationId: activeConvId, content });
    } catch { /* handled */ }
  };

  const handleClose = async () => {
    if (!activeConvId) return;
    if (confirm('Bu konuşmayı kapatmak istediğinize emin misiniz?')) {
      await closeConversation.mutateAsync(activeConvId);
      setActiveConvId(null);
    }
  };

  const messages = convDetail?.messages || [];

  return (
    <div className="p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {(() => { try { return t('doctorTitle'); } catch { return 'Hasta Mesajları'; } })()}
            </h1>
            <p className="text-sm text-gray-500">Hastalarınızla iletişim kurun</p>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="hidden md:flex items-center gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">{stats.active_conversations}</div>
              <div className="text-xs text-gray-400">Aktif</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-red-500">{stats.total_unread}</div>
              <div className="text-xs text-gray-400">Okunmamış</div>
            </div>
          </div>
        )}
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Conversation List */}
        <div className="md:col-span-1 bg-white rounded-xl border border-gray-200">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-800 text-sm">Konuşmalar</h3>
          </div>
          <div className="max-h-[540px] overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-400 text-sm">Yükleniyor...</div>
            ) : conversations.length === 0 ? (
              <div className="p-6 text-center">
                <Inbox className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-400">Henüz mesaj yok</p>
                <p className="text-xs text-gray-300 mt-1">Hastalar size mesaj gönderdiğinde burada görünecek</p>
              </div>
            ) : (
              conversations.map((conv: Conversation) => (
                <div
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`px-4 py-3 cursor-pointer transition border-b border-gray-50 ${
                    activeConvId === conv.id
                      ? 'bg-blue-50 border-l-2 border-l-blue-500'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-800 truncate">
                          {conv.patient_name}
                        </span>
                        {conv.doctor_unread_count > 0 && (
                          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
                            {conv.doctor_unread_count}
                          </span>
                        )}
                      </div>
                      {conv.subject && (
                        <div className="text-xs text-gray-500 truncate">{conv.subject}</div>
                      )}
                      {conv.last_message && (
                        <div className="text-xs text-gray-400 truncate mt-0.5">
                          {conv.last_message.content}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                      conv.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
                    }`}>
                      {conv.status === 'active' ? 'Aktif' : 'Kapalı'}
                    </span>
                    {conv.last_message_at && (
                      <span className="text-[10px] text-gray-400 flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        {new Date(conv.last_message_at).toLocaleDateString('tr-TR')}
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="md:col-span-2 bg-white rounded-xl border border-gray-200 flex flex-col h-[600px]">
          {activeConvId && convDetail ? (
            <>
              {/* Chat Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <div>
                  <div className="font-semibold text-gray-800">{convDetail.patient_name}</div>
                  {convDetail.subject && (
                    <div className="text-xs text-gray-500">{convDetail.subject}</div>
                  )}
                </div>
                {convDetail.status === 'active' && (
                  <button
                    onClick={handleClose}
                    className="text-xs text-gray-400 hover:text-red-500 transition"
                  >
                    Konuşmayı Kapat
                  </button>
                )}
              </div>

              <MessageList isEmpty={messages.length === 0}>
                {messages.map((msg) => (
                  <ChatBubble
                    key={msg.id}
                    role={msg.sender_role === 'doctor' ? 'user' : 'patient'}
                    content={msg.content}
                    senderName={msg.sender_name}
                    timestamp={msg.created_at}
                    isRead={msg.is_read}
                  />
                ))}
              </MessageList>

              {convDetail.status === 'active' ? (
                <ChatInput
                  onSend={handleSend}
                  isLoading={sendMessage.isPending}
                  placeholder="Hastanıza yanıt yazın..."
                />
              ) : (
                <div className="p-3 bg-gray-50 border-t text-center text-sm text-gray-400">
                  Bu konuşma kapatılmış.
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <Inbox className="w-16 h-16 text-gray-200 mb-4" />
              <p className="text-lg font-medium text-gray-500">Konuşma Seçin</p>
              <p className="text-sm text-gray-400 mt-1">
                Sol panelden bir konuşma seçerek mesajları görüntüleyebilirsiniz
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
