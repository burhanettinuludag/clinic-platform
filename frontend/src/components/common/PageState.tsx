'use client';

import { AlertTriangle, RefreshCw, Inbox } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

interface PageLoadingProps {
  text?: string;
  fullPage?: boolean;
}

export function PageLoading({ text = 'Yukleniyor...', fullPage = true }: PageLoadingProps) {
  return (
    <div className={fullPage ? 'flex items-center justify-center min-h-[60vh]' : 'flex justify-center py-12'}>
      <LoadingSpinner size="lg" text={text} />
    </div>
  );
}

interface PageErrorProps {
  message?: string;
  onRetry?: () => void;
}

export function PageError({ message = 'Bir hata olustu.', onRetry }: PageErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 mb-4">
        <AlertTriangle className="h-7 w-7 text-red-500" />
      </div>
      <p className="text-sm text-gray-600 mb-4 text-center max-w-sm">{message}</p>
      {onRetry && (
        <button onClick={onRetry}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          <RefreshCw className="h-4 w-4" /> Tekrar Dene
        </button>
      )}
    </div>
  );
}

interface PageEmptyProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}

export function PageEmpty({ icon, title = 'Veri bulunamadi', description, action }: PageEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-50 mb-4">
        {icon || <Inbox className="h-7 w-7 text-gray-300" />}
      </div>
      <p className="text-sm font-medium text-gray-700 mb-1">{title}</p>
      {description && <p className="text-xs text-gray-400 mb-4 text-center max-w-sm">{description}</p>}
      {action && (
        <button onClick={action.onClick}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          {action.label}
        </button>
      )}
    </div>
  );
}
