'use client';

import { useTranslations } from 'next-intl';
import { useEducationItems } from '@/hooks/useStoreData';
import { Link } from '@/i18n/navigation';
import { BookOpen, Video, FileText, Image, Clock, CheckCircle2 } from 'lucide-react';

const contentTypeIcons = {
  video: Video,
  text: FileText,
  infographic: Image,
  interactive: BookOpen,
};

export default function EducationPage() {
  const t = useTranslations();
  const { data: items, isLoading } = useEducationItems();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('nav.education')}</h1>
      <p className="text-gray-500 mb-8">Hastalik bazli egitim icerikleri ve materyaller.</p>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>
      ) : items && items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => {
            const Icon = contentTypeIcons[item.content_type] || BookOpen;
            const isCompleted = item.progress?.progress_percent === 100;

            return (
              <div
                key={item.id}
                className={`bg-white rounded-xl border overflow-hidden hover:shadow-lg transition ${
                  isCompleted ? 'border-green-200' : 'border-gray-200'
                }`}
              >
                {item.image ? (
                  <div className="aspect-video bg-gray-100 overflow-hidden">
                    <img src={item.image} alt={item.title} className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="aspect-video bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
                    <Icon className="w-12 h-12 text-blue-300" />
                  </div>
                )}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="w-4 h-4 text-blue-600" />
                    <span className="text-xs text-blue-600 font-medium capitalize">{item.content_type}</span>
                    <span className="flex items-center gap-1 text-xs text-gray-400 ml-auto">
                      <Clock className="w-3 h-3" /> {item.estimated_duration_minutes} dk
                    </span>
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h2>

                  {/* Progress Bar */}
                  {item.progress ? (
                    <div className="mt-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-400">
                          %{item.progress.progress_percent}
                        </span>
                        {isCompleted && (
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                        )}
                      </div>
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isCompleted ? 'bg-green-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${item.progress.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="mt-3">
                      <span className="text-xs text-gray-400">Henuz baslanmadi</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">{t('common.noResults')}</div>
      )}
    </div>
  );
}
