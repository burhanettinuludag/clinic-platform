'use client';

import { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';

interface MessageListProps {
  children: React.ReactNode;
  isLoading?: boolean;
  emptyMessage?: string;
  isEmpty?: boolean;
}

export default function MessageList({ children, isLoading, emptyMessage, isEmpty }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [children]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
    >
      {isEmpty && !isLoading && (
        <div className="flex items-center justify-center h-full text-gray-400 text-sm">
          {emptyMessage || 'Henuz mesaj yok'}
        </div>
      )}
      {children}
      {isLoading && (
        <div className="flex items-center gap-2 text-gray-400 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Yanitlaniyor...</span>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
