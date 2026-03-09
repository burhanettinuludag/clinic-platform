'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { MessageSquare, Plus, User, Clock } from 'lucide-react';
import ChatBubble from '@/components/chat/ChatBubble';
import ChatInput from '@/components/chat/ChatInput';
import MessageList from '@/components/chat/MessageList';
import {
  useConversations,
  useConversationDetail,
  useSendMessage,
  useMarkRead,
  useCloseConversation,
} from '@/hooks/useChatData';
import type { Conversation } from '@/lib/types/chat';

export default function PatientMessagesPage() {
  const t = useTranslations('messages');
  const [activeConvId, setActiveConvId] = useState<string | null>(null);

  const { data: conversations = [], isLoading } = useConversations();
  const { data: convDetail } = useConversationDetail(activeConvId);
  const sendMessage = useSendMessage();
  const markRead = useMarkRead();
  const closeConversation = useCloseConversation();

  // Okundu isaretle
  useEffect(() => {
    if (activeConvId && convDetail && convDetail.patient_unread_count > 0) {
      markRead.mutate(activeConvId);
    }
  }, [activeConvId, convDetail?.patient_unread_count]);

  const handleSend = async (content: string) => {
    if (!activeConvId) return;
    try {
      await sendMessage.mutateAsync({ conversationId: activeConvId, content });
    } catch { /* handled */ }
  };

  const handleClose = async () => {
    if (!activeConvId) return;
    if (confirm('Bu konusmayi kapatmak istediginize emin misiniz?')) {
      await closeConversation.mutateAsync(activeConvId);
      setActiveConvId(null);
    }
  };

  const messages = convDetail?.messages || [];
  const activeConv = conversations.find((c: Conversation) => c.id === activeConvId);

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-teal-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {(() => { try { return t('title'); } catch { return 'Mesajlar'; } })()}
            </h1>
            <p className="text-sm text-gray-500">
              {(() => { try { return t('subtitle'); } catch { return 'Doktorunuzla iletisim kurun'; } })()}
            </p>
          </div>
        </div>
        <Link
          href="/patient/messages/new"
          className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-medium hover:bg-teal-700 transition"
        >
          <Plus className="w-4 h-4" />
          Yeni Mesaj
        </Link>
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Conversation List */}
        <div className="md:col-span-1 bg-white rounded-xl border border-gray-200">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-800 text-sm">Konusmalar</h3>
          </div>
          <div className="max-h-[540px] overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-400 text-sm">Yukleniyor...</div>
            ) : conversations.length === 0 ? (
              <div className="p-6 text-center">
                <MessageSquare className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-400">Henuz konusma yok</p>
                <Link
                  href="/patient/messages/new"
                  className="text-xs text-teal-600 hover:underline mt-1 inline-block"
                >
                  Doktor secin ve mesajlasmaya baslayin
                </Link>
              </div>
            ) : (
              conversations.map((conv: Conversation) => (
                <div
                  key={conv.id}
                  onClick={() => setActiveConvId(conv.id)}
                  className={`px-4 py-3 cursor-pointer transition border-b border-gray-50 ${
                    activeConvId === conv.id
                      ? 'bg-teal-50 border-l-2 border-l-teal-500'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-teal-100 flex items-center justify-center flex-shrink-0">
                      <User className="w-4 h-4 text-teal-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-800 truncate">{conv.doctor_name}</span>
                        {conv.patient_unread_count > 0 && (
                          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-teal-500 text-white text-xs flex items-center justify-center">
                            {conv.patient_unread_count}
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
                      {conv.status === 'active' ? 'Aktif' : 'Kapali'}
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
                  <div className="font-semibold text-gray-800">{convDetail.doctor_name}</div>
                  {convDetail.doctor_specialty && (
                    <div className="text-xs text-teal-600">{convDetail.doctor_specialty}</div>
                  )}
                </div>
                {convDetail.status === 'active' && (
                  <button
                    onClick={handleClose}
                    className="text-xs text-gray-400 hover:text-red-500 transition"
                  >
                    Konusmayi Kapat
                  </button>
                )}
              </div>

              <MessageList isEmpty={messages.length === 0}>
                {messages.map((msg) => (
                  <ChatBubble
                    key={msg.id}
                    role={msg.sender_role === 'patient' ? 'user' : 'doctor'}
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
                  placeholder="Doktorunuza mesaj yazin..."
                />
              ) : (
                <div className="p-3 bg-gray-50 border-t text-center text-sm text-gray-400">
                  Bu konusma kapatilmis.
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400">
              <MessageSquare className="w-16 h-16 text-gray-200 mb-4" />
              <p className="text-lg font-medium text-gray-500">Bir Konusma Secin</p>
              <p className="text-sm text-gray-400 mt-1">
                Sol panelden bir konusma secin veya yeni bir mesaj gonderin
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
