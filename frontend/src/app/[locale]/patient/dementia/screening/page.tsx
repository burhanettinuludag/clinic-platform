'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Brain,
  Clock,
  MapPin,
  BookOpen,
  Target,
  Lightbulb,
  ChevronRight,
  ChevronLeft,
  Check,
  X,
  AlertCircle,
  Trophy,
} from 'lucide-react';
import { useCreateCognitiveScreening, useLatestCognitiveScreening } from '@/hooks/useDementiaData';

// Screening questions - original, copyright-free
const SCREENING_SECTIONS = [
  {
    id: 'orientation',
    title: 'Yonelim',
    icon: MapPin,
    description: 'Zaman ve mekan farkindaliginizi olcuyoruz',
    questions: [
      { id: 'or1', text: 'Simdi hangi yildayiz?', type: 'text', answer: new Date().getFullYear().toString() },
      { id: 'or2', text: 'Simdi hangi mevsim?', type: 'choice', options: ['Ilkbahar', 'Yaz', 'Sonbahar', 'Kis'], answer: getCurrentSeason() },
      { id: 'or3', text: 'Bugun ayin kaci?', type: 'text', answer: new Date().getDate().toString() },
      { id: 'or4', text: 'Bugun haftanin hangi gunu?', type: 'choice', options: ['Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi', 'Pazar'], answer: getCurrentDay() },
      { id: 'or5', text: 'Su an hangi ulkedesiniz?', type: 'text', answer: 'turkiye' },
    ],
  },
  {
    id: 'memory',
    title: 'Bellek',
    icon: Brain,
    description: 'Kisa sureli belleginizi olcuyoruz',
    questions: [
      { id: 'mem1', text: 'Su uc kelimeyi ezberleyin: ELMA, MASA, PARA. Simdi bunlari tekrar edin.', type: 'memory_recall', words: ['elma', 'masa', 'para'] },
      { id: 'mem2', text: '5 dakika once size soyledigim uc kelimeyi hatirlayabilir misiniz?', type: 'delayed_recall', words: ['elma', 'masa', 'para'] },
    ],
  },
  {
    id: 'attention',
    title: 'Dikkat',
    icon: Target,
    description: 'Dikkat ve konsantrasyon yeteneginizi olcuyoruz',
    questions: [
      { id: 'att1', text: '100\'den 7\'ser 7\'ser geriye dogru sayin (100, 93, 86...)', type: 'serial_subtraction', expected: [93, 86, 79, 72, 65] },
      { id: 'att2', text: '"DUNYA" kelimesini tersten soyleyin', type: 'text', answer: 'aynud' },
    ],
  },
  {
    id: 'language',
    title: 'Dil',
    icon: BookOpen,
    description: 'Dil ve anlama yeteneginizi olcuyoruz',
    questions: [
      { id: 'lan1', text: 'Bu nesnenin adi nedir? (Kol saati gosteriliyor)', type: 'text', answer: 'saat' },
      { id: 'lan2', text: 'Bu nesnenin adi nedir? (Kalem gosteriliyor)', type: 'text', answer: 'kalem' },
      { id: 'lan3', text: '"Ne yagmur ne kar" cumlesini tekrar edin', type: 'text', answer: 'ne yagmur ne kar' },
      { id: 'lan4', text: 'Bir dakikada aklina gelen hayvan isimlerini say', type: 'fluency', minCount: 10 },
    ],
  },
  {
    id: 'executive',
    title: 'Yurutucu Islevler',
    icon: Lightbulb,
    description: 'Planlama ve problem cozme yeteneginizi olcuyoruz',
    questions: [
      { id: 'exe1', text: '"Bir elde bes parmak varsa, iki elde kac parmak var?"', type: 'text', answer: '10' },
      { id: 'exe2', text: '"Elma ve portakal birbirine nasil benzer?" (Ortak ozellikleri)', type: 'similarity', validAnswers: ['meyve', 'yenilen', 'vitamin'] },
      { id: 'exe3', text: 'Su sirayi tamamlayin: 2, 4, 6, 8, ?', type: 'text', answer: '10' },
    ],
  },
];

function getCurrentSeason(): string {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'Ilkbahar';
  if (month >= 5 && month <= 7) return 'Yaz';
  if (month >= 8 && month <= 10) return 'Sonbahar';
  return 'Kis';
}

function getCurrentDay(): string {
  const days = ['Pazar', 'Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma', 'Cumartesi'];
  return days[new Date().getDay()];
}

interface QuestionResponse {
  questionId: string;
  answer: string | string[] | number[];
  correct: boolean;
  score: number;
}

