'use client';

import { useState } from 'react';
import { Link } from '@/i18n/navigation';
import {
  useRelativePatient,
  useRelativeNotes,
  useRelativeAssessments,
  useRelativeAlerts,
} from '@/hooks/useRelativeData';
import {
  Brain,
  Heart,
  ClipboardList,
  AlertTriangle,
  Eye,
  Calendar,
  ChevronDown,
  ChevronUp,
  Activity,
  Shield,
  UserCheck,
  Pill,
  Footprints,
  Wind,
} from 'lucide-react';

const MOOD_EMOJIS = ['', '\u{1F622}', '\u{1F615}', '\u{1F610}', '\u{1F642}', '\u{1F60A}'];
const SEVERITY_COLORS: Record<number, string> = {
  1: 'bg-blue-50 border-blue-200 text-blue-800',
  2: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  3: 'bg-red-50 border-red-200 text-red-800',
};

export default function RelativeDashboardPage() {
  const { data: patient, isLoading: loadingPatient, isError: errorPatient } = useRelativePatient();
  const { data: notes, isLoading: loadingNotes } = useRelativeNotes();
  const { data: assessments, isLoading: loadingAssessments } = useRelativeAssessments();
  const { data: alerts } = useRelativeAlerts();

  const [activeTab, setActiveTab] = useState<'overview' | 'notes' | 'assessments'>('overview');

  if (loadingPatient) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-pulse text-gray-500">Yukleniyor...</div>
      </div>
    );
  }

  if (errorPatient || !patient) {
    return (
      <div className="max-w-lg mx-auto py-12">
        <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-8 text-center">
          <Shield className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Hasta Bağlantısı Bulunamadı</h2>
          <p className="text-gray-600">
            Onaylanmış bir hasta bağlantınız bulunmuyor. Lütfen doktorunuz veya bakıcınız ile iletişime geçin.
          </p>
        </div>
      </div>
    );
  }

  const hasAlerts = alerts && alerts.length > 0;
  const criticalAlerts = alerts?.filter((a) => a.severity >= 3) ?? [];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Eye className="w-7 h-7 text-teal-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Hasta Takibi</h1>
          <p className="text-sm text-gray-500">
            {patient.first_name} {patient.last_name} - Uzaktan Izlem
          </p>
        </div>
      </div>

      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <div className="bg-red-50 border-2 border-red-300 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h3 className="font-semibold text-red-800">Acil Uyarilar</h3>
          </div>
          <div className="space-y-2">
            {criticalAlerts.map((alert, idx) => (
              <div key={idx} className="flex items-start gap-2 text-sm text-red-700">
                {alert.alert_type === 'fall' && <Footprints className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                {alert.alert_type === 'wandering' && <Wind className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                {alert.alert_type === 'medication' && <Pill className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                {alert.alert_type === 'flagged_note' && <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                <span>{alert.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Patient Status Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-teal-600 mb-1">
            <Brain className="w-4 h-4" />
            <span className="text-xs font-medium">Bilissel Skor</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {patient.latest_score ? `%${Math.round(patient.latest_score)}` : '-'}
          </div>
          <div className="text-xs text-gray-500">son deger</div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-indigo-600 mb-1">
            <Activity className="w-4 h-4" />
            <span className="text-xs font-medium">Bu Hafta</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{patient.exercises_this_week}</div>
          <div className="text-xs text-gray-500">egzersiz</div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-2 text-amber-600 mb-1">
            <Heart className="w-4 h-4" />
            <span className="text-xs font-medium">Ruh Hali</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {patient.today_mood ? MOOD_EMOJIS[patient.today_mood] : '-'}
          </div>
          <div className="text-xs text-gray-500">bugun</div>
        </div>

        <div className={`rounded-xl border-2 p-4 ${
          patient.recent_incidents > 0 ? 'bg-red-50 border-red-300' : 'bg-green-50 border-green-200'
        }`}>
          <div className={`flex items-center gap-2 mb-1 ${
            patient.recent_incidents > 0 ? 'text-red-600' : 'text-green-600'
          }`}>
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs font-medium">Olaylar</span>
          </div>
          <div className={`text-2xl font-bold ${
            patient.recent_incidents > 0 ? 'text-red-700' : 'text-green-700'
          }`}>
            {patient.recent_incidents}
          </div>
          <div className="text-xs text-gray-500">son 7 gun</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        {(['overview', 'notes', 'assessments'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition ${
              activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            {tab === 'overview' && <Eye className="w-4 h-4" />}
            {tab === 'notes' && <ClipboardList className="w-4 h-4" />}
            {tab === 'assessments' && <Calendar className="w-4 h-4" />}
            {tab === 'overview' && 'Genel Bakis'}
            {tab === 'notes' && 'Bakici Notlari'}
            {tab === 'assessments' && 'Gunluk Degerlendirme'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <OverviewTab alerts={alerts ?? []} notes={notes ?? []} assessments={assessments ?? []} />
      )}
      {activeTab === 'notes' && (
        <NotesTab notes={notes ?? []} isLoading={loadingNotes} />
      )}
      {activeTab === 'assessments' && (
        <AssessmentsTab assessments={assessments ?? []} isLoading={loadingAssessments} />
      )}

      {/* Info Notice */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <UserCheck className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-700">
            <p className="font-medium mb-1">Salt Okunur Erisim</p>
            <p>
              Hasta yakini olarak yalnizca izlem notlarini, gunluk degerlendirmeleri ve uyarilari
              gorebilirsiniz. Degisiklik yapmak icin bakici veya doktor ile iletisime gecin.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Overview Tab ───

function OverviewTab({
  alerts,
  notes,
  assessments,
}: {
  alerts: any[];
  notes: any[];
  assessments: any[];
}) {
  return (
    <div className="space-y-6">
      {/* Recent Alerts */}
      {alerts.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Son Uyarilar</h3>
          <div className="space-y-2">
            {alerts.slice(0, 5).map((alert, idx) => (
              <div key={idx} className={`rounded-lg border p-3 text-sm ${SEVERITY_COLORS[alert.severity] || SEVERITY_COLORS[1]}`}>
                <div className="flex items-center gap-2">
                  {alert.alert_type === 'fall' && <Footprints className="w-4 h-4" />}
                  {alert.alert_type === 'wandering' && <Wind className="w-4 h-4" />}
                  {alert.alert_type === 'medication' && <Pill className="w-4 h-4" />}
                  {alert.alert_type === 'flagged_note' && <AlertTriangle className="w-4 h-4" />}
                  <span className="font-medium">{alert.message}</span>
                </div>
                <div className="text-xs opacity-75 mt-1">
                  {new Date(alert.timestamp).toLocaleDateString('tr-TR', {
                    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Notes Preview */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Son Bakici Notlari</h3>
        {notes.length === 0 ? (
          <p className="text-sm text-gray-500">Henuz bakici notu yok.</p>
        ) : (
          <div className="space-y-2">
            {notes.slice(0, 3).map((note) => (
              <div key={note.id} className="bg-white rounded-lg border border-gray-200 p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-teal-600">{note.note_type_display}</span>
                  <span className="text-xs text-gray-400">
                    {new Date(note.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                  </span>
                </div>
                <h4 className="text-sm font-medium text-gray-900">{note.title}</h4>
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{note.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Assessments Preview */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Son Degerlendirmeler</h3>
        {assessments.length === 0 ? (
          <p className="text-sm text-gray-500">Henuz gunluk degerlendirme yok.</p>
        ) : (
          <div className="grid grid-cols-3 gap-3">
            {assessments.slice(0, 3).map((a) => (
              <div key={a.id} className="bg-white rounded-lg border border-gray-200 p-3 text-center">
                <div className="text-xs text-gray-500 mb-1">
                  {new Date(a.assessment_date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
                </div>
                <div className="text-2xl">{a.mood_score ? MOOD_EMOJIS[a.mood_score] : '-'}</div>
                <div className="flex items-center justify-center gap-1 mt-1">
                  {a.fall_occurred && <span className="text-[10px] bg-red-100 text-red-700 px-1 rounded">Dusme</span>}
                  {a.wandering_occurred && <span className="text-[10px] bg-orange-100 text-orange-700 px-1 rounded">Gezinme</span>}
                  {a.medication_missed && <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1 rounded">Ilac</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Notes Tab ───

function NotesTab({ notes, isLoading }: { notes: any[]; isLoading: boolean }) {
  const [expandedNote, setExpandedNote] = useState<string | null>(null);

  if (isLoading) return <div className="text-center py-8 text-gray-500">Yukleniyor...</div>;
  if (notes.length === 0) {
    return (
      <div className="text-center py-12">
        <ClipboardList className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Henuz bakici notu yok.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {notes.map((note) => {
        const isExpanded = expandedNote === note.id;
        return (
          <div key={note.id} className={`bg-white rounded-xl border-2 p-4 transition ${
            note.severity >= 3 ? 'border-red-200' : note.severity >= 2 ? 'border-yellow-200' : 'border-gray-200'
          }`}>
            <button
              onClick={() => setExpandedNote(isExpanded ? null : note.id)}
              className="w-full text-left"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    note.severity >= 3 ? 'bg-red-100 text-red-700'
                    : note.severity >= 2 ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-blue-100 text-blue-700'
                  }`}>
                    {note.note_type_display}
                  </span>
                  {note.is_flagged_for_doctor && (
                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                      Doktora Bildirildi
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">
                    {new Date(note.created_at).toLocaleDateString('tr-TR', {
                      day: 'numeric', month: 'short', year: 'numeric'
                    })}
                  </span>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                </div>
              </div>
              <h4 className="font-medium text-gray-900 mt-2">{note.title}</h4>
            </button>
            {isExpanded && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-sm text-gray-600 whitespace-pre-wrap">{note.content}</p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─── Assessments Tab ───

function AssessmentsTab({ assessments, isLoading }: { assessments: any[]; isLoading: boolean }) {
  if (isLoading) return <div className="text-center py-8 text-gray-500">Yukleniyor...</div>;
  if (assessments.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Henuz gunluk degerlendirme yok.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {assessments.map((a) => (
        <div key={a.id} className={`bg-white rounded-xl border-2 p-4 ${
          a.fall_occurred || a.wandering_occurred ? 'border-red-200' : 'border-gray-200'
        }`}>
          <div className="flex items-center justify-between mb-3">
            <span className="font-medium text-gray-900">
              {new Date(a.assessment_date).toLocaleDateString('tr-TR', {
                weekday: 'long', day: 'numeric', month: 'long'
              })}
            </span>
            <span className="text-2xl">{a.mood_score ? MOOD_EMOJIS[a.mood_score] : '-'}</span>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {a.confusion_level !== null && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">{a.confusion_level}/5</div>
                <div className="text-[10px] text-gray-500">Konfuzyon</div>
              </div>
            )}
            {a.anxiety_level !== null && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">{a.anxiety_level}/5</div>
                <div className="text-[10px] text-gray-500">Anksiyete</div>
              </div>
            )}
            {a.sleep_quality !== null && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">{a.sleep_quality}/5</div>
                <div className="text-[10px] text-gray-500">Uyku Kalitesi</div>
              </div>
            )}
            {a.sleep_hours !== null && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">{a.sleep_hours}s</div>
                <div className="text-[10px] text-gray-500">Uyku Suresi</div>
              </div>
            )}
          </div>

          {/* Incidents */}
          {(a.fall_occurred || a.wandering_occurred || a.medication_missed) && (
            <div className="mt-3 pt-3 border-t border-gray-100 flex flex-wrap gap-2">
              {a.fall_occurred && (
                <span className="flex items-center gap-1 text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full">
                  <Footprints className="w-3 h-3" /> Dusme Olayi
                </span>
              )}
              {a.wandering_occurred && (
                <span className="flex items-center gap-1 text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full">
                  <Wind className="w-3 h-3" /> Gezinme Olayi
                </span>
              )}
              {a.medication_missed && (
                <span className="flex items-center gap-1 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
                  <Pill className="w-3 h-3" /> Ilac Atlama
                </span>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
