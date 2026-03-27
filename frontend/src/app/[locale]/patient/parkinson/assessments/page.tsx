'use client';

import { useState } from 'react';
import { useLocale } from 'next-intl';
import { Link } from '@/i18n/navigation';
import {
  useHoehnYahrAssessments,
  useCreateHoehnYahr,
  useSchwabEnglandAssessments,
  useCreateSchwabEngland,
  useNMSQuestAssessments,
  useCreateNMSQuest,
  useNoseraMotorAssessments,
  useCreateNoseraMotor,
  useNoseraDailyLivingAssessments,
  useCreateNoseraDailyLiving,
} from '@/hooks/useParkinsonData';
import {
  ArrowLeft,
  ClipboardCheck,
  Activity,
  BarChart3,
  Brain,
  Heart,
  ChevronRight,
  Plus,
  X,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

type AssessmentType = 'hoehn-yahr' | 'schwab-england' | 'nmsquest' | 'motor' | 'daily-living';

const ASSESSMENTS: { key: AssessmentType; label_tr: string; label_en: string; desc_tr: string; desc_en: string; icon: typeof Activity; color: string }[] = [
  {
    key: 'hoehn-yahr',
    label_tr: 'Hoehn & Yahr Evreleme',
    label_en: 'Hoehn & Yahr Staging',
    desc_tr: 'Hastalık evresi (0-5)',
    desc_en: 'Disease stage (0-5)',
    icon: BarChart3,
    color: 'purple',
  },
  {
    key: 'schwab-england',
    label_tr: 'Schwab & England Ölçeği',
    label_en: 'Schwab & England Scale',
    desc_tr: 'Günlük yaşam bağımsızlığı (%0-100)',
    desc_en: 'Daily living independence (0-100%)',
    icon: Heart,
    color: 'blue',
  },
  {
    key: 'nmsquest',
    label_tr: 'NMSQuest (Non-Motor Semptomlar)',
    label_en: 'NMSQuest (Non-Motor Symptoms)',
    desc_tr: '30 soruluk non-motor semptom taraması',
    desc_en: '30-question non-motor symptom screening',
    icon: Brain,
    color: 'orange',
  },
  {
    key: 'motor',
    label_tr: 'Norosera Motor Değerlendirme',
    label_en: 'Norosera Motor Assessment',
    desc_tr: '10 maddelik motor fonksiyon testi (0-40)',
    desc_en: '10-item motor function test (0-40)',
    icon: Activity,
    color: 'teal',
  },
  {
    key: 'daily-living',
    label_tr: 'Norosera Günlük Yaşam',
    label_en: 'Norosera Daily Living',
    desc_tr: '12 maddelik günlük aktivite testi (0-48)',
    desc_en: '12-item daily activity test (0-48)',
    icon: ClipboardCheck,
    color: 'green',
  },
];

export default function ParkinsonAssessmentsPage() {
  const locale = useLocale();
  const tr = (trText: string, enText: string) => (locale === 'tr' ? trText : enText);
  const [activeTest, setActiveTest] = useState<AssessmentType | null>(null);

  const hyData = useHoehnYahrAssessments();
  const seData = useSchwabEnglandAssessments();
  const nmsData = useNMSQuestAssessments();
  const motorData = useNoseraMotorAssessments();
  const dailyData = useNoseraDailyLivingAssessments();

  const getLatest = (key: AssessmentType) => {
    switch (key) {
      case 'hoehn-yahr': return hyData.data?.[0];
      case 'schwab-england': return seData.data?.[0];
      case 'nmsquest': return nmsData.data?.[0];
      case 'motor': return motorData.data?.[0];
      case 'daily-living': return dailyData.data?.[0];
    }
  };

  const getScore = (key: AssessmentType) => {
    const latest = getLatest(key);
    if (!latest) return '-';
    switch (key) {
      case 'hoehn-yahr': return `Evre ${(latest as any).stage}`;
      case 'schwab-england': return `${(latest as any).score}%`;
      case 'nmsquest': return `${(latest as any).total_score}/30`;
      case 'motor': return `${(latest as any).total_score}/40`;
      case 'daily-living': return `${(latest as any).total_score}/48`;
    }
  };

  const getCount = (key: AssessmentType) => {
    switch (key) {
      case 'hoehn-yahr': return hyData.data?.length ?? 0;
      case 'schwab-england': return seData.data?.length ?? 0;
      case 'nmsquest': return nmsData.data?.length ?? 0;
      case 'motor': return motorData.data?.length ?? 0;
      case 'daily-living': return dailyData.data?.length ?? 0;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Link href="/patient/parkinson" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{tr('Klinik Değerlendirmeler', 'Clinical Assessments')}</h1>
          <p className="text-sm text-gray-500">{tr('Parkinson hastalığı ölçekleri ve testler', 'Parkinson\'s disease scales and tests')}</p>
        </div>
      </div>

      <div className="space-y-3">
        {ASSESSMENTS.map((a) => {
          const Icon = a.icon;
          const count = getCount(a.key);
          const score = getScore(a.key);
          return (
            <div key={a.key} className="bg-white border border-gray-200 rounded-xl p-4">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl bg-${a.color}-100 flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-6 h-6 text-${a.color}-600`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{locale === 'tr' ? a.label_tr : a.label_en}</h3>
                  <p className="text-xs text-gray-500">{locale === 'tr' ? a.desc_tr : a.desc_en}</p>
                  <div className="flex items-center gap-3 mt-1 text-xs">
                    <span className="text-gray-400">{count} {tr('kayıt', 'entries')}</span>
                    {score !== '-' && <span className="font-medium text-teal-700">{tr('Son:', 'Latest:')} {score}</span>}
                  </div>
                </div>
                <button
                  onClick={() => setActiveTest(a.key)}
                  className="px-4 py-2 bg-teal-600 text-white text-sm rounded-lg hover:bg-teal-700 transition flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" /> {tr('Yeni Test', 'New Test')}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {activeTest === 'hoehn-yahr' && <HoehnYahrModal locale={locale} onClose={() => setActiveTest(null)} />}
      {activeTest === 'schwab-england' && <SchwabEnglandModal locale={locale} onClose={() => setActiveTest(null)} />}
      {activeTest === 'motor' && <NoseraMotorModal locale={locale} onClose={() => setActiveTest(null)} />}
      {activeTest === 'daily-living' && <NoseraDailyLivingModal locale={locale} onClose={() => setActiveTest(null)} />}
      {activeTest === 'nmsquest' && <NMSQuestModal locale={locale} onClose={() => setActiveTest(null)} />}
    </div>
  );
}

// ==================== HOEHN & YAHR MODAL ====================

const HY_STAGES = [
  { value: '0', tr: 'Evre 0 - Hastalık belirtisi yok', en: 'Stage 0 - No signs of disease' },
  { value: '1', tr: 'Evre 1 - Tek taraflı tutulum', en: 'Stage 1 - Unilateral involvement' },
  { value: '1.5', tr: 'Evre 1.5 - Tek taraflı + aksiyel tutulum', en: 'Stage 1.5 - Unilateral + axial involvement' },
  { value: '2', tr: 'Evre 2 - İki taraflı, denge sorunu yok', en: 'Stage 2 - Bilateral, no balance impairment' },
  { value: '2.5', tr: 'Evre 2.5 - Hafif iki taraflı', en: 'Stage 2.5 - Mild bilateral' },
  { value: '3', tr: 'Evre 3 - Postüral instabilite', en: 'Stage 3 - Postural instability' },
  { value: '4', tr: 'Evre 4 - Ciddi engel', en: 'Stage 4 - Severe disability' },
  { value: '5', tr: 'Evre 5 - Yatağa/sandalyeye bağımlı', en: 'Stage 5 - Wheelchair/bedridden' },
];

function HoehnYahrModal({ locale, onClose }: { locale: string; onClose: () => void }) {
  const tr = (t: string, e: string) => locale === 'tr' ? t : e;
  const [stage, setStage] = useState('');
  const [notes, setNotes] = useState('');
  const create = useCreateHoehnYahr();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Hoehn & Yahr</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-4 space-y-3">
          {HY_STAGES.map((s) => (
            <button
              key={s.value}
              onClick={() => setStage(s.value)}
              className={`w-full text-left p-3 rounded-lg border-2 text-sm transition ${
                stage === s.value ? 'border-teal-500 bg-teal-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {locale === 'tr' ? s.tr : s.en}
            </button>
          ))}
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr('Notlar...', 'Notes...')} className="w-full border rounded-lg p-2 text-sm h-16 resize-none" />
          <button
            disabled={!stage || create.isPending}
            onClick={() => create.mutate({ assessed_at: new Date().toISOString(), stage: stage as any, notes }, { onSuccess: onClose })}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />} {tr('Kaydet', 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== SCHWAB & ENGLAND MODAL ====================

const SE_SCORES = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0];
const SE_LABELS: Record<number, { tr: string; en: string }> = {
  100: { tr: 'Tamamen bağımsız', en: 'Completely independent' },
  90: { tr: 'Yavaş da olsa bağımsız', en: 'Completely independent, slower' },
  80: { tr: 'Çoğu işi bağımsız yapar', en: 'Independent in most chores' },
  70: { tr: 'Tam bağımsız değil', en: 'Not completely independent' },
  60: { tr: 'Biraz bağımlı', en: 'Some dependency' },
  50: { tr: 'Daha bağımlı, yardım gerekir', en: 'More dependent, help needed' },
  40: { tr: 'Çok bağımlı', en: 'Very dependent' },
  30: { tr: 'Zor yapabilir', en: 'With effort, does few chores' },
  20: { tr: 'Hiçbir şeyi tek başına yapamaz', en: 'Nothing alone' },
  10: { tr: 'Tamamen bağımlı, yatalak', en: 'Totally dependent, bedridden' },
  0: { tr: 'Yatalak, vejetatif', en: 'Bedridden, vegetative' },
};

function SchwabEnglandModal({ locale, onClose }: { locale: string; onClose: () => void }) {
  const tr = (t: string, e: string) => locale === 'tr' ? t : e;
  const [score, setScore] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const create = useCreateSchwabEngland();

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Schwab & England</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-4 space-y-2">
          {SE_SCORES.map((s) => (
            <button
              key={s}
              onClick={() => setScore(s)}
              className={`w-full text-left p-3 rounded-lg border-2 text-sm transition flex items-center justify-between ${
                score === s ? 'border-teal-500 bg-teal-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <span>{locale === 'tr' ? SE_LABELS[s].tr : SE_LABELS[s].en}</span>
              <span className="font-bold text-teal-700">{s}%</span>
            </button>
          ))}
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr('Notlar...', 'Notes...')} className="w-full border rounded-lg p-2 text-sm h-16 resize-none" />
          <button
            disabled={score === null || create.isPending}
            onClick={() => create.mutate({ assessed_at: new Date().toISOString(), score: score!, notes }, { onSuccess: onClose })}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />} {tr('Kaydet', 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== NOROSERA MOTOR MODAL ====================

const MOTOR_ITEMS: { field: string; tr: string; en: string }[] = [
  { field: 'tremor_rest', tr: 'İstirahat tremoru', en: 'Rest tremor' },
  { field: 'tremor_action', tr: 'Aksiyon tremoru', en: 'Action tremor' },
  { field: 'rigidity', tr: 'Rijidite', en: 'Rigidity' },
  { field: 'finger_tapping', tr: 'Parmak vurma', en: 'Finger tapping' },
  { field: 'hand_movements', tr: 'El hareketleri', en: 'Hand movements' },
  { field: 'leg_agility', tr: 'Bacak çevikliği', en: 'Leg agility' },
  { field: 'arising_from_chair', tr: 'Sandalyeden kalkma', en: 'Arising from chair' },
  { field: 'gait', tr: 'Yürüyüş', en: 'Gait' },
  { field: 'postural_stability', tr: 'Postüral stabilite', en: 'Postural stability' },
  { field: 'body_bradykinesia', tr: 'Genel bradikinezi', en: 'Body bradykinesia' },
];

function NoseraMotorModal({ locale, onClose }: { locale: string; onClose: () => void }) {
  const tr = (t: string, e: string) => locale === 'tr' ? t : e;
  const [scores, setScores] = useState<Record<string, number>>(Object.fromEntries(MOTOR_ITEMS.map((i) => [i.field, 0])));
  const [notes, setNotes] = useState('');
  const create = useCreateNoseraMotor();
  const total = Object.values(scores).reduce((a, b) => a + b, 0);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{tr('Norosera Motor Değerlendirme', 'Norosera Motor Assessment')}</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-4 space-y-4">
          <p className="text-xs text-gray-500">{tr('Her maddeyi 0 (normal) ile 4 (çok şiddetli) arasında puanlayın.', 'Rate each item from 0 (normal) to 4 (most severe).')}</p>
          {MOTOR_ITEMS.map((item) => (
            <div key={item.field}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{locale === 'tr' ? item.tr : item.en}</span>
                <span className="text-sm font-bold text-teal-700">{scores[item.field]}/4</span>
              </div>
              <input
                type="range" min={0} max={4} value={scores[item.field]}
                onChange={(e) => setScores((prev) => ({ ...prev, [item.field]: parseInt(e.target.value) }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>
          ))}
          <div className="bg-teal-50 rounded-lg p-3 text-center">
            <span className="text-lg font-bold text-teal-700">{tr('Toplam:', 'Total:')} {total}/40</span>
          </div>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr('Notlar...', 'Notes...')} className="w-full border rounded-lg p-2 text-sm h-16 resize-none" />
          <button
            disabled={create.isPending}
            onClick={() => create.mutate({ assessed_at: new Date().toISOString(), ...scores, notes } as any, { onSuccess: onClose })}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />} {tr('Kaydet', 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== NOROSERA DAILY LIVING MODAL ====================

const DAILY_ITEMS: { field: string; tr: string; en: string }[] = [
  { field: 'speech', tr: 'Konuşma', en: 'Speech' },
  { field: 'salivation', tr: 'Tükürük', en: 'Salivation' },
  { field: 'swallowing', tr: 'Yutma', en: 'Swallowing' },
  { field: 'handwriting', tr: 'El yazısı', en: 'Handwriting' },
  { field: 'cutting_food', tr: 'Yemek kesme', en: 'Cutting food' },
  { field: 'dressing', tr: 'Giyinme', en: 'Dressing' },
  { field: 'hygiene', tr: 'Hijyen', en: 'Hygiene' },
  { field: 'turning_in_bed', tr: 'Yatakta dönme', en: 'Turning in bed' },
  { field: 'falling', tr: 'Düşme', en: 'Falling' },
  { field: 'freezing', tr: 'Donma', en: 'Freezing' },
  { field: 'walking', tr: 'Yürüme', en: 'Walking' },
  { field: 'tremor_impact', tr: 'Tremor etkisi', en: 'Tremor impact' },
];

function NoseraDailyLivingModal({ locale, onClose }: { locale: string; onClose: () => void }) {
  const tr = (t: string, e: string) => locale === 'tr' ? t : e;
  const [scores, setScores] = useState<Record<string, number>>(Object.fromEntries(DAILY_ITEMS.map((i) => [i.field, 0])));
  const [notes, setNotes] = useState('');
  const create = useCreateNoseraDailyLiving();
  const total = Object.values(scores).reduce((a, b) => a + b, 0);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{tr('Norosera Günlük Yaşam', 'Norosera Daily Living')}</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-4 space-y-4">
          <p className="text-xs text-gray-500">{tr('Her maddeyi 0 (normal) ile 4 (çok güç) arasında puanlayın.', 'Rate each item from 0 (normal) to 4 (most difficult).')}</p>
          {DAILY_ITEMS.map((item) => (
            <div key={item.field}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">{locale === 'tr' ? item.tr : item.en}</span>
                <span className="text-sm font-bold text-teal-700">{scores[item.field]}/4</span>
              </div>
              <input
                type="range" min={0} max={4} value={scores[item.field]}
                onChange={(e) => setScores((prev) => ({ ...prev, [item.field]: parseInt(e.target.value) }))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
              />
            </div>
          ))}
          <div className="bg-teal-50 rounded-lg p-3 text-center">
            <span className="text-lg font-bold text-teal-700">{tr('Toplam:', 'Total:')} {total}/48</span>
          </div>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr('Notlar...', 'Notes...')} className="w-full border rounded-lg p-2 text-sm h-16 resize-none" />
          <button
            disabled={create.isPending}
            onClick={() => create.mutate({ assessed_at: new Date().toISOString(), ...scores, notes } as any, { onSuccess: onClose })}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />} {tr('Kaydet', 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
}

// ==================== NMSQUEST MODAL ====================

const NMS_QUESTIONS: { field: string; tr: string; en: string }[] = [
  { field: 'q1_drooling', tr: 'Ağızdan salya akması', en: 'Drooling' },
  { field: 'q2_dysphagia', tr: 'Yutma güçlüğü', en: 'Swallowing difficulty' },
  { field: 'q3_constipation', tr: 'Kabızlık', en: 'Constipation' },
  { field: 'q4_urinary_urgency', tr: 'İdrar sıkışması', en: 'Urinary urgency' },
  { field: 'q5_nocturia', tr: 'Gece idrara çıkma', en: 'Nocturia' },
  { field: 'q6_dizziness', tr: 'Baş dönmesi', en: 'Dizziness' },
  { field: 'q7_sweating', tr: 'Aşırı terleme', en: 'Excessive sweating' },
  { field: 'q8_sexual_dysfunction', tr: 'Cinsel işlev bozukluğu', en: 'Sexual dysfunction' },
  { field: 'q9_insomnia', tr: 'Uykuya dalamama', en: 'Insomnia' },
  { field: 'q10_daytime_sleepiness', tr: 'Gündüz uyuklama', en: 'Daytime sleepiness' },
  { field: 'q11_rbd', tr: 'REM uyku davranış bozukluğu', en: 'REM sleep behavior disorder' },
  { field: 'q12_restless_legs', tr: 'Huzursuz bacak', en: 'Restless legs' },
  { field: 'q13_depression', tr: 'Depresif ruh hali', en: 'Depression' },
  { field: 'q14_anxiety', tr: 'Anksiyete/endişe', en: 'Anxiety' },
  { field: 'q15_apathy', tr: 'İlgisizlik/apati', en: 'Apathy' },
  { field: 'q16_attention_difficulty', tr: 'Dikkat güçlüğü', en: 'Attention difficulty' },
  { field: 'q17_memory_problem', tr: 'Bellek sorunu', en: 'Memory problem' },
  { field: 'q18_hallucination', tr: 'Halüsinasyon', en: 'Hallucination' },
  { field: 'q19_pain', tr: 'Ağrı', en: 'Pain' },
  { field: 'q20_numbness', tr: 'Uyuşma/karıncalanma', en: 'Numbness/tingling' },
  { field: 'q21_taste_smell', tr: 'Tat/koku değişikliği', en: 'Taste/smell change' },
  { field: 'q22_weight_change', tr: 'Kilo değişikliği', en: 'Weight change' },
  { field: 'q23_fatigue', tr: 'Yorgunluk', en: 'Fatigue' },
  { field: 'q24_double_vision', tr: 'Çift görme', en: 'Double vision' },
  { field: 'q25_speech', tr: 'Konuşma değişikliği', en: 'Speech change' },
  { field: 'q26_falling', tr: 'Düşme', en: 'Falling' },
  { field: 'q27_freezing', tr: 'Donma', en: 'Freezing' },
  { field: 'q28_leg_swelling', tr: 'Bacak şişmesi', en: 'Leg swelling' },
  { field: 'q29_excessive_saliva', tr: 'Aşırı tükürük', en: 'Excessive saliva' },
  { field: 'q30_unexplained_fever', tr: 'Açıklanamayan ateş', en: 'Unexplained fever' },
];

function NMSQuestModal({ locale, onClose }: { locale: string; onClose: () => void }) {
  const tr = (t: string, e: string) => locale === 'tr' ? t : e;
  const [answers, setAnswers] = useState<Record<string, boolean>>(Object.fromEntries(NMS_QUESTIONS.map((q) => [q.field, false])));
  const [notes, setNotes] = useState('');
  const create = useCreateNMSQuest();
  const yesCount = Object.values(answers).filter(Boolean).length;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">NMSQuest</h2>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-4">
          <p className="text-xs text-gray-500 mb-3">{tr('Son 1 ayda aşağıdaki belirtileri yaşadınız mı?', 'Have you experienced the following in the past month?')}</p>
          <div className="space-y-2 mb-4">
            {NMS_QUESTIONS.map((q, idx) => (
              <button
                key={q.field}
                onClick={() => setAnswers((prev) => ({ ...prev, [q.field]: !prev[q.field] }))}
                className={`w-full text-left p-3 rounded-lg border-2 text-sm flex items-center gap-3 transition ${
                  answers[q.field] ? 'border-orange-400 bg-orange-50' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className={`w-6 h-6 rounded flex items-center justify-center flex-shrink-0 ${
                  answers[q.field] ? 'bg-orange-500 text-white' : 'bg-gray-100'
                }`}>
                  {answers[q.field] && <CheckCircle2 className="w-4 h-4" />}
                </div>
                <span className="flex-1">{idx + 1}. {locale === 'tr' ? q.tr : q.en}</span>
              </button>
            ))}
          </div>
          <div className="bg-orange-50 rounded-lg p-3 text-center mb-4">
            <span className="text-lg font-bold text-orange-700">{tr('Skor:', 'Score:')} {yesCount}/30</span>
          </div>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={tr('Notlar...', 'Notes...')} className="w-full border rounded-lg p-2 text-sm h-16 resize-none mb-4" />
          <button
            disabled={create.isPending}
            onClick={() => create.mutate({ assessed_at: new Date().toISOString(), ...answers, notes } as any, { onSuccess: onClose })}
            className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />} {tr('Kaydet', 'Save')}
          </button>
        </div>
      </div>
    </div>
  );
}
