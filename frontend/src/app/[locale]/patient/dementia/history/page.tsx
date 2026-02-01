'use client';

import { useState } from 'react';
import { Link } from '@/i18n/navigation';
import { useDailyAssessments, useAssessmentChart, type DailyAssessment } from '@/hooks/useDementiaData';
import {
  ArrowLeft,
  Calendar,
  TrendingUp,
  TrendingDown,
  Minus,
  Moon,
  Heart,
  Brain,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const MOOD_EMOJIS = ['', '😢', '😕', '😐', '🙂', '😊'];

export default function HistoryPage() {
  const { data: assessments, isLoading } = useDailyAssessments();
  const { data: chartData } = useAssessmentChart(30);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Calculate trends
  const getTrend = (current: number | null, previous: number | null, inverse = false) => {
    if (current === null || previous === null) return 'stable';
    const diff = current - previous;
    if (Math.abs(diff) < 0.5) return 'stable';
    if (inverse) {
      return diff > 0 ? 'declining' : 'improving';
    }
    return diff > 0 ? 'improving' : 'declining';
  };

  // Calculate averages from recent assessments
  const recentAssessments = assessments?.slice(0, 7) || [];
  const olderAssessments = assessments?.slice(7, 14) || [];

  const calcAvg = (items: DailyAssessment[], field: keyof DailyAssessment) => {
    const values = items.map((a) => a[field]).filter((v) => v !== null) as number[];
    if (values.length === 0) return null;
    return values.reduce((a, b) => a + b, 0) / values.length;
  };

  const stats = {
    mood: {
      current: calcAvg(recentAssessments, 'mood_score'),
      previous: calcAvg(olderAssessments, 'mood_score'),
    },
    sleep: {
      current: calcAvg(recentAssessments, 'sleep_quality'),
      previous: calcAvg(olderAssessments, 'sleep_quality'),
    },
    confusion: {
      current: calcAvg(recentAssessments, 'confusion_level'),
      previous: calcAvg(olderAssessments, 'confusion_level'),
    },
    anxiety: {
      current: calcAvg(recentAssessments, 'anxiety_level'),
      previous: calcAvg(olderAssessments, 'anxiety_level'),
    },
  };

  const TrendIcon = ({ trend }: { trend: 'improving' | 'declining' | 'stable' }) => {
    if (trend === 'improving') return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (trend === 'declining') return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/patient/dementia"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Değerlendirme Geçmişi</h1>
          <p className="text-sm text-gray-500">Son 30 günlük değerlendirmeler</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-pink-600">
              <Heart className="w-4 h-4" />
              <span className="text-xs font-medium">Ruh Hali</span>
            </div>
            <TrendIcon trend={getTrend(stats.mood.current, stats.mood.previous)} />
          </div>
          <div className="text-2xl">
            {stats.mood.current ? MOOD_EMOJIS[Math.round(stats.mood.current)] : '-'}
          </div>
          <div className="text-xs text-gray-500">
            Ort: {stats.mood.current?.toFixed(1) || '-'}/5
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-indigo-600">
              <Moon className="w-4 h-4" />
              <span className="text-xs font-medium">Uyku</span>
            </div>
            <TrendIcon trend={getTrend(stats.sleep.current, stats.sleep.previous)} />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.sleep.current?.toFixed(1) || '-'}
          </div>
          <div className="text-xs text-gray-500">Kalite (1-5)</div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-purple-600">
              <Brain className="w-4 h-4" />
              <span className="text-xs font-medium">Konfüzyon</span>
            </div>
            <TrendIcon trend={getTrend(stats.confusion.current, stats.confusion.previous, true)} />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.confusion.current?.toFixed(1) || '-'}
          </div>
          <div className="text-xs text-gray-500">Seviye (1-5)</div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-yellow-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-xs font-medium">Kaygı</span>
            </div>
            <TrendIcon trend={getTrend(stats.anxiety.current, stats.anxiety.previous, true)} />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {stats.anxiety.current?.toFixed(1) || '-'}
          </div>
          <div className="text-xs text-gray-500">Seviye (1-5)</div>
        </div>
      </div>

      {/* Chart placeholder */}
      {chartData && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Son 30 Gün Trendi</h3>
          <div className="h-40 flex items-end gap-1">
            {chartData.map((day: { date: string; mood_score: number | null }, index: number) => (
              <div
                key={index}
                className="flex-1 bg-indigo-100 rounded-t hover:bg-indigo-200 transition relative group"
                style={{
                  height: day.mood_score ? `${(day.mood_score / 5) * 100}%` : '10%',
                  backgroundColor: day.mood_score ? undefined : '#f3f4f6',
                }}
              >
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">
                  {new Date(day.date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                  {day.mood_score && `: ${day.mood_score}/5`}
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

      {/* Assessment List */}
      <h3 className="text-sm font-semibold text-gray-900 mb-3">Tüm Değerlendirmeler</h3>

      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Yükleniyor...</div>
      ) : !assessments || assessments.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Henüz değerlendirme yapılmamış.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {assessments.map((assessment) => (
            <AssessmentCard
              key={assessment.id}
              assessment={assessment}
              isExpanded={expandedId === assessment.id}
              onToggle={() => setExpandedId(expandedId === assessment.id ? null : assessment.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AssessmentCard({
  assessment,
  isExpanded,
  onToggle,
}: {
  assessment: DailyAssessment;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const hasIncident = assessment.fall_occurred || assessment.wandering_occurred || assessment.medication_missed;

  return (
    <div className={`bg-white rounded-xl border overflow-hidden ${
      hasIncident ? 'border-red-200' : 'border-gray-200'
    }`}>
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-2xl">
              {assessment.mood_score ? MOOD_EMOJIS[assessment.mood_score] : '😐'}
            </div>
          </div>
          <div className="text-left">
            <div className="font-medium text-gray-900">
              {new Date(assessment.assessment_date).toLocaleDateString('tr-TR', {
                weekday: 'long',
                day: 'numeric',
                month: 'long',
              })}
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              {assessment.sleep_hours && (
                <span className="flex items-center gap-1">
                  <Moon className="w-3 h-3" />
                  {assessment.sleep_hours}s uyku
                </span>
              )}
              {hasIncident && (
                <span className="flex items-center gap-1 text-red-500">
                  <AlertTriangle className="w-3 h-3" />
                  Olay var
                </span>
              )}
            </div>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-gray-100">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Ruh Hali</div>
              <div className="font-medium">{assessment.mood_score || '-'}/5</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Uyku Kalitesi</div>
              <div className="font-medium">{assessment.sleep_quality || '-'}/5</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Kaygı</div>
              <div className="font-medium">{assessment.anxiety_level || '-'}/5</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Konfüzyon</div>
              <div className="font-medium">{assessment.confusion_level || '-'}/5</div>
            </div>
          </div>

          {/* ADL Scores */}
          <div className="mb-4">
            <div className="text-xs font-medium text-gray-500 mb-2">Günlük Aktiviteler (1-5)</div>
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-500">Yemek</div>
                <div className="font-medium">{assessment.eating_independence || '-'}</div>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-500">Giyinme</div>
                <div className="font-medium">{assessment.dressing_independence || '-'}</div>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-500">Hijyen</div>
                <div className="font-medium">{assessment.hygiene_independence || '-'}</div>
              </div>
              <div className="p-2 bg-gray-50 rounded">
                <div className="text-gray-500">Hareket</div>
                <div className="font-medium">{assessment.mobility_independence || '-'}</div>
              </div>
            </div>
          </div>

          {/* Incidents */}
          {hasIncident && (
            <div className="flex flex-wrap gap-2 mb-4">
              {assessment.fall_occurred && (
                <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                  Düşme
                </span>
              )}
              {assessment.wandering_occurred && (
                <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                  Kaybolma/Dolaşma
                </span>
              )}
              {assessment.medication_missed && (
                <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                  İlaç Atlandı
                </span>
              )}
            </div>
          )}

          {/* Notes */}
          {assessment.notes && (
            <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg mb-2">
              <span className="font-medium">Not:</span> {assessment.notes}
            </div>
          )}
          {assessment.concerns && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">
              <span className="font-medium">Endişe:</span> {assessment.concerns}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
