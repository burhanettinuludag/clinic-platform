'use client';

import { useState } from 'react';
import { Link } from '@/i18n/navigation';
import {
  useEducationItems,
  useStartEducation,
  useCompleteEducation,
  type EducationItem,
} from '@/hooks/usePatientData';
import {
  ArrowLeft,
  BookOpen,
  Clock,
  CheckCircle2,
  Play,
  FileText,
  Image,
  Sparkles,
  ChevronRight,
  X,
  Zap,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function EpilepsyEducationPage() {
  const { data: educationItems, isLoading, error } = useEducationItems({ disease_module: 'epilepsy' });
  const [selectedItem, setSelectedItem] = useState<EducationItem | null>(null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yukleniyor...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Link
            href="/patient/epilepsy"
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-600" />
            <h1 className="text-xl font-bold text-gray-900">Epilepsi Egitim Modulu</h1>
          </div>
        </div>
        <div className="text-center py-12 bg-white rounded-xl border border-red-200">
          <BookOpen className="w-12 h-12 text-red-300 mx-auto mb-3" />
          <p className="text-red-500 font-medium mb-2">Icerikler yuklenemedi</p>
          <p className="text-sm text-gray-400">Lutfen giris yaptiginizdan emin olun ve sayfayi yenileyin.</p>
        </div>
      </div>
    );
  }

  const completedCount = educationItems?.filter((item) => item.progress?.completed_at).length ?? 0;
  const totalCount = educationItems?.length ?? 0;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/patient/epilepsy"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-600" />
            <h1 className="text-xl font-bold text-gray-900">Epilepsi Egitim Modulu</h1>
          </div>
          <p className="text-sm text-gray-500">
            Epilepsinizi daha iyi anlamak ve yonetmek icin egitim iceriklerini tamamlayin
          </p>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl p-6 text-white mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BookOpen className="w-8 h-8" />
            <div>
              <div className="text-sm opacity-90">Ilerleme Durumu</div>
              <div className="text-2xl font-bold">{completedCount}/{totalCount} Tamamlandi</div>
            </div>
          </div>
          <div className="text-4xl font-bold">%{progressPercent}</div>
        </div>
        <div className="h-2 bg-white/30 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Content List */}
      <div className="space-y-3">
        {educationItems?.map((item, index) => (
          <EducationCard
            key={item.id}
            item={item}
            index={index + 1}
            onClick={() => setSelectedItem(item)}
          />
        ))}
      </div>

      {educationItems?.length === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Henuz egitim icerigi eklenmemis.</p>
        </div>
      )}

      {/* Content Modal */}
      {selectedItem && (
        <EducationModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </div>
  );
}

function EducationCard({
  item,
  index,
  onClick,
}: {
  item: EducationItem;
  index: number;
  onClick: () => void;
}) {
  const isCompleted = !!item.progress?.completed_at;
  const inProgress = item.progress && !item.progress.completed_at;

  const getContentIcon = () => {
    switch (item.content_type) {
      case 'video':
        return <Play className="w-5 h-5" />;
      case 'infographic':
        return <Image className="w-5 h-5" />;
      case 'interactive':
        return <Sparkles className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const getContentTypeLabel = () => {
    switch (item.content_type) {
      case 'video':
        return 'Video';
      case 'infographic':
        return 'Infografik';
      case 'interactive':
        return 'Interaktif';
      default:
        return 'Makale';
    }
  };

  return (
    <button
      onClick={onClick}
      className={`w-full text-left bg-white rounded-xl border-2 p-4 transition-all hover:shadow-md ${
        isCompleted
          ? 'border-green-200 bg-green-50/30'
          : inProgress
          ? 'border-amber-200 bg-amber-50/30'
          : 'border-gray-200 hover:border-amber-300'
      }`}
    >
      <div className="flex items-center gap-4">
        {/* Status/Number */}
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
            isCompleted
              ? 'bg-green-100 text-green-600'
              : inProgress
              ? 'bg-amber-100 text-amber-600'
              : 'bg-gray-100 text-gray-500'
          }`}
        >
          {isCompleted ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <span className="font-semibold">{index}</span>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className={`font-medium ${isCompleted ? 'text-green-700' : 'text-gray-900'}`}>
            {item.title}
          </h3>
          <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              {getContentIcon()}
              {getContentTypeLabel()}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {item.estimated_duration_minutes} dk
            </span>
            {item.category_name && (
              <span className="px-2 py-0.5 bg-gray-100 rounded-full text-xs">
                {item.category_name}
              </span>
            )}
          </div>
        </div>

        {/* Arrow */}
        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
      </div>

      {/* Progress bar for in-progress items */}
      {inProgress && item.progress && (
        <div className="mt-3 pt-3 border-t border-amber-200">
          <div className="flex items-center justify-between text-xs text-amber-600 mb-1">
            <span>Ilerleme</span>
            <span>%{item.progress.progress_percent}</span>
          </div>
          <div className="h-1.5 bg-amber-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-500 rounded-full"
              style={{ width: `${item.progress.progress_percent}%` }}
            />
          </div>
        </div>
      )}
    </button>
  );
}

function EducationModal({
  item,
  onClose,
}: {
  item: EducationItem;
  onClose: () => void;
}) {
  const startEducation = useStartEducation();
  const completeEducation = useCompleteEducation();
  const [isCompleting, setIsCompleting] = useState(false);

  const isCompleted = !!item.progress?.completed_at;
  const hasStarted = !!item.progress;

  const handleStart = () => {
    if (!hasStarted) {
      startEducation.mutate(item.id);
    }
  };

  const handleComplete = () => {
    if (item.progress?.id) {
      setIsCompleting(true);
      completeEducation.mutate(item.progress.id, {
        onSuccess: () => {
          setTimeout(() => {
            onClose();
          }, 1000);
        },
        onError: () => {
          setIsCompleting(false);
        },
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-amber-50 to-orange-50">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{item.title}</h2>
            <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>{item.estimated_duration_minutes} dakika</span>
              {isCompleted && (
                <span className="flex items-center gap-1 text-green-600 font-medium">
                  <CheckCircle2 className="w-4 h-4" />
                  Tamamlandi
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {item.content_type === 'video' && item.video_url && (
            <div className="aspect-video bg-black rounded-lg mb-6 overflow-hidden">
              <iframe
                src={item.video_url}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          )}

          {item.image && (
            <img
              src={item.image}
              alt={item.title}
              className="w-full rounded-lg mb-6"
            />
          )}

          <div className="prose-education">
            <ReactMarkdown>{item.body}</ReactMarkdown>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50">
          {isCompleted ? (
            <div className="flex items-center justify-center gap-2 py-2 text-green-600">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-medium">Bu icerigi tamamladiniz</span>
            </div>
          ) : isCompleting ? (
            <div className="flex items-center justify-center gap-2 py-2 text-green-600">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-medium">Tamamlandi!</span>
            </div>
          ) : !hasStarted ? (
            <button
              onClick={handleStart}
              disabled={startEducation.isPending}
              className="w-full py-3 bg-amber-600 text-white font-medium rounded-lg hover:bg-amber-700 disabled:opacity-50 transition"
            >
              {startEducation.isPending ? 'Baslatiliyor...' : 'Okumaya Basla'}
            </button>
          ) : (
            <button
              onClick={handleComplete}
              disabled={completeEducation.isPending}
              className="w-full py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
            >
              {completeEducation.isPending ? 'Tamamlaniyor...' : 'Tamamladim'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
