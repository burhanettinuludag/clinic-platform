'use client';

import { useState } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  useParkinsonDashboard,
  useParkinsonSymptoms,
  useParkinsonMedications,
  useCreateParkinsonSymptom,
  useCreateParkinsonMedication,
  useDeleteParkinsonSymptom,
  useDeleteParkinsonMedication,
  useTodayMedLogs,
  useTakeMedication,
  useLEDSummary,
  useParkinsonSymptomStats,
} from '@/hooks/useParkinsonData';
import {
  Activity,
  Plus,
  Pill,
  BarChart3,
  List,
  Clock,
  Check,
  X,
  Loader2,
  Bot,
  ChevronRight,
  BookOpen,
  ClipboardCheck,
  AlertTriangle,
  TrendingUp,
  Calendar,
  Trash2,
} from 'lucide-react';
import type { MotorState, DrugClass } from '@/lib/types/parkinson';

const MOTOR_STATES: { value: MotorState; label_tr: string; label_en: string; color: string }[] = [
  { value: 'on', label_tr: 'ON (İlaç etkili)', label_en: 'ON (Medication effective)', color: 'bg-green-100 text-green-700' },
  { value: 'off', label_tr: 'OFF (İlaç etkisiz)', label_en: 'OFF (Medication off)', color: 'bg-red-100 text-red-700' },
  { value: 'dyskinesia', label_tr: 'Diskinezi', label_en: 'Dyskinesia', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'wearing_off', label_tr: 'İlaç etkisi azalıyor', label_en: 'Wearing off', color: 'bg-orange-100 text-orange-700' },
];

const DRUG_CLASSES: { value: DrugClass; label_tr: string; label_en: string }[] = [
  { value: 'levodopa', label_tr: 'Levodopa / Karbidopa', label_en: 'Levodopa / Carbidopa' },
  { value: 'dopamine_agonist', label_tr: 'Dopamin Agonisti', label_en: 'Dopamine Agonist' },
  { value: 'mao_b_inhibitor', label_tr: 'MAO-B İnhibitörü', label_en: 'MAO-B Inhibitor' },
  { value: 'comt_inhibitor', label_tr: 'COMT İnhibitörü', label_en: 'COMT Inhibitor' },
  { value: 'amantadine', label_tr: 'Amantadin', label_en: 'Amantadine' },
  { value: 'anticholinergic', label_tr: 'Antikolinerjik', label_en: 'Anticholinergic' },
  { value: 'other', label_tr: 'Diğer', label_en: 'Other' },
];

const LED_FACTORS: Record<string, number> = {
  levodopa: 1,
  dopamine_agonist: 100,
  mao_b_inhibitor: 100,
  comt_inhibitor: 33,
  amantadine: 1,
  anticholinergic: 0,
  other: 0,
};

