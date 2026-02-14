'use client';

import { useState, useRef, useEffect } from 'react';
import { Bell, Check, CheckCheck, Info, AlertTriangle, X } from 'lucide-react';
import { useUnreadCount, useNotifications, useMarkRead, useMarkAllRead } from '@/hooks/useNotifications';
import type { Notification } from '@/hooks/useNotifications';
import { useRouter } from 'next/navigation';

const TYPE_ICON: Record<string, { icon: typeof Info; color: string }> = {
  info: { icon: Info, color: 'text-blue-500' },
  alert: { icon: AlertTriangle, color: 'text-orange-500' },
  reminder: { icon: Bell, color: 'text-purple-500' },
  system: { icon: Bell, color: 'text-gray-500' },
};

function timeAgo(d: string) {
  const diff = Date.now() - new Date(d).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'simdi';
  if (m < 60) return m + ' dk';
  const h = Math.floor(m / 60);
  if (h < 24) return h + ' saat';
  return Math.floor(h / 24) + ' gun';
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const { data: unreadData } = useUnreadCount();
  const { data: notifications } = useNotifications(8);
  const markRead = useMarkRead();
  const markAll = useMarkAllRead();
  const count = unreadData?.unread_count || 0;

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleClick = (n: Notification) => {
    if (!n.is_read) markRead.mutate(n.id);
    if (n.action_url) router.push(n.action_url);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <button onClick={() => setOpen(!open)} className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
        <Bell className="h-5 w-5 text-gray-600" />
        {count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {count > 9 ? '9+' : count}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-12 z-50 w-80 rounded-xl border bg-white shadow-xl">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">Bildirimler</h3>
            <div className="flex gap-1">
              {count > 0 && (
                <button onClick={() => markAll.mutate()} className="rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50" title="Tumunu okundu yap">
                  <CheckCheck className="h-3.5 w-3.5" />
                </button>
              )}
              <button onClick={() => setOpen(false)} className="rounded p-1 text-gray-400 hover:text-gray-600">
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {!notifications?.length ? (
              <div className="py-8 text-center text-sm text-gray-400">Bildirim yok</div>
            ) : notifications.map((n) => {
              const cfg = TYPE_ICON[n.notification_type] || TYPE_ICON.info;
              const Icon = cfg.icon;
              return (
                <button key={n.id} onClick={() => handleClick(n)}
                  className={'flex w-full items-start gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors ' + (!n.is_read ? 'bg-blue-50/40' : '')}>
                  <Icon className={'h-4 w-4 mt-0.5 flex-shrink-0 ' + cfg.color} />
                  <div className="min-w-0 flex-1">
                    <p className={'text-sm ' + (!n.is_read ? 'font-medium text-gray-900' : 'text-gray-700')}>{n.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                    <p className="text-[10px] text-gray-400 mt-1">{timeAgo(n.created_at)}</p>
                  </div>
                  {!n.is_read && <span className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-blue-500" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
