'use client';

import { useState } from 'react';
import { Link } from '@/i18n/navigation';
import {
  ArrowLeft, ArrowRight, Brain, CheckCircle2, AlertTriangle,
  Info, RotateCcw, Stethoscope, ClipboardList,
} from 'lucide-react';

// ID Migraine (3 soru) + Genişletilmiş tarama (toplam 10 soru)
const QUESTIONS = [
  {
    id: 'q1',
    text: 'Baş ağrınız sırasında bulantı veya mide rahatsızlığı yaşıyor musunuz?',
    category: 'id-migraine',
    weight: 2,
  },
  {
    id: 'q2',
    text: 'Baş ağrınız sırasında ışığa karşı hassasiyet (fotofobi) hissediyor musunuz?',
    category: 'id-migraine',
    weight: 2,
  },
  {
    id: 'q3',
    text: 'Baş ağrınız günlük aktivitelerinizi (iş, ev işi, sosyal hayat) engelliyor mu?',
    category: 'id-migraine',
    weight: 2,
  },
  {
    id: 'q4',
    text: 'Baş ağrınız genellikle başınızın bir tarafında mı hissediliyor?',
    category: 'location',
    weight: 1,
  },
  {
    id: 'q5',
    text: 'Baş ağrınız zonklayıcı veya nabız atar gibi bir karakter taşıyor mu?',
    category: 'character',
    weight: 1,
  },
  {
    id: 'q6',
    text: 'Baş ağrınız fiziksel aktiviteyle (merdiven çıkma, yürüyüş) artıyor mu?',
    category: 'activity',
    weight: 1,
  },
  {
    id: 'q7',
    text: 'Baş ağrınız sırasında sese karşı hassasiyet (fonofobi) yaşıyor musunuz?',
    category: 'phonophobia',
    weight: 1,
  },
  {
    id: 'q8',
    text: 'Baş ağrınız başlamadan önce görme bozuklukları (parlak noktalar, çizgiler, bulanıklık) oluyor mu?',
    category: 'aura',
    weight: 1,
  },
  {
    id: 'q9',
    text: 'Baş ağrılarınız genellikle 4 saatten uzun sürüyor mu?',
    category: 'duration',
    weight: 1,
  },
  {
    id: 'q10',
    text: 'Ailenizde (anne, baba, kardeş) migren tanısı alan biri var mı?',
    category: 'family',
    weight: 1,
  },
];

interface Result {
  score: number;
  maxScore: number;
  idMigraineScore: number;
  level: 'low' | 'moderate' | 'high';
  label: string;
  description: string;
  recommendations: string[];
}

