'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Link } from '@/i18n/navigation';
import { useDoctorPatient, useDementiaReport } from '@/hooks/useDoctorData';
import {
  ArrowLeft,
  Brain,
  Activity,
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  FileText,
  Download,
  ChevronDown,
  ChevronUp,
  Moon,
  Heart,
  User,
  Flag,
  CheckCircle,
} from 'lucide-react';

const MOOD_EMOJIS = ['', '😢', '😕', '😐', '🙂', '😊'];

export default function DementiaReportPage() {
  const params = useParams() as { id: string };
  const patientId = params.id;

  const [days, setDays] = useState(30);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    exercises: true,
    assessments: true,
    notes: true,
  });

  const { data: patient, isLoading: patientLoading } = useDoctorPatient(patientId);
  const { data: report, isLoading: reportLoading } = useDementiaReport(patientId, days);

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  if (patientLoading || reportLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!patient || !report) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <Link
          href={`/doctor/patients/${patientId}`}
          className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Geri Dön
        </Link>
        <p className="text-gray-500">Rapor yüklenemedi.</p>
      </div>
    );
  }

  const { exercise_summary, assessment_summary, caregiver_notes, weekly_performance } = report;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            href={`/doctor/patients/${patientId}`}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Demans İlerleme Raporu</h1>
            <p className="text-gray-500">{patient.full_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value={7}>Son 7 gün</option>
            <option value={14}>Son 14 gün</option>
            <option value={30}>Son 30 gün</option>
            <option value={60}>Son 60 gün</option>
            <option value={90}>Son 90 gün</option>
          </select>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
          >
            <Download className="h-4 w-4" />
            Yazdır / PDF
          </button>
        </div>
      </div>

      {/* Report Period */}
      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6">
        <div className="flex items-center gap-2 text-indigo-700">
          <Calendar className="h-5 w-5" />
          <span className="font-medium">Rapor Dönemi:</span>
          <span>
            {new Date(report.report_period.start_date).toLocaleDateString('tr-TR')} -{' '}
            {new Date(report.report_period.end_date).toLocaleDateString('tr-TR')}
          </span>
          <span className="text-indigo-500">({report.report_period.days} gün)</span>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Brain className="h-5 w-5" />
            <span className="text-sm font-medium">Egzersiz</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{exercise_summary.total_sessions}</div>
          <div className="text-xs text-gray-500">toplam oturum</div>
          {exercise_summary.avg_accuracy && (
            <div className="mt-2 text-sm">
              <span className="text-gray-500">Ort. başarı: </span>
              <span className={`font-medium ${
                exercise_summary.avg_accuracy >= 70 ? 'text-green-600' :
                exercise_summary.avg_accuracy >= 50 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                %{exercise_summary.avg_accuracy}
              </span>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-pink-600 mb-2">
            <Heart className="h-5 w-5" />
            <span className="text-sm font-medium">Ruh Hali</span>
          </div>
          <div className="text-2xl">
            {assessment_summary.avg_mood_score
              ? MOOD_EMOJIS[Math.round(assessment_summary.avg_mood_score)]
              : '-'}
          </div>
          <div className="text-xs text-gray-500">
            Ort: {assessment_summary.avg_mood_score?.toFixed(1) || '-'}/5
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-purple-600 mb-2">
            <Activity className="h-5 w-5" />
            <span className="text-sm font-medium">Değerlendirme</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{assessment_summary.total_assessments}</div>
          <div className="text-xs text-gray-500">günlük form</div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-red-600 mb-2">
            <AlertTriangle className="h-5 w-5" />
            <span className="text-sm font-medium">Olaylar</span>
          </div>
          <div className="flex gap-4 text-sm">
            <div>
              <span className="font-bold text-gray-900">{assessment_summary.incidents.falls}</span>
              <span className="text-gray-500 ml-1">düşme</span>
            </div>
            <div>
              <span className="font-bold text-gray-900">{assessment_summary.incidents.wanderings}</span>
              <span className="text-gray-500 ml-1">kaybolma</span>
            </div>
          </div>
        </div>
      </div>

      {/* Exercise Section */}
      <CollapsibleSection
        title="Bilişsel Egzersiz Performansı"
        icon={Brain}
        isExpanded={expandedSections.exercises}
        onToggle={() => toggleSection('exercises')}
      >
        {/* Weekly Performance Chart */}
        {weekly_performance.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Haftalık Performans</h4>
            <div className="flex items-end gap-2 h-32">
              {weekly_performance.reverse().map((week, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-indigo-100 rounded-t hover:bg-indigo-200 transition relative group"
                    style={{
                      height: week.avg_accuracy ? `${week.avg_accuracy}%` : '10%',
                      backgroundColor: week.avg_accuracy ? undefined : '#f3f4f6',
                    }}
                  >
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none z-10">
                      {week.sessions_count} oturum
                      {week.avg_accuracy && ` - %${week.avg_accuracy}`}
                    </div>
                  </div>
                  <span className="text-xs text-gray-500 mt-1">H{4 - idx}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Exercise by Type */}
        {exercise_summary.by_type.length > 0 && (
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Kategorilere Göre</h4>
            <div className="space-y-3">
              {exercise_summary.by_type.map((type) => (
                <div key={type.type}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-700">{type.type_display}</span>
                    <span className="text-sm font-medium text-gray-900">
                      %{type.avg_score} ({type.count} oturum)
                    </span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        type.avg_score >= 70 ? 'bg-green-500' :
                        type.avg_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${type.avg_score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recent Sessions */}
        {report.recent_sessions.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Son Egzersizler</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 font-medium text-gray-500">Tarih</th>
                    <th className="text-left py-2 font-medium text-gray-500">Egzersiz</th>
                    <th className="text-left py-2 font-medium text-gray-500">Tür</th>
                    <th className="text-right py-2 font-medium text-gray-500">Başarı</th>
                    <th className="text-right py-2 font-medium text-gray-500">Süre</th>
                  </tr>
                </thead>
                <tbody>
                  {report.recent_sessions.map((session) => (
                    <tr key={session.id} className="border-b border-gray-100">
                      <td className="py-2 text-gray-600">
                        {new Date(session.date).toLocaleDateString('tr-TR', {
                          day: 'numeric',
                          month: 'short',
                        })}
                      </td>
                      <td className="py-2 text-gray-900">{session.exercise_name}</td>
                      <td className="py-2 text-gray-500">{session.exercise_type}</td>
                      <td className={`py-2 text-right font-medium ${
                        (session.accuracy ?? 0) >= 70 ? 'text-green-600' :
                        (session.accuracy ?? 0) >= 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {session.accuracy ? `%${session.accuracy}` : '-'}
                      </td>
                      <td className="py-2 text-right text-gray-500">
                        {session.duration_minutes ? `${session.duration_minutes} dk` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </CollapsibleSection>

      {/* Assessment Section */}
      <CollapsibleSection
        title="Günlük Değerlendirmeler"
        icon={Activity}
        isExpanded={expandedSections.assessments}
        onToggle={() => toggleSection('assessments')}
      >
        {/* ADL Scores */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Günlük Yaşam Aktiviteleri (GYA)</h4>
          <div className="grid grid-cols-5 gap-4">
            {[
              { key: 'eating', label: 'Yemek', icon: '🍽️' },
              { key: 'dressing', label: 'Giyinme', icon: '👔' },
              { key: 'hygiene', label: 'Hijyen', icon: '🚿' },
              { key: 'mobility', label: 'Hareket', icon: '🚶' },
              { key: 'communication', label: 'İletişim', icon: '💬' },
            ].map((item) => {
              const score = assessment_summary.adl_scores[item.key as keyof typeof assessment_summary.adl_scores];
              return (
                <div key={item.key} className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl mb-1">{item.icon}</div>
                  <div className="text-xs text-gray-500 mb-1">{item.label}</div>
                  <div className={`text-lg font-bold ${
                    (score ?? 0) >= 4 ? 'text-green-600' :
                    (score ?? 0) >= 3 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {score?.toFixed(1) || '-'}
                  </div>
                  <div className="text-xs text-gray-400">/5</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Assessments */}
        {report.recent_assessments.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Son Değerlendirmeler</h4>
            <div className="space-y-2">
              {report.recent_assessments.map((assessment, idx) => (
                <div key={idx} className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      {new Date(assessment.date).toLocaleDateString('tr-TR', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'short',
                      })}
                    </span>
                    <div className="flex items-center gap-3 text-sm">
                      <span>{assessment.mood_score ? MOOD_EMOJIS[assessment.mood_score] : '-'}</span>
                      {assessment.sleep_hours && (
                        <span className="flex items-center gap-1 text-gray-500">
                          <Moon className="h-3 w-3" />
                          {assessment.sleep_hours}s
                        </span>
                      )}
                    </div>
                  </div>
                  {(assessment.fall_occurred || assessment.wandering_occurred || assessment.medication_missed) && (
                    <div className="flex gap-2 mb-2">
                      {assessment.fall_occurred && (
                        <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">Düşme</span>
                      )}
                      {assessment.wandering_occurred && (
                        <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs rounded-full">Kaybolma</span>
                      )}
                      {assessment.medication_missed && (
                        <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">İlaç Atlandı</span>
                      )}
                    </div>
                  )}
                  {assessment.concerns && (
                    <p className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      <span className="font-medium">Endişe:</span> {assessment.concerns}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CollapsibleSection>

      {/* Caregiver Notes Section */}
      <CollapsibleSection
        title={`Bakıcı Notları (${caregiver_notes.unreviewed} incelenmemiş)`}
        icon={FileText}
        isExpanded={expandedSections.notes}
        onToggle={() => toggleSection('notes')}
        badge={caregiver_notes.unreviewed > 0 ? 'warning' : undefined}
      >
        {caregiver_notes.notes.length === 0 ? (
          <p className="text-gray-500 text-center py-4">Doktora iletilen not bulunmuyor.</p>
        ) : (
          <div className="space-y-3">
            {caregiver_notes.notes.map((note) => (
              <div
                key={note.id}
                className={`p-4 rounded-lg border ${
                  note.doctor_reviewed
                    ? 'bg-gray-50 border-gray-200'
                    : 'bg-yellow-50 border-yellow-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      note.severity === 3 ? 'bg-red-100 text-red-700' :
                      note.severity === 2 ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {note.severity === 3 ? 'Yüksek' : note.severity === 2 ? 'Orta' : 'Düşük'}
                    </span>
                    <h4 className="font-medium text-gray-900">{note.title}</h4>
                  </div>
                  {note.doctor_reviewed ? (
                    <span className="flex items-center gap-1 text-green-600 text-xs">
                      <CheckCircle className="h-3 w-3" />
                      İncelendi
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-yellow-600 text-xs">
                      <Flag className="h-3 w-3" />
                      İncelenmedi
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mb-2">{note.content}</p>
                <span className="text-xs text-gray-400">
                  {new Date(note.created_at).toLocaleDateString('tr-TR', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .print-area, .print-area * {
            visibility: visible;
          }
          .print-area {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          button, select {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}

function CollapsibleSection({
  title,
  icon: Icon,
  isExpanded,
  onToggle,
  badge,
  children,
}: {
  title: string;
  icon: typeof Brain;
  isExpanded: boolean;
  onToggle: () => void;
  badge?: 'warning' | 'success';
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 mb-4 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition"
      >
        <div className="flex items-center gap-3">
          <Icon className="h-5 w-5 text-indigo-600" />
          <span className="font-semibold text-gray-900">{title}</span>
          {badge === 'warning' && (
            <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>
      {isExpanded && <div className="px-5 pb-5">{children}</div>}
    </div>
  );
}