export default function ParkinsonPage() {
  const t = useTranslations();
  const locale = useLocale();
  const tr = (trText: string, enText: string) => (locale === 'tr' ? trText : enText);

  const [activeTab, setActiveTab] = useState<'overview' | 'diary' | 'medications' | 'today'>('overview');
  const [showSymptomForm, setShowSymptomForm] = useState(false);
  const [showMedForm, setShowMedForm] = useState(false);

  const dashboard = useParkinsonDashboard();
  const symptoms = useParkinsonSymptoms();
  const medications = useParkinsonMedications();
  const todayLogs = useTodayMedLogs();
  const ledSummary = useLEDSummary();
  const stats = useParkinsonSymptomStats();
  const createSymptom = useCreateParkinsonSymptom();
  const deleteSymptom = useDeleteParkinsonSymptom();
  const createMed = useCreateParkinsonMedication();
  const deleteMed = useDeleteParkinsonMedication();
  const takeMed = useTakeMedication();

  const tabs = [
    { key: 'overview' as const, label: tr('Genel Bakış', 'Overview'), icon: BarChart3 },
    { key: 'diary' as const, label: tr('Semptom Günlüğü', 'Symptom Diary'), icon: List },
    { key: 'medications' as const, label: tr('İlaçlarım', 'My Medications'), icon: Pill },
    { key: 'today' as const, label: tr('Bugünkü İlaçlar', 'Today\'s Meds'), icon: Clock },
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-teal-600" />
          <h1 className="text-2xl font-bold text-gray-900">{tr('Parkinson Takibi', 'Parkinson Tracking')}</h1>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/patient/parkinson/assessments"
            className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700 text-sm font-medium rounded-lg hover:bg-orange-200 transition"
          >
            <ClipboardCheck className="w-4 h-4" /> {tr('Testler', 'Assessments')}
          </Link>
          <Link
            href="/patient/parkinson/education"
            className="flex items-center gap-2 px-4 py-2 bg-teal-100 text-teal-700 text-sm font-medium rounded-lg hover:bg-teal-200 transition"
          >
            <BookOpen className="w-4 h-4" /> {tr('Eğitim', 'Education')}
          </Link>
        </div>
      </div>

      {/* AI Assistant Quick Link */}
      <Link
        href="/patient/ai-assistant"
        className="flex items-center gap-3 p-3 mb-4 bg-teal-50 border border-teal-200 rounded-xl hover:bg-teal-100 transition"
      >
        <div className="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4 text-teal-600" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-teal-800">
            {tr('Parkinson hakkında soru sorun', 'Ask questions about Parkinson\'s')}
          </p>
          <p className="text-xs text-teal-600">
            {tr('AI sağlık asistanı ile sohbet edin', 'Chat with AI health assistant')}
          </p>
        </div>
        <ChevronRight className="w-4 h-4 text-teal-400" />
      </Link>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-xl mb-6 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all flex-1 justify-center ${
                activeTab === tab.key
                  ? 'bg-white text-teal-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard
              label={tr('Aktif İlaç', 'Active Meds')}
              value={dashboard.data?.active_medications ?? 0}
              icon={<Pill className="w-5 h-5 text-blue-600" />}
              bg="bg-blue-50"
            />
            <StatCard
              label={tr('Günlük LED', 'Daily LED')}
              value={`${(dashboard.data?.total_daily_led ?? 0).toFixed(0)} mg`}
              icon={<TrendingUp className="w-5 h-5 text-green-600" />}
              bg="bg-green-50"
            />
            <StatCard
              label={tr('H&Y Evresi', 'H&Y Stage')}
              value={dashboard.data?.latest_hoehn_yahr?.stage ?? '-'}
              icon={<Activity className="w-5 h-5 text-purple-600" />}
              bg="bg-purple-50"
            />
            <StatCard
              label={tr('S&E Skoru', 'S&E Score')}
              value={dashboard.data?.latest_schwab_england ? `${dashboard.data.latest_schwab_england.score}%` : '-'}
              icon={<BarChart3 className="w-5 h-5 text-orange-600" />}
              bg="bg-orange-50"
            />
          </div>

          {/* ON/OFF Times */}
          {(dashboard.data?.avg_on_time || dashboard.data?.avg_off_time) && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">{tr('Son 30 Gün ON/OFF Ortalaması', 'Last 30 Days ON/OFF Average')}</h3>
              <div className="flex gap-4">
                <div className="flex-1 bg-green-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-green-700">
                    {dashboard.data?.avg_on_time?.toFixed(1) ?? '-'}
                  </p>
                  <p className="text-xs text-green-600">{tr('ON saat/gün', 'ON hours/day')}</p>
                </div>
                <div className="flex-1 bg-red-50 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-red-700">
                    {dashboard.data?.avg_off_time?.toFixed(1) ?? '-'}
                  </p>
                  <p className="text-xs text-red-600">{tr('OFF saat/gün', 'OFF hours/day')}</p>
                </div>
              </div>
            </div>
          )}

          {/* LED Summary */}
          {ledSummary.data && ledSummary.data.medications.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                {tr('Levodopa Eşdeğer Doz (LED)', 'Levodopa Equivalent Dose (LED)')}
              </h3>
              <div className="space-y-2">
                {ledSummary.data.medications.map((med, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{med.name}</span>
                    <span className="font-medium text-gray-900">{med.daily_led.toFixed(0)} mg</span>
                  </div>
                ))}
                <div className="border-t pt-2 flex items-center justify-between font-semibold">
                  <span>{tr('Toplam Günlük LED', 'Total Daily LED')}</span>
                  <span className="text-teal-700">{ledSummary.data.total_daily_led.toFixed(0)} mg</span>
                </div>
              </div>
            </div>
          )}

          {/* Next Visit */}
          {dashboard.data?.next_visit && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-1">
                <Calendar className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-semibold text-blue-800">{tr('Sonraki Randevu', 'Next Visit')}</h3>
              </div>
              <p className="text-sm text-blue-700">
                {new Date(dashboard.data.next_visit.visit_date).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US', {
                  day: 'numeric', month: 'long', year: 'numeric',
                })}
                {dashboard.data.next_visit.doctor_name && ` - ${dashboard.data.next_visit.doctor_name}`}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Symptom Diary Tab */}
      {activeTab === 'diary' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">{tr('Semptom Günlüğü', 'Symptom Diary')}</h2>
            <button
              onClick={() => setShowSymptomForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700"
            >
              <Plus className="w-4 h-4" /> {tr('Kayıt Ekle', 'Add Entry')}
            </button>
          </div>

          {/* Symptom Stats */}
          {stats.data && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-xl font-bold text-gray-900">{stats.data.last_30_days}</p>
                <p className="text-xs text-gray-500">{tr('Son 30 gün', 'Last 30 days')}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-xl font-bold text-gray-900">{stats.data.avg_overall_severity?.toFixed(1) ?? '-'}</p>
                <p className="text-xs text-gray-500">{tr('Ort. Şiddet', 'Avg. Severity')}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-xl font-bold text-gray-900">{stats.data.avg_tremor?.toFixed(1) ?? '-'}</p>
                <p className="text-xs text-gray-500">{tr('Ort. Tremor', 'Avg. Tremor')}</p>
              </div>
            </div>
          )}

          {/* Symptom List */}
          {symptoms.data?.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <Activity className="w-10 h-10 mx-auto text-gray-300 mb-2" />
              <p className="text-gray-500">{tr('Henüz semptom kaydı yok.', 'No symptom entries yet.')}</p>
            </div>
          )}
          {symptoms.data?.map((s) => (
            <div key={s.id} className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">
                    {new Date(s.recorded_at).toLocaleDateString(locale === 'tr' ? 'tr-TR' : 'en-US', {
                      day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
                    })}
                  </span>
                  {s.motor_state && (
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      MOTOR_STATES.find((m) => m.value === s.motor_state)?.color ?? 'bg-gray-100'
                    }`}>
                      {MOTOR_STATES.find((m) => m.value === s.motor_state)?.[locale === 'tr' ? 'label_tr' : 'label_en']}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => deleteSymptom.mutate(s.id)}
                  className="text-gray-400 hover:text-red-500 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <div className="grid grid-cols-5 gap-2 text-center text-xs">
                <div>
                  <p className="font-semibold text-gray-900">{s.tremor_severity}</p>
                  <p className="text-gray-500">{tr('Tremor', 'Tremor')}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{s.rigidity_severity}</p>
                  <p className="text-gray-500">{tr('Rijidite', 'Rigidity')}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{s.bradykinesia_severity}</p>
                  <p className="text-gray-500">{tr('Bradikinezi', 'Bradykinesia')}</p>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{s.gait_difficulty}</p>
                  <p className="text-gray-500">{tr('Yürüme', 'Gait')}</p>
                </div>
                <div>
                  <p className="font-bold text-teal-700">{s.overall_severity}/10</p>
                  <p className="text-gray-500">{tr('Genel', 'Overall')}</p>
                </div>
              </div>
              {s.notes && <p className="text-xs text-gray-500 mt-2">{s.notes}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Medications Tab */}
      {activeTab === 'medications' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold">{tr('İlaçlarım', 'My Medications')}</h2>
            <button
              onClick={() => setShowMedForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700"
            >
              <Plus className="w-4 h-4" /> {tr('İlaç Ekle', 'Add Medication')}
            </button>
          </div>

          {medications.data?.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <Pill className="w-10 h-10 mx-auto text-gray-300 mb-2" />
              <p className="text-gray-500">{tr('Henüz ilaç kaydı yok.', 'No medications yet.')}</p>
            </div>
          )}
          {medications.data?.map((med) => (
            <div key={med.id} className={`bg-white border rounded-xl p-4 ${med.is_active ? 'border-gray-200' : 'border-gray-100 opacity-60'}`}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-gray-900">{med.name}</h3>
                  {med.generic_name && <p className="text-xs text-gray-500">{med.generic_name}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${med.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {med.is_active ? tr('Aktif', 'Active') : tr('Pasif', 'Inactive')}
                  </span>
                  <button
                    onClick={() => deleteMed.mutate(med.id)}
                    className="text-gray-400 hover:text-red-500 transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs text-center">
                <div className="bg-gray-50 rounded p-2">
                  <p className="font-medium text-gray-900">{med.dosage_mg} mg</p>
                  <p className="text-gray-500">{tr('Doz', 'Dose')}</p>
                </div>
                <div className="bg-gray-50 rounded p-2">
                  <p className="font-medium text-gray-900">x{med.frequency_per_day}</p>
                  <p className="text-gray-500">{tr('Günde', 'Daily')}</p>
                </div>
                <div className="bg-gray-50 rounded p-2">
                  <p className="font-medium text-gray-900">{DRUG_CLASSES.find((d) => d.value === med.drug_class)?.[locale === 'tr' ? 'label_tr' : 'label_en']}</p>
                  <p className="text-gray-500">{tr('Sınıf', 'Class')}</p>
                </div>
                <div className="bg-teal-50 rounded p-2">
                  <p className="font-bold text-teal-700">{med.daily_led.toFixed(0)} mg</p>
                  <p className="text-gray-500">LED</p>
                </div>
              </div>
              {med.schedules.length > 0 && (
                <div className="mt-2 flex gap-2 flex-wrap">
                  {med.schedules.map((s) => (
                    <span key={s.id} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-lg flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {s.time_of_day.slice(0, 5)} {s.label && `(${s.label})`}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Today's Medications Tab */}
      {activeTab === 'today' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">{tr('Bugünkü İlaç Programı', 'Today\'s Medication Schedule')}</h2>
          {todayLogs.data?.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-xl">
              <Clock className="w-10 h-10 mx-auto text-gray-300 mb-2" />
              <p className="text-gray-500">{tr('Bugün için ilaç kaydı yok.', 'No medication schedule for today.')}</p>
            </div>
          )}
          {todayLogs.data?.map((log) => (
            <div key={log.id} className={`bg-white border rounded-xl p-4 flex items-center gap-4 ${log.was_taken ? 'border-green-200 bg-green-50/30' : 'border-gray-200'}`}>
              <button
                onClick={() => !log.was_taken && takeMed.mutate({ id: log.id })}
                disabled={log.was_taken || takeMed.isPending}
                className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition ${
                  log.was_taken
                    ? 'bg-green-100 text-green-600'
                    : 'bg-gray-100 text-gray-400 hover:bg-teal-100 hover:text-teal-600'
                }`}
              >
                {takeMed.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Check className="w-5 h-5" />}
              </button>
              <div className="flex-1">
                <p className={`font-medium ${log.was_taken ? 'text-green-800 line-through' : 'text-gray-900'}`}>{log.medication_name}</p>
                <p className="text-xs text-gray-500">
                  {new Date(log.scheduled_time).toLocaleTimeString(locale === 'tr' ? 'tr-TR' : 'en-US', {
                    hour: '2-digit', minute: '2-digit',
                  })}
                  {log.was_taken && log.taken_at && (
                    <span className="text-green-600 ml-2">
                      {tr('Alındı', 'Taken')}: {new Date(log.taken_at).toLocaleTimeString(locale === 'tr' ? 'tr-TR' : 'en-US', {
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Symptom Form Modal */}
      {showSymptomForm && (
        <SymptomFormModal
          locale={locale}
          tr={tr}
          onClose={() => setShowSymptomForm(false)}
          onSubmit={(data) => {
            createSymptom.mutate(data, {
              onSuccess: () => setShowSymptomForm(false),
            });
          }}
          isPending={createSymptom.isPending}
        />
      )}

      {/* Medication Form Modal */}
      {showMedForm && (
        <MedicationFormModal
          locale={locale}
          tr={tr}
          onClose={() => setShowMedForm(false)}
          onSubmit={(data) => {
            createMed.mutate(data, {
              onSuccess: () => setShowMedForm(false),
            });
          }}
          isPending={createMed.isPending}
        />
      )}
    </div>
  );
}

// ==================== STAT CARD ====================

function StatCard({ label, value, icon, bg }: { label: string; value: string | number; icon: React.ReactNode; bg: string }) {
  return (
    <div className={`${bg} rounded-xl p-4`}>
      <div className="flex items-center gap-2 mb-1">{icon}</div>
      <p className="text-xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-600">{label}</p>
    </div>
  );
}

// ==================== SYMPTOM FORM MODAL ====================

function SymptomFormModal({
  locale,
  tr,
  onClose,
  onSubmit,
  isPending,
}: {
  locale: string;
  tr: (trText: string, enText: string) => string;
  onClose: () => void;
  onSubmit: (data: Record<string, unknown>) => void;
  isPending: boolean;
}) {
  const [motorState, setMotorState] = useState('');
  const [tremor, setTremor] = useState(0);
  const [rigidity, setRigidity] = useState(0);
  const [bradykinesia, setBradykinesia] = useState(0);
  const [overall, setOverall] = useState(0);
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      recorded_at: new Date().toISOString(),
      motor_state: motorState,
      tremor_severity: tremor,
      rigidity_severity: rigidity,
      bradykinesia_severity: bradykinesia,
      overall_severity: overall,
      notes,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{tr('Semptom Kaydı', 'Symptom Entry')}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Motor State */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('Motor Durum', 'Motor State')}</label>
            <div className="grid grid-cols-2 gap-2">
              {MOTOR_STATES.map((ms) => (
                <button
                  type="button"
                  key={ms.value}
                  onClick={() => setMotorState(ms.value)}
                  className={`px-3 py-2 rounded-lg text-xs font-medium transition ${
                    motorState === ms.value ? ms.color + ' ring-2 ring-offset-1 ring-teal-500' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {locale === 'tr' ? ms.label_tr : ms.label_en}
                </button>
              ))}
            </div>
          </div>

          {/* Severity Sliders */}
          <SeveritySlider label={tr('Tremor', 'Tremor')} value={tremor} onChange={setTremor} max={4} />
          <SeveritySlider label={tr('Rijidite', 'Rigidity')} value={rigidity} onChange={setRigidity} max={4} />
          <SeveritySlider label={tr('Bradikinezi', 'Bradykinesia')} value={bradykinesia} onChange={setBradykinesia} max={4} />
          <SeveritySlider label={tr('Genel Şiddet', 'Overall Severity')} value={overall} onChange={setOverall} max={10} />

          {/* Notes */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('Notlar', 'Notes')}</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-200 rounded-lg p-2 text-sm resize-none h-20 focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder={tr('İsteğe bağlı notlar...', 'Optional notes...')}
            />
          </div>

          <button
            type="submit"
            disabled={isPending}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            {tr('Kaydet', 'Save')}
          </button>
        </form>
      </div>
    </div>
  );
}

// ==================== MEDICATION FORM MODAL ====================

function MedicationFormModal({
  locale,
  tr,
  onClose,
  onSubmit,
  isPending,
}: {
  locale: string;
  tr: (trText: string, enText: string) => string;
  onClose: () => void;
  onSubmit: (data: Record<string, unknown>) => void;
  isPending: boolean;
}) {
  const [name, setName] = useState('');
  const [genericName, setGenericName] = useState('');
  const [drugClass, setDrugClass] = useState<DrugClass>('levodopa');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState(3);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      name,
      generic_name: genericName,
      drug_class: drugClass,
      dosage_mg: parseFloat(dosage),
      frequency_per_day: frequency,
      led_conversion_factor: LED_FACTORS[drugClass] ?? 1,
      start_date: new Date().toISOString().split('T')[0],
      is_active: true,
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{tr('İlaç Ekle', 'Add Medication')}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('İlaç Adı', 'Medication Name')}</label>
            <input
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder={tr('Ör. Madopar 250mg', 'e.g. Sinemet 25/100')}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('Etken Madde', 'Generic Name')}</label>
            <input
              value={genericName}
              onChange={(e) => setGenericName(e.target.value)}
              className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              placeholder={tr('Ör. Levodopa/Karbidopa', 'e.g. Levodopa/Carbidopa')}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('İlaç Sınıfı', 'Drug Class')}</label>
            <select
              value={drugClass}
              onChange={(e) => setDrugClass(e.target.value as DrugClass)}
              className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
            >
              {DRUG_CLASSES.map((dc) => (
                <option key={dc.value} value={dc.value}>
                  {locale === 'tr' ? dc.label_tr : dc.label_en}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('Doz (mg)', 'Dose (mg)')}</label>
              <input
                required
                type="number"
                step="0.01"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 mb-1 block">{tr('Günde kaç kez', 'Times per day')}</label>
              <input
                required
                type="number"
                min={1}
                max={10}
                value={frequency}
                onChange={(e) => setFrequency(parseInt(e.target.value))}
                className="w-full border border-gray-200 rounded-lg p-2 text-sm focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="bg-teal-50 rounded-lg p-3 text-sm">
            <p className="text-teal-700">
              <strong>LED:</strong> {dosage ? (parseFloat(dosage) * frequency * (LED_FACTORS[drugClass] ?? 1)).toFixed(0) : '0'} mg/gün
            </p>
          </div>
          <button
            type="submit"
            disabled={isPending || !name || !dosage}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            {tr('Kaydet', 'Save')}
          </button>
        </form>
      </div>
    </div>
  );
}

// ==================== SEVERITY SLIDER ====================

function SeveritySlider({ label, value, onChange, max }: { label: string; value: number; onChange: (v: number) => void; max: number }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-bold text-teal-700">{value}/{max}</span>
      </div>
      <input
        type="range"
        min={0}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
      />
    </div>
  );
}
