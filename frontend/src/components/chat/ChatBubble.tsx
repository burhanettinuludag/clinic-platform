'use client';

import { Bot, User, CheckCheck } from 'lucide-react';

interface ChatBubbleProps {
  role: 'user' | 'assistant' | 'patient' | 'doctor';
  content: string;
  senderName?: string;
  timestamp?: string;
  isRead?: boolean;
  confidence?: string;
}

export default function ChatBubble({
  role,
  content,
  senderName,
  timestamp,
  isRead,
  confidence,
}: ChatBubbleProps) {
  const isUser = role === 'user' || role === 'patient';
  const isAI = role === 'assistant';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isAI
            ? 'bg-purple-100'
            : isUser
            ? 'bg-blue-100'
            : 'bg-teal-100'
        }`}
      >
        {isAI ? (
          <Bot className="w-4 h-4 text-purple-600" />
        ) : (
          <User className="w-4 h-4 text-blue-600" />
        )}
      </div>

      {/* Message */}
      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        {senderName && (
          <div className={`text-xs text-gray-500 mb-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {senderName}
          </div>
        )}
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-md'
              : isAI
              ? 'bg-gray-100 text-gray-800 rounded-bl-md'
              : 'bg-teal-50 text-gray-800 rounded-bl-md border border-teal-200'
          }`}
        >
          {content}
        </div>
        <div className={`flex items-center gap-2 mt-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {timestamp && (
            <span className="text-[10px] text-gray-400">
              {new Date(timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
          {confidence && isAI && (
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded ${
                confidence === 'high'
                  ? 'bg-green-100 text-green-700'
                  : confidence === 'medium'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-red-100 text-red-700'
              }`}
            >
              {confidence === 'high' ? 'Yuksek' : confidence === 'medium' ? 'Orta' : 'Dusuk'}
            </span>
          )}
          {isUser && typeof isRead === 'boolean' && (
            <CheckCheck className={`w-3.5 h-3.5 ${isRead ? 'text-blue-500' : 'text-gray-300'}`} />
          )}
        </div>
      </div>
    </div>
  );
}
