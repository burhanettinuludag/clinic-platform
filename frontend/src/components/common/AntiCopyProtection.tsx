'use client';

import { useEffect } from 'react';

/**
 * Production ortamında sağ tık ve metin kopyalamayı engelleyen
 * caydırıcı bileşen. Tam koruma sağlamaz ama casual kopyalamayı zorlaştırır.
 */
export default function AntiCopyProtection() {
  useEffect(() => {
    if (process.env.NODE_ENV !== 'production') return;

    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };

    document.addEventListener('contextmenu', handleContextMenu);

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
    };
  }, []);

  return null;
}
