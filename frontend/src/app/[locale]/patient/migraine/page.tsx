'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  useMigraineAttacks,
  useCreateAttack,
  useMigraineStats,
  useMigraineTriggers,
  useTriggerAnalysis,
  useCreateTrigger,
} from '@/hooks/usePatientData';
import { Brain, Plus, BarChart3, List, Target, X, PlusCircle, Check, Loader2, BookOpen } from 'lucide-react';
import { Link } from '@/i18n/navigation';
import MigraineChart from '@/components/patient/MigraineChart';
import type { MigraineAttack } from '@/lib/types/patient';

const PAIN_LOCATIONS = ['left', 'right', 'bilateral', 'frontal', 'occipital', 'other'] as const;

export default function MigrainePage() {
  const t = useTranslations();
  const [activeTab, setActiveTab] = useState<'diary' | 'stats' | 'triggers'>('diary');
  const [showForm, setShowForm] = useState(false);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-purple-600" />
          <h1 className="text-2xl font-bold text-gray-900">{t('patient.migraine.title')}</h1>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/patient/migraine/education"
            className="flex items-center gap-2 px-4 py-2 bg-purple-100 text-purple-700 text-sm font-medium rounded-lg hover:bg-purple-200 transition"
          >
            <BookOpen className="w-4 h-4" /> Egitim
          </Link>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700"
          >
            <Plus className="w-4 h-4" /> {t('patient.migraine.logAttack')}
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
            {t(`patient.migraine.${tab === 'diary' ? 'attackDiary' : tab}`)}
          </button>
        ))}
      </div>

      {showForm && <AttackForm onClose={() => setShowForm(false)} />}

      {activeTab === 'diary' && <AttackDiary />}
      {activeTab === 'stats' && <StatsView />}
      {activeTab === 'triggers' && <TriggersView />}
    </div>
  );
}

