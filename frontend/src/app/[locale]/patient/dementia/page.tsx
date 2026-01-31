'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import {
  useCognitiveExercisesByType,
  useExerciseStats,
  useRecentExerciseSessions,
  useTodayAssessment,
  useExerciseChart,
  useExerciseTypeStats,
} from '@/hooks/useDementiaData';
import {
  Brain,
  Gamepad2,
  ClipboardList,
  TrendingUp,
  Calendar,
  Clock,
  Flame,
  ChevronRight,
  Play,
} from 'lucide-react';

const EXERCISE_TYPE_ICONS: Record<string, string> = {
  memory: '🧠',
  attention: '👁️',
  language: '📝',
  problem_solving: '🧩',
  calculation: '🔢',
  orientation: '🧭',
};

export default function DementiaPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'exercises' | 'progress' | 'assessment'>('exercises');

  const { data: exercisesByType, isLoading: exercisesLoading } = useCognitiveExercisesByType();
  const { data: stats } = useExerciseStats();
  const { data: recentSessions } = useRecentExerciseSessions();
  const { data: todayAssessment } = useTodayAssessment();

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-7 h-7 text-indigo-600" />
        <h1 className="text-2xl font-bold text-gray-900">Bilişsel Sağlık</h1>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-indigo-600 mb-1">
              <Gamepad2 className="w-4 h-4" />
              <span className="text-xs font-medium">Bu Hafta</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.exercises_this_week}</div>
            <div className="text-xs text-gray-500">egzersiz</div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-orange-600 mb-1">
              <Flame className="w-4 h-4" />
              <span className="text-xs font-medium">Seri</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.current_streak_days}</div>
            <div className="text-xs text-gray-500">gün</div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-green-600 mb-1">
              <TrendingUp className="w-4 h-4" />
              <span className="text-xs font-medium">Ortalama</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {stats.avg_score_this_week ? `%${Math.round(stats.avg_score_this_week)}` : '-'}
            </div>
            <div className="text-xs text-gray-500">
              {stats.score_trend === 'improving' && '↑ Yükseliyor'}
              {stats.score_trend === 'declining' && '↓ Düşüyor'}
              {stats.score_trend === 'stable' && '→ Sabit'}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-purple-600 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Toplam</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_exercises_completed}</div>
            <div className="text-xs text-gray-500">tamamlandı</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        {(['exercises', 'progress', 'assessment'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition ${
              activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            {tab === 'exercises' && <Gamepad2 className="w-4 h-4" />}
            {tab === 'progress' && <TrendingUp className="w-4 h-4" />}
            {tab === 'assessment' && <ClipboardList className="w-4 h-4" />}
            {tab === 'exercises' && 'Egzersizler'}
            {tab === 'progress' && 'İlerleme'}
            {tab === 'assessment' && 'Günlük Değerlendirme'}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'exercises' && (
        <ExercisesTab exercisesByType={exercisesByType} isLoading={exercisesLoading} />
      )}
      {activeTab === 'progress' && (
        <ProgressTab recentSessions={recentSessions} stats={stats} />
      )}
      {activeTab === 'assessment' && (
        <AssessmentTab todayAssessment={todayAssessment} />
      )}
    </div>
  );
}

function ExercisesTab({
  exercisesByType,
  isLoading,
}: {
  exercisesByType: { type: string; type_display: string; exercises: any[] }[] | undefined;
  isLoading: boolean;
}) {
  if (isLoading) {
    return <div className="text-center py-8 text-gray-500">Yükleniyor...</div>;
  }

  if (!exercisesByType || exercisesByType.length === 0) {
    return <div className="text-center py-8 text-gray-500">Egzersiz bulunamadı.</div>;
  }

  return (
    <div className="space-y-6">
      {exercisesByType.map((group) => (
        <div key={group.type}>
          <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-3">
            <span>{EXERCISE_TYPE_ICONS[group.type] || '🎯'}</span>
            {group.type_display}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {group.exercises.map((exercise) => (
              <Link
                key={exercise.id}
                href={`/patient/dementia/exercise/${exercise.slug}`}
                className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-md transition group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 group-hover:text-indigo-600 transition">
                      {exercise.name}
                    </h4>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{exercise.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {exercise.estimated_duration_minutes} dk
                      </span>
                      <span className={`px-2 py-0.5 rounded-full ${
                        exercise.difficulty === 'easy'
                          ? 'bg-green-100 text-green-700'
                          : exercise.difficulty === 'medium'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {exercise.difficulty_display}
                      </span>
                    </div>
                  </div>
                  <div className="ml-3 p-2 bg-indigo-50 rounded-lg text-indigo-600 group-hover:bg-indigo-100 transition">
                    <Play className="w-5 h-5" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function ProgressTab({
  recentSessions,
  stats,
}: {
  recentSessions: any[] | undefined;
  stats: any;
}) {
  const { data: chartData } = useExerciseChart(30);
  const { data: typeStats } = useExerciseTypeStats();

  const EXERCISE_TYPE_LABELS: Record<string, string> = {
    memory: 'Hafıza',
    attention: 'Dikkat',
    language: 'Dil',
    problem_solving: 'Problem Çözme',
    calculation: 'Hesaplama',
    orientation: 'Yönelim',
  };

  if (!recentSessions || recentSessions.length === 0) {
    return (
      <div className="text-center py-12">
        <Gamepad2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Henüz egzersiz tamamlamadınız.</p>
        <p className="text-sm text-gray-400 mt-1">
          Bilişsel egzersizlere başlayarak ilerlemenizi takip edin.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Performance Chart */}
      {chartData && chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Son 30 Gün Performans</h3>
          <div className="h-32 flex items-end gap-1">
            {chartData.map((day: { started_at__date: string; avg_score: number | null; sessions_count: number }, index: number) => (
              <div
                key={index}
                className="flex-1 bg-indigo-100 rounded-t hover:bg-indigo-300 transition relative group cursor-pointer"
                style={{
                  height: day.avg_score ? `${day.avg_score}%` : '5%',
                  backgroundColor: day.avg_score ? undefined : '#f3f4f6',
                }}
              >
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                  {new Date(day.started_at__date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                  <br />
                  {day.avg_score ? `%${Math.round(day.avg_score)} (${day.sessions_count} egzersiz)` : 'Egzersiz yok'}
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-2">
            <span>30 gün önce</span>
            <span>Bugün</span>
          </div>
        </div>
      )}

      {/* Exercise Type Performance */}
      {typeStats && Object.keys(typeStats).length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Kategorilere Göre Performans</h3>
          <div className="space-y-3">
            {Object.entries(typeStats).map(([type, data]) => (
              <div key={type}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm text-gray-700">
                    {EXERCISE_TYPE_LABELS[type] || type}
                  </span>
                  <span className="text-sm font-medium text-gray-900">
                    %{Math.round((data as any).avgScore)} ({(data as any).count} egzersiz)
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      (data as any).avgScore >= 80
                        ? 'bg-green-500'
                        : (data as any).avgScore >= 60
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${(data as any).avgScore}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Sessions */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Son Egzersizler</h3>
        <div className="space-y-2">
          {recentSessions.slice(0, 10).map((session) => (
            <div
              key={session.id}
              className="bg-white rounded-lg border border-gray-200 p-3 flex items-center justify-between"
            >
              <div>
                <div className="font-medium text-gray-900">{session.exercise_name}</div>
                <div className="text-xs text-gray-500">
                  {new Date(session.started_at).toLocaleDateString('tr-TR', {
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
              <div className="text-right">
                <div className={`text-lg font-bold ${
                  session.accuracy_percent >= 80
                    ? 'text-green-600'
                    : session.accuracy_percent >= 60
                    ? 'text-yellow-600'
                    : 'text-red-600'
                }`}>
                  %{Math.round(session.accuracy_percent || 0)}
                </div>
                <div className="text-xs text-gray-400">
                  {session.duration_seconds ? `${Math.round(session.duration_seconds / 60)} dk` : '-'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AssessmentTab({ todayAssessment }: { todayAssessment: any }) {
  const hasAssessment = !!todayAssessment;

  return (
    <div className="space-y-6">
      {/* Today's Status */}
      <div className={`rounded-xl border-2 p-5 ${
        hasAssessment ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-full ${
            hasAssessment ? 'bg-green-100' : 'bg-yellow-100'
          }`}>
            <Calendar className={`w-5 h-5 ${
              hasAssessment ? 'text-green-600' : 'text-yellow-600'
            }`} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {hasAssessment ? 'Bugünkü Değerlendirme Tamamlandı' : 'Bugünkü Değerlendirme'}
            </h3>
            <p className="text-sm text-gray-600">
              {hasAssessment
                ? 'Günlük değerlendirmenizi doldurdunuz.'
                : 'Günlük ruh hali ve aktivite değerlendirmesi yapın.'}
            </p>
          </div>
        </div>

        {!hasAssessment && (
          <Link
            href="/patient/dementia/assessment"
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
          >
            Değerlendirmeyi Başlat
            <ChevronRight className="w-4 h-4" />
          </Link>
        )}
      </div>

      {/* Assessment Summary */}
      {hasAssessment && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Bugünkü Özet</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl mb-1">
                {['😢', '😕', '😐', '🙂', '😊'][todayAssessment.mood_score - 1] || '😐'}
              </div>
              <div className="text-xs text-gray-500">Ruh Hali</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-lg font-bold text-gray-900">
                {todayAssessment.sleep_hours || '-'} saat
              </div>
              <div className="text-xs text-gray-500">Uyku</div>
            </div>
            {todayAssessment.fall_occurred && (
              <div className="col-span-2 p-3 bg-red-50 rounded-lg text-center">
                <div className="text-red-600 font-medium">⚠️ Düşme Kaydedildi</div>
              </div>
            )}
          </div>
          <Link
            href="/patient/dementia/assessment"
            className="mt-4 text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
          >
            Detayları Görüntüle
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      )}

      {/* Quick Links */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          href="/patient/dementia/screening"
          className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 transition"
        >
          <Brain className="w-5 h-5 text-purple-600 mb-2" />
          <div className="font-medium text-gray-900">Bilissel Tarama</div>
          <div className="text-xs text-gray-500">Kapsamli bilissel degerlendirme</div>
        </Link>
        <Link
          href="/patient/dementia/notes"
          className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 transition"
        >
          <ClipboardList className="w-5 h-5 text-indigo-600 mb-2" />
          <div className="font-medium text-gray-900">Notlar</div>
          <div className="text-xs text-gray-500">Gozlem ve notlari goruntule</div>
        </Link>
        <Link
          href="/patient/dementia/history"
          className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 transition"
        >
          <TrendingUp className="w-5 h-5 text-green-600 mb-2" />
          <div className="font-medium text-gray-900">Gecmis</div>
          <div className="text-xs text-gray-500">Tum degerlendirmeleri gor</div>
        </Link>
      </div>
    </div>
  );
}
