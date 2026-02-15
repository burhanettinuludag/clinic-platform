'use client';

import { useEffect } from 'react';

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-900 px-4">
      <div className="text-center">
        <div className="mb-6">
          <span className="text-8xl font-bold bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">500</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Bir Hata Olustu</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-sm mx-auto">
          Beklenmeyen bir sorun yasandi. Lutfen tekrar deneyin veya daha sonra gelin.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button onClick={reset} className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
            Tekrar Dene
          </button>
          <a href="/" className="rounded-lg border border-gray-300 dark:border-gray-600 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Ana Sayfa
          </a>
        </div>
      </div>
    </div>
  );
}
