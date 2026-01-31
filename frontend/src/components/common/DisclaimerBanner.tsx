'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { X } from 'lucide-react';

export default function DisclaimerBanner() {
  const t = useTranslations('disclaimer');
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center text-sm text-amber-800">
      <div className="flex items-center justify-center gap-2">
        <span>{t('text')}</span>
        <button
          onClick={() => setDismissed(true)}
          className="ml-2 text-amber-600 hover:text-amber-800"
          aria-label="Dismiss"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
