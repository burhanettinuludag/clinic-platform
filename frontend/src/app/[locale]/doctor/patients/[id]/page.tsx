'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import {
  useDoctorPatient,
  usePatientTimeline,
  usePatientNotes,
  useCreateNote,
} from '@/hooks/useDoctorData';
import { Link } from '@/i18n/navigation';
import {
  ArrowLeft,
  Clock,
  AlertTriangle,
  Brain,
  Pill,
  ListTodo,
  Activity,
  MessageSquare,
  Send,
  FileText,
} from 'lucide-react';

type Tab = 'timeline' | 'notes';

const timelineIcons: Record<string, { icon: typeof Brain; color: string }> = {
  migraine_attack: { icon: Brain, color: 'text-red-500' },
  task_completion: { icon: ListTodo, color: 'text-green-500' },
  symptom_entry: { icon: Activity, color: 'text-blue-500' },
  medication_log: { icon: Pill, color: 'text-purple-500' },
  doctor_note: { icon: MessageSquare, color: 'text-gray-500' },
};

export default function DoctorPatientDetailPage() {
  const t = useTranslations();
  const params = useParams() as { locale: string; id: string };
  const patientId = params.id;

  const [activeTab, setActiveTab] = useState<Tab>('timeline');
  const [noteContent, setNoteContent] = useState('');
  const [noteType, setNoteType] = useState('general');

  const { data: patient, isLoading: patientLoading } = useDoctorPatient(patientId);
  const { data: timeline, isLoading: timelineLoading } = usePatientTimeline(patientId);
  const { data: notes, isLoading: notesLoading } = usePatientNotes(patientId);
  const createNote = useCreateNote();

  const handleSubmitNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteContent.trim()) return;

    await createNote.mutateAsync({
      patientId: patientId,
      content: noteContent,
      note_type: noteType,
    });

    setNoteContent('');
    setNoteType('general');
  };

  if (patientLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <Link
          href="/doctor/patients"
          className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Geri Don
        </Link>
        <p className="text-gray-500">Hasta bulunamadi.</p>
      </div>
    );
  }

  const sortedTimeline = timeline
    ? [...timeline].sort(
        (a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime()
      )
    : [];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Back Button */}
      <Link
        href="/doctor/patients"
        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Hastalara Don
      </Link>

      {/* Patient Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">{patient.full_name}</h1>
          <Link
            href={`/doctor/patients/${patientId}/dementia-report`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
          >
            <FileText className="h-4 w-4" />
            Demans Raporu
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">E-posta:</span>{' '}
            <span className="text-gray-900">{patient.email}</span>
          </div>
          <div>
            <span className="text-gray-500">Telefon:</span>{' '}
            <span className="text-gray-900">{patient.phone || '-'}</span>
          </div>
          <div>
            <span className="text-gray-500">Dogum Tarihi:</span>{' '}
            <span className="text-gray-900">
              {patient.date_of_birth
                ? new Date(patient.date_of_birth).toLocaleDateString('tr-TR')
                : '-'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Cinsiyet:</span>{' '}
            <span className="text-gray-900">{patient.gender || '-'}</span>
          </div>
          <div>
            <span className="text-gray-500">Acil Durum Irtibat:</span>{' '}
            <span className="text-gray-900">
              {patient.emergency_contact_name
                ? `${patient.emergency_contact_name} (${patient.emergency_contact_phone})`
                : '-'}
            </span>
          </div>
        </div>
      </div>

      {/* Alert Flags */}
      {patient.alert_flags && patient.alert_flags.length > 0 && (
        <div className="space-y-2 mb-6">
          {patient.alert_flags.map((flag: any, idx: number) => (
            <div
              key={idx}
              className={`flex items-center gap-2 p-3 rounded-lg ${
                flag.severity === 'critical'
                  ? 'bg-red-50 border border-red-200 text-red-800'
                  : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
              }`}
            >
              <AlertTriangle className="h-5 w-5 flex-shrink-0" />
              <span className="font-medium">{flag.message || flag.type}</span>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4">
          <button
            onClick={() => setActiveTab('timeline')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'timeline'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Timeline
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'notes'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Notlar
          </button>
        </nav>
      </div>

      {/* Timeline Tab */}
      {activeTab === 'timeline' && (
        <div>
          {timelineLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
            </div>
          ) : sortedTimeline.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="h-10 w-10 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">Henuz timeline verisi yok.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {sortedTimeline.map((entry: any, idx: number) => {
                const iconConfig = timelineIcons[entry.entry_type] || {
                  icon: Clock,
                  color: 'text-gray-400',
                };
                const IconComponent = iconConfig.icon;

                return (
                  <div
                    key={idx}
                    className="flex gap-4 bg-white rounded-lg shadow p-4"
                  >
                    <div
                      className={`flex-shrink-0 mt-1 ${iconConfig.color}`}
                    >
                      <IconComponent className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900">
                        {entry.title}
                      </h3>
                      {entry.detail && (
                        <p className="text-sm text-gray-500 mt-1">{entry.detail}</p>
                      )}
                      <p className="text-xs text-gray-400 mt-2">
                        {new Date(entry.date).toLocaleDateString('tr-TR', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {activeTab === 'notes' && (
        <div>
          {notesLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
            </div>
          ) : (
            <>
              {/* Existing Notes */}
              <div className="space-y-3 mb-8">
                {notes && notes.length > 0 ? (
                  notes.map((note: any, idx: number) => (
                    <div key={idx} className="bg-white rounded-lg shadow p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                          {note.note_type}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(note.created_at).toLocaleDateString('tr-TR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{note.content}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <MessageSquare className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">Henuz not eklenmemis.</p>
                  </div>
                )}
              </div>

              {/* Add Note Form */}
              <div className="bg-white rounded-lg shadow p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Not Ekle</h3>
                <form onSubmit={handleSubmitNote} className="space-y-3">
                  <textarea
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    placeholder="Notunuzu yazin..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                  <div className="flex items-center gap-3">
                    <select
                      value={noteType}
                      onChange={(e) => setNoteType(e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="general">Genel</option>
                      <option value="observation">Gozlem</option>
                      <option value="treatment">Tedavi</option>
                      <option value="follow_up">Takip</option>
                    </select>
                    <button
                      type="submit"
                      disabled={!noteContent.trim() || createNote.isPending}
                      className="inline-flex items-center gap-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <Send className="h-4 w-4" />
                      {createNote.isPending ? 'Gonderiliyor...' : 'Gonder'}
                    </button>
                  </div>
                </form>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
