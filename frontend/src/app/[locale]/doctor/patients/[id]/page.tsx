'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import {
  useDoctorPatient,
  usePatientTimeline,
  usePatientNotes,
  useCreateNote,
  useRelativeInvitations,
  useInviteRelative,
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
  UserPlus,
  Mail,
  CheckCircle,
  XCircle,
  Copy,
  Users,
} from 'lucide-react';

type Tab = 'timeline' | 'notes' | 'relatives';

const timelineIcons: Record<string, { icon: typeof Brain; color: string }> = {
  migraine_attack: { icon: Brain, color: 'text-red-500' },
  task_completion: { icon: ListTodo, color: 'text-green-500' },
  symptom_entry: { icon: Activity, color: 'text-blue-500' },
  medication_log: { icon: Pill, color: 'text-purple-500' },
  doctor_note: { icon: MessageSquare, color: 'text-gray-500' },
};

const RELATIONSHIP_LABELS: Record<string, string> = {
  child: 'Cocuk',
  spouse: 'Es',
  sibling: 'Kardes',
  grandchild: 'Torun',
  other: 'Diger',
};

export default function DoctorPatientDetailPage() {
  const t = useTranslations();
  const params = useParams() as { locale: string; id: string };
  const patientId = params.id;

  const [activeTab, setActiveTab] = useState<Tab>('timeline');
  const [noteContent, setNoteContent] = useState('');
  const [noteType, setNoteType] = useState('general');

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRelType, setInviteRelType] = useState('child');
  const [inviteSuccess, setInviteSuccess] = useState<{ url: string; emailSent: boolean } | null>(null);
  const [inviteError, setInviteError] = useState('');
  const [copied, setCopied] = useState(false);

  const { data: patient, isLoading: patientLoading } = useDoctorPatient(patientId);
  const { data: timeline, isLoading: timelineLoading } = usePatientTimeline(patientId);
  const { data: notes, isLoading: notesLoading } = usePatientNotes(patientId);
  const createNote = useCreateNote();
  const { data: invitations, isLoading: invitationsLoading } = useRelativeInvitations(patientId);
  const inviteRelative = useInviteRelative();

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

  const handleInviteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteError('');
    setInviteSuccess(null);

    try {
      const result = await inviteRelative.mutateAsync({
        patient_id: patientId,
        invited_email: inviteEmail,
        invited_name: inviteName,
        relationship_type: inviteRelType,
      });
      setInviteSuccess({ url: result.invite_url, emailSent: result.email_sent });
      setInviteEmail('');
      setInviteName('');
      setInviteRelType('child');
    } catch (err: any) {
      const msg = err?.response?.data?.invited_email?.[0]
        || err?.response?.data?.error
        || err?.response?.data?.detail
        || 'Davet olusturulamadi.';
      setInviteError(msg);
    }
  };

  const copyLink = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
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
          <button
            onClick={() => setActiveTab('relatives')}
            className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 ${
              activeTab === 'relatives'
                ? 'border-teal-600 text-teal-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="h-4 w-4" />
            Hasta Yakinlari
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
                      {createNote.isPending ? 'Gönderiliyor...' : 'Gönder'}
                    </button>
                  </div>
                </form>
              </div>
            </>
          )}
        </div>
      )}

      {/* Relatives Tab */}
      {activeTab === 'relatives' && (
        <div className="space-y-6">
          {/* Info Banner */}
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Users className="h-5 w-5 text-teal-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-teal-800">Hasta Yakini Davet Sistemi</h3>
                <p className="text-sm text-teal-700 mt-1">
                  Hastanin cocugu veya yakini, hastanin durumunu uzaktan takip edebilir.
                  Davet linki ile guvenli kayit olur ve yalnizca bu hastanin bilissel verilerine
                  salt-okunur erisim saglar.
                </p>
              </div>
            </div>
          </div>

          {/* Invite Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <UserPlus className="h-5 w-5 text-teal-600" />
              Yeni Yakin Davet Et
            </h3>

            {inviteSuccess && (
              <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="text-sm font-medium text-green-800">
                    Davet basariyla olusturuldu!
                  </span>
                </div>
                {inviteSuccess.emailSent ? (
                  <p className="text-sm text-green-700">
                    Davet e-postasi gonderildi. Yakin, e-postadaki linke tiklayarak kayit olabilir.
                  </p>
                ) : (
                  <p className="text-sm text-yellow-700">
                    E-posta gonderilemedi. Asagidaki linki yakinla manuel olarak paylasiniz:
                  </p>
                )}
                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={inviteSuccess.url}
                    className="flex-1 px-3 py-2 bg-white border border-green-300 rounded-lg text-xs text-gray-600 font-mono"
                  />
                  <button
                    onClick={() => copyLink(inviteSuccess.url)}
                    className="inline-flex items-center gap-1 px-3 py-2 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 transition"
                  >
                    <Copy className="h-3.5 w-3.5" />
                    {copied ? 'Kopyalandi!' : 'Kopyala'}
                  </button>
                </div>
              </div>
            )}

            {inviteError && (
              <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <span className="text-sm text-red-700">{inviteError}</span>
              </div>
            )}

            <form onSubmit={handleInviteSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    E-posta Adresi *
                  </label>
                  <input
                    type="email"
                    required
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="yakin@email.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ad Soyad
                  </label>
                  <input
                    type="text"
                    value={inviteName}
                    onChange={(e) => setInviteName(e.target.value)}
                    placeholder="Opsiyonel"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Yakinlik Derecesi
                </label>
                <select
                  value={inviteRelType}
                  onChange={(e) => setInviteRelType(e.target.value)}
                  className="w-full md:w-auto px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                >
                  <option value="child">Cocuk</option>
                  <option value="spouse">Es</option>
                  <option value="sibling">Kardes</option>
                  <option value="grandchild">Torun</option>
                  <option value="other">Diger</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={!inviteEmail.trim() || inviteRelative.isPending}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-teal-600 text-white text-sm font-medium rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Mail className="h-4 w-4" />
                {inviteRelative.isPending ? 'Gönderiliyor...' : 'Davet Gönder'}
              </button>
            </form>
          </div>

          {/* Existing Invitations */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Gönderilen Davetler</h3>

            {invitationsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-teal-600" />
              </div>
            ) : !invitations || invitations.length === 0 ? (
              <div className="text-center py-8">
                <Mail className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">Henuz davet gonderilmemis.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {invitations.map((inv) => (
                  <div
                    key={inv.id}
                    className={`flex items-center justify-between p-4 rounded-lg border ${
                      inv.status === 'active'
                        ? 'bg-teal-50 border-teal-200'
                        : inv.status === 'used'
                        ? 'bg-green-50 border-green-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-900">
                          {inv.invited_name || inv.invited_email}
                        </span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          inv.status === 'active'
                            ? 'bg-teal-100 text-teal-700'
                            : inv.status === 'used'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {inv.status === 'active' ? 'Bekliyor' : inv.status === 'used' ? 'Kayıt Oldu' : 'Süresi Doldu'}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                        <span>{inv.invited_email}</span>
                        <span>{RELATIONSHIP_LABELS[inv.relationship_type] || inv.relationship_type}</span>
                        <span>
                          {new Date(inv.created_at).toLocaleDateString('tr-TR', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </span>
                      </div>
                    </div>
                    {inv.status === 'active' && (
                      <button
                        onClick={() => copyLink(`${window.location.origin}/tr/auth/register-relative?token=${inv.token}`)}
                        className="ml-3 p-2 text-teal-600 hover:bg-teal-100 rounded-lg transition"
                        title="Linki Kopyala"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
