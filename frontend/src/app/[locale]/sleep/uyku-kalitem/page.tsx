'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  Moon, ChevronLeft, ChevronRight, RotateCcw,
  AlertTriangle, CheckCircle2, ShieldAlert, Stethoscope, Clock,
} from 'lucide-react';

interface Question {
  id: number;
  text: string;
  helpText?: string;
  options: { text: string; score: number }[];
  category: 'quality' | 'latency' | 'duration' | 'efficiency' | 'disturbance' | 'daytime';
}

const QUESTIONS: Question[] = [
  {
    id: 1,
    text: 'Son 3 ayda genel uyku kalitenizi nasıl değerlendirirsiniz?',
    category: 'quality',
    options: [
      { text: 'Çok iyi', score: 0 },
      { text: 'Oldukça iyi', score: 1 },
      { text: 'Oldukça kötü', score: 2 },
      { text: 'Çok kötü', score: 3 },
    ],
  },
  {
    id: 2,
    text: 'Yatağa girdikten sonra uykuya dalmanız genellikle ne kadar sürer?',
    category: 'latency',
    options: [
      { text: '15 dakikadan az', score: 0 },
      { text: '16-30 dakika', score: 1 },
      { text: '31-60 dakika', score: 2 },
      { text: '60 dakikadan fazla', score: 3 },
    ],
  },
  {
    id: 3,
    text: 'Gecede ortalama kaç saat uyursunuz?',
    category: 'duration',
    options: [
      { text: '7 saat veya daha fazla', score: 0 },
      { text: '6-7 saat', score: 1 },
      { text: '5-6 saat', score: 2 },
      { text: '5 saatten az', score: 3 },
    ],
  },
  {
    id: 4,
    text: 'Gece boyunca kaç kez uyanırsınız?',
    category: 'disturbance',
    options: [
      { text: 'Hiç veya nadiren', score: 0 },
      { text: '1-2 kez', score: 1 },
      { text: '3-4 kez', score: 2 },
      { text: '5 veya daha fazla', score: 3 },
    ],
  },
  {
    id: 5,
    text: 'Gece uyandığınızda tekrar uyumakta zorlanır mısınız?',
    category: 'efficiency',
    options: [
      { text: 'Hayır, hemen uyurum', score: 0 },
      { text: 'Bazen biraz zorlanırım', score: 1 },
      { text: 'Çoğu zaman zorlanırım', score: 2 },
      { text: 'Evet, uzun süre uyuyamam', score: 3 },
    ],
  },
  {
    id: 6,
    text: 'Sabah uyandığınızda kendinizi dinlenmiş hissediyor musunuz?',
    category: 'quality',
    options: [
      { text: 'Evet, her zaman', score: 0 },
      { text: 'Çoğu zaman', score: 1 },
      { text: 'Nadiren', score: 2 },
      { text: 'Hayır, hiçbir zaman', score: 3 },
    ],
  },
  {
    id: 7,
    text: 'Gündüz saatlerinde aşırı uyuklama veya yorgunluk yaşıyor musunuz?',
    category: 'daytime',
    options: [
      { text: 'Hayır', score: 0 },
      { text: 'Haftada 1-2 gün', score: 1 },
      { text: 'Haftada 3-4 gün', score: 2 },
      { text: 'Neredeyse her gün', score: 3 },
    ],
  },
  {
    id: 8,
    text: 'Gündüz uykululuğunuz günlük aktivitelerinizi (iş, araba kullanma, sosyal hayat) etkiliyor mu?',
    category: 'daytime',
    options: [
      { text: 'Hayır, hiç etkilemiyor', score: 0 },
      { text: 'Hafif etkiliyor', score: 1 },
      { text: 'Belirgin şekilde etkiliyor', score: 2 },
      { text: 'Ciddi şekilde etkiliyor', score: 3 },
    ],
  },
  {
    id: 9,
    text: 'Son 3 ayda aşağıdakilerden hangilerini haftada en az 3 kez yaşadınız?',
    helpText: 'En sık yaşadığınız durumu seçin',
    category: 'disturbance',
    options: [
      { text: 'Bunların hiçbiri', score: 0 },
      { text: 'Horlama veya nefes zorluğu', score: 2 },
      { text: 'Bacaklarda huzursuzluk veya kramp', score: 2 },
      { text: 'Kâbus görme veya uyku sırasında konuşma/yürüme', score: 2 },
    ],
  },
  {
    id: 10,
    text: 'Uyumak için ilaç (reçeteli, bitkisel veya takviye) kullanıyor musunuz?',
    category: 'quality',
    options: [
      { text: 'Hayır, hiç kullanmıyorum', score: 0 },
      { text: 'Ayda birkaç kez', score: 1 },
      { text: 'Haftada 1-2 kez', score: 2 },
      { text: 'Haftada 3 veya daha fazla', score: 3 },
    ],
  },
  {
    id: 11,
    text: 'Uyku saatleriniz düzenli mi? (Hafta içi ve hafta sonu arasında 1 saatten fazla fark var mı?)',
    category: 'efficiency',
    options: [
      { text: 'Evet, çok düzenli (fark 1 saatten az)', score: 0 },
      { text: 'Genellikle düzenli (1-2 saat fark)', score: 1 },
      { text: 'Düzensiz (2-3 saat fark)', score: 2 },
      { text: 'Çok düzensiz (3+ saat fark)', score: 3 },
    ],
  },
  {
    id: 12,
    text: 'Yatmadan önce ekran (telefon, tablet, bilgisayar) kullanır mısınız?',
    category: 'latency',
    options: [
      { text: 'Hayır veya yatmadan 1+ saat önce bırakırım', score: 0 },
      { text: 'Yatmadan 30-60 dakika önce bırakırım', score: 1 },
      { text: 'Yatağa kadar kullanırım', score: 2 },
      { text: 'Yatakta da kullanmaya devam ederim', score: 3 },
    ],
  },
];

