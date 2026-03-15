'use client';

import { AlertTriangle } from 'lucide-react';

interface DisclaimerBannerProps {
  variant?: 'default' | 'compact';
}

export default function DisclaimerBanner({ variant = 'default' }: DisclaimerBannerProps) {
  if (variant === 'compact') {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
        <AlertTriangle className="w-3 h-3 flex-shrink-0" />
        <span>Bu yanıtlar tıbbi tavsiye değildir. Hekiminize danışınız.</span>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
      <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
      <div>
        <div className="font-medium text-amber-800 text-sm">Önemli Bilgilendirme</div>
        <div className="text-xs text-amber-700 mt-1">
          Bu yapay zeka asistanı platformda yayınlanmış içerikler üzerinden bilgi verir.
          Tıbbi teşhis koymaz, tedavi planlamaz veya ilaç önerisinde bulunmaz.
          Sağlık kararlarınız için mutlaka hekiminize danışınız.
        </div>
      </div>
    </div>
  );
}