export default function CognitiveScreeningPage() {
  const router = useRouter();
  const { data: latestScreening } = useLatestCognitiveScreening();
  const createScreening = useCreateCognitiveScreening();

  const [currentSection, setCurrentSection] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [responses, setResponses] = useState<QuestionResponse[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const [memoryWords, setMemoryWords] = useState<string[]>([]);
  const [serialNumbers, setSerialNumbers] = useState<number[]>([]);
  const [fluencyAnswers, setFluencyAnswers] = useState<string[]>([]);
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [showMemoryPhase, setShowMemoryPhase] = useState(false);
  const [memoryTimer, setMemoryTimer] = useState(0);

  const section = SCREENING_SECTIONS[currentSection];
  const question = section?.questions[currentQuestion];
  const totalQuestions = SCREENING_SECTIONS.reduce((sum, s) => sum + s.questions.length, 0);
  const answeredQuestions = responses.length;

  // Memory timer for delayed recall
  useEffect(() => {
    if (showMemoryPhase && memoryTimer > 0) {
      const timer = setTimeout(() => setMemoryTimer(memoryTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [showMemoryPhase, memoryTimer]);

  const startTest = () => {
    setTestStarted(true);
    setStartTime(new Date());
  };

  const evaluateAnswer = useCallback((q: typeof question, answer: string | string[] | number[]): { correct: boolean; score: number } => {
    if (!q) return { correct: false, score: 0 };

    switch (q.type) {
      case 'text': {
        const normalizedAnswer = String(answer).toLowerCase().trim();
        const normalizedExpected = (q.answer as string).toLowerCase().trim();
        const correct = normalizedAnswer === normalizedExpected ||
                       normalizedAnswer.includes(normalizedExpected) ||
                       normalizedExpected.includes(normalizedAnswer);
        return { correct, score: correct ? 100 : 0 };
      }
      case 'choice': {
        const correct = String(answer) === q.answer;
        return { correct, score: correct ? 100 : 0 };
      }
      case 'memory_recall': {
        const words = answer as string[];
        const expectedWords = q.words as string[];
        const correctCount = words.filter(w =>
          expectedWords.some(ew => ew.toLowerCase() === w.toLowerCase().trim())
        ).length;
        return { correct: correctCount === expectedWords.length, score: (correctCount / expectedWords.length) * 100 };
      }
      case 'delayed_recall': {
        const words = answer as string[];
        const expectedWords = q.words as string[];
        const correctCount = words.filter(w =>
          expectedWords.some(ew => ew.toLowerCase() === w.toLowerCase().trim())
        ).length;
        return { correct: correctCount === expectedWords.length, score: (correctCount / expectedWords.length) * 100 };
      }
      case 'serial_subtraction': {
        const numbers = answer as number[];
        const expected = q.expected as number[];
        let correctCount = 0;
        numbers.forEach((num, idx) => {
          if (idx < expected.length && num === expected[idx]) correctCount++;
        });
        return { correct: correctCount === expected.length, score: (correctCount / expected.length) * 100 };
      }
      case 'similarity': {
        const validAnswers = q.validAnswers as string[];
        const normalizedAnswer = String(answer).toLowerCase().trim();
        const correct = validAnswers.some(va => normalizedAnswer.includes(va.toLowerCase()));
        return { correct, score: correct ? 100 : 0 };
      }
      case 'fluency': {
        const items = answer as string[];
        const uniqueItems = [...new Set(items.map(i => i.toLowerCase().trim()).filter(i => i))];
        const minCount = q.minCount as number;
        const score = Math.min(100, (uniqueItems.length / minCount) * 100);
        return { correct: uniqueItems.length >= minCount, score };
      }
      default:
        return { correct: false, score: 0 };
    }
  }, []);

  const submitAnswer = () => {
    if (!question) return;

    let answer: string | string[] | number[] = currentAnswer;

    if (question.type === 'memory_recall' || question.type === 'delayed_recall') {
      answer = memoryWords;
    } else if (question.type === 'serial_subtraction') {
      answer = serialNumbers;
    } else if (question.type === 'fluency') {
      answer = fluencyAnswers;
    }

    const { correct, score } = evaluateAnswer(question, answer);

    setResponses(prev => [...prev, {
      questionId: question.id,
      answer,
      correct,
      score,
    }]);

    // Reset inputs
    setCurrentAnswer('');
    setMemoryWords([]);
    setSerialNumbers([]);
    setFluencyAnswers([]);

    // Move to next question or section
    if (currentQuestion < section.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else if (currentSection < SCREENING_SECTIONS.length - 1) {
      setCurrentSection(currentSection + 1);
      setCurrentQuestion(0);
    } else {
      // Test completed
      setTestCompleted(true);
    }
  };

  const calculateResults = useCallback(() => {
    const sectionScores: Record<string, number[]> = {};

    responses.forEach(r => {
      const sectionId = SCREENING_SECTIONS.find(s =>
        s.questions.some(q => q.id === r.questionId)
      )?.id;
      if (sectionId) {
        if (!sectionScores[sectionId]) sectionScores[sectionId] = [];
        sectionScores[sectionId].push(r.score);
      }
    });

    const domainScores = {
      orientation: sectionScores.orientation ?
        sectionScores.orientation.reduce((a, b) => a + b, 0) / sectionScores.orientation.length : 0,
      memory: sectionScores.memory ?
        sectionScores.memory.reduce((a, b) => a + b, 0) / sectionScores.memory.length : 0,
      attention: sectionScores.attention ?
        sectionScores.attention.reduce((a, b) => a + b, 0) / sectionScores.attention.length : 0,
      language: sectionScores.language ?
        sectionScores.language.reduce((a, b) => a + b, 0) / sectionScores.language.length : 0,
      executive: sectionScores.executive ?
        sectionScores.executive.reduce((a, b) => a + b, 0) / sectionScores.executive.length : 0,
    };

    const totalScore = Object.values(domainScores).reduce((a, b) => a + b, 0) / 5;

    return { domainScores, totalScore };
  }, [responses]);

  const saveResults = async () => {
    const { domainScores, totalScore } = calculateResults();
    const endTime = new Date();
    const durationMinutes = startTime ? Math.round((endTime.getTime() - startTime.getTime()) / 60000) : null;

    try {
      await createScreening.mutateAsync({
        assessment_date: new Date().toISOString().split('T')[0],
        orientation_score: domainScores.orientation,
        memory_score: domainScores.memory,
        attention_score: domainScores.attention,
        language_score: domainScores.language,
        executive_score: domainScores.executive,
        responses: Object.fromEntries(responses.map(r => [r.questionId, r])),
        duration_minutes: durationMinutes,
      });
      router.push('/patient/dementia');
    } catch (error) {
      console.error('Failed to save screening results:', error);
    }
  };

  const getInterpretation = (score: number) => {
    if (score >= 80) return { level: 'normal', label: 'Normal Bilissel Fonksiyon', color: 'text-green-600' };
    if (score >= 60) return { level: 'mild', label: 'Hafif Bilissel Zorluk', color: 'text-yellow-600' };
    if (score >= 40) return { level: 'moderate', label: 'Orta Duzey Bilissel Zorluk', color: 'text-orange-600' };
    return { level: 'severe', label: 'Ciddi Bilissel Zorluk', color: 'text-red-600' };
  };

  // Test intro screen
  if (!testStarted) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Brain className="h-8 w-8 text-indigo-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Bilissel Tarama Testi</h1>
          <p className="text-gray-600 mb-6">
            Bu test, bilissel fonksiyonlarinizi degerlendirmek icin tasarlanmistir.
            Test yaklasik 10-15 dakika surecektir ve su alanlari olcer:
          </p>

          <div className="grid grid-cols-2 gap-4 mb-8">
            {SCREENING_SECTIONS.map((section) => {
              const Icon = section.icon;
              return (
                <div key={section.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Icon className="h-5 w-5 text-indigo-600" />
                  <span className="text-sm font-medium text-gray-700">{section.title}</span>
                </div>
              );
            })}
          </div>

          {latestScreening && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                Son test tarihi: {new Date(latestScreening.assessment_date).toLocaleDateString('tr-TR')}
                <br />
                Son skor: %{latestScreening.total_score.toFixed(0)}
              </p>
            </div>
          )}

          <button
            onClick={startTest}
            className="w-full py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition"
          >
            Teste Basla
          </button>
        </div>
      </div>
    );
  }

  // Test completed screen
  if (testCompleted) {
    const { domainScores, totalScore } = calculateResults();
    const interpretation = getInterpretation(totalScore);

    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Trophy className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Test Tamamlandi!</h1>
            <p className={`text-lg font-semibold ${interpretation.color}`}>
              {interpretation.label}
            </p>
          </div>

          {/* Overall Score */}
          <div className="text-center mb-8">
            <div className="text-5xl font-bold text-indigo-600 mb-2">
              %{totalScore.toFixed(0)}
            </div>
            <p className="text-gray-500">Genel Skor</p>
          </div>

          {/* Domain Scores */}
          <div className="space-y-4 mb-8">
            {SCREENING_SECTIONS.map((section) => {
              const score = domainScores[section.id as keyof typeof domainScores] || 0;
              const Icon = section.icon;
              return (
                <div key={section.id}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-gray-500" />
                      <span className="text-sm font-medium text-gray-700">{section.title}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">%{score.toFixed(0)}</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Recommendation */}
          <div className="p-4 bg-blue-50 rounded-lg mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-blue-800">
                  Bu test sadece tarama amacidir ve tibbi tani yerine gecmez.
                  Sonuclariniz hakkinda endiseleriniz varsa lutfen doktorunuza danisin.
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={saveResults}
            disabled={createScreening.isPending}
            className="w-full py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {createScreening.isPending ? 'Kaydediliyor...' : 'Sonuclari Kaydet'}
          </button>
        </div>
      </div>
    );
  }

  // Active test screen
  return (
    <div className="p-6 max-w-2xl mx-auto">
      {/* Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span>{section.title}</span>
          <span>{answeredQuestions + 1} / {totalQuestions}</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 rounded-full transition-all duration-300"
            style={{ width: `${((answeredQuestions) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          {(() => {
            const Icon = section.icon;
            return <Icon className="h-6 w-6 text-indigo-600" />;
          })()}
          <div>
            <h2 className="font-semibold text-gray-900">{section.title}</h2>
            <p className="text-sm text-gray-500">{section.description}</p>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-lg text-gray-800 mb-4">{question?.text}</p>

          {/* Text input */}
          {question?.type === 'text' && (
            <input
              type="text"
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Cevabinizi yazin..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              autoFocus
            />
          )}

          {/* Choice input */}
          {question?.type === 'choice' && (
            <div className="space-y-2">
              {(question.options as string[])?.map((option) => (
                <button
                  key={option}
                  onClick={() => setCurrentAnswer(option)}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 transition ${
                    currentAnswer === option
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          )}

          {/* Memory recall input */}
          {(question?.type === 'memory_recall' || question?.type === 'delayed_recall') && (
            <div className="space-y-3">
              {[0, 1, 2].map((idx) => (
                <input
                  key={idx}
                  type="text"
                  value={memoryWords[idx] || ''}
                  onChange={(e) => {
                    const newWords = [...memoryWords];
                    newWords[idx] = e.target.value;
                    setMemoryWords(newWords);
                  }}
                  placeholder={`${idx + 1}. kelime`}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              ))}
            </div>
          )}

          {/* Serial subtraction input */}
          {question?.type === 'serial_subtraction' && (
            <div className="grid grid-cols-5 gap-2">
              {[0, 1, 2, 3, 4].map((idx) => (
                <input
                  key={idx}
                  type="number"
                  value={serialNumbers[idx] || ''}
                  onChange={(e) => {
                    const newNumbers = [...serialNumbers];
                    newNumbers[idx] = parseInt(e.target.value) || 0;
                    setSerialNumbers(newNumbers);
                  }}
                  placeholder={`${idx + 1}.`}
                  className="w-full px-3 py-3 text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              ))}
            </div>
          )}

          {/* Similarity input */}
          {question?.type === 'similarity' && (
            <input
              type="text"
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Ortak ozelligi yazin..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              autoFocus
            />
          )}

          {/* Fluency input */}
          {question?.type === 'fluency' && (
            <div>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && currentAnswer.trim()) {
                      setFluencyAnswers([...fluencyAnswers, currentAnswer.trim()]);
                      setCurrentAnswer('');
                    }
                  }}
                  placeholder="Hayvan adi yazin ve Enter'a basin"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <button
                  onClick={() => {
                    if (currentAnswer.trim()) {
                      setFluencyAnswers([...fluencyAnswers, currentAnswer.trim()]);
                      setCurrentAnswer('');
                    }
                  }}
                  className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Ekle
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {fluencyAnswers.map((item, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm"
                  >
                    {item}
                    <button
                      onClick={() => setFluencyAnswers(fluencyAnswers.filter((_, i) => i !== idx))}
                      className="hover:text-indigo-900"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {fluencyAnswers.length} hayvan eklendi (hedef: en az 10)
              </p>
            </div>
          )}
        </div>

        <button
          onClick={submitAnswer}
          disabled={
            (question?.type === 'text' && !currentAnswer.trim()) ||
            (question?.type === 'choice' && !currentAnswer) ||
            (question?.type === 'similarity' && !currentAnswer.trim())
          }
          className="w-full py-3 px-6 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
        >
          Devam Et
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