interface ResultLevel {
  min: number;
  max: number;
  level: 'excellent' | 'good' | 'moderate' | 'poor' | 'severe';
  title: string;
  description: string;
  color: string;
  bgColor: string;
  borderColor: string;
  recommendations: string[];
  seeDoctor: boolean;
  doctorNote?: string;
}

const RESULT_LEVELS: ResultLevel[] = [
  {
    min: 0,
    max: 6,
    level: 'excellent',
    title: 'Mükemmel Uyku Kalitesi',
    description: 'Uyku kaliteniz çok iyi görünüyor. Mevcut uyku alışkanlıklarınızı korumaya devam edin.',
    color: 'text-emerald-700',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    seeDoctor: false,
    recommendations: [
      'Mevcut uyku düzeninizi koruyun',
      'Düzenli egzersiz yapmaya devam edin',
      'Stres yönetimi tekniklerini sürdürün',
      'Düzenli sağlık kontrollerinizi yaptırın',
    ],
  },
  {
    min: 7,
    max: 13,
    level: 'good',
    title: 'İyi Uyku Kalitesi',
    description: 'Uyku kaliteniz genel olarak iyi, ancak bazı küçük iyileştirmeler yapabilirsiniz.',
    color: 'text-teal-700',
    bgColor: 'bg-teal-50',
    borderColor: 'border-teal-200',
    seeDoctor: false,
    recommendations: [
      'Uyku saatlerinizi daha düzenli hale getirin',
      'Yatmadan 1 saat önce ekranları kapatın',
      'Yatak odası sıcaklığını 18-20°C arasında tutun',
      'Kafein tüketimini öğleden sonra saat 14:00 ile sınırlandırın',
    ],
  },
  {
    min: 14,
    max: 21,
    level: 'moderate',
    title: 'Orta Düzey Uyku Sorunu',
    description: 'Uyku kalitenizde belirgin sorunlar var. Uyku hijyeni kurallarına dikkat etmeniz önerilir. Şikayetleriniz 4 haftadan uzun sürüyorsa bir hekime başvurmanız faydalı olacaktır.',
    color: 'text-amber-700',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    seeDoctor: true,
    doctorNote: 'Şikayetleriniz 4 haftadan uzun sürüyorsa bir uyku uzmanına veya nöroloğa başvurmanız önerilir.',
    recommendations: [
      'Uyku hijyeni kurallarını titizlikle uygulayın',
      'Her gün aynı saatte yatıp kalkın (hafta sonları dahil)',
      'Yatmadan 2-3 saat önce ağır yemekten kaçının',
      'Gevşeme teknikleri (4-7-8 nefes, kas gevşetme) uygulayın',
      'Yatakta 20 dakikadan fazla uyanık kalmayın — kalkıp sakin bir aktivite yapın',
      'Gündüz uykusunu 20 dakika ile sınırlandırın',
    ],
  },
  {
    min: 22,
    max: 28,
    level: 'poor',
    title: 'Kötü Uyku Kalitesi',
    description: 'Uyku kaliteniz ciddi şekilde bozulmuş görünüyor. Günlük yaşamınızı olumsuz etkileyebilecek düzeyde uyku sorununuz var. Bir sağlık profesyoneline başvurmanız önemle önerilir.',
    color: 'text-orange-700',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    seeDoctor: true,
    doctorNote: 'Bir uyku uzmanı veya nöroloğa en kısa sürede başvurmanız önerilir. Uyku bozukluğu tedavi edilebilir bir durumdur.',
    recommendations: [
      'En kısa sürede bir uyku uzmanına veya nöroloğa başvurun',
      'Uyku günlüğü tutmaya başlayın (doktorunuza götürmek için)',
      'Alkol ve kafein tüketimini tamamen bırakın veya minimize edin',
      'Düzenli uyku programı oluşturun ve kesinlikle uygulayın',
      'Yatak odasını sadece uyku için kullanın',
      'Stres kaynaklarınızı belirlemeye çalışın',
      'Uyku ilacını doktora danışmadan kullanmayın',
    ],
  },
  {
    min: 29,
    max: 36,
    level: 'severe',
    title: 'Ciddi Uyku Bozukluğu Riski',
    description: 'Sonuçlarınız ciddi bir uyku bozukluğuna işaret ediyor olabilir. Bu durum sağlığınızı, iş performansınızı ve yaşam kalitenizi önemli ölçüde etkileyebilir. Mutlaka bir sağlık profesyoneline başvurun.',
    color: 'text-red-700',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    seeDoctor: true,
    doctorNote: 'Bir uyku uzmanına veya nöroloğa acil başvurmanız önerilir. Polisomnografi (uyku testi) gerekebilir. Uyku bozuklukları tedavi edilebilir — yardım almaktan çekinmeyin.',
    recommendations: [
      'Bir uyku uzmanına veya nöroloğa acil başvurun',
      'Polisomnografi (uyku laboratuvarı testi) gerekebilir',
      'Araç kullanırken ve dikkat gerektiren işlerde ekstra dikkatli olun',
      'Uyku günlüğü tutun ve doktorunuza gösterin',
      'Horlama, nefes durması veya bacak huzursuzluğu varsa mutlaka belirtin',
      'Alkol ve sedatif ilaçlardan tamamen kaçının',
      'Bilişsel Davranışçı Terapi (BDT-İ) hakkında doktorunuza danışın',
    ],
  },
];

