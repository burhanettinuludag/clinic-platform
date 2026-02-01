'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import Cookies from 'js-cookie';
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
  TrendingDown,
  Minus,
  Calendar,
  Clock,
  Flame,
  ChevronRight,
  Play,
  LogIn,
  AlertCircle,
  ArrowUpRight,
  ArrowDownRight,
  ArrowRight,
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
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  const { data: exercisesByType, isLoading: exercisesLoading, error: exercisesError } = useCognitiveExercisesByType();
  const { data: stats } = useExerciseStats();
  const { data: recentSessions } = useRecentExerciseSessions();
  const { data: todayAssessment } = useTodayAssessment();

  // Giriş durumunu kontrol et
  useEffect(() => {
    const token = Cookies.get('access_token');
    setIsAuthenticated(!!token);
  }, []);

  // Giriş yapılmamışsa uyarı göster
  if (isAuthenticated === false) {
    return (
      <div className="max-w-lg mx-auto py-12">
        <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-8 text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-amber-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Giriş Yapmanız Gerekiyor</h2>
          <p className="text-gray-600 mb-6">
            Bilişsel sağlık egzersizlerine ve testlere erişmek için lütfen hesabınıza giriş yapın.
          </p>
          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
          >
            <LogIn className="w-5 h-5" />
            Giriş Yap
          </Link>
          <p className="text-sm text-gray-500 mt-4">
            Hesabınız yok mu?{' '}
            <Link href="/auth/register" className="text-indigo-600 hover:text-indigo-700 font-medium">
              Kayıt olun
            </Link>
          </p>
        </div>
      </div>
    );
  }

  // Yükleniyor durumu
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  // API hatası durumunda da uyarı göster (401 unauthorized)
  if (exercisesError && (exercisesError as any)?.response?.status === 401) {
    return (
      <div className="max-w-lg mx-auto py-12">
        <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-8 text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-amber-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Oturum Süreniz Dolmuş</h2>
          <p className="text-gray-600 mb-6">
            Güvenliğiniz için oturumunuz sonlandırıldı. Lütfen tekrar giriş yapın.
          </p>
          <Link
            href="/auth/login"
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
          >
            <LogIn className="w-5 h-5" />
            Tekrar Giriş Yap
          </Link>
        </div>
      </div>
    );
  }

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

          <div className={`bg-white rounded-xl border-2 p-4 ${
            stats.score_trend === 'improving'
              ? 'border-green-300 bg-green-50'
              : stats.score_trend === 'declining'
              ? 'border-red-300 bg-red-50'
              : 'border-gray-200'
          }`}>
            <div className={`flex items-center gap-2 mb-1 ${
              stats.score_trend === 'improving'
                ? 'text-green-600'
                : stats.score_trend === 'declining'
                ? 'text-red-600'
                : 'text-gray-600'
            }`}>
              {stats.score_trend === 'improving' && <ArrowUpRight className="w-4 h-4" />}
              {stats.score_trend === 'declining' && <ArrowDownRight className="w-4 h-4" />}
              {stats.score_trend === 'stable' && <ArrowRight className="w-4 h-4" />}
              <span className="text-xs font-medium">Eğilim</span>
            </div>
            <div className={`text-xl font-bold ${
              stats.score_trend === 'improving'
                ? 'text-green-700'
                : stats.score_trend === 'declining'
                ? 'text-red-700'
                : 'text-gray-700'
            }`}>
              {stats.score_trend === 'improving' && 'İyiye Gidiyor'}
              {stats.score_trend === 'declining' && 'Düşüşte'}
              {stats.score_trend === 'stable' && 'Stabil'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {stats.avg_score_this_week && stats.avg_score_last_week && (
                <>
                  Bu hafta %{Math.round(stats.avg_score_this_week)}
                  {stats.avg_score_last_week && ` (geçen hafta %${Math.round(stats.avg_score_last_week)})`}
                </>
              )}
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

      {/* Exercise Type Performance with Trend */}
      {typeStats && Object.keys(typeStats).length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Kategorilere Göre Eğilim</h3>
          <div className="space-y-4">
            {Object.entries(typeStats).map(([type, data]) => {
              const trend = (data as any).trend;
              return (
                <div key={type} className={`p-3 rounded-lg border-2 ${
                  trend === 'improving'
                    ? 'border-green-200 bg-green-50'
                    : trend === 'declining'
                    ? 'border-red-200 bg-red-50'
                    : 'border-gray-200 bg-gray-50'
                }`}>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{EXERCISE_TYPE_ICONS[type] || '🎯'}</span>
                      <div>
                        <span className="text-sm font-medium text-gray-900">
                          {EXERCISE_TYPE_LABELS[type] || type}
                        </span>
                        <div className="text-xs text-gray-500">
                          {(data as any).count} egzersiz tamamlandı
                        </div>
                      </div>
                    </div>
                    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${
                      trend === 'improving'
                        ? 'bg-green-100 text-green-700'
                        : trend === 'declining'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {trend === 'improving' && <ArrowUpRight className="w-4 h-4" />}
                      {trend === 'declining' && <ArrowDownRight className="w-4 h-4" />}
                      {trend === 'stable' && <ArrowRight className="w-4 h-4" />}
                      <span className="text-sm font-medium">
                        {trend === 'improving' && 'İyiye Gidiyor'}
                        {trend === 'declining' && 'Düşüşte'}
                        {trend === 'stable' && 'Stabil'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Sessions - Trend-focused display */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Son Aktiviteler</h3>
        <div className="space-y-2">
          {recentSessions.slice(0, 10).map((session, index) => {
            // Compare with previous session of same type
            const previousSameType = recentSessions
              .slice(index + 1)
              .find((s) => s.exercise_type === session.exercise_type);

            let sessionTrend: 'improving' | 'stable' | 'declining' = 'stable';
            if (previousSameType && session.accuracy_percent && previousSameType.accuracy_percent) {
              const diff = session.accuracy_percent - previousSameType.accuracy_percent;
              if (diff > 5) sessionTrend = 'improving';
              else if (diff < -5) sessionTrend = 'declining';
            }

            return (
              <div
                key={session.id}
                className={`rounded-lg border-2 p-3 flex items-center justify-between ${
                  sessionTrend === 'improving'
                    ? 'border-green-200 bg-green-50'
                    : sessionTrend === 'declining'
                    ? 'border-red-200 bg-red-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{EXERCISE_TYPE_ICONS[session.exercise_type] || '🎯'}</span>
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
                </div>
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${
                  sessionTrend === 'improving'
                    ? 'bg-green-100 text-green-700'
                    : sessionTrend === 'declining'
                    ? 'bg-red-100 text-red-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {sessionTrend === 'improving' && <ArrowUpRight className="w-4 h-4" />}
                  {sessionTrend === 'declining' && <ArrowDownRight className="w-4 h-4" />}
                  {sessionTrend === 'stable' && <ArrowRight className="w-4 h-4" />}
                  <span className="text-sm font-medium">
                    {session.duration_seconds ? `${Math.round(session.duration_seconds / 60)} dk` : '-'}
                  </span>
                </div>
              </div>
            );
          })}
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
