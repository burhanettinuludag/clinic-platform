'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  useSeizureEvents,
  useCreateSeizure,
  useSeizureStats,
  useEpilepsyTriggers,
  useEpilepsyTriggerAnalysis,
  useCreateEpilepsyTrigger,
} from '@/hooks/usePatientData';
import { Zap, Plus, BarChart3, List, Target, X, PlusCircle, Check, Loader2, BookOpen } from 'lucide-react';
import { Link } from '@/i18n/navigation';
import SeizureChart from '@/components/patient/SeizureChart';

const SEIZURE_TYPES = [
  'focal_aware',
  'focal_impaired',
  'generalized_tonic_clonic',
  'generalized_absence',
  'generalized_myoclonic',
  'unknown',
] as const;

export default function EpilepsyPage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'diary' | 'stats' | 'triggers'>('diary');
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Zap className="w-6 h-6 text-amber-600" />
          <h1 className="text-2xl font-bold text-gray-900">{t('patient.epilepsy.title')}</h1>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/patient/epilepsy/education"
            className="flex items-center gap-2 px-4 py-2 bg-amber-100 text-amber-700 text-sm font-medium rounded-lg hover:bg-amber-200 transition"
          >
            <BookOpen className="w-4 h-4" /> {t('patient.epilepsy.education')}
          </Link>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white text-sm rounded-lg hover:bg-amber-700"
          >
            <Plus className="w-4 h-4" /> {t('patient.epilepsy.logSeizure')}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
        {(['diary', 'stats', 'triggers'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition ${
              activeTab === tab ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            }`}
          >
            {tab === 'diary' && <List className="w-4 h-4" />}
            {tab === 'stats' && <BarChart3 className="w-4 h-4" />}
            {tab === 'triggers' && <Target className="w-4 h-4" />}
            {t(`patient.epilepsy.${tab === 'diary' ? 'seizureDiary' : tab}`)}
          </button>
        ))}
      </div>

      {showForm && <SeizureForm onClose={() => setShowForm(false)} />}

      {activeTab === 'diary' && <SeizureDiary />}
      {activeTab === 'stats' && <StatsView />}
      {activeTab === 'triggers' && <TriggersView />}
    </div>
  );
}

function SeizureForm({ onClose }: { onClose: () => void }) {
  const t = useTranslations();
  const createSeizure = useCreateSeizure();
  const { data: triggers } = useEpilepsyTriggers();
  const [form, setForm] = useState({
    seizure_type: '' as string,
    duration_seconds: '' as string,
    intensity: 5,
    loss_of_consciousness: false,
    medication_taken: true,
    notes: '',
  });
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([]);

  const handleSubmit = () => {
    createSeizure.mutate(
      {
        seizure_datetime: new Date().toISOString(),
        seizure_type: form.seizure_type || 'unknown',
        duration_seconds: form.duration_seconds ? Number(form.duration_seconds) : null,
        intensity: form.intensity,
        trigger_ids: selectedTriggers,
        loss_of_consciousness: form.loss_of_consciousness,
        medication_taken: form.medication_taken,
        notes: form.notes,
      } as any,
      { onSuccess: onClose }
    );
  };

  const toggleTrigger = (id: string) => {
    setSelectedTriggers((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  return (
    <div className="bg-white rounded-xl border-2 border-amber-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{t('patient.epilepsy.logSeizure')}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            {t('patient.epilepsy.intensity')} (1-10)
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={form.intensity}
            onChange={(e) => setForm({ ...form, intensity: Number(e.target.value) })}
            className="w-full accent-amber-600"
          />
          <div className="text-center text-2xl font-bold text-amber-600">{form.intensity}</div>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">{t('patient.epilepsy.duration')}</label>
          <input
            type="number"
            value={form.duration_seconds}
            onChange={(e) => setForm({ ...form, duration_seconds: e.target.value })}
            placeholder="30"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
      </div>

      {/* Seizure Type */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-2">{t('patient.epilepsy.type')}</label>
        <div className="flex flex-wrap gap-2">
          {SEIZURE_TYPES.map((type) => (
            <button
              key={type}
              onClick={() => setForm({ ...form, seizure_type: type })}
              className={`px-3 py-1.5 rounded-lg text-sm border transition ${
                form.seizure_type === type
                  ? 'bg-amber-50 border-amber-300 text-amber-700'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              }`}
            >
              {t(`patient.epilepsy.seizureTypes.${type}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Symptoms toggles */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-2">{t('patient.epilepsy.postIctal')}</label>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setForm({ ...form, loss_of_consciousness: !form.loss_of_consciousness })}
            className={`px-3 py-1.5 rounded-lg text-sm border transition ${
              form.loss_of_consciousness
                ? 'bg-purple-50 border-purple-300 text-purple-700'
                : 'border-gray-200 text-gray-500 hover:bg-gray-50'
            }`}
          >
            {t('patient.epilepsy.consciousnessLoss')}
          </button>
          <button
            onClick={() => setForm({ ...form, medication_taken: !form.medication_taken })}
            className={`px-3 py-1.5 rounded-lg text-sm border transition ${
              form.medication_taken
                ? 'bg-green-50 border-green-300 text-green-700'
                : 'bg-red-50 border-red-300 text-red-700'
            }`}
          >
            {t('patient.epilepsy.medicationTaken')}
          </button>
        </div>
      </div>

      {/* Triggers */}
      {triggers && triggers.length > 0 && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-2">{t('patient.epilepsy.triggers')}</label>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {triggers.map((trigger) => (
              <button
                key={trigger.id}
                onClick={() => toggleTrigger(trigger.id)}
                className={`px-2.5 py-1 rounded-lg text-xs border transition ${
                  selectedTriggers.includes(trigger.id)
                    ? 'bg-orange-50 border-orange-300 text-orange-700'
                    : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                }`}
              >
                {trigger.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-1">{t('patient.epilepsy.notes')}</label>
        <textarea
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          rows={2}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleSubmit}
          disabled={createSeizure.isPending}
          className="px-6 py-2.5 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 disabled:opacity-50"
        >
          {t('common.save')}
        </button>
        <button onClick={onClose} className="px-4 py-2.5 text-gray-500 text-sm rounded-lg hover:bg-gray-100">
          {t('common.cancel')}
        </button>
      </div>
    </div>
  );
}

function SeizureDiary() {
  const t = useTranslations();
  const { data: events, isLoading } = useSeizureEvents();

  if (isLoading) return <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>;

  if (!events || events.length === 0) {
    return <div className="text-center py-12 text-gray-500">{t('patient.epilepsy.noSeizures')}</div>;
  }

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <div key={event.id} className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">
              {new Date(event.seizure_datetime).toLocaleDateString('tr-TR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${
              event.intensity >= 7
                ? 'bg-red-100 text-red-700'
                : event.intensity >= 4
                ? 'bg-orange-100 text-orange-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {event.intensity}/10
            </span>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="px-2 py-1 bg-amber-100 rounded text-amber-600">
              {t(`patient.epilepsy.seizureTypes.${event.seizure_type}`)}
            </span>
            {event.duration_seconds && (
              <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">
                {event.duration_seconds} sn
              </span>
            )}
            {event.medication_taken && (
              <span className="px-2 py-1 bg-blue-100 rounded text-blue-600">
                {t('patient.epilepsy.medicationTakenLabel')}
              </span>
            )}
            {!event.medication_taken && (
              <span className="px-2 py-1 bg-red-100 rounded text-red-600">
                {t('patient.epilepsy.medicationNotTaken')}
              </span>
            )}
            {event.loss_of_consciousness && (
              <span className="px-2 py-1 bg-red-100 rounded text-red-600">
                {t('patient.epilepsy.consciousnessLoss')}
              </span>
            )}
            {event.trigger_count > 0 && (
              <span className="px-2 py-1 bg-orange-100 rounded text-orange-600">
                {event.trigger_count} tetikleyici
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function StatsView() {
  const t = useTranslations();
  const { data: stats, isLoading } = useSeizureStats();

  if (isLoading) return <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>;

  if (!stats) return null;

  return (
    <div className="space-y-6">
      {/* Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold mb-4">{t('patient.epilepsy.monthlyChart')}</h3>
        <SeizureChart months={6} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('common.total')}</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total_seizures}</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.epilepsy.attacksThisMonth')}</div>
          <div className="text-2xl font-bold text-amber-600">{stats.seizures_this_month}</div>
          {stats.seizures_last_month > 0 && (
            <div className="text-xs text-gray-400 mt-1">
              ({t('patient.epilepsy.lastMonth')}: {stats.seizures_last_month})
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.epilepsy.avgIntensity')}</div>
          <div className="text-2xl font-bold text-orange-600">{stats.avg_intensity}/10</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.epilepsy.consciousnessLossRate')}</div>
          <div className="text-2xl font-bold text-red-600">%{stats.consciousness_loss_percentage}</div>
        </div>
      </div>

      {stats.most_common_triggers.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold mb-3">{t('patient.epilepsy.commonTriggers')}</h3>
          <div className="space-y-2">
            {stats.most_common_triggers.map((trigger, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-gray-700">{trigger.name}</span>
                    <span className="text-xs text-gray-400">{trigger.count}x</span>
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-400 rounded-full"
                      style={{
                        width: `${(trigger.count / (stats.most_common_triggers[0]?.count || 1)) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TriggersView() {
  const t = useTranslations();
  const { data: analysis, isLoading } = useEpilepsyTriggerAnalysis();
  const { data: allTriggers } = useEpilepsyTriggers();
  const createTrigger = useCreateEpilepsyTrigger();

  const [showAddForm, setShowAddForm] = useState(false);
  const [newTriggerName, setNewTriggerName] = useState('');
  const [newTriggerCategory, setNewTriggerCategory] = useState<string>('other');
  const [addSuccess, setAddSuccess] = useState(false);

  const handleAddTrigger = () => {
    if (!newTriggerName.trim()) return;

    createTrigger.mutate(
      {
        name_tr: newTriggerName.trim(),
        name_en: newTriggerName.trim(),
        category: newTriggerCategory,
      },
      {
        onSuccess: () => {
          setNewTriggerName('');
          setAddSuccess(true);
          setTimeout(() => {
            setAddSuccess(false);
            setShowAddForm(false);
          }, 1500);
        },
      }
    );
  };

  if (isLoading) return <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>;

  const categories = ['sleep', 'stress', 'substance', 'sensory', 'physical', 'hormonal', 'other'] as const;

  const getCategoryLabel = (cat: string) => {
    return t(`patient.epilepsy.categories.${cat}`);
  };

  return (
    <div className="space-y-6">
      {/* Analysis */}
      {analysis && analysis.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold mb-3">{t('patient.epilepsy.commonTriggers')}</h3>
          <div className="space-y-2">
            {analysis.slice(0, 10).map((item) => (
              <div key={item.id} className="flex items-center justify-between py-1.5">
                <span className="text-sm text-gray-700">{item.name_tr}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">
                    {getCategoryLabel(item.category)}
                  </span>
                  <span className="text-sm font-medium text-amber-600">{item.seizure_count}x</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Triggers by Category */}
      {categories.map((cat) => {
        const catTriggers = allTriggers?.filter((tr) => tr.category === cat);
        if (!catTriggers || catTriggers.length === 0) return null;
        return (
          <div key={cat}>
            <h3 className="text-sm font-semibold text-gray-500 mb-2">
              {getCategoryLabel(cat)}
            </h3>
            <div className="flex flex-wrap gap-2">
              {catTriggers.map((trigger) => (
                <span key={trigger.id} className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-600">
                  {trigger.name}
                </span>
              ))}
            </div>
          </div>
        );
      })}

      {/* Add Custom Trigger Section */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border-2 border-amber-200 p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">{t('patient.epilepsy.addCustomTrigger')}</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              {t('patient.epilepsy.addCustomTriggerDesc')}
            </p>
          </div>
          {!showAddForm && (
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition"
            >
              <PlusCircle className="w-4 h-4" />
              Tetikleyici Ekle
            </button>
          )}
        </div>

        {showAddForm && (
          <div className="mt-4 p-4 bg-white rounded-lg border border-amber-200">
            {addSuccess ? (
              <div className="flex items-center justify-center gap-2 py-4 text-green-600">
                <Check className="w-5 h-5" />
                <span className="font-medium">{t('patient.epilepsy.triggerAdded')}</span>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">{t('patient.epilepsy.triggerName')}</label>
                    <input
                      type="text"
                      value={newTriggerName}
                      onChange={(e) => setNewTriggerName(e.target.value)}
                      placeholder="Örn: Gürültü"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">{t('patient.epilepsy.category')}</label>
                    <select
                      value={newTriggerCategory}
                      onChange={(e) => setNewTriggerCategory(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
                    >
                      {categories.map((cat) => (
                        <option key={cat} value={cat}>
                          {getCategoryLabel(cat)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleAddTrigger}
                    disabled={!newTriggerName.trim() || createTrigger.isPending}
                    className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {createTrigger.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Ekleniyor...
                      </>
                    ) : (
                      <>
                        <Check className="w-4 h-4" />
                        Ekle
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setNewTriggerName('');
                    }}
                    className="px-4 py-2 text-gray-500 text-sm rounded-lg hover:bg-gray-100 transition"
                  >
                    İptal
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