const CATEGORY_LABELS: Record<string, string> = {
  quality: 'Uyku Kalitesi',
  latency: 'Uykuya Dalma',
  duration: 'Uyku Süresi',
  efficiency: 'Uyku Verimliliği',
  disturbance: 'Uyku Bozulması',
  daytime: 'Gündüz İşlevselliği',
};

export default function UykuKalitemPage() {
  const params = useParams();
  const locale = (params?.locale as string) || 'tr';

  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [showResult, setShowResult] = useState(false);

  const question = QUESTIONS[currentQ];
  const totalQ = QUESTIONS.length;
  const progress = ((currentQ + 1) / totalQ) * 100;
  const answeredCount = Object.keys(answers).length;

  const totalScore = Object.values(answers).reduce((sum, v) => sum + v, 0);
  const maxScore = QUESTIONS.length * 3;
  const scorePercent = Math.round((totalScore / maxScore) * 100);

  const resultLevel = RESULT_LEVELS.find(
    (r) => totalScore >= r.min && totalScore <= r.max
  ) || RESULT_LEVELS[RESULT_LEVELS.length - 1];

  // Category breakdown
  const categoryScores: Record<string, { score: number; max: number }> = {};
  QUESTIONS.forEach((q) => {
    if (!categoryScores[q.category]) {
      categoryScores[q.category] = { score: 0, max: 0 };
    }
    categoryScores[q.category].max += 3;
    if (answers[q.id] !== undefined) {
      categoryScores[q.category].score += answers[q.id];
    }
  });

  const handleAnswer = (score: number) => {
    setAnswers((prev) => ({ ...prev, [question.id]: score }));
    if (currentQ < totalQ - 1) {
      setTimeout(() => setCurrentQ((prev) => prev + 1), 300);
    }
  };

  const handleFinish = () => {
    if (answeredCount === totalQ) {
      setShowResult(true);
    }
  };

  const handleRestart = () => {
    setAnswers({});
    setCurrentQ(0);
    setShowResult(false);
  };

  // ── RESULT SCREEN ──
  if (showResult) {
    const levelColors: Record<string, string> = {
      excellent: 'from-emerald-500 to-emerald-600',
      good: 'from-teal-500 to-teal-600',
      moderate: 'from-amber-500 to-amber-600',
      poor: 'from-orange-500 to-orange-600',
      severe: 'from-red-500 to-red-600',
    };

    const levelIcons: Record<string, React.ReactNode> = {
      excellent: <CheckCircle2 className="w-8 h-8 text-white" />,
      good: <CheckCircle2 className="w-8 h-8 text-white" />,
      moderate: <AlertTriangle className="w-8 h-8 text-white" />,
      poor: <ShieldAlert className="w-8 h-8 text-white" />,
      severe: <ShieldAlert className="w-8 h-8 text-white" />,
    };

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-2xl mx-auto px-4 py-8">
          {/* Back */}
          <Link
            href={`/${locale}/sleep`}
            className="inline-flex items-center gap-1.5 text-gray-500 hover:text-teal-600 text-sm mb-6 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Uyku Sağlığı
          </Link>

          {/* Score Card */}
          <div className={`rounded-2xl overflow-hidden shadow-lg mb-6 ${resultLevel.bgColor} ${resultLevel.borderColor} border`}>
            <div className={`bg-gradient-to-r ${levelColors[resultLevel.level]} p-6 text-center text-white`}>
              <div className="flex items-center justify-center gap-3 mb-3">
                {levelIcons[resultLevel.level]}
                <h1 className="text-2xl font-bold">{resultLevel.title}</h1>
              </div>
              <div className="flex items-center justify-center gap-2">
                <span className="text-4xl font-bold">{totalScore}</span>
                <span className="text-lg opacity-80">/ {maxScore}</span>
              </div>
              <p className="text-sm opacity-80 mt-1">puan</p>
            </div>

            <div className="p-6">
              {/* Score bar */}
              <div className="mb-4">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Mükemmel</span>
                  <span>Ciddi Sorun</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-1000 bg-gradient-to-r ${levelColors[resultLevel.level]}`}
                    style={{ width: `${scorePercent}%` }}
                  />
                </div>
              </div>

              <p className={`text-sm leading-relaxed ${resultLevel.color}`}>
                {resultLevel.description}
              </p>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Kategori Analizi</h2>
            <div className="space-y-3">
              {Object.entries(categoryScores).map(([cat, { score, max }]) => {
                const pct = Math.round((score / max) * 100);
                const barColor =
                  pct <= 25 ? 'bg-emerald-500' :
                  pct <= 50 ? 'bg-teal-500' :
                  pct <= 75 ? 'bg-amber-500' : 'bg-red-500';

                return (
                  <div key={cat}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700 font-medium">{CATEGORY_LABELS[cat] || cat}</span>
                      <span className="text-gray-500">{score}/{max}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div className={`h-2 rounded-full transition-all duration-700 ${barColor}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Doctor Warning */}
          {resultLevel.seeDoctor && (
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 mb-6">
              <div className="flex items-start gap-3">
                <Stethoscope className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-800 mb-1">Hekime Başvuru Önerisi</h3>
                  <p className="text-sm text-red-700 leading-relaxed">
                    {resultLevel.doctorNote}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Öneriler</h2>
            <ul className="space-y-3">
              {resultLevel.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 ${resultLevel.bgColor} ${resultLevel.color}`}>
                    {i + 1}
                  </span>
                  <span className="text-sm text-gray-700 leading-relaxed">{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 3-Month Warning */}
          <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-5 mb-6">
            <div className="flex items-start gap-3">
              <Clock className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-indigo-800 text-sm mb-1">Son 3 Ay Kriteri</h3>
                <p className="text-xs text-indigo-700 leading-relaxed">
                  Uyku bozuklukları tanısı için şikayetlerin <strong>son 3 ay içinde haftada en az 3 kez</strong> tekrarlanması önemlidir.
                  Bu kritere uyan şikayetleriniz varsa, tedavi edilebilir bir uyku bozukluğunuz olabilir — bir uyku uzmanına başvurun.
                </p>
              </div>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="bg-gray-100 rounded-xl p-4 mb-6 text-center">
            <p className="text-xs text-gray-500 leading-relaxed">
              Bu test tıbbi tanı aracı değildir. Genel bilgilendirme amaçlıdır ve profesyonel tıbbi değerlendirmenin yerini almaz.
              Uyku sorunlarınız için mutlaka bir sağlık profesyoneline başvurunuz.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleRestart}
              className="flex-1 flex items-center justify-center gap-2 px-5 py-3 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition text-sm font-medium"
            >
              <RotateCcw className="w-4 h-4" />
              Tekrar Yap
            </button>
            <Link
              href={`/${locale}/sleep`}
              className="flex-1 flex items-center justify-center gap-2 px-5 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition text-sm font-medium"
            >
              <Moon className="w-4 h-4" />
              Uyku Rehberi
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // ── QUESTION SCREEN ──
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Back */}
        <Link
          href={`/${locale}/sleep`}
          className="inline-flex items-center gap-1.5 text-gray-500 hover:text-teal-600 text-sm mb-6 transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          Uyku Sağlığı
        </Link>

        {/* Title */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Moon className="w-7 h-7 text-indigo-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Uyku Kalitem Nasıl?</h1>
          <p className="text-sm text-gray-500">
            12 soruyla uyku kalitenizi değerlendirin ve kişisel öneriler alın
          </p>
        </div>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 mb-1.5">
            <span>Soru {currentQ + 1} / {totalQ}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-indigo-500 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
              {CATEGORY_LABELS[question.category]}
            </span>
          </div>

          <h2 className="text-lg font-semibold text-gray-900 mb-1 leading-snug">
            {question.text}
          </h2>

          {question.helpText && (
            <p className="text-xs text-gray-400 mb-4">{question.helpText}</p>
          )}

          <div className="space-y-2 mt-4">
            {question.options.map((opt, i) => {
              const isSelected = answers[question.id] === opt.score;
              return (
                <button
                  key={i}
                  onClick={() => handleAnswer(opt.score)}
                  className={`w-full text-left px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-800'
                      : 'border-gray-100 bg-gray-50 text-gray-700 hover:border-indigo-200 hover:bg-indigo-50/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                      isSelected ? 'border-indigo-500 bg-indigo-500' : 'border-gray-300'
                    }`}>
                      {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                    </div>
                    {opt.text}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentQ((prev) => Math.max(0, prev - 1))}
            disabled={currentQ === 0}
            className="flex items-center gap-1.5 px-4 py-2.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-30 transition"
          >
            <ChevronLeft className="w-4 h-4" />
            Önceki
          </button>

          {/* Question dots */}
          <div className="flex gap-1">
            {QUESTIONS.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentQ(i)}
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  i === currentQ
                    ? 'bg-indigo-500 scale-125'
                    : answers[QUESTIONS[i].id] !== undefined
                    ? 'bg-indigo-300'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>

          {currentQ === totalQ - 1 ? (
            <button
              onClick={handleFinish}
              disabled={answeredCount < totalQ}
              className="flex items-center gap-1.5 px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-40 transition"
            >
              Sonucu Gör
            </button>
          ) : (
            <button
              onClick={() => setCurrentQ((prev) => Math.min(totalQ - 1, prev + 1))}
              className="flex items-center gap-1.5 px-4 py-2.5 text-sm text-gray-600 hover:text-gray-900 transition"
            >
              Sonraki
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Disclaimer at bottom */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-400">
            Bu test tıbbi tanı aracı değildir. Bilgilendirme amaçlıdır.
          </p>
        </div>
      </div>
    </div>
  );
}