function AttackForm({ onClose }: { onClose: () => void }) {
  const t = useTranslations();
  const createAttack = useCreateAttack();
  const { data: triggers } = useMigraineTriggers();
  const [form, setForm] = useState<Partial<MigraineAttack>>({
    intensity: 5,
    has_aura: false,
    has_nausea: false,
    has_vomiting: false,
    has_photophobia: false,
    has_phonophobia: false,
  });
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([]);

  const handleSubmit = () => {
    createAttack.mutate(
      {
        ...form,
        start_datetime: form.start_datetime || new Date().toISOString(),
        trigger_ids: selectedTriggers,
      } as Partial<MigraineAttack>,
      { onSuccess: onClose }
    );
  };

  const toggleTrigger = (id: string) => {
    setSelectedTriggers((prev) =>
      prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]
    );
  };

  return (
    <div className="bg-white rounded-xl border-2 border-red-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">{t('patient.migraine.logAttack')}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            {t('patient.migraine.intensity')} (1-10)
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={form.intensity ?? 5}
            onChange={(e) => setForm({ ...form, intensity: Number(e.target.value) })}
            className="w-full accent-red-600"
          />
          <div className="text-center text-2xl font-bold text-red-600">{form.intensity}</div>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">{t('patient.migraine.duration')}</label>
          <input
            type="number"
            value={form.duration_minutes ?? ''}
            onChange={(e) => setForm({ ...form, duration_minutes: Number(e.target.value) || undefined })}
            placeholder="60"
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
          />
        </div>
      </div>

      {/* Pain Location */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-2">{t('patient.migraine.location')}</label>
        <div className="flex flex-wrap gap-2">
          {PAIN_LOCATIONS.map((loc) => (
            <button
              key={loc}
              onClick={() => setForm({ ...form, pain_location: loc })}
              className={`px-3 py-1.5 rounded-lg text-sm border transition ${
                form.pain_location === loc
                  ? 'bg-red-50 border-red-300 text-red-700'
                  : 'border-gray-200 text-gray-500 hover:bg-gray-50'
              }`}
            >
              {t(`patient.migraine.locations.${loc}`)}
            </button>
          ))}
        </div>
      </div>

      {/* Symptoms toggles */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-2">Eslik eden semptomlar</label>
        <div className="flex flex-wrap gap-2">
          {(['has_aura', 'has_nausea', 'has_vomiting', 'has_photophobia', 'has_phonophobia'] as const).map((key) => {
            const labelKey = key.replace('has_', '') as 'aura' | 'nausea' | 'vomiting' | 'photophobia' | 'phonophobia';
            return (
              <button
                key={key}
                onClick={() => setForm({ ...form, [key]: !form[key] })}
                className={`px-3 py-1.5 rounded-lg text-sm border transition ${
                  form[key]
                    ? 'bg-purple-50 border-purple-300 text-purple-700'
                    : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                }`}
              >
                {t(`patient.migraine.${labelKey}`)}
              </button>
            );
          })}
        </div>
      </div>

      {/* Triggers */}
      {triggers && triggers.length > 0 && (
        <div className="mb-4">
          <label className="block text-xs text-gray-500 mb-2">{t('patient.migraine.selectTriggers')}</label>
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

      {/* Medication */}
      <div className="mb-4">
        <label className="block text-xs text-gray-500 mb-1">{t('patient.migraine.medicationTaken')}</label>
        <input
          type="text"
          value={form.medication_taken ?? ''}
          onChange={(e) => setForm({ ...form, medication_taken: e.target.value })}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleSubmit}
          disabled={createAttack.isPending}
          className="px-6 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
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

function AttackDiary() {
  const t = useTranslations();
  const { data: attacks, isLoading } = useMigraineAttacks();

  if (isLoading) return <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>;

  if (!attacks || attacks.length === 0) {
    return <div className="text-center py-12 text-gray-500">{t('patient.migraine.noAttacks')}</div>;
  }

  return (
    <div className="space-y-3">
      {attacks.map((attack) => (
        <div key={attack.id} className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">
              {new Date(attack.start_datetime).toLocaleDateString('tr-TR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${
              attack.intensity >= 7
                ? 'bg-red-100 text-red-700'
                : attack.intensity >= 4
                ? 'bg-orange-100 text-orange-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {attack.intensity}/10
            </span>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            {attack.duration_minutes && (
              <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">
                {attack.duration_minutes} dk
              </span>
            )}
            {attack.pain_location && (
              <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">
                {t(`patient.migraine.locations.${attack.pain_location}`)}
              </span>
            )}
            {attack.has_aura && (
              <span className="px-2 py-1 bg-purple-100 rounded text-purple-600">Aura</span>
            )}
            {attack.medication_taken && (
              <span className="px-2 py-1 bg-blue-100 rounded text-blue-600">
                {attack.medication_taken}
              </span>
            )}
            {attack.trigger_count > 0 && (
              <span className="px-2 py-1 bg-orange-100 rounded text-orange-600">
                {attack.trigger_count} tetikleyici
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
  const { data: stats, isLoading } = useMigraineStats();

  if (isLoading) return <div className="text-center py-8 text-gray-500">{t('common.loading')}</div>;

  if (!stats) return null;

  return (
    <div className="space-y-6">
      {/* Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h3 className="text-sm font-semibold mb-4">Aylik Atak Grafigi</h3>
        <MigraineChart months={6} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('common.total')}</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total_attacks}</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.migraine.attacksThisMonth')}</div>
          <div className="text-2xl font-bold text-red-600">{stats.attacks_this_month}</div>
          {stats.attacks_last_month > 0 && (
            <div className="text-xs text-gray-400 mt-1">
              (Gecen ay: {stats.attacks_last_month})
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.migraine.avgIntensity')}</div>
          <div className="text-2xl font-bold text-orange-600">{stats.avg_intensity}/10</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="text-xs text-gray-400 mb-1">{t('patient.migraine.auraRate')}</div>
          <div className="text-2xl font-bold text-purple-600">%{stats.aura_percentage}</div>
        </div>
      </div>

      {stats.most_common_triggers.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold mb-3">{t('patient.migraine.commonTriggers')}</h3>
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
                      className="h-full bg-orange-400 rounded-full"
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
  const { data: analysis, isLoading } = useTriggerAnalysis();
  const { data: allTriggers } = useMigraineTriggers();
  const createTrigger = useCreateTrigger();

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

  const categories = ['dietary', 'environmental', 'hormonal', 'emotional', 'physical', 'sleep', 'other'] as const;

  const categoryLabels: Record<string, string> = {
    dietary: 'Beslenme',
    environmental: 'Çevresel',
    hormonal: 'Hormonal',
    emotional: 'Duygusal',
    physical: 'Fiziksel',
    sleep: 'Uyku',
    other: 'Diğer',
  };

  return (
    <div className="space-y-6">
      {/* Analysis */}
      {analysis && analysis.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-sm font-semibold mb-3">{t('patient.migraine.commonTriggers')}</h3>
          <div className="space-y-2">
            {analysis.slice(0, 10).map((item) => (
              <div key={item.id} className="flex items-center justify-between py-1.5">
                <span className="text-sm text-gray-700">{item.name_tr}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">
                    {categoryLabels[item.category] || item.category}
                  </span>
                  <span className="text-sm font-medium text-orange-600">{item.attack_count}x</span>
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
              {categoryLabels[cat] || cat}
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
      <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl border-2 border-orange-200 p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Kendi Tetikleyicinizi Ekleyin</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Listede olmayan bir tetikleyici mi var? Buradan ekleyebilirsiniz.
            </p>
          </div>
          {!showAddForm && (
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white text-sm font-medium rounded-lg hover:bg-orange-700 transition"
            >
              <PlusCircle className="w-4 h-4" />
              Tetikleyici Ekle
            </button>
          )}
        </div>

        {showAddForm && (
          <div className="mt-4 p-4 bg-white rounded-lg border border-orange-200">
            {addSuccess ? (
              <div className="flex items-center justify-center gap-2 py-4 text-green-600">
                <Check className="w-5 h-5" />
                <span className="font-medium">Tetikleyici eklendi!</span>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Tetikleyici Adı</label>
                    <input
                      type="text"
                      value={newTriggerName}
                      onChange={(e) => setNewTriggerName(e.target.value)}
                      placeholder="Örn: Parfüm kokusu"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                      autoFocus
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Kategori</label>
                    <select
                      value={newTriggerCategory}
                      onChange={(e) => setNewTriggerCategory(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      {categories.map((cat) => (
                        <option key={cat} value={cat}>
                          {categoryLabels[cat]}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleAddTrigger}
                    disabled={!newTriggerName.trim() || createTrigger.isPending}
                    className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white text-sm font-medium rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
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
