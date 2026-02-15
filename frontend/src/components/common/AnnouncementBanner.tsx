'use client';

import { useState } from 'react';
import { X, ExternalLink } from 'lucide-react';
import { useActiveAnnouncements, useLocalizedField } from '@/hooks/useSiteData';
import { useLocale } from 'next-intl';

function SingleBanner({ announcement, onDismiss }: {
  announcement: { id: string; title_tr: string; title_en: string; message_tr: string; message_en: string; link_url: string; link_text_tr: string; link_text_en: string; bg_color: string; text_color: string };
  onDismiss: (id: string) => void;
}) {
  const locale = useLocale();
  const title = locale === 'en' ? announcement.title_en : announcement.title_tr;
  const message = locale === 'en' ? announcement.message_en : announcement.message_tr;
  const linkText = locale === 'en' ? announcement.link_text_en : announcement.link_text_tr;

  return (
    <div
      className="relative px-4 py-3"
      style={{
        backgroundColor: announcement.bg_color || '#1e40af',
        color: announcement.text_color || '#ffffff',
      }}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-3 text-sm">
        <div className="flex items-center gap-2 text-center">
          {title && <span className="font-semibold">{title}</span>}
          {title && message && <span className="opacity-70">—</span>}
          <span className="opacity-90">{message}</span>
          {announcement.link_url && (
            <a
              href={announcement.link_url}
              className="inline-flex items-center gap-1 font-medium underline underline-offset-2 hover:opacity-80 transition-opacity ml-1"
              target={announcement.link_url.startsWith('http') ? '_blank' : undefined}
              rel={announcement.link_url.startsWith('http') ? 'noopener noreferrer' : undefined}
            >
              {linkText || 'Detay'}
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
        <button
          onClick={() => onDismiss(announcement.id)}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-md hover:bg-white/20 transition-colors"
          aria-label="Kapat"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default function AnnouncementBanner() {
  const { data: announcements } = useActiveAnnouncements();
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const handleDismiss = (id: string) => {
    setDismissed(prev => new Set(prev).add(id));
  };

  const visible = announcements?.filter(a => !dismissed.has(a.id));

  if (!visible?.length) return null;

  return (
    <div className="announcement-banners">
      {visible.map(announcement => (
        <SingleBanner
          key={announcement.id}
          announcement={announcement}
          onDismiss={handleDismiss}
        />
      ))}
    </div>
  );
}
