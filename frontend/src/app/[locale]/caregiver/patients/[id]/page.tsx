'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import { useCaregiverPatientDetail } from '@/hooks/useCaregiverData';
import {
  ArrowLeft, Brain, Activity, FileText, ClipboardList,
  TrendingUp, AlertTriangle, Calendar, Clock, Target,
} from 'lucide-react';

type TabType = 'exercises' | 'assessments' | 'notes' | 'scores';

export default function CaregiverPatientDetailPage() {
  const params = useParams();
  const patientId = params.id as string;
  const [activeTab, setActiveTab] = useState<TabType>('exercises');

  const { data, isLoading } = useCaregiverPatientDetail(patientId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Yukleniyor...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12">
        <h1 className="text-xl font-bold text-gray-900 mb-2">Hasta Bulunamadi</h1>
        <Link
          href="/caregiver/dashboard"
          className="text-teal-600 hover:text-teal-700 flex items-center gap-2 justify-center"
        >
          <ArrowLeft className="w-4 h-4" />
          Panele Don
        </Link>
      </div>
    );
  }

  const { patient, recent_sessions, recent_assessments, recent_notes, cognitive_scores, latest_screening } = data;

  const tabs = [
    { key: 'exercises' as TabType, label: 'Egzersizler', icon: Activity, count: recent_sessions.length },
    { key: 'assessments' as TabType, label: 'Degerlendirmeler', icon: ClipboardList, count: recent_assessments.length },
    { key: 'notes' as TabType, label: 'Notlar', icon: FileText, count: recent_notes.length },
    { key: 'scores' as TabType, label: 'Skorlar', icon: TrendingUp, count: cognitive_scores.length },
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/caregiver/dashboard"
          className="p-2 hover:bg-gray-100 rounded-lg transition"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center">
            <span className="text-teal-700 font-bold">
              {patient.first_name[0]}{patient.last_name[0]}
            </span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              {patient.first_name} {patient.last_name}
            </h1>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Brain className="w-4 h-4" />
                Skor: {patient.latest_score !== null ? Math.round(Number(patient.latest_score)) : '-'}
              </span>
              <span className="flex items-center gap-1">
                <Target className="w-4 h-4" />
                Seri: {patient.streak_days} gun
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-purple-600">
            {patient.latest_score !== null ? Math.round(Number(patient.latest_score)) : '-'}
          </p>
          <p className="text-xs text-gray-500">Bilissel Skor</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{patient.exercises_today}</p>
          <p className="text-xs text-gray-500">Bugunun Egzersizi</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-blue-600">{patient.exercises_this_week}</p>
          <p className="text-xs text-gray-500">Haftalik Egzersiz</p>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-amber-600">{patient.streak_days}</p>
          <p className="text-xs text-gray-500">Gun Serisi</p>
        </div>
      </div>

      {/* Screening Summary */}
      {latest_screening && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-indigo-500" />
              <h3 className="font-semibold text-gray-900">Son Tarama Sonucu</h3>
            </div>
            <span className="text-xs text-gray-400">
              {new Date(latest_screening.assessment_date).toLocaleDateString('tr-TR')}
            </span>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <span className="text-2xl font-bold text-indigo-600">
              {Math.round(latest_screening.total_score)}%
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              latest_screening.interpretation === 'normal' ? 'bg-green-100 text-green-700' :
              latest_screening.interpretation === 'mild' ? 'bg-yellow-100 text-yellow-700' :
              latest_screening.interpretation === 'moderate' ? 'bg-orange-100 text-orange-700' :
              'bg-red-100 text-red-700'
            }`}>
              {latest_screening.interpretation_label}
            </span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-teal-600 text-teal-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.count > 0 && (
                <span className="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        {/* Exercises Tab */}
        {activeTab === 'exercises' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Son Egzersizler (7 Gun)</h3>
            {recent_sessions.length === 0 ? (
              <p className="text-gray-400 text-center py-8">Bu hafta egzersiz yapilmamis.</p>
            ) : (
              <div className="space-y-3">
                {recent_sessions.map((session) => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-green-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{session.exercise_name}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(session.started_at).toLocaleDateString('tr-TR', {
                            day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-gray-900">{session.score}</p>
                      <p className="text-xs text-gray-400">
                        {session.duration_seconds ? `${Math.floor(session.duration_seconds / 60)}dk` : '-'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Assessments Tab */}
        {activeTab === 'assessments' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Gunluk Degerlendirmeler</h3>
            {recent_assessments.length === 0 ? (
              <p className="text-gray-400 text-center py-8">Bu hafta degerlendirme yapilmamis.</p>
            ) : (
              <div className="space-y-3">
                {recent_assessments.map((assessment) => (
                  <div key={assessment.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">
                        {new Date(assessment.assessment_date).toLocaleDateString('tr-TR', {
                          day: 'numeric', month: 'long', year: 'numeric',
                        })}
                      </span>
                      <div className="flex gap-1">
                        {assessment.fall_occurred && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">Dusme</span>
                        )}
                        {assessment.wandering_occurred && (
                          <span className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded text-xs">Gezinme</span>
                        )}
                        {assessment.medication_missed && (
                          <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-xs">Ilac</span>
                        )}
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div>
                        <p className="text-xs text-gray-500">Ruh hali</p>
                        <p className="text-sm font-medium">{assessment.mood_score ?? '-'}/5</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Karisiklik</p>
                        <p className="text-sm font-medium">{assessment.confusion_level ?? '-'}/5</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500">Uyku</p>
                        <p className="text-sm font-medium">{assessment.sleep_quality ?? '-'}/5</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Notes Tab */}
        {activeTab === 'notes' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Bakici Notlari</h3>
            {recent_notes.length === 0 ? (
              <p className="text-gray-400 text-center py-8">Henuz not eklenmemis.</p>
            ) : (
              <div className="space-y-3">
                {recent_notes.map((note) => (
                  <div key={note.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {note.is_flagged_for_doctor && (
                          <AlertTriangle className="w-4 h-4 text-red-500" />
                        )}
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          note.severity >= 3 ? 'bg-red-100 text-red-700' :
                          note.severity === 2 ? 'bg-amber-100 text-amber-700' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                          {note.note_type_display}
                        </span>
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(note.created_at).toLocaleDateString('tr-TR')}
                      </span>
                    </div>
                    <h4 className="text-sm font-medium text-gray-900">{note.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{note.content}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Scores Tab */}
        {activeTab === 'scores' && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Bilissel Skorlar (Son 30 Gun)</h3>
            {cognitive_scores.length === 0 ? (
              <p className="text-gray-400 text-center py-8">Henuz skor hesaplanmamis.</p>
            ) : (
              <div className="space-y-3">
                {cognitive_scores.map((score) => (
                  <div key={score.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-gray-900 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        {new Date(score.score_date).toLocaleDateString('tr-TR')}
                      </span>
                      <span className="text-lg font-bold text-purple-600">
                        {score.overall_score !== null ? Math.round(Number(score.overall_score)) : '-'}
                      </span>
                    </div>
                    <div className="grid grid-cols-5 gap-2">
                      {[
                        { label: 'Bellek', value: score.memory_score, color: 'text-blue-600' },
                        { label: 'Dikkat', value: score.attention_score, color: 'text-green-600' },
                        { label: 'Dil', value: score.language_score, color: 'text-indigo-600' },
                        { label: 'P.Cozme', value: score.problem_solving_score, color: 'text-amber-600' },
                        { label: 'Yonelim', value: score.orientation_score, color: 'text-teal-600' },
                      ].map((domain) => (
                        <div key={domain.label} className="text-center">
                          <p className={`text-sm font-bold ${domain.color}`}>
                            {domain.value !== null ? Math.round(Number(domain.value)) : '-'}
                          </p>
                          <p className="text-[10px] text-gray-500">{domain.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