function calculateResult(answers: Record<string, boolean>): Result {
  let score = 0;
  let idMigraineScore = 0;
  const maxScore = QUESTIONS.reduce((sum, q) => sum + q.weight, 0);

  for (const q of QUESTIONS) {
    if (answers[q.id]) {
      score += q.weight;
      if (q.category === 'id-migraine') {
        idMigraineScore++;
      }
    }
  }

  // ID Migraine: 2+ evet = %93 olasılıkla migren (Lipton et al. 2003)
  if (idMigraineScore >= 2 && score >= 7) {
    return {
      score, maxScore, idMigraineScore,
      level: 'high',
      label: 'Yüksek Olasılık',
      description: 'Belirtileriniz migren baş ağrısı ile yüksek düzeyde uyumludur. ID Migraine tarama kriterlerine göre, 3 temel sorudan en az 2\'sine "Evet" cevabı veren kişilerde migren olasılığı %93\'e kadar çıkmaktadır.',
      recommendations: [
        'Bir nöroloji uzmanına başvurmanızı öneririz',
        'Baş ağrısı günlüğü tutmaya başlayın',
        'Tetikleyicilerinizi belirlemeye çalışın',
        'Norosera migren takip modülünü kullanarak ataklarınızı kaydedin',
        'Doktorunuza bu tarama sonucunu gösterebilirsiniz',
      ],
    };
  } else if (idMigraineScore >= 2 || score >= 5) {
    return {
      score, maxScore, idMigraineScore,
      level: 'moderate',
      label: 'Orta Olasılık',
      description: 'Belirtileriniz kısmen migren baş ağrısı ile uyumludur. Kesin bir değerlendirme için tıbbi muayene önerilir. Gerilim tipi baş ağrısı veya diğer baş ağrısı türleri de benzer belirtiler gösterebilir.',
      recommendations: [
        'Bir hekime danışmanızı öneririz',
        'Baş ağrısı sıklığını ve süresini not edin',
        'Ağrı karakterini (zonklayıcı, sıkıştırıcı, baskı hissi) takip edin',
        'Stres, uyku düzeni ve beslenme alışkanlıklarınızı gözden geçirin',
      ],
    };
  } else {
    return {
      score, maxScore, idMigraineScore,
      level: 'low',
      label: 'Düşük Olasılık',
      description: 'Belirtileriniz tipik migren baş ağrısı kriterleri ile düşük düzeyde uyumludur. Ancak farklı baş ağrısı türleri olabilir. Baş ağrınız sık veya şiddetli ise bir hekime danışmanızı öneririz.',
      recommendations: [
        'Baş ağrınız devam ediyorsa bir hekime danışın',
        'Yeterli su tüketimi ve düzenli uyku alışkanlığı edinin',
        'Stres yönetimi tekniklerini deneyin',
        'Ağrı kesici kullanımını kontrol altında tutun',
      ],
    };
  }
}

