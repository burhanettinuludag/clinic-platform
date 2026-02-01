'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  useCaregiverNotes,
  useCreateCaregiverNote,
  type CaregiverNote,
} from '@/hooks/useDementiaData';
import {
  ArrowLeft,
  Plus,
  X,
  FileText,
  AlertTriangle,
  TrendingUp,
  Activity,
  Pill,
  MessageSquare,
  Flag,
  CheckCircle,
  Clock,
} from 'lucide-react';

const NOTE_TYPES = [
  { value: 'observation', label: 'Gözlem', icon: FileText, color: 'blue' },
  { value: 'concern', label: 'Endişe', icon: AlertTriangle, color: 'yellow' },
  { value: 'improvement', label: 'İyileşme', icon: TrendingUp, color: 'green' },
  { value: 'incident', label: 'Olay', icon: Activity, color: 'red' },
  { value: 'medication', label: 'İlaç', icon: Pill, color: 'purple' },
  { value: 'behavior', label: 'Davranış', icon: MessageSquare, color: 'orange' },
  { value: 'other', label: 'Diğer', icon: FileText, color: 'gray' },
] as const;

const SEVERITY_LEVELS = [
  { value: 1, label: 'Düşük', color: 'green' },
  { value: 2, label: 'Orta', color: 'yellow' },
  { value: 3, label: 'Yüksek', color: 'red' },
];

export default function NotesPage() {
  const t = useTranslations();
  const { data: notes, isLoading } = useCaregiverNotes();
  const createNote = useCreateCaregiverNote();

  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  const filteredNotes = notes?.filter((note) => {
    if (filter === 'all') return true;
    if (filter === 'flagged') return note.is_flagged_for_doctor;
    return note.note_type === filter;
  });

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link
            href="/patient/dementia"
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Bakıcı Notları</h1>
            <p className="text-sm text-gray-500">Gözlem ve notlarınızı kaydedin</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition"
        >
          <Plus className="w-4 h-4" />
          Yeni Not
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
            filter === 'all'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Tümü
        </button>
        <button
          onClick={() => setFilter('flagged')}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
            filter === 'flagged'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          <Flag className="w-3.5 h-3.5" />
          Doktora İletilen
        </button>
        {NOTE_TYPES.slice(0, 4).map((type) => (
          <button
            key={type.value}
            onClick={() => setFilter(type.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
              filter === type.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* New Note Form */}
      {showForm && (
        <NoteForm
          onClose={() => setShowForm(false)}
          onSubmit={async (data) => {
            await createNote.mutateAsync(data);
            setShowForm(false);
          }}
          isLoading={createNote.isPending}
        />
      )}

      {/* Notes List */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">Yükleniyor...</div>
      ) : !filteredNotes || filteredNotes.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Henüz not eklenmemiş.</p>
          <p className="text-sm text-gray-400 mt-1">
            Gözlemlerinizi kaydetmek için &quot;Yeni Not&quot; butonunu kullanın.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotes.map((note) => (
            <NoteCard key={note.id} note={note} />
          ))}
        </div>
      )}
    </div>
  );
}

function NoteForm({
  onClose,
  onSubmit,
  isLoading,
}: {
  onClose: () => void;
  onSubmit: (data: {
    note_type: string;
    title: string;
    content: string;
    severity: number;
    is_flagged_for_doctor: boolean;
  }) => Promise<void>;
  isLoading: boolean;
}) {
  const [noteType, setNoteType] = useState('observation');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [severity, setSeverity] = useState(1);
  const [flagForDoctor, setFlagForDoctor] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      note_type: noteType,
      title,
      content,
      severity,
      is_flagged_for_doctor: flagForDoctor,
    });
  };

  return (
    <div className="bg-white rounded-xl border-2 border-indigo-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Yeni Not Ekle</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Note Type Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Not Türü
          </label>
          <div className="grid grid-cols-4 gap-2">
            {NOTE_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setNoteType(type.value)}
                  className={`flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition ${
                    noteType === type.value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${
                    noteType === type.value ? 'text-indigo-600' : 'text-gray-400'
                  }`} />
                  <span className={`text-xs ${
                    noteType === type.value ? 'text-indigo-600 font-medium' : 'text-gray-500'
                  }`}>
                    {type.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Title */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Başlık
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Kısa bir başlık girin..."
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        {/* Content */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            İçerik
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            rows={4}
            placeholder="Detaylı açıklama yazın..."
            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        {/* Severity */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Önem Derecesi
          </label>
          <div className="flex gap-2">
            {SEVERITY_LEVELS.map((level) => (
              <button
                key={level.value}
                type="button"
                onClick={() => setSeverity(level.value)}
                className={`flex-1 py-2 rounded-lg font-medium text-sm transition ${
                  severity === level.value
                    ? level.color === 'green'
                      ? 'bg-green-600 text-white'
                      : level.color === 'yellow'
                      ? 'bg-yellow-500 text-white'
                      : 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {level.label}
              </button>
            ))}
          </div>
        </div>

        {/* Flag for Doctor */}
        <div className="mb-6">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={flagForDoctor}
              onChange={(e) => setFlagForDoctor(e.target.checked)}
              className="w-5 h-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <div>
              <span className="text-sm font-medium text-gray-700">Doktora İlet</span>
              <p className="text-xs text-gray-500">
                Bu notu doktorun görmesi için işaretle
              </p>
            </div>
          </label>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={isLoading || !title || !content}
            className="flex-1 py-2.5 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {isLoading ? 'Kaydediliyor...' : 'Kaydet'}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            İptal
          </button>
        </div>
      </form>
    </div>
  );
}

function NoteCard({ note }: { note: CaregiverNote }) {
  const noteType = NOTE_TYPES.find((t) => t.value === note.note_type);
  const Icon = noteType?.icon || FileText;

  const getTypeColor = () => {
    switch (noteType?.color) {
      case 'blue': return 'bg-blue-100 text-blue-600';
      case 'yellow': return 'bg-yellow-100 text-yellow-600';
      case 'green': return 'bg-green-100 text-green-600';
      case 'red': return 'bg-red-100 text-red-600';
      case 'purple': return 'bg-purple-100 text-purple-600';
      case 'orange': return 'bg-orange-100 text-orange-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getSeverityBadge = () => {
    switch (note.severity) {
      case 3: return 'bg-red-100 text-red-700';
      case 2: return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-green-100 text-green-700';
    }
  };

  return (
    <div className={`bg-white rounded-xl border p-4 ${
      note.is_flagged_for_doctor && !note.doctor_reviewed
        ? 'border-red-200 border-2'
        : 'border-gray-200'
    }`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${getTypeColor()}`}>
          <Icon className="w-5 h-5" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <h3 className="font-medium text-gray-900">{note.title}</h3>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getSeverityBadge()}`}>
              {SEVERITY_LEVELS.find((l) => l.value === note.severity)?.label}
            </span>
            {note.is_flagged_for_doctor && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                <Flag className="w-3 h-3" />
                Doktora İletildi
              </span>
            )}
            {note.doctor_reviewed && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                <CheckCircle className="w-3 h-3" />
                İncelendi
              </span>
            )}
          </div>

          <p className="text-sm text-gray-600 mb-2">{note.content}</p>

          <div className="flex items-center gap-3 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(note.created_at).toLocaleDateString('tr-TR', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            {note.caregiver_name && (
              <span>Yazan: {note.caregiver_name}</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