export default function MigraineTestPage() {
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, boolean>>({});
  const [showResult, setShowResult] = useState(false);

  const question = QUESTIONS[currentQ];
  const answeredCount = Object.keys(answers).length;
  const progress = (answeredCount / QUESTIONS.length) * 100;
  const allAnswered = answeredCount === QUESTIONS.length;

  const handleAnswer = (value: boolean) => {
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
    if (currentQ < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentQ(currentQ + 1), 300);
    }
  };

  const handleReset = () => {
    setAnswers({});
    setCurrentQ(0);
    setShowResult(false);
  };

  const result = allAnswered ? calculateResult(answers) : null;

  if (showResult && result) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Link href="/patient/migraine" className="p-2 hover:bg-gray-100 rounded-lg transition">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Tarama Sonucu</h1>
        </div>

        {/* Result Card */}
        <div className={`rounded-2xl border-2 p-6 mb-6 ${
          result.level === 'high' ? 'border-red-200 bg-red-50' :
          result.level === 'moderate' ? 'border-yellow-200 bg-yellow-50' :
          'border-green-200 bg-green-50'
        }`}>
          <div className="flex items-center gap-4 mb-4">
            <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
              result.level === 'high' ? 'bg-red-100' :
              result.level === 'moderate' ? 'bg-yellow-100' :
              'bg-green-100'
            }`}>
              {result.level === 'high' ? <AlertTriangle className="w-7 h-7 text-red-600" /> :
               result.level === 'moderate' ? <Info className="w-7 h-7 text-yellow-600" /> :
               <CheckCircle2 className="w-7 h-7 text-green-600" />}
            </div>
            <div>
              <div className={`text-sm font-medium ${
                result.level === 'high' ? 'text-red-600' :
                result.level === 'moderate' ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                Migren Olasılığı
              </div>
              <div className="text-2xl font-bold text-gray-900">{result.label}</div>
              <div className="text-sm text-gray-500">
                Puan: {result.score}/{result.maxScore} | ID Migraine: {result.idMigraineScore}/3
              </div>
            </div>
          </div>

          <p className="text-sm text-gray-700 leading-relaxed mb-4">
            {result.description}
          </p>

          {/* Score bar */}
          <div className="mb-4">
            <div className="h-3 bg-white/50 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${
                  result.level === 'high' ? 'bg-red-500' :
                  result.level === 'moderate' ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}
                style={{ width: `${(result.score / result.maxScore) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <Stethoscope className="w-5 h-5 text-teal-600" />
            Önerilerimiz
          </h3>
          <ul className="space-y-3">
            {result.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-gray-700">
                <CheckCircle2 className="w-4 h-4 text-teal-500 mt-0.5 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>

        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <p className="text-xs text-amber-700">
            <strong>Önemli Uyarı:</strong> Bu tarama testi bilgilendirme amaçlıdır ve tıbbi bir tanı yerine geçmez.
            ID Migraine tarama aracı (Lipton RB, et al. Neurology, 2003) temel alınarak hazırlanmıştır.
            Kesin tanı için mutlaka bir nöroloji uzmanına başvurunuz.
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleReset}
            className="flex-1 flex items-center justify-center gap-2 py-3 border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition"
          >
            <RotateCcw className="w-4 h-4" />
            Testi Tekrarla
          </button>
          <Link
            href="/patient/migraine"
            className="flex-1 flex items-center justify-center gap-2 py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition"
          >
            <ClipboardList className="w-4 h-4" />
            Migren Takibine Git
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Link href="/patient/migraine" className="p-2 hover:bg-gray-100 rounded-lg transition">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Başağrım Migren mi?</h1>
          <p className="text-sm text-gray-500">ID Migraine tarama testi - 10 soru</p>
        </div>
      </div>

      {/* Info Banner */}
      {currentQ === 0 && Object.keys(answers).length === 0 && (
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <Brain className="w-5 h-5 text-purple-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-purple-900">Bu test ne işe yarar?</p>
              <p className="text-xs text-purple-700 mt-1">
                Uluslararası geçerliliği kanıtlanmış ID Migraine tarama aracı ve ek sorularla,
                baş ağrınızın migren olup olmadığını değerlendirmenize yardımcı olur.
                Test yaklaşık 2 dakika sürer.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
          <span>Soru {currentQ + 1}/{QUESTIONS.length}</span>
          <span>%{Math.round(progress)} tamamlandı</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-purple-600 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 mb-6">
        <div className="flex items-start gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold flex-shrink-0">
            {currentQ + 1}
          </div>
          <p className="text-lg font-medium text-gray-900 leading-relaxed pt-1.5">
            {question.text}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleAnswer(true)}
            className={`py-4 px-6 rounded-xl border-2 font-medium text-lg transition-all ${
              answers[question.id] === true
                ? 'border-purple-500 bg-purple-50 text-purple-700 ring-1 ring-purple-500'
                : 'border-gray-200 text-gray-700 hover:border-purple-300 hover:bg-purple-50/50'
            }`}
          >
            Evet
          </button>
          <button
            onClick={() => handleAnswer(false)}
            className={`py-4 px-6 rounded-xl border-2 font-medium text-lg transition-all ${
              answers[question.id] === false
                ? 'border-gray-500 bg-gray-50 text-gray-700 ring-1 ring-gray-500'
                : 'border-gray-200 text-gray-700 hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            Hayır
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
          disabled={currentQ === 0}
          className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg disabled:opacity-30 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Önceki
        </button>

        {/* Question dots */}
        <div className="flex items-center gap-1.5">
          {QUESTIONS.map((q, idx) => (
            <button
              key={q.id}
              onClick={() => setCurrentQ(idx)}
              className={`w-2.5 h-2.5 rounded-full transition-all ${
                idx === currentQ
                  ? 'bg-purple-600 scale-125'
                  : answers[q.id] !== undefined
                  ? 'bg-purple-300'
                  : 'bg-gray-200'
              }`}
            />
          ))}
        </div>

        {currentQ < QUESTIONS.length - 1 ? (
          <button
            onClick={() => setCurrentQ(currentQ + 1)}
            className="flex items-center gap-2 px-4 py-2 text-sm text-purple-700 hover:bg-purple-50 rounded-lg transition"
          >
            Sonraki
            <ArrowRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            onClick={() => setShowResult(true)}
            disabled={!allAnswered}
            className="flex items-center gap-2 px-6 py-2.5 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-30 transition font-medium"
          >
            Sonucu Gör
          </button>
        )}
      </div>
    </div>
  );
}
